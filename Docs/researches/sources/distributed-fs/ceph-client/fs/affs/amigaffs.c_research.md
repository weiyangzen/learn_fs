# sources/distributed-fs/ceph-client/fs/affs/amigaffs.c

## Purpose
`amigaffs.c` implements low-level AFFS metadata manipulation: directory hash insertion/removal, hard-link chain removal, object header removal, block checksums, Amiga timestamp conversion, protection-bit translation, error reporting, and filename validation/copying.

## Important APIs, types, and functions
Public functions include `affs_insert_hash()`, `affs_remove_hash()`, `affs_remove_header()`, `affs_checksum_block()`, `affs_fix_checksum()`, `affs_secs_to_datestamp()`, `affs_prot_to_mode()`, `affs_mode_to_prot()`, `affs_error()`, `affs_warning()`, `affs_nofilenametruncate()`, `affs_check_name()`, and `affs_copy_name()`. Internal helpers include `affs_fix_dcache()`, `affs_remove_link()`, and `affs_empty_dir()`.

## Control flow
Create/link operations insert headers into a directory hash bucket by walking `hash_chain` to the tail and updating parent/checksum fields. Removal locks link and directory state, validates empty directories, unlinks the header from its hash chain, handles hard-link inheritance if needed, and frees link blocks. Error reporting remounts writable filesystems read-only.

## State and persistence
It mutates on-disk header tails, hash buckets, link chains, parent pointers, checksums, timestamps, and protection bits. Directory inode ctime/mtime and i_version are updated on hash changes.

## Dependencies and integration points
It is used by `namei.c`, `inode.c`, and `file.c`, and depends on buffer-head I/O, AFFS checksum layout, VFS dentry aliases, metadata buffer tracking, and mount flags.

## Risks and test signals
Risks include broken hard-link inheritance, stale `d_fsdata`, checksum delta mistakes, directory non-empty races, remount-readonly behavior on metadata errors, lossy permission mapping, and filename truncation semantics. Test signals include create/unlink/link/rename cycles, hard-link removal order, nonempty rmdir, invalid names, protection-bit round trips, and checksum verification after every mutation.
