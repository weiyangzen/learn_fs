# Research: subset-b-008576

This grouped report covers RocksDB compaction job execution, its public/internal stats surface, remote compaction serialization hooks, resumable progress support, and the event-listener tests for compaction job statistics.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job.cc

## Purpose

`compaction_job.cc` implements the runtime of a RocksDB compaction job. It turns a selected `Compaction` into one or more `SubcompactionState`s, optionally delegates work to a compaction service, scans input internal keys through `CompactionIterator`, writes table/blob outputs, verifies and installs those outputs into the MANIFEST through `VersionEdit`, and publishes both internal and listener-visible statistics.

The implementation is the bridge between compaction planning (`Compaction`, `VersionSet`, `VersionStorageInfo`) and persistence side effects: SST creation, blob file creation, MANIFEST mutation, directory sync, table cache verification, event listener callbacks, thread status, perf/IO stats, and resumable compaction progress.

## Important APIs, Types, and Functions

- `GetCompactionReasonString()` and `GetCompactionProximalOutputRangeTypeString()` convert enum values into logging/event strings.
- `CompactionJob::CompactionJob()` initializes a `CompactionState`, file options optimized for compaction reads, thread-status metadata, snapshot state, blob/output directories, and job-level stats derived from compaction inputs.
- `Prepare()` must run under DB mutex. It computes write lifetime hints, bottommost state, subcompaction key boundaries, optional progress resume state, seqno-to-time mappings, `preserve_seqno_after_`, `proximal_after_seqno_`, and the active options file number.
- `GenSubcompactionBoundaries()` samples approximate table anchors, sorts/deduplicates user-key anchors, computes target range sizes, and creates split boundaries. Round-robin level compaction can reserve extra background threads beyond `max_subcompactions`.
- `Run()` drives the no-mutex phase: log start, run subcompactions, sync directories, verify outputs, aggregate stats, verify record counts, and finalize job status.
- `ProcessKeyValueCompaction()` is the per-subcompaction body. It handles remote-service fallback, compaction filter validation, listener notifications, input iterator layering, progress resume, merge helper creation, `CompactionIterator` creation, the key loop, cleanup, blob finalization, and stats finalization.
- `ProcessKeyValue()` is the central key loop. It periodically checks `compaction_aborted_`, records incremental stats, decides proximal-vs-last-level placement by sequence number, calls `SubcompactionState::AddToOutput()`, and advances the compaction iterator.
- `OpenCompactionOutputFile()` allocates a new file number, creates a writable SST file, initializes `FileMetaData`, unique IDs, temperature, `WritableFileWriter`, and `TableBuilderOptions`.
- `FinishCompactionOutputFile()` adds range tombstones, finishes the table builder, syncs/closes the writer, removes empty SSTs, emits table creation events, notifies the SST file manager, and persists resumable progress when eligible.
- `InstallCompactionResults()` adds input deletions, output SSTs, blob additions, blob garbage accounting, round-robin compact cursor state, and calls `VersionSet::LogAndApply()` with a callback that releases compaction input files.
- `MaybeResumeSubcompactionProgressOnInputIterator()`, `UpdateSubcompactionProgress()`, and `PersistSubcompactionProgress()` restore and persist single-subcompaction progress records through `VersionEdit::SetSubcompactionProgress()`.
- `UpdateInternalStatsFromInputFiles()`, `UpdateCompactionJobInputStatsFromInternalStats()`, `UpdateCompactionJobOutputStatsFromInternalStats()`, `VerifyInputRecordCount()`, and `VerifyOutputRecordCount()` reconcile table properties, iterator counters, output table properties, and public `CompactionJobStats`.

## Control Flow

The normal lifecycle is `Prepare()` -> `Run()` -> `Install()` -> `CleanupCompaction()`.

During `Prepare()`, the job builds subcompactions either from generated user-key boundaries or from a known single range used by remote compaction/resume flows. Boundary generation releases the DB mutex while reading table anchor estimates, then may reserve additional Env threads for round-robin compaction. `Prepare()` also gathers input table seqno-time metadata when time preservation/tiering is enabled, derives the sequence-number threshold for preserving sequence numbers, and derives `proximal_after_seqno_` for per-key placement into proximal output versus last-level output.

