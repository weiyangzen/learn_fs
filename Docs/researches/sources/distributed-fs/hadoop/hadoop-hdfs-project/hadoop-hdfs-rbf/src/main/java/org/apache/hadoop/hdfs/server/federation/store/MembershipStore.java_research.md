# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MembershipStore.java

## Purpose
`MembershipStore` defines the state-store management API for federated NameNode membership and HA state records.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<MembershipState>` with expired-record override enabled. Abstract methods include `namenodeHeartbeat`, `getNamenodeRegistrations`, `getExpiredNamenodeRegistrations`, `getNamespaceInfo`, and `updateNamenodeRegistration`.

## Control Flow
Implementations receive heartbeat requests from router heartbeat services, write membership records, query cached registrations, aggregate namespace info, identify expired entries, and override specific NameNode registration state.

## State, Persistence, And Dependencies
Persistent state is `MembershipState` records in the driver backend. Cache state is periodically refreshed and expired membership records can be overridden or deleted by the base class using configured expiration/deletion intervals.

## Integration Points
`RouterHeartbeatService` writes NameNode observations. `ActiveNamenodeResolver` and router RPC routing read membership state. `StateStoreService` registers `MembershipStoreImpl` and configures membership expiration.

## Risks
Federation correctness depends on timely cache refresh and consistent quorum/aggregation in implementations. Expiration overrides may race with fresh heartbeats from other routers. Abstract requests/responses need compatible protocol implementations.

## Test Signals
Tests should cover heartbeat upserts, HA state updates, expired and deleted membership handling, namespace info aggregation, cache refresh, concurrent router observations, and unavailable state-store behavior.
