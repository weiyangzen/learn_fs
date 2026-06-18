# Research: subset-b-008105

Grouped source research for Apache Ozone OM snapshot diff, snapshot defrag, snapshot reclaim filters, OM upgrade gating, and OM admin/inter-service PB adapters. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManager.java

Purpose: `SnapshotDiffManager` is the OM-private service that accepts snapshot diff submissions, tracks job state, computes diff reports asynchronously, pages persisted report entries back to clients, supports cancellation/listing, and exposes job state through JMX.

Important APIs and types: it implements `AutoCloseable` and `SnapshotDiffManagerMXBean`. Public entry points are `submitSnapshotDiff`, `getSnapshotDiffReport`, deprecated submit-on-read `getSnapshotDiffReport(... forceFullDiff, disableNativeDiff)`, `cancelSnapshotDiff`, `getSnapshotDiffJobList`, `getSnapshotDiffJobs`, and static helpers `getSnapshotRootPath`, `getReportKeyForIndex`, and `getIndexFromReportKey`. Internally it uses `SnapshotDiffJob`, `SnapshotDiffResponse`, `SnapshotDiffReportOzone`, HDFS `DiffReportEntry`, `PersistentMap`, `ManagedRocksDB`, temporary RocksDB column families, and `CompositeDeltaDiffComputer`.

Control flow: construction reads snapshot diff configuration, initializes persistent job/report maps from supplied column families, creates a bounded `ThreadPoolExecutor`, recreates the snap-diff SST backup directory, optionally loads raw SST native libraries, reloads in-progress jobs, and registers an MXBean. Submission resolves both snapshots, derives a stable job key from their UUIDs, creates or reuses a job row, moves eligible jobs to `IN_PROGRESS`, and schedules `generateSnapshotDiffReport`. Report reads return status-only responses for queued/in-progress/rejected/failed/cancelled jobs and page through persisted `DONE` entries for completed jobs. Generation validates that both snapshots and the job are still active before each heavy phase, opens both snapshot DBs, creates job-scoped intermediate column families, computes candidate delta SST files for key and FSO directory tables, fills object-ID-to-key maps, resolves FSO parent paths, emits ordered diff entries, and marks the job done.

State and persistence: durable state lives in `snapDiffJobTable`, `snapDiffReportTable`, and `snapDiffPurgedJobCfh`. Report keys are `jobId + delimiter + diffTypeOrdinalPrefix + zeroPaddedIndex`, enforcing delete, rename, create, modify ordering independent of generation order. Temporary object maps are persisted in transient RocksDB column families named with the job id and dropped in `finally`. `sstBackupDirForSnapDiffJobs/jobId` stores hard links to SSTs while a job runs so RocksDB checkpoint differ pruning cannot delete files needed by the job. Failed/retried jobs enqueue previous job ids in the purged-job CF for cleanup.

Dependencies and integration: the manager is wired to `OzoneManager`, `OMMetadataManager`, `OmSnapshotManager`, `RocksDBCheckpointDiffer`, snapshot chain state via `SnapshotUtils`, `FSODirectoryPathResolver`, `TableMergeIterator`, and Ozone metrics. It is sensitive to bucket layout, using key tables for OBS/legacy and both key and directory tables for FSO. Native raw SST reading controls whether tombstones are visible directly or the diff must compensate with fuller input sets.

Risks and edge cases: job state updates are synchronized but background work can still race with cancellation or snapshot purge, so `areDiffJobAndSnapshotsActive` checks are central. `updateJobStatusToFailed` assumes the job is still `IN_PROGRESS`; if another thread cancels first, failure handling can throw. Integrity checking marks a done job failed if the last paged entry does not match `largestEntryKey`. `resolveBucketRelativePath` can throw for unresolved FSO parents unless the caller explicitly skips unresolved IDs; skipped unresolved objects can hide entries during concurrent delete chains. The estimated-key limit depends on SST estimates, not exact counts. Loading in-progress jobs on every OM node is intentionally inefficient until HA-aware snapshot diff exists.

Test signals: focused tests should cover report key ordering and pagination tokens, duplicate submission and executor rejection paths, cancellation during each generation phase, failed/retry cleanup enqueueing, OBS versus FSO path resolution, native versus non-native SST reading, max-key-limit rejection, JMX job listing, and integrity check failure. Existing `@VisibleForTesting` methods indicate intended seams: `createPageResponse`, `checkReportsIntegrity`, `addToObjectIdMap`, `generateDiffReport`, `getBucketLayout`, `isKeyInBucket`, and `loadJobsOnStartUp`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManagerMXBean.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManagerMXBean.java

Purpose: JMX contract for exposing snapshot diff jobs from `SnapshotDiffManager`.

Important APIs and types: declares one method, `List<SnapshotDiffJob> getSnapshotDiffJobs()`, with `@InterfaceAudience.Private`.

Control flow and state: no implementation or persistence; the implementing manager iterates its persistent job table and returns job values.

Dependencies and integration: used by Hadoop `MBeans` registration in `SnapshotDiffManager`, under the `OzoneManager/SnapshotDiffManager` bean name.

Risks and test signals: callers receive all jobs, so large job tables may make JMX reads expensive. Tests should verify MXBean registration delegates to the same job table used by API listing and unregisters on manager close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotDiffManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotUtils.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotUtils.java

