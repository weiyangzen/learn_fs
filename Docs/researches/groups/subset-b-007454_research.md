# subset-b-007454 Research

Grouped source research for HDFS Router federation tests under `hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router`. Each section preserves the source path in its title and is delimited for deterministic reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFaultTolerant.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFaultTolerant.java

## Purpose

`TestRouterFaultTolerant.java` verifies Router behavior for multi-destination mount points when one subcluster becomes unavailable. It builds two `MockNamenode` instances and two `Router` instances, registers subclusters through the state store, and checks write, list, content-summary, and read behavior across fault-tolerant and non-fault-tolerant mount settings. The source was read as a complete 675-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `RouterClient`, `MountTableManager`, `MultipleDestinationMountTableResolver`, `MembershipNamenodeResolver`, `DestinationOrder`, `RouterRpcClient.isUnavailableException`, and federation test helpers such as `createMountTableEntry`, `registerSubclusters`, `getFileSystem`, and `refreshRoutersCaches`. Key helpers are `setup`, `cleanup`, `updateMountPointFaultTolerant`, `testWriteWithFailedSubcluster(DestinationOrder)`, `checkDirectoriesFaultTolerant`, `checkFilesFaultTolerant`, `collectResults`, `TaskResults`, `getRandomRouter`, and `getRandomRouterFileSystem`.

## Control Flow

`setup` starts active mock namenodes for `ns0` and `ns1`, configures routers with RPC/admin/state-store support, uses router0 with partial listing disabled and router1 with partial listing enabled, registers all subclusters while excluding `ns1` from the active set, and creates a fixed thread pool. `testWriteWithFailedSubcluster` stops `ns1`, then runs write checks concurrently for `HASH_ALL`, `SPACE`, `RANDOM`, and `HASH` orderings. Each order creates a mount, tries directory and file creation before fault tolerance is enabled, updates the `MountTable` to `faultTolerant=true`, and repeats checks only for `FOLDER_ALL` orders; unsupported orders must reject the update. `testReadWithFailedSubcluster` creates a file, detects which namespace owns it, stops that namespace, and verifies opening the old path now yields an unavailable-cluster `RemoteException` rather than `FileNotFoundException`.

## State and Persistence Behavior

State lives in mock namenodes, router-local resolver caches, and state-store mount-table records. `updateMountPointFaultTolerant` mutates a persisted `MountTable` record through the admin API and explicitly refreshes router caches. The test intentionally creates per-call random `UserGroupInformation` instances to exercise router client concurrency. File and directory state is transient in mock namenode filesystems and is torn down by stopping mocks and routers.

## Dependencies and Integration Points

The test integrates Router RPC, admin APIs, mount-table state-store protocols (`GetMountTableEntriesRequest`, `UpdateMountTableEntryRequest`), membership registration, multi-destination resolver behavior, partial listing configuration, HDFS `FileSystem` operations, and remote exception classification. It is closely related to `TestRouterRpcMultiDestination#testSubclusterDown`.

## Risks and Edge Cases

The assertions depend on concurrent task scheduling and random router selection, so failures may expose timing-sensitive cache or resolver behavior. It also relies on mock namenode semantics, including zero-byte creates reporting a positive length through the mock. The `tasks` list is intentionally reused and cleared by `collectResults`; changing this helper can silently alter later list/content-summary checks. Fault-tolerant updates are valid only for all-destination orderings.

## Test Signals

Strong signals are successful mixed-result expectations before fault tolerance, all-success expectations after fault tolerance for supported orderings, explicit rejection for unsupported orderings, router0/router1 partial listing differences, and unavailable-cluster classification after the owning subcluster is stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFaultTolerant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederatedState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederatedState.java

## Purpose

`TestRouterFederatedState.java` validates that router federated namespace state IDs can be serialized into an IPC request header through an `AlignmentContext` and parsed back as `RouterFederatedStateProto`. The source was read as a complete 104-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `AlignmentContext`, `ClientId`, `RPC.RpcKind`, `RpcHeaderProtos.RpcRequestHeaderProto`, `ProtoUtil.makeRpcRequestHeader`, and `HdfsProtos.RouterFederatedStateProto`. The local `AlignmentContextWithRouterState` implements `updateRequestState` by writing a `RouterFederatedStateProto` byte string into the request header.

## Control Flow

`testRpcRouterFederatedState` creates a client ID and an expected map of namespace state IDs, builds an RPC request header with the custom alignment context, extracts `header.getRouterFederatedState()`, parses it as `RouterFederatedStateProto`, and asserts that the resulting map equals the original map.

## State and Persistence Behavior

The only state is an in-memory `Map<String, Long>` held by the test alignment context and encoded into a protobuf field. There is no persistence beyond the request header byte string.

## Dependencies and Integration Points

This targets the IPC alignment extension point shared by HDFS clients, namenodes, and routers. It ensures `ProtoUtil.makeRpcRequestHeader` calls `AlignmentContext.updateRequestState` and that the router-specific protobuf field preserves namespace-state mappings.

## Risks and Edge Cases

The test only covers request-side propagation and does not exercise response state, threshold handling, coordinated-call detection, empty maps, duplicate keys, or malformed protobuf payloads. It still protects the key compatibility boundary between `AlignmentContext` and RPC header serialization.

## Test Signals

The primary signal is exact map equality after protobuf round trip. A regression would appear as an empty router state field, parse failure, or missing/changed namespace IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederatedState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRename.java

## Purpose

`TestRouterFederationRename.java` provides the main positive and negative tests for Router Federation Rename, especially cross-namespace directory rename through the router. It extends `TestRouterFederationRenameBase` and covers success, unsupported file rename shape, pre-existing destinations, missing sources, mount-point restrictions, multi-destination source restrictions, and scheduler counter accounting. The source was read as a complete 350-line JUnit 5 test.

## Important APIs, Types, and Functions

