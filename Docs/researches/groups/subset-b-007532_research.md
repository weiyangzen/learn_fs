# subset-b-007532 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSecureEncryptionZoneWithKMS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSecureEncryptionZoneWithKMS.java

Purpose: JUnit 5 integration coverage for HDFS encryption zones backed by a secure Kerberos MiniKMS and a secure MiniDFSCluster. It proves that encrypted file creation and encryption-zone creation keep working with KMS authentication, HTTPS-only HDFS endpoints, block access tokens, SASL retries, delegation-token forcing, and a deliberately small KMS encrypted-key cache.

Important APIs and types: `MiniKdc`, `MiniKMS`, `MiniDFSCluster`, `HdfsAdmin.createEncryptionZone`, `KMSClientProvider`, `KeyStoreTestUtil`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `UserGroupInformation.createProxyUser`, `FileSystemTestWrapper`, `DFSTestUtil.createKey`, and `DFSTestUtil.createFile`. The two tests are `testSecureEncryptionZoneWithKMS` and `testCreateZoneAfterAuthTokenExpiry`.

Control flow: `@BeforeAll init` creates a temp target directory, starts MiniKdc, generates principals/keytab, configures Kerberos, HTTPS, proxy-user mapping, KMS ACLs, and low auth-token validity, writes `kms-site.xml`, and starts MiniKMS. `@BeforeEach setup` starts a secure MiniDFSCluster using the KMS URI, creates the test key once, and prepares `FileSystem` and `HdfsAdmin`. The first test creates an EZ owned by a proxied Oozie user and creates three files to trigger KMS EDEK cache refill. The second logs in as hdfs, creates one zone, sleeps beyond auth token validity, and creates another zone to verify token refresh.

State and persistence behavior: State is mostly ephemeral test infrastructure in `baseDir`, generated keytab, keystore files, KMS keystore, MiniKMS service, and MiniDFSCluster metadata. `testKeyCreated` is static so repeated per-test clusters reuse the logical key without recreating it. No long-lived repository files are modified.

Dependencies and integration points: This test touches HDFS security configuration, KMS authentication, SSL config resources, DFS block-token/data-transfer protection, proxy users, KMS ACL enforcement, encryption-zone creation, and DFS client file creation in EZs.

Risks and test signals: It is sensitive to Kerberos hostname behavior, token-expiry timing, HTTPS keystore cleanup, and static key state across test methods. Passing tests signal that secure KMS/HDFS integration supports proxied encrypted writes and KMS auth-token renewal after expiration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSecureEncryptionZoneWithKMS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSeekBug.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSeekBug.java

Purpose: Regression coverage for historical seek bugs in `FSDataInputStream` against both HDFS and local filesystems. It validates large buffered reads followed by small backward/forward seeks, negative seek rejection, and seek-past-EOF rejection.

Important APIs and types: `FSDataInputStream.seek`, `FSDataInputStream.getPos`, `IOUtils.readFully`, `ChecksumFileSystem.getRawFileSystem`, `MiniDFSCluster`, `DFSTestUtil.createFile`, `FileSystem.getLocal`, and JUnit `assertThrows`.

Control flow: `seekReadFile` opens with a 4096-byte buffer, reads an initial 128 bytes, then reads a large 100000-byte range and seeks to 96036 to verify bytes match the deterministic random payload. `smallReadSeek` unwraps checksum filesystems, uses a buffer size of 1, seeks to 100000, then performs nearby seeks to exercise HADOOP-922 behavior. `testSeekBugDFS` creates a 1 MiB HDFS file and runs both helpers. `testNegativeSeek` and `testSeekPastFileSize` create files, perform a valid seek, then assert an `IOException` for invalid offsets. `testSeekBugLocalFS` repeats the main seek check on LocalFS.

State and persistence behavior: Each test creates temporary data (`seektest.dat` or `seekboundaries.dat`) with deterministic seed `0xDEADBEEF`, then deletes or closes cluster resources. LocalFS uses `GenericTestUtils.getTempPath`.

Dependencies and integration points: Exercises HDFS client stream buffering, local raw filesystem behavior, DFS block sizing/default replication, and checksum wrapper behavior.

Risks and test signals: The tests depend on exact byte identity from deterministic random data and on invalid seeks throwing during `seek`. Passing signals that buffered and positioned seek semantics preserve stream position and data integrity across DFS and LocalFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSeekBug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetTimes.java

Purpose: Tests HDFS file and directory access-time/modification-time behavior, including explicit `setTimes`, close-time mtime updates, access-time lock behavior, disabled automatic atime support, and persistence after NameNode restart.

Important APIs and types: `FileSystem.setTimes`, `FileStatus.getAccessTime`, `FileStatus.getModificationTime`, `FSDataOutputStream.close`, `DFSClient.datanodeReport`, `NameNodeAdapterMockitoUtil.spyOnFsLock`, `MockitoUtil.doThrowWhenCallStackMatches`, `DFS_NAMENODE_ACCESSTIME_PRECISION_KEY`, and `MiniDFSCluster`.

Control flow: `writeFile` writes deterministic data. `testTimes` creates a file, records atime/mtime before and after close, verifies `-2` leaves times unchanged, sets atime and mtime independently, sets directory times, validates a missing path error, restarts the cluster without formatting, and checks persisted times. `testTimesAtClose` confirms mtime changes when a written file is closed. `testGetBlockLocationsOnlyUsesReadLock` spies on the FSNamesystem lock and fails if `getBlockLocations` takes the write lock when atime precision says no update is needed. `testAtimeUpdate` disables automatic atime updates but verifies explicit `setTimes` still sets atime.

