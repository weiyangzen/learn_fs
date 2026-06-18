# sources/distributed-fs/openafs/src/vol/vg_cache_impl_types.h

## Purpose

`vg_cache_impl_types.h` defines private data structures for the demand-attach volume-group cache. It deliberately errors out unless `__VOL_VG_CACHE_IMPL` is defined, protecting internal layout from external consumers.

## Important Types

`VVGCache_entry_t` represents one volume group: `rw` is the read-write parent id, `children` is a fixed vector of `VOL_VG_MAX_VOLS` member ids, and `refcnt` tracks child-vector memberships. `VVGCache_hash_table_t` owns a dynamically allocated array of queue heads. `VVGCache_hash_entry_t` is the per-member hash node, containing queue links, the member `volid`, the associated partition pointer, and the shared `VVGCache_entry_t`.

Scanner-only types include `VVGCache_scan_entry_t` for one discovered `(volid,parent)` tuple and `VVGCache_scan_table_t` for the thread-local batch with counters for discovered volumes and groups. `VVGCache_part_state_t` defines `VALID`, `INVALID`, and `UPDATING`. `VVGCache_dlist_entry_t` records a pending delete during a scan, and `VVGCache_part_t` stores each partition's state, condition variable, and temporary delete-list buckets. `VVGCache_t` is the global array of per-partition state for `VOLMAXPARTS + 1`.

## State and Persistence Behavior

These structures are in-memory only. Persistent truth is in OpenAFS volume headers and vnode/index files. The cache entry refcount is not a generic object reference count; it tracks how many children currently keep the group alive. The RW hash entry can exist separately from children so lookups by parent still resolve to the group, but the group is freed after all child vector entries have been removed.

## Dependencies and Integration Points

The file depends on `volume.h`, `rx_queue`, pthread condition variables via included types, and `VOL_VG_MAX_VOLS` from volume definitions. It is tightly integrated with `vg_cache.c` and `vg_scan.c`; layout changes require auditing queue scanning, allocation/free paths, and scanner dlist operations.

## Risks and Test Signals

Risks include fixed-size child arrays, ambiguous semantics of `refcnt`, and stale dlist buckets when scan start fails. Tests should assert queue nodes are initialized before use, dlist buckets are allocated only during `UPDATING`, condition variables are initialized for every partition in package init, and cache entries are freed exactly once after last child deletion.
