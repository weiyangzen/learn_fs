# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leapcrash.c

## Purpose
Destructive regression/demo test for historical leap-second deadlocks. It repeatedly sets the system near a leap second and hammers `adjtimex(STA_INS)` through the boundary.

## Important APIs, Types, and Functions
Functions are `clear_time_state`, `handler`, and `main`. It uses `clock_gettime`, `settimeofday`, `adjtimex`, signal handling, and kselftest exits.

## Control Flow
`main()` clears NTP time state, computes next midnight, then loops 20 times. Each loop sets wall time to two seconds before the leap, calls `adjtimex`, repeatedly sets `STA_INS` until after the leap second, clears time state, and prints progress. Permission failures from `settimeofday` fail the test.

## State and Persistence Behavior
It modifies global wall clock time and NTP leap status. It attempts cleanup on SIGINT and normal loop completion, but abrupt termination can leave time state changed.

## Dependencies and Integration Points
Depends on root privileges, realtime clock, `settimeofday`, `adjtimex`, and kselftest. Integrates with leap-second handling and NTP state transitions.

## Risks and Edge Cases
The source warning notes possible hard hangs and data loss on affected kernels. It is destructive and should only run in controlled environments. SIGKILL cannot actually be handled.

## Test Signals
Signals are completion of 20 boundary-hammer loops, printed progress dots, cleanup of time state, and kselftest pass without hang.
