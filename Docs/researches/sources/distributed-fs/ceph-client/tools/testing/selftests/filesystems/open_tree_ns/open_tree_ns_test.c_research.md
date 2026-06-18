# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/open_tree_ns_test.c

## Purpose

`open_tree_ns_test.c` verifies that `open_tree(..., OPEN_TREE_NAMESPACE, ...)` creates a mount namespace containing a selected mount tree, handles recursive and unbindable cases, and enforces namespace/capability containment rules.

## Important APIs, Types, and Functions

Helpers mirror the fsmount namespace test: `get_mnt_ns_id`, `get_mnt_ns_id_from_path`, `log_mount`, and `dump_mounts`. Fixtures cover basic variants, capability checks, user namespace behavior, and unbindable mounts. APIs include `sys_open_tree`, `ioctl(NS_GET_MNTNS_ID)`, `listmount`, `statmount_alloc`, `setns`, `enter_userns`, `caps_down`, `umount2`, `mount`, and `mkdtemp`.

## Control Flow, State, and Persistence

Basic variants call `open_tree` on `/`, `/tmp`, `/proc`, or `/run` with `OPEN_TREE_NAMESPACE`, optional `AT_RECURSIVE`, and cloexec, expecting a new namespace id and at least one visible mount. A negative variant with `AT_RECURSIVE` but no namespace flag expects `EINVAL`. Setns and property tests verify entering the returned namespace and root mount metadata. Capability tests drop privileges and expect `EPERM`. User namespace tests create namespaces, open trees inside them, setns from an inner child, verify recursive copies, and compare locked mount unmount failure (`EINVAL`) with private unshared tree unmount success. Unbindable tests require direct namespace open on an unbindable mount to fail and recursive root copy to omit the unbindable mount. State is the returned namespace fd and copied mount trees.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include `OPEN_TREE_NAMESPACE`, statmount/listmount, user namespaces, mount propagation, and CAP_SYS_ADMIN. It integrates with VFS open_tree clone/copy semantics and namespace containment. Risks are path assumptions for `/run` and `/proc`, older kernels skipping, userns restrictions, and exact unbindable filtering. Passing signals are different ns ids, successful `setns`, expected `EINVAL` or `EPERM`, visible mount count floors, locked unmount behavior, and absence of the unbindable mount from recursive results.
