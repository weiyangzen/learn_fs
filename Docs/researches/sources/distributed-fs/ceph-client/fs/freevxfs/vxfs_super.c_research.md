# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_super.c` implements FreeVxFS module registration, mount context handling, superblock probing/filling, statfs, inode cache management, and unmount cleanup. The complete 347-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `vxfs_put_super()`, `vxfs_statfs()`, `vxfs_reconfigure()`, `vxfs_alloc_inode()`, `vxfs_free_inode()`, `vxfs_try_sb_magic()`, `vxfs_fill_super()`, `vxfs_get_tree()`, `vxfs_init_fs_context()`, `vxfs_init()`, and `vxfs_cleanup()`. Important objects are `vxfs_super_ops`, `vxfs_context_ops`, `vxfs_fs_type`, and `vxfs_inode_cachep`.

## Control Flow

Module init creates a usercopy-safe inode cache and registers filesystem type `vxfs`. Mount uses `get_tree_bdev()` to call `vxfs_fill_super()`, forces read-only, allocates `vxfs_sb_info`, sets an initial block size, probes little-endian UnixWare superblock at block 1 and big-endian HP-UX superblock at block 8, validates VxFS version 2-4, sets final block size, reads OLT, reads fileset headers, loads the root inode, and creates the root dentry. Reconfigure syncs and preserves read-only. Unmount drops pinned metadata inodes, releases the raw superblock buffer, and frees private info.

## State and Persistence Behavior

Runtime mount state is stored in `super_block` and `vxfs_sb_info`. The driver is read-only (`SB_RDONLY` forced), so it does not modify persistent VxFS data. Statfs reads free/block counters from the raw superblock.

## Dependencies and Integration Points

This file integrates with the VFS filesystem registry, fs_context API, block-device mount helper, buffer-head superblock reads, OLT/fileset/inode loaders, dentry root creation, slab cache lifecycle, module aliases, and RCU barrier cleanup before cache destruction.

## Risks and Edge Cases

Risks include incomplete cleanup on mount failure, limited superblock location/version support, trusting raw geometry values before deeper validation, usercopy cache range correctness for inline immediate data, and read-only enforcement during remount/reconfigure.

## Test Signals

Signals include module load/unload, mount valid little-endian and big-endian images, unsupported version rejection, wrong magic at both offsets, OLT/fileset failure cleanup under kmemleak, statfs output, forced read-only remount, and slab/RCU debug on module removal.
