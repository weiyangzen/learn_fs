# sources/distributed-fs/ceph-client/tools/perf/util/time-utils.c

## Purpose

`time-utils.c` parses, formats, and applies time ranges for perf data filtering. It supports absolute seconds.nanoseconds ranges, multiple ranges, percentage slices of recorded sample time, and relative ranges from the first sample.

## Important APIs, Types, and Functions

Key functions are `parse_nsec_time()`, `perf_time__parse_str()`, `perf_time__percent_parse_str()`, `perf_time__range_alloc()`, `perf_time__skip_sample()`, `perf_time__ranges_skip_sample()`, `perf_time__parse_for_ranges_reltime()`, `perf_time__parse_for_ranges()`, `timestamp__scnprintf_usec()`, `timestamp__scnprintf_nsec()`, and `fetch_current_timestamp()`. Internal helpers split `start,end`, parse `N%/slice`, parse `start%-end%`, convert percentages to nanosecond windows, and reject overlapping intervals.

## Control Flow and State

Parsing copies input strings before inserting terminators. Absolute ranges default missing start/end to zero. Multiple absolute ranges are comma separated and checked for non-overlap. Percentage ranges require session first/last sample timestamps; relative mode offsets parsed ranges by the first sample time. Skip helpers return false for missing timestamps and true only when a sample falls outside all selected intervals.

## Dependencies and Integration Points

It depends on `perf_session`, `evlist` first/last sample times, `debug` diagnostics, libc time functions, and Linux nanosecond constants. It integrates with report/script time filters and timestamp display.

## State and Persistence Behavior

The module keeps no global state. It allocates caller-owned interval arrays and writes formatted timestamps into caller buffers.

## Risks and Test Signals

Risks include off-by-one endpoints in percentage conversion, overlapping range rejection, invalid fractional nanoseconds over 9 digits, missing sample-boundary metadata, and relative ranges with zero endpoints. Tests should cover `1.2`, `1,2`, multiple intervals, invalid overlaps, `10%/2`, `0%-10%`, single `50%`, relative mode, formatting, and empty timestamp behavior.
