# subset-b-007542 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailure.java

Purpose: fine-grained HDFS DataNode volume-failure regression coverage. It uses `MiniDFSCluster` with two DataNodes, two volumes per DN, short block size, one tolerated failed volume, and explicit disk-check timing to validate block availability, DataNode survival, NameNode failure accounting, startup behavior, reconfiguration, and volume metrics.

Important APIs and types: `MiniDFSCluster`, `DataNode`, `DataNodeTestUtils`, `FsDatasetSpi`, `FsVolumeSpi`, `DataStorage`, `BlockPoolSliceStorage`, `VolumeFailureSummary`, `BlockReaderFactory`, `BlockManagerTestUtil`, `StorageLocation`, and an inner `BadDiskFSDataset` extending `SimulatedFSDataset`. Helper state includes `block_map` mapping block IDs to physical metadata files and NameNode block locations.

Control flow: setup creates a live cluster and filesystem. Tests mutate actual data directories by deleting block files, making finalized directories read-only, injecting data-dir failures, or restarting DataNodes. `testVolumeFailure` creates a replicated file, corrupts one DN volume, forces block access through `BlockReaderFactory`, waits for `VolumeFailureSummary`, triggers heartbeat processing, verifies NameNode counters, reconciles physical block counts against NameNode locations, and confirms later writes still replicate. Other tests check startup after add-block-pool exceptions, removal of failed volumes from `DataStorage`, shutdown when tolerated failures are exceeded, hot swap and re-add flows, refresh-volume deadlock avoidance, under-replication after failures, startup with non-writable directories, failure detection during restart, and `VolumeFailures` metrics.

State and persistence behavior: the tests exercise storage directories, block pool storage directories, replica maps, failed-storage-location summaries, DataNode configuration `dfs.datanode.data.dir`, NameNode aggregate counters, and persisted block files/meta files. Risks center on permission-sensitive tests skipped on Windows, asynchronous heartbeat/disk-check timing, real filesystem mutability, and failure-injection cleanup. Test signals are assertions on DataNode liveness, config contents, storage-dir counts, replica volume paths, NameNode volume-failure totals, low-redundancy counts, and metrics counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureReporting.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureReporting.java

Purpose: validates DataNode and NameNode reporting of failed volumes, lost capacity, failed storage locations, JMX attributes, and behavior across restart/reconfiguration. It is tagged slow and skips Windows because it relies on `DataNodeTestUtils.injectDataDirFailure`.

Important APIs and types: `MiniDFSCluster`, `DatanodeManager`, `DatanodeDescriptor`, `FSNamesystem`, `FsDatasetSpi`, `VolumeFailureSummary`, metrics helpers (`getMetrics`, `getLongCounter`), platform `MBeanServer`, and DataNode reconfiguration helpers. `initCluster` configures block size, heartbeat/recheck/DF intervals, tolerated failures, and storage count per DataNode, then computes per-volume capacity for assertions.

Control flow: `testSuccessiveVolumeFailures` scales to three DNs, injects failures one volume at a time, writes files to trigger disk checks, verifies DNs remain up while within tolerance, checks NameNode aggregate totals and per-DN summaries, then fails all volumes on one DN and waits for death. It restores directories, restarts, and confirms counters clear. Other tests verify NameNode re-learns failure stats after restart, multiple failures per node with four storage dirs, idempotent reporting during repeated reconfiguration, auto-format protections when `VERSION` is missing, block-pool `VERSION` handling, and hot-swapping a failed volume while watching JMX `NumFailedVolumes`.

State and persistence behavior: failure state flows from FsDataset failed-storage-location arrays to DataNode metrics, heartbeat `VolumeFailureSummary`, NameNode `DatanodeDescriptor`, `FSNamesystem` aggregate counters, and JMX. Capacity lost is zero when pre-failure capacity was unknown and `volumeCapacity * failures` otherwise. Risks include asynchronous detection, capacity assumptions, failed-volume path URI normalization, and reconfiguration edge cases. Test signals are live/dead DN counts, volume failure counts, lost capacity, failed path arrays, JMX attributes, and absence of double-counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureReporting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureToleration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureToleration.java

