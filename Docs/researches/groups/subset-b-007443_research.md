# Research Group: subset-b-007443

Grouped source-tree-aligned research for Hadoop HDFS Router-Based Federation protocol, balance, fairness, and metrics files. Each section is delimited for deterministic splitting into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientProtocolTranslatorPB.java

Purpose: client-side protobuf translator for Router `ClientProtocol` calls. It subclasses the standard `ClientNamenodeProtocolTranslatorPB` and preserves synchronous behavior by delegating to `super`, while adding async-mode paths that build request protos, call `ClientNamenodeProtocolPB`, and convert responses back into HDFS domain objects.

Important APIs and types: constructor stores `ClientNamenodeProtocolPB rpcProxy`; every override checks `Client.isAsynchronousMode()`. Covered operations span file creation/append/block allocation, listings, leases, snapshots, cache pools/directives, ACLs, xattrs, encryption zones, erasure coding, storage policies, delegation tokens, stats, datanode reports, HA state, inotify edits, and enclosing-root lookup. Conversion depends heavily on `PBHelperClient`, `PBHelper`, generated `ClientNamenodeProtocolProtos`, `AclProtos`, `XAttrProtos`, `EncryptionZonesProtos`, `ErasureCodingProtos`, and security protos.

Control flow: synchronous calls immediately call the parent translator. Async calls build a concrete request proto, pass a lambda invoking `rpcProxy.method(null, request)` into `asyncIpcClient`, and provide a response-conversion lambda plus the expected return class. Void methods use a response lambda returning `null`. Optional response fields are checked with `has*()` before conversion, and batched/list responses construct Hadoop collections such as `BatchedListEntries`, `BatchedDirectoryListing`, `HdfsPartialListing`, and arrays.

State and persistence: the class holds only the RPC proxy; no durable state is created. It preserves protocol state through serialized protobuf fields, including file IDs, block IDs, lease holders, permissions including unmasked permissions, cache cursors, snapshot cursors, and namespace lists. Persistence effects occur on downstream Router/NameNode services.

Dependencies and integration points: integrates Router async IPC with the existing HDFS client-name-node protobuf protocol. It must stay aligned with the parent translator, generated proto schemas, `RouterClientNamenodeProtocolServerSideTranslatorPB`, and `AsyncRpcProtocolPBUtil.asyncIpcClient`. It is used when Router RPC clients run in asynchronous mode.

Risks: async paths duplicate many parent conversion details, so schema drift or missing optional-field handling can create async-only bugs. `addAllStorageIDs(storageIDs == null ? null : ...)` is sensitive to protobuf builder null handling. `getEnclosingRoot` assumes the response path is present. Raw `List.class`, `Map.class`, and `Token.class` return classes lose generic type checks. Tests should compare sync and async behavior for representative write, read, listing, security, snapshot, EC, xattr, and error cases, especially batched listings with embedded remote exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolServerSideTranslatorPB.java

Purpose: server-side protobuf adapter for `GetUserMappingsProtocol` on the Router, adding async Router RPC support to the standard tools translator.

Important APIs and types: constructor accepts `GetUserMappingsProtocol`, passes it to the parent, casts it to `RouterRpcServer`, and caches `server.isAsync()`. The sole override is `getGroupsForUser(RpcController, GetGroupsForUserRequestProto)`.

Control flow: non-async mode delegates to `super.getGroupsForUser`. Async mode schedules `server.getGroupsForUser(request.getUser())` through `asyncRouterServer`, converts returned group strings into `GetGroupsForUserResponseProto`, and returns `null` because completion is handled asynchronously.

State and persistence: no durable state. It only retains the Router RPC server and async flag. Group data comes from Router security/group mapping services.

Dependencies and integration points: integrates Hadoop tools group lookup protobuf protocol with `RouterRpcServer` and `AsyncRpcProtocolPBUtil.asyncRouterServer`. It pairs with `RouterGetUserMappingsProtocolTranslatorPB`.

Risks: the cast to `RouterRpcServer` assumes the implementation object is exactly the Router server. Async response completion relies on returning `null`; callers must be on the async-capable server path. Tests should cover sync fallback, async response content, empty group lists, and exception propagation from group mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolTranslatorPB.java

Purpose: client-side Router translator for `GetUserMappingsProtocol`, preserving normal protobuf behavior while using async IPC when the Hadoop IPC client is in asynchronous mode.

Important APIs and types: stores `GetUserMappingsProtocolPB rpcProxy` and overrides `getGroupsForUser(String)`.

