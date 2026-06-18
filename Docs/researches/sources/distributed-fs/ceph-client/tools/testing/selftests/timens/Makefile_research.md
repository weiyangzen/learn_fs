# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/Makefile

## Purpose
Builds time namespace selftests and the extended `gettime_perf` benchmark.

## Important APIs, Types, and Functions
Sets `TEST_GEN_PROGS := timens timerfd timer clock_nanosleep procfs exec futex vfork_exec`, `TEST_GEN_PROGS_EXTENDED := gettime_perf`, `CFLAGS := -Wall -Werror -pthread`, `LDLIBS := -lrt -ldl`, and includes `../lib.mk`.

## Control Flow
Kselftest build compiles the listed programs with pthread, realtime, and dl dependencies. `gettime_perf` is marked extended rather than part of the default generated program set.

## State and Persistence Behavior
Only build outputs are produced. Runtime namespace/proc state is handled by individual tests.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, POSIX realtime library, pthreads, and dlopen support. Integrates with CONFIG_TIME_NS testing.

## Risks and Edge Cases
`-Werror` makes warnings build-breaking. Some tests require root/time namespace support at runtime even when compilation succeeds.

## Test Signals
Signals include successful build of all default time namespace tests and optional extended benchmark.
