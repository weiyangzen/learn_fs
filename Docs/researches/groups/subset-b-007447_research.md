# subset-b-007447 research

Grouped research for the HDFS Router federation RPC and async protocol files in `subset-b-007447`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcMonitor.java

## Purpose
`RouterRpcMonitor` is the pluggable monitoring interface used by `RouterRpcServer` and `RouterRpcClient` call paths to report router RPC activity, Namenode proxy activity, and router-local failures. It decouples the router core from the concrete metrics implementation, with the default implementation selected by `RBFConfigKeys.DFS_ROUTER_METRICS_CLASS`.

## Important APIs and Types
The interface exposes lifecycle methods `init(Configuration, RouterRpcServer, StateStoreService)` and `close()`, metrics access through `getRPCMetrics()`, operation markers `startOp()`, `proxyOp()`, and `proxyOpComplete(...)`, plus failure counters for standby, communication failure, permit rejection, client overload, not implemented calls, retries, missing Namenodes, State Store failure, safe mode, locked path, and read-only path. `proxyOpComplete` carries `nsId` and `FederationNamenodeServiceState` so metrics can distinguish active, standby, observer, or unavailable target states.

## Control Flow
`RouterRpcServer.checkOperation` calls `startOp()` before operation dispatch and uses router failure methods when safe mode or unsupported operations block a request. Lower-level proxy clients call the `proxyOp*` methods around actual Namenode forwarding. Implementations therefore see both the client-facing operation boundary and per-subcluster proxy attempts.

## State and Persistence
This interface owns no state or persistence directly. Implementations may maintain counters, histograms, or JMX state in `FederationRPCMetrics`, and may use the supplied `StateStoreService` for contextual reporting.

## Dependencies and Integration Points
Primary dependencies are Hadoop `Configuration`, `FederationRPCMetrics`, `StateStoreService`, `RouterRpcServer`, and `FederationNamenodeServiceState`. It is instantiated reflectively by `RouterRpcServer` when router metrics are enabled.

## Risks
Metrics correctness depends on every router path consistently calling the monitor. A custom implementation can impact RPC latency if it blocks in hot methods such as `startOp`, `proxyOp`, or `proxyOpComplete`. Null-monitor handling in callers must be retained because metrics can be disabled.

## Test Signals
Look for tests that enable router metrics and assert proxy success/failure counters, safe mode failures, read-only mount failures, and not-implemented calls. Custom monitor tests should verify `init` receives the router server and state store and that `close` is called during service stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcServer.java

## Purpose
`RouterRpcServer` is the Router's client-facing RPC service. It implements `ClientProtocol`, `NamenodeProtocol`, `RefreshUserMappingsProtocol`, and `GetUserMappingsProtocol`, binds Hadoop protobuf RPC services, and forwards client calls to federated Namenodes through routing modules. It is the central policy gate for safe mode, mount-table routing, read-only mounts, quota verification, async mode selection, state-id propagation, and datanode report aggregation.

## Important APIs and Types
The constructor wires protocol translators, service authorization, `RouterSecurityManager`, `RouterStateIdContext`, `RouterRpcClient` or `RouterAsyncRpcClient`, module implementations (`RouterClientProtocol` or `RouterAsyncClientProtocol`, `RouterNamenodeProtocol` or `RouterAsyncNamenodeProtocol`, `RouterUserProtocol` or async variant, `Quota` or `AsyncQuota`), and a Guava `LoadingCache<DatanodeReportType,DatanodeInfo[]>`. Public protocol methods mostly delegate to these modules. Internal APIs include `checkOperation`, `invokeAtAvailableNs`, `invokeAtAvailableNsAsync`, `invokeOnNs`, `getCreateLocation`, `getLocationsForPath`, `getCachedDatanodeReport`, `getDatanodeReport(...timeout...)`, `getDatanodeStorageReportMap`, `merge`, `toArray`, `isPathAll`, `isPathFaultTolerant`, `isInvokeConcurrent`, and `getRemoteUser`.

