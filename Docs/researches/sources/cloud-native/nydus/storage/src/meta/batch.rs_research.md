# sources/cloud-native/nydus/storage/src/meta/batch.rs

## Purpose
Implements on-disk batch-inflate metadata and a builder-side helper for RAFS v6 batch chunks, where several small logical chunks share one compressed batch payload.

## Important APIs, Types, And Functions
`BatchInflateContext` is a 40-byte `#[repr(C, packed)]` record with little-endian compressed batch size and unaligned uncompressed batch size plus reserved fields. Getters/setters normalize endian format, and `as_slice()` exposes the packed record as bytes for serialization. `BatchContextGenerator` buffers uncompressed small-chunk data, records completed batch contexts, and emits `BlobChunkInfoV2Ondisk` entries via `generate_chunk_info()`.

## Control Flow
Builders append chunk bytes into `chunk_data_buf`, call `generate_chunk_info()` before dumping a small chunk so the v2 chunk receives a batch flag, batch index, and offset inside the batch buffer, then call `add_context()` after a batch payload is compressed. `to_vec()` serializes all contexts in insertion order for placement after the chunk table.

## State And Persistence
State is process-local until serialized: `chunk_data_buf` holds pending uncompressed batch data and `contexts` holds packed records later persisted inside the blob meta area. Generated v2 chunk records store zero per-chunk compressed size, the shared compressed offset, and per-chunk placement in the batch buffer.

## Dependencies And Integration Points
Depends on `BlobChunkInfoV2Ondisk` and `BlobMetaChunkInfo` setters from `meta/chunk_info_v2.rs` and is re-exported by `meta/mod.rs`. Runtime validation and lookup consume these contexts through `BlobCompressionContext.batch_info_array`.

## Risks
The unsafe byte view depends on exact packed layout and little-endian setters. `add_context()` casts `chunk_data_buf_len()` to `u32`, so callers must keep batch buffers within the on-disk field limit. Batch chunks disable CRC32 because the v2 `data` field is already used for batch index and in-batch offset.

## Test Signals
Unit tests verify endian setters, 40-byte serialization, generator buffer lifecycle, context serialization through raw packed reconstruction, and that generated chunks are marked batch. Source size reviewed: 204 lines.
