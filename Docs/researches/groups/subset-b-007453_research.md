# subset-b-007453 research

Grouped research for Hadoop HDFS Router-Based Federation tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableRouterQuota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableRouterQuota.java

## Purpose

`TestDisableRouterQuota` verifies that the Router quota subsystem is consistently disabled when the Router is configured with `RouterConfigBuilder().quota(false).rpc()`. It is a focused guard around `Quota` behavior exposed through `RouterRpcServer`, ensuring admin-side and client-side quota paths fail with the same disabled-quota message.

## Important APIs, types, and functions

The test owns a static `Router` lifecycle in `setUp()` and `tearDown()`. `checkDisableQuota()` asserts `router.isQuotaEnabled()` is false before each test. `testSetQuota()` calls `Quota.setQuota(path, nsQuota, ssQuota, storageType, checkMountEntry)` twice, covering both `checkMountEntry=false` for `RouterAdminServer#synchronizeQuota` and `checkMountEntry=true` for `RouterClientProtocol#setQuota`. `testGetQuotaUsage()` calls `Quota.getQuotaUsage()`, and `testGetGlobalQuota()` calls `Quota.getGlobalQuota()`. `LambdaTestUtils.intercept` and `GenericTestUtils.assertExceptionContains` are the primary assertion helpers.

## Control flow

The class starts a real Router bound to an ephemeral RPC address, assigns a router id, and starts services. Each test fetches the quota module from `router.getRpcServer().getQuotaModule()` and asserts that quota APIs throw `IOException` containing `The quota system is disabled in Router.` No federated cluster or state store is involved.

## State and persistence behavior

The only persistent state is in-memory Router service state. The test does not write mount-table records or quota records. Its key state signal is the Router config bit that disables quota before RPC service startup.

## Dependencies and integration points

The file integrates `Router`, `RouterRpcServer`, `Quota`, `RouterConfigBuilder`, and `RBFConfigKeys.DFS_ROUTER_RPC_ADDRESS_KEY`. It protects the contract that all quota entry points honor the top-level Router quota switch.

## Risks and test signals

The test is sensitive to exact exception text. It is valuable for catching partial quota-disable regressions, especially if future changes bypass `Quota` checks in admin synchronization or client protocol paths. Because it uses a single Router without a state store, it does not validate disabled quota behavior through full `RouterAdmin` CLI or persisted mount-table quota metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableRouterQuota.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestFederationUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestFederationUtil.java

## Purpose

`TestFederationUtil` validates reflective resolver creation through `FederationUtil`. It ensures RBF can instantiate configured resolver classes both with and without optional contextual objects.

## Important APIs, types, and functions

`testInstanceCreation()` uses `HdfsConfiguration`, config keys `FEDERATION_NAMENODE_RESOLVER_CLIENT_CLASS` and `FEDERATION_FILE_RESOLVER_CLIENT_CLASS`, `MockResolver`, `ActiveNamenodeResolver`, `FileSubclusterResolver`, `StateStoreService`, and `Router`. It calls `FederationUtil.newActiveNamenodeResolver(conf, stateStore)`, `FederationUtil.newActiveNamenodeResolver(conf, null)`, `FederationUtil.newFileSubclusterResolver(conf, router)`, and `FederationUtil.newFileSubclusterResolver(conf, null)`.

## Control flow

The test registers `MockResolver` as both the namenode resolver implementation and file-subcluster resolver implementation. It then constructs resolver instances through utility methods and asserts all returned references are non-null. It does not start Router services.

## State and persistence behavior

No state store persistence is exercised. The supplied `StateStoreService` and `Router` are constructor-context probes: the test checks that resolver construction paths can tolerate both present and missing context.

## Dependencies and integration points

This file touches resolver extension wiring, especially the constructor-selection behavior in `FederationUtil`. It is an integration point for pluggable resolver classes and the config keys that bind them.

## Risks and test signals

