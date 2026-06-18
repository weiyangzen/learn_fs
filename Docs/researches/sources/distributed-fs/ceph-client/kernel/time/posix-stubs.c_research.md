# sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c` provides minimal POSIX clock syscall support when `CONFIG_POSIX_TIMERS=n`. It preserves basic `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, and `CLOCK_BOOTTIME` behavior for settime/gettime/getres/nanosleep without supporting full POSIX timer objects. The complete 209-line source was read.

## Important APIs, Types, and Functions

The file defines native syscalls `clock_settime`, `clock_gettime`, `clock_getres`, and `clock_nanosleep`, plus compat 32-bit-time variants `clock_settime32`, `clock_gettime32`, `clock_getres_time32`, and `clock_nanosleep_time32` under `CONFIG_COMPAT_32BIT_TIME`. The main helper is `do_clock_gettime`, which switches among the supported clocks. It uses `struct timespec64`, `ktime_t`, restart-block nanosleep fields, and user-copy helpers.

## Control Flow

`clock_settime` accepts only `CLOCK_REALTIME`, copies a timespec from user space, and calls `do_sys_settimeofday64`. `clock_gettime` calls `do_clock_gettime`, which samples realtime, monotonic, or boottime and applies time namespace offsets for monotonic and boottime. `clock_getres` returns `hrtimer_resolution` for the same three clocks. `clock_nanosleep` validates the clock, copies and validates the requested time, disables remaining-time copyout for absolute sleeps, initializes the restart block, converts absolute time through `timens_ktime_to_host`, and delegates to `hrtimer_nanosleep`.

## State and Persistence Behavior

The file owns no persistent state. It mutates only the calling task's restart block for nanosleep restart/copyout behavior and relies on global timekeeping state for clock reads and realtime setting.

## Dependencies and Integration Points

Dependencies are the core timekeeping API, hrtimer nanosleep, time namespaces, syscall user-copy helpers, and compat timespec conversion helpers. This file substitutes for `posix-timers.c` when full POSIX timers are disabled, so unsupported clocks and all timer object operations fail elsewhere rather than being implemented here.

## Risks and Edge Cases

The deliberately small supported clock set is the main compatibility risk. `clock_getres` writes to `tp` unconditionally for valid clocks, unlike the full implementation which allows NULL for POSIX getres semantics. Absolute nanosleep must translate namespace-adjusted monotonic and boottime values to host time; missing that conversion would sleep until the wrong deadline in time namespaces.

## Test Signals

Build coverage with `CONFIG_POSIX_TIMERS=n`, syscall tests for the three supported clocks, negative tests for unsupported clocks, compat syscall coverage, namespace-aware absolute nanosleep tests, and realtime set permission/error tests are the strongest signals.
