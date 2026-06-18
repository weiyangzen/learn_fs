# sources/distributed-fs/openafs/src/vol/vg_cache.c

## Purpose

`vg_cache.c` implements the demand-attach file server volume-group cache. A volume group is keyed by its read-write parent volume id and contains the ids of the RW, RO, and backup children recorded in volume headers. The cache lets callers query membership by any member id without walking partition header files for every lookup.

The file is compiled only under `AFS_DEMAND_ATTACH_FS`. It owns the global `VVGCache_hash_table` and `VVGCache` instances declared in the implementation header, allocates the hash table during package init, tracks per-partition validity, and exposes locked and `_r` caller-lock-held entry add/delete/query/scan functions.

## Important APIs, Types, and Functions

Public APIs from this file include `VVGCache_PkgInit`, `VVGCache_PkgShutdown`, `VVGCache_entry_add`, `VVGCache_entry_add_r`, `VVGCache_entry_del`, `VVGCache_entry_del_r`, `VVGCache_query`, `VVGCache_query_r`, `VVGCache_scanStart`, `VVGCache_scanStart_r`, `VVGCache_scanWait`, and `VVGCache_scanWait_r`. Internal APIs exported for `vg_scan.c` include `_VVGC_flush_part`, `_VVGC_flush_part_r`, `_VVGC_state_change`, and `_VVGC_entry_purge_r`.

The core private object is `VVGCache_entry_t`, with `rw`, fixed `children[VOL_VG_MAX_VOLS]`, and `refcnt`. Each member id also has a `VVGCache_hash_entry_t` stored in `VVGCache_hash_table.hash_buckets[VVGC_HASH(volid)]`; the hash entry records `volid`, partition pointer, and shared `entry`. The RW id has a hash entry even when it is also a child; child hash entries are removed individually, and the shared cache entry is freed when its refcount drops to zero.

## Control Flow

`VVGCache_PkgInit` allocates one queue head per `VolumeHashTable.Size` bucket and initializes every partition state to `VVGC_PART_STATE_INVALID` with a condition variable. `VVGCache_PkgShutdown` frees the bucket array and destroys per-partition condition variables, but returns `EOPNOTSUPP`, so consumers should not treat it as a complete cleanup implementation.

`VVGCache_entry_add_r` first looks up parent and child ids. If both exist and point to the same entry, it is usually a no-op, except the parent-equals-child case still ensures the RW id is present in the child list. If only the child exists, the existing entry is re-rooted by changing `rw` and adding a parent hash entry. If neither exists, `_VVGC_entry_add` allocates a new entry and RW hash entry. Any newly associated child gets a hash entry and is appended to the fixed child vector by `_VVGC_entry_cl_add`, which also increments the entry refcount. When a partition is in `UPDATING`, a successful add removes the tuple from the scanner delete-list so a delete/recreate race does not wipe out the new mapping.

`VVGCache_entry_del_r` records deletes on the partition delete-list while a scan is active, then calls `_VVGC_entry_purge_r`. Purge looks up the child id, optionally verifies the supplied parent maps to the same entry, then calls `_VVGC_hash_entry_del`. That removes the child from the vector and decrements the shared entry refcount; non-RW hash entries are unlinked immediately. When the final reference is dropped, `_VVGC_entry_put` looks up and unlinks the RW hash entry and frees the shared entry.

`VVGCache_query_r` lazy-starts a partition scan if the partition cache is invalid, returning `EAGAIN` while the async scan is starting or running. Valid state performs a hash lookup by any member id and exports the RW id plus child vector into `VVGCache_query_t`.

## State, Persistence, and Concurrency

This is an in-memory cache of persistent `.vol` header parent/id relationships. It does not write volume metadata. Persistence is provided by volume header files scanned by `vg_scan.c`; this file only keeps derived state and invalidates/rebuilds per partition.

All `_r` functions expect `VOL_LOCK` to be held unless documented otherwise. Non-`_r` wrappers acquire and release `VOL_LOCK`. Per-partition condition variables wake waiters when `_VVGC_state_change` changes `INVALID`, `UPDATING`, or `VALID`. `_VVGC_lookup` refuses to return mappings for invalid partitions.

## Dependencies and Integration Points

The implementation depends on OpenAFS queue primitives (`rx_queue`), volume package globals (`VolumeHashTable`, `DiskPartitionList`, `VOL_LOCK`), partition paths, volume ids, and logging through `ViceLog`. It integrates with `vg_scan.c` for async scans and delete-list reconciliation. The public cache API is consumed by demand-attach volume management code that needs fast volume-group membership.

## Risks and Test Signals

Important risks are hash/list/refcount consistency, race behavior during `UPDATING`, fixed child-vector capacity, and error propagation. A notable wrapper defect is that `VVGCache_entry_add` initializes `code` but ignores the return value from `VVGCache_entry_add_r`, so non-locked callers will always see success. Tests should cover add idempotency, parent re-rooting, conflicting parent/child mappings, delete of RW versus non-RW ids, query-triggered scan `EAGAIN`, partition invalidation, and delete-list behavior during a simulated scan. Stress tests should use colliding hash buckets and full `VOL_VG_MAX_VOLS` groups.
