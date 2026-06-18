<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDirectBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDirectBufferPool.java

## Purpose

`TestDirectBufferPool.java` validates pooling, reset, and weak-reference cleanup behavior for direct byte buffers.

## Important APIs, Types, and Functions

It uses `DirectBufferPool.getBuffer`, `returnBuffer`, and `countBuffersOfSize`, plus `ByteBuffer` capacity/remaining checks.

## Control Flow

Tests allocate buffers, return them, assert reuse for same size, assert a second outstanding request returns a different buffer, verify returned buffers are cleared/reset, and force GC to ensure stale weak references are removed on later pool access.

## State and Persistence Behavior

State lives in the pool's in-memory weak-reference buckets. No persistence exists.

## Dependencies and Integration Points

It integrates with Hadoop direct-buffer pooling and Java GC/weak-reference behavior.

## Risks and Edge Cases

GC-dependent assertions can be flaky. Buffer position/limit reset is essential to avoid data corruption in users.

## Test Signals

Signals include object identity reuse, non-reuse while checked out, remaining reset to capacity, and weak-reference bucket count after GC-triggered cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDirectBufferPool.java -->
