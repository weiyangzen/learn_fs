# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockCache.java

## Purpose
Interface for local block cache implementations used by prefetching input streams.

## Important APIs, Types, and Functions
containsBlock(), blocks(), size(), get(blockNumber, ByteBuffer), put(blockNumber, ByteBuffer, Configuration, LocalDirAllocator), close().

## Control Flow
Implementations decide storage. get copies cached content into caller buffer; put persists one block into cache using configuration and local directory allocation.

## State and Persistence Behavior
Interface has no state. Implementations may persist cache files on local disk.

## Dependencies and Integration Points
Depends on ByteBuffer, Configuration, LocalDirAllocator. Used by caching/prefetch block managers.

## Risks and Test Signals
Tests for implementations should cover block presence, buffer position/limit, overwrite behavior, close cleanup, and local directory failures.
