# sources/distributed-fs/ceph-client/fs/ocfs2/inode.h

## Purpose
`inode.h` declares OCFS2 private inode state and the public inode helpers used across the filesystem. It defines the core `struct ocfs2_inode_info` wrapper around VFS `struct inode`, flags that describe OCFS2-specific inode roles and lifecycle state, and prototypes for inode loading, validation, refresh, dirtying, and eviction.

## Important APIs, types, and functions
- `struct ocfs2_inode_info` embeds lock resources for rw/meta/open locks, allocation and xattr semaphores, metadata cache, extent map, JBD2 inode, reservation state, quota pointers, fsync transaction ids, and the embedded `vfs_inode`.
- `OCFS2_I()` converts VFS inode pointers to OCFS2 private inode state.
- `INODE_CACHE()` exposes the inode metadata cache.
- `OCFS2_INODE_SYSTEM_FILE`, `OCFS2_INODE_JOURNAL`, `OCFS2_INODE_BITMAP`, `OCFS2_INODE_DELETED`, `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_OPEN_DIRECT`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` encode cluster and deletion state.
- `OCFS2_FI_FLAG_*` controls `ocfs2_iget()` behavior for system files, orphan recovery, and filecheck check/fix modes.
- Exported functions include `ocfs2_iget()`, `ocfs2_ilookup()`, `ocfs2_populate_inode()`, `ocfs2_mark_inode_dirty()`, `ocfs2_validate_inode_block()`, and inode-block read helpers.

## Control flow
Most callers use `ocfs2_iget()` to obtain an inode by disk block. The returned inode carries an initialized `ocfs2_inode_info` and can be passed to journal, locking, allocation, xattr, and extent-map helpers through the accessors in this header. Metadata I/O helpers use `INODE_CACHE()` so lower layers can retrieve owner block numbers and locking operations through `ocfs2_inode_caching_ops`.

## State and persistence behavior
The header separates persistent disk-backed fields from in-memory coordination state. `ip_blkno`, `ip_clusters`, `ip_dyn_features`, and `ip_attr` mirror dinode fields. Lock resources, semaphores, open counters, I/O markers, reservation data, and `ip_next_orphan` coordinate cluster-visible behavior but are rebuilt on iget. `i_sync_tid` and `i_datasync_tid` remember the journal transactions needed by fsync/fdatasync.

## Dependencies and integration points
The header depends on `extent_map.h` and forward declarations from the rest of OCFS2. It is included by most OCFS2 implementation files because `OCFS2_I()` and `INODE_CACHE()` are the common bridges from VFS objects to OCFS2 metadata, journal, DLM, and allocator state.

## Risks and edge cases
- The semantics of `OCFS2_INODE_MAYBE_ORPHANED`, `OCFS2_INODE_SKIP_ORPHAN_DIR`, and `OCFS2_INODE_DIO_ORPHAN_ENTRY` are subtle and directly affect whether eviction removes on-disk state.
- `ip_next_orphan` is protected by recovery-only assumptions rather than a general-purpose lock.
- Lock resource and semaphore ordering is not visible in the header but all users must follow the ordering established by inode, allocation, mmap, and recovery code.

## Test signals
Compile-time and runtime coverage should exercise flag transitions, `container_of()` access via `OCFS2_I()`, inode-cache operations, iget modes for system/orphan/filecheck cases, and fsync transaction id updates after metadata changes.
