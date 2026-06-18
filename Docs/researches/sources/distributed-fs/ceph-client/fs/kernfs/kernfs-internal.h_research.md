# sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h` is the private coordination header for kernfs implementation files. It defines root and superblock-private state, inode attribute storage, lock helpers, dentry/node helpers, revision helpers, and cross-file prototypes. The source was read as a complete 214-line file.

## Important APIs, Types, and Functions

Key types are `struct kernfs_iattrs`, `struct kernfs_root`, and `struct kernfs_super_info`. Important inline helpers include `kernfs_root`, `kernfs_root_is_locked`, `kernfs_rename_is_locked`, `kernfs_rcu_name`, `kernfs_parent`, `kernfs_dentry_node`, `kernfs_set_rev`, `kernfs_inc_rev`, and `kernfs_dir_changed`. The header declares `kernfs_sops`, global slab caches, directory/file/symlink operation tables, inode hooks, and open-file drain helpers.

## Control Flow

The header has no runtime flow by itself, but its inlines define the rules for traversing kernfs parent/name state. `kernfs_root` walks to a parent under RCU because non-root nodes derive root through their parent directory. `kernfs_parent` uses RCU with lockdep checks that allow dereference when the root rwsem, rename lock, or final node teardown makes the parent stable.

## State and Persistence Behavior

`kernfs_root` owns the inode IDR, root flags, syscall hooks, superblock list, deactivate wait queue, hierarchy rwsem, iattr rwsem, superblock rwsem, rename lock, and RCU lifetime. `kernfs_super_info` binds each superblock to one root and one namespace tag. `kernfs_iattrs` persists inode metadata and simple xattrs in the node.

## Dependencies and Integration Points

This header ties together `mount.c`, `inode.c`, `dir.c`, `file.c`, and `symlink.c`; it also exposes the hashed global lock table used by open-file state. It depends on public `<linux/kernfs.h>`, VFS, xattr, fs_context, mutex, rwsem, RCU, and lockdep APIs.

## Risks and Edge Cases

Incorrect parent/name dereference outside the documented locks can race with rename or reparenting. The root/superblock namespace model assumes a single namespace tag per superblock. Revision helpers are simple counters, so users must update them consistently on directory mutations to keep dcache validation reliable.

## Test Signals

Signals include lockdep/RCU-sched validation during rename, lookup, unmount, and notification; build coverage across all kernfs implementation files; namespace-mount tests that compare `kernfs_super_info` matching; and directory revalidation tests that depend on `dir.rev` and dentry `d_time`.
