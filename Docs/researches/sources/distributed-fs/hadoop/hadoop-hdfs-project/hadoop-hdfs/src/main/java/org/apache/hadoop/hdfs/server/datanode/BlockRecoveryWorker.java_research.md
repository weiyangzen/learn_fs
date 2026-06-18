# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockRecoveryWorker.java

## Purpose

`BlockRecoveryWorker` executes NameNode-issued block recovery commands on a DataNode. It coordinates with peer DataNodes through `InterDatanodeProtocol`, chooses recoverable replicas, updates replicas under recovery to a new generation stamp and length, and commits the synchronized result back to the active NameNode. It supports both contiguous replicated blocks and erasure-coded striped block groups.

## Important APIs, types, and functions

- `recoverBlocks(String who, Collection<RecoveringBlock> blocks)` starts a `Daemon` that processes recovery commands and maintains the DataNode block recovery worker metric.
- `BlockRecord` binds a `DatanodeID`, `InterDatanodeProtocol` proxy, `ReplicaRecoveryInfo`, and returned storage ID. `updateReplicaUnderRecovery` calls the remote or local DataNode to truncate/update the replica.
- `RecoveryTaskContiguous.recover()` asks each target DataNode to `initReplicaRecovery`, filters invalid generation stamps, zero-length replicas, and weak replica states, then calls `syncBlock`.
- `RecoveryTaskContiguous.syncBlock(...)` selects the best replica state, computes the recovered length, updates participating replicas, and calls `commitBlockSynchronization`.
- `RecoveryTaskStriped.recover()` maps internal block IDs to the longest valid replica, computes a safe block-group length, truncates internal blocks that can participate, and commits a block-group synchronization result.
- `getActiveNamenodeForBP`, `getDatanodeID`, and `callInitReplicaRecovery` isolate block-pool service lookup and RemoteException unwrapping.

## Control flow

The daemon iterates each `RecoveringBlock`, logs the command, branches by `isStriped()`, and catches per-block `IOException`s so one failed recovery does not stop the remaining batch.

For contiguous blocks, recovery probes all listed locations. A local target uses the in-process DataNode as `InterDatanodeProtocol`; remote targets use a proxy configured with `DNConf.socketTimeout` and `connectToDnViaHostname`. A replica is considered a candidate when its generation stamp is at least the block generation stamp and its length is positive. Only replicas whose original state is `RWR` or better join the synchronization list. If all probes fail, or candidates exist but none are recoverable, recovery fails.

`syncBlock` commits deletion when no non-empty replicas are available. Otherwise it finds the best state: finalized replicas dominate and must agree on length; RBW/RWR recovery uses the minimum length across replicas in the best state. Truncate recovery overrides the computed length with `rBlock.getNewBlock().getNumBytes()`. Each participating DataNode is asked to update its replica under recovery to the recovery generation stamp, new block ID, and new length. At least one success is required before the NameNode is notified with the successful DataNode and storage IDs.

For striped blocks, the worker validates that at least the number of data units are available, probes internal block replicas, keeps the longest replica per internal block, computes a safe block-group length through `StripedBlockUtil.getSafeLength`, and truncates internal blocks whose current length can satisfy the safe length. It commits either deletion when the safe length is zero or a block-group update with arrays indexed by internal block index.

## State and persistence behavior

The worker does not persist local state directly. Persistence occurs through peer `updateReplicaUnderRecovery` calls, which change replica generation stamp, block ID, length, and state in each DataNode dataset, and through `commitBlockSynchronization`, which updates NameNode metadata. `BlockRecord.storageID` is populated only after successful replica update and is sent to the NameNode to bind recovered locations to storage volumes.

Recovery IDs are treated as new generation stamps. The code aborts if a peer reports `RecoveryInProgressException`, preventing overlapping recoveries with conflicting generation stamps. For striped block groups, the safe length policy deliberately prefers truncation to a length that can be represented by enough internal blocks; TODO comments state that parity regeneration for partial stripes is not implemented here.

## Dependencies and integration points

This class depends on `DataNode`, `BPOfferService`, active NameNode translator `DatanodeProtocolClientSideTranslatorPB`, `InterDatanodeProtocol`, `ReplicaRecoveryInfo`, `RecoveringBlock`, `RecoveringStripedBlock`, `ErasureCodingPolicy`, `StripedBlockUtil`, and `HdfsServerConstants.ReplicaState`. It integrates with DataNode metrics and logging, and relies on `DNConf` for inter-DataNode proxy behavior.

## Risks and edge cases

Contiguous recovery must avoid committing a length that loses finalized data or extends beyond a valid replica. The finalized-length consistency check is critical because conflicting finalized replicas imply deeper corruption. Striped recovery is more limited: it chooses the longest duplicate internal replica, truncates to a safe length, and explicitly leaves decode/encode parity repair TODOs, so changes here can affect erasure-coded file correctness. A partial failure after some `updateReplicaUnderRecovery` calls but before NameNode commit causes recovery to be retried with updated peer state, so idempotence and generation-stamp validation are important.

## Test signals

Tests should cover no replicas, all DataNodes failing, in-progress recovery abort, finalized length disagreement, RBW/RWR min-length selection, truncate recovery with a new block, partial participant failure, active NameNode lookup failure, and striped safe-length computation with missing and zero-length internal blocks. The `@VisibleForTesting getSafeLength` method and fault-injector delay point are direct hooks for deterministic tests.
