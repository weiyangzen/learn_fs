<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSBlockMoveTaskHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSBlockMoveTaskHandler.java

## Purpose

`ExternalSPSBlockMoveTaskHandler` executes external Storage Policy Satisfier block moves by connecting to target DataNodes and issuing DataTransfer `replaceBlock`-style movement through `BlockDispatcher`.

## Important APIs and types

The class implements `BlockMoveTaskHandler`. Key fields include a mover `ExecutorService`, `CompletionService<BlockMovementAttemptFinished>`, `NameNodeConnector`, `SaslDataTransferClient`, `BlockStorageMovementTracker`, `SPSService`, `BlockDispatcher`, and `maxRetry`. `submitMoveTask(BlockMovingInfo)` queues movement work. `cleanUp()` stops the tracker and interrupts the tracker thread.

## Control flow

Construction reads mover-thread and retry configuration, creates a thread pool with a `SynchronousQueue` and `CallerRunsPolicy`, builds SASL and dispatcher helpers, creates the movement tracker, and starts a daemon thread. `submitMoveTask` wraps `BlockMovingInfo` in `BlockMovingTask`. Each task builds an `ExtendedBlock`, obtains a block access token from `KeyManager`, calls test fault injection, and invokes `blkDispatcher.moveBlock(...)` with retry until success or retry exhaustion. Completion results are consumed by `BlockStorageMovementTracker`, whose status handler notifies `SPSService`.

## State and persistence behavior

The handler maintains runtime threads and queues only. Successful block movement mutates DataNode storage placement through DataTransfer operations; NameNode state is updated indirectly through SPS completion callbacks and later reports.

## Dependencies and integration points

It integrates external SPS with `NameNodeConnector`, balancer `KeyManager`, DataTransfer SASL/trusted-channel resolution, `BlockDispatcher`, `BlockStorageMovementTracker`, and `SPSService.notifyStorageMovementAttemptFinishedBlk`.

## Risks and test signals

Risks include caller-thread execution under saturation, incomplete cleanup of `moveExecutor`, retry storms, token mismatch for target storage types, socket leaks inside dispatcher paths, and TODO-noted missing target scheduled-space accounting. Tests should cover successful move, injected retry failures, max retry exhaustion, tracker notification, thread-pool saturation behavior, security-enabled transfers, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSBlockMoveTaskHandler.java -->
