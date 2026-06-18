<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config

## Purpose
Kernel configuration fragment for the `MOVE_MOUNT_SET_GROUP` selftest.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
No executable behavior.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports the C test's unprivileged namespace setup.

## Risks and Edge Cases
Kernel config does not guarantee the `MOVE_MOUNT_SET_GROUP` flag is implemented; the test probes that at runtime.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/config -->
