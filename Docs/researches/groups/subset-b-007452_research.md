# Research Report: subset-b-007452

Grouped worker report for Hadoop HDFS Router Based Federation test fixtures and tests. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockNamenode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockNamenode.java

## Purpose
`MockNamenode` is a test fixture that exposes a Mockito-backed `NamenodeProtocols` implementation through real Hadoop RPC and HTTP endpoints. Router federation tests use it to register lightweight NameNodes with routers without starting full `NameNode` processes.

## Important APIs, Types, and Functions
The public surface includes constructors taking a nameservice id and optional `Configuration`, endpoint accessors `getRPCPort()` and `getHTTPPort()`, `getMock()` for extending the Mockito object, HA helpers `transitionToActive()` and `transitionToStandby()`, lifecycle `stop()`, feature installers `addFileSystemMock()` and `addDatanodeMock()`, and static `registerSubclusters(...)`. Internally it wires `ClientNamenodeProtocolPB`, `NamenodeProtocolPB`, `DatanodeProtocolPB`, and `HAServiceProtocolPB` translators into one `RPC.Server`, and starts an `HttpServer2`.

## Control Flow
Construction initializes namespace identity, creates the Mockito `NamenodeProtocols`, stubs `versionRequest()` and `getServiceStatus()`, then starts RPC and HTTP servers on ephemeral ports. `addFileSystemMock()` installs Mockito answers backed by a `ConcurrentSkipListMap<String,String>` that models path type, handles listing, file info, create, block location, complete, add block, mkdirs, server defaults, and content summary. `addDatanodeMock()` returns the fixture's datanode list and synthetic storage reports. `registerSubclusters()` builds `NamenodeStatusReport` records for each mock NameNode and pushes them into each router's `MembershipNamenodeResolver`.

## State and Persistence
State is in-memory only: `nsId`, `haState`, `dns`, server handles, and the file-system map captured by `addFileSystemMock()`. There is no durable persistence. Registration writes to router resolver/state-store layers through `MembershipNamenodeResolver`, but this fixture itself only owns transient ports and mock behavior.

## Dependencies and Integration Points
The class depends heavily on Mockito, Hadoop IPC/protobuf protocol translators, `HttpServer2`, HDFS protocol records, HA service protocol types, and router membership APIs. It integrates with router registration tests and mock-cluster tests that need real RPC addresses and block tokens carrying a nameservice-specific block pool id.

