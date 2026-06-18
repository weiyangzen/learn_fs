# subset-b-007550 Research

Grouped research for the listed Hadoop HDFS NameNode test files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLog.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLog.java

## Purpose
`TestEditLog` is the broad regression suite for NameNode edit-log write, roll, read, recovery, and compatibility behavior. It is parameterized over synchronous and asynchronous edit logging, so most scenarios are exercised against both the classic `FSEditLog` path and the async edit-log implementation. The class verifies pre-transaction-id log compatibility, multi-threaded edit generation, sync batching semantics, checksum enforcement, crash recovery from in-progress segments, manifest construction across journals, failover between redundant edit directories, fuzz tolerance, active in-progress reads, and layout-version behavior when erasure coding is not supported.

## Important APIs, Types, And Functions
The suite drives `FSEditLog`, `FSImage`, `FSEditLogLoader`, `EditLogFileInputStream`, `EditLogFileOutputStream`, `NNStorage`, `StorageDirectory`, `MiniDFSCluster`, `FSNamesystem`, and `DistributedFileSystem`. The helper `Transactions` writes paired open/close file operations and syncs them. `GarbageMkdirOp` is a deliberately malformed edit operation used to exercise scan failure paths. `EditLogByteInputStream` adapts an in-memory byte array to the `EditLogInputStream` API for legacy log loading tests. `setupEdits`, `AbortSpec`, `readAllEdits`, and `mockStorageWithEdits` build synthetic journal layouts for manifest and failover validation.

## Control Flow
Most tests create a `MiniDFSCluster`, perform NameNode metadata operations or direct edit-log calls, roll or close edit segments, then reopen the same storage through loaders or a restarted cluster. `testSimpleEditLog` verifies begin/end transaction placement around a roll. `testMultiThreadedEditLog` starts 100 transaction threads, rolls the log, then reloads the finalized segment to confirm transaction count and lease cleanup. `testSyncBatching` uses two single-thread executors to show that one `logSync` can durably cover edits from multiple threads and increments `TransactionsBatchedInSync`. `testBatchedSyncWithClosedLogs` covers the legal sequence where `logSyncAll` and close happen before a thread calls its own `logSync`.

## State And Persistence Behavior
The file inspects actual storage filenames such as finalized `edits_start-end`, in-progress `edits_inprogress_txid`, image files, and `seen_txid` side effects. Crash tests copy live storage aside before shutdown, restore it, and verify that startup recovers edits and optionally checkpoints if the uncheckpointed transaction count exceeds `CHECKPOINT_ON_STARTUP_MIN_TXNS`. Empty-log crash tests simulate a segment header without `START_LOG_SEGMENT` and vary whether `seen_txid` was updated, proving when startup should tolerate or reject a transaction gap. Checksum tests corrupt the last checksum bytes and expect startup or scan failures rather than silent replay.

## Dependencies And Integration Points
The suite integrates with local storage directories, `LocalFileSystem` permission checks, NameNode metrics, ACL propagation, inotify reads, `ExitUtil` interception, and HDFS layout-version feature gates. It uses `FSImageTestUtil` to build standalone edit logs and mock storage directories. The failover tests rely on redundant edit directories selecting a complete non-corrupt stream when another segment is missing or corrupt. The EC compatibility test sets an older log version lacking `ERASURE_CODING` support, writes add-block edits, and verifies replay still works.

## Risks And Test Signals
The highest-risk behaviors are transaction ordering, gaps between segments, async-vs-sync semantic differences, and recovery decisions that can either lose metadata or falsely block startup. Test signals include exact transaction counts, expected file names, storage-dir existence checks, thrown `ChecksumException` or gap `IOException`, metrics counters, absence of unexpected JVM exits, and successful cluster restart. Several tests are timing- or volume-sensitive (`testFuzzSequences`, `testManyEditLogSegments`, active-log reads) and can expose flakiness if filesystem latency or async queues behave differently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogAutoroll.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogAutoroll.java

## Purpose
`TestEditLogAutoroll` verifies automatic NameNode edit-log rolling in an HA topology. It is parameterized for synchronous and asynchronous edit logging and focuses on the active NameNode's `NameNodeEditLogRoller` behavior when transaction thresholds or forced-roll time windows are reached.

## Important APIs, Types, And Functions
The class configures `DFS_NAMENODE_CHECKPOINT_TXNS_KEY`, `DFS_NAMENODE_EDIT_LOG_AUTOROLL_MULTIPLIER_THRESHOLD`, `DFS_NAMENODE_EDIT_LOG_AUTOROLL_CHECK_INTERVAL_MS`, and `DFS_NAMENODE_EDIT_LOG_AUTOROLL_MAX_INTERVAL_MS`. It uses `MiniDFSNNTopology`, `MiniDFSCluster`, `HATestUtil.configureFailoverFs`, `NameNode`, `FSNamesystem`, `FSEditLog`, and `GenericTestUtils.waitFor`. The shared state is the active `NameNode`, its `FileSystem`, and the current edit-log segment transaction id.

