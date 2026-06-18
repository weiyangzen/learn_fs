<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c

## Purpose
Kselftest for `move_mount(..., MOVE_MOUNT_SET_GROUP)`, validating that sharing/propagation group state can be copied from one mount to another across nested namespace scenarios.

## Important APIs, Types, and Functions
- Namespace helpers `create_and_enter_userns()` and `prepare_unpriv_mountns()`.
- `is_shared_mount()` parses `/proc/self/mountinfo` to detect a `shared:` propagation tag for a path.
- `move_mount_set_group_supported()` builds a temporary mount setup and probes `__NR_move_mount` with `MOVE_MOUNT_SET_GROUP`.
- `get_nestedns_mount_cb()` creates a nested unprivileged mount namespace, optionally marks a mount shared, and returns user/mount namespace fds and a mount fd through shared clone memory.
- `complex_sharing_copying` is the core harness test.

## Control Flow
Fixture setup enters an unprivileged private mount namespace, probes support, remounts `/tmp`, and mounts tmpfs at `/tmp/A`. The test creates two cloned child contexts sharing memory/files: one with `/tmp/A` marked shared and one private. It then calls `move_mount` with source and target empty-path fds plus `MOVE_MOUNT_SET_GROUP`, enters the target mount namespace, and verifies `/tmp/A` is shared there.

## State and Persistence Behavior
All mount changes are namespace-local. The test opens namespace and mount fds from child contexts and uses them after the child exits. It detaches `/tmp` in fixture teardown.

## Dependencies and Integration Points
Requires user/mount namespaces, tmpfs, `move_mount` syscall, `MOVE_MOUNT_SET_GROUP`, `setns`, clone with `CLONE_VFORK | CLONE_VM | CLONE_FILES`, and kselftest harness.

## Risks and Edge Cases
Runtime flag support is not assumed. Passing fds through clone-shared memory is concise but sensitive to clone flags and child completion. The test validates propagation through mountinfo parsing, which depends on stable mountinfo optional field formatting.

## Test Signals
Unsupported flag is skipped/XFAIL. Assertions validate setup, syscall success, namespace switch, and final shared propagation state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/move_mount_set_group/move_mount_set_group_test.c -->
