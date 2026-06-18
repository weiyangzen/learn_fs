<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/log.h

## Purpose
`log.h` is the public journal-accounting interface used by GFS2 transaction, glock, metadata, inode, superblock, and quota code. It exposes log reservation, release, flush, revoke, ordered-data, AIL, and logd entry points.

## Important APIs, types, and functions
The central constant is `GFS2_LOG_FLUSH_MIN_BLOCKS`, reserving room for revoke and log header activity during flush. The inline helper `gfs2_ordered_add_inode` adds non-journaled ordered-data inodes to `sd_log_ordered` unless the inode is journaled data or the filesystem is not in ordered mode. Prototypes cover `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_logd`, revoke helpers, and `gfs2_ail_drain`.

## Control Flow
The header itself has no complex runtime flow. Its APIs define the expected transaction sequence: reserve log space, add buffers/revokes through transaction helpers, commit through `gfs2_log_commit`, let `gfs2_logd` or explicit callers run `gfs2_log_flush`, and use AIL/revoke helpers to release journal space once in-place blocks are safe.

## State and Persistence
The header declares no standalone state. It documents the state managed by `log.c`: in-memory reservation counters, ordered inode lists, revokes, AIL lists, and persistent journal headers/descriptors. `gfs2_ordered_add_inode` mutates `sd_log_ordered` under `sd_ordered_lock`.

## Dependencies and Integration Points
Includes `incore.h`, `inode.h`, Linux list/spinlock/writeback definitions, and buffer-head types through prototypes. It is included by transaction code, metadata I/O, lops, recovery, superblock lifecycle, glock operations, quota, resource-group code, and file/inode write paths.

## Risks
Callers must respect locking rules that are only partly visible in the header: `gfs2_log_try_reserve` expects `sd_log_flush_lock`, `gfs2_log_release_revokes` expects flush-lock protection, and ordered inode list insertion depends on double-checked list state. Misuse can produce log-space leaks, deadlocks, or ordered-data violations.

## Test Signals
Compile coverage for all log clients, transaction begin/end paths, ordered-data workloads, revoke-heavy deletes, flush callers under freeze/remount/unmount, and lockdep coverage around flush lock and ordered lock are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/log.h -->
