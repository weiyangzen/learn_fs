# sources/cloud-native/nydus/storage/src/meta/zran.rs

## Purpose
Implements builder-side ZRan metadata generation and on-disk inflate contexts used to randomly access gzip/zlib streams in RAFS blobs.

## Important APIs, Types, And Functions
`ZranInflateContext` is a 40-byte packed record containing compressed stream offset/size, uncompressed stream offset/size, dictionary table offset/size, and zlib bit context. It exposes little-endian getters, `as_slice()`, and conversion to `nydus_utils::compress::zlib_random::ZranContext`. `ZranContextGenerator<R>` wraps `ZranGenerator` and `ZranReader`, tracks aligned uncompressed position, implements `Read`, and emits v2 chunk records and serialized ZRan context/dictionary data.

## Control Flow
Construction creates a `ZranReader`, configures min/max compressed and uncompressed sizes around `RAFS_DEFAULT_CHUNK_SIZE`, and starts with uncompressed position zero. Callers call `start_chunk()`, read through the generator, and call `finish_chunk()` to get a v2 chunk marked compressed and ZRan with context index and offset. `to_vec()` writes all fixed-size context records first, then appends dictionaries in record order.

## State And Persistence
Generator state is in memory while building. Persisted state is a sequence of `ZranInflateContext` records plus dictionary bytes stored after the chunk table in the blob compression context area. Runtime loads these through `BlobCompressionContext.zran_info_array` and `zran_dict_table`.

## Dependencies And Integration Points
Depends on `nydus_utils::compress::zlib_random`, `BlobChunkInfoV2Ondisk`, the `BlobMetaChunkInfo` setter trait, `round_up_4k()`, and `RAFS_DEFAULT_CHUNK_SIZE`. `meta/mod.rs` validates ZRan chunk indices/ranges and serves contexts to decompression paths.

## Risks
The unsafe byte slice depends on packed layout remaining 40 bytes. `finish_chunk()` increments uncompressed position by 4K-aligned chunk length, so callers must coordinate RAFS chunk alignment with tar/gzip reads. Dictionary offset accumulation is `u64`, but individual dictionary sizes are stored as `u32`.

## Test Signals
Tests verify context getters, serialized length, conversion to runtime `ZranContext`, zero values, generating chunks from a gzip tar fixture, and that serialized data includes fixed contexts plus dictionaries. Source size reviewed: 399 lines.
