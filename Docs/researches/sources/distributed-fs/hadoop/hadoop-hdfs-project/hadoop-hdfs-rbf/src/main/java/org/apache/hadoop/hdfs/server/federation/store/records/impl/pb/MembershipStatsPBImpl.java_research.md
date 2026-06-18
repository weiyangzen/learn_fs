<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatsPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatsPBImpl.java

## Purpose
Protobuf implementation of the embedded `MembershipStats` record.

## APIs, Types, and Functions
Wraps `NamenodeMembershipStatsRecordProto`. It provides direct setters/getters for capacity, file/block counters, datanode state counts, corrupt files, replication scheduling, missing blocks with replication factor one, badly distributed blocks, low redundancy priorities, EC low redundancy, and pending SPS paths.

## Control Flow, State, and Persistence
All methods directly map abstract stats fields to protobuf builder or proto-or-builder accessors. Stats are embedded in `MembershipState` and do not carry independent timestamps or keys.

## Dependencies and Integration
Used by `MembershipStatePBImpl`, resolver ordering such as available space, and metrics-fed heartbeat paths. Depends on generated federation protos and `FederationProtocolPBTranslator`.

## Risks and Test Signals
The proto field for highest priority EC blocks is capitalized `HighestPriorityLowRedundancyECBlocks`, while the generated accessor still maps through Java naming; schema changes here are risky. Serialization tests and resolver behavior using capacity counters are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatsPBImpl.java -->
