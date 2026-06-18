# Research Report: subset-b-007445

This grouped report covers the requested Hadoop HDFS Router-Based Federation router source files. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationUtil.java

## Purpose
`FederationUtil` is a static utility holder for Router-Based Federation support code. It centralizes JMX retrieval from NameNode web endpoints, build/version reporting, reflective construction of configurable federation components, mount-point `HdfsFileStatus` rewriting, fairness-controller construction, and parsing configured nameservices from `dfs.federation.router.monitor.namenode`.

## Important APIs, Types, And Functions
- `getJmx(String, String, URLConnectionFactory, String)` builds `/jmx?qry=...` URLs, opens secure-aware HTTP(S) connections, reads JSON, and returns the `beans` array.
- `newFileSubclusterResolver`, `newActiveNamenodeResolver`, `newSecretManager`, and `newFairnessPolicyController` load configured classes from `RBFConfigKeys` and instantiate them reflectively.
- Private `newInstance` supports no-arg, `Configuration`, and `(Configuration, context)` constructors.
- `updateMountPointStatus` rebuilds an `HdfsFileStatus` while replacing the child count.
- `getAllConfiguredNS` extracts nameservice IDs from `ns` or `ns.nn` monitor entries and rejects malformed dotted names.

## Control Flow
JMX calls parse host and optional port, create a `URL`, open a connection using security mode, enforce 5 second connect/read timeouts, buffer all response text, and parse it through Jettison JSON. Reflective factory methods read class keys, call `newInstance`, and return null on reflective failure after logging. `getAllConfiguredNS` iterates configured monitor entries and normalizes each entry to a nameservice identifier.

## State And Persistence
The class owns no durable state. All returned objects are newly constructed or derived from inputs. JMX data is transient. Errors are logged and usually converted to `null`, so callers must handle absent utility results.

## Dependencies And Integration Points
It integrates with `Router`, `StateStoreService`, `FileSubclusterResolver`, `ActiveNamenodeResolver`, delegation token secret managers, `RouterRpcFairnessPolicyController`, `HdfsFileStatus`, and `RBFConfigKeys`. `NamenodeHeartbeatService` uses `getJmx` for NameNode metrics, while `Router` uses the resolver factories during initialization.

## Risks And Edge Cases
`getJmx` has broad exception handling and returns null on network, parsing, or unexpected errors, so downstream metric population must tolerate stale or absent arrays. `webAddress.split(":")` assumes simple host:port input and is not IPv6-safe. Reflective construction hides type-constructor mismatches as null, which can delay failure until router initialization checks. `getAllConfiguredNS` throws on names with more than one dot, which is correct for the configured `ns.nn` syntax but strict for accidental FQDN-like values.

## Test Signals
Fairness controller factory behavior is exercised by fairness tests such as `TestRouterRpcFairnessPolicyController`, `TestProportionRouterRpcFairnessPolicyController`, and async fairness tests. `getAllConfiguredNS` behavior is indirectly covered by router heartbeat/monitoring tests that configure `DFS_ROUTER_MONITOR_NAMENODE`. JMX behavior is indirectly covered through `TestRouterNamenodeHeartbeat` and web-scheme tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/IsRouterActiveServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/IsRouterActiveServlet.java

## Purpose
`IsRouterActiveServlet` exposes the router readiness decision through Hadoop's generic `IsActiveServlet`. It answers whether the Router HTTP service should report itself active and ready to serve requests.

## Important APIs, Types, And Functions
- `isActive()` obtains the `ServletContext`, retrieves the `Router` via `RouterHttpServer.getRouterFromContext`, reads `Router.getRouterState()`, and returns true only for `RouterServiceState.RUNNING`.

## Control Flow
The servlet delegates all context lookup and state ownership to `RouterHttpServer` and `Router`. There is no request-specific branching beyond comparing the current state to `RUNNING`.

## State And Persistence
The servlet stores no state. It reflects the in-memory router state at the instant the servlet method executes.

## Dependencies And Integration Points
It depends on Hadoop HTTP's `IsActiveServlet`, the router object stored in servlet context by `RouterHttpServer`, and the `RouterServiceState` lifecycle enum. Load balancers and health check clients can use this endpoint to avoid routing to routers in initializing, safemode, shutdown, or unavailable states.

## Risks And Edge Cases
If the servlet context does not contain a router, or the router is not fully initialized, this method can fail rather than returning false. The active decision is intentionally strict: safemode is not active even though the HTTP server may be alive. Tests should verify this against router lifecycle transitions instead of only HTTP process liveness.

