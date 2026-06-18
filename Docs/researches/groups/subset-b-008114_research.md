# subset-b-008114 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeCreateResponse.java

Purpose: Tests `OMVolumeCreateResponse` persistence for successful and failed CreateVolume responses. Important APIs and types include `OMMetadataManager`, `BatchOperation`, `OmVolumeArgs`, `PersistedUserVolumeInfo`, protobuf `OMResponse`, and `CreateVolumeResponse`.

Control flow: The inherited base test creates a temporary OM RocksDB and batch. The success test builds a random volume, owner user, user-volume list, and successful `OMResponse`, calls `addToDBBatch`, manually commits the batch, and verifies `volumeTable` and `userTable`. The no-op test builds a failed `VOLUME_ALREADY_EXISTS` response, calls `checkAndUpdateDB`, and expects no rows.

State and persistence behavior: The test is specifically about deferred batch writes into `volumeTable` and `userTable`; nothing should be visible as accepted state until `commitBatchOperation`. Dependencies and integration points are OM response replay, metadata table key generation, protobuf status handling, and RocksDB batch semantics.

Risks: The test assumes object equality for `OmVolumeArgs` and `PersistedUserVolumeInfo` is stable and that failed responses do not mutate DB state. Test signals are exact table row counts and matching stored values after commit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeDeleteResponse.java

Purpose: Tests `OMVolumeDeleteResponse` batch behavior for deleting a volume and its user-volume mapping. Important APIs and types include `OMVolumeCreateResponse` for setup, `OMVolumeDeleteResponse`, `OMMetadataManager`, `PersistedUserVolumeInfo`, `OmVolumeArgs`, and delete-volume `OMResponse`.

Control flow: The success test stages a volume create and a volume delete in the same batch. The delete response carries an updated empty `PersistedUserVolumeInfo`, then the batch is committed and both volume and user entries are expected to be gone. The no-op path uses failed `VOLUME_NOT_FOUND` status and verifies `checkAndUpdateDB` does not throw.

State and persistence behavior: This exercises deletion from `volumeTable` and removal of the `userTable` row when a user has no remaining volumes. It depends on OM DB key construction for volume/user keys and on ordered batch operations.

Risks: The success path composes create and delete in one batch, so it validates final batch state but not visibility between operations. Test signals are null reads from `volumeTable` and `userTable`, plus no exception for unsuccessful replay.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeResponse.java

Purpose: Shared fixture for OM volume response tests. It provides a temporary on-disk OM metadata store and a reusable DB batch for subclasses.

