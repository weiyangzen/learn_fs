# subset-b-007509 research

Grouped research for HDFS server protocol command/value/RPC contracts, external Storage Policy Satisfier support, ExternalSPS JMX metrics, and HDFS cache/crypto admin tools. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java

## Purpose

`CheckpointCommand` is the `NamenodeCommand` returned by `NamenodeProtocol.startCheckpoint` when a subordinate or backup NameNode is allowed to run a checkpoint. It packages the checkpoint identity and whether the produced image must be sent back to the active NameNode.

## Important APIs and types

The class extends `NamenodeCommand` with action `NamenodeProtocol.ACT_CHECKPOINT`. Its payload is a `CheckpointSignature` plus `needToReturnImage`. The public surface is the default constructor for serialization, the main constructor, `getSignature()`, and `needToReturnImage()`.

## Control flow

The constructor calls the superclass with the checkpoint action code and stores the signature/return flag. Consumers inspect the command after the active NameNode admits a checkpoint and use the signature to bind subsequent `endCheckpoint` or image-transfer work to the same checkpoint attempt.

## State and persistence behavior

This is an in-memory RPC value object. It does not persist data itself, but it carries a `CheckpointSignature` that describes persistent namespace/checkpoint state managed by NameNode storage.

## Dependencies and integration points

It integrates `NamenodeProtocol`, `NamenodeCommand`, and `CheckpointSignature`. Wire compatibility depends on the corresponding protobuf RPC translator for Namenode protocol commands.

## Risks and test signals

Risks are mostly protocol drift: missing or mismatched signatures can let a backup node complete the wrong checkpoint, and the return-image flag affects whether the NameNode receives a fresh fsimage. Useful tests cover accepted/rejected checkpoint flows, image-return decisions, null/default serialization, and signature mismatch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java

## Purpose

`DatanodeCommand` is the abstract base for commands the NameNode returns to a DataNode, usually in `HeartbeatResponse` or block-report responses. It separates DataNode command classes from generic `ServerCommand` while preserving the protocol-specific integer action code.

## Important APIs and types

The only constructor is package-private and accepts an action code. Subclasses such as `RegisterCommand`, `FinalizeCommand`, `KeyUpdateCommand`, `DropSPSWorkCommand`, block commands, cache commands, and movement commands supply constants from `DatanodeProtocol`.

## Control flow

There is no additional control flow beyond delegating construction to `ServerCommand`. DataNode-side dispatch reads `getAction()` and downcasts/deserializes to the matching command payload.

## State and persistence behavior

The object stores only inherited immutable action state. It is serialized through the HDFS RPC/protobuf layer and has no persistence outside command delivery.

## Dependencies and integration points

It depends on `ServerCommand` and `DatanodeProtocol` action namespaces. The integration point is the NameNode-to-DataNode command path, especially heartbeat responses.

## Risks and test signals

Because the constructor is package-private, new commands must live in the protocol package or use existing constructors. Risks are action-code collisions and protobuf translator mismatch. Tests should verify each concrete command maps to the expected `DNA_*` code and that DataNode command dispatch handles singleton/default commands correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java

## Purpose

`DatanodeLifelineProtocol` defines the lightweight DataNode-to-NameNode RPC used to send lifeline messages separate from full heartbeats. Lifelines keep a DataNode from being considered dead while avoiding the full command-return path.

## Important APIs and types

The interface is annotated with `@KerberosInfo`, using NameNode and DataNode principal keys. `sendLifeline(...)` is marked `@Idempotent` and carries the DataNode registration, storage reports, cache capacity/usage, transfer and xceiver counts, failed volume count, and `VolumeFailureSummary`.

## Control flow

The DataNode periodically calls `sendLifeline` with status data. The NameNode updates liveness/health information but the method returns `void`, so this channel does not deliver `DatanodeCommand` arrays.

## State and persistence behavior

The protocol mutates NameNode in-memory DataNode liveness and storage-health state through the server implementation. No persistent state is written by the interface itself.

## Dependencies and integration points

It shares most heartbeat payload types with `DatanodeProtocol.sendHeartbeat` and is included in `NamenodeProtocols`, the full NameNode RPC surface. Security depends on configured Kerberos principals.

## Risks and test signals

Risks include skew between lifeline and heartbeat payload semantics, null volume summaries, and over-trusting stale storage reports. Tests should cover lifeline-only liveness extension, authentication principal selection, and behavior when lifelines report failed volumes without returning commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java

## Purpose

`DatanodeRegistration` carries the identity and compatibility information a DataNode sends to the NameNode for registration and subsequent RPCs. It combines network identity from `DatanodeID` with storage layout metadata, block-token keys, software version, and optional namespace info.

## Important APIs and types

The class extends `DatanodeID` and implements `NodeRegistration`. Fields include `StorageInfo storageInfo`, mutable `ExportedBlockKeys exportedKeys`, `softwareVersion`, and mutable `NamespaceInfo nsInfo`. It exposes getters, `setExportedKeys`, `setNamespaceInfo`, `getRegistrationID()`, `getAddress()`, `getVersion()`, and a detailed `toString()`.

## Control flow

DataNodes construct registrations from their ID, storage info, exported keys, and software version. The NameNode may return updated registration data including block keys. Registration ID is derived from storage info using `Storage.getRegistrationID`.

## State and persistence behavior

The object mirrors persistent DataNode storage metadata but does not persist it. Equality and hash code defer entirely to `DatanodeID`, so storage info and exported keys are not part of equality.

## Dependencies and integration points

It integrates `DatanodeID`, `StorageInfo`, `Storage`, `ExportedBlockKeys`, `NamespaceInfo`, and registration checks in NameNode code. Tests use the visible-for-testing constructor to substitute UUIDs.

## Risks and test signals

Risks include equality ignoring storage state, stale exported keys, namespace info being unset, and registration IDs changing with layout/namespace metadata. Tests should cover registration round trips, block-key update propagation, storage compatibility checks, and equality/hash behavior when UUIDs differ but storage fields match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeRegistration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java

## Purpose

`DisallowedDatanodeException` reports that a DataNode is not allowed to register or communicate with a NameNode because include/exclude host rules rejected it.

## Important APIs and types

The exception extends `IOException` and has constructors accepting a `DatanodeID` plus an optional reason. The default reason states that the host is not in the include list.

## Control flow

