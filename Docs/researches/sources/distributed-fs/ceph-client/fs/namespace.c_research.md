# sources/distributed-fs/ceph-client/fs/namespace.c

## Purpose

`namespace.c` is the VFS mount and mount-namespace implementation. It owns mount allocation, mountpoint hashing, mount tree attachment and detachment, mount propagation, namespace cloning, legacy `mount(2)`/`umount(2)`, the newer file-descriptor mount API (`open_tree`, `fsmount`, `move_mount`, `mount_setattr`, `open_tree_attr`), mount namespace proc operations, and mount enumeration/stat APIs (`statmount`, `listmount`). Although this repository path is under a Ceph client source snapshot, this file is generic Linux VFS infrastructure that network filesystems such as CephFS depend on for mount lifecycle, visibility, write access accounting, and namespace isolation.

## Important APIs, Types, and Functions

Key global state includes `namespace_sem` for topology updates and enumeration, `mount_lock` as a seqlock for mount hash/topology readers and writers, `mount_hashtable` and `mountpoint_hashtable`, `mnt_id_xa` for legacy mount ids, `mnt_group_ida` for shared peer groups, and the global `event` counter used to signal namespace changes. `struct mount_kattr` is the internal representation for `mount_setattr()` and `open_tree_attr()`, carrying set/clear flags, propagation changes, recursive mode, and idmap replacement state.

Mount lifetime is managed by `alloc_vfsmnt()`, `free_vfsmnt()`, `mntget()`, `mntput()`, `mntput_no_expire()`, `cleanup_mnt()`, `mnt_make_shortterm()`, `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()`. Mount identity and propagation are handled by `mnt_alloc_id()`, `mnt_free_id()`, `mnt_alloc_group_id()`, `mnt_release_group_id()`, `invent_group_ids()`, `cleanup_group_ids()`, `change_mnt_propagation()` from `pnode.h`, and `vfsmount_to_propagation_flags()`.

Write access and read-only transitions are handled by `__mnt_is_readonly()`, `mnt_get_write_access()`, `mnt_want_write()`, file variants of those helpers, `mnt_put_write_access()`, `mnt_drop_write()`, `mnt_hold_writers()`, `mnt_unhold_writers()`, `mnt_make_readonly()`, and `sb_prepare_remount_readonly()`. These APIs are exported to filesystem code and are central to racing safely with remount-readonly and freezing.

Mountpoint and tree operations are centered on `get_mountpoint()`, `unpin_mountpoint()`, `mnt_set_mountpoint()`, `attach_mnt()`, `mnt_change_mountpoint()`, `commit_tree()`, `umount_tree()`, `attach_recursive_mnt()`, `graft_tree()`, `copy_tree()`, and `clone_private_mount()`. Namespace APIs include `alloc_mnt_ns()`, `copy_mnt_ns()`, `put_mnt_ns()`, `mount_subtree()`, `mntns_get()`, `mntns_put()`, and `mntns_install()`.

User-visible operations include `path_umount()`, `ksys_umount()`, `SYSCALL_DEFINE2(umount)`, legacy `oldumount`, `path_mount()`, `do_mount()`, `SYSCALL_DEFINE5(mount)`, `SYSCALL_DEFINE3(open_tree)`, `SYSCALL_DEFINE3(fsmount)`, `SYSCALL_DEFINE5(move_mount)`, `SYSCALL_DEFINE5(mount_setattr)`, `SYSCALL_DEFINE5(open_tree_attr)`, `SYSCALL_DEFINE4(statmount)`, `SYSCALL_DEFINE4(listmount)`, and `SYSCALL_DEFINE2(pivot_root)`.

## Control Flow

Mount creation through the legacy path begins in `mount(2)`, copies type/source/options from userspace, resolves the target path in `do_mount()`, and dispatches from `path_mount()` according to flags. Remounts go to `do_remount()` or `do_reconfigure_mnt()`, bind mounts to `do_loopback()`, propagation changes to `do_change_type()`, moves to `do_move_mount_old()`, and new filesystem mounts to `do_new_mount()`. `do_new_mount()` creates an `fs_context`, parses filesystem data, checks capabilities, obtains a `vfsmount` through `fc_mount()`, and attaches it with `do_new_mount_fc()` and `do_add_mount()`.

The fd-based API splits configuration from installation. `fsmount()` consumes an `fs_context` fd and creates a detached anonymous namespace-backed mount fd or a new namespace fd. `open_tree()` either opens an existing path, clones a detached tree, or builds a namespace containing the selected tree. `move_mount()` moves or installs trees using path/fd inputs and delegates to `vfs_move_mount()`, which either changes propagation-group membership or calls `do_move_mount()`. `mount_setattr()` builds `struct mount_kattr` from userspace, resolves the target, prepares writer holds and idmap state, then commits flags/idmaps/propagation changes.

Unmount starts at `path_umount()`, validates in `can_umount()`, and calls `do_umount()`. Forced unmount can call `sb->s_op->umount_begin`. Root unmount is converted into a readonly remount. Normal unmount takes `namespace_sem` and `mount_lock`, checks the mount is still valid and not locked, shrinks submounts, checks busy propagation, and calls `umount_tree()` with synchronous and propagation flags. Lazy detach uses `UMOUNT_PROPAGATE` without the synchronous busy check. `namespace_unlock()` later handles fsnotify, deferred mountpoint dentry shrinking, RCU synchronization, and final `mntput()`.

