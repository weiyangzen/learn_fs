# Research Report: subset-b-008083

This grouped report covers the subset-b-008083 Apache Ozone integration-test files. Each section is delimited for deterministic reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOMSnapshotDAG.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOMSnapshotDAG.java

## Purpose
`TestOMSnapshotDAG` is an integration test for OM snapshot diff DAG reconstruction and for the guard that skips RocksDB compaction tracking when no snapshots exist. It runs against a real `MiniOzoneCluster` and exercises Freon key generation, object-store snapshot creation, OM metadata lookup, snapshot-local SST metadata, RocksDB checkpoint differ APIs, and persistence across OM restart.

## Important APIs, Types, and Functions
- `init()` builds a three-datanode `MiniOzoneCluster`, lowers Ratis timeouts, enables filesystem snapshots, disables snapshot defrag service scheduling, and shrinks the RocksDB CF write buffer to force flush/compaction with relatively few keys.
- `getSnapshotDBKey(...)` builds the snapshot table key as `/volume/bucket/snapshot`.
- `getDifferSnapshotInfo(...)` reads `SnapshotInfo`, opens `OmSnapshotLocalDataManager` state, extracts version-to-SST-file maps, and wraps them in `DifferSnapshotVersion` for `RocksDBCheckpointDiffer`.
- `testDAGReconstruction()` creates keys through `RandomKeyGenerator`, takes snapshots `snap1`, `snap2`, and `snap3`, obtains SST diff lists for `snap2-snap1`, `snap3-snap2`, `snap3-snap1`, and `snap2-snap2`, restarts OM, and asserts the diff lists are reproduced.
- `testSkipTrackingWithZeroSnapshot()` generates enough keys to force compaction without creating snapshots, then asserts compaction log files are empty and SST backup directory has no files.

## Control Flow
The DAG test first creates initial keys and discovers the generated non-S3 volume and bucket via OM list APIs. After `snap1`, it writes 2000 zero-byte keys directly through `OzoneBucket`, creates `snap2`, pulls `OMMetadataManager`, `OmSnapshotLocalDataManager`, `RDBStore`, and `RocksDBCheckpointDiffer`, then asks the differ for pairwise SST deltas. It deletes 1000 keys, creates `snap3`, checks same-snapshot diff emptiness, closes active snapshot suppliers, restarts OM, reacquires metadata/snapshot handles, and repeats the same diff queries to prove the reconstructed DAG matches the in-memory pre-restart DAG.

## State and Persistence Behavior
The test depends on `SnapshotInfo` rows, checkpoint paths under OM metadata, snapshot-local DB transaction sequence numbers, per-version SST file metadata, compaction logs under `OM_SNAPSHOT_DIFF_DIR/DB_COMPACTION_LOG_DIR`, and SST backup files under `DB_COMPACTION_SST_BACKUP_DIR`. The restart portion verifies that DAG-related state is persisted and can be reconstructed after OM process restart, not just retained in memory.

## Dependencies and Integration Points
The file integrates Freon `RandomKeyGenerator`, Picocli command execution, Ozone client volume/bucket APIs, OM metadata tables, `OmSnapshotManager`, `OmSnapshotLocalDataManager`, `RDBStore`, and `RocksDBCheckpointDiffer`. It also depends on Ratis configuration and RocksDB compaction behavior, with logging levels adjusted for Ratis classes.

## Risks and Test Signals
Important risks are timing sensitivity around RocksDB flush/compaction, leaked active snapshot suppliers, and diff instability if SST metadata collection changes. Strong test signals are equality of diff lists before and after OM restart, empty diff for the same snapshot, successful Freon validation counts, and explicit filesystem checks showing no compaction tracking artifacts when snapshots are absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOMSnapshotDAG.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteFileOps.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteFileOps.java

## Purpose
This abstract non-HA integration test validates the Freon `obrwf` command, which performs mixed read/write file operations through the Hadoop `FileSystem` interface against an Ozone bucket path. It checks that the command creates the expected read and write path structures and that OM lock metrics remain healthy.

## Important APIs, Types, and Functions
- `parameters()` builds six `OmBucketTestUtils.ParameterBuilder` scenarios covering default read/write mix, nested prefixes, root prefix, small objects, pure reads, and pure writes.
- `testOmBucketReadWriteFileOps(...)` creates a volume/bucket, constructs an `o3fs://bucket.volume/prefix` root, runs `new Freon().getCmd().execute("obrwf", ...)`, and validates the resulting filesystem entries.
- `verifyFileCreation(...)` counts either directories or files in a `FileStatus[]`.
- `verifyOMLockMetrics(...)` is called on OM metadata lock metrics after Freon execution.

## Control Flow
For each parameter set, the test creates the target bucket, passes OM address and Freon command-line options for counts, data size, buffer size, length, total threads, read-thread percentage, read operations, write operations, and one run. It then opens a Hadoop `FileSystem` for the O3FS URI, lists the root, `readPath`, and `writePath`, and compares directory/file counts against the builder's expected values.

## State and Persistence Behavior
The command creates actual keys/files in Ozone and materializes namespace entries visible through the Hadoop filesystem adapter. The test relies on OM metadata state being updated consistently enough for `listStatus` calls to observe `readPath` and `writePath` contents immediately after command completion.