State and persistence behavior: HDFS metadata times are stored in NameNode namespace/edit log state and are verified across restart in `testTimes`. DataNode reports are only diagnostic on failure.

Dependencies and integration points: Integrates `FileSystem`, `DFSClient`, NameNode locking, heartbeat timing, datanode reports, Mockito-based lock spying, and HDFS access-time precision configuration.

Risks and test signals: Timing comparisons can be sensitive to clock granularity and restart timing. Passing signals that time metadata updates are durable, close updates mtime, explicit atime works even when automatic atime is disabled, and read-only block-location paths avoid unnecessary write locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetTimes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepDecreasing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepDecreasing.java

Purpose: Minimal wrapper test for decreasing HDFS file replication through the shared `TestSetrepIncreasing.setrep` helper.

Important APIs and types: JUnit `@Test`, `@Timeout`, and `TestSetrepIncreasing.setrep`.

Control flow: The sole test method `testSetrepDecreasing` calls `setrep(5, 3, false)`, which creates a MiniDFSCluster, writes a file, runs `FsShell -setrep -w`, and validates resulting block-location host counts.

State and persistence behavior: All state is delegated to the helper: a temporary MiniDFSCluster, HDFS test path `/test/setrep5-3`, and a file whose replication factor is changed from 5 to 3.

Dependencies and integration points: Depends directly on the increasing test helper and indirectly on FsShell replication command handling, NameNode replication tracking, block reports, and `DistributedFileSystem.getFileBlockLocations`.

Risks and test signals: Because this class is only a wrapper, any failure points to helper behavior or setrep semantics rather than local code. Passing signals that reducing replication through `-setrep -w` converges to the requested replica count within the timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepDecreasing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepIncreasing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepIncreasing.java

Purpose: End-to-end tests for increasing replication with FsShell, simulated-storage behavior, and edge cases involving storage policy and erasure-coded files.

Important APIs and types: `FsShell -setrep`, `MiniDFSCluster`, `SimulatedFSDataset`, `DistributedFileSystem`, `BlockLocation`, `NameNodeProxies.createProxy`, `ClientProtocol.enableErasureCodingPolicy`, `ClientProtocol.setErasureCodingPolicy`, and `StripedFileTestUtil.getDefaultECPolicy`.

Control flow: Static `setrep` builds a 10-datanode cluster, optionally installs `SimulatedFSDataset`, configures default replication and short block-report/pending reconstruction intervals, creates a file with `TestDFSShell`, runs `-setrep -w`, refreshes the filesystem, and validates each block location has `toREP` hosts. `testSetrepIncreasing` and `testSetrepIncreasingSimulatedStorage` call it for 3 to 7 replicas. `testSetRepWithStoragePolicyOnEmptyFile` sets HOT storage policy on a directory, creates an empty file, and sets replication to 4 without error. `testSetRepOnECFile` enables EC at root, creates an EC file, runs `-setrep 2`, expects a skip message, and validates replication remains 1.

State and persistence behavior: Test state lives in MiniDFSCluster metadata and block placement. Shell output is captured for the EC skip message.

Dependencies and integration points: Covers FsShell, NameNode block-management convergence, simulated datanode storage, storage policy metadata, EC policy metadata, and client RPC proxy setup.

Risks and test signals: Setrep convergence depends on block reports and reconstruction timing. Passing signals replication changes are honored for replicated files, tolerated for empty storage-policy files, and intentionally ignored for erasure-coded files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSetrepIncreasing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSlowDatanodeReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSlowDatanodeReport.java

Purpose: Verifies that DataNode peer outlier metrics propagate to NameNode slow-datanode reports and are visible through client-facing `DistributedFileSystem.getSlowDatanodeStats` and NameNode slow peer report strings.

Important APIs and types: `DataNode.getPeerMetrics().setTestOutliers`, `OutlierMetrics`, `DistributedFileSystem.getDataNodeStats`, `DistributedFileSystem.getSlowDatanodeStats`, `NameNode.getSlowPeersReport`, `GenericTestUtils.waitFor`, and slow-node DFS config keys.

Control flow: `@BeforeEach` creates a three-datanode cluster with peer stats enabled, low report interval, and one-node/one-sample outlier thresholds. `testSingleNodeReport` injects one outlier map entry from datanode 0 about datanode 1, waits until exactly one slow node appears, then asserts the report includes hostname and metric values. `testMultiNodesReport` injects two outlier entries from different reporters about datanodes 1 and 2, waits for two slow nodes, and checks report contents.

State and persistence behavior: State is in-memory peer metrics and NameNode aggregated slow-peer reports. There is no persistence check; cluster shutdown clears state.

Dependencies and integration points: Integrates datanode peer metrics, outlier detection thresholds, NameNode reporting aggregation, DFS client admin stats, and async report timing.

Risks and test signals: Uses long waits up to 180-200 seconds because reports are asynchronous. Passing signals slow peer metrics are consumed, aggregated, and surfaced with expected outlier values and host identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSlowDatanodeReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSmallBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSmallBlock.java

Purpose: Tests HDFS files whose block size and checksum size are smaller than normal client buffers, specifically one-byte blocks for a 20-byte file.

Important APIs and types: `DFSTestUtil.createFile`, `DistributedFileSystem.getFileBlockLocations`, `FSDataInputStream.readFully`, `LocatedBlocks`, `DFSTestUtil.fillExpectedBuf`, and `SimulatedFSDataset`.