Tree attachment is deliberately two phase. `do_lock_mount()` or `lock_mount_exact()` pins a mountpoint and locks the target inode plus namespace. `attach_recursive_mnt()` then counts pending mounts, handles shared propagation through `propagate_mnt()`, moves a source tree out of its old parent or anonymous namespace, attaches the source and propagated copies, handles overmount replacement, updates namespace rbtrees through `commit_tree()`, and unwinds group ids and partial trees on failure.

Mount enumeration uses the namespace rbtree sorted by unique mount id. Proc mount iteration uses `mnt_find_id_at()` under `namespace_sem`. `statmount()` copies a `mnt_id_req`, resolves a mount namespace by id/fd/current namespace or a mount fd, builds fixed fields and strings in a retryable `seq_file` buffer, and copies a `struct statmount` plus string payload to userspace. `listmount()` resolves a namespace and root, verifies reachability/capability, walks the rbtree forward or backward, and returns matching child mount ids.

## State and Persistence Behavior

All state is in-kernel and memory-resident. Mounts carry per-mount flags, roots, parent/mountpoint pointers, namespace membership, propagation group ids, idmaps, expiry list entries, per-superblock mount linkage, and per-CPU ref/write counters. Namespaces carry a root mount, mount rbtree, mount count, passive/active references, user namespace ownership, ucounts charging, event counters, and poll waitqueues. No durable on-disk state is written by this file, but changes affect persistent VFS visibility and therefore filesystem access semantics.

Mount lifetime uses a combination of refcounts, RCU, task work, delayed work, and namespace references. Detached or unmounted mounts have `mnt_ns` cleared and are placed on `unmounted` until `namespace_unlock()` can run RCU cleanup. Long-term kernel mounts use `MNT_NS_INTERNAL` until explicitly made short-term. Anonymous mount namespaces are used as detached mount containers and can be dissolved on file release with `dissolve_on_fput()`.

Read-only and writer state uses per-CPU writer counters and `WRITE_HOLD` bits to make remount-readonly and mount attribute changes race safely with active writers. Mount ids are allocated from an xarray and unique 64-bit ids start above the 32-bit legacy range to avoid user ABI confusion.

## Dependencies and Integration Points

The file integrates with VFS path lookup, dcache, superblock management, fs contexts, idmapped mounts, user namespaces, proc namespace operations, sysctl, sysfs/kernfs/shmem/rootfs initialization, fsnotify, LSM hooks, pidfs/nsfs loop detection, pnode mount propagation, RCU, xarray/IDA, rbtrees, seq_file, uaccess, and task work. Filesystems interact through exported helpers such as `vfs_kern_mount()`, `kern_mount()`, `kern_unmount()`, `mnt_want_write()`, `mnt_drop_write()`, `clone_private_mount()`, `mount_subtree()`, `path_is_under()`, and mount namespace proc operations.

For CephFS and other network filesystems, the key integration points are superblock reconfiguration, mount option display (`show_options`, `show_devname`, `show_path`), write access/freeze protection, mount propagation into namespaces, idmapped mount permission checks through `FS_ALLOW_IDMAP`, and visibility restrictions in user namespaces through `mount_too_revealing()`.

## Risks and Edge Cases

The dominant risks are races among namespace topology changes, RCU path walking, final mount references, remount-readonly, and propagation. The code uses strict lock ordering (`inode_lock` before `namespace_sem`, `namespace_sem` before mount hash writes), seqlock retry loops, and memory barriers, but regressions here can produce use-after-free, leaked mounts, hidden writable mounts after readonly transitions, or namespace visibility bugs.

Security-sensitive checks include `CAP_SYS_ADMIN` in the relevant user namespace, locked mount flags that cannot be cleared, prevention of nsfs mount loops, restrictions on anonymous namespace origins, `mount_too_revealing()` for user namespaces, `mnt_may_suid()` for foreign mounts, idmapped mount restrictions, and LSM hooks for mount, umount, move, pivot, statfs, and option display. Errors here may expose covered directories, permit unsafe suid semantics, or allow namespace cycles.

Compatibility risk is high because the file implements legacy and modern mount ABIs. `statmount()` and `listmount()` must preserve id semantics, buffer sizing, restart behavior, reachability filtering, and permission behavior. The initial nullfs/rootfs layering also makes early boot assumptions visible to `pivot_root()` and namespace creation.

## Test Signals

Important signals include Linux VFS selftests for mount API behavior, namespace and idmapped mount tests, LTP mount/umount/pivot_root/unshare tests, fsnotify mount namespace notifications, `statmount`/`listmount` ABI tests with small and overflow buffers, syzkaller coverage for mount propagation and racing unmount, and filesystem-specific tests that use `mnt_want_write()`/`mnt_drop_write()` across remount-readonly and freeze. Runtime signals include `/proc/*/mountinfo`, `/proc/sys/fs/mount-max`, `statmount()` results, mount namespace poll events, and warnings from `VFS_WARN_ON_ONCE`, `WARN_ON_ONCE`, and timestamp expiry warnings.
