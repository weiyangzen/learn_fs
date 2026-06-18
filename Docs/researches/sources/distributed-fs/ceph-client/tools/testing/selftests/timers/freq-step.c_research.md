# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/freq-step.c

## Purpose
Destructive precision test for kernel response to frequency steps made with `adjtimex()`. It measures `CLOCK_MONOTONIC` frequency error and stability relative to `CLOCK_MONOTONIC_RAW` after step changes.

## Important APIs, Types, and Functions
Defines `struct sample` and globals for bases, user HZ, precision, and raw frequency offset. Functions are `diff_timespec`, `get_sample`, `reset_ntp_error`, `set_frequency`, `regress`, `run_test`, `init_test`, and `main`.

## Control Flow
`init_test()` verifies raw and monotonic clocks, estimates sampling precision, skips if precision is too poor, seeds randomness, and calibrates raw frequency offset. `main()` runs multiple randomized frequency base/step combinations. `run_test()` sets a base frequency, resets NTP error, applies a step, samples 100 monotonic/raw offsets, performs linear regression on first and second halves, and fails if second-interval frequency error or standard deviation exceed thresholds. It resets frequency to zero at the end.

## State and Persistence Behavior
Modifies global timekeeping frequency and NTP error through `adjtimex`. Runtime samples are stack arrays. Cleanup resets frequency, but interruption can leave modified timekeeping.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, math library, monotonic/raw clocks, `sysconf(_SC_CLK_TCK)`, and kselftest. Integrates with kernel timekeeping frequency discipline.

## Risks and Edge Cases
Results are sensitive to CPU scheduling, virtualization, clocksource quality, and NTP interference. Randomized intervals can make failures hard to reproduce without logging seeds.

## Test Signals
Signals are acceptable sampling precision, printed frequency error/stddev/max rows marked OK, and final pass after resetting frequency.
