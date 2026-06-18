
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplittableCompressionCodec.java

## Purpose
`SplittableCompressionCodec` marks codecs that can decompress from arbitrary or codec-adjusted positions in a compressed stream, enabling parallel processing of compressed files.

## Important APIs and Types
It extends `CompressionCodec`, defines `READ_MODE { CONTINUOUS, BYBLOCK }`, and declares split-aware `createInputStream(InputStream, Decompressor, long, long, READ_MODE)`.

## Control Flow
Implementations seek or scan the compressed stream to a valid boundary and return a `SplitCompressionInputStream`. `READ_MODE.BYBLOCK` allows codecs such as bzip2 to surface block-boundary events, while `CONTINUOUS` hides block structure.

## State and Persistence
The interface has no state. Implementations maintain split offset and block-state tracking.

## Dependencies and Integration
Implemented by `BZip2Codec` in this subset. Hadoop input formats and record readers use this interface to split compressed inputs safely.

## Risks
The contract is difficult for codecs with stream-global state. Implementations must coordinate compressed positions with record boundaries, or consumers can miss/duplicate records.

## Test Signals
`TestBZip2Codec` directly exercises BYBLOCK and CONTINUOUS mode semantics for the bzip2 implementation.