## Test Signals
Router lifecycle and HTTP tests, including `TestRouter`, `TestRouterSafemode`, and router HTTP server tests, provide indirect coverage. Health-check behavior should be validated by driving router state transitions and confirming only `RUNNING` produces an active response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/IsRouterActiveServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherService.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherThread.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherThread.java

## Purpose
`MountTableRefresherThread` is the per-router worker used by `MountTableRefresherService` to invoke `refreshMountTableEntries` against either the local admin server or a remote router admin proxy.

## Important APIs, Types, And Functions
- The constructor accepts a `MountTableManager` and admin address, sets a descriptive daemon thread name, and stores the manager.
- `work()` runs under login-user credentials, refreshes Kerberos TGTs when security is enabled, calls `manager.refreshMountTableEntries`, records the response result, and always counts down the latch.
- `isSuccess()`, `setCountDownLatch`, `getAdminAddress`, and `toString()` expose worker state to the service.

## Control Flow
The inherited `SubjectInheritingThread` invokes `work`. The worker wraps the admin call in `SecurityUtil.doAsLoginUser`; successful responses drive the `success` flag, `IOException` is logged, and `finally` releases the parent latch. The service later reads `isSuccess` to log aggregate results and evict failed clients.

## State And Persistence
The thread stores only process-local execution state: target admin address, manager proxy, latch, and a boolean success flag. It does not persist anything itself; persistence happens through the target router's cache reload and state-store-backed mount table.

## Dependencies And Integration Points
It depends on `MountTableManager`, `RefreshMountTableEntriesRequest/Response`, Hadoop security utilities, and `SubjectInheritingThread`. It is instantiated by `MountTableRefresherService` for local and remote targets.

## Risks And Edge Cases
`countDownLatch` must be set before `start`; otherwise `finally` can throw `NullPointerException` after an admin failure. There is no explicit timeout inside the worker; the parent service controls waiting but not thread cancellation. A false response and an exception both appear as unsuccessful, so diagnostics rely on logs.

## Test Signals
Coverage is mainly through `TestRouterMountTableCacheRefresh` and secure refresh tests, which validate the service-level behavior that creates and observes these threads. Unit tests can use a fake `MountTableManager` to assert latch countdown and success flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NamenodeHeartbeatService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NamenodeHeartbeatService.java

## Purpose
`NamenodeHeartbeatService` periodically probes one NameNode and registers its namespace, address, HA state, safemode state, storage, datanode, and corruption metrics with the active NameNode resolver/state store. Routers use these records to choose active NameNodes and expose federation health.

## Important APIs, Types, And Functions
- Constructors identify a nameservice and optional NameNode ID; the resolved-host constructor creates a synthetic NameNode ID for DNS-expanded monitor targets.
- `serviceInit` resolves RPC, service RPC, lifeline, and web addresses, creates an `NNHAServiceTarget` for HA NameNodes, sets heartbeat and JMX intervals, and initializes URL connection factory/scheme.
- `periodicInvoke` runs `updateState` as the login user.
- `getNamenodeStatusReport` builds a `NamenodeStatusReport` and populates namespace info, safemode, JMX metrics, and HA status.
- `updateNameSpaceInfoParameters`, `updateSafeModeParameters`, `updateJMXParameters`, and `updateHAStatusParameters` isolate the individual probes.

## Control Flow
Each tick creates a report, calls the NameNode protocol `versionRequest` first, and stops early if namespace registration is invalid. Safemode is fetched through `ClientProtocol`, JMX is refreshed only when enabled and the configured interval has elapsed, and HA state is fetched through a cached health monitor proxy. If a HA-enabled target cannot report HA state, the service leaves the current resolver state unchanged; otherwise it registers the report through `ActiveNamenodeResolver.registerNamenode`.

## State And Persistence
The service caches RPC protocol proxies, JMX arrays, last JMX update attempt time, address strings, and health-monitor timeout. Proxies are reset to null on their respective failures so future ticks recreate them. Durable federation state is written indirectly through the resolver/state store registration path.

## Dependencies And Integration Points
It integrates with `PeriodicService`, `ActiveNamenodeResolver`, `NamenodeStatusReport`, `NameNodeProxies`, `NamenodeProtocol`, `ClientProtocol`, `NNHAServiceTarget`, `HAServiceProtocol`, `FederationUtil.getJmx`, `DFSUtil`, `DFSHAAdmin`, `URLConnectionFactory`, and router monitor configuration keys. `Router.createNamenodeHeartbeatServices` owns service creation.

