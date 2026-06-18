# sources/distributed-fs/ceph-client/fs/qnx4/inode.c

## Purpose
`inode.c` registers and mounts the read-only QNX4 filesystem, validates the root/bitmap metadata, maps file extents, and instantiates VFS inodes.

## Important APIs, types, and functions
Important functions are `qnx4_fill_super`, `qnx4_checkroot`, `qnx4_iget`, `qnx4_block_map`, `try_extent`, `qnx4_get_block`, `qnx4_statfs`, `qnx4_kill_sb`, and inode cache lifecycle functions.

## Control flow
Mount allocates `qnx4_sb_info`, sets a 512-byte block size, reads block 1 as the superblock, validates the root directory and finds `.bitmap`, loads the root inode, and creates the root dentry. Block mapping first checks the inode's first extent, then follows extent blocks with signature `IamXblk`. `qnx4_iget` reads the raw inode entry, populates mode, ownership, timestamps, size, blocks, and assigns file, directory, or symlink operations.

## State and persistence
The driver is read-only. Runtime state includes the copied bitmap inode, inode cache entries, and raw inode data embedded in `qnx4_inode_info`.

## Dependencies and integration points
It depends on block devices, buffer heads, VFS fs_context/get_tree_bdev, generic block read/bmap helpers, slab inode cache, and QNX4 on-disk structures.

## Risks and test signals
Risks include leaks on early mount failure, extent-chain corruption, `qnx4_block_map` returning `-EIO` as an unsigned block, missing release of bad extent blocks, and strict root bitmap assumptions. Test signals include valid QNX4 images, corrupt root name, missing `.bitmap`, multi-extent files, symlink reads, statfs, remount read-only, and malformed inode modes.
