# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/clock_nanosleep.c

## Purpose
Tests `clock_nanosleep()` behavior inside a time namespace for relative and absolute sleeps across namespace-offset clocks.

## Important APIs, Types, and Functions
Uses `test_sig()` as a signal handler, `run_test(clockid, abs)` for one clock/mode, and `main()` to set up support checks and run cases. It includes `timens.h` and `log.h` for namespace helpers and kselftest logging.

## Control Flow
The program verifies time namespace support, unshares a new time namespace, applies offsets through `/proc/self/timens_offsets`, then runs `clock_nanosleep()` for selected clocks in relative and absolute modes. It checks that sleeps do not complete too early relative to the clock's offset behavior and reports kselftest results.

## State and Persistence Behavior
State is per-process namespace membership and offset entries in `/proc/self/timens_offsets`. No files are persisted. Signal state is process-local.

## Dependencies and Integration Points
Depends on `CLONE_NEWTIME`, `/proc/self/timens_offsets`, POSIX clock APIs, and kselftest helpers. Integrates with the shared skip logic in `timens.h`.

## Risks and Edge Cases
Requires privileges to unshare time namespaces. Alarm-clock and POSIX timer support may be unavailable and should be skipped. Timing tolerances can be affected by scheduler latency.

## Test Signals
Signals are kselftest pass/skip/fail lines for relative and absolute `clock_nanosleep` on supported clocks after applying namespace offsets.
