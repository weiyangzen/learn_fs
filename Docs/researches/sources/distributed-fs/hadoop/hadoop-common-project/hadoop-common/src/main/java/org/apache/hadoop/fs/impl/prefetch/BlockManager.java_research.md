# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManager.java

## Purpose
Simplest block manager abstraction: reads whole blocks into fresh ByteBuffers and offers no-op hooks for prefetching/caching.

## Important APIs, Types, and Functions
Constructor; getBlockData(); get(int); abstract read(ByteBuffer,long,int); release(); requestPrefetch(); cancelPrefetches(); requestCaching(); close().

## Control Flow
get validates block number, allocates a heap buffer sized from BlockData, invokes subclass read, flips the buffer, and wraps it in BufferData. Optional hooks are no-ops in the base class.

## State and Persistence Behavior
Stores BlockData only. Persistent state depends on subclass read source; base does not cache.

## Dependencies and Integration Points
Base class for prefetch/caching block managers.

## Risks and Test Signals
Risks are short reads not checked by base get, heap allocation per block, and no-op release. Tests should simulate read implementations including short/error reads.
