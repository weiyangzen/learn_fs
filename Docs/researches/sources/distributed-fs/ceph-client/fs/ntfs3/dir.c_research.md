# sources/distributed-fs/ceph-client/fs/ntfs3/dir.c

## Purpose
Implements NTFS3 directory-facing helpers: UTF-16/NLS name conversion, directory lookup by Unicode name, directory iteration, entry emission, directory entry counting, empty-directory checks, and directory file operations.

## Important APIs, Types, And Functions
`ntfs_utf16_to_nls()` converts NTFS little-endian UTF-16 names to UTF-8 or a configured NLS charset. `ntfs_nls_to_utf16()` converts VFS input names to UTF-16 with a custom `_utf8s_to_utf16s()` that reports `-ENAMETOOLONG` before overflowing output. `dir_search_u()` finds a Unicode name in the directory index and returns an inode. `ntfs_readdir()` is the `iterate_shared` implementation. `ntfs_read_hdr()` validates and walks index headers. `ntfs_dir_emit()` filters and emits entries. `ntfs_dir_count()` and `dir_is_empty()` inspect directory contents. `ntfs_dir_operations` wires VFS methods.

## Control Flow
Lookup converts or receives a `cpu_str`, searches the NTFS index with `indx_find()`, then opens the referenced inode with `ntfs_iget5()`. Readdir emits dots, loads child MFT records when needed, reads the root index first, then walks allocation index blocks by used bitmap bits. It uses `ctx->pos` as a synthetic position and sets end-of-directory to `i_size + record_size`. If a directory changed after a complete pass, it restarts at position 3 to support common readdir/unlink loops.

## State And Persistence
Directory contents are persistent in NTFS index root/allocation entries and bitmaps, but this file mostly reads them. Runtime state includes `file->private_data` storing `ni->dir.version`, temporary name buffers, `ntfs_fnd` search contexts, and index nodes. `dir_search_u()` returns referenced inodes and validates bad-inode state.

## Dependencies And Integration Points
Depends on NTFS3 index code, inode loading, NLS configuration, VFS `dir_context`, file operations, leases, ioctl, fsync, and file open logic. Filtering respects mount options such as `showmeta` and `nohidden`.

## Risks And Edge Cases
Directory iteration deliberately avoids sorted enumeration to reduce risk from malformed index loops. Conversion failures replace unconvertible NLS characters with `_` on output after warning. Entry validation must catch corrupt sizes/key lengths to avoid overreads. `dt_type` from duplicated parent information may be unreliable, so the code optionally opens the child for extended data. Readdir restart after modification is pragmatic but not POSIX-guaranteed.

## Test Signals
Test UTF-8 and NLS name conversion including surrogate pairs and overlong names, lookup of missing/bad entries, readdir on root and large indexed directories, hidden/meta filtering, DOS-name skipping, directory mutation during iteration, corrupted index entry sizes, empty-directory checks, and dtype accuracy for reparse/symlink-like files.
