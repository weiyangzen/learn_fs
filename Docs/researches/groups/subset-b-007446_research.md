<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java

## Purpose
`RouterClientProtocol` is the router-side implementation of HDFS `ClientProtocol`. It is the main translation layer between client RPCs and Router-Based Federation: it checks operation category, resolves the federated path to one or more `RemoteLocation`s, chooses sequential, concurrent, or single-namespace dispatch through `RouterRpcClient`, and synthesizes router-visible results such as virtual mount-point statuses, merged listings, datanode reports, content summaries, and open-file listings.

## Important APIs, Types, and Functions
The constructor wires the `RouterRpcServer`, `RouterRpcClient`, `FileSubclusterResolver`, `ActiveNamenodeResolver`, feature modules for erasure coding/cache/snapshot/storage policy, the security manager, and `RouterFederationRename`. It selects async helper implementations when `rpcServer.isAsync()` is true.

Client-facing methods cover file lifecycle (`create`, `append`, `addBlock`, `complete`, `truncate`, `delete`, `mkdirs`), metadata (`getFileInfo`, `getListing`, `getLocatedFileInfo`, `setPermission`, ACL and xattr operations), cluster-wide admin reads/writes (`getStats`, `setSafeMode`, `rollEdits`, `refreshNodes`, `setBalancerBandwidth`), feature delegates (`RouterSnapshot`, `RouterCacheAdmin`, `RouterStoragePolicy`, `ErasureCoding`), quota (`setQuota`, `getQuotaUsage`), and federation-specific helpers (`getRenameDestinations`, `aggregateContentSummary`, `getMountPointStatus`, `getLocationsForContentSummary`, `mergeAndSortOpenFileListResults`).

Several protocol methods are intentionally not implemented or not supported through the router: `getDelegationTokens` returns `null`, `getBatchedListing` throws, `upgradeStatus` throws, and edit-log/encryption-key related APIs return `null` after restricted `checkOperation` calls.

## Control Flow
Every public RPC begins with `rpcServer.checkOperation` using the matching NameNode operation category. Path-based methods usually call `rpcServer.getLocationsForPath`, build a reflective `RemoteMethod`, and dispatch through `rpcClient.invokeSequential`, `invokeConcurrent`, `invokeSingle`, `invokeSingleBlockPool`, or `invokeAll`.

Write creation first handles `/.../_all` style parent creation, chooses a create location via `rpcServer.getCreateLocation`, and retries alternate destinations only when `checkFaultTolerantRetry` sees a connection/no-namenode failure and the path is fault tolerant. Rename first filters source/destination pairs with matching nameservices. If none remain, it delegates cross-namespace rename to `RouterFederationRename`; multi-destination directory renames require all source locations to remain eligible.

Listing is federated. `getListingInt` concurrently reads downstream directory listings, `getListing` merges them by local name, trims entries past the lowest downstream batch boundary to preserve pagination correctness, injects virtual mount points from the resolver, and honors `allowPartialList` for non-`FileNotFoundException` failures. `getFileInfo` similarly falls back to mount point metadata when no downstream file exists. Content summary recursively gathers direct and child mount locations, removes descendant redundancy per namespace, invokes downstream summaries, and aggregates counts.

Block-oriented operations route by block pool when possible. `addBlock`, `getAdditionalDatanode`, `abandonBlock`, `complete`, `updateBlockForPipeline`, `updatePipeline`, and `reportBadBlocks` use an `ExtendedBlock` or block pool id to target the owning namespace. Cluster-wide methods invoke all registered namespaces and aggregate values, with a few methods using `requireResponse` or standby calls depending on semantics.

## State and Persistence Behavior
The class itself persists no durable state. It caches `FsServerDefaults` in volatile fields for `serverDefaultsValidityPeriod`, keeps configuration-derived flags such as `allowPartialList`, mount-status timeout, default nameservice behavior, superuser/group reporting identity, and exposes the live cross-namespace rename counter through `RouterFederationRename`.

Persistent state is read or changed through collaborators: namespace metadata through downstream NameNodes, mount table metadata through the resolver, quota through `Quota`, delegation tokens through `RouterSecurityManager`, and federation rename jobs through the FedBalance scheduler. Virtual `HdfsFileStatus` objects for mount points are synthesized in memory and may overlay downstream status details.

## Dependencies and Integration Points
Primary dependencies are `RouterRpcServer`, `RouterRpcClient`, `FileSubclusterResolver`/`MountTableResolver`, `ActiveNamenodeResolver`, `RemoteLocation`, `RemoteMethod`, `RemoteResult`, `NameNode.OperationCategory`, and HDFS protocol model classes. Feature calls integrate with `RouterSnapshot`, `RouterCacheAdmin`, `RouterStoragePolicy`, `ErasureCoding`, and async variants. Quota integration goes through `rpcServer.getQuotaModule()`. Federation rename integrates with `RouterFederationRename` and FedBalance.