Purpose: tests DataNode tolerance policy for failed storage volumes during startup and runtime. It focuses on `dfs.datanode.failed.volumes.tolerated`, including invalid values, `-1` semantics, minimum viable volumes, and NameNode accounting for startup-time failures.

Important APIs and types: `MiniDFSCluster`, `DataNodeTestUtils`, `DatanodeManager`, `DFSTestUtil`, `HadoopIllegalArgumentException`, `StorageLocation` indirectly via MiniDFS storage dirs, and `FileUtil.chmod` for permission-driven failures.

Control flow: setup uses one DN, two storage dirs, one tolerated failure, and fast heartbeat/recheck intervals. `testValidVolumesAtStartup` shuts down DNs, creates one good and one permission-denied directory, starts a DN with manually managed dirs, and asserts only the good directory appears in storage info. `testConfigureMinValidVolumes` starts DNs with zero tolerance, injects a failure, proves the affected DN dies and remains unavailable even after directory restoration. `testVolumeAndTolerableConfiguration` drives a matrix through `testVolumeConfig`, preparing current dirs to fail, restarting with different tolerated values, and asserting BP service state or invalid-config exceptions. `testFailedVolumeOnStartupIsCounted` checks NameNode live status and failed-volume totals for a startup failure.

State and persistence behavior: tests mutate permissions under `current`, rely on `restartDatanodes` to rebuild DataNode state, and compare NameNode status against capacity changes. Integration points include DataNode startup validation, BP service liveness, cluster-managed versus manually managed dirs, and NameNode datanode status. Risks are platform permissions, timing, and cleanup chmod. Signals include `isBPServiceAlive`, storage-info contents, live/dead DN counts, and expected capacity after volume loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeFailureToleration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeMetrics.java

Purpose: validates per-volume file I/O profiling metrics for DataNode volumes. It uses one DataNode, two storage types (`RAM_DISK`, `DISK`), two storages per DN, and 100 percent sampling to make metric increments observable.

Important APIs and types: `DataNodeVolumeMetrics`, `FsVolumeSpi`, `MiniDFSCluster`, `SimulatedFSDataset`, `ExtendedBlock`, `DFSOutputStream`, `FSDataOutputStream`, metrics asserts, and DataNode volume departure/arrival utilities.

Control flow: `setupClusterForVolumeMetrics` enables `dfs.datanode.fileio.profiling.sampling.percentage`, installs `SimulatedFSDataset`, and builds a storage-typed cluster. `testVolumeMetrics` creates a file larger than `Integer.MAX_VALUE`, appends data, calls `hsync`, then resolves the first block to its volume and validates metric counters/tags. `testVolumeMetricsWithVolumeDepartureArrival` repeats the workload, injects a second-volume failure, validates metrics while a volume is failed, restores/reconfigures the volume, and validates again. `testWriteIoVolumeMetrics` checks sample-count relationships before and after append plus `hflush`.

State and persistence behavior: metric state lives on each `FsVolumeSpi` via `DataNodeVolumeMetrics`; cluster data is transient. Integration points include append, flush, sync, block-to-volume lookup, and volume reconfiguration. Risks include metric sampling configuration, simulated dataset behavior versus real disks, huge logical file lengths, and assumptions about count ordering. Test signals include `TotalDataFileIos`, `VolumeName`, nonzero write counts, zero sync before explicit sync, and monotonic write sample growth after append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataSetLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataSetLockManager.java

Purpose: unit-tests `DataSetLockManager` hierarchical read/write lock behavior and leak detection for block-pool, volume, and directory lock levels.

Important APIs and types: `DataSetLockManager`, `AutoCloseDataSetLock`, `DataNodeLockManager.LockLevel`, and `SubjectInheritingThread`. Assertions inspect `manager.getLastException()` after `lockLeakCheck`.