The test will catch obvious reflection or constructor signature regressions, but it does not assert exact class identity, initialized state, or resolver behavior after construction. Failures here indicate resolver bootstrap breakage rather than runtime federation routing problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestFederationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestNoNamenodesAvailableLongTime.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestNoNamenodesAvailableLongTime.java

## Purpose

`TestNoNamenodesAvailableLongTime` reproduces a failover window where a Router cache records no active namenode even though one namenode has become active in the cluster. It verifies that Router RPC cache rotation recovers without waiting for the next state-store cache refresh, including observer-read scenarios.

## Important APIs, types, and functions

The setup path uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `NamenodeHeartbeatService`, `FederationRPCMetrics`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `NameNode`, and client `FileSystem` instances. Helper methods include `setupCluster()`, `initEnv()`, `routerCacheNoActiveNamenode()`, `allRoutersLoadCache()`, `allRoutersHeartbeat()`, `transitionActiveToStandby()`, `setSecondNonObserverNamenodeInTheRouterCacheActive()`, and `stopObserver()`.

## Control flow

`setupCluster()` builds an HA federated cluster with configurable observer namenode count and a long cache flush interval. `initEnv()` transitions all namenodes to standby, heartbeats and loads Router caches so the Router sees no active, then switches the second non-observer cached namenode to active and heartbeats without refreshing the Router cache. Tests then perform filesystem operations that initially hit stale routing state and rely on Router RPC retry/cache rotation to recover.

`testShouldRotatedCache()` verifies create succeeds after one `NoNamenodesAvailableException` metric increment. `testShouldNotBeRotatedCache()` proves illegal operations, such as default ACL on a file, should not be treated as cache-rotation signals after the active is already reachable. `testUseObserver()`, `testAtLeastOneObserverNormal()`, and `testAllObserverAbnormality()` cover observer reads when observers are available, partially down, or all down.

## State and persistence behavior

State is split between NameNode HA state, heartbeat records in the state store, and Router in-memory resolver cache. The central persistence behavior is intentional staleness: heartbeat records are updated, but Router cache refresh is withheld. Metrics such as `getProxyOpNoNamenodes()`, `getObserverProxyOps()`, and `getProxyOpFailureCommunicate()` are used as observable state.

## Dependencies and integration points

This test integrates failover, Router resolver cache ordering, observer read routing, client retry policy (`dfs.client.retry.max.attempts`), ACL validation, and RPC metrics. It depends on `NoNamenodesAvailableException` being classified as an unavailable exception by `RouterRpcClient`.

## Risks and test signals

The test is timing and ordering sensitive because it depends on cached namenode list order and manual heartbeat/cache refresh sequencing. It provides strong signals for regressions that cause long-lived stale `NoNamenodesAvailableException` responses after failover, but it does not model real asynchronous cache refresh races beyond the controlled mini-cluster sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestNoNamenodesAvailableLongTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestObserverWithRouter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestObserverWithRouter.java

## Purpose

`TestObserverWithRouter` is the main observer-read and state-id propagation test suite for Router-Based Federation. It verifies that reads are routed to observer namenodes only when client and Router configuration permit it, that `msync` and federated state propagation keep observer reads consistent, and that the Router handles observer failure, stale state ids, and per-namespace overrides.

## Important APIs, types, and functions

The suite uses `MiniRouterDFSCluster`, `RouterContext`, `MockResolver`, `RouterConfigBuilder`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `MembershipNamenodeResolver`, `RouterStateIdContext`, `ClientGSIContext`, `RouterFederatedStateProto`, `RpcHeaderProtos`, and the client proxy providers `RouterObserverReadProxyProvider` and `RouterObserverReadConfiguredFailoverProxyProvider`. `ConfigSetting` enumerates three client enablement modes: a namenode proxy flag, direct Router observer-read proxy provider, and configured HA failover proxy provider.

## Control flow

