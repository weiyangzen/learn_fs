<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/write_issue.c -->
# sources/distributed-fs/ceph-client/fs/netfs/write_issue.c

## Purpose
Constructs and issues netfs write requests for writeback, writethrough, copy-to-cache, and single-object writeback. It overlays variable-sized folios with up to two parallel IO streams: upload to server and write to cache.

## Important APIs, Types, And Functions
Exports `netfs_prepare_write_failed()`, `netfs_writepages()`, and `netfs_writeback_single()`. Defines `netfs_create_write_req()`, `netfs_prepare_write()`, `netfs_reissue_write()`, `netfs_issue_write()`, `netfs_advance_write()`, `netfs_begin_writethrough()`, `netfs_advance_writethrough()`, and `netfs_end_writethrough()`.

## Control Flow
`netfs_create_write_req()` allocates a request, begins cache write resources if cacheable, initializes the rolling buffer, and configures stream 0 for server upload and stream 1 for cache write when available. `netfs_writepages()` serializes with `wb_lock`, obtains dirty folios with `writeback_iter()`, starts writeback, begins netfs writeback when a server-upload folio appears, and hands each folio to `netfs_write_folio()`. That function handles EOF truncation/zeroing, dirty groups, copy-to-cache sentinel groups, streaming dirty ranges, rolling buffer append, and alternating stream advancement by lowest submit offset. End issue flushes constructed subrequests and sets `ALL_QUEUED`.

## State And Persistence
Writes mutate server state via netfs `issue_write()` and cache state via FS-Cache ops. Request state includes rolling buffer, `issued_to`, `len`, stream availability/constructs, `wsize`, dirty group, and cache resources. Folios move through dirty/writeback/private/group states.

## Dependencies And Integration Points
Depends on netfs inode ops (`begin_writeback`, `prepare_write`, `issue_write`), FS-Cache write operations, write collector, retry code, folio queues, VM writeback, and writeback control.

## Risks
High-risk areas include EOF handling, partial streaming writes, dirty group mismatch/redirty, constructed subrequest flush boundaries, and cache/server stream divergence. Allocation failure after dirty folio acquisition calls `netfs_kill_dirty_pages()`, which is intentionally destructive to dirty folios in unrecoverable startup failure.

## Test Signals
Exercise contiguous and discontiguous writeback, Ceph-like dirty groups, copy-to-cache folios, EOF writes, mmap beyond EOF, writethrough partial pages, cache disabled/enabled, writeback lock contention, and negotiated `wsize` splitting.