Important APIs and types: `@TempDir`, `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, `OmMetadataManagerImpl`, `OMMetadataManager`, and `BatchOperation`.

Control flow: `setup` creates an `OzoneConfiguration`, points OM DB directories at the JUnit temp path, constructs `OmMetadataManagerImpl`, and initializes a batch operation from the store. `tearDown` closes the batch when present. Protected getters expose the metadata manager and batch to tests.

State and persistence behavior: The fixture creates a real local RocksDB-backed metadata manager, not just mocks, so subclasses verify actual table and batch semantics. The only persistent state is temporary test DB data scoped to each test.

Risks: The batch is shared per test method and must be manually committed by subclasses that expect durable results. Test signal is indirect: subclasses rely on this setup to produce isolated metadata state and avoid leaking open batch resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetOwnerResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetOwnerResponse.java

Purpose: Tests `OMVolumeSetOwnerResponse` persistence when a volume owner changes and when a failed set-property response is replayed. Important APIs and types include `OMVolumeCreateResponse`, `OMVolumeSetOwnerResponse`, `OmVolumeArgs`, `PersistedUserVolumeInfo`, `Table.KeyValue`, and set-volume-property `OMResponse`.

Control flow: The success test creates an initial volume for `user1`, constructs new owner metadata for `user2`, stages create plus owner-change responses in one batch, commits, and then verifies the volume row key/value and the new owner's user-volume row. The no-op test uses `VOLUME_NOT_FOUND`, calls `checkAndUpdateDB`, and expects the volume table to stay empty.

State and persistence behavior: The response updates `volumeTable` and transitions ownership metadata in `userTable`, including removal or replacement of old-owner volume state. Integration points are owner/admin fields in `OmVolumeArgs`, user-volume protobuf persistence, and OM response batch replay.

Risks: Assertions focus on the new owner and table count; they do not separately assert old-owner row absence. Test signals are the exact volume key, updated `OmVolumeArgs`, new-owner user list, and zero rows for failed replay.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetOwnerResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetQuotaResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetQuotaResponse.java

Purpose: Tests `OMVolumeSetQuotaResponse` as a volume-table update response. Important APIs and types include `OMVolumeSetQuotaResponse`, `OmVolumeArgs`, `OMMetadataManager`, `BatchOperation`, `Table.KeyValue`, and set-volume-property protobuf responses.

Control flow: The success test builds a volume argument object and successful response, calls `addToDBBatch`, commits manually, and verifies exactly one `volumeTable` row with the expected metadata key and value. The no-op path builds a failed response, calls `checkAndUpdateDB`, and expects no volume-table rows.

State and persistence behavior: The response writes only `volumeTable`; user-volume mapping is not part of quota updates. The test validates that batch replay can upsert full `OmVolumeArgs` metadata and that failed response replay is inert.

Dependencies and integration points: OM response status, volume table key construction, RocksDB batch commit, and quota/property mutation response logic. Risks are that the test does not inspect individual quota fields, only full object equality. Test signals are volume table row count, key equality, value equality, and zero rows after failed replay.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetQuotaResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/package-info.java

Purpose: Package descriptor for OM volume response tests. It documents the package as testing volume functions under `org.apache.hadoop.ozone.om.response.volume`.

Important APIs and types: There are no executable types or methods. The file only contains package Javadoc and the package declaration.

Control flow: None.

State and persistence behavior: None. This file does not touch metadata tables, batches, RocksDB, or response classes.

Dependencies and integration points: The descriptor attaches documentation to the Java package that contains tests for create, delete, set-owner, and set-quota OM volume response replay. Risks are documentation-only: if the package purpose broadens, the short Javadoc may become underspecified. Test signals are not applicable; compilation/package documentation is the only effect.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestCompactionService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestCompactionService.java

Purpose: Unit-tests `CompactionService` table selection and periodic execution without running real RocksDB compaction. Important APIs and types include `CompactionService`, mocked `OzoneManager`, `OMMetadataManager`, `TypedTable`, compaction config keys, `GenericTestUtils.waitFor`, and `ExitUtils`.

Control flow: `setup` enables compaction, configures a tiny interval, mocks OM metadata table lookup/listing, and exposes a set of valid table names. Tests create an anonymous `CompactionService` overriding `compactFully` to log only. Success starts/suspends/resumes the service and waits for `getNumCompactions`. Invalid-table coverage confirms mixed valid/invalid config keeps valid tables and all-invalid config throws.

State and persistence behavior: The service maintains in-memory counters, table-name filtering, and background scheduling state. No real table data is compacted. Dependencies and integration points are OM table registry, service lifecycle methods, configured column-family lists, and periodical task scheduling.

Risks: Timing uses millisecond intervals and short sleeps; failures can be scheduler-sensitive. Test signals are compaction count growth, compactable table membership, invalid table exclusion, and constructor exception for no valid tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestCompactionService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingService.java

Purpose: Tests FSO directory deletion service behavior, configured concurrency, live reconfiguration, and Ratis request batching. Important APIs and types include `DirectoryDeletingService`, `DirDeletingTask`, `OmTestManagers`, `KeyManager`, `OzoneManagerProtocol`, `OMRequestTestUtils`, FSO `OmDirectoryInfo`/`OmKeyInfo`, `ThreadPoolExecutor`, and `PurgeDirectoriesRequest`.

Control flow: The size-limit test creates one FSO directory and 2000 child files with long names, recursively deletes the directory through the write client, and waits for moved-file counters. The multithread test verifies the deletion executor core size, submits latch-blocked tasks to prove parallelism, then exercises `processDeletedDirsForStore`. `testUpdateAndRestart` applies new thread-count and interval config. The batching test spies `submitRequest`, feeds many large purge paths, and asserts multiple bounded `PurgeDirectories` requests.

State and persistence behavior: Tests write real OM metadata tables for FSO directories/files, deleted-directory state, and service counters. Integration points include recursive delete request handling, OM Ratis byte limits, key manager service wiring, and executor lifecycle.

Risks: Background waits and executor counts are timing-sensitive. Batching assertions depend on protobuf serialized sizes. Test signals are moved-file/run counters, exact thread pool sizing, restarted interval, captured request count, command type, and payload bytes under the configured limit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestKeyDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestKeyDeletingService.java

Purpose: Large integration-style unit suite for `KeyDeletingService` across active-object-store deletion, SCM block deletion, snapshots, rename tracking, deep cleaning, metrics, failure behavior, and purge batching. Important APIs and types include `KeyDeletingService`, `DirectoryDeletingService`, `SstFilteringService`, `OmTestManagers`, `ScmBlockLocationTestingClient`, `PendingKeysDeletion`, `ReclaimableKeyFilter`, `SnapshotInfo`, `SnapshotChainManager`, `OzoneManagerRatisUtils`, `DeletingServiceMetrics`, and OM key/delete/rename tables.

Control flow: Nested `Normal`, `Failing`, `Metrics`, and `RequestBatching` classes build OM managers with either successful or failing SCM block clients. Helpers create volumes, buckets, open/commit/delete keys, rename keys, and count pending blocks. Tests verify normal deletion, zero-block filtering, multiple key versions, snapshot-retained deletes, concurrent snapshot creation while deletion is running, renamed-key reclamation, snapshot deep clean, skipping active snapshot retrieval for already deep-cleaned snapshots, exclusive-size accounting, SCM failure retention, partial-commit cleanup, 24-hour metrics, and `PurgeKeys` request splitting by Ratis byte limit.

State and persistence behavior: The suite heavily mutates OM metadata: key table, deleted table, snapshot info table, snapshot renamed table, bucket quota/snapshot usage counters, snapshot-local metadata, and purge requests. It also tracks in-memory service run/deleted counters and mocked/static Ratis submission outcomes.

Dependencies and integration points: OM write client APIs, SCM block deletion, snapshot manager/cache, Ratis request path, deep-clean directory service, SST filtering, replication-size calculation, and metrics. Risks are timing, snapshot flush ordering, static mocks, and flaky deep-clean behavior. Test signals include pending deletion emptiness or retention, SCM deleted-block counts, table row counts, snapshot usage/exclusive sizes, metric counters, and captured purge request sizes/counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestKeyDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestMultipartUploadCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestMultipartUploadCleanupService.java

Purpose: Tests that `MultipartUploadCleanupService` finds expired incomplete multipart uploads and submits abort cleanup for both default and FSO bucket layouts. Important APIs and types include `MultipartUploadCleanupService`, `KeyManager.getExpiredMultipartUploads`, `ExpiredMultipartUploadsBucket`, `OmMultipartInfo`, `OpenKeySession`, `OMRequestTestUtils`, `BucketLayout`, and MPU config keys.

Control flow: Class setup creates an OM test manager with short cleanup interval, short expiration threshold, and high per-task part cleanup limit. The parameterized test suspends the service, records counters, creates incomplete MPU keys in default and/or FSO buckets, optionally commits random parts, waits past expiration, verifies expired uploads are visible, resumes the service, and waits until no expired uploads remain.

State and persistence behavior: Test data persists volume/bucket rows, multipart info rows, open MPU part keys, and committed MPU part metadata. Cleanup changes OM metadata through normal abort/cleanup service paths and increments submitted MPU counters.

Dependencies and integration points: MPU initiate/open/commit part APIs, bucket layout-specific metadata tables, expiration scanning, service scheduling, and OM write client behavior. Risks include random distribution of volumes/buckets/part counts and short sleep-based expiration. Test signals are non-empty then empty expired-upload lists, increased service run count, and submitted MPU count at least equal to created uploads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestMultipartUploadCleanupService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestOpenKeyCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestOpenKeyCleanupService.java

Purpose: Tests `OpenKeyCleanupService` expiration behavior for ordinary open keys, hsync lease recovery, recovery-in-progress hsync keys, and multipart-upload open part keys across default and FSO layouts. Important APIs and types include `OpenKeyCleanupService`, `ExpiredOpenKeys`, `OMMetrics`, `OzoneManagerProtocol`, `OpenKeySession`, `OmMultipartInfo`, `BucketLayout`, lease config keys, and mocked SCM container pipeline lookup.

Control flow: Setup enables HBase enhancements and hsync with very short hard lease and cleanup thresholds. Parameterized tests create open keys, wait for expiration, verify expired-key discovery, resume cleanup, and wait for table cleanup/counter increments. Hsync tests mock an open pipeline, ensure expired recoverable hsync keys are auto-committed, ensure keys with recovery flag remain open, and verify directory path file names. MPU tests ensure committed MPU open keys are excluded, while uncommitted MPU part keys are cleaned.

State and persistence behavior: The suite manipulates open key tables, key tables, multipart tables, metrics counters, lease recovery flags, and allocated block metadata. Dependencies include OM lease semantics, hsync commit path, bucket layout table selection, MPU metadata distinction, and SCM container client.

Risks: Ordered tests share one OM instance and use sleep-based expiration. Test signals are expired-key counts, open/key table emptiness or retained recovery keys, submitted-open-key count, hsync/open cleanup metrics, and preserved MPU parent keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestOpenKeyCleanupService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestQuotaRepairTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestQuotaRepairTask.java

Purpose: Tests `QuotaRepairTask` and its generated `OMQuotaRepairRequest`/`OMQuotaRepairResponse` against object-store and FSO buckets plus old quota sentinel values. Important APIs and types include `QuotaRepairTask`, `OMQuotaRepairRequest`, `OMQuotaRepairResponse`, mocked `OzoneManagerRatisServer`, `BatchOperation`, `OmBucketInfo`, `OmVolumeArgs`, `OmKeyInfo`, and `OMRequestTestUtils`.

Control flow: The main test adds an OBS bucket with 10 keys and an FSO bucket with parent directories plus 10 files, zeros bucket usage, runs repair, captures the submitted Ratis request, validates it through OM request code, applies the response batch, and checks recomputed namespace/bytes. The old-version test creates volume/bucket quota values of `-2`, runs repair, applies the response, and expects migration to `-1`.

State and persistence behavior: It directly populates key/file/dir/bucket/volume tables and cache entries, then repairs bucket usage and quota flags via the same request/response flow used in OM. Dependencies are quota calculation, replication factor accounting, FSO namespace counting, Ratis submission, and DB batch persistence.

Risks: Direct table insertion bypasses normal request side effects by design. Test signals are successful repair future, captured request, updated OBS usage `10/30000`, FSO usage `13/10000`, and old quota flags converted to `-1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestQuotaRepairTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingService.java