## Control Flow
`setUp` builds a two-NameNode nameservice, retries random HTTP base ports on `BindException`, transitions the first NameNode to active, and captures the active edit log. `testEditLogAutoroll` writes 11 mkdir edits after configuring a threshold that should roll after 10 edits, waits until `getCurSegmentTxId` advances, transitions the NameNode to standby, and asserts the roller thread is gone. `testForceRoll` manually rolls once, writes another edit, moves `lastRollTime` far into the past, waits for an autoroll, then verifies a second forced check does not roll an empty segment.

## State And Persistence Behavior
The test observes persisted edit-log segment boundaries indirectly through `FSEditLog.getCurSegmentTxId`. It also validates lifecycle state: the autoroller is expected to run only while the NameNode is active and stop after standby transition. The forced-roll test protects against creating empty or redundant edit segments when the roller sees an expired last-roll timestamp but no new transactions.

## Dependencies And Integration Points
This test sits at the intersection of HA state transitions, checkpoint thresholds, the edit-log roller background thread, and edit-log segment accounting. It relies on `MiniDFSCluster` rather than direct mocks because the behavior depends on NameNode state, filesystem operations, and background thread scheduling.

## Risks And Test Signals
The main risks are missed autorolls causing unbounded active segments, autoroller threads surviving standby transition, and forced rolling producing empty segments. Test signals are segment txid advancement, absence of matching roller threads, and stable txid after a no-op forced roll. Timing is controlled with short check intervals but still depends on scheduler progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogAutoroll.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileInputStream.java

## Purpose
`TestEditLogFileInputStream` covers edit-log input streams backed by HTTP URLs, protobuf `ByteString` values, and local files. It targets read completeness, length detection, operation checksum validation, and handling of files filled by failed preallocation.

## Important APIs, Types, And Functions
The tests use `EditLogFileInputStream.fromUrl`, `EditLogFileInputStream.fromByteString`, `EditLogFileInputStream.scanEditLog`, `EditLogFileOutputStream`, `FSEditLogOp.MkdirOp`, `FSImageTestUtil.countEditLogOpTypes`, `URLConnectionFactory`, mocked `HttpURLConnection`, `ByteString`, and `FSEditLogLoader.EditLogValidation`. `FAKE_LOG_DATA` reuses the legacy Hadoop 0.20 edit sequence from `TestEditLog`.

## Control Flow
`testReadURL` mocks an HTTP connection returning edit-log bytes, status OK, and a `Content-Length`; it reads the stream and checks operation counts and reported length. `testByteStringLog` performs the same validation against an in-memory `ByteString`. `testScanCorruptEditLog` writes two mkdir operations, flushes the log, corrupts the last four checksum bytes, then confirms `scanNextOp` reads the first transaction and fails on the corrupt second transaction. `testScanEditThatFailedDuringPreAllocate` creates a file containing only `0xff` bytes and expects scan validation to classify the header as corrupt and report no end txid.

## State And Persistence Behavior
The file-based tests create real edit-log files and mutate bytes in place with `RandomAccessFile`. They verify that persisted checksums are not advisory: corruption during scan produces an `IOException` and protects replay. The preallocation test models an aborted writer that left trailer bytes only, ensuring a JournalNode can move such a file aside rather than treating it as valid metadata.

## Dependencies And Integration Points
The URL path integrates edit-log loading with web transfer through `URLConnectionFactory`, while the byte-string path supports in-memory/protobuf transport use cases. Local-file tests integrate with `EditLogFileOutputStream` layout creation, permission-status serialization, and loader validation.

## Risks And Test Signals
Important risks are silent acceptance of corrupt operations, incorrect HTTP length accounting, and startup blockage from all-`OP_INVALID` preallocated files. Test signals include exact operation counts for `OP_ADD`, `OP_SET_GENSTAMP_V1`, and `OP_CLOSE`, stream length equality, expected checksum failure text, `hasCorruptHeader()`, and invalid end txid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileOutputStream.java

## Purpose
`TestEditLogFileOutputStream` validates low-level edit-log output stream write, preallocation, flush, close, and abort behavior. It is narrowly focused on `EditLogFileOutputStream` rather than full NameNode replay.

## Important APIs, Types, And Functions
The class uses `EditLogFileOutputStream`, `NameNodeLayoutVersion.CURRENT_LAYOUT_VERSION`, `EditLogFileOutputStream.MIN_PREALLOCATION_LENGTH`, `setReadyToFlush`, `flushAndSync`, `writeRaw`, `close`, and `abort`. Test setup disables fsync for speed and deletes the shared test edits file before and after each test.

