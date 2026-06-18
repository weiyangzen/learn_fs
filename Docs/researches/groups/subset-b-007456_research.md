# subset-b-007456 Research

Grouped research for Hadoop HDFS Router-Based Federation test sources. Each section preserves the original source path and is intended to be split into the mirrored per-file `Docs/researches/<source>_research.md` output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterTrash.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterTrash.java

Purpose: verifies Router trash behavior across RBF mount tables, including user-specific trash paths, Kerberos-style short usernames, multiple mounted namespaces, explicit trash-root mounts, and the `MountTableResolver` helpers that recognize and strip trash prefixes.

Important APIs/types/functions: `StateStoreDFSCluster`, `MiniRouterDFSCluster.RouterContext`, `RouterClient`, `MountTableManager`, `MountTableResolver`, `MountTable`, `DFSClient`, `Trash`, `DFSTestUtil.getFileSystemAs`, `UserGroupInformation`, `FsPermission`, `FileSystem`, `Time`, `MountTableResolver.isTrashPath`, and `MountTableResolver.subtractTrashCurrentPath`. `globalSetUp()` starts two nameservices with state store/admin/rpc/http router services and enables trash. `addMountTable()` adds an entry through admin RPC and reloads the resolver cache.

Control flow: tests create mount entries, set NN root ownership, create files as a remote user, delete through the router-backed `Trash`, then inspect the physical namespace to ensure data lands under `/user/<shortUser>/.Trash/Current`. Duplicate trash targets are expected to coexist by generating a suffixed target. Multi-mount coverage checks that the logical trash view spans mounted destinations and that empty mounted trash subdirectories list as empty instead of throwing.

State and persistence behavior: mount-table rows are written into the state store and reloaded into router cache; file/trash state persists on individual namenode file systems until `@AfterEach` removes mount entries and clears NN root children. Risks include shared static cluster state, order-sensitive cleanup, short-user-name handling for Kerberos principals, and assumptions about trash path syntax. Test signals cover successful trash moves, duplicate-name handling, multi-namespace listing, explicit trash mount behavior, and resolver helper edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterTrash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterUserMappings.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterUserMappings.java

Purpose: tests router-side propagation of user/group mapping refresh and proxy-superuser authorization refresh commands when clients address multiple routers through an HA-style federated namespace.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterConfigBuilder`, `DFSAdmin`, `GetGroups`, `Groups`, `ProxyUsers`, `DefaultImpersonationProvider`, `ConfiguredFailoverProxyProvider`, `NameNodeProxies`, `GetUserMappingsProtocol`, and the nested `MockUnixGroupsMapping`. `setUp()` installs the mock group mapping provider and a short group cache. `setUpMultiRoutersAndReturnDefaultFs()` starts a two-nameservice, multi-router cluster and builds a synthetic `router_ns` namespace with router RPC addresses.

Control flow: `testRefreshSuperUserGroupsConfiguration()` configures proxy-user group/host rules, proves one proxied user is denied and another allowed, writes a temporary default XML resource with changed proxy groups, runs `dfsadmin -refreshSuperUserGroupsConfiguration`, then verifies the allow/deny behavior flips. `testGroupMappingRefresh()` confirms cached groups are stable before refresh, invokes `dfsadmin -refreshUserToGroupsMappings`, and waits until the mock provider produces different groups after refresh/cache timeout.

State and persistence behavior: mutable global Hadoop configuration resources, `Groups` cache, proxy-user static state, and router processes are all involved. The temporary XML file is added to default resources and deleted in teardown. Integration points include command-line admin, protocol-level group lookups, router HA client configuration, and impersonation authorization. Risks are classpath resource leakage, static cache contamination between tests, and timing-sensitive cache expiry. Test signals include CLI output, protocol group arrays, authorization exceptions, and cache-refresh polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterUserMappings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWebHdfsMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWebHdfsMethods.java

Purpose: validates WebHDFS create handling through the Router, namespace selection from mount tables, datanode network-location namespace parsing, and invalid path error conversion.

Important APIs/types/functions: `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterContext`, `RouterWebHdfsMethods`, `WebHdfsFileSystem.jsonParse`, `DestinationOrder`, `FederationTestUtils.createMountTableEntry`, `HttpURLConnection`, `FileSystem`, and `Path`. `globalSetUp()` starts a two-nameservice state-store cluster with RPC, HTTP, and admin services and records the router HTTP URI.

Control flow: `testWebHdfsCreate()` sends an HTTP `PUT` to `/webhdfs/v1/tmp/file?op=CREATE&user.name=<user>` and expects HTTP 201, then checks the file exists only in the default `ns0`. `testWebHdfsCreateWithMounts()` installs a mount point to `ns1`, creates through WebHDFS, and verifies placement only in `ns1`. `testGetNsFromDataNodeNetworkLocation()` checks namespace extraction from rack paths. `testWebHdfsCreateWithInvalidPath()` sends duplicated slashes and expects HTTP 400 with `InvalidPathException` in the parsed JSON response.

State and persistence behavior: mount-table state affects HTTP routing and physical NN file creation. The suite relies on the shared cluster shutdown for cleanup. Dependencies include router HTTP endpoints, WebHDFS request parsing, mount resolution, and namenode file status checks. Risks include real socket timing, local username query parameters, and state leakage from created files or mount entries. Test signals are HTTP response codes, parsed remote exception class names, and per-namespace file existence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWebHdfsMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWithSecureStartup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWithSecureStartup.java

Purpose: covers secure Router startup validation for Kerberos/SPNEGO-related configuration in the Router WebHDFS contract.

Important APIs/types/functions: `SecurityConfUtil.initSecurity`, `RouterWebHDFSContract.createCluster`, `RouterWebHDFSContract.getCluster`, `DFS_ROUTER_KEYTAB_FILE_KEY`, and the HTTP auth principal key `hadoop.http.authentication.kerberos.principal`. The helper `testCluster()` removes a required key and expects cluster creation to fail with `IOException`.

Control flow: `testStartupWithoutSpnegoPrincipal()` unsets the SPNEGO principal and expects startup to still succeed because the HTTP auth principal has a default. `testStartupWithoutKeytab()` removes the router keytab file key and asserts secure mode fails. `testSuccessfulStartup()` uses the full security configuration and expects a cluster object.

State and persistence behavior: no custom persistence is added by this class; cluster lifecycle is delegated to `RouterWebHDFSContract`. Integration points are secure Hadoop configuration, Router startup, keytab validation, and WebHDFS contract utilities. Risks include shared static contract cluster state and brittle assertion messages if startup validation text changes. Test signals are successful cluster creation for valid/defaulted configs and `IOException` for missing keytab.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWithSecureStartup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestSafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestSafeMode.java

Purpose: sanity-checks that router client protocol calls can proxy HDFS safe-mode operations to registered active namenodes in an HA federated cluster.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterContext`, `ClientProtocol`, `SafeModeAction`, and `FederationTestUtils.NAMENODES`. `setup()` starts a two-nameservice HA cluster, starts routers, registers namenodes, installs mock locations, transitions `nn0` active and `nn1` standby for each namespace, and waits for active namespace visibility.

