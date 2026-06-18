<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/StateStoreVersionPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/StateStoreVersionPBImpl.java

## Purpose
Protobuf implementation of embedded `StateStoreVersion`.

## APIs, Types, and Functions
Wraps `StateStoreVersionRecordProto`. Provides PBRecord methods plus `getMembershipVersion()`, `setMembershipVersion(long)`, `getMountTableVersion()`, and `setMountTableVersion(long)`.

## Control Flow, State, and Persistence
The class directly maps version counters to proto fields. It is embedded in `RouterStatePBImpl` rather than stored as a standalone row.

## Dependencies and Integration
Used by router heartbeat and State Store version propagation. Depends on generated federation protos and `FederationProtocolPBTranslator`.

## Risks and Test Signals
Default absent counters read as zero, which may represent either unknown or initial version. Router heartbeat/version tests should verify transitions after mount table and membership updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/StateStoreVersionPBImpl.java -->