Purpose: utility holder for common snapshot lookup, activity validation, chain traversal, deleted-table merge, previous-snapshot validation, and key block-location comparison.

Important APIs and types: `getSnapshotInfo` overloads resolve snapshots by volume/bucket/name, table key, or UUID plus `SnapshotChainManager`; `checkSnapshotActive` validates `SNAPSHOT_ACTIVE`; `getNextSnapshot`, `getPreviousSnapshot`, and `getPreviousSnapshotId` navigate path chains; `createMergedRepeatedOmKeyInfoFromDeletedTableEntry` merges snapshot move protobuf key versions into deleted table entries; `getLatestSnapshotInfo` and `getLatestPathSnapshotId` query chain tails; `validatePreviousSnapshotId` enforces expected chain predecessor; `isBlockLocationInfoSame` compares key block lists, with an hsync object-ID shortcut.

Control flow: lookup functions read OM metadata tables and translate null/missing entries to `OMException(FILE_NOT_FOUND)`. Chain functions tolerate `NoSuchElementException` from in-memory chain lag after purge. Deleted-table merge converts protobuf key infos, reads any existing `RepeatedOmKeyInfo`, and appends only if the new list is not already the latest suffix. Block comparison handles nulls, hsync keys, version group counts, latest version locations, and per-block identity.

State and persistence: the class does not own state. It reads snapshot metadata, deleted table entries, and chain manager indexes; the deleted-table merge returns a value to be persisted by the caller.

Dependencies and integration: used broadly by diff generation, reclaim filters, defrag, purge, and request validation paths. It depends on `OzoneManager`, `OMMetadataManager`, `SnapshotChainManager`, OM protobufs, and `OmKeyInfo` location models.

Risks and edge cases: `dropColumnFamilyHandle` converts RocksDB failures into runtime exceptions. Chain helpers return null at chain ends, but some callers must handle null snapshot infos carefully. `createMergedRepeatedOmKeyInfoFromDeletedTableEntry` relies on list equality and suffix ordering to avoid duplicate replay additions. Hsync block comparison treats same object ID as same key even when block locations differ, which is intentional but should remain isolated to hsync semantics.

Test signals: cover missing snapshot table entries, inactive snapshots, chain races around purged snapshots, previous-id validation for AOS/null snapshot cases, idempotent deleted-table merge on replay, hsync versus non-hsync block comparison, and null/latest-location handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffDBDefinition.java

Purpose: defines the RocksDB schema for the standalone snapshot diff database.

Important APIs and types: singleton `SnapshotDiffDBDefinition.get()` extends `DBDefinition.WithMap`; names the DB via `OM_SNAPSHOT_DIFF_DB_NAME` and location config key `OZONE_OM_SNAPSHOT_DIFF_DB_DIR`. Column families include `snap-diff-job-table`, `snap-diff-report-table`, `snap-diff-purged-job-table`, and intermediate `-from-snap`, `-to-snap`, `-unique-ids`.

Control flow and persistence: the class builds an immutable CF map with codecs for `SnapshotDiffJob`, `DiffReportEntry`, `Long`, `SnapshotDiffObjectInfo`, and `Boolean`. Intermediate CF definitions are schema names, while runtime code prefixes them with job IDs for temporary per-job tables.

Dependencies and integration: consumed by `SnapshotDiffMetadataManagerImpl` and `SnapshotDiffManager` when creating/dropping temporary column families. Diff report entries use `SnapshotDiffReportOzone.getDiffReportEntryCodec`.

Risks and test signals: schema changes require versioning in `SnapshotDiffMetadataManagerImpl`; codec compatibility is critical for persisted jobs and reports. Tests should verify CF names, codecs, immutable map contents, DB name/location config, and that temporary CF suffixes match manager expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManager.java

Purpose: interface for accessing snapshot diff metadata tables.

Important APIs and types: extends `AutoCloseable` and exposes getters for job, report, purged-job, from-snapshot object-info, to-snapshot object-info, and unique-object-id tables.

Control flow and state: no implementation; it defines the table access contract used by callers that should not depend directly on `DBStore`.

Dependencies and integration: tied to `SnapshotDiffDBDefinition`, Hadoop `Table`, `SnapshotDiffJob`, HDFS `DiffReportEntry`, and `SnapshotDiffObjectInfo`.

Risks and test signals: implementations must return tables with codecs matching the DB definition and must close the backing store. Interface-level tests are minimal; integration tests should instantiate the implementation and round-trip every table type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManagerImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManagerImpl.java

Purpose: concrete `SnapshotDiffMetadataManager` backed by a `DBStore`, responsible for opening the snapshot diff DB and exposing typed table handles.

Important APIs and types: constructor takes `ConfigurationSource`; getters return typed `Table` instances; `close` closes `dbStore`. It uses `DBStoreBuilder`, `DBStoreBuilder.getDBDirPath`, `PARTIAL_CACHE`, and table definitions from `SnapshotDiffDBDefinition`.

Control flow: constructor computes the DB path, checks `VERSION`, deletes the entire DB directory when the content is absent or not equal to `"1"`, builds the DB store, opens each table with partial cache, and writes the version file when a new DB is created.

