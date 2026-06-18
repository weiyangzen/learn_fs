# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fsmount_ns/fsmount_ns_test.c

## Purpose

`fsmount_ns_test.c` verifies that `fsmount(..., FSMOUNT_NAMESPACE, ...)` can create a mount namespace containing a configured tmpfs mount, expose a namespace id, allow `setns`, preserve mount attributes, and enforce capability/containment rules.

## Important APIs, Types, and Functions

Helpers include `get_mnt_ns_id`, `get_mnt_ns_id_from_path`, `log_mount`, `dump_mounts`, and `create_tmpfs_fd`. The tests use `sys_fsopen`, `sys_fsconfig`, `sys_fsmount`, `setns`, `ioctl(NS_GET_MNTNS_ID)`, `listmount`, `statmount`, `statmount_alloc`, `setup_userns`, `enter_userns`, `caps_down`, `umount2`, and kselftest fixtures/variants.

## Control Flow, State, and Persistence

The main fixture checks syscall availability and records the current mount namespace id. Variants exercise `FSMOUNT_NAMESPACE|FSMOUNT_CLOEXEC`, `FSMOUNT_CLOEXEC` alone, and namespace without cloexec. Core tests create a tmpfs fscontext, call `fsmount`, compare namespace ids, list mounts in the new namespace, and fork a child to enter it. Property tests inspect root mount metadata and fs type. Capability tests pre-create an fs fd, drop privileges in a child, and expect `EPERM`. Userns tests create namespaces with mapped privileges, create fsmount namespaces, setns into them, and verify locked mounts fail unmount with `EINVAL` while unshared private mount trees can be unmounted. Attribute tests assert `MOUNT_ATTR_RDONLY`, `NOEXEC`, `NOSUID`, `NOATIME`, and combined bits via statmount. State is held in fds, tmpfs fscontexts, and mount namespace objects.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are new mount API syscalls, nsfs mount namespace ids, statmount/listmount, user namespace helpers, and CAP_SYS_ADMIN behavior. It integrates with VFS mount namespace creation semantics and statmount namespace-aware queries. Risks include skipping on older kernels, user namespace restrictions, exact errno expectations, and cleanup relying on fd closure rather than mounted paths. Passing signals include different ns ids when expected, successful `setns`, tmpfs fs type visibility, correct mount count floor, `EPERM` after capability drop, expected `EINVAL` for locked unmounts, and visible mount attribute bits.
