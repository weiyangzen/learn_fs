<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java

## Purpose
Abstract base for fixed/reusable resource pools used by the prefetch implementation.

## Important APIs, Types, And Functions
Subclasses implement `acquire`, `tryAcquire`, `release`, and `createNew`. `close()` is a no-op hook, and protected `close(T)` lets subclasses clean individual items.

## Control Flow
This base class defines contracts only. Concrete implementations such as `BoundedResourcePool` provide blocking, non-blocking, and lifecycle behavior.

## State And Persistence
No state is stored in this class.

## Dependencies And Integration Points
`BufferPool` uses a bounded subclass to manage `ByteBuffer` instances. Other resource types can reuse the abstraction if they match the acquire/release model.

## Risks
The base class does not enforce bounds, closed state, null handling, or duplicate release protection. Those guarantees must be supplied by subclasses and callers.

## Test Signals
Tests belong mostly to subclasses: acquire/release ordering, close cleanup, item creation limits, and behavior after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java -->