## Control Flow
Startup builds the RPC server with `ClientNamenodeProtocolPB`, adds Namenode, refresh-user, and get-user mappings protocols, configures terse/suppressed exceptions, and optionally initializes async handler/responder pools. `serviceStart` starts the RPC server; `serviceStop` shuts down RPC, metrics, security, federation rename scheduler, and async executors. Every client operation enters through a `ClientProtocol` override, delegates to the selected module, and normally starts with `checkOperation`. Write operations call `checkSafeMode`; read and unchecked operations are allowed through and may fail later if downstream state is unavailable. Routing resolves mount-table destinations, rejects locked/mount-parent writes when requested, rejects read-only mount writes, checks router quota usage, filters disabled namespaces, and throws `NoLocationException` when no usable destination remains. Async variants use `AsyncUtil` continuations and `asyncReturn` while preserving the same external protocol signature.

## State and Persistence
Persistent remote state remains in Namenodes and State Store records; this class maintains process-local runtime state: RPC address/server, security manager, router state-id context, current operation category thread-local, optional current user thread-local, async executors, datanode report cache, and router federation rename scheduler. Federation rename setup derives a per-router journal URI from HA nameservice/namenode IDs or listener address. The datanode cache refreshes in background and stamps network locations with `/nameservice/...` so WebHDFS can choose a Datanode in the right subcluster.

## Dependencies and Integration Points
This class is integrated with `Router`, `ActiveNamenodeResolver`, `FileSubclusterResolver`, `MountTableResolver`, `RouterRpcClient`, async router classes, `RouterSecurityManager`, `FederationRPCMetrics`, Hadoop IPC `RPC.Server`, protobuf translators, `BalanceProcedureScheduler`, and the HDFS `ClientProtocol`/`NamenodeProtocol` surfaces. It also integrates with observer-read state propagation through `RouterStateIdContext`.

## Risks
This is a high-blast-radius facade. Misclassified `OperationCategory` can bypass safe mode or block valid reads. Mount-table lock/read-only/quota checks are centralized, so regressions affect many file operations. Async mode depends on queue sizes and per-namespace executor configuration; invalid counts throw during construction and overloaded queues can surface as client failures. `getLocationsForPath` reports most `IOException`s as state-store failures before rethrowing, which can overcount metrics. Background scheduled executors are created without retained handles, so lifecycle and leak behavior should be watched. Datanode deduplication uses transfer address and last update; overlapping subclusters or stale reports can bias WebHDFS redirects.

## Test Signals
Useful coverage includes constructor/service lifecycle in sync and async modes, service authorization enabled, safe mode read/write behavior, disabled namespace filtering, read-only mount rejection, quota verification, default namespace fallback, async namespace handler selection, datanode report merge/cache refresh, federation rename journal path construction, WebHDFS create-location namespace selection, and observer-read state-id cleanup for stale namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSafemodeService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSafemodeService.java

## Purpose
`RouterSafemodeService` is a `PeriodicService` that controls whether the Router should reject write operations as if it were a standby Namenode. It protects clients from stale State Store cache data during startup or after State Store cache refreshes stop.

## Important APIs and Types
The key methods are package-visible `isInSafeMode()`, package-visible `setManualSafeMode(boolean)`, private `enter()`, private `leave()`, `serviceInit(Configuration)`, and `periodicInvoke()`. It updates `RouterServiceState.SAFEMODE` and `RouterServiceState.RUNNING` through `router.updateRouterState`.

## Control Flow
On initialization, the service reads the safe mode check period, startup extension, and State Store expiration from `RBFConfigKeys`, records `startupTime`, and immediately enters safe mode. Each periodic tick waits until the startup interval expires, reads `StateStoreService.getCacheUpdateTime()`, considers the cache stale when it has never updated or exceeds the stale interval, enters safe mode if stale, and leaves safe mode only when cache data is fresh and safe mode was not manually set.

## State and Persistence
The service keeps volatile booleans for `safeMode` and `isSafeModeSetManually`, plus timing fields for startup, stale threshold, and safe-mode duration. It persists no data itself, but updates the Router service record/state and reports safe-mode duration into `RouterMetrics`.

## Dependencies and Integration Points
It depends on `Router`, `StateStoreService`, `RouterMetrics`, `PeriodicService`, and router safe-mode configuration keys. `RouterRpcServer.checkSafeMode` uses this service to reject unsafe client operations.

## Risks
Manual safe mode directly sets both flags; leaving manual safe mode requires callers to clear it correctly. If `StateStoreService.getCacheUpdateTime()` is stuck at zero, the Router remains in safe mode after startup. `leave()` logs an error if metrics are disabled but still transitions to running. The stale-cache check is only as accurate as the State Store cache timestamp.

