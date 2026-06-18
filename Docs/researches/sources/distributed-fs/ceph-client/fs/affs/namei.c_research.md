# sources/distributed-fs/ceph-client/fs/affs/namei.c

## Purpose
`namei.c` implements AFFS namespace operations: case-folded hashing/comparison, lookup, create, mkdir, unlink, rmdir, symlink creation, hard links, rename/exchange, and NFS export helpers.

## Important APIs, types, and functions
Key functions are `affs_hash_name()`, `affs_lookup()`, `affs_create()`, `affs_mkdir()`, `affs_unlink()`, `affs_rmdir()`, `affs_symlink()`, `affs_link()`, `affs_rename2()`, `affs_rename()`, `affs_xrename()`, `affs_get_parent()`, and export/dentry operation tables. Internal case helpers are `affs_toupper()` and `affs_intl_toupper()`.

## Control flow
Lookups hash a case-folded name to a directory bucket, walk the hash chain, store the real header block in `d_fsdata`, and follow file-link originals. Create/mkdir allocate inodes and insert headers. Symlink creation rewrites absolute paths using the configured volume name and collapses simple `.`/`..` syntax into AFFS representation. Rename removes source and optional destination headers, changes the stored name, then inserts into the new directory; exchange swaps two headers.

## State and persistence
Persistent namespace state is encoded in directory hash tables, header names, parent pointers, link chains, originals, and symlink payloads. Dentry state uses AFFS-specific casefolding and `d_fsdata` header keys.

## Dependencies and integration points
It depends on `amigaffs.c` hash/removal helpers, inode allocation, AFFS mount flags, VFS dentry operations, and generic exportfs helpers.

## Risks and test signals
Risks include 30-byte truncation ambiguity, international case folding, rename rollback gaps, hard-link and `d_fsdata` consistency, exchange error handling, and symlink path rewriting. Test signals include case-insensitive lookup, no-truncate mode, create/unlink/mkdir/rmdir/link, rename overwrite and exchange, NFS filehandle lookup, and absolute/relative symlink round trips.