`init()` starts a two-nameservice HA cluster with two observers per nameservice unless a test is tagged to skip automatic startup. `startUpCluster()` applies default observer-read, tail-edits, and state-context settings; starts namenodes; transitions one active, one standby, and remaining observers per namespace; starts Router RPC; registers namenodes; installs mock locations; and selects a Router.

The early tests verify basic routing: writes go to active, eligible reads go to observers, and missing client observer configuration keeps reads on active. Other tests disable federated state propagation or per-nameservice observer reads and assert active-only behavior. Failure tests stop observers and verify fallback to active or remaining observers while marking unavailable namenodes. `testRouterMsync()` and the auto-msync tests count active RPCs caused by explicit and implicit `msync`.

State-id tests exercise `ClientGSIContext.receiveResponseState()`, `RouterStateIdContext.updateResponseState()`, max-size filtering, namespace cleanup, shared state across connection-pool cleanup, periodic active refresh when state becomes stale, and behavior when restarted active namenodes stop sending state ids.

## State and persistence behavior

The key state is in-memory state id tracking per namespace via `LongAccumulator`, encoded router federated state in RPC response headers, Router resolver membership cache, observer eligibility configuration, and metrics counters for active versus observer proxy operations. The suite also manipulates cluster membership expiry and connection pool cleanup to validate state cleanup. It does not persist mount table edits; locations are installed through mock cluster setup.

## Dependencies and integration points

This file spans HDFS client failover configuration, Router RPC routing, observer namenode HA states, tail edits, connection pools, state-id propagation headers, and metrics. It is a major integration signal for consistency of observer reads through RBF.

## Risks and test signals

The tests rely on precise RPC-count expectations and mini-cluster timing, especially for auto-msync periods, connection-pool cleanup, and periodic state refresh. They catch regressions that route reads to stale observers, omit `msync`, over-propagate state headers, fail to clean namespace state, or mishandle restarted namenodes with disabled state context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestObserverWithRouter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestPoolAlignmentContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestPoolAlignmentContext.java

## Purpose

`TestPoolAlignmentContext` validates per-connection-pool state-id behavior used by Router observer reads. It ensures request headers carry only pool-local client state while last-seen namenode state is shared through `RouterStateIdContext`.

## Important APIs, types, and functions

The file constructs `RouterStateIdContext` and `PoolAlignmentContext`, then directly manipulates `RpcRequestHeaderProto.Builder` and `RpcResponseHeaderProto`. Helpers are `assertRequestHeaderStateId()` and `getRpcResponseHeader()`.

## Control flow

`testNamenodeRequestsOnlyUsePoolLocalStateID()` seeds namespace state id `20` in the shared Router context, creates two pool contexts for the same namespace, and verifies both initially send `Long.MIN_VALUE` in request headers while seeing last-seen state `20`. Advancing client state id on one pool to `30` affects only that pool's request header, not the other pool.

`testWhenNamenodeStopsSendingStateId()` receives a response with state id `10`, advances client state to `10`, then receives a response with state id `0`. A zero state id represents a namenode with state context disabled, so the pool resets last-seen and request state to `Long.MIN_VALUE`.

## State and persistence behavior

State is strictly in-memory. The test distinguishes shared namespace state in `RouterStateIdContext` from pool-local client state in `PoolAlignmentContext`. There is no state-store or filesystem dependency.

## Dependencies and integration points

This file protects the RPC header alignment contract between Router connection pools, clients, and observer namenodes. It is closely related to `TestObserverWithRouter` but isolates the state machine without a mini-cluster.

## Risks and test signals

Failures indicate potential stale state-id leakage across connection pools or continued observer state use after a namenode stops sending state ids. The test does not exercise concurrent updates, but it is a precise unit signal for header values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestPoolAlignmentContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRBFConfigFields.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRBFConfigFields.java

## Purpose

`TestRBFConfigFields` is a configuration consistency test. It compares Java constants in `RBFConfigKeys` against `hdfs-rbf-default.xml` and fails on missing properties in either direction.

## Important APIs, types, and functions