NameNode registration or heartbeat validation throws this exception after checking host admission rules. The message includes the reason and DataNode identity for logs and client-side diagnostics.

## State and persistence behavior

There is no state beyond the serialized exception message and `serialVersionUID`. Include/exclude state is maintained elsewhere by NameNode host managers.

## Dependencies and integration points

It depends only on `DatanodeID` and Java `IOException`. It integrates with DataNode registration, decommission/exclusion handling, and administrative host-list configuration.

## Risks and test signals

The main risk is diagnostic clarity: the exception should expose enough identity and reason without leaking unrelated internals. Tests should cover default and custom reasons, registration rejection, and DataNode behavior after receiving the exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java

## Purpose

`DropSPSWorkCommand` instructs a DataNode to drop pending Storage Policy Satisfier worker block-movement queues. It is part of the DataNode command channel used when SPS state must be reset or cancelled.

## Important APIs and types

The class extends `DatanodeCommand` and uses action `DatanodeProtocol.DNA_DROP_SPS_WORK_COMMAND`. It exposes a singleton `DNA_DROP_SPS_WORK_COMMAND` and a public no-argument constructor for serialization and construction.

## Control flow

The NameNode returns this command to a DataNode, usually via `HeartbeatResponse`. DataNode command handling dispatches on the action code and clears local SPS work queues.

## State and persistence behavior

The command has no payload beyond its action code. Runtime effects occur only when DataNode SPS worker queues process the command.

## Dependencies and integration points

It depends on `DatanodeCommand` and `DatanodeProtocol`. Integration points are NameNode SPS control logic, DataNode heartbeat command processing, and protobuf command translators.

## Risks and test signals

Risks include losing queued movement work unexpectedly or failing to clear stale work after SPS disablement. Tests should verify singleton/default serialization, action-code mapping, and DataNode queue behavior after receiving the command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java

## Purpose

`FenceResponse` is the return value for `JournalProtocol.fence`. It tells a new journal writer what epoch it replaced, the last transaction observed by the journal, and whether the journal was in sync.

## Important APIs and types

The immutable fields are `previousEpoch`, `lastTransactionId`, and `isInSync`. Public methods are the constructor, `getPreviousEpoch()`, `getLastTransactionId()`, and `isInSync()`.

## Control flow

A NameNode or fencer calls `JournalProtocol.fence(...)`. The journal implementation fences older writers, computes these status values, and returns `FenceResponse`. Callers use it to decide whether journal state is safe for failover or recovery.

## State and persistence behavior

The response is in-memory, but it summarizes persistent edit-log/journal state and fencing epoch state maintained by the journal implementation.

## Dependencies and integration points

It depends on `JournalProtocol` semantics and is serialized through journal RPC protobuf translators. It integrates with backup-node journaling and HA failover safety checks.

## Risks and test signals

Incorrect `isInSync` or transaction IDs can make failover unsafe. Tests should cover fencing an older writer, repeated fence calls, stale epoch rejection, and out-of-sync journal reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FenceResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java

## Purpose

`FencedException` indicates that a previous writer or resource user attempted to use a shared journal/resource after another writer fenced it.

## Important APIs and types

The class extends `IOException`, declares `serialVersionUID`, and exposes a single string-message constructor.

## Control flow

Journal methods such as `journal`, `startLogSegment`, and `fence` document this exception. Implementations throw it when the caller's epoch or writer identity is no longer valid.

## State and persistence behavior

The exception carries only a message. Fencing epochs and writer state are maintained by the journal implementation.

## Dependencies and integration points

It integrates with `JournalProtocol`, HA edit-log replication, backup-node journaling, and RPC retry/failover logic that must distinguish fenced writers from transient IO failures.

## Risks and test signals

Risks are callers retrying a fenced operation as if it were transient or implementations throwing generic IO errors instead. Tests should verify stale epochs receive `FencedException` and active writers stop after being fenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FencedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java

## Purpose

`FinalizeCommand` tells a DataNode to finalize a previous HDFS upgrade for a specific block pool.

## Important APIs and types

The class extends `DatanodeCommand` with action `DatanodeProtocol.DNA_FINALIZE`. It stores `blockPoolId`, has a private no-argument constructor for serialization, a public constructor taking the block pool ID, and `getBlockPoolId()`.

## Control flow

The NameNode returns this command through the DataNode command channel after upgrade finalization is appropriate. The DataNode reads the block pool ID and finalizes local storage for that pool.

## State and persistence behavior

The command is transient, but processing it changes persistent DataNode storage by removing rollback state for the targeted block pool.

## Dependencies and integration points

It depends on `DatanodeProtocol` action constants and DataNode storage-upgrade code. It is serialized through DataNode command RPC translators.

## Risks and test signals

Risks include a null/wrong block pool ID, finalizing storage too early, and command loss during heartbeat retry. Tests should cover command serialization, correct pool targeting in federated clusters, and DataNode storage state after finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java

## Purpose

`HeartbeatResponse` is the NameNode's response to `DatanodeProtocol.sendHeartbeat`. It bundles commands for the DataNode, HA status for the NameNode, rolling-upgrade status, a full block-report lease ID, and whether the DataNode is considered slow.

## Important APIs and types

Fields are `DatanodeCommand[] commands`, `NNHAStatusHeartbeat haStatus`, `RollingUpgradeStatus rollingUpdateStatus`, `fullBlockReportLeaseId`, and `isSlownode`. Constructors support old and new forms with default `isSlownode=false`. Getters expose all fields.

## Control flow

The DataNode sends heartbeat metrics and receives this object. It processes commands, updates its view of active/standby NameNode HA state, tracks rolling upgrade, and uses the block-report lease ID before submitting a full block report.

## State and persistence behavior

The response is transient. It represents NameNode in-memory command queues, HA txid state, rolling-upgrade state, and block-report lease state.

## Dependencies and integration points

It integrates `DatanodeProtocol`, command subclasses, `NNHAStatusHeartbeat`, and `RollingUpgradeStatus`. It is central to DataNode liveness and NameNode-to-DataNode control.

## Risks and test signals

Risks include command ordering, null command arrays, stale HA txids, invalid block-report leases, and slow-node flag compatibility with older constructors. Tests should cover mixed command arrays, lease-request heartbeats, rolling upgrade propagation, HA state changes, and slow-node reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java

## Purpose