## Test Signals
Tests should cover startup delay, stale cache entry, fresh cache exit, manual safe mode preventing automatic leave, Router state transitions, and metrics safe-mode duration update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSafemodeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterServiceState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterServiceState.java

## Purpose
`RouterServiceState` is the enum used to describe the lifecycle and availability state of a Router instance.

## Important APIs and Types
The enum values are `UNINITIALIZED`, `INITIALIZING`, `SAFEMODE`, `RUNNING`, `STOPPING`, `SHUTDOWN`, and `EXPIRED`. There are no methods beyond the enum constants.

## Control Flow
Other services set or compare these states. `RouterSafemodeService` transitions between `SAFEMODE` and `RUNNING`; `RouterRpcServer.clearStaleNamespacesInRouterStateIdContext` only runs cleanup while the Router reports `RUNNING`.

## State and Persistence
The enum itself has no state. Values are likely stored in Router state records and surfaced through admin/state-store APIs.

## Dependencies and Integration Points
It is referenced by `Router`, safe mode, admin/state-manager interfaces, and state-store records describing router availability.

## Risks
Adding or renaming states impacts serialization, admin output, and state-store compatibility. Logic that treats only `RUNNING` as active must be reviewed if new active states are introduced.

## Test Signals
Tests should assert Router lifecycle transitions and admin/state-store reporting for safe mode, running, shutdown, and expired routers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterServiceState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSnapshot.java

## Purpose
`RouterSnapshot` implements Router-side handling for snapshot-related `ClientProtocol` calls. It resolves federation paths to remote locations and forwards snapshot operations to the appropriate Namenodes while translating returned paths back to the federated namespace when needed.

## Important APIs and Types
The module exposes `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, and `getSnapshotDiffReportListing`. It uses `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `RemoteMethod`, `RemoteParam`, `RemoteResult`, and HDFS snapshot result types.

## Control Flow
Write operations check `OperationCategory.WRITE`, resolve locations with `getLocationsForPath(..., true, false)`, create a `RemoteMethod`, and either invoke all destinations concurrently for multi-destination/mount paths or sequentially otherwise. Reads check `READ`, either fan out to all namespaces for global listings or resolve the snapshot root and query the selected locations. `createSnapshot` and `getSnapshotListing` rewrite returned paths from remote destination prefixes to federated source prefixes.

## State and Persistence
This class owns no durable state. It mutates snapshot state in remote Namenodes through forwarded RPCs and rewrites in-memory response objects before returning them to clients.

## Dependencies and Integration Points
It integrates with `ClientProtocol` through `RouterClientProtocol`/`RouterRpcServer`, mount-table routing through `RouterRpcServer.getLocationsForPath`, namespace discovery through `ActiveNamenodeResolver`, and Hadoop snapshot types such as `SnapshotDiffReport` and `SnapshotStatus`.

## Risks
Concurrent snapshot operations on multi-destination paths can leave partial state if some subclusters succeed and others fail. Several concurrent-read paths return the first result only, which may hide divergent snapshot state. Path rewriting uses `replaceFirst`, so unexpected regex-sensitive characters or mismatched prefixes could produce incorrect client-visible paths.

## Test Signals
Tests should cover snapshot creation path rewriting, multi-destination allow/disallow/delete/rename behavior, snapshottable listing merge, snapshot listing parent path rewrite, diff report fan-out, and partial failure semantics for concurrent mount entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateIdContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateIdContext.java

## Purpose
`RouterStateIdContext` implements Hadoop IPC `AlignmentContext` for HDFS observer-read state propagation across a federated Router. It tracks last-seen state IDs per namespace from Namenode responses and attaches an eligible federated state map to client responses.

## Important APIs and Types
The class builds `coordinatedMethods` by reflecting over `ClientProtocol` methods annotated `@ReadOnly(isCoordinated=true)`. It maintains `ConcurrentHashMap<String, LongAccumulator> namespaceIdMap`, exposes `getNamespaceStateId`, `getNamespaces`, `getNamespaceIdMap`, `removeNamespaceStateId`, static `getRouterFederatedStateMap(ByteString)`, static `getClientStateIdFromCurrentCall`, `updateResponseState`, `receiveRequestState`, `isCoordinatedCall`, and package-visible `isNamespaceObserverReadEligible`.

