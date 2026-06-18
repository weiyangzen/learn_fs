# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/raw_skew.c

## Purpose
This test estimates drift between `CLOCK_MONOTONIC` and `CLOCK_MONOTONIC_RAW` and compares that measured drift to the kernel frequency adjustment reported by `adjtimex()`. It validates that raw and disciplined monotonic clocks diverge consistently with the configured NTP frequency correction.

## Important APIs, Types, and Functions
Important helpers are `ts_to_nsec()`, `nsec_to_ts()`, `diff_timespec()`, and `get_monotonic_and_raw()`. The program uses `clock_gettime(CLOCK_MONOTONIC[_RAW])`, `adjtimex()`, `sleep(120)`, and VDSO nanosecond constants. `shift_right()` preserves signed right-shift behavior for scaled ppm conversion.

## Control Flow
`main()` verifies raw clock availability, samples `adjtimex()` and the initial monotonic/raw delta, sleeps for 120 seconds, samples again, computes estimated ppm from delta change over elapsed monotonic time, compares it with averaged `tx.freq`, and passes if the difference is within 1 ppm scaled as 1000 milli-ppm units. External time adjustment causes a skip when offsets, frequency, or tick values change.

## State and Persistence
There is no persistent state. The test samples kernel timekeeping state before and after a long interval and does not modify it.

## Dependencies and Integration Points
It depends on `CLOCK_MONOTONIC_RAW`, `adjtimex`, VDSO time constants, and kselftest exit codes. It is a long-running timers selftest intended to run where NTP or other time daemons are not actively changing frequency/offset during the sample.

## Risks
The 120 second runtime is expensive for automated suites. External time synchronization or offset correction makes the estimate unreliable and is treated as skip when detected. Short clock-read latency is mitigated by sampling three bracketing monotonic/raw reads and choosing the narrowest monotonic window.

## Test Signals
Pass means estimated monotonic/raw drift matches kernel frequency correction within tolerance. Skip means time was externally adjusted or counters were unavailable. Failure means raw/monotonic skew is inconsistent with `adjtimex` frequency state.