Control flow: setup creates a fresh manager. `testBaseFunc` registers locks for BP, volume, and dir, acquires and closes combinations of write/read locks at different levels, runs leak checks after each valid close sequence, then intentionally leaves a write lock open and expects `"lock Leak"`. `testAcquireWriteLockError` starts a subject-inheriting thread that takes a read lock and then attempts a write lock for the same block pool, waits briefly, and verifies leak detection catches the blocked/acquired state. `testLockLeakCheck` directly leaves a block-pool write lock open and asserts the same error.

State and persistence behavior: all state is in-memory lock-manager state: registered lock hierarchy, held locks, and last exception. Integration points are low-level concurrency primitives used by FsDataset code paths such as directory scanning and replica map updates. Risks include thread timing in `testAcquireWriteLockError`, reliance on exact exception message text, and no explicit closure for intentionally leaked locks. Test signals are null last exception for balanced close paths and `"lock Leak"` for held or blocked locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataSetLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataStorage.java

Purpose: tests `DataStorage` storage-directory initialization, block-pool slice setup, duplicate/invalid additions, missing `VERSION` protections, and failure behavior during recovery/transition.

Important APIs and types: `DataStorage`, `Storage.StorageDirectory`, `StorageLocation`, `NamespaceInfo`, `StartupOption`, mocked `DataNode`, `FileUtil`, and `GenericTestUtils`. Helpers create temporary storage locations as directories or regular files and build multiple namespace infos.

Control flow: setup creates a clean `dstest` directory, a `DataStorage`, a mocked DN returning `HdfsConfiguration`, and a default namespace. `testAddStorageDirectories` adds the same storage locations across multiple namespaces and verifies both DataNode storage roots and block-pool slices contain `current/VERSION`; duplicate active locations return no additions; adding a larger set updates active storage dir count. `testAddStorageDirectoriesFailure` shows a restarted DN with a different cluster ID rejects existing locations. `testMissingVersion` places a fake block-pool directory under uninitialized `current` and asserts storage add does not format it away. `testRecoverTransitionReadFailure` passes regular files as locations and expects all dirs fail. `testRecoverTransitionReadDoTransitionFailure` verifies transition exceptions leave no active dirs after reset.

State and persistence behavior: this file creates and deletes local storage tree artifacts, `VERSION` files, and block-pool directories. Integration points are DN startup and namespace transition storage contracts. Risks include filesystem cleanup, URI parsing, cluster ID mismatch semantics, and exact exception text. Signals are directory/file existence checks, returned added-location counts, storage-dir counts, and expected IOException messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferEncryptionKey.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferEncryptionKey.java

Purpose: small unit test for DataNode data-transfer retry behavior after `InvalidEncryptionKeyException`, specifically that the cached data encryption key is cleared only on the first retry.

Important APIs and types: private static `DataNode.prepareRetryAfterInvalidEncryptionKey`, accessed reflectively, `DataEncryptionKeyFactory`, `DataEncryptionKey`, and an inner `CountingKeyFactory` that records `clearDataEncryptionKey` calls.

Control flow: `testClearEncryptionKeyOnRetry` invokes the private method with retry count 1 and verifies it returns true and clears exactly once. It then invokes retry count 2 and verifies it returns false without additional clears. The helper uses `DataNode.class.getDeclaredMethod`, `setAccessible(true)`, and reflective invocation.

State and persistence behavior: all state is in the in-memory `clearCount` field of `CountingKeyFactory`; no cluster or filesystem is involved. Integration point is SASL/encrypted data transfer retry logic in DataNode. Risks include brittle reflection if the private method signature changes, method accessibility under stricter Java/module policies, and limited behavior coverage beyond retry counts 1 and 2. Test signals are boolean retry decisions and `clearCount`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferEncryptionKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferThrottler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferThrottler.java

Purpose: integration test for read-side DataNode transfer throttling controlled by `dfs.datanode.data.read.bandwidthPerSec`.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DataXceiverServer#getReadThrottler`, `DFSTestUtil`, `Path`, `HdfsConfiguration`, and `Time.monotonicNow`.

