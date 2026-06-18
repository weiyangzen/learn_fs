# sources/cloud-native/nydus/storage/src/cache/state/digested_chunk_map.rs

Purpose: implements `DigestedChunkMap`, a compatibility `ChunkMap` for legacy RAFS images that lack a stable chunk array/index. It tracks readiness by chunk digest rather than numeric chunk index.

Important APIs and control flow: `DigestedChunkMap::new` creates an empty `RwLock<HashSet<RafsDigest>>`. `is_ready` checks whether `chunk.chunk_id()` is present. `set_ready_and_clear_pending` inserts the digest into the set. `ChunkIndexGetter` returns the digest value, allowing `BlobStateMap<DigestedChunkMap, RafsDigest>` to key inflight slots by content digest.

State and persistence behavior: all readiness state is memory-only and is lost when the process exits. Because digest hashing and set storage are heavier than bitmap indexing, the module comments explicitly restrict its role to backward compatibility.

Dependencies and integration points: depends on `RafsDigest`, `BlobChunkInfo`, `ChunkMap`, and `ChunkIndexGetter`. It is selected by `FileCacheEntry::create_chunk_map` when RAFS v5 indexing is disabled or the blob has `_V5_NO_EXT_BLOB_TABLE`.

Risks and test signals: digest-based readiness can conflate duplicate chunks by content, which is acceptable for deduplicated content but different from per-index readiness. Lock poisoning is not expected and is unwrapped. Direct tests are mostly through `BlobStateMap` performance/concurrency comparisons against `IndexedChunkMap`.