## Dependencies and Integration Points
Dependencies include `NonHATests.TestCase` for cluster provisioning, Ozone client creation, `TestDataUtil.createVolumeAndBucket`, Freon command dispatch, `OZONE_OM_ADDRESS_KEY`, Hadoop `FileSystem`, O3FS URI handling, and OM lock metrics.

## Risks and Test Signals
Risks include command-line option drift, expected write-count semantics changing for pure read/write cases, and path normalization differences for root and trailing-slash prefixes. The main signals are exact counts in root/read/write directories and successful OM lock metric verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteFileOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteKeyOps.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteKeyOps.java

## Purpose
This abstract non-HA integration test validates Freon's `obrwk` command for direct Ozone key operations. It covers mixed read/write, pure read, pure write, varying key lengths, zero-byte objects, buffer size, and thread-mix behavior in an `OBJECT_STORE` bucket.

## Important APIs, Types, and Functions
- `setup()` and `cleanup()` manage one `OzoneClient` per test method.
- `parameters()` returns six `ParameterBuilder` cases for command-line coverage.
- `testOmBucketReadWriteKeyOps(...)` creates an object-store bucket, runs `new Freon().getCmd().execute("obrwk", ...)`, measures elapsed monotonic time, validates key counts, and checks lock metrics.
- `verifyKeyCreation(...)` lists keys under `/readPath/` or `/writePath/` and asserts exact counts.

## Control Flow
The test creates a volume and bucket with `BucketLayout.OBJECT_STORE`, executes Freon with OM address, volume, bucket, read key count, write key count, data size, buffer, key length, thread count, read percentage, read/write operation counts, and run count. After the command returns, it iterates keys under read and write prefixes and compares counts with expected values.

## State and Persistence Behavior
The command persists OM key-table entries under stable `/readPath/` and `/writePath/` prefixes. The test does not inspect block data content; it uses key namespace visibility and Freon counters as the state signal.

## Dependencies and Integration Points
The file integrates `NonHATests.TestCase`, `TestDataUtil`, `OzoneBucket.listKeys`, Picocli-backed Freon command dispatch, OM config address injection, `BucketLayout.OBJECT_STORE`, and `OmBucketTestUtils.verifyOMLockMetrics`.

## Risks and Test Signals
Risks include prefix normalization with leading slashes, concurrency-sensitive key counts, and expected-write-count logic in `ParameterBuilder`. Signals are exact read/write prefix counts and clean OM lock metrics after threaded command execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOmBucketReadWriteKeyOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestRandomKeyGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestRandomKeyGenerator.java

## Purpose
`TestRandomKeyGenerator` verifies Freon's random key generator and the base Freon execution framework against a MiniOzoneCluster supplied by `NonHATests`. It covers failure accounting, default replication, EC replication, multithreading, large key sizes, zero-byte keys, cleanup behavior, and bucket layout selection.

## Important APIs, Types, and Functions
- `singleFailedAttempt()` uses `BaseFreonGenerator` directly and asserts a single runtime failure is counted.
- `testDefaultReplication()`, `testECKey()`, `testMultiThread()`, `testKeyLargerThan2GB()`, `testZeroSizeKey()`, and `testThreadPoolSize()` execute `RandomKeyGenerator` through Picocli and assert generator counters.
- `cleanObjectsTest()` validates `--clean-objects` counters for cleaned volumes and buckets.
- `testBucketLayoutOption()` asserts `--bucket-layout OBJECT_STORE` affects the created bucket and bucket map.

## Control Flow
Each command constructs a fresh `RandomKeyGenerator` using the cluster config, executes Picocli options, then reads generator counters such as number of volumes, buckets, keys added, validations attempted, successful validations, thread-pool size, cleanup counters, and bucket map size. The failure test initializes `BaseFreonGenerator`, waits until the subject reports completion inside the failing lambda, and asserts `runTests` propagates an exception while recording one failure.

## State and Persistence Behavior
The generator creates real Ozone volumes, buckets, and keys. Validation cases read back created keys and update validation counters. Cleanup cases remove created object hierarchy and record cleaned volume/bucket counts. Bucket-layout state is persisted in OM bucket metadata and observable through `OzoneBucket.getBucketLayout()`.

## Dependencies and Integration Points
The file depends on Picocli `CommandLine`, Freon `RandomKeyGenerator` and `BaseFreonGenerator`, Ozone client bucket APIs, `BucketLayout`, and the MiniOzoneCluster fixture provided by `NonHATests`.

## Risks and Test Signals
Risks include large-key behavior depending on sparse/write implementation rather than full local memory, EC replication support in the test cluster, and timing in `singleFailedAttempt`. Signals include exact generator counters, validation success/failure counts, cleanup counters, and persisted bucket layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestRandomKeyGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/package-info.java

## Purpose
This package descriptor documents the `org.apache.hadoop.ozone.freon` integration-test package as containing classes related to Ozone tools tests. It carries the ASF license header and package-level Javadoc only.

## Important APIs, Types, and Functions
The only exported declaration is `package org.apache.hadoop.ozone.freon;`. There are no methods, fields, or runtime types.

## Control Flow
There is no executable control flow. The file contributes package documentation to generated Javadocs and keeps package metadata aligned with Freon-related test classes.

