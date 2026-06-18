
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressor.java

## Purpose
`DirectDecompressor` defines the direct `ByteBuffer` decompression operation used by codecs with native or direct-buffer paths.

## Important APIs and Types
The single method is `decompress(ByteBuffer src, ByteBuffer dst)`. The contract says it moves source and destination positions by bytes consumed/written, does not modify limits, and may require multiple calls.

## Control Flow
Implementations read from `src` and write to `dst` using internal codec state. Some block codecs require enough destination space for a complete decompressed block.

## State and Persistence
The interface has no state. Implementations may hold codec context between calls and must be reset or recreated according to their own contracts.

## Dependencies and Integration
Implemented by direct variants in zlib, Snappy, and ZStandard packages. Created by codecs implementing `DirectDecompressionCodec`.

## Risks
The method assumes non-null direct buffers with remaining space/data; implementations often reject heap-backed arrays. Callers must handle partial consumption and avoid assuming one call completes a stream.

## Test Signals
`TestSnappyCompressorDecompressor` and `TestZStandardCompressorDecompressor` include direct decompressor paths and error cases.
