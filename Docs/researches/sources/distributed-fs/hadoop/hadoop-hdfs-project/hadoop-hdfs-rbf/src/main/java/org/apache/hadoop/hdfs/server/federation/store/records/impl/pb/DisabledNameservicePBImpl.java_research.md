<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/DisabledNameservicePBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/DisabledNameservicePBImpl.java

## Purpose
Protobuf-backed concrete record for disabled nameservice rows.

## APIs, Types, and Functions
Implements `DisabledNameservice` and `PBRecord` over `DisabledNameserviceRecordProto`. Provides proto access, base64 reading, nameservice ID getter/setter, and creation/modification timestamp getter/setter.

## Control Flow, State, and Persistence
The translator stores `nameServiceId`, `dateCreated`, and `dateModified`. The inherited primary key uses the nameservice ID, so the persisted row marks exactly one disabled nameservice.

## Dependencies and Integration
Used by nameservice disable/enable stores and admin APIs. Depends on `FederationProtocolPBTranslator` and generated federation protos.

## Risks and Test Signals
No null-clearing logic is present for nameservice ID, so callers should set a valid non-null ID. Nameservice manager tests should verify record creation, deletion on enable, and listing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/DisabledNameservicePBImpl.java -->
