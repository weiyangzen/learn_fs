<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile

## Purpose
Builds the modern mount API selftest program `mount_setattr_test`.

## Important APIs, Types, and Functions
- `CFLAGS = -g $(KHDR_INCLUDES) -Wall -O2 -pthread`.
- Adds local header dependency `../filesystems/wrappers.h`.
- `TEST_GEN_PROGS := mount_setattr_test`.
- Includes `../lib.mk`.

## Control Flow
Kselftest builds the single harness-based test binary with pthread support and kernel header includes.

## State and Persistence Behavior
Only build artifacts are generated.

## Dependencies and Integration Points
Uses kselftest `lib.mk`, kernel headers, pthreads, and wrappers for modern filesystem/mount syscalls.

## Risks and Edge Cases
If kernel headers lack newer mount constants, the C file contains fallback definitions for many of them. Missing wrapper header would break the build.

## Test Signals
Build success creates `mount_setattr_test`; runtime results are emitted by the kselftest harness in the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/Makefile -->
