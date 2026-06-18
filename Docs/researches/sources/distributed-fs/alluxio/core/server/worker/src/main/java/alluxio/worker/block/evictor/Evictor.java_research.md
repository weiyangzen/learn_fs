# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/Evictor.java

Purpose: Public deprecated eviction policy interface for producing plans that free worker block-store space.

Important APIs: `Mode` enum with `BEST_EFFORT` and `GUARANTEED`; `Factory.create` instantiates configured `WORKER_EVICTOR_CLASS`; overloaded `freeSpaceWithView` methods produce an `EvictionPlan`.

Control flow: Callers provide requested free bytes, a location range, and a `BlockMetadataEvictorView`. Guaranteed mode may return null if no feasible plan exists; best-effort returns the maximum possible plan.

State and persistence: Interface only. Implementations maintain policy state in memory.

Dependencies and integration: References `LocalBlockStore`, `Allocator`, `BlockMetadataEvictorView`, and `BlockStoreLocation`. Retained for compatibility and emulation.

Risks and test signals: Deprecated in favor of annotator-backed iteration. Tests should verify factory configuration, guaranteed versus best-effort semantics, and invalid location handling.