`Run()` executes subcompactions in parallel: subcompaction 0 runs on the caller thread and the rest run on `port::Thread`s. After all threads join, empty output builders are removed and reserved extra subcompaction resources are released. The job then checks subcompaction status, optionally deletes aborted output files, fsyncs output directories, verifies output files by reopening/iterating/checksumming according to `verify_output_flags`, records output table properties on the `Compaction`, aggregates subcompaction stats, builds input stats from table metadata, and verifies input/output record counts when possible.

Inside a local subcompaction, the input iterator stack is `VersionSet::MakeInputIterator()` plus optional `ClippingIterator`, optional `BlobCountingIterator`, and optional `HistoryTrimmingIterator`. `CompactionIterator` applies snapshot/drop/merge/filter/range-deletion rules and emits records to `SubcompactionState::AddToOutput()`. File open/close are callbacks into `OpenCompactionOutputFile()` and `FinishCompactionOutputFile()`, so file rollover is controlled by `CompactionOutputs` while physical file construction remains in `CompactionJob`.

`Install()` returns to the DB mutex. It adds internal stats to the column family, applies the `VersionEdit`, logs human and structured event records, propagates install failure into `compact_->status` so cleanup releases uninstalled table-cache entries, and deletes `CompactionState`.

## State and Persistence Behavior

The persistent outputs are SST files, blob files, MANIFEST edits, directory fsyncs, and optional compaction progress log records. `OpenCompactionOutputFile()` tracks every new output path in `CompactionOutputs` so abort cleanup can delete files even if they were not retained in final output vectors. `FinishCompactionOutputFile()` deletes empty SSTs, records `TableProperties`, preserves file checksums, and integrates with `SstFileManagerImpl` quota enforcement.

`InstallCompactionResults()` is the MANIFEST boundary. It records deleted input files, added output files for normal and proximal levels, blob additions, blob garbage counts, and round-robin compact cursor state. It uses `VersionSet::LogAndApply()` and releases compaction files via callback only after the manifest path has progressed.

Resumable compaction is intentionally narrow: progress is attached only when there is exactly one subcompaction. Progress persistence is skipped for timestamped comparators, range-deletion file boundaries, same-user-key adjacent output files, final output files, empty outputs, and cases where `CompactionIterator` has looked ahead at the current key. On resume, previously completed outputs are restored from recorded `FileMetaData` plus table properties read directly from the output files, and file-number allocation is advanced past restored outputs.

Stateful stats include `internal_stats_`, per-subcompaction `compaction_job_stats`, `job_stats_`, perf counters, `io_status_`, thread-status properties, seqno-to-time mapping, blob garbage meters, and `SubcompactionProgress`.

## Dependencies and Integration Points

This file integrates with:

- LSM/versioning: `Compaction`, `CompactionState`, `SubcompactionState`, `VersionSet`, `VersionEdit`, `ColumnFamilyData`, `VersionStorageInfo`.
- Iteration and compaction semantics: `CompactionIterator`, `MergeHelper`, `CompactionRangeDelAggregator`, `ClippingIterator`, `HistoryTrimmingIterator`, `BlobCountingIterator`.
- File/table IO: `FileSystem`, `FSDirectory`, `WritableFileWriter`, `TableBuilder`, `TableCache`, `TableReader`, table properties, unique SST IDs, file checksums.
- BlobDB: `BlobFileBuilder`, `BlobFileCompletionCallback`, blob additions, blob garbage accounting.
- Observability: `EventLogger`, event listeners, `ThreadStatusUtil`, histograms/tickers, `IOSTATS`, sync points.
- Scheduling: `Env::ReserveThreads()`/`ReleaseThreads()`, background compaction scheduled counters, write-controller-aware IO priority.
- Compaction service: `ShouldUseLocalCompaction()` delegates to service processing when `db_options_.compaction_service` is configured, otherwise falls back locally.

## Risks and Edge Cases