Control flow: `testProxySetSafemode()` obtains the router-facing `ClientProtocol` from a random router and calls `setSafeMode(SAFEMODE_GET, true)` and `setSafeMode(SAFEMODE_GET, false)`. Although the method name references set, `SAFEMODE_GET` exercises proxying of safe-mode query actions through the router.

State and persistence behavior: cluster routing state includes mock location mappings and namenode HA state, but the test does not mutate files or long-lived state. Teardown shuts down the entire mini cluster. Dependencies include router RPC startup, namenode registration, HA transitions, and client protocol forwarding. Risks are minimal beyond cluster startup flakiness; assertions are implicit because the test fails on thrown exceptions. Test signal is successful completion of both safe-mode proxy calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncProtocolTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncProtocolTestBase.java

Purpose: shared fixture for async Router protocol module tests. It creates a small HA federated cluster and supplies both the normal `RouterRpcServer` and a Mockito-spied async variant backed by `RouterAsyncRpcClient`.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterConfigBuilder`, `RouterRpcServer`, `RouterAsyncRpcClient`, `MockResolver`, `CallerContext`, `FsPermission`, and async config keys `DFS_ROUTER_ASYNC_RPC_HANDLER_COUNT_KEY` and `DFS_ROUTER_ASYNC_RPC_RESPONDER_COUNT_KEY`. Static getters expose router configuration, cluster, and nameservice id; instance getters expose router context, filesystem, and RPC servers.

Control flow: `setUpCluster()` starts one nameservice with two HA NNs and three DNs, makes `nn0` active, enables router RPC, constrains client/async handler/responder threads to one, reduces DN report cache expiry, starts routers, registers NNs, and waits for active namespaces. `setUp()` obtains a router, initializes async thread pools, creates an async client, spies the RPC server so `getRPCClient()` returns the async client and `isAsync()` returns true, maps `/` to the active namespace, and creates `/testdir`. `tearDown()` clears `CallerContext`, deletes `/testdir`, and closes the router FS.

State and persistence behavior: tests inherit filesystem state under `/testdir`, resolver mappings, thread pools, and async call context. Risks include static cluster sharing, single-thread timing sensitivity, and async thread-pool cleanup. Test signal is mostly indirect: subclasses depend on the fixture to produce comparable sync/async protocol behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/RouterAsyncProtocolTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestAsyncRouterAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestAsyncRouterAdmin.java

Purpose: async-enabled version of `TestRouterAdmin`, proving admin mount checks and inherited router-admin behavior work when async RPC is enabled.

Important APIs/types/functions: extends `TestRouterAdmin`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `ActiveNamenodeResolver`, `RouterRpcServer`, `RemoteMethod`, `RemoteLocation`, `HdfsFileStatus`, `AsyncUtil`, Mockito spies, and reflection via inherited `setField`. Config enables state store, admin, RPC, mount-checking, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`.

Control flow: `globalSetUp()` starts a one-nameservice state-store cluster with async RPC and admin mount checks. It registers synthetic active `ns0` and `ns1` namenode reports, refreshes state-store caches, and calls `setUpMocks()`. `setUpMocks()` replaces the router RPC server with a spy, stubs `getFileInfo`, replaces the RPC client with a spy, and prepares mocked async responses for destination checks against remote locations.

State and persistence behavior: the test mutates router internals through reflection and state-store/membership records; inherited admin tests operate on the static fields initialized here. Integration points include mount-table admin validation, async client response handling, namenode membership, and state-store cache refresh. Risks include tight coupling to private field names and inherited tests relying on static state. Test signals are inherited from `TestRouterAdmin`, with this class specifically ensuring they execute under async RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestAsyncRouterAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncCacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncCacheAdmin.java

Purpose: validates async cache administration operations through `RouterAsyncCacheAdmin` against the shared async protocol fixture.

Important APIs/types/functions: `RouterAsyncCacheAdmin`, `CachePoolInfo`, `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CachePoolEntry`, `CacheFlag`, `BatchedEntries`, `FSDataOutputStream`, `Path`, and `AsyncUtil.syncReturn`. The test creates a file under `/testdir` and exercises add/list/modify/remove cache pool and directive operations.

Control flow: setup builds `RouterAsyncCacheAdmin` from the async RPC server and writes a test file. The test creates a cache pool, lists pools to verify it appears, adds a cache directive for the test path, lists directives, modifies directive metadata, removes the directive, and removes the pool. Each async call is followed by `syncReturn` to materialize the result or propagate failures.

State and persistence behavior: cache pools and directives are persisted in the target namenode namespace for the duration of the test; `/testdir` is deleted by the base teardown. Dependencies include cache admin protocol support, path resolution through `MockResolver`, and async return context. Risks include requiring cache-admin support in the mini cluster and relying on singleton async context ordering. Test signals are returned IDs, batch entries, and successful removal without exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncCacheAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncClientProtocol.java

Purpose: compares selected async client-protocol methods with the synchronous `RouterClientProtocol` behavior.

Important APIs/types/functions: `RouterAsyncClientProtocol`, `RouterClientProtocol`, `FsServerDefaults`, `HdfsFileStatus`, `LocatedBlocks`, `AsyncUtil.syncReturn`, and the shared `RouterAsyncProtocolTestBase`. Setup instantiates async and sync protocol modules from the async and normal RPC servers.

Control flow: `testGetServerDefaults()` calls async `getServerDefaults`, materializes `FsServerDefaults`, then compares fields against the synchronous module result. `testClientProtocolRpc()` exercises common file-status/block-location style calls through the async module and compares returned metadata with synchronous router protocol results for paths created by the base fixture.

State and persistence behavior: depends on `/testdir` and any test file created in setup; no independent persistent state beyond base fixture cleanup. Integration points include Router async client protocol wrappers, synchronous protocol parity, path resolution, and async context retrieval. Risks include incomplete comparison if new fields are added to HDFS protocol objects and brittle async global state. Test signals are matching server defaults, non-null file metadata, and equal file/block information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncErasureCoding.java

