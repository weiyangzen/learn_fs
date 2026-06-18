<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile

## Purpose
This kselftest Makefile builds the xattr socket test binaries.

## Important APIs, Types, And Functions
It appends `$(KHDR_INCLUDES)` to `CFLAGS`, declares `TEST_GEN_PROGS := xattr_socket_test xattr_sockfs_test xattr_socket_types_test`, and includes `../../lib.mk`.

## Control Flow
The kselftest build system compiles the three C harness tests and installs/runs them as generated test programs.

## State And Persistence
No runtime state is owned by the Makefile. It produces build artifacts under the kselftest output directory.

## Dependencies And Integration Points
It depends on kernel headers and kselftest `lib.mk`. The generated programs exercise VFS xattr behavior on Unix socket path inodes and sockfs inodes.

## Risks
Missing `KHDR_INCLUDES` or older headers can hide constants used by the tests. The Makefile has no per-test skip handling; runtime skip behavior lives in the binaries.

## Test Signals
Successful `make -C tools/testing/selftests/filesystems/xattr` and execution of all three generated binaries are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/Makefile -->
