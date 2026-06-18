# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/ClientDatanodeProtocol.proto

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/proto/ClientDatanodeProtocol.proto` is a Hadoop HDFS protobuf schema read as a complete 308-line source file. It defines private stable protobuf RPC surface from HDFS clients/admin tools to a DataNode. The header marks these private/stable wire contracts where field numbers, required/optional status, and generated Java names are compatibility-sensitive.

## Important APIs, Types, and Functions

Major declared protobuf types include `GetReplicaVisibleLengthRequestProto`, `GetReplicaVisibleLengthResponseProto`, `RefreshNamenodesRequestProto`, `RefreshNamenodesResponseProto`, `DeleteBlockPoolRequestProto`, `DeleteBlockPoolResponseProto`, `GetBlockLocalPathInfoRequestProto`, `GetBlockLocalPathInfoResponseProto`, `ShutdownDatanodeRequestProto`, `ShutdownDatanodeResponseProto`, `EvictWritersRequestProto`, `EvictWritersResponseProto`, `GetDatanodeInfoRequestProto`, `GetDatanodeInfoResponseProto`, `GetVolumeReportRequestProto`, `GetVolumeReportResponseProto`, `TriggerBlockReportRequestProto`, `TriggerBlockReportResponseProto`, `GetBalancerBandwidthRequestProto`, `GetBalancerBandwidthResponseProto`, `SubmitDiskBalancerPlanRequestProto`, `SubmitDiskBalancerPlanResponseProto`, `CancelPlanRequestProto`, `CancelPlanResponseProto`, `QueryPlanStatusRequestProto`, `QueryPlanStatusResponseProto`, `DiskBalancerSettingRequestProto`, `DiskBalancerSettingResponseProto`, `ClientDatanodeProtocolService`. RPCs declared in this file include `getReplicaVisibleLength`, `refreshNamenodes`, `deleteBlockPool`, `getBlockLocalPathInfo`, `shutdownDatanode`, `evictWriters`, `getDatanodeInfo`, `getVolumeReport`, `getReconfigurationStatus`, `startReconfiguration`, `listReconfigurableProperties`, `triggerBlockReport`, `getBalancerBandwidth`, `submitDiskBalancerPlan`, `cancelDiskBalancerPlan`, `queryDiskBalancerPlan`, `getDiskBalancerSetting`. The schema messages and service methods for replica visible length, federated NameNode refresh, block-pool deletion, deprecated local path lookup, shutdown/evict writers, DataNode info and volumes, reconfiguration, block report triggering, balancer bandwidth, and disk balancer plan submit/cancel/status/settings.

## Control Flow

There is no direct runtime control flow in the `.proto` file. Build tooling generates Java message and service classes, client translators populate request messages, server-side translators unpack them into HDFS domain objects, and responses are serialized back over Hadoop RPC or the DataTransfer stream path.

## State and Persistence Behavior

The file defines wire state rather than owning runtime storage. Required fields must be present on the wire, optional fields model feature evolution or nullable server results, repeated fields carry listings/status collections, and cursor fields support batched APIs. Some messages represent durable HDFS metadata such as blocks, quotas, snapshots, ACLs, xattrs, encryption zones, and erasure coding policies, but persistence is owned by NameNode/DataNode code outside the schema.

## Dependencies and Integration Points

Proto imports: `Security.proto`, `hdfs.proto`, `ReconfigurationProtocol.proto`. imports `Security.proto`, `hdfs.proto`, and `ReconfigurationProtocol.proto`; generated Java lands in `org.apache.hadoop.hdfs.protocol.proto.ClientDatanodeProtocolProtos` with generic services enabled. The generated Java classes are consumed by HDFS protobuf translators, client protocol proxies, NameNode RPC implementations, DataNode protocol handlers, and compatibility tests.

## Risks and Edge Cases

The largest risk is wire incompatibility: reusing field numbers, changing required fields, renaming generated service methods, or changing enum numeric values can break rolling upgrades and mixed-version clients. Required fields make omission fatal, while optional fields require translators to preserve old-client behavior. Large repeated responses also need batching/cursor handling to avoid memory pressure.

## Test Signals

Coverage should include protobuf translator round trips, old/new client compatibility, missing optional field behavior, enum numeric stability, batched-listing cursor behavior, and integration tests for the corresponding HDFS RPC or DataTransfer operation.