## Risks And Edge Cases
Address fallback is important: absent service RPC falls back to client RPC, absent lifeline falls back to service RPC. DNS resolution mode clones a configured NameNode across resolved hosts and rewrites ports from configured addresses. JMX failures are logged but stale cached metrics may continue to populate reports. `updateHAStatusParameters` calls `e.getMessage().startsWith(...)`; a throwable with null message could fail this branch. Health-monitor timeout is coerced to zero for negative config values.

## Test Signals
`TestRouterNamenodeHeartbeat` covers lifecycle, local NameNode discovery, HA failover reporting, HA service/lifeline address selection, DNS resolution, and security-enabled heartbeat registration. `TestRouterNamenodeMonitoring` and `TestRouterNamenodeWebScheme` provide additional monitor and HTTP/HTTPS scheme coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NamenodeHeartbeatService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NameserviceManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NameserviceManager.java

## Purpose
`NameserviceManager` defines the admin contract for disabling, enabling, and listing disabled nameservices in Router-Based Federation.

## Important APIs, Types, And Functions
- `disableNameservice(DisableNameserviceRequest)` returns a `DisableNameserviceResponse`.
- `enableNameservice(EnableNameserviceRequest)` returns an `EnableNameserviceResponse`.
- `getDisabledNameservices(GetDisabledNameservicesRequest)` returns a `GetDisabledNameservicesResponse`.

## Control Flow
The interface has no implementation. `RouterAdminServer` implements this contract through the protobuf admin translator. Its implementation verifies superuser privilege, validates namespace existence or disabled-state membership, and delegates to `DisabledNameserviceStore`.

## State And Persistence
The interface owns no state. Implementations persist disabled nameservice state through the federation state store's `DisabledNameserviceStore`, allowing routers to avoid routing to administratively disabled namespaces.

## Dependencies And Integration Points
It depends on state-store protocol request/response types. `RouterClient.getNameserviceManager` exposes a remote proxy for callers such as admin CLI tooling and tests.

## Risks And Edge Cases
Because this is an interface, compatibility depends on protobuf translators and implementers preserving request/response semantics. Disabling a nonexistent namespace should fail cleanly; enabling a namespace not currently disabled should also report failure. Authorization is implementation-specific and must not be bypassed by alternate implementations.

## Test Signals
`TestDisableNameservices`, `TestRouterAdmin`, and admin CLI tests exercise the implementation path through `RouterAdminServer` and `RouterClient`/translator proxies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NameserviceManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoLocationException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoLocationException.java

## Purpose
`NoLocationException` is a typed `IOException` thrown when the Router cannot map a federation path to any remote location, so it cannot forward the request to a subcluster.

## Important APIs, Types, And Functions
- Constructor `NoLocationException(String path, Class<?> t)` formats the path and calling class simple name into a diagnostic message.

## Control Flow
There is no internal branching. Callers create the exception at location-resolution failure points and propagate it through normal HDFS client RPC error handling.

## State And Persistence
The exception carries only the inherited message and serial version UID. It has no persistence behavior.

## Dependencies And Integration Points
It depends only on `IOException`. Router RPC modules and resolvers use it to distinguish "no mount/location" failures from downstream NameNode failures.

## Risks And Edge Cases
The message includes the class simple name but not resolver state or candidate mount table entries, so debugging may require surrounding logs. It does not store path/type as structured fields. Callers must avoid using it when locations exist but all NameNodes are unavailable; that condition has a separate exception type.

## Test Signals
Missing mount and path resolution behavior is exercised indirectly by router mount table, missing-folder, and RPC tests such as `TestRouterMissingFolderMulti`, `TestRouterMountTable`, and multi-destination router RPC tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoLocationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoNamenodesAvailableException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoNamenodesAvailableException.java

## Purpose
`NoNamenodesAvailableException` is a typed `IOException` for the case where a nameservice is known, but no usable NameNode is available for routing.

## Important APIs, Types, And Functions
- Constructor `NoNamenodesAvailableException(String nsId, IOException ioe)` wraps the underlying IO failure with a nameservice-specific message.

## Control Flow
The class has no internal control flow. Router client code throws it after resolver or connection attempts fail for a nameservice.

## State And Persistence
The exception stores the formatted message and cause via `IOException`. It carries no extra fields.

## Dependencies And Integration Points
It depends only on `IOException` and is consumed by router RPC error handling, fault-tolerant routing, and client-facing diagnostics.

