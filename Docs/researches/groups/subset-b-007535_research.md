# subset-b-007535 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestBlockToken.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestBlockToken.java

## Purpose
`TestBlockToken` is a broad security test suite for HDFS block access tokens. It validates `BlockTokenIdentifier` serialization in legacy and protobuf formats, `BlockTokenSecretManager` token generation and verification, `BlockPoolTokenSecretManager` key distribution, token-backed datanode RPC authorization, storage type and storage ID matching, block-token serial number ranges, and client behavior when a last in-progress block token expires.

## Important APIs, Types, and Functions
The file centers on `BlockTokenSecretManager`, `BlockTokenIdentifier`, `BlockPoolTokenSecretManager`, `ExportedBlockKeys`, `Token<BlockTokenIdentifier>`, `ExtendedBlock`, `LocatedBlock`, and `MiniDFSCluster`. Helper methods include `generateTokenId`, `checkAccess`, `tokenGenerationAndVerification`, `createMockDatanode`, `testBlockTokenRpc`, `testBlockTokenRpcLeak`, `testCraftedBlockTokenIdentifier`, `writeAndReadBlockToken`, and `testBadStorageIDCheckAccess`. `GetLengthAnswer` is a Mockito `Answer` used by a mock `ClientDatanodeProtocolPB` RPC endpoint to verify the current UGI contains exactly the expected block token.

## Control Flow
Each test resets UGI to simple auth, then specific RPC tests enable Kerberos-style SASL. Secret-manager tests create master/slave managers, export keys from the master, import them into the slave, generate single-mode and multi-mode tokens, update keys, and repeat verification. RPC tests start a local protobuf RPC server with a secret manager, attach a token to a remote UGI, call `getReplicaVisibleLength`, and assert that server-side token identity and access checks pass. Serialization tests deliberately parse token bytes with both encodings and assert the auto-detecting `readFields` path chooses the expected format. MiniDFSCluster tests create files, fetch located blocks, shorten token lifetime, and read after expiry to assert no slow refetch path is required for completed last blocks.

## State and Persistence Behavior
The suite mutates global `UserGroupInformation` configuration, uses per-test `BlockTokenSecretManager` key state, writes token identifiers to `DataOutputBuffer`, reads them through `DataInputBuffer` and `DataInputStream`, and creates temporary MiniDFSCluster file/block state. The RPC leak test counts `/proc/self/fd` descriptors and is guarded by `assumeTrue(FD_DIR.exists())`. `FieldUtils` mutates private identifier storage fields to simulate old NameNodes that did not include storage metadata.

## Dependencies and Integration Points
Dependencies span HDFS security token classes, protobuf RPC (`ProtobufRpcEngine2`, `ClientDatanodeProtocolPB`), IPC client/server code, `DFSUtilClient` datanode proxy creation, MiniDFSCluster, `DistributedFileSystem`, Mockito, Apache Commons reflection, and `SecurityTestUtil`. The tests integrate block-token semantics with storage type/ID authorization, RPC SASL token transport, block location generation, and NameNode block manager token expiry behavior.

## Risks and Test Signals
Important risks are global UGI state leakage, timing sensitivity in token expiry and RPC leak loops, platform dependence on `/proc/self/fd`, brittle crafted-byte expectations, and compatibility between legacy and protobuf token encodings. Strong signals include explicit equality and inequality checks for parsed identifiers, expected `InvalidToken` failures for bad storage IDs, key-update range assertions across many serial numbers, RPC round-trip authorization, descriptor leak bounds, and MiniDFSCluster reads after token expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestBlockToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestUpdateDataNodeCurrentKey.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestUpdateDataNodeCurrentKey.java

## Purpose
This test verifies that DataNodes receive and retain the current HDFS block-token key from the correct NameNode in an HA topology. It covers standby startup, active NameNode failover, DataNode joins after activation, and standby restart scenarios.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `DFSConfigKeys.DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, `DataNode`, `BlockPoolTokenSecretManager`, `BlockKey`, `DatanodeInfo`, and `HdfsConstants.DatanodeReportType.LIVE`. Test methods are `testUpdateDatanodeCurrentKeyWithStandbyNameNodes`, `testUpdateDatanodeCurrentKeyWithFailover`, and `testUpdateDatanodeCurrentKeyFromActiveNameNode`.

## Control Flow
`setup` builds a one-DataNode HA cluster with block access tokens enabled and replication/reconstruction settings adjusted for fast test behavior. The standby test reads the block pool ID from NameNode 0 and asserts the DataNode's block-pool token manager already has a non-null current key. The failover test transitions NameNode 0 active, waits briefly for propagation, compares the active NameNode's block token secret manager current key to the DataNode current key, and expects equality. The new-DataNode test activates NameNode 0, starts a second DataNode, confirms two live DataNodes, restarts the standby NameNode, then asserts old and new DataNodes both match the active NameNode current key.

## State and Persistence Behavior
The primary state is cluster-local HA NameNode state, DataNode block-pool token secret manager state, and current `BlockKey` values. Cluster lifecycle is owned by `@BeforeEach` and `@AfterEach`, and `cluster.shutdown()` clears MiniDFSCluster state. The test does not write application files; it relies on block-pool registration, heartbeats, and key update propagation.

## Dependencies and Integration Points
The file integrates HDFS HA MiniDFSCluster startup, NameNode active/standby transitions, DataNode block-pool token managers, NameNode block manager token secret manager, and DataNode live reports. It specifically exercises the NameNode-to-DataNode key distribution path used when block access tokens are enabled.

## Risks and Test Signals
Timing is the main risk: `Thread.sleep(3000)` assumes key propagation has completed after active transition. The duplicate config set for `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY` is harmless but noisy. Test signals are direct `assertTrue(currentKey != null)` and `assertEquals` comparisons between active NameNode and DataNode `BlockKey` instances after failover and DataNode addition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/token/block/TestUpdateDataNodeCurrentKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/ITestInMemoryAliasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/ITestInMemoryAliasMap.java

## Purpose
`ITestInMemoryAliasMap` is an integration test for the LevelDB-backed in-memory alias map used by HDFS provided storage. It validates missing reads, write/read round trips, listing, and snapshot isolation for block-to-provided-storage mappings.

## Important APIs, Types, and Functions
The file uses `InMemoryAliasMap`, `InMemoryAliasMap.IterationResult`, `Block`, `ProvidedStorageLocation`, `Path`, `DFSConfigKeys.DFS_PROVIDED_ALIASMAP_INMEMORY_LEVELDB_DIR`, Java `Optional`, and `FileUtils`. Test methods are `readNotFoundReturnsNothing`, `readWrite`, `list`, and `testSnapshot`.

## Control Flow
`setUp` creates a temporary directory, adds a block-pool subdirectory, points the alias-map LevelDB directory configuration at it, and initializes `InMemoryAliasMap` for `bpid-0`. Tests create `Block` keys and `ProvidedStorageLocation` values with path, offset, length, and nonce data. `readNotFoundReturnsNothing` asserts absent blocks return `Optional.empty`. `readWrite` writes one mapping and reads it back. `list` writes three mappings and expects one complete page with no continuation block. `testSnapshot` writes one block, creates a snapshot, writes a second block, opens a new alias map from the snapshot path, and confirms only the first block is visible.

## State and Persistence Behavior
Persistent state is LevelDB data under the temporary alias-map directory. The snapshot test creates an on-disk snapshot file/directory and reopens it through normal `InMemoryAliasMap.init` configuration. `tearDown` closes the alias map and deletes the block-pool temp directory, so failures can leave temp data behind if close/delete is interrupted.

## Dependencies and Integration Points
The test integrates provided-storage metadata classes with the `InMemoryAliasMap` storage backend and snapshot creation. It depends on filesystem temp directories, Apache Commons IO deletion, and HDFS `ProvidedStorageLocation` equality semantics.

## Risks and Test Signals
The class comment notes it is integration-style because the alias map cannot safely run in parallel when ports conflict, although this file primarily uses local LevelDB paths. Risks include temp directory cleanup, snapshot path configuration correctness, and iteration ordering assumptions being avoided by only checking count and no next block. Signals are optional-presence assertions, equality of full `ProvidedStorageLocation`, list size of three, and snapshot isolation across writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/ITestInMemoryAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/TestSecureAliasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/TestSecureAliasMap.java

## Purpose
`TestSecureAliasMap` verifies that a secured HDFS cluster can create and use a provided-storage alias map reader over the secured NameNode/DataNode communication path. It is focused on Kerberos and SSL/TLS configuration around provided storage.

## Important APIs, Types, and Functions
The file uses `MiniKdc`, `MiniDFSCluster.setupKerberosConfiguration`, `MiniDFSCluster.setupNamenodeProvidedConfiguration`, `SecurityUtil`, `UserGroupInformation`, `KeyStoreTestUtil`, `StorageType.PROVIDED`, `BlockManager`, `BlockAliasMap`, `FsDatasetSpi.FsVolumeReferences`, and `FsVolumeSpi`. The single test is `testSecureConnectionToAliasMap`.

## Control Flow
`init` creates a test directory, starts a MiniKdc, configures Kerberos authentication in `baseConf`, creates user and HTTP principals, and prepares SSL material. `testSecureConnectionToAliasMap` clones the secure configuration, enables NameNode provided-storage settings, assigns a free in-memory alias-map RPC address, starts a MiniDFSCluster with one DataNode containing `DISK` and `PROVIDED` storage, and waits for activation. It locates the DataNode's provided volume, reads its block-pool list, obtains the NameNode `BlockManager` alias map, and asserts a `BlockAliasMap.Reader` can be created for that block pool. `destroy` stops KDC and removes SSL/test directories; `shutdown` closes the filesystem and cluster.

## State and Persistence Behavior
The test creates persistent temp security artifacts: KDC database, keytab, SSL keystores, and MiniDFSCluster directories. Runtime state includes global UGI security configuration, provided-storage volume registration, and alias-map RPC service binding. Cleanup removes the base directory and SSL config after all tests.

## Dependencies and Integration Points
Integration points include Kerberos login configuration, SPNEGO principal setup, HDFS secure cluster boot, provided-storage volume exposure from the DataNode dataset, NameNode `ProvidedStorageMap`, and alias-map reader creation. It reuses `TestSecureNNWithQJM` only to locate a classpath SSL directory.

## Risks and Test Signals
Risks are security-global state leaking across tests, localhost vs `127.0.0.1` principal behavior on Windows, free-port races, and provided volume lookup returning null if storage registration fails. Signals include security-enabled assertion, one provided block pool, non-null alias map reader, and cluster lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/aliasmap/TestSecureAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancer.java

## Purpose
`TestBalancer` is the main HDFS balancer test harness. It verifies balancer behavior for normal imbalance, uneven distribution, CLI parsing, include/exclude host lists, source/target filtering, rolling upgrade behavior, concurrent balancer leases, erasure-coded striped files, secure keytab execution, RPC throttling, and several exit-status paths.

## Important APIs, Types, and Functions
Important production types include `Balancer`, `Balancer.Cli`, `BalancerParameters`, `BalancingPolicy`, `Dispatcher`, `NameNodeConnector`, `ExitStatus`, `MiniDFSCluster`, `ClientProtocol`, `DatanodeInfo`, `LocatedBlocks`, `FSNamesystem`, and `SimulatedFSDataset`. Core helpers are `initConf`, `initSecureConf`, `createFile`, `generateBlocks`, `distributeBlocks`, `testUnevenDistribution`, `waitForHeartBeat`, overloaded `waitForBalancer`, `doTest`, `runBalancer`, `runBalancerCli`, `testBalancerDefaultConstructor`, `spyFSNamesystem`, and `testBalancerRPCDelay`. `HostNameBasedNodes` and `PortNumberBasedNodes` model added node sets and host filters.

## Control Flow
Most tests configure small simulated-capacity clusters with 100-byte blocks, write data to make original nodes partially full, start empty nodes, run balancer through either API or CLI, and poll NameNode reports until capacity and utilization match expectations. Uneven-distribution tests first generate blocks, shut down, rebuild without formatting, inject block reports with custom distributions, then rebalance. CLI tests parse invalid parameters, block-pool lists, hot-block intervals, host include/exclude lists, and host-file inputs. Rolling-upgrade tests enter safe mode, prepare upgrade, assert default balancer aborts, assert `runDuringUpgrade` succeeds, then finalize. Striped-file tests enable EC policy, create striped files, rebalance, trigger heartbeats/deletion reports, and verify located striped blocks. Secure keytab tests initialize MiniKdc and SSL config, log in with the balancer keytab, and run a functional unknown-datanode scenario under `doAs`.

## State and Persistence Behavior
The suite mutates static balancer behavior through `NameNodeConnector.setWrite2IdFile`, creates MiniDFSCluster data, creates and deletes include/exclude host files, creates a `balancer.id` lease file for concurrency tests, uses MiniKdc/keytab/SSL artifacts for secure tests, and spies on `FSNamesystem` to record `getBlocks` timing. `@AfterEach` shuts down clusters, while `@AfterAll` stops the KDC and deletes secure temp data. Many tests rely on heartbeat, block report, deletion report, and safe-mode state transitions.

## Dependencies and Integration Points
Dependencies cover HDFS cluster simulation, NameNode RPC URI discovery, DataNode storage reports, block placement, erasure coding (`StripedFileTestUtil`), Kerberos/SSL, Mockito spies, host topology, and balancer internal dispatchers. The class is also reused by companion tests such as encrypted transfer, SASL transfer, RPC delay, HA service tests, and balancer service mode tests.

## Risks and Test Signals
Risks include heavy timing sensitivity, random block distribution, global static flags, security-global UGI state, cleanup of balancer lease and host files, reflection into dispatcher fields, and several long-running MiniDFSCluster scenarios. Signals include exact exit-code assertions (`SUCCESS`, `NO_MOVE_BLOCK`, `NO_MOVE_PROGRESS`, `UNFINALIZED_UPGRADE`, `IO_EXCEPTION`), utilization variance checks, host-filter exclusion counts, parser exception messages, EC block placement verification, metrics around RPC throttling, and secure keytab login assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerHttpServer.java

## Purpose
`TestBalancerHttpServer` verifies that the balancer HTTP server honors the configured HTTP policy and binds/connects correctly. In this test, HTTP is enabled and HTTPS is configured but expected not to be reachable under `HTTP_ONLY`.

## Important APIs, Types, and Functions
The file uses `BalancerHttpServer`, `DFSConfigKeys.DFS_HTTP_POLICY_KEY`, `DFS_BALANCER_HTTP_ADDRESS_KEY`, `DFS_BALANCER_HTTPS_ADDRESS_KEY`, `HttpConfig.Policy.HTTP_ONLY`, `URLConnectionFactory`, `KeyStoreTestUtil`, and `NetUtils.getHostPortString`. `checkConnection` performs the actual URL open/connect/read probe.

## Control Flow
`setUp` creates a temp base directory, configures balancer HTTP and HTTPS bind addresses to `localhost:0`, generates SSL config even though the policy is HTTP-only, and creates a default URL connection factory. `testHttpServer` starts `BalancerHttpServer`, asserts an HTTP connection succeeds against `getHttpAddress`, asserts an HTTPS connection fails or has no address, and stops the server in `finally`. `tearDown` deletes temp files and SSL config.

## State and Persistence Behavior
State includes generated keystore material under the temp directory, static test configuration, and a running server socket during the test. The server is explicitly stopped, and SSL/test directories are cleaned after all tests.

## Dependencies and Integration Points
The test integrates the balancer's web server wrapper with Hadoop HTTP policy configuration, SSL test utilities, and Java URL connection behavior. It validates externally observable server reachability rather than internal fields.

## Risks and Test Signals
Risks include free-port binding races, localhost resolution differences, connection timeout slowness, and false negatives if `conn.getContent()` behavior changes. Signals are AssertJ truth checks: HTTP must connect, HTTPS must not connect under the selected policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerLongRunningTasks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerLongRunningTasks.java

## Purpose
`TestBalancerLongRunningTasks` contains slow, integration-heavy balancer tests for edge cases that require larger storage layouts or longer runtime: same-DataNode replica avoidance, RAM_DISK lazy persist behavior, minimum block size and source-node filtering, upgrade-domain and rack placement preservation, pinned blocks, top-node sorting, limiting over-utilized nodes, metrics duplicate registration, and max iteration time cancellation.

## Important APIs, Types, and Functions
The file uses `Balancer`, `BalancerParameters`, `BalancingPolicy.Node`, `ExitStatus`, `MiniDFSCluster`, `SimulatedFSDataset`, `LazyPersistTestCase`, `StorageType.RAM_DISK`, `BlockPlacementPolicyWithUpgradeDomain`, `BlockPlacementStatus`, `DatanodeManager`, `DataNodeTestUtils`, `DefaultMetricsSystem`, and `NameNodeConnector`. Helpers include `initConf`, `initConfWithRamDisk`, and `runBalancerAndVerifyBlockPlacmentPolicy`.

## Control Flow
Tests build MiniDFSClusters with carefully chosen storage capacities, storage types, racks, hosts, and upgrade domains. They create files to fill selected nodes, start new empty nodes, then call `Balancer.run` or run a single `Balancer.runOneIteration`. Placement tests verify every located block still satisfies the active placement policy after balancing. RAM_DISK tests create lazy-persist files, wait for lazy writer activity, add a new DataNode, and assert no RAM_DISK moves. Sorting tests mark DataNodes dead/alive in sequence to create deterministic utilization levels, run one balancer iteration with `-sortTopNodes` or `-limitOverUtilizedNum`, then assert bytes/blocks moved and maximum usage. The max-iteration-time test throttles bandwidth and mover threads so a 500 ms iteration must end with `NO_MOVE_PROGRESS`.

## State and Persistence Behavior
The tests rely on cluster storage state, DataNode liveness state, block reports, heartbeats, deletion reports, lazy-persist memory settings, sticky-bit pinned blocks, upgrade-domain metadata stored in the in-memory datanode manager, and the metrics system. Most clusters are shut down in `@AfterEach` or try-with-resources, but `DefaultMetricsSystem` mode is temporarily changed in the metrics duplicate test.

## Dependencies and Integration Points
Integration points include DataNode storage-type policies, lazy persist, block placement policies, balancer dispatcher node selection, NameNode block reports, metrics registration, client socket timeout behavior, and HDFS configuration parsing for balancer CLI flags. The class reuses `TestBalancer.createFile`, `TestBalancer.waitForHeartBeat`, and `TestBalancer.sum`.

## Risks and Test Signals
Risks are slow runtime, timing and heartbeat sensitivity, platform restriction for pinned blocks (`assumeNotWindows`), random block choice in sorting tests, and global metrics-system side effects. Signals include precise exit statuses, storage-type replica verification, block placement satisfaction, exact top-node movement counts, maximum usage expectations, and zero moved blocks when max iteration time is too short.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerLongRunningTasks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerRPCDelay.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerRPCDelay.java

## Purpose
`TestBalancerRPCDelay` isolates balancer NameNode RPC throttling behavior. It verifies that balancer `getBlocks` calls are dispersed so the NameNode RPC queue is not saturated.

## Important APIs, Types, and Functions
The file delegates to `TestBalancer.testBalancerRPCDelay`. It uses `DFSConfigKeys.DFS_NAMENODE_GETBLOCKS_MAX_QPS_DEFAULT`, JUnit lifecycle methods, and class-level `@Timeout(100)`.

## Control Flow
`setup` constructs a `TestBalancer` instance and calls its setup method to initialize counters. `testBalancerRPCDelayQps3` runs the shared balancer RPC delay scenario with QPS 3. `testBalancerRPCDelayQpsDefault` runs the same scenario with the default configured QPS. `teardown` calls `TestBalancer.shutdown` to stop any cluster created by the delegated scenario.

## State and Persistence Behavior
All substantive state lives in the delegated `TestBalancer`: MiniDFSCluster, spied `FSNamesystem`, atomic counters for `getBlocks` count and timing, and balancer configuration. This wrapper owns lifecycle boundaries so the delegated cluster does not leak.

## Dependencies and Integration Points
The class integrates with `TestBalancer` rather than directly with HDFS internals. The underlying delegated path spies on NameNode `getBlocks` and verifies calls per second relative to configured QPS.

## Risks and Test Signals
Risks are mostly inherited timing sensitivity: elapsed wall-clock duration is rounded to seconds and can vary under load. Signals are the underlying assertions that the number of `getBlocks` calls reaches the target and that calculated calls per second do not exceed the configured maximum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerRPCDelay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerService.java

## Purpose
`TestBalancerService` tests the balancer's long-running service mode (`-asService`). It verifies repeated balancing without process exit, retry behavior after NameNode outages, and service metrics/MBean exposure.

## Important APIs, Types, and Functions
Key APIs include `Balancer.Cli`, `Balancer.stop`, `Balancer.getExceptionsSinceLastBalance`, `MiniDFSCluster` HA topology, `HATestUtil`, `NameNodeProxies`, `SubjectInheritingThread`, `DefaultMetricsSystem`, `MetricsAsserts`, `ManagementFactory`, and `VersionInfo`. Helpers are `setupCluster`, `addOneDataNode`, and `newBalancerService`.

## Control Flow
`setupCluster` starts an HA MiniDFSCluster, transitions NameNode 0 active, creates a failover-aware `ClientProtocol`, and writes a replicated file to fill two DataNodes to 30 percent. `addOneDataNode` starts an empty DataNode and waits for heartbeat stats. `newBalancerService` runs `Balancer.Cli` in a subject-inheriting thread. `testBalancerServiceBalanceTwice` starts service mode, waits for metrics initialization and nonzero bytes-left-to-move, waits for balance, adds another node, waits for balance again, then stops the service. `testBalancerServiceOnError` shuts down the active NameNode, waits for exception accounting, restarts it, rebalances, and verifies the exception count resets. `testBalancerServiceMetrics` verifies the BalancerInfo MBean version/revision and metrics tag block pool ID.

## State and Persistence Behavior
State includes an HA MiniDFSCluster, a long-lived balancer service thread, service interval configuration, balancer global stop flag, exception counters, Hadoop metrics sources, and JMX MBeans. Each test stops the balancer and shuts down the cluster in `finally`.

## Dependencies and Integration Points
Integration points are service-mode CLI parsing, failover proxy configuration, HA NameNode active/standby transitions, DataNode heartbeats, balancer metrics source naming by block pool ID, JMX BalancerInfo, and `TestBalancer` utility methods.

## Risks and Test Signals
Risks include thread lifecycle leaks if `Balancer.stop()` is not reached, metrics source timing, HA retry timing, and MBean registration races. Signals include successful repeated utilization convergence, `BytesLeftToMove` and `BytesMovedInCurrentRun` gauges, nonzero then reset exception counter, BalancerInfo version/revision content, and block-pool metrics tag assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithEncryptedTransfer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithEncryptedTransfer.java

## Purpose
This wrapper test verifies that the standard balancer scenarios work when HDFS data transfer encryption and block access tokens are enabled.

## Important APIs, Types, and Functions
The file uses `HdfsConfiguration`, `DFSConfigKeys.DFS_ENCRYPT_DATA_TRANSFER_KEY`, `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, and delegates to `TestBalancer.testBalancer0Internal`, `testBalancer1Internal`, and `testBalancer2Internal`.

