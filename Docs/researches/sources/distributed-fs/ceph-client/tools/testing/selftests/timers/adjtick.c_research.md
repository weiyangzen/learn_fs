# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/adjtick.c

## Purpose
Destructive timer test that adjusts the kernel tick length with `adjtimex(ADJ_TICK)` and verifies the measured monotonic-vs-raw drift matches the expected ppm shift.

## Important APIs, Types, and Functions
Uses global `systick`. Helpers are `llabs`, `ts_to_nsec`, `nsec_to_ts`, `diff_timespec`, `get_monotonic_and_raw`, `get_ppm_drift`, `check_tick_adj`, and `main`.

## Control Flow
`main()` checks `CLOCK_MONOTONIC_RAW`, computes the nominal tick from `_SC_CLK_TCK`, and iterates tick values across +/-10 percent. `check_tick_adj()` sets tick/frequency/status through `adjtimex`, waits, measures drift over 15 seconds, validates returned adjtimex values, compares expected and measured ppm within 100 ppm, and prints OK/FAILED. Finally it resets tick/frequency to nominal.

## State and Persistence Behavior
It modifies global kernel timekeeping discipline through `adjtimex`. It attempts to reset tick, offset, and frequency at the end, but interruption or failure can leave altered state.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, `CLOCK_MONOTONIC_RAW`, `CLOCK_MONOTONIC`, and kselftest. It integrates with kernel NTP/tick adjustment code.

## Risks and Edge Cases
The test is long-running and sensitive to NTP daemons, scheduler interruptions, and clocksource precision. It destructively changes system timekeeping and assumes it can restore state.

## Test Signals
Signals are per-tick OK lines with measured ppm close to expected, no unexpected adjtimex return values, and final kselftest pass after reset.
