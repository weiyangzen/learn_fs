# sources/distributed-fs/ceph-client/fs/btrfs/xattr.h

## Purpose

`xattr.h` declares the Btrfs xattr interface shared by inode, VFS, security, and property code. It exposes the handler table installed on Btrfs inodes plus the direct get/set/list/security-init helpers implemented in `xattr.c`.

## Important APIs, Types, And Functions

The header forward declares `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`. `btrfs_xattr_handlers[]` is the VFS namespace handler table. `btrfs_getxattr()`, `btrfs_setxattr()`, `btrfs_setxattr_trans()`, and `btrfs_listxattr()` provide direct xattr operations. `btrfs_xattr_security_init()` initializes security xattrs during inode creation using an existing transaction handle.

## Control Flow And Integration

VFS inode setup references `btrfs_xattr_handlers[]`, while Btrfs create paths can call `btrfs_xattr_security_init()` after inode allocation. Internal callers with an existing transaction can use `btrfs_setxattr()` directly; generic VFS handler paths use `btrfs_setxattr_trans()` so transaction lifetime, inode ctime, and inode item update are handled consistently.

## State And Persistence Behavior

The header itself stores no state, but its API boundary controls whether callers supply a transaction or request transaction management. That distinction matters for persistence ordering, especially during inode creation when security xattrs must be inserted under the same transaction as the new inode.

## Dependencies

It depends only on Linux `types.h` and forward declarations, keeping compile-time coupling low. Implementations require `xattr.c`, transaction handling, dir-item storage, and VFS xattr infrastructure.

## Risks And Edge Cases

The main risk is using the wrong entry point: calling `btrfs_setxattr()` without a valid transaction violates its assertion, while starting a nested transaction during create/security hooks can disturb reserved block state. Prototype changes must remain synchronized with VFS handler expectations and security initialization call sites.

## Test Signals

Build coverage should catch prototype drift. Runtime signals come from security xattr initialization, VFS xattr handler registration, direct transaction callers, and xattr list/get/set/remove tests described for `xattr.c`.
