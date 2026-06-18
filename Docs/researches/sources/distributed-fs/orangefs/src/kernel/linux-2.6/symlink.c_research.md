<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c

## Purpose
Defines inode operations for OrangeFS symlinks and adapts symlink-follow behavior across multiple Linux kernel `follow_link` APIs. The core behavior is to return or install `PVFS2_I(inode)->link_target` as the target path known from OrangeFS inode attributes.

## Important APIs, Types, and Functions
The file provides version-dependent `pvfs2_follow_link` implementations and the global `pvfs2_symlink_inode_operations`. The operations table wires `.readlink = generic_readlink`, `.follow_link = pvfs2_follow_link`, `.setattr = pvfs2_setattr`, `.getattr = pvfs2_getattr`, `.listxattr = pvfs2_listxattr`, and either `generic_setxattr` or `pvfs2_setxattr`. With generic ACL-capable xattrs it also installs `.permission = pvfs2_permission`.

## Control Flow
VFS symlink resolution calls `pvfs2_follow_link`. Older kernels return `vfs_follow_link(nd, link_target)`, intermediate kernels call `nd_set_link(nd, link_target)` and return `NULL`, and newer callback forms return `target` while storing it in `*cookie`. All paths read the cached link target from the OrangeFS inode-private structure and do not issue a new network request here.

## State and Persistence
No state is allocated in this file. It relies on inode-private `link_target` lifetime being valid for the symlink inode and populated by earlier getattr/lookup paths. The symlink target itself represents remote filesystem metadata cached in memory.

## Dependencies and Integration Points
Depends on `pvfs2-kernel.h`, `pvfs2-bufmap.h`, `pvfs2-internal.h`, the OrangeFS inode-private accessor `PVFS2_I`, generic VFS readlink helpers, attribute callbacks, xattr callbacks, and optional permission handling.

## Risks
The implementation trusts `link_target` to be non-NULL and properly NUL-terminated. Stale or freed targets would surface as bad path resolution. Behavior differs by kernel API, so compatibility macro coverage matters. The symlink operations table does not define `.get_link` for modern kernels, indicating this file targets old 2.6-era compatibility layers.

## Test Signals
Create and read symlinks with short, long, relative, and absolute targets; resolve symlinks after inode cache eviction; verify xattr and setattr callbacks on symlink inodes; and compile-test all supported `follow_link` macro branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/symlink.c -->
