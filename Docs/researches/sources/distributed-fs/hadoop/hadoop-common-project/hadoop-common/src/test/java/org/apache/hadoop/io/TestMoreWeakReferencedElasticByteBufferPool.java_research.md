<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java

## Purpose
Additional non-parameterized tests for `WeakReferencedElasticByteBufferPool`, focusing on mixed direct/heap buffers and invalid size/null inputs.

## Important APIs, Types, and Functions
Uses `WeakReferencedElasticByteBufferPool.getBuffer`, `putBuffer`, `release`, and `getCurrentBuffersCount(boolean direct)`. `assertBufferCounts()` asserts direct and heap pool counts with AssertJ. `LambdaTestUtils.intercept` checks expected exceptions.

## Control Flow and State
`testMixedBuffersInPool()` obtains direct and heap buffers of several sizes, verifies the pool count is zero while checked out, returns them in mixed order, checks direct/heap counts, then releases and checks zero. `testUnexpectedBufferSizes()` verifies zero-length direct buffers overflow on write, negative length is rejected, and null buffer return throws.

## Dependencies and Integration Points
Integrates Java NIO `ByteBuffer`, Hadoop test base, and byte buffer pool counters. This pool can be used by IO paths that reuse buffers without strong references.

## Risks and Test Signals
Risks are count accuracy across direct/heap pools, weak-reference cleanup not deterministically exercised, zero/negative size edge cases, and null input handling. Signals are explicit count transitions and exception types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestMoreWeakReferencedElasticByteBufferPool.java -->
