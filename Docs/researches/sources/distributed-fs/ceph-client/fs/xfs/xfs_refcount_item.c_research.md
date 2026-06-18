# sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.c

Purpose: Implements refcount btree deferred update log items: CUI intent items and CUD done items for data-device and realtime refcount operations. These items make refcount updates recoverable across rolled transactions and crashes.

Important APIs and functions: `xfs_refcount_defer_add` attaches a `struct xfs_refcount_intent` to the deferred operation system and selects data versus realtime defer types. `xfs_cui_log_space` and `xfs_cud_log_space` expose reservation sizing. Internal CUI/CUD item ops format, unpin, release, match, and identify intent-done relationships. `xfs_refcount_update_defer_type` and `xfs_rtrefcount_update_defer_type` provide create intent, create done, finish item, cleanup, cancel, recover, and relog callbacks.

Control flow: Deferred refcount callers allocate intents and call `xfs_refcount_defer_add`, which pins the target AG or RT group and queues the correct defer type. Intent creation optionally sorts by group, allocates a CUI with a fast cache or dynamic allocation, and encodes each operation into `xfs_phys_extent` flags. Finish callbacks call `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`; if reservation is exhausted and blockcount remains, they return `-EAGAIN` to requeue. Done item creation creates a CUD referencing the CUI id, and release drops the CUI reference.

State and persistence: Persistent redo state is the logged CUI format containing startblock, length, and operation type; logged CUD records completion by CUI id. In-core CUI reference counts handle log and done-item lifetimes and AIL removal. Recovery reconstructs CUIs from log records, validates feature flags and extent ranges, rebuilds deferred intents, allocates a recovery transaction, finishes the intent, and captures remaining deferred work.

Dependencies and integration: Integrates with xfs_defer, xfs_log_item, AIL, log recovery, refcount btree code, realtime groups, transaction reservations, group intent references, tracepoints, and corruption reporting. Realtime support is conditional; without `CONFIG_XFS_RT`, realtime CUI/CUD recovery reports corruption for those item types.

Risks and invariants: CUI extent counts must be fully populated before formatting. Recovered records are rejected if reflink is disabled, flags are invalid, operation type is unknown, or data/realtime extents fail verification. Data and realtime updates are deliberately separated to avoid mixing RT metadata file locks and AGF locks in one deferred finish transaction. Reference counting must tolerate CUD processing racing AIL insertion order.

Test signals: Crash-recovery tests for refcount increase/decrease and COW alloc/free across transaction rolls, malformed CUI/CUD log record size and flags, realtime CUI/CUD recovery with and without RT support, reservation exhaustion requeue, AIL release ordering, and group reference cleanup on cancel/error.