Control flow: `testSmallBlock` configures `dfs.bytes-per-checksum` to 1, optionally uses simulated storage, starts a MiniDFSCluster, creates `/smallblocktest.dat` with block size 1 and file size 20, then calls `checkFile`. `checkFile` asserts there are exactly 20 block locations, reads the whole file from offset 0, and compares against either deterministic random bytes or simulated-storage expected bytes. `testSmallBlockSimulatedStorage` toggles the instance flag and reuses `testSmallBlock`.

State and persistence behavior: HDFS stores 20 tiny blocks and associated checksums for the duration of the test. Simulated mode changes expected data derivation because bytes are synthesized from located-block metadata.

Dependencies and integration points: Exercises block-location listing, checksum configuration, client reads over many tiny blocks, and simulated storage dataset integration.

Risks and test signals: The mutable `simulatedStorage` flag is reset after the simulated test; failure to reset could affect later methods in the same instance. Passing signals HDFS correctly handles sub-buffer block/checksum sizes and maps one byte per block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSmallBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSnapshotCommands.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSnapshotCommands.java

Purpose: End-to-end coverage for HDFS snapshot-related DFSAdmin, FsShell, and SnapshotDiff command behavior.

Important APIs and types: `DistributedFileSystem.allowSnapshot`, `deleteSnapshot`, `disallowSnapshot`, `getSnapshotDiffReport`, `DFSTestUtil.DFSAdminRun`, `DFSTestUtil.FsShellRun`, `DFSTestUtil.toolRun`, `SnapshotDiff`, `SnapshotDiffReport`, and `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`.

Control flow: `@BeforeAll` starts one cluster with max snapshots set to 3. `@BeforeEach` recreates `/sub1`, allows snapshots, and creates child dirs. Tests cover idempotent allow/disallow, snapshot creation and duplicate-name errors, max snapshot limit enforcement, reserved `.snapshot` mkdir behavior, snapshot rename success and failure cases, delete-snapshot errors, blocked deletion of snapshottable dirs with snapshots, fully qualified URI paths ignoring bad defaultFS, and snapshot diff output matching API reports. `testSnapshotDiff` creates enough files to force chunked diff generation.

State and persistence behavior: The tests mutate HDFS namespace snapshots under `/sub1`, `/sub3`, `/Fully/QPath`, and `/snap_dir`. `@AfterEach` deletes snapshots before disallowing snapshot and deleting `/sub1`, but some tests perform their own cleanup for other paths.

Dependencies and integration points: Integrates CLI parsing, admin commands, filesystem snapshots, reserved path names, URI-qualified paths, snapshot diff API/tool parity, and chunked diff report backing storage.

Risks and test signals: Cleanup completeness matters because the cluster is shared across tests. Passing signals command-line snapshot workflows produce expected status codes/messages and consistent API-visible snapshot state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSnapshotCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStateAlignmentContextWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStateAlignmentContextWithHA.java

Purpose: Slow HA/observer-read tests for server-to-client state alignment. It verifies that client `ClientGSIContext` last-seen state IDs catch up after writes, reads, fresh clients, failover, and concurrent client load.

Important APIs and types: `MiniQJMHACluster`, `HATestUtil.setUpObserverCluster`, `HATestUtil.configureObserverReadFs`, `ObserverReadProxyProvider`, `ClientGSIContext`, `ClientProtocol`, `DFSTestUtil.writeFile/readFile`, `MiniDFSCluster.transitionToStandby/transitionToActive`, and inner `Worker`.

Control flow: Static startup config enables state context and observer cluster setup. `ORPPwithAlignmentContexts` subclasses `ObserverReadProxyProvider` and records each created alignment context in `AC_LIST`. Tests compare client last-seen state IDs against active NameNode `getLastWrittenTransactionId` after write/read RPCs, verify a fresh client starts at `Long.MIN_VALUE`, and repeat write validation across failover. `testMultiClientStatesWithRandomFailovers` creates multiple DFS clients, starts worker callables writing many files, triggers failover while they run, waits for completion, and verifies all workers report success.

State and persistence behavior: NameNode transaction IDs and client GSI contexts are the core state. The cluster persists across tests but `@AfterEach` kills clients, resets active/standby roles, closes DFS, and clears context tracking.

Dependencies and integration points: Integrates HA failover, QJM-backed observer cluster, observer-read proxy provider, client RPC alignment context, DFS write/read paths, and concurrent client operation.

Risks and test signals: `AC_LIST` indexing depends on client creation order; worker `nonce` maps to context list positions. Passing signals clients receive and retain monotonic state IDs even when active NameNode changes during concurrent writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStateAlignmentContextWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStoragePolicyPermissionSettings.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStoragePolicyPermissionSettings.java

Purpose: Tests NameNode storage-policy permission modes: default POSIX-style permission checks, superuser-only enforcement, and global storage-policy disablement.

Important APIs and types: `DistributedFileSystem.setStoragePolicy`, `getStoragePolicy`, `BlockStoragePolicySuite`, `FSNamesystem` fields `isStoragePolicyEnabled` and `isStoragePolicySuperuserOnly`, `ReflectionUtils.setFinalField`, `UserGroupInformation.createUserForTesting`, `DFSTestUtil.getFileSystemAs`, and `LambdaTestUtils.intercept`.