## Risks And Edge Cases
Callers should preserve the underlying cause to avoid hiding whether the failure was resolver staleness, all NameNodes down, connection timeout, or access failure. Long-lived unavailable states need tests that verify retry/failover behavior rather than merely message formatting.

## Test Signals
`TestNoNamenodesAvailableLongTime`, `TestRouterFaultTolerant`, and failover/router RPC tests provide direct and indirect coverage of prolonged NameNode unavailability and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoNamenodesAvailableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PeriodicService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PeriodicService.java

## Purpose
`PeriodicService` is a reusable `AbstractService` base class for router subsystems that execute a task repeatedly with fixed delay, such as NameNode heartbeat, router heartbeat, safemode checks, and quota updates.

## Important APIs, Types, And Functions
- Constructors set a service name and interval, defaulting to one minute.
- `setIntervalMs` changes the interval before the service starts and throws `ServiceStateException` if called after start.
- `serviceStart` and `serviceStop` start and stop periodic execution.
- `startPeriodic` creates the runnable wrapper, sets `isRunning`, and schedules it with fixed delay.
- `stopPeriodic` clears `isRunning` and shuts down the scheduler.
- `periodicInvoke()` is the abstract hook implemented by subclasses.
- Protected counters expose run count, error count, and last successful update time.

## Control Flow
`serviceStart` delegates to `startPeriodic`, which first calls `stopPeriodic`, then schedules a runnable with initial delay zero. The runnable checks `isRunning`, calls `periodicInvoke`, increments `runCount`, and records `lastRun`; any exception increments `errorCount` and is logged without stopping future executions.

## State And Persistence
State is in-memory only: interval, scheduler, running flag, run/error counters, and last-run timestamp. It has no external persistence. The scheduler is constructed once in the constructor and shut down on stop.

## Dependencies And Integration Points
It depends on Hadoop service lifecycle APIs, Java scheduled executors, Guava `ThreadFactoryBuilder`, and Hadoop `Time`. Router periodic services subclass it to inherit consistent lifecycle and metric-like counters.

## Risks And Edge Cases
Because the scheduler is shut down in `stopPeriodic`, calling `startPeriodic` after a full stop on the same instance may fail because the executor cannot accept new tasks. Counters are not atomic; they are adequate for approximate service inspection but not strict concurrent accounting. Long-running `periodicInvoke` calls delay the next tick because scheduling is fixed-delay.

## Test Signals
Coverage is indirect through lifecycle tests for subclasses, especially `TestRouterNamenodeHeartbeat`, `TestRouterSafemode`, router heartbeat tests, and quota update tests. Unit tests should assert exception isolation and interval immutability after start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PeriodicService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PoolAlignmentContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PoolAlignmentContext.java

## Purpose
`PoolAlignmentContext` implements client-side RPC state-id alignment for a single router connection pool associated with a namespace and user. It propagates client-observed state IDs to NameNode requests while sharing NameNode-observed state globally through `RouterStateIdContext`.

## Important APIs, Types, And Functions
- Constructor receives a `RouterStateIdContext` and namespace ID, obtains the shared namespace `LongAccumulator`, and creates a pool-local accumulator.
- `receiveResponseState` updates the shared global state from NameNode responses and resets both accumulators when a zero state ID indicates state context is disabled.
- `updateRequestState` writes the pool-local state ID into outgoing RPC request headers.
- `advanceClientStateId` advances the pool-local value with a client-observed state ID.
- `getLastSeenStateId` exposes the shared namespace state.

## Control Flow
Responses from NameNodes are trusted for the shared global maximum. Client-originated state is isolated to the connection pool local accumulator, so a client can only affect later requests sharing the same namespace/UGI pool. Server-side alignment hooks that do not apply to this client-side context are no-ops or unsupported.

## State And Persistence
State is in memory inside two `LongAccumulator` objects. The shared accumulator is held by `RouterStateIdContext`; the pool-local accumulator is scoped to this connection pool. No durable state is written.

## Dependencies And Integration Points
It depends on Hadoop IPC `AlignmentContext` and protobuf RPC headers. `ConnectionPool` uses it for observer-read state propagation; `RouterStateIdContext` supplies namespace-level shared state.

## Risks And Edge Cases
The initial value is `Long.MIN_VALUE`, which is intentionally propagated until a client state is advanced; callers must treat that as "no state" according to the wider alignment protocol. A NameNode response state ID of zero resets accumulated state when global state was positive, preventing stale observer state after alignment is disabled. `isCoordinatedCall` throws because this context should not be used for server-side coordination decisions.

## Test Signals
`TestPoolAlignmentContext` directly verifies pool-local versus shared state separation and reset behavior when NameNodes stop sending state IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/PoolAlignmentContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Quota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Quota.java

## Purpose
`Quota` implements router-side handling for `ClientProtocol#setQuota` and `getQuotaUsage` across federated mount points. It fans quota mutations out to relevant remote locations and aggregates remote quota usage into a federation-level result.

## Important APIs, Types, And Functions
- `setQuota` checks quota enablement, optionally blocks direct mount-entry quota changes, and delegates to `setQuotaInternal`.
- `setQuotaInternal` resolves quota remote locations and invokes `setQuota` concurrently on NameNodes using `RemoteMethod` and `RemoteParam`.
- `getEachQuotaUsage` resolves valid quota locations and invokes `getQuotaUsage` concurrently.
- `aggregateQuota` sums counts and storage consumption, chooses quota limits, handles unset quotas, and uses global mount-table quota for mount entries.
- `getGlobalQuota` walks parent quota records from `RouterQuotaManager` to resolve inherited quota values.
- `getValidQuotaLocations` filters duplicate parent-child destinations within the same nameservice to avoid double-counting.

## Control Flow
Writes require `OperationCategory.WRITE`, reads require `READ`, and both fail when router quota is disabled. If the quota manager has child paths under the requested path, those child mount locations are used; otherwise the direct path locations are used. Aggregation treats mount entries differently from non-mount paths: mount entries sum usage across children and take quota limits from global mount-table metadata, while non-mount paths take returned NameNode quota values unless any returned usage reports quota unset.

## State And Persistence
The class itself holds references to `Router`, `RouterRpcServer`, and `RouterRpcClient`. Persistent quota intent lives in mount-table `RouterQuotaUsage` records managed by `RouterQuotaManager` and state store; actual quota application is persisted on downstream NameNodes by remote `setQuota` calls.

## Dependencies And Integration Points
It integrates with `RouterRpcServer`, `RouterRpcClient`, `RouterQuotaManager`, `RouterQuotaUsage`, `RemoteLocation`, `RemoteMethod`, `RemoteParam`, HDFS quota constants, `StorageType`, and NameNode operation categories. `RouterAdminServer` calls it to synchronize quotas after mount table updates and removals.

## Risks And Edge Cases
Quota aggregation can be wrong if parent-child destination filtering misses a topology case or if remote locations change while quota synchronization is running. `setQuota` intentionally rejects direct quota changes on mount entries when `checkMountEntry` is true, but admin synchronization bypasses this check. If any non-mount remote usage reports quota unset, the aggregate quota limits are reset even when other locations have quotas. Storage-type quota handling must keep arrays aligned with `StorageType.values()`.

## Test Signals
`TestRouterQuota`, `TestDisableRouterQuota`, and quota sections of `TestRouterAdminCLI` cover enablement, set/clear quota, storage-type quotas, aggregation, and admin synchronization. Multi-destination router RPC tests add signal for remote fan-out and aggregation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Quota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RBFConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RBFConfigKeys.java

## Purpose
`RBFConfigKeys` defines the Router-Based Federation configuration namespace, all router-specific keys, and default values used by router services, state store, RPC clients, HTTP/admin servers, quota, safemode, security, fairness, observer reads, async RPC, and federation rename.

## Important APIs, Types, And Functions
- `FEDERATION_ROUTER_PREFIX` is the root `dfs.federation.router.` prefix.
- RPC/admin/http defaults define bind keys, addresses, ports, handler counts, and enable flags.
- Heartbeat and monitor keys define router and NameNode heartbeat intervals, monitor lists, DNS resolution options, and health timeouts.
- State-store keys define enablement, serializer, driver class, ZooKeeper defaults, cache TTLs, and membership/router expiration.
- Quota, safemode, mount-table cache, security, delegation token, fairness, observer, async RPC, and federation rename keys supply feature flags and defaults.

## Control Flow
There is no executable control flow beyond class initialization of constants. Runtime services read these keys from `Configuration` during their own initialization.

## State And Persistence
The class stores only immutable public constants. It indirectly controls persisted behavior by selecting state-store drivers, paths, cache TTLs, and feature enablement defaults.

