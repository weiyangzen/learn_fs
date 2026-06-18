# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherService.java

## Purpose
`MountTableRefresherService` refreshes mount table caches after mount table changes. It refreshes the local router directly and remote routers via admin RPC clients, reducing the propagation delay that would otherwise depend on normal state-store cache polling.

## Important APIs, Types, And Functions
- The constructor binds the service to a `Router`.
- `serviceInit` obtains `MountTableStore`, attaches itself as the store refresh service, computes the local admin address, initializes timeouts, and creates a Guava `LoadingCache<String, RouterClient>`.
- `refresh()` reloads router state, scans cached router records, skips routers without admin addresses or not in `RUNNING`, chooses local versus remote refreshers, and invokes them concurrently.
- `invokeRefresh` starts `MountTableRefresherThread` instances, waits on a `CountDownLatch`, and logs success/failure counts.
- `createRouterClient`, `getClientCreator`, and `getClientRemover` manage secure admin RPC client lifecycle.

## Control Flow
Initialization wires the service into `MountTableStore` and starts a daemon scheduler that periodically calls `routerClientsCache.cleanUp()`. On refresh, the service reloads `RouterStore` cache, builds a refresher thread list from `RouterState` records, removes stale clients for non-running routers, uses direct admin server calls for the local router, and reuses cached `RouterClient` proxies for remote routers. Failures to create or use clients cause warnings and cache invalidation.

## State And Persistence
The persistent source of truth is the state store's router records and mount table. This service maintains process-local state: `localAdminAddress`, `cacheUpdateTimeout`, a cached set of admin clients, and a cleaner scheduler. Cache entries expire after `dfs.federation.router.mount-table.cache.update.client.max.time`; removal closes the underlying RPC proxy.

## Dependencies And Integration Points
It depends on `Router`, `MountTableStore`, `RouterStore`, `RouterState`, `RouterClient`, `RouterAdminServer`, `MountTableRefresherThread`, `SecurityUtil`, `UserGroupInformation`, Guava cache, and address helpers in `StateStoreUtils`. `Router` only adds this service when mount-table cache updates are enabled and both state store and admin server dependencies are present.

## Risks And Edge Cases
Local admin address comparison is string-based and must match the address format selected by `DFS_ROUTER_HEARTBEAT_WITH_IP_ENABLE`. Slow or hung refreshes are bounded only by the configured latch timeout; threads may continue after timeout and then update their success flags later. If the cleaner scheduler is null or not started due to failed init, stop paths must avoid leaking clients. Kerberos refresh relies on login-user relogin before creating remote clients.

## Test Signals
`TestRouterMountTableCacheRefresh` and `TestRouterMountTableCacheRefreshSecure` exercise immediate mount-table cache refresh, remote/local refresh paths, client reuse/cleanup behavior, and secure-mode behavior. Router admin and mount table tests provide additional integration signal for refresh side effects after add/update/remove operations.
