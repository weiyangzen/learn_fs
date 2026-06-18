# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/AbstractEvictor.java

Purpose: Deprecated base implementation for eviction policies, providing recursive cascading eviction across storage tiers.

Important APIs: Constructor takes `BlockMetadataEvictorView` and `Allocator`; `freeSpaceWithView` builds an `EvictionPlan`; protected `cascadingEvict` selects candidate blocks and recursively moves them down-tier or evicts from the last tier; subclass API is `getBlockIterator`.

Control flow: The evictor first checks whether a directory already has requested space. If not, it scans blocks in policy order, accumulates candidate blocks per directory, picks the directory with maximum reclaimable space, then tries to allocate each candidate in the next tier. Failed next-tier allocation triggers recursive eviction; last-tier candidates are evicted.

State and persistence: Keeps mutable metadata view and allocator references. It marks projected moves in `StorageDirEvictorView` during plan generation and clears marks before returning.

Dependencies and integration: Depends on `BlockMetadataEvictorView`, storage views, `Allocator`, `EvictionDirCandidates`, `EvictionPlan`, and `BlockTransferInfo`. Used by deprecated `LRUEvictor` and by `EmulatingBlockIterator`.

Risks and test signals: Not thread-safe and deprecated. BEST_EFFORT can return a plan even when guaranteed space is not reached. Tests should cover recursive cascading, stale block removal from iterators, mark cleanup, exact/any location handling, and null plan behavior.
