# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-timer-lat.c

## Purpose
This latency test arms POSIX timers on all supported wall-time style clocks and checks that they do not fire early, have reasonable maximum latency, and one-shot timers fire exactly once.

## Important APIs, Types, and Functions
Key functions are `clockstring()`, `timespec_sub()`, `sigalarm()`, `setup_timer()`, `check_timer_latency()`, `check_alarmcount()`, `do_timer()`, and `do_timer_oneshot()`. It uses `timer_create()`, `timer_settime()`, `timer_delete()`, `clock_gettime()`, realtime signal `SIGRTMAX`, and `select()` for one-shot wait.

## Control Flow
`main()` installs a signal handler and iterates clock IDs up to `CLOCK_TAI`, skipping CPU, raw, coarse, and deprecated hardware-specific clocks. For each remaining clock, it runs periodic and one-shot timers in both absolute and relative modes. The signal handler computes the delta from expected expiry and records early fires and maximum latency.

## State and Persistence
Per-run state lives in globals `alarmcount`, `clock_id`, `start_time`, `max_latency_ns`, and `timer_fired_early`. Timers are deleted after each subtest. No persistent system state is changed.

## Dependencies and Integration Points
The test depends on Linux clock IDs, POSIX timer support, realtime signal delivery, and kselftest exit codes. Alarm clocks may require `CAP_WAKE_ALARM`; unsupported alarm timers are reported as unsupported and do not fail the run.

## Risks
The `UNRESONABLE_LATENCY` threshold is 40 ms, so heavily loaded or virtualized hosts can fail despite correct kernel behavior. Signal scheduling delays directly affect max latency. The test walks numeric clock IDs and relies on known skip cases.

## Test Signals
Pass requires no early signal and maximum latency below 40 ms for periodic and one-shot modes, plus exactly one signal for one-shot timers. Unsupported alarm timers are accepted as environment limitations.
