
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyDecompressor.java

## Purpose
`BZip2DummyDecompressor` is the placeholder decompressor type returned when native bzip2 is unavailable and pure-Java bzip2 decompression does not use the `Decompressor` interface.

## Important APIs and Types
It implements `Decompressor`. Most methods throw `UnsupportedOperationException`; `reset()` is a no-op.

## Control Flow
It is not used to actually decompress data in pure-Java `BZip2Codec` stream creation; the codec constructs `BZip2CompressionInputStream` around `CBZip2InputStream` instead.

## State and Persistence
It has no fields and no persistent state.

## Dependencies and Integration
Returned by `Bzip2Factory` when native bzip2 is not loaded. `CodecPool.getDecompressor(codec)` may return it, and `BZip2Codec.createInputStream(in, decompressor)` ignores it in pure-Java mode.

## Risks
Direct decompressor API use in pure-Java bzip2 mode throws. As with the dummy compressor, it is not marked `DoNotPool`, but the no-op reset makes placeholder pooling low risk.

## Test Signals
`TestBZip2Codec` obtains a decompressor from `CodecPool` and passes it into split input creation, validating that pure-Java bzip2 ignores the dummy for actual reads.
