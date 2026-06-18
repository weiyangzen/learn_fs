# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBoundedResourcePool.java

## Purpose
`TestBoundedResourcePool` validates the generic bounded resource pool used by prefetch buffers/resources.

## Important APIs, Types, And Functions
The nested `BufferPool` extends `BoundedResourcePool<ByteBuffer>` and implements `createNew()` with `ByteBuffer.allocate(10)`. Tests use `acquire()`, `release()`, `numCreated()`, and `numAvailable()`.

## Control Flow
Argument tests check invalid pool sizes, null release, and releasing an item not owned by the pool. Single acquire/release verifies a released buffer is reused without creating another. Multiple acquire/release obtains the full pool, tracks identity uniqueness, releases each buffer idempotently, and reacquires the same identities.

## State And Persistence
State is in-memory pool ownership, available count, and created count. No persistence.

## Dependencies And Integration Points
It depends on `BoundedResourcePool`, `ByteBuffer`, identity sets, and JUnit assertions.

## Risks
Ownership tracking must distinguish equal resources by identity. Double release should be harmless but releasing foreign resources must fail.

## Test Signals
Signals are created/available counters, identity reuse, rejection of foreign/null items, and no counter inflation on repeated release.