## Risks
Dispatch semantics vary by method; using sequential dispatch where all destinations must be mutated, or concurrent dispatch where first-success is expected, can cause inconsistent federation state. Listing pagination is sensitive to the `lastName` and `remainingEntries` logic and can skip or duplicate entries if downstream batches are merged incorrectly. Virtual mount-point status may mask downstream failures because it catches `IOException` and falls back to mount table defaults. Several protocol methods return `null` rather than throwing, so client compatibility depends on callers tolerating unsupported APIs. Recursive content-summary location discovery can be expensive on deep mount trees. Fault-tolerant retry is deliberately limited to availability-style exceptions; expanding it could duplicate writes.

## Test Signals
Useful tests should cover path resolution and operation-category checks for representative read/write/admin calls, create/mkdir retry behavior on fault-tolerant mounts, same-namespace and cross-namespace rename cases, multi-destination directory rename rejection, directory listing pagination with overlapping downstream entries and mount points, `allowPartialList` behavior, mount-point status synthesis from mount table and downstream status, block-pool routing, content summary deduplication, open-file merge ordering, quota delegation, async feature-module construction, and unsupported/null-return protocol methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java

## Purpose
`RouterFederationRename` implements the exceptional case where a router rename crosses nameservices. Normal HDFS rename cannot move data between namespaces, so this class validates the request, checks permissions, builds a FedBalance job with DistCp and trash phases, submits it to the router's rename scheduler, and waits for completion.

## Important APIs, Types, and Functions
`routerFedRename` is the main API. It requires cross-namespace rename to be enabled, exactly one source and one destination `RemoteLocation`, no `.snapshot` component, and write access to both parents. `checkPermission` runs permission checks either as a proxy user in secure mode or as the remote user in simple mode. `buildRouterRenameJob` validates configuration and constructs `FedBalanceContext`, `DistCpProcedure`, `TrashProcedure`, and `BalanceJob`. `getRouterFederationRenameCount`, `countIncrement`, and `countDecrement` expose and maintain the number of active rename jobs.

## Control Flow
`routerFedRename` rejects disabled or ambiguous requests, validates snapshot and permission constraints, switches to the router login user, creates a `BalanceJob`, increments the active counter, submits the job to `BalanceProcedureScheduler`, waits synchronously until done, checks `job.getError()`, and decrements the counter in a `finally` block. Interrupted waits become `InterruptedIOException`.

## State and Persistence Behavior
The class holds only the router RPC server, configuration, and an in-memory `AtomicInteger` counter. Durable data movement and cleanup are delegated to FedBalance procedures and the scheduler. The job context reads policy from router configuration, including map count, bandwidth, delay, diff threshold, trash policy, and force-close behavior.

## Dependencies and Integration Points
It depends on `RouterRpcServer` for enablement and scheduler access, `RemoteLocation` for resolved source/destination locations, `UserGroupInformation` and `NameNode.getRemoteUser` for identity handling, HDFS `Path` and `FileSystem.access` for permission checks, and `org.apache.hadoop.tools.fedbalance` classes for the actual data move.

## Risks
The operation is synchronous from the RPC handler perspective while the FedBalance job runs, so long data moves can tie up request handling. Configuration validation rejects negative map, bandwidth, delay, or diff values, but operational correctness still depends on FedBalance semantics. Permission checking uses parent write access only and separate filesystems for source/destination; changes between validation and execution are possible. Snapshot path detection is string based on `.snapshot/`. The active counter must remain balanced on all submit/wait failures.

## Test Signals
Tests should cover disabled cross-namespace rename, source/destination cardinality checks, snapshot path rejection, secure and simple-mode permission checks, invalid configuration values, job build fields, scheduler submit/wait success and failure, interruption conversion, and active counter decrement on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFederationRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java

## Purpose
`RouterFsck` exposes a federated FSCK wrapper. Instead of checking local namespace state, it discovers active NameNodes from the federation state store and proxies the incoming `/fsck` query to each active NameNode web endpoint, streaming their output back to the caller.

## Important APIs, Types, and Functions
The constructor captures the `Router`, query parameter map, response `PrintWriter`, and remote address. `fsck` is the public execution method. `remoteFsck` builds the downstream URL from `MembershipState.getWebScheme`, `getWebAddress`, and `getURLArguments`, then copies UTF-8 lines from the downstream response. `getURLArguments` serializes the first value for each query key.

