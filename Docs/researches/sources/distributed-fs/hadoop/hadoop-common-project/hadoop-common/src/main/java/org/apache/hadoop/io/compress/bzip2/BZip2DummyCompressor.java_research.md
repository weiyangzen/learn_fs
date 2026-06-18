
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyCompressor.java

## Purpose
`BZip2DummyCompressor` is the placeholder compressor type returned when native bzip2 is unavailable and the pure-Java bzip2 codec path does not implement the `Compressor` interface.

## Important APIs and Types
It implements `Compressor`. Most compressor methods throw `UnsupportedOperationException`; `reset()` and `reinit(Configuration)` are no-ops.

## Control Flow
The class is not intended to compress. It exists so `BZip2Codec.getCompressorType()` and `createCompressor()` can satisfy the interface in pure-Java mode while stream creation bypasses compressor-based APIs.

## State and Persistence
It has no fields and no persistent state.

## Dependencies and Integration
Returned by `Bzip2Factory` when `isNativeBzip2Loaded(conf)` is false. It may pass through `CodecPool`, but because pure-Java `BZip2Codec.createOutputStream(out, compressor)` ignores the supplied compressor when native is unavailable, ordinary stream creation still works.

## Risks
Direct callers that borrow a bzip2 compressor in pure-Java mode and call compressor methods will get unsupported-operation failures. The class is not annotated `DoNotPool`, but its no-op reset/reinit makes pooling harmless for placeholder use.

## Test Signals
`BZip2Codec` and stream reuse tests cover pure-Java stream behavior. Failure behavior is implicit in the documented unsupported compressor API for pure-Java bzip2 mode.
