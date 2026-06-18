# sources/distributed-fs/openafs/src/vol/vg_cache_types.h

## Purpose

`vg_cache_types.h` defines the public data returned by volume-group cache queries. It is intentionally small and independent of private hash/scanner internals.

## Important Types

`VVGCache_query_t` contains `rw`, the read-write volume id for the group, and `children[VOL_VG_MAX_VOLS]`, the fixed vector of member volume ids. The implementation copies internal `VVGCache_entry_t` fields directly into this public structure.

## Control Flow and State

Callers pass a pointer to `VVGCache_query` or `VVGCache_query_r`; on success the buffer is filled with the RW id and child slots. Empty child slots are zero because the internal representation uses zero as the empty marker. There is no count field, so callers must scan the whole fixed array and ignore zero entries.

## Dependencies and Integration Points

The header includes `voldefs.h` for `VOL_VG_MAX_VOLS` and OpenAFS volume id types. It is included by `vg_cache.h` and should be the only volume-group cache type visible to external callers.

## Risks and Test Signals

The lack of an explicit child count is easy to misuse. Tests for callers should include sparse child vectors, zero-terminated assumptions, and groups at maximum capacity. ABI-sensitive consumers should be rebuilt when `VOL_VG_MAX_VOLS` changes because the public structure size changes.
