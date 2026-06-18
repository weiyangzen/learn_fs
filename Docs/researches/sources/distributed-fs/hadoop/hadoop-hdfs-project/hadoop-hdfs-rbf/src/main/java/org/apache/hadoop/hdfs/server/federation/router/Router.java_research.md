# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Router.java

## Purpose
`Router` is the top-level composite service for HDFS Router-Based Federation. It creates and owns RPC, admin, HTTP, state-store, resolver, heartbeat, metrics, safemode, quota, and mount-table refresh services, and exposes the router lifecycle state used by health checks and router heartbeats.

## Important APIs, Types, And Functions
- `serviceInit` logs in securely, creates state store, resolvers, RPC/admin/HTTP servers, heartbeat services, metrics, quota services, safemode, and optional mount-table refresh service.
- `serviceStart` moves to `RUNNING` when no safemode service owns the transition and starts JVM pause monitoring.
- `serviceStop` marks state `SHUTDOWN`, stops pause monitoring, and stops child services.
- `createNamenodeHeartbeatServices`, `createLocalNamenodeHeartbeatService`, and overloaded `createNamenodeHeartbeatService` build monitor services from local config and explicit monitor lists.
- `updateRouterState`, `setRouterId`, and getters expose router identity, state, stores, resolvers, metrics, quota, and admin server.
- `verifyToken` delegates delegation-token verification to `RouterSecurityManager`.

## Control Flow
Initialization is feature-flag driven. State store is created first when enabled; resolvers are created next and are required. RPC server creation can set the actual bound RPC address and router ID. Admin and HTTP servers are optional. NameNode heartbeat defaults to router heartbeat enablement. Metrics initialize Hadoop's default metrics system. Quota and safemode services are optional. Mount-table immediate refresh is added only when both state store and admin server are enabled.

## State And Persistence
`Router` stores references to all child services and caches `routerStateManager`. It sets router ID into the state store and NameNode resolver. Durable state is written by child services: router heartbeats, NameNode registrations, mount table records, disabled nameservices, and quotas. The router's own lifecycle state is process-local but heartbeated when the heartbeat service exists.

## Dependencies And Integration Points
It integrates with `CompositeService`, `SecurityUtil`, `StateStoreService`, resolver factories in `FederationUtil`, `RouterRpcServer`, `RouterAdminServer`, `RouterHttpServer`, `RouterMetricsService`, `RouterQuotaManager`, `RouterQuotaUpdateService`, `RouterSafemodeService`, `MountTableRefresherService`, `RouterHeartbeatService`, and `NamenodeHeartbeatService`.

## Risks And Edge Cases
Router ID generation depends on local hostname plus RPC port and can be null early if address resolution fails. If state store is disabled but the default resolver class expects it, resolver construction can fail. `serviceStart` leaves state transition to safemode when safemode service is enabled, so health checks must understand safemode. Mount-table refresh enablement silently degrades with warnings if dependent services are disabled. After initialization, `MountTableStore.setQuotaManager` is called only when state store exists.

## Test Signals
`TestRouter`, `TestRouterSafemode`, `TestRouterNamenodeHeartbeat`, `TestRouterMountTableCacheRefresh`, `TestRouterAdmin`, quota tests, metrics tests, and many `MiniRouterDFSCluster` integration tests exercise router composition and lifecycle.
