# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.h

## Purpose
Shared helper header for time namespace selftests.

## Important APIs, Types, and Functions
Defines `CLONE_NEWTIME` fallback, globals `config_posix_timers` and `config_alarm_timers`, and inline helpers `check_supported_timers`, `check_skip`, `unshare_timens`, `_settime`, `_gettime`, and `nscheck`.

## Control Flow
Tests include this header, call `nscheck()` and `check_supported_timers()`, create a namespace with `unshare_timens()`, write offsets through `_settime()`, read clocks through `_gettime()`, and skip unsupported clock cases through `check_skip()`.

## State and Persistence Behavior
The header owns per-translation-unit static booleans for timer feature availability. `_settime()` writes to `/proc/self/timens_offsets`, changing kernel namespace state.

## Dependencies and Integration Points
Depends on fcntl/unistd/stdlib/stdbool, kselftest, procfs time namespace files, clock APIs, and raw syscalls in includers. It integrates all timens tests with common skip and offset behavior.

## Risks and Edge Cases
Because globals are `static` in a header, each C file has its own copy, which is intended but notable. `_settime()` maps coarse/raw monotonic clocks to `CLOCK_MONOTONIC`; callers must understand shared offset semantics. `unshare_timens()` exits skip only on `EPERM`.

## Test Signals
Signals are consistent skip behavior for unsupported time namespaces, alarm timers, or POSIX timers, plus successful offset writes and clock reads.
