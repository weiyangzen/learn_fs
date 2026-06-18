<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/namei.c -->
# sources/distributed-fs/ceph-client/fs/efs/namei.c

## Purpose
`namei.c` implements EFS pathname lookup and exportfs helpers for NFS-style file handles and parent discovery.

## Important APIs, types, and functions
Important functions are `efs_find_entry`, `efs_lookup`, `efs_nfs_get_inode`, `efs_fh_to_dentry`, `efs_fh_to_parent`, and `efs_get_parent`.

## Control flow
Lookup scans each directory block using `efs_bmap` and `sb_bread`, validates directory block magic, iterates slots, compares name length and bytes, and returns the found inode number. `efs_lookup` converts that inode number into a VFS inode with `efs_iget` and splices aliases. Export helpers use `generic_fh_to_dentry`/`generic_fh_to_parent` with `efs_nfs_get_inode`, and `get_parent` looks up the `..` entry.

## State and persistence
No on-disk state changes occur. Runtime state includes transient buffer heads and dentry/inode cache results.

## Dependencies and integration points
It depends on EFS directory layout, buffer-head reads, `efs_iget`, exportfs, and VFS dentry aliasing. It is wired into directory inode operations and superblock export operations.

## Risks and test signals
Risks include missing boundary checks compared with readdir, corrupted directory slot offsets, bad magic, ESTALE generation checks, and parent lookup on damaged directories. Test signals include positive and negative lookups, NFS export handle decode, hard-linked aliases, `..` parent lookup, and corrupted directory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/namei.c -->