Important types include `MiniRouterDFSCluster`, `RouterContext`, `DFSClient`, `ClientProtocol`, `RouterFederationRename`, `RemoteLocation`, `FileContext`, and Mockito spies. `MockGroupsMapping` implements `GroupMappingServiceProvider` and returns a deterministic group based on user name. Key methods are `testRenameDir`, `testSuccessfulRbfRename`, `testRbfRenameFile`, `testRbfRenameWhenDstAlreadyExists`, `testRbfRenameWhenSrcNotExists`, `testRbfRenameOfMountPoint`, `testRbfRenameWithMultiDestination`, and `testCounter`.

## Control Flow

Class-level setup starts the base federated mini-cluster. Each test calls `setup`, chooses a router, and uses nameservice-specific federated paths. The positive directory test creates a source directory with a file, invokes both `rename` and `rename2`, and checks the source is gone while the destination contains the child file. Negative tests call the router's `ClientProtocol` and expect `RemoteException` messages for file-to-directory rename, existing destination, missing source, mount-point rename, and multi-destination source. `testCounter` directly constructs a spy `RouterFederationRename`, starts a watcher thread on `RouterRpcServer.getSchedulerJobCount`, triggers `routerFedRename`, and verifies count increment/decrement plus maximum observed scheduler count.

## State and Persistence Behavior

Persistent test state is held in the MiniRouterDFSCluster namenode filesystems, router resolver mock locations, DistCp scheduler journal configured by the base class, and router metrics counters. Per-test source/destination paths are cleaned with `FileContext.delete`. `MockGroupsMapping` affects permission/group lookup for the cluster.

## Dependencies and Integration Points

The tests integrate DFS client protocol rename variants, router federation rename orchestration, DistCp procedure scheduling, caller context, router metrics, mock location resolution, and cross-namespace file movement. They depend on the base class's router rename options, journal URI, bandwidth/map settings, and datanode heartbeat tuning.

## Risks and Edge Cases

Message-fragment assertions make error text a compatibility surface. The scheduler counter test uses a 1 ms polling watcher and a timeout; slow environments could expose race conditions. The tests focus on directory rename; file rename support is intentionally expected to fail when the destination is a directory. Multi-destination source handling must stay strict because the implementation assumes exactly one remote source and one remote destination.

## Test Signals

Signals include successful `rename`/`rename2` across namespaces, stable source/destination existence checks, expected `RemoteException` messages, Mockito verification of `countIncrement` and `countDecrement`, and cleanup checks against the underlying namenode filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameBase.java

## Purpose

`TestRouterFederationRenameBase.java` is the shared fixture for router federation rename tests. It creates a two-subcluster, six-datanode-per-subcluster federated mini-cluster, enables the rename feature, configures permissions/group mapping, optionally enables async RPC, and provides helpers for per-test path setup. The source was read as a complete 217-line Java fixture.

## Important APIs, Types, and Functions

Important APIs include `MiniRouterDFSCluster`, `RouterConfigBuilder.routerRenameOption`, `DistCpProcedure.enableForTest`, `DFS_ROUTER_FEDERATION_RENAME_MAP`, `DFS_ROUTER_FEDERATION_RENAME_BANDWIDTH`, `SCHEDULER_JOURNAL_URI`, `RouterAsyncRpcFairnessPolicyController`, and `MockResolver`. Key methods are `globalSetUp(boolean enableAsyncRpc)`, `tearDown`, `setup`, `setRouter`, `setNs`, `setNamenode`, `getRouterFileSystem`, `createDir`, `getCluster`, and `getRouterContext`.

## Control Flow

`globalSetUp` configures namenodes with caller context and the mock group mapping, starts the federated HDFS cluster, creates a DistCp journal under the second namenode, configures routers with metrics/RPC/admin/rename options, starts routers, registers namenodes, lowers datanode heartbeat expiry for faster tests, and enables `DistCpProcedure` test mode. `setup` installs mock locations, deletes old files, creates test directories, picks a random router and a nameservice, installs a special `/same` mapping with two destinations in the same namespace, and creates a random test file on the selected namenode.

## State and Persistence Behavior

The static `cluster` owns all mini-cluster state for subclasses. Instance fields cache the current router context, selected nameservice, router filesystem, namenode filesystem, and created namenode file. Router rename state includes the scheduler journal URI and feature configuration. `tearDown` shuts down the cluster and disables DistCp test mode.

## Dependencies and Integration Points

This base integrates MiniRouterDFSCluster, HDFS permission checking, group mapping, router fairness policy selection, router rename configuration, DistCp scheduler state, mock resolver locations, and datanode heartbeat configuration. Subclasses rely on its generated federated paths and file helpers.

## Risks and Edge Cases

The fixture uses a static cluster shared by subclass test methods, so cleanup in `setup` and `tearDown` is critical. The `/same` multi-destination mapping is deliberately unusual and tests must not assume one-to-one mount resolution. Async mode changes router fairness controller and handler count; code paths must remain behaviorally equivalent.

## Test Signals

Useful signals are successful router/namenode registration, available router and namenode filesystems, a created random file on the selected namespace, functioning mock `/same` locations, and successful cluster shutdown with DistCp test mode disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameInKerberosEnv.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameInKerberosEnv.java

## Purpose

`TestRouterFederationRenameInKerberosEnv.java` verifies router federation rename in a Kerberos-secured mini-cluster. It starts a `MiniKdc`, configures secure namenode/datanode/router principals and keytabs, enables block tokens and delegation-token ZooKeeper settings, and tests a client keytab user renaming a directory across namespaces. The source was read as a complete 298-line JUnit 5 test.

## Important APIs, Types, and Functions

Important types include `MiniKdc`, `ClientBaseWithFixes`, `MiniRouterDFSCluster`, `RouterContext`, `SecurityUtil`, `UserGroupInformation`, `ImpersonationProvider`, `DFSClient`, and `ClientProtocol`. The nested `AllowUserImpersonationProvider` authorizes proxying only when the real user matches the current MiniCluster user. Key methods are `globalSetUp`, `setUp`, `tearDown`, `prepareEnv`, `testRenameDir`, `setRouter`, and `testClientRename`.

## Control Flow