Control flow: Shared cluster setup creates one datanode, default policy suite, COLD policy, a non-admin user, and a supergroup admin. `setStoragePolicyPermissions` mutates final FSNamesystem fields by reflection. `testStoragePolicyPermissionDefault` first denies non-admin on a non-writable file, then chmods to 777 and allows setting COLD. `testStoragePolicyPermissionAdmins` enables superuser-only mode and verifies non-admin denial but admin success. `testStoragePolicyPermissionDisabled` disables storage policies and verifies an IOException while policy remains default.

State and persistence behavior: Tests reuse a static cluster and repeatedly create `/foo`; policy and permission state are stored in NameNode namespace. Reflection mutates global NameNode booleans and can affect subsequent tests if not overwritten.

Dependencies and integration points: Integrates storage policy RPCs, FS permission checking, superuser privilege checks, UGI impersonation, and NameNode internal configuration state.

Risks and test signals: Shared `/foo` and reflected final fields create order sensitivity if a test fails before resetting expected modes. Passing signals policy setting respects configured permission gates and disabled mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStoragePolicyPermissionSettings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStripedFileAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStripedFileAppend.java

Purpose: Tests append behavior for erasure-coded striped files, including supported append-to-new-block behavior and unsupported append-without-new-block behavior.

Important APIs and types: `DistributedFileSystem.setErasureCodingPolicy`, `dfs.append` with `CreateFlag.APPEND` and `CreateFlag.NEW_BLOCK`, `LocatedBlocks`, `StripedFileTestUtil.verifyStatefulRead`, `verifySeek`, `RemoteIterator<OpenFileEntry>`, and `OpenFilesType.ALL_OPEN_FILES`.

Control flow: Each test creates a MiniDFSCluster with nine datanodes and block size derived from default EC policy cell size and stripes-per-block, creates `/TestFileAppendStriped`, and sets EC policy. `testAppendToNewBlock` writes six splits: first with create, subsequent with append plus NEW_BLOCK. Each split writes a random length less than one block group from a generated expected buffer, then closes. It asserts six located block groups and verifies reads/seeks. `testAppendWithoutNewBlock` writes a small EC file, attempts append without NEW_BLOCK, asserts the expected unsupported-operation message, then lists open files to ensure the failed append left no lease/open-file state.

State and persistence behavior: File data and EC block groups live in MiniDFSCluster for the test. The failed append test checks transient open-file state is cleaned up.

Dependencies and integration points: Integrates EC policy inheritance, DFS striped output, append flags, NameNode open-file tracking, located-block metadata, and striped read verification.

Risks and test signals: Random split lengths mean coverage varies while staying under block-group size. Passing signals append-to-new-block creates correct block groups and failed unsupported append does not leak open file handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStripedFileAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithEncryptionZones.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithEncryptionZones.java

Purpose: Tests Trash behavior inside non-Kerberos HDFS encryption zones using a local Java keystore provider.

Important APIs and types: `JavaKeyStoreProvider`, `HdfsAdmin.createEncryptionZone`, `CreateEncryptionZoneFlag.NO_TRASH`, `PROVISION_TRASH`, `FsShell`, `ToolRunner`, `FileSystemTestWrapper`, `DFSTestUtil.verifyDelete`, `DFSTestUtil.createKey`, and `UserGroupInformation.doAs`.

Control flow: `setup` builds a MiniDFSCluster with Java key provider path, delegation-token forcing, small EZ list batch size, and Trash interval of one minute, then creates the test key and shell. `testDeleteWithinEncryptionZone` creates an EZ with provisioned trash, creates an encrypted file, and verifies file and directory delete move through Trash. `testDeleteEZWithMultipleUsers` creates an EZ without provisioned trash, makes it world-writable, has a non-admin user create/delete a file into per-user EZ trash, verifies that user cannot delete the whole EZ, then recreates shell as the original user and deletes the zone.

State and persistence behavior: State includes the local JKS file in the test root, HDFS EZ metadata, trash directories under EZs, and per-user ownership/permissions. It is removed when the cluster/test root is torn down.

Dependencies and integration points: Integrates key provider flushing, encryption-zone metadata, FsShell delete semantics, Trash path selection, UGI user ownership, and NameNode EZ deletion permission checks.

Risks and test signals: The client key provider is explicitly pointed at the NameNode provider for JKS flushing; without that, key updates can be stale. Passing signals Trash works correctly for EZ contents and protects multi-user EZ deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithEncryptionZones.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithSecureEncryptionZones.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithSecureEncryptionZones.java

Purpose: Secure counterpart to encryption-zone Trash tests, using Kerberos MiniKdc, MiniKMS, HTTPS-only HDFS endpoints, and a shared secure MiniDFSCluster.

Important APIs and types: `MiniKdc`, `MiniKMS`, `HdfsAdmin.createEncryptionZone`, `FsShell`, `ToolRunner`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `KMSClientProvider`, `KeyStoreTestUtil`, `DFSTestUtil.verifyDelete`, and Trash helpers `getCurrentTrashDir`, `-expunge`, `-skipTrash`.

Control flow: Static `init` creates Kerberos principals/keytab, configures secure HDFS/KMS/SSL, writes `kms-site.xml`, starts MiniKMS and MiniDFSCluster, creates the KMS key, and configures `FsShell` with Trash interval 1. Tests validate encrypted-file delete goes to EZ-local Trash, whole-zone delete goes to home Trash, expunge removes encrypted and non-encrypted trash entries, `-skipTrash` bypasses trash, empty directory delete requires `-r`, deleting a file from inside EZ Trash works, and trash files survive NameNode restart.

