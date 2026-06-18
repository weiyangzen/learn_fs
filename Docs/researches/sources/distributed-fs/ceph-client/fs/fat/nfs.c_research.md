# sources/distributed-fs/ceph-client/fs/fat/nfs.c

## Purpose
`nfs.c` implements FAT export operations for NFS. It provides normal export support based on VFS inode numbers and a `nostale_ro` mode that encodes stable directory-entry positions into file handles and can rebuild disconnected inodes.

## Important APIs, Types, and Functions
- `struct fat_fid` is the on-wire file handle layout for `nostale_ro`: inode generation, child `i_pos`, and optional parent `i_pos` and generation.
- `fat_dget()` looks up cached directory inodes by start cluster in `sbi->dir_hashtable`.
- `fat_ilookup()` chooses `fat_iget()` by `i_pos` for nostale mode or `ilookup()` by inode number for normal mode.
- `__fat_nfs_get_inode()` validates generation and, in nostale mode, can read the directory entry and build an inode if it is not already cached.
- `fat_encode_fh_nostale()`, `fat_fh_to_dentry_nostale()`, and `fat_fh_to_parent_nostale()` encode/decode stable handles.
- `fat_rebuild_parent()` and `fat_get_parent()` reconnect exported directories using `..` entries and logstart scans.

## Control Flow
Normal export delegates encoding and decoding mostly to generic helpers using 32-bit inode numbers. Nostale export encodes `i_pos` and generation into `fat_fid`; decode reconstructs `i_pos`, looks for an existing inode by directory-entry position, and if absent reads the directory entry block, rejects free/deleted entries, and calls `fat_build_inode()`.

Parent lookup reads the child's `..` entry. If the parent directory is in the directory hash, it returns that inode. In nostale mode, if the parent is not cached, `fat_rebuild_parent()` reads the parent cluster, builds a temporary grandparent from `..`, scans it for the parent's start cluster, and builds the real parent inode.

## State and Persistence
Normal NFS handles are vulnerable because FAT inode numbers are synthetic and can be stale after eviction/remount. Nostale mode persists identity through directory-entry position (`i_pos`) and generation, so `fat_fill_super()` forces read-only when `nfs=nostale_ro`. Directory hash state is populated by `fat_attach()` for directories when NFS support is enabled.

## Dependencies and Integration Points
This file depends on exportfs generic helpers, inode hash/dir hash maintenance from `inode.c`, directory scanning from `dir.c`, cluster start helpers from `fat.h`, and `fat_build_inode()`. Mount option handling in `inode.c` selects the export operation table.

## Risks and Test Signals
`i_pos` handles become invalid if directory entries move, which is why nostale mode is read-only. Rebuild depends on valid `.` and `..` entries and unique start clusters; corrupted directories or double-linked directories can break reconnect. NFS export tests should cover normal `stale_rw`, `nostale_ro` forcing read-only, file handle decode after eviction, parent reconnect, generation mismatch rejection, deleted-entry rejection, and corrupted dotdot entries.
