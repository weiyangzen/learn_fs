# subset-b-007523 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientRetries.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientRetries.java

Purpose: This JUnit 5 class exercises DFSClient retry behavior across read, write, lease-renewal, checksum, DataNode RPC timeout, NameNode restart, safe mode, and configuration parsing paths. It is mostly MiniDFSCluster-backed integration coverage, with Mockito spies around NamenodeProtocols and DFSClientFaultInjector hooks for precise fault injection.

Important APIs/types/functions: `DFSClient`, `DFSInputStream`, `LeaseRenewer`, `DataStreamer`, `NamenodeProtocols.addBlock/complete/getBlockLocations/renewLease`, `ClientDatanodeProtocol`, `MultipleLinearRandomRetry`, and `HdfsUtils.isHealthy`. Helper types include `TestServer`, `FailNTimesAnswer`, `DFSClientReader`, `Counter`, and `SleepFixedTimeAnswer`.

Control flow: The tests set small retry/socket windows, build clusters or mock RPC endpoints, inject transient failures, then verify success/failure boundaries. `testFailuresArePerOperation` poisons block locations repeatedly to prove failures reset between user-visible reads. `testIdempotentAllocateBlockAndClose` calls real NN methods twice through spies to confirm retried `addBlock` and `complete` remain idempotent. `namenodeRestartTest` drives concurrent reads, writes, creates, NameNode shutdown/restart, and safe-mode leave events while retry policies are enabled.

State and persistence behavior: The class writes real HDFS files, corrupts replicas, restarts NameNodes/DataNodes, mutates lease-renewer state, and verifies persisted file length/checksum after recovery. It also checks that aborted leases are removed, safe-mode and health state affect retryability, and duplicate close/allocation RPCs do not create extra blocks.

Dependencies and integration points: It depends on MiniDFSCluster, WebHDFS test utilities, NameNode RPC protocols, DataNode client protocol proxy creation, Hadoop retry policy parsing, and low-level socket/RPC server behavior. Several tests are regression-style assertions for historical HDFS issues.

Risks and test signals: The strongest signals are exception class/message checks, checksum equality, block-count invariants, lease emptiness, thread exception collection, and timeouts. Risk areas include timing sensitivity, long restart waits, randomized busy-block concurrency, and reliance on Mockito behavior against complex protocol interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientRetries.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientSocketSize.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientSocketSize.java

Purpose: This small integration test verifies how DFS client write-pipeline sockets apply `dfs.client.socket.send.buffer.size`. It checks the default auto-tuned case, an explicit large-versus-small setting, and an explicit zero value.

Important APIs/types/functions: `DataStreamer.createSocketForPipeline`, `DatanodeInfoBuilder`, `DFS_CLIENT_SOCKET_SEND_BUFFER_SIZE_KEY`, `Socket.getSendBufferSize`, `MiniDFSCluster`, and `DFSClient` via the cluster filesystem.

Control flow: Each test delegates to `getSendBufferSize(Configuration)`, which starts a one-DataNode MiniDFSCluster, waits for it to become active, constructs a pipeline socket to that DataNode using the cluster DFS client, returns the OS-observed send buffer size, and shuts down the cluster. Assertions compare positive auto-tuned values or relative configured values.

State and persistence behavior: No HDFS files are persisted. The state under test is socket configuration derived from Hadoop configuration and the kernel/socket implementation. The cluster is temporary and always shut down in a finally block.

Dependencies and integration points: The test directly integrates DFS client pipeline socket creation with DataNode identity metadata. It relies on the OS honoring socket send-buffer hints enough for a larger configured buffer to report larger than a smaller configured buffer.

Risks and test signals: The comments acknowledge `Socket.setSendBufferSize` is only a hint, so platform/kernel differences can make the explicit-size comparison flaky. The useful signal is that default and zero do not force invalid zero-sized buffers and that configured values flow into DataStreamer socket setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientSocketSize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSFinalize.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSFinalize.java