## Control Flow
`fsck` logs and prints an unstable-feature warning and start banner, obtains `MembershipStore` from the router state store, reads all Namenode registrations, sorts them, and invokes `remoteFsck` only for `ACTIVE` memberships. Per-namenode IO failures are printed and do not abort the whole run. Top-level exceptions produce an end banner and error text, and the writer is always closed.

## State and Persistence Behavior
This class stores no durable data. It reads live membership records from the state store and streams remote HTTP data. It does not cache membership or FSCK responses.

## Dependencies and Integration Points
It integrates with `StateStoreService`, `MembershipStore`, `GetNamenodeRegistrations*`, `MembershipState`, `FederationNamenodeServiceState`, NameNode web `/fsck`, and the servlet wrapper that supplies the authenticated user context.

## Risks
`getURLArguments` does not URL-encode keys or values and only uses `value[0]`, which can mis-handle special characters or repeated parameters. FSCK output is streamed serially, so a slow NameNode delays the whole response. There is no explicit connection/read timeout here. The writer is closed by this helper, which is suitable for servlet ownership but important for callers. The feature is explicitly logged as unstable.

## Test Signals
Tests should exercise active-only filtering, membership sorting, downstream URL construction including schemes and query arguments, handling of individual NameNode IO failures, top-level exception reporting, writer closure, and behavior for empty membership sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java

## Purpose
`RouterFsckServlet` binds the router HTTP `/fsck` endpoint to `RouterFsck`. It authenticates the HTTP caller using the standard DFS servlet path and executes the federated FSCK under that `UserGroupInformation`.

## Important APIs, Types, and Functions
The servlet constants are `SERVLET_NAME = "fsck"` and `PATH_SPEC = "/fsck"`. `doGet` reads the request parameter map, response writer, remote address, servlet context, router configuration, and UGI, then calls `new RouterFsck(...).fsck()` inside `ugi.doAs`.

## Control Flow
On GET, the servlet resolves the caller address with `InetAddress.getByName`, retrieves `Configuration` and `Router` from `RouterHttpServer` context attributes, builds a `RouterFsck`, and delegates. If the privileged action is interrupted, it responds with HTTP 400 and the interruption message.

## State and Persistence Behavior
The servlet has no mutable state beyond serialization metadata. It relies on servlet-context attributes populated by `RouterHttpServer` and streams output through the response writer.

## Dependencies and Integration Points
It extends `DfsServlet`, uses `getUGI`, `RouterHttpServer.getConfFromContext`, `RouterHttpServer.getRouterFromContext`, `UserGroupInformation.doAs`, and `RouterFsck`. It is installed by `RouterHttpServer.setupServlets`.

## Risks
The response writer is obtained before delegated FSCK and is closed by `RouterFsck`. `InterruptedException` is the only caught exception; IO errors propagate through servlet handling. Remote address resolution may fail if the request remote address is not resolvable. Query parameter validation is delegated entirely to downstream NameNode FSCK handling.

## Test Signals
Tests should verify context attribute lookup, UGI execution, parameter and remote-address propagation to `RouterFsck`, servlet registration constants, and interrupted-action response status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java

## Purpose
`RouterHeartbeatService` periodically publishes the router's liveness, state, admin address, and state-store version view into the federation state store. Other routers and admin tools use these `RouterState` records to discover router status.

## Important APIs, Types, and Functions
It extends `PeriodicService`. `periodicInvoke` calls `updateStateStore`. `updateStateAsync` starts a daemon `SubjectInheritingThread` for asynchronous update. `updateStateStore` builds `RouterState`, adds `StateStoreVersion` from membership and mount-table cached records, sets the admin address according to heartbeat-with-IP configuration, and sends `RouterHeartbeatRequest` to `RouterStore.routerHeartbeat`. `getStateStoreVersion` scans cached records for the maximum modification time.

## Control Flow
Initialization reads `DFS_ROUTER_HEARTBEAT_STATE_INTERVAL_MS` and configures the periodic interval. Each tick checks router id and state-store availability, builds a heartbeat record from router runtime state, resolves version timestamps, chooses host:port or ip:port admin address, submits the heartbeat, and logs success or failure.

