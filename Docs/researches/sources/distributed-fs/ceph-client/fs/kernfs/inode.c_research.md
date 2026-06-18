# sources/distributed-fs/ceph-client/fs/kernfs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/inode.c` maps persistent `kernfs_node` metadata into VFS inodes. It handles inode allocation and eviction, attribute storage, permission/getattr/setattr, and trusted/security/user xattrs for kernfs-based filesystems. The source was read as a complete 406-line file.

## Important APIs, Types, and Functions

Important entry points are `kernfs_get_inode`, `kernfs_evict_inode`, `kernfs_iop_permission`, `kernfs_iop_setattr`, `kernfs_iop_getattr`, `kernfs_iop_listxattr`, `kernfs_setattr`, `__kernfs_setattr`, `kernfs_xattr_get`, and `kernfs_xattr_set`. The private attribute allocator `__kernfs_iattrs` lazily creates `struct kernfs_iattrs`, whose layout is declared in `kernfs-internal.h`. `kernfs_xattr_handlers` registers VFS xattr handlers.

## Control Flow

`kernfs_get_inode` uses `iget_locked` on `kernfs_ino(kn)` and initializes new inodes through `kernfs_init_inode`. Initialization pins the node, installs `ram_aops`, sets default timestamps, refreshes attributes, and then chooses directory, regular-file, or symlink operations. `setattr` and `getattr` take `root->kernfs_iattr_rwsem` so inode-visible attributes and persistent kernfs attributes stay coherent. Xattr handlers translate VFS prefix/suffix pairs into full names, lazily allocate simple xattr storage, and enforce user-xattr support only when the root opts in.

## State and Persistence Behavior

Metadata is persistent for the lifetime of the `kernfs_node`, not the transient inode. `kn->iattr` stores uid, gid, atime, mtime, ctime, xattrs, and xattr limits after first non-default use. Inode eviction truncates page cache, clears the inode, and drops the node reference taken during initialization.

## Dependencies and Integration Points

The file integrates with `kernfs_file_fops`, `kernfs_dir_iops`, `kernfs_dir_fops`, and `kernfs_symlink_iops`. It depends on `ram_aops` and `simple_inode_init_ts` from `libfs.c`, simple xattr helpers, VFS permission and setattr helpers, and root-level locks from `kernfs-internal.h`.

## Risks and Edge Cases

Lazy `kn->iattr` allocation can race, so `try_cmpxchg` correctness matters. Size changes are deliberately ignored in kernfs setattr. User xattrs must remain gated by `KERNFS_ROOT_SUPPORT_USER_XATTR`; otherwise pseudo filesystems could expose unexpected mutable metadata. Directory link counts depend on `kn->dir.subdirs` and must not be refreshed for removing nodes.

## Test Signals

Use inode lifetime tests around lookup/eviction, chmod/chown/timestamp tests across inode drop and relookup, xattr get/set/list tests for trusted/security/user prefixes, lockdep coverage for `kernfs_iattr_rwsem`, and sysfs/kernfs permission tests with and without user-xattr root support.