State and persistence behavior: Uses static cluster, filesystem, shell, counters, KDC, KMS, generated keytab, KMS keystore, and SSL artifacts. `testTrashRetentionAfterNamenodeRestart` explicitly validates Trash metadata persists across NameNode restart.

Dependencies and integration points: Integrates secure HDFS, secure KMS, encryption-zone trash provisioning, shell delete/expunge behavior, user home trash layout, and NameNode restart behavior.

Risks and test signals: Method ordering is fixed by method name, but static counters still avoid path reuse. Security setup is heavyweight and hostname-sensitive. Passing signals secure EZ Trash placement, skip/expunge semantics, and restart retention are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestTrashWithSecureEncryptionZones.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestUnsetAndChangeDirectoryEcPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestUnsetAndChangeDirectoryEcPolicy.java

Purpose: Tests setting, unsetting, changing, inheriting, and persisting erasure-coding policies on directories and root, plus invalid path/file cases.

Important APIs and types: `DistributedFileSystem.setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `getErasureCodingPolicy`, `DFSTestUtil.enableAllECPolicies`, `SystemErasureCodingPolicies`, `NoECPolicySetException`, `ErasureCodeNative`, `NativeRSRawErasureCoderFactory`, and `cluster.restartNameNode`.

Control flow: Setup creates a cluster with `dataBlocks + parityBlocks` datanodes, EC block size, no reconstruction max streams, optional native RS coder config, and all EC policies enabled. Tests cover unsetting absent EC policy, creating EC files before unset and replicated files after unset, nested child policy override then fallback to parent policy, root policy unset/change, replicated files with different replication factors after unset, nonexistent path failures, disallowing set/unset on files, and edit-log persistence of root unset across restart.

State and persistence behavior: EC policy xattrs/metadata live in NameNode namespace and are inherited at file creation time. Existing EC files retain their policy after directory policy changes. `testUnsetEcPolicyInEditLog` confirms unset operation persists via edit log.

Dependencies and integration points: Integrates EC policy management, system policies, native coder configuration, file creation under EC directories, root path behavior, exceptions, and NameNode restart/edit-log replay.

Risks and test signals: Some tests delete root recursively after root-policy cases, so isolation relies on fresh MiniDFSCluster per test. Passing signals EC directory policy semantics and persistence are correct for inheritance and invalid operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestUnsetAndChangeDirectoryEcPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystem.java

Purpose: Extends the normal `TestDistributedFileSystem` suite while substituting `ViewDistributedFileSystem`, and adds ViewDFS-specific tests for path handles, delegation tokens, rename options, quotas, path capabilities, and safe mode APIs.

Important APIs and types: `ViewDistributedFileSystem`, `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `PathHandle`, `Options.Rename`, `CommonPathCapabilities.FS_TRUNCATE`, `LEASE_RECOVERABLE`, `LeaseRecoverable`, `SafeMode`, `SafeModeAction`, and deprecated `HdfsConstants.SafeModeAction`.

Control flow: `getTestConfiguration` maps `fs.hdfs.impl` to ViewDFS. `testStatistics` resets ViewDFS statistics thread-local state before invoking the superclass test. Other tests start MiniDFSClusters, configure fallback/mount links, and validate opening by path handle, empty delegation token handling, rename with options through fallback and mount entries, quota setting through ViewDFS reflected in real DFS, path capabilities/interfaces, and safe mode transitions through both new and deprecated APIs.

State and persistence behavior: State is temporary HDFS namespace data, mount-table configuration, statistics thread-local data, quota metadata, and NameNode safe-mode state. Each cluster is closed inside tests.

Dependencies and integration points: Integrates ViewDFS overload of the HDFS scheme, fallback links, mount entries, DFS admin APIs routed through ViewDFS, inherited DFS contract behavior, and compatibility APIs.

Risks and test signals: The statistics test uses Whitebox reflection on internal thread-local state. Passing signals ViewDFS preserves expected DistributedFileSystem behavior while exposing HDFS-specific capabilities and administrative operations through viewfs routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemContract.java

Purpose: Runs the HDFS filesystem contract against `ViewDistributedFileSystem`, with mount-table setup that maps `/user` and fallback to the underlying MiniDFSCluster.

Important APIs and types: `TestHDFSFileSystemContract`, `MiniDFSCluster`, `FileSystemContractBaseTest.TEST_UMASK`, `ConfigUtil.addLink`, `ConfigUtil.addLinkFallback`, `ViewDistributedFileSystem`, `UserGroupInformation`, and `LambdaTestUtils.intercept`.

Control flow: Static `init` creates a randomized-base MiniDFSCluster with two datanodes and records the expected default working directory. `setUp` installs `fs.hdfs.impl` as ViewDFS, extracts the default HDFS URI from config, maps `/user` to that URI, adds fallback, and opens `fs`. `getDefaultWorkingDirectory` returns the recorded `/user/<shortname>`. `testRenameRootDirForbidden` delegates to the superclass root rename test but expects `AccessControlException` because ViewFS internal directories are read-only.

State and persistence behavior: Contract tests mutate HDFS namespace through the ViewDFS wrapper. The mount table is in-memory configuration. Static cluster persists for the class and shuts down in `@AfterAll`.

Dependencies and integration points: Integrates HDFS contract tests, ViewDFS mount-table routing, default working-directory semantics, permissions umask, and special ViewFS internal-dir protection.

Risks and test signals: Most behavior is inherited, so failures can arise from superclass assumptions about root handling. Passing signals ViewDFS satisfies HDFS contract expectations except for intentionally forbidden root internal-dir rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemWithMountLinks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemWithMountLinks.java

Purpose: Extends ViewFS overload-scheme tests with HDFS-scheme `ViewDistributedFileSystem` and explicit mount-link/fallback rename scenarios.

Important APIs and types: `TestViewFileSystemOverloadSchemeWithHdfsScheme`, `ViewDistributedFileSystem`, `ConfigUtil.addLinkFallback`, `ViewFsTestSetup.addMountLinksToConf`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, `DistributedFileSystem.initialize`, and `FileSystem.rename`.

Control flow: `setUp` calls the superclass setup, forces delegation tokens, short IPC retry count, HDFS implementation to ViewDFS, default ignore-port setting, and fallback link for the default HDFS authority. It reuses superclass helpers for create-on-root and nonexistent-link tests. `testRenameOnInternalDirWithFallback` creates mount links and matching fallback directories, then verifies renames among root fallback paths, internal mount parents, and mount targets. `testRenameWhenDstOnInternalDirWithFallback` validates successful destination handling when fallback structure exists and a false result when an internal destination has no corresponding fallback directory.

State and persistence behavior: Mount-link config is in memory; target directories and files are created in the MiniDFSCluster namespace. `verifyRename` checks source removal and destination existence.

Dependencies and integration points: Integrates viewfs mount-table resolution, fallback routing, HDFS-scheme overloading, delegation-token behavior, and rename implementation across internal dirs and real DFS paths.

Risks and test signals: Rename expectations depend on fallback namespace mirroring internal mount structure. Passing signals ViewDFS correctly falls back for root/internal-dir renames and fails cleanly when fallback cannot resolve the destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestViewDistributedFileSystemWithMountLinks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteBlockGetsBlockLengthHint.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteBlockGetsBlockLengthHint.java

Purpose: Regression test ensuring DFSClient propagates the intended block length hint through the DataTransferProtocol path to the DataNode dataset layer when creating RBW replicas.

Important APIs and types: `DFSTestUtil.createFile`, `SimulatedFSDataset`, `FsDatasetSpi.Factory`, `DataNode`, `DataStorage`, `ExtendedBlock`, `ReplicaHandler`, `StorageType`, and overridden `createRbw`.

Control flow: `blockLengthHintIsPropagated` installs custom `FsDatasetChecker` as the datanode dataset factory, sets default block length to 1024, disables volume scanner, starts one datanode, and creates a file with expected block length 2048. `FsDatasetChecker.createRbw` asserts the local block byte count equals `EXPECTED_BLOCK_LENGTH` before delegating to `SimulatedFSDataset`.

State and persistence behavior: The custom simulated dataset sees block creation state only during test execution. Assertion failure occurs at RBW creation time, before normal file completion can hide the incorrect hint.

Dependencies and integration points: Integrates DFSOutputStream, BlockReceiver/DataTransferProtocol, DataNode FsDataset factory configuration, simulated storage, and block metadata.

Risks and test signals: The test relies on the dataset override being used by the MiniDFSCluster and on `createFile` exercising RBW creation. Passing signals the block-length hint survives client-to-datanode plumbing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteBlockGetsBlockLengthHint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteConfigurationToDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteConfigurationToDFS.java

Purpose: Regression test for HDFS-1542, a deadlock between `Configuration.writeXml` holding the configuration monitor and `DFSOutputStream.DataStreamer` writing to DFS.

Important APIs and types: `Configuration.writeXml`, `MiniDFSCluster`, `FileSystem.create`, `OutputStream`, `IOUtils.cleanupWithLogger`, and JUnit `@Timeout`.

Control flow: `testWriteConf` creates a configuration with small 4096 block size, starts a one-datanode cluster, creates `/testWriteConf.xml`, stores a large `foobar` property around 500 KB, writes the configuration XML directly to an HDFS output stream, closes the stream and filesystem, and always cleans up resources in `finally`.

State and persistence behavior: The HDFS file `/testWriteConf.xml` contains serialized configuration XML only for the lifetime of the MiniDFSCluster. The main observable state is absence of timeout/deadlock rather than file contents.

Dependencies and integration points: Integrates Hadoop `Configuration` serialization, DFS client output stream, DataStreamer thread behavior, block creation, and close semantics.

Risks and test signals: The 60-second timeout is the primary failure detector. Passing signals writing large synchronized configuration XML to DFS no longer deadlocks with the DataStreamer path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteConfigurationToDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteRead.java

Purpose: Stress-style tests for reading files while they are still being written, covering sequential reads, positional reads, reads of the current block, hflush visibility, close visibility, and a command-line mode for real clusters.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `FileContext`, `FSDataOutputStream.hflush`, `HdfsDataInputStream.getVisibleLength`, `FSDataInputStream.read`, positional `read(position, ...)`, `FileStatus.getLen`, and `CreateFlag`.

Control flow: `@BeforeEach` starts a three-datanode cluster with 100 KB block size and creates `/tmp`. Tests configure sequential or positional read options and call `testWriteAndRead`. The helper opens a file for create/append/truncate, writes repeated chunks, hflushes every other iteration, then reads back only the visible length from either the beginning or a block-internal position. After final close it verifies readers see all bytes and NameNode length matches. Helper methods support both `FileSystem` and `FileContext` paths. `main` parses options and runs against an existing cluster.

State and persistence behavior: The key state is visible length versus bytes written but not hflushed. HDFS namespace length is checked after close. Command-line options mutate instance fields for alternate runs.

Dependencies and integration points: Integrates DFS write pipeline, hflush semantics, visible length reporting, read APIs, append/truncate behavior, FileContext compatibility, and NameNode length metadata.

Risks and test signals: This is timing/load heavy (`350` write-read loops in unit tests) and verbose logging can be large. Passing signals readers never observe less than the expected visible data and never more than total written data while a file is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteReadStripedFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteReadStripedFile.java

Purpose: Broad tests for writing, reading, seeking, preading, WebHDFS reading, and concat behavior for erasure-coded striped files.

Important APIs and types: `DistributedFileSystem.enableErasureCodingPolicy`, `setErasureCodingPolicy`, `StripedFileTestUtil.verifyPread`, `verifyStatefulRead`, `verifySeek`, `waitBlockGroupsReported`, `WebHdfsTestUtil.getWebHdfsFileSystem`, `fs.concat`, `RemoteException`, and RS-3-2 `ErasureCodingPolicy`.

Control flow: Setup starts a cluster with `dataBlocks + parityBlocks` datanodes, enables RS-3-2 EC, creates `/ec`, and sets EC policy. Many test methods call `testOneFileUsingDFSStripedInputStream` for file lengths around boundaries: empty, under one cell, one cell, under/equal/over stripe, under/equal/over block group, and multiple groups, with and without one datanode shutdown. The helper writes deterministic bytes, waits for block groups, validates length, optionally stops a datanode serving the first block, then verifies positional/stateful reads with byte arrays and `ByteBuffer`. WebHDFS is tested for a multi-block-group length. Concat tests merge EC files and reject concat with different EC policy.

State and persistence behavior: EC files and block groups are created in `/ec`; datanode shutdown simulates degraded reads. Concat mutates target namespace/file contents.

Dependencies and integration points: Integrates striped output/input streams, block placement, degraded reads, WebHDFS, concat policy validation, and EC test utilities.

Risks and test signals: Slow and boundary-heavy; degraded read chooses datanode index 1. Passing signals EC striped files are readable across key length boundaries, after a datanode loss, through WebHDFS, and after valid concat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteReadStripedFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteStripedFileWithFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteStripedFileWithFailure.java

Purpose: Disabled stress/regression test scaffold for writing erasure-coded striped files while shutting down data and parity datanodes mid-write.

Important APIs and types: `DFSStripedOutputStream`, `StripedFileTestUtil.randomArray`, `killDatanode`, `verifyLength`, `verifySeek`, `verifyStatefulRead`, `verifyPread`, `FSDataOutputStream`, and JUnit `@Disabled`.

Control flow: `testWriteStripedFileWithDNFailure` is disabled pending HDFS-8704/HDFS-9040. If enabled, it iterates small and large file lengths, all data-node failure counts from 1 to parity count, and parity-node failure counts such that total failures stay within parity capacity. For each combination it manually calls `setup`, writes one byte at a time, kills selected datanodes at halfway through the file, closes output, verifies the number of live datanodes decreased, validates read/seek/pread, deletes the file, and tears down the cluster.

State and persistence behavior: The test uses manual cluster lifecycle rather than `@BeforeEach/@AfterEach`; HDFS state is per combination. Mid-write state includes a wrapped `DFSStripedOutputStream`, an atomic position counter, and killed DataNodes.

Dependencies and integration points: Integrates striped output failure handling, datanode shutdown during writes, EC parity tolerance, read-after-failure verification, and cluster lifecycle utilities.

Risks and test signals: Because it is disabled, it provides no normal CI signal. If re-enabled, it is expensive and failure-injection heavy. Passing would signal striped writes can tolerate bounded data/parity datanode failures during write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteStripedFileWithFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/UpgradeUtilities.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/UpgradeUtilities.java

Purpose: Static helper library for HDFS upgrade tests. It creates canonical populated NameNode/DataNode storage directories, copies them into test layouts, computes checksums, writes VERSION files, corrupts files, and exposes current layout/namespace/cluster/block-pool identifiers.

Important APIs and types: `MiniDFSCluster`, `DFSTestUtil.formatNameNode`, `NamenodeProtocols.versionRequest`, `Storage`, `StorageDirectory`, `NNStorage`, `DataStorage`, `BlockPoolSliceStorage`, `StorageInfo`, `DataNodeLayoutVersion`, `LayoutVersion.Feature.FEDERATION`, `CRC32`, and `FileUtil`.

Control flow: `initialize` wipes the test root, formats NameNode/DataNode storage, starts a cluster without managing dirs, records namespace/cluster/block-pool IDs and cTime, writes files before and after `saveNamespace`, shuts down, removes lock files, and computes master checksums for NameNode, DataNode, block pool, finalized, and rbw dirs. Other helpers build name/data dir config strings, create empty dirs, copy master NameNode/DataNode/block-pool storage into requested parents, create NameNode/DataNode/block-pool VERSION files, corrupt a target byte sequence in a file, report current layout/IDs from a running cluster or cached master, and create empty block-pool dirs.

State and persistence behavior: Maintains static master directories under `MiniDFSCluster.getBaseDirectory()` and cached checksums/IDs. It deliberately mutates local filesystem storage layouts and VERSION properties for upgrade tests.