## State and Persistence Behavior
The service persists router heartbeat records in the state store via `RouterStore`; it keeps no independent durable state. Version values are inferred from cached record stores and default to `-1` if unavailable. The method is synchronized to avoid overlapping updates from periodic and async paths.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterStore`, `StateStoreService`, `MembershipStore`, `MountTableStore`, `CachedRecordStore`, `RouterState`, `StateStoreVersion`, `StateStoreUtils`, `RouterHeartbeatRequest`, and `RouterHeartbeatResponse`.

## Risks
Heartbeat quality depends on state-store driver readiness and cached record freshness. If record stores are not `CachedRecordStore`, version stays `-1`. Admin address formatting differs based on configuration and can affect discoverability. Exceptions are logged but do not fail the periodic service, so monitoring must inspect heartbeat freshness.

## Test Signals
Tests should cover interval initialization, unavailable state store paths, null router id, heartbeat request fields, admin address IP-vs-host behavior, cached version extraction, failed heartbeat response logging, async thread creation, and synchronization under concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHeartbeatService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java

## Purpose
`RouterHttpServer` manages the router web server. It exposes the router UI, WebHDFS handlers, active-state probe, federated FSCK, and network-topology servlet through Hadoop `HttpServer2`.

## Important APIs, Types, and Functions
It extends `AbstractService`. `serviceInit` resolves HTTP and HTTPS bind addresses from router config. `serviceStart` builds the `HttpServer2` template with router SPNEGO/keytab settings, configures X-Frame headers, initializes WebHDFS with `RouterWebHdfsMethods`, stores router/config context attributes, registers internal servlets, starts the server, and updates the actual HTTP port if an ephemeral port was used. `serviceStop` stops the server. `getConfFromContext` and `getRouterFromContext` retrieve context attributes for servlets.

## Control Flow
The service lifecycle follows Hadoop service phases: configuration-derived addresses in init, server construction and servlet registration in start, connector address reconciliation after start, and graceful stop if a server exists.

## State and Persistence Behavior
The class holds runtime-only `Configuration`, `Router`, `HttpServer2`, and socket addresses. It persists no data. Servlet context attributes are process-local integration state.

## Dependencies and Integration Points
Dependencies include `DFSUtil.getHttpServerTemplate`, `NameNodeHttpServer.initWebHdfs`, `HttpServer2`, `JspHelper.CURRENT_CONF`, `IsRouterActiveServlet`, `RouterFsckServlet`, `RouterNetworkTopologyServlet`, `RouterWebHdfsMethods`, and router HTTP/HTTPS/SPNEGO config keys.

## Risks
Misconfigured bind hosts, SPNEGO principal, keytab, or X-Frame settings affect availability and security. Context attribute names must remain compatible with `DfsServlet` and router servlets. Ephemeral port handling updates only the HTTP address from connector zero. Servlet registration order and `requireAuth` flags matter for operational endpoints.

## Test Signals
Tests should cover address resolution, X-Frame propagation, WebHDFS initialization package, servlet registration and auth flag for FSCK, context attributes, ephemeral port update, getters, and stop behavior when startup partially failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java

## Purpose
`RouterMetrics` registers router activity metrics with Hadoop metrics2. It currently exposes router process/session tags, JVM metrics, and a startup safe-mode duration gauge.

## Important APIs, Types, and Functions
`create` obtains the DFS metrics session id, creates `JvmMetrics` for process name `Router`, and registers a `RouterMetrics` instance with `DefaultMetricsSystem`. `setSafeModeTime` updates the annotated `MutableGaugeInt`. `getJvmMetrics` exposes the JVM metrics handle. `shutdown` shuts down the default metrics system.

## Control Flow
Construction tags the internal `MetricsRegistry` with process and session. Metrics registration is centralized through the static factory rather than public constructor access.

## State and Persistence Behavior
Metrics are in-memory and exported by the Hadoop metrics system. No durable state is written. The safe-mode time is cast from `long` to `int`, so very large elapsed values would truncate.

## Dependencies and Integration Points
It depends on `DefaultMetricsSystem`, `MetricsSystem`, `MetricsRegistry`, metrics annotations, `MutableGaugeInt`, `JvmMetrics`, and `DFS_METRICS_SESSION_ID_KEY`. `RouterMetricsService` owns lifecycle.

## Risks
Calling `DefaultMetricsSystem.shutdown()` from this component affects the process-wide metrics system, not just router metrics. The `safeModeTime` gauge is annotation-injected by metrics2 registration and must be non-null before use. The int cast is a minor overflow risk.

## Test Signals
Tests should validate metrics registration, process/session tags, JVM metrics creation, safe-mode gauge update after registration, and service shutdown interactions with other metrics components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java

## Purpose
`RouterMetricsService` owns the lifecycle of all router metrics and JMX-facing federation metrics. It creates core metrics during service init, creates JMX beans during service start, and closes everything during service stop.

## Important APIs, Types, and Functions
`serviceInit` creates `RouterMetrics` and `RouterClientMetrics`. `serviceStart` constructs `NamenodeBeanMetrics` and `RBFMetrics` wrappers over the router. `serviceStop` closes `RBFMetrics` and `NamenodeBeanMetrics`, then shuts down router and client metrics. Getter methods expose each metrics object and `getJvmMetrics` safely returns null before initialization.

## Control Flow
The service follows Hadoop lifecycle ordering: basic metrics are available after init, JMX beans after start, and all handles are guarded for null on stop. It does not call `super.serviceInit/start/stop` in the shown overrides, so lifecycle behavior relies on `AbstractService` caller semantics around override methods.

## State and Persistence Behavior
All state is process-local metrics/JMX handles. No durable state is written. Shutdown closes MBeans and metrics systems.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterMetrics`, `RouterClientMetrics`, `RBFMetrics`, `NamenodeBeanMetrics`, `JvmMetrics`, and `AbstractService`.

