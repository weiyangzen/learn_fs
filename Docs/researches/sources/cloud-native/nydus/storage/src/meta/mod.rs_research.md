# sources/cloud-native/nydus/storage/src/meta/mod.rs

## Purpose
Acts as the RAFS v6 blob metadata hub: defines the compression-context header, loads and validates `.blob.meta` cache files, maps chunk metadata into typed arrays, serves range-to-chunk queries, exposes batch and ZRan context lookup, and adapts metadata chunks to `BlobChunkInfo`/`BlobV5ChunkInfo`.

## Important APIs, Types, And Functions
`BlobCompressionContextHeader` is the 4K on-disk trailer/header with magic values, feature bits, chunk-info compressor, offsets, compressed/uncompressed metadata sizes, and optional ZRan/batch table offsets/counts. `BlobCompressionContextInfo::new()` loads or downloads metadata and optionally inlined chunk digests. Public query methods include `get_chunks_uncompressed()`, `get_chunks_compressed()`, `add_more_chunks()`, `get_chunk_index()`, digest accessors, batch accessors, and ZRan accessors. `BlobCompressionContext` stores the mapped state, `BlobMetaChunkArray` abstracts v1/v2 arrays, `BlobMetaChunk` implements chunk traits, `BlobMetaChunkInfo` is the common on-disk entry trait, `format_blob_features()` formats feature flags, and `round_up_4k()` provides alignment.

## Control Flow
`new()` validates compile-time layout assumptions, checks chunk count, opens or creates `<blob>.blob.meta`, sizes it to `4K header + aligned metadata`, mmaps it, validates the header, and if invalid downloads encrypted/compressed metadata from the backend through `read_metadata()`. It then maps v1 or v2 chunk entries from the file map, maps batch or ZRan side tables when feature flags require them, and optionally extracts/loads inlined chunk digests from a ToC entry.

Range lookup uses binary search in `_get_chunk_index_nocheck()`, then walks adjacent entries to cover requested uncompressed or compressed ranges. ZRan paths back up to the first chunk in the same ZRan context and include context groups according to batch-size amplification. Batch paths account for shared compressed ranges and expand reads to include all chunks in the current batch. `add_more_chunks()` performs read amplification for ZRan, batch, and normal chunks.

## State And Persistence
Persistent state lives in cache files named `<blob>.blob.meta`, `<blob>.blob.digest`, and `<blob>.blob.toc`, plus data embedded in the remote/local blob. `FileMapState` owns the mmap backing, while `ManuallyDrop<Vec<...>>` views typed arrays over mapped memory without freeing the mmap storage. The state also stores feature bits, blob sizes, optional digest arrays, batch contexts, ZRan contexts, and dictionaries.

## Dependencies And Integration Points
Integrates with backend `BlobReader`, device `BlobInfo`, `BlobFeatures`, `BlobChunkInfo`, `BlobChunkFlags`, v5 compatibility, ToC extraction, `FileMapState`, compression/decompression, encryption, digest handling, and constants for max chunk size/count. It re-exports v1/v2 chunk formats, batch generators, ZRan generators, and ToC support for builder/runtime callers.

## Risks
This file is unsafe-layout heavy: it converts mmap regions into vectors with `Vec::from_raw_parts()` and relies on `ManuallyDrop` to avoid freeing mapped memory. Header validation is central; missing checks can turn corrupt metadata into unsafe typed access. `get_compressed_size()` unwraps `get_batch_context()` after a prior batch-index read, so validation must protect against malformed batch indices. `get_chunks_compressed()` has a nested `einval!(einval!(...))` in one error path, and large read-amplification settings can return many chunks.

## Test Signals
Tests cover 4K alignment, loading real ZRan fixture metadata, ZRan compressed/uncompressed range lookup, ZRan read amplification, header getters/setters and stable digest, feature formatting, batch read amplification, and shared helpers used by v1 tests. Source size reviewed: 2,510 lines.