## Risks and Test Signals
Risks include incomplete HDFS semantics: directory parent creation skips root, file lengths are fixed at 100, block locations are synthetic, and the filesystem map does not enforce all NameNode invariants. RPC/HTTP lifecycle leaks would affect test stability if `stop()` is not called. Strong test signals are endpoint startup, registration of available/unavailable subclusters, and expected failures for missing files through `FileNotFoundException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockNamenode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockResolver.java

## Purpose
`MockResolver` is an in-memory implementation of both `ActiveNamenodeResolver` and `FileSubclusterResolver`. It gives router tests a controllable substitute for state-store-backed membership and mount-table resolution.

## Important APIs, Types, and Functions
The class exposes `addLocation()`, `removeLocation()`, `cleanRegistrations()`, `setDisableRegistration()`, namespace disable helpers, `registerNamenode()`, `getNamespaces()`, `getDestinationForPath()`, `getMountPoints()`, and `getDefaultNamespace()`. `MockNamenodeContext` implements `FederationNamenodeContext` with RPC, service, lifeline, web, nameservice, namenode, state, and modification timestamp fields.

## Control Flow
Mounts are stored by source path. Destination lookup sorts mount keys in reverse order and uses the first prefix match, appending unmatched path suffixes to each `RemoteLocation`. Namenode registration converts a `NamenodeStatusReport` into `MockNamenodeContext`, inserts or replaces by `getNamenodeKey()`, aliases the same list under both nameservice and block-pool ids, and sorts by `NamenodePriorityComparator`. State update methods find a matching RPC address and resort the nameservice list. Observer reads split observer and non-observer memberships, shuffle observers, sort non-observers, and return an immutable list.

## State and Persistence
All state is process-local: `resolver` maps nameservice/block-pool ids to membership lists, `locations` maps mount paths to remote destinations, `namespaces` holds `FederationNamespaceInfo`, and disabled/default namespace flags simulate availability. There is no persistence and no state-store synchronization.

## Dependencies and Integration Points
It integrates with router tests through the same resolver interfaces as production resolvers. Constructors accept `Configuration`, `StateStoreService`, or `Router` for dependency-injection compatibility but ignore them. It depends on `RemoteLocation`, `PathLocation`, `NamenodeStatusReport`, namespace info records, and Hadoop `Time`.

## Risks and Test Signals
`removeLocation()` removes the entire mount key before removing the target from the old list, which is intentionally simple but can surprise tests with multi-destination mounts. `getNamenodesForBlockPoolId()` assumes a non-null list. The path matching is prefix-based, so tests relying on exact path component boundaries should use the production resolver. Test signals are deterministic registration ordering, disabled namespace filtering, default namespace empty-string behavior, and path-to-remote suffix translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/RouterConfigBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/RouterConfigBuilder.java

## Purpose
`RouterConfigBuilder` is a fluent test helper for constructing router `Configuration` objects with selected services enabled. It keeps test setup compact and ensures test routers bind to ephemeral local ports.

## Important APIs, Types, and Functions
The builder controls RPC, admin, HTTP, heartbeat, local heartbeat, state store, metrics, quota, safemode, cache refresh, and federation rename behavior. It exposes paired boolean setters such as `rpc(boolean)` and convenience enablers such as `rpc()`, `stateStore()`, `metrics()`, `quota()`, and `safemode()`. `set(String,String)` records arbitrary extra configuration.

## Control Flow
Callers set flags fluently, then `build()` writes the matching `RBFConfigKeys` into the underlying `Configuration`. RPC, admin, and HTTP services get `127.0.0.1:0` advertised addresses and `0.0.0.0` bind hosts when enabled. `stateStore()` also resets the state-store driver class to the test driver from `FederationStateStoreTestUtils`.

## State and Persistence
The builder holds mutable booleans, the selected `RouterRenameOption`, an extra key-value map, and the target `Configuration`. `build()` mutates and returns that same configuration; repeated builds reuse accumulated state.

## Dependencies and Integration Points
It depends on router config keys, `RouterFederationRename.RouterRenameOption`, the state-store test utility, and `StateStoreDriver`. It is used throughout router, fairness, metrics, resolver, and disable-nameservice tests to start only the router services a test needs.

## Risks and Test Signals
Because the builder mutates its `Configuration`, sharing one builder across tests can leak settings. `all()` does not enable quota or cache refresh, so tests needing those must opt in. Test signals are router startup with expected service endpoints, state-store-backed resolver availability when `stateStore()` is used, and metrics/JMX visibility when `metrics()` and `http()` are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/RouterConfigBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/StateStoreDFSCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/StateStoreDFSCluster.java

## Purpose
`StateStoreDFSCluster` extends `MiniRouterDFSCluster` with state-store-backed router resolver configuration and helpers for creating membership and mount-table fixtures. It is the main integration-test cluster for Router Based Federation tests that exercise state-store behavior.

## Important APIs, Types, and Functions
Constructors choose HA mode, numbers of nameservices and NameNodes, heartbeat/cache intervals, and optional file resolver class. Fixture methods include `createTestRegistration(StateStoreService)`, `createTestMountTable(StateStoreService)`, `generateMockMountTable()`, and `getRouterClientConf()`.

## Control Flow
Construction delegates to `MiniRouterDFSCluster`, creates a state-store test configuration, sets `FEDERATION_NAMENODE_RESOLVER_CLIENT_CLASS` to `MembershipNamenodeResolver`, sets `FEDERATION_FILE_RESOLVER_CLIENT_CLASS` to the requested file resolver, and adds those overrides to routers. Registration fixtures iterate the mini-cluster NameNode contexts and synchronize synthetic `MembershipState` records. Mount table fixtures create one direct federated path per nameservice plus a root mount to the first nameservice, then refresh caches.

## State and Persistence
The cluster state is inherited from `MiniRouterDFSCluster`; this class writes membership and mount-table records into the provided `StateStoreService` using `synchronizeRecords()`. It does not maintain a separate durable store beyond the configured test driver.

## Dependencies and Integration Points
It depends on federation state-store test utilities, `MembershipNamenodeResolver`, `MountTableResolver`, `MountTable`, `MembershipState`, `DFSTestUtil`, and HDFS HA client configuration keys. `getRouterClientConf()` integrates with Hadoop HA client failover by advertising all router RPC ports under a synthetic nameservice `fed`.

## Risks and Test Signals
The fixture assumes nameservice ordering is stable, especially for the root mount to index 0. A typo in the constructor parameter name is harmless but visible. Tests using this class signal state-store integration by successfully loading router resolver caches, resolving generated federated paths, and failing over client RPCs across routers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/StateStoreDFSCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestProportionRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestProportionRouterRpcFairnessPolicyController.java

## Purpose
This JUnit 5 test validates `ProportionRouterRpcFairnessPolicyController`, which allocates router RPC permits per nameservice by configured or default proportions of the total handler count.

## Important APIs, Types, and Functions
Tests call `FederationUtil.newFairnessPolicyController(conf)`, then exercise the `RouterRpcFairnessPolicyController` API: `acquirePermit(ns)`, `releasePermit(ns)`, and timeout behavior. Config inputs include `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_MONITOR_NAMENODE`, `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, and `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`.

## Control Flow
`createConf()` installs the proportional controller class and a monitored NameNode list containing `ns1` and `ns2`. Tests assert default 10% allocation, a custom `ns1=0.5` allocation, acquire timeout duration after all permits are consumed, minimum one permit for zero proportion, support for configured totals greater than router handler count, and transparent expansion for unregistered namespaces that receive default permits.

## State and Persistence
State is confined to controller semaphore/permit state inside each test-created controller. No cluster, state store, or persistent records are used.

## Dependencies and Integration Points
The test depends on `HdfsConfiguration`, router fairness config keys, `RouterRpcFairnessConstants.CONCURRENT_NS`, and `Time.monotonicNow()` for timeout assertions. It integrates indirectly with production controller construction through `FederationUtil`.

## Risks and Test Signals
The timeout assertions depend on wall-clock scheduling and only check lower bounds. The proportional controller intentionally allows aggregate namespace permits to exceed total handlers, so regressions would show as unexpected failures in overcommit and unregistered namespace cases. Passing tests signal correct default proportioning, configured override parsing, release semantics, and cluster expansion friendliness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestProportionRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterAsyncRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterAsyncRpcFairnessPolicyController.java

## Purpose
This test verifies `RouterAsyncRpcFairnessPolicyController`, the fairness controller for async RPC call permits. It focuses on per-nameservice async permit limits and the special behavior of the concurrent namespace.