`InterDatanodeProtocol` defines private DataNode-to-DataNode RPCs used during replica recovery. It lets one DataNode inspect and update a replica on another DataNode.

## Important APIs and types

The interface is secured with DataNode Kerberos principals and declares `versionID = 6L`. Methods are `initReplicaRecovery(RecoveringBlock)` returning `ReplicaRecoveryInfo` or null, and `updateReplicaUnderRecovery(ExtendedBlock, recoveryId, newBlockId, newLength)` returning a storage ID string.

## Control flow

Recovery begins by asking each candidate DataNode for replica state. Once the recovery coordinator selects a length/generation, it calls `updateReplicaUnderRecovery` to bump generation stamp, adjust length, and possibly rename the block ID on the target replica.

## State and persistence behavior

Implementations read and mutate persistent on-disk replica metadata and block files. The interface itself stores no state.

## Dependencies and integration points

It uses `BlockRecoveryCommand.RecoveringBlock`, `ReplicaRecoveryInfo`, `ExtendedBlock`, and DataNode RPC/protobuf translators. It integrates with lease recovery, block generation-stamp management, and DataNode storage.

## Risks and test signals

Risks include updating the wrong replica, accepting stale recovery IDs, inconsistent lengths across replicas, and authentication errors between DataNodes. Tests should cover missing replicas, finalized/rbw/rwr states, recovery ID ordering, storage ID return values, and protobuf compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java

## Purpose

`InvalidBlockReportLeaseException` reports that a full block report was rejected because the supplied lease ID is invalid, expired, or otherwise not accepted by the NameNode.

## Important APIs and types

The class extends `IOException` and formats the block-report ID and lease ID as hexadecimal in its message.

## Control flow

DataNodes may request a full block-report lease in heartbeat. When they later submit `blockReport`, the NameNode validates the lease and throws this exception on mismatch.

## State and persistence behavior

The exception is transient. The relevant state is the NameNode's in-memory block-report lease table and block-report tracking.

## Dependencies and integration points

It integrates with `DatanodeProtocol.blockReport`, `HeartbeatResponse.getFullBlockReportLeaseId()`, and NameNode block-manager lease admission.

## Risks and test signals

Risks include incorrectly rejecting valid reports or accepting stale reports that defeat throttling. Tests should cover valid lease use, expired leases, duplicate lease reuse, missing leases, and DataNode retry behavior after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InvalidBlockReportLeaseException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalInfo.java

## Purpose

`JournalInfo` identifies the namespace/journal being written to a remote journal receiver such as a BackupNode.

## Important APIs and types

It stores `layoutVersion`, `clusterId`, and `namespaceId`. It exposes getters, a compact `toString()` format, and equality/hash code based on all three fields.

## Control flow

`JournalProtocol` methods receive `JournalInfo` with each journal, log-segment, or fence request. Implementations compare it to local storage identity before accepting edits.

## State and persistence behavior

The object is immutable and transient, representing persistent namespace identity stored by NameNode storage.

## Dependencies and integration points

It integrates with `JournalProtocol`, edit-log backup output streams, and storage compatibility checks.

## Risks and test signals

`equals` assumes `clusterId` is non-null, so null cluster IDs can throw. Incorrect equality permits cross-namespace journal writes. Tests should verify matching/mismatched namespace ID, cluster ID, layout version, toString diagnostics, and null-safety expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java

## Purpose

`JournalProtocol` defines the RPC path used by an active NameNode to publish edit-log records to a remote BackupNode-style journal receiver.

## Important APIs and types

The interface is secured with NameNode Kerberos principals and declares `versionID = 1L`. Methods are `journal(JournalInfo, epoch, firstTxnId, numTxns, byte[] records)`, `startLogSegment(JournalInfo, epoch, txid)`, and `fence(JournalInfo, epoch, fencerInfo)` returning `FenceResponse`.

## Control flow

The active NameNode sends edit batches through `journal`, announces log rolls through `startLogSegment`, and uses `fence` to invalidate older writers when a new epoch begins. Implementations reject stale epochs with fencing errors and append serialized edit records to remote state.

## State and persistence behavior

Server implementations persist edit-log records and log-segment boundaries. The interface carries epoch and transaction ID ordering needed to make remote journal state consistent.

## Dependencies and integration points

It depends on `JournalInfo`, `FenceResponse`, `FencedException`, NameNode storage/edit-log code, and `JournalProtocol.proto` translators.

## Risks and test signals

Risks are severe: stale writers, transaction gaps/overlap, or namespace mismatches can corrupt recovery. Tests should cover in-order journal batches, log roll boundaries, fencing with old/new epochs, namespace mismatch, and RPC retry around duplicate batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/JournalProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java

## Purpose

`KeyUpdateCommand` tells a DataNode to update its exported block-token keys.

## Important APIs and types

The class extends `DatanodeCommand` with action `DatanodeProtocol.DNA_ACCESSKEYUPDATE`. It stores an `ExportedBlockKeys` object and exposes `getExportedKeys()`. The package-private default constructor creates an empty `ExportedBlockKeys` for serialization.

## Control flow

The NameNode includes this command in heartbeat responses when block-token keys change. The DataNode applies the provided keys to token validation/issuance paths.

## State and persistence behavior

The command is transient. Applying it mutates in-memory DataNode block-token key state; persistence and key rotation are handled by security/token managers.

## Dependencies and integration points

It depends on HDFS block-token security (`ExportedBlockKeys`), `DatanodeProtocol`, heartbeat command dispatch, and protobuf translators.

## Risks and test signals

Risks include missing key updates causing token failures, accepting empty/default keys, or command loss during heartbeat retry. Tests should cover key rotation propagation, serialization of current and all keys, and DataNode behavior with stale tokens before and after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java

## Purpose

`NNHAStatusHeartbeat` carries the NameNode's HA service state and most recent transaction ID in heartbeat responses to DataNodes.

## Important APIs and types

The class stores an `HAServiceState` and a txid initialized from constructor input. The default invalid txid constant is `HdfsServerConstants.INVALID_TXID`. Getters are `getState()` and `getTxId()`.

## Control flow

The NameNode attaches this object to `HeartbeatResponse`. DataNodes use it to decide whether they are talking to an active or standby NameNode and what edit-log point the NameNode has reached.

## State and persistence behavior