## State and Persistence Behavior
No state is read or written.

## Dependencies and Integration Points
The descriptor integrates with Java package documentation tooling and the package namespace used by Freon tests.

## Risks and Test Signals
Risk is limited to stale package documentation. The signal is successful compilation/Javadoc packaging of the package declaration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/fsck/TestContainerMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/fsck/TestContainerMapper.java

## Purpose
`TestContainerMapper` validates that the fsck `ContainerMapper` can parse an OM database and derive a container-to-key/block mapping after keys have been written into a stopped MiniOzoneCluster. It specifically uses object-store buckets because Recon's mapping did not support FSO buckets for the referenced TODO.

## Important APIs, Types, and Functions
- `init()` configures OM DB directory, 100 MB SCM containers, zero datanode free-space minimum, and an elevated pipeline owner container count, then writes twenty 10 MB keys.
- `testContainerMapper()` creates `ContainerMapper`, calls `parseOmDB(conf)`, and asserts the returned map has three containers.
- `generateData(...)` creates a fixed byte array used for all keys.
- `shutdown()` closes the client and shuts down the cluster.

## Control Flow
The setup method starts a three-datanode cluster, creates a random volume and object-store bucket, writes twenty keys with standalone replication factor one, closes the output streams, and stops the cluster so the DB can be parsed offline. The test then parses the OM DB and validates the expected container count.

## State and Persistence Behavior
The test writes real OM key metadata and data blocks, then relies on the persisted OM RocksDB path configured by `OZONE_OM_DB_DIRS`. The parsed result is a nested `Map<Long, List<Map<Long, BlockIdDetails>>>`, keyed by container ID, containing block details for keys.

## Dependencies and Integration Points
Dependencies include `MiniOzoneCluster`, `OzoneClientFactory`, object-store bucket creation, SCM container sizing, datanode Ratis space configuration, `ContainerMapper`, and the `BlockIdDetails` model.

## Risks and Test Signals
Risks include assumptions about container closure and allocation count: twenty 10 MB keys into 100 MB containers are expected to occupy three containers because containers close before the threshold. The main signal is the exact parsed container map size after offline OM DB parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/fsck/TestContainerMapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/AbstractOzoneManagerHATest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/AbstractOzoneManagerHATest.java

## Purpose
`AbstractOzoneManagerHATest` is a shared base class for Ozone Manager HA integration tests. It centralizes HA cluster setup, client creation, retry tuning, follower-read toggles, key deleting-service configuration, and common helpers for volume, bucket, key, file, prefix, and failure/quorum assertions.

## Important APIs, Types, and Functions
- `initCluster(boolean followerReadEnabled)` configures ACLs, administrators, client retry limits, IPC retry intervals, Ratis purge/snapshot thresholds, filesystem snapshots, default bucket layout, optional follower reads/local leases, key deletion service settings, and a three-OM HA cluster.
- Accessors expose the cluster, object store, client, configuration, service ID, purge gap, snapshot threshold, retry cache duration, and OM count.
- `createKey(...)`, `createPrefixName()`, and `createPrefix(...)` create reusable OM objects.
- `setupBucket()` creates a volume/bucket and validates owner/admin metadata.
- `linkBucket(...)` creates a linked bucket pointing at a source bucket.
- `createVolumeTest(...)`, `createKeyTest(...)`, and `testCreateFile(...)` execute success/failure-oriented operations and validate results.
- `waitForLeaderToBeReady()` waits for OM leader election.

## Control Flow
Subclasses call `initCluster` before tests. The helper sets configuration, builds `MiniOzoneHAClusterImpl`, waits for readiness, creates a client with follower-read config if requested, and stores the object store. Operation helpers create objects through `ObjectStore` and `OzoneBucket` APIs, then read back metadata/content. Failure helpers catch `IOException`, distinguish `RemoteException`, `ConnectException`, and leader-discovery failures, and assert error text when quorum should be unavailable.

## State and Persistence Behavior
The base class creates persistent HA OM state through Ratis and OM RocksDB. It sets snapshot and log purge thresholds, retry cache duration, and key-deleting limits, so subclass tests inherit deterministic HA and background-service behavior. Created volumes, buckets, keys, linked buckets, and ACL prefixes are persisted in OM metadata.

## Dependencies and Integration Points
The class integrates MiniOzone HA cluster construction, Ozone RPC clients, `OzoneManagerRatisServerConfig`, `OmConfig`, ACL objects, Ozone bucket/key/file APIs, Ratis leader election, and Hadoop IPC retry settings.

## Risks and Test Signals
Risks include static shared state across subclasses, assumptions about exact exception messages, and follower-read configuration impacting client routing. Signals include validated volume/bucket attributes, readable key/file contents, correct `isFile` behavior during listing, and expected failure modes when quorum is absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/AbstractOzoneManagerHATest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OMUpgradeTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OMUpgradeTestUtils.java

## Purpose
`OMUpgradeTestUtils` provides small polling helpers for OM upgrade and prepare-state integration tests. It verifies that all OMs enter prepare at the expected transaction index and waits for upgrade finalization to complete.