## Control Flow
`setUpConf` enables encrypted data transfer and block access tokens on a shared configuration. Each test constructs a fresh `TestBalancer` and runs one of the core internal scenarios: balanced cluster plus new node, uneven distribution, and default-constructor balancing. The delegated tests initialize normal balancer configuration on top of the security settings.

## State and Persistence Behavior
This class owns only a configuration instance. Cluster creation, data files, token behavior, and shutdown are handled by the delegated `TestBalancer` methods and their internal `finally` blocks.

## Dependencies and Integration Points
The integration point is between balancer block movement and encrypted HDFS data transfer with block tokens. It ensures balancer copy paths can authenticate and move blocks under encryption rather than only in simple unencrypted clusters.

## Risks and Test Signals
Risks are inherited from `TestBalancer` plus encrypted transfer setup. Signals are delegated success: each scenario must complete within 60 seconds and satisfy `TestBalancer` exit-code and utilization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithEncryptedTransfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithHANameNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithHANameNodes.java

## Purpose
`TestBalancerWithHANameNodes` validates balancer behavior in HA and observer NameNode environments. It covers active/standby failover configuration, optional standby `getBlocks` access, observer read routing, observer failure fallback, and storage report equality between active and standby.

## Important APIs, Types, and Functions
The file uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `MiniQJMHACluster`, `HATestUtil`, `ObserverReadProxyProvider`, `NameNodeConnector`, `DatanodeStorageReport`, `NameNodeAdapterMockitoUtil`, and `TestBalancer` utilities. `waitStoragesNoStale` is a shared helper that triggers block reports and waits until all storage infos are no longer stale.

