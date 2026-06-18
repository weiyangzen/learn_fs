# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HdfsServer.proto

## Purpose

`HdfsServer.proto` defines shared server-side HDFS protobuf messages used by multiple private stable protocols, including block keys, block locations, edit-log manifests, namespace/storage information, replica recovery state, checkpoint commands, NameNode registration, and HA heartbeat status. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `HdfsServerProtos`, and imports `hdfs.proto` and `HAServiceProtocol.proto`. Important messages include `BlockKeyProto`, `ExportedBlockKeysProto`, `BlockWithLocationsProto`, `BlocksWithLocationsProto`, `RemoteEditLogProto`, `RemoteEditLogManifestProto`, `NamespaceInfoProto`, `RecoveringBlockProto`, `CheckpointSignatureProto`, `CheckpointCommandProto`, `NamenodeCommandProto`, `VersionRequestProto`, `VersionResponseProto`, `StorageInfoProto`, `NamenodeRegistrationProto`, and `NNHAStatusHeartbeatProto`. It also defines `ReplicaStateProto`.

## Control Flow

This is a shared schema file rather than a service. Other RPC protocols import these messages to exchange version information, edit-log availability, block-token keys, block replica recovery data, checkpoint commands, storage identity, and HA state. For example, DataNode heartbeats return `NNHAStatusHeartbeatProto`, inter-datanode recovery uses `RecoveringBlockProto` and `ReplicaStateProto`, and journal/name-node protocols return `RemoteEditLogManifestProto`.

## State and Persistence Behavior

The messages describe important persistent or semi-persistent cluster state: storage layout version, namespace/cluster IDs, block pool IDs, block-token keys, edit-log segment ranges, checkpoint signatures, and recovery generation stamps. They are wire schemas, but their field layout constrains generated Java and upgrade compatibility.

## Dependencies and Integration Points

Integration points span DataNode protocol, inter-datanode protocol, NameNode protocol, journal protocol, qjournal protocol, checkpointing, block-token security, HA state reporting, rolling upgrade, erasure-coded block recovery, and remote edit-log transfer.

## Risks and Edge Cases

The misspelled `namespceID` field in `StorageInfoProto` is part of the generated API and must not be renamed without compatibility handling. Required fields in storage/namespace messages can break mixed-version nodes if changed. Optional HA state and capabilities fields must be handled when absent. Edit-log range and checkpoint signature correctness is critical to avoid namespace divergence.

## Test Signals

Tests should cover translator round trips for storage/namespace info, exported block keys, remote edit-log manifests, recovery blocks, checkpoint signatures, HA status, and mixed-version decoding when optional fields are missing.