Control flow: sync mode delegates to the standard client-side translator. Async mode builds `GetGroupsForUserRequestProto`, invokes `rpcProxy.getGroupsForUser(null, request)` via `asyncIpcClient`, and converts the response group list into a `String[]`.

State and persistence: no persisted state; the only field is the PB proxy. Runtime state is the requested user and response group list.

Dependencies and integration points: pairs with the Router server-side user-mapping translator and Hadoop tools protocol PB classes. It depends on `Client.isAsynchronousMode()` and `AsyncRpcProtocolPBUtil.asyncIpcClient` matching the async IPC contract.

Risks: group order and duplicates are passed through exactly as returned. Empty responses must produce an empty array. Tests should exercise sync parity and async group lookup with users that have zero, one, and multiple groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterGetUserMappingsProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolServerSideTranslatorPB.java

Purpose: Router server-side protobuf translator for `NamenodeProtocol`, adding async handling to checkpoint, block-key, block-report, edit-log, version, upgrade, and SPS protocol calls.

Important APIs and types: extends `NamenodeProtocolServerSideTranslatorPB`, stores a `RouterRpcServer`, and overrides methods such as `getBlocks`, `getBlockKeys`, `getTransactionId`, `getMostRecentCheckpointTxId`, `getMostRecentNameNodeFileTxId`, `rollEditLog`, `errorReport`, `registerSubordinateNamenode`, `startCheckpoint`, `endCheckpoint`, `getEditLogManifest`, `versionRequest`, `isUpgradeFinalized`, `isRollingUpgrade`, and `getNextSPSPath`.

Control flow: sync mode delegates to the parent translator. Async mode converts request protos into server domain types, calls the matching `RouterRpcServer` method inside `asyncRouterServer`, builds the response proto in the completion lambda, and returns `null`. Void operations use static empty response protos inherited from the parent.

State and persistence: the translator has only `server` and `isAsyncRpc`. Persistent side effects, such as checkpoints, edit-log rolling, registration, and SPS path updates, occur in the Router/NameNode protocol implementation and downstream NameNodes.

Dependencies and integration points: depends on `PBHelper`, `PBHelperClient`, generated `NamenodeProtocolProtos`, `HdfsServerProtos`, `NNStorage.NameNodeFile`, and Router async server completion. It pairs with `RouterNamenodeProtocolTranslatorPB`.

Risks: `NNStorage.NameNodeFile.valueOf(request.getNameNodeFile())` requires exact enum string compatibility. `getNextSPSPath` sets `spsPath` without a null guard, so null results would be unsafe in async mode. Returning `null` is correct only when the async RPC server infrastructure captures the response. Tests should compare sync and async outputs for optional block keys, checkpoint signatures, manifests, and null/absent SPS path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolTranslatorPB.java

Purpose: client-side Router translator for the HDFS `NamenodeProtocol`, adding async IPC while inheriting normal synchronous protobuf behavior.

Important APIs and types: extends `NamenodeProtocolTranslatorPB`, stores `NamenodeProtocolPB rpcProxy`, defines reusable empty request protos, and overrides name-node protocol calls for blocks, block keys, transaction IDs, checkpoints, edit manifests, registration, version requests, upgrade status, and SPS path retrieval.

Control flow: each method checks `Client.isAsynchronousMode()`. Sync mode calls the parent. Async mode builds the relevant request proto, invokes `rpcProxy` through `asyncIpcClient`, and converts the response with `PBHelper`/`PBHelperClient`. Optional responses are represented with `hasKeys()` and `hasSpsPath()`.

State and persistence: no local durable state. The translator carries only the RPC proxy and static immutable empty request protos. Protocol calls may mutate downstream NameNode state, for example rolling edit logs or ending checkpoints.

Dependencies and integration points: integrates the Router with HDFS server protocol protobufs, `ExportedBlockKeys`, `CheckpointSignature`, `NamenodeRegistration`, `NamespaceInfo`, `RemoteEditLogManifest`, and `NNStorage.NameNodeFile`. It must align with the server-side Router namenode translator.

Risks: async conversion must match the parent translator exactly, especially around nullable block keys and SPS paths. `nnf.toString()` must be accepted by the server-side `valueOf` conversion. Tests should verify async mode for each protocol family and that exceptions are propagated as `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterNamenodeProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterPolicyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterPolicyProvider.java

Purpose: RBF policy provider that extends HDFS service authorization with Router-specific protocol ACLs.

Important APIs and types: extends `HDFSPolicyProvider`; defines `RBF_SERVICES` with `CommonConfigurationKeys.SECURITY_ROUTER_ADMIN_PROTOCOL_ACL` mapped to `RouterAdminProtocol`; constructor merges `super.getServices()` with Router services; `getServices()` returns a defensive copy.

Control flow: construction eagerly builds the combined service array. Calls to `getServices()` do not expose the internal array.

State and persistence: holds an immutable-by-convention `Service[]` for process lifetime. Actual ACL values are read elsewhere from Hadoop configuration.

Dependencies and integration points: used by Hadoop service authorization to recognize Router admin protocol permissions alongside normal HDFS protocol permissions.

Risks: missing Router protocols here would bypass intended service-level ACL configuration. Duplicate or stale service entries can confuse authorization diagnostics. Tests should assert the provider includes all parent HDFS services plus the Router admin ACL service and that returned arrays are defensive copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolServerSideTranslatorPB.java

Purpose: Router server-side protobuf adapter for `RefreshUserMappingsProtocol`, with async support for refreshing user-group and superuser group mappings.

Important APIs and types: extends `RefreshUserMappingsProtocolServerSideTranslatorPB`, stores `RouterRpcServer`, caches `isAsyncRpc`, and defines empty response protos for both refresh operations.

Control flow: sync mode delegates to the parent. Async mode schedules either `server.refreshUserToGroupsMappings()` or `server.refreshSuperUserGroupsConfiguration()` through `asyncRouterServer`, maps completion to the prebuilt empty response, and returns `null`.

State and persistence: no local persisted state. The operations refresh in-memory security/group mapping caches in the Router process.

Dependencies and integration points: integrates Router RPC refresh handling with Hadoop security protobuf protocol classes and the async Router server utility. It pairs with `RouterRefreshUserMappingsProtocolTranslatorPB`.

Risks: refresh calls are operationally sensitive because stale groups affect authorization. The implementation assumes the passed protocol implementation is a `RouterRpcServer`. Tests should cover both refresh methods in sync and async mode and confirm exceptions are surfaced to clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolTranslatorPB.java

Purpose: client-side Router translator for the security refresh-user-mappings protocol, adding async IPC paths for administrative refresh operations.

Important APIs and types: extends `RefreshUserMappingsProtocolClientSideTranslatorPB`, stores `RefreshUserMappingsProtocolPB rpcProxy`, and overrides `refreshUserToGroupsMappings()` and `refreshSuperUserGroupsConfiguration()`.

Control flow: sync mode delegates to the standard translator. Async mode builds the corresponding empty request proto and uses `asyncIpcClient` to invoke the PB proxy; completion returns `null` for both void operations.

State and persistence: no local state beyond the proxy. Refresh effects happen in the remote Router service's caches.

Dependencies and integration points: pairs with the Router server-side refresh translator and Hadoop security protocol PB classes. It is used by admin clients when asynchronous IPC is enabled.

Risks: callers expect refresh completion or failure, so async error propagation must match the synchronous translator. Tests should verify both methods complete successfully and preserve exception behavior in async mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterRefreshUserMappingsProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/package-info.java

Purpose: package-level metadata for Router protobuf protocol implementations.

Important APIs and types: package annotation marks `org.apache.hadoop.hdfs.protocolPB` as `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`.

Control flow: no executable logic.

State and persistence: no state.

Dependencies and integration points: the documentation identifies this package as containing protobuf protocols related to HDFS Router, including Router admin, client, namenode, and refresh/user mapping translators.

Risks: annotation drift can mislead downstream users about API stability. Test signal is compilation and generated Javadocs/package metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/MountTableProcedure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/MountTableProcedure.java

Purpose: `BalanceProcedure` that updates a Router mount-table entry from the source namespace/path to the destination namespace/path after data movement, then makes the mount writable again.

Important APIs and types: fields `mount`, `dstPath`, `dstNs`, and `Configuration conf`; `execute()`, `updateMountTableDestination`, `getMountEntry`, `disableWrite`, `enableWrite`, `setMountReadOnly`, Writable `write/readFields`, and testing getters.

Control flow: `execute()` calls `updateMountTable()`, which updates the mount destination and calls `enableWrite`. Admin communication uses `DFS_ROUTER_ADMIN_ADDRESS_KEY`, `NetUtils.createSocketAddr`, `RouterClient`, and `MountTableManager`. `getMountEntry` fetches entries under a source path and picks the exact `sourcePath` match. Updates mutate the existing `MountTable`, submit `UpdateMountTableEntryRequest`, require a true response status, and refresh mount-table entries.

State and persistence: procedure state is serialized through `DataOutput` with `Text.writeString` and `Configuration.write`, allowing scheduler recovery. Persistent cluster state is the Router State Store mount-table record: destinations and readonly flag.

Dependencies and integration points: part of the fedbalance job pipeline created by `RouterFedBalance`. It integrates with Router admin RPC, state-store mount-table records, and `RouterDistCpProcedure` readonly control.

Risks: the procedure overwrites destinations with a single `RemoteLocation`, so multi-destination mounts are not preserved. Mutating the fetched `MountTable` in place assumes update semantics accept the modified object. If refresh fails or stale routers exist, clients may see old routing. Tests should cover missing mount errors, readonly toggling, serialization round trip, exact path matching, and successful refresh after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/MountTableProcedure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterDistCpProcedure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterDistCpProcedure.java

Purpose: Router-specific `DistCpProcedure` that freezes writes through mount-table readonly state before the final DistCp phase.

Important APIs and types: constructors mirror the parent, `disableWrite(FedBalanceContext)`, and `enableWrite()`.

Control flow: when the parent DistCp workflow asks to disable writes, this procedure reads `conf` and `mount` from `FedBalanceContext`, calls `MountTableProcedure.disableWrite`, and advances its stage to `Stage.FINAL_DISTCP`. `enableWrite()` intentionally does nothing because write re-enablement happens after the mount-table switch in `MountTableProcedure`.

State and persistence: inherits DistCp procedure state. It updates persistent Router mount-table readonly state through `MountTableProcedure`.

Dependencies and integration points: used as the first procedure in `RouterFedBalance` jobs. It depends on fedbalance `DistCpProcedure` stage semantics and Router mount-table admin RPC.

Risks: if later procedures fail, the mount can remain readonly until recovery or manual intervention. The no-op `enableWrite` is intentional but makes procedure ordering critical. Tests should verify stage transitions, readonly state changes, and recovery behavior after failures between DistCp and mount update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterDistCpProcedure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterFedBalance.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterFedBalance.java

Purpose: command-line tool for balancing data across Router-Based Federation namespaces by running DistCp, switching the mount-table destination, and then trashing/deleting/skipping source cleanup.

Important APIs and types: extends `Configured` and implements `Tool`; commands `submit` and `continue`; inner `Builder`; `run`, `submit`, `continueJob`, `getSrcPath`, `printUsage`, `getDefaultConf`, and `main`. It uses `FedBalanceContext`, `BalanceJob`, `BalanceProcedureScheduler`, `RouterDistCpProcedure`, `MountTableProcedure`, `TrashProcedure`, and shared fedbalance CLI options.

Control flow: `run` parses CLI options and dispatches to submit or continue. `submit` parses map count, bandwidth, delay, diff threshold, force-close-open, and trash behavior, builds a three-procedure job, submits it to a scheduler, and waits for completion. `continueJob` initializes the scheduler in recovery mode and loops until all jobs report done. `Builder.build` resolves the source mount to an HDFS URI through Router admin APIs, validates the destination has an authority, creates the context with readonly mount handling, then chains DistCp, mount update, and trash procedures.

State and persistence: persistent state is held by `BalanceProcedureScheduler` and serialized procedure contexts. Cluster state changes include copied data, mount-table destination/readonly updates, and source trash/delete behavior.

Dependencies and integration points: integrates Hadoop ToolRunner, fedbalance configuration resources, Router admin address config, mount-table manager, DistCp-based migration, and fedbalance recovery.

Risks: CLI parsing accepts numeric options without range validation beyond downstream behavior. `continueJob` polls forever until jobs complete. `getSrcPath` only supports mounts with exactly one destination. A failed mount-table update or trash step can leave data duplicated or mount readonly. Tests should cover argument validation, destination authority requirement, single-destination source resolution, procedure ordering, scheduler recovery, and trash option parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterFedBalance.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/package-info.java

Purpose: package metadata for the RBF fedbalance tool.

Important APIs and types: marks `org.apache.hadoop.hdfs.rbfbalance` as `@InterfaceAudience.Public` and documents FedBalance as a tool for balancing data across federation clusters.

Control flow: no executable logic.

State and persistence: no state.

Dependencies and integration points: applies to `RouterFedBalance`, `RouterDistCpProcedure`, and `MountTableProcedure`, indicating this package is intended for public tool-facing use.

Risks: public audience annotation makes API churn more visible. Test signal is package compilation and documentation generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/AbstractRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/AbstractRouterRpcFairnessPolicyController.java

Purpose: base semaphore-backed implementation of Router RPC fairness permits by nameservice.

Important APIs and types: implements `RouterRpcFairnessPolicyController`; fields `Map<String, Semaphore> permits` and `acquireTimeoutMs`; methods `init`, `acquirePermit`, `releasePermit`, `shutdown`, `insertNameServiceWithPermits`, `getAvailablePermits`, `getAvailableHandlerOnPerNs`, and `contains`.

Control flow: `init` creates the permit map and reads `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, falling back on invalid negative values. `acquirePermit` performs timed `Semaphore.tryAcquire`. `releasePermit` releases one permit. `shutdown` drains all semaphores. JSON reporting iterates permits and writes available counts with Jettison.

State and persistence: all state is in-memory semaphore counts. There is no persistence across Router restart; policy subclasses reconstruct permits from configuration.

Dependencies and integration points: used by static, proportional, and async fairness policies. Integrated with Router RPC client admission control and metrics/JMX available-handler reporting.

Risks: no null checks around `permits.get(nsId)` mean unknown nameservices cause `NullPointerException` unless subclasses handle them. Release without a matching acquire can over-increment permits. Tests should verify timeout behavior, shutdown drain, JSON output, invalid timeout config, and release/acquire balance under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/AbstractRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/NoRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/NoRouterRpcFairnessPolicyController.java

Purpose: pass-through fairness policy that disables admission limiting.

Important APIs and types: implements `RouterRpcFairnessPolicyController`; constructor accepts `Configuration` only for reflection/configuration compatibility.

Control flow: `acquirePermit` always returns true; `releasePermit` and `shutdown` do nothing; reporting returns `"N/A"`, `0` permits, and `contains` always true.

State and persistence: no state.

Dependencies and integration points: selected when Router fairness should not limit downstream namespace calls, while still satisfying the controller interface used by RPC client and metrics.

Risks: metrics can show zero available permits while all calls are allowed, which must be understood by operators. Tests should verify it is safe for arbitrary ns IDs and does not throw on release or shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/NoRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/ProportionRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/ProportionRouterRpcFairnessPolicyController.java

Purpose: fairness policy assigning per-nameservice permits as a configured proportion of the Router handler count.

Important APIs and types: extends the abstract semaphore controller; uses `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`, default proportion config, `FederationUtil.getAllConfiguredNS`, special `CONCURRENT_NS`, and internal `DEFAULT_NS`.

Control flow: initialization gathers configured nameservices, adds concurrent and default namespaces, calculates `int(proportion * handlerCount)`, enforces at least one permit per entry, and inserts semaphores. `acquirePermit` and `releasePermit` route unknown namespaces to `DEFAULT_NS`.

State and persistence: in-memory semaphore counts derived from static configuration at initialization. No runtime persistence.

Dependencies and integration points: supports clusters where new or unregistered namespaces should share default permits instead of failing. Exposed through Router RPC fairness metrics.

Risks: proportions are not normalized, so total allocated permits can exceed handler count. Truncation can under-allocate small proportions, then the minimum-one rule can over-allocate. Tests should cover unknown namespaces, default fallback release symmetry, zero/negative proportions, and aggregate allocation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/ProportionRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RefreshFairnessPolicyControllerHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RefreshFairnessPolicyControllerHandler.java

Purpose: Hadoop refresh handler that triggers Router fairness policy controller refresh by identifier.

Important APIs and types: implements `RefreshHandler`; constant `HANDLER_IDENTIFIER = "RefreshFairnessPolicyController"`; stores `Router`.

Control flow: `handleRefresh` checks the supplied identifier. A match calls `router.getRpcServer().refreshFairnessPolicyController()` and returns a successful `RefreshResponse`; any other identifier returns code `-1` and `"Failed"`.

State and persistence: no state beyond the Router reference. Refreshing may replace or reinitialize the Router RPC fairness controller from current configuration.

Dependencies and integration points: integrates with Hadoop refresh command infrastructure and Router RPC server management.

Risks: no argument validation is needed, but a null router or unavailable RPC server would fail at refresh time. Tests should cover identifier matching, nonmatching identifiers, and that the response message is the RPC server refresh result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RefreshFairnessPolicyControllerHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterAsyncRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterAsyncRpcFairnessPolicyController.java

Purpose: async-RPC-oriented fairness policy that limits outstanding async calls per configured nameservice.

Important APIs and types: extends the abstract semaphore controller; reads `DFS_ROUTER_ASYNC_RPC_MAX_ASYNCCALL_PERMIT_KEY`; uses configured nameservices plus `CONCURRENT_NS`; overrides `acquirePermit` and `releasePermit`.

Control flow: initialization validates the max-permit value, falling back to default when nonpositive, then inserts that permit count for every configured namespace and for the concurrent namespace. `CONCURRENT_NS` acquire/release is a no-op allowed path; all other namespaces use normal semaphore acquisition.

State and persistence: in-memory semaphore permits only. Counts are reconstructed from configuration on controller creation/refresh.

Dependencies and integration points: recommended when Router async RPC is enabled and consumed by Router RPC client permit checks plus metrics reporting.

Risks: unknown non-concurrent nameservices are not handled and can NPE in the base class. Concurrent fan-out calls bypass permit limiting by design. Tests should cover invalid permit config, configured namespaces, concurrent namespace bypass, and missing namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterAsyncRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessConstants.java

Purpose: constants holder for Router RPC fairness.

Important APIs and types: exposes `CONCURRENT_NS = "concurrent"` and has a protected hidden constructor.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies and integration points: `CONCURRENT_NS` is shared by static, proportional, and async policies to represent fan-out/concurrent Router calls.

Risks: string changes would break configuration, metrics, and policy special cases. Tests indirectly verify this through fairness policy allocation and metrics keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessPolicyController.java

Purpose: policy interface for Router RPC downstream nameservice admission control.

Important APIs and types: declares `acquirePermit`, `releasePermit`, `shutdown`, `getAvailableHandlerOnPerNs`, `getAvailablePermits`, and `contains`.

Control flow: implementations decide whether a Router handler may proceed to a downstream NameNode for a namespace. Callers are expected to acquire before proxying and release afterward.

State and persistence: interface has no state. Implementations may keep in-memory semaphores or be pass-through.

Dependencies and integration points: used by Router RPC client code and exposed in JMX/RPC metrics for available handler and permit rejection/acceptance reporting.

Risks: the contract relies on balanced acquire/release calls and consistent namespace IDs. Tests for implementations should include success, rejection, unknown namespace, shutdown, and metrics-reporting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/StaticRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/StaticRouterRpcFairnessPolicyController.java

Purpose: static fairness policy that assigns fixed handler permits per nameservice from configuration and divides remaining handlers equally.

Important APIs and types: extends abstract semaphore controller; reads `DFS_ROUTER_HANDLER_COUNT_KEY` and `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`; uses `FederationUtil.getAllConfiguredNS` and `CONCURRENT_NS`; exposes `ERROR_MSG` for insufficient handler allocation.

Control flow: initialization gets total handler count, adds concurrent namespace, validates that dedicated counts plus one minimum for unassigned namespaces fit within total handlers, inserts dedicated permits, divides remaining permits among unassigned namespaces, and assigns leftovers to `CONCURRENT_NS`.

State and persistence: in-memory semaphore counts derived from configuration. The assignment is static until controller refresh/restart.

Dependencies and integration points: used by Router RPC fairness admission control when operators want predictable per-namespace handler pools.

Risks: unknown nameservices are not supported by the base class. If `CONCURRENT_NS` receives dedicated permits and leftovers, it is reinserted with a combined permit count. Integer division can allocate zero only after validation prevents impossible minimums. Tests should verify validation failures, dedicated counts, equal split, leftover assignment, and available-permit metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/StaticRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/package-info.java

Purpose: package metadata for Router RPC fairness controllers.

Important APIs and types: marks `org.apache.hadoop.hdfs.server.federation.fairness` as private and evolving.

Control flow: no executable logic.

State and persistence: no state.

Dependencies and integration points: describes the package as containing Router handler fairness manager and policy implementations used by Router RPC.

Risks: package annotations communicate stability expectations. Test signal is compilation and package documentation generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationMBean.java

Purpose: JMX contract for federation-wide Router metrics and status.

Important APIs and types: private evolving interface exposing JSON views for namenodes, nameservices, mount table, routers, capacities as `long` and `BigInteger`, datanode counts, block/file counts, Router identity/status/security, corrupt files, low redundancy, scheduled replication, and SPS paths.

Control flow: no implementation; consumers call getters through JMX or metrics code.

State and persistence: interface has no state. Implementations aggregate state from Router, State Store, membership records, and downstream NameNodes.

Dependencies and integration points: implemented by RBF metrics classes and consumed by operators, tests, JMX clients, and compatibility code that expects NameNode-like metrics on the Router.

Risks: method names are a compatibility surface. Deprecated Router identity methods remain for older clients. Large capacities can overflow `long`, hence BigInteger alternatives. Tests should validate implementation JSON shape and capacity aggregation, including overflow-safe methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMBean.java

Purpose: JMX interface for Router RPC server/client activity.

Important APIs and types: exposes proxy/processing operation counts and averages, active/observer proxy counts, failure counters, retry counters, Router failure counters, RPC server queue/connections, RPC client connection-pool stats, JSON connection details, per-namespace available handlers, async caller pool JSON, and permit rejection/acceptance metrics.

Control flow: no implementation.

State and persistence: no state in the interface. Implementations read mutable metrics counters and live RPC server/client state.

Dependencies and integration points: implemented by `FederationRPCMetrics` and registered by `FederationRPCPerformanceMonitor` as a StandardMBean.

Risks: values mix counters, gauges, averages, and JSON strings, so clients must interpret each correctly. Tests should assert getter values after simulated monitor events and verify JSON-producing methods tolerate missing RPC client internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMetrics.java

Purpose: metrics2/JMX implementation for Router RPC activity.

Important APIs and types: annotated `@Metrics(name = "RouterRPCActivity")`; stores `RouterRpcServer`; maintains `MutableRate` metrics for processing/proxy time and `MutableCounterLong` counters for proxy ops, active/observer ops, failures, retries, Router failures, and permit rejection. Static `create` registers with `DefaultMetricsSystem`; `reset` unregisters.

Control flow: increment methods update counters. `addProxyTime` records proxy latency, increments active or observer counters based on `FederationNamenodeServiceState`, then increments total proxy ops. `addProcessingTime` records Router internal processing latency. Gauge getters query live server/client state such as call queue, open connections, connection pools, fairness controller JSON, and async caller pool JSON.

State and persistence: metrics are in-memory process counters/rates registered with metrics2 and JMX. They reset on process restart or explicit reset.

Dependencies and integration points: created by `FederationRPCPerformanceMonitor`, exposed through `FederationRPCMBean`, and depends on `RouterRpcServer`, RPC client internals, and fairness controller metrics.

Risks: gauge getters can throw if `rpcServer`, `getServer()`, `getRPCClient()`, or fairness controller is unavailable. `lastStat().mean()` depends on metrics2 snapshot state. Tests should drive monitor events and verify counters, active/observer split, permit metrics JSON, and registration/unregistration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCPerformanceMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCPerformanceMonitor.java

Purpose: `RouterRpcMonitor` implementation that records Router RPC processing/proxy timings, per-nameservice metrics, failure counters, and registers the Federation RPC JMX bean.

Important APIs and types: thread locals `START_TIME` and `PROXY_TIME`; fields for `Configuration`, `RouterRpcServer`, `StateStoreService`, `FederationRPCMetrics`, per-nameservice `NameserviceRPCMetrics`, JMX `ObjectName`, and executor; methods `init`, `close`, `resetPerfCounters`, `startOp`, `proxyOp`, `proxyOpComplete`, failure callbacks, permit callbacks, and `getRPCMetrics`.

Control flow: `init` creates global metrics, creates nameservice metrics for all configured namespaces plus `"concurrent"`, creates a one-thread executor, and registers a `FederationRPCMBean`. `startOp` records receive time; `proxyOp` records proxy-start time and adds processing time; `proxyOpComplete` records proxy latency on success, excluding concurrent namespace from global proxy metrics but including matching per-namespace metrics. Failure callbacks increment global and, where available, per-namespace counters.

State and persistence: metrics and thread-local timestamps are in-memory only. JMX registration lives until `close` or reset. The executor currently exists for stats logging capacity but is not used by the shown code.

Dependencies and integration points: consumed by Router RPC server instrumentation. It integrates with `FederationRPCMetrics`, `NameserviceRPCMetrics`, `DefaultMetricsSystem`, MBeans, configured nameservices, and Router RPC monitor callbacks.

Risks: thread locals must be set in the correct order; missing `startOp` or `proxyOp` yields skipped latency. Dynamic nameservices created after init are not in the per-namespace map. `close` unregisters only the MBean and shuts down executor; nameservice metrics are not explicitly unregistered here. Tests should verify timing callbacks, concurrent namespace treatment, reset behavior, JMX registration, and failures for unknown namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/FederationRPCPerformanceMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NamenodeBeanMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NamenodeBeanMetrics.java

Purpose: exposes Router federation metrics through NameNode-compatible JMX interfaces so existing HDFS monitoring can treat the Router as a logical NameNode.

Important APIs and types: implements `FSNamesystemMBean`, `NameNodeMXBean`, and `NameNodeStatusMXBean`; registers FSNamesystem, FSNamesystemState, NameNodeInfo, and NameNodeStatus MBeans; uses `RBFMetrics`, `RouterClientProtocol`, `StateStoreService`, `MembershipStore`, `LoadingCache<DatanodeReportType,String>`, and Jetty JSON serialization.

Control flow: constructor registers MBeans and creates a datanode-report cache with configured timeout/expiry. Many getters delegate to `router.getMetrics()` with defensive logging and default zero/empty values on failure. `getNodes` reads cached JSON; cache loading calls Router client protocol `getDatanodeStorageReport`, waits through `syncReturn` in async mode, and serializes datanode/storage details. Namespace info getters query the membership store and collect unique cluster/block-pool IDs. Status methods return Router-derived host/port, start time, security, active state, and many unsupported NameNode fields as `"N/A"`, `null`, zero, or `-1`.

State and persistence: in-memory MBean registrations and datanode JSON cache. It does not persist metrics; it reflects Router, State Store, and downstream NameNode state at query/cache-load time.

Dependencies and integration points: bridges RBF metrics to Hadoop NameNode monitoring APIs and JMX clients. It depends on Router RPC server, RBF metrics initialization, State Store membership records, and downstream datanode reports.

Risks: `close` unregisters FSNamesystemState, NameNodeInfo, and NameNodeStatus but not the `fsBeanName`, which may leak a registration. Some NameNode fields are placeholders and can mislead generic dashboards. Datanode report collection can be expensive or timeout, so cache settings are important. Tests should verify MBean registration/close behavior, delegation to `RBFMetrics`, JSON node output, async datanode report handling, and fallback values on missing metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NamenodeBeanMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMBean.java

Purpose: JMX interface for per-nameservice Router RPC proxy metrics.

Important APIs and types: exposes proxy operation count/average and counters for communicate failures, standby failures, no-namenode failures, permit rejections, and permit acceptances.

Control flow: no implementation; metrics classes implement these getters.

State and persistence: no interface state.

Dependencies and integration points: implemented by `NameserviceRPCMetrics` and created by `FederationRPCPerformanceMonitor` for each configured namespace and the concurrent namespace.

Risks: per-namespace metrics only exist for nameservices known at monitor initialization. Tests should assert each getter reflects the corresponding counter in `NameserviceRPCMetrics`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMetrics.java

Purpose: metrics2 implementation for RPC activity scoped to a single nameservice.

Important APIs and types: annotated `@Metrics(name = "NameserviceRPCActivity")`; constant prefix `NameserviceActivity-`; fields `nsId`, `MetricsRegistry`, `MutableRate proxy`, and counters for proxy ops, failures, permit rejected, and permit accepted. Static `create` registers a metrics source, using a random undefined suffix for empty nameservice names.

Control flow: increment methods update specific counters. `addProxyTime` records proxy latency and increments proxy-op count. Getter methods expose counts and last proxy average. `getNsId` returns the registered prefixed ID.

State and persistence: in-memory metrics source registered with `DefaultMetricsSystem`. State resets when unregistered or process restarts.

Dependencies and integration points: created by `FederationRPCPerformanceMonitor` and exposed through `NameserviceRPCMBean`; used for per-namespace visibility distinct from aggregate `FederationRPCMetrics`.

Risks: empty nameservice IDs create random metric names, which can make tests and dashboards unstable. No reset/unregister method is defined in this class. Tests should verify registration naming, counter increments, proxy average updates, and permit accepted/rejected counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NameserviceRPCMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NullStateStoreMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NullStateStoreMetrics.java

Purpose: no-op `StateStoreMetrics` implementation used when state-store metrics are disabled, especially in tests.

Important APIs and types: extends `StateStoreMetrics` and overrides read/write/failure/remove metric update and getter methods, cache size, reset, and shutdown.

Control flow: update methods do nothing; operation count and average getters return `-1`; cache/reset/shutdown methods are no-ops.

State and persistence: no state and no metrics registration.

Dependencies and integration points: lets code depend on a `StateStoreMetrics` instance without checking for null when metrics collection is disabled.

Risks: returning `-1` is a sentinel and must not be treated as a real metric. Tests should verify callers tolerate disabled metrics and do not publish negative values as normal operational data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NullStateStoreMetrics.java -->
