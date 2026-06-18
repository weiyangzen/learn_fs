# sources/distributed-fs/ceph-client/fs/qnx4/dir.c

## Purpose
`dir.c` implements QNX4 directory iteration.

## Important APIs, types, and functions
The main function is `qnx4_readdir`; exported operation tables are `qnx4_dir_operations` and `qnx4_dir_inode_operations`.

## Control flow
`qnx4_readdir` maps each directory file block through `qnx4_block_map`, reads the block, iterates fixed-size directory entries, extracts either direct inode names or link-entry names with `get_entry_fname`, computes inode numbers, and emits entries through `dir_emit`.

## State and persistence
Iteration state is `ctx->pos`. On-disk directories are read-only fixed-size entries; no mutations are performed.

## Dependencies and integration points
It depends on QNX4 inode extents, buffer-head reads, VFS dir context APIs, file lease helpers, and the shared directory-entry union in `qnx4.h`.

## Risks and test signals
Risks include invalid block maps, link-entry inode calculation, malformed status/name bytes, and returning success after read failures. Test signals include short and long link-style names, sparse/corrupt directory extents, interrupted `dir_emit`, and directory position resume.
