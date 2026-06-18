# subset-b-008085 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmContainerLocationCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmContainerLocationCache.java

## Purpose
Integration test for OM-side container location caching during key reads. It builds an `OzoneManager` with mocked SCM block/container protocols and mocked datanode `XceiverClientGrpc` instances so client reads can exercise cached container pipelines without a full datanode cluster.

## Important APIs, types, and functions
- Uses `OmTestManagers`, `ObjectStore`, `RpcClient`, `OzoneBucket`, `OzoneKeyDetails`, and `OzoneOutputStream` as the client/OM surface.
- Mocks `ScmBlockLocationProtocol.allocateBlock`, `StorageContainerLocationProtocol.getContainerWithPipelineBatch`, and datanode `sendCommandAsync` for `WriteChunk`, `PutBlock`, `GetBlock`, and `ReadChunk`.
- Helper methods create Ratis and EC `Pipeline` instances, SCM `AllocatedBlock` objects, `ContainerWithPipeline` responses, block/chunk protobuf responses, and Mockito matchers for pipelines and command types.
- Parameter sources divide errors into refresh-triggering failures (`CLOSED_CONTAINER_IO`, `CONTAINER_NOT_FOUND`, gRPC `UNAVAILABLE`) and non-refresh failures (`UNAUTHENTICATED`, arbitrary `IOException`).

## Control flow
`setUp` configures topology-aware reads, initializes OM metadata, creates a test volume plus regular and versioned buckets, and replaces the RPC client's xceiver factory with mocks. Each test increments the container id and resets SCM/datanode mocks. Happy-path reads write a key, fetch its container pipeline from SCM once, read from the mocked datanode, then read a second key in the same container and assert SCM is not called again. Error-path tests inject datanode `GetBlock` or `ReadChunk` failures, optionally reconfigure SCM to return a DN2 pipeline, and assert either a successful refresh/retry or a fast propagated exception.

## State and persistence behavior
Persistent OM state is limited to in-process metadata tables created through `OMRequestTestUtils`; actual block data is synthetic datanode responses. The relevant persisted signal is that key metadata stores a block location whose container id is later resolved through OM's container location cache. The cache should retain usable Ratis pipelines, refuse to retain empty pipelines, and cache EC pipelines only when all required data replica indexes are present.

## Dependencies and integration points
This test sits at the boundary between OM metadata, SCM container-location lookup, and the Ozone RPC client read path. It depends heavily on Mockito spies, `XceiverClientManager`, HDDS pipeline/container helper classes, protobuf datanode command types, checksum creation, and Ozone client stream semantics. It also integrates with network-topology-aware read configuration.

## Risks and edge cases
The main risks are stale cached container locations after datanode movement, caching unusable empty pipelines, EC reads with insufficient data indexes, and over-refreshing on authentication or unrelated IO failures. Mockito matching is narrow: changes to acquisition methods, EC pipeline shape, or datanode command sequencing may make this test fail before product behavior is actually broken.

## Test signals
Assertions check byte-for-byte data reads, exact SCM `getContainerWithPipelineBatch` call counts, expected exception classes/messages, and EC cache/no-cache behavior across repeated `getKey` calls. These signals directly verify cache reuse, cache invalidation, and non-cacheable pipeline handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmContainerLocationCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmInit.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmInit.java

## Purpose
Small integration test proving OM initialization is idempotent enough to run again after an already initialized MiniOzoneCluster OM is stopped.

## Important APIs, types, and functions
- Uses `MiniOzoneCluster.newBuilder(conf).build()` and `waitForClusterToBeReady()` to create a normal cluster.
- Calls `cluster.getOzoneManager().stop()` and then `OzoneManager.omInit(conf)`.
- JUnit lifecycle is static `@BeforeAll`/`@AfterAll`; assertion is `assertTrue`.

## Control flow
The class starts one MiniOzoneCluster for all tests, waits for readiness, stops the active OM in `testOmInitAgain`, then calls the static initialization path against the same configuration. Cleanup shuts the cluster down if it exists.