Purpose: This upgrade/finalization integration test validates that NameNode, DataNode, and block-pool finalization remove `previous` directories while preserving valid `current` storage contents.

Important APIs/types/functions: `UpgradeUtilities`, `MiniDFSCluster.Builder`, `StartupOption.REGULAR`, `cluster.finalizeCluster`, `cluster.triggerBlockReports`, `FSImageTestUtil`, `BlockPoolSliceStorage`, and `DataStorage.STORAGE_DIR_FINALIZED`.

Control flow: For one and two storage directories, the test initializes synthetic upgrade storage states. It runs two variants for whole DataNode storage finalization, first with existing `previous` directories and then idempotently without them. It then resets directories and repeats for block-pool-level finalization. After each finalization, it triggers block reports, waits briefly for asynchronous DataNode/block-pool work, and calls `checkResult`.

State and persistence behavior: This file is entirely about on-disk HDFS storage state. `checkResult` validates that NameNode `current` dirs are reasonable and parallel-identical, DataNode current checksums match master data, `previous` dirs are gone, and block-pool finalized content matches expected checksums. Duplicate replica deletion and block scanning are disabled to keep deliberately mirrored test directories unchanged.

Dependencies and integration points: It uses the shared upgrade test harness, HDFS storage directory configuration keys, MiniDFSCluster startup without formatting or managed dirs, and DataNode block reports as the finalization trigger.

Risks and test signals: Signals are filesystem existence checks and checksum comparisons. Timing risk exists in the fixed one-second wait for asynchronous finalization. Because it disables normal scanners and deletion, it tests finalization behavior in a controlled upgrade-fixture environment rather than arbitrary production storage churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSFinalize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStream.java

Purpose: This class verifies DFS inotify event-stream semantics: edit-log opcode coverage, event payload translation, txid ordering, erasure-coded file metadata, HA failover behavior, split-brain active protection, and timed polling.

Important APIs/types/functions: `DFSInotifyEventInputStream`, `EventBatch`, `Event` subtypes (`CreateEvent`, `CloseEvent`, `AppendEvent`, `MetadataUpdateEvent`, `RenameEvent`, `UnlinkEvent`, `TruncateEvent`), `MiniQJMHACluster`, `FSEditLogOpCodes`, `HATestUtil`, and `MissingEventsException`. Helpers `waitForNextEvents` and `checkTxid` enforce event availability and monotonic transaction IDs.

Control flow: `testBasic` creates a QJM HA cluster, performs a sequence of DFSClient namespace operations, and consumes the inotify stream in exact order, asserting event type, path, payload fields, timestamps, overwrite flags, xattr/ACL metadata, and `getTxidsBehindEstimate`. Other tests focus on EC create/close events, failover reading from the new active, a two-active scenario where the old active cannot read edits written by a fenced writer, and `poll(timeout)` unblocking after a scheduled mkdir.

State and persistence behavior: The tests mutate HDFS namespace and edit logs through create, append, close, access-time update, setReplication, concat, delete, mkdir, chmod/chown, symlink, xattr, ACL, rename, truncate, and erasure-coding operations. The stream’s persistent cursor is represented by txids returned in batches; HA tests depend on shared QJM edit-log state.

Dependencies and integration points: It integrates the NameNode edit-log op translator with client inotify APIs and HA/QJM storage. The opcode count assertion intentionally forces updates when edit-log enum size changes.

Risks and test signals: Strong signals are exact event counts/types, txid monotonicity, EC flags, and null poll after catch-up. Risks include brittleness when opcodes are added, busy-wait in `waitForNextEvents`, and HA timing/fencing behavior that depends on MiniQJMHACluster fidelity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStreamKerberized.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStreamKerberized.java

Purpose: This security integration test verifies that `DFSInotifyEventInputStream` continues to work in a Kerberized, HTTPS-only, QJM-backed HA cluster after a short-lived TGT expires and the client relogs from keytab.

