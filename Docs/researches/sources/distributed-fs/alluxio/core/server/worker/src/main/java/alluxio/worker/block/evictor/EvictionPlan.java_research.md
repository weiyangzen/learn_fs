# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionPlan.java

Purpose: Data container listing block transfers and block removals required to free space.

Important APIs: Constructor validates non-null move and evict lists; `toMove`, `toEvict`, `isEmpty`, and `toString`.

Control flow: Evictors append to the contained mutable lists while building a plan. Callers then execute moves and evictions in order.

State and persistence: Stores caller-provided lists and exposes them directly. Thread-safe annotation applies to object reference safety, not immutability of list contents.

Dependencies and integration: Uses `BlockTransferInfo`, `Pair<Long,BlockStoreLocation>`, and Guava preconditions. Consumed by block store eviction and emulated iterators.

Risks and test signals: Direct list exposure means later mutations affect the plan. Tests should cover empty plan semantics, null rejection, and execution behavior when move and evict lists are both populated.
