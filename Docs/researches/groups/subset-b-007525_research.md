# subset-b-007525 research

Grouped research for the Hadoop HDFS test files assigned to subset-b-007525. Each section preserves the source path for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureBase.java

Purpose: base fixture for striped HDFS write tests under datanode failure. It constructs an erasure-coded MiniDFSCluster, writes files at boundary-heavy lengths, kills striped stream targets mid-write, and verifies generation stamps plus reconstructed data.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSStripedOutputStream`, `StripedDataStreamer`, `ErasureCodingPolicy`, `ECSchema`, `AddErasureCodingPolicyResponse`, `BlockTokenSecretManager`, `SecurityTestUtil`, and `StripedFileTestUtil`. Helper methods include `init`, `newLengths`, `getDnIndexSuite`, `combinations`, `setup`, `newHdfsConfiguration`, `runTest`, `runTestWithMultipleFailure`, `killDatanode`, `getDatanodes`, and `waitTokenExpires`.

Control flow: `init` derives data/parity counts, block size, block group size, failure index combinations, and file lengths around cell and block-group boundaries. `setup` starts a cluster with one DN per EC unit, registers/enables the policy, creates the EC directory, and configures native RS coders when available. `runTest` writes byte-by-byte through `FSDataOutputStream`, records generation stamps after flush positions and block groups, stops specific datanodes at configured byte offsets, optionally waits for block-token expiry, then closes and validates block reports and file data.

State and persistence: creates HDFS directories/files under the test path, mutates cluster datanode liveness, changes block-token lifetime in the NameNode block manager, and relies on block reports to persist post-failure block-group metadata. It also maintains in-memory length suites, killed DN lists, and generation-stamp lists.

Dependencies and integration: integrates HDFS client write pipeline, EC policy registration, block placement, NameNode block management, datanode stop/start semantics, block tokens, native erasure coding, and `StripedFileTestUtil.checkData`.

Risks: timing-sensitive waits for streamer targets and token expiry; randomized DN index subset selection; skipped cases when kill positions occur before `FLUSH_POS`; strong dependence on internal stream state and generation stamp behavior.

Test signals: assertions on valid kill positions, datanode selection, generation stamp monotonicity, number of killed DNs, block-group reports, and full data verification against expected striped bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java

Purpose: variant of striped-output failure tests that runs the inherited failure suite with a random non-default erasure coding schema.

Important APIs and types: extends `TestDFSStripedOutputStreamWithFailure`, uses `ECSchema`, `StripedFileTestUtil.getRandomNonDefaultECPolicy`, SLF4J logging, and JUnit `@Tag("slow")`.

Control flow: constructor chooses and logs a random non-default EC policy schema. The overridden `getEcSchema` returns that schema to the base initialization path, so inherited setup computes data/parity units and block sizing from this non-default policy.

State and persistence: only stores the selected schema in an instance field. Persistent state is produced by inherited MiniDFSCluster writes, EC policy registration, DN failures, and verification.

Dependencies and integration: depends entirely on the inherited striped failure framework and random EC policy utility. It broadens coverage from the default schema to alternate codec layouts.

Risks: random policy selection can vary runtime, parity count, DN count, and failure combinations. Failures may be harder to reproduce unless logs capture the selected schema.

Test signals: inherited assertions from the base failure tests are the real signal; this class adds evidence that non-default EC schemas survive the same failure scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailureWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithRandomECPolicy.java

Purpose: variant of the base striped output stream tests that runs normal striped writes against a random non-default erasure coding policy.

Important APIs and types: extends `TestDFSStripedOutputStream`, stores an `ErasureCodingPolicy`, and obtains it from `StripedFileTestUtil.getRandomNonDefaultECPolicy`.

Control flow: constructor selects/logs the policy once per test instance. Overridden `getEcPolicy` feeds that policy into the inherited striped-output setup and assertions.

State and persistence: this class only persists the chosen policy in memory. HDFS state, files, block groups, and EC metadata are created by inherited tests.

Dependencies and integration: integrates with the general striped output test suite and policy utilities, ensuring inherited write, flush, close, and validation code is not bound to the default EC policy.

Risks: randomized policy choice can make failures policy-dependent and less deterministic. Because this class contains no direct assertions, any missing inherited coverage would leave the variant shallow.

Test signals: inherited striped-output test assertions, with constructor logging of the selected policy for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgrade.java

Purpose: validates NameNode and DataNode upgrade behavior across valid storage layouts, invalid storage states, multiple storage directories, rolling-upgrade rejection during upgrade, and layout-version boundaries.

Important APIs and types: `UpgradeUtilities`, `MiniDFSCluster.Builder`, `StartupOption.UPGRADE/REGULAR`, `StorageInfo`, `Storage`, `DataNodeLayoutVersion`, `NNStorage` image/edit filename helpers, `InconsistentFSStateException`, `RemoteException`, and `TestParallelImageWrite`.

Control flow: `initialize` prepares master upgrade fixtures. `testUpgrade` loops over one and two storage directories, creates current/previous NN and DN states, starts clusters with `format(false)` and unmanaged directories, verifies success cases, and asserts failures for existing previous dirs, future layout versions, newer CTime, missing edits/image files, corrupt VERSION files, and too-old/future NameNode versions. A four-directory case verifies parallel image writes. Helpers check checksums and expected file presence.

State and persistence: directly creates, deletes, and corrupts NameNode/DataNode storage directories under test storage. Verifies `current`, `previous`, `VERSION`, `seen_txid`, fsimage, and in-progress edits files. DataNode checks include finalized block-pool directories.

Dependencies and integration: exercises storage upgrade code, block pool initialization, safe mode, rolling upgrade guardrails, image write parallelism, and checksum fixtures from `UpgradeUtilities`.

Risks: hard-coded `EXPECTED_TXID`, directory-sensitive checksum expectations, disabled manual failure test, and broad filesystem mutation make failures environment-sensitive.

Test signals: expected directory existence, checksum equality with master fixtures, image parity across storage dirs, expected startup exceptions, failed block-pool service, and layout-version exception checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgradeFromImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgradeFromImage.java

Purpose: upgrades archived historical HDFS image/data directories, verifies file checksums and namespace shape, tests reserved-path migrations, checks corrupt image rejection, and ensures edit logs remain available through inotify after upgrade.

Important APIs and types: `MiniDFSCluster`, `StartupOption.UPGRADE`, `FSImageFormat`, `FSImageTestUtil`, `IllegalReservedPathException`, `DFSInotifyEventInputStream`, `EventBatch`, `DirectoryListing`, `HdfsFileStatus`, `CRC32`, `FileUtil.unTar`, and `ClusterVerifier`.

Control flow: `unpackStorage` extracts a tarred DFS image and loads reference checksums. `upgradeAndVerify` starts an unmanaged upgrade cluster, waits for safe mode exit, recursively recovers leases, verifies file contents, and optionally invokes a verifier. Reserved-path tests set rename pairs, list the namespace before and after finalize/restart, and compare expected paths. Corrupt MD5 modifies VERSION files and checks startup failure. `testPreserveEditLogs` consumes expected create/close/rename/unlink inotify events from preserved edits.

State and persistence: unpacks historical NN/DN storage under test directories, reads checksum manifests, mutates fsimage rename-reserved settings, finalizes clusters, restarts NameNode, recovers leases, and reads edit-log-backed inotify streams.

Dependencies and integration: integrates upgrade storage loading, FSImage compatibility, reserved namespace protection, lease recovery, DFSClient listings, block reads, and inotify event reconstruction.

Risks: depends on external test tarballs and checksum text order, sleeps/retries lease recovery, static reserved rename pairs can leak if not reset by framework, and inotify expectations are tightly bound to fixture edit order.

Test signals: exact per-file CRCs and overall CRC, expected startup failures/messages, expected renamed paths and counts, lease recovery success, preserved inotify event types/paths/txids, and null polling past the last edit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUpgradeFromImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUtil.java

Purpose: broad unit/regression coverage for DFS utility methods spanning block-location conversion, HA/federation address resolution, config key rewriting, internal NameNode URI discovery, path validation, credentials, encryption probing, metrics math, and lazy DNS resolution.

Important APIs and types: `DFSUtil`, `DFSUtilClient`, `HAUtil`, `NameNode.initializeGenericKeys`, `ConfiguredFailoverProxyProvider`, `HdfsClientConfigKeys`, `CredentialProviderFactory`, `JavaKeyStoreProvider`, `DataNodeMetrics`, `LocatedBlocks`, `BlockLocation`, and `UserGroupInformation`.

Control flow: each JUnit test constructs focused `HdfsConfiguration` objects, sets nameservice/NN-specific keys, calls DFS utility methods, and asserts returned maps, URIs, addresses, exceptions, or formatted values. Credential tests create a local JKS provider and confirm passwords are loaded through DFSUtil. Transfer-rate tests mock metrics. Lazy resolution tests toggle client config and inspect unresolved socket addresses.

State and persistence: mostly in-memory configuration state; persistent state is limited to a temporary Java keystore for credential-provider checks. `resetUGI` restores UGI configuration before each test to avoid cross-test security state.

Dependencies and integration: touches HDFS client/server config contracts, HA proxy provider semantics, WebHDFS HTTP/HTTPS address selection, Hadoop credential providers, platform-specific path validation, Java DNS behavior, and DataNode metrics.

Risks: host resolution differs by Java version and platform, Windows path acceptance is conditional, keystore files must be isolated, and assertions mirror subtle precedence rules among global, nameservice, and namenode-specific keys.

Test signals: exact address maps, URI sets, exception messages, password values, path validity booleans, duration/relative-time conversions, equality assertion behavior, encryption enabled flags, metric mock invocations, and lazy/unresolved socket state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataStream.java

Purpose: regression test ensuring client write streaming does not emit a slow `ReadProcessor` warning during delayed writes and flushes.

Important APIs and types: `MiniDFSCluster`, `FSDataOutputStream`, `DataStreamer`, `GenericTestUtils.LogCapturer`, and HDFS client write packet/socket/slow-IO configuration keys.

Control flow: `setup` starts a cluster with a 1024-byte write packet size, high slow-IO warning threshold, and long socket timeout. The test captures `DataStreamer` logs, writes two packets, hflushes, sleeps past the warning threshold, writes two more packets, hflushes again, closes, and checks the captured logs.

State and persistence: creates `/file1` in the cluster and writes random bytes. Captured logs are in-memory; cluster is static for the class and shut down in `tearDown`.

Dependencies and integration: integrates DFSClient packetization, `DataStreamer` log behavior, MiniDFSCluster write pipeline, and `hflush`.

Risks: sleep-based timing can be slow or flaky on overloaded hosts. The signal is a negative log assertion, so message text changes can affect the test without functional breakage.

Test signals: absence of `Slow ReadProcessor read fields for block` in captured DataStreamer logs after successful writes and flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferKeepalive.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferKeepalive.java

Purpose: verifies client and datanode socket keepalive behavior for data-transfer reads, including stale cached peers, client-side expiry, slow-reader write timeout, and many closed sockets in the client cache.

Important APIs and types: `MiniDFSCluster`, `DataNode`, `PeerCache`, `ClientContext`, `Peer`, `FSDataInputStream`, `DFSTestUtil`, `DataNodeProperties`, and socket cache/keepalive/write-timeout config keys.

Control flow: setup starts a one-DN cluster with short datanode keepalive and no block acquire retries. Tests create small or large files, read to populate `PeerCache`, sleep past either DN or client expiry, inspect active xceiver counts, fetch cached peers, restart the DN with a shorter write timeout for slow-reader behavior, and verify reads survive multiple cached closed sockets.

State and persistence: creates `/test`, fills client peer caches keyed by `DFS_CLIENT_CONTEXT`, restarts datanode with modified config, and observes datanode xceiver thread counts.

Dependencies and integration: integrates client peer caching, datanode xceiver lifecycle, socket EOF handling, restart properties, stream close cleanup, and DataNode write timeout behavior.

Risks: timing-sensitive sleeps and xceiver-count polling; direct reliance on internal peer cache and datanode thread counts; slow-reader test has a long timeout because it waits for server-side timeout.

Test signals: expected `PeerCache` sizes, expected xceiver counts, EOF from stale cached peer, null return for expired client peer, eventual xceiver exit during slow read, and successful read despite closed cached sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferKeepalive.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferProtocol.java

Purpose: low-level protocol robustness tests for DataNode data-transfer operations, malformed requests, block write stages, packet header serialization, pipeline-ack compatibility, and volume-reference cleanup on exceptions.

Important APIs and types: `DataTransferProtocol`, `Sender`, `Op`, `PacketHeader`, `PipelineAck`, `BlockConstructionStage`, `BlockOpResponseProto`, `ReadOpChecksumInfoProto`, `DataChecksum`, `ExtendedBlock`, `BlockTokenSecretManager.DUMMY_TOKEN`, `DataNodeTestUtils`, and `FsVolumeImpl`.

Control flow: helpers manually fill send/receive buffers, open sockets to the datanode transfer address, write raw protocol bytes, and compare expected protobuf/ack responses or EOF. `testOpWrite` walks finalized, new, and RBW block states across create/append/recovery stages. `testDataTransferProtocol` sends bad versions/opcodes, bad checksum parameters, negative packet lengths, zero-length blocks, and read-block edge cases. Other tests round-trip packet headers, merge old/new ack fields, and delete a meta file before `copyBlock` to verify volume reference counts.

State and persistence: creates HDFS files and blocks, appends to make RBW replicas, mutates `ExtendedBlock` IDs/generation stamps, deletes a replica meta file, and observes FsVolume reference counts.

Dependencies and integration: exercises DataXceiver protocol parsing, block sender/receiver, protobuf compatibility, checksum serialization, pipeline recovery rules, and fsdataset volume reference handling.

Risks: brittle expected wire responses and message strings; direct socket protocol construction bypasses higher-level clients; generation-stamp/block-state assumptions must track DataNode internals.

Test signals: exact hex/protobuf response matches, expected EOF on invalid operations, successful zero-length block write, read error responses for invalid offsets/lengths, packet-header equality/sanity checks, ack flag compatibility, final readable file, and unchanged volume reference count after exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDataTransferProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeConfig.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeConfig.java

Purpose: validates DataNode startup behavior for configured storage directory URI schemes, locked-memory limits, and consistency of bound IPC/HTTP addresses written back to configuration.

Important APIs and types: `DataNode.createDataNode`, `MiniDFSCluster`, `StartupOption.REGULAR`, `NativeIO.POSIX.getCacheManipulator`, `DFS_DATANODE_DATA_DIR_KEY`, `DFS_DATANODE_MAX_LOCKED_MEMORY_KEY`, and AssertJ assertions.

Control flow: class setup clears the cluster base dir and starts a zero-DN NameNode with ephemeral DN ports. `testDataDirectories` verifies unsupported URI schemes fail and file URI/path forms succeed. `testMemlockLimit` assumes native IO and finite memlock limit, then starts a DN at the limit and expects failure above it. `testDataNodeIpcAndHttpSeverConf` starts a DN and compares live listener/HTTP addresses to DN config values.

State and persistence: deletes and recreates MiniDFSCluster base dirs, configures datanode data directories, starts/shuts down individual DataNode instances, and mutates config values.

Dependencies and integration: covers DataNode storage path validation, native OS resource limits, address binding on ephemeral ports, and config normalization during startup.

Risks: native memlock test is platform-dependent and skipped when assumptions fail; base directory cleanup is destructive within the test root; URI parsing must match `Util.fileAsURI` behavior.

Test signals: null DN after unsupported scheme failure, cluster DN up for accepted directories, expected memlock-limit exception text, and exact IPC/HTTP host:port equality with DN configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeDeath.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeDeath.java

Purpose: stress tests HDFS write pipeline recovery when datanodes die or restart during active writes, both with single-file targeted failures and concurrent workloads.

Important APIs and types: `MiniDFSCluster`, `DFSOutputStream`, `FSDataOutputStream`, `FSDataInputStream`, `BlockLocation`, `SubjectInheritingThread`, `AppendTestUtil`, and HDFS heartbeat/reconstruction/client socket configs. Inner classes `Workload` and `Modify` coordinate writers and datanode restarts.

Control flow: `simpleTest` writes part of a file, obtains the write pipeline, stops a selected pipeline datanode, writes the rest, closes, and verifies full data and replication. `complexTest` starts multiple `Workload` threads creating and checking files while `Modify` waits for all workers to complete at least one file, then restarts random datanodes and resets progress stamps.

State and persistence: creates multiple HDFS files, writes deterministic random data, restarts/stops datanodes, waits for block locations and replica counts, and reads back full file contents.

Dependencies and integration: integrates DFSClient pipeline construction, packet/chunk settings, datanode restart handling, NameNode heartbeat/reconstruction timing, block-location reporting, and replica recovery.

Risks: highly timing-sensitive with sleeps, random victims/seeds, and thread coordination; long waits for replication can mask slow failures; tests use internal slowdown/chunk controls.

Test signals: file length equality, sufficient number of block locations and hosts per block, byte-for-byte data equality, and no assertion failures from workload or modifier threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeDeath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeLayoutUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeLayoutUpgrade.java

Purpose: verifies DataNode on-disk block layout upgrades from historical layouts to the current 32x32 block ID-based layout.

Important APIs and types: `TestDFSUpgradeFromImage`, `MiniDFSCluster.Builder`, `GenericTestUtils.getTestDir`, and fixture tar/checksum files for Hadoop 2.4 and layout -56 images.

Control flow: each test creates a `TestDFSUpgradeFromImage` helper, unpacks a historical DN/NN storage image, sets unmanaged data/name dirs to the unpacked fixture locations, and delegates to `upgradeAndVerify` with one datanode.

State and persistence: unpacks archived NameNode/DataNode directories, configures test data/name storage paths, runs an upgrade startup, and verifies filesystem contents via the shared checksum verifier.

Dependencies and integration: reuses the image-upgrade framework while specifically targeting DataNode layout conversion from LDir and 256x256 ID-based layouts to 32x32.

Risks: dependent on fixture availability and checksum manifest correctness; failure diagnostics are indirect because validation is delegated to shared upgrade verification.

Test signals: successful cluster upgrade and checksum verification for both historical layout inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeLayoutUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeRegistration.java

Purpose: tests DataNode registration semantics: avoiding DNS lookups after registration, reporting changed IPC/storage IDs, enforcing software-version/CTime rules, and forced re-registration after block-report or IBR failures.

Important APIs and types: `DatanodeRegistration`, `DatanodeID`, `DatanodeDescriptor`, `DatanodeManager`, `DatanodeStorageInfo`, `NamenodeProtocols`, `NameNodeAdapter`, `DataNodeTestUtils`, `BlockReportOptions`, `IncorrectVersionException`, and mocked `StorageInfo`.

Control flow: DNS test installs a `SecurityManager` counting reverse lookups and verifies refresh/report paths do not add lookups. IPC and storage ID tests restart/register nodes and inspect reports. Version tests mock DN registrations against configured minimum versions and CTimes. `testForcedRegistration` disables heartbeats, toggles `forceRegistration`, triggers heartbeats/block reports/deletion reports/failed IBR, and verifies registration object identity and descriptor state transitions.

State and persistence: starts clusters, registers fake datanodes with NameNode RPC, restarts datanodes, manipulates descriptor registration flags, triggers heartbeats/block reports, and sends deletion reports.

Dependencies and integration: covers NameNode datanode manager, client reports, registration RPCs, heartbeat pipeline, block-report processing, software compatibility checks, and incremental block report failure safety net.

Risks: `SecurityManager` is deprecated and may be unavailable; forced-registration checks rely on internal object identity and timing; mocked registration fields must remain consistent with NameNode validation.

Test signals: unchanged DNS lookup count, report length/IPC port equality, single report entry after storage ID change, expected `IncorrectVersionException` messages, block report processed or skipped as expected, and registration object identity changes only after forced heartbeat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeRegistration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeReport.java

Purpose: validates live/all/dead datanode reports, storage reports, upgrade-domain propagation from host config, expired heartbeat metrics, and reporting after all replicas of a block are deleted from disk.

Important APIs and types: `DFSClient.datanodeReport`, `getDatanodeStorageReport`, `DatanodeReportType`, `DatanodeAdminProperties`, `CombinedHostFileManager`, `HostsFileWriter`, `DatanodeStorageReport`, `StorageReport`, `LocatedBlock`, and metrics assertions.

Control flow: upgrade-domain test writes include-host JSON entries, refreshes nodes, and checks report domains. Main report test starts four DNs, checks ALL/LIVE/DEAD counts and storage IDs, shuts down one DN, waits until it appears dead, rechecks counts, and asserts `ExpiredHeartbeats`. Missing-block test writes a file, deletes block files on DNs, expects read failure, triggers heartbeats, and verifies located block locations drop to zero.

State and persistence: creates host include files, starts/shuts down datanodes, creates and corrupts HDFS block files, and observes NameNode metrics and block-location metadata.

Dependencies and integration: integrates host include provider, datanode manager refresh, DFSClient reports, fsdataset storage reports, block corruption/deletion handling, and FSNamesystem metrics.

Risks: waits for dead-node detection by polling, shared static configuration can retain values across tests, and direct block-file deletion bypasses normal datanode workflows.

Test signals: report counts, upgrade-domain values, datanode info equality with storage reports, matching storage IDs, `ExpiredHeartbeats` counter, read exception for missing block, and zero locations after deletion acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeStartupFixesLegacyStorageIDs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeStartupFixesLegacyStorageIDs.java

Purpose: verifies that DataNode startup or layout upgrade replaces legacy storage IDs with UUID-based IDs, while preserving already-valid unique storage IDs.

Important APIs and types: `TestDFSUpgradeFromImage`, `ClusterVerifier`, `DatanodeStorage.isValidStorageId`, `StorageReport`, `MiniDFSCluster.Builder`, `GenericTestUtils.getMethodName`, and AssertJ/JUnit assertions.

Control flow: `runLayoutUpgradeTest` unpacks a fixture named after the test method, initializes data/name dirs, runs shared upgrade verification, then inspects the first DataNode storage report. It asserts the storage ID is valid and optionally equals an expected preserved ID. Three tests cover upgrade from 2.2, startup from a 2.6 layout with legacy IDs, and startup from a 2.6 layout with a valid existing ID.

State and persistence: unpacks historical NN/DN images, performs upgrade/startup with unmanaged dirs, reads block-pool storage reports, and validates/generated storage IDs.

Dependencies and integration: shares checksum-based image upgrade verification and then adds DataNode storage-ID-specific assertions against fsdataset reports.

Risks: fixture names are tied to test method names; storage report ordering assumes a single report; generated UUID values are validated only structurally unless an expected ID is supplied.

Test signals: successful upgrade verification, exactly one storage report, valid `DS-...` storage ID format, and exact preservation of the known valid storage ID in the preservation case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeStartupFixesLegacyStorageIDs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeadNodeDetection.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeadNodeDetection.java

Purpose: tests DFSClient dead-node detection, shared detector lifecycle, background probe queues, dead-node recovery, suspect-node handling, and cleanup when streams or clients close.

Important APIs and types: `DeadNodeDetector`, `DFSClient`, `DFSInputStream`, `ClientContext`, `MiniDFSCluster`, `BlockMissingException`, `SubjectInheritingThread`, `DeadNodeDetector.UniqueQueue`, and dead-node detection config keys.

Control flow: setup enables dead-node detection with short probe intervals/timeouts. Tests create replicated small files, stop datanodes, trigger reads that throw `BlockMissingException`, then wait until detected-dead-node counts reach expected values. Multi-stream tests confirm shared client context. Recovery restarts one DN and expects count reduction. Probe tests spy suspect/dead queues. Suspect-node test disables probe thread, restarts a DN, then starts scheduler and expects queues to drain. Lifecycle tests open two DFS instances to the same URI and verify detector sharing, shutdown, and recreation.

State and persistence: creates and deletes test files, stops/restarts datanodes, mutates static test flags for detector threads, tracks detector queues and client dead-node maps, and closes streams/filesystems to trigger cleanup.

Dependencies and integration: integrates DFSInputStream failure handling, ClientContext sharing, background detector scheduler, datanode probe connection attempts, and MiniDFSCluster node lifecycle.

Risks: background-thread timing and static test flags can cause flakiness if cleanup fails; repeated `clearAndGetDetectedDeadNodes` both observes and mutates detector state; tests depend on same-context DFSClient reuse.

Test signals: exact dead-node map sizes, detected-dead-node counts, expected datanode UUIDs, Mockito queue offer/poll counts, suspect queue drain after scheduler start, detector alive/shutdown/null state after filesystem close, and cleanup to zero dead nodes after file deletion/stream close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeadNodeDetection.java -->
