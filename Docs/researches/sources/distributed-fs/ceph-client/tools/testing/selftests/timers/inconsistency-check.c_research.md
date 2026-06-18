# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/inconsistency-check.c

## Purpose
Checks that repeated clock reads do not go backward or become inconsistent across supported clocks over a test duration.

## Important APIs, Types, and Functions
Defines `CLOCK_HWSPECIFIC` and `CALLS_PER_LOOP`. Important functions include `clockstring`, `in_order`, `consistency_test(clock_type, seconds)`, and `main`.

## Control Flow
`main()` prints a kselftest plan and iterates clock IDs, skipping unsupported or inappropriate clocks. `consistency_test()` repeatedly samples a clock for the requested duration and flags any out-of-order timestamps. Unsupported clocks are skipped.

## State and Persistence Behavior
No persistent state. It reads clocks only and keeps last/current timestamps in memory.

## Dependencies and Integration Points
Depends on POSIX clock APIs, kselftest, and optionally command-line duration. It integrates with generic timekeeping monotonicity validation and is also invoked by destructive meta-tests.

## Risks and Edge Cases
Virtualized or unstable clocksources can produce false failures. CPU time clocks and deprecated hardware-specific clock IDs need special handling. Very short or long durations alter detection sensitivity.

## Test Signals
Signals are pass/skip/fail results per clock, with failures indicating time moved backward or clock reads were inconsistent.