State and persistence: owns the snapshot diff RocksDB directory and a plain `VERSION` file. Persistence includes jobs, reports, purged jobs, and intermediate object tables.

Dependencies and integration: used by OM snapshot diff initialization and cleanup components. Its destructive version mismatch behavior is the operational boundary for incompatible schema upgrades.

Risks and edge cases: missing `VERSION` is treated as mismatch and deletes an existing DB path, which is acceptable only if old data is intentionally disposable or incompatible. Version file write happens after DB open; failures can leave a recreated DB without a version. Tests should cover new DB creation, matching-version open preserving data, mismatched-version deletion, missing-version behavior, table codec round trips, and close idempotence expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/SnapshotDiffMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/package-info.java

Purpose: package documentation for snapshot diff DB management classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.db` and documents that it contains classes for managing the snapshot diff DB.

State, risks, and test signals: no executable behavior. Test signal is documentation/package consistency with actual DB definition and metadata manager classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/SnapshotDefragService.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/SnapshotDefragService.java

Purpose: background service that rewrites active snapshot RocksDB checkpoints into less-fragmented versions, either by full prefix-trimming for the first path snapshot or by incremental SST ingestion for later snapshots.

Important APIs and types: extends `BackgroundService` and implements `BootstrapStateHandler`. Key methods are `start`, `pause`, `resume`, `triggerSnapshotDefragOnce`, `checkAndDefragSnapshot`, `needsDefragmentation`, `performFullDefragmentation`, `performIncrementalDefragmentation`, `ingestNonIncrementalTables`, `createCheckpoint`, `atomicSwitchSnapshotDB`, `getTasks`, and `shutdown`.

Control flow: construction creates a single-threaded background service, configures per-task snapshot limits, deletes/recreates `tmp_defrag`, creates a `CompositeDeltaDiffComputer`, and sets up snapshot content and bootstrap locks. Each task runs only when OM is running and `SNAPSHOT_DEFRAG` is finalized. Manual or scheduled execution iterates the global snapshot chain, checks active status and local `needsDefrag`, creates a checkpoint from the previous snapshot or itself, performs full or incremental defrag for tracked column families, acquires the snapshot content lock, ingests non-incremental tables from the original snapshot, atomically moves the checkpoint to the next version directory, updates local YAML metadata, and deletes old checkpoint directories.

State and persistence: persistent changes are new versioned snapshot DB directories and updates to `OmSnapshotLocalData` version metadata, including SST file info. Temporary state lives under `tmp_defrag` and `tmp_defrag/differSstFiles`; shutdown deletes this tree. Metrics count skipped, successful, failed, full, incremental, compacted tables, and delta files processed.

Dependencies and integration: uses `OmSnapshotManager`, `OmSnapshotLocalDataManager`, `SnapshotChainManager`, `CompositeDeltaDiffComputer`, `TableMergeIterator`, `RDBSstFileWriter`, RocksDB checkpoints, `COLUMN_FAMILIES_TO_TRACK_IN_SNAPSHOT`, `BOOTSTRAP_LOCK`, and `SNAPSHOT_DB_CONTENT_LOCK`. Admin RPC can trigger it through `OzoneManager.triggerSnapshotDefrag`.

Risks and edge cases: the service refuses to run without the rocks-tools native library. Full defrag deletes ranges outside the bucket prefix and force compacts tables; off-by-one range bounds could lose or retain unrelated data. Incremental defrag deletes all computed delta and spill files in `finally`, so ingestion failures must not require later reuse. `atomicSwitchSnapshotDB` moves directories and updates metadata; partial failures can leave checkpoint directories needing cleanup. Lock ordering and local metadata consistency are central to avoiding concurrent snapshot mutation.

Test signals: cover `needsDefragmentation` local metadata updates, full defrag range deletion/compaction bounds, incremental defrag single-file reingest versus spill path, tombstone spill behavior, non-incremental table prefix dumping, content-lock failure, atomic switch version metadata, old checkpoint deletion, no-native-library skip, layout-feature gating, snapshot limit handling, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/SnapshotDefragService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/package-info.java

Purpose: package documentation for snapshot defragmentation classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.defrag` and documents that it contains classes for defragmenting snapshots in Ozone Manager.

State, risks, and test signals: no executable behavior. Test signal is package documentation alignment with `SnapshotDefragService`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/defrag/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/CompositeDeltaDiffComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/CompositeDeltaDiffComputer.java

Purpose: orchestrates delta SST selection between snapshots, preferring checkpoint-differ DAG results and falling back to full SST comparison.

Important APIs and types: public constructor wires `RDBDifferComputer` when full diff is not forced, always wires `FullDiffComputer`, and accepts an activity reporter. Overrides `computeDeltaFiles` and `close`.

Control flow: attempts `RDBDifferComputer` with substatus `SST_FILE_DELTA_DAG_WALK`; on exception or empty result logs a warning and executes `FullDiffComputer` with substatus `SST_FILE_DELTA_FULL_DIFF`. If non-native diff mode is enabled, it also adds all relevant SSTs from the from-snapshot so delete/tombstone information is available to higher layers.

State and persistence: creates temporary hard links under child directories of the supplied delta directory and removes them on close through child computers and the superclass.

