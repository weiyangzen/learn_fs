# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockCache.java

## Purpose
`TestBlockCache` validates the prefetch block cache implementation, especially argument checks and put/get data preservation.

## Important APIs, Types, And Functions
It tests the `BlockCache` interface via `SingleFilePerBlockCache`, using `put()`, `get()`, `size()`, and `containsBlock()`. `assertBuffersEqual()` compares buffer limits and contents.

## Control Flow
`testArgChecks()` constructs a cache, then expects null buffer put and null statistics construction to fail. `testPutAndGet()` fills a 16-byte buffer, stores block 0, verifies size/contains, reads into a different buffer and compares bytes, then repeats for block 1.

## State And Persistence
The cache may persist block data through local temp files selected by `LocalDirAllocator(HADOOP_TMP_DIR)`. Test buffers are in memory.

## Dependencies And Integration Points
It depends on prefetch cache classes, `EmptyPrefetchingStatistics`, Hadoop `Configuration`, `LocalDirAllocator`, and JUnit assertions.

## Risks
Tests verify only simple capacity-two storage, not eviction, cleanup of cache files, or concurrent access. Buffer position/limit handling is important for correctness.

## Test Signals
Signals are cache size changes, `containsBlock()` results, distinct output buffer identity, and exact byte equality after retrieval.
