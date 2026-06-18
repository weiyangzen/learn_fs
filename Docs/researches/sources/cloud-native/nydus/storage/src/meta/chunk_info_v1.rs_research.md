# sources/cloud-native/nydus/storage/src/meta/chunk_info_v1.rs

## Purpose
Defines the legacy RAFS v6 chunk compression-info v1 on-disk format and implements the common `BlobMetaChunkInfo` trait for range lookup, validation, and compatibility with existing blob metadata.

## Important APIs, Types, And Functions
`BlobChunkInfoV1Ondisk` is a packed 16-byte record with `uncomp_info` and `comp_info` bitfields. Constants define masks and shifts for 40-bit compressed offsets, 4K-aligned uncompressed offsets, and 24-bit encoded sizes. Trait methods get/set compressed and uncompressed offset/size, compute compressed state, return unsupported v2-only feature accessors, and validate against a `BlobCompressionContext`.

## Control Flow
Setters assert field-range compatibility, preserve unrelated bits where needed, and encode size as `size - 1`. Getters decode little-endian fields and return sizes as `encoded + 1`. Validation rejects chunks whose compressed or uncompressed end exceeds blob bounds, zero uncompressed sizes, or inconsistent uncompressed chunks.

## State And Persistence
The type is pure on-disk state. It is created by builders through `BlobMetaChunkArray::add_v1()` and is memory-mapped from `.blob.meta` by `BlobMetaChunkArray::from_file_map()` when `CHUNK_INFO_V2` is absent. V1 has no encryption, CRC32, ZRan, or batch side data.

## Dependencies And Integration Points
Implements the trait declared in `meta/mod.rs` and uses `BlobCompressionContext` plus `BLOB_CCT_CHUNK_SIZE_MASK`. Tests exercise integration through `BlobCompressionContextInfo`, `BlobMetaChunkArray`, `BlobInfo`, `BlobReader`, compression helpers, and temporary files.

## Risks
Invalid calls to unsupported v2-only methods panic through `unimplemented!()`, so generic code must only request ZRan or batch fields when feature flags and chunk format permit it. The bitfield encoding is assert-driven, which is appropriate for builder invariants but can panic if misused on untrusted construction paths.

## Test Signals
Tests cover boundary bitfield encoding, old-format compatibility values, chunk lookup with holes, uncompressed range lookup, metadata reading with no compression and LZ4, and error cases for uncovered ranges. Source size reviewed: 484 lines.
