
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DoNotPool.java

## Purpose
`DoNotPool` is a marker annotation for compressor/decompressor classes that must not be reused through `CodecPool`.

## Important APIs and Types
It is a runtime-retained, type-targeted, documented annotation with no elements.

## Control Flow
`CodecPool` checks for this annotation when borrowing counts and returning instances. Annotated instances are ended instead of reset and stored.

## State and Persistence
The annotation adds class metadata only; no runtime mutable state or persistence.

## Dependencies and Integration
Used by `CodecPool` and by implementations such as built-in gzip classes where return-to-pool should close resources rather than permit reuse.

## Risks
Omitting the annotation from non-reusable implementations can cause stale state or closed-resource reuse. Adding it to reusable native wrappers can reduce performance by defeating pooling.

## Test Signals
`TestCodecPool` explicitly verifies annotated built-in gzip compressor/decompressor instances are not usable after return and are not pooled.