Important APIs/types/functions: `MiniKdc`, `MiniQJMHACluster`, `UserGroupInformation`, `SecurityUtil`, `KeyStoreTestUtil`, `DFSInotifyEventInputStream`, `EventBatch`, and the many NameNode/DataNode/JournalNode Kerberos, keytab, SPNEGO, HTTPS, and block-token configuration keys.

Control flow: `initKerberizedCluster` creates a temporary MiniKdc with five-second tickets, keytabs for HDFS and HTTP principals, SSL config, and secure HDFS/QJM configuration. The test builds a remote-edits-only HA cluster, transitions NN0 active, logs in as `hdfs`, creates `/test`, drains any existing inotify events, sleeps past ticket lifetime, explicitly calls `checkTGTAndReloginFromKeytab`, creates `/test1`, and asserts one new event is pollable. `shutdownCluster` tears down cluster, KDC, temp dirs, and SSL config.

State and persistence behavior: The test mutates local keytab/keystore files, Hadoop global UGI security state, RPC connection-idle settings, and HDFS namespace/edit-log state. It deliberately avoids RPC connection reuse to force authentication paths after TGT expiration.

Dependencies and integration points: It spans Kerberos login renewal, HTTPS/SPNEGO server setup, QJM edit-log URL reading, block access tokens, and inotify polling. Remote-only edits are forced to exercise URL log behavior rather than local edit files.

Risks and test signals: The main signal is successful event polling after ticket expiry and relogin. Risks include global UGI side effects, platform principal naming differences (`localhost` versus `127.0.0.1` on Windows), timing sensitivity around five-second tickets, and cleanup requirements for generated SSL/KDC artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStreamKerberized.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStream.java

Purpose: This class tests DFSInputStream read-side behavior: skip semantics, short-circuit local reads, selecting a new source DataNode, open-info length accounting, NULL checksum behavior across DataNode restart, cached replica preference, and invalid block-token retry during block-reader creation.

Important APIs/types/functions: `DFSInputStream`, `DistributedFileSystem`, `DFSClient`, `DomainSocket`, `TemporarySocketDirectory`, `DfsClientConf`, `LocatedBlock`, `DatanodeInfoWithStorage`, `DFSClientFaultInjector`, and `InvalidBlockTokenException`.

Control flow: `testSkipInner` creates a deterministic 4 MiB file and repeatedly skips random distances, validating the next byte. Remote and local-block-reader tests delegate to it, with local reads enabling short-circuit sockets and temporarily disabling TCP reads for testing. Other tests open a file and check `seekToNewSource`, configure last-block-length retries to zero, restart a DataNode while writing with NULL checksum, mock located-block cached/non-cached locations, and inject one invalid token exception before a successful read.

State and persistence behavior: Tests write actual HDFS files, flush under-construction data, restart a DataNode, inspect live DataNode descriptors, and temporarily mutate `DFSInputStream.tcpReadsDisabledForTesting` and `DFSClientFaultInjector`. The invalid-token test keeps an under-construction block open while reading from offset 1024.

Dependencies and integration points: It integrates short-circuit domain sockets, DataNode block loading after restart, NameNode block-location metadata, DFS client read-priority configuration, and token-refresh retry logic in block-reader construction.

Risks and test signals: Signals include byte-accurate reads after skip, different current datanode after source switch, expected file length/last-block state, live DataNode count after restart, selected DataNode identity, and successful read after injected token failure. Risks include domain-socket platform assumptions, sleeps for block loading, and global fault-injector cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStreamBlockLocations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStreamBlockLocations.java

Purpose: This parameterized test verifies DFSInputStream located-block cache refresh and deferred registration with the client-side located-block refresher, with expiration enabled and disabled.

Important APIs/types/functions: `DFSInputStream.refreshBlockLocations`, `getLastRefreshedBlocksAtForTesting`, `addToLocalDeadNodes`, `getLocalDeadNodes`, `chooseDataNode`, `DFSClient.getLocatedBlockRefresher`, and configuration keys for stale DataNodes, short-circuit reads, replication, prefetch size, and `DFS_CLIENT_REFRESH_READ_BLOCK_LOCATIONS_MS_KEY`.