## Risks
Partial initialization can leave some handles null; the stop path handles that. Metrics shutdown order matters because `RouterMetrics.shutdown()` shuts down the default metrics system. Missing `super` calls could be relevant if `AbstractService` changes expectations. JMX wrapper constructors may throw during start, leaving only init metrics active.

## Test Signals
Tests should cover init/start/stop lifecycle, null-safe stop after partial start, getter behavior before and after init/start, JVM metrics delegation, and MBean close calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterMetricsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java

## Purpose
`RouterNamenodeProtocol` implements selected `NamenodeProtocol` calls through the router, mainly for operations that can be proxied to one available namespace or targeted to the namespace containing a datanode. Many checkpoint/secondary-NameNode style operations are deliberately unsupported.

## Important APIs, Types, and Functions
The constructor captures `RouterRpcServer` and `RouterRpcClient`. Implemented methods include `getBlocks`, `getBlockKeys`, `getTransactionID`, `getMostRecentCheckpointTxId`, `getMostRecentNameNodeFileTxId`, and `versionRequest`. Unsupported or no-op methods include `rollEditLog`, subordinate namenode registration, checkpoint start/end, edit-log manifest, upgrade/rolling-upgrade flags, and SPS path retrieval.

## Control Flow
`getBlocks` checks read access, asks the router for datanode storage reports across namespaces, finds the namespace whose report contains the input datanode UUID, and invokes `NamenodeProtocol.getBlocks` on that namespace. Namespace-agnostic reads build a `RemoteMethod` for `NamenodeProtocol` and call `rpcServer.invokeAtAvailableNs`. Restricted unsupported methods still call `checkOperation` with `false` for operation support before returning null/false or doing nothing.

## State and Persistence Behavior
The class is stateless beyond collaborator references. It reads datanode reports and delegates protocol calls; it does not persist or cache protocol results.

## Dependencies and Integration Points
Dependencies include `NamenodeProtocol`, `RouterRpcServer`, `RouterRpcClient`, `RemoteMethod`, `DatanodeStorageReport`, `DatanodeInfo`, `NamespaceInfo`, `ExportedBlockKeys`, and NameNode operation categories.

## Risks
`getBlocks` returns `null` if the datanode UUID is not found, so callers must handle missing routing. Datanode report retrieval can be expensive and stale. Unsupported checkpoint-related methods may not satisfy components expecting a real NameNode. Methods returning `false` for upgrade state may hide actual namespace-specific state if called unexpectedly.

## Test Signals
Tests should cover datanode-to-namespace resolution, no-match return behavior, `RemoteMethod` protocol/signature correctness, invocation at available namespace, operation-category enforcement, and explicit unsupported method behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNamenodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java

## Purpose
`RouterNetworkTopologyServlet` exposes a router-level network topology view by collecting federated datanode reports and reusing NameNode topology rendering in text or JSON form.

## Important APIs, Types, and Functions
`doGet` parses the Accept header through `NetworkTopologyServlet.parseAcceptHeader`, sets response content type, retrieves the `Router` from servlet context, gets an `ALL` datanode report from the router RPC server, converts the array to `List<Node>`, and calls `printTopology`.

## Control Flow
The servlet supports both sync and async router RPC servers. In async mode it calls `getDatanodeReportAsync` and then `syncReturn(DatanodeInfo[].class)`; in sync mode it calls `getDatanodeReport`. Output is written through a UTF-8 `PrintStream`. Any throwable while printing sends HTTP 410 and is rethrown as `IOException`; the response output stream is closed in `finally`.

## State and Persistence Behavior
The servlet has no persistent state. It reads current router datanode reports and streams a derived topology response.

