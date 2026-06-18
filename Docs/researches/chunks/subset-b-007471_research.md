# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/hadoop-hdfs_0.21.0.xml lines 11833-16220

## Purpose

This chunk is a JDiff public API description for Hadoop HDFS 0.21.0. It covers the tail of `org.apache.hadoop.hdfs.server.namenode.FSNamesystem`, the main NameNode servlet/daemon/helper classes, NameNode metrics APIs, server-side HDFS RPC protocol types, command/value objects exchanged between NameNode, DataNode, backup/secondary NameNode, and several end-user tools.

The source is generated XML rather than Java implementation. The research signal is therefore the exposed API surface: packages, class/interface inheritance, method signatures, checked exceptions, public/protected fields, synchronization markers, and embedded Javadocs. Implementation-specific behavior below is inferred only where the Javadocs and signatures make the integration path explicit.

## Important APIs, Types, and Functions

The `org.apache.hadoop.hdfs.server.namenode` portion is centered on namespace management and the public RPC facade:

- The chunk begins inside `FSNamesystem`, which implements `FSConstants`, `FSNamesystemMBean`, and `FSClusterStats`. Exposed methods include namespace mutations (`setPermission`, `setOwner`, `concat`, `setTimes`, `createSymlink`, `delete`, `mkdirs`), block allocation and completion (`getAdditionalBlock`, `abandonBlock`, `completeFile`, `setReplication`, `markBlockAsCorrupt`), DataNode lifecycle (`registerDatanode`, `removeDatanode`, `processReport`, `blockReceived`, `refreshNodes`, `stopDecommission`), capacity/replication counters, generation stamp accessors, delegation-token methods, and edit-log master-key logging.
- `FSNamesystem` exposes core stateful collaborators as fields: `dir` (`FSDirectory`), `leaseManager`, `lmthread`, `replthread`, plus `LOG` and `auditLog`. This identifies it as the in-memory namespace/block manager behind the RPC layer.
- `GetImageServlet`, `ListPathsServlet`, and `StreamFile` are HTTP integration points for fsimage retrieval, filesystem metadata listing, and streaming file data through `DFSClient`.
- `INodeSymlink` extends `INode` and exposes symlink identity/value methods (`isLink`, `getLinkValue`, `getSymlink`) while reporting `isDirectory`.
- `LeaseManager` exposes lease lookup by path, lease count, lease-period tuning, and string rendering; `LeaseExpiredException` reports expired write leases.
- `NameNode` implements `NamenodeProtocols` and `FSConstants`. It exposes configuration/bootstrap (`format`, `initialize`, `loadNamesystem`, `createNameNode`, `main`), service lifecycle (`join`, `stop`), RPC/HTTP addresses, metrics, fsimage access, client file APIs, DataNode protocol APIs, backup-node checkpoint/journal APIs, safe mode, namespace save/roll/finalize/upgrade operations, quotas, corrupt-file reporting, symlink APIs, delegation tokens, and refresh operations for hosts, service ACLs, and user/group mappings.
- `NamenodeFsck` provides filesystem checking with status constants (`CORRUPT_STATUS`, `HEALTHY_STATUS`, `NONEXISTENT_STATUS`, `FAILURE_STATUS`) and fixing modes (`FIXING_NONE`, `FIXING_MOVE`, `FIXING_DELETE`).
- `SecondaryNameNode` is a runnable helper daemon for periodic metadata checkpoints. `SafeModeException`, `NotReplicatedYetException`, and `UnsupportedActionException` encode important NameNode state-machine failure modes.
- `UpgradeObjectNamenode` is the abstract NameNode-side distributed-upgrade hook with `processUpgradeCommand`, `startUpgrade`, `forceProceed`, and `getType`.

The `org.apache.hadoop.hdfs.server.namenode.metrics` package exposes operational monitoring:

