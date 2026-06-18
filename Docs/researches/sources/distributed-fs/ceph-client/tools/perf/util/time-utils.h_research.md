# sources/distributed-fs/ceph-client/tools/perf/util/time-utils.h

## Purpose

`time-utils.h` declares time interval parsing, filtering, formatting, and monotonic clock helpers.

## Important APIs, Types, and Functions

It defines `struct perf_time_interval { u64 start, end; }`, declares all parser/filter/formatter functions from `time-utils.c`, and provides inline `rdclock()` using `clock_gettime(CLOCK_MONOTONIC)`.

## Control Flow and State

The header has no persistent state. `rdclock()` returns nanoseconds since the monotonic clock epoch and is used by synthetic duration events.

## Dependencies and Integration Points

It depends on Linux integer types and libc time. It is used by tool PMU duration counting and perf data time filtering.

## Risks and Test Signals

Callers must free arrays from `perf_time__range_alloc()` and understand that zero means unbounded for intervals. Build tests should validate availability of `CLOCK_MONOTONIC`.