The object is immutable from callers' perspective and transient. It reflects NameNode HA state and edit transaction progress maintained elsewhere.

## Dependencies and integration points

It integrates `HAServiceProtocol.HAServiceState`, `HeartbeatResponse`, and DataNode failover/actor logic.

## Risks and test signals

Risks include stale txids during failover, null state, and DataNodes misclassifying standby responses. Tests should cover active-to-standby transitions, invalid txid defaults, and heartbeat behavior during HA failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java

## Purpose

`NamenodeCommand` is the concrete base for commands returned by the active NameNode to subordinate NameNodes, such as checkpoint or shutdown commands.

## Important APIs and types

The constructor accepts an action code and delegates to `ServerCommand`. `CheckpointCommand` is the main payload-bearing subclass in this group.

## Control flow

Subordinate NameNode RPC calls such as `startCheckpoint` receive a `NamenodeCommand`, inspect its action, and act accordingly.

## State and persistence behavior

Only the inherited immutable action code is stored. Runtime effects are handled by the receiving subordinate service.

## Dependencies and integration points

It depends on `ServerCommand` and `NamenodeProtocol` action constants. It integrates with secondary/backup NameNode checkpoint control.

## Risks and test signals

Risks are action-code mismatch and insufficient subtype handling in RPC translators. Tests should cover action propagation, checkpoint command downcasting, and unknown/shutdown command handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java

## Purpose

`NamenodeProtocols` is a marker interface composing the full set of RPC protocols implemented by a NameNode.

## Important APIs and types

It extends `ClientProtocol`, `DatanodeProtocol`, `DatanodeLifelineProtocol`, `NamenodeProtocol`, authorization and user-mapping refresh protocols, reconfiguration, call-queue refresh, generic refresh, user mapping lookup, and `HAServiceProtocol`.

## Control flow

There are no methods declared locally. The NameNode RPC server advertises/implements this aggregate so server-side code can expose all protocol facets through one implementation type.

## State and persistence behavior

The interface has no state. Implementing classes coordinate client namespace operations, DataNode block reports, admin refreshes, HA transitions, and NameNode protocol operations.

## Dependencies and integration points

This is an integration hub for HDFS client, DataNode, HA, reconfiguration, security refresh, and admin RPCs. Any addition/removal changes the NameNode's advertised surface.

## Risks and test signals

Risks include accidentally omitting a protocol from the aggregate or exposing a protocol on an unintended RPC server. Tests should cover NameNode RPC startup, protocol proxy creation, ACL enforcement per protocol, and HA/admin command routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java

## Purpose

`NamenodeRegistration` carries subordinate NameNode identity during registration with an active NameNode. It includes RPC/HTTP addresses, storage information, and the subordinate node role.

## Important APIs and types

The class extends `StorageInfo` and implements `NodeRegistration`. Fields are `rpcAddress`, `httpAddress`, and `NamenodeRole role`. Methods include `getAddress()`, `getHttpAddress()`, `getRegistrationID()`, `getVersion()`, `getRole()`, `isRole()`, and `toString()`.

## Control flow

A backup or checkpoint NameNode builds this object and calls `NamenodeProtocol.registerSubordinateNamenode`. The active NameNode uses storage identity and role to validate and track the subordinate.

## State and persistence behavior

The object is transient, reflecting persistent NameNode storage layout, namespace ID, cluster ID, and creation time inherited from `StorageInfo`.

## Dependencies and integration points

It depends on `Storage`, `StorageInfo`, `HdfsServerConstants.NamenodeRole`, and `NodeRegistration`. It integrates with checkpoint/backup NameNode registration and diagnostics.

## Risks and test signals

Risks include stale storage identity, wrong role checks, and address mismatches. Tests should cover registration ID derivation, role matching, toString output, and rejection of incompatible storage info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeRegistration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamespaceInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamespaceInfo.java

## Purpose

`NamespaceInfo` is returned by the NameNode during handshakes to describe namespace identity, block pool identity, software/build version, HA state, and supported protocol capabilities.

## Important APIs and types

It extends `StorageInfo`. Fields include `buildVersion`, `blockPoolID`, `softwareVersion`, `capabilities`, and `HAServiceState state`. The `Capability` enum currently includes `STORAGE_BLOCK_REPORT_BUFFERS`, with a computed supported-capability mask. Methods expose getters, testing setters for capabilities/state, capability checks, setters for cluster and block pool IDs, `toString()`, and `validateStorage(NNStorage)`.

## Control flow

NameNode server constructors default capabilities to supported values. DataNodes and other clients receive namespace info through `versionRequest`, then validate layout, namespace ID, cluster ID, cTime, and block pool ID before joining. Capability checks gate optional optimized behavior such as block-report buffer transfer.

## State and persistence behavior

The object represents persistent NameNode storage identity inherited from `StorageInfo` and `NNStorage`, but it is a transient handshake value. `validateStorage` compares it against persistent `NNStorage` and throws detailed `IOException` on mismatch.

## Dependencies and integration points

It depends on `StorageInfo`, `HdfsServerConstants`, `NNStorage`, `VersionInfo`, `HAServiceState`, and `Preconditions`. It integrates with DataNode/NameNode handshakes, HA state advertisement, and feature negotiation.

## Risks and test signals

Risks include capability bit ordering changes, null block pool IDs from non-`NNStorage` copies, testing setters hiding invalid server state, and strict storage validation breaking mixed-version clusters. Tests should cover every constructor, capability mask behavior, unknown capability rejection, storage validation success/failure, HA state propagation, and serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamespaceInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java

## Purpose

`NodeRegistration` is the shared interface for registration records sent to a NameNode by server-side HDFS participants.

## Important APIs and types

It declares `getAddress()`, `getRegistrationID()`, `getVersion()`, and `toString()`. `DatanodeRegistration` and `NamenodeRegistration` implement it.

## Control flow

Registration code consumes this interface to validate identity, layout version, and address regardless of whether the registering node is a DataNode or subordinate NameNode.

## State and persistence behavior

The interface owns no state. Implementations usually derive registration ID from persistent `StorageInfo`.

## Dependencies and integration points

It is part of the `server.protocol` registration contract and integrates with NameNode admission/compatibility checks.

## Risks and test signals

Risks are too-small abstraction boundaries: implementations may differ in equality, address source, or storage identity. Tests should cover both known implementations and any generic registration validation logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java

