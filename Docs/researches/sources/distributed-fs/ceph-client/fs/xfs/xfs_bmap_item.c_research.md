<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c

Purpose: Implements BUI/BUD logged intent handling for deferred bmap updates, allowing map/unmap operations to be replayed after crashes.

Important APIs and functions: `xfs_bmap_defer_add` queues a `struct xfs_bmap_intent`. `xfs_bui_log_space` and `xfs_bud_log_space` calculate reservation sizes. The defer type `xfs_bmap_update_defer_type` uses create-intent/done, finish, cancel, recover, and relog callbacks. Recovery entry points are `xlog_recover_bui_commit_pass2` and `xlog_recover_bud_commit_pass2`.

Control flow: Queueing takes a passive AG/RTG intent reference and pre-adjusts `i_delayed_blks` for map intents. Intent creation sorts by inode if requested, records owner/startblock/startoff/length/type/fork/realtime/unwritten flags in one BUI extent slot, and logs the item. Finish calls `xfs_bmap_finish_one`; if an unmap remains partially unfinished, it returns `-EAGAIN` for transaction rolling. Cancel reverses delayed block accounting and drops group intent refs. Recovery validates the logged extent, reconstructs a bmap intent, obtains inode and group state, allocates a transaction, verifies realtime flag consistency, reserves incore extent changes, finishes the recovered intent, and commits captured deferred work.

State and persistence: BUI persists unfinished bmbt map/unmap work in the log; BUD cancels it when complete. In-core state tracks BUI refcounts, next extent index, group intent refs, and temporary delayed-block accounting. Persistent replay updates inode data/attr fork mappings and related rmap/refcount side effects via deferred operations.

Dependencies and integration: Integrates with XFS log item ops, defer framework, AIL, bmap btree updates, inode recovery, AG/RT group intent accounting, transaction reservations, rmap/realtime validation, and corruption reporting.

Risks: Only `XFS_BUI_MAX_FAST_EXTENTS == 1` is supported, so format validation rejects other counts. Delayed block pre-accounting must be undone exactly once. Recovered realtime flags must match the target fork or replay could corrupt the wrong address space. Refcount ordering between BUI unpin/release and BUD commit is subtle.

Test signals: Crash recovery after BUI before BUD, map and unmap intents, partial unmap `-EAGAIN` loops, realtime and attr-fork flags, malformed log records, relogging, and delayed-block accounting under out-of-place writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.c -->