## Control Flow
The main HA test starts a two-NameNode HA cluster, configures failover, activates NameNode 0, creates a failover-aware client, and calls `doTest`. `doTest` writes data to 30 percent usage, optionally waits for standby catch-up or storage freshness, starts an empty DataNode, runs `Balancer.run` with namespace IDs, and waits for balance. Standby-request testing disables `getBlocks` operation checks, captures `NameNodeConnector` logs, runs `doTest`, and asserts standby success log lines. Observer tests create a QJM HA observer cluster, spy each namesystem, optionally shut down one observer, configure observer-read DFS, run `doTest`, and verify only the expected observer received `getBlocks`. Storage-report testing builds HA, compares active and standby `getLiveDatanodeStorageReport` fields after enabling standby reads.

## State and Persistence Behavior
State includes HA cluster roles, edit tailing, storage stale flags, observer NameNode availability, log capture buffers, Mockito spy invocation counts, and NameNodeConnector instances that must be closed. Clusters are shut down in `finally`, including QJM HA clusters.

## Dependencies and Integration Points
Integration points include HDFS HA failover, observer read proxy routing, standby operation checks, NameNodeConnector standby optimization, block reports, datanode storage reports, and balancer namespace/block-pool handling.

## Risks and Test Signals
Risks include HA timing (`Thread.sleep(500)`, edit tailing, stale storage wait), log-message brittleness, observer failover retry settings, and unclosed connectors. Signals include successful balance, standby log lines for `getBlocks` and storage reports, Mockito verification of observer-only `getBlocks`, and field-by-field active/standby storage report equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithHANameNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithMultipleNameNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithMultipleNameNodes.java