## Dependencies And Integration Points
Defaults reference implementation classes such as `MountTableResolver`, `MembershipNamenodeResolver`, `StateStoreZooKeeperImpl`, `StateStoreSerializerPBImpl`, `ZKDelegationTokenSecretManagerImpl`, `FederationRPCPerformanceMonitor`, and `NoRouterRpcFairnessPolicyController`. Nearly every router class in this subset imports some keys.

## Risks And Edge Cases
Default choices are operationally significant: RPC, admin, HTTP, state store, router heartbeat, metrics, and safemode are enabled by default, while quota and async RPC are disabled by default. Misconfigured timeouts or handler counts can cause broad router behavior changes. Because keys are public constants, renames are compatibility-sensitive and must preserve deprecated behavior or migration paths.

## Test Signals
Configuration defaults are exercised broadly through `MiniRouterDFSCluster`-based tests, `TestRouter`, heartbeat tests, admin tests, quota tests, fairness tests, observer-read tests, and async RPC tests. Tests that instantiate routers with minimal configs are especially useful for detecting accidental default changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RBFConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteLocationContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteLocationContext.java

## Purpose
`RemoteLocationContext` is an abstract base for location objects that identify a destination in one nameservice. It supplies comparison, equality, and hashing semantics used by router RPC fan-out maps.

## Important APIs, Types, And Functions
- Abstract `getNameserviceId`, `getDest`, and `getSrc` define the required location fields.
- `hashCode` combines nameservice ID and destination.
- `equals` compares nameservice ID and destination for any `RemoteLocationContext`.
- `compareTo` orders by nameservice ID and then destination.

## Control Flow
The class delegates field access to subclasses and performs deterministic equality/order comparisons. Source path is intentionally not included in equality or ordering.

## State And Persistence
The class stores no fields itself. Subclasses such as `RemoteLocation` provide actual state. It has no persistence behavior.

## Dependencies And Integration Points
It depends on Apache Commons `HashCodeBuilder`. It is used by `RemoteParam`, `RemoteResult`, `RemoteMethod`, `RouterRpcClient`, quota code, cache admin code, and other fan-out modules as the common key type for per-location results.

## Risks And Edge Cases
Ignoring `getSrc` in equality means two contexts with the same nameservice and destination but different source path compare equal. That is usually desired for remote-operation fan-out but can collapse map entries if callers expect source-sensitive identity. Subclasses must return non-null nameservice and destination strings or equality/comparison can throw.

## Test Signals
Coverage is indirect through remote parameter/result maps in router RPC, quota, cache admin, and multi-destination tests. Map-key behavior should be considered when adding new `RemoteLocationContext` subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteLocationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteMethod.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteMethod.java

## Purpose
`RemoteMethod` describes a protocol method and parameter template for router fan-out calls to remote NameNodes. It lets callers combine static parameters with per-location dynamic parameters resolved from `RemoteLocationContext`.

## Important APIs, Types, And Functions
- Constructors support no-arg methods, `ClientProtocol` methods, and arbitrary protocol classes.
- `getMethod` resolves the reflected Java method using stored protocol, method name, and parameter types.
- `getParams(RemoteLocationContext)` converts the parameter template into actual invocation parameters for a specific location.
- `getProtocol`, `getTypes`, `getMethodName`, and `toString` expose metadata.
- Special handling rebuilds `CacheDirectiveInfo` with a destination path when the dynamic parameter type is `CacheDirectiveInfo`.

## Control Flow
The typed constructor validates that parameter count matches type count. `getMethod` uses `Class.getDeclaredMethod` and converts reflection/security failures to `IOException`. `getParams` returns an empty array for no-arg calls; otherwise it copies static values and replaces `RemoteParam` placeholders with per-context values.

## State And Persistence
`RemoteMethod` is immutable after construction except that parameter objects themselves may be mutable references. It stores no persistent state.

## Dependencies And Integration Points
It depends on Java reflection, `ClientProtocol`, `CacheDirectiveInfo`, `Path`, `RemoteParam`, and `RemoteLocationContext`. `RouterRpcClient`, `Quota`, `RouterCacheAdmin`, admin destination validation, and fairness tests use it as the common invocation description.

## Risks And Edge Cases
`getTypes` assumes `types` is non-null; callers should avoid it for no-arg methods. Reflection catches method signature mismatches only at runtime. The cache directive special case assumes destination path replacement while preserving other directive fields. Dynamic parameters return null if called without context, which can break protocol invocations unless callers only use context-free calls for static parameters.

