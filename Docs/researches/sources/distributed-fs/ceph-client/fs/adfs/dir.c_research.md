<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir.c

## Purpose
`dir.c` provides common ADFS directory handling independent of on-disk directory format: buffer loading, copying, iteration, lookup, name hashing/comparison, and optional update/commit coordination.

## Important APIs, types, and functions
Important functions are `adfs_dir_copyfrom`, `adfs_dir_copyto`, `adfs_dir_relse`, `adfs_dir_read_buffers`, `adfs_object_fixup`, `adfs_dir_update`, `adfs_iterate`, `adfs_dir_lookup_byname`, `adfs_hash`, `adfs_compare`, and `adfs_lookup`. It exports `adfs_dir_operations`, `adfs_dentry_operations`, and `adfs_dir_inode_operations`.

## Control flow
Directory reads load mapped blocks into buffer_heads via `__adfs_block_map`; format-specific ops validate and parse entries. Iteration emits dot, dotdot, then delegates to the active `adfs_dir_ops`. Lookup scans entries case-insensitively. Updates take the global directory write semaphore, call format update/commit, mark buffers dirty, and optionally sync.

## State and persistence
Runtime state is loaded buffer_heads in `struct adfs_dir` and a global `adfs_dir_rwsem`. Directory data persists on disk; write support modifies buffers only when `CONFIG_ADFS_FS_RW` is enabled.

## Dependencies and integration points
It depends on format-specific F/F+ ops, buffer-head I/O, VFS dentry/inode operations, ADFS map lookup, and RISC OS name/filetype rules.

## Risks and test signals
Risks include global lock contention, buffer boundary copy errors, corrupted directory parent IDs, name normalization collisions, and dirty-buffer handling after failed commits. Test signals include directory iteration across block boundaries, case-insensitive lookup, `/` to `.` fixups, filetype suffixes, RW update failures, and fsync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir.c -->
