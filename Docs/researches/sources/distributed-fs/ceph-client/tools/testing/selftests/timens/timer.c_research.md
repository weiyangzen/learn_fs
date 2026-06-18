# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timer.c

## Purpose
Tests POSIX timer expiration behavior under time namespace offsets.

## Important APIs, Types, and Functions
Core function is `run_test(clockid, now)`, with `main()` setting up namespace and iterating supported clocks. Uses `timer_create`, `timer_settime`, `clock_gettime`, and shared timens helpers.

## Control Flow
The test creates or enters a time namespace, sets offsets, gets current time, arms timers for selected clocks, waits for expiration or signal delivery, and verifies timers fire according to namespace-adjusted time rather than host time.

## State and Persistence Behavior
Runtime state includes POSIX timer IDs, signal/timer state, and namespace offsets. No persistent files are created.

## Dependencies and Integration Points
Depends on POSIX timers, supported clock IDs, `CLONE_NEWTIME`, procfs offset writes, and kselftest. Integrates with kernel timer namespace offset handling.

## Risks and Edge Cases
POSIX timers may be unavailable when `CONFIG_POSIX_TIMERS` is off, requiring skips. Timer delivery can be delayed by scheduling, so tests should detect early/wrong-clock behavior more strictly than late behavior.

## Test Signals
Signals are kselftest pass/skip/fail outcomes for timer expiration on each supported clock.
