<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config

## Purpose
Kernel configuration fragment for `mount_setattr` selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
Static configuration metadata only.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Supports the test binary's repeated use of unprivileged user namespaces and mount namespaces.

## Risks and Edge Cases
Runtime policy can still disable unprivileged user namespaces even if the config symbol exists.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/config -->
