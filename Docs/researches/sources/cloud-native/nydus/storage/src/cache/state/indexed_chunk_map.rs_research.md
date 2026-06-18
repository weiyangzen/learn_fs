# sources/cloud-native/nydus/storage/src/cache/state/indexed_chunk_map.rs

Purpose: implements `IndexedChunkMap`, the preferred bitmap-file-backed readiness map for blobs with stable chunk indices. It supports both per-chunk `ChunkMap` operations and batch `RangeMap<u32>` operations.

Important APIs and control flow: `IndexedChunkMap::new` opens `${blob_path}.chunk_map` through `PersistMap::open`. `is_ready` fast-paths when the whole range is ready, otherwise validates the chunk id and reads its bit. `set_ready_and_clear_pending` sets the bit in `PersistMap`. `RangeMap` methods check all-ready, scan indices for readiness, return not-ready indices for `check_range_ready_and_mark_pending`, and set a range ready one bit at a time.

State and persistence behavior: state is a memory-mapped bitmap with a 4096-byte header and one bit per chunk. The `persist` constructor argument controls whether the file remains on disk after mapping. `is_persist` returns true because the implementation supports persistent state even when a caller chooses non-persistent open.

Dependencies and integration points: wraps `persist_map::PersistMap`; is wrapped by `BlobStateMap` for pending tracking; is created by filecache/fscache entry constructors; supplies `ChunkIndexGetter<Index = u32>`.

Risks and test signals: invalid chunk counts or mismatched existing file sizes return errors to avoid trusting corrupt readiness. `check_range_ready_and_mark_pending` does not validate every index before `is_chunk_ready` in the scan, so callers rely on bounded ranges. Tests cover invalid file size, zero-size initialization, header-not-ready, all-ready header, v0 header loading, bit setting, and range behavior indirectly through `BlobStateMap`.