## Important APIs, Types, and Functions
The tests use `DFS_ROUTER_ASYNC_RPC_MAX_ASYNCCALL_PERMIT_KEY`, `DFS_ROUTER_ASYNC_RPC_MAX_ASYNC_CALL_PERMIT_DEFAULT`, `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, `DFS_ROUTER_MONITOR_NAMENODE`, `FederationUtil.newFairnessPolicyController()`, `getAvailableHandlerOnPerNs()`, `acquirePermit()`, and `releasePermit()`.

## Control Flow
`createConf()` installs `RouterAsyncRpcFairnessPolicyController` and sets the per-namespace async permit count. The main allocation test consumes 30 permits for `ns1` and `ns2`, while `CONCURRENT_NS` is not bounded by those permits and continues to acquire successfully. Timeout and invalid-permit tests check that exhausted namespaces wait at least the configured interval and that zero or negative config falls back to the default with an initialization log message.

## State and Persistence
Only in-memory controller permit state is exercised. There is no router process or persistent state-store interaction.

## Dependencies and Integration Points
The test depends on Hadoop configuration, `GenericTestUtils.LogCapturer`, SLF4J logger capture, and the fairness controller factory. It integrates with metrics/JMX indirectly through `getAvailableHandlerOnPerNs()` JSON formatting expectations.

## Risks and Test Signals
String equality on JSON-like maps is order-sensitive and can catch intentional formatting or ordering changes. Timeout checks are scheduler-sensitive but use a lower-bound assertion. Passing tests signal bounded async per-namespace permits, unbounded concurrent namespace handling, fallback defaults, log messages, and availability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterAsyncRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterHandlersFairness.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterHandlersFairness.java

## Purpose
`TestRouterHandlersFairness` is an integration test for router RPC fairness enforcement under real `DFSClient` calls. It verifies that configured controllers reject overloaded requests and release permits on exceptional paths.

## Important APIs, Types, and Functions
The parameterized test matrix covers `StaticRouterRpcFairnessPolicyController` and `ProportionRouterRpcFairnessPolicyController`. It uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterRpcClient`, `DFSClient`, `ClientProtocol`, `RemoteMethod`, `RemoteLocation`, `getAcceptedPermitForNs()`, `getRejectedPermitForNs()`, and `getRouterRpcFairnessPolicyController()`.

## Control Flow
`setupCluster()` starts a two-nameservice state-store cluster with RPC enabled, optional fairness controller class configured, a short acquire timeout, and no datanodes. `startLoadTest()` runs concurrent fan-out (`renewLease`) and sequential (`getFileInfo`) operations. When fairness is enabled, the test pre-acquires all relevant permits to force overload, checks `StandbyException` messages and rejected metrics, releases permits, then verifies later calls succeed and accepted metrics advance. `testReleasedWhenExceptionOccurs()` injects a mocked `ActiveNamenodeResolver` into `RouterRpcClient` so resolver failures occur after acquisition paths are entered, then confirms semaphore counts return to their original values.

## State and Persistence
State lives in the mini cluster, router RPC client permit counters, fairness controller semaphores, and state-store-backed resolver data. No durable files are written.

## Dependencies and Integration Points
This class exercises production routing paths across `RouterRpcServer`, `RouterRpcClient`, active namenode resolver ordering, client protocol RPCs, and metrics counters. It depends on reflection to replace a private resolver field for exception-path testing.

## Risks and Test Signals
The test uses real threads, sockets, and timeouts; failures can be timing-related. Reflection against `RouterRpcClient.namenodeResolver` is brittle under refactors. Strong signals include overload exceptions containing "is overloaded for NS", accepted/rejected metric deltas matching operation counts, and permit availability unchanged after resolver exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterHandlersFairness.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRefreshFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRefreshFairnessPolicyController.java

## Purpose
This integration test validates dynamic replacement of a router's fairness policy controller, including invalid class handling, concurrent refresh requests, and changed handler allocations after refresh.

## Important APIs, Types, and Functions
The test uses `RouterRpcClient.refreshFairnessPolicyController(Configuration)`, `getRouterRpcFairnessPolicyController()`, `StaticRouterRpcFairnessPolicyController`, `NoRouterRpcFairnessPolicyController`, `DFS_ROUTER_FAIRNESS_POLICY_CONTROLLER_CLASS`, `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`, `RemoteMethod`, and router RPC metrics for accepted/rejected permits.

## Control Flow
Each test starts a two-nameservice `StateStoreDFSCluster` with state store and RPC enabled, static fairness configured, nine handlers, and metrics enabled. Invalid refresh tests set nonexistent or non-implementing classes and expect the old static controller class name to be returned. Successful refresh switches from static to no-fairness. The concurrent test starts 100 threads that refresh the controller and counts shutdown log messages. The handler-change test blocks mocked remote invocations, refreshes configured ns0/ns1 permit counts, waits for old calls to finish, then issues new calls and checks accepted/rejected metrics reflect both old and new allocations.

## State and Persistence
State is in the running router's RPC client controller reference, active invocation threads, and metrics counters. The state store only backs cluster membership and mount resolution.

## Dependencies and Integration Points
The test integrates controller construction, shutdown, router RPC invocation, metrics, and subject-preserving threads. It uses Mockito to delay `RouterRpcClient.invokeMethod()` and `GenericTestUtils.LogCapturer` to inspect controller shutdown logs.

## Risks and Test Signals
The concurrent refresh count assumes every refresh creates and shuts down a controller; implementation changes may alter log count while remaining correct. Sleeps around mocked invocations can be timing-sensitive. Passing tests signal safe fallback on invalid classes, class-change success, no controller leaks during concurrent refresh, and immediate application of new per-namespace permit limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRefreshFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRpcFairnessPolicyController.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRpcFairnessPolicyController.java

## Purpose
This unit test validates `StaticRouterRpcFairnessPolicyController`, which allocates a fixed number of router handler permits across monitored nameservices and the concurrent-operation namespace.

