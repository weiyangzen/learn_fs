# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterAdminServer.java

## Purpose
`RouterAdminServer` implements the router admin RPC service. It handles mount table CRUD, safemode commands, nameservice disable/enable operations, cache refresh, destination lookup/validation, call queue refresh, superuser-group refresh, and generic refresh handlers.

## Important APIs, Types, And Functions
- The constructor builds a protobuf RPC server for `RouterAdminProtocolPB`, registers generic refresh and call-queue protocols, initializes permission settings, and sets the bound admin address on `Router`.
- Mount table methods delegate to `MountTableStore` after component-length and optional destination-existence validation.
- `updateMountTableEntry` and `removeMountTableEntry` synchronize downstream quotas when router quota is enabled.
- Safemode methods update router state and manual safemode flags, then verify the resulting state.
- Nameservice methods use `DisabledNameserviceStore` with superuser checks.
- `refreshMountTableEntries` refreshes the subcluster resolver cache when it implements `StateStoreCache`; otherwise it delegates to the mount table store.
- `refresh`, `refreshSuperUserGroupsConfiguration`, and `refreshCallQueue` implement generic admin refresh protocols.

## Control Flow
RPC server construction sets the protocol engine and service translators, binds to configured admin host/port, and applies service authorization when enabled. Mount table writes first validate path length and optional downstream file existence, then write state-store records. Updates compare old and new mount records to decide whether namespace and storage-type quotas must be synchronized. Safemode transitions require superuser privilege and are checked against both router state and safemode service state.

## State And Persistence
The server keeps cached handles to `MountTableStore` and `DisabledNameserviceStore`, static permission settings, admin RPC server/address, and config-driven validation flags. Persistent data lives in the state store: mount table records and disabled nameservices. Downstream quota synchronization persists on NameNodes through the router quota module.

## Dependencies And Integration Points
It depends on Hadoop IPC/protobuf RPC, `RouterAdminProtocol`, `RefreshCallQueueProtocol`, `MountTableStore`, `DisabledNameserviceStore`, `MountTableResolver`, `StateStoreCache`, `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `RemoteParam`, `RouterPermissionChecker`, `RefreshRegistry`, and fairness refresh handlers. `RouterClient` exposes remote proxies to this server.

## Risks And Edge Cases
Quota synchronization exceptions are logged and ignored to avoid failing mount table updates, which can leave downstream quota state temporarily inconsistent. Destination validation performs remote `getFileInfo` calls and can be expensive or partially unavailable. Static permission fields are shared across server instances in the same JVM. `iStateStoreCache` is computed at construction and assumes the resolver type will not change. Safemode verification depends on both router state and safemode service state being updated synchronously enough for the check.

## Test Signals
`TestRouterAdmin`, `TestRouterAdminCLI`, `TestDisableNameservices`, `TestRouterRefreshSuperUserGroupsConfiguration`, `TestRouterAdminGenericRefresh`, `TestRouterMountTableCacheRefresh`, and async admin tests cover admin RPC behavior, permissions, mount CRUD, quotas, safemode, and refresh handlers.
