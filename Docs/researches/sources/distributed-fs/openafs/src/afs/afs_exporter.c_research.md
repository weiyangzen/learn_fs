# sources/distributed-fs/openafs/src/afs/afs_exporter.c

Purpose: Maintains the cache-manager registry of "AFS exporters", such as the NFS exporter. Exporters provide operation vectors that other cache-manager code can discover and periodically garbage collect.

Important APIs and functions: `exporter_add` lazily initializes `afs_xexp`, allocates an exporter object of caller-specified size or `sizeof(struct afs_exporter)`, appends it to `root_exported`, and fills operation, state, data, and type fields. `exporter_find` scans the registry for a matching type. `shutdown_exporter` frees the linked list and resets initialization state.

Control flow: The registry is append-only during normal operation. On first add, the lock is initialized. Adds walk to the tail under the write lock, link the new node, release the lock, then initialize fields. Finds take the read lock and return the matching pointer after releasing the lock. Shutdown walks `root_exported` and frees nodes without taking the exporter lock.

State and persistence: Global state is `root_exported`, `afs_xexp`, and `init_xexported`. Entries are heap allocations with caller-owned `exp_data` and operation-vector pointers. There is no on-disk persistence.

Dependencies and integration points: Uses `struct afs_exporter` and `struct exporterops` from AFS headers, OSI allocation/free, locks, stats, and the daemon maintenance loop. `afs_nfsclnt.c` registers the NFS exporter; `afs_pioctl.c` discovers exporters for exporter-related pioctls; `afs_Daemon` iterates `root_exported` and calls `EXP_GC` every ten-minute cycle.

Risks: `exporter_add` links the new node before fully initializing its fields, so concurrent readers could observe a partially initialized exporter. `exporter_find` returns an unlocked raw pointer with no refcount, so lifetime must be controlled by subsystem shutdown ordering. `shutdown_exporter` frees every node as `sizeof(struct afs_exporter)` even when `exporter_add` allocated a larger caller-specific size. It also does not clear `root_exported`, leaving a stale pointer after shutdown unless cold shutdown ordering prevents reuse.

Test signals: Register one and multiple exporters, find by existing/missing type, and verify daemon GC sees entries. Stress concurrent add/find if supported by target platforms. Test shutdown after variable-size allocations and ensure callers do not dereference stale exporter pointers. Static review should confirm `exp_data` ownership and cleanup responsibilities outside this file.