## Purpose

`ReceivedDeletedBlockInfo` is the per-block entry used in incremental block reports to tell the NameNode that a DataNode is receiving, has received, or has deleted a block.

## Important APIs and types

The class stores `Block block`, `BlockStatus status`, and deletion hints. `BlockStatus` maps `RECEIVING_BLOCK`, `RECEIVED_BLOCK`, and `DELETED_BLOCK` to numeric codes with `fromCode(int)`. Methods include getters/setters for block and hints, `getStatus()`, `blockEquals`, `isDeletedBlock`, `equals`, `hashCode`, and `toString`.

## Control flow

DataNode storage code creates entries and wraps them in `StorageReceivedDeletedBlocks` for `DatanodeProtocol.blockReceivedAndDeleted`. The NameNode updates pending/received/deleted block state based on `status`.

## State and persistence behavior

The value is mutable and transient. It reflects DataNode on-disk block state but is not persisted directly.

## Dependencies and integration points

It depends on `Block` and integrates with incremental block reports, replication/deletion tracking, and protobuf encoding of status codes.

## Risks and test signals

`equals` requires non-null `delHints`; two otherwise equal entries with null hints compare false. `hashCode` intentionally asserts false and returns 0, so this type is unsafe for hash collections. Tests should cover status code mapping, null hints, deleted-block detection, and NameNode handling for each status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java

## Purpose

`RegisterCommand` tells a DataNode to register or re-register with the NameNode.

## Important APIs and types

It extends `DatanodeCommand` with action `DatanodeProtocol.DNA_REGISTER` and exposes a singleton `REGISTER`.

## Control flow

The NameNode returns this command in a heartbeat response when it needs a DataNode to refresh registration. The class comment notes it cannot be combined with other commands because DataNode processing skips the rest of the response after handling registration.

## State and persistence behavior

There is no payload. Processing triggers a DataNode registration handshake that refreshes NameNode in-memory DataNode state.

## Dependencies and integration points

It depends on `DatanodeProtocol` action codes and DataNode heartbeat command dispatch.

## Risks and test signals

Risks include combining it with other commands, causing skipped work, or sending it repeatedly during registration failures. Tests should cover singleton serialization, command ordering, and DataNode behavior when registration is required mid-heartbeat cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLog.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLog.java

## Purpose

`RemoteEditLog` describes one edit-log segment available from a remote NameNode.

## Important APIs and types

Fields are `startTxId`, `endTxId`, and `isInProgress`, defaulting txids to `INVALID_TXID`. Constructors infer in-progress status when `endTxId` is invalid or accept it explicitly. It implements `Comparable` by start txid then end txid, equality delegates to comparison, and `GET_START_TXID` is a null-safe `Function`.

## Control flow

NameNode protocol implementations build sorted lists of `RemoteEditLog` values for `RemoteEditLogManifest`. Consumers use ordering and string forms to fetch finalized or in-progress edit segments.

## State and persistence behavior

The object is transient metadata for persistent edit-log files. It does not validate txid ranges on construction.

## Dependencies and integration points

It uses Hadoop's shaded `ComparisonChain` and `HdfsServerConstants.INVALID_TXID`. It integrates with checkpointing and edit-log transfer.

## Risks and test signals

`hashCode` multiplies txids and can collide/overflow; equality ignores `isInProgress` if txids match. Tests should cover ordering, in-progress string output, invalid txid handling, manifest sorting, and equality when only the in-progress flag differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java

## Purpose

`RemoteEditLogManifest` is a list of remote edit-log segments plus the committed transaction ID known by the provider.

## Important APIs and types

Fields are `List<RemoteEditLog> logs` and `committedTxnId`. Constructors accept a log list and optional committed txid. `checkState()` enforces non-null logs and non-overlapping sorted order. `getLogs()` returns an unmodifiable view.

## Control flow

`NamenodeProtocol.getEditLogManifest` returns this object to checkpoint or tailing clients. The constructor validates segment order immediately so callers do not fetch overlapping ranges.

## State and persistence behavior

The object is transient and represents persistent edit-log files. It does not copy the input list, so external mutation of the original list after construction can bypass validation despite `getLogs()` being unmodifiable.

## Dependencies and integration points

It depends on `RemoteEditLog`, `Preconditions`, `Joiner`, and `HdfsServerConstants`. It integrates with checkpointing, backup nodes, and edit-log fetchers.

## Risks and test signals

Risks include unsorted lists, overlapping ranges, in-progress logs with invalid end txids, and post-construction mutation of the backing list. Tests should cover overlap rejection, gap allowance, unmodifiable getter behavior, committed txid formatting, and defensive-copy expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RemoteEditLogManifest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java

## Purpose

`ReplicaRecoveryInfo` describes a replica's block identity, disk length, generation stamp, and original replica state during block recovery.

## Important APIs and types

The class extends `Block` and stores `ReplicaState originalState`. The constructor calls `set(blockId, diskLen, gs)`. It exposes `getOriginalReplicaState()` and appends length/state to `toString()`. Equality and hash code defer to `Block`.

## Control flow

`InterDatanodeProtocol.initReplicaRecovery` returns this value to the recovery coordinator, which compares replica states and lengths before deciding how to update replicas.

## State and persistence behavior

It is a transient snapshot of persistent DataNode replica metadata. Equality ignores original replica state because it delegates to `Block`.

## Dependencies and integration points

It depends on `Block` and `HdfsServerConstants.ReplicaState`, and integrates with lease recovery and DataNode replica update RPCs.

## Risks and test signals

Risks include state being ignored in equality, null `originalState` causing `toString()` failure, and mismatched disk length/generation values. Tests should cover each replica state, equality semantics, and recovery decisions when states differ but block IDs match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java

## Purpose

`ServerCommand` is the common base for protocol-specific commands sent from a NameNode to other HDFS server components.

## Important APIs and types

It stores a final integer `action`, exposes `getAction()`, and formats `toString()` as class name plus action code. `DatanodeCommand` and `NamenodeCommand` derive from it.

## Control flow

NameNode implementations construct concrete command subclasses with action constants from the relevant protocol. Receivers dispatch on `getAction()` and command subtype.

## State and persistence behavior

The action code is immutable and transient. Runtime side effects occur only when receivers process commands.

## Dependencies and integration points

