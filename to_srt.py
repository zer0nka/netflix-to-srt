import codecs
import re
import math
import argparse


def leading_zeros(value, digits=2):
    value = "000000" + str(value)
    return value[-digits:]


def convert_time(raw_time):
    ms = leading_zeros(int(raw_time[:-4]) % 1000, 3)
    # only interested in milliseconds, let's drop the additional digits
    time_in_seconds = int(raw_time[:-7])
    second = leading_zeros(time_in_seconds % 60)
    minute = leading_zeros(int(math.floor(time_in_seconds / 60)))
    hour = leading_zeros(int(math.floor(time_in_seconds / 3600)))
    return "{}:{}:{},{}".format(hour, minute, second, ms)


def to_srt(text):
    sub_lines = (l for l in text.split("\n") if l.startswith("<p begin="))
    subs = []
    prev_time = {"start": 0, "end": 0}
    prev_content = []
    for s in sub_lines:
        start = re.search(u'begin\="([0-9]*)', s).group(1)
        end = re.search(u'end\="([0-9]*)', s).group(1)
        content = re.search(u'xml\:id\=\"subtitle[0-9]+\">(.*)</p>', s).group(1)
        alt_content = re.search(u'<span style=\"style_0\">(.*)</span>', s)
        if alt_content:  # some background text has additional styling
            content = alt_content.group(1)
        prev_start = prev_time["start"]
        if (prev_start == start and prev_time["end"] == end) or not prev_start:
            # Fix for multiple lines starting at the same time
            prev_time = {"start": start, "end": end}
            prev_content.append(content)
            continue
        subs.append({
            "start_time": convert_time(prev_time["start"]),
            "end_time": convert_time(prev_time["end"]),
            "content": u"\n".join(prev_content),
            })
        prev_time = {"start": start, "end": end}
        prev_content = [content]
    subs.append({
        "start_time": convert_time(start),
        "end_time": convert_time(end),
        "content": u"\n".join(prev_content),
    })

    lines = (u"{}\n{} --> {}\n{}\n".format(
        s+1, subs[s]["start_time"], subs[s]["end_time"], subs[s]["content"])
        for s in range(len(subs)))
    return u"\n".join(lines)

filename = "sample.xml"
help_text = "path to the {} file (defaults to {})"
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type=str, default=filename,
                    help=help_text.format("input", filename))
parser.add_argument("-o", "--output", type=str, default=filename + ".srt",
                    help=help_text.format("output", filename + ".srt"))
a = parser.parse_args()

with codecs.open(a.input, 'rb', "utf-8") as f:
    text = f.read()

with codecs.open(a.output, 'wb', "utf-8") as f:
    f.write(to_srt(text))
