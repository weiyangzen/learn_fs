# sources/compression/zstd/programs/timefn.c

## Purpose

This file implements cross-platform monotonic or best-available high-resolution timing helpers for zstd benchmarks, progress refreshes, and tracing.

## Important APIs, Types, and Functions

`UTIL_getTime()` has platform-specific implementations: Windows `QueryPerformanceCounter`, macOS `mach_absolute_time`, POSIX `clock_gettime(CLOCK_MONOTONIC)`, C11 `timespec_get`, or C90 `clock()` fallback. Common helpers are `UTIL_getSpanTimeNano()`, `UTIL_getSpanTimeMicro()`, `UTIL_clockSpanMicro()`, `UTIL_clockSpanNano()`, `UTIL_waitForNextTick()`, and `UTIL_support_MT_measurements()`.

## Control Flow, State, and Persistence

Windows and macOS paths lazily cache conversion factors in static variables. Span helpers subtract opaque nanosecond counters. `UTIL_waitForNextTick()` busy-waits until clock resolution advances. The fallback `clock()` path marks multi-threaded measurements unsupported.

## Dependencies and Integration Points

It includes `timefn.h` and `platform.h`, plus platform timing headers. `fileio_common.h`, benchmark code, and `zstdcli_trace.c` use these helpers.

## Risks and Test Signals

Clock APIs abort on unexpected failures. Busy-waiting can cost CPU, and `clock()` measures process CPU time rather than wall time. Tests should validate monotonic spans, nonzero tick waits, `UTIL_support_MT_measurements()` by platform, and benchmark stability on Windows/macOS/Linux/C11 fallback builds.