Purpose: Unit-tests snapshot deletion decision logic and request batching for moving deleted snapshot table entries. Important APIs and types include `SnapshotDeletingService`, `SnapshotDeletingTask`, `SnapshotInfo`, `TransactionInfo`, `SnapshotMoveKeyInfos`, `OMRequest`, `OMConfigKeys.OZONE_OM_RATIS_LOG_APPENDER_QUEUE_BYTE_LIMIT`, and mocked OM metadata/snapshot managers.

Control flow: `testProcessSnapshotLogicInSDS` parameterizes flushed/unflushed snapshots and active/deleted status, stubs transaction info for deleted snapshots, and asserts `shouldIgnoreSnapshot`. `testSnapshotMoveKeysRequestBatching` creates large deleted-key, renamed-key, and deleted-directory payloads, spies `submitRequest`, calls `submitSnapshotMoveDeletedKeysWithBatching`, and verifies all entries are submitted across multiple bounded requests.

State and persistence behavior: The tests use mocked managers rather than real RocksDB. State is protobuf request payloads, snapshot status fields, transaction info, and captured submitted requests. Integration points are snapshot GC eligibility, SST-filter/flush markers, active versus deleted status, Ratis buffer sizing, and snapshot move-table request structure.

Risks: Large string helpers assume serialized sizes exceed the test buffer and remain below per-batch limits after splitting. Test signals are boolean ignore decisions, total submitted entry count, multiple captured `SnapshotMoveTableKeys` requests, size under limit, and no orphaned deleted/renamed/dir entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDiffCleanupService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDiffCleanupService.java