## Purpose
`TestBalancerWithMultipleNameNodes` verifies balancer behavior in federated HDFS clusters with multiple NameNodes and block pools. It tests both datanode-level balancing and block-pool-specific balancing, including balancing only selected block pools while preserving usage in unselected pools.

## Important APIs, Types, and Functions
The file uses `MiniDFSNNTopology.simpleFederatedTopology`, `MiniDFSCluster`, `DFSTestUtil.setFederatedConfiguration`, `Balancer.run`, `BalancerParameters`, `BalancingPolicy.Pool`, `DatanodeStorageReport`, and `StorageReport`. The `Suite` helper bundles configuration, cluster, per-NameNode `ClientProtocol` instances, replication, and balancer parameters. Core helpers are `createFile`, `generateBlocks`, `wait`, `runBalancer`, `compareTotalPoolUsage`, `getStorageReports`, `unevenDistribution`, and `runTest`.

## Control Flow
`runTest` creates a federated cluster, writes files into each namespace, starts empty DataNodes, and runs the balancer over all or selected block pools. `unevenDistribution` first creates blocks in a formatted cluster, shuts it down, restarts without formatting with capacity scaled by number of NameNodes, injects custom block distributions into each block pool, builds `BalancerParameters` for selected pools, and runs the balancer. `runBalancer` captures pre-run storage reports for unselected pools, runs `Balancer.run`, polls all NameNode clients until datanode utilization or pool utilization is within threshold, then compares total pool usage before and after for pools that should not have been touched.

## State and Persistence Behavior
State includes multiple block pools, per-NameNode file/block metadata, injected block reports, federated configuration, and datanode storage usage across pools. Clusters are explicitly shut down after each generated or test cluster. The tests depend on block pool IDs from namesystems to build selected pool sets.

## Dependencies and Integration Points
Integration points include federation configuration, NameNode RPC URI discovery, block-pool storage reports, balancer block-pool filtering, `BalancingPolicy.Pool`, and shared `TestBalancer` block distribution utilities.

## Risks and Test Signals
Risks include long waits without explicit timeout in `wait`, assumptions about client/name system ordering, block-pool ID selection by index, and high runtime for 600-second tests. Signals include balancer `SUCCESS`, all clients reporting consistent datanode used/capacity values, threshold-based balance checks, and unchanged total pool usage for unselected block pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithMultipleNameNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithNodeGroup.java

## Purpose
`TestBalancerWithNodeGroup` verifies that the balancer respects node-group-aware topology and block placement. It tests rack locality, node-group locality, no-move convergence when placement prevents movement, and configuration validation for `BlockPlacementPolicyWithNodeGroup`.

## Important APIs, Types, and Functions
The file uses `MiniDFSClusterWithNodeGroup`, `NetworkTopologyWithNodeGroup`, `BlockPlacementPolicyWithNodeGroup`, `BlockPlacementPolicy`, `BlockPlacementStatus`, `Balancer.run`, `ExitStatus`, and `LambdaTestUtils.intercept`. Helpers include `createConf`, `waitForHeartBeat`, `waitForBalancer`, `runBalancer`, `runBalancerCanFinish`, `getBlocksOnRack`, `verifyNetworkTopology`, and `verifyProperBlockPlacement`.