## Important APIs, Types, and Functions
- `assertClusterPrepared(long preparedIndex, List<OzoneManager> ozoneManagers)` loops over OMs and uses `LambdaTestUtils.await` until each running OM reports `PREPARE_COMPLETED` at the expected index.
- `waitForFinalization(OzoneManagerProtocol omClient)` polls `queryUpgradeFinalizationProgress("finalize-test", false, false)` until status is `FINALIZATION_DONE`.

## Control Flow
The prepare helper skips progress until the OM is running, then checks prepare status. If an OM is prepared at the wrong index, it throws immediately to break out rather than waiting until timeout. The finalization helper catches `IOException`, fails the test with the message, and keeps polling otherwise.

## State and Persistence Behavior
The utilities inspect persisted/replicated OM prepare state and upgrade finalization state through live OM objects or protocol calls, but they do not mutate state themselves.

## Dependencies and Integration Points
Dependencies include `OzoneManagerPrepareState.State`, `OzoneManagerProtocol`, `UpgradeFinalization.StatusAndMessages`, `GenericTestUtils.waitFor`, and `LambdaTestUtils.await`.

## Risks and Test Signals
Risks are timeout sensitivity and hard-coded client ID `"finalize-test"`. Test signals are all OMs prepared at one exact index and finalization status reaching `FINALIZATION_DONE`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OMUpgradeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OmTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OmTestUtil.java

## Purpose
`OmTestUtil` exposes static utilities for inspecting OM RPC failover internals from an `ObjectStore`. It helps tests verify which OM proxy is active and access follower-read failover providers.

## Important APIs, Types, and Functions
- `getFailoverProxyProvider(ObjectStore store)` unwraps the object-store client proxy to `OzoneManagerProtocolClientSideTranslatorPB`, then to `Hadoop3OmTransport`, and returns the HA failover proxy provider.
- `getFollowerReadFailoverProxyProvider(ObjectStore store)` returns the follower-read failover proxy provider from the same transport.
- `getCurrentOmProxyNodeId(ObjectStore store)` returns the current proxy OM node ID.

## Control Flow
Each method performs downcasts through the client proxy transport stack and returns provider state. There is no retry or fallback logic; it assumes the store uses the Hadoop 3 OM transport.

## State and Persistence Behavior
No persistent state is modified. The methods inspect client-side routing state maintained by the failover provider.

## Dependencies and Integration Points
The utility integrates `ObjectStore`, `OzoneManagerProtocolClientSideTranslatorPB`, `Hadoop3OmTransport`, `HadoopRpcOMFailoverProxyProvider`, and `HadoopRpcOMFollowerReadFailoverProxyProvider`.

## Risks and Test Signals
The main risk is brittle downcasting if the client transport implementation changes. Its signals are direct access to current proxy node IDs and failover provider objects for HA/follower-read assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OmTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestAddRemoveOzoneManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestAddRemoveOzoneManager.java

## Purpose
`TestAddRemoveOzoneManager` exercises dynamic OM HA membership: bootstrapping voting OMs, bootstrapping listener OMs, forced bootstrap behavior, decommissioning, authorization, listener leadership safety, mixed voting/listener clusters, and listener removal.

## Important APIs, Types, and Functions
- `setupCluster(...)` creates an HA cluster, optionally enables test authorization, creates a volume/bucket/key, and records the leader's last applied transaction index.
- `getCurrentPeersFromRaftConf(...)`, `assertNewOMExistsInPeerList(...)`, and `assertNewOMExistsInListenerList(...)` validate OM peer/listener state and Ratis log catch-up.
- `testBootstrapOMs(...)` and `testBootstrapListenerOMs(...)` call `cluster.bootstrapOzoneManager(...)`.
- `decommissionOM(...)` updates `OZONE_OM_DECOMMISSIONED_NODES_KEY`, pushes config to active OMs, calls `OMAdminProtocolClientSideImpl.decommission`, waits for peer removal, and waits for leader election.
- Test methods cover normal bootstrap, missing config failures, force bootstrap, listener bootstrap/decommission, decommission authorization, listener non-leadership, mixed node types, and listener removal.

## Control Flow
The tests start from one-, two-, or three-OM clusters, add new OMs with different flags, and validate both high-level OM peer lists and underlying Ratis peer/listener configuration. Failure tests capture logs and assert expected exception messages/system-exit messages. Decommission tests modify configuration, create an admin protocol client under a selected `UserGroupInformation`, issue decommission, and then check live cluster operations still succeed.

## State and Persistence Behavior
The file mutates HA membership state, Ratis raft configuration, OM peer-node lists, decommissioned-node config, local Ratis log directories, and OM metadata state used to verify new nodes catch up. It also depends on user authorization state when test authorization is enabled.

## Dependencies and Integration Points
Major integrations are `MiniOzoneHAClusterImpl`, OM bootstrap APIs, `OzoneManagerRatisServer`, Ratis `RaftPeer` and listener configuration, `OMAdminProtocolClientSideImpl`, `UserGroupInformation`, `GenericTestUtils.waitFor`, log capture, and `TestOzoneManagerHA.createKey`.

## Risks and Test Signals
Risks include flaky timing around Ratis leader election and log replication, exact log-message assertions, and authorization context leakage. Signals include new node presence in peer/listener lists, Ratis logs on bootstrapped OMs, last-applied index catch-up, leader election by a new voting OM, listener nodes not becoming leaders, successful reads/writes after membership changes, and peer/listener removal after decommission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestAddRemoveOzoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucket.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucket.java