Purpose: Tests `SnapshotDiffCleanupService` cleanup of snapshot diff jobs and report rows in RocksDB column families. Important APIs and types include `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, `SnapshotDiffJob`, `SnapshotDiffReportOzone.DiffReportEntry`, `SnapshotDiffResponse.JobStatus`, and snapshot diff cleanup config keys.

Control flow: Static setup opens a temporary RocksDB. Each test creates active job, purged job, and report column families, registers codecs, and constructs the service with mocked config. The main test inserts DONE, stale DONE, QUEUED, IN_PROGRESS, FAILED, and REJECTED jobs with report rows. First run moves terminal/stale jobs into the purged table; second run removes their report rows and purged markers. A separate test verifies zero-entry purged jobs can still remove stray report rows.

State and persistence behavior: This is real RocksDB column-family persistence with raw codec serialization. The service transitions rows from active job table to purged job table, then deletes report table entries.

Dependencies and integration points: Snapshot diff job status lifecycle, report retention duration, max purge count, filesystem snapshot enablement, RocksDB iterators, and codec compatibility. Risks include manual column-family lifecycle and exact table counts. Test signals are row counts, job presence/absence, purged entry counts, and report byte equality/nullness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDiffCleanupService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotFeatureEnabledUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotFeatureEnabledUtil.java

Purpose: Tiny test utility for the snapshot feature-enabled aspect. It provides a method annotated with `@RequireSnapshotFeatureState(true)` and a public feature-state accessor.

Important APIs and types: `RequireSnapshotFeatureState`, `snapshotMethod()`, and `isFilesystemSnapshotEnabled()`.

Control flow: `snapshotMethod` returns a constant string if invoked. `isFilesystemSnapshotEnabled` always returns `false`, intentionally modeling an object whose snapshot feature gate is disabled.

State and persistence behavior: No mutable state and no persistence. The utility exists to drive aspect/reflection behavior in tests outside this file.

Dependencies and integration points: The aspect under test must discover the annotation and reflectively call a public `isFilesystemSnapshotEnabled` method, mirroring `OzoneManager#isFilesystemSnapshotEnabled`. Risks are limited to method visibility/signature: changing either can break aspect tests. Test signals are indirect: aspect tests should block or allow `snapshotMethod` based on the false feature state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotFeatureEnabledUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTestUtils.java

