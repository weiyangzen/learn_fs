# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/annotator/EmulatingBlockIterator.java

Purpose: Adapter that exposes deprecated `Evictor` ordering through the newer `BlockIterator` interface.

Important APIs: Constructor accepts `BlockMetadataManager` and `Evictor`; `getIterator` builds a best-effort eviction plan and extracts ordered move or evict block IDs; intersection, swap, and alignment APIs return empty or false because they cannot be derived from old evictors.

Control flow: `initEvictorConfiguration` computes per-tier reserved-space thresholds from configured high and low watermarks. `getIterator` invokes `freeSpaceWithView` against a fresh `BlockMetadataEvictorView`, extracts `toMove` source IDs if present or `toEvict` IDs otherwise, and reverses for reverse order.

State and persistence: Keeps the metadata manager, evictor, and an in-memory `mReservedSpaces` map. No persistent state.

Dependencies and integration: Depends on deprecated `Evictor`, `EvictionPlan`, `BlockMetadataEvictorView`, tier association, and watermark properties. It also forwards listeners if the evictor implements `BlockStoreEventListener`.

Risks and test signals: The adapter assumes plan list order reflects eviction order and cannot support tier alignment. Tests should cover watermark validation, ANY_TIER reservation accumulation, reverse order, null plan handling expectations, and listener forwarding for old evictors.