- `FSNamesystemMBean` publishes stable JMX state: FS state, block/file counts, capacity used/remaining/total, replication queues, total load, and live/dead DataNode counts.
- `FSNamesystemMetrics` implements Hadoop `Updater`; `doUpdates` periodically samples `FSNamesystem` state, converts some values for metrics collectors, and exposes `numExpiredHeartbeats`.
- `NameNodeActivityMBean` wraps the metrics registry as the dynamic JMX bean for NameNode activity.
- `NameNodeMetrics` implements `Updater`, owns public metrics counters/rates for file creation, append, block-location lookup, rename, listing, delete, file-info lookup, add-block, symlink/link-target calls, edit-log transactions, syncs, batched transactions, block reports, safe-mode time, fsimage load time, corrupt blocks, and file counts returned by listings.

The `org.apache.hadoop.hdfs.server.protocol` package defines the low-level wire contracts:

- `DatanodeProtocol` is the DataNode-to-NameNode RPC contract. It includes registration, heartbeats returning `DatanodeCommand[]`, compact long-array block reports, block-received notifications with deletion hints, error reports, namespace-version handshakes, distributed upgrade commands, bad-block reports, and lease-recovery block synchronization commits. Its constants define error codes and DataNode command action codes (`DNA_TRANSFER`, `DNA_INVALIDATE`, `DNA_SHUTDOWN`, `DNA_REGISTER`, `DNA_FINALIZE`, `DNA_RECOVERBLOCK`, `DNA_ACCESSKEYUPDATE`).
- `NamenodeProtocol` is the secondary/backup NameNode contract. It exposes block-location export for a DataNode, access-key export, edit-log size and roll, fsimage roll, version requests, registration, checkpoint start/end, journal sizing, and edit-record journaling. Its constants describe notification/fatal errors, journal actions, and subordinate-node actions (`ACT_SHUTDOWN`, `ACT_CHECKPOINT`).
- `NamenodeProtocols` composes the full NameNode RPC surface by extending `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `RefreshAuthorizationPolicyProtocol`, and `RefreshUserToGroupMappingsProtocol`.
- `BlockCommand`, `BlockRecoveryCommand`, `BlockRecoveryCommand.RecoveringBlock`, `DatanodeCommand`, `KeyUpdateCommand`, `NamenodeCommand`, `ServerCommand`, and `UpgradeCommand` are serializable command objects sent as protocol responses. They carry block transfer/invalidation targets, recovery work and generation stamps, access-key updates, checkpoint actions, generic action codes, and upgrade status/version data.
- `BlocksWithLocations` and nested `BlockWithLocations` provide custom `Writable` serialization for arrays of block/location pairs to avoid the default RPC array overhead.
- `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, and `NodeRegistration` model the identity, layout version, registration ID, storage info, exported keys, role, checkpoint time, and namespace/build/distributed-upgrade version data exchanged during registration and handshakes.
- `InterDatanodeProtocol` supports replica recovery between DataNodes through `initReplicaRecovery` and `updateReplicaUnderRecovery`.
- `ReplicaRecoveryInfo` extends `Block` with original replica state. `DisallowedDatanodeException` reports registration/communication by a DataNode not permitted by include/exclude host policy.

The tools packages expose operational CLIs:

- `DelegationTokenFetcher` obtains a delegation token from the current NameNode and writes it to a supplied output stream/file.
- `DFSAdmin` extends `FsShell` and implements administrative commands: report, safe mode, namespace save, failed-storage restore checks/toggles, host refresh, upgrade finalization/progress, metadata save, topology printing, service ACL refresh, user-to-groups refresh, `run`, and `main`.
- `DFSck` implements `Tool` for filesystem consistency checks and optional repair of missing/corrupt blocks via none, move to `/lost+found`, or delete behavior.
- `HDFSConcat` exposes a CLI entry point for block-level file concatenation.
- `JMXGet` reads NameNode/DataNode MBeans using service, port, server, or local-VM URL settings and can print all values or retrieve one key.
- `OfflineImageViewer` processes an fsimage through an `ImageVisitor`, builds Commons CLI options, and provides a command-line `main`.

## Control Flow and Execution Model