## Purpose
`TestBucket` is a test wrapper around `OzoneBucket` that simplifies creating buckets, writing keys with deterministic or random data, opening key input streams, and validating read buffers against written data.

## Important APIs, Types, and Functions
- `newBuilder(OzoneClient)` returns a builder that creates a volume and bucket if names are not supplied.
- `delegate()` exposes the wrapped `OzoneBucket`.
- `getKeyInputStream(...)` unwraps `readKey(...).getInputStream()` as `KeyInputStream`.
- `writeKey(...)` overloads write fixed-length string data or supplied bytes with `RatisReplicationConfig` defaulting to factor three.
- `writeRandomBytes(...)` writes random bytes through the same path.
- `validateData(...)` compares a read window to the expected slice of original input.

## Control Flow
The builder obtains the object store, creates a random volume if needed, creates a random bucket if needed, and wraps the resulting bucket. Write helpers generate data, delegate to `TestDataUtil.createKey`, and return the bytes for later validation.

## State and Persistence Behavior
The helper creates real Ozone volume, bucket, and key metadata/data. The wrapper itself holds only an `OzoneBucket` reference and does not manage cleanup.

## Dependencies and Integration Points
Dependencies include Ozone client/object-store APIs, `TestDataUtil`, `ContainerTestHelper`, Ratis replication config, `KeyInputStream`, and `ThreadLocalRandom`.

## Risks and Test Signals
Risks include implicit random names complicating diagnosis and default replication factor three requiring enough datanodes. Signals are successful key creation and byte-for-byte validation through `assertArrayEquals`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketLayoutWithOlderClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketLayoutWithOlderClient.java

## Purpose
This abstract non-HA integration test verifies bucket-layout behavior for older clients. It confirms modern client bucket creation follows explicit/default layout rules, while a manually constructed legacy-version `CreateBucket` request without bucket layout is interpreted as `LEGACY`.

## Important APIs, Types, and Functions
- `init()` stores the cluster reference and opens an Ozone client.
- `testCreateBucketWithOlderClient()` creates buckets through modern client helpers, constructs an `OMRequest` with `ClientVersion.DEFAULT_VERSION`, submits it directly through OM server protocol, and checks stored `OmBucketInfo`.
- `cleanup()` closes the client.

## Control Flow
The test reads the OM default bucket layout, creates a bucket without explicit layout and asserts the default, creates explicit FSO and OBS buckets and asserts those layouts, then builds a protobuf `CreateBucketRequest` that omits layout and uses an older client version. After setting `UserInfo`, it submits the request directly to `OzoneManager.getOmServerProtocol().submitRequest` and verifies the persisted bucket layout is `LEGACY`.

## State and Persistence Behavior
Bucket metadata in OM is the core state. The test toggles `OzoneManager.setTestSecureOmFlag(true)` before direct request submission, and the resulting bucket row must contain the legacy layout.

## Dependencies and Integration Points
Integrates `ClientVersion`, OM protobuf request/response types, secure OM test flag, `UserGroupInformation`, `TestDataUtil`, `BucketLayout`, and direct OM server protocol submission.

## Risks and Test Signals
Risks include coupling to protobuf request defaults and global secure-OM test flag state. Signals are response status `OK` and stored `OmBucketInfo.getBucketLayout()` equal to `LEGACY` for the older request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketLayoutWithOlderClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketOwner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketOwner.java

## Purpose
`TestBucketOwner` validates authorization semantics for bucket owners, volume owners, and unrelated users. It ensures bucket owners and volume owners can perform key and ACL operations while non-owners cannot.

## Important APIs, Types, and Functions
- `init()` creates three test users, creates a volume as admin, sets volume owner and world ACL, then logs in as user1 to create three buckets owned by user1.
- `testBucketOwner()` checks user1 can create/delete keys, delete a bucket, list keys, get ACLs, and add ACLs.
- `testNonBucketNonVolumeOwner()` checks user3 cannot create/delete/rename/list keys or get/add ACLs.
- `testVolumeOwner()` checks user2, the volume owner, can create/delete keys, list keys, manage ACLs, and delete a bucket.
- `createVolumeWithOwnerAndAcl(...)` and `setVolumeAcl(...)` set owner and ACL state through client protocol and object ACL APIs.

## Control Flow
The tests repeatedly set `UserGroupInformation` login user, create clients under that identity, and execute operations against the same volume/buckets. Positive cases simply execute operations, while negative cases wrap each operation in `assertThrows`.

## State and Persistence Behavior
Persistent state includes volume owner, bucket owner, world volume ACL, bucket metadata, keys, and ACL entries. The static login user is process-wide state and is deliberately changed between setup and tests.

## Dependencies and Integration Points
Dependencies include `AclTests.ADMIN_UGI`, `UserGroupInformation`, Ozone client APIs, `ClientProtocol.setVolumeOwner`, Ozone ACL parsing/building, `OzoneObjInfo`, and `TestDataUtil.createKey`.

## Risks and Test Signals
Risks include global login-user leakage and broad `assertThrows(Exception.class)` hiding exact authorization error types. Signals are positive operation completion for bucket/volume owners and exceptions for a non-owner/non-volume-owner.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestBucketOwner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java

