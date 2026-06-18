# subset-b-008084 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServlet.java

Purpose: This integration test validates the original `OMDBCheckpointServlet` HTTP checkpoint export path for OM DB bootstrapping. It covers unauthenticated/no-ACL access, SPNEGO admin filtering, GET and multipart POST handling, SST exclusion parameters, snapshot-data inclusion, hard-link preservation, and bootstrap lock coordination with OM background services.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `OzoneManager`, `OMDBCheckpointServlet`, `DBStore`, `DBCheckpoint`, `DBCheckpointMetrics`, `BootstrapStateHandler`, `OmSnapshotManager`, `SnapshotInfo`, `RocksDBCheckpointDiffer`, servlet request/response mocks, `FileUtil.unTar`, and OM constants such as `OM_DB_NAME`, `OM_SNAPSHOT_DIR`, `OM_HARDLINK_FILE`, and checkpoint request parameter names. Helpers such as `setupMocks`, `setupHttpMethod`, `prepSnapshotData`, `getFiles`, `checkLine`, and `testBootstrapLocking` define most of the scenario shape.

Control flow: Each test creates an in-process Ozone cluster, wires a Mockito servlet to call real servlet methods, writes the servlet response into a temp tar file, then exercises `doGet`, `doPost`, or `writeDbDataToStream`. Snapshot tests create keys, create two snapshots, fabricate additional hard links and compaction backup files, download the checkpoint, untar it, and compare the checkpoint tree and snapshot tree against the original OM metadata directory. Lock tests take the servlet bootstrap write lock or competing service locks and assert the other side blocks.

State and persistence behavior: The persistent state under test is RocksDB checkpoint content, active OM DB files, snapshot DB directories, compaction log/SST backup directories, generated tar archives, and the hard-link manifest. The test checks that excluded SST files are omitted, snapshot files are included only when requested, fabricated hard links map to one real copy, `CURRENT` is not treated as a hard link, temporary hard-link helper files do not leak in `java.io.tmpdir`, and checkpoint metrics record creation and streaming times.

Dependencies and integration points: This suite links servlet authorization, OM metadata snapshots, RocksDB checkpoint differ pause directories, snapshot manager layout, key/snapshot creation through `OzoneManagerProtocol`, multipart request parsing, and OM bootstrap state locking for key deleting, snapshot deleting, SST filtering, and checkpoint differ services.

Risks: It is filesystem- and timing-sensitive because it relies on hard-link semantics, temp directories, servlet stream closing, background snapshot materialization, and future lock timeouts. The assertions encode tar layout details and relative path truncation behavior, so checkpoint format changes must update the test deliberately.

Test signals: Strong signals include non-empty tarballs, response status `400` for bad POST content type, `403` for unauthorized SPNEGO principals, checkpoint metric increments, exact file-set equality after untar, expected omitted SST names, hard-link manifest line validation, copied compaction log/SST files, and mutual exclusion between servlet bootstrap lock and other bootstrap-aware handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServletInodeBasedXfer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServletInodeBasedXfer.java

Purpose: This suite validates the inode-based OM DB checkpoint transfer servlet. It covers batched tarball generation, inode/mtime file naming, snapshot checkpoint inclusion, snapshot DB consistency, deleted-file handling during collection, snapshot cache locking, bootstrap lock behavior, and the guarantee that checkpoint snapshot paths come from frozen checkpoint metadata rather than mutable live OM state.

Important APIs and types: The test exercises `OMDBCheckpointServletInodeBasedXfer`, `OMDBArchiver`, `InodeMetadataRocksDBCheckpoint`, `DBCheckpoint`, `DBStore`, `SnapshotCache`, `OmSnapshotManager`, `OmSnapshot`, `OzoneSnapshot`, `OMDBDefinition`, raw RocksDB column family reads, `OzoneManagerRatisServer`, `SnapshotPurge` protobuf requests, and config keys such as `OZONE_OM_RATIS_SNAPSHOT_MAX_TOTAL_SST_SIZE_KEY` and `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA`.

Control flow: Setup starts a one-datanode mini cluster, spies the OM, configures long snapshot-cache cleanup intervals, and routes servlet output to temp tar files. The tarball tests write keys and optional snapshots, call `doGet`, untar into an `om.db` directory, then compare inode sets and generated YAML metadata. Other tests call `collectFilesFromDir` directly for SST-only filtering, stream closure, batching, and deletion races. Locking tests hold checkpoint locks while services or snapshot purge work tries to proceed. Frozen-state tests create an extra snapshot while the snapshot cache lock is acquired and then inspect the untarred checkpoint.

State and persistence behavior: The file verifies persistent archive contents, inode-derived file names, snapshot checkpoint DB directories, generated `.yaml` files, delete-table entries written into snapshot DBs, candidate transfer data, and hard-link map semantics. It also checks that `OM_HARDLINK_FILE` is consumed by `InodeMetadataRocksDBCheckpoint` and not left as a regular file in the reconstructed checkpoint.

Dependencies and integration points: It integrates the servlet with OM snapshot manager/cache locking, RocksDB checkpoint creation, checkpoint differ SST backup directories, snapshot delete/purge Ratis responses, low-level RocksDB column families, and Ozone client operations that create keys and snapshots.

Risks: These tests are sensitive to concurrent snapshot deletion, file removal during directory scans, stream lifecycle, inode availability, and background snapshot services. Several assertions depend on exact archive layout, inode string parsing, and timing between checkpoint creation, cache locks, and Ratis double-buffer flushes.

Test signals: Signals include batched archive size behavior with and without snapshot data, closed `Files.list` streams, inode sets matching OM data, correct hard-link maps, expected YAML counts, presence of snapshot DB directories and delete-table values, successful skip of deleted files only when allowed, lock blocking counters, and snapshot inclusion from frozen checkpoint state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMDbCheckpointServletInodeBasedXfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMHALeaderSpecificACLEnforcement.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMHALeaderSpecificACLEnforcement.java

Purpose: This HA integration test proves that OM ACL and admin checks are enforced by the current leader's local configuration. It intentionally reconfigures only one OM in a three-node HA service and verifies that privileges do not implicitly follow the user after leadership transfers to a node without the same admin setting.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `OzoneClientFactory.getRpcClient`, `OzoneManager.transferLeadership`, OM reconfiguration through `getReconfigurationHandler().reconfigureProperty`, `UserGroupInformation`, `OzoneNativeAuthorizer`, `OzoneVolume`, `OzoneBucket`, `VolumeArgs`, `BucketArgs`, `OzoneOutputStream`, `OMException`, and `PERMISSION_DENIED`.

Control flow: `init` creates test and admin users, starts a three-OM HA cluster with ACLs enabled, and creates an admin-owned volume. `restoreLeadership` returns leadership to the original OM before each test. The admin-privilege test adds the test user to only the current leader's `OZONE_ADMINISTRATORS`, verifies volume and bucket creation succeeds as that user, transfers leadership to another OM, then verifies the same operations fail. The set-times test creates a key as admin, lets the test user update mtime while admin on the leader, transfers leadership, and expects `setTimes` to fail.

State and persistence behavior: Persistent OM metadata includes volumes, buckets, and keys created through the HA service. The leader-specific state is runtime OM configuration: the admin username list is reconfigured on only one process and is not treated as replicated metadata. The test also mutates the JVM login user and restores it after client operations.

Dependencies and integration points: It integrates HA leader election/transfer, client proxy routing by service ID, OM native ACL authorization, dynamic reconfiguration, admin checks for create volume/create bucket, and preExecute ACL enforcement for key `setTimes`.

Risks: Leadership transfer and user-context switching are timing-sensitive. Because the test validates intentionally node-local configuration, any future design that replicates reconfiguration would change the expected result. The static random names reduce collisions but make failures slightly harder to reproduce by name.

Test signals: Key signals are admin list membership on old and new leaders, successful object creation before transfer, `PERMISSION_DENIED` for volume/bucket creation after transfer, mtime update before transfer, unchanged privilege state on the new leader, and `PERMISSION_DENIED` from `setTimes` after leadership changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMHALeaderSpecificACLEnforcement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshotTransfer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshotTransfer.java

Purpose: This parameterized HA suite validates OM Ratis snapshot installation paths that require checkpoint transfer from leader to follower. It runs under both legacy and inode-based checkpoint transfer formats and focuses on full snapshot installs, multi-tarball batching, incremental transfers, fallback after corruption, and post-install read/write viability.

Important APIs and types: The tests use `MiniOzoneHAClusterImpl`, `OzoneManagerRatisServer`, `TransactionInfo`, Ratis `TermIndex`, `OMSnapshotProvider`, `DBCheckpointMetrics`, `FaultInjector`, `InodeMetadataRocksDBCheckpoint`, `HAUtils`, `RDB` checkpoint utilities, `AuditLogTestUtils`, and the helper methods shared from `TestOMRatisSnapshots`. `SnapshotMaxSizeInjector` inspects downloaded tarballs and changes `OZONE_OM_RATIS_SNAPSHOT_MAX_TOTAL_SST_SIZE_KEY` to force batching.

Control flow: Setup builds a three-OM cluster with two active OMs, small Ratis segments, a low snapshot trigger threshold, and a bucket using `OBJECT_STORE` layout for direct RocksDB checks. `testInstallSnapshot` leaves one OM inactive, writes many keys and snapshots on the leader, starts the inactive OM, waits for snapshot install, verifies follower metadata, confirms audit/log signals, reads and writes after install, verifies snapshot hard-link behavior, and proves each tarball has a disjoint SST set. Incremental tests use a pausing fault injector to block installs, create later checkpoints, inspect incremental tarballs for non-duplication, then resume and validate metrics or corruption fallback.

State and persistence behavior: Persistent state includes OM DB checkpoints, Ratis snapshot tarballs in the follower snapshot directory, follower candidate DB contents, snapshot DB directories, active key tables, transaction term/index metadata, audit logs, and DB checkpoint metrics. Failure tests delete candidate SST files to simulate corruption and then require a later full snapshot path plus cleanup.

Dependencies and integration points: It integrates Ozone client writes, OM HA start/stop, Ratis log purge and snapshot auto-trigger settings, checkpoint provider transfer, follower checkpoint installation, snapshot lookup semantics, audit logging, and RocksDB archive inspection.

Risks: Several tests are annotated unhealthy for known instability and depend on precise timing around log indexes, pauses, downloads, and purge thresholds. Direct tar and RocksDB file inspection makes the tests sensitive to checkpoint layout changes.

Test signals: Signals include follower `lastAppliedTermIndex` reaching the leader snapshot index/term, log messages for DB reload and checkpoint completion, follower key-table entries for inactive-period writes, RPC server restart, audit log checkpoint install entries, non-overlapping SST entries across tarballs, incremental excluded-SST metrics, empty candidate directories, and snapshot lookup/hard-link validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshotTransfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshots.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshots.java

Purpose: This HA test class validates OM Ratis snapshot installation behavior independent of checkpoint transfer format. It focuses on follower state reload while clients read or write, rejection of stale checkpoints, shutdown behavior on corrupted checkpoints, and cleanup after failed snapshot download.

Important APIs and types: The suite uses `MiniOzoneHAClusterImpl`, `OzoneManagerRatisServer`, `TransactionInfo`, Ratis `TermIndex`, `DBCheckpoint`, `RDBStore`, `RDBCheckpointUtils`, `OzoneManagerRatisUtils`, `ExitManager`, `FaultInjector`, `OMMetadataManager`, `SnapshotInfo`, `OmKeyArgs`, `OmKeyInfo`, `getINode`, and `OmSnapshotManager.getSnapshotPath`. Static helpers `writeKeys`, `createOzoneSnapshot`, and `checkSnapshot` are reused by the transfer-specific test class.

Control flow: Setup creates a three-OM HA cluster with two active OMs, small Ratis logs, and an object-store-layout bucket. Client-write and client-read tests advance leader log index while an OM is inactive, start the inactive OM, perform concurrent client operations, wait for install logs and term/index catch-up, then verify follower key-table state. Failure tests create old or corrupted checkpoints, arrange the checkpoint under `om.db`, call `installCheckpoint`, and assert rejection or simulated system exit. A download failure test injects an `IOException` during snapshot provider pause and waits for candidate directory cleanup.

State and persistence behavior: The file verifies OM DB checkpoint contents, active and snapshot RocksDB directories, follower candidate directories, Ratis term/index persisted in checkpoint transaction info, key table rows, and hard-link identity between active and snapshot SST files. Corruption is modeled by deleting alternating SST files from a checkpoint before install.

Dependencies and integration points: It connects OM HA lifecycle, Ratis snapshot install, RocksDB checkpoint parsing, Ozone client read/write paths, snapshot lookup, OM service restart/reload, log capture, and exit-manager behavior.

Risks: The tests depend on timing, log messages, filesystem hard links, and direct manipulation of checkpoint directories. Stale-checkpoint and corrupted-checkpoint scenarios encode precise install safety semantics that should change only with explicit design changes.

Test signals: Signals include log messages for aborted install, reloaded OM state, finished checkpoint install, stale-checkpoint rejection, RPC server stop on corrupted reload, exact `TermIndex` preservation, follower metadata rows for all written keys, successful client reads/writes after install, hard-link inode equality for live snapshot SSTs, and empty candidate directory after failed download.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMStartupWithBucketLayout.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMStartupWithBucketLayout.java

Purpose: This compact integration test verifies that bucket layout metadata survives OM restarts and remains independent of later changes to the default bucket layout configuration. It covers both default-FSO and default-OBS startup modes.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneConfiguration`, `OzoneClient`, `TestDataUtil.createVolumeAndBucket`, `OzoneBucket`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, and `BucketLayout` values `FILE_SYSTEM_OPTIMIZED` and `OBJECT_STORE`.

Control flow: Static helpers start a no-datanode mini cluster, restart only the OM, and tear everything down. `testRestartWithFSOLayout` starts with FSO as the default, creates an explicit FSO bucket, restarts and creates a bucket with no requested layout, restarts and creates an explicit OBS bucket, then verifies all layouts across another restart and after changing the default to OBS. `testRestartWithOBSLayout` mirrors the same sequence with OBS as the initial default and later flips the default to FSO.

State and persistence behavior: The persistent state under test is the bucket layout stored in OM metadata. The tests specifically distinguish per-bucket persisted layout from the mutable `OZONE_DEFAULT_BUCKET_LAYOUT` configuration used only when a new bucket request has no explicit layout.

Dependencies and integration points: It integrates OM startup/restart, bucket creation request handling, client-side `OzoneBucket` layout reads, and the default bucket layout config path. Running without datanodes keeps the scope on OM metadata rather than key IO.

Risks: The class uses static cluster/client fields and manual `try/finally` teardown, so failed startup can affect later tests if cleanup is skipped. It does not inspect raw DB rows; it verifies through client-visible bucket metadata.

Test signals: Signals are exact `BucketLayout` equality for explicit FSO buckets, default-created buckets, explicit OBS buckets, and previously created buckets after multiple restarts and after changing the default layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMStartupWithBucketLayout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMUpgradeFinalization.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMUpgradeFinalization.java

Purpose: This HA upgrade test verifies that OM upgrade finalization can complete while one OM is down and that the restarted OM catches up to the finalized metadata layout version. It also checks audit logging for prepare, cancel, and finalize operations.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `OzoneManagerProtocol`, `OMUpgradeTestUtils.assertClusterPrepared`, `waitForFinalization`, `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, `OMLayoutFeature.INITIAL_VERSION`, `OMLayoutVersionManager.maxLayoutVersion`, `OzoneManagerStateMachine`, Ratis `LifeCycle`, `LAYOUT_VERSION_KEY`, and audit helpers for `OMAction.UPGRADE_PREPARE`, `UPGRADE_CANCEL`, and `UPGRADE_FINALIZE`.

Control flow: The test builds a three-OM HA cluster initialized at the initial layout version, stops one OM, prepares the remaining active OMs to compact/purge logs, verifies prepare state and audit success, cancels prepare, finalizes upgrade through the OM client, waits for finalization, restarts the downed OM, waits through any state-machine pause/resume window, and finally checks the restarted OM's layout version and metadata table value.

State and persistence behavior: Persistent state includes OM upgrade metadata, the meta table's `LAYOUT_VERSION_KEY`, Ratis logs/snapshots affected by prepare/finalize, and audit log records. The downed OM starts with older local state and must replay or install finalized state until its version manager and DB metadata match `maxLayoutVersion()`.

Dependencies and integration points: It integrates HA OM lifecycle, upgrade prepare/cancel/finalize RPCs, Ratis state-machine lifecycle, audit logging, metadata layout version management, and cluster restart with catch-up.

Risks: The test is timing-sensitive around state-machine pause states and uses a fallback assertion if pausing is not observed before timeout. It validates one downed-OM scenario but not multiple failures or partial finalization errors.

Test signals: Signals include stopped OM state, successful cluster prepare index on running OMs, audit log success records for prepare/cancel/finalize, finalization completion, state machine leaving paused states after restart, version manager metadata layout equal to `maxLayoutVersion()`, and a non-null DB `LAYOUT_VERSION_KEY` matching the same version.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMUpgradeFinalization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStore.java

Purpose: This abstract non-HA integration test verifies object-store bucket layout behavior when filesystem path handling is not the focus. It checks explicit bucket layouts, default layout selection, link bucket layout resolution, dangling link behavior, and loop detection for linked buckets.

Important APIs and types: The test uses the `NonHATests.TestCase` cluster contract, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `BucketArgs`, `BucketLayout`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, and `OMException` result code `DETECTED_LOOP_IN_BUCKET_LINKS`.

Control flow: `init` takes the shared non-HA cluster config and client. `testCreateBucketWithBucketLayout` creates a volume and then buckets with no layout, `OBJECT_STORE`, `LEGACY`, and `FILE_SYSTEM_OPTIMIZED`, verifying each returned bucket layout. Link tests create source buckets of different layouts, create link buckets by setting source volume/bucket with `BucketLayout.DEFAULT`, and inspect resolved layout through `getBucket`. The dangling link test points at a missing source and expects the default layout. The loop test creates three link buckets that reference one another and expects lookup to fail.

State and persistence behavior: Persistent state is volume/bucket metadata, including bucket layout, link source volume/bucket fields, and link-chain relationships. The test observes that link buckets inherit the resolved source layout when possible, while dangling links fall back to the current configured default.

Dependencies and integration points: It covers client object-store APIs, OM bucket creation and lookup, bucket layout defaults, link bucket resolution, and loop detection in link traversal. It is intended to run under the non-HA test harness configuration.

Risks: Default-layout expectations depend on the surrounding non-HA cluster configuration. Link-chain checks validate client-visible metadata rather than raw DB records. The loop test intentionally constructs invalid metadata through normal API calls, so future stricter creation-time validation could shift the failure point.

Test signals: Signals are exact layout equality for each bucket creation mode, link bucket layouts matching source bucket layouts including chained links, dangling source name preservation with default layout fallback, and `DETECTED_LOOP_IN_BUCKET_LINKS` when resolving a cyclic link chain.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithFSO.java

Purpose: This abstract non-HA integration suite validates object-store and filesystem behavior for `FILE_SYSTEM_OPTIMIZED` buckets. It covers FSO key creation, open-file table movement, bucket emptiness with intermediate directories, lookup visibility for open/deleted keys, recursive key listing, path normalization, key renames, and bucket layout creation defaults.

Important APIs and types: The file uses `MiniOzoneCluster`, `OzoneFileSystem`, `FileSystem`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneOutputStream`, `KeyOutputStream`, `OMMetadataManager`, `Table<String, OmKeyInfo>`, `OmDirectoryInfo`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OmUtils.normalizeKey`, `OMException` result codes `KEY_NOT_FOUND` and `KEY_ALREADY_EXISTS`, and config `OZONE_FS_ITERATE_BATCH_SIZE`.

Control flow: Setup creates an FSO volume/bucket, configures `fs.defaultFS` to the Ozone URI, and cleans root contents after each test. Key-creation and lookup tests create nested keys, inspect directory table parent object IDs, verify rows appear in open-file tables while streams are open, then close streams and verify rows move to the key table. Listing tests build a multi-level tree and compare depth-first listings for root, prefixes, previous-key boundaries, not-normalized paths, and direct bucket-level keys. Rename tests move keys to bucket level, across subdirectories, and into existing-key conflicts.

State and persistence behavior: The suite directly checks OM FSO metadata tables: directory table rows, open-key table rows keyed by parent ID and client ID, final key table rows, and bucket emptiness after file and directory deletion. It also validates filesystem-visible data by reading through both `OzoneBucket.readKey` and `OzoneFileSystem.open`.

Dependencies and integration points: It integrates Ozone object-store APIs, FSO metadata manager key generation, Hadoop filesystem URI handling, key stream client IDs, batch listing, path normalization, and recursive cleanup.

Risks: Tests rely on async DB cleanup for open-key rows and use `GenericTestUtils.waitFor`. Direct parent-object-ID assertions are sensitive to FSO DB key format changes. Root cleanup assumes all created paths can be recursively removed through the filesystem API.

Test signals: Signals include expected open-key and key-table presence/absence, correct parent object IDs and filenames, `KEY_NOT_FOUND` for open/deleted/renamed keys, bucket deletion failure until intermediate directories are removed, exact listing order for the constructed tree, normalized prefix behavior, successful reads through both APIs, and `KEY_ALREADY_EXISTS` on conflicting rename.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithLegacyFS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithLegacyFS.java

Purpose: This abstract non-HA integration test verifies legacy filesystem-path behavior when OM filesystem paths are enabled, especially the distinction between flat `OBJECT_STORE` buckets and path-like `LEGACY` buckets. It also tests multipart upload completion when directory-like keys already exist.

Important APIs and types: The file uses `OmConfig.isFileSystemPathEnabled`, `setFileSystemPathEnabled`, `OzoneClient`, `OzoneVolume`, `OzoneBucket`, `BucketArgs`, `BucketLayout.OBJECT_STORE`, `BucketLayout.LEGACY`, `Table<String, OmKeyInfo>`, `RatisReplicationConfig`, `OmMultipartInfo`, `OmMultipartCommitUploadPartInfo`, `OmMultipartUploadCompleteInfo`, `OzoneConsts.ETAG`, MD5 ETags, and `OMException.ResultCodes.NOT_A_FILE`.

Control flow: `initClass` records and enables the OM filesystem path flag, and `cleanup` restores it. Each test creates a fresh object-store-layout bucket. `testFlatKeyStructureWithOBS` creates a nested key in an OBS bucket, iterates the object-store key table from a prefix, verifies only the flat key exists, renames it, and verifies the flat row changed without intermediate directory rows. `testMultiPartCompleteUpload` uploads one MPU part to an OBS bucket while a trailing-slash key exists and expects success, then repeats in a LEGACY bucket with a directory-like conflicting path and expects failure.

State and persistence behavior: Persistent state includes OM key table rows, renamed flat key names, multipart upload state, part ETags, and layout-specific interpretation of trailing slash keys. The key-table iterator check ensures OBS remains a flat key-value structure even when filesystem paths are globally enabled.

Dependencies and integration points: It integrates object-store bucket operations, OM runtime config mutation, metadata table iteration, key rename, multipart upload initiation/part creation/completion, replication config, and legacy directory conflict detection.

Risks: The test mutates shared OM config and must restore it to avoid leaking filesystem-path behavior into later tests. Iterator prefix counting is sensitive to DB key encoding. MPU behavior depends on MD5 ETag metadata being set on the output stream before close.

Test signals: Signals include exactly one matching OBS key row before and after rename, successful OBS MPU completion despite a trailing-slash key, `NOT_A_FILE` for LEGACY MPU completion with a conflicting directory-like path, non-null upload IDs and completion info, and restored filesystem-path config after the class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestObjectStoreWithLegacyFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmAcls.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmAcls.java

Purpose: This integration test verifies OM ACL enforcement and audit/log signals for denied volume, bucket, key, file-status, and key ACL operations. It uses a custom authorizer whose per-resource booleans can be flipped to force negative authorization outcomes.

Important APIs and types: The suite uses `MiniOzoneCluster`, `OzoneConfiguration`, `OZONE_TEST_AUTHORIZATION_ENABLED`, `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS`, wildcard administrators, `IAccessAuthorizer`, `OzoneObjInfo`, `RequestContext`, `OzoneAcl`, `ObjectStore`, `OzoneBucket`, `TestDataUtil`, `OMException`, `ResultCodes.PERMISSION_DENIED`, `AuditLogTestUtils`, `OMAction`, and `LogCapturer`.

Control flow: Cluster setup enables ACLs and installs `OzoneAccessAuthorizerTest`, then stores the actual authorizer from the OM. Before each test it clears captured logs/audit logs and resets all resource booleans to allow. Individual tests turn off one resource class, perform an operation that needs create/read/write/read-ACL/write-ACL permission, assert `OMException`, inspect the error log text, and verify relevant audit failure records where present. The nested authorizer returns allow/deny based solely on resource type: volume, bucket, key, or prefix.

State and persistence behavior: Successful setup creates volumes, buckets, and keys needed before flipping denial flags. The important mutable state is the in-memory authorizer booleans and audit log file content. The test does not inspect metadata tables; it validates that operations are blocked before or during OM request processing with the expected result code.

Dependencies and integration points: It integrates OM native ACL call sites, object-store client APIs, file-status lookup, key ACL management operations (`getAcl`, `setAcl`, `addAcl`, `removeAcl`), audit logging, and OM log messages.

Risks: The custom authorizer ignores ACL type and identity, so the tests validate OM call-site routing and denial handling rather than real ACL policy semantics. Assertions on log substrings can break when diagnostic text changes even if authorization remains correct.

Test signals: Signals include `PERMISSION_DENIED`, log messages naming the missing permission and resource type, audit failures for create/read/set/get/add/remove ACL operations, and correct use of volume, bucket, or key resource type in the test authorizer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmBlockVersioning.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmBlockVersioning.java

Purpose: This abstract non-HA integration test preserves OM-side block versioning behavior for key open, block allocation, commit, overwrite, and read-latest semantics. It documents the current behavior that bucket versioning is not generally supported, while explicit open/commit updates can still produce sequential location versions.

Important APIs and types: The file uses `OzoneClient`, `OzoneManager`, `OzoneManagerProtocol`, `OzoneBucket`, `TestDataUtil`, `OmKeyArgs`, `OpenKeySession`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `ExcludeList`, `StandaloneReplicationConfig`, and protobuf replication factor `ONE`.

Control flow: `testAllocateCommit` creates a volume/bucket/key, calls `bucket.setVersioning(true)` to preserve historical behavior, then performs three `openKey`/`commitKey` cycles. The first two commits use the latest open-key block list directly. The third allocates an additional block through `allocateBlock`, appends it to the latest location list, commits, and checks that versions are sequential and the latest version has two blocks. `testReadLatestVersion` creates and overwrites a key through normal client IO while versioning is disabled and checks reads and OM lookup always expose version 0 with one block.

State and persistence behavior: Persistent state is OM key metadata: location version groups, block lists, and latest version selected by lookup/read. The first test expects multiple version groups after explicit commits, while the second expects overwrites without bucket versioning to reset/remain at version 0 rather than accumulating visible versions.

Dependencies and integration points: It integrates OM protocol open/commit/allocate calls, client key creation/read helpers, replication config, SCM block allocation through OM, and `OzoneManager.lookupKey`.

Risks: The tests encode legacy compatibility around unsupported bucket versioning. If full versioning support changes overwrite semantics, these assertions will need intentional updates. They do not validate block contents, only metadata version and block-count behavior.

Test signals: Signals include sequential version numbers from `checkVersions`, latest versions 0, 1, and 2 after explicit commit cycles, latest location-list sizes of one/one/two, normal overwrite reads returning the newest data string, and latest version staying 0 with one block when versioning is disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmBlockVersioning.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmConf.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmConf.java

Purpose: This small unit-style integration test verifies that `OzoneManagerRatisServerConfig.logAppenderWaitTimeMin` is translated correctly from `OzoneConfiguration` into the Ratis `RaftProperties` used by OM Ratis.

Important APIs and types: The file uses `OzoneConfiguration`, `OzoneManagerRatisServerConfig`, `OzoneManagerRatisServer.newRaftProperties`, `RaftProperties`, `RaftServerConfigKeys.Log.Appender.waitTimeMin`, and Ratis `TimeDuration`.

Control flow: `testConf` creates a fresh configuration, reads the typed OM Ratis config object, asserts the default wait-time minimum is zero, and calls `assertWaitTimeMin` to verify the generated Ratis property is `TimeDuration.ZERO`. It then sets the typed value to `1`, writes the object back to the configuration with `setFromObject`, and verifies the generated Ratis property becomes one millisecond.

State and persistence behavior: There is no filesystem or DB persistence. State is limited to the in-memory configuration object and derived Ratis properties. The test protects config serialization/deserialization between Ozone's typed config object and the Ratis property namespace.

Dependencies and integration points: It covers OM Ratis server configuration plumbing, especially the conversion path used during OM Ratis server startup when `newRaftProperties` is built from Ozone config plus port and storage directory inputs.

Risks: The test only checks one Ratis property and uses a dummy directory/port, so it does not validate full Ratis startup. It assumes the integer config value is expressed in milliseconds.

Test signals: Signals are exact equality for default typed value `0`, generated wait-time `TimeDuration.ZERO`, generated wait-time `TimeDuration.ONE_MILLISECOND` after setting the typed config to `1`, and the Ratis property key reported in assertion messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmConf.java -->
