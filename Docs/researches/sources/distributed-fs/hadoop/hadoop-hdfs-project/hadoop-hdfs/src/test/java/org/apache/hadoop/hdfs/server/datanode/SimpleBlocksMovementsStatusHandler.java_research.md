# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimpleBlocksMovementsStatusHandler.java

Purpose: this simple test implementation of `BlocksMovementsStatusHandler` collects completed storage-policy-satisfier block movement attempts so tests can inspect and remove them later.

Important APIs and types: `BlocksMovementsStatusHandler`, `BlockMovementAttemptFinished`, Hadoop `Block`, `List`, and `Collections.unmodifiableList`.

Control flow: `handle` extracts the block from a completed movement event and appends it to `blockIdVsMovementStatus` under synchronization. `getMoveAttemptFinishedBlocks` returns an empty mutable list if no blocks are present, otherwise an unmodifiable view of the backing list. `remove` removes supplied blocks from the tracking list if the argument is non-null. `removeAll` clears the list under synchronization.

State and persistence: state is an in-memory `ArrayList<Block>`. There is no disk or network persistence. Synchronization is partial: add, read, and clear synchronize on the list, but `remove` calls `removeAll` without the same lock.

Dependencies and integration points: this class plugs into DataNode/SPS tests that need a lightweight movement-status sink instead of the production heartbeat path to the NameNode.

Risks: `getMoveAttemptFinishedBlocks` can return an unmodifiable view of the live backing list, so later mutations are visible and concurrent iteration may still be unsafe. `remove` is not synchronized, unlike other mutating operations. The field name says status but stores only block IDs, so it does not preserve success/failure detail.

Test signals: no local tests exist. It is validated indirectly when SPS/DataNode tests can observe expected movement-completion blocks and clear them.
