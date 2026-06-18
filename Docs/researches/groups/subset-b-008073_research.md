# subset-b-008073 research

Grouped research for the Ozone filesystem integration-test subset. Each section is delimited for reconciliation into the mapped per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestBase.java

Purpose: abstract shared test suite for Ozone Hadoop `FileSystem` behavior across O3FS and OFS variants. It contains reusable assertions for listing, implicit directories, recursive delete, invalid path handling, capabilities, timestamp mutation, and rename edge cases. Concrete subclasses provide `getFs`, `pathUnderFsRoot`, key lookup, child-key naming, and layout-specific verification hooks.

Important APIs/types/functions: `listStatusIteratorOnPageSize` configures a small listing page size and verifies iterator paging; `listLocatedStatusForZeroByteFile` checks zero-length files expose no block locations; `createKeyWithECReplicationConfig` validates EC replication configuration through `OzoneKeyDetails`; `verifyListStatus`, `listStatusOnRoot`, and `listStatusOnSubDirs` encode immediate-child listing semantics. Rename helpers cover file-to-file, file-to-directory, parent rename, self-subdir prevention, and missing destination parent failures.

Control flow: each helper creates a focused tree under the supplied root, performs filesystem operations through the abstract `FileSystem`, asserts Hadoop-compatible status or exception behavior, then cleans up the tree. Some helpers additionally query OM key metadata to distinguish real key rows from synthetic filesystem parents.

State and persistence behavior: the tests intentionally exercise Ozone's object-store-backed directory model. Creating a deep child must not automatically persist parent directory keys, but listing and status calls must synthesize parent directories. Deleting the last child may create a fake parent dir key, and recursive deletes must remove batched children. EC tests persist replication metadata and confirm it is stored on the created key.

Dependencies and integration points: depends on Hadoop `FileSystem`, `Path`, `FileStatus`, `RemoteIterator`, `ContractTestUtils`, Ozone `OzoneConfiguration`, `OzoneKeyDetails`, and OM exceptions. It integrates with concrete O3FS/OFS test subclasses and their key-table lookup implementations.

Risks: assertions depend on subtle synthetic-directory semantics and ordering-insensitive listing behavior. Iterator paging uses a disabled FS cache so stale cached configuration would hide page-size bugs. Tests that inspect OM key rows are sensitive to bucket layout and key-name composition differences.

Test signals: failures indicate regressions in listStatus/listStatusIterator parity, directory materialization, delete batching, rename validation, EC replication config propagation, path validation, path capabilities, or mtime handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestUtils.java

Purpose: tiny utility holder for Ozone filesystem integration tests.

Important APIs/types/functions: `setPageSize(ConfigurationTarget, int)` asserts a positive page size, writes `ozone.fs.listing.page.size`, and disables both `o3fs` and `ofs` filesystem caches so future `FileSystem.get` calls observe the new setting.

Control flow: validate input with Ratis `Preconditions`, set the integer config, then set `fs.o3fs.impl.disable.cache` and `fs.ofs.impl.disable.cache`.

State and persistence behavior: no persistent Ozone state. It mutates only the supplied Hadoop/Ozone configuration target.

Dependencies and integration points: uses Ozone URI scheme constants and `OZONE_FS_LISTING_PAGE_SIZE`. It is used by listing tests such as `OzoneFileSystemTestBase.listStatusIteratorOnPageSize`.

Risks: forgetting to disable caches would make page-size tests reuse an old filesystem instance. Passing zero or negative page size is explicitly rejected.

Test signals: useful signal is whether paginated list tests actually run with the configured page size for both O3FS and OFS.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSync.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSync.java

Purpose: large integration suite for `hflush`/`hsync` support in Ozone, centered on FSO buckets, OM open-key state, committed key rows, datanode chunk persistence, lease cleanup, overwrite interactions, stream capabilities, and concurrent write/sync behavior.

Important APIs/types/functions: `init` builds a five-DN `MiniOzoneCluster` with hbase enhancements, filesystem hsync, FSO bucket layout, tuned chunk/block sizes, open-key cleanup intervals, and suspended `OpenKeyCleanupService`. Public tests include `testKeyMetadata`, `testEmptyHsync`, `testKeyHSyncThenClose`, `testHSyncSeek`, `testO3fsHSync`, `testOfsHSync`, expiry/deletion/recursive-delete cases, overwrite cases, `testHsyncKeyCallCount`, concurrent hsync tests, stream capability checks, EC capability checks, disabled-hsync behavior, and small/big buffer Ozone client hsync writes. Helpers expose table scans, datanode chunk-path discovery, read-after-hsync verification, and error injection.

Control flow: setup creates the cluster, client, and bucket once, then each test sets `fs.defaultFS` to either O3FS or OFS. File tests open `FSDataOutputStream`, write data, call `hsync`, inspect filesystem visibility or OM tables, and close or deliberately delete/overwrite paths. Concurrency tests start writer/syncer threads for timed loops, collect exceptions, and validate the final byte stream. Overwrite tests suspend deletion services, clean OM tables, create normal and hsynced streams in conflicting orders, then verify final content, metrics, deleted-table entries, and bucket usage.

State and persistence behavior: hsync writes an open-key table row and a committed key-table row with `HSYNC_CLIENT_ID`; final close removes the open row and clears hsync metadata from the committed key. Deleted hsync keys are marked with `DELETED_HSYNC_KEY` and later reclaimed by open-key cleanup. The tests verify no duplicate deleted-table blocks after hsync-close, chunk files stay open until close, hsynced bytes become readable after datanode PutBlock propagation, and overwrite races leave only the winning committed key while stale open keys are cleaned later.

Dependencies and integration points: uses `MiniOzoneCluster`, `OzoneClient`, `OzoneBucket`, OM `OMMetadataManager`, `OMMetrics`, `OpenKeyCleanupService`, `KeyOutputStream`, `ECKeyOutputStream`, `OzoneFSOutputStream`, `CapableOzoneFSOutputStream`, `CapableOzoneFSDataStreamOutput`, Ratis error injection through `XceiverClientManager`, and Hadoop `FSDataInputStream/OutputStream`. It also interacts with bucket replication config and encryption stream wrappers.

Risks: tests are timing-sensitive because OM double-buffer flushing, datanode DB application, open-key cleanup, and key deletion are asynchronous. Some tests intentionally manipulate global config and service state and must restore hsync/datastream/deletion settings. Concurrent error injection is marked unhealthy and can expose race conditions in exception propagation.

Test signals: strong coverage of hsync correctness, OM metadata transitions, read-after-sync durability, lease-expiry cleanup, deletion and overwrite consistency, stream capability advertisement, EC non-support of hsync, disabled feature behavior, buffer-size edge cases, and concurrency safety.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSyncUpgrade.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSyncUpgrade.java

Purpose: verifies that hsync-related features are blocked before OM layout-feature finalization and available only after upgrade finalization starts and completes.

Important APIs/types/functions: `init` creates a five-DN FSO cluster initialized at the `MULTITENANCY_SCHEMA` layout version, with hsync enabled in configuration but not finalized. `upgrade` runs `preFinalizationChecks` and `finalizeOMUpgrade`. Assertions validate `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION` for hsync, `listOpenFiles`, and `recoverLease`.

Control flow: setup configures hsync, open-key cleanup, client buffering, and logging; the test opens OFS, creates a file, expects `outputStream.hsync()` to throw the pre-finalization OMException, checks the OM protocol and filesystem lease recovery APIs also fail, deletes the file, then calls `finalizeUpgrade` and polls progress until done.

State and persistence behavior: before finalization, open file creation may exist but hsync metadata and recovery operations must not be accepted. Finalization mutates OM upgrade state from starting to done through `OzoneManagerProtocol`.

Dependencies and integration points: depends on `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, `OMLayoutFeature`, `UpgradeFinalization`, `OzoneManagerProtocol`, `RootedOzoneFileSystem`, and the same hsync cluster/client config used by normal hsync tests.

Risks: tied to upgrade layout versions and finalization status messages. Polling waits up to 120 seconds and can fail if finalization stalls. The test assumes hsync support is gated by feature finalization, independent of client-side config.

Test signals: protects rolling-upgrade compatibility by proving clients receive explicit unsupported-operation errors before finalization and that OM finalization progresses successfully.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSyncUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestLeaseRecovery.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestLeaseRecovery.java

Purpose: integration tests for `RootedOzoneFileSystem.recoverLease` and `isFileClosed` on hsynced open files, including datanode block-length probing, container closure, forced recovery, OM connection failure, wrong path handling, and partial block edge cases.

Important APIs/types/functions: `closeIgnoringKeyNotFound` and `closeIgnoringOMException` normalize expected close failures after recovery. `testRecovery` parameterizes file sizes around block boundaries. Other tests cover no final hsync/hflush on the last block, OBS bucket rejection, finalizeBlock failure logging, closed pipeline recovery, `GetCommittedBlockLength` timeout/exception handling, OM outage, missing file, empty block list, partial hsync block, and equal block counts in open-file and file tables. `closeLatestContainer`, `verifyData`, and `getData` support the scenarios.

Control flow: setup creates a three-DN FSO cluster with hsync enabled, zero lease soft limit, disabled flush delay, and a rooted OFS default URI. Each test creates a unique file, writes and hsyncs data, writes additional data with or without flush, triggers a recovery path, asserts closure state and file length, then closes the stale stream expecting key-not-found or lease-recovery exceptions.

State and persistence behavior: recovery commits or truncates open-key state into the final file depending on datanode block-length evidence. If all committed-length probes time out and force recovery is enabled, OM's known hsynced length becomes final. Closing containers or pipelines simulates stale block state. After successful recovery the original stream's open key is gone.

Dependencies and integration points: uses `RootedOzoneFileSystem`, `MiniOzoneCluster`, SCM container/pipeline managers, `OzoneTestUtils.closeContainer`, `KeyValueHandler` fault injection, `FaultInjectorImpl`, `XceiverClientGrpc` logs, and OM exceptions. It is marked flaky for HDDS-11323.

Risks: asynchronous pipeline closure, RPC timeout tuning, and forced recovery via system property can make tests timing-sensitive. Error assertions depend on log messages and exception wrapping. Shared fault injectors must be reset between tests.

Test signals: validates that recovery is idempotent, rejects unsupported bucket layouts and wrong files, preserves readable data across partial/unflushed writes when evidence is available, fails or truncates predictably when evidence is unavailable, and survives OM restart recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestLeaseRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FS.java

Purpose: concrete O3FS test selector for the shared non-rooted filesystem suite using legacy bucket layout and non-filesystem-path behavior.

Important APIs/types/functions: package-private `TestO3FS` extends `AbstractOzoneFileSystemTest` and calls `super(false, BucketLayout.LEGACY)`. `@TestInstance(PER_CLASS)` lets inherited setup share class lifecycle.

Control flow: no local tests; JUnit runs inherited tests from the abstract superclass with constructor-supplied parameters.

State and persistence behavior: inherits all cluster, bucket, filesystem, listing, delete, and rename state behavior from the parent suite, specifically under O3FS URI authority semantics.

Dependencies and integration points: depends on `AbstractOzoneFileSystemTest` and `BucketLayout.LEGACY`.

Risks: small selector can silently change large inherited coverage if constructor flags are modified. It does not contain assertions itself.

Test signals: any failure comes from inherited O3FS legacy behavior tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSO.java

Purpose: concrete O3FS selector for the file-system-optimized bucket-layout test suite.

Important APIs/types/functions: extends `AbstractOzoneFileSystemTestWithFSO` and invokes its default constructor under `@TestInstance(PER_CLASS)`.

Control flow: local class only binds inherited tests to the FSO O3FS configuration.

State and persistence behavior: inherits FSO-specific path, key-table, and directory semantics from the parent fixture.

Dependencies and integration points: depends on `AbstractOzoneFileSystemTestWithFSO`, which supplies cluster setup and actual test methods.

Risks: coverage relies entirely on the superclass. A constructor or superclass change changes all behavior here.

Test signals: inherited failures signal O3FS FSO regressions in the shared filesystem contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSPaths.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSPaths.java

Purpose: concrete O3FS selector for legacy buckets with filesystem-path handling enabled.

Important APIs/types/functions: extends `AbstractOzoneFileSystemTest` and calls `super(true, BucketLayout.LEGACY)`.

Control flow: no local test logic; inherited tests run with the filesystem-path flag enabled.

State and persistence behavior: parent tests exercise legacy-bucket directory semantics while OM filesystem-path support is active.

Dependencies and integration points: depends on the shared O3FS abstract test class and legacy bucket layout.

Risks: a one-argument flag flip changes expected path normalization and directory materialization behavior.

Test signals: inherited failures isolate regressions specific to O3FS legacy buckets when FS path mode is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFS.java

Purpose: concrete OFS/rooted filesystem selector for legacy bucket layout without filesystem paths or extra feature flags.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTest` and calls `super(BucketLayout.LEGACY, false, false)`.

Control flow: local class only parameterizes the inherited rooted filesystem suite.

State and persistence behavior: inherited tests operate through `ofs://` volume/bucket-rooted paths with legacy layout semantics.

Dependencies and integration points: depends on `AbstractRootedOzoneFileSystemTest` and `BucketLayout.LEGACY`.

Risks: constructor flag order is compact and easy to misread; mistakes would route broad inherited coverage to a different layout or mode.

Test signals: inherited test failures point to OFS legacy-rooted behavior regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSO.java

Purpose: concrete rooted OFS selector for the file-system-optimized bucket-layout test suite.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTestWithFSO` and passes `false` to its constructor.

Control flow: no local tests; inherited rooted FSO tests execute under PER_CLASS lifecycle.

State and persistence behavior: exercises FSO metadata and rooted path behavior supplied by the superclass.

Dependencies and integration points: depends on `AbstractRootedOzoneFileSystemTestWithFSO`.

Risks: local coverage is wholly delegated; the meaning of the boolean constructor flag must remain consistent with the superclass.

Test signals: failures come from inherited OFS FSO filesystem behavior tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSPaths.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSPaths.java

Purpose: concrete rooted OFS selector for legacy bucket layout with filesystem paths enabled.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTest` and invokes `super(BucketLayout.LEGACY, true, false)`.

Control flow: delegates entirely to inherited tests.

State and persistence behavior: inherited tests run on `ofs://` paths and verify legacy layout behavior under filesystem path support.

Dependencies and integration points: depends on rooted abstract test fixture and legacy layout.

Risks: relies on constructor flags for all behavior and contains no local assertions.

Test signals: inherited failures identify rooted OFS regressions in filesystem-path-enabled legacy buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSPaths.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSBucketLayout.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSBucketLayout.java

Purpose: parameterized abstract test for OFS default bucket-layout configuration and validation when filesystem operations create buckets.

Important APIs/types/functions: `validDefaultBucketLayouts` returns empty/default, FSO, and LEGACY. `invalidDefaultBucketLayouts` returns an unknown value and OBJECT_STORE. `fileSystemWithUnsupportedDefaultBucketLayout` expects OMException messages; `fileSystemWithValidBucketLayout` creates a bucket through `fs.mkdirs` and checks actual `OzoneBucket.getBucketLayout`. `configWithDefaultBucketLayout` writes `OzoneClientConfig.fsDefaultBucketLayout` into a fresh configuration.

Control flow: setup obtains a cluster client, object store, OFS root URI, and a volume. Each parameter builds a new `OzoneConfiguration`, creates a new filesystem, and either expects construction failure or creates a bucket path `/volume/bucket-layout-suffix`.

State and persistence behavior: valid cases persist newly created buckets in OM with the requested layout. Invalid cases should fail before creating filesystem-visible state. Empty config maps to `OzoneClientConfig.Defaults.OZONE_CLIENT_FS_DEFAULT_BUCKET_LAYOUT`.

Dependencies and integration points: uses `NonHATests.TestCase`, `ObjectStore`, `OzoneBucket`, `OzoneClientConfig`, `FileSystem.newInstance`, and OFS URI scheme.

Risks: error-message assertions are specific. Bucket names are deterministic by layout, so repeated runs in one shared cluster depend on isolated test state or unique volume setup.

Test signals: detects unsupported default layout acceptance, OBJECT_STORE misuse for filesystem semantics, and drift between client config and actual bucket creation layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSBucketLayout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java

Purpose: verifies `OzoneFSInputStream` read semantics through Hadoop APIs and SequenceFile integration, for both replicated O3FS buckets and EC buckets.

Important APIs/types/functions: setup creates a 30 MiB random file in O3FS and an EC FSO bucket. Tests cover single-byte `read`, byte-array reads, `ByteBuffer` read, positioned `read(position, ByteBuffer)`, positioned `readFully`, invalid positions, EOF exceptions, and `SequenceFile.Reader.sync` against replicated and EC files.

Control flow: class-level setup writes known random data once. Each test opens `FSDataInputStream`, reads through a particular API, compares returned bytes and file position behavior, and closes streams. SequenceFile tests upload a resource file to Ozone then verify `sync(0)` moves to the same position as HDFS behavior.

State and persistence behavior: persists a large test file and EC bucket data in the mini cluster. Positioned reads must not mutate stream position. Invalid or beyond-EOF positioned reads return `-1` for `read` and throw `EOFException` for `readFully`.

Dependencies and integration points: uses Hadoop `FSDataInputStream`, `ByteBufferPositionedReadable` behavior through `FSDataInputStream`, `SequenceFile.Reader`, Ozone EC replication config, and `TestDataUtil` bucket creation.

Risks: large random fixture increases runtime and memory. Assertions assume multi-byte read chunks exactly match the 1 MiB temporary buffer count. SequenceFile resource availability is required.

Test signals: catches regressions in byte-level correctness, positioned read contract, EOF handling, stream position preservation, ByteBuffer support, and EC read compatibility with SequenceFile sync.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSWithObjectStoreCreate.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSWithObjectStoreCreate.java

Purpose: abstract non-HA integration tests for interactions between object-store-created keys and O3FS filesystem path semantics in legacy buckets with filesystem paths enabled.

Important APIs/types/functions: setup enables `OmConfig.fileSystemPathEnabled`, creates a fresh legacy volume/bucket for each test, and opens `OzoneFileSystem`. Tests include object-store key creation with slashy paths, O3FS status of ancestors, object-store delete plus O3FS recursive delete/rename, key close failure when a directory appears before commit, MPU complete failure/success around same-name directory conflicts, directory-first conflicts, non-normalized `listKeys`, and double-slash prefix normalization. Helpers `checkKeyList`, `createAndAssertKey`, `readKey`, `checkPath`, and `checkAncestors` centralize verification.

Control flow: each scenario creates keys through `OzoneBucket` APIs, then reads or mutates through O3FS. Conflict tests deliberately create an object-store stream or multipart part, create a filesystem directory at the same path before commit/complete, assert `NOT_A_FILE`, remove the directory if needed, and retry.

State and persistence behavior: validates normalization from leading or repeated slashes to canonical key names, implicit ancestor directories, deletion of synthetic parents after object-store key removal, and correct persistence of MPU parts only after complete succeeds. Same path cannot be both directory and file/key.

Dependencies and integration points: uses `OzoneClient`, `OzoneBucket`, `OzoneVolume`, `OzoneOutputStream`, MPU metadata/ETag calculation, `OmUtils.normalizeKey`, `OzoneFileSystem`, OM config, and legacy bucket layout.

Risks: path strings intentionally include leading and repeated slashes; changing normalization rules can shift many assertions. The test temporarily mutates OM config and must restore it. The MPU path depends on MD5/ETag metadata setup.

Test signals: strong signal for S3/object-store and filesystem interoperability, directory/file conflict handling, path normalization, key listing prefix/previous-key behavior, and ancestor status synthesis.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSWithObjectStoreCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileChecksum.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileChecksum.java

Purpose: verifies Ozone `FileSystem.getFileChecksum` produces the same checksum for EC and replicated data across many sizes, checksum granularities, topology-aware read modes, and missing datanodes.

Important APIs/types/functions: setup creates a five-DN cluster with 1 MiB chunks and 2 MiB blocks. `testEcFileChecksum` parameterizes missing datanode indexes and `ozone.client.bytes.per.checksum`, creates a legacy replicated bucket and an EC bucket, writes identical data via `BasicRootedOzoneClientAdapterImpl.createFile`, records replicated checksums, shuts down selected datanodes, then compares EC checksums under topology-aware true and false. `missingIndexesAndChecksumSize` supplies six failure/checksum-size combinations.

Control flow: for each data size in two generated arrays, write replicated data, compute checksum, write EC data, then after DN shutdowns open a fresh filesystem for each topology mode and compare EC checksum hex to the recorded replicated checksum.

State and persistence behavior: persists two copies of each random object, one replicated and one EC. Datanode shutdown simulates missing EC fragments while checksum reconstruction should remain deterministic and equal to replicated checksum semantics.

Dependencies and integration points: uses `MiniOzoneCluster`, `RootedOzoneFileSystem`, `BasicRootedOzoneClientAdapterImpl`, `FileChecksum`, EC replication config `RS-3-2-1024k`, network topology aware read config, and Hadoop checksum byte formatting.

Risks: many large data sizes make this an expensive test. Random data and datanode shutdowns can amplify flaky reconstruction or timeout behavior. It assumes two missing indexes remain within EC tolerance.

Test signals: detects checksum algorithm drift, EC reconstruction checksum mismatches, topology-aware read regressions, and failure to serve checksums when tolerated datanodes are unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMetrics.java

Purpose: validates OM `numKeys` metrics for key, file, and directory operations through Ozone filesystem and object-store APIs.

Important APIs/types/functions: enum `TestOps` selects Key, File, or Directory. `testOzoneFileCommit` records `OMMetrics.getNumKeys`, creates either an object-store key, an O3FS file, or a directory, asserts the count increased by two, deletes the parent, and asserts the count returns to the baseline.

Control flow: setup suspends key and directory deleting services, enables filesystem paths, creates a legacy bucket, and opens O3FS. Each test delegates to the common helper with a different operation kind.

State and persistence behavior: operations create a parent plus leaf entry, hence the expected `+2` key count. Recursive delete removes both entries while deletion services are suspended to keep accounting deterministic. OM config is restored and services resumed in cleanup.

Dependencies and integration points: uses `OMMetrics`, `OzoneBucket.createKey`, `FileSystem.create`, `FileSystem.mkdirs`, OM deleting services, and `OmConfig.fileSystemPathEnabled`.

Risks: metric semantics are tightly coupled to how directories are counted in legacy filesystem-path mode. Asynchronous deletion would make assertions flaky if services were not suspended.

Test signals: catches mismatches between OM metadata mutations and exposed `numKeys` metric for object-store keys, filesystem files, and directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMissingParent.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMissingParent.java

Purpose: tests OFS commit failure behavior when an open file's parent directory is removed or renamed before stream close.

Important APIs/types/functions: setup creates a volume/bucket and opens rooted OFS. `testCloseFileWithDeletedParent` creates `/volume/bucket/parent/file`, deletes `parent`, and expects close to fail. `testCloseFileWithRenamedParent` renames the parent to `parent1` before close and expects the same failure.

Control flow: create a file stream, mutate parent directory while stream remains open, then call `stream.close` inside `assertThrows(OMException.class)` and verify message text.

State and persistence behavior: file creation initially materializes the missing parent. If that parent disappears before commit, OM must not commit the child file; it reports that the parent directory does not exist.

Dependencies and integration points: uses OFS URI, `FSDataOutputStream`, `FileSystem.delete`, `FileSystem.rename`, and OM exception reporting. Per-test cleanup recursively deletes the bucket path.

Risks: stream close error text is asserted literally enough to catch message changes. Open stream resources are intentionally not closed successfully after failure.

Test signals: detects stale-parent validation gaps that could commit files into deleted or renamed directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMissingParent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemPrefixParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemPrefixParser.java

Purpose: verifies the offline OM `PrefixParser` correctly classifies volumes, buckets, intermediate directories, missing directories, files, and directories in an FSO bucket.

Important APIs/types/functions: setup creates a three-DN cluster, an FSO O3FS bucket, directory `/a/b/c/d/e`, and file `/a/b/c/file1`. `testPrefixParsePath` stops the cluster and parses paths against the OM DB directory. `assertPrefixStats`, `testPrefixParseWithInvalidPaths`, and `verifyPrefixParsePath` compare parser counters.

Control flow: after cluster stop, parse an existing directory parent, an existing file, invalid volume, invalid bucket, and an invalid intermediate directory path. Each parse uses volume, bucket, OM DB path, and target path.

State and persistence behavior: relies on RocksDB state persisted by OM before shutdown. The parser reads DB files directly rather than live OM services.

Dependencies and integration points: uses `PrefixParser`, `OMStorage.getOmDbDir`, `MiniOzoneCluster`, O3FS, and FSO bucket layout.

Risks: stopping the cluster before parsing is required to inspect stable DB state. Parser counters are sensitive to FSO metadata layout and path-depth interpretation.

Test signals: catches regressions in offline prefix diagnostics for existing and missing path components, invalid volume/bucket handling, and file-vs-directory classification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemPrefixParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreaming.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreaming.java

Purpose: tests filesystem write behavior when Ozone datastream is enabled and automatic stream selection is controlled by a size threshold.

Important APIs/types/functions: setup enables container RATIS datastream, filesystem datastream, `ozone.fs.datastream.auto.threshold` at 2 MiB, and tuned client buffers. `testO3fsCreateFile` and `testOfsCreateFile` run the same create/read verification for O3FS and OFS paths. `createFile` asserts the wrapped stream is `SelectorOutputStream` and that the chosen underlying stream is null below threshold before close, `CapableOzoneFSOutputStream` after below-threshold close, or `CapableOzoneFSDataStreamOutput` for above-threshold data. `runTestCreateFile` verifies bytes read back exactly.

Control flow: for file sizes 1, 2, and 3 MiB, create file, write all data, inspect stream selection before and after close, then read and compare the file.

State and persistence behavior: below-threshold writes stay on the normal Ozone FS output path; above-threshold writes switch to datastream. Both modes must persist identical bytes and be readable through normal filesystem reads.

Dependencies and integration points: uses `MiniOzoneCluster`, `SelectorOutputStream`, `CapableOzoneFSOutputStream`, `CapableOzoneFSDataStreamOutput`, O3FS/OFS URI schemes, and datastream configuration keys.

Risks: relies on implementation class names and threshold boundary semantics. Writing exactly threshold-sized data is classified as below threshold. Stream selection may be lazy until sufficient bytes are written.

Test signals: catches accidental fallback or wrong stream choice, datastream read/write corruption, and differences between O3FS and OFS datastream behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreaming.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreamingDisabledDatanode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreamingDisabledDatanode.java

Purpose: verifies client-side datastream writes fail fast when datanode-side RATIS datastream ports are disabled, instead of silently falling back to the old gRPC/HTTP2 path.

Important APIs/types/functions: setup disables `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, enables `OZONE_FS_DATASTREAM_ENABLED`, sets auto-threshold to 1 byte, and creates a three-DN FSO O3FS bucket. `testDatastreamWriteFailsFastWhenDatanodeStreamingDisabled` writes a 3 MiB file and expects `IOException`. `collectMessages` flattens the exception cause chain.

Control flow: set O3FS default URI, create random bytes above threshold, attempt create/write/close, then inspect the exception messages for datastream-port validation text and absence of HTTP/2 or timeout fallback indicators.

State and persistence behavior: the write is expected to fail; no successful file content persistence is asserted. The important state is pipeline metadata missing `RATIS_DATASTREAM` ports.

Dependencies and integration points: uses datastream configuration, `MiniOzoneCluster`, O3FS, and client write path validation.

Risks: assertion matches a set of allowed message fragments rather than a specific exception type. If lower layers change wording, test may need updates while preserving fail-fast semantics.

Test signals: detects regressions where the client proceeds with datastream despite missing datanode support or degrades into slow gRPC/HTTP2 timeout failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemWithStreamingDisabledDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsHAURLs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsHAURLs.java

Purpose: tests client-side URI authority parsing and `FsShell` behavior for O3FS/OFS paths in Ozone Manager HA clusters.

Important APIs/types/functions: setup obtains a `MiniOzoneHAClusterImpl`, OM service ID, client, creates a unique volume/bucket, sets `fs.defaultFS` to `o3fs://bucket.volume.serviceId/`, and creates directories. `getLeaderOMNodeAddr`, `getHostFromAddress`, and `getPortFromAddress` derive authority components. Tests cover qualified default FS, unqualified/default-FS variants, and incorrect service IDs for both schemes.

Control flow: `testWithQualifiedDefaultFS` runs `ozone fs -ls` through `FsShell` against `/`, `o3fs:///`, unqualified bucket.volume, leader hostname, leader host:port, service ID, and service ID with port, asserting success or stderr messages. `testOtherDefaultFS` calls `testWithDefaultFS` for file, HDFS, unqualified o3fs, and bucket.volume defaults. `testIncorrectAuthorityInURI` checks correct and dummy service IDs for OFS and O3FS.

State and persistence behavior: creates real volume/bucket and directories in HA OM state, but tests focus on client resolution and shell exit codes. No persistent mutation beyond setup directories is central to assertions.

Dependencies and integration points: uses `HATests.TestCase`, `MiniOzoneHAClusterImpl`, `ConfUtils`, OM address config keys, `FsShell`, `ToolRunner`, O3FS/OFS implementation keys, and Hadoop URI parsing helpers.

Risks: shell stderr text and exit code conventions are part of the assertions. Tests depend on an active OM leader and configuration where `ozone.om.address` can be overridden for leader host/port cases.

Test signals: catches authority parsing regressions, missing service ID validation, incorrect use of ports with service IDs, and bad error reporting for unresolved OM hosts in HA mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsHAURLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsSnapshot.java

Purpose: integration suite for `ozone fs` snapshot CRUD and snapshot listing semantics through OFS against an HA-style mini cluster with snapshots enabled.

Important APIs/types/functions: setup enables filesystem snapshots, short snapshot-deletion interval, disabled SST filtering, larger listing max/page sizes, and disabled snapshot rename; creates volume, bucket, and key through `OzoneFsShell`. Tests cover duplicate snapshot names, subdirectory input normalization, valid/invalid snapshot names and paths, blocked rename through object-store API and CLI, `.snapshot` listing with deleted snapshots filtered out, snapshot key listing, bucket deletion blocked by snapshots, delete success/failure, and snapshot name reuse. Helpers `execShellCommandAndGetOutput` and `createSnapshot` wrap shell execution and wait for snapshot DB/directory state.

Control flow: most tests issue shell commands with `ToolRunner.run(shell, args)` and assert exit codes plus stdout/stderr. Some tests inspect `SnapshotInfoTable` directly to avoid race with DB flush. Listing tests pause `SnapshotDeletingService`, create multiple snapshots beyond page size, delete one, wait for `SNAPSHOT_DELETED`, and confirm only active snapshots are listed.

State and persistence behavior: snapshots are persisted in OM metadata and on-disk snapshot directories. Deleted snapshots can remain in metadata while marked deleted and must be hidden from filesystem listing. Existing snapshots prevent bucket deletion while preserving snapshot-visible keys after live keys are removed. Rename is blocked by OM config and returns `FEATURE_NOT_ENABLED`.

Dependencies and integration points: uses `MiniOzoneCluster.newHABuilder`, `OzoneFsShell`, `OzoneShell`, `OzoneClient.renameSnapshot`, `SnapshotInfo`, `OmSnapshotManager.getSnapshotPath`, snapshot/deleting services, and shell output capture.

Risks: helper restores `System.out/err` to new print streams over byte arrays, so it is suitable for test isolation but fragile in shared output contexts. Snapshot deletion and directory materialization are asynchronous and guarded by waits. Assertions depend on CLI messages and page-size configuration.

Test signals: catches snapshot validation regressions, path normalization bugs for subdirectory inputs, deleted snapshot leakage in listings, broken snapshot key access, bucket-deletion safety violations, rename feature-gate bypass, and snapshot-name reuse failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestSafeMode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestSafeMode.java

Purpose: verifies O3FS and OFS implement Hadoop `SafeMode` against SCM safe mode state and force-exit behavior.

Important APIs/types/functions: `MiniOzoneClusterProvider` creates reusable clusters. `ofs` and `o3fs` call `testSafeMode` with URI builders. `testSafeMode` casts the filesystem to `SafeMode`, checks `GET`, stops datanodes, restarts SCM without waiting for normal exit, checks safe mode, calls `FORCE_EXIT`, and verifies SCM cannot allocate a writable container because datanodes remain down.

Control flow: each test creates a fresh cluster, volume, and bucket, opens either `ofs://om/` or `o3fs://bucket.volume.om/`, performs safe-mode state transitions, and closes the filesystem.

State and persistence behavior: safe mode reflects SCM runtime state rather than file metadata. Force exit changes SCM safe mode status, but container allocation still fails due to absent datanodes, proving the test did not restart capacity.

Dependencies and integration points: uses Hadoop `SafeMode` and `SafeModeAction`, `MiniOzoneClusterProvider`, `StorageContainerManager` writable container factory, `RatisReplicationConfig`, and O3FS/OFS URI schemes.

Risks: depends on cluster restart semantics and datanode shutdown behavior. Allocation failure is used as a secondary check that force exit does not imply datanode availability.

Test signals: catches missing SafeMode implementation on filesystem classes, incorrect propagation of SCM safe mode, and broken force-exit handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContract.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContract.java

Purpose: base Hadoop filesystem contract wrapper for Ozone-backed tests.

Important APIs/types/functions: extends `AbstractFSContract`, stores a `MiniOzoneCluster`, declares abstract `getRootURI`, exposes `getCluster`, and implements `getTestFileSystem` by setting `fs.defaultFS` to the concrete Ozone root URI and returning `FileSystem.get(getConf())`.

Control flow: concrete contract supplies the URI; this base validates the cluster exists, mutates the contract configuration, and opens the filesystem.

State and persistence behavior: no Ozone metadata is created here directly. It controls client configuration state used by downstream contract tests.

Dependencies and integration points: integrates Hadoop contract test framework with `MiniOzoneCluster` and Ozone concrete contract classes such as `OzoneContract` and rooted variants.

Risks: `fs.defaultFS` is mutated on the shared contract configuration, so concrete tests must supply an isolated or stable configuration. If `getRootURI` creates buckets, that side effect is owned by the subclass.

Test signals: failures here usually mean cluster setup or URI construction is broken before contract tests can run.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContractTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContractTest.java

Purpose: shared JUnit 5 host for Hadoop filesystem contract tests against a single `MiniOzoneCluster`, using nested classes to run create, delete, status, mkdir, open, rename, root, seek, unbuffer, distcp, and lease-recovery contracts.

Important APIs/types/functions: `createOzoneContract(Configuration)` is implemented by subclasses. `createOzoneConfig` builds base Ozone config and adds `contract/ozone.xml`; `createCluster` starts a five-DN mini cluster. Nested classes override `createConfiguration` and `createContract` for each Hadoop contract suite. OFS root-directory tests use AssertJ assumptions to skip cases unsupported by rooted OFS. Lease recovery contract tests run only when default bucket layout is FSO.

Control flow: `ClusterForTests` manages cluster lifecycle. Each nested contract class creates a fresh configuration but points to the same cluster-backed Ozone contract. The DistCp nested class additionally cleans local test directories in teardown.

State and persistence behavior: nested tests create and mutate filesystem state according to Hadoop contract expectations. Root-directory tests avoid unsupported recursive volume/root deletion paths for OFS. Lease recovery is gated to FSO because only that layout supports the tested recovery semantics.

Dependencies and integration points: depends on Hadoop contract test classes, `AbstractContractDistCpTest`, `ClusterForTests`, Ozone bucket layout config, OFS URI scheme, and `contract/ozone.xml` behavior declarations.

Risks: contract tests are broad and may exercise unsupported Hadoop assumptions; skip assumptions document known OFS differences. Shared cluster speeds execution but can make poor cleanup visible across nested suites.

Test signals: provides broad compatibility coverage for Hadoop `FileSystem` contract behavior and pinpoints where Ozone intentionally diverges for OFS root operations or non-FSO lease recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/AbstractOzoneContractTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/OzoneContract.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/OzoneContract.java

Purpose: concrete Hadoop filesystem contract implementation for O3FS.

Important APIs/types/functions: final class extends `AbstractOzoneContract`; `getScheme` returns `o3fs`; `getTestPath` returns `/test`; `getRootURI` creates a volume and bucket using the configured default bucket layout and returns `o3fs://bucket.volume/`.

Control flow: when a contract test requests the test filesystem, the base class calls `getRootURI`; this class opens an `OzoneClient`, creates a fresh volume/bucket, formats the O3FS URI, and closes the client.

State and persistence behavior: each root URI creation persists a test volume and bucket in the mini cluster. The bucket layout follows `ozone.default.bucket.layout` from the contract configuration, defaulting to `BucketLayout.DEFAULT`.

Dependencies and integration points: uses `TestDataUtil.createVolumeAndBucket`, `OzoneClient`, `OzoneBucket`, `OzoneConsts.OZONE_URI_SCHEME`, and `OZONE_DEFAULT_BUCKET_LAYOUT`.

Risks: root URI creation has side effects and can leave buckets if contract cleanup misses them. Layout-dependent contract behavior is controlled externally by config.

Test signals: enables the abstract contract suite to validate O3FS semantics for the configured bucket layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/OzoneContract.java -->
