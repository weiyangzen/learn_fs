# sources/distributed-fs/ceph-client/fs/udf/namei.c

## Purpose
`namei.c` implements UDF VFS namespace operations for directories: lookup, create, tmpfile, mknod, mkdir, rmdir, unlink, symlink, hard link, rename, and NFS export file-handle conversion. It owns file identifier descriptor creation/deletion and keeps Logical Volume Integrity Descriptor file/dir counters in sync.

## Important APIs, types, and functions
The exported operation tables are `udf_dir_inode_operations` and `udf_export_ops`. Core helpers include `udf_fiiter_find_entry`, `udf_fiiter_add_entry`, `udf_fiiter_delete_entry`, `udf_expand_dir_adinicb`, `udf_add_nondir`, `empty_dir`, `udf_get_parent`, `udf_nfs_get_inode`, and `udf_encode_fh`. It relies on `struct udf_fileident_iter`, `struct fileIdentDesc`, and `struct allocDescImpUse`.

## Control flow
Lookup scans a directory iterator, filters deleted/hidden entries unless mount flags expose them, converts CS0 names to the host charset, and instantiates `udf_iget` results. Creation allocates an inode, sets file ops/address ops, appends or reuses a FID, stores the target ICB and unique-id imp-use value, updates parent times, and instantiates the dentry. Directories get an internal parent FID first, then the parent directory receives the child FID. Symlink creation encodes UDF `pathComponent` records either inline or into a new data block.

Rename validates source identity, directory emptiness and link counts, optionally locates the child `..` FID, creates/reuses the destination entry, copies the source FID payload, deletes the old entry, adjusts counters/link counts, and rewrites `..` when moving directories across parents. NFS export encodes UDF logical block, partition reference, and generation fields.

## State and persistence
Persistent state includes directory FID records, inode link counts, inode times, directory sizes and allocation extents, LVID file/dir counters, symlink encoded path components, and exported file-handle identity. It also converts inline AD-in-ICB directories to block-backed extents when an entry no longer fits inline.

## Dependencies and integration points
It integrates with `directory.c` iterators, `unicode.c` filename conversion, `inode.c` inode allocation and extent insertion, `balloc.c` block allocation, `truncate.c` tail truncation, VFS dcache/inode APIs, and Linux exportfs.

## Risks and test signals
Risks include FID tag-location mistakes after expanding inline directories, link-count/counter drift on failure paths, stale iterators after destination allocation during rename, mishandled hidden/deleted entries, symlink size limits, and the parent generation field in `udf_encode_fh` using the child generation. Test signals include create/unlink/rmdir/rename across directories, AD-in-ICB directory expansion, hidden and undelete mount flags, long or non-UTF8 names, absolute and relative symlinks, NFS export/restore, and corrupted `..` entries.
