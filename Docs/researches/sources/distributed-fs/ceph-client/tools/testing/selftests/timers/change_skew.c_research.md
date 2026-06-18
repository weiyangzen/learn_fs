# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/change_skew.c

## Purpose
Destructive meta-test that changes kernel clock frequency skew and runs other timer tests to detect regressions under adjusted timekeeping.

## Important APIs, Types, and Functions
Functions are `change_skew_test(ppm)` and `main`. It uses `adjtimex(ADJ_FREQUENCY)`, `system("./raw_skew")`, `system("./inconsistency-check")`, and `system("./nanosleep")`.

## Control Flow
`main()` kills `ntpd`, clears offset adjustment, then iterates ppm values `{0, 250, 500, -250, -500}`. For each value, `change_skew_test()` applies frequency adjustment and runs the three companion tests, accumulating failures. At the end it resets frequency to zero and exits pass/fail.

## State and Persistence Behavior
It modifies global kernel frequency discipline and kills the `ntpd` process. It relies on cleanup to reset frequency, but abrupt termination can leave changed timekeeping.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, companion binaries in the current directory, shell `system()`, and kselftest. Integrates with NTP frequency adjustment and timer correctness tests.

## Risks and Edge Cases
Highly disruptive: kills NTP and changes global clock skew. It assumes current working directory contains required binaries. `system()` return aggregation loses detailed failure attribution.

## Test Signals
Signals are successful companion test runs under each ppm setting and final reset to zero frequency.
