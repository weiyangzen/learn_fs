# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RouterStore.java

## Purpose
`RouterStore` defines the state-store API for router registration and heartbeat records.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<RouterState>` with expired-record override enabled. Abstract methods are `getRouterRegistration`, `getRouterRegistrations`, and `routerHeartbeat`.

## Control Flow
Concrete implementations write router heartbeat state, query one router registration, or query all router registrations from cached/persistent state.

## State, Persistence, And Dependencies
Persistent state is `RouterState` records in the driver backend. Cache behavior and expired/deleted router-state overrides are inherited.

## Integration Points
Router heartbeat, admin status views, mount-table refresh across routers, and `StateStoreService` registration use this store.

## Risks
Stale router records can cause peers to target dead routers until expiration/deletion runs. The class Javadoc says no data is cached, but the class extends `CachedRecordStore`, so implementation behavior should be checked for consistency.

## Test Signals
Tests should cover heartbeat upsert, single/all registration queries, expiration and deletion, cache refresh, and peer-router discovery behavior.