Dependencies and integration points: Integrates local filesystem copying, HDFS storage layout internals, NameNode saveNamespace, DataNode block-pool storage, version files, and upgrade test setup.

Risks and test signals: `createDataNodeStorageDirs` appears to alter the master datanode VERSION storage UUID after copying rather than the copied directory, so callers should inspect expected UUID behavior. The utility is foundational: incorrect cleanup, checksum exclusions, or VERSION generation can invalidate many upgrade tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/UpgradeUtilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/BlockReaderTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/BlockReaderTestUtil.java

Purpose: Test utility for block-reader tests. It builds MiniDFSClusters, writes random files, fetches located blocks, constructs `BlockReader` instances directly, resolves serving DataNodes, and enables trace logging for block-reader/cache components.

Important APIs and types: `MiniDFSCluster`, `DFSClient`, `BlockReaderFactory`, `RemotePeerFactory`, `Peer`, `ClientContext`, `CachingStrategy`, `LocatedBlock`, `ExtendedBlock`, `DatanodeInfo`, `Token<BlockTokenIdentifier>`, `ShortCircuitCache`, and trace helpers.

Control flow: Constructors create or wrap a MiniDFSCluster. `writeFile` writes `sizeKB` random data and returns the bytes. `getFileBlocks` calls NameNode `getBlockLocations`. `getDFSClient` connects to localhost NameNode port. `readAndCheckEOS` reads a requested length through a `BlockReader` and optionally checks EOF. Static `getBlockReader` selects the first datanode, builds a `BlockReaderFactory` with block token, offset, length, checksum verification, client cache context, short-circuit enabled, and a `RemotePeerFactory` that opens a socket and wraps it as a peer. `getDataNode` maps located-block IPC port to cluster datanode.

State and persistence behavior: Owns a cluster/config pair and caller-managed shutdown. Generated files persist in the MiniDFSCluster until test cleanup.

Dependencies and integration points: Integrates low-level block read factory setup with NameNode block locations, datanode network peers, short-circuit cache context, and logging controls.

Risks and test signals: Directly creates sockets and assumes the first located block location is usable. Utility correctness is critical for block-reader tests because it bypasses normal high-level `DFSInputStream` setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/BlockReaderTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderFactory.java

Purpose: Integration and concurrency tests for `BlockReaderFactory`, UNIX domain socket fallback, short-circuit read cache behavior, shared-memory compatibility, cache shutdown, and purging interrupted replicas.

Important APIs and types: `BlockReaderFactory`, `ShortCircuitCache`, `ShortCircuitReplicaInfo`, `DomainSocketFactory`, `TemporarySocketDirectory`, `DFSInputStream.tcpReadsDisabledForTesting`, `BlockReaderTestUtil.getBlockReader`, `DfsClientConf.ShortCircuitConf`, `DfsClientShmManager.Visitor`, `SubjectInheritingThread`, `CountDownLatch`, `Semaphore`, and domain-socket config keys.

Control flow: `init` disables domain socket bind-path validation and skips if native domain sockets are unavailable; `cleanup` restores static test hooks. `createShortCircuitConf` builds a short-circuit/domain-socket config. Tests cover fallback from failed short-circuit to UNIX domain traffic, unresolved-host rejection, single cache load shared by many waiters, temporary short-circuit failure not being cached, unbuffer behavior with/without domain socket disable interval, server/client shared-memory mismatch fallback, cache shutdown closing watcher, and purging replicas whose channels were closed by interrupt before future reads use them.

State and persistence behavior: Several tests mutate static hooks (`tcpReadsDisabledForTesting`, `createShortCircuitReplicaInfoCallback`) and short-circuit cache contents. Temporary socket directories and MiniDFSClusters are per test and must be closed. Cache maps and shm manager visitor output are inspected as state.

Dependencies and integration points: Integrates client short-circuit local reads, UNIX domain sockets, fallback to TCP/domain traffic, cache concurrency, datanode shared memory, interrupt handling, and DFS file reads.

Risks and test signals: Heavy concurrency and static hooks make cleanup essential. Passing signals cache load serialization, retry behavior, fallback paths, and replica purge semantics are robust under failure and interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderIoProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderIoProvider.java

Purpose: Unit test for short-circuit read latency profiling in `BlockReaderIoProvider`.

Important APIs and types: `BlockReaderIoProvider`, `BlockReaderLocalMetrics`, `DfsClientConf`, `HdfsClientConfigKeys.Read.ShortCircuit.METRICS_SAMPLING_PERCENTAGE_KEY`, `FakeTimer`, Mockito `FileChannel`, and `ByteBuffer`.

Control flow: `testSlowShortCircuitReadsIsRecorded` configures 100 percent metrics sampling, mocks `BlockReaderLocalMetrics`, and mocks `FileChannel.read(ByteBuffer,long)` so it advances the fake timer by the slow-read threshold and returns 0. It then constructs `BlockReaderIoProvider`, calls `read`, and verifies `metrics.addShortCircuitReadLatency` was invoked once.

State and persistence behavior: State is limited to the static `FakeTimer`, mocked metrics call count, and mocked file-channel behavior. No filesystem or cluster state is involved.

Dependencies and integration points: Integrates DfsClient short-circuit config, the latency measurement wrapper, timer abstraction, and metrics emission.

Risks and test signals: The call passes Mockito matchers as arguments to the method under test, which works here because the mocked `FileChannel` accepts broad matchers, but it is unusual and tied to Mockito behavior. Passing signals slow sampled short-circuit reads are recorded in metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderIoProvider.java -->
