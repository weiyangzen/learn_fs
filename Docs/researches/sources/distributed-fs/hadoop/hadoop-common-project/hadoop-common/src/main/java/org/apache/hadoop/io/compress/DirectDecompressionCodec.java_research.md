
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressionCodec.java

## Purpose
`DirectDecompressionCodec` marks codecs that can create direct `ByteBuffer` decompressors for zero-copy or native-buffer workflows.

## Important APIs and Types
It extends `CompressionCodec` and adds `createDirectDecompressor()`.

## Control Flow
There is no implementation logic; concrete codecs decide whether direct decompression is supported and return either a direct decompressor instance or, in some implementations, `null` when unavailable.

## State and Persistence
The interface has no state or persistence.

## Dependencies and Integration
Implemented by `DefaultCodec`, `GzipCodec`, `SnappyCodec`, and `ZStandardCodec`. Downstream readers can check this interface before using `DirectDecompressor`.

## Risks
The contract does not require non-null return, so callers must handle unavailable native/direct support. Direct decompression has stricter buffer requirements than byte-array streams.

## Test Signals
Snappy and ZStandard tests cover direct decompressor classes. Gzip/default direct behavior depends on native zlib availability and is exercised through zlib-related tests.
