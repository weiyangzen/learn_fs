<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h

Purpose: Defines in-core BUI/BUD log item structures and public helpers for deferred bmap update logging.

Important APIs and types: `XFS_BUI_MAX_FAST_EXTENTS` is currently one. `struct xfs_bui_log_item` contains the log item, refcount, next extent counter, and BUI format. `xfs_bui_log_item_sizeof` computes variable-sized allocation needs. `struct xfs_bud_log_item` links a done item to its BUI. Exports the BUI/BUD slab caches, `xfs_bmap_defer_add`, and log space calculators.

Control flow and integration: Higher-level bmap code allocates `struct xfs_bmap_intent` and queues it through `xfs_bmap_defer_add`; the implementation handles log formatting and recovery.

State and persistence: Structures represent redo intent and done records that persist in the journal until replayed or canceled.

Dependencies: Requires XFS log format definitions and transaction/defer users.

Risks: The header comment states the crash contract: intent in the first transaction and done with actual bmbt update. Any caller violating that ordering risks unrecoverable mapping changes.

Test signals: Log reservation sizing, one-extent intent assumptions, and BUI/BUD recovery ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_item.h -->