Control flow: the test starts a default cluster, writes an 80 MiB file, waits for replication, and asserts the DataNode read throttler is null under default bandwidth 0. It reads the file unthrottled, sets read bandwidth to 8 MiB/s, restarts the DataNode with the new conf, verifies the throttler bandwidth, then reads the full file again and asserts elapsed time is at least roughly 10 seconds with a 1 second margin.

State and persistence behavior: the test persists one HDFS file across DataNode restart; throttle state is in the restarted `DataXceiverServer`. Integration points include DataNode restart, DataXceiver read path, configuration propagation, and client read helpers. Risks include wall-clock timing variability, slow CI environments, cache effects, and the confusing comment naming acceptable error as "1 milliseconds" while the value is 1000 ms. Test signals are throttler null/non-null state, configured bandwidth, full byte-count reads, and elapsed-time lower bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferThrottler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverBackwardsCompat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverBackwardsCompat.java

Purpose: mock-based compatibility test proving `DataXceiver.writeBlock` can process Hadoop 2.x-style write-block calls that omit newer storage ID and target storage type data far enough to send downstream data.

Important APIs and types: `DataXceiver`, `DataXceiverServer`, `BlockReceiver`, `Peer`, `PeerServer`, `SaslDataTransferClient`, `FsDatasetSpi`, `ReplicaHandler`, `DatanodeInfo`, `ExtendedBlock`, `DataChecksum`, block tokens, and an inner `NullDataNode` subclass. `NullDataNode` installs mocked dataset/SASL fields and starts a one-shot local `NullServer`.

Control flow: `testBackwardsCompat` builds a mocked peer, a byte output stream, a local acceptor port, a `NullDataNode`, and a spied `DataXceiver`. It stubs `getBlockReceiver`, creates token/checksum/datanode-info mocks, and calls `writeBlock` with `new String[0]` storage IDs and null/empty optional arrays. Exceptions are tolerated after the call has progressed far enough; the test fails if no bytes are written to the downstream output because that means the compatibility path aborted too early.

State and persistence behavior: state is in mocked objects, a local socket, and a byte output buffer. Integration points are DataXceiver pipeline setup, SASL send, block receiver creation, and datatransfer protocol serialization. Risks include partial mocking brittleness, one-shot server timing, and reliance on "some bytes written" as the success boundary rather than full protocol completion. Test signals are non-empty downstream output and absence of early exception before serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverBackwardsCompat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverLazyPersistHint.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverLazyPersistHint.java

Purpose: unit-tests how `DataXceiver.writeBlock` passes the lazy-persist hint to `BlockReceiver` based on client locality and `dfs.datanode.allow.non.local.lazy.persist`.

Important APIs and types: `DataXceiver`, `BlockReceiver`, `Peer`, `DataNode`, `DNConf`, `DataNodeMetrics`, `DatanodeRegistration`, `ArgumentCaptor<Boolean>`, `StorageType.RAM_DISK`, `DataChecksum`, and enum helpers `PeerLocality` and `NonLocalLazyPersist`.

Control flow: `testWithLocalClient` creates a stub xceiver for a local peer and verifies both true and false lazy-persist inputs are captured unchanged. `testWithRemoteClient` uses a remote peer with non-local lazy persist disallowed and verifies the captured value is always false. `testOverrideWithRemoteClient` enables the config and verifies remote requests pass through unchanged. `issueWriteBlockCall` sends a dummy `writeBlock` call where the meaningful parameter is lazyPersist. `makeStubDataXceiver` spies on `DataXceiver.create`, stubs `getBlockReceiver` to capture the boolean, and stubs output stream creation.

State and persistence behavior: purely mocked, with configuration carried through `DNConf`. Integration points are DataXceiver local-peer detection, DataNode config, and block-receiver construction. Risks include fragile argument-position matching and incomplete coverage after receiver creation. Test signals are captured boolean values for local, remote denied, and remote allowed cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataXceiverLazyPersistHint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeProtocolRetryPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeProtocolRetryPolicy.java

Purpose: verifies DataNode protocol retry behavior when a NameNode asks a DataNode to re-register and `registerDatanode` transiently fails with `EOFException`.

