<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeProtocol.java

## Purpose

`DatanodeProtocol` is the main private RPC contract a DataNode uses to communicate with the NameNode. It covers registration, heartbeats, full and incremental block reports, cache reports, error reports, bad-block reporting, version handshakes, and lease-recovery block synchronization.

## Important APIs and types

The interface declares protocol `versionID = 28L`, error codes (`NOTIFY`, `DISK_ERROR`, `INVALID_BLOCK`, `FATAL_DISK_ERROR`), and DataNode command action codes from `DNA_TRANSFER` through `DNA_DROP_SPS_WORK_COMMAND`. Methods include `registerDatanode`, `sendHeartbeat`, `blockReport`, `cacheReport`, `blockReceivedAndDeleted`, `errorReport`, `versionRequest`, `reportBadBlocks`, and `commitBlockSynchronization`.

## Control flow

A DataNode first requests namespace version data and registers with `DatanodeRegistration`. It then sends recurring heartbeats, optionally requesting a full block-report lease, and receives `HeartbeatResponse` commands. Full block reports use `StorageBlockReport[]` plus `BlockReportContext`, while incremental reports use `StorageReceivedDeletedBlocks[]`. Error and bad-block reports notify the NameNode asynchronously. During lease recovery, a DataNode commits synchronization with new generation stamp, length, targets, and target storage IDs.

## State and persistence behavior

The interface itself stores nothing, but server implementations update NameNode block maps, DataNode descriptors, cache state, slow peer/disk tracking, block-report lease state, and namespace recovery state. Several calls are marked `@Idempotent`, allowing RPC retry, but the implementation must preserve idempotent semantics around block maps and reports.

## Dependencies and integration points

The contract uses `DatanodeRegistration`, `StorageReport`, `VolumeFailureSummary`, `SlowPeerReports`, `SlowDiskReports`, `StorageBlockReport`, `BlockReportContext`, `LocatedBlock`, `ExtendedBlock`, and `DatanodeID`. Any method or payload change must be mirrored in `DatanodeProtocol.proto` and protocol buffer translators.

## Risks and test signals

This is a high-risk compatibility surface. Action-code drift, wrong idempotency annotations, full block-report lease mistakes, or mismatched block list encodings can corrupt NameNode block state or trigger needless re-registration. Tests should exercise registration handshakes, heartbeat command dispatch, full/incremental block reports across multiple storages, cache reports, slow reports, lease invalidation, and recovery synchronization under RPC retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeProtocol.java -->