## Test Signals
Remote method behavior is exercised indirectly by extensive router RPC tests, cache admin tests, quota tests, and fairness handler tests such as `TestRouterHandlersFairness` and `TestRouterRefreshFairnessPolicyController`. Signature regressions surface when reflected methods are invoked through `RouterRpcClient`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteMethod.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteParam.java

## Purpose
`RemoteParam` is a placeholder for a parameter whose value depends on the remote location being invoked. It supports default destination-path mapping and explicit per-location map lookup.

## Important APIs, Types, And Functions
- The no-arg constructor creates a default parameter that resolves to `context.getDest()`.
- The map constructor stores a `Map<? extends RemoteLocationContext, ? extends Object>` used to look up context-specific values.
- `getParameterForContext(RemoteLocationContext)` returns null for null context, map lookup value when a map exists, or destination path by default.
- `toString` exposes the map for diagnostics.

## Control Flow
Resolution is a simple three-way branch: no context, map-backed context, or default destination. The class does not validate map completeness.

## State And Persistence
The instance stores an optional map reference. There is no defensive copy and no persistence, so external mutations to the map can affect later parameter resolution.

## Dependencies And Integration Points
It depends on `RemoteLocationContext` and is consumed by `RemoteMethod`. Router modules use it when forwarding path-like parameters, cache directive info, and quota paths to subclusters.

## Risks And Edge Cases
Missing map entries resolve to null and may produce downstream RPC failures. Default mapping ignores source path and always uses destination. Mutable maps can introduce race-prone behavior if shared across concurrent invocations.

## Test Signals
Behavior is indirectly covered by router RPC tests that verify operations reach destination paths, plus cache admin and quota tests where `RemoteMethod` uses `RemoteParam` to rewrite paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteResult.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteResult.java

## Purpose
`RemoteResult` is a typed container for the outcome of invoking a remote operation against one `RemoteLocationContext`. It can hold either a result, including a void-style explicit result marker, or an `IOException`.

## Important APIs, Types, And Functions
- `RemoteResult(T location, R result)` records a successful result and sets `resultSet`.
- `RemoteResult(T location, IOException e)` records a failed result.
- `getLocation`, `hasResult`, `getResult`, `hasException`, and `getException` expose the outcome.
- `toString` includes location plus result and/or exception details.

## Control Flow
The class has no complex control flow. It encodes success and failure with constructor choice and boolean checks.

## State And Persistence
State is immutable after construction: location, result, result-present flag, and exception. It is process-local and not persisted.

## Dependencies And Integration Points
It depends on `IOException` and `RemoteLocationContext`. Router RPC fan-out code can use it to return partial results while preserving per-location failure details.

## Risks And Edge Cases
A successful result may itself be null while `hasResult` remains true, which is useful for void-like calls but requires callers to check `hasResult` rather than `getResult() != null`. The failure constructor sets `resultSet` false even if the failed operation might have produced partial side effects.

## Test Signals
Coverage is indirect through fan-out methods in `RouterRpcClient`, quota aggregation, cache admin, and multi-destination tests that inspect per-location results or exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Router.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Router.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterAdminServer.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterAdminServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterCacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterCacheAdmin.java

## Purpose
`RouterCacheAdmin` implements router-side forwarding for HDFS cache directive and cache pool client protocol operations.

## Important APIs, Types, And Functions
- `addCacheDirective`, `modifyCacheDirective`, `removeCacheDirective`, and `listCacheDirectives` handle cache directives.
- `addCachePool`, `modifyCachePool`, `removeCachePool`, and `listCachePools` handle cache pools.
- Protected invoke methods expose map-returning behavior for tests and subclasses.
- `getRemoteMap` maps each `RemoteLocation` to the original `CacheDirectiveInfo` so `RemoteMethod` can rebuild it with destination paths.

## Control Flow
Directive operations with a path resolve router locations and invoke remote methods against those locations. Directive modification without a path, directive removal by ID, and all cache pool operations fan out across all namespaces from `ActiveNamenodeResolver`. Public list/add methods return the first value from the remote response map for single logical results.

## State And Persistence
The class stores references to `RouterRpcServer`, `RouterRpcClient`, and `ActiveNamenodeResolver`. Cache directive and pool state is persisted by downstream NameNodes, not by the router class.

