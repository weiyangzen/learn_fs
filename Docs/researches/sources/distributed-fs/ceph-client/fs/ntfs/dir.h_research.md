# sources/distributed-fs/ceph-client/fs/ntfs/dir.h

Purpose: declares directory-facing NTFS interfaces and the alias-return structure shared by lookup/namei code.

Important APIs and types:
- `struct ntfs_name` carries an MFT reference, filename namespace type, Unicode length, and optional little-endian Unicode name bytes. It is packed because it mirrors compact on-disk name metadata for dcache alias resolution.
- `extern __le16 I30[5]` exposes the `$I30` Unicode index name used by directory and index code.
- `ntfs_lookup_inode_by_name()` is the directory name-to-MFT-reference lookup API.
- `ntfs_check_empty_dir()` verifies whether a directory MFT record contains only the empty index-root form.

Control flow and integration:
- `namei.c` callers use `ntfs_lookup_inode_by_name()` and inspect the optional `struct ntfs_name` result to avoid dcache aliases for DOS and case-insensitive names.
- Directory removal paths can call `ntfs_check_empty_dir()` before deleting directories.
- `I30` is shared with `index.c`, `inode.c`, `file.c`, and `ea.c` for directory index allocation and syncing.

State and persistence behavior:
- The header owns no persistence, but its APIs expose MFT references containing sequence numbers, so consumers can perform stale-reference checks.
- The flexible `name[]` member is caller-allocated by `dir.c`; users must free it according to lookup ownership rules.

Dependencies:
- Includes `inode.h` for `struct ntfs_inode` and NTFS inode state.
- Uses kernel little-endian integer types and NTFS MFT record declarations from included headers.

Risks and edge cases:
- `struct ntfs_name` packing and flexible array sizing must match allocations in `dir.c`; misuse can overread names.
- Callers must not treat the raw `u64` return as a signed integer without extracting the MFT record number, because error encoding uses NTFS MFT reference macros.

Test signals:
- Compile coverage should catch prototype drift.
- Lookup/namei tests should verify returned `struct ntfs_name` ownership and DOS-name behavior.