## Important APIs, Types, and Functions
It constructs controllers through `FederationUtil.newFairnessPolicyController()`, uses `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_MONITOR_NAMENODE`, `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`, and `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, and asserts `acquirePermit()`, `releasePermit()`, and `getAvailableHandlerOnPerNs()` behavior.

## Control Flow
Default tests divide 30 handlers equally among `ns1`, `ns2`, and `concurrent`; 31 handlers allocate the extra permit to concurrent. Preconfigured handler tests reserve `ns1=30` and split remaining handlers. Error tests verify insufficient total handlers or low preconfigured counts log `StaticRouterRpcFairnessPolicyController.ERROR_MSG`. Timeout tests exhaust `ns1` and assert a failed acquire waits at least 100 ms. Availability tests check JSON-like reporting before and after one acquire.

## State and Persistence
Controller state is in-memory semaphores per namespace. No router cluster or state store is started.

## Dependencies and Integration Points
The test depends on `HdfsConfiguration`, the controller factory, SLF4J log capture, and `RouterRpcFairnessConstants.CONCURRENT_NS`. It is a fast validation layer below the router integration tests.

## Risks and Test Signals
JSON string assertions are sensitive to map ordering. Error tests catch logs after swallowing expected construction exceptions, so they validate operator-facing diagnostics as well as validation behavior. Passing tests signal correct static allocation, leftover handling, configured overrides, timeout waits, release semantics, and no-fairness fallback reporting as `N/A`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/fairness/TestRouterRpcFairnessPolicyController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestMetricsBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestMetricsBase.java

## Purpose
`TestMetricsBase` is a reusable JUnit base for RBF metrics tests. It starts a router with state store, metrics, and HTTP enabled, seeds membership, mount-table, and router records, and exposes fixture accessors to subclasses.

## Important APIs, Types, and Functions
Setup uses `RouterConfigBuilder().stateStore().metrics().http()`, `Router`, `StateStoreService`, `MembershipStore`, and `RouterStore`. Fixture methods include `createFixtures()`, `getNameserviceStateMap(JSONObject)`, `refreshNamenodeRegistration()`, and protected getters for active/standby memberships, mount tables, routers, nameservices, router, and state store.

## Control Flow
`setupBase()` initializes and starts the router once per test instance, waits for the state store, clears all records, creates two nameservices with active and standby membership heartbeats, synchronizes mock mount-table records, adds two mock router heartbeats, refreshes caches, and pauses for metrics visibility. `testObserverMetrics()` adds an observer membership for `ns0`, reloads state-store and resolver caches, then asserts the nameservice JSON reports `OBSERVER`.

## State and Persistence
The state-store test driver holds `MembershipState`, `MountTable`, and `RouterState` records. Router caches and `MembershipNamenodeResolver` caches are explicitly refreshed. Teardown stops and closes the router.

## Dependencies and Integration Points
The class integrates federation state-store protocol requests, router metrics, router store, membership store, JSON parsing, and resolver cache loading. It is the foundation for `TestRBFMetrics` and also directly tests observer metrics behavior.

## Risks and Test Signals
The `Thread.sleep(1000)` after cache refresh is a timing buffer that can mask slow async registration. Fixture records use utility-generated stats, so metric expectations depend on those utilities. Passing tests signal state-store records are visible to metrics, observer state can win nameservice reporting, and refreshed membership registrations update both store and resolver caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestMetricsBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestNameserviceRPCMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestNameserviceRPCMetrics.java

## Purpose
This test verifies per-nameservice RPC metrics emitted by router proxy operations. It checks both single-namespace operations and concurrent fan-out operations.

## Important APIs, Types, and Functions
The test uses `MiniRouterDFSCluster`, `RouterConfigBuilder().metrics().rpc().quota()`, `MockResolver`, `FileSystem.listStatus()`, `RouterRpcServer.setBalancerBandwidth()`, and metrics assertions against `NameserviceRPCMetrics.NAMESERVICE_RPC_METRICS_PREFIX`.

## Control Flow
`globalSetUp()` starts a non-HA federated mini-cluster with two subclusters and three datanodes per nameservice, starts routers with metrics and RPC enabled, then registers NameNodes. Each test setup installs mock locations, clears files, creates test directories, obtains router filesystem/router references, and adds explicit `/target-ns0` and `/target-ns1` mounts. `testProxyOp()` lists each target path and verifies only that nameservice's `ProxyOp` counter increments. `testProxyOpCompleteConcurrent()` records ns0, ns1, and concurrent counters, calls `setBalancerBandwidth()`, and expects all three to increment by one.

## State and Persistence
Cluster filesystem state is reset before each test through mini-cluster helpers. Metrics are process-local Hadoop metrics counters. Resolver mount state is in the router's `MockResolver`.

## Dependencies and Integration Points
This class integrates router RPC metrics, the mock file resolver, mini DFS clusters, router-to-NameNode proxy calls, and Hadoop metrics test helpers. It validates metrics source naming by nameservice id and by the special `concurrent` source.

## Risks and Test Signals
Metrics counters can be cumulative across tests, so the concurrent test captures baselines while the single-op test asserts absolute values after setup reset. The unused `nnFS` field is benign. Passing tests signal correct attribution of proxy operations to the target nameservice and correct accounting for fan-out operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestNameserviceRPCMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRBFMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRBFMetrics.java

## Purpose
`TestRBFMetrics` validates the router federation metrics exposed both as JMX beans and as `RBFMetrics` data-source JSON. It covers cluster aggregates, mount table rows, NameNode rows, nameservice rows, router rows, and large capacity values.

## Important APIs, Types, and Functions
The class extends `TestMetricsBase`. It uses JMX bean names `Hadoop:service=Router,name=FederationState` and `Hadoop:service=Router,name=Router`, interfaces `FederationMBean` and `RouterMBean`, `RBFMetrics.getMountTable()`, `getNamenodes()`, `getNameservices()`, `getRouters()`, `MembershipStats`, `MountTable`, `RouterState`, and `StateStoreVersion`.

## Control Flow
JMX and direct data-source tests call common validators. Mount-table validation parses a JSON array and matches entries by source path. NameNode validation iterates JSON objects and compares state, datanode counts, block counts, and addresses to active/standby membership fixtures. Nameservice validation expects one active NameNode per nameservice and compares aggregate capacity and maintenance stats. Router validation matches router JSON by address and checks status, compile/version metadata, timestamps, and state-store version formatting. `testCapacity()` sets each active membership's total and available space to `Long.MAX_VALUE`, refreshes registrations, and verifies BigInteger accessors preserve the sum while long accessors overflow.

## State and Persistence
State comes from `TestMetricsBase` fixtures in the state store and from modified membership stats written back through `refreshNamenodeRegistration()`. Metrics read router caches after explicit refreshes.

## Dependencies and Integration Points
The test integrates JMX lookup, JSON serialization, router metrics aggregation, state-store membership/router/mount records, and capacity overflow handling. It depends on `ListUtils.union()` to search active and standby fixture records.

## Risks and Test Signals
JSON object order is not assumed except where counts are checked. There is a notable assertion mapping `numOfEnteringMaintenanceDataNodes` to stale datanodes in nameservice stats, which documents current behavior and would catch changes. Passing tests signal JMX registration, JSON field completeness, active-membership aggregation, router heartbeat visibility, and overflow-safe capacity reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRBFMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRouterClientMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRouterClientMetrics.java

## Purpose
This test verifies router client activity metrics for individual client protocol operations and their concurrent fan-out variants.

## Important APIs, Types, and Functions
It uses `MiniRouterDFSCluster`, `RouterConfigBuilder().metrics().rpc().quota()`, `MockResolver`, router `FileSystem`, router RPC server methods, and metrics assertions on the `RouterClientActivity` metrics source. Operations include listing, create, get server defaults, set/get quota, renew lease, datanode report, and slow datanode report.

## Control Flow
The class-level setup starts a two-subcluster mini-router cluster with datanodes, routers, and registered NameNodes. Per-test setup installs mock locations, deletes files, creates NameNode test directories, gets the first router filesystem, and adds an additional root mount to the second nameservice so root operations fan out. Each test invokes one router operation and asserts the expected operation counter; fan-out operations assert both the per-NameNode count of two and the concurrent counter of one.

## State and Persistence
Filesystem and resolver state are reset per test. Metrics counters are held in Hadoop's in-process metrics system. No external persistence is involved.

## Dependencies and Integration Points
The test integrates the client-facing filesystem API, direct `RouterRpcServer` calls, `MockResolver` multi-destination root routing, quota support, and Hadoop metrics test helpers.

## Risks and Test Signals
Absolute counter assertions assume the metrics source is clean enough after setup for each method. Fan-out counts depend on the extra root mount to both nameservices. Passing tests signal that router metrics names are wired for both simple and concurrent versions of each operation and that direct RPC-server calls record client activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRouterClientMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestFederationNamespaceInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestFederationNamespaceInfo.java

## Purpose
This small regression test verifies `FederationNamespaceInfo` ordering/equality behavior when stored in a `TreeSet`, specifically for HDFS-15900.

## Important APIs, Types, and Functions
The test constructs two `FederationNamespaceInfo` instances with the same nameservice id but different block-pool and cluster/name fields, inserts them into a `TreeSet`, and uses AssertJ `assertThat(set).hasSize(2)`.

## Control Flow
`testHashCode()` first adds an instance with an empty block-pool id, then adds another with `bp1` but the same `ns1`. The assertion requires comparison/hash semantics to preserve both records rather than collapsing by nameservice alone.

## State and Persistence
All state is local to the test method. There is no resolver or state-store interaction.

## Dependencies and Integration Points
The test depends on Java collection semantics and the `FederationNamespaceInfo` comparable/hash implementation used by namespace sets in resolvers such as `MockResolver` and state-store-backed membership resolvers.

## Risks and Test Signals
The test is narrow by design. Passing it signals that empty block-pool ids do not cause namespace records to compare equal incorrectly, protecting namespace discovery and disabled-namespace filtering from losing records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestFederationNamespaceInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestInitializeMountTableResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestInitializeMountTableResolver.java

## Purpose
This test validates `MountTableResolver` default nameservice initialization from configuration, including explicit disablement.

## Important APIs, Types, and Functions
It constructs `MountTableResolver` with `Configuration` values for `DFS_ROUTER_DEFAULT_NAMESERVICE`, `DFS_ROUTER_DEFAULT_NAMESERVICE_ENABLE`, `DFS_NAMESERVICE_ID`, and `DFS_NAMESERVICES`, then checks `getDefaultNamespace()` and `isDefaultNSEnable()`.

## Control Flow
Tests cover no configured default, an explicitly empty default string, a router default nameservice value, and a disabled default namespace even when HDFS nameservice settings are present. Empty string is expected to disable default namespace routing.

## State and Persistence
Only resolver initialization state is used. There is no mount table, cache mutation, or state-store persistence.

## Dependencies and Integration Points
The test depends on HDFS client configuration keys and router configuration keys. It protects router startup behavior for mount-table resolution before any state-store entries are loaded.

## Risks and Test Signals
The class only tests initialization, not later changes through setters. Passing tests signal that missing or disabled defaults produce an empty namespace, explicit empty defaults disable fallback routing, and configured router defaults are honored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestInitializeMountTableResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMountTableResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMountTableResolver.java

## Purpose
`TestMountTableResolver` is the main unit test for single-destination `MountTableResolver` behavior. It verifies path normalization, longest-prefix destination resolution, mount listing, entry removal/update, default nameservice fallback, cache behavior, and scalability.

## Important APIs, Types, and Functions
The tests use `MountTableResolver.addEntry()`, `removeEntry()`, `refreshEntries()`, `getDestinationForPath()`, `getMountPoint()`, `getMountPoints()`, `getMounts()`, `getCacheSize()`, `getLocCacheAccess()`, `getLocCacheMiss()`, and `MountTable.newInstance()`. Config keys include `FEDERATION_MOUNT_TABLE_MAX_CACHE_SIZE`, `FEDERATION_MOUNT_TABLE_CACHE_ENABLE`, and `DFS_ROUTER_DEFAULT_NAMESERVICE`.

## Control Flow
`setupMountTable()` creates a resolver with max cache size 10, default namespace `0`, root mapping, nested `/user` and `/usr/bin` mappings, read-only `/readonly`, and multi-destination `/multi`. Destination tests assert suffix rewriting for files/folders and consecutive slash normalization. Default namespace tests remove root and check fallback, then disable fallback and expect an IOException for root. Listing tests verify virtual child names and records below paths. Removal tests distinguish real subtree, virtual node, and leaf removal. Refresh/update tests replace entries and assert old cache/data invalidation. Scalability adds 100,000 flat entries, 1,000 deep entries, and 100,000 deep/wide entries. Cache tests cover disabled local cache, cache size cap, location cache update after refresh, child invalidation after adding a more specific mount, and hit/miss counters.

## State and Persistence
All resolver state is in memory: mount tree, default namespace flags, local location cache, and cache counters. There is no state-store backing in this unit test.

## Dependencies and Integration Points
The test integrates `MountTable` records, `PathLocation`, `RemoteLocation`, router config keys, and `GenericTestUtils` exception assertions. It guards behavior used by router path resolution before RPC fan-out.

## Risks and Test Signals
The scalability test is intentionally heavy and can be runtime-sensitive. `testMuiltipleDestinations` documents that this resolver rejects multi-destination mounts; those belong to `MultipleDestinationMountTableResolver`. Passing tests signal correct trie semantics, normalized paths, cache invalidation, read-only metadata retention, and safe fallback/default namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMountTableResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMultipleDestinationResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMultipleDestinationResolver.java

## Purpose
This test validates `MultipleDestinationMountTableResolver`, especially destination ordering strategies for mounts with more than one subcluster.

## Important APIs, Types, and Functions
The setup uses `MultipleDestinationMountTableResolver`, `MountTable.setDestOrder()`, `DestinationOrder` values `HASH`, `HASH_ALL`, `LOCAL`, `RANDOM`, and `LEADER_FOLLOWER`, `PathLocation`, `RemoteLocation`, `PathLocation.prioritizeDestination()`, and `HashResolver.extractTempFileName()`.

## Control Flow
Setup registers single-destination `/tmp`, default multi-destination `/`, hash mounts `/hash` and `/hashall`, local and random mounts, read-only multi-destination `/readonly`, and a leader-follower mount with insertion order. Tests assert even distribution for hash-all and random paths, first-level stickiness for hash, hard-coded hash-all examples, single-destination passthrough, same-subcluster resolution for files below a chosen parent directory, temp-file-name extraction for copy/speculation patterns, read-only hashing behavior, leader-follower first destination selection, local default selection, random resolver variability across repeated calls, and explicit destination prioritization.

## State and Persistence
State is the in-memory mount table and resolver cache. There is no router, membership store, or filesystem persistence in this test.

## Dependencies and Integration Points
The test integrates all built-in destination-order resolvers through the multiple-destination resolver. It is a behavioral contract for router routing decisions when a mount table entry has multiple `RemoteLocation` targets.

## Risks and Test Signals
Hash expectations encode deterministic hashing details and may need updates if the hash algorithm changes. Random distribution tests depend on probability but use enough iterations to expect all three subclusters. Passing tests signal stable destination selection, parent-child stickiness where required, temp-file canonicalization, and correct ordering delegation for local/random/leader-follower modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMultipleDestinationResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestNamenodeResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestNamenodeResolver.java

## Purpose
`TestNamenodeResolver` validates `MembershipNamenodeResolver`, the state-store-backed active NameNode resolver used by routers to choose NameNodes by nameservice and block pool.

## Important APIs, Types, and Functions
The test uses `StateStoreService`, `MembershipNamenodeResolver`, `NamenodeStatusReport`, `FederationNamenodeContext`, `FederationNamenodeServiceState`, `registerNamenode()`, `getNamenodesForNameserviceId()`, `getNamenodesForBlockPoolId()`, `updateActiveNamenode()`, and state-store expiration config `FEDERATION_STORE_MEMBERSHIP_EXPIRATION_MS`.

## Control Flow
Class setup creates a test state store with five-second membership expiration and a resolver with router id. Each test loads the driver and clears membership records. `testShuffleObserverNNs()` registers active, standby, then observer NameNodes, refreshes caches, asserts observer-first ordering when observer reads are requested, and loops until observer ordering is shuffled. `testStateStoreDisconnected()` closes the store driver, refreshes caches, verifies lookups return no cached data, and expects `StateStoreUnavailableException` on registration. `testRegistrationExpired()` verifies an active record disappears after expiration and reappears after heartbeat. `testRegistrationNamenodeSelection()` exercises active-vs-standby-vs-unavailable ordering, expiration, and newest-active/newest-standby selection. The final tests update a standby NameNode to active by RPC address, including an IP address case.

## State and Persistence
Membership records are persisted in the state-store test driver and loaded into resolver caches. Expiration is time-based and requires sleeps plus cache refreshes.

## Dependencies and Integration Points
The test integrates federation state-store utilities, resolver cache refresh, HA service states, RPC address parsing, and router membership selection policy. It protects router failover and observer-read behavior.

## Risks and Test Signals
Tests use real sleeps beyond the expiration interval, so they are slow and timing-sensitive. `verifyFirstRegistration()` expects null for zero results, documenting resolver behavior when caches are empty. Passing tests signal correct priority ordering, observer shuffling, state-store outage handling, expiry cleanup, and in-cache active-state promotion after successful RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestNamenodeResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestAvailableSpaceResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestAvailableSpaceResolver.java

## Purpose
This test validates `AvailableSpaceResolver`, which orders multiple destinations by available nameservice space with a configurable balancer preference.

## Important APIs, Types, and Functions
It uses `AvailableSpaceResolver`, `SubclusterAvailableSpace`, `SubclusterSpaceComparator`, `MultipleDestinationMountTableResolver`, `DestinationOrder.SPACE`, mocked `Router`, `StateStoreService`, `MembershipStore`, `GetNamenodeRegistrationsResponse`, `MembershipState`, and `MembershipStatsPBImpl`. Config keys are `BALANCER_PREFERENCE_KEY` and `BALANCER_PREFERENCE_DEFAULT`.

## Control Flow
`mockAvailableSpaceResolver()` builds mocked membership data for ten subclusters with available space 0 through 9, installs an available-space resolver into a multiple-destination mount table, and creates a `/space` mount with `SPACE` order. Tests with preference `1.0` expect subcluster9 for root and subdir paths. Default preference tests retry until a non-max subcluster appears, proving randomness/probabilistic balancing. Comparator tests sort synthetic subclusters for preference 0, 1, 0.5, default, and invalid values, checking ascending/descending/partial ordering and exception messages. `testChooseFirstNamespace()` asserts the default location is the first ordered namespace.

## State and Persistence
All state is mocked or in-memory. No real state-store driver is used.

## Dependencies and Integration Points
The test integrates destination ordering with membership stats fetched from the membership store. It protects routing behavior for space-balanced multi-destination mounts.

## Risks and Test Signals
The default-preference test is probabilistic and could theoretically retry only max selections, though the retry count reduces that risk. Comparator partial-order assertions are intentionally loose for randomized preferences. Passing tests signal correct highest-space preference, valid range enforcement, and resolver integration with `PathLocation` default destination selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestAvailableSpaceResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLeaderFollowerResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLeaderFollowerResolver.java

## Purpose
This test verifies `LeaderFollowerResolver`, which preserves a configured leader destination as first choice for a multi-destination mount.

## Important APIs, Types, and Functions
The test uses `LeaderFollowerResolver`, `MultipleDestinationMountTableResolver`, `DestinationOrder.LEADER_FOLLOWER`, `MountTable`, `PathLocation`, and `RemoteLocation`.

## Control Flow
It creates a mocked router, constructs a multiple-destination resolver, registers the leader-follower ordering resolver, and adds `/local` with a `LinkedHashMap` destination order of subcluster2, subcluster0, subcluster1. Resolving `/local/file0.txt` must return subcluster2 as the first destination.

## State and Persistence
All state is local to the resolver and mount entry. There is no membership data, state store, or persistent filesystem.

## Dependencies and Integration Points
The test depends on insertion-order preservation through `LinkedHashMap` and destination ordering delegation from `MultipleDestinationMountTableResolver`.

## Risks and Test Signals
The test is intentionally narrow and does not inspect follower order beyond the first destination. Passing it signals that leader-follower mounts preserve the configured leader as the default route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLeaderFollowerResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLocalResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLocalResolver.java

## Purpose
This test validates `LocalResolver`, which prioritizes the subcluster whose NameNode address matches the client locality.

## Important APIs, Types, and Functions
It uses mocked `Router`, `StateStoreService`, and `MembershipStore`, `GetNamenodeRegistrationsResponse`, `MembershipState.newInstance()`, `FederationNamenodeServiceState.ACTIVE`, `LocalResolver.getClientAddr()`, `MultipleDestinationMountTableResolver`, and `DestinationOrder.LOCAL`.

## Control Flow
The test creates three active membership records mapping client0/client1/client2 addresses to subcluster0/subcluster1/subcluster2. It spies `LocalResolver` so `getClientAddr()` returns a mutable `StringBuilder` value. A `/local` multi-destination mount is added with LOCAL ordering. Resolution defaults to subcluster0 for unknown clientX, then returns subcluster2, subcluster1, and subcluster0 as the mocked client changes.

## State and Persistence
State is mocked membership data, the mutable client string, and the in-memory mount table. There is no real router state store.

## Dependencies and Integration Points
The test integrates `LocalResolver` with membership-store lookup and the multiple-destination resolver. It protects client-local routing decisions for multi-subcluster mount entries.

## Risks and Test Signals
The test relies on Mockito spying to override network client address discovery. It only tests active memberships and exact host string matching before ports. Passing tests signal that known clients route to their local subcluster and unknown clients fall back to the original/default destination order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLocalResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestConnectionManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestConnectionManager.java

## Purpose
`TestConnectionManager` validates router NameNode connection pooling, cleanup, connection creation failure handling, per-connection concurrency, protocol support, state-id alignment, and duplicate creation suppression.

## Important APIs, Types, and Functions
The class exercises `ConnectionManager`, `ConnectionPool`, `ConnectionPoolId`, `ConnectionContext`, `ConnectionManager.ConnectionCreator`, `ConnectionPool.newConnection()`, `getConnection()`, `cleanup()`, `getPools()`, `getNumCreatingConnections()`, and alignment through `RouterFederatedStateProto` on `Server.Call`. It covers `ClientProtocol` and `NamenodeProtocol`.

## Control Flow
Setup creates a `ConnectionManager`, adds static host resolution for `nn1`, and starts the manager. Cleanup tests seed pools with total/active connections and assert idle cleanup respects minimum active ratio and minimum size. Concurrency tests set max concurrency per connection, consume slots, detect unusable active connections when saturated, then add a new connection. Failure tests verify unresolvable hosts do not kill `ConnectionCreator` and that eager bad pool construction throws. Basic get-connection tests exhaust idle connections for client and namenode protocols. State-id tests set thread-local `Server.Call` federated namespace state and assert the pool alignment context advances from state id 1 to 2. Duplicate-creation tests close the background creator and confirm repeated requests for the same pool only enqueue one creation, while another user creates a second. Unsupported protocol tests assert the error message.

## State and Persistence
State is in-memory connection pools keyed by UGI, NameNode address, and protocol; per-connection active counts; creator queue state; and thread-local server call state. No durable persistence is involved.

## Dependencies and Integration Points
The test integrates Hadoop RPC client creation, UGI identity, network address resolution, router config keys for concurrency and cleanup ratio, and router state-id propagation to NameNode connections.

## Risks and Test Signals
Tests use real connection construction to a statically resolved address and background threads. Identity comparison of UGI in helper checks is intentional because keys are created with the same static instances. Passing tests signal pool cleanup safety, saturation handling, robust async creation, protocol validation, and correct propagation of federated namespace state ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestConnectionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDFSRouter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDFSRouter.java

## Purpose
This test validates default `DFSRouter` configuration values and cleanup of stale namespace state-id context entries when a nameservice is disabled/expired.

## Important APIs, Types, and Functions
It uses `DFSRouter.getConfiguration()`, FedBalance config keys `SCHEDULER_JOURNAL_URI` and `WORK_THREAD_NUM`, `Router`, `RouterRpcServer`, `RouterStateIdContext`, `MockResolver`, `createNamenodeReport()`, and `FEDERATION_STORE_MEMBERSHIP_EXPIRATION_MS`.

## Control Flow
`testDefaultConfigs()` asserts the scheduler journal URI defaults to `hdfs://localhost:8020/tmp/procedure` and worker threads default to 10. `testClearStaleNamespacesInRouterStateIdContext()` configures a router with mock active/file resolvers, short membership expiration, and safemode disabled; registers two active namespaces; touches both namespace state ids; disables one namespace; verifies the map remains size 2 before router start; starts the router and waits; then asserts the state-id map shrinks to one.