## Dependencies And Integration Points
It depends on HDFS cache protocol classes, `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `RemoteParam`, `RemoteLocation`, `FederationNamespaceInfo`, and NameNode operation categories. `RouterClientProtocol` delegates cache-related `ClientProtocol` calls to this module.

## Risks And Edge Cases
Returning the first response for add/list operations assumes responses are equivalent or the relevant operation targets one logical location. Namespace-wide operations can partially fail depending on `invokeConcurrent` flags. `getRemoteMap` maps every location to the same directive object and relies on `RemoteMethod` special handling to rewrite the path per destination. Cache directive IDs are NameNode-local, so remove/modify semantics across namespaces require careful client expectations.

## Test Signals
Router client protocol, cache admin, and multi-destination tests indirectly exercise this module. Coverage should include path-remapping of cache directives and namespace-wide pool operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterCacheAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClient.java

## Purpose
`RouterClient` is a closeable admin-protocol client for connecting to a router's admin RPC server. It is used by router internals and tools to access mount table, router state, nameservice, and generic admin managers.

## Important APIs, Types, And Functions
- `createRouterProxy` configures protobuf RPC engine, creates a `RouterAdminProtocolPB` proxy, and wraps it in `RouterAdminProtocolTranslatorPB`.
- The constructor captures the current UGI and creates the proxy for a given admin address.
- `getMountTableManager`, `getRouterStateManager`, `getNameserviceManager`, and `getRouterGenericManager` expose the translator through narrower interfaces.
- `close` stops the RPC proxy.

## Control Flow
Construction sets protocol engine and gets a versioned protocol proxy using the configured socket factory and RPC timeout. Manager getters simply return the translator. Close is synchronized and calls `RPC.stopProxy`.

## State And Persistence
The client stores a translator proxy and the current user. It owns no persistent state. Remote calls persist data through `RouterAdminServer` and state-store-backed managers.

## Dependencies And Integration Points
It depends on Hadoop IPC, `RouterAdminProtocolPB`, `RouterAdminProtocolTranslatorPB`, `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `RouterGenericManager`, `NetUtils`, and `UserGroupInformation`. `MountTableRefresherService` caches `RouterClient` instances for remote cache refreshes.

## Risks And Edge Cases
The captured `ugi` is used at proxy creation time; long-lived cached clients in secure clusters depend on the refresher service recreating clients after expiration and relogin. `fallbackToSimpleAuth` is local to proxy creation and not exposed. Calling getters after `close` returns a stopped proxy reference, so owners must manage lifecycle.

## Test Signals
Admin CLI tests, router admin tests, disabled nameservice tests, and mount-table cache refresh tests cover proxy usage. Secure cache refresh tests are especially relevant because this client is cached and closed by `MountTableRefresherService`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientMetrics.java

## Purpose
`RouterClientMetrics` publishes counters for router client protocol activity through Hadoop Metrics2. It tracks total invoked operations and a subset of concurrently invoked fan-out operations.

## Important APIs, Types, And Functions
- `create(Configuration)` registers a `RouterClientMetrics` instance with `DefaultMetricsSystem` and tags it with process/session metadata.
- `shutdown()` shuts down the default metrics system.
- `incInvokedMethod(Method)` increments a method-specific counter for many `ClientProtocol` methods, defaulting to `otherOps`.
- `incInvokedConcurrent(Method)` increments counters for methods invoked concurrently across remote locations, defaulting to `concurrentOtherOps`.
- Numerous `@Metric MutableCounterLong` fields define the published metric names.

## Control Flow
Both increment methods switch on `method.getName()`. Known operation names increment dedicated counters; unknown names increment the appropriate `other` counter. There is no reflection beyond reading the method name passed by caller code.

## State And Persistence
Metrics counters are in-memory Metrics2 mutable counters registered in the process metrics system. They are exposed to configured metrics sinks but not persisted by this class.

## Dependencies And Integration Points
It depends on `Configuration`, `DFSConfigKeys.DFS_METRICS_SESSION_ID_KEY`, `DefaultMetricsSystem`, `MetricsRegistry`, Metrics2 annotations, and Java reflection `Method`. `RouterMetricsService` creates and exposes this class; router RPC client/server paths call increment methods around proxied operations.

## Risks And Edge Cases
The switches are manually maintained and can miss new `ClientProtocol` methods, sending them to `otherOps`. Some counter names must match expected metrics consumers, so renaming fields is externally visible. `shutdown` calls `DefaultMetricsSystem.shutdown`, which can affect other metrics registered in the same process. Concurrent counters cover a subset of methods, not every method listed in total counters.

## Test Signals
`TestRouterClientMetrics` directly validates metric registration and operation counters. Broader router RPC tests indirectly exercise counter increments for client operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientMetrics.java -->
