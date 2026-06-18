<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/misc.c -->
# sources/distributed-fs/ceph-client/fs/netfs/misc.c

## Purpose
Collects netfs utility routines for folio-queue buffers, iterator reset, dirty/writeback pinning, folio invalidation/release, collector wakeups, and synchronous waits for read/write request completion or pause points.

## Important APIs, Types, And Functions
Exports `netfs_alloc_folioq_buffer()`, `netfs_free_folioq_buffer()`, `netfs_dirty_folio()`, `netfs_unpin_writeback()`, `netfs_clear_inode_writeback()`, `netfs_invalidate_folio()`, and `netfs_release_folio()`. Internal but central functions include `netfs_reset_iter()`, `netfs_wake_collector()`, `netfs_subreq_clear_in_progress()`, `netfs_wait_for_in_progress_stream()`, `netfs_wait_for_read()`, `netfs_wait_for_write()`, and pause wait helpers.

## Control Flow
Folio-queue allocation grows a chain until target size is met, allocating folios and marking slots for release. Dirtying delegates to `filemap_dirty_folio()` and pins the FS-Cache cookie once per inode writeback episode. Invalidation updates `zero_point`, waits for deprecated private_2, adjusts or removes `netfs_folio` dirty-range metadata, and drops dirty groups. Collector waits either sleep for workqueue completion or run collection in the caller via `netfs_collect_in_app()` when offload is disabled.

## State And Persistence
State touched includes folio queues, folio private/group metadata, inode `I_PINNING_NETFS_WB`, netfs inode `zero_point`, request flags (`IN_PROGRESS`, `OFFLOAD_COLLECTION`, `RETRYING`, `PAUSE`), stream active state, waitqueues, and transferred/error fields.

## Dependencies And Integration Points
Used by read/write collectors, retry paths, pagecache address_space ops, and FS-Cache writeback pinning. Depends on folio_queue, swap/pagecache, waitqueues, and fscache cookie helpers.

## Risks
Partial invalidation of streaming-write metadata is subtle. Collector wait logic relies on memory ordering in flag helpers. Release must avoid blocking reclaim improperly on `PG_private_2`. Cookie pin/unpin balance depends on filesystem write_inode/evict hooks.

## Test Signals
Stress partial folio invalidation, dirty/writeback pin balance, kswapd folio release, non-offloaded collection waits, pause/unpause during retry, and short read detection in `netfs_wait_for_in_progress()`.