Dependencies and integration: used by `SnapshotDiffManager` and `SnapshotDefragService`. Depends on `OmSnapshotManager`, active metadata table prefixes, `SstFileInfo`, and raw/non-native SST read behavior.

Risks and test signals: fallback can be expensive and should preserve correctness. Non-native mode can enlarge delta input substantially. Tests should verify activity transitions, forced-full disabling of RDB differ, fallback on RDB differ exception, non-native addition of from-snapshot files, duplicate path handling in the returned map, and recursive cleanup on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/CompositeDeltaDiffComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/DeltaFileComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/DeltaFileComputer.java

Purpose: closeable strategy interface for computing SST files that can be scanned to derive table changes between two snapshots.

Important APIs and types: `Collection<Pair<Path, SstFileInfo>> getDeltaFiles(SnapshotInfo fromSnapshot, SnapshotInfo toSnapshot, Set<String> tablesToLookup) throws IOException`.

Control flow and state: no implementation; implementers may hold native resources or temp directories, hence `Closeable`.

Dependencies and integration: implemented by file-link based RDB/full/composite computers and consumed by snapshot diff and defrag logic.

Risks and test signals: callers assume returned paths are readable until `close`. Implementer tests should verify table filtering, empty-diff semantics, IOException propagation, and cleanup after close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/DeltaFileComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FileLinkDeltaFileComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FileLinkDeltaFileComputer.java

Purpose: abstract base for delta computers that materialize selected SST files as hard links in a temporary directory.

Important APIs and types: final `getDeltaFiles` resolves bucket table prefixes and delegates to abstract `computeDeltaFiles`; `createLink` creates unique numbered hard links preserving file extension; `getLocalDataProvider`, `getSnapshot`, `getActiveMetadataManager`, `updateActivity`, and `close` support subclasses.

Control flow: constructor creates the temp directory. `getDeltaFiles` maps subclass optional results to collection values and throws if no result can be computed. `createLink` loops on `FileAlreadyExistsException` using an atomic counter. `close` deletes the temp directory if present.

State and persistence: state is temporary filesystem hard links and an in-memory link counter. No durable metadata is written.

Dependencies and integration: base for `RDBDifferComputer`, `FullDiffComputer`, and `CompositeDeltaDiffComputer`; integrates with `OmSnapshotManager`, active metadata table-prefix lookup, and snapshot local data manager.

Risks and test signals: hard links require same filesystem and sufficient permissions; callers rely on deletion not touching source SSTs. Tests should cover unique link creation, extension preservation, missing source filename errors, optional-empty to IOException conversion, table-prefix lookup, and recursive cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FileLinkDeltaFileComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FullDiffComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FullDiffComputer.java

Purpose: exhaustive delta strategy that compares relevant SST files in two snapshot DBs and links all files unique to either side, with a fallback to all relevant files if inode-based comparison fails.

Important APIs and types: package-private subclass of `FileLinkDeltaFileComputer`; overrides `computeDeltaFiles`; static helpers `getSSTFileMapForSnapshot` and `getSSTFileSetForSnapshot`.

Control flow: opens both snapshots, obtains their DB locations, collects relevant SST metadata by table and prefix. Primary path compares maps keyed by inode/comparison identity and links only asymmetric files. On `IOException`, it clears results and links every relevant SST from both snapshots using set-based comparison metadata.

State and persistence: produces temporary hard links only. No durable state.

Dependencies and integration: uses `RdbUtil.getSSTFilesWithInodesForComparison`, `RdbUtil.getSSTFilesForComparison`, and `RocksDiffUtils.filterRelevantSstFiles`. Invoked by `CompositeDeltaDiffComputer` for forced diff or fallback.

Risks and test signals: fallback broadens the scan set and may duplicate source paths from both snapshots. Inode metadata can be unavailable on some filesystems. Tests should cover table-prefix filtering, unique-file linking, fallback path, empty diffs, link failures, and correct `SstFileInfo.getFilePath` base path use.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FullDiffComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/RDBDifferComputer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/RDBDifferComputer.java

Purpose: efficient delta strategy backed by `RocksDBCheckpointDiffer`, using snapshot local version metadata and the compaction DAG to identify changed SSTs.

Important APIs and types: package-private subclass of `FileLinkDeltaFileComputer`; overrides `computeDeltaFiles`; helper `toDifferSnapshotInfo` converts `SnapshotInfo` and `OmSnapshotLocalData` to `DifferSnapshotInfo`.

Control flow: obtains the active metadata store's checkpoint differ. For the target snapshot, opens local data resolved against the from-snapshot, constructs differ snapshot descriptors for both ends, builds a map from current version to previous snapshot version, synchronizes on the differ, asks for a full-path SST diff list filtered by table prefix and table names, and hard-links each returned path.

State and persistence: reads `OmSnapshotLocalData` version/SST metadata; creates temporary hard links; does not mutate durable state.

Dependencies and integration: used by `CompositeDeltaDiffComputer` when partial differ is enabled. Depends on correctly maintained snapshot version metadata from snapshot creation/defrag and on active `RocksDBCheckpointDiffer`.

