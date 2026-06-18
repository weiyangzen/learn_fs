# sources/cloud-native/nydus/storage/src/meta/chunk_info_v2.rs

## Purpose
Defines the RAFS v6 chunk compression-info v2 on-disk format, including flags and attached data used for compressed, encrypted, CRC, ZRan, and batch chunks.

## Important APIs, Types, And Functions
`BlobChunkInfoV2Ondisk` is a packed 24-byte record with uncompressed info, compressed info, and a `data` field. Private setters toggle flags and populate `data` as either CRC32, ZRan index/offset, or batch index/in-batch offset. The `BlobMetaChunkInfo` implementation exposes offsets, sizes, flags, side-data accessors, CRC/data accessors, and `validate()`. `Display` prints decoded offsets, sizes, data, and flags.

## Control Flow
Offset and size setters encode into bounded bitfields: compressed offset is 40 bits, compressed size is 24 bits, uncompressed offset is 4K-granular, and uncompressed size is encoded as `size - 1`. Validation first checks common range and consistency constraints, logs unknown flags once per flag byte, then performs feature-specific validation for ZRan contexts and batch contexts.

## State And Persistence
The record is persisted in blob metadata and memory-mapped into `BlobMetaChunkArray::V2`. The `data` field is multiplexed, so producers must ensure mutually coherent flags: CRC32 uses the low 32 bits, ZRan uses high 32-bit context index plus low 32-bit offset, and batch uses high 32-bit batch index plus low 32-bit uncompressed offset in the batch buffer.

## Dependencies And Integration Points
Used by `batch.rs`, `zran.rs`, and `meta/mod.rs`; validation depends on `BlobFeatures`, `BlobCompressionContext.zran_info_array`, and `batch_info_array`. It integrates with range lookup through the `BlobMetaChunkInfo` trait and with blob feature gates for `ZRAN` and `BATCH`.

## Risks
Unknown flags are only warned, not rejected, which preserves forward compatibility but may hide producer bugs. CRC32 validation rejects a set CRC flag with value zero, so legitimate zero CRC32 values would be impossible under this format. Batch validation checks context index and in-batch bounds but relies on correct shared compressed offsets across same-batch chunks.

## Test Signals
Tests cover field encoding limits, flag toggling, ZRan and batch side-data accessors, old-format compatibility, hole-aware chunk lookup, validation failures for missing ZRan features/context arrays, encrypted behavior, and unknown flag tolerance. Source size reviewed: 544 lines.