It defines the shared shape used by DataNode and subordinate NameNode command channels and is serialized by protocol translators.

## Risks and test signals

Integer action spaces are protocol-specific, so using a command in the wrong channel can be ambiguous. Tests should cover action preservation, toString diagnostics, and translator behavior for unknown actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java

## Purpose

`StorageBlockReport` pairs one DataNode storage volume with its full block report payload.

## Important APIs and types

The immutable fields are `DatanodeStorage storage` and `BlockListAsLongs blocks`. Getters expose both. `BlockListAsLongs` encodes finalized and under-construction replicas compactly as longs.

## Control flow

DataNodes build an array of these objects for `DatanodeProtocol.blockReport`, one per storage. The NameNode reads storage identity and block list to reconcile its block map.

## State and persistence behavior

The object is transient. It reports persistent DataNode block state but does not persist or copy it.

## Dependencies and integration points

It depends on `DatanodeStorage`, `BlockListAsLongs`, `DatanodeProtocol`, and NameNode block-manager processing.

## Risks and test signals

Risks include null storage/block lists, wrong storage IDs, compact block-list decoding mistakes, and memory pressure from full reports. Tests should cover multi-storage reports, empty storages, under-construction encoding, and NameNode reconciliation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java

## Purpose

`StorageReceivedDeletedBlocks` groups incremental block-report entries for one DataNode storage.

## Important APIs and types

It stores `DatanodeStorage storage` and `ReceivedDeletedBlockInfo[] blocks`. The deprecated constructor accepts a storage ID string and wraps it in a new `DatanodeStorage`; `getStorageID()` is also deprecated. New code uses `getStorage()` and the `DatanodeStorage` constructor.

## Control flow

DataNodes send arrays of these values to `DatanodeProtocol.blockReceivedAndDeleted`. The NameNode applies each block status in the context of the specified storage.

## State and persistence behavior

The object is immutable in references but does not copy the block array. It transiently reports DataNode storage changes.

## Dependencies and integration points

It depends on `DatanodeStorage`, `ReceivedDeletedBlockInfo`, and incremental block-report processing. Deprecated methods preserve wire/source compatibility.

## Risks and test signals

Risks include array mutation after construction, storage ID compatibility, and null block arrays. Tests should cover deprecated/new constructors, toString output, per-storage incremental updates, and NameNode behavior for mixed received/deleted entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java

## Purpose

`VolumeFailureSummary` summarizes failed DataNode storage locations, the last failure time, and estimated lost capacity.

## Important APIs and types

Fields are `String[] failedStorageLocations`, `lastVolumeFailureDate` in epoch milliseconds, and `estimatedCapacityLostTotal` in bytes. Getters expose all three.

## Control flow

DataNodes include this summary in heartbeats and lifelines. The NameNode uses it for DataNode health, admin reporting, and capacity accounting.

## State and persistence behavior

The value is transient but reports persistent/local volume failure state. The failed-location array is not defensively copied.

## Dependencies and integration points

It integrates with `DatanodeProtocol.sendHeartbeat`, `DatanodeLifelineProtocol.sendLifeline`, DataNode volume checkers, and NameNode health reporting.

## Risks and test signals

Risks include mutable array exposure, unsorted or duplicate locations despite the getter comment, negative/unknown capacity estimates, and clock skew in failure dates. Tests should cover empty/no-failure summaries, multiple failed volumes, lost-capacity aggregation, and heartbeat/lifeline serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/VolumeFailureSummary.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java

## Purpose

`ExternalSPSContext` adapts an externally running `StoragePolicySatisfier` to NameNode and DFS services. It supplies file metadata, storage policy lookup, datanode topology, SPS path polling, block-move submission, hint cleanup, and metrics registration.

## Important APIs and types

The class implements `Context`. It owns `SPSService service`, `NameNodeConnector nnc`, default `BlockStoragePolicySuite`, `ExternalSPSFilePathCollector`, `ExternalSPSBlockMoveTaskHandler`, `ExternalBlockMovementListener`, and optional `ExternalSPSBeanMetrics`. Methods include `isRunning`, `isInSafeMode`, `getNetworkTopology`, `isFileExist`, `getStoragePolicy`, `removeSPSHint`, `getNumLiveDataNodes`, `getFileInfo`, `getLiveDatanodeStorageReport`, `getNextSPSPath`, `scanAndCollectFiles`, `submitMoveTask`, `notifyMovementTriedBlocks`, and metrics helpers.

## Control flow

The external service creates this context, then SPS asks it for NameNode state as work progresses. It converts inode IDs to reserved file-ID paths, uses DFS clients through `NameNodeConnector`, builds a `NetworkTopology` from target DataNodes, delegates scans to the collector, delegates moves to the external handler, and records attempted movement blocks in an internal listener.

## State and persistence behavior

Runtime state is mostly references, a default policy suite, an in-memory list of attempted movement blocks, and JMX registration. Persistent HDFS effects occur when it removes the SPS xattr hint or when delegated block moves change placement.

## Dependencies and integration points

It bridges `StoragePolicySatisfier`, `NameNodeConnector`, DFS client APIs, `BlockStoragePolicySuite`, `NetworkTopology`, `DatanodeStorageReport`, and ExternalSPS metrics.

## Risks and test signals

Risks include `closeMetrics()` NPE if metrics were never initialized, safe-mode errors being treated as false, XAttr removal swallowing IOExceptions when the hint disappears, and unbounded attempted-block list growth. Tests should cover file-ID path conversion, missing files, safe mode failures, xattr removal races, storage reports, metrics lifecycle, and move-task delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java

## Purpose

`ExternalSPSFaultInjector` is a test hook for injecting failures into external SPS block movement retry paths.

## Important APIs and types

It keeps a static singleton `instance`, with visible-for-testing `getInstance()` and `setInstance(...)`. `mockAnException(int retry)` is a no-op by default and may be overridden to throw `IOException`.

## Control flow

`ExternalSPSBlockMoveTaskHandler.BlockMovingTask.moveBlock()` calls `mockAnException(retry)` before obtaining a block token and moving the block. Tests can replace the singleton to force failures on specific retry attempts.

## State and persistence behavior

State is only the static singleton reference. There is no persistence.

## Dependencies and integration points

It integrates with external SPS move retry tests and depends on `VisibleForTesting` and `IOException`.

## Risks and test signals

