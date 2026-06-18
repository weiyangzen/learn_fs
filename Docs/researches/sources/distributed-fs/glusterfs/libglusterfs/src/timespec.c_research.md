# sources/distributed-fs/glusterfs/libglusterfs/src/timespec.c

## Purpose

`timespec.c` provides portable time helpers for monotonic, realtime, and raw monotonic timestamps plus simple arithmetic and comparison operations used by timers, latency measurement, and scheduling.

## Important APIs, Types, and Functions

The exported functions are `timespec_now()`, `timespec_now_realtime()`, `timespec_now_monotonic_raw()`, `timespec_adjust_delta()`, `timespec_sub()`, and `timespec_cmp()`. Darwin builds use `mach_absolute_time()` and `mach_timebase_info`; Linux/Solaris/BSD builds use `clock_gettime()` with fallbacks.

## Control Flow and Data Flow

`timespec_now()` prefers `CLOCK_MONOTONIC`, falls back to `gettimeofday()`, and aborts if both fail on supported POSIX platforms. Darwin converts mach absolute time using the mach timebase. `timespec_now_realtime()` prefers `CLOCK_REALTIME` then falls back to `gettimeofday()`. `timespec_now_monotonic_raw()` uses Linux `CLOCK_MONOTONIC_RAW` when available and otherwise delegates to monotonic time. Arithmetic functions adjust or subtract nanosecond fields and compare seconds then nanoseconds.

## State and Persistence Behavior

The functions do not persist state except Darwin's static timebase/scaling values. Returned timestamps are caller-owned values. Monotonic timestamps are suitable for intervals; realtime timestamps reflect wall-clock changes.

## Dependencies and Integration Points

The file depends on platform time APIs, `glusterfs/timespec.h`, common utilities for abort, and message definitions. It integrates with `timer.c`, `stack.c` latency metadata, statedump formatting, and any subsystem needing interval measurement.

## Risks and Edge Cases

`timespec_adjust_delta()` updates `tv_nsec` before computing carry from the original plus delta expression, which can produce incorrect carry for some inputs because the expression is recomputed after modulo. Darwin conversion in the observed code appears suspicious because it assigns seconds and nanoseconds from a scaled nanosecond value with `NANO`/`GIGA` macros, so platform tests are important. Realtime waits can be affected by wall-clock changes, whereas timer condvars use monotonic clock attributes elsewhere.

## Test Signals

Tests should cover nanosecond carry and borrow, comparison equality and ordering, monotonic nondecreasing behavior, realtime fallback behavior under mocked failures, raw monotonic fallback, and platform-specific Darwin conversion. Timer integration tests can catch arithmetic errors in scheduled deadlines.