Purpose: Provides in-memory implementations of snapshot persistent collection interfaces for tests. Important APIs and types include `PersistentMap`, `PersistentSet`, `PersistentList`, `ClosableIterator`, `CodecRegistry`, Guava unsigned byte comparator, `TreeMap`, `TreeSet`, and `ArrayList`.

Control flow: A codec-backed comparator serializes keys to raw bytes and orders them lexicographically as unsigned bytes, matching RocksDB-style ordering more closely than Java object comparison. `StubbedPersistentMap` supports get/put/remove and bounded iteration with optional lower/upper keys. `StubbedPersistentSet` supports add and iteration. `ArrayPersistentList` extends `ArrayList`, implements persistent-list `addAll`, and returns closeable iterators.

State and persistence behavior: State is purely in memory, but ordering and iterator APIs emulate persistent snapshot data structures. No files or RocksDB instances are used.

Dependencies and integration points: Snapshot diff/local-data tests can use these classes where production code expects persistent interfaces. Risks include codec serialization failures and simplified close/no-resource behavior. Test signals are deterministic ordering, range filtering, add/remove semantics, and compatibility with `ClosableIterator`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestFSODirectoryPathResolver.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestFSODirectoryPathResolver.java

Purpose: Tests `FSODirectoryPathResolver` reconstruction of absolute FSO directory paths from object IDs. Important APIs and types include mocked `Table<String, OmDirectoryInfo>`, `Table.KeyValueIterator`, `OmDirectoryInfo`, `Optional<Set<Long>>`, `Path`, and `OM_KEY_PREFIX`.

Control flow: The helper returns a mocked directory table whose prefix iterator decodes the requested parent object ID and yields child directory rows from an in-memory parent-to-children map. The test builds a multi-level tree, asks for paths for selected object IDs, compares the returned map to expected absolute paths, then includes an unreachable ID and expects `IllegalArgumentException`.

State and persistence behavior: All directory metadata is mocked/in-memory. The resolver state under test is traversal from bucket root object ID through directory table prefixes to build object-ID-to-path mappings.

Dependencies and integration points: FSO directory table key format, object ID hierarchy, path normalization, and snapshot diff/path reporting that needs human-readable paths. Risks are that the mock table only models iterator-by-prefix behavior needed by this resolver. Test signals are exact path mapping for root and nested IDs, result size, and exception message for missing IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestFSODirectoryPathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestMultiSnapshotLocks.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestMultiSnapshotLocks.java

Purpose: Tests `MultiSnapshotLocks`, the helper for acquiring/releasing write locks for multiple snapshot IDs. Important APIs and types include `IOzoneManagerLock`, `OzoneManagerLock.LeveledResource`, `SNAPSHOT_GC_LOCK`, `OMLockDetails`, `OMException`, and UUID collections.

