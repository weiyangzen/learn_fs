# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BoundedResourcePool.java

## Purpose
Fixed-size resource pool that lazily creates resources, reuses returned resources, and blocks when exhausted.

## Important APIs, Types, and Functions
acquire(), tryAcquire(), release(), close(), numCreated(), numAvailable(), toString(), abstract createNew(), protected close(T).

## Control Flow
acquire first polls available items, then creates a new item under capacity, otherwise blocks on the queue. tryAcquire follows the same path but returns null instead of blocking. release validates identity membership, ignores duplicate release already in queue, then puts the item back. close calls close(item) for all created resources and clears structures.

## State and Persistence Behavior
Stores capacity, ArrayBlockingQueue, and identity-based set of created resources. After close, fields are nulled.

## Dependencies and Integration Points
Base for buffer/cache pools in prefetching code.

## Risks and Test Signals
Risks are use-after-close NPEs, release blocking invariant, interrupted acquire returning null, and duplicate-release semantics. Tests should cover capacity, blocking/try behavior, foreign resource rejection, duplicate release, and close cleanup.
