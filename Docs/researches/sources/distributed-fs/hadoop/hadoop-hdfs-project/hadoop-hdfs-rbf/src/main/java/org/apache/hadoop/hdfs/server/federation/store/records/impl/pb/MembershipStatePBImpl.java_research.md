<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatePBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatePBImpl.java

## Purpose
Protobuf implementation of the `MembershipState` Namenode registration record.

## APIs, Types, and Functions
Wraps `NamenodeMembershipRecordProto`. Setters for most optional strings clear the field on null; getters return null when `has*` is false. It maps `FederationNamenodeServiceState` to/from strings, embeds `MembershipStatsPBImpl`, and exposes last contact and timestamps.

## Control Flow, State, and Persistence
The record builder accumulates membership identity, addresses, state, safemode, stats, and timestamps. `getStats()` creates a serializer-backed stats record and injects the nested stats proto. `setDateModified()` refuses to update modification time once the state is `EXPIRED`, preserving expiration timing.

## Dependencies and Integration
Used by namenode heartbeat requests, membership stores, resolvers, and tests. Depends on generated membership protos, `StateStoreSerializer`, `MembershipStatsPBImpl`, and `FederationProtocolPBTranslator`.

## Risks and Test Signals
`setServiceAddress()` does not null-check unlike other string setters. Invalid state strings are swallowed and return `UNAVAILABLE`, while absent state returns null. Tests should cover serialization round trips, null optional fields, stats embedding, expiration timestamp behavior, and state parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/MembershipStatePBImpl.java -->
