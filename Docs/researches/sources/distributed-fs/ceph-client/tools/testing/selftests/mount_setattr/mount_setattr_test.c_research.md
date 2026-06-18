<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c

## Purpose
Large kselftest harness suite for the `mount_setattr()` and related modern mount APIs. It validates mount attribute changes, recursive behavior, writer rollback, propagation, namespace permissions, idmapped mount restrictions, `MOUNT_ATTR_NOSYMFOLLOW`, `open_tree_attr()`, detached mount trees, and anonymous mount namespace lifetime rules.

## Important APIs, Types, and Functions
- Syscall wrappers `sys_mount_setattr()` and `sys_open_tree_attr()` plus wrappers from `../filesystems/wrappers.h` for `open_tree`, `move_mount`, `fsopen`, `fsconfig`, and `fsmount`.
- Namespace helpers `create_and_enter_userns()` and `prepare_unpriv_mountns()`.
- Flag helpers `read_mnt_flags()` and `is_shared_mount()`.
- Fixture `mount_setattr` creates a layered `/mnt` and `/tmp` tree with tmpfs, ramfs, devpts, bind mounts, and symlink targets.
- Fixture `mount_setattr_idmapped` additionally creates an ext4 loop image and mount for idmapped mount tests.
- User namespace fd helpers `map_ids()`, `do_clone()`, `get_userns_fd()`, and `expected_uid_gid()` support idmap cases.

## Control Flow
The primary fixture enters an unprivileged user/mount namespace, makes `/` private, mounts controlled filesystems under `/tmp` and `/mnt`, creates nested bind mounts, and prepares symlink test data. Tests then call `mount_setattr()` with valid and invalid attribute structures, recursive and nonrecursive flags, writer-held mounts, mixed option trees, time policy transitions, multithreaded calls, wrong namespace contexts, and nosymfollow toggling. Detached mount tests clone trees with `open_tree`, attach them via `move_mount`, check mount-root and unique mount IDs with `statx`, and verify invalid namespace or subtree operations fail.

## State and Persistence Behavior
Most state is isolated in private user/mount namespaces. The idmapped fixture creates `/mnt/C/ext4.img`, formats it with `mkfs.ext4`, and loop-mounts it at `/mnt/D` inside the test namespace. Tests mutate mount flags, propagation groups, anonymous mount namespaces, detached tree fds, and idmap state. Fixture teardown detaches `/mnt/A` and `/tmp`, but many effects are namespace-scoped.

## Dependencies and Integration Points
Requires user namespaces, mount namespaces, tmpfs, ramfs, devpts, ext4 tooling (`mkfs.ext4`), loop mounting, modern mount syscalls, `statx` mount attributes, pthreads, and kselftest harness macros. It integrates directly with kernel mount API compatibility and permission semantics.

## Risks and Edge Cases
The suite is sensitive to kernel support; unsupported `mount_setattr` is skipped through `SKIP`/`XFAIL`. The idmapped fixture is heavier than most selftests because it creates and formats a 2 GiB sparse image. Recursive changes must be atomic on failure when writers exist; the tests explicitly check rollback. Namespace ownership, detached tree roots, and anonymous namespace lifetimes are subtle and heavily validated.

## Test Signals
Uses `TEST_F`/`ASSERT_*`/`EXPECT_*` kselftest harness output. Skips occur when syscalls are unsupported. Failures include mismatched flags, unexpected errno values, symlink traversal behavior, mount-root identity problems, idmap uid/gid mismatches, and invalid detached tree operations succeeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mount_setattr/mount_setattr_test.c -->
