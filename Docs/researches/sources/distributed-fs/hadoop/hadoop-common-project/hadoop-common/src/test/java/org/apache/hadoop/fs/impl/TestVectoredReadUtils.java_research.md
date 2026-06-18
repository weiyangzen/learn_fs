# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestVectoredReadUtils.java

## Purpose
`TestVectoredReadUtils` validates the low-level helper logic behind Hadoop vectored reads: buffer slicing, range sorting/validation, range merging, positioned reads into heap/direct buffers, future completion, EOF validation, and vector buffer pool adaptation.

## Important APIs, Types, And Functions
Production APIs under test include `VectoredReadUtils.sliceTo()`, `roundDown()`, `roundUp()`, `sortRangeList()`, `sortRanges()`, `validateAndSortRanges()`, `isOrderedDisjoint()`, `mergeSortedRanges()`, `readRangeFrom()`, and `readVectored()`, plus `CombinedFileRange` and `VectorIOBufferPool`. The local `Stream` interface combines `PositionedReadable` and `ByteBufferPositionedReadable`.

## Control Flow
Early tests validate slicing without copies when offsets match and shared backing arrays when slicing subranges. Sorting/merging tests construct overlapping, duplicate, consecutive, gapped, and aligned ranges, then assert merged `CombinedFileRange` start/length/underlying references. Read tests use Mockito streams to fill buffers or throw IOEs and then assert futures complete successfully or exceptionally. EOF tests validate negative offsets, negative lengths, reads at/over EOF, whole-file reads, and zero-length vectored reads. Buffer-pool tests adapt an `ElasticByteBufferPool` to vector IO get/put lambdas and confirm release behavior.

## State And Persistence
All state is in memory: `ByteBuffer`s, `FileRange` futures, mocked streams, and buffer pools. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on Hadoop vectored read abstractions, Mockito, AssertJ, Java futures, `ByteBufferPool`, and test future assertions. Filesystem stream implementations rely on this utility for correctness and efficient coalescing.

## Risks
Range merging must not merge overlapping or duplicate user ranges incorrectly, because returned buffers must map back to original references and offsets. Direct vs heap allocation must both work. EOF validation must match contract tests or backends will disagree on exception timing.

## Test Signals
Signals include exact merged ranges, preserved underlying references, expected exceptions for invalid ranges, completed/failed futures on success/IOE, buffers filled with deterministic bytes, zero-length range buffers with limit 0, and buffer-pool size changes after put/get/release.