Control flow: One test uses a real `OzoneManagerLock` and two `MultiSnapshotLocks` instances to repeatedly acquire/release different snapshot locks. Mock-based tests verify successful acquisition delegates once to `acquireWriteLocks`, failed acquisition clears internal state, release delegates to `releaseWriteLocks` and empties tracked locks, and attempting to acquire again before release throws an `OMException` with current lock IDs.

State and persistence behavior: State is in-memory lock ownership within `MultiSnapshotLocks`; there is no filesystem or DB state. Integration points are OM lock manager multi-resource APIs and snapshot GC locking resources.

Risks: Mock tests validate delegation and local state, not actual deadlock ordering beyond the real-lock smoke loop. Test signals are acquired flags, empty/non-empty object-lock set, verified acquire/release calls, and exact exception message for reentrant acquisition.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestMultiSnapshotLocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMSnapshotDirectoryMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMSnapshotDirectoryMetrics.java

Purpose: Tests `OMSnapshotDirectoryMetrics` filesystem scanning for snapshot directories and SST backup directories. Important APIs and types include `OMMetadataManager`, mocked `RDBStore`, mocked `RocksDBCheckpointDiffer`, `OzoneConfiguration`, `ROCKSDB_SST_SUFFIX`, Java `Files`, and hardlink creation.

Control flow: Setup points mocked store methods at temporary snapshot and backup directories. The test creates one snapshot directory with one `.sst` file, two backup `.sst` files, updates metrics, and asserts snapshot count, SST counts, and sizes. It then creates a second snapshot with a hardlink to the first SST file, updates metrics again, and expects deduplicated snapshot SST count/size. Finally it adds a non-SST backup file and verifies backup directory size includes it while backup SST count stays unchanged.

State and persistence behavior: Uses real temporary filesystem files and links, but no OM DB data. Metrics state is recomputed from directory contents.

Dependencies and integration points: Snapshot checkpoint directory layout, SST suffix filtering, hardlink-aware size/count handling, and checkpoint differ backup path. Risks include filesystems without hardlink support, handled by fallback write. Test signals are exact metric counts and byte totals after each update.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMSnapshotDirectoryMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotLocalDataManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotLocalDataManager.java

Purpose: Comprehensive unit suite for `OmSnapshotLocalDataManager`, which manages per-snapshot YAML local metadata, version chains, SST file metadata, defrag state, transaction info, orphan-version cleanup, and locking. Important APIs and types include `OmSnapshotLocalDataManager`, readable/writable providers, `OmSnapshotLocalData`, `YamlSerializer`, `SnapshotInfo`, `TransactionInfo`, `LiveFileMetaData`, `SstFileInfo`, `HierarchicalResourceLockManager`, `DAGLeveledResource.SNAPSHOT_LOCAL_DATA_LOCK`, `OMLayoutVersionManager`, and static `OmSnapshotManager` helpers.

Control flow: Setup mocks OM metadata store paths, hierarchical locks, layout feature checks, snapshot purge checks, and snapshot RocksDB live-file metadata. Tests cover lock ordering when resolving a snapshot against prior snapshots, previous-version resolution, validation of writes when predecessor versions are missing, transaction info updates, adding new versions from RocksDB live files, orphan version deletion after version removal or chain update, chain rewrites and defrag flags, version removal protection while dependents exist, version-resolution maps across snapshot chains, YAML path construction, YAML creation/overwrite/content filtering, mismatched snapshot ID failures, loading existing YAML files, missing YAML upgrade behavior, stale snapshot-chain purge regression, invalid YAML path rejection, close behavior, and purged-last-snapshot cleanup not being requeued.

State and persistence behavior: The suite writes real YAML files under the temporary snapshots directory, builds in-memory version-node maps, records lock acquisition/release order, stores transaction info and SST version maps, and may delete YAML for purged snapshots. It also mocks snapshot DB live SST metadata and layout upgrade gates.

Dependencies and integration points: Snapshot local YAML schema/checksum, OM snapshot path naming, RocksDB live-file metadata, snapshot chain manager, purge detection, layout feature `SNAPSHOT_DEFRAG`, hierarchical locks, and defrag/orphan maintenance. Risks are high because behavior depends on chain ordering, previous-version math, file paths, static mocks, and cleanup side effects. Test signals include exact lock traces, YAML existence/content, version sets/maps, previous snapshot IDs, `needsDefrag`, transaction info persistence, expected exceptions, version-node map membership, and orphan-check queue contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotLocalDataManager.java -->