Purpose: exercises `AsyncErasureCoding` router wrappers for policy assignment, policy/codecs retrieval, adding a new EC policy, and topology verification.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterAsyncRpcClient`, `AsyncErasureCoding`, `StripedFileTestUtil`, `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, `AddErasureCodingPolicyResponse`, `ECTopologyVerifierResult`, `ECSchema`, `HdfsFileStatus`, `MockResolver`, and `syncReturn`. The cluster has one HA nameservice, three DNs, and rack placement to support EC checks.

Control flow: setup creates `/testdir/testAsyncErasureCoding.file`, wires a spy RPC server to an async client, and maps `/` to `ns0`. The test sets the default EC policy on `/testdir`, fetches it back, compares all policy and codec listings with direct NN client results, adds an `RS-12-4-1024k` policy, verifies policy count increases, and checks topology support for both supported and unsupported policy sets.

State and persistence behavior: EC policy state is persisted in the namenode and file/directory state is cleaned per test. Dependencies include HDFS EC configuration, datanode/rack topology, async RPC, and direct NN client comparison. Risks include EC policy global state across tests, topology assumptions tied to DN count, and async context ordering. Test signals include policy names, full policy arrays, codec maps, add-policy success, and topology support booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncErasureCoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncFederationRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncFederationRename.java

Purpose: async variant of federation rename tests, verifying router rename semantics across namespaces when async RPC is enabled.

Important APIs/types/functions: extends `TestRouterFederationRename`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`. The class reuses inherited cluster fields, setup helpers, and rename assertions while changing the router configuration to async RPC.

Control flow: `globalSetUp()` builds a state-store cluster with router RPC/admin/state-store behavior and async RPC enabled. Inherited per-test setup installs mount entries and creates source/destination filesystem state. The overridden async tests run the same rename cases as the synchronous superclass, including cases where rename crosses federation boundaries and must coordinate physical namespace operations.

State and persistence behavior: state-store mount entries and physical HDFS paths are the key state; inherited teardown clears the test environment. Integration points include mount resolution, router client protocol rename implementation, async invocation of underlying namenodes, and failure cleanup across destinations. Risks are inherited-test coupling and subtle cross-namespace partial-rename failure modes. Test signals are inherited assertions about final source/destination existence, return values, and namespace placement under async execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncFederationRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncHandlerQueueOverflow.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncHandlerQueueOverflow.java

Purpose: validates that a saturated per-namespace async handler queue fails predictably instead of blocking unboundedly.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterAsyncRpcClient`, `RouterRpcServer.getAsyncExecutorForNamespace`, `RouterAsyncRpcFairnessPolicyController`, config keys for queue size, handler/responder counts, fairness timeout, max async-call permits, `FSNamesystem`, `NameNodeAdapterMockitoUtil`, `CountDownLatch`, `ThreadPoolExecutor`, `RemoteMethod`, `OpenFilesIterator`, `LambdaTestUtils`, and `syncReturn`.

Control flow: setup starts a two-nameservice HA cluster with active/standby/observer NNs, configures async queue capacity to 2 with single handlers/responders and one async permit, spies an NN `FSNamesystem` method (`getFilesBlockingDecom`) to wait on a latch for `/veryBigOperation`, then creates an async client. The test sends one call downstream, another blocked at permit acquisition, two queued calls, and a fifth call that should be rejected. `syncReturn` is expected to throw `StandbyException` with a busy-namespace message. The latch is released so the test can terminate.

State and persistence behavior: no file state is central; the state is executor queue size, completed-task count, permits, and the latch-blocked NN method. Integration points include router fairness, per-namespace async executors, NN protocol invocation, and rejection-to-exception mapping. Risks are timing sensitivity and a mocked namesystem lock. Test signals are executor queue sizes, completed task counts, timeout-bounded completion, and exact busy exception text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncHandlerQueueOverflow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncMountTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncMountTable.java

Purpose: runs the standard mount-table router tests with async RPC enabled.

Important APIs/types/functions: extends `TestRouterMountTable`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, and inherited mount-table admin/client helpers. Static inherited fields such as `cluster`, `routerContext`, `stateStore`, and test mount table state are initialized by the subclass.

Control flow: `globalSetUp()` creates a state-store-backed Router cluster with admin/RPC services and async RPC enabled, starts routers, obtains a router context, generates a mock mount table, and initializes inherited state-store references. The actual test methods are inherited from `TestRouterMountTable`, so this class functions as a configuration specialization rather than adding new assertions.

State and persistence behavior: inherited tests persist mount-table records in the router state store and exercise router cache reloads. Integration points include admin RPC, mount-table manager, state-store cache, and router client path resolution under async RPC. Risks are inherited static state coupling and missed async-specific assertions beyond successful inherited behavior. Test signals are the inherited suite’s mount-table add/remove/list/cache/path-resolution assertions executed with async RPC enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncMountTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncNamenodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncNamenodeProtocol.java

Purpose: verifies async `RouterAsyncNamenodeProtocol` parity with synchronous `RouterNamenodeProtocol` for selected NamenodeProtocol methods.

Important APIs/types/functions: `RouterAsyncNamenodeProtocol`, `RouterNamenodeProtocol`, `DatanodeInfo`, `BlocksWithLocations`, `ExportedBlockKeys`, `NamespaceInfo`, `HdfsConstants.DatanodeReportType`, and `AsyncUtil.syncReturn`. It inherits cluster and async RPC server setup from `RouterAsyncProtocolTestBase`.

Control flow: setup instantiates async and sync protocol modules. `getBlocks()` obtains a datanode report, calls async `getBlocks`, synchronizes the return, then compares block IDs with the sync result. `getBlockKeys()`, `getTransactionID()`, `getMostRecentCheckpointTxId()`, and `versionRequest()` make async calls and compare key fields with sync calls. Private helpers compare block-key metadata and namespace version fields.

State and persistence behavior: reads namenode block, key, transaction, checkpoint, and namespace metadata; it does not mutate filesystem state. Dependencies are active NN routing, async return context, and direct sync protocol parity. Risks include empty-block cases making coverage shallow and field-by-field comparisons needing updates if protocol objects evolve. Test signals are non-null async results and equality of transaction IDs, block-key attributes, namespace IDs, layout version, cluster ID, and ctime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncNamenodeProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncQuota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncQuota.java

Purpose: tests `AsyncQuota` read and write operations against a router namespace with storage-type quota support enabled.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterConfigBuilder.quota(true)`, `AsyncQuota`, `QuotaUsage`, `StorageType`, `DFS_QUOTA_BY_STORAGETYPE_ENABLED_KEY`, `RouterAsyncRpcClient`, `MockResolver`, `FSDataOutputStream`, and `syncReturn`. The cluster uses one HA nameservice, three DNs, rack configuration, and single async handler/responder counts.

Control flow: setup maps `/` to `ns0`, creates `/testdir`, writes a 1024-byte file, and wires a spy RPC server so `AsyncQuota` uses the async client. `testRouterAsyncGetQuotaUsage()` fetches quota usage for `/testdir` and verifies space consumed is `3 * 1024` with one directory and one file. `testRouterAsyncSetQuotaUsage()` sets a DISK type quota of 8096, waits for completion, reads quota usage back, and verifies the storage-type quota.

State and persistence behavior: quota metadata is persisted in the namenode for `/testdir`; file data and directory are removed after each test. Integration points include quota module routing, storage-type quota enablement, replication accounting, and async completion. Risks include replication-factor assumptions and quota state leakage if cleanup fails. Test signals are exact space consumption, file/directory counts, and type quota values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncQuota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRPCMultipleDestinationMountTableResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRPCMultipleDestinationMountTableResolver.java

Purpose: async version of multiple-destination mount table resolver tests, focused on local resolver datanode mapping, invoking available namespaces when one destination is down, and multi-destination directory detection.

Important APIs/types/functions: extends `TestRouterRPCMultipleDestinationMountTableResolver`; uses `StateStoreDFSCluster` with `MultipleDestinationMountTableResolver`, `DistributedFileSystem`, `MountTable`, `RouterQuotaUsage`, `DestinationOrder`, `LocalResolver`, `RouterClientProtocol`, `RemoteMethod`, `FsServerDefaults`, `MiniDFSCluster`, and `syncReturn`.

Control flow: setup starts three nameservices with async RPC, quota, admin, state store, and ACL-enabled namenodes. `testLocalResolverGetDatanodesSubcluster()` installs a LOCAL multi-destination mount, asks the `LocalResolver` for datanode-to-subcluster mapping, then removes mount and NN paths. `testInvokeAtAvailableNs()` creates a fault-tolerant RANDOM mount, shuts down two NNs, invokes async `getServerDefaults` at an available namespace, and restarts NNs in finally. `testIsMultiDestDir()` calls async client protocol `isMultiDestDirectory` for directories, files, and symlinks under HASH_ALL and HASH mount orders.

State and persistence behavior: mount-table entries persist in state store and physical paths in multiple NNs; cleanup is explicit or inherited. Integration points include multi-destination ordering, local datanode resolver, fault-tolerant invocation, symlink resolution, and async RPC. Risks include NN shutdown/restart fragility and resolver cache state. Test signals are non-empty datanode mapping, non-null server defaults, and expected boolean values for multi-destination directory checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRPCMultipleDestinationMountTableResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpc.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpc.java

Purpose: configures the broad `TestRouterRpc` suite to run with async RPC and overrides selected assertions that need async result retrieval.

Important APIs/types/functions: extends `TestRouterRpc`; uses `MiniRouterDFSCluster`, `RouterConfigBuilder`, `RouterAsyncRpcFairnessPolicyController`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, `DFS_ROUTER_FAIRNESS_POLICY_CONTROLLER_CLASS`, `UserGroupInformation`, `FSDataOutputStream`, `OpenFilesIterator`, `LocatedBlock`, `HAServiceState`, `RemoteException`, reflection, and `syncReturn`.

Control flow: `globalSetUp()` builds router configuration with metrics/RPC, async RPC enabled, async fairness controller, lowered DN report cache, and delegates cluster setup to the superclass. `testSetup()` calls inherited per-test setup. Overrides include `testgetGroupsForUser()` retrieving async group arrays via `syncReturn`, `testConcurrentCallExecutorInitial()` verifying async clients do not initialize the synchronous concurrent executor, `testGetDelegationTokenAsyncRpc()`, and `testProxyGetHAServiceStateAsync()`.

State and persistence behavior: inherited tests create files, mount locations, delegation-token state, and router metrics. Async-specific state includes async worker pools and thread-local/current future state consumed by `syncReturn`. Integration points are the full router client/RPC surface, fairness controller, security token calls, HA state proxying, and inherited superclass behavior. Risks include large inherited coverage making failures harder to localize and async context reuse between overrides. Test signals are inherited `TestRouterRpc` assertions plus explicit async groups, delegation token, and HA state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcClient.java

Purpose: directly tests `RouterAsyncRpcClient` invocation paths, metrics, failover/error behavior, and sequential remote-location lookup.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterAsyncRpcClient`, `RouterRpcServer`, `RouterRpcMetrics`, `RemoteMethod`, `RemoteParam`, `FederationNamenodeContext`, `NamenodeProtocol`, `LocatedBlocks`, `MockResolver`, `NetUtils`, `CallerContext`, `RetriableException`, `StandbyException`, `LambdaTestUtils`, and `syncReturn`. The cluster has two nameservices and three HA NNs per nameservice: active, standby, and observer.

Control flow: setup installs mock locations for `/` and `/multDes` to both namespaces, initializes async thread pools, creates an async client, and writes `/testdir/testAsyncRpcClient.file`. `testInvokeSingle()` invokes `getTransactionID` on one namespace and verifies proxy metrics. `testInvokeAll()` invokes `mkdirs` over multi-destination locations, first expecting parent-not-found then success. `testInvokeMethod()` verifies normal file info retrieval, empty namenode list, standby-only list, no-active-namenodes, and bad protocol/connection failures with metric counters. `testInvokeSequential()` resolves block locations sequentially.

State and persistence behavior: filesystem paths, mock resolver entries, HA state transitions, active namenode resolver cache, and RPC metrics are mutated. Teardown restores `ns0` active, updates the resolver, deletes the test file, and closes FS. Risks are metrics counter coupling, HA transition timing, and async failure propagation. Test signals include returned transaction IDs/status/blocks, exact exceptions, queue-independent metric increments, and proxy failure counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcMultiDestination.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcMultiDestination.java

Purpose: async-enabled specialization of multi-destination router RPC tests.

Important APIs/types/functions: extends `TestRouterRpcMultiDestination`; uses `RouterConfigBuilder`, `MiniRouterDFSCluster.RouterContext`, `RouterAsyncRpcFairnessPolicyController`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, `DFS_ROUTER_FAIRNESS_POLICY_CONTROLLER_CLASS`, `UserGroupInformation`, and `syncReturn`.

Control flow: `globalSetUp()` builds a metrics/RPC router configuration, lowers DN report cache, enables async RPC, selects the async fairness controller, and delegates cluster setup to the superclass. `testgetGroupsForUser()` overrides the synchronous superclass method by invoking router RPC `getGroupsForUser` and then materializing the async `String[]` via `syncReturn`. `testConcurrentCallExecutorInitial()` asserts the async router RPC client does not use the synchronous concurrent call executor.

State and persistence behavior: inherited multi-destination mounts and cluster state provide coverage; this subclass mainly changes runtime execution mode. Integration points include group mapping RPC, async fairness, multi-destination resolver behavior inherited from the superclass, and router client internals. Risks are limited direct assertions and reliance on superclass setup semantics. Test signals are exact group-array equality and a null synchronous executor under async mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcMultiDestination.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcServer.java

Purpose: tests async helper methods on `RouterRpcServer` itself rather than on higher-level protocol modules.

Important APIs/types/functions: `RouterRpcServer`, `RemoteMethod`, `RemoteLocation`, `BlockStoragePolicy`, `DatanodeInfo`, `DatanodeStorageReport`, `HdfsConstants.DatanodeReportType`, and `syncReturn`. It inherits async RPC server setup and `/testdir` creation from `RouterAsyncProtocolTestBase`.

Control flow: `testInvokeAtAvailableNsAsync()` invokes remote `getStoragePolicies` at an available namespace and expects the standard eight storage policies. `testGetCreateLocationAsync()` gets locations for `/testdir`, invokes async create-location selection, and verifies the returned nameservice is `ns0`. `testGetDatanodeReportAsync()` fetches datanode reports, namespace-to-storage-report maps, and slow datanode reports asynchronously, comparing the slow report with the synchronous version.

State and persistence behavior: mostly read-only cluster state; create-location selection depends on resolver mappings and `/testdir`. Integration points include low-level async invocation, location selection, datanode report fan-out, and slow-datanode report handling. Risks include hard-coded expected policy/DN counts and type-erased map retrieval from `syncReturn(Map.class)`. Test signals are storage policy count, selected nameservice, datanode report sizes, map size, and array equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcWhenNamenodeFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcWhenNamenodeFailover.java

Purpose: regression test for async router behavior when a nameservice transitions out of active service after prior successful operations.

Important APIs/types/functions: `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFSClient`, `DirectoryListing`, `HdfsFileStatus`, `FederationTestUtils.transitionClusterNSToActive`, `transitionClusterNSToStandby`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`.

Control flow: `setupCluster(true)` starts an HA state-store cluster with metrics/admin/RPC/heartbeat and async RPC enabled. The test builds a router `DFSClient` for `hdfs://fed`, limits retry attempts, transitions namespace 0 active, creates `/ARR/testGetFileInfo`, confirms listing `/ARR` returns one child, transitions the cluster nameservices to standby, then asserts a subsequent `getFileInfo` for a non-existing path variant throws `IOException`.

State and persistence behavior: namespace HA state and router membership heartbeat state are central; filesystem path `/ARR/testGetFileInfo` is created before failover. The class keeps `cluster` as an instance field but does not show explicit teardown, so shutdown responsibility may rely on test framework or external cleanup in the larger suite. Integration points include router async RPC, DFS client retry/failover, heartbeat-discovered HA state, and client protocol error handling. Risks are resource leakage and timing between HA transition and router cache update. Test signal is an expected `IOException` instead of stale success or hang after failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncRpcWhenNamenodeFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncSnapshot.java

Purpose: verifies snapshot operations through `RouterAsyncSnapshot`.

Important APIs/types/functions: `RouterAsyncSnapshot`, `SnapshotStatus`, `SnapshottableDirectoryStatus`, `SnapshotDiffReport`, `SnapshotDiffReportListing`, `SnapshotException`, `LambdaTestUtils`, `FSDataOutputStream`, `Path`, and `syncReturn`. It inherits cluster and async server setup from `RouterAsyncProtocolTestBase`.

Control flow: setup writes `/testdir/testSnapshot.file` and constructs `RouterAsyncSnapshot`. The test allows snapshots on `/testdir`, creates `testdirSnapshot`, verifies the returned snapshot path, lists snapshottable directories and snapshots, modifies the file to generate diff data, fetches diff reports/listings, renames or deletes snapshots where applicable, and verifies invalid snapshot operations surface expected `SnapshotException` behavior.

State and persistence behavior: snapshot enablement and snapshot records are persisted in the namenode under `/testdir`; base teardown removes the directory. Integration points include async snapshot protocol wrappers, file mutation, diff generation, and exception propagation. Risks are cleanup if snapshot deletion is skipped, diff assertions that depend on exact mutation order, and global async context. Test signals include returned snapshot path, snapshot status/listing objects, diff entries, and expected snapshot exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncStoragePolicy.java

Purpose: verifies async router storage policy operations against the shared async protocol fixture.

Important APIs/types/functions: `RouterAsyncStoragePolicy`, `BlockStoragePolicy`, `FSDataOutputStream`, `Path`, and `syncReturn`. Setup creates the async storage policy module from the async router RPC server and writes `/testdir/testAsyncStoragePolicy.file`.

Control flow: the test retrieves the namenode's storage policy array directly, calls async `getStoragePolicies()`, and asserts array equality. It then reads the current policy for the test file, calls async `setStoragePolicy(testfilePath, "COLD")`, reads the policy again, verifies it changed, and checks the returned policy name is `COLD`. The path under test routes through the base fixture's mock `/` mapping to `ns0`.

State and persistence behavior: storage policy metadata is stored on the namenode for the test file and removed when the base fixture deletes `/testdir`. Integration points include router async storage-policy wrappers, NN storage policy protocol, path resolution, and async result conversion. Risks include hard-coded default policy availability and storage policy support varying with cluster configuration. Test signals are full policy-array equality, changed file policy, and exact `COLD` policy name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncUserProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncUserProtocol.java

Purpose: verifies async user/group mapping protocol support through the router.

Important APIs/types/functions: `RouterAsyncUserProtocol`, `GetUserMappingsProtocol`, `UserGroupInformation`, and `syncReturn`. It inherits router cluster, async RPC server, and `/testdir` fixture state from `RouterAsyncProtocolTestBase`.

Control flow: setup instantiates `RouterAsyncUserProtocol` from the async RPC server. The test creates a synthetic UGI user named `user` with groups `bar` and `group2`, calls async `getGroupsForUser("user")`, retrieves the `String[]` through `syncReturn`, and asserts exact array equality. This covers the async wrapper path for `GetUserMappingsProtocol` without involving CLI refresh commands.