## Control Flow
During RPC server construction, `RouterRpcServer` installs this alignment context into the IPC server and passes it into router RPC clients. Namenode response handling updates namespace accumulators elsewhere. On client response, `updateResponseState` calls `setResponseHeaderState`, which serializes namespace state IDs into `RouterFederatedStateProto` only for observer-read-eligible namespaces and only when the configured max-size limit is not exceeded. Request-side state from clients is intentionally ignored so clients cannot poison shared router state.

## State and Persistence
State is process-local and concurrent: one `LongAccumulator(Math::max, Long.MIN_VALUE)` per namespace. It is pruned by `RouterRpcServer.clearStaleNamespacesInRouterStateIdContext` when namespaces disappear from the resolver. No state is written to disk; state IDs travel in IPC protobuf headers.

## Dependencies and Integration Points
It depends on `ClientProtocol`, `@ReadOnly`, Hadoop IPC `Server.Call`, `RpcRequestHeaderProto`, `RpcResponseHeaderProto`, HDFS `RouterFederatedStateProto`, and observer-read config keys. It directly affects observer read consistency and `msync` behavior in async client protocol.

## Risks
The propagation size cap silently omits all federated state when the map is too large. Override logic uses XOR-like semantics: a namespace is eligible when the default differs from membership in the override set. Parsing invalid protobuf data throws a runtime exception. Shared accumulators must only be updated from trusted Namenode responses.

## Test Signals
Tests should cover coordinated method discovery, response header serialization under size cap, override/default observer eligibility combinations, stale namespace removal, parsing of federated state maps, and client state lookup from current IPC call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateIdContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateManager.java

## Purpose
`RouterStateManager` defines the admin/state-store contract for changing and querying Router safe mode state.

## Important APIs and Types
It declares `enterSafeMode(EnterSafeModeRequest)`, `leaveSafeMode(LeaveSafeModeRequest)`, and `getSafeMode(GetSafeModeRequest)`, returning the corresponding protocol response types. All methods throw `IOException`.

## Control Flow
Implementations are expected to translate admin/state-store requests into Router safe-mode changes, probably by calling `RouterSafemodeService.setManualSafeMode` and updating `RouterServiceState`.

## State and Persistence
The interface stores nothing. Implementations may update in-memory Router state and state-store records that advertise Router availability.

## Dependencies and Integration Points
It depends on federation store protocol request/response types. It is the abstraction for Router admin RPCs or state-store service code that manages safe mode.

## Risks
Because this is an interface, consistency depends on implementation behavior. Enter/leave operations must coordinate manual safe mode with automatic stale-cache safe mode to avoid accidental exit while State Store data is stale.

## Test Signals
Tests should verify admin enter/leave/get behavior, idempotency, IOException propagation, and Router state transitions through the concrete implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStoragePolicy.java

## Purpose
`RouterStoragePolicy` handles storage policy `ClientProtocol` operations for federated paths. It resolves the path, enforces router operation checks, and forwards the storage policy calls to one or more target Namenodes.

## Important APIs and Types
The module exposes `setStoragePolicy`, `getStoragePolicies`, `unsetStoragePolicy`, `getStoragePolicy`, and `satisfyStoragePolicy`. It uses `RouterRpcServer`, `RouterRpcClient`, `RemoteLocation`, `RemoteMethod`, `RemoteParam`, and `BlockStoragePolicy`.

## Control Flow
Write-like path operations check `WRITE` or supported read categories, resolve remote locations with quota checks disabled where appropriate, and then use `isInvokeConcurrent(path)` to decide between concurrent fan-out for mount/all paths and sequential invocation for normal paths. `getStoragePolicies` is namespace-independent and calls `invokeAtAvailableNs` to query any available namespace.

## State and Persistence
No local state is stored beyond references to the server and client. Mutations are persisted by target Namenodes. The Router only performs routing and result forwarding.

## Dependencies and Integration Points
It integrates with `RouterRpcServer` operation safety, mount-table routing, disabled namespace filtering, and Namenode storage policy RPCs.

## Risks
`satisfyStoragePolicy` is checked as `READ` despite triggering Namenode work; callers rely on the upstream protocol classification. Concurrent fan-out can leave policies inconsistent on multi-destination paths if a subset fails. `getStoragePolicies` returning from the first available namespace assumes policy definitions are compatible across the federation.

