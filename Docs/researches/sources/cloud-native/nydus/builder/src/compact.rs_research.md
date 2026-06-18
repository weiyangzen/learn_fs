# sources/cloud-native/nydus/builder/src/compact.rs

Purpose: implements RAFS blob compaction: removes unused blobs, optionally rebuilds low-utilization blobs, greedily merges small blobs, rewrites chunk references in the bootstrap tree, and emits a new bootstrap/blob table.

Important APIs/types/functions: `Config` controls thresholds (`min_used_ratio`, `compact_blob_size`, `max_compact_size`, `layers_to_compact`, `blobs_dir`). `ChunkKey` deduplicates chunks by digest for v5/ref or by `(blob_index, compressed_offset)` for v6. `ChunkSet` tracks unique chunks and can `dump` them into a new blob. `State` models each original blob as `ChunkDict`, `Delete`, `Invalid`, `Original`, or `Rebuild`. `BlobCompactor::compact` is the public entry.

Control flow: `compact` builds a synthetic `BuildContext`, loads original blob table and optional chunk dictionary, exits early if blob count is below threshold, reconstructs the tree from `RafsSuper`, creates `BlobCompactor`, runs `do_compact`, dumps new blobs, rebuilds bootstrap, and returns `BuildOutput`. Initialization marks chunkdict blobs, walks bootstrap BFS to deduplicate chunks against the dictionary and within the image, and builds chunk/blob-to-node indexes. Dumping either keeps/moves original blobs, skips deletes, or writes rebuilt chunks in original blob order and updates all referenced nodes.

State and persistence: mutates in-memory tree chunk metadata and blob managers, reads original blob content from `BlobBackend`, writes compacted blobs to `cfg.blobs_dir`, and overwrites/dumps bootstrap storage.

Dependencies and integration points: depends on RAFS super/layout, storage backend readers, digest/hash utilities, builder artifact writers, blob manager, chunk dictionaries, and build output generation.

Risks: backend reads use `expect`, so missing blobs can panic. `prepare_to_rebuild` appears to check `!is_rebuild()` before converting `Original` to `Rebuild`, which may make rebuild threshold behavior fragile. `take_blob(idx)` removes from a vector while iterating original indexes, so keeping original blobs relies on state/order interactions. Greedy merge is size-only, not locality-aware. Size calculations use compressed sizes that may be zero and then require backend `blob_size()`.

Test signals: tests cover chunk key construction, chunk set merge/dump, state transitions, chunk rewrite validation, compactor creation, chunkdict blob marking, BFS dedup index construction, dump error/success paths, and compaction state changes.