State and persistence behavior: relies on process-level test UGI/group mapping state; no HDFS filesystem mutations are required beyond the inherited fixture. Integration points include router async protocol module, Hadoop security group mapping, and async result materialization. Risks are singleton UGI/group mapping and async context interactions. Test signal is exact group-array equality returned through the async router module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncUserProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncWebHdfsMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncWebHdfsMethods.java

Purpose: runs WebHDFS Router method tests with async RPC enabled.

Important APIs/types/functions: extends `TestRouterWebHdfsMethods`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterContext`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`. The superclass supplies HTTP request construction, file verification, mount table creation, namespace parsing, and invalid-path JSON checks.

Control flow: `globalSetUp()` creates a two-nameservice state-store cluster with RPC, HTTP, admin, and async RPC enabled, sets independent DNs, starts cluster/routers, waits for readiness, selects a router, and records the HTTP URI. Inherited tests then perform WebHDFS create operations and path validation through the async-enabled router.

State and persistence behavior: inherited tests create files in physical nameservices and mount entries in the state store. Integration points include HTTP/WebHDFS frontend, async router RPC backend, mount resolution, and invalid path exception serialization. Risks mirror the superclass plus the possibility that HTTP request handling hides async backend failures until response time. Test signals are inherited HTTP status codes, namespace file existence checks, network-location parsing, and JSON remote exception validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncWebHdfsMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncClass.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncClass.java

Purpose: test utility implementation that mirrors `SyncClass` behavior using `AsyncUtil` primitives, serving as a compact model for async chaining, exception handling, foreach control, finally cleanup, and concurrent composition.

Important APIs/types/functions: extends `SyncClass`; uses `CompletableFuture`, `ExecutorService`, `Executors`, `Async.CUR_COMPLETABLE_FUTURE`, `asyncApply`, `asyncCatch`, `asyncComplete`, `asyncCurrent`, `asyncFinally`, `asyncForEach`, `asyncReturn`, `asyncThrowException`, and `asyncTry`. The constructor creates a single daemon worker named `Async Worker`.

Control flow: methods call `timeConsumingMethod()` to seed the current future, then compose async transformations. `applyMethod` adds prefixes or optional exceptions. `exceptionMethod` emits async exceptions directly. `forEachMethod`, `forEachBreakMethod`, and `forEachBreakByExceptionMethod` iterate asynchronously with normal break or exception-driven break. `applyThenApplyMethod` demonstrates an async apply that can enqueue another async call. `applyCatchThenApplyMethod` recovers from IO exceptions by rerunning input 1. `applyCatchFinallyMethod` wraps/catches and always clears resources. `currentMethod` dispatches multiple current async calls and aggregates future results.

State and persistence behavior: state is in the executor service, mutable result builders, provided resource lists, and thread-local async future context. There is no persistent storage. Risks include no explicit executor shutdown, shared mutable builders captured by async callbacks, and reliance on `AsyncUtil` thread-local ordering. Test signals come from `TestAsyncUtil`, which compares this async implementation with `SyncClass`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/BaseClass.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/BaseClass.java

Purpose: common interface for the synchronous and asynchronous utility classes used to test `AsyncUtil` conversion patterns.

Important APIs/types/functions: declares `applyMethod(int)`, `applyMethod(int, boolean)`, `exceptionMethod(int)`, `forEachMethod(List<Integer>)`, `forEachBreakMethod(List<Integer>)`, `forEachBreakByExceptionMethod(List<Integer>)`, `applyThenApplyMethod(int)`, `applyCatchThenApplyMethod(int)`, `applyCatchFinallyMethod(int, List<String>)`, and `currentMethod(List<Integer>)`. Exception signatures allow IO failures in methods that model checked-exception paths.

Control flow: the interface itself has no implementation; its role is to let `TestAsyncUtil` run the same semantic checks against `SyncClass` and `AsyncClass` depending on execution mode.

State and persistence behavior: no state or persistence. Dependencies are only Java `IOException` and `List`. Integration points are local test utility classes rather than production router code. Risks are contract drift: if `SyncClass` and `AsyncClass` diverge while still satisfying the interface, tests must catch behavioral differences. Test signals are indirect through parameterized `TestAsyncUtil` coverage over both implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/BaseClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/SyncClass.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/SyncClass.java

Purpose: synchronous reference implementation for `BaseClass`, used as the behavioral oracle for `AsyncClass`.

Important APIs/types/functions: implements `BaseClass`; uses `SubjectInheritingThread`, `ExecutorService`, `Executors`, `Future`, `IOException`, and `List`. Core methods include `applyMethod`, `exceptionMethod`, foreach variants, catch/finally variants, `currentMethod`, `timeConsumingMethod`, and private `getExecutorService()`.

Control flow: `timeConsumingMethod()` sleeps or simulates delay and returns bracketed input text. `applyMethod()` prefixes the result and can throw checked/runtime exceptions for inputs 2 and 3. Foreach methods build comma-delimited output, optionally stopping at input 2 or stopping on runtime exception while recording IO exceptions. Chained methods call `applyMethod` and then additional logic. `applyCatchFinallyMethod` clears the provided resource list in a finally block. `currentMethod` submits tasks through a subject-inheriting executor, waits on futures, and aggregates values or exception messages.

State and persistence behavior: state is limited to the configured time-consuming delay and lazily created executor. There is no persistent storage. Dependencies include thread identity/security context inheritance for current-method tests. Risks include executor lifecycle, timing in tests, and exception-message coupling. Test signals are exact string outputs and thrown exception types/messages used by `TestAsyncUtil`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/SyncClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/TestAsyncUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/TestAsyncUtil.java

Purpose: parameterized tests for `AsyncUtil` semantics, comparing synchronous and asynchronous implementations of the same `BaseClass` operations.

Important APIs/types/functions: `ExecutionMode` parameter source, `BaseClass`, `SyncClass`, `AsyncClass`, `AsyncUtil.syncReturn`, `Async.CUR_COMPLETABLE_FUTURE`, `LambdaTestUtils`, `Time`, `Callable`, and JUnit assertions. `setUp(ExecutionMode)` selects the implementation, while `after()` clears async thread-local/current future state.

Control flow: tests cover basic `apply`, checked/runtime exception propagation, direct exception methods, chained apply, catch-then-apply recovery, catch/finally resource cleanup, async foreach, explicit foreach break, exception-driven foreach break, and concurrent/current aggregation. Helpers `checkResult` and `checkException` normalize sync versus async behavior by either using direct returns or `syncReturn` and exception interception.

State and persistence behavior: state is in thread-local async future context, worker threads, mutable resource lists, and simulated timing. No external persistence is used. Integration points are the async utility DSL and the paired reference/async implementations. Risks include timing-sensitive async completion, thread-local leakage between parameterized runs, and assertions tied to exact exception strings. Test signals are expected strings, expected exception classes/messages, cleared resources after finally, and false/non-null async future state after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/TestAsyncUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/security/token/TestSQLDelegationTokenSecretManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/security/token/TestSQLDelegationTokenSecretManagerImpl.java

Purpose: comprehensive tests for SQL-backed delegation token secret manager behavior, covering token/key persistence, multi-manager coordination, expiration removal, sequence/key allocation, Hikari configuration, and retry handling.

Important APIs/types/functions: `SQLDelegationTokenSecretManagerImpl`, `SQLDelegationTokenSecretManager`, `DelegationTokenManager`, `DelegationTokenIdentifier`, `AbstractDelegationTokenIdentifier`, `AbstractDelegationTokenSecretManager`, `Token`, `UserGroupInformation`, JDBC `Connection/DriverManager`, Hikari connection factory, `GenericTestUtils`, `LambdaTestUtils`, `Time`, `ReentrantLock`, and nested classes `TestDelegationTokenSecretManager`, `TestConnectionFactory`, and `TestRetryHandler`. Static DB setup creates/drops token/key/timer tables for tests.

Control flow: lifecycle opens an in-memory test DB connection, creates tables once, truncates rows per test, and drops tables at the end. Tests validate single and multiple managers sharing stored keys/tokens, cancellation, renewal, expired-token cleanup, sequence number uniqueness and rollover, delegation-key allocation with key-roll locking to avoid races, Hikari config parsing, and retry attempts when the test connection factory simulates failures. Helpers create token managers, allocate/validate tokens, query SQL presence, and stop managers.

State and persistence behavior: SQL rows are the main persistence contract for tokens, keys, sequence numbers, and timers; managers also keep in-memory token/key caches and background threads. Integration points include Hadoop delegation-token web manager, JDBC/Hikari pooling, retriable SQL command wrapper, and user identities. Risks are race conditions in key rolling/expiry, sequence rollover edge cases, DB cleanup ordering, and retry masking. Test signals include successful token decode/renew/cancel, SQL row presence/absence, unique sequence IDs, key IDs, eviction waits, Hikari values, and retry counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/security/token/TestSQLDelegationTokenSecretManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockDelegationTokenSecretManager.java

Purpose: simple running mock secret manager for router security tests.

Important APIs/types/functions: extends `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`, uses `Configuration`, `IOException`, and HDFS `DelegationTokenIdentifier`. The constructor accepts a `Configuration` for reflective creation compatibility and configures delegation token timing values through the superclass constructor.

Control flow: the class provides the minimum implementation needed by `RouterSecurityManager`: construct successfully and return a new `DelegationTokenIdentifier` from `createIdentifier()`. It does not add custom storage, token validation, or lifecycle behavior beyond the superclass.

State and persistence behavior: superclass in-memory token/key state applies; there is no external persistence. Integration points are reflective secret-manager instantiation via router config and tests that need a functioning manager without ZooKeeper or SQL. Risks are that it may not represent production persistence or background lifecycle behavior, so it is useful for unit-level security manager tests only. Test signals are indirect: router security tests can create the manager and issue/verify tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockNotRunningSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockNotRunningSecretManager.java

Purpose: mock secret manager that can be reflectively constructed but is intentionally not running, used to test router startup/error behavior with an unusable delegation-token manager.

Important APIs/types/functions: extends `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`, has a `Configuration` constructor, and implements `createIdentifier()` by returning an HDFS `DelegationTokenIdentifier`.

Control flow: like the running mock, this class only supplies construction and identifier creation. Its value comes from not starting or not satisfying runtime expectations in `RouterSecurityManager` tests, allowing failure paths to be exercised.

State and persistence behavior: no external persistence; any superclass in-memory state is not relied upon as active service state. Integration points are router security manager reflection and service lifecycle validation. Risks are semantic ambiguity: the name and test use must clearly indicate that construction success does not mean the manager is operational. Test signals are indirect in `TestRouterSecurityManager`, where operations with this class are expected to throw service-state errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockNotRunningSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterHttpDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterHttpDelegationToken.java

Purpose: tests WebHDFS/HTTP delegation-token operations against a secure Router configured with a no-auth test filter.

Important APIs/types/functions: `RouterHDFSContract`, `RouterWebHDFSContract`, `RouterConfigBuilder`, `Router`, `WebHdfsFileSystem`, `WebHdfsTestUtil`, `DelegationTokenIdentifier`, `Token`, WebHDFS op params (`GetOpParam`, `PutOpParam`, `TokenArgumentParam`, `RenewerParam`, `UserParam`), `AuthenticationFilterInitializer`, `AuthenticationFilter`, `PseudoAuthenticationHandler`, `FilterContainer`, and nested `NoAuthFilterInitializer`/`NoAuthFilter`.

Control flow: setup initializes security, configures router HTTP/RPC/security services and a no-auth HTTP filter that injects pseudo-auth settings, starts the router contract cluster, and obtains a WebHDFS client. `testGetDelegationToken()` requests a token for a renewer and decodes the identifier. `testRenewDelegationToken()` obtains and renews a token, asserting a positive renewal time. `testCancelDelegationToken()` obtains then cancels a token and verifies subsequent renewal/cancel behavior through WebHDFS helper calls. Helpers build operation URLs and parse token identifiers.

State and persistence behavior: token state lives in the router secret manager backing the secure contract cluster; HTTP authentication state is test-filter driven. Integration points include Router HTTP endpoints, WebHDFS token operations, delegation-token manager, and security configuration. Risks include static contract cluster cleanup, no-auth filter hiding authentication issues, and token lifecycle timing. Test signals are non-null decoded identifiers, valid renewal timestamps, and expected failures after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterHttpDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterSecurityManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterSecurityManager.java

Purpose: tests `RouterSecurityManager` construction, token issue/verify/credentials behavior, token-owner metrics, and failure handling for missing or non-running secret managers.

Important APIs/types/functions: `RouterSecurityManager`, `Router`, `RouterConfigBuilder`, `ZKDelegationTokenSecretManagerImpl`, `MockDelegationTokenSecretManager`, `MockNotRunningSecretManager`, `DelegationTokenIdentifier`, `Token`, `Credentials`, `UserGroupInformation`, `DefaultMetricsSystem`, `RouterMBean`, Jackson `ObjectMapper/JsonNode`, `Metrics2Util.NameValuePair`, `ServiceStateException`, `SecretManager.InvalidToken`, and security config keys including `DFS_ROUTER_DELEGATION_TOKEN_DRIVER_CLASS`.