The class extends `TestConfigurationFieldsBase` and overrides `initializeMemberVariables()`. It sets `xmlFilename` to `hdfs-rbf-default.xml`, `configurationClasses` to `RBFConfigKeys.class`, and enables both `errorIfMissingConfigProps` and `errorIfMissingXmlProps`.

## Control flow

There are no local `@Test` methods because the inherited base class drives the comparison. Initialization also creates skip sets and excludes dynamic fair-handler prefixes: `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX` and `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`.

## State and persistence behavior

The test reads configuration metadata from class constants and XML resources. It does not mutate runtime Router state or the state store.

## Dependencies and integration points

This file integrates RBF config definitions with Hadoop's shared config-field test framework. It ensures default XML documentation and code constants remain synchronized.

## Risks and test signals

The skip-prefix list is important because fair-handler keys are prefix families rather than concrete XML entries. A failure usually means a new RBF config key was added without XML documentation/defaults, an XML property lacks a Java constant, or a dynamic prefix needs explicit skip handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRBFConfigFields.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRenewLeaseWithSameINodeId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRenewLeaseWithSameINodeId.java

## Purpose

`TestRenewLeaseWithSameINodeId` verifies that a single Router-facing `DFSClient` can renew leases for multiple files in different namespaces even when the namespace-local inode ids are the same.

## Important APIs, types, and functions

The suite uses `MiniRouterDFSCluster`, `RouterContext`, `RouterConfigBuilder`, `MockResolver`, `DistributedFileSystem`, `FSDataOutputStream`, `HdfsFileStatus`, and `DFSClient` writer tracking. `globalSetUp()` starts a non-HA two-namespace cluster with three datanodes per nameservice, metrics, RPC, and quota enabled.

## Control flow

The test adds mock resolver locations `/ns0` and `/ns1` to different nameservices. It opens two output streams through the same `DistributedFileSystem`, one under each namespace, fetches file status from the underlying client, asserts the two `fileId` values match, and then asserts `getNumOfFilesBeingWritten()` is `2`. Closing both streams should reduce that count to `0`.

## State and persistence behavior

The test creates real files in the mini-cluster and tracks client-side lease-renewer state. The important state key is not just inode id, but the federated file identity that must distinguish namespace plus inode for active writes.

## Dependencies and integration points

This is an integration test for Router path resolution, DFSClient lease renewal, file creation, and open-file accounting across subclusters. It protects behavior where two namespaces can legitimately allocate identical inode ids.

## Risks and test signals

A failure indicates the client is conflating files by inode id alone or leaking writer state after stream close. The test focuses on two files and two namespaces; it does not stress long-running renewer threads beyond checking the in-memory writer count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRenewLeaseWithSameINodeId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouter.java

## Purpose

`TestRouter` validates core Router service lifecycle and basic RPC behavior without a full federated state-store cluster. It checks startup states for different service combinations, RPC shutdown, no-subcluster error paths, router id propagation, disabled metrics, and heartbeat service switches.

## Important APIs, types, and functions

The file uses `Router`, `RouterConfigBuilder`, `RouterServiceState`, Hadoop `Service.STATE`, `MockResolver`, `ActiveNamenodeResolver`, `FileSubclusterResolver`, `DFSClient`, `RemoteMethod`, `RouterRpcServer`, `RouterHeartbeatService`, and `NamenodeHeartbeatService`. `create()` builds a static base `Configuration` with mock resolvers, ephemeral RPC/admin/HTTP ports, and a simulated co-located nameservice.

## Control flow

`testRouterStartup()` is the central helper: instantiate Router, assert `NOTINITED` and `UNINITIALIZED`, initialize, assert `SAFEMODE` or `INITIALIZING` depending on safemode config, start, assert `SAFEMODE` or `RUNNING`, then stop and close. `testRouterService()` applies that helper to admin-only, HTTP-only, RPC-only, safemode, metrics, state store, heartbeat, and all-services configs.

