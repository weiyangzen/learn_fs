# sources/distributed-fs/ceph-client/fs/qnx6/inode.c

## Purpose
`inode.c` registers and mounts the read-only QNX6 filesystem, validates mirrored superblocks, maps indirect block trees, and instantiates VFS inodes.

## Important APIs, types, and functions
Key functions are `qnx6_fill_super`, `qnx6_check_first_superblock`, `qnx6_private_inode`, `qnx6_iget`, `qnx6_block_map`, `qnx6_get_block`, `qnx6_checkroot`, `qnx6_statfs`, `qnx6_parse_param`, and inode cache lifecycle functions.

## Control flow
Mount allocates `qnx6_sb_info`, parses the optional `mmi_fs` flag, reads/checks the active superblock pair, selects the highest serial, sets the real block size and block offset, verifies indirect depth, creates private inodes for the inode table and longfile, instantiates the root inode, and validates `.`/`..`. File block mapping uses direct root pointers plus up to `di_filelevels` of indirect pointer blocks.

## State and persistence
The driver is read-only. Runtime state includes active superblock buffer, endian setting, block offset, pointer-bit width, private inodes, and per-inode direct pointers/file levels.

## Dependencies and integration points
It depends on block devices, CRC32, buffer heads, folios/mpage, VFS fs_context, QNX6 endian wrappers, and optional MMI superblock handling.

## Risks and test signals
Risks include stale `sb1` use after MMI path, unreleased buffer heads on some error paths, indirect pointer corruption, endian detection gaps, block offset mistakes, and unsupported write semantics. Test signals include little- and big-endian images, bootblock and no-bootblock layouts, mirrored superblock serial selection, MMI mount option, deep indirect files, symlinks/special inodes, statfs, and corrupt CRCs.