## Test Signals
Tests should cover single-destination and multi-destination set/unset/satisfy, unavailable default namespace fallback for `getStoragePolicies`, read-only mount rejection for write operations, and behavior when policies differ across namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterUserProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterUserProtocol.java

## Purpose
`RouterUserProtocol` implements user/group refresh and group lookup protocols for the Router. It either handles the request locally when no namespaces are available or forwards it to all resolved Namenodes.

## Important APIs and Types
It implements `RefreshUserMappingsProtocol` and `GetUserMappingsProtocol` with `refreshUserToGroupsMappings`, `refreshSuperUserGroupsConfiguration`, and `getGroupsForUser`. It uses `Groups`, `ProxyUsers`, `UserGroupInformation`, `ActiveNamenodeResolver`, `FederationNamespaceInfo`, `RemoteMethod`, and `RouterRpcServer.merge`.

## Control Flow
All methods call `rpcServer.checkOperation(OperationCategory.UNCHECKED)`. Refresh calls discover namespaces; if none exist, they refresh local Router caches, otherwise they invoke the corresponding protocol method concurrently across namespaces. `getGroupsForUser` falls back to local UGI group resolution when no namespace exists, otherwise it concurrently queries all namespaces and merges the returned string arrays into a unique array.

## State and Persistence
The module holds only server/client/resolver references. Refresh operations mutate local security caches or remote Namenode caches, not durable application data.

## Dependencies and Integration Points
It is exposed through `RouterRpcServer` protobuf protocol registration and selected as the user protocol module in sync mode. Async mode uses `RouterAsyncUserProtocol`.

## Risks
Concurrent refresh requires all target Namenodes to be reachable unless lower layers relax failures. Merging group arrays loses namespace provenance and ordering may depend on map iteration. Local fallback behavior when namespace discovery is empty must match admin expectations.

## Test Signals
Tests should cover local fallback with no namespaces, concurrent remote refresh, group merging/deduplication, and exception behavior when one namespace fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterUserProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterWebHdfsMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterWebHdfsMethods.java

## Purpose
`RouterWebHdfsMethods` adapts WebHDFS REST requests for the Router. It reuses `NamenodeWebHdfsMethods` for many metadata operations while adding Router-specific Datanode redirects for data-transfer operations such as create, append, open, and checksum.

## Important APIs and Types
The class extends `NamenodeWebHdfsMethods`, is rooted at JAX-RS `@Path("")`, and overrides `init`, `getRpcClientProtocol`, `queueExternalCall`, `put`, `post`, `get`, and `createCredentials`. Router-specific helpers include `redirectURI`, `chooseDatanode`, `getNsFromDataNodeNetworkLocation`, and `getRandomDatanode`.

## Control Flow
The constructor captures HTTP method, query, servlet path, and remote address. `getRpcClientProtocol` returns the Router RPC server or throws `RetriableException` during startup. `put`, `post`, and `get` whitelist supported WebHDFS operations. `CREATE`, `APPEND`, `OPEN`, and `GETFILECHECKSUM` build a redirect URI to a selected Datanode unless `noredirect` requests a JSON location. `chooseDatanode` reads the cached live Datanode report from `RouterRpcServer`, determines the target namespace for create using `getCreateLocation` (sync or async via `syncReturn`), excludes caller-provided Datanodes and non-target namespaces, and for read/append/checksum prefers a Datanode from the file's located blocks. Otherwise it chooses a random non-excluded Datanode.

## State and Persistence
It stores per-request fields for remote address and request metadata. It does not persist state. Token credentials are generated through `RouterSecurityManager.createCredentials`.

## Dependencies and Integration Points
It integrates servlet/JAX-RS request handling, `NamenodeWebHdfsMethods`, `Router`, `RouterRpcServer`, `ClientProtocol`, `RouterSecurityManager`, `JsonUtil`, WebHDFS resource params, cached Datanode reports, and HDFS block location APIs.

## Risks
Datanode namespace filtering relies on `RouterRpcServer.updateDnMap` prefixing network locations as `/ns/rack`; malformed or stale locations make `getNsFromDataNodeNetworkLocation` return empty and can misroute create redirects. `getRandomDatanode` instantiates `Random` in a loop and returns null if all nodes are excluded. `reset()` clears only `remoteAddr`; other captured request fields are unused but stale if instances are reused. Redirect security depends on correct delegation-token handling for secure and insecure clusters.

