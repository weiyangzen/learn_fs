<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MountTablePBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MountTablePBImpl.java

## Purpose
Protobuf implementation of the `MountTable` State Store record.

## APIs, Types, and Functions
Wraps `MountTableRecordProto`. It maps source path, destination list, timestamps, read-only, destination order, fault tolerance, owner/group/mode, and quota. Helper conversions translate between proto `DestOrder` and resolver `DestinationOrder`; quota mapping handles namespace, space, and per-storage-type quota/usage.

## Control Flow, State, and Persistence
Destination getters rebuild `RemoteLocation` objects from repeated `RemoteLocationProto` entries; setters clear and repopulate the repeated field. `addDestination()` rejects exact duplicate namespace/path pairs. ACL getters provide superuser/supergroup/default mode fallbacks when fields are absent. Quota getters initialize reset/default arrays and fill any serialized quota data.

## Dependencies and Integration
Used by mount table requests/responses, Router admin, quota operations, resolvers, and State Store drivers. Depends on HDFS quota protos, `StorageType`, `RouterQuotaUsage`, `RouterAdminServer`, `RouterPermissionChecker`, and `FederationProtocolPBTranslator`.

## Risks and Test Signals
`addDestination()` assumes `getDestinations()` is non-null. Destination order conversion defaults unknown values to HASH. Storage type quota conversion depends on enum name compatibility. Mount table serialization, quota, ACL fallback, duplicate destination, and multi-destination resolver tests are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MountTablePBImpl.java -->