Global setup starts MiniKdc, creates client and server principals in a generated keytab, sets Kerberos authentication and service principals in `baseConf`, configures data-transfer protection and secure-port test overrides, and enables `DistCpProcedure` test mode. Per-test setup creates a secure MiniRouterDFSCluster, starts namenodes and routers, configures router rename and ZK delegation token settings, registers namespaces, lowers datanode heartbeat expiry, installs mock locations, creates test directories, and picks a random router. The actual test prepares permissive parents, creates a source directory/file, logs in as the client principal from keytab, performs `ClientProtocol.rename` through the router, and checks the source disappears and destination file exists.

## State and Persistence Behavior

Static state includes `baseConf`, generated keytab path, MiniKdc, and principal names. Per-test state is the secure mini-cluster and selected router context. Temporary filesystem state is deleted in `testRenameDir`; cluster state is shut down after each test; KDC and DistCp test mode are stopped globally.

## Dependencies and Integration Points

This test integrates Hadoop security, router and namenode Kerberos principals, data-transfer protection, block access tokens, ZK delegation token secret-manager configuration, proxy-user authorization, router federation rename, DistCp scheduling, and MiniRouterDFSCluster.

## Risks and Edge Cases

The server principal uses the `USERNAME` environment variable and `localhost`, making the test sensitive to local environment assumptions. The generated keytab path lives under `test.dir` or `target`. Because it starts KDC, ZooKeeper-backed token configuration, and full mini-clusters, it is heavier and more timing-sensitive than unsecured rename tests. It only covers the successful client rename path, not secure failure cases.

## Test Signals

Signals are successful KDC principal creation, secure cluster startup, router/namenode registration, successful keytab login, no exception during cross-namespace rename, and post-rename source/destination existence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameInKerberosEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenamePermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenamePermission.java

## Purpose

`TestRouterFederationRenamePermission.java` checks permission and ACL enforcement for router federation rename. It extends the shared rename base, uses a synthetic remote user `foo`, and verifies source existence, source parent permissions, ACLs, destination parent existence and ownership, successful rename, and snapshot path rejection. The source was read as a complete 246-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `UserGroupInformation`, `DFSClient`, `ClientProtocol`, `RemoteLocation`, `RouterFederationRename.checkSnapshotPath`, `FsPermission`, `AclEntry`, `AclEntryScope`, `AclEntryType`, and `FsAction`. Important methods are `testSetup`, `testRenameSnapshotPath`, `testPermission1` through `testPermission7`, and `buildAcl`.

## Control Flow

Each test sets source and destination nameservices, source/destination paths under `/d0/<method>`, creates user `foo`, and gets the current router filesystem. Snapshot tests call `checkSnapshotPath` with `.snapshot` in either source or destination and expect `IOException`. Permission tests progressively create the source, alter source parent mode or ACLs, create destination parent, and invoke `ClientProtocol.rename` as user `foo`. The last case grants source ACL, creates and transfers destination parent ownership to `foo`, performs rename, and verifies the moved child file.

## State and Persistence Behavior

State is transient in the mini-cluster filesystems and router permissions model. The test mutates ACLs, owners, and modes on source and destination parents. The inherited base resets locations/files for each method and tears down the shared cluster at class end.

## Dependencies and Integration Points

The file integrates HDFS ACL semantics, user/group mapping from the base class, router-side federation rename prechecks, `RemoteException` propagation, and snapshot path validation independent of live cluster state.

## Risks and Edge Cases

The tests assert specific exception class-name fragments inside `RemoteException`, so changes in wrapped exception text may break them. ACL construction deliberately includes unnamed user and group entries plus a named user; missing mask behavior is not separately tested. Only classic `rename` is used in permission cases, not `rename2`.

## Test Signals

Expected signals are `FileNotFoundException` for absent source or destination parent, `AccessControlException` for insufficient source/destination permissions, `IOException` for snapshot paths, and final successful rename when ACL and destination ownership allow it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenamePermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFsck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFsck.java

## Purpose

`TestRouterFsck.java` is an end-to-end test for the Router HTTP `/fsck` endpoint. It creates a two-namespace state-store-backed router cluster, maps two mount points to different namespaces, creates different file counts under each, and verifies federated fsck output for all paths and for a filtered path. The source was read as a complete 218-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `MiniRouterDFSCluster.RouterContext`, `RouterConfigBuilder.http`, `MountTableManager`, `MountTableResolver`, `MembershipStore`, `MembershipState`, Apache HTTP client classes, and `EntityUtils`. Helpers are `globalSetUp`, `clearMountTable`, `addMountTable`, and `testFsck`.

## Control Flow

Global setup starts cluster and routers with state-store/admin/RPC/HTTP enabled, captures router filesystem and HTTP address, and reads sorted namenode memberships from the state store. `testFsck` adds `/testdir` on `ns0` and `/testdir2` on `ns1`, creates one file in the first and three in the second, calls `/fsck`, asserts HTTP 200 and output delimiters/counts for both namespaces, then calls `/fsck?path=/testdir` and asserts only the one-file count remains while all active namenodes are still checked.

## State and Persistence Behavior

Mount-table records are persisted through the admin API and cache-loaded in the resolver. Files are created through the router filesystem. `clearMountTable` removes all mount-table records after each test. Membership state is read once from the router's state store for output verification.

## Dependencies and Integration Points

This test bridges Router HTTP server, `FsckServlet`/federated fsck behavior, mount-table resolution, state-store membership records, namenode web addresses, and filesystem mutations through the router.

## Risks and Edge Cases

Assertions depend on textual fsck output and active membership string formatting. The test notes HTTPS is not covered. It validates file counts and active namenode inclusion but not corrupt block reporting, permissions, unhealthy namenodes, or non-OK HTTP paths.

## Test Signals

Signals include HTTP 200 responses, `"Federated FSCK started"` and `"Federated FSCK ended"` markers, expected `Total files` counts, absence of unrelated namespace count for filtered path, and exactly two active namenode checks in output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFsck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHeartbeatService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHeartbeatService.java

## Purpose

`TestRouterHeartbeatService.java` validates router heartbeat publication into a ZooKeeper-backed state store, including graceful behavior when the state store is unavailable. The source was read as a complete 145-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `Router`, `RouterHeartbeatService`, `StateStoreService`, `RouterStore`, `StateStoreZooKeeperImpl`, `TestingServer`, Curator `CuratorFramework`, `GetRouterRegistrationRequest/Response`, `RouterState`, and `StateStoreVersion`. Key methods are `setup`, `testStateStoreUnavailable`, `testStateStoreAvailable`, and `tearDown`.

## Control Flow

`setup` creates a router with ID `router1`, configures state-store support with ZooKeeper driver, starts an embedded ZooKeeper server and Curator client, starts the router, and waits for the state store. The unavailable test closes Curator, stops ZooKeeper and state store, asserts the driver is not ready, then calls `updateStateStore` and expects no thrown exception. The available test refreshes caches, observes no existing router ID/version, runs a heartbeat, refreshes again, and asserts router ID and state-store version are now present.

## State and Persistence Behavior

Router registration state is persisted in ZooKeeper through the federation state store. The heartbeat writes `RouterState` including router ID and `StateStoreVersion`. Cleanup closes Curator, stops ZooKeeper, and shuts down the router.

## Dependencies and Integration Points

This test integrates Router lifecycle, state-store driver readiness, ZooKeeper driver configuration, router state manager protocols, and heartbeat update logic.

## Risks and Edge Cases

The unavailable path only checks no exception escapes; it does not verify logging or retry state. The available path assumes refresh visibility after a single heartbeat and cache refresh. Embedded ZooKeeper lifecycle issues can affect test stability.

## Test Signals

Key signals are `isDriverReady` false/true in the two scenarios, null registration before heartbeat, non-null router ID and version after heartbeat, and no exception from `updateStateStore` when the driver is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHeartbeatService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHttpServerXFrame.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHttpServerXFrame.java

## Purpose

`TestRouterHttpServerXFrame.java` verifies that the Router HTTP server emits the configured `X-FRAME-OPTIONS` header. The source was read as a complete 67-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `RouterConfigBuilder.http`, `DFSConfigKeys.DFS_XFRAME_OPTION_ENABLED`, `DFSConfigKeys.DFS_XFRAME_OPTION_VALUE`, `HttpServer2.XFrameOption.SAMEORIGIN`, `Router`, and `HttpURLConnection`. The only test method is `testRouterXFrame`.

## Control Flow

The test builds an HTTP-enabled router configuration, enables X-Frame options with value `SAMEORIGIN`, starts a router on an ephemeral HTTP address, opens an HTTP connection to the root URL, reads the `X-FRAME-OPTIONS` response header, asserts it exists and ends with `SAMEORIGIN`, then stops and closes the router in `finally`.

## State and Persistence Behavior

There is no persistent state. The router's in-memory HTTP server is started and stopped within the test.

## Dependencies and Integration Points

This checks Router HTTP server wiring to Hadoop `HttpServer2` security headers and DFS configuration keys.

## Risks and Edge Cases

Only the enabled `SAMEORIGIN` case is covered. Disabled headers, other X-Frame values, HTTPS, and non-root endpoints are not checked. The assertion uses `endsWith`, allowing prefixes in the header.

## Test Signals

Signals are successful router HTTP startup, reachable root URL, non-null `X-FRAME-OPTIONS`, and header suffix matching `SAMEORIGIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterHttpServerXFrame.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterListOpenFiles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterListOpenFiles.java

## Purpose

`TestRouterListOpenFiles.java` verifies Router handling of `listOpenFiles` for single- and multi-destination mount points in both synchronous and asynchronous router RPC modes. It checks path rewriting, duplicate open-file de-duplication, and batched iteration across namespaces with overlapping inode ID ranges. The source was read as a complete 263-line parameterized JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterClientProtocol`, `DFSClient`, `OpenFileEntry`, `OpenFilesIterator.OpenFilesType`, `BatchedRemoteIterator.BatchedEntries`, `RemoteIterator`, `DestinationOrder.HASH_ALL`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, and `AsyncUtil.syncReturn`. Key methods are constructor/setup, `resetInodeId`, `cleanupNamespaces`, `testSingleDestination`, `testMultipleDestinations`, `testMultipleDestinationsMultipleBatches`, `runBatchListOpenFilesTest`, and `createMountTableEntry`.

## Control Flow

The parameterized class runs with `useAsync=true` and `false`. Setup starts a two-namespace state-store cluster with heartbeat/admin/RPC, monitor-namenode settings, mount-table cache update, and a small open-files response batch size. Each test resets both namespaces' inode generators, creates matching destination directories, adds a source mount, opens files directly on namespace clients, then calls router protocol or router client `listOpenFiles`. Async calls retrieve the result through `syncReturn`.

## State and Persistence Behavior

Mount-table records are added through the router admin client and router state-store caches are refreshed. Open file state is maintained by namespace `DFSClient` streams until each stream is closed. Namespaces are cleaned after each test by deleting `/` on both clients. Inode IDs are explicitly reset to create duplicate and ordered-batch scenarios.

## Dependencies and Integration Points

This test integrates router client protocol modules, async RPC bridging, mount-table path translation, open-file batched iterators, namenode inode IDs, and multi-destination resolver de-duplication.

## Risks and Edge Cases

It depends on deterministic ordering of open-file results for some assertions. Duplicate file names across namespaces should collapse to one logical entry, while different names should both appear. Batch tests intentionally make one namespace's inode IDs much larger than the other, then reverse the ordering to catch cursor bugs.

## Test Signals

Signals include one result for single-destination mounts, two distinct results for different files across namespaces, one deduplicated result for same-name files, correct rewritten source paths, and complete iteration of `3 * 2 * BATCH_SIZE` entries in both inode ordering directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterListOpenFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMissingFolderMulti.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMissingFolderMulti.java

## Purpose

`TestRouterMissingFolderMulti.java` validates Router listing and content-summary behavior for a multi-destination `HASH_ALL` mount when folders exist everywhere, nowhere, or in only one subcluster. The source was read as a complete 182-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `MultipleDestinationMountTableResolver`, `MembershipNamenodeResolver`, `DestinationOrder.HASH_ALL`, `FileSystem`, `ContentSummary`, and federation helpers `createMountTableEntry`, `getFileSystem`, and `registerSubclusters`. Test methods are `testSuccess`, `testFileNotFound`, and `testOneMissing`.

## Control Flow

Setup creates active mock namenodes `ns0` and `ns1`, starts a router with state-store/admin/RPC and partial listing disabled, configures membership and file resolvers, and registers subclusters. `testSuccess` writes ten files through the router and expects listing and content summary counts to match. `testFileNotFound` creates only the mount and expects `FileNotFoundException` for listing and content summary under a missing child path. `testOneMissing` writes files directly to only `ns0`, then accesses through the router and expects successful listing/summary rather than failure from the missing `ns1` folder.

## State and Persistence Behavior

State is held in mock namenode filesystems and router mount-table/resolver caches. All mocks and the router are stopped after each test. There is no durable persistence beyond the in-memory state store.

## Dependencies and Integration Points

The test targets multi-destination resolver behavior, partial-list policy, router filesystem list/status aggregation, and content-summary aggregation across mock namenodes.

## Risks and Edge Cases

The core edge case is distinguishing all destinations missing from one destination missing. The test forces `DFS_ROUTER_ALLOW_PARTIAL_LIST=false` but still expects one-missing success for existing data, so changes to missing-location semantics can break it. It does not cover more than two destinations or stale cache updates.

## Test Signals

Signals are exact file counts for success, `FileNotFoundException` when no subcluster has the path, and successful ten-entry listing plus ten item summary when only one namespace contains the folder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMissingFolderMulti.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTable.java

## Purpose

`TestRouterMountTable.java` is a broad end-to-end test suite for Router mount-table behavior. It covers read-only mounts, admin path component limits, listing modification times, synthetic mount-point statuses, default namespace disabling, mount permissions, child counts, exception path rewriting, trailing slash listings, file info on ancestor mounts, delete/rename guards around mount points, erasure-coding status, and `getEnclosingRoot`. The source was read as a complete 815-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `RouterContext`, `NamenodeContext`, `MountTableResolver`, `MountTableManager`, `RouterClientProtocol`, `ClientProtocol`, `DirectoryListing`, `HdfsFileStatus`, `DistributedFileSystem`, `FsPermission`, `UserGroupInformation`, and mount-table state-store requests. Helpers include `globalSetUp`, `clearMountTable`, `addMountTable`, `updateMountTable`, `getListing`, and `createEntry`.

## Control Flow

Global setup starts a two-namespace state-store cluster with admin/RPC enabled and a maximum mount component length. Each test adds mount-table records via admin API, refreshes the resolver cache, performs router or namenode filesystem operations, and asserts behavior. The suite tests read-only write rejection; add/update validation for overly long path components; root listing modification-time consistency between mount records and actual namespace entries; synthetic mount-point status owner/group behavior when remote `getFileInfo` raises permission errors; listing without a default namespace; permissions from mount records versus remote destinations; multi-destination permission and child aggregation; path rewriting in exceptions; trailing-slash `getListing`; mount-point delete/rename protection; erasure-coded mount status; and enclosing-root resolution before and after adding a mount.

## State and Persistence Behavior

Mount-table entries are persisted through the router admin client and then loaded into `MountTableResolver`. Remote filesystem state is created on `nnFs0` and `nnFs1` and deleted in `finally` blocks. `clearMountTable` removes every mount entry and resets default namespace support after each test. `startTime` is captured to validate modification times generated during the suite.

## Dependencies and Integration Points

The file integrates state-store mount-table protocols, router RPC path resolution, router filesystem behavior, HDFS metadata/status types, HDFS permissions, EC policy state, default namespace fallback, and mount-point guard logic for destructive operations.

## Risks and Edge Cases

This is a high-blast-radius regression suite: it asserts exact exception message fragments, owner/group/mode fallback behavior, ordering-sensitive root listings, and HDFS path rewriting. Some multi-destination permission tests allow either namespace's metadata when destinations differ. The default namespace is toggled inside tests and must be reset to avoid cross-test contamination.

## Test Signals

Strong signals include read-only `IOException`, path component limit failures, listing lengths and modification times, synthetic owner/group values, `FileNotFoundException` with router-visible paths, exact mount permissions when destination is absent, destination permissions when present, child-count aggregation, `AccessControlException` for deleting or renaming mount points, EC status visible through `listStatus`, and correct `getEnclosingRoot` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefresh.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefresh.java

## Purpose

`TestRouterMountTableCacheRefresh.java` verifies that enabling `MountTableRefresherService` propagates mount-table cache updates to all running routers after add, remove, update, explicit refresh, router stop, timeout, and cached client expiration scenarios. It runs each parameterized case with router heartbeats using IP addresses and host names. The source was read as a complete 429-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `TestingServer`, `MiniRouterDFSCluster`, `RouterContext`, `RouterStore`, `MountTableManager`, `MountTableRefresherService`, `MountTableRefresherThread`, `RouterClient`, `STATE.STARTED`, and mount-table add/remove/update/refresh requests. Parameter data is `true` and `false` for `DFS_ROUTER_HEARTBEAT_WITH_IP_ENABLE`. Helpers include `initTestRouterMountTableCacheRefresh`, `destroy`, `clearEntries`, `getRouters`, `getNumMountTableEntries`, `getMountTableEntry`, `addMountTableEntry`, and `getMountTableEntries`.

## Control Flow

Initialization starts an embedded ZooKeeper server, a two-namespace MiniRouterDFSCluster with refresh-cache/admin/RPC/heartbeat support, ZooKeeper-backed federation store, and router store enabled. It waits for routers to register. Add/remove/update tests mutate the mount table through one router and read mount table entries from every started router's admin client. The stopped-router test populates caches, stops a non-primary router, adds another entry, and asserts remaining routers refresh. The explicit API test calls `refreshMountTableEntries`. Timeout and client-expiration tests subclass `MountTableRefresherService` to inject slow local work or count RouterClient creation/closure, then assert refresh timeout and cache eviction behavior.

## State and Persistence Behavior

Mount-table records and router registrations persist in the ZooKeeper-backed state store. RouterClient connections are cached inside `MountTableRefresherService` and expire according to `MOUNT_TABLE_CACHE_UPDATE_CLIENT_MAX_TIME`. The test destroys the cluster and ZooKeeper server after each parameterized invocation and removes mount entries in cleanup.

## Dependencies and Integration Points

This suite integrates Router admin APIs, router state registration, mount-table refresh RPCs between routers, ZooKeeper state-store driver, heartbeat address selection, timeout configuration, and cached RouterClient lifecycle.

## Risks and Edge Cases

The initialization guard reuses static state within a parameter but teardown resets it; ordering matters. Timeout coverage depends on `@Timeout(100)` and a configured 5-second refresh timeout. Cache eviction waits up to three times the configured client lifetime. A stopped router must not prevent updates from reaching started routers.

## Test Signals

Signals include all running routers seeing added/updated/removed entries, successful explicit refresh response, no hang when a refresher sleeps for one minute, and equality of RouterClient create and close counters after cache expiration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefresh.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefreshSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefreshSecure.java

## Purpose

`TestRouterMountTableCacheRefreshSecure.java` repeats core mount-table cache propagation checks with security configuration enabled. It ensures add, remove, update, and stopped-router refresh behavior work when Router refresh-cache services, admin RPC, heartbeat, and ZooKeeper-backed state store run in secure mode. The source was read as a complete 342-line JUnit 5 test.

## Important APIs, Types, and Functions

The file uses `SecurityConfUtil.initSecurity`, `TestingServer`, `MiniRouterDFSCluster`, `StateStoreZooKeeperImpl`, `StateStoreDriver`, `RouterStore`, `MountTableManager`, `RouterContext`, `MountTable`, and add/remove/update/get state-store protocols. Key methods are `setUp`, `destory`, `tearDown`, `clearEntries`, `testMountTableEntriesCacheUpdatedAfterAddAPICall`, `testMountTableEntriesCacheUpdatedAfterRemoveAPICall`, `testMountTableEntriesCacheUpdatedAfterUpdateAPICall`, and `testCachedRouterClientBehaviourAfterRouterStoped`.

## Control Flow

Class setup starts embedded ZooKeeper, builds a secure refresh-cache/admin/RPC/heartbeat router configuration, creates a two-namespace MiniRouterDFSCluster with the same security resource, starts cluster and routers, obtains a random router and mount manager, and waits for router registration. Each test mutates a mount-table entry through the manager, iterates all started routers, and verifies their admin views. The stopped-router test stops one non-primary router and verifies a subsequent add reaches all remaining started routers.

## State and Persistence Behavior

Secure cluster and router registration state are class-level static resources. Mount-table records are stored in ZooKeeper and cleared after each test. Router cache refresh state is observed through each router's admin client. Class teardown closes ZooKeeper and shuts down the cluster.

## Dependencies and Integration Points

The test integrates secure Hadoop configuration, ZooKeeper federation store, router registration, mount-table refresh RPCs, and admin APIs. It is the secure counterpart to the non-secure cache refresh test but does not include timeout/client-expiration subtests.

## Risks and Edge Cases

The teardown method name is misspelled `destory` but annotated correctly. Secure setup is heavy and can be sensitive to security resource cleanup. The update test compares some expected values through `updatedMountTable` while iterating routers, so it mainly proves store update plus per-router entry count/source path.

## Test Signals

Signals include every started router reporting exactly one added entry, zero entries after removal, updated destination namespace/path after update, and two entries on remaining routers after one router is stopped and another entry is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableCacheRefreshSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableWithoutDefaultNS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableWithoutDefaultNS.java

## Purpose

`TestRouterMountTableWithoutDefaultNS.java` verifies Router behavior when default nameservice fallback is disabled. It checks synthetic ancestor metadata for submounts, failure for paths with no location or submount, recursive content summary over nested mount points, all-location discovery, and content-summary location selection. The source was read as a complete 268-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `RouterContext`, `MountTableResolver`, `RouterClientProtocol`, `RouterRpcServer`, `RemoteLocation`, `RouterResolveException`, `NoLocationException`, `ContentSummary`, and mount-table admin protocols. Helpers are `globalSetUp`, `clearMountTable`, `addMountTable`, and `writeData`.

## Control Flow

Global setup starts a two-namespace state-store/admin/RPC router cluster with `DFS_ROUTER_DEFAULT_NAMESERVICE_ENABLE=false`. Tests add mount entries and force resolver cache reload. `testGetFileInfoWithSubMountPoint` asserts `/testdir` returns synthetic directory info when `/testdir/1` is mounted. `testGetFileInfoWithoutSubMountPoint` expects `RouterResolveException` for unrelated `/testdir2`. Content-summary tests write data directly to namespace filesystems and request summaries at ancestor paths. Location tests check `getAllLocations` and `getLocationsForContentSummary` over nested mount hierarchies and expect `NoLocationException` for unrelated roots.

## State and Persistence Behavior

Mount entries persist through the state store and are cleared after each test. File data is created directly in namespace filesystems and deleted in `finally` blocks. Default namespace fallback remains disabled for the class lifetime.

## Dependencies and Integration Points

This suite targets Router path resolution without fallback, synthetic mount ancestors, recursive content-summary aggregation, nested mount-table traversal, and direct router RPC protocol helper methods.

## Risks and Edge Cases

The test creates a mount with nameservice `ns2` in `testGetAllLocations` even though the cluster has two namespaces; this is acceptable for resolver map traversal but would be unsafe for live filesystem operations. `writeData` writes one byte per loop iteration, making large file creation slower but deterministic. No-default namespace behavior must distinguish ancestor-with-submount from unrelated missing path.

## Test Signals

Signals are non-null synthetic `HdfsFileStatus` for ancestors, `RouterResolveException`/`NoLocationException` for unrelated paths, exact content summary file counts and lengths, and expected remote destination paths for nested content-summary locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMountTableWithoutDefaultNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMultiRack.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMultiRack.java

## Purpose

`TestRouterMultiRack.java` verifies erasure-coding topology support results through a Router when two nameservices have independent datanodes spread across multiple racks. The source was read as a complete 129-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `DistributedFileSystem`, `ECTopologyVerifierResult`, router quota/RPC configuration, independent datanodes, and per-namespace `DistributedFileSystem` handles. The single test method is `testGetECTopologyResultForPolicies`.

## Control Flow