Risks and test signals: missing previous snapshot local data or empty version maps turn into IO failures and cause composite fallback. Synchronization serializes differ use across callers. Tests should cover null differ, missing previous local data, empty versions, version-map construction, table filtering, synchronized differ invocation, and link creation for each returned SST.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/RDBDifferComputer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/package-info.java

Purpose: package documentation for snapshot delta-file computation.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.diff.delta` and documents that it contains classes to compute delta files between snapshots.

State, risks, and test signals: no executable behavior. Test signal is package documentation alignment with the `DeltaFileComputer` implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/SnapshotDiffObjectInfo.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/SnapshotDiffObjectInfo.java

Purpose: small serializable value object for snapshot diff intermediate object metadata.

Important APIs and types: fields `objectId` and `key`; constructor; static `getCodec`; private protobuf conversion methods using `DelegatedCodec` and `Proto2Codec` over `SnapDiffObjectInfo`.

Control flow and persistence: codec serializes to/from OM storage protobuf fields `objectID` and `keyName`, enabling use as a RocksDB table value.

Dependencies and integration: schema definitions include this type for from-snapshot and to-snapshot object-info tables, though current `SnapshotDiffManager` uses raw byte maps for intermediate state to reduce serialization overhead.

Risks and test signals: fields are mutable but have no getters in this file, so practical use is codec-centered. Tests should round-trip object id and key through the codec and verify compatibility with protobuf defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/SnapshotDiffObjectInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/package-info.java

Purpose: package documentation for snapshot diff helper classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.diff.helper` and documents helper classes for computing deltas between snapshots.

State, risks, and test signals: no executable behavior. Test signal is package documentation alignment with `SnapshotDiffObjectInfo`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/helper/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableDirFilter.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableDirFilter.java

Purpose: reclaim filter for deleted directory markers, deciding whether a directory can be removed because it is not referenced by the previous snapshot.

Important APIs and types: extends `ReclaimableFilter<OmKeyInfo>` with one previous snapshot. Overrides volume/bucket extraction and `isReclaimable`.

Control flow: for each deleted directory entry, gets the previous snapshot's `KeyManager` if available and calls `getPreviousSnapshotOzoneDirInfo`. A directory is reclaimable when no previous snapshot exists, the previous directory is absent, or its object ID differs.

State and persistence: no own durable state; uses base class snapshot locks and cached previous snapshot handles.

Dependencies and integration: used by snapshot GC/purge logic over deleted directory entries, and depends on FSO directory lookup semantics in `KeyManager`.

Risks and test signals: object-ID equality is the only preservation signal; ACL-only directory changes are not relevant to reclaim. Tests should cover no previous snapshot, matching object ID retained, different object ID reclaimable, deleted volume/bucket handling inherited from base filter, and lock reacquisition on chain changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableDirFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableFilter.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableFilter.java

Purpose: abstract base for GC filters that decide whether snapshot-related entries can be reclaimed after validating a stable view of the last N path snapshots.

Important APIs and types: implements Ratis `CheckedFunction<Table.KeyValue<String,V>, Boolean, IOException>` and `Closeable`. Key methods are `apply`, `initializePreviousSnapshotsFromChain`, `validateExistingLastNSnapshotsInChain`, `getLastNSnapshotInChain`, abstract `getVolumeName`, `getBucketName`, `isReclaimable`, and protected accessors for previous snapshots, bucket info, volume id, and key manager.

Control flow: `apply` extracts volume/bucket, checks whether the cached snapshot handles match the current chain and locks are held, opens/reopens the previous N snapshots in chain order under `SNAPSHOT_GC_LOCK`, loads active bucket and volume IDs, delegates to subclass logic, then validates the chain again before returning true. If the bucket or volume is already gone, entries are treated as reclaimable.

State and persistence: maintains cached previous snapshot infos and handles, locked snapshot IDs, bucket info, volume id, and reusable temporary lists. It does not write metadata but holds locks and snapshot references until closed or reinitialized.

Dependencies and integration: used by key, directory, and rename-entry reclaim filters. It integrates with `SnapshotChainManager`, `OmSnapshotManager`, `MultiSnapshotLocks`, active OM lock manager, `SnapshotUtils`, bucket manager, and key manager.

Risks and edge cases: `getLastNSnapshotInChain` calls `OmSnapshotManager.areSnapshotChangesFlushedToDB` even when `snapshotInfo` can become null; callers rely on that helper tolerating null or the loop can fail at chain start. Returning reclaimable for deleted buckets/volumes is intentional but high impact. Chain validation before and after subclass evaluation is essential; tests should simulate chain mutation, unflushed snapshot changes, lock acquisition failure, missing bucket/volume, current snapshot bucket mismatch, close cleanup, and ordering of locked snapshot IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableKeyFilter.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableKeyFilter.java

Purpose: reclaim filter for deleted key entries and calculator for previous snapshot exclusive size.

Important APIs and types: extends `ReclaimableFilter<OmKeyInfo>` with two previous snapshots. Public accessors expose `exclusiveSizeMap` and `exclusiveReplicatedSizeMap`.

Control flow: for a deleted key, it memoizes lookup in the immediately previous snapshot using `KeyManager.getPreviousSnapshotOzoneKeyInfo`; if absent, the deleted key is reclaimable. If present, it checks the previous-to-previous snapshot to see whether the key is exclusive to the previous snapshot and updates exclusive size counters, then returns false because a previous snapshot still references the key.