- `CompactionJob` assumes a strict mutex contract: `Prepare()` and `Install()` need DB mutex, while `Run()` must not hold it. Boundary generation deliberately unlocks during table anchor reads.
- Additional subcompaction resources mutate shared scheduled-compaction counters and must be released on all paths. Leaks here can distort background scheduling.
- Abort cleanup deletes tracked output paths only when progress persistence is not active. Resumable compaction keeps files for later restoration, so stale or corrupt progress can leave durable partial outputs until recovery logic handles them.
- Record-count verification is disabled or softened in several cases: old block-based table format versions with unreliable entry counts, timestamp trimming, table factories without output table property support, and configured non-fatal verification.
- Progress persistence relies on user-key boundary safety. Same-user-key boundaries, range tombstones, merge/lookahead behavior, and timestamped keys are deliberately excluded because naive resume would double-count or lose versions/tombstones.
- Per-key/proximal placement splits range tombstones by sequence-number interval and traverses them twice when needed. This is correct but potentially CPU-heavy for tombstone-heavy workloads.
- Output verification may be expensive: iteration checksum and file checksum verification can reread all outputs, including remote compaction outputs when enabled.
- `ReadOutputFilesTableProperties()` accepts an `is_proximal_level` label but the resume call currently passes the default value even for proximal outputs, affecting only diagnostics.

## Test Signals

The file has extensive sync points for unit tests around subcompaction resource reservation, output file opening/finishing, manual pause, abort checks, record-count verification, and progress/tiering thresholds. The mapped `compaction_job_stats_test.cc` validates listener-visible job stats for level and universal compactions, deletion-drop counters, compression-size tolerances, subcompaction-dependent output-file counts, and IO timing stats. Other nearby compaction tests likely exercise abort cleanup, progress resume, proximal-level placement, remote compaction, and output verification because the implementation exposes explicit `TEST_SYNC_POINT` hooks for those paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job.h

## Purpose

`compaction_job.h` declares the main `CompactionJob` execution class, the data contracts for compaction service input/output/result serialization, and the `CompactionServiceCompactionJob` wrapper used by remote/read-only compaction workers. The header captures the lifecycle contract, mutex expectations, subcompaction model, stats aggregation model, and private helper boundaries implemented in `compaction_job.cc`.

## Important APIs, Types, and Functions

- `class CompactionJob` is the primary compaction executor. Public methods are `Prepare()`, `Run()`, `Install()`, `io_status()`, and a destructor that expects `CleanupCompaction()` to have released `compact_`.
- `CompactionJob::kCompactionAbortedFalse` is a constant abort flag used by compaction service jobs, which do not support normal DB abort signaling.
- Protected helpers expose core overridable/customizable behavior: `RecordCompactionIOStats()`, `LogCompaction()`, `CleanupCompaction()`, and `ProcessKeyValueCompaction()`.
- `UpdateInternalStatsFromInputFiles()`, `UpdateCompactionJobInputStatsFromInternalStats()`, `UpdateCompactionJobOutputStatsFromInternalStats()`, `VerifyInputRecordCount()`, and `VerifyOutputRecordCount()` define the boundary between internal compaction stats and public `CompactionJobStats`.
- Subcompaction scheduling helpers include `GenSubcompactionBoundaries()`, `GetSubcompactionsLimit()`, `AcquireSubcompactionResources()`, `ShrinkSubcompactionResources()`, and `ReleaseSubcompactionResources()`.
- Run-stage helpers split the large execution into `InitializeCompactionRun()`, `RunSubcompactions()`, `UpdateTimingStats()`, `RemoveEmptyOutputs()`, `CleanupAbortedSubcompactions()`, `SyncOutputDirectories()`, `VerifyOutputFiles()`, `AggregateSubcompactionOutputAndJobStats()`, and `FinalizeCompactionRun()`.
- `SubcompactionKeyBoundaries` owns optional start/end slices plus derived timestamp-stripped bounds, max timestamp storage, internal-key bounds, and user-key bounds.
- `SubcompactionInternalIterators` owns the layered input iterator objects used during processing.
- Process helpers include filter validation, read option initialization, input iterator construction, blob builder creation, compaction iterator creation, output file handler creation, key processing, incremental/final stats updates, status finalization, file cleanup, blob finalization, and subcompaction finalization.
- Output helpers include `OpenCompactionOutputFile()`, `FinishCompactionOutputFile()`, `InstallCompactionResults()`, `GetTableFileName()`, and `GetRateLimiterPriority()`.
- Progress helpers include `MaybeAssignCompactionProgressAndWriter()`, `MaybeResumeSubcompactionProgressOnInputIterator()`, `ReadOutputFilesTableProperties()`, `ReadTablePropertiesDirectly()`, `RestoreCompactionOutputs()`, `ShouldUpdateSubcompactionProgress()`, `UpdateSubcompactionProgress()`, `PersistSubcompactionProgress()`, and `UpdateSubcompactionProgressPerLevel()`.
- `struct CompactionServiceInput` serializes the column family, snapshots, expanded input file list, output level, source DB id, optional subcompaction begin/end boundaries, and options file number.
- `struct CompactionServiceOutputFile` serializes metadata for remote-generated SST outputs, including sequence range, internal-key range, oldest ancestor time, creation time, epoch, checksums, paranoid hash, unique ID, table properties, proximal-output flag, and file temperature.
- `struct CompactionServiceResult` carries remote compaction status, output files, output path, bytes read/written, job-level stats, and internal per-level stats.
- `class CompactionServiceCompactionJob : private CompactionJob` exposes a narrower read-only API: `Prepare()`, `Run()`, `CleanupCompaction()`, `io_status()`, and an override of table-file naming and IO stat recording.