## State and persistence behavior
The test depends on metadata and VERSION files produced by the original cluster initialization. Re-running `omInit` should recognize existing storage and succeed rather than treating prior initialization as corruption or a fatal duplicate operation.

## Dependencies and integration points
It exercises `OzoneManager.omInit`, MiniOzoneCluster storage initialization, and Hadoop authentication exception plumbing. It is intentionally high-level and does not inspect the OM database directly.

## Risks and edge cases
Coverage is narrow: it only checks success after a clean `stop`, not partially initialized metadata, secure OM init, HA init, or failed prior initialization. Because it reuses cluster configuration, failures usually indicate a regression in storage init idempotency.

## Test signals
The only behavioral signal is that `omInit(conf)` returns `true` without throwing `IOException` or `AuthenticationException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmMetrics.java

## Purpose
Integration test suite for `OMMetrics` counters across volume, bucket, key, directory, snapshot, and ACL operations. It validates both success counters and failure counters by combining real MiniOzoneCluster operations with white-box fault injection.

## Important APIs, types, and functions
- Uses `MiniOzoneCluster`, `OzoneManagerProtocol`, `ObjectStore`, `OMMetrics`, `MetricsAsserts.getMetrics/getLongCounter`, and `HddsWhiteboxTestUtils`.
- Operation helpers `doVolumeOps`, `doBucketOps`, and `doKeyOps` intentionally swallow IO exceptions so metric increments can be asserted after injected failures.
- `mockWritePathExceptions` spies `OMMetadataManager` tables and forces `RocksDatabaseException` from `Table.isExist` to exercise write failure metrics.
- Key helpers build `OmKeyArgs` with `OmKeyLocationInfo`, `BlockID`, `MockPipeline`, Ratis or EC replication configs, and owner names.

## Control flow
The suite starts a five-datanode cluster with metrics-save interval, faster directory deleting service, filesystem-path support, and snapshot rename enabled. Each operation test records initial counters, performs successful operations, verifies deltas, injects manager or metadata failures, repeats operations, verifies failure deltas, and restores white-box state. Snapshot testing creates keys and snapshots, waits for diff jobs, lists/cancels diffs, gets/lists/renames/deletes snapshots, and checks invalid cases. Directory testing runs for `FILE_SYSTEM_OPTIMIZED` and `LEGACY` bucket layouts through OFS filesystem paths.

## State and persistence behavior
The test creates real OM metadata in RocksDB through cluster APIs. It observes aggregate counters such as current `NumVolumes`, `NumBuckets`, `NumKeys`, active/deleted snapshot counts, EC bucket/key create totals, block allocation failures, and directory delete cleanup effects. Background services matter: directory deletion must decrement key counts, and snapshot diff jobs must reach `DONE`.

## Dependencies and integration points
It integrates OM manager classes (`VolumeManager`, `BucketManager`, `KeyManager`, `OmMetadataReader`), Ozone client protocol, Hadoop `FileSystem` over OFS, snapshot diff service, ACL authorization types, metrics2/JMX records, EC replication placement, and RocksDB table abstractions.

## Risks and edge cases
The test is timing-sensitive around background directory deletion and snapshot diff completion. It also relies on private-field names for white-box replacement, so refactors of OM internals can break tests without changing external behavior. Counter deltas are exact and may need updates when new sub-operations are added.

## Test signals
Signals are exact metric counter deltas after success and failure paths, expected EC placement failure text for insufficient datanodes, `GenericTestUtils.waitFor` cleanup convergence, snapshot invalid-operation exceptions, and direct `OMMetrics` getter increments for HA-style ACL calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmStartupSlvLessThanMlv.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmStartupSlvLessThanMlv.java

## Purpose
Verifies OM refuses to start when the on-disk metadata layout version is newer than the software layout version supported by the running binary.

## Important APIs, types, and functions
- Uses `OMLayoutFeature.values()` to compute the largest supported software layout version.
- Uses `UpgradeTestUtils.createVersionFile` with `HddsProtos.NodeType.OM` to create a VERSION file.
- Starts through `MiniOzoneCluster.newBuilder(conf).build()` and expects `OMException`.

## Control flow
The test creates an `om/current` directory inside a JUnit temp folder, points `OZONE_OM_DB_DIRS` at that folder, writes a VERSION file with MLV set to `largestSlv + 1`, then builds a MiniOzoneCluster under disabled logging. Startup must throw before the cluster is usable.

## State and persistence behavior
The only persisted state is the VERSION file under OM metadata storage. The version manager must compare the stored metadata layout version against compiled layout features and reject future metadata to avoid unsafe downgrade/open behavior.

## Dependencies and integration points
This test integrates upgrade layout metadata, OM storage initialization, MiniOzoneCluster startup, and `MiniOzoneClusterImpl` logging. It is a guard for upgrade/downgrade compatibility logic.

## Risks and edge cases
The assertion hard-codes the exact exception message using `mlv` and `mlv - 1`, so message changes or non-contiguous layout versions can affect it. It does not test equal versions, lower versions, or HA storage directories.

## Test signals
Expected signal is an `OMException` from cluster build with the precise message that metadata layout version is greater than software layout version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmStartupSlvLessThanMlv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerConfiguration.java

## Purpose
Tests OM configuration parsing for single-node and HA services, including address defaults, peer/ratis address derivation, unresolved hosts, invalid HA configs, and multiple service IDs.

## Important APIs, types, and functions
- Builds `MiniOzoneCluster` without datanodes from an `OzoneConfiguration` rooted in a temp metadata directory.
- Uses `OMConfigKeys`, `ConfUtils.addKeySuffixes`, `OZONE_OM_SERVICE_IDS_KEY`, `OZONE_OM_NODES_KEY`, `OZONE_OM_ADDRESS_KEY`, and `OZONE_OM_RATIS_PORT_KEY`.
- Inspects `OzoneManager.getOmRpcServerAddr`, `getPeerNodes`, `getOMServiceId`, `getOmRatisServerState`, `OzoneManagerRatisServer.getRaftGroup`, and `RaftPeer` addresses.

## Control flow
Each test prepares a different configuration and then calls `startCluster`. Positive tests assert local address binding, default RPC/Ratis ports, selected local OM node id, peer count, peer addresses, unresolved peer metadata, and service ID selection. Negative tests run startup under disabled logs and expect `OzoneIllegalArgumentException` for no local matching address, missing node list, or missing OM addresses.

## State and persistence behavior
The cluster writes metadata under a temp path, but the tested state is runtime configuration materialized into OM node details and Ratis peer groups. No long-lived metadata content is inspected.

## Dependencies and integration points
This file sits between configuration keys, HA node discovery, NetUtils local-address checks, MiniOzoneCluster construction, OM Ratis server setup, and Ratis peer configuration.

## Risks and edge cases
Tests use dummy IPs and `0.0.0.0` to force local-node detection. Address resolution behavior can vary by environment, so unresolved-host assertions deliberately check `isHostUnresolved` and null inet addresses. Exact exception messages are part of the contract.

## Test signals
Signals include cluster readiness, Ratis lifecycle `RUNNING`, expected `RaftPeer` counts and addresses, selected service/node ids, unresolved peer flags, and expected startup exceptions/messages for invalid configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHA.java

## Purpose
Abstract base for standard OM HA integration tests. It initializes the shared HA cluster without follower-read mode and provides a helper to stop the current leader.

## Important APIs, types, and functions
- Extends `AbstractOzoneManagerHATest`.
- Static `init` calls `initCluster(false)`.
- `stopLeaderOM` uses `OmTestUtil.getCurrentOmProxyNodeId(getObjectStore())` and `getCluster().stopOzoneManager(nodeId)`.

## Control flow
Subclasses inherit a ready HA cluster from `@BeforeAll`. When a test needs failover, `stopLeaderOM` asks the client failover proxy which OM is currently serving as leader and stops that node.

## State and persistence behavior
The base does not mutate metadata directly. It controls cluster process state by stopping OM nodes while preserving the shared HA metadata/Ratis state managed by `AbstractOzoneManagerHATest`.

## Dependencies and integration points
It binds subclass tests to the common HA harness, object store client failover provider, MiniOzoneHACluster node control, and OM leader discovery utilities.

## Risks and edge cases
Because the helper trusts the current client proxy node, stale proxy state can stop a node that was leader from the client's view rather than the cluster's latest leader. Subclasses typically wait for leader readiness around node restarts.

## Test signals
This base has no assertions of its own; its signal is successful cluster initialization and correct behavior of subclasses that depend on stopping the leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerRead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerRead.java

## Purpose
Abstract base for OM HA tests with follower-read mode enabled. It centralizes cluster initialization and the expected read failure handling when quorum or connectivity is unavailable.

## Important APIs, types, and functions
- Extends `AbstractOzoneManagerHATest`.
- Static `init` calls `initCluster(true)`.
- `listVolumes(boolean checkSuccess)` calls `getObjectStore().getClientProxy().listVolumes(null, null, 100)` and validates acceptable failures.

## Control flow
Subclasses start from a follower-read-enabled HA cluster. `listVolumes(false)` permits several failure shapes: a `RemoteException` wrapping a Ratis `RaftException`, a `ConnectException` with connection refused, or a leader-determination/connectivity message. `listVolumes(true)` rethrows unexpected IO failures.

## State and persistence behavior
No metadata is created here. The base focuses on read consistency/failure semantics under changing cluster availability and lets subclasses drive OM node state.

## Dependencies and integration points
It integrates the Ozone client proxy, follower-read HA mode, Hadoop IPC `RemoteException`, Java network exceptions, and Ratis read-index/read-timeout exception surfaces.

## Risks and edge cases
The accepted failure messages/classes encode client retry ordering and last-proxy behavior; changes in retry policy can alter which exception is observed. It intentionally checks broad message alternatives for non-RemoteException cases.

## Test signals
The reusable signal is that successful list-volume reads complete silently, while expected degraded-cluster failures are classified as Ratis quorum/read failures or connection failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithAllRunning.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithAllRunning.java

## Purpose
Follower-read HA integration tests where all OM nodes stay running. It verifies follower proxy initialization, follower targeting, linearizable read consistency, normal object operations, response leader metadata, and read consistency mode metrics.

## Important APIs, types, and functions
- Uses `HadoopRpcOMFollowerReadFailoverProxyProvider`, `HadoopRpcOMFailoverProxyProvider`, `OMProxyInfo`, `OmTransport`, and `OzoneManagerProtocolClientSideTranslatorPB`.
- Exercises client APIs for volumes, buckets, files, deletes, and `headObject/listKeys`.
- Reads configs `OZONE_CLIENT_FOLLOWER_READ_ENABLED_KEY`, `OZONE_CLIENT_FOLLOWER_READ_DEFAULT_CONSISTENCY_KEY`, and `OZONE_CLIENT_LEADER_READ_DEFAULT_CONSISTENCY_KEY`.
- Directly submits protobuf `OMRequest` messages for suggested-leader and leader-node-id checks.

## Control flow
The suite first confirms follower-read proxy maps contain every OM RPC address and that a forced initial follower remains the last proxy after a read. It then checks write requests sent to a follower fail with `OMNotLeaderException` and suggested leader. Linearizable consistency uses a second client to immediately read keys written by the first client. Reused object-operation tests mirror the all-running HA suite. Later tests validate returned `leaderOMNodeId`, leader-only clients after leadership transfer, linearizable leader-read metrics, and local-lease follower-read metrics.

## State and persistence behavior
The tests create real volumes, buckets, keys, and directory-like paths in the HA OM metadata replicated through Ratis. They also observe metrics state on specific OM nodes: `NumLinearizableRead` on the leader and `NumFollowerReadLocalLeaseSuccess` on the selected follower/current proxy.

## Dependencies and integration points
This class covers the unified OM transport, separate leader and follower-read failover providers, OM Ratis leader status, client-side consistency configuration, object-store metadata APIs, and protobuf server translator behavior.

## Risks and edge cases
`testLinearizableReadConsistency` is marked flaky, showing timing sensitivity in cross-client read-after-write visibility. Tests that force proxy selection rely on test-only provider methods. Metrics assertions depend on a request hitting the expected node and consistency path.

## Test signals
Signals include exact proxy counts/address matches, last-proxy node ids, suggested-leader exception suffixes, immediate cross-client key visibility, expected file operation `OMException` codes, stable leader proxy state, and increasing read-consistency metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithAllRunning.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithStoppedNodes.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithStoppedNodes.java

## Purpose
Follower-read HA integration tests for stopped/restarted OM nodes. It verifies that leader and follower-read proxy providers fail over correctly when selected OMs go down, and that reads fail with expected Ratis/connectivity errors when quorum is lost.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHAFollowerRead`.
- Uses `MiniOzoneHAClusterImpl`, `HadoopRpcOMFailoverProxyProvider`, `HadoopRpcOMFollowerReadFailoverProxyProvider`, and `OMProxyInfo`.
- Exercises volume/key creation, multipart upload create/complete/read, list volumes, and retry proxy logging.
- Helpers `changeFollowerReadInitialProxy(int/String)` force the follower-read provider to start from a target OM.

## Control flow
Before each test it waits for a ready leader; after each test it restarts all OMs. One-node-down tests stop a selected OM and expect writes/keys to succeed. Two-node-down tests expect writes to fail and follower reads to fail through `listVolumes(false)`. Multipart upload starts normally, then leader is stopped and the upload/read sequence must complete through failover. Separate tests verify leader proxy failover, follower-read proxy failover, skipping a stopped follower, incremental wait-time accounting, and max-failover retry logging when all OMs are stopped.

## State and persistence behavior
The suite creates replicated HA metadata for volumes, buckets, keys, and multipart upload state. Node stop/restart affects availability but should not lose committed metadata. Retry wait time and current proxy state are in-memory client/provider state.

## Dependencies and integration points
It integrates Ozone HA cluster lifecycle controls, client leader and follower-read failover providers, multipart upload metadata, Ratis leader election timing, log4j `LogVerificationAppender`, and node failure timeout constants.

## Risks and edge cases
Tests use sleeps based on `NODE_FAILURE_TIMEOUT` and client retry defaults, so they are timing-sensitive. The max-retry log assertions depend on exact log text. Follower-read behavior is sensitive to which node is the initial/current proxy.

## Test signals
Signals include operation success/failure booleans, changed proxy node ids after failover, follower-read provider still using follower reads, skipped stopped follower id, increased same-node wait time, and expected counts of failover log lines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAFollowerReadWithStoppedNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithAllRunning.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithAllRunning.java

## Purpose
Standard OM HA integration tests where all OM nodes remain running. It covers object-store operations, client failover metadata, Ratis/JMX exposure, retry cache semantics, ACL behavior, link bucket ACL propagation, snapshots, and follower-read disabled fallback.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHA` and uses common helpers from `AbstractOzoneManagerHATest` such as `setupBucket`, `createKey`, `testCreateFile`, and ACL helpers.
- Uses `HadoopRpcOMFailoverProxyProvider`, `HadoopRpcOMFollowerReadFailoverProxyProvider`, `OzoneManagerRatisServer`, `OMRatisHelper`, `OzoneManagerProtocolServerSideTranslatorPB`, `RaftServer`, and `RaftClientRequest`.
- Builds `OzoneObj` instances for bucket/key/prefix ACL operations and resolves link buckets back to source buckets for ACL equality.

## Control flow
Early tests validate recursive/non-recursive file creation, key deletion partial failures, volume and bucket CRUD, proxy initialization, suggested-leader exceptions, read failover to leader, JMX Ratis metrics, and retry-cache behavior by submitting duplicate Ratis requests with the same client/call id before and after cache expiry. ACL tests add/remove/set ACLs on buckets, keys, prefixes, and link buckets, then compare source/link ACL views. Ratis snapshot testing drives enough key writes to cross snapshot thresholds twice. The final test enables client follower-read against a cluster without follower-read support and expects fallback to leader-only reads.

## State and persistence behavior
The class creates HA-replicated volumes, buckets, keys, directories, prefixes, ACL entries, link buckets, retry-cache entries, and Ratis snapshots. Retry cache state is temporary and expires after configured duration. Snapshot index state is read from OM transaction info/Ratis state. ACL state must be stored against source buckets when link buckets are used.

## Dependencies and integration points
It integrates OM HA client routing, Ratis state machine submission, Hadoop UGI, Ozone object-store APIs, ACL authorizer data structures, JMX MBean server, Ratis application metrics, and link bucket source resolution.

## Risks and edge cases
Exact log/cache behavior and private retry-cache timing make the retry test sensitive. Link bucket ACL tests depend on recursive source resolution and default ACLs added by the RPC client. Snapshot tests depend on write volume and snapshot threshold configuration inherited from the HA harness.

## Test signals
Signals include expected `OMException` result codes, proxy map size/address matches, current proxy id equals leader id after read failover, MBean availability and nonnegative count, retry duplicate not re-executing before cache expiry, ACL list equality across link/source objects, and increasing Ratis snapshot indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithAllRunning.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithStoppedNodes.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithStoppedNodes.java

## Purpose
Standard OM HA integration tests for leader/follower outages and restarts. It validates write availability with one OM down, failure with quorum loss, multipart upload failover, OM restart catch-up through snapshot install, key deletion replication, retry proxy behavior, list volumes after leader loss, HA metrics, and retry-cache continuity after leadership transfer.

## Important APIs, types, and functions
- Extends `TestOzoneManagerHA`.
- Uses `MiniOzoneHAClusterImpl`, `HadoopRpcOMFailoverProxyProvider`, `OMHAMetrics`, `KeyDeletingService`, `LogVerificationAppender`, and low-level `OzoneManagerProtocolProtos.OMRequest`.
- Uses Ratis `RaftClient.admin().transferLeadership` to force a new leader for retry-cache testing.
- Multipart helpers initiate MPU, create part keys, complete MPU with ETags, list parts, and read back data.

## Control flow
Each test starts after leader readiness and restarts OMs afterward. The suite stops one or two OMs and verifies operation success/failure. It stops the current proxy/leader to verify failover. Restart testing stops a follower, advances the leader far beyond purge gap, asserts the follower lags behind the leader snapshot, restarts it, waits for catch-up, then checks it applies later writes. Other tests validate list parts after leader stop, Ratis appender wait config, deleted table cleanup on all OMs, wait-time increments for same-node failover, HA leader-state metrics before/after leader restart, retry exhaustion logs, list-volume results after leader stop, and retry-cache reuse on a new leader after old leader shutdown.

## State and persistence behavior
The tests create and replicate volumes, buckets, keys, multipart upload parts, deleted-table entries, retry cache entries, Ratis logs, and snapshots. Key deletion state must be drained by `KeyDeletingService` and reflected in every OM's metadata table. Restart catch-up depends on snapshot installation when purged logs are unavailable.

## Dependencies and integration points
It spans HA cluster lifecycle, OM Ratis log/snapshot internals, client retry/failover state, multipart upload metadata, key deleting background service, OM HA metrics, Hadoop IPC current-call context, and Ratis leadership transfer.

## Risks and edge cases
Several tests are timing-sensitive due to sleeps and background services. Exact log message counts can change with retry policy changes. Low-level retry-cache tests manually set `Server.getCurCall`, so RPC/Ratis plumbing changes can affect setup.

## Test signals
Signals include operation success booleans, changed proxy/leader node ids, follower last-applied index catching up to snapshot index, part ETag equality, empty deleted tables on all OMs, HA leader-state metric values, retry log counts, expected `KEY_NOT_FOUND` after rename, and duplicate request success from retry cache on the new leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHAWithStoppedNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumes.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumes.java

## Purpose
Abstract non-HA integration test for `ObjectStore.listVolumesByUser` and `listVolumes` under ACL-enabled/disabled and `ozone.om.volume.listall.allowed` combinations.

## Important APIs, types, and functions
- Implements `NonHATests.TestCase` and uses `cluster().newClient()` from the test harness.
- Uses `ObjectStore`, `ClientProtocol.setVolumeOwner`, `OzoneObjInfo`, `OzoneAcl.parseAcls`, and UGI login switching.
- Helper `checkUser` validates both user-scoped listing and list-all behavior with expected permission failures.

## Control flow
`@BeforeAll` creates five uniquely prefixed volumes as admin, assigns owners user1/user2, and sets ACLs so some volumes are owner-accessible, some cross-user accessible, and one world-accessible. Each test switches login UGI and configures `setListAllVolumesAllowed`, then checks expected visible volumes and whether list-all should succeed. Parameterized tests cover ACL-disabled behavior for both list-all settings.

## State and persistence behavior
The suite persists volume ownership and ACLs in OM metadata. It mutates in-memory OM config `listAllVolumesAllowed` per test and restores the default in `@AfterEach`. Login user state is also reset after each test.

## Dependencies and integration points
It integrates non-HA MiniOzoneCluster harnesses, client volume APIs, ACL parsing/authorization, UGI identity/short-name behavior, config assumptions for ACL-enabled mode, and default `s3v` volume visibility.

## Risks and edge cases
The tests are conditional via `assumeConfig`, so coverage depends on the cluster's ACL config. Runtime exceptions wrap `OMException`, and the helper must preserve unexpected causes. Expected lists include ACL-derived access rather than exact full listing except for count/list-all checks.

## Test signals
Signals include accessible volume sets containing expected names, exact count of five prefixed volumes for list-all, `PERMISSION_DENIED` for disallowed non-admin list-all/list-other-user cases, and successful short-name handling for a Kerberos-style username.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumesSecure.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumesSecure.java

## Purpose
Secure-mode counterpart for list-volume authorization. It starts a Kerberos-backed standalone OM and verifies list-by-user and list-all behavior with ACL enabled and disabled, including OM admin principals from the configured host and another host.

## Important APIs, types, and functions
- Uses `MiniKdc`, Kerberos keytabs, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, and `doAs`.
- Starts `OzoneManager` directly with secure settings, `OMStorage`, test certificate/secret-key clients, and a testing SCM topology client.
- Uses `OzoneManagerProtocolClientSideTranslatorPB` over `OmTransportFactory.create` for direct OM protocol calls.
- Nested classes `AclEnabled` and `AclDisabled` start separate OM instances with different `OZONE_ACL_ENABLED` settings.

## Control flow
Global setup starts MiniKdc, creates admin/user principals and keytabs, configures Kerberos, and logs in UGIs. `startOM` creates a fresh metadata directory, initializes OM storage with a cert serial id, starts secure OM, creates six volumes with owners and optional ACLs, then closes the admin client. Nested tests toggle `om.getConfig().setListAllVolumesAllowed`, run checks under user/admin UGIs, and stop OM after each nested class.

## State and persistence behavior
Each nested mode writes a fresh OM metadata store containing volume ownership, ACL entries, default `s3v`, and secure VERSION/cert metadata. Authorization behavior depends on current UGI, ACL-enabled config, and runtime `listAllVolumesAllowed`.

## Dependencies and integration points
The test integrates Kerberos authentication, secure OM startup, native ACL authorizer, OM storage initialization, certificate and secret-key client test doubles, SCM topology client stubs, and direct protobuf client transport.

## Risks and edge cases
Secure setup is environment-sensitive because it uses canonical local host names and MiniKdc. `checkUser` closes the client in both try and finally paths, which relies on close idempotency. Admin principal matching intentionally covers another host, so admin short-name/host rules are part of the contract.

## Test signals
Signals include exact accessible volume sets for each UGI, successful or denied list-all according to ACL/list-all config, six explicitly created volumes plus `s3v` for admin expectations, and `PERMISSION_DENIED` classification for expected failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumesSecure.java -->
