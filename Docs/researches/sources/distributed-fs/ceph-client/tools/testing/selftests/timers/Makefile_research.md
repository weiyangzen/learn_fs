# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/Makefile

## Purpose
Builds the general kernel timer selftests and separates safe default tests from destructive time-changing tests.

## Important APIs, Types, and Functions
Sets `CFLAGS += -O3 -Wl,-no-as-needed -Wall -I $(top_srcdir)` and `LDLIBS += -lrt -lpthread -lm`. `TEST_GEN_PROGS` includes safe tests such as `posix_timers`, `nanosleep`, `nsleep-lat`, `mqueue-lat`, `inconsistency-check`, `raw_skew`, `threadtest`, and `rtcpie`. `DESTRUCTIVE_TESTS` includes `alarmtimer-suspend`, `valid-adjtimex`, `adjtick`, `change_skew`, `skew_consistency`, `clocksource-switch`, `freq-step`, `leap-a-day`, `leapcrash`, `set-tai`, `set-2038`, and `set-tz`. `TEST_GEN_PROGS_EXTENDED` is set to destructive tests.

## Control Flow
Default kselftest builds safe programs and extended destructive programs. The `run_destructive_tests` target first runs default tests, then invokes `RUN_TESTS` for destructive tests.

## State and Persistence Behavior
Build outputs are test binaries. Destructive runtime state can include system time, NTP state, clocksource selection, suspend state, and timezone/TAI settings, but those are controlled by individual tests.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, realtime library, pthreads, math library, and top source includes. Integrates with generic timers selftest execution.

## Risks and Edge Cases
The Makefile explicitly distinguishes tests that modify global system state or trigger suspend. Running `run_destructive_tests` on shared machines can disrupt timekeeping or power state.

## Test Signals
Signals include successful compilation of safe and extended tests and deliberate opt-in execution of destructive tests.