## Control Flow

The header documents the main sequencing and lock discipline:

- `Prepare()` requires the DB mutex and builds subcompaction boundaries plus seqno/time state. It accepts optional known single-subcompaction bounds for remote compaction and optional `CompactionProgress` plus a progress log writer for resume support.
- `Run()` requires the DB mutex not be held. It launches subcompaction workers, waits for completion, verifies generated outputs, and unifies bookkeeping.
- `Install()` requires the DB mutex. It writes compaction input/output changes into the current version and releases compaction files via `Compaction::ReleaseCompactionFiles()`.

Internally, the header divides `Run()` into high-level stages and divides each subcompaction into setup, processing, output finalization, stats finalization, and listener notification. This decomposition is important because compaction jobs combine CPU-heavy iteration, file IO, manifest mutation, listener callbacks, and abort/manual-pause paths with different mutex and error-handling requirements.

## State and Persistence Behavior

`CompactionJob` owns transient execution state through `compact_` and durable-output coordination through `versions_`, directories, file options, table cache, blob callback, and `VersionEdit` installation. Public listener stats are accumulated into `job_stats_`; RocksDB internal metrics are accumulated into `internal_stats_`, which contains separate normal-output and proximal-output stats.

The class stores DB identity (`dbname_`, `db_id_`, `db_session_id_`) for file creation, unique IDs, event records, and blob builders. It stores snapshot state (`earliest_snapshot_`, `job_context_`) to decide what sequence numbers and tombstones are still visible. It stores `full_history_ts_low_` and `trim_ts_` to support timestamp-history preservation/trimming. It stores `preserve_seqno_after_` and `proximal_after_seqno_` to decide sequence-number preservation and per-key output placement.

Persistence-related fields include `output_directory_`, `blob_output_directory_`, `db_directory_`, `compaction_progress_writer_`, `options_file_number_`, and the progress-related helper declarations. The header makes clear that resumable progress is not a general multi-subcompaction contract; it is attached through the single-subcompaction path.

## Dependencies and Integration Points

The header depends on most of the DB compaction stack: blob builders/callbacks, column families, compaction iterator/output state, flush/job contexts, internal stats, log writer, memtables, range deletion aggregation, seqno-time mapping, version edits, write controller/thread, event logging, options, Env/FileSystem abstractions, table cache, and public `CompactionJobStats`.

External integration surfaces are:

- Public event listeners, through `CompactionJobStats`, `SubcompactionJobInfo`, and table file creation notifications.
- Compaction service RPC/storage contracts, through `CompactionServiceInput` and `CompactionServiceResult` serialization.
- File-system and rate-limiter behavior, through `FileOptions`, `Env::Priority`, `Env::IOPriority`, `FSDirectory`, and IO tracer.
- DB scheduling, through background compaction scheduled counters and reserved threads.
- BlobDB, through blob output directory/callback and `CompactionServiceOutputFile` blob-related metadata.

## Risks and Edge Cases

- The class is deliberately non-copyable and non-movable because it owns stateful pointers, references, thread-visible subcompaction state, and cleanup-sensitive resources.
- Many constructor arguments are references or raw pointers that must outlive the job; lifetime ownership is external for DB options, mutexes, directories, stats, event logger, job context, and scheduled counters.
- The mutex contract is not enforced by the type system. Misusing `Prepare()`, `Run()`, or `Install()` under the wrong lock state can deadlock or race with version/file state.
- Progress persistence APIs expose a partial feature: only single-subcompaction resume is supported, and implementation-level restrictions exclude several boundary cases.
- Compaction service result serialization must preserve both job-level and internal per-level stats because job-level stats cannot currently be reconstructed exactly from per-level stats.
- Proximal-level output doubles several data paths: stats, output vectors, table properties, range tombstone filtering, manifest edits, and service metadata all need to keep normal and proximal outputs distinct.

## Test Signals

The header exposes `friend class CompactionJobTestBase`, `TEST_Equals()` methods for service input/result structs in debug builds, and many private helpers that have sync-point coverage in the implementation. The mapped stats test validates the public `CompactionJobStats` contract that this class declares and populates. Remote compaction tests should exercise `CompactionServiceInput`, `CompactionServiceOutputFile`, `CompactionServiceResult`, and `CompactionServiceCompactionJob` serialization and path overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc

## Purpose

`compaction_job_stats_test.cc` is a parameterized RocksDB unit test for listener-visible `CompactionJobStats`. It builds controlled LSM layouts, triggers manual and automatic compactions, and verifies that `CompactionJobInfo::stats` reports expected input/output record counts, file counts, byte estimates, raw key/value bytes, replacement/deletion counters, key prefixes, full/manual flags, and optional IO timing fields.

The suite runs with `max_subcompactions` values `1` and `4`, so it checks both sequential compaction and subcompaction-sensitive behavior.

## Important APIs, Types, and Functions

- `RandomString()` and `Key()` generate compressible values and fixed-width numeric keys.
- `CompactionJobStatsTest` is the fixture. It owns the DB path, WAL path, `Env`, `DB`, column family handles, last options, and selected `max_subcompactions_`.
- Fixture helpers wrap DB lifecycle and operations: `Reopen()`, `DestroyAndReopen()`, `CreateAndReopenWithCF()`, `Flush()`, `Put()`, `Delete()`, `Get()`, `FilesPerLevel()`, `NumTableFilesAtLevel()`, `Compact()`, `TEST_Compact()`, `MakeTables()`, `MakeTableWithKeyValues()`, and `SelectivelyDeleteKeys()`.
- `CompactionJobStatsChecker` is an `EventListener` that queues expected `CompactionJobStats` and verifies the next `OnCompactionCompleted()` callback under a mutex.
- `CompactionJobDeletionStatsChecker` specializes verification to deletion/replacement counters.
- `EstimatedFileSize()` approximates SST sizes with data, footer, filter, and index overhead so byte counters can be checked with tolerance instead of exact equality.
- `NewManualCompactionJobStats()` builds expected stats for a compaction range, including file/record counts, estimated bytes, raw key/value bytes, flags, replacement count, and output key prefixes.
- `GetAnyCompression()` selects an available compression type for compression-tolerant stat checks.
- `GetUniversalCompactionInputUnits()` predicts which flushed runs universal compaction will compact.

## Control Flow

`CompactionJobStatsTest` fixture setup creates a fresh DB with one LOW and one HIGH background thread and parameterized `max_subcompactions`. Teardown disables sync points, closes handles, and destroys all DB paths.

`TEST_P(CompactionJobStatsTest, CompactionJobStatsTest)` performs a multi-phase level-compaction scenario on a `pikachu` column family:

