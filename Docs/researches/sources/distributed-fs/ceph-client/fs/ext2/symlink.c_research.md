# sources/distributed-fs/ceph-client/fs/ext2/symlink.c

## Purpose

`fs/ext2/symlink.c` declares the inode operation tables used for ext2 symlinks. Modern symlink body handling is generic; this file only selects the correct `get_link` strategy for page-backed symlinks versus ext2 fast symlinks whose target is stored inline in the inode block array.

## Important APIs, types, and functions

- `ext2_symlink_inode_operations` uses `page_get_link` for normal symlinks whose content is in pagecache-backed file data.
- `ext2_fast_symlink_inode_operations` uses `simple_get_link` for fast symlinks where the target is available directly from inode-private memory.
- Both operation tables share `ext2_getattr`, `ext2_setattr`, and `ext2_listxattr`, so attribute changes and xattr listing behavior are consistent across both symlink storage forms.

## Control flow

The inode instantiation path in other ext2 code chooses one of these tables based on whether a symlink is fast or normal. VFS link resolution calls `.get_link`; generic code either obtains a page-backed target or returns the inline target. VFS stat and chmod/chown/truncate-style metadata operations flow to `ext2_getattr()` and `ext2_setattr()`, and listxattr delegates to ext2 xattr handling when compiled in.

## State and persistence behavior

This file does not write persistent state directly. Persistence is determined by the inode format chosen elsewhere: normal symlink target data is stored in data blocks/pages, while fast symlink bytes are stored inside ext2 inode block fields. Attribute and xattr persistence is delegated to ext2 inode and xattr code.

## Dependencies and integration points

The file includes `ext2.h` for ext2 inode attribute helpers and `xattr.h` for `ext2_listxattr`. Its exported constants are consumed by inode setup code that assigns `inode->i_op`.

## Risks and edge cases

Correctness depends on assigning the matching operation table to the matching on-disk symlink format. A fast symlink routed through `page_get_link` or a normal symlink routed through `simple_get_link` would expose wrong or missing link targets. Optional xattr support changes whether `.listxattr` is a real function or `NULL` through `xattr.h`.

## Test signals

Create and read short fast symlinks and longer block-backed symlinks, run `lstat`, `readlink`, `chmod/chown` where allowed, list xattrs on symlinks with xattrs enabled/disabled, and verify targets survive unmount/remount.