## Control Flow
`testRawWrites` creates a stream, writes a small byte array, flushes, and expects the file to expand to the minimum preallocation length. A second small write should reuse preallocated space and keep the same file length. A larger multi-buffer write exceeding the current allocation should grow the file to four times the minimum length. The remaining tests exercise `close` then `abort`, `close` then `close`, and `abort` then `abort` sequences for HDFS-2011 regressions.

## State And Persistence Behavior
The central persisted state is the physical edit-log file length. The test confirms file size includes preallocated space beyond valid edit bytes and that repeated lifecycle operations do not corrupt internal stream state or throw `NullPointerException`. A second `close` is expected to surface an IOException that identifies use of an aborted output stream.

## Dependencies And Integration Points
This class integrates only with local filesystem test directories, `Configuration`, and Hadoop IO cleanup helpers. It underpins higher-level edit-log tests by ensuring the raw stream honors allocation and lifecycle contracts.

## Risks And Test Signals
Risks include excessive or missing preallocation, lifecycle calls leaving partially initialized fields, and repeated close/abort sequences masking real stream state. Test signals are exact file lengths after flushes, no exception for close-abort and abort-abort, and an expected diagnostic on close-close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogJournalFailures.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogJournalFailures.java

## Purpose
`TestEditLogJournalFailures` verifies NameNode behavior when one or more edit journals fail during write, flush, `setReadyToFlush`, or log-segment start. It is parameterized over synchronous and asynchronous edit logging and checks that redundant failures are tolerated up to configured thresholds while required or total failures halt the NameNode.

## Important APIs, Types, And Functions
The suite uses `MiniDFSCluster`, `FSEditLog`, `FSImage`, `JournalSet.JournalAndStream`, `JournalManager`, `EditLogFileOutputStream`, `DistributedFileSystem.rollEdits`, and configuration keys such as `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`, `DFS_NAMENODE_EDITS_DIR_MINIMUM_KEY`, and `DFS_NAMENODE_CHECKED_VOLUMES_MINIMUM_KEY`. Helper methods `invalidateEditsDirAtIndex`, `spyOnStream`, `spyOnJASjournal`, `getJournalAndStream`, and `doAnEdit` inject controlled failures.

## Control Flow
The default setup starts a no-datanode cluster with system exit checking disabled. Tests first perform a mkdir edit, replace selected journal streams with Mockito spies that throw on specific calls, and then perform another edit or roll. Single non-required failures on flush or `setReadyToFlush` should leave the cluster alive. Failure of all journals, a required journal, too many journals below the minimum, or too few successful `startLogSegment` calls should return a `RemoteException` wrapping `ExitException`.

## State And Persistence Behavior
The suite validates the active/inactive status of journal streams and the NameNode's durability threshold decisions. In the required-journal case, it also asserts that after a required journal fails during `setReadyToFlush`, later non-required journals are not asked to set ready, preventing partial side effects from HDFS-2874. The tests do not inspect on-disk log bytes directly; they validate persistence availability through journal state and exception messages about unsynced transactions.

## Dependencies And Integration Points
This class integrates journal quorum/minimum policy, required-edits-dir configuration, NameNode shutdown behavior, RPC exception wrapping, and filesystem mutation. It depends on Mockito spies because actual disk failures would be slower and less deterministic.

## Risks And Test Signals
The main risks are continuing after too little durable edit storage, halting too aggressively when redundancy remains, or partially advancing non-required streams after a required-stream failure. Test signals are successful mkdirs, safe mode remaining false after tolerated failures, exact exception text for fatal paths, inactive journal state, and verification that non-required streams were not invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogJournalFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogRace.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogRace.java

## Purpose
`TestEditLogRace` exercises race-prone NameNode edit-log operations under concurrent namespace mutation, log rolling, safe mode, saveNamespace, and async edit-log queue pressure. Like other edit-log suites, it is parameterized over synchronous and asynchronous edit logging.

## Important APIs, Types, And Functions
The class uses `MiniDFSCluster`, `NamenodeProtocols`, `FSNamesystem`, `FSImage`, `FSEditLog`, `FSEditLogAsync`, `EditLogFileInputStream`, `FSEditLogLoader`, `JournalSet.JournalAndStream`, `EditLogFileOutputStream`, `SafeModeAction`, `RwLockMode`, and `SubjectInheritingThread`. The internal `Transactions` worker repeatedly creates and deletes directories through both `FileSystem` and direct NameNode RPC. `verifyEditLogs` replays every edit log copy for a segment and asserts all journals contain the same number of readable edits.

## Control Flow
`testEditLogRolling` starts 16 transaction workers and rolls logs 30 times, verifying each finalized segment and the next in-progress segment. `testSaveNamespace` performs repeated safe-mode enters and namespace saves while workers mutate the namespace, checking pre-save in-progress edits and post-save finalized edits. `testSaveImageWhileSyncInProgress` spies on stream flush to block a writer in the unsynchronized `logSync` section, then asserts entering safe mode waits for the flush before saving. `testSaveRightBeforeSync` logs an edit under the write lock but sleeps before `logSync`; entering safe mode should call `logSyncAll` and avoid waiting for the sleeping thread. `testDeadlock` congests the async edit queue with spammers, blocks a specific edit operation, then starts a synchronized edit/logSync path to prove queue-full and monitor-lock interactions do not deadlock.

## State And Persistence Behavior
The tests inspect finalized and in-progress edit segment files in the NameNode storage directory, replay them from expected txids, and compare counts across journal copies. They validate the invariant that saveNamespace finalizes all edits up to the checkpoint txid and creates a new in-progress segment containing only the begin transaction. The deadlock test uses last-written txid stagnation as the signal that the async queue is full before releasing the blocked operation.

## Dependencies And Integration Points
This suite integrates concurrency primitives (`CountDownLatch`, `Semaphore`, `Future`, `AtomicReference`, `AtomicBoolean`), NameNode safe mode, edit-log internals, RPC mutation paths, storage files, and async edit queue behavior. It uses Mockito spies and argument matchers to create deterministic stalls inside normally fast code paths.

## Risks And Test Signals
The highest risks are corruption during log rolls, saveNamespace racing with in-flight sync, incorrectly waiting or not waiting when entering safe mode, and deadlocks between synchronized callers and async queue backpressure. Test signals are successful replay of every segment, expected wait-time comparisons around `BLOCK_TIME`, checkpoint txid alignment with last-written txid, completion of futures under timeout, and absence of worker-captured exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogRace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditsDoubleBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditsDoubleBuffer.java

## Purpose
`TestEditsDoubleBuffer` verifies the in-memory double-buffer used by edit-log output streams before flushing bytes to persistent storage. It checks buffer accounting, flush-state transitions, close behavior with unflushed data, and human-readable edit dumps on close failure.

## Important APIs, Types, And Functions
The file exercises `EditsDoubleBuffer`, `DataOutputBuffer`, `writeRaw`, `setReadyToFlush`, `flushTo`, `close`, and `countBufferedBytes`. For operation serialization it uses `FSEditLogOp.SetReplicationOp`, `DeleteOp`, `AllocateBlockIdOp`, `OpInstanceCache`, and a layout version from `NameNodeLayoutVersion.Feature.ROLLING_UPGRADE`.

## Control Flow
`testDoubleBuffer` writes raw bytes to the current buffer, swaps buffers, flushes to an output buffer, and repeats to confirm byte counts and `isFlushed` status. `shouldFailToCloseWhenUnflushed` writes one byte and expects close to throw an IOException mentioning unflushed data. `testDumpEdits` writes three typed edit operations, captures `EditsDoubleBuffer.LOG`, attempts to close without flushing, and verifies the logged output contains each operation's string form.

## State And Persistence Behavior
The buffer maintains a current write buffer and a ready-to-flush buffer. This test asserts that writing into the current buffer alone does not mark the buffer unflushed until `setReadyToFlush` swaps it, and that `flushTo` drains the ready buffer and resets byte counts. The dump test ensures unflushed edit operations are observable in logs for diagnostics before data is discarded by a failed close.

## Dependencies And Integration Points
`EditsDoubleBuffer` is a lower-level dependency of edit-log file streams. Its correctness affects batching, flushing, and diagnostics in `FSEditLog`. The test integrates with `GenericTestUtils.LogCapturer` rather than full filesystem storage.

## Risks And Test Signals
Risks include byte-accounting drift, incorrectly allowing close with unflushed edits, losing diagnostics for pending operations, and mistaken flush-state transitions. Test signals are exact buffer lengths, `isFlushed` booleans, expected close exception text, and logged serialized edit operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditsDoubleBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEnabledECPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEnabledECPolicies.java

## Purpose
`TestEnabledECPolicies` validates how `ErasureCodingPolicyManager` initializes and reports enabled erasure-coding policies from configuration, including invalid policy names, default policy changes, and persisted-vs-effective policy state.

## Important APIs, Types, And Functions
The test uses `HdfsConfiguration`, `DFS_NAMENODE_EC_SYSTEM_DEFAULT_POLICY`, `ErasureCodingPolicyManager`, `SystemErasureCodingPolicies`, `ErasureCodingPolicy`, `ErasureCodingPolicyInfo`, and `ErasureCodingPolicyState`. Helpers `expectInvalidPolicy`, `expectValidPolicy`, `testGetPolicies`, `constructAllDisabledInitialPolicies`, `isPolicyEnabled`, and `assertAllPoliciesAreDisabled` isolate manager behaviors.

## Control Flow
`testDefaultPolicy` reads the configured default policy and expects one enabled policy. `testInvalid` feeds malformed policy lists and expects initialization failures. `testValid` enables the default striped policy. `testGetPolicies` enables zero, one, and two policies, then checks uniqueness and `getEnabledPolicyByName` filtering. `testChangeDefaultPolicy` changes the configured default, simulates fsimage loading with all persisted policies disabled, and verifies how effective enabled state differs from persisted state until explicit disable/enable operations occur.

## State And Persistence Behavior
The distinction between effective runtime policy state and persisted policy state is the central persistence concern. A newly configured default policy can be effectively enabled after init/load even when it remains disabled in the persisted list until an explicit enable operation. Setting the default to an empty string should leave all policies disabled after loading.

## Dependencies And Integration Points
The manager is a singleton, so tests repeatedly call `init` to reset state. The file integrates configuration defaults, system policy definitions, and fsimage-like `loadPolicies` input. It does not start a cluster; it tests policy manager logic directly.

## Risks And Test Signals
Risks include accepting invalid policy names, duplicate enabled-policy results, exposing disabled policies through enabled lookups, and persisting default-policy state incorrectly. Test signals are exception messages, enabled-policy counts, uniqueness checks, null/non-null lookup results, and state comparisons across `getPolicies` and `getPersistedPolicies`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEnabledECPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEncryptionZoneManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEncryptionZoneManager.java

## Purpose
`TestEncryptionZoneManager` validates `EncryptionZoneManager.listEncryptionZones` when some encryption-zone inode IDs no longer resolve to valid namespace paths. The tests cover root zones, valid child zones, orphaned zones, and zones under invalid parent chains.

## Important APIs, Types, And Functions
The file uses `EncryptionZoneManager`, mocked `FSDirectory` and `INodesInPath`, `INodeDirectory`, `BatchedListEntries<EncryptionZone>`, `CipherSuite.AES_CTR_NOPADDING`, `CryptoProtocolVersion.ENCRYPTION_ZONES`, and `FSDirectory.DirOp.READ_LINK`. Setup constructs root, first, and second directory inodes and mocks `getInode` and `getINodesInPath` lookups.

## Control Flow
Each test creates a manager and adds encryption zones by inode ID. Validity is controlled by setting inode parent pointers and configuring path resolution mocks. `testListEncryptionZonesOneValidOnly` leaves one zone without a parent and expects only `/first`. `testListEncryptionZonesTwoValids` sets both parents and expects both zones. `testListEncryptionZonesForRoot` validates the special root path. `testListEncryptionZonesSubDirInvalid` adds a zone under a child whose parent chain is invalid and expects it to be skipped.

## State And Persistence Behavior
The manager stores encryption-zone entries keyed by inode ID. The tests verify that listing does not blindly persist or expose stale IDs: it resolves the inode to a path, validates the parent chain through `FSDirectory`, and returns only zones that correspond to a current, reachable namespace path. No edit-log or fsimage persistence is exercised directly.

## Dependencies And Integration Points
This is a mock-heavy unit test for NameNode encryption-zone listing. It integrates with inode parent relationships and `FSDirectory` path resolution, which are the boundaries where deleted or moved directories can make zone metadata stale.

## Risks And Test Signals
Risks include leaking stale encryption-zone entries to clients, throwing on orphaned inodes, or mishandling the root zone. Test signals are returned batch sizes, stable ordering by zone ID, and expected zone paths and IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEncryptionZoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirAttrOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirAttrOp.java

## Purpose
`TestFSDirAttrOp` unit-tests unprotected FSDirectory attribute mutations: permission changes, owner changes, access/modification time updates, and missing-inode handling. It focuses on return-value semantics that indicate whether a namespace change actually occurred.

## Important APIs, Types, And Functions
The file exercises `FSDirAttrOp.unprotectedSetPermission`, `unprotectedSetOwner`, and `unprotectedSetTimes`. It mocks `FSNamesystem`, `SnapshotManager`, `FSDirectory`, `INodesInPath`, and `INode`, and uses real `INodeDirectory`, `PermissionStatus`, and `FsPermission` for permission/owner tests.

## Control Flow
The helper `unprotectedSetAttributes` constructs an inode with initial owner and permission state, then calls either set-permission or set-owner. Tests assert true when values change and false when the requested values match existing state. The helper `unprotectedSetTimes` mocks access-time precision and current access time, then tests atime below, equal to, and above the precision threshold, plus force and mtime cases. The missing-inode test passes an `INodesInPath` whose last inode is null and expects `FileNotFoundException`.

## State And Persistence Behavior
These are unprotected in-memory namespace operations, so they mutate inode state but do not write edit-log records directly. The tests verify that no-op changes return false, which is important because callers use the return signal to decide whether to log or propagate changes. Access-time precision protects against excessive persistence churn for small atime deltas unless forced or paired with an mtime change.

## Dependencies And Integration Points
The functions depend on `FSDirectory` write-lock ownership, snapshot-manager behavior, latest snapshot IDs, and inode mutators. This unit test isolates those dependencies with Mockito to avoid cluster startup.

## Risks And Test Signals
Risks include logging/persisting no-op permission or owner changes, failing to update atime when force or mtime requires it, updating atime too often despite precision, and missing-file paths not throwing. Test signals are boolean return values and the expected `FileNotFoundException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirAttrOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirEncryptionZoneOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirEncryptionZoneOp.java

## Purpose
`TestFSDirEncryptionZoneOp` verifies retry behavior in the encrypted data encryption key cache warm-up path used by encryption-zone operations.

## Important APIs, Types, And Functions
The test initializes NameNode metrics, mocks `KeyProviderCryptoExtension`, and constructs `FSDirEncryptionZoneOp.EDEKCacheLoader` with an array of key names, an initial delay, retry interval, and `maxRetries`. It verifies calls to `warmUpEncryptedKeys`.

## Control Flow
The mocked key provider throws `IOException` twice and would succeed on a third call. The loader is configured with `maxRetries = 2`, then run synchronously. The verification expects exactly two warm-up attempts, proving the loader stops at the configured retry limit rather than continuing to the later success answer.

## State And Persistence Behavior
The loader does not persist namespace state in this test. Its relevant state is retry count and scheduling delays. The test protects operational behavior around external KMS failures: warm-up should retry transient failures but remain bounded.

## Dependencies And Integration Points
This test integrates encryption-zone namespace code with Hadoop crypto key-provider APIs and NameNode metrics initialization. It uses a direct unit path rather than creating real encryption zones or a KMS.

## Risks And Test Signals
Risks include unbounded retry loops, too few warm-up attempts, or accidental dependency on metrics being initialized elsewhere. The test signal is the Mockito verification that `warmUpEncryptedKeys` is called exactly `maxRetries` times.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirEncryptionZoneOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirWriteFileOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirWriteFileOp.java

## Purpose
`TestFSDirWriteFileOp` checks that the `IGNORE_CLIENT_LOCALITY` add-block flag prevents NameNode block placement from resolving or passing a client source node.

## Important APIs, Types, And Functions
The test uses `FSDirWriteFileOp.chooseTargetForNewBlock`, `FSDirWriteFileOp.ValidateAddBlockResult`, `BlockManager.chooseTarget4NewBlock`, `AddBlockFlag.IGNORE_CLIENT_LOCALITY`, `EnumSet`, and a Mockito `ArgumentCaptor<Node>`.

## Control Flow
The test constructs a minimal `ValidateAddBlockResult`, passes the ignore-locality flag, mocks `BlockManager.chooseTarget4NewBlock`, and calls `chooseTargetForNewBlock` with a localhost client. It verifies the block manager is called once, captures the source-node argument, asserts there are no other block-manager interactions, and checks the captured source node is null.

## State And Persistence Behavior
No namespace or edit-log state is persisted. The relevant state is the computed block-placement input: when locality is ignored, the source node should remain null so downstream target selection is not biased toward the client host.

## Dependencies And Integration Points
This is a unit boundary between file-write namespace validation and block placement. It protects integration with `BlockManager` and add-block flags without requiring datanodes or a cluster.

## Risks And Test Signals
Risks include unintended hostname resolution, extra `BlockManager` calls, and incorrect locality bias when the flag is set. Test signals are a single `chooseTarget4NewBlock` invocation, no additional interactions, and a null captured `Node`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirWriteFileOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirectory.java

## Purpose
`TestFSDirectory` covers selected behaviors of the in-memory NameNode namespace tree: dump formatting, quota-check bypass, xattr limits and multi-operation semantics, and parent-directory verification for different directory operations.

## Important APIs, Types, And Functions
The class uses `MiniDFSCluster`, `FSNamesystem`, `FSDirectory`, `DistributedFileSystem`, `DFSTestUtil`, `INode.dumpTreeRecursively`, `FSDirXAttrOp.setINodeXAttrs`, `FSDirXAttrOp.filterINodeXAttrs`, `FSDirectory.resolvePath`, `FSDirectory.verifyParentDir`, and `FSDirectory.DirOp`. It constructs `XAttr` instances across user, system, raw, and trusted namespaces.

## Control Flow
Setup creates a cluster with three datanodes, configures a two-xattr visible limit per inode, creates a small directory/file tree, and keeps handles to `FSDirectory` and HDFS. `testDumpTree` dumps the root inode tree and verifies non-snapshot lines use expected tree markers and inode class names. `testSkipQuotaCheck` sets a quota that blocks file creation, disables quota checks, confirms creation succeeds, then re-enables checks and confirms creation fails again. Xattr tests add and remove generated xattrs in random batches, check duplicate and flag errors, and validate namespace-specific limits. `testVerifyParentDir` resolves valid and invalid paths under read/write/create modes and checks the exception type and message.

## State And Persistence Behavior
The tests mutate live namespace state in the cluster: files, directories, quotas, and xattrs. The quota bypass toggles global FSDirectory quota-check state and uses `finally` cleanup to restore quota and delete test files. Xattr tests primarily operate on in-memory lists returned by `FSDirXAttrOp`, validating list transformation semantics and configured limits rather than relying on edit-log replay.

## Dependencies And Integration Points
This file integrates NameNode namespace logic with HDFS client operations, quota enforcement, xattr policy, path resolution, and access-control exception mapping. It depends on `DFS_NAMENODE_MAX_XATTRS_PER_INODE_KEY` to create a low-limit boundary.

## Risks And Test Signals
Risks include malformed dump output, quota bypass state leaking, visible xattr limits applying to system/raw namespaces incorrectly, duplicate xattr inputs being accepted, CREATE/REPLACE flags being ignored, and wrong exception classes for non-directory parents. Test signals are exact xattr counts and values, expected exception text, successful or failed file creation under quota, and path-resolution exception classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSEditLogLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSEditLogLoader.java

## Purpose
`TestFSEditLogLoader` validates edit-log replay, validation, diagnostic logging, block and erasure-coding replay, replication adjustment, and throttled loader progress logs. It is parameterized over synchronous and asynchronous edit logging and tagged slow.

## Important APIs, Types, And Functions
The suite exercises `FSEditLogLoader`, `FSEditLogLoader.EditLogValidation`, `EditLogFileInputStream.scanEditLog`, `FSEditLog`, `FSImage`, `MiniDFSCluster`, `DistributedFileSystem`, `PositionTrackingInputStream`, `BlockInfoContiguous`, `BlockInfoStriped`, `ErasureCodingPolicyManager`, `ErasureCodingPolicy`, and `FakeTimer`. Helpers include `corruptByteInFile`, `truncateFile`, `getNonTrailerLength`, `prepareUnfinalizedTestEditLog`, and `getFakeEditLogInputStream`.

## Control Flow
Diagnostic tests corrupt a recent edits file and expect startup failure text to include recent opcode offsets. Replication tests create a file with replication one, restart with minimum replication two, and wait for the replayed file to be adjusted. Validation tests prepare an unfinalized log, corrupt its header/body or truncate before operations, and check validation end txids. The opcode test round-trips all byte values through `FSEditLogOpCodes.fromByte`. EC tests replay add-block/update-block edits for striped files, detect contiguous blocks with striped IDs, and replay add/enable/disable/remove EC policy operations across NameNode restarts. The throttling test uses a fake timer to verify loader log messages are emitted and suppressed at configured intervals.

## State And Persistence Behavior
The file manipulates real edit-log files, including in-progress logs with trailer bytes, byte-level corruption, and truncation. It validates the persistent replay result by restarting NameNodes and checking namespace inodes, block metadata, block-manager flags, EC policy states, and readable files. `getNonTrailerLength` explicitly distinguishes valid content from `OP_INVALID` preallocation trailers when recording transaction offsets.

## Dependencies And Integration Points
The suite integrates edit-log loading with NameNode startup, block manager state, erasure coding policy manager state, replication monitor behavior, logging, and filesystem clients. It relies on `FSImageTestUtil`, `DFSTestUtil`, `StripedFileTestUtil`, and Guava file utilities for test setup.

## Risks And Test Signals
Risks include poor diagnostics on replay failure, validation reporting the wrong last good txid, replication minimum changes not applying during replay, striped block metadata being lost, EC policy edits not surviving restart, and progress logs flooding logs. Test signals include expected error-message regexes, validation header/end-txid fields, exact block IDs/sizes/generation stamps, EC policy states, `hasNonEcBlockUsingStripedID`, file readability after policy changes, and captured log output with suppression counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSEditLogLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImage.java

## Purpose
`TestFSImage` validates fsimage save/load behavior across ordinary files, under-construction files, compression, legacy image compatibility, erasure coding, block maps, policy persistence, parallel fsimage loading, and snapshot/name-cache rebuilds.

## Important APIs, Types, And Functions
The class uses `MiniDFSCluster`, `FSNamesystem`, `FSImage`, `FSImageSerialization`, `FSImageFormat.Loader`, `FSImageFormatProtobuf`, `FSImageTestUtil`, `DistributedFileSystem`, `SecondaryNameNode`, `MD5FileUtils`, `ErasureCodingPolicyManager`, `SystemErasureCodingPolicies`, `BlockInfoStriped`, `BlockInfoContiguous`, `SnapshotTestHelper`, and `DFSOutputStream.hsync`. Helpers include `testPersistHelper`, `testSaveAndLoadStripedINodeFile`, `testChangeErasureCodingPolicyState`, `isPolicyEnabledInFsImage`, `createAndLoadParallelFSImage`, `getSubSectionsOfName`, and `ensureSubSectionsAlignWithParent`.

## Control Flow
Basic persistence tests create empty and under-construction files, save the namespace, restart, and validate directory presence, file size, block under-construction state, and lease tracking. Compression tests rerun persistence with default, gzip, bzip2, and native lz4 codecs. Striped inode tests serialize and deserialize normal and under-construction striped inode files. Checkpoint tests validate missing checkpoint edits-dir errors, deletion of stale `fsimage.ckpt_*`, and fsimage MD5 sidecar correctness. Legacy and block tests load a Hadoop 2.7 image with zero block size, persist/reload block groups under multiple EC policies, and detect non-EC blocks with striped IDs in files, under-construction files, and snapshots.

## State And Persistence Behavior
The file is centered on fsimage persistence. It creates checkpoints through safe mode and `saveNamespace`, restarts NameNodes without formatting, and inspects both client-visible paths and internal inode/block state. EC policy tests verify policy definitions and enabled/disabled/removed states in `ErasureCodingPolicyManager` and the persisted policy list. Parallel fsimage tests inspect protobuf file-summary sections to ensure generated inode and directory subsections cover contiguous byte ranges and align with parent sections. The async block-map/name-cache test compares pre- and post-restart namespace tree dumps after snapshots and renames.

## Dependencies And Integration Points
This suite integrates fsimage serialization with HDFS client operations, NameNode lease manager, block manager, EC policy manager, secondary checkpointing, compression codecs, native-code availability, old test-cache images, protobuf section metadata, and snapshot tree utilities. Some tests depend on enough datanodes for EC group sizes.

## Risks And Test Signals
Risks include losing under-construction file state, broken compression handling, stale checkpoint files accumulating, digest mismatches, legacy images failing upgrade, EC block groups or policy IDs being serialized incorrectly, non-EC striped-ID flags being missed, default protobuf block type changing, parallel fsimage sections overlapping or leaving gaps, and async restart rebuilding a different namespace tree. Test signals are file existence, lease presence, exact block metadata, MD5 equality, policy state assertions, readable file bytes, section counts and offsets, and tree-dump comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageStorageInspector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageStorageInspector.java

## Purpose
`TestFSImageStorageInspector` validates the transactional fsimage storage inspector's ability to discover image files and select the latest checkpoint image from a NameNode storage directory containing images and edits.

## Important APIs, Types, And Functions
The test uses `FSImageTransactionalStorageInspector`, `FSImageStorageInspector.FSImageFile`, `FSImageTestUtil.mockStorageDirectory`, `StorageDirectory`, `NameNodeDirType.IMAGE_AND_EDITS`, and `NNStorage` filename helpers for finalized edits, in-progress edits, and image files.

## Control Flow
`testCurrentStorageInspector` creates a mock storage directory containing `fsimage_123`, finalized edits `123-456`, `fsimage_456`, and in-progress edits starting at 457. It runs `inspectDirectory`, asserts two images were found, obtains the latest image, and checks txid, storage-directory identity, upgrade-finalized status, and resolved file path.

## State And Persistence Behavior
The test models persisted storage contents by filename rather than writing real files. It validates that the inspector treats the highest-txid image as latest and associates it with the storage directory that reported it. The in-progress edits file should not prevent upgrade-finalized detection in this current-directory scenario.

## Dependencies And Integration Points
This is a focused unit test for the storage-inspection layer used during NameNode startup and checkpoint discovery. It depends on canonical `NNStorage` file naming rules and `FSImageTestUtil` mocks.

## Risks And Test Signals
Risks include selecting an older image, misclassifying upgrade state, or constructing the wrong image file path. Test signals are found-image count, latest txid 456, object identity with the mocked storage directory, `isUpgradeFinalized()`, and the expected `/foo/current/fsimage_456` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageStorageInspector.java -->
