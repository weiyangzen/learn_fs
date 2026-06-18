# sources/cloud-native/nydus/rafs/src/metadata/md_v5.rs

## Purpose
`md_v5.rs` wires the version-neutral `RafsSuper` facade to RAFS v5 metadata loading, v5 prefetch, v5 update skipping, IO amplification, and a v5-specific storage chunk adapter. It is the bridge between the raw v5 layout definitions and runtime metadata implementations in `direct_v5` and `cached_v5`.

## Important APIs, Types, And Functions
The main methods are `RafsSuper::try_load_v5`, `prefetch_data_v5`, `skip_v5_superblock`, `amplify_user_io`, and the private `merge_chunks_io`. `V5IoChunk` represents a chunk address passed to the storage layer and implements `BlobChunkInfo` by exposing digest, index, compression status, CRC32, offsets, sizes, and blob index.

## Control Flow
`try_load_v5` seeks to the end to get metadata size, seeks back to offset zero, reads a `RafsV5SuperBlock`, returns `Ok(false)` if the magic/version do not match v5, validates the superblock, copies all relevant fields into `self.meta`, and creates either `DirectSuperBlockV5` or `CachedSuperBlockV5` depending on `self.mode`. The selected implementation loads the remaining metadata and is stored as `self.superblock`.

`prefetch_data_v5` exits early when the v5 prefetch table has no entries. Otherwise it loads inode hints from the prefetch table offset, walks the hinted inode list until a zero padding entry, tracks whether the root inode was included, deduplicates hardlinks, appends file IO into a `BlobIoMerge`, and flushes remaining merged descriptors through the caller's fetch callback. `amplify_user_io` expands an existing user IO descriptor by reading adjacent file content and then nearby regular files with increasing inode numbers, merging only chunks from the same blob and within the configured maximum gap.

## State And Persistence
`try_load_v5` persists no new data; it materializes persistent v5 superblock fields into `RafsSuperMeta`. `prefetch_data_v5` consumes persistent prefetch-table hints but only produces transient `BlobIoVec` fetch requests. `amplify_user_io` is purely runtime behavior that opportunistically enlarges read-ahead based on inode order and chunk continuity. `V5IoChunk` is a runtime wrapper around persistent chunk metadata.

## Dependencies And Integration Points
The file depends on `RafsV5SuperBlock` and `RafsV5PrefetchTable` from `layout/v5.rs`, `DirectSuperBlockV5`, `CachedSuperBlockV5`, `BlobDevice`, `BlobIoVec`, `BlobIoMerge`, `BlobChunkFlags`, and the shared `RafsSuper` API from `metadata/mod.rs`. `V5IoChunk` adapts v5 RAFS chunk records to the storage crate's generic `BlobChunkInfo` interface.

## Risks
`try_load_v5` must leave the reader at the right place for direct/cached loaders and must not partially mutate state for non-v5 images. V5 cached mode is supported but v6 cached mode is not, so version detection order matters. Prefetch assumes the prefetch table is trustworthy after superblock validation and that zero terminates aligned padding. IO amplification has an explicit TODO for unit coverage and depends on inode-number locality, blob continuity, and gap thresholds; overly aggressive merging could over-read while overly conservative merging loses performance.

## Test Signals
Tests focus on `V5IoChunk`: basic field access, compressed flag behavior, CRC32 gating, `as_any` downcast, and combined flags. Comments identify missing unit tests for `try_load_v5`, `amplify_io`, and `amplify_user_io`.
