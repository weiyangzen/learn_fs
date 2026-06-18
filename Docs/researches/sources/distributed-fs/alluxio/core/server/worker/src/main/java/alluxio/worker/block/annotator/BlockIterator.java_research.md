# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/BlockIterator.java

Purpose: Provides the abstraction for ordered block traversal used by eviction, promotion, alignment, and swap calculations.

Important APIs: `getIterator` returns block IDs for a location and order; `getIntersectionList` builds a bounded ordered intersection candidate list; `getSwaps` returns paired block IDs to swap between locations; `aligned` detects tier overlap; `getListeners` exposes store event listeners that keep iterator state current.

Control flow: Management tasks query this interface for ranked blocks and pass filters for pinned, locked, or otherwise non-evictable blocks. Implementations may be event-driven (`DefaultBlockIterator`) or evictor-emulated (`EmulatingBlockIterator`).

State and persistence: Interface only. Implementations own in-memory ranking state and do not persist ordering to disk.

Dependencies and integration: Integrates with `BlockStoreLocation`, `BlockOrder`, `BlockStoreEventListener`, and `Pair`. Tier management depends heavily on `getSwaps` and `aligned`.

Risks and test signals: The filter function returns true for blocks to exclude in current implementations, so call sites need clear tests to avoid inverted predicates. Exercise empty locations, any-tier locations, reverse order, and partial intersections.