Other tests verify stopping the Router stops `RouterRpcServer`; creating a file and requesting datanode reports with no subclusters return expected errors; `RouterRpcClient.invokeSingle()` includes the router id in exceptions; disabled namenode metrics throw an initialization error; and heartbeat service objects exist or not based on `DFS_ROUTER_HEARTBEAT_ENABLE` and `DFS_ROUTER_NAMENODE_HEARTBEAT_ENABLE`. A default-value test ties namenode heartbeat enablement to the router heartbeat switch when not explicitly configured.

## State and persistence behavior

State is in-memory service state and configuration-driven service composition. No state-store records are persisted. The tests do create ephemeral RPC listeners and clients.

## Dependencies and integration points

This file protects Router lifecycle contracts used by all higher-level RBF tests. It also verifies error contracts for empty topology and heartbeater initialization logic.

## Risks and test signals

The strongest signals are service-state transitions and absence/presence of subservices. Because the cluster is mocked, it does not validate real membership, mount-table lookup, or end-to-end data operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdmin.java

## Purpose

`TestRouterAdmin` tests the programmatic Router admin protocol through `RouterClient`, `MountTableManager`, `NameserviceManager`, and `RouterAdminServer`. It focuses on state-store mutations for mount-table and disabled-nameservice records plus permission checks around nameservice management.

## Important APIs, types, and functions

The class uses `StateStoreDFSCluster`, `RouterContext`, `StateStoreService`, `MountTable`, `MountTableManager`, `NameserviceManager`, `RouterClient`, request/response protocol records, `DisabledNameserviceStoreImpl`, `MountTableStoreImpl`, and `ActiveNamenodeResolver`. `setUpMocks()` uses Mockito spies and reflection to replace the Router RPC server and RPC client so destination validation can return controlled `HdfsFileStatus` maps.

## Control flow

`globalSetUp()` starts a state-store-backed Router with admin and RPC enabled, registers two active nameservices, refreshes caches, and installs mocks. `testSetup()` synchronizes mock mount-table records into the state store before each test and resets the admin client.

Mount-table tests add entries, reject duplicates, preserve read-only and destination order flags, remove entries, update destinations, list all entries, fetch a single entry, and call `RouterAdminServer.verifyFileInDestinations()`. Nameservice tests disable and enable `ns0`, assert disabled set contents, reject unknown nameservices, and exercise authorization by running requests as normal users or kerberos-style superuser principals.

## State and persistence behavior

This suite directly persists and reloads `MountTable` and disabled-nameservice records through the state store. Cache refreshes via `stateStore.loadCache()` are explicit and part of the test contract. Mocked RPC destination checks isolate admin validation from real HDFS paths.

## Dependencies and integration points

It integrates the Router admin RPC server, state-store protocol records, mount-table resolver persistence, disabled nameservice store, active namenode resolver registration, and Hadoop `UserGroupInformation` authorization.

## Risks and test signals

