# sources/cloud-native/nydus/storage/src/cache/state/noop_chunk_map.rs

Purpose: implements `NoopChunkMap`, a trivial readiness map that reports every chunk as either always ready or always not ready. It is used when the cache layer should not maintain real per-chunk state, such as dummy cache and tarfs/local-disk paths.

Important APIs and control flow: `NoopChunkMap::new(cached)` stores a boolean. `ChunkMap::is_ready` returns that boolean for any chunk. `ChunkIndexGetter` returns `chunk.id()` so it can still be wrapped by generic code if needed.

State and persistence behavior: state is only the immutable `cached` flag and has no persistence, pending tracking, or readiness mutation.

Dependencies and integration points: used by `DummyCacheMgr` to control prefetch eligibility semantics and by filecache tarfs handling through `BlobStateMap::from(NoopChunkMap::new(true))`.

Risks and test signals: because all chunks share one readiness answer, using this map in a path that expects real partial caching would produce either redundant backend reads or false cache hits. Tests cover true/false readiness and index getter behavior.
