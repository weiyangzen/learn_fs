<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile

## Purpose
Builds the uevent_filtering kselftest binary and registers it with the selftest harness.

## Important APIs, Types, and Functions
BINARIES, TEST_PROGS, EXTRA_CLEAN, CFLAGS, ../lib.mk.

## Control Flow
Declares uevent_filtering from uevent_filtering.c plus harness headers, adds no-as-needed/Wall flags, and includes the common selftest make rules.

## State and Persistence
No runtime state; build artifacts are cleaned through EXTRA_CLEAN.

## Dependencies and Integration Points
Depends on kselftest lib.mk and a C compiler/linker.

## Risks and Edge Cases
Architecture-independent but root/runtime namespace support is checked only by the binary.

## Test Signals
Successful build and kselftest execution of uevent_filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/Makefile -->
