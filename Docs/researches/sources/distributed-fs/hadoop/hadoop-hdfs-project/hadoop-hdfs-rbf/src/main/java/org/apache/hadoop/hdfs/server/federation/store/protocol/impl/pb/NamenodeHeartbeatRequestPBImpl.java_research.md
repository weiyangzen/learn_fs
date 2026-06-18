<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/NamenodeHeartbeatRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/NamenodeHeartbeatRequestPBImpl.java

## Purpose
PB implementation of `NamenodeHeartbeatRequest`, carrying a `MembershipState` record from a Router heartbeat into the State Store membership subsystem.

## APIs, Types, and Functions
Wraps `NamenodeHeartbeatRequestProto` and exposes `getNamenodeMembership()` and `setNamenodeMembership(MembershipState)`. Nested membership data is converted through `NamenodeMembershipRecordProto` and `MembershipStatePBImpl`.

## Control Flow, State, and Persistence
`setNamenodeMembership()` accepts only `MembershipStatePBImpl`, extracts its protobuf, and sets `namenodeMembership`. `getNamenodeMembership()` creates a serializer-selected `MembershipState`, requires it to be PB-backed, injects the nested proto, and returns it. The request is transient, but the contained membership record is later written or refreshed in the State Store.

## Dependencies and Integration
Depends on `StateStoreSerializer`, `MembershipState`, `MembershipStatePBImpl`, and generated federation protos. It is part of the heartbeat path from Router/Namenode monitoring into membership registration storage.

## Risks and Test Signals
The implementation throws `IOException` if the configured serializer is not PB-backed. It also does not check `hasNamenodeMembership()`, so an absent field becomes a default record. Tests around namenode heartbeat, membership registration, and serializer selection are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/NamenodeHeartbeatRequestPBImpl.java -->
