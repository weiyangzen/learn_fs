# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/PromoteTaskTest.java

Purpose: integration test for the tier-management promotion task moving blocks from a lower tier into available higher-tier space.

Important APIs and helpers: extends `BaseTierManagementTaskTest`; `before()` reloads configuration, disables tier alignment, sets `WORKER_MANAGEMENT_TIER_PROMOTE_QUOTA_PERCENT`, and calls `init()`. `testBlockPromotion()` uses `TieredBlockStoreTestUtils.cache` and `CommonUtils.waitFor`.

Control flow and state: the test starts simulated load to defer management work, fills lower-tier `mTestDir3` with committed blocks, asserts upper-tier directories are empty, then stops the load. It computes the expected first-tier used-byte limit from tier capacity and the promotion quota, then waits until committed bytes in `mTestDir1` plus `mTestDir2` match that quota.

Dependencies and integration: uses real tiered block-store metadata, global worker management properties, and the background task scheduler/load detector.

Risks and test signals: timing depends on a 60-second wait and background task scheduling. It validates byte-level promotion quota behavior, but not which specific blocks were promoted or ordering under LRU.