Because the singleton is static and mutable, tests must reset it to avoid cross-test leakage. Tests should verify injected failures produce expected retry counts and that the default injector has no behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java

## Purpose

`ExternalSPSFilePathCollector` recursively scans a file-ID path for files needing storage policy satisfaction and submits work items to external SPS.

## Important APIs and types

The class implements `FileCollector`. It holds a `DistributedFileSystem`, `SPSService`, and queue limit from `DFS_STORAGE_POLICY_SATISFIER_QUEUE_LIMIT_KEY`. Core methods are `scanAndCollectFiles(long pathId)`, private recursive `processPath(Long startID, String childPath)`, `checkProcessingQueuesFree()`, and `remainingCapacity()`.

## Control flow

Construction obtains the default DFS, logging if unavailable. `scanAndCollectFiles` lazily recreates DFS if needed, converts the inode ID to a file-ID path, and calls `processPath`. `processPath` pages through `listPaths`, adds files as `ItemInfo(startID, childFileId)`, waits when the SPS processing queue is full, and recursively descends directories. If no files are found, it submits an empty completed list so the SPS hint can be removed; otherwise it marks scanning complete for the root path.

## State and persistence behavior

Runtime state is the DFS handle and queue-limit value. Persistent HDFS state is only read during directory listing; SPS service state is updated through processing queues and scan-complete markers.

## Dependencies and integration points

It depends on `DistributedFileSystem`, `DFSUtilClient.makePathFromFileId`, `DirectoryListing`, `HdfsFileStatus`, `ItemInfo`, and `SPSService`.

## Risks and test signals

Risks include deep recursion, sleeping forever when queues do not drain, continuing after interruption, ignoring directories that fail listing, and assuming the default FS is HDFS. Tests should cover file, empty directory, nested directory, paginated listing, queue backpressure, DFS initialization failure/recovery, and scan-completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalSPSFilePathCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java

## Purpose

`ExternalStoragePolicySatisfier` is the standalone entry point for running HDFS Storage Policy Satisfier outside the NameNode process.

## Important APIs and types

The class is final with a private constructor. `main` creates configuration, performs secure login, constructs `StoragePolicySatisfier`, obtains a `NameNodeConnector`, creates `ExternalSPSContext`, starts SPS in `StoragePolicySatisfierMode.EXTERNAL`, registers metrics, and joins. `secureLogin` logs in using SPS keytab/principal config. `getNameNodeConnector` retries connector creation and exits if another external SPS instance is running.

## Control flow

Startup logs standard daemon messages, initializes security, connects to internal NameNode RPC URIs using `NameNodeConnector.newNameNodeConnectors`, then starts SPS. On any throwable it logs and terminates with exit code 1. The finally block closes the connector and metrics if initialized. Connector creation retries every three seconds unless it detects the "Another ExternalStoragePolicySatisfier is running" lock condition.

## State and persistence behavior

The process holds a NameNodeConnector lock/path (`MOVER_ID_PATH`) to prevent concurrent movers/SPS instances. It mutates HDFS block placement and SPS xattr hints through the context and service; no direct persistence happens in this wrapper.

## Dependencies and integration points

It integrates `HdfsConfiguration`, Kerberos `SecurityUtil`, `UserGroupInformation`, `DFSUtil.getInternalNsRpcUris`, `NameNodeConnector`, `StoragePolicySatisfier`, `ExternalSPSContext`, and metrics.

## Risks and test signals

Risks include infinite retry on misconfiguration, brittle string comparison for duplicate-instance detection, metrics/context cleanup ordering, and secure-login principal host resolution. Tests should cover secure and simple auth startup, duplicate instance exit, connector retry, external mode startup, and cleanup on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java

## Purpose

`ExternalSPSBeanMetrics` exposes external Storage Policy Satisfier runtime counters through a JMX MBean.

## Important APIs and types

The class implements `ExternalSPSMXBean`. It registers a `StandardMBean` under `ExternalSPS/ExternalSPS`, stores the returned `ObjectName`, and delegates metrics to `StoragePolicySatisfier`. Public metrics are processing queue size, movement-finished block count, and attempted item count. Visible-for-testing helpers mutate SPS queues/sets to exercise metric changes.

## Control flow

Construction registers the MBean and throws a runtime exception on non-compliant MBean setup. `close()` unregisters the MBean and nulls the object name. Metric getters read current SPS queue/monitor state on demand.

## State and persistence behavior

State is runtime-only: the MBean registration and reference to SPS. No persistent data is written.

## Dependencies and integration points

It depends on `MBeans`, JMX `StandardMBean`, `ExternalSPSMXBean`, `StoragePolicySatisfier`, `ItemInfo`, and `Block`. It is initialized by `ExternalSPSContext`.

## Risks and test signals

Risks include duplicate MBean registration, failure to unregister on shutdown, direct test mutation of internal SPS collections, and null SPS references. Tests should cover registration, close idempotence, getter values before/after queue changes, and ExternalSPS process shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSBeanMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java

## Purpose

`ExternalSPSMXBean` is the JMX management interface for external Storage Policy Satisfier metrics.

## Important APIs and types

The stable private interface declares `getProcessingQueueSize()`, `getMovementFinishedBlocksCount()`, and `getAttemptedItemsCount()`.

## Control flow

JMX clients call these methods through the registered `ExternalSPSBeanMetrics` MBean. No implementation lives in the interface.

## State and persistence behavior

The interface has no state. Implementations read external SPS runtime state.

## Dependencies and integration points

It is consumed by `ExternalSPSBeanMetrics` and Hadoop's JMX/MBeans helper.

## Risks and test signals

Because this is a management interface, method renames or signature changes break JMX clients. Tests should cover MBean compliance, exported attribute names, and metric values under representative SPS queue/attempt states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/ExternalSPSMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/package-info.java

## Purpose

This package-info documents the `org.apache.hadoop.hdfs.server.sps.metrics` package as the external SPS JMX metrics package.

## Important APIs and types

The package contains `ExternalSPSMXBean` and `ExternalSPSBeanMetrics`, which define and register the externally visible metric attributes.

## Control flow

There is no executable flow. JavaDoc/package metadata is consumed by documentation generation and annotation processing.

## State and persistence behavior

No runtime state or persistence is defined here.

## Dependencies and integration points

It integrates with Java package documentation for the external SPS metrics namespace.