The reflection-based RPC server replacement is brittle if Router internals change. The tests are strong at catching admin protocol and state-store regressions, but they do not exercise the CLI parsing layer; that is covered by `TestRouterAdminCLI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminCLI.java

## Purpose

`TestRouterAdminCLI` is a broad CLI integration suite for `hdfs dfsrouteradmin` behavior. It validates command parsing, output, error messages, state-store effects, permission enforcement, quota operations, safe mode, nameservice control, cache refresh, destination lookup, call queue refresh, dump-state formatting, and batch mount-point addition.

## Important APIs, types, and functions

The test uses `RouterAdmin`, `ToolRunner`, `StateStoreDFSCluster`, `RouterContext`, `RouterClient`, `StateStoreService`, `MountTableManager`, `MountTableResolver`, `MultipleDestinationMountTableResolver`, `MountTable`, `RemoteLocation`, `DestinationOrder`, `RouterQuotaUsage`, `RBFMetrics`, `RouterClientProtocol`, `MockStateStoreDriver`, `MembershipState`, `UserGroupInformation`, `Whitebox`, and Mockito. It captures `System.out` and `System.err` with `ByteArrayOutputStream`.

## Control flow

`globalSetUp()` starts a Router with state store, metrics, admin, RPC, quota, and safemode, registers fake active nameservices, mocks quota calls, and spies the RPC server to avoid real file info checks. Tests then run CLI arrays through `ToolRunner.run(admin, argv)` and reload state-store caches before assertions.

Mount-table coverage includes `-add`, `-addAll`, `-update`, `-rm`, `-ls`, `-ls -d`, normalized trailing slashes, nested mount listing, multiple destinations, destination order variants including `LEADER_FOLLOWER`, read-only, fault-tolerant validation, owner/group/mode defaults and mutations, and permission behavior for owner, group, other, and superuser cases. Quota coverage includes `-setQuota`, `-clrQuota`, storage type quota set/clear, size-string parsing, multi-path clear, and invalid arguments. Safe mode tests cover enter/leave/get, metrics and HA service state, argument validation, and permission checks. Nameservice tests cover enable/disable and disabled-list output. Other commands cover `-refresh`, `-getDestination`, `-refreshCallQueue`, and static `RouterAdmin.dumpStateStore()`.

## State and persistence behavior

The suite persists mount-table, quota, disabled-nameservice, and membership records in the state store and repeatedly forces `MountTableStoreImpl` or `DisabledNameserviceStoreImpl` cache reloads. It also mutates process-global login user and process-global stdout/stderr, restoring them in teardown or finally blocks.

## Dependencies and integration points

This file is the highest-level admin contract for users. It bridges CLI parsing, Router admin RPC, mount-table resolver cache, quota module synchronization, safemode service, metrics, state-store driver serialization, and Hadoop security permissions.

## Risks and test signals

The test is intentionally large and sensitive to exact usage text, output formatting, command aliases, and global login-user state. It catches regressions that lower-level admin tests miss, especially parsing and user-visible errors. The mocked quota and RPC file-info paths mean it validates CLI-to-state-store behavior more than real namenode quota enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminGenericRefresh.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminGenericRefresh.java

## Purpose

`TestRouterAdminGenericRefresh` validates the Router admin generic refresh command, `-refreshRouterArgs`, and the `RefreshRegistry` behavior behind it. It ensures RouterAdmin can dispatch refresh calls to registered handlers, pass variable arguments, combine return codes, and handle exceptions.

## Important APIs, types, and functions

The suite uses `Router`, `RouterAdmin`, `RefreshHandler`, `RefreshRegistry`, `RefreshResponse`, Mockito, and `RouterConfigBuilder().admin().rpc()`. `setUpBeforeClass()` starts a Router and creates an admin client pointed at its config. `setUp()` registers two mock handlers before each test.

## Control flow

Tests cover malformed commands, unknown identifiers, a successful single-handler refresh, variable handler arguments returning codes `2` and `3`, unregistration, unregister return value, multiple handlers registered to one id, merging of multiple non-zero return codes to `-1`, and exception handling that still invokes all registered handlers.

## State and persistence behavior

State is process-local `RefreshRegistry.defaultRegistry()` membership plus Router service lifecycle. There is no state-store persistence. Each test unregisters handler ids after execution to avoid leaking handlers into subsequent tests.

## Dependencies and integration points

The file connects CLI command parsing in `RouterAdmin`, admin RPC to the Router admin server address, and Hadoop IPC generic refresh infrastructure. It is a user-facing operational hook for refreshing components without dedicated command types.

## Risks and test signals

Because the registry is global, missed cleanup can cause cross-test contamination. Failures here signal broken generic refresh dispatch, argument propagation, return-code rules, or exception isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAdminGenericRefresh.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAllResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAllResolver.java

## Purpose

`TestRouterAllResolver` verifies multiple-destination mount-table behavior for destination orders that write directories to all namespaces and distribute files across namespaces. It covers `HASH_ALL`, `RANDOM`, and `SPACE` mount points through real filesystem operations.

## Important APIs, types, and functions

The suite uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterContext`, `FileSystem`, `DistributedFileSystem`, `MountTableManager`, `MountTable`, `DestinationOrder`, state-store add/get mount-table protocol records, and `TestFileTruncate.checkBlockRecovery()`. Helpers include `testAll()`, `assertDirsEverywhere()`, `assertFilesDistributed()`, `createTestFile()`, `appendTestFile()`, `listRecursive()`, and `createMountTableEntry()`.