Important APIs and types: `DataNode`, `DatanodeProtocolClientSideTranslatorPB`, `DatanodeRegistration`, `NamespaceInfo`, `HeartbeatResponse`, `RegisterCommand`, `NNHAStatusHeartbeat`, `StorageLocation`, `MiniDFSCluster` base directories, Mockito answers, and `GenericTestUtils.waitFor`.

Control flow: setup creates a standalone DataNode data directory, configures DN RPC/HTTP/IPC ports to random, sets default URI to a fake NN address, disables IPC client connect retries, and stores one `StorageLocation`. The test mocks the NameNode protocol: first registration succeeds, re-registration attempts 2 through 4 throw `EOFException`, later attempts succeed with a new registration; the first heartbeat returns `RegisterCommand.REGISTER`, later heartbeats return no commands. A custom `DataNode` overrides `connectToNN` to return the mock protocol. The test triggers a heartbeat and waits until a block report reaches the mock NN, proving retry and re-registration recovered.

State and persistence behavior: local data dir is created and deleted; DataNode BP service state and registration state are live in process. Integration points include BPOfferService heartbeat loop, protocol retry policy, NN HA status, and block report emission. Risks include async timing, fixed fake NN address comparisons, and static registration mutation. Test signals are mock invocation verification for `blockReport` after transient registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeProtocolRetryPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeRegister.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeRegister.java

Purpose: unit-tests DataNode registration and namespace-info validation for version compatibility, layout versions, shutdown-before-register behavior, and invalid configuration values.

Important APIs and types: `BPServiceActor`, `BPOfferService`, `DataNode`, `DNConf`, `NamespaceInfo`, `DatanodeProtocolClientSideTranslatorPB`, `VersionInfo`, `IncorrectVersionException`, `HadoopIllegalArgumentException`, `LambdaTestUtils.intercept`, and `Lists`.

Control flow: setup builds mocked DN config and BPOfferService, constructs a `BPServiceActor` against an invalid address, and wires a mocked NN protocol returning a fake `NamespaceInfo` with current software and layout versions. `testSoftwareVersionDifferences` accepts equal versions and NN versions above the DN minimum, then expects `IncorrectVersionException` when the NN version is below `getMinimumNameNodeVersion`. `testDifferentLayoutVersions` documents that differing layout versions no longer fail namespace retrieval. `testDNShutdwonBeforeRegister` creates a real DataNode with empty locations, initializes a BPOfferService/actor, stops the actor before registration, and expects `"DN shut down before block pool registered"`. `testInvalidConfigurationValue` verifies DataNode construction rejects tolerated failed volumes below -1.

State and persistence behavior: mostly mocked, with one short-lived DataNode config and BP service state. Integration points are namespace version negotiation, actor lifecycle, and DataNode config validation. Risks include exact exception messages and mixed mocked/real actor state. Signals are retrieved namespace values, expected exceptions, and invalid-config interception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeRegister.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeStartupOptions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeStartupOptions.java

Purpose: verifies DataNode command-line startup option parsing and storage of the parsed `StartupOption` in configuration.

Important APIs and types: `DataNode.parseArguments`, `DataNode.getStartupOption`, `HdfsConfiguration`, and `HdfsServerConstants.StartupOption`. AssertJ is used for boolean and enum equality.

Control flow: `initConfiguration` creates a fresh config before each test because parsing mutates configuration. `checkExpected` copies varargs into a String array, calls `DataNode.parseArguments`, obtains `DataNode.getStartupOption`, and checks parse success plus expected option when success is expected. `testStartupSuccess` covers no args, `-regular`, uppercase `-REGULAR`, and `-rollback`. `testStartupFailure` covers an unknown option and a single combined string `"-regular -rollback"` that should not parse as two valid options.

State and persistence behavior: only the in-memory configuration is mutated. Integration point is DataNode CLI parsing used before DN startup. Risks are limited: the failure case with a combined string tests one shell-tokenization shape, not all conflicting option arrays. Test signals are parse return values and `StartupOption` enum stored in config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeStartupOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDeleteBlockPool.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDeleteBlockPool.java

Purpose: integration-tests deleting a block pool from DataNode storage in a federated HDFS cluster, both through direct DataNode API and `DFSAdmin`.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology`, `DataNode.deleteBlockPool`, `DataNode.refreshNamenodes`, `DFSAdmin`, `FsDatasetTestUtils`, `DFSTestUtil`, and `DFSConfigKeys.DFS_NAMESERVICES`.

Control flow: `testDeleteBlockPool` starts two nameservices and two DNs, writes one file in each namespace, and obtains both block pool IDs. It verifies deletion fails while the block-pool offer service is still running, refreshes the DN to only the second nameservice, verifies non-forced deletion fails when blocks remain, then force-deletes and confirms missing storage. On the second DN it deletes the file, waits for replicas in the old block pool to disappear, shuts down the first NN, refreshes namenodes, and confirms non-forced deletion succeeds when no blocks remain. It verifies the second block pool still works by creating and replicating `/gamma`. `testDfsAdminDeleteBlockPool` repeats the scenario through CLI args, requiring `force` for a block pool not served by the active DN config.

State and persistence behavior: DataNode local block-pool directories are created and removed; BPOfferService membership changes with namenode refresh. Integration points are federation, admin CLI, dataset storage verification, and replication after deletion. Risks include polling for replica deletion, force semantics, and namespace config mutation. Signals are expected IOExceptions/return codes, offer-service counts, block-pool exists/missing checks, and successful unaffected namespace replication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDeleteBlockPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDirectoryScanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDirectoryScanner.java

Purpose: comprehensive regression suite for `DirectoryScanner`, which reconciles on-disk block files/meta files with FsDataset in-memory replicas across normal disks, RAM_DISK/lazy-persist storage, throttled scanning, federation, malformed local replica paths, and concurrent update/failure cases.

Important APIs and types: `DirectoryScanner`, `DirectoryScanner.Stats`, `DirectoryScanner.ReportCompiler`, `FsDatasetSpi`, `FsVolumeSpi.ScanInfo`, `ReplicaInfo`, `LocalReplica`, `DatanodeUtil`, `DataNodeFaultInjector`, `FsDatasetTestUtil`, `AutoCloseableLock`, `LockLevel`, `MiniDFSCluster`, `LazyPersistTestCase`, and `StorageType`. Helpers create, delete, truncate, and duplicate block/meta files under finalized dirs, then call `scanner.reconcile()` and verify retained diffs/stats.

Control flow: setup initializes cache manipulation. The main `runTest` creates 100 blocks and then exercises no-diff, missing meta, missing block, disk-only block, meta-only, block+meta-only, bulk deletes/additions, length mismatches, combined cases, and no-throttle timing for both one and two scan threads. Lazy-persist tests verify duplicates on transient storage are resolved by retaining persistent copies or deleting transient copies. Other tests cover invalid thread count defaulting, log warning suppression for meta-only scans, regular-block symlink mismatch bad-block reporting, concurrent scanner versus append metadata update avoiding false bad-block report, throttle ratios for multiple limits and shutdown during throttling, `ScanInfo` construction, exception handling while compiling volume reports, federated cluster per-BP stats, local replica path parsing and update correction, last finish time update, and null storage after volume removal between scan and update.

State and persistence behavior: tests directly mutate finalized block directories and metadata, maintain retained scanner diffs, update FsDataset replica map, and inspect per-block-pool scanner stats. Integration points include NameNode bad-block reporting, lazy writer, FsDataset locks, short-lived executor concurrency, federated block pools, throttling counters, and DataNode failure injection. Risks are high due to real filesystem mutation, async waits, timing-sensitive throttling, symlink/platform behavior, and exact log text checks. Test signals are `Stats` counters (`missingMetaFile`, `missingBlockFile`, `missingMemoryBlocks`, `mismatchBlocks`, `duplicateBlocks`), replica additions/deletions/generation stamps, storage type, NameNode logs, throttle time ratios, and last scanner finish timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDirectoryScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDiskError.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDiskError.java

Purpose: validates DataNode behavior for disk errors during shutdown, replication, local directory permissions, async disk checking, and corrupt metadata during block transfer.

Important APIs and types: `MiniDFSCluster`, `DataNodeTestUtils`, `FsDatasetSpi.FsVolumeReferences`, `Sender.writeBlock`, `NameNodeAdapter`, `BlockScanner`, `BlockTokenSecretManager.DUMMY_TOKEN`, `DataChecksum`, `RandomAccessFile`, and `DatanodeDescriptor`.

Control flow: setup creates one DN with 512-byte blocks and zero disk-check min gap. `testShutdown` injects failure into both storage dirs, calls `checkDiskError`, and waits for DN down. `testReplicationError` opens a raw socket to a second DN, sends a write-block header for an existing block, closes before content, waits for temporary replicas to disappear, then raises file replication and verifies later replication can proceed. `testLocalDirs` checks local FS permissions match `dfs.datanode.data.dir.perm`. `testcheckDiskError` records last disk-check timestamp, calls `checkDiskError`, and waits for an async update. `testDataTransferWhenBytesPerChecksumIsZero` corrupts a metadata header to zero checksum type/bytes, starts another DN, calls `transferBlock`, and verifies the mocked `BlockScanner` marks the suspect block.

State and persistence behavior: tests mutate local data dirs, temporary replica files, metadata headers, and DN block scanner state. Integration points include DataXceiver write-block protocol, replication cleanup, FsDataset volumes, NameNode block location lookup, and block scanner suspect marking. Risks include platform-dependent permissions, socket-level partial writes, sleeps for async transfer, and a suspicious DN identity comparison using `equals(datanodeId0)`. Signals are DN liveness, absence of temp replicas, successful replication, permission equality, timestamp growth, and `markSuspectBlock` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDiskError.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDnRespectsBlockReportSplitThreshold.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDnRespectsBlockReportSplitThreshold.java

Purpose: verifies DataNode block-report batching respects `dfs.blockreport.split.threshold`.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `InternalDataNodeTestUtils.spyOnBposToNN`, `DataNodeTestUtils.triggerBlockReport`, `DatanodeProtocolClientSideTranslatorPB`, `StorageBlockReport`, `BlockListAsLongs`, Mockito `ArgumentCaptor`, and `DFSConfigKeys.DFS_BLOCKREPORT_SPLIT_THRESHOLD_KEY`.

Control flow: `startUpCluster` builds a one-DN cluster with a configured threshold and records the block pool ID. `createFile` writes a file with five blocks. `verifyCapturedArguments` inspects every captured `StorageBlockReport[]`, asserts expected reports per RPC call, and sums block counts. `testAlwaysSplit` sets threshold 0 and expects one `blockReport` RPC per storage with one report per call. `testCornerCaseUnderThreshold` sets threshold to block count plus one and expects one RPC containing reports for all storages. `testCornerCaseAtThreshold` sets threshold equal to block count and expects splitting per storage.

State and persistence behavior: HDFS file blocks are persisted in the mini cluster; block-report behavior is observed through a spied NN protocol in the BPOfferService path. Integration points are DataNode block-report scheduler/RPC batching and NameNode protocol calls. Risks include assertion using Java `assert` for total block count, dependence on cluster storage count, and spy timing. Signals are Mockito call counts, captured report-array lengths, and total reported block count meeting or exceeding expected file blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDnRespectsBlockReportSplitThreshold.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestFsDatasetCacheRevocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestFsDatasetCacheRevocation.java

Purpose: tests FsDataset cache revocation semantics when a client has a short-circuit mmap reference to a cached replica.

Important APIs and types: `NativeIO.POSIX.CacheManipulator`, `NoMlockCacheManipulator`, `TemporarySocketDirectory`, `DomainSocket`, `MiniDFSCluster`, `DistributedFileSystem`, `CachePoolInfo`, `CacheDirectiveInfo`, `FsDatasetSpi`, `FSDataInputStream.read` with `ByteBuffer`, and cache verification helpers from `DFSTestUtil`/`TestFsDatasetCache`.

Control flow: setup saves/restores the native cache manipulator, disables domain socket bind-path validation, and creates a temporary socket directory. `getDefaultConf` enables short-circuit reads, configures domain socket path, small cache-report intervals, locked memory capacity, and block size. `testPinning` assumes native code and non-Windows, sets a long revocation timeout and short polling, caches a file, mmaps it, removes the cache directive, waits briefly, and verifies the block remains cached until `releaseBuffer`, after which cache usage drops to zero. `testRevocation` sets a very short revocation timeout, keeps the mmap held after directive removal, waits, and verifies the dataset uncaches despite the outstanding client reference.

State and persistence behavior: cache state lives in FsDataset locked-memory accounting and cache directive state in the NameNode. Integration points include short-circuit domain sockets, mmap buffer lifecycle, cache reports, and revocation timeout/polling. Risks include native-code availability, Windows exclusion, timing sleeps, and global native cache manipulator restoration. Signals are expected cache bytes/replica counts before and after directive removal and buffer release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestFsDatasetCacheRevocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHSync.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHSync.java

Purpose: integration-tests HDFS `hflush`/`hsync` semantics and DataNode `FsyncCount` metrics, including append, exact block boundaries, SequenceFile wrappers, and replicated pipelines.

Important APIs and types: `MiniDFSCluster`, `FSDataOutputStream`, `DistributedFileSystem`, `CreateFlag.SYNC_BLOCK`, `SequenceFile.Writer`, `RandomDatum`, `DefaultCodec`, `AppendTestUtil`, and metrics assertions against DataNode `FsyncCount`.

Control flow: `checkSyncMetric` reads each DataNode metric record. `testHSync` and `testHSyncWithAppend` call `testHSyncOperation`, which creates or appends a SYNC_BLOCK file, verifies `hflush` and empty `hsync` do not increment, writes data, verifies each `hsync` increments, verifies close increments for SYNC_BLOCK, then repeats without SYNC_BLOCK where close does not sync. `testHSyncBlockBoundary` writes exactly one block, observes sync on full-block `hflush`, then verifies further sync and close increments. `testSequenceFileSync` wraps an output stream in `SequenceFile.Writer`, checks writer `hflush` versus `hsync`, append plus `hsync`, writer close, and stream close. `testHSyncWithReplication` writes with replication 3 and verifies all three DNs increment on each `hsync`.

State and persistence behavior: files are written to a mini HDFS cluster and DataNode metrics persist for cluster lifetime. Integration points include DFS output stream flags, append path, sync-block packet handling, SequenceFile delegation, and replicated DataNode pipelines. Risks include metric naming stability and cleanup through explicit cluster shutdown. Signals are exact `FsyncCount` values after each operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHdfsServerConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHdfsServerConstants.java

Purpose: unit-tests parsing of `HdfsServerConstants.StartupOption` and optional `RollingUpgradeStartupOption` suffixes.

Important APIs and types: `StartupOption.getEnum`, `StartupOption`, `RollingUpgradeStartupOption`, and JUnit assertions/failures.

Control flow: `verifyStartupOptionResult` parses a string, asserts the expected startup option, and when a rolling-upgrade sub-option is expected, asserts `option.getRollingUpgradeStartupOption()`. `testStartupOptionParsing` covers plain options: `FORMAT`, `REGULAR`, `CHECKPOINT`, `UPGRADE`, `ROLLBACK`, `ROLLINGUPGRADE`, `IMPORT`, and `INITIALIZESHAREDEDITS`; it then expects `IllegalArgumentException` for an unknown option wrapper. `testRollingUpgradeStartupOptionParsing` covers `ROLLINGUPGRADE(ROLLBACK)` and `ROLLINGUPGRADE(STARTED)`, and expects `IllegalArgumentException` for an unknown rolling-upgrade sub-option.

State and persistence behavior: parsing may mutate the enum instance's rolling-upgrade sub-option state, but no filesystem or cluster state is involved. Integration point is common server startup option parsing used by NameNode/DataNode commands. Risks include enum-level mutable state leaking between calls if parser implementation changes and exact accepted string forms. Test signals are parsed enum equality, parsed rolling-upgrade sub-option equality, and expected exceptions for unknown values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHdfsServerConstants.java -->