## Risks and test signals

Risk is low. Documentation should stay aligned with the actual package role if metrics are added or moved. Build/Javadoc checks are the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java

## Purpose

This package-info describes the external/server SPS package as a mechanism for satisfying a path's storage policy.

## Important APIs and types

The package includes the external SPS process entry point, context, file collector, block move handler, and fault injector. It is annotated `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control flow

There is no executable code. The annotations communicate that the package is internal and unstable.

## State and persistence behavior

No state is defined in this file. State lives in the package classes and the HDFS namespace/block placement they manipulate.

## Dependencies and integration points

It depends only on Hadoop classification annotations and package-level Java metadata.

## Risks and test signals

Risk is documentation drift: the package has both external-process orchestration and block movement support. Javadoc/package annotation checks are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java

## Purpose

`AdminHelper` centralizes shared command-line utility code for HDFS admin tools such as cache, crypto, and storage policy administration.

## Important APIs and types

It provides DFS resolution (`getDFS`, URI overload, `checkAndGetDFS`), exception formatting (`prettifyException`), table formatting (`getOptionDescriptionListing`), cache TTL/limit parsers, command resolution (`determineCommand`), usage printing, the `Command` interface, and the built-in `HelpCommand`.

## Control flow

Admin tools call `determineCommand` on the first argument, then invoke the returned command. `-help` returns a dynamic `HelpCommand` that prints either all command long usages or a specific command's long usage. DFS resolution handles `ViewFileSystemOverloadScheme` by unwrapping the raw mounted filesystem for the configured default URI before requiring `DistributedFileSystem`.

## State and persistence behavior

The helper is stateless. It parses strings and returns wrappers; actual persistence is performed by tool commands against HDFS.

## Dependencies and integration points

It integrates Hadoop `Configuration`, `FileSystem`, `DistributedFileSystem`, ViewFS overload scheme, `CachePoolInfo`, `DFSUtil`, and `TableListing`. The `Command` contract is implemented by `CacheAdmin` and `CryptoAdmin` nested commands.

## Risks and test signals

Risks include incorrect ViewFS unwrapping, `prettifyException` truncating useful diagnostics, help returning exit code 1 when all help is printed, and parser edge cases for "never" and "unlimited". Tests should cover HDFS and non-HDFS filesystems, ViewFS overload, command lookup, help for unknown commands, TTL parsing, and limit parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java

## Purpose

`CacheAdmin` implements the `hdfs cacheadmin` CLI for managing HDFS cache directives and cache pools.

## Important APIs and types

The tool extends `Configured` and implements `Tool`. Command classes implement `AdminHelper.Command`: `-addDirective`, `-modifyDirective`, `-listDirectives`, `-removeDirective`, `-removeDirectives`, `-addPool`, `-modifyPool`, `-removePool`, and `-listPools`. It uses `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CacheDirectiveStats`, `CachePoolInfo`, `CachePoolEntry`, `CachePoolStats`, `CacheFlag.FORCE`, `FsPermission`, `RemoteIterator`, and `TableListing`.

## Control flow

`run` validates the first argument, dispatches to a command, and converts `IllegalArgumentException` to exit `-1`. Directive commands parse options, validate required IDs/paths/pools, build `CacheDirectiveInfo`, optionally set `FORCE`, and call `DistributedFileSystem` cache APIs. Listing commands stream remote iterators into tables and optionally add stats. Pool commands parse owner/group/mode/limit/default replication/max TTL, build `CachePoolInfo`, and call add/modify/remove/list APIs.

## State and persistence behavior

The CLI itself is stateless. It mutates persistent NameNode cache metadata: directives, pools, permissions, limits, TTLs, and default replication. Listing reads current NameNode cache manager state.

## Dependencies and integration points

It depends on `AdminHelper`, `DistributedFileSystem`, HDFS protocol cache classes, Hadoop CLI `ToolRunner`, `StringUtils` option parsing, Commons `WordUtils`, shaded Guava `Joiner`, and `TableListing`.

## Risks and test signals

Risks include partial success in `-removeDirectives`, insufficient numeric validation for replication/default replication, octal mode parsing errors, path URI selection for ViewFS or federated paths, and list output compatibility. Tests should cover every command's required/unknown arguments, success and NameNode failure exit codes, "never"/"unlimited" parsing, `-force` propagation, stats output, and partial deletion failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java

## Purpose

`CryptoAdmin` implements the `hdfs crypto` CLI for HDFS encryption zones, file encryption information, trash provisioning, and zone re-encryption commands/status.

## Important APIs and types

The tool extends `Configured` and implements `Tool`. Commands are `-createZone`, `-listZones`, `-provisionTrash`, `-getFileEncryptionInfo`, `-reencryptZone`, and `-listReencryptionStatus`. It uses `HdfsAdmin`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `EncryptionZone`, `FileEncryptionInfo`, `ReencryptAction`, `ZoneReencryptionStatus`, `RemoteIterator`, `TableListing`, and `Time`.

## Control flow

`run` dispatches to a command and reports unknown commands/argument exceptions. `-createZone` requires `-path` and `-keyName`, creates an `HdfsAdmin` for the path URI, and provisions trash while creating the zone. `-listZones` lists all zones from the default filesystem. `-getFileEncryptionInfo` fetches and prints stable file encryption info. `-provisionTrash` provisions an encryption-zone trash directory. `-reencryptZone` requires exactly one of `-start` or `-cancel` plus `-path`, then submits the action. `-listReencryptionStatus` prints status rows and emits a warning when failures are present.

## State and persistence behavior

The CLI mutates persistent NameNode encryption-zone metadata, trash directories, and re-encryption work queues. It also reads encryption info and re-encryption status.

## Dependencies and integration points

It integrates with HDFS encryption-zone administration through `HdfsAdmin`, Hadoop key-provider-backed encryption metadata, NameNode re-encryption status, CLI option parsing, and generic tool execution.

## Risks and test signals

`-getFileEncryptionInfo` and `-provisionTrash` do not explicitly reject missing `-path` before constructing `new Path(path)`, so missing path may surface as an argument exception rather than command-specific help. `prettifyException` assumes a non-null localized message. Tests should cover all commands, missing/extra arguments, create-zone trash provisioning, list output, null encryption info, re-encryption start/cancel exclusivity, failure warning output, and exit codes for NameNode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java -->