## Test Signals
Tests should cover supported/unsupported WebHDFS operation whitelists, `noredirect` JSON location responses, secure vs insecure delegation query construction, create redirects constrained to resolved namespace, open offset validation, excludeDatanodes filtering, network-location namespace parsing, and startup-mode `RetriableException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterWebHdfsMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/SubClusterTimeoutException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/SubClusterTimeoutException.java

## Purpose
`SubClusterTimeoutException` is a specific `IOException` type used when a Router operation times out waiting for a subcluster response.

## Important APIs and Types
It extends `IOException`, defines `serialVersionUID = 1L`, and provides a single `SubClusterTimeoutException(String msg)` constructor.

## Control Flow
The class has no internal control flow. Callers can throw it to let upstream code distinguish timeout failures from other IO failures.

## State and Persistence
It carries only the inherited exception message and stack trace. There is no persistence behavior.

## Dependencies and Integration Points
It integrates with router RPC exception handling and any timeout-aware caller logic. It may be used by concurrent invocation paths that apply per-subcluster timeouts.

## Risks
Because it is an `IOException`, generic catch blocks may erase the timeout distinction unless they check the concrete type. The message should include enough namespace/path context at throw sites.

## Test Signals
Tests should assert timeout paths throw this specific type where intended and that client-visible error handling treats it as retriable or partial according to the operation contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/SubClusterTimeoutException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ThreadLocalContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ThreadLocalContext.java

## Purpose
`ThreadLocalContext` captures thread-local RPC and metrics context so asynchronous Router work can restore the original caller context on worker threads.

## Important APIs and Types
The constructor captures `Server.getCurCall().get()`, `CallerContext.getCurrent()`, `FederationRPCPerformanceMonitor.getStartOpTime()`, and `getProxyOpTime()`. `transfer()` installs those values into the current thread. `toString()` reports captured fields.

## Control Flow
Async code creates an instance on the caller thread before scheduling work. Worker code calls `transfer()`, which clears the current `Server.Call` and `CallerContext`, restores captured values when non-null, and restores metrics timestamps when they are not `-1L`.

## State and Persistence
The object is immutable after construction and persists only in memory long enough to cross async execution boundaries. It does not clear metrics values when captured timestamps are `-1L`.

## Dependencies and Integration Points
It depends on Hadoop IPC `Server.Call`, `CallerContext`, and `FederationRPCPerformanceMonitor`. It supports async router RPC implementations and performance metrics attribution.

## Risks
Restoring stale context on reused worker threads can corrupt attribution if `transfer()` is called at the wrong time or without later cleanup. The method clears call/context before restoration but only conditionally sets metric timestamps, so existing worker-thread metric values can remain when captured values are absent.

## Test Signals
Tests should cover transfer of non-null and null call/context, metric timestamp propagation, worker-thread reuse, and async RPC metrics attribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ThreadLocalContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncErasureCoding.java

## Purpose
`AsyncErasureCoding` is the async-mode implementation of erasure coding Router operations. It extends the synchronous `ErasureCoding` module and rewrites selected calls with `AsyncUtil` continuation style.

## Important APIs and Types
Overrides include `getErasureCodingPolicies`, `getErasureCodingCodecs`, `addErasureCodingPolicies`, `getErasureCodingPolicy`, `getECTopologyResultForPolicies`, and `getECBlockGroupStats`. It uses `RouterRpcServer`, `RouterRpcClient`, `ActiveNamenodeResolver`, `RemoteMethod`, `RemoteParam`, `asyncApply`, `asyncReturn`, and merge helpers.

## Control Flow
Global read/write operations fan out to all namespaces with `rpcClient.invokeConcurrent` and then merge results. `getErasureCodingPolicy(src)` resolves the path and invokes target locations sequentially. `getECTopologyResultForPolicies` fans out, returns the first unsupported result when present, otherwise returns the first namespace result. Stats are merged through `ECBlockGroupStats.merge`.

## State and Persistence
No local persistent state is kept. Policy mutations and lookups affect or read Namenode state. Async results live in the per-call async context.

## Dependencies and Integration Points
It is selected by `RouterRpcServer` indirectly through async client protocol paths and depends on normal Router location resolution and namespace discovery.

## Risks
Cluster-wide EC policy definitions are assumed compatible enough to merge. `getECTopologyResultForPolicies` throws a misspelled "No namespace availaible." error when the namespace set is empty and otherwise uses iteration order for the positive result. Async casts to raw `Map`/array classes require translator expectations to remain aligned.

## Test Signals
Tests should cover merge of EC policies/codecs/stats across namespaces, unsupported topology precedence, empty namespace failure, path-specific policy lookup, and async exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncErasureCoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncQuota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncQuota.java

## Purpose
`AsyncQuota` is the async-mode quota module. It queries quota usage from all valid remote locations concurrently and aggregates the results into a federated `QuotaUsage`.

## Important APIs and Types
It extends `Quota` and overrides `getQuotaUsage(String)` and protected `getEachQuotaUsage(String)`. It uses `Router`, `RouterRpcServer`, `RouterRpcClient`, `RemoteLocation`, `RemoteMethod`, `RemoteParam`, `QuotaUsage`, and `AsyncUtil`.

## Control Flow
`getQuotaUsage` calls `getEachQuotaUsage`, then applies `aggregateQuota(path, results)` in an async continuation. `getEachQuotaUsage` checks `READ`, verifies router quota is enabled, computes valid quota locations from the superclass, and invokes `getQuotaUsage` concurrently on those locations with required responses.

## State and Persistence
No local state is persisted. It reads remote Namenode quota usage and router quota configuration/state through the `Router` reference.

## Dependencies and Integration Points
It integrates with router quota manager behavior in the superclass, `RouterRpcServer.getLocationsForPath` quota verification, and async RPC result handling.

## Risks
Aggregation exceptions are wrapped in `CompletionException`, so caller-side unwrapping must preserve `IOException` semantics. Required concurrent responses mean one slow or failed subcluster can fail the aggregate. The module assumes `getValidQuotaLocations` has filtered destinations correctly.

## Test Signals
Tests should cover quota-disabled failure, multi-location aggregation, missing/failed subcluster behavior, storage-type quota aggregation, and wrapped async exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/AsyncQuota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncCacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncCacheAdmin.java

## Purpose
`RouterAsyncCacheAdmin` is the async-mode cache administration module. It extends `RouterCacheAdmin` and converts the superclass invocation helpers into async-returning methods.

## Important APIs and Types
Overrides include `addCacheDirective`, `listCacheDirectives`, and `listCachePools`. It uses cache types `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CachePoolEntry`, `CacheFlag`, `BatchedEntries`, and async helpers.

## Control Flow
Each method calls the corresponding superclass helper (`invokeAddCacheDirective`, `invokeListCacheDirectives`, or `invokeListCachePools`), then `asyncApply` extracts the first value from the returned map and `asyncReturn`s the expected type.

## State and Persistence
The class has no own fields and persists no local state. Cache directive/pool changes are persisted by Namenodes.

## Dependencies and Integration Points
It relies on `RouterCacheAdmin` for operation checks, path resolution, and remote invocation details. It is used by async client protocol composition.

## Risks
Returning the first map value assumes all namespaces return equivalent cache admin results or that only one result matters. Empty maps would throw through iterator access. Generic casts suppress type safety around `BatchedEntries`.

## Test Signals
Tests should cover add/list behavior in multi-namespace routing, empty-result handling, failed subcluster behavior, and parity with synchronous `RouterCacheAdmin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncCacheAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncClientProtocol.java