## Purpose
`TestKeyManagerImpl` is a broad integration/unit hybrid for `KeyManagerImpl`. It starts real SCM/OM test managers but also uses mocked SCM block/container clients to cover key opening, block allocation, directory/file semantics, ACL checks, prefix ACLs, lookup and pipeline refresh, list-status behavior with DB/cache interactions, fake directories, multipart part selection, and previous-snapshot key/dir resolution.

## Important APIs, Types, and Functions
- `setUp()` initializes metadata directories, topology-aware read config, SCM with a mock node manager and network topology, `OmTestManagers`, `KeyManagerImpl`, `PrefixManager`, write/rpc clients, and mock SCM clients. It also configures safe-mode block allocation failures and creates the base volume.
- `init()` and `cleanupTest()` create buckets before each test and remove them via OFS `FileSystem` paths afterward.
- SCM switching helpers `mockContainerClient()` and `mockBlockClient()` replace internal `scmClient` fields on `keyManager` and `om`.
- Directory/file tests cover `createDirectory`, create-file overwrite/recursive rules, file under nonexistent parent, directory under file, root directory behavior, lookup file, and `getFileStatus`.
- ACL tests cover file, directory, nonexistent key access, prefix ACL add/set/remove/get, invalid prefix validation, and longest-prefix lookup.
- Listing tests exercise table cache merging, recursive and non-recursive status, deleted cache entries, pagination, filesystem-path config toggles, and fake directory discovery.
- Pipeline and version tests cover topology-aware closest-node sorting, latest-only versus all-version location behavior, refresh batching by container ID, and exception mapping to `SCM_GET_PIPELINE_EXCEPTION`.
- Multipart tests select all parts with part number zero, a specific part, or no locations for a missing part.
- Previous-snapshot tests verify object-ID based rename-table lookup for keys across all bucket layouts and FSO directory info.

## Control Flow
The setup path constructs a realistic OM/SCM environment and then mutates internals to simulate SCM failures or container-pipeline lookups. Many tests create `OmKeyArgs`, call write-client methods (`openKey`, `createFile`, `commitKey`, `createDirectory`, ACL APIs), and assert `KeyManagerImpl` read-side behavior. Metadata-heavy tests insert entries directly through `OMRequestTestUtils` into DB tables or table cache, then call `listStatus` and validate counts, sorting, deleted-entry filtering, pagination, and directory/file classification.

## State and Persistence Behavior
The file exercises multiple state layers: OM volume/bucket/key/open-key tables, key table cache entries including delete markers, prefix ACL metadata, directory marker/fake directory semantics, versioned bucket key-location versions, snapshot renamed table mappings, SCM container-to-pipeline metadata, Ratis/standalone replication configs, and filesystem-path configuration flags. Cleanup deletes per-test buckets but static managers persist across tests.

## Dependencies and Integration Points
Major integrations include `OmTestManagers`, `StorageContainerManager`, `ScmClient`, SCM block/container protocols, Hadoop `FileSystem`, `OMRequestTestUtils`, `PrefixManager`, `OzoneManagerProtocol`, Ozone ACL/request context types, `InMemoryTestTable`, Mockito, network topology classes, pipeline manager, and bucket layout-specific metadata key builders.

## Risks and Test Signals
Risks include static cross-test state, direct internal field mutation through whitebox utilities, cache delete-marker cleanup requirements, assumptions about network topology node ordering, and config toggles not restored per test. Strong signals include exact OM exception result codes, block count for multi-block opens, created parent directory rows, access checks avoiding SCM pipeline calls, ACL merge/remove behavior, longest-prefix result positions, latest-version location counts, list-status counts and pagination sets, fake-directory positives/negatives across buckets, SCM refresh call counts, exception result mapping, multipart part filtering, and previous-snapshot lookup results through rename tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyPurging.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyPurging.java

## Purpose
`TestKeyPurging` verifies that OM's `KeyDeletingService` processes deleted keys and purges pending-deletion metadata. It uses a live MiniOzoneCluster with short heartbeat, container-report, and block-deleting intervals.

## Important APIs, Types, and Functions
- `setup()` configures fast background service intervals, starts a three-datanode cluster, opens an RPC client, and records the `OzoneManager`.
- `testKeysPurgingByKeyDeletingService()` creates a volume/bucket, writes ten 100-byte keys, deletes them, waits for `KeyDeletingService` progress, and checks pending-deletion keys are empty.
- `shutdown()` closes the client and cluster.

## Control Flow
The test writes fixed data to ten keys through `TestDataUtil.createKey`, deletes each key, obtains `KeyManager.getDeletingService()`, waits until deleted-key count reaches ten, asserts the service has run more than once, then repeatedly calls `getPendingDeletionKeys(...).getPurgedKeys()` until it is empty.

## State and Persistence Behavior
The test relies on deleted-key metadata being created when keys are deleted and then purged by the background deleting service after SCM/container reports advance. It observes service counters and pending-deletion query results.

## Dependencies and Integration Points
Dependencies include MiniOzoneCluster, Ozone client APIs, `KeyManager`, `KeyDeletingService`, block-deleting interval config, heartbeat/container report config, `GenericTestUtils.waitFor`, and `ContainerTestHelper` data generation.

