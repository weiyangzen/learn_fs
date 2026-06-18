# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nanosleep.c

## Purpose
Verifies `clock_nanosleep()` does not return before requested absolute or relative deadlines, and that interrupted sleeps report a sane remaining time.

## Important APIs, Types, and Functions
Defines `CLOCK_HWSPECIFIC` and `UNSUPPORTED`. Functions are `clockstring`, `in_order`, `timespec_add`, `nanosleep_test`, `dummy_event_handler`, `nanosleep_test_remaining`, and `main`.

## Control Flow
`main()` plans tests for clocks from `CLOCK_REALTIME` through `CLOCK_TAI`, skipping process/thread CPU and hardware-specific clocks. For each supported clock it runs absolute and relative sleeps from 10 ns to 10 seconds and fails on early return. It then arms a timer to interrupt a longer sleep and validates returned remaining time is between zero and requested duration.

## State and Persistence Behavior
No persistent state. Runtime state includes a temporary POSIX timer and SIGALRM handler, restored to default after the interrupted-sleep check.

## Dependencies and Integration Points
Depends on POSIX clocks, `clock_nanosleep`, POSIX timers, signal handling, and kselftest. Integrates with generic timer and sleep paths.

## Risks and Edge Cases
Unsupported clocks are skipped. The remaining-time test depends on signal delivery and `timer_create` support for the same clock. It treats early wakeups as hard failures but tolerates late wakeups.

## Test Signals
Signals are per-clock pass/skip lines, with immediate failure if any sleep returns before target or remaining time is invalid.