Control flow: tests initialize security configs, set the mock or ZK-backed manager class, construct/start routers, and call `RouterSecurityManager` APIs. Coverage includes reflective secret-manager creation, issuing delegation tokens, verifying valid and invalid tokens, creating credentials for clients, aggregating top token owners/real owners through metrics JSON, and failure cases without a manager or with a non-running manager. Helpers build user/group arrays and start routers with selected configs.

State and persistence behavior: token state lives in the configured secret manager, while metrics state is exported through router MBeans/metrics system. Some tests use proxy/real users to create owner distributions. Integration points include router service startup, Hadoop security authentication, token encoding/decoding, metrics JSON, and secret-manager lifecycle. Risks include static metrics contamination, JSON schema coupling, timing/lifecycle of ZK manager, and typo-preserved method name `testDelgationTokenTopOwners`. Test signals are issued token fields, credential contents, verified passwords, expected exceptions, and top-owner metric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/TestRouterSecurityManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/token/TestZKDelegationTokenSecretManagerImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/token/TestZKDelegationTokenSecretManagerImpl.java

Purpose: tests router-specific ZooKeeper delegation-token manager synchronization when token watchers are disabled and multiple manager instances operate concurrently.

Important APIs/types/functions: extends Hadoop `TestZKDelegationTokenSecretManager`; uses `ZKDelegationTokenSecretManagerImpl`, `ZKDelegationTokenSecretManager`, `DelegationTokenManager`, web `DelegationTokenIdentifier`, `Token`, `SecretManager.InvalidToken`, `UserGroupInformation`, `Text`, `Time`, and config keys `ZK_DTSM_TOKEN_WATCHER_ENABLED`, `ZK_DTSM_ROUTER_TOKEN_SYNC_INTERVAL`, `RENEW_INTERVAL`, and `REMOVAL_SCAN_INTERVAL`.

Control flow: teardown stops any created managers. `testMultiNodeOperationWithoutWatch()` starts multiple managers without watchers, issues tokens from one, validates retrieval/renew/cancel behavior through another after sync intervals. `testMultiNodeTokenRemovalShortSyncWithoutWatch()` and `testMultiNodeTokenRemovalLongSyncWithoutWatch()` use different router sync intervals to prove expired/cancelled token removal propagates without watchers after the configured sync/removal timing. The tests use waits and invalid-token assertions to confirm propagation.

State and persistence behavior: token/key state is persisted in ZooKeeper by the base test infrastructure and cached locally by each manager. Watchers are disabled, so periodic sync is the persistence-to-cache bridge. Integration points include router-specific ZK sync, Hadoop web delegation-token manager, token expiration/removal scans, and multi-instance coordination. Risks are timing flakiness from sync intervals and reliance on inherited ZK test setup. Test signals are successful cross-manager token operations before removal and `InvalidToken`/failure after propagated removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/token/TestZKDelegationTokenSecretManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/FederationStateStoreTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/FederationStateStoreTestUtils.java

Purpose: utility class for creating, configuring, clearing, and seeding Router Federation state-store services in tests.

Important APIs/types/functions: `StateStoreService`, `StateStoreDriver`, `StateStoreFileImpl`, `StateStoreFileBaseImpl`, `HdfsConfiguration`, `Configuration`, `FileUtils`, `GenericTestUtils`, `Time`, `BaseRecord`, `MountTable`, `MembershipState`, `MembershipStats`, and `FederationNamenodeServiceState`. Constants define a file-backed test driver and test state-store directory.

Control flow: `getStateStoreConfiguration()` creates base configuration; overloaded variant applies a specific driver class. `newStateStore()` deletes old file state, initializes a `StateStoreService`, and waits for readiness. `waitStateStore()` polls until the store becomes ready. `deleteStateStore()` removes the file-backed state directory. `setFileConfiguration()` points config at a unique local state-store directory. `clearAllRecords()` and `clearRecords()` remove persisted records by record type. `synchronizeRecords()` inserts/replaces a collection of records. `createMockMountTable()` and `createMockRegistrationForNamenode()` construct representative mount and membership records for tests.

State and persistence behavior: primarily manipulates file-backed state-store directories under test data paths and record collections inside the driver. Integration points include state-store driver initialization, cache refresh paths, mount-table records, membership records, and test cleanup. Risks include deleting shared test directories if configuration is wrong, UUID/path uniqueness assumptions, and direct driver access bypassing service-level validation. Test signals are helper return booleans and readiness polling used by dependent tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/FederationStateStoreTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreBase.java

Purpose: base fixture for state-store tests, providing a ready `StateStoreService` and configuration backed by the test file driver.

Important APIs/types/functions: `FederationStateStoreTestUtils.newStateStore`, `getStateStoreConfiguration`, `waitStateStore`, `StateStoreService`, `Configuration`, `RBFConfigKeys`, JUnit lifecycle hooks, and `TimeUnit`. Static getters expose the service and config to subclasses.

Control flow: `createBase()` builds test state-store configuration and creates a new state store. `setupBase()` waits for the state store to be ready and refreshes/clears state as needed before each test. `destroyBase()` closes/stops the state store and removes any file-backed test data. Subclasses call protected getters for store access.

State and persistence behavior: owns a static state-store instance and config for the test class hierarchy; persistent file data is cleaned by utility methods. Integration points are file-backed state-store driver, service readiness polling, and subclass record-store operations. Risks include static state leaking across subclasses, readiness timing, and tests assuming a clean store when setup did not clear a specific record type. Test signals are successful state-store readiness and non-null service/config assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreDisabledNameservice.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreDisabledNameservice.java

Purpose: verifies persistence and retrieval of disabled nameservice records in the state store.

Important APIs/types/functions: extends `TestStateStoreBase`; uses `DisabledNameservice`, `DisabledNameserviceStore`, `FederationStateStoreTestUtils.clearRecords`, `Set`, and JUnit assertions. `setup()` clears existing `DisabledNameservice` records before each test.

Control flow: `testDisableNameservice()` gets the disabled-nameservice store from the shared state store, creates disabled records for nameservices, inserts them through the store, retrieves the disabled set, and checks expected nameservice IDs and count. It validates both write and read paths for this record type.

State and persistence behavior: records are stored in the file-backed state-store driver supplied by `TestStateStoreBase`; setup clears only the relevant record type to isolate runs. Integration points include the state-store service, typed record store, and disabled nameservice record serialization. Risks include stale records if cleanup fails and set-order assumptions if future assertions become order-sensitive. Test signals are successful insertions and exact retrieved disabled nameservice set contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreDisabledNameservice.java -->