## Purpose
`RouterAsyncClientProtocol` is the async-mode implementation of core HDFS `ClientProtocol` operations behind `RouterRpcServer`. It extends `RouterClientProtocol` and rewrites high-traffic file, namespace, listing, datanode, admin, token, and consistency calls using async continuations.

## Important APIs and Types
Important overrides include `getServerDefaults`, `create`, `append`, `rename`, `rename2`, `concat`, `mkdirs`, `getListing`, `getListingInt`, `getFileInfo`, `getFileRemoteLocation`, `getMountPointStatus`, `getFileInfoAll`, `recoverLease`, `getStats`, `getReplicatedBlockStats`, `listOpenFiles`, datanode report methods, `setSafeMode`, `saveNamespace`, `rollEdits`, `restoreFailedStorage`, `rollingUpgrade`, `getContentSummary`, `getCurrentEditLogTxid`, `msync`, `setReplication`, `isMultiDestDirectory`, `getEnclosingRoot`, delegation token methods, and `getHAServiceState`.

## Control Flow
The constructor captures router/client/resolver references and configuration-derived behavior such as partial-list allowance, mount-status timeout, default nameservice, and superuser/group. File creation optionally creates parents on `isPathAll`, resolves create location, invokes a single Namenode, stamps the namespace into returned status, and retries on fault-tolerant mount failures. Rename resolves source and destination without quota verification, trims destinations through inherited rename logic, falls back to router federation rename when no direct same-namespace destination remains, and uses concurrent invocation for multi-destination directories. Listing concurrently queries remote directories, merges sorted entries with a comparator, handles partial failures according to `allowPartialList`, adds mount-table children with synthetic statuses, and computes remaining entries. File info checks remote status first, then synthesizes mount-point status when no backing path exists. Cluster-wide calls fan out and merge sums, booleans, maximum txids, first rolling-upgrade info, or merged stats as appropriate.

