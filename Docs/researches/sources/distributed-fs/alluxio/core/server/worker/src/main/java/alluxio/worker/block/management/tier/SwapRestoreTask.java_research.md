# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/tier/SwapRestoreTask.java

Purpose: Restores reserved swap space after alignment swaps fail or consume too much reserved capacity.

Important APIs: `run`; private `getSwapRestorePlan`; private `getBalancingTransfersList`.

Control flow: The restore plan cascades bytes beyond reserve down tiers, removing blocks from the last tier and moving blocks down from higher tiers. After removals and flush transfers, balancing scans each directory whose available bytes are below reserved bytes and moves cold blocks to sibling dirs with enough surplus.

State and persistence: Uses transient plan lists and storage view mark accounting. Removals and moves mutate block store metadata and files.

Dependencies and integration: Uses `LocalBlockStore`, `BlockMetadataEvictorView`, `StorageTierAssoc`, `StorageDirEvictorView`, `BlockIterator`, `BlockTransferExecutor`, and internal sessions.

Risks and test signals: Balancing does not evict if no sibling has room and may leave reserved space unrecovered. Tests should cover cascading math, last-tier removals, sibling balance mark accounting, missing metadata, and partial failure counts.