## State and Persistence
State is router configuration, `MockResolver` namespace registrations/disabled set, and the in-memory `RouterStateIdContext` namespace id map. No external persistence is used.

## Dependencies and Integration Points
The test integrates `DFSRouter` defaults, router initialization/startup, mock resolvers, membership expiration config, and the periodic stale namespace cleanup in router RPC state-id tracking.

## Risks and Test Signals
The stale cleanup test uses `Thread.sleep(3000)` around a two-second expiration, so it is timing-sensitive. Passing tests signal expected command-line router defaults and that starting the router activates background cleanup of disabled namespace state ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDFSRouter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableNameservices.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableNameservices.java

## Purpose
`TestDisableNameservices` verifies router behavior when a nameservice is administratively disabled. It checks request skipping, directory listing output, and metrics state reporting.

## Important APIs, Types, and Functions
The class uses `StateStoreDFSCluster`, `RouterConfigBuilder().stateStore().metrics().admin().rpc()`, `RouterClient`, `NameserviceManager.disableNameservice()`, `DisabledNameserviceStore`, `MembershipNamenodeResolver.loadCache()`, `MountTableManager.addMountTableEntry()`, `MountTableResolver.loadCache()`, router `ClientProtocol`, and `RBFMetrics.getNameservices()`.