## Risks and Test Signals
Risks include timing sensitivity in background services and cluster reports. Signals are deleted-key count reaching `NUM_KEYS`, service run count greater than one, and no pending purged keys returned by the key manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestKeyPurging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeys.java

## Purpose
`TestListKeys` validates `OzoneBucket.listKeys(keyPrefix, startKey, shallow)` behavior for legacy and object-store bucket layouts. It stresses trailing-slash and non-trailing-slash prefixes, start-key ordering, shallow directory projection, replication metadata, and pagination-related batch settings.

## Important APIs, Types, and Functions
- `init()` enables filesystem path behavior, temporarily lowers OM max list size, configures client list/cache batch sizes, creates LEGACY and OBJECT_STORE buckets, and builds identical namespace trees.
- `buildNameSpaceTree(...)` creates a nested key tree and an explicit directory `a1/b4/`.
- Parameter sources define expected shallow-list outputs for trailing-slash and non-trailing-slash cases, with OBS-specific expectations where prefix directory entries differ.
- `checkKeyShallowList(...)` calls `bucket.listKeys(prefix, startKey, true)`, validates replication config on each `OzoneKey`, collects names, and asserts exact order/content.

## Control Flow
Setup creates both bucket layouts and writes the same tree. Parameterized tests feed prefix/start-key/expected-list tuples. The checker iterates the returned keys and compares to expected linked lists, printing diagnostics around each case.

## State and Persistence Behavior
The namespace consists of persisted keys and directory markers in two bucket layouts. The test temporarily mutates OM config (`fileSystemPathEnabled`, `maxListSize`) and restores it after all tests. Client-side list cache and server-side batch sizes are reduced to make list iteration cross batch boundaries.

## Dependencies and Integration Points
Dependencies include `NonHATests`, Ozone client factory, bucket layouts, `TestDataUtil.createStringKey`, Hadoop IO utilities, OM config, Ozone list cache/batch config, and replication config defaults.

## Risks and Test Signals
Risks include subtle layout-specific directory marker behavior and start-key inclusivity rules. Signals are exact ordered key-name lists for each case and replication config equality for every returned key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeysWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeysWithFSO.java

## Purpose
`TestListKeysWithFSO` validates FSO bucket `listKeys` behavior by comparing FSO output to legacy bucket output for equivalent namespaces. It covers valid and nonexistent start keys, trailing slash normalization, mixed directory/file trees, shallow listing, empty buckets, and `OzoneKey.isFile` classification.

## Important APIs, Types, and Functions
- `init()` enables filesystem path behavior, lowers max list size, configures list batch/cache sizes, creates legacy and FSO buckets in the same volume, plus empty comparison buckets.
- `buildNameSpaceTree(...)` and `buildNameSpaceTree2(...)` create two test namespaces with nested keys, flat keys, and file names that resemble directories.
- `getExpectedKeyList(...)` and `getExpectedKeyShallowList(...)` compute expected results from legacy buckets.
- `checkKeyList(...)` and `checkKeyShallowList(...)` iterate FSO results, validate replication config, collect names, and compare with expected legacy output.
- `testIsFileFalseForDir()` validates FSO listing returns a directory key with `isFile=false` followed by the real file with `isFile=true`.

## Control Flow
The main tests derive expected lists from legacy buckets for many prefix/start-key combinations, then assert the FSO bucket matches. Cases include start keys before/after prefixes, file versus directory start keys, nonexistent leaf/parent paths, empty prefix, partial prefix, mixed directories/files, shallow listing with null start key, and empty buckets.

## State and Persistence Behavior
The file creates persistent legacy and FSO bucket namespaces and temporarily mutates OM path/list-size configuration. FSO state is object-ID/path-table based internally, but the public observable state must match legacy `listKeys` names for these scenarios.

## Dependencies and Integration Points
Dependencies include FSO and legacy bucket layouts, Ozone client factory, `BucketArgs`, `StorageType`, `TestDataUtil`, Ozone list cache/batch config, replication config defaults, and Hadoop IO utilities.

## Risks and Test Signals
Risks include using legacy behavior as the oracle, path normalization differences for leading slashes, and batch-size effects. Signals are exact name-list equality with legacy output, replication config equality, and explicit `isFile` checks for directory and file entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListKeysWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListStatus.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListStatus.java

## Purpose
`TestListStatus` asserts sorted `OzoneFileStatus` output for FSO bucket `listStatus` across full prefixes, partial prefixes, start-key cases, and bounded result sizes.

## Important APIs, Types, and Functions
- `init()` creates an FSO bucket with `OZONE_FS_ITERATE_BATCH_SIZE` set to five and builds a namespace containing directories and files under `a*` and `b*`.
- `sortedListStatusParametersSource()` defines thirteen cases for prefix, start key, requested entry count, expected result size, partial-prefix flag, and description.
- `testSortedListStatus(...)` calls `checkKeyList(...)`.
- `checkKeyList(...)` calls `fsoOzoneBucket.listStatus(prefix, false, startKey, numEntries, isPartialPrefix)`, asserts expected size, and checks strict ascending path order.