State and persistence: keeps in-memory maps from snapshot UUID to exclusive logical and replicated sizes. Reclaim decisions read prior snapshot key/file tables but do not write metadata directly.

Dependencies and integration: used by snapshot GC over deleted key tables and by snapshot accounting logic that consumes exclusive size maps. Uses `SnapshotUtils.isBlockLocationInfoSame` plus object-ID equality to decide whether prior key info represents the same block data.

Risks and test signals: hsync special handling comes from `SnapshotUtils`; non-hsync keys with same object ID but different block locations are considered not present. Exclusive size updates happen as side effects even though the entry is not reclaimable. Tests should cover absent previous key, present previous key, absent previous-to-previous key exclusive accounting, replicated size aggregation, object-ID mismatch, block-location mismatch, memoization behavior, and OBS/FSO bucket layout lookup through `KeyManager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableKeyFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableRenameEntryFilter.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableRenameEntryFilter.java

Purpose: reclaim filter for rename-table entries, deleting them only when the previous snapshot no longer references the renamed object.

Important APIs and types: extends `ReclaimableFilter<String>` with one previous snapshot. Overrides volume/bucket parsing via `metadataManager.splitRenameKey`, and `isReclaimable` checks previous key and directory tables.

Control flow: for each rename entry, opens previous snapshot tables if available. It looks up the rename entry value as the previous DB key in key and, for FSO buckets, directory tables. If any table contains an object with that DB key, the rename entry is retained; otherwise it is reclaimable.

State and persistence: no durable writes; uses base class cached previous snapshot handles and locks.

Dependencies and integration: used by snapshot GC of rename tables. Depends on rename key encoding, bucket layout, and `WithObjectID` table values.

Risks and test signals: if rename value encoding does not match previous table DB key format, entries may be reclaimed too early. Tests should cover OBS key-only lookup, FSO key plus directory lookup, no previous snapshot, splitRenameKey parsing, null previous tables, and chain-change validation inherited from `ReclaimableFilter`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableRenameEntryFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/package-info.java

Purpose: package documentation for snapshot reclaim filters.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.filter` and documents filters used to perform reclaimable checks on snapshots.

State, risks, and test signals: no executable behavior. Test signal is documentation consistency with key, directory, rename, and base reclaim filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/package-info.java

Purpose: package documentation for OM snapshot-related classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot`.

State, risks, and test signals: no executable behavior. Test signal is broad package documentation alignment with snapshot diff, utilities, local data, and locking classes in the same package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/TableMergeIterator.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/TableMergeIterator.java

Purpose: iterator that takes a sorted/filter key stream and returns that key with values from multiple RocksDB-backed tables, using null for missing table entries.

Important APIs and types: generic `TableMergeIterator<K extends Comparable<K>, V>` implements `ClosableIterator<Table.KeyValue<K,List<V>>>`; constructor accepts `keysToFilter`, a seek prefix, and varargs tables; `hasNext`, `next`, and `close` implement iteration.

Control flow: each table iterator is opened at the prefix. For every filter key, `updateAndGetValueAtIndex` seeks a table iterator when its cached key is behind the requested key, caches the next KV, and returns the value only on exact key match. `next` reuses a mutable `nextValues` list and wraps it with `Table.newKeyValue`.

State and persistence: maintains table iterators, cached key-values per table, and a reusable values list. It only reads tables.

Dependencies and integration: used by snapshot diff object-map construction and snapshot defrag SST spill logic to compare values between snapshot tables for candidate SST keys.

Risks and test signals: returned value lists are mutable and reused on the next `next` call, so callers must copy if retaining. It assumes the filter key stream is ordered compatibly with table iterators; out-of-order keys can force seeks but may still work less efficiently. Exceptions during seek are wrapped as `UncheckedIOException`. Tests should cover missing entries, exact matches across multiple tables, mutable-list reuse, prefix seeks, out-of-order or duplicate filter keys, close closing all iterators, and seek exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/TableMergeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/package-info.java

Purpose: package documentation for snapshot utility classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.snapshot.util` and documents utility classes for snapshot management.

State, risks, and test signals: no executable behavior. Test signal is documentation consistency with `TableMergeIterator`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/BelongsToLayoutVersion.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/BelongsToLayoutVersion.java

Purpose: class-level annotation marking OM request classes as belonging to an `OMLayoutFeature`.

Important APIs and types: runtime-retained annotation targeting `TYPE` with single value `OMLayoutFeature value()`.

Control flow and integration: enforced by `OMLayoutFeatureAspect.beforeRequestApplyTxn`, which checks annotated `OMClientRequest.preExecute` calls against the current OM layout version.

State, risks, and test signals: no state. Missing annotation on new layout-sensitive requests bypasses aspect gating. Tests should verify runtime retention, target type, and aspect rejection for requests annotated with future features.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/BelongsToLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/DisallowedUntilLayoutVersion.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/DisallowedUntilLayoutVersion.java

Purpose: method-level annotation used to block APIs until an OM layout feature is finalized/allowed.

