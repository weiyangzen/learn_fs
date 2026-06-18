# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/leap-a-day.c

## Purpose
Destructive leap-second stress test. It repeatedly schedules insert/delete leap seconds, optionally sets the system time near midnight UTC, and checks timer/NTP state around the leap boundary.

## Important APIs, Types, and Functions
Globals are `next_leap` and `error_found`. Functions include `in_order`, `timespec_add`, `time_state_str`, `clear_time_state`, `handler`, `sigalarm`, `test_hrtimer_failure`, and `main`.

## Control Flow
`main()` parses options for wait mode, iterations, and TAI printing; validates `CLOCK_TAI` when requested; installs handlers; then loops. Each iteration computes next midnight, optionally uses `settimeofday()` to move to ten seconds before it, clears NTP state, sets `STA_INS` or `STA_DEL`, arms a realtime timer for the leap moment, sleeps to just before the leap, repeatedly prints `adjtimex` state through the boundary, checks for early hrtimer expiry, toggles insert/delete mode, and exits after the requested iterations. Cleanup clears time state.

## State and Persistence Behavior
It modifies global wall clock time, NTP leap status, TAI/leap state, and POSIX timers. It tries to clear state on normal exit and SIGINT, but it cannot catch SIGKILL despite registering a handler call.

## Dependencies and Integration Points
Depends on root privileges, `adjtimex`, `settimeofday`, POSIX timers, realtime clock, optional `CLOCK_TAI`, and kselftest. Integrates with kernel leap-second state machine and hrtimer behavior.

## Risks and Edge Cases
Very disruptive: changes system time by days in default mode. NTP daemons can conflict. Signal registration for SIGKILL is ineffective. Option string in source includes `s` but switch handles `w`, indicating documentation/parser drift.

## Test Signals
Signals include correct `TIME_WAIT` observation at the leap, no early timer expiration, no hrtimer failure, and cleanup of NTP state before pass.
