# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/MountTableStore.java

## Purpose
`MountTableStore` defines the cached management API for mount-table records that map global router paths to destination nameservices and paths.

## Important APIs, Types, And Functions
It extends `CachedRecordStore<MountTable>` and implements `MountTableManager`. Additional methods set `MountTableRefresherService` and `RouterQuotaManager`, expose the quota manager, and call `updateCacheAllRouters`.

## Control Flow
Concrete manager operations are inherited from `MountTableManager` and implemented by subclasses. After a mount-table mutation, implementations can call `updateCacheAllRouters`, which asks the refresher service to refresh this and peer routers.

## State, Persistence, And Dependencies
Persistent state is `MountTable` records in the state-store backend. Local state includes optional refresh service and quota manager references plus inherited cache state.

## Integration Points
Router path resolution, admin APIs, quota management, and `MountTableRefresherService` depend on this store. `StateStoreService` registers `MountTableStoreImpl`.

## Risks
If `refreshService` is null, mutations may not proactively refresh router caches. Refresh failure on state-store unavailability is logged but not thrown by `updateCacheAllRouters`. Quota manager coordination depends on implementation use.

## Test Signals
Tests should cover mount-table CRUD through the concrete implementation, cache refresh after mutation, refresh-service failure logging, quota-manager propagation, and router path resolution against cached records.
