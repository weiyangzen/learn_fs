<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile

## Purpose
Builds the `move_mount_set_group_test` kselftest binary for `MOVE_MOUNT_SET_GROUP`.

## Important APIs, Types, and Functions
- `CFLAGS = -g $(KHDR_INCLUDES) -Wall -O2`.
- `TEST_GEN_FILES += move_mount_set_group_test`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles the single C helper and runs it as a generated test file.

## State and Persistence Behavior
Only build artifacts are created.

## Dependencies and Integration Points
Depends on kernel headers and kselftest `lib.mk`.

## Risks and Edge Cases
No pthread flag is needed here. Runtime support is checked inside the C test.

## Test Signals
Build success creates `move_mount_set_group_test`; runtime signals come from the harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/Makefile -->
