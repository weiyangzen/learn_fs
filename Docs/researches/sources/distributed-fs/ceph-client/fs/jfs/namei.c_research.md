<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/jfs/namei.c

## Purpose
`namei.c` implements JFS VFS namespace operations: create, mkdir, unlink, rmdir, link, symlink, rename, mknod, lookup, NFS filehandle recovery, directory file operations, and optional case-insensitive dentry operations for OS/2-compatible mounts.

## Important APIs, types, and functions
The VFS entry points are installed through `jfs_dir_inode_operations`, `jfs_dir_operations`, and `jfs_ci_dentry_operations`. Major functions include `jfs_create`, `jfs_mkdir`, `jfs_rmdir`, `jfs_unlink`, `jfs_link`, `jfs_symlink`, `jfs_rename`, `jfs_mknod`, `jfs_lookup`, `jfs_fh_to_dentry`, `jfs_fh_to_parent`, and `jfs_get_parent`. Resource cleanup is split through `commitZeroLink`, `jfs_free_zero_link`, and `free_ea_wmap`.

## Control flow
Creation paths initialize quota, convert dentries to JFS Unicode component names, allocate inodes before directory search to avoid blocking with dtree pages pinned, start a transaction, lock parent/child commit mutexes, initialize ACL/security xattrs, initialize an xtree or dtree root, insert a directory entry with `dtInsert`, set VFS operations, dirty inodes, and commit. Removal paths delete dtree entries, adjust link counts and timestamps, free EA/ACL extents, and commit delete metadata. For unlinked regular files and long symlinks, `commitZeroLink` starts persistent-map truncation; callers then loop with `xtTruncate_pmap` and synchronous commits until the bounded truncation completes.

`jfs_symlink` stores short targets in the inode inline area and long targets in a single xtree extent written through metapages. `jfs_rename` validates source and destination inumbers before the transaction, supports only `RENAME_NOREPLACE`, updates or inserts the destination, removes the old entry, adjusts directory link counts and `..` for cross-directory moves, and handles victim zero-link truncation like unlink. Lookup resolves `dtSearch` results to inodes via `jfs_iget` and returns `d_splice_alias`.

## State and persistence behavior
Persistent updates include directory dtree entries, inode allocation records, link counts, timestamps, inline symlink data, xtree-backed symlink data, EA/ACL descriptors, and deleted-file pmap truncation records. Runtime state includes transaction ids, commit mutex ordering, JFS component-name buffers, VFS dentries, IWRITE locks for unlink/rename victims, and cflags such as `COMMIT_Nolink`, `COMMIT_Freewmap`, and `COMMIT_Stale`.

## Dependencies and integration points
This file is the bridge between Linux VFS namespace methods and JFS internals: dtree search/insert/delete/modify, inode allocation and iget, transaction manager, xtree truncate/insert, ACL and LSM initialization, quota, exportfs, metapage cache invalidation, and casefold-style dentry hashing/comparison for OS/2 mounts.

## Risks and test signals
Risks include deadlocks from commit mutex ordering, pinned dtree pages across blocking allocation, partially completed zero-link truncation, directory `..` updates during rename, stale dentry behavior under case-insensitive mode, and error cleanup of newly allocated inodes with inline/extent EAs. Tests should cover create/mkdir/mknod failures at each stage, long and short symlinks, unlink of open large fragmented files, rename over files/directories and across parents, NFS filehandle generation checks, OS/2 case-insensitive lookup/revalidate, quota failures, and crash-recovery around delete/create transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/namei.c -->
