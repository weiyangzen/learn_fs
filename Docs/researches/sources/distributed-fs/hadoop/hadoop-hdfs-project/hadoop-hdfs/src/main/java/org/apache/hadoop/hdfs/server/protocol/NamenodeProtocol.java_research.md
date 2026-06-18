<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocol.java

## Purpose

`NamenodeProtocol` is the private RPC contract used by secondary/backup NameNodes, the balancer, and external Storage Policy Satisfier to query or coordinate with the active NameNode.

## Important APIs and types

It declares `versionID = 6L`, error codes, and action codes `ACT_SHUTDOWN` and `ACT_CHECKPOINT`. Methods include `getBlocks`, `getBlockKeys`, transaction/checkpoint txid accessors, `rollEditLog`, `versionRequest`, `errorReport`, subordinate NameNode registration, `startCheckpoint`, `endCheckpoint`, `getEditLogManifest`, `isUpgradeFinalized`, `isRollingUpgrade`, and `getNextSPSPath`.

## Control flow

Balancer-like callers request block samples with placement constraints. Secondary/backup NameNodes roll edit logs, start/end checkpoints with `CheckpointSignature`, fetch edit-log manifests, and register/report errors. External SPS polls `getNextSPSPath()` for inode IDs needing storage policy satisfaction.

## State and persistence behavior

Server implementations expose persistent namespace identity, edit-log transaction IDs, checkpoint txids, upgrade state, and SPS path queues. `startCheckpoint` and `endCheckpoint` are `@AtMostOnce`, reflecting side effects that should not be blindly retried.

## Dependencies and integration points

It depends on `DatanodeInfo`, `StorageType`, `BlocksWithLocations`, `ExportedBlockKeys`, `CheckpointSignature`, `NNStorage.NameNodeFile`, `RemoteEditLogManifest`, `NamenodeRegistration`, and HA read-only annotations. Method changes must be mirrored in `NamenodeProtocol.proto`.

## Risks and test signals

Risks include retrying non-idempotent checkpoint operations, exposing stale edit-log manifests, returning blocks unsuitable for balancer/SPS use, and losing SPS path queue items. Tests should cover checkpoint admission/finalization, edit-log rolling and manifest ranges, balancer block queries with storage type and hot-block filters, upgrade state reads, and external SPS path polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocol.java -->
