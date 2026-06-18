# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.h

Purpose: Declares XFS exchange-mapping intent and done log item structures plus the deferred-add entry point.

Important APIs, types, and functions: Defines `struct xfs_xmi_log_item` with common log item, refcount, and `xfs_xmi_log_format`; `struct xfs_xmd_log_item` with common log item, intent pointer, and `xfs_xmd_log_format`; declares `xfs_xmi_cache`, `xfs_xmd_cache`, `struct xfs_exchmaps_intent`, and `xfs_exchmaps_defer_add()`.

Control flow: Exchange-map code queues an intent with `xfs_exchmaps_defer_add()`, and the implementation creates XMI/XMD log items around deferred work and recovery.

State and persistence: Defines in-core wrappers for persistent XMI/XMD log formats. XMI refcounting spans AIL insertion, unpin, done processing, and cancellation.

Dependencies and integration points: Consumed by exchange-map implementation, transaction logging, recovery, and slab-cache initialization.

Risks and test signals: Risks are struct/log-format drift and lifecycle mistakes around XMI refcounting. Test large exchange operations, log recovery matching, and cache lifecycle builds.