Control flow: Each test initializes a seven-DataNode rack-aware cluster with four replicas, a 24-block file, and optional block-location expiration. `testRefreshBlockLocations` first proves no refresh occurs without a trigger, then fakes a local dead node and unresolved address cache to force refresh and validates changed located-block state. Deferred-registration tests open a stream, invoke a read/readFully/getAllBlocks before and after artificially aging `lastRefreshedBlocksAt`, and assert tracking only occurs when expiration is enabled. `testClearIgnoreListChooseDataNode` passes all replica locations in an ignore list and expects the list to be cleared so retry selection can proceed.

State and persistence behavior: The test creates large replicated files, mutates DFSInputStream internal dead-node and refresh timestamps through testing hooks, and checks registration state in the client refresher. Cleanup closes client/filesystem and deletes files on exit.

Dependencies and integration points: It connects NameNode stale-node avoidance, rack-aware block placement, client prefetching, located-block refresher registration, and hedged-read DataNode selection behavior.

Risks and test signals: Signals are object identity changes for `locatedBlocks`, timestamp advancement, dead-node clearing, refresher tracking state, and ignore-list size. Risks include heavy cluster/file setup and reliance on testing-only mutators and timing thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStreamBlockLocations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSMkdirs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSMkdirs.java

Purpose: This class tests HDFS directory creation behavior for recursive `mkdirs`, single-level `mkdir`, and NameNode RPC rejection of non-canonical paths.

Important APIs/types/functions: `FileSystem.mkdirs`, `DistributedFileSystem.mkdir`, `NamenodeProtocols.mkdirs`, `ParentNotDirectoryException`, `FileNotFoundException`, `InvalidPathException`, `FsPermission`, `MiniDFSCluster`, and `DFSTestUtil.writeFile`.

Control flow: `testDFSMkdirs` creates `/test/mkdirs`, confirms idempotent `mkdirs`, writes a file below it, and verifies `mkdirs` fails when asked to create a subdirectory under that file. `testMkdir` uses the non-recursive DFS API: root-level creation succeeds, a parent that is a file yields `ParentNotDirectoryException`, and a missing parent yields `FileNotFoundException`. `testMkdirRpcNonCanonicalPath` starts a NameNode-only cluster and directly calls NN RPC with paths containing duplicate slashes, `..`, or `.` components, expecting `InvalidPathException`.

State and persistence behavior: The tests create and delete real namespace entries but no meaningful block data except a small file used as a non-directory parent. Clusters are temporary and shut down after each test.

Dependencies and integration points: Coverage spans the public FileSystem API, DFS-specific `mkdir`, and low-level NamenodeProtocols validation, ensuring client-side canonicalization is not the only defense.

Risks and test signals: The signal is exception specificity and final path existence. Risk is low, but path-normalization behavior is easy to break if validation moves between client and server layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSMkdirs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSOutputStream.java

Purpose: This class validates write-stream internals: close exception clearing, packet/chunk sizing, overflow prevention, congestion backoff, `NO_LOCAL_WRITE`, lease closure/recovery, hflush/hsync capability, and first-packet sizing across block boundaries.

Important APIs/types/functions: `DFSOutputStream`, `DataStreamer`, `DFSPacket`, `PacketReceiver.MAX_PACKET_SIZE`, `PacketHeader.PKT_MAX_HEADER_LEN`, `DfsClientConf`, `LastExceptionInStreamer`, `BlockManager`, `DatanodeManager`, `BlockListAsLongs`, `RECOVER_LEASE_ON_CLOSE_EXCEPTION_KEY`, and Whitebox/reflection access to internal fields/methods.

