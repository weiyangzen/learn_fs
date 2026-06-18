<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h

Purpose: Defines in-core structures and public entry points for logged extended-attribute intent/done items.

Important APIs and types: `struct xfs_attri_log_nameval` stores name, optional new name, value, optional new value, and a refcount, with payload bytes immediately following the struct. `struct xfs_attri_log_item` wraps an XFS log item, refcount, shared name/value buffer, and on-disk log format. `struct xfs_attrd_log_item` references the matching ATTRI and stores done format. `enum xfs_attr_defer_op` names set/remove/replace, and `xfs_attr_defer_add` queues work.

Control flow and integration: The header is consumed by attr mutation code to queue deferred logged work and by log infrastructure to allocate ATTRI/ATTRD caches. It exposes only the queuing API; item operation details remain in `xfs_attr_item.c`.

State and persistence: Structures mirror log intent state that survives crashes until canceled by ATTRD. Shared name/value state is in-core but copied from/to log iovecs.

Dependencies: Requires XFS mount/log format definitions, `struct kvec`, refcounting, and attr state definitions from broader XFS headers.

Risks: Layout and length semantics must remain compatible with log recovery. New operation types must update validation, formatting, recovery, and this enum together.

Test signals: Compile/link of cache users, intent format size expectations, and operation coverage through `xfs_attr_defer_add` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.h -->