1. Create eight L0 files with disjoint key ranges while auto-compaction is held off.
2. Manually compact six single L0 ranges to L1, expecting one input file, one output file, and unchanged record counts for each.
3. Compact remaining L0 files into one L1 output, expecting multiple input files but one output.
4. Generate sparse wider L0 files and compact overlapping L0/L1 ranges, expecting three input files, two files at output level, replacement of one third of records, and subcompaction-dependent output file count (`2` when `max_subcompactions > 1`, otherwise `1`).
5. Perform a broader compaction and then, when compression is available, rerun with compressed output and sync-point-induced delays to assert IO timing stats are nonzero.

`TEST_P(..., DeletionStatsTest)` builds overlapping data across L2, L1, and L0, inserts deletion records for existing and non-existing keys, then compacts L0 to L1 and verifies `num_input_deletion_records`, `num_expired_deletion_records`, and `num_records_replaced`.

`TEST_P(..., UniversalCompactionTest)` configures universal compaction, precomputes expected stats for automatic compactions after flushes, writes six flushed runs, waits for compactions, and verifies full/manual flags and input-unit accounting.

## State and Persistence Behavior

The tests create real RocksDB databases under `test::PerThreadDBPath()`, create and drop column family handles, flush memtables into SSTs, invoke manual compaction APIs, and wait for background compaction. Expected stats are queued before each compaction so the listener callback can consume them in order. The queue is protected by a mutex because compaction completion callbacks can occur on background threads.

`FilesPerLevel()` and `NumTableFilesAtLevel()` read RocksDB properties to assert that the physical LSM shape matches the expected test phase before checking stats. The tests use `DestroyAndReopen()` to reset persistent DB state between compression/no-compression runs while preserving the same listener object in options.

Sync points around `WritableFileWriter` deliberately sleep in append/flush/sync/range-sync paths so `file_write_nanos`, `file_prepare_write_nanos`, `file_fsync_nanos`, and `file_range_sync_nanos` become observable when `options.report_bg_io_stats` is true.

## Dependencies and Integration Points

The test depends on RocksDB DB APIs (`DB::Open`, column families, `CompactRange`, `Flush`, `Put`, `Delete`, properties), `DBImpl::TEST_CompactRange()` and `TEST_WaitForCompact()`, `EventListener::OnCompactionCompleted()`, sync-point instrumentation, table factories/properties, compression support helpers, and test harness utilities.

It directly validates behavior implemented in `compaction_job.cc`: stat aggregation from inputs/outputs, output key prefix copying, replacement/drop counters from `RecordDroppedKeys()`, manual/full flags from `ReportStartedCompaction()` and compaction style, subcompaction output count effects, and IO timing population from `RecordCompactionIOStats()`/finalization.

## Risks and Edge Cases

- Byte-size checks are approximate by design. They tolerate 10% normally and 20% with compression, so regressions within that tolerance may not fail.
- The tests use fixed assumptions about key/value sizes, table overhead, L0/L1 file layout, and universal compaction input grouping. Changes in table format defaults or compaction picking can require expected-stat updates.
- With `max_subcompactions > 1`, output file count differs because subcompactions do not coordinate to minimize output files like the sequential path; the test encodes this distinction.
- `CompactionJobStatsChecker` verifies only when expected stats are queued. Unexpected extra compactions can be missed except where the test asserts queue length at the end or between phases.
- IO timing assertions rely on sync-point sleeps and may be sensitive to platform-specific IO/stat behavior, which is why the entire file is disabled for `IOS_CROSS_COMPILE`.

## Test Signals

This file is itself the primary test signal for compaction job stats. It covers:

- Manual level compaction stats, including input/output levels and key prefixes.
- Replacement/drop accounting when newer records replace older records.
- Deletion-specific stats for expired deletion records and replaced records.
- Universal compaction stats and full-compaction flag behavior.
- Parameterized single-subcompaction and multi-subcompaction paths.
- Compression-aware byte estimate tolerance.
- Background IO timing fields when `report_bg_io_stats` is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_stats_test.cc -->
