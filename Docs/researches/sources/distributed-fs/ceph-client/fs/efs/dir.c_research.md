<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/dir.c -->
# sources/distributed-fs/ceph-client/fs/efs/dir.c

## Purpose
`dir.c` implements EFS directory iteration and directory inode/file operation tables.

## Important APIs, types, and functions
The exported tables are `efs_dir_operations` and `efs_dir_inode_operations`. The main function is `efs_readdir`, which emits entries from EFS directory blocks using `struct efs_dir` and `struct efs_dentry`.

## Control flow
`iterate_shared` computes the directory block and slot from `ctx->pos`, reads each mapped directory block through `sb_bread(inode->i_sb, efs_bmap(inode, block))`, validates the directory block magic, scans slot offsets, checks entry name bounds inside the block, and calls `dir_emit`. It advances `ctx->pos` by encoding block and slot. The inode ops only supply lookup through `efs_lookup`.

## State and persistence
EFS is read-only; no on-disk state is changed. Runtime state is the directory iteration position and buffer-head lifetime for each directory block.

## Dependencies and integration points
It depends on `efs_bmap` block mapping from `inode.c`, buffer-head reads, VFS directory iteration, file leasing helpers, and EFS on-disk directory layout macros from `efs.h`.

## Risks and test signals
Risks include malformed slot offsets, non-multiple directory sizes, invalid directory magic, truncated names, and block mapping failures. Test signals include readdir over multi-block directories, empty slots, corrupted directory images, long names near block boundaries, and interrupted or resumed `getdents` positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/dir.c -->
