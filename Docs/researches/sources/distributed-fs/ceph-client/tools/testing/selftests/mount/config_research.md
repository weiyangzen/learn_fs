<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config

## Purpose
Kernel configuration fragment for mount namespace selftests.

## Important APIs, Types, and Functions
- Requires `CONFIG_USER_NS=y`.

## Control Flow
No executable flow. Kselftest config tooling consumes it before running mount tests.

## State and Persistence Behavior
Static metadata only.

## Dependencies and Integration Points
Supports `nosymfollow-test.c` and `unprivileged-remount-test.c`, both of which create user namespaces.

## Risks and Edge Cases
If user namespaces are disabled by kernel config or runtime policy, wrappers skip or helpers fail during `unshare(CLONE_NEWUSER)`.

## Test Signals
None directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount/config -->
