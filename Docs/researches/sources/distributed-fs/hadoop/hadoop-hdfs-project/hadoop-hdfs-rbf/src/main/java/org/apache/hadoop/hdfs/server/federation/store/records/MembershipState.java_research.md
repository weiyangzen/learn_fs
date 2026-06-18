<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipState.java

## Purpose
State Store schema for Namenode membership/registration data reported by Routers, implementing `FederationNamenodeContext`.

## APIs, Types, and Functions
Factory methods create initialized records and populate router, nameservice, namenode, cluster, block pool, RPC/service/lifeline/web addresses, state, safemode, and web scheme. Abstract accessors cover identity, addresses, service state, stats, and last contact. Utility methods include `like()`, `validate()`, `isAvailable()`, `overrideState()`, `compareNameTo()`, `getNamenodeKey()`, expiration/deletion setters, and `compareTo()`.

## Control Flow, State, and Persistence
Primary key is `(routerId, nameserviceId, namenodeId)`. Validation requires nameservice, web address, RPC address, and block pool except for bad states (`EXPIRED` or `UNAVAILABLE`). Expiration mutates state to `EXPIRED` and returns true so the State Store can commit the change; deletion is controlled by static class-level timeout.

## Dependencies and Integration
Used by membership stores, resolvers, heartbeats, and failover state logic. Concrete storage is `MembershipStatePBImpl` over `NamenodeMembershipRecordProto`, with nested `MembershipStats`.

## Risks and Test Signals
Static expiration/deletion settings affect all records in a JVM. Validation calls `getBlockPoolId().isEmpty()` after bad-state check and assumes non-null in non-bad states. Membership heartbeat, resolver selection, expiration, and state override tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MembershipState.java -->
