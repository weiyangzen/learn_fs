# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/VectoredReadUtils.java

## Purpose
Utility class for Hadoop vectored IO: validates ranges, supplies a default synchronous vectored read implementation, handles direct-buffer fallback reads, sorts/merges ranges, slices combined reads, and answers default vector capability probes.

## Important APIs, Types, and Functions
Key APIs: validateRangeRequest(), validateAndSortRanges(), readVectored(), readRangeFrom(), readInDirectBuffer(), isOrderedDisjoint(), roundDown(), roundUp(), mergeSortedRanges(), sliceTo(), hasVectorIOCapability().

## Control Flow
Default readVectored validates/sorts ranges then sets each FileRange future from readRangeFrom. readRangeFrom allocates a ByteBuffer, uses ByteBufferPositionedReadable when available, otherwise falls back to PositionedReadable array reads or chunked direct-buffer reads with a 64 KiB temp buffer. Range validation sorts inputs, rejects overlaps, negative lengths, negative offsets, and optional file-length overruns. mergeSortedRanges rounds to chunk boundaries and coalesces nearby reads through CombinedFileRange.

## State and Persistence Behavior
No durable state. It creates ByteBuffers/futures and calls a release consumer on read failure so caller-owned pools can reclaim buffers.

## Dependencies and Integration Points
Depends on FileRange, PositionedReadable, ByteBufferPositionedReadable, CombinedFileRange, StreamCapabilities, CompletableFuture, and Function4RaisingIOE. Filesystem implementations use it for common vector IO behavior.

## Risks and Test Signals
Risks include overlap math, integer truncation when combined ranges exceed int length, direct-buffer position/limit mistakes, and futures completed with leaked buffers on failure. Tests should cover empty lists, EOF boundaries, direct and heap buffers, merging thresholds, slicing offsets, and capability casing.
