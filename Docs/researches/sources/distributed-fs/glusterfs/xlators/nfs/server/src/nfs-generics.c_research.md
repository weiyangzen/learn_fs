<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c

## Purpose

`nfs-generics.c` provides the public generic NFS operation facade used by protocol handlers. Most functions validate common arguments and delegate either to low-level `nfs_fop_*` wrappers or higher-level inode-maintenance wrappers from `nfs-inodes.c`. Source read: complete 311-line file.

## Important APIs, Types, and Functions

The file implements `nfs_fstat`, `nfs_access`, `nfs_stat`, `nfs_readdirp`, `nfs_lookup`, `nfs_create`, `nfs_flush`, `nfs_mkdir`, `nfs_truncate`, `nfs_read`, `nfs_lk`, `nfs_getxattr`, `nfs_setxattr`, `nfs_fsync`, `nfs_write`, `nfs_open`, `nfs_rename`, `nfs_link`, `nfs_unlink`, `nfs_rmdir`, `nfs_mknod`, `nfs_readlink`, `nfs_symlink`, `nfs_setattr`, `nfs_statfs`, and `nfs_opendir`.

## Control Flow

Read-only or simple fd operations usually delegate directly to `nfs_fop_*`. Operations that create, link, rename, remove, or open path-based objects often call `nfs_inode_*` wrappers so inode table maintenance is handled before the protocol callback sees results. Validation failures return `-EFAULT`.

## State and Persistence Behavior

This file owns no state. It passes through `nfs_user_t`, `loc_t`, fd, iobref, and callback state to lower layers. State effects happen in `nfs-fops.c` and `nfs-inodes.c`.

## Dependencies and Integration Points

It depends on `nfs.h`, `nfs-fops.h`, `nfs-inodes.h`, and `nfs-generics.h`. It is the stable API layer used by MOUNT subdir resolution and NFS protocol implementations, allowing protocol code to avoid choosing between raw fop and inode-maintenance variants.

## Risks and Edge Cases

Validation is inconsistent: some wrappers require `nfsx`, while `nfs_truncate`, `nfs_unlink`, `nfs_read`, `nfs_lk`, `nfs_getxattr`, and `nfs_setxattr` do not check it even though lower layers may use it. The facade is thin, so behavioral differences between direct fop and inode-aware paths must stay intentional.

## Test Signals

Tests should exercise every public generic wrapper through protocol operations, especially create/open/link/rename/unlink paths where inode maintenance differs from raw fops. Static checks can catch signature drift between this file, `nfs-generics.h`, and `nfs-fops.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c -->