## Control Flow
Class setup starts a two-nameservice state-store cluster with independent datanodes, reduced router handler/client threads, router admin/RPC/metrics enabled, and a simulated slow NameNode for ns0. `setupNamespace()` creates mount entries `/dirns0` and `/dirns1`, refreshes the mount-table resolver, and creates directories in each namespace plus a root-level directory in ns0. `testWithoutDisabling()` verifies `renewLease()` waits more than one second because ns0 is slow and root listing includes ns0 and ns1 content. `testDisabling()` disables ns0, reloads disabled-nameservice and membership caches, verifies `renewLease()` completes quickly, and root/listing output excludes ns0-backed content where appropriate. `testMetrics()` parses nameservice metrics and expects ns0 to report `DISABLED` while ns1 remains `ACTIVE`. After each test, disabled nameservices are re-enabled in the store.

## State and Persistence
Disabled nameservice state is stored in `DisabledNameserviceStore`; mount table and membership data are in the router state store; filesystem directories live in the mini DFS cluster. Cleanup restores disabled namespace records.

## Dependencies and Integration Points
The test integrates admin APIs, router RPC fan-out, state-store-backed disabled namespace filtering, mount table resolution, mini DFS NameNodes, slow NameNode simulation, and metrics JSON.

## Risks and Test Signals
Timing assertions depend on the slow NameNode simulation and local scheduling. Directory ordering assertions assume stable listing order. Passing tests signal that disabled nameservices are skipped for fan-out operations, removed from resolver-visible active sets, and surfaced as `DISABLED` in metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestDisableNameservices.java -->
