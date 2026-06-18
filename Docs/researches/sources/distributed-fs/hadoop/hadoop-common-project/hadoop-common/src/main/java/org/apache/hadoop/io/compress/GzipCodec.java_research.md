
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/GzipCodec.java

## Purpose
`GzipCodec` provides gzip-format compression/decompression by specializing `DefaultCodec` with gzip headers and gzip-capable zlib or built-in implementations.

## Important APIs and Types
It overrides stream creation, compressor/decompressor type and creation, direct decompressor creation, and default extension. Nested `GzipZlibCompressor` and `GzipZlibDecompressor` specialize zlib wrappers for gzip format and autodetect gzip/zlib input.

## Control Flow
No-argument stream creation uses `CodecPool`. Supplied-compressor output creates a `CompressorStream` when the compressor is non-null, otherwise delegates. Compressor and decompressor creation branch on `ZlibFactory.isNativeZlibLoaded(conf)` to choose native zlib gzip wrappers or built-in gzip classes. Direct decompression is available only with native zlib.

## State and Persistence
State is inherited `conf`; nested zlib wrappers own native stream state. The output format uses `.gz` and gzip framing.

## Dependencies and Integration
Depends on zlib package classes, `IO_FILE_BUFFER_SIZE_*`, and `CodecConstants.GZIP_CODEC_EXTENSION`. Used by default codec discovery, SequenceFile append tests, and output formats requiring gzip compression.

## Risks
Native and built-in paths differ in pooling behavior and direct decompression support. Built-in gzip compressor/decompressor types are annotated not to pool in their classes, so lifecycle differs from native wrappers. `createInputStream(in, null)` creates a decompressor directly and does not attach it to pool tracking.

## Test Signals
`TestGzipCodec`, `TestCodecPool`, `TestCodecFactory`, `TestSequenceFileAppend`, and stream reuse tests cover gzip stream creation, pooling, discovery, and reset behavior.
