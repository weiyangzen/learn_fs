# sources/distributed-fs/ceph-client/fs/jffs2/symlink.c

## Purpose

`symlink.c` defines the inode operations table for JFFS2 symbolic links. The actual symlink target data is cached during inode read; this file exposes the VFS operations needed to follow and manage symlink inodes.

## Important APIs, Types, And Functions

The sole exported object is `jffs2_symlink_inode_operations`. It assigns `.get_link = simple_get_link`, `.setattr = jffs2_setattr`, and `.listxattr = jffs2_listxattr`.

## Control Flow

When VFS operates on a JFFS2 symlink inode, link resolution calls `simple_get_link()`, which expects the inode's link string to have been set up in the inode state. Attribute changes route through JFFS2's setattr implementation, and xattr listing routes through the common JFFS2 xattr list function.

## State And Persistence Behavior

This file does not directly persist anything. Symlink target persistence is handled as inode data by write/read paths; `readinode.c` loads the target into `f->target`, and `super.c` frees it with the inode. Attribute changes through `.setattr` can persist metadata nodes through other JFFS2 code.

## Dependencies And Integration Points

It depends on `nodelist.h` for operation declarations and on Linux VFS symlink helpers. It integrates with `readinode.c` target caching, `fs.c` setattr/listxattr implementations, and `os-linux.h` declarations.

## Risks And Edge Cases

The correctness of `simple_get_link()` depends on the symlink target being cached and NUL-terminated elsewhere. Large or corrupt symlink targets are rejected in `readinode.c`, not here. The operation table is intentionally minimal, so missing behavior would surface as VFS-level symlink or xattr regressions.

## Test Signals

Tests should cover creating, reading, following, renaming, and deleting symlinks; listing xattrs on symlinks; changing symlink metadata; and corrupt/oversized target handling through inode read.