Important APIs and types: runtime-retained annotation targeting `METHOD` with single value `OMLayoutFeature value()`.

Control flow and integration: enforced by `OMLayoutFeatureAspect.checkLayoutFeature` on annotated method execution. The aspect discovers a `LayoutVersionManager` from `OzoneManagerRequestHandler`, `OMClientRequest.preExecute`, a `getOmVersionManager` method, or a default manager fallback.

State, risks, and test signals: no state. Fallback to a default current-version manager can accidentally allow methods on unsupported target types. Tests should cover annotated methods on request handlers, client requests, generic classes with version manager accessors, and unsupported/fallback targets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/DisallowedUntilLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeature.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeature.java

Purpose: enum of OM layout features and layout versions.

Important APIs and types: implements `LayoutFeature`; features run from `INITIAL_VERSION(0)` through `SNAPSHOT_DEFRAG(9)`. Methods expose `layoutVersion`, `description`, `addAction`, and optional `action`.

Control flow and state: enum instances hold layout version, description, and an optional `OmUpgradeAction`; `addAction` only stores the first action to avoid overwriting.

Dependencies and integration: consumed by `OMLayoutVersionManager`, layout aspects, upgrade finalizer, annotations, and service feature gates such as snapshot defrag.

Risks and test signals: ordering defines software max layout version. Adding a feature requires appending a new enum value, guarding new behavior, and optionally registering upgrade actions. Tests should verify max version, descriptions, first-action-wins, deprecated `HSYNC` handling, and that new feature numbers are monotonic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureAspect.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureAspect.java

Purpose: AspectJ-based cross-cutting guard that blocks OM operations before their required layout feature is allowed.

Important APIs and types: `checkLayoutFeature` runs before methods annotated `@DisallowedUntilLayoutVersion`; `beforeRequestApplyTxn` runs before `OMClientRequest.preExecute` when the request class has `@BelongsToLayoutVersion`; `checkIsAllowed` throws `OMException(NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION)`.

Control flow: the annotation advice extracts the feature name and locates a layout version manager from known target types or reflection. The request-class advice reads the class annotation and first preExecute argument as `OzoneManager`. Both delegate to `checkIsAllowed`.

State and persistence: no persistent state. Static `aspectOf` exists to avoid intermittent test `NoSuchMethodError`.

Dependencies and integration: integrates OM request handling, `OzoneManagerRequestHandler`, `OMClientRequest`, `LayoutVersionManager`, and annotation classes.

Risks and test signals: reflection fallback to a new `OMLayoutVersionManager` can mask missing accessors by using current software layout. The pointcut only covers `preExecute`; apply-transaction paths require explicit guards elsewhere if needed. Tests should cover both annotations, failure messages, fallback behavior, current versus future layout versions, and `aspectOf`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutFeatureAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutVersionManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutVersionManager.java

Purpose: OM-specific layout version manager that initializes feature sets, tracks metadata/software layout version, and registers OM upgrade actions.

Important APIs and types: extends `AbstractLayoutVersionManager<OMLayoutFeature>`; constructors initialize from explicit metadata layout or current software layout; `registerUpgradeActions`, `getRequestClasses`, `finalized`, and `maxLayoutVersion` are key methods.

Control flow: explicit constructor calls `init(layoutVersion)`, which initializes known features, maps initialization IO failure to `OMException(NOT_SUPPORTED_OPERATION)`, and scans the upgrade package for `@UpgradeActionOm` classes implementing `OmUpgradeAction`. Registration instantiates action classes and attaches actions only for features above current metadata layout.

State and persistence: state is inherited layout-version tracking and enum-held actions. No direct disk writes; finalization storage is handled by the upgrade finalizer/storage layer.

Dependencies and integration: uses Reflections classpath scanning over OM upgrade and request packages, `OMLayoutFeature`, `OmUpgradeAction`, and OM request classes.

Risks and test signals: `Class.newInstance` requires public no-arg constructors and hides richer construction errors in logs. Classpath scanning can be expensive or sensitive to shading. Tests should cover metadata layout greater than software layout, action registration skip/register decisions, invalid action classes, request class discovery excluding abstract classes, and `maxLayoutVersion`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMUpgradeFinalizer.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMUpgradeFinalizer.java

Purpose: OM service implementation of layout finalization.

Important APIs and types: extends `BasicUpgradeFinalizer<OzoneManager, OMLayoutVersionManager>`; constructor accepts version manager; overrides `finalizeLayoutFeature`.

Control flow: delegates finalization to the base class with the feature's optional action and OM storage, allowing registered `OmUpgradeAction`s to run while finalizing features.

State and persistence: persistence is via `om.getOmStorage()` through the base finalizer. This class owns no independent state.

Dependencies and integration: used by OM upgrade workflows, `OMLayoutVersionManager`, `LayoutFeature`, and storage finalization.

Risks and test signals: action execution failure should surface as `UpgradeException` through the base class. Tests should verify the correct storage object and action optional are passed, finalization advances layout version, and failed actions do not partially mark features finalized.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OMUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OmUpgradeAction.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OmUpgradeAction.java

Purpose: marker interface for OM-specific upgrade actions that execute with an `OzoneManager` argument.

Important APIs and types: extends `LayoutFeature.UpgradeAction<OzoneManager>` without adding methods.