## Control Flow
Setup creates directories/files through `createDirectory` and `createFile`. Each parameterized test executes one `listStatus` call, validates count, then walks adjacent statuses and asserts each path compares less than the next.

## State and Persistence Behavior
The test persists FSO directory and file entries in OM metadata. It does not mutate global OM config except client-side iterate batch size for this client. The important observable state is sorted status order and result truncation.

## Dependencies and Integration Points
Dependencies include FSO bucket layout, `OzoneBucket.listStatus`, `OzoneFileStatus`, Ratis replication config, `TestDataUtil`, and Ozone iterate batch config.

## Risks and Test Signals
Risks include lexicographic ordering changes, partial-prefix semantics, and null start-key handling. Signals are exact result sizes and strictly increasing path comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestListStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBootstrap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBootstrap.java

## Purpose
`TestOMBootstrap` verifies that a stopped OM follower can bootstrap from an installed checkpoint after the leader has advanced, for both v1 and v2 OM DB checkpoint formats. It ensures metadata and snapshots are restored on the follower.

## Important APIs, Types, and Functions
- The class is parameterized over `useV2Checkpoint`.
- `init()` configures checkpoint format, small Ratis purge gap and segment sizes, snapshot auto-trigger threshold, log appender wait time, client RPC timeout, and a three-OM HA cluster with an object-store test bucket.
- `testBootstrapFollower()` stops a follower, writes keys and snapshots on the leader, restarts the follower, waits for catch-up, asserts checkpoint-install log messages and endpoint selection, verifies metadata tables, and checks snapshot contents.
- `assertLogCapture(...)` waits until captured logs contain a message.

## Control Flow
The test determines the leader via `OmTestUtil.getCurrentOmProxyNodeId`, selects a follower from leader peer nodes, stops it, writes 25 keys and snapshot `snap1`, writes five more keys and snapshot `snap2`, captures OM and snapshot-provider logs, restarts the follower, computes leader transaction term/index from metadata, waits until follower last-applied index reaches the leader snapshot index, and then validates logs, metadata rows, RPC server restart, and snapshot equivalence.

## State and Persistence Behavior
State under test includes OM Ratis log/snapshot state, DB checkpoints served over v1 or v2 HTTP endpoints, volume/bucket/key metadata, snapshot metadata, and follower OM local DB after checkpoint install. The follower must reload state and resume RPC service.

## Dependencies and Integration Points
Dependencies include MiniOzone HA cluster, OM Ratis snapshot helpers (`TestOMRatisSnapshots`), `OmRatisSnapshotProvider`, DB checkpoint endpoint constants, `TransactionInfo`, Ratis `TermIndex`, Ozone client/object store, and log capture utilities.

## Risks and Test Signals
Risks include timing around follower stop/restart, snapshot index comparison, and log-message coupling. Signals include captured `"Reloaded OM state"` and `"Install Checkpoint is finished"` messages, expected v1/v2 endpoint in snapshot-provider logs, follower metadata rows for all keys, follower RPC server running, and snapshot content checks matching leader state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBootstrap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBucketLayoutUpgrade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBucketLayoutUpgrade.java

## Purpose
`TestOMBucketLayoutUpgrade` validates bucket-layout feature gating across OM upgrade finalization. Before finalization, only legacy buckets are allowed; after finalization, all `BucketLayout` values may be created.

## Important APIs, Types, and Functions
- `setup()` starts a three-OM HA cluster initialized at `INITIAL_VERSION`, creates a client and OM protocol proxy, and creates a sample volume.
- Ordered tests are grouped by constants `PRE_UPGRADE`, `DURING_UPGRADE`, and `POST_UPGRADE`.
- `omLayoutBeforeUpgrade()` checks metadata layout version and absence of the persisted layout-version meta-table key.
- `blocksNewLayoutBeforeUpgrade(...)` expects `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION` for non-legacy layouts.
- `allowsLegacyBucketBeforeUpgrade()` and `allowsBucketCreationWithAnyLayoutAfterUpgrade(...)` assert bucket creation and stored layout.
- `finalizeUpgrade()` calls `finalizeUpgrade`, waits for finalization, and waits for `LAYOUT_VERSION_KEY` to equal `maxLayoutVersion()`.

## Control Flow
All test methods share one cluster, so method order matters. The pre-upgrade phase validates initial layout state and allowed/disallowed bucket creation. The during-upgrade phase finalizes the cluster. The post-upgrade phase iterates all enum layouts and verifies creation succeeds and `getBucketInfo` returns the requested layout.

## State and Persistence Behavior
The cluster starts with a testing initial layout version and later persists the finalized layout version in OM metadata. Bucket rows created before and after finalization preserve their requested layouts. The shared cluster means upgrade state intentionally carries across test methods.

## Dependencies and Integration Points
Dependencies include `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, OM layout-version manager, `OMUpgradeTestUtils.waitForFinalization`, Ozone upgrade finalization protocol, `OmBucketInfo`, `OmVolumeArgs`, and JUnit method ordering.

## Risks and Test Signals
Risks include order dependence, shared cluster state, and future enum additions changing pre-upgrade expectations. Signals are exact layout-version metadata checks, `OMException` result code before finalization, finalization reaching done, meta-table layout key matching max layout version, and bucket-info layout equality after creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMBucketLayoutUpgrade.java -->
