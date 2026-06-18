# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/SwapRestoreTaskTest.java

Purpose: exercises tier-alignment recovery when swaps can exhaust reserved space and require the swap-restore path.

Important APIs and helpers: extends `BaseTierManagementTaskTest`; setup disables promotion, reserves one `BLOCK_SIZE` for alignment, and uses LRU. `testTierAlignment()` fills one upper-tier directory with small blocks and the remaining directories with large blocks, then uses random access to disturb ordering.

Control flow and state: simulated load blocks background activity while directories are populated and accessed. The test first asserts the `BlockIterator` reports tiers are not naturally aligned from first to second tier. After stopping load, it waits until alignment becomes true for all candidate blocks.

Dependencies and integration: uses `BlockStoreLocation`, `BlockOrder.NATURAL`, `StorageDir`, `TieredBlockStoreTestUtils`, `CommonUtils.waitFor`, and background management tasks.

Risks and test signals: random access is intended to make misalignment likely but not mathematically deterministic. A TODO notes the test does not directly prove the swap-restore task was activated. The pass condition still signals end-to-end realignment under constrained swap space.