## Dependencies and Integration Points
It extends `NetworkTopologyServlet`, uses `RouterHttpServer.getRouterFromContext`, `RouterRpcServer`, async `syncReturn`, HDFS `DatanodeInfo`, `HdfsConstants.DatanodeReportType.ALL`, Hadoop `Node`, and servlet response APIs. It is registered by `RouterHttpServer`.

## Risks
The method closes the servlet output stream explicitly after try-with-resources already manages the print stream. Async result handling wraps any exception in `IOException`. Large federations may produce expensive reports. Error handling sends HTTP 410 for all print failures, which may be semantically broad.

## Test Signals
Tests should cover Accept header handling and content types, sync and async datanode report paths, topology rendering calls, exception-to-HTTP-410 behavior, stream closure, and servlet context router lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java

## Purpose
`RouterPermissionChecker` adapts HDFS permission checking for router mount-table records. It checks ACL-like owner/group/other bits on `MountTable` entries and implements router superuser checks based on the active RPC caller.

## Important APIs, Types, and Functions
Constructors initialize the superclass `FSPermissionChecker` with router superuser/group and a caller UGI. `checkPermission(MountTable, FsAction)` evaluates mount-table mode bits against current user and groups. `checkSuperuserPrivilege` overrides NameNode behavior to require the RPC remote user to be the router superuser or a member of the configured supergroup.

## Control Flow
Mount-table checks short-circuit for superuser, owner permissions, group permissions, and finally other permissions for non-owner non-group callers. Failure raises `AccessControlException` with source path and requested action. Superuser checks fetch `NameNode.getRemoteUser`, reject missing UGI, compare short user name, then group set.

## State and Persistence Behavior
The checker stores immutable `superUser` and `superGroup` strings. It persists no data and reads caller/group state from `FSPermissionChecker` and `NameNode` request context.

## Dependencies and Integration Points
Dependencies include `FSPermissionChecker`, `MountTable`, `FsPermission`, `FsAction`, `UserGroupInformation`, `NameNode.getRemoteUser`, and `AccessControlException`. It is used by router admin and mount table access paths.

## Risks
Correctness depends on the current RPC context being set; missing UGI is an access denial. The owner/group/other logic does not consider extended ACLs, only `FsPermission` bits stored on mount-table entries. Supergroup membership uses the remote user's current group set.

## Test Signals
Tests should cover superuser bypass, owner/group/other allow and deny cases, default mount permission expectations, missing remote user denial, supergroup membership, and constructor behavior with explicit and current UGIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterPermissionChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java

## Purpose
`RouterQuotaManager` maintains the router's in-memory quota cache for mount-table paths. It supports lookup of applicable ancestor quotas, child path scans, parent quota scans, and cache updates/removals under a read/write lock.

## Important APIs, Types, and Functions
`getAll` returns all cached mount paths. `getQuotaUsage` returns the nearest quota-set usage for a path or ancestor. `getPaths` returns cached entries under a parent path. `getParentsContainingQuota` returns quota-set ancestors for a child. `put`, `updateQuota`, `remove`, and `clear` mutate the cache. `isQuotaSet` checks namespace, space, or per-storage-type quota values against `HdfsConstants.QUOTA_RESET`.

## Control Flow
Lookups use the sorted `TreeMap` to find exact, descendant, or floor entries. `getQuotaUsage` recurses toward parent paths until it finds a quota-set entry or reaches no parent. `getPaths` scans a `subMap` bounded by parent path and `Character.MAX_VALUE`, then filters with `DFSUtil.isParentEntry`. `updateQuota` preserves existing usage counters while replacing quota limits.

## State and Persistence Behavior
The only state is a process-local `TreeMap<String, RouterQuotaUsage>` guarded by `ReentrantReadWriteLock`. It is a cache of mount table quota information and aggregated usage; durable mount-table quota state is elsewhere.

## Dependencies and Integration Points
Dependencies include `RouterQuotaUsage`, `QuotaUsage`, `Path`, `HdfsConstants`, NameNode `Quota` storage-type iteration, and `DFSUtil.isParentEntry`. `RouterQuotaUpdateService` refreshes this cache and `Quota` uses it for enforcement.

## Risks
`getAll` returns the live `keySet` view after releasing the read lock, so concurrent mutation can affect callers. `getQuotaUsage` recursively reacquires the read lock, which works with `ReentrantReadWriteLock` but can be surprising. Cache correctness depends on periodic refresh and explicit updates from mount-table changes. Path prefix scans must be paired with `isParentEntry` to avoid false positives.

## Test Signals
Tests should cover exact and ancestor quota lookup, unset quota skipping, root and parent recursion, child path scans with prefix collisions, parent quota collection order, update preserving usage, stale removal/clear, per-storage-type quota detection, and concurrent read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java

