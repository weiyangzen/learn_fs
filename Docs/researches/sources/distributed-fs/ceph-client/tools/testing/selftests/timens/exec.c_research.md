# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/exec.c

## Purpose
Tests that time namespace offsets survive an `exec` boundary and are visible in the executed program.

## Important APIs, Types, and Functions
Contains `main()` using helpers from `timens.h` and kselftest logging. It uses `unshare_timens()`, `_settime()`, `clock_gettime()`, and `exec`-style process replacement.

## Control Flow
The program checks namespace support, creates a child time namespace or detects an execed mode via arguments, sets offsets, then executes itself or a helper path to validate that the new image observes the expected shifted clock values.

## State and Persistence Behavior
Time namespace offsets are stored by the kernel for the namespace and should persist across `exec`. No external files are written.

## Dependencies and Integration Points
Depends on `CLONE_NEWTIME`, procfs timens offsets, `execve`, clock APIs, and shared timens helpers.

## Risks and Edge Cases
Exec argument handling must distinguish parent and execed phases correctly. Privilege failures should skip rather than look like clock regressions. Timing comparisons need tolerance for elapsed time during exec.

## Test Signals
Signals are successful observation of expected offsets after exec and kselftest skip on unsupported or unprivileged systems.