Control flow and integration: discovered by `OMLayoutVersionManager.registerUpgradeActions` when classes are annotated with `@UpgradeActionOm`, and invoked by `OMUpgradeFinalizer` through feature actions.

State, risks, and test signals: no state. Implementations must be public/no-arg instantiable for reflection scanning. Tests should verify action discovery requires this interface and annotation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/OmUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/QuotaRepairUpgradeAction.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/QuotaRepairUpgradeAction.java

Purpose: upgrade action for the `QUOTA` layout feature that optionally recalculates quota usage during finalization.

Important APIs and types: annotated `@UpgradeActionOm(feature = QUOTA)` and implements `OmUpgradeAction`; `execute(OzoneManager)` reads `OZONE_OM_UPGRADE_QUOTA_RECALCULATE_ENABLE` and runs `QuotaRepairTask.repair`.

Control flow: if enabled, checks leader status, constructs a quota repair task, and runs repair. Non-leader or leader-not-ready exceptions are caught and logged so only the leader performs the repair during upgrade.

State and persistence: repair task updates quota usage metadata; this class itself stores nothing.

Dependencies and integration: discovered by `OMLayoutVersionManager` and invoked by `OMUpgradeFinalizer` when finalizing the `QUOTA` feature.

Risks and test signals: repair is skipped silently except for a warning on non-leaders, so clusters rely on leader finalization or manual CLI repair. Tests should cover config disabled, leader success, non-leader skip, leader-not-ready skip, repair exceptions propagating, and annotation/action registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/QuotaRepairUpgradeAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/UpgradeActionOm.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/UpgradeActionOm.java

Purpose: class-level annotation linking an OM upgrade action implementation to an `OMLayoutFeature`.

Important APIs and types: runtime-retained annotation targeting `TYPE` with `OMLayoutFeature feature()`.

Control flow and integration: `OMLayoutVersionManager.registerUpgradeActions` scans for this annotation, instantiates classes implementing `OmUpgradeAction`, and attaches them to the annotated feature when not already finalized.

State, risks, and test signals: no state. Missing annotation means the action is never registered; wrong feature binds it to the wrong finalization step. Tests should verify retention, target, feature extraction, and registration behavior for annotated/non-annotated action classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/UpgradeActionOm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/package-info.java

Purpose: package documentation for OM upgrade classes.

APIs and integration: declares package `org.apache.hadoop.ozone.om.upgrade`.

State, risks, and test signals: no executable behavior. Test signal is documentation consistency with layout features, aspects, finalizer, annotations, and actions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMAdminProtocolServerSideImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMAdminProtocolServerSideImpl.java

Purpose: protobuf server-side translator for OM admin RPCs.

Important APIs and types: implements `OMAdminProtocolPB`; methods are `getOMConfiguration`, `decommission`, `compactDB`, and `triggerSnapshotDefrag`.

Control flow: configuration returns OM nodes in current memory and new configuration. Decommission validates non-null request, checks leader status, resolves the peer node, enforces admin authorization when enabled, and asks Ratis to remove the OM. Compact validates the column-family table exists before calling `ozoneManager.compactOMDB`. Snapshot defrag delegates to `ozoneManager.triggerSnapshotDefrag(noWait)`. RPC methods convert IO failures into protobuf responses with `success=false` and an error string.

State and persistence: the translator owns only an `OzoneManager` reference. Effects happen in OM/Ratis: membership changes, DB compaction, and snapshot defrag triggering.

Dependencies and integration: server adapter for admin clients, Ratis utilities, admin authorization via remote user, OM metadata store, and snapshot defrag service.

Risks and test signals: `decommission` returns null for null request, which is unusual for PB services. Decommission checks leader before authorization. Compact can expose table names and compaction cost through admin RPC. Tests should cover node list serialization, unknown peer, non-admin denial, leader checks, removeOM IO errors, valid/invalid column family compaction, defrag success/failure, and null request behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMAdminProtocolServerSideImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMInterServiceProtocolServerSideImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMInterServiceProtocolServerSideImpl.java

Purpose: protobuf server-side translator for OM inter-service RPCs, currently bootstrapping new OM nodes into the Ratis ring.

Important APIs and types: implements `OMInterServiceProtocolPB`; constructor receives `OzoneManager` and `OzoneManagerRatisServer`; method `bootstrap` handles `BootstrapOMRequest`.

Control flow: null request returns null. For valid requests, it checks current OM leader status, builds `OMNodeDetails` from node id, host, Ratis port, and listener flag, then delegates to `omRatisServer.addOMToRatisRing`. IO failures return a response with `success=false`, `RATIS_BOOTSTRAP_ERROR`, and a stringified error.

State and persistence: the adapter owns only references; durable membership changes are handled by Ratis/OM configuration logic.

Dependencies and integration: used by OM peer bootstrap flows and depends on Ratis leader checks plus protobuf request/response types.

Risks and test signals: like the admin adapter, null request returns null. No explicit admin authorization appears in this inter-service path, so endpoint security must be enforced by transport/service configuration. Tests should cover leader rejection, node detail mapping, successful add, IO failure error code, listener flag propagation, and null request behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/OMInterServiceProtocolServerSideImpl.java -->
