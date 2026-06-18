# sources/cloud-native/nydus/storage/src/cache/state/range_map.rs

Purpose: implements `BlobRangeMap`, a bitmap-backed `RangeMap<u64>` for readiness of fixed-size data address ranges rather than chunk indices.

Important APIs and control flow: `BlobRangeMap::new` creates `${blob_path}.range_map`; `open` opens an existing `${workdir}/${blob_id}.range_map`. `get_range(start, count)` converts byte offsets to bitmap indices by shifting with `shift`, validates start and end indices, and returns a half-open index range. `is_range_ready` scans all bits for the computed range unless all-ready. `check_range_ready_and_mark_pending` returns the shifted start offsets for not-ready bitmap entries. `set_range_ready_and_clear_pending` sets all bits covering the requested range.

State and persistence behavior: readiness is persisted through `PersistMap` with one bit per range bucket. `shift` defines bucket size as `1 << shift`; pending state is not in this type directly and is added by `BlobStateMap<BlobRangeMap, u64>`.

Dependencies and integration points: used through `RangeMap` and `BlobStateMap::from_range_map`. It shares persistence, atomic bit setting, and all-ready accounting with `IndexedChunkMap`.

Risks and test signals: `get_range` assumes `count > 0`; otherwise `end - 1` can underflow in debug/produce invalid behavior. Capacity allocation in `check_range_ready_and_mark_pending` uses byte count as `usize`, which can be excessive for large ranges even though the returned vector is per bucket. Tests cover concurrent million-range readiness and simple check/set behavior.