Setup starts a two-namespace cluster with nine datanodes per nameservice and an explicit rack list covering six racks. The test enables `RS-6-3-1024k` through the router, checks default enabled-policy support, queries unsupported and supported policy combinations, enables an unsupported `RS-10-4-1024k` policy through the router, and then toggles that policy on individual namespace filesystems to prove the federated result is unsupported if any namespace has an unsupported enabled policy.

## State and Persistence Behavior

EC policy state is mutated on the router filesystem and underlying namespace filesystems during the class-level mini-cluster lifetime. Cluster state is torn down after all tests.

## Dependencies and Integration Points

This test integrates Router EC policy RPC forwarding, topology aggregation across namespaces, rack placement metadata, and `ECTopologyVerifierResult` semantics.

## Risks and Edge Cases

The test assumes specific EC policy names and datanode/rack counts. It checks support booleans but not detailed error messages. Because policy state is changed multiple times, cleanup by cluster shutdown is important.

## Test Signals

Signals are `isSupported()` true for policies satisfiable by the configured topology and false for policies requiring more datanodes than any subcluster can provide or when one namespace has an unsupported enabled policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMultiRack.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeHeartbeat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeHeartbeat.java

## Purpose

`TestRouterNamenodeHeartbeat.java` validates the service that heartbeats namenode status into the Router's active namenode resolver. It covers service lifecycle, local namenode heartbeat creation, HA active/standby updates, HA service-protocol address selection, DNS resolution expansion, and secure heartbeat registration. The source was read as a complete 365-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `MiniRouterDFSCluster`, `NamenodeHeartbeatService`, `ActiveNamenodeResolver`, `MockResolver`, `FederationNamenodeContext`, `Router.createLocalNamenodeHeartbeatService`, `Router.createNamenodeHeartbeatServices`, `DFSUtil`, `MockDomainNameResolver`, and `SecurityConfUtil`. Helpers include `globalSetUp`, `testNamenodeHeartbeatServiceHAServiceProtocol`, and `generateNamenodeConfiguration`.

## Control Flow

Global setup starts an HA mini-cluster with two nameservices, creates a `MockResolver`, and starts one heartbeat service per namenode. Lifecycle tests instantiate a service and assert INITED/STARTED/STOPPED transitions. Local heartbeat tests check no service without a local nameservice and a service description when local HA keys are configured. `testHearbeat` forces `nn0` active, waits for periodic heartbeats, checks active/standby order, performs a failover in one namespace, waits again, and validates only that namespace changes. Address-selection tests generate configs with RPC, service RPC, and lifeline RPC ports and assert chosen health monitor addresses. Secure heartbeat test starts a secure mini-cluster and verifies resolver namespaces are populated.

## State and Persistence Behavior

Heartbeat services write in-memory resolver records in `MockResolver` or router resolver state. Global services are started once and closed at teardown. Secure test resets `UserGroupInformation` and destroys security config in `finally`.

## Dependencies and Integration Points

This file integrates HA namenode state, router heartbeat services, local namenode detection, domain-name resolution, health monitor target construction, Java-version-sensitive unresolved address formatting, and secure MiniRouterDFSCluster registration.

## Risks and Edge Cases

`testHearbeat` uses fixed five-second sleeps, which can be slow or timing-sensitive. Address string expectations branch on Java 14+ unresolved-address formatting. Secure test must reset global UGI state. The typo in `testHearbeat` is harmless but visible in method naming.

## Test Signals

Signals include service state transitions, null/non-null local heartbeat creation, correct active/standby ordering before and after failover, expected health monitor address precedence from lifeline/service/RPC ports, resolved namenode descriptions for multiple host expansions, and non-empty resolver namespaces under security.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeHeartbeat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeMonitoring.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeMonitoring.java

## Purpose

`TestRouterNamenodeMonitoring.java` tests Router monitoring of configured namenodes, JMX URL scheme/frequency behavior, and the router's merged datanode view across namespaces. It uses `MockNamenode` instances for two namespaces with two namenodes each. The source was read as a complete 437-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `MockNamenode`, `Router`, `NamenodeHeartbeatService`, `MembershipNamenodeResolver`, `NamenodeStatusReport`, `LogVerificationAppender`, `HttpConfig.Policy`, `DatanodeInfoBuilder`, `DatanodeStorageReport`, `DFSClient.getDatanodeStorageReport`, and `DatanodeReportType.ALL`. Helpers are `getNamenodesConfig`, `testConfig`, `assertNamenodeHeartbeatService`, and overloaded `verifyUrlSchemes`.

## Control Flow

Setup creates mock namenodes and sets `nn0` active, `nn1` standby. `testNamenodeMonitoring` configures state store and resolver classes, monitors explicit `ns1` namenodes plus local `ns0.nn1`, starts a router, manually invokes all heartbeat services, reloads resolver cache, and asserts monitored records have newer modification times while unmonitored `ns0.nn0` does not. Config tests parse variations of the monitor-namenode list. JMX tests attach a log appender, build heartbeat services, call `getNamenodeStatusReport` one or more times, and count logged HTTP/HTTPS JMX URLs based on policy and configured interval. `testDatanodesView` registers mock subclusters, injects datanode views with conflicting admin states and timestamps, then asserts the router reports the most recent state per datanode UUID.

## State and Persistence Behavior

Mock namenode state, router state-store cache, heartbeat timestamps, and injected datanode reports are all in memory. The root log appender is modified during JMX tests. Cleanup stops all mock namenodes and the router after each test.

## Dependencies and Integration Points

This suite integrates router heartbeat configuration, membership resolver cache, state-store membership records, DFS HTTP policy, JMX status fetching frequency, datanode report aggregation, and mock namenode registration.

## Risks and Edge Cases

Modification-time assertions compare to `initializedTime`, so startup timing matters. Log appender assertions depend on debug log messages. JMX frequency tests infer requests from log counts rather than network calls. Datanode view merging depends on `lastUpdate` timestamps and duplicate UUID handling.

## Test Signals

Signals include expected monitored namenode set, newer timestamps only for monitored nodes, exact heartbeat service sets for config strings, HTTP versus HTTPS log counts, suppression of JMX when interval is negative, and merged datanode admin states (`dn0` decommissioned, `dn1` normal) based on newest reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeMonitoring.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeWebScheme.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeWebScheme.java

## Purpose

`TestRouterNamenodeWebScheme.java` verifies that namenode web schemes reported through the Router honor `dfs.http.policy`, specifically HTTP-only and HTTPS-only configurations. The source was read as a complete 204-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `NamenodeHeartbeatService`, `MembershipNamenodeResolver`, `FederationNamenodeContext`, `HttpConfig.Policy`, `RouterConfigBuilder`, and state-store resolver configuration. Key methods are `setup`, `cleanup`, `getNamenodesConfig`, `testWebSchemeHttp`, `testWebSchemeHttps`, and `testWebScheme`.

## Control Flow

Setup creates two namespaces with active/standby mock namenodes. `testWebScheme` builds namenode configuration, configures router heartbeat/state-store/RPC with the requested HTTP policy, monitors `ns1` plus local `ns0.nn1`, starts the router, manually invokes heartbeat services, reloads the membership resolver cache, gathers all namespace reports, and asserts every report has the expected web scheme string.

## State and Persistence Behavior

Membership reports are written to the router's in-memory/state-store-backed resolver cache during heartbeat invocation. Mock namenodes and router are stopped after each test.

## Dependencies and Integration Points

This checks the integration between DFS HTTP policy, namenode heartbeat status reports, membership resolver records, and web address scheme rendering in router-visible namespace metadata.

## Risks and Edge Cases

Only `HTTP_ONLY` and `HTTPS_ONLY` are covered, not mixed policies. The test does not open actual web URLs; it validates reported scheme fields. All reports are expected to share the same scheme regardless of namespace or active/standby role.

## Test Signals

Signals are resolver reports for all configured namespaces and exact `getWebScheme()` equality to `http` or `https` depending on policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeWebScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNetworkTopologyServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNetworkTopologyServlet.java

## Purpose

`TestRouterNetworkTopologyServlet.java` verifies the Router HTTP `/topology` endpoint in synchronous and asynchronous RPC modes, for text and JSON responses, with and without datanodes. It also defines a JUnit extension that starts and tears down the appropriate test clusters for nested parameterized classes. The source was read as a complete 319-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterConfigBuilder`, `DFS_ROUTER_HTTP_ENABLE`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, `HttpURLConnection`, Jackson `ObjectMapper`/`JsonNode`, `IOUtils.copyBytes`, nested test classes, and `RouterServerHelper` implementing `BeforeEachCallback` and `AfterAllCallback`. Core helper methods are `setUp`, `testPrintTopologyTextFormat`, `testPrintTopologyJsonFormat`, `testPrintTopologyNoDatanodesTextFormat`, and `testPrintTopologyNoDatanodesJsonFormat`.

## Control Flow

For each RPC mode, `RouterServerHelper.beforeEach` inspects the parameterized method's `ValueSource` and calls `setUp` once. Setup builds one federated cluster with nine datanodes per nameservice and explicit racks, and another with zero datanodes. Text tests call `/topology` and assert rack path strings and the count of `127.0.0.1` occurrences. JSON tests send `Accept: application/json`, parse the response, assert six racks, and count datanode entries. No-datanode tests call the same endpoint on the empty cluster and assert `"No DataNodes"` in text or JSON-response content. `afterAll` shuts down both clusters and clears thread-local state.

## State and Persistence Behavior

Static cluster fields hold the active topology clusters for each nested class run. Router HTTP state is in-process. The helper stores itself in an inheritable thread-local but removes it at teardown. There is no durable persistence.

## Dependencies and Integration Points

This test integrates Router HTTP server, network topology servlet, router sync/async RPC modes, datanode rack metadata aggregation across namespaces, JSON serialization, and JUnit 5 nested parameterized extension behavior.

## Risks and Edge Cases

URL construction uses `"http:/" + httpAddress + "/topology"`, relying on `httpAddress` string formatting. Static clusters require reliable `afterAll` cleanup. JSON no-datanode output is checked as text rather than parsed JSON. The datanode count assertion in text mode depends on host string repetition.

## Test Signals

Signals include expected rack labels `/ns0/rack1` through `/ns1/rack6`, eighteen datanode entries for populated clusters, six JSON rack nodes, `"No DataNodes"` for empty clusters, and identical behavior under async and sync router RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNetworkTopologyServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterPolicyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterPolicyProvider.java

## Purpose

`TestRouterPolicyProvider.java` verifies that `RouterPolicyProvider` declares security policy entries for every RPC protocol interface implemented by key HDFS RPC server classes. The source was read as a complete 99-line parameterized JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `RouterPolicyProvider`, Hadoop `Service`, Apache Commons `ClassUtils.getAllInterfaces`, `Sets.difference`, `RouterRpcServer`, `NameNodeRpcServer`, `DataNode`, `RouterAdminServer`, and JUnit parameterization. Key methods are `initialize`, `data`, `initTestRouterPolicyProvider`, and `testPolicyProviderForServer`.

## Control Flow

`initialize` reads all services from `RouterPolicyProvider` and stores their protocol classes in a static set. The parameterized test runs for each server class, finds all implemented interfaces whose simple names end in `Protocol`, logs both protocol sets, asserts the server exposes at least one protocol, computes the difference between server protocols and provider protocols, and fails if any server protocol lacks a policy entry.

## State and Persistence Behavior

State is limited to the static `policyProviderProtocols` set and the current parameter's `rpcServerClass`. No external state is modified.

## Dependencies and Integration Points

This test protects the security authorization boundary between HDFS RPC server protocol interfaces and router policy provider service declarations. It also indirectly tracks protocol interface changes on namenode, datanode, router RPC, and router admin servers.

## Risks and Edge Cases

The heuristic only considers interfaces whose simple names end with `Protocol`; protocols with different naming would be ignored. It checks presence but not ACL key correctness or service principal configuration. Interface inheritance changes can add protocols and require provider updates.

## Test Signals

Signals are a non-empty protocol set for every scanned server class and an empty difference between implemented protocol interfaces and `RouterPolicyProvider` service protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterPolicyProvider.java -->
