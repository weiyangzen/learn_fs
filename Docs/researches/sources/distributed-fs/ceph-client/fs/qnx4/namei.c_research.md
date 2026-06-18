# sources/distributed-fs/ceph-client/fs/qnx4/namei.c

## Purpose
`namei.c` implements QNX4 pathname lookup inside directories.

## Important APIs, types, and functions
Important functions are `qnx4_lookup`, `qnx4_find_entry`, and `qnx4_match`.

## Control flow
Lookup scans the directory block by block using `qnx4_block_map`, compares fixed-size entries with the requested name, handles link entries by resolving the real inode block/index, releases the directory buffer, and returns `d_splice_alias(qnx4_iget(...), dentry)`.

## State and persistence
It reads directory entries only; no dcache-persistent state beyond normal VFS aliasing is created.

## Dependencies and integration points
It depends on QNX4 directory-entry status interpretation from `qnx4.h`, buffer-head reads, VFS dentry lookup, and inode instantiation in `qnx4_iget`.

## Risks and test signals
Risks include entry offset arithmetic, linked-entry inode conversion, malformed names/status bytes, and skipped unreadable blocks hiding entries. Test signals include direct and linked entries, missing names, corrupt blocks, maximum-length names, and lookup/dcache alias behavior.