The primary execution path is layered. `NameNode` owns the externally visible RPC server and HTTP server addresses, receives calls through the combined `NamenodeProtocols` interface, verifies requests/version where exposed, and delegates filesystem bookkeeping to `FSNamesystem`. `FSNamesystem` then mutates namespace and block state through `FSDirectory`, `LeaseManager`, generation stamps, replication queues, and DataNode descriptor/block maps. Several mutating `FSNamesystem` methods are marked synchronized in the JDiff (`setPermission`, `setOwner`, `setTimes`, `createSymlink`, `abandonBlock`, `markBlockAsCorrupt`, `registerDatanode`, `removeDatanode`, `processReport`, `blockReceived`, `datanodeReport`, `DFSNodesStatus`), while other public methods are unsynchronized at the API level and likely rely on internal or caller-side locking in the implementation.

Client write flow is visible through both `NameNode` and `FSNamesystem`: clients create or append files, request additional blocks, abandon failed block allocations, complete files, and renew leases. The `getAdditionalBlock` Javadoc notes that the previous blocks must have been reported and replicated before another block is issued, and may ask clients to try again later. Completion returns `FSNamesystem.CompleteFileStatus` internally and a boolean through `NameNode.complete`.

DataNode flow is modeled by `DatanodeProtocol`: a DataNode registers, sends periodic heartbeats with capacity/load values, uploads full block reports as compact `long[]` arrays, sends incremental block-received notifications, reports bad blocks or errors, and receives commands only as return values from those calls. Commands drive block transfer, invalidation, shutdown, re-registration, finalization, block recovery, and access-key updates.

Checkpoint and backup flow is modeled by `NamenodeProtocol`, `NamenodeRegistration`, and `CheckpointCommand`: a subordinate NameNode registers with the active NameNode, requests checkpoint start, receives a command with a `CheckpointSignature` and image-obsolete/return-image flags, finalizes the checkpoint with the same signature, and may receive journal records from the active NameNode via `journal`.

HTTP helper flow is separate from RPC. `GetImageServlet` retrieves image files through the NameNode web server, `ListPathsServlet` turns query parameters into a root/options map and services metadata listing requests, and `StreamFile` obtains a `DFSClient` from the servlet request before streaming data.

Metrics flow is push-oriented through Hadoop metrics `Updater`: `FSNamesystemMetrics.doUpdates` and `NameNodeMetrics.doUpdates` are called periodically by the metrics context, sample current NameNode/FSNamesystem values, and publish them to metrics/JMX registries. `NameNodeActivityMBean` exposes dynamic metrics, while `FSNamesystemMBean` is a stable JMX interface.

Tool execution is command-line oriented: `DFSAdmin.run`, `DFSck.run`, `DelegationTokenFetcher.go`, `OfflineImageViewer.go`, and the various `main` methods translate command-line inputs into RPC, filesystem, JMX, or fsimage-processing calls.

## State and Persistence Behavior

Persistent NameNode state is implied by the namespace and storage APIs. `FSNamesystem` tracks namespace edits directories, upgrade permissions, generation stamps, delegation-token master-key edits (`logUpdateMasterKey`), leases, replication state, corrupt replicas, block counts, DataNode registration IDs, and capacity counters. Its class-level documentation says the NameNode keeps two critical tables: filename to block sequence, which is stored on disk, and block to machine list, which is rebuilt when the NameNode starts.

`NameNode` exposes persistence operations that affect fsimage and edit-log lifecycle: `format`, `saveNamespace`, `getEditLogSize`, `rollEditLog`, `rollFsImage`, `getFsImageName`, `getFsImageNameCheckpoint`, `getFSImage`, checkpoint start/end, and `journal`. The API also carries distributed-upgrade state through `finalizeUpgrade`, `distributedUpgradeProgress`, `UpgradeObjectNamenode`, and `UpgradeCommand`.

Registration state persists across restarts through namespace IDs and registration IDs. `FSNamesystem.registerDatanode` documents that namespace ID is a persistent attribute and that DataNodes with inappropriate registration IDs are rejected. `DatanodeRegistration` combines `DatanodeID`, `StorageInfo`, and exported access keys; `NamenodeRegistration` combines `StorageInfo`, address, role, and checkpoint time; `NamespaceInfo` carries namespace handshake data including build and distributed-upgrade versions.