## Control flow

`setup()` starts a two-namespace non-HA cluster with Router admin and RPC, registers namenodes, creates three mount entries pointing each namespace to the same mount path, and opens Router and namespace filesystems. `testHashAll()`, `testRandomAll()`, and `testSpaceAll()` all call `testAll(path)`.

`testAll()` creates a directory tree and asserts every directory exists in every namespace. It creates files at multiple depths and asserts the federated view sees all files while namespace views split files across subclusters. It then tests append, truncate with block recovery, subtree delete, and final cleanup deletion, checking directory replication and file distribution after each phase.

## State and persistence behavior

Mount-table entries are persisted in the state store and caches are explicitly refreshed. Files and directories are real HDFS mini-cluster data. The expected invariant is directory fanout to all destinations and file placement according to resolver policy.

## Dependencies and integration points

This is an end-to-end integration point for mount-table state, multiple-destination resolution, Router filesystem operations, append/truncate/delete semantics, and namespace-level filesystem consistency.

## Risks and test signals

The distribution assertion only requires each namespace to receive at least one file when files exist; it does not require exact balance. The test is strong at catching operations that fail to propagate directories or delete consistently across namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterAllResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterClientRejectOverload.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterClientRejectOverload.java

## Purpose

`TestRouterClientRejectOverload` validates Router RPC client overload control and related failover metrics. It ensures overloaded Router client pools reject work only when configured, that HA Router clients can spread load, and that no-namenode and communication failures are reported correctly.

## Important APIs, types, and functions

The suite uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `DFSClient`, `ClientProtocol`, `FederationRPCMetrics`, `MiniDFSCluster`, `NameNode`, `simulateSlowNamenode()`, `simulateThrowExceptionRouterRpcServer()`, `transitionClusterNSToStandby()`, `transitionClusterNSToActive()`, `ObjectMapper`, and Java executors/futures.

## Control flow

`setupCluster(overloadControl, ha)` starts a two-nameservice cluster, enables state store, metrics, admin, RPC, and heartbeat, reduces Router client threads to `4`, optionally enables `DFS_ROUTER_CLIENT_REJECT_OVERLOAD`, and starts without datanodes. `testOverloaded()` submits parallel `renewLease()` calls via separate DFS clients, staggers start times, counts overload `StandbyException` remote failures, and asserts expected counts.

`testWithoutOverloadControl()` proves slow namenodes do not cause client overload rejections. `testOverloadControl()` simulates a slow namenode and expects several overload rejections, then verifies an HA client using two Routers distributes operations. `testConnectionNullException()` injects Router RPC connection-null failures and checks failure metrics. `testNoNamenodesAvailable()` and `testNoNamenodesAvailableLongTimeWhenNsFailover()` cover standby-only windows and cache rotation. `testAsyncCallerPoolMetrics()` parses JSON from `getAsyncCallerPool()` while a slow request is active.

## State and persistence behavior

State includes Router RPC metrics, async caller pool counters, namenode HA states, Router state-store cache, and client retry configuration. No durable user data is needed; calls use `renewLease()` and metadata reads.

## Dependencies and integration points

This file integrates overload rejection, asynchronous RPC caller pool sizing, Router HA failover, metrics JSON, simulated slow namenodes, and no-namenode cache recovery.

## Risks and test signals

The concurrency tests are timing sensitive, with tolerated overload ranges. They are strong signals for thread-pool saturation behavior and metrics regressions, but can be affected by scheduler timing on slow test hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterClientRejectOverload.java -->