Control flow: The shared cluster is created once. Reflection tests invoke private `computePacketChunkSize` and `adjustChunkBoundary`, then inspect `packetSize`, `writePacketSize`, and `chunksPerPacket`. Congestion tests construct mocked DataStreamer instances with manipulated queues and congested-node lists. Placement and lease tests use a real cluster: `NO_LOCAL_WRITE` spies DataNodeManager local-host resolution, close-thread behavior verifies `endFileLease`, recover-on-close toggles lease recovery when `completeFile` throws, and hflush/hsync plus repeated block-sized writes verify stream capabilities and packet sizing.

State and persistence behavior: Tests write real HDFS files, inspect NameNode block reports, mutate BlockManager internals temporarily, and recover or leave leases depending on configuration. Mock-based tests mutate DataStreamer queues and internal stage state.

Dependencies and integration points: It spans DFSClient create paths, block placement, packet serialization sizing, streamer response/backoff logic, NameNode lease state, filesystem stream capability reporting, and cluster block-report inspection.

Risks and test signals: Strong signals include internal field equality, no repeated close exception, congested-list clearing/progress, exactly one DataNode without data for `NO_LOCAL_WRITE`, lease recovery state, file-closed polling, and packet-size invariants. Risks include brittle reflection/Whitebox access, concurrent mock timing, and shared-cluster cross-test state if cleanup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSPermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSPermission.java

Purpose: This extensive permission test validates HDFS POSIX-style permission setting, ownership changes, access checks, trash protection, denial messages, and operation-specific permission requirements for owner, group, other, and superuser identities.

Important APIs/types/functions: `FsPermission`, `FsAction`, `FileSystem.access`, `setPermission`, `setOwner`, `Trash`, `UserGroupInformation`, `DFSTestUtil.login/updateConfWithFakeGroupMapping`, `AccessControlException`, `PermissionGenerator`, `PermissionVerifier`, and verifier subclasses for create, open, replication, times, stats, list, rename, and delete.

Control flow: Static setup enables permissions, installs fake user-group mappings, and creates test UGIs. Each test starts a three-DataNode MiniDFSCluster. `testPermissionSetting` iterates randomized umasks and verifies create/mkdir permissions. `testOwnership` checks superuser and owner/group constraints. `testPermissionChecking` builds many ancestor/parent/file/dir combinations with randomized modes, then runs the same operation matrix as USER1, USER2, USER3, and SUPERUSER. Access tests verify owner/group/other masks and exception messages. Trash and non-directory ancestor tests check denial cause/message quality and information hiding.

State and persistence behavior: The tests create real HDFS namespace trees, files, ownership, permissions, trash roots, and per-user FileSystem instances. The permission matrix repeatedly mutates inode modes and ownership while verifier classes compute expected required masks from identity role and operation type.

Dependencies and integration points: It covers NameNode permission enforcement, FileSystem client APIs, fake group mapping, Trash move semantics, content-summary/list/stat paths, and recursive delete semantics for non-empty directories.

Risks and test signals: Signals include exact mode values, owner/group equality, expected allow/deny outcomes, non-AccessControlException for nonexistent files, and denial messages containing or hiding user/path details as appropriate. Risks include randomized coverage size, shared static configuration mutation, and high runtime from the operation matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRemove.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRemove.java

Purpose: This integration test checks that deleting files releases DataNode disk usage after block deletion has propagated.

Important APIs/types/functions: `MiniDFSCluster`, `FileSystem.delete`, `DataNodeTestUtils.getFSDataset`, `FsDatasetSpi.getDfsUsed`, and helper methods `createFile` and `getTotalDfsUsed`.

Control flow: The test starts a two-DataNode cluster, creates `/test/remove/`, records aggregate DFS used, creates 100 small files, records peak usage, deletes all files non-recursively, sleeps for three default heartbeat intervals to allow block deletion, then asserts final aggregate usage equals the starting value.

State and persistence behavior: It writes and deletes real block files on DataNode storage. The observed state is physical dataset usage across all DataNodes, not only NameNode namespace state.

Dependencies and integration points: It depends on DataNode storage accounting, block invalidation/deletion after namespace delete, and heartbeat-driven cleanup timing.

Risks and test signals: The main signal is equality of aggregate DataNode DFS-used before and after the create/delete cycle. The test is timing-sensitive because it uses a fixed sleep based on heartbeat interval rather than an explicit wait-for-condition loop. Small-file metadata or storage accounting changes could affect exact equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRemove.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRename.java

Purpose: This class tests rename semantics, lease preservation, overwrite cleanup, NameNode restart persistence, and audit logging of multiple rename options.

Important APIs/types/functions: `FileSystem.rename`, `DistributedFileSystem.rename(Path, Path, Rename...)`, `NameNodeAdapter.getLeaseManager`, `NameNodeAdapter.getBlockLocations`, `BlockManager`, `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty`, `LocatedBlocks`, `FSNamesystem.AUDIT_LOG`, and rename options `OVERWRITE` and `TO_TRASH`.

Control flow: `testRename` creates files/directories and verifies open-file lease count survives unrelated rename, invalid destination cases fail, prefix-similar paths can rename, and same-path/trailing-slash cases follow expected return values. `testRenameWithOverwrite` creates source and destination files, captures destination blocks, renames source over destination, waits for marked-delete queue drainage, verifies old destination blocks are removed from BlockManager, restarts NameNodes, and confirms source absence/destination presence. `testRename2Options` captures audit logs and verifies both rename flags reach the NameNode.

State and persistence behavior: Tests mutate namespace entries, active leases, block maps, delete queues, audit logs, and restart-persisted metadata. The overwrite test explicitly validates that storage/block-manager state for overwritten destination blocks is cleaned.

Dependencies and integration points: It integrates FileSystem API rename behavior, lease manager state, block manager deletion, NameNode restart loading, and audit logging.

Risks and test signals: Signals are boolean rename results, lease counts, block-map absence, post-restart namespace checks, and audit-log contents. Risks include audit string brittleness and timing around block deletion queue drainage, though the latter uses a test utility wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRollback.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRollback.java

Purpose: This upgrade test validates NameNode, DataNode, and block-pool rollback success and failure behavior across valid storage snapshots, missing snapshots, incompatible layout versions, newer federation state times, missing edits/images, and corrupt VERSION files.

Important APIs/types/functions: `UpgradeUtilities`, `NameNode.doRollback`, `MiniDFSCluster.Builder`, `StartupOption.ROLLBACK/UPGRADE`, `StorageInfo`, `DataNodeLayoutVersion`, `FSImageTestUtil`, `BlockPoolSliceStorage` via utility-created dirs, and helper methods `checkResult`, `startNameNodeShouldFail`, `startBlockPoolShouldFail`, and `deleteMatchingFiles`.

Control flow: For one and two storage dirs, the test repeatedly constructs synthetic `current` and `previous` states. It runs normal NameNode rollback, normal DataNode rollback, and block-pool rollback with a deliberately newer current layout. It then checks failure cases: no previous dir, future layout version in previous, newer fsscTime, missing edits, missing image, corrupt VERSION layoutVersion, and too-old layout version. Expected failures are validated by exception message substrings or dead block-pool service state.

State and persistence behavior: The file directly manipulates on-disk NameNode/DataNode storage directories, VERSION files, fsimage/edits files, namespace IDs, cluster IDs, block-pool IDs, and layout/fsscTime metadata. Successful rollback must promote `previous` to `current`, remove `previous`, and preserve parallel-identical/current checksummed contents.

Dependencies and integration points: It depends on the upgrade utility fixture, NameNode rollback code, DataNode block-pool service startup, layout-version compatibility checks, and MiniDFSCluster unmanaged-dir startup.

Risks and test signals: Signals include checksum comparisons, `previous` directory removal, NameNode failure message substrings, and `isBPServiceAlive` false for bad block-pool rollback. Risks include brittle failure-message matching, many storage-state mutations in one long test, and assumptions about utility master checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRollback.java -->