Block and replica state is transient but operationally critical. `BlocksWithLocations` serializes block-location state for balancing/secondary operations. `BlockCommand` and `BlockRecoveryCommand` carry work queues rather than durable state. `ReplicaRecoveryInfo` preserves the original replica state while recovery updates generation stamp and length. `commitBlockSynchronization` finalizes lease recovery and can close files, delete old blocks, and install new targets.

Metrics and JMX APIs expose sampled runtime state rather than persistent state. `NameNodeMetrics` fields are mutable metrics objects. `FSNamesystemMetrics` notes that capacity values are rounded to GB for collectors, while some long counters are cast to int because collectors may not handle long values.

Tooling persists or inspects external state: `DelegationTokenFetcher` writes tokens to a file/output stream, `DFSAdmin` can trigger namespace saves and metadata dumps, `DFSck` may move or delete corrupt files, `HDFSConcat` changes file block layout, `JMXGet` observes process MBeans, and `OfflineImageViewer` reads an fsimage without requiring a live NameNode.

## Dependencies and Integration Points

This chunk integrates with these HDFS and Hadoop subsystems:

- Core NameNode internals: `FSDirectory`, `LeaseManager`, `DatanodeDescriptor`, `FSImage`, `CheckpointSignature`, safe mode, generation stamps, replication queues, corrupt-replica tracking, and block maps.
- Public HDFS protocols: `ClientProtocol`, `DatanodeProtocol`, `NamenodeProtocol`, `NamenodeProtocols`, `InterDatanodeProtocol`, `VersionedProtocol`, and Hadoop IPC `Server`.
- HDFS protocol/value classes: `Block`, `LocatedBlock`, `LocatedBlocks`, `DirectoryListing`, `HdfsFileStatus`, `DatanodeID`, `DatanodeInfo`, `BlockListAsLongs`, `ContentSummary`, and `FsServerDefaults`.
- Security: delegation-token secret manager, exported access keys, `Token<DelegationTokenIdentifier>`, `UserGroupInformation`, service ACL refresh, user/group mapping refresh, and access-control exceptions.
- Storage and upgrade: `StorageInfo`, `NamespaceInfo`, `NamenodeRegistration`, `DatanodeRegistration`, `HdfsConstants.NamenodeRole`, `NodeType`, `UpgradeStatusReport`, `UpgradeCommand`, and edit-log journal actions.
- Servlet/HTTP tooling: `HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `DfsServlet`, NameNode Jetty/HTTP server, `DFSClient`, and Commons CLI for offline image viewer options.
- Hadoop metrics/JMX: `MetricsContext`, `MetricsRegistry`, `MetricsDynamicMBeanBase`, `MetricsTimeVaryingInt`, `MetricsTimeVaryingRate`, `MetricsIntValue`, and the stable `FSNamesystemMBean` interface.
- Java and Hadoop serialization: `Writable`, `DataInput`, `DataOutput`, arrays of protocol objects, compact block-report `long[]` encoding, and `IOException`-based RPC failure signaling.

## Risks and Edge Cases

- The chunk starts mid-`FSNamesystem` method metadata, so the class header and earlier methods must be reconciled with the previous chunk. Conclusions about the complete class should not be drawn from this slice alone.
- This XML exposes signatures and docs, not method bodies. Locking, validation order, exact persistence writes, and error handling need implementation-source confirmation before changing behavior.
- API synchronization is mixed. Several namespace/block/DataNode methods are marked synchronized, but many high-impact `NameNode` and `FSNamesystem` APIs are not. Callers and implementations must preserve the expected NameNode/FSNamesystem locking discipline.
- `concat` explicitly validates all arguments before moving blocks to avoid rollback complexity. Any implementation change that partially moves blocks before all preconditions pass risks namespace/block-map inconsistency.
- `setTimes` documents that edits are written but not flushed when needed, so callers relying on immediate durability must understand edit-log sync boundaries.
- `getAdditionalBlock` depends on previous blocks being reported and replicated; tests should cover retry-later behavior and under-replicated last-block cases.
- DataNode registration is sensitive to namespace ID, storage ID, host include/exclude policy, and layout version. Incorrect registration ID or `DisallowedDatanodeException` handling can strand valid DataNodes or admit invalid ones.
- Full block reports use a compact `long[]` representation where each block is represented by multiple longs. Producer/consumer encoding drift would corrupt the NameNode's block map.
- Command action integers are protocol-specific. Reusing `ServerCommand` action values across DataNode and NameNode protocols without checking the target protocol can trigger wrong behavior.
- Checkpointing depends on `CheckpointSignature`, image-obsolete flags, return-image flags, and journal action ordering. Mismatched signatures or stale checkpoint time can corrupt backup/secondary coordination.
- Metrics casts and capacity rounding are documented compatibility compromises; large clusters can lose precision in metrics output even if internal counters remain wider.
- `DFSAdmin.restoreFaileStorage` appears misspelled in the public API. Scripts or compatibility checks may depend on that exact method name.
- `NamenodeFsck` and `DFSck` can perform destructive fixes (`FIXING_DELETE`) or namespace-moving fixes (`FIXING_MOVE`), so CLI option parsing and dry-run/default behavior are safety-critical.
- `OfflineImageViewer` reads fsimage files directly; it must remain compatible with the image format produced by the corresponding NameNode version.

## Test Signals

Validation for this surface should come from subsystem tests rather than XML-only checks:

- NameNode namespace tests: permissions/owner/times/symlink changes, mkdir/delete/rename/concat, quotas, content summaries, corrupt-file reporting, safe-mode rejection, and edit-log/fsimage persistence across restart.
- Client write-path tests: create/append, add-block retry behavior before replication is sufficient, abandon-block cleanup, complete-file status transitions, lease renewal and `LeaseExpiredException`, pipeline update, fsync, and block synchronization during lease recovery.
- DataNode protocol tests: registration with new/existing storage IDs, wrong namespace/layout rejection, heartbeat command generation, block reports using compact `long[]`, incremental block-received notifications with deletion hints, bad-block reports, access-key update commands, and decommission include/exclude refresh.
- Checkpoint/backup tests: `NamenodeProtocol.register`, `startCheckpoint`, `endCheckpoint`, `journal`, edit-log roll, fsimage roll, checkpoint signatures, obsolete-image handling, and secondary NameNode shutdown/run lifecycle.
- Upgrade tests: `UpgradeObjectNamenode.processUpgradeCommand`, `startUpgrade`, `forceProceed`, `UpgradeCommand` serialization, distributed-upgrade progress, and finalization.
- Serialization compatibility tests: `BlockCommand`, `BlockRecoveryCommand`, `RecoveringBlock`, `BlocksWithLocations`, `BlockWithLocations`, `CheckpointCommand`, `DatanodeRegistration`, `NamenodeRegistration`, `NamespaceInfo`, `ReplicaRecoveryInfo`, `ServerCommand`, `UpgradeCommand`, and `KeyUpdateCommand` `write/readFields` round trips.
- Metrics/JMX tests: `FSNamesystemMBean` values, periodic `doUpdates`, NameNode activity MBean registration/shutdown, min/max reset, large-capacity rounding, and heartbeat-expiry metrics.
- HTTP/tool tests: image servlet downloads, list-path query defaults, stream-file reads, `DFSAdmin` command parsing and return codes, `DFSck` healthy/corrupt/missing statuses plus move/delete repair modes, delegation-token fetch output, `JMXGet` key lookup and print-all behavior, `HDFSConcat` argument handling, and `OfflineImageViewer` CLI option parsing plus fsimage visitor output.

## Chunk Boundary Notes

Lines 11833-16220 begin inside the `FSNamesystem` entry and end after the complete `OfflineImageViewer` class and closing `api` tag. The merge lane should combine this report with the preceding chunk for full `FSNamesystem` coverage and with earlier/later chunks for the complete generated JDiff API file.