## State and Persistence
Local mutable state is limited to cached `FsServerDefaults` and copied configuration fields. Persistent mutations happen in Namenodes or through federation rename scheduling. Async state is managed by `AsyncUtil` per call.

## Dependencies and Integration Points
It is selected by `RouterRpcServer` when async RPC is enabled. It integrates with `RouterRpcClient`, `RouterFederationRename`, `MountTableResolver`, `ActiveNamenodeResolver`, `RouterSecurityManager`, observer-read eligibility through `msync`, inherited `RouterClientProtocol` helpers, and many HDFS protocol result types.

## Risks
This class has high async-control-flow risk: missed `asyncComplete`, wrong continuation type, or exception swallowed in `asyncCatch` can hang or corrupt responses. Listing merge and remaining-count logic is subtle and must preserve HDFS pagination ordering across subclusters and mount points. `concat` uses an array index mutated inside async loop. `getMountPointStatus` falls back to default metadata on failures, which can mask real permissions. `msync` intentionally no-ops when no namespace is observer-read eligible. Federation rename and multi-destination rename can create partial updates if failures occur after some namespaces succeed.

## Test Signals
Tests should cover async create with fault-tolerant retry, parent creation for all-destination mounts, rename/rename2 federation fallback, concat same-namespace validation, listing pagination with mount points and partial failures, synthetic mount-point file info, datanode and storage report merge, safe mode aggregation, txid max selection, content summary aggregation, observer-read `msync`, token operations, and parity with sync `RouterClientProtocol`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncNamenodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncNamenodeProtocol.java

## Purpose
`RouterAsyncNamenodeProtocol` is the async-mode implementation of the Router's `NamenodeProtocol` module. It supports Namenode-to-Namenode style administrative/block APIs through the Router.

## Important APIs and Types
It extends `RouterNamenodeProtocol` and overrides `getBlocks`, `getBlockKeys`, `getTransactionID`, `getMostRecentCheckpointTxId`, `getMostRecentNameNodeFileTxId`, and `versionRequest`. It uses `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `NamenodeProtocol`, `DatanodeStorageReport`, `BlocksWithLocations`, `ExportedBlockKeys`, `NamespaceInfo`, and async helpers.

## Control Flow
`getBlocks` checks `READ`, requests all datanode storage reports asynchronously, scans reports for the requested datanode UUID to find its namespace, and invokes `NamenodeProtocol.getBlocks` on that namespace. If the datanode is not found, it completes with null. Other methods check `READ`, build protocol-scoped `RemoteMethod`s, and call `rpcServer.invokeAtAvailableNsAsync` to use the default namespace or fallback namespaces.

## State and Persistence
The class stores only server/client references. It reads block and metadata state from Namenodes and writes no local durable state.

## Dependencies and Integration Points
It is composed by `RouterRpcServer` in async mode and backs `RouterRpcServer`'s `NamenodeProtocol` overrides. It depends on datanode-report aggregation from the RPC server and namespace fallback routing.

## Risks
`getBlocks` can return null when reports are stale or a datanode UUID cannot be found, which may differ from expected NamenodeProtocol errors. Scanning all storage reports can be expensive in large federations. Fallback methods assume any available namespace is a valid source for block keys, txids, checkpoint IDs, or version info.

## Test Signals
Tests should cover datanode UUID namespace resolution, stale/missing datanode behavior, fallback when default namespace is unavailable, and async return type correctness for primitive long methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncNamenodeProtocol.java -->