## Control Flow
`createConf` starts from `TestBalancer.initConf`, disables DFS network topology auto-use, sets the network topology implementation to node-group topology, and selects the node-group placement policy. Rack-locality and node-group tests build clusters with explicit racks and node groups, write a file to selected utilization, add a DataNode in a target rack/node group, run the balancer, and verify block placement after movement. The no-move test creates a topology where replicas cannot legally move without violating node-group policy and expects `NO_MOVE_PROGRESS`. `testBPPNodeGroup` intentionally enables DFS network topology while configuring node-group placement and expects cluster construction to fail with a specific `IllegalArgumentException`.

## State and Persistence Behavior
State includes static node-group assignments on `MiniDFSClusterWithNodeGroup`, MiniDFSCluster block placement metadata, datanode reports, and network topology objects. Each test shuts down the cluster in `finally`.

## Dependencies and Integration Points
Integration points are HDFS topology resolution, node-group placement policy, balancer candidate selection, NameNode block placement verification, and shared `TestBalancer` utilities for file creation and summed capacities.

## Risks and Test Signals
Risks include static node-group configuration leakage, timing in heartbeat/balance polling, and exact exception-message dependency. Signals include topology instance checks, rack block-set preservation, `SUCCESS` or `NO_MOVE_PROGRESS` exit statuses, and per-block `BlockPlacementStatus.isPlacementPolicySatisfied`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithSaslDataTransfer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithSaslDataTransfer.java

## Purpose
This wrapper verifies that the baseline balancer scenario works under SASL data-transfer protection modes: authentication, integrity, and privacy.

## Important APIs, Types, and Functions
The class extends `SaslDataTransferTestCase`, uses `createSecureConfig`, and delegates to a shared static `TestBalancer` instance through `testBalancer0Internal`.

## Control Flow
Each test creates a secure HDFS configuration for one SASL protection level and invokes the standard `TestBalancer` one-node/two-node balancing scenario. The delegated scenario initializes balancer defaults, builds MiniDFSClusters, creates files, starts empty nodes, runs balancer, and checks utilization.

## State and Persistence Behavior
The class itself has no cluster fields; state is delegated to the shared `TEST_BALANCER`. Because the instance is static, cleanup relies on the delegated test's internal `finally` and `@AfterEach` behavior when invoked through this wrapper is not automatic. The underlying methods do use cluster shutdown paths.

## Dependencies and Integration Points
Integration points include HDFS SASL data transfer setup, block access token/security settings from `SaslDataTransferTestCase`, and balancer block movement over secured transfer channels.

## Risks and Test Signals
Risks include shared static `TestBalancer` state, security configuration leakage, and inherited timing from balancer cluster tests. Signals are delegated balancer success and utilization convergence for all three SASL quality-of-protection modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithSaslDataTransfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestDispatcherEncryptionKey.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestDispatcherEncryptionKey.java

## Purpose
`TestDispatcherEncryptionKey` verifies dispatcher retry handling after `InvalidEncryptionKeyException`. The expected behavior is to update block keys and clear the cached data encryption key only on the first retry.

## Important APIs, Types, and Functions
The file tests private `Dispatcher.prepareRetryAfterInvalidEncryptionKey` through reflection. It defines `CountingKeyManager`, a `KeyManager` subclass that counts `updateBlockKeys` and `clearDataEncryptionKey` calls. It also builds a dynamic `NamenodeProtocol` proxy returning `ExportedBlockKeys.DUMMY_KEYS` for `getBlockKeys`.

## Control Flow
`testClearEncryptionKeyOnRetry` creates a `CountingKeyManager`, invokes the private dispatcher method with retry count 1, expects `true`, and asserts both counters incremented once. It invokes the method with retry count 2, expects `false`, and asserts counters remain unchanged. `prepareRetryAfterInvalidEncryptionKey` performs reflective lookup and invocation of the private dispatcher method.

## State and Persistence Behavior
State is in-memory only: counter fields on `CountingKeyManager` and a lightweight proxy NamenodeProtocol. No cluster or filesystem state is created.

## Dependencies and Integration Points
Integration points include dispatcher encryption-key retry policy, `KeyManager` block-key refresh and data-encryption-key cache clearing, and NamenodeProtocol block-key retrieval. Reflection makes this a direct unit test of private retry logic rather than a full data-transfer integration test.

## Risks and Test Signals
Risks include brittleness if the private method name/signature changes and limited coverage of actual `InvalidEncryptionKeyException` propagation. Signals are exact boolean return values and counter assertions proving first retry refreshes/clears once while later retry does not repeat the action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestDispatcherEncryptionKey.java -->
