# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_i.h

## Purpose

This header defines SquashFS per-inode private state embedded around the VFS inode.

## Important APIs, Types, and Functions

`struct squashfs_inode_info` stores metadata start/offset, xattr location/count/size, parent inode number, and a union for regular-file fragment/block-list state or directory-index state. The inline `squashfs_i()` converts from `struct inode *` to the private container.

## Control Flow

There is no standalone control flow beyond `container_of` conversion. `inode.c` fills fields and other modules consume them during lookup, reads, readdir, xattr, and export parent lookup.

## State and Persistence Behavior

Instances persist for the lifetime of VFS inodes in the SquashFS inode slab cache. They cache decoded on-disk pointers, not writable filesystem metadata.

## Dependencies and Integration Points

Used by `super.c` inode allocation, `inode.c`, `file.c`, `dir.c`, `namei.c`, `export.c`, `symlink.c`, and `xattr.c`.

## Risks and Edge Cases

The union requires file and directory code to use fields only for the matching inode type. Parent defaults of 0 for non-directories matter for export parent lookup.

## Test Signals

Inode type coverage, export parent tests, xattr listing, directory index lookup, and regular file read tests validate field initialization and use.