## Purpose
`RouterQuotaUpdateService` periodically reconciles router quota cache entries with mount-table quota definitions and actual downstream namespace usage. It also fixes remote quota settings that differ from the global router quota.

## Important APIs, Types, and Functions
The constructor validates that the router quota manager exists. `serviceInit` sets the periodic interval from `DFS_ROUTER_QUOTA_CACHE_UPDATE_INTERVAL`. `periodicInvoke` is the main refresh loop. `getMountTableStore`, `getMountTableEntries`, and `getQuotaSetMountTables` retrieve mount-table records and update/remove cache entries. `fixGlobalQuota` pushes global quota values to remote locations through `Quota.setQuotaInternal`. `generateNewQuota` combines old quota limits with current usage counters.

## Control Flow
Each tick loads quota-set mount tables, initializes a remote-usage map, then for each quota entry checks whether the federated source exists. Missing or zero-mtime destinations reset usage to zero while preserving limits. Existing entries ask the quota module for per-location usage, aggregate it, store remote usage for later consistency repair, update the quota manager, and write the new quota back to the `MountTable` record object. After scanning, every observed remote quota is compared to the global quota and corrected if namespace, space, or type quota differs.

## State and Persistence Behavior
The service mutates the in-memory `RouterQuotaManager` cache. It reads mount-table entries from the state store and calls downstream quota-setting APIs to repair remote quota values. It does not explicitly write modified `MountTable` objects back to the state store in this class; durable updates are expected from store/cache behavior or other quota paths.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterRpcServer`, `RouterQuotaManager`, `MountTableStore`, `MountTable`, `Quota`, `RemoteLocation`, `QuotaUsage`, `RouterQuotaUsage`, `StorageType`, `HdfsFileStatus`, state-store request/response types, and async `syncReturn`.

## Risks
A broad catch logs errors and continues, which keeps the service alive but can leave stale quota cache. Existing-path detection treats `ret == null` or modification time zero as absent, which relies on router virtual mount-status conventions. `fixGlobalQuota` can issue writes to remote namespaces during a periodic refresh. Async mode depends on `syncReturn` matching the immediately preceding call. Cache `getAll` returns a live key view, so stale-path set construction must copy before mutations, which this code does.

## Test Signals
Tests should cover constructor failure without quota manager, interval config, mount-store lookup failure, stale cache removal, quota-set filtering, missing destination zero-usage generation, successful aggregate usage update, IO failure for one entry continuing others, global quota repair for namespace/space/type quotas, async `syncReturn` paths, and `generateNewQuota` preservation of limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java

## Purpose
`RouterQuotaUsage` is the router-specific `QuotaUsage` subclass used to represent aggregated quota usage and limits for federation mount points. It adds fluent builder methods, quota violation checks, and a compact string representation.

## Important APIs, Types, and Functions
`RouterQuotaUsage.Builder` extends `QuotaUsage.Builder` and overrides setters to return the router builder type. `verifyNamespaceQuota`, `verifyStoragespaceQuota`, and `verifyQuotaByStorageType` throw HDFS quota exceptions when usage exceeds configured limits. `toString` renders namespace and storage-space quota/usage pairs, using `-` for reset quotas and byte descriptions for space values.

## Control Flow
Violation checks read the relevant quota and consumed values, skip reset storage-type quotas, and use NameNode `Quota.isViolated`. Storage-type verification iterates only over types supporting quota.

## State and Persistence Behavior
Instances are immutable through the inherited `QuotaUsage` builder pattern. No persistence occurs here; values are held in router quota cache and mount-table records.

## Dependencies and Integration Points
Dependencies include `QuotaUsage`, `StorageType`, `HdfsConstants`, `NSQuotaExceededException`, `DSQuotaExceededException`, NameNode `Quota`, `DirectoryWithQuotaFeature` semantics, and `StringUtils.byteDesc`. `RouterQuotaManager` and `RouterQuotaUpdateService` build and consume this type.

## Risks
Quota checks must be called by enforcement paths; this class does not enforce automatically. The builder supports array setters inherited from `QuotaUsage`, so callers must provide arrays aligned with `StorageType.values()`. `toString` omits per-storage-type quotas, which is fine for compact logs but not full diagnostics.

## Test Signals
Tests should cover fluent builder chaining, namespace violation and reset behavior, storage-space violation and reset behavior, per-storage-type iteration and exception, default counts, inherited getter values, and `toString` formatting for set and unset quotas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java

## Purpose
`RouterRpcClient` is the router-to-NameNode RPC engine. It owns connection pooling, reflective protocol invocation, failover/retry behavior, observer-read routing, concurrent fan-out, fairness permits, caller-context propagation, result post-processing, and monitoring hooks used by higher-level router protocols.

## Important APIs, Types, and Functions
The constructor creates a `ConnectionManager`, concurrent-call executor, retry policy, fairness controller, observer-read settings, proxy-user behavior, and active state-id freshness tracking. Connection and health APIs expose counts and JSON for connection pools, executor pool, and fairness permit counters.

Core invocation APIs are `invokeSingle` by namespace, block, block pool, or `RemoteLocationContext`; `invokeSequential`; `invokeAll`; and multiple `invokeConcurrent` overloads returning maps or `RemoteResult` lists. Lower-level helpers include `invokeMethod`, `invoke`, `handlerInvokeException`, `handleInvokeMethodIOException`, `handlerAllNamenodeFail`, `postProcessResult`, `processException`, `processExceptionMsg`, `getCleanException`, `getOrderedNamenodes`, `isObserverReadEligible`, `isNamespaceStateIdFresh`, `acquirePermit`, `releasePermit`, and `refreshFairnessPolicyController`. `ExecutionStatus` packs failover, observer-use, and completion flags.

## Control Flow
For a single namespace call, the client gets the remote UGI, acquires a fairness permit for the namespace, determines whether the reflected method is read-only and observer eligible, orders NameNodes from the resolver, resolves method parameters from `RemoteMethod`, invokes `invokeMethod`, and releases the permit. `invokeMethod` iterates candidate NameNodes, gets/reuses a connection for the current user and RPC address, augments caller context with client IP/port/id/call id/real user, invokes the method reflectively, updates active NameNode state and metrics on success, and handles IO failures by marking failover, observer fallback, unavailable observers, retriable cache rotation, or clean remote exceptions.

Sequential calls iterate `RemoteLocationContext`s in resolver order, localize remote exception messages from destination paths to federated source paths, and stop only when expected result class/value conditions are met. Concurrent calls acquire the global concurrent fairness permit, capture current `Server.Call` and `CallerContext`, create callables per location or per NameNode when standby fan-out is requested, run them with `executorService.invokeAll`, convert futures into `RemoteResult`s including timeout and execution exceptions, then optionally require all responses in `postProcessResult`.

Observer reads are enabled per namespace by XOR-like default/override logic. A read method must carry `@ReadOnly(activeOnly=false)`, the namespace state id must be fresh unless refresh is disabled, and the current call must include a client state id before observers are listed first. Calls to active NameNodes refresh the last-active timestamp.

## State and Persistence Behavior
The client maintains runtime state only: connection pools, executor threads, retry policy, fairness controller, accepted/rejected permit counters, observer-read override set, active state-id refresh accumulators, and monitor references. It persists no durable state. It updates resolver caches for active/unavailable NameNodes and can rotate resolver caches on no-namenode failures. Shutdown closes connection manager, executor, and fairness controller.

## Dependencies and Integration Points
Dependencies include `Router`, `ActiveNamenodeResolver`, `FederationNamenodeContext`, `ConnectionManager`, `ConnectionContext`, `RemoteMethod`, `RemoteLocationContext`, `RemoteResult`, Hadoop IPC `CallerContext`/`Server`, HA exceptions, retry policies, `RouterRpcMonitor`, `RouterClientMetrics`, `RouterRpcFairnessPolicyController`, `RouterStateIdContext`, and HDFS/IPC configuration keys.

## Risks
Reflective invocation makes method signatures and parameter mapping in `RemoteMethod` critical. Connection pooling is per user plus NameNode and may grow with user cardinality. Concurrent calls can overload the fixed executor; overload is surfaced as `StandbyException` so clients may fail over to another router. `invokeAll` returns true if any location succeeds, which is appropriate only for selected operations. `postProcessResult(requireResponse=true)` must distinguish partial success from total failure correctly. Observer reads depend on state-id freshness; stale state can route reads to active NameNodes, while incorrect freshness could expose stale observer data. Exception message rewriting uses string replacement and can mis-map unusual paths. Fairness permits must be released on every path.

## Test Signals
Tests should cover client configuration transformation, executor queue mode and overload handling, connection UGI/proxy-user selection, retry/failover decisions for standby/unavailable/remote exceptions, active NameNode update on failover success, observer-read eligibility and override logic, state-id freshness, sequential expected class/value semantics, exception localization, concurrent timeout and execution-exception results, require-response behavior, standby fan-out location mapping, fairness permit accept/reject counters and release paths, caller-context transfer to worker threads, resolver cache rotation, clean exception reconstruction, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterRpcClient.java -->
