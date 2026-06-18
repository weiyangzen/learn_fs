<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestChunkedArrayList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestChunkedArrayList.java

## Purpose

`TestChunkedArrayList.java` validates `ChunkedArrayList` growth, iteration, removal, indexed access after removal, and rough insertion performance.

## Important APIs, Types, and Functions

Tests cover `add`, `isEmpty`, `size`, `getNumChunks`, `getMaxChunkSize`, iterator traversal/removal, `get`, and `StopWatch`.

## Control Flow

The suite adds tens of thousands to one million elements, verifies chunking and order, removes even elements through an iterator, removes remaining odd elements, then checks indexed access shifts after removals.

## State and Persistence Behavior

State is in-memory list chunks and iterators. The performance test prints elapsed times but persists nothing.

## Dependencies and Integration Points

It integrates with `ChunkedArrayList`, Java `ArrayList`, `Iterator`, `StopWatch`, and JUnit 5.

## Risks and Edge Cases

Large allocation and `System.gc()` calls make the performance test environment-sensitive. Iterator removal across chunk boundaries is the key correctness risk.

## Test Signals

Signals include expected size/chunk count, preserved iteration order, successful removal-to-empty, and indexed values after iterator removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestChunkedArrayList.java -->
