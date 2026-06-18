# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageEvictorTest.java

Purpose: randomized differential test for `BlockPageEvictor`, ensuring block pinning wraps underlying page evictors correctly.

Important APIs and helpers: parameterized data combines `LRUCacheEvictor`, `LFUCacheEvictor`, and `FIFOCacheEvictor` with block/page/pinned-block counts. `runAndInspect` applies random get/put/delete access sequences to both the wrapped evictor and a truth supplier. `pinnedBlocks` uses `addPinnedBlock` and `removePinnedBlock`.

Control flow and state: for each parameter set, a fixed-seed random stream produces many page operations. Without pins, wrapped eviction should match inner eviction. With pins, eviction is compared against `inner.evictMatching` excluding pinned block IDs, then pins are removed and normal behavior resumes.

Dependencies and integration: depends on Alluxio cache evictors, `PageId`, `BlockPageEvictor`, and reflection utility construction.

Risks and test signals: randomized but deterministic by seed; strong signal across eviction algorithms. It checks selected eviction result, not full internal queues.
