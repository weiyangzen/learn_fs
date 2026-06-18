# sources/cloud-native/nydus/utils/src/compress/mod.rs

Purpose: central compression abstraction for Nydus utilities, supporting no compression, LZ4 block, gzip, zstd, streaming gzip/zstd decoders, gzip compressed-size estimation, and feature-gated zran random access.

Important APIs/types/functions: `Algorithm::{None,Lz4Block,GZip,Zstd}` with display, string parsing, numeric conversion, and `is_none`. `compress(src, algorithm)` returns a `Cow<[u8]>` plus boolean indicating whether compression was kept. `decompress(src, dst, algorithm)` reverses block compression. `Decoder<R>` wraps `Read` implementations for no compression, gzip `MultiGzDecoder`, and zstd stream decoder; LZ4 block is explicitly unsupported for streaming. `ZlibDecoder<R>` wraps gzip/zlib multi-member decoding. `compute_compressed_gzip_size` estimates how many compressed bytes may be needed to inflate a gzip member. `zstd_compress` uses zstd default compression level.

Control flow: `compress` short-circuits empty and `None` data, compresses via algorithm-specific path, then discards compressed output if it does not meet `COMPRESSION_MINIMUM_RATIO` (currently 100%, meaning compressed size must be strictly smaller). `decompress` requires exact size match for `None`, delegates to LZ4 FFI, reads exact gzip output into destination, or calls zstd bulk decompression. `Decoder::new` selects stream decoder and panics for LZ4 block.

State and persistence: no durable state. Stream decoders hold reader/decompressor state while reading.

Dependencies and integration points: depends on `flate2`, `zstd`, internal `lz4_standard`, and optional `zlib_random`. Used across RAFS/blob paths for chunk compression and image conversion. Fixture tests read from `tests/texture/zran`.

Risks: `Algorithm::from_str` error text mentions only none/lz4 despite gzip/zstd support. `Decoder::new` panics for LZ4 instead of returning an error, so callers must branch first. `decompress` for gzip uses `read_exact`, requiring callers to know exact uncompressed size. Compression-ratio arithmetic uses integer division and could lose precision for small buffers. Some tests rely on fixture files and may not run in minimal package contexts.

Test signals: extensive unit tests cover gzip/none/zstd/lz4 round trips across sizes, one/two/16/4095/4096/4097-byte cases, stream decoders over fixture gzip files, algorithm parsing/display/numeric conversion, invalid strings, and consistency.
