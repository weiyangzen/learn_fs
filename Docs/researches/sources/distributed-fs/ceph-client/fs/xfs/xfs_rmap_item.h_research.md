# sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.h

Purpose: Declares in-core RUI/RUD log item structures and public helpers for deferred reverse-mapping updates.

Important APIs and types: `struct xfs_rui_log_item` contains the generic log item, RUI reference count, next extent index, and variable-sized `xfs_rui_log_format`. `struct xfs_rud_log_item` contains the done log item, pointer to the related RUI, and `xfs_rud_log_format`. `XFS_RUI_MAX_FAST_EXTENTS` controls the slab-cache fast path. `xfs_rui_log_item_sizeof` computes variable allocation size. Public functions are `xfs_rmap_defer_add`, `xfs_rui_log_space`, and `xfs_rud_log_space`.

Control flow and integration: Rmap update producers queue `xfs_rmap_intent` work through `xfs_rmap_defer_add`; deferred operation code creates RUI/RUD items, and log recovery can replay unresolved RUIs. The comment documents the transaction ordering: intent in the first transaction, done item in the transaction that performs rmapbt updates, with possible bnobt/cntbt updates later.

State and persistence: The structures wrap log-format records that persist redo and done state. In-core reference counts protect an RUI until both log and done processing release it.

Dependencies and integration points: Depends on log item infrastructure, rmap log format definitions, and kmem caches. Used by allocation, bmap, refcount, and recovery code that changes reverse mappings.

Risks and invariants: Structure sizing must match log format sizing for arbitrary extent counts. The fast extent threshold must match cache allocation expectations. Any semantic change to rmap extent flags or owner encoding requires coordinated recovery validation updates.

Test signals: Log-space reservation calculations, RUI/RUD size checks, crash replay of unresolved RUI, cancellation by RUD, and compile/link checks for data and realtime builds.
