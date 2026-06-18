# sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.c

Purpose: Implements reverse-mapping btree deferred update log items: RUI intent items and RUD done items for data-device and realtime rmap updates. It provides crash-recoverable redo for map, unmap, convert, alloc, and free operations.

Important APIs and functions: `xfs_rmap_defer_add` queues an `xfs_rmap_intent` to data or realtime defer types. `xfs_rui_log_space` and `xfs_rud_log_space` size log reservations. Internal item ops allocate, format, release, match, relog, and recover RUI/RUD items. `xfs_rmap_update_defer_type` and `xfs_rtrmap_update_defer_type` plug into the generic deferred operation system.

Control flow: Rmap callers create intents with owner, fork, extent, state, and operation type. Defer-add grabs the AG or RT group intent reference and queues the proper defer type. Intent creation optionally sorts by group and encodes each operation into `xfs_map_extent` owner/startoff/startblock/length/flags. Finish calls `xfs_rmap_finish_one`, then cancels the item. Recovery validates logged RUI records, reconstructs `xfs_rmap_intent` objects, allocates a transaction with rmap btree reservation, finishes the intents, captures remaining deferred work, or reports corruption.

State and persistence: Persistent redo state is the logged RUI format; completion is a logged RUD referencing the RUI id. In-core RUI reference counts coordinate log and done lifetimes, including AIL deletion. Recovered map records restore owner, fork, unwritten state, physical range, and logical offset into deferred work.

Dependencies and integration: Integrates with xfs_defer, xfs_log_item, AIL, log recovery, rmap btrees, realtime groups, btree cursors, transaction reservations, group intent refs, and corruption reporting. It participates in allocator/bmap/refcount operations that must keep reverse mappings consistent.

Risks and invariants: Recovery rejects RUI records when rmapbt is disabled, flags are invalid, owner inode is invalid, file extent range is invalid, or physical data/realtime extent is invalid. Data and realtime rmap updates are separated to avoid incompatible lock mixing. Without RT support, realtime RUI/RUD records are corruption. RUD log record size must exactly match the format.

Test signals: Crash recovery of map/unmap/convert/alloc/free intents, shared and unwritten flag combinations, malformed log formats and invalid owners, RT rmap recovery with RT enabled/disabled, relogging of long-running intents, and group reference release on cancel/error.
