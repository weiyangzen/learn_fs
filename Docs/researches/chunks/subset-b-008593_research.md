# sources/storage-engines/rocksdb/db/db_impl/db_impl.cc lines 7131-8132

## Scope

This chunk covers the end of `DBImpl`'s external SST ingestion commit path and a set of public or internal DB maintenance APIs implemented near the end of `db_impl.cc`. The code starts inside `DBImpl::CommitFileIngestionHandles`, after ingestion jobs have run and assigned sequence numbers, then continues through single-call ingestion, column-family import, column-family clipping, database/file checksum verification, user and block-cache tracing, file-number reservation for ingestion, oldest-file creation-time lookup, seqno-to-time mapping maintenance, periodic compaction triggering, and SstFileManager tracking.

The chunk is production code in `ROCKSDB_NAMESPACE`, not tests. It ties foreground APIs to `VersionSet`, `ColumnFamilyData`, `SuperVersion`, MANIFEST logging, file checksums, trace writers, periodic tasks, and metadata-derived file tracking.

## Purpose

The main responsibilities in this range are:

- finalize prepared external SST ingestion atomically across one or more column families;
- expose higher-level wrappers for ingestion and import workflows;
- implement destructive range-clipping by combining flush, file deletion, range tombstones, and full compaction;
- verify table and blob file integrity by either stored full-file checksums or SST/table checksum iteration;
- start, stop, and feed RocksDB operation traces and block-cache traces;
- reserve persistent file numbers before ingestion/import so crash recovery cannot reuse numbers assigned to linked files;
- maintain sequence-number-to-wall-time samples for preserve/preclude timestamp features;
- queue periodic/read-triggered compaction work for eligible column families;
- synchronize `SstFileManager` tracking with live table/blob metadata and already existing data files.

## Important APIs, Types, And Functions

- `DBImpl::CommitFileIngestionHandles(...)` completes a group of prepared ingestion handles. In this chunk it updates memtable ingestion barriers, builds foreground `VersionEdit` groups, calls `VersionSet::LogAndApply`, updates last sequence state, installs `SuperVersion`s, handles MANIFEST write errors, resumes writers, updates stats, releases pending outputs, and consumes handles.
- `DBImpl::IngestExternalFiles(...)` is the public convenience path: `PrepareFileIngestion()` followed by `CommitFileIngestionHandle()`.
- `DBImpl::CreateColumnFamilyWithImport(...)` creates a new column family, reserves file numbers, logs a dummy edit, imports exported SST metadata via `ImportColumnFamilyJob`, installs imported version edits, and drops/destroys the CF on failure.
- `DBImpl::ClipColumnFamily(...)` keeps only `[begin_key, end_key)` style data by flushing first, deleting non-overlapping files outside the clip bounds, writing `DeleteRange` tombstones for remaining overlap, deleting the inclusive largest key when needed, and compacting the whole CF to clear tombstones.
- `DBImpl::VerifyFileChecksums(...)`, `DBImpl::VerifyChecksum(...)`, `DBImpl::VerifyChecksumInternal(...)`, and `DBImpl::VerifyFullFileChecksum(...)` implement two integrity modes: stored file checksum verification through `GenerateOneFileChecksum()`, or SST checksum verification through `VerifySstFileChecksumInternal()`.
- `DBImpl::NotifyOnExternalFileIngested(...)` adapts `ExternalSstFileIngestionJob` file metadata into `ExternalFileIngestionInfo` callbacks for `EventListener`s.
- `DBImpl::StartTrace(...)`, `EndTrace()`, `NewDefaultReplayer(...)`, `TraceIteratorSeek(...)`, and `TraceIteratorSeekForPrev(...)` manage generic operation tracing through `Tracer` and `ReplayerImpl`.
- `DBImpl::StartBlockCacheTrace(...)` overloads and `EndBlockCacheTrace()` bridge public trace options to `BlockCacheTracer`.
- `DBImpl::ReserveFileNumbersBeforeIngestion(...)` captures a pending output marker, allocates a contiguous file-number range with `VersionSet::FetchAddFileNumber()`, and persists a dummy foreground edit.
- `DBImpl::GetCreationTimeOfOldestFile(...)` scans live versions for oldest SST creation time when `max_open_files == -1`, optionally waiting for async file open on legacy metadata.
- `DBImpl::GetSeqnoToTimeSample()`, `EnsureSeqnoToTimeMapping()`, `PrepopulateSeqnoToTimeMapping()`, `InstallSuperVersionForConfigChange()`, and `RecordSeqnoToTimeMapping()` maintain `SeqnoToTimeMapping` snapshots shared through `SuperVersion`.
- `DBImpl::TriggerPeriodicCompaction()` recomputes compaction scores and enqueues CFs with configured time-based compaction or read-triggered compaction.
- `DBImpl::TrackOrUntrackFiles(...)` reconciles `SstFileManagerImpl` file accounting against live table/blob metadata plus externally discovered data files.

Important local types and collaborators include `FileIngestionHandleImpl`, `ExternalSstFileIngestionJob`, `ImportColumnFamilyJob`, `VersionEdit`, `SuperVersionContext`, `ReadOptions`, `WriteOptions`, `ColumnFamilyData`, `ColumnFamilyHandleImpl`, `VersionStorageInfo`, `FileMetaData`, `BlobFileMetaData`, `MinAndMaxPreserveSeconds`, `SeqnoToTimeMapping`, `BlockCacheTraceWriter`, `TraceWriter`, and `SstFileManagerImpl`.

## Control Flow

The ingestion commit tail assumes earlier code has validated handles, merged same-CF ingestion jobs, entered write threads, flushed memtables if needed, run each ingestion job, and registered file ranges. The chunk first bumps each affected memtable's ingest sequence-number barrier to the assigned ingestion sequence number while holding shared per-CF ingestion locks. This prevents concurrent memtable conversion from accepting inserts whose sequence number is older than an installed external file.

For a successful ingestion run, the code builds one `VersionEdit` list per column family, marks each edit as a foreground operation, and marks them as one atomic group when more than one CF is involved. `VersionSet::LogAndApply()` persists the edits to the MANIFEST and installs them into version state. Only after `LogAndApply()` does the code advance `VersionSet`'s allocated, published, and visible last-sequence numbers to the maximum assigned ingestion sequence. The comments call out the reason: `LogAndApply()` releases `mutex_` while writing the MANIFEST, and publishing the new sequence too early would let snapshots observe an unstable boundary.

After MANIFEST application, registered ingest ranges are unregistered. On success, each affected CF installs a new `SuperVersion`, with a debug sync point after the first CF in a multi-CF group. On MANIFEST I/O failure, `error_handler_` records a background error under `kManifestWrite`. Both write queues are then resumed, ingest latency timing stops, job stats are updated, pending output file-number guards are released, `num_running_ingest_file_` is decremented, and waiters are signaled when no ingestion/import remains. Outside the DB mutex, `SuperVersionContext`s are cleaned. A failed atomic commit returns without consuming handles so their destructors can roll back; a successful commit calls each job's cleanup, emits ingestion listener callbacks, marks handles consumed, decrements outstanding prepared ingestion count, records histogram latency when enabled, and returns.

`CreateColumnFamilyWithImport()` is a two-stage workflow. It validates imported metadata comparator names, creates an empty CF, reserves enough file numbers under the DB mutex, and persists a dummy foreground edit so those numbers cannot be reused after a crash. It then prepares import work outside the mutex against a referenced `SuperVersion`. The actual import run re-enters the write queues, increments `num_running_ingest_file_`, runs `ImportColumnFamilyJob::Run()`, logs the import edit with `LogAndApply()`, installs a config-change `SuperVersion`, resumes writers, decrements the counter, and cleans the context. Failure after CF creation triggers `DropColumnFamily()` and `DestroyColumnFamilyHandle()` before returning the original error.

`ClipColumnFamily()` is ordered to avoid leaving old data visible. It first flushes the target CF or all CFs under atomic flush, then deletes whole SST files outside the desired key interval with `DeleteFilesInRanges()`. If files remain, it writes range tombstones below `begin_key` and above `end_key`; because the upper-side deletion uses `[end_key, largest_user_key)` semantics, it also deletes `largest_user_key` as a point key. A full manual compaction with forced optimized bottommost compaction clears the tombstones and remaining obsolete keys.

Checksum verification gathers stable CF and `SuperVersion` references first, then walks each non-empty level's `LevelFilesBrief` while no DB mutex is held for file I/O. In full-file-checksum mode it requires `options.file_checksum_gen_factory`, verifies each table file's stored checksum, and also verifies blob files. In SST-checksum mode it rebuilds `Options` per CF under the mutex and calls `VerifySstFileChecksumInternal()` with file metadata and largest seqno. Byte-read deltas are recorded to `VERIFY_CHECKSUM_READ_BYTES` after each file and once more during cleanup. `SuperVersion`s and CF references are unrefed under the mutex; obsolete superversions are either queued for purge or deleted immediately depending on `avoid_unnecessary_blocking_io`.

Seqno-to-time mapping code samples last sequence before current time while holding `mutex_`. `EnsureSeqnoToTimeMapping()` initializes capacity and appends a recent sample if the mapping is empty or stale relative to the configured recording cadence. `PrepopulateSeqnoToTimeMapping()` is only for new DB open with preservation enabled and no user writes: it pre-allocates `kMaxSeqnoTimePairsPerSST` sequence numbers, persists that last sequence to the MANIFEST, and backfills historical time samples. `InstallSuperVersionForConfigChange()` and `RecordSeqnoToTimeMapping()` copy the mutable DB-level mapping into shared immutable snapshots installed in applicable CF `SuperVersion`s.

`TriggerPeriodicCompaction()` scans non-dropped, not-already-queued CFs. If a CF has any time-based compaction setting, FIFO temperature threshold, TTL-style interval, or positive read-triggered compaction threshold, it recomputes compaction scores and enqueues pending compaction before scheduling flush/compaction work and signaling waiters.

## State And Persistence Behavior

- Ingestion and import persist file additions through MANIFEST `VersionEdit`s. Atomic group markers on multi-CF ingestion edits ensure all involved CF edits are replayed as one logical foreground operation.
- Ingestion updates in-memory memtable barriers and `VersionSet` sequence-number fields only after files have assigned sequence numbers and the MANIFEST edit is durable. This protects snapshot stability and write ordering.
- Pending output markers protect allocated file numbers from background cleanup while ingestion/import is in progress; dummy MANIFEST edits make reserved file-number ranges survive crashes.
- `num_running_ingest_file_` represents both external ingestion and CF import activity. It gates background cleanup/waiters through `bg_cv_`.
- `SuperVersion` installation publishes new versions, config-change seqno-to-time mappings, and import/ingestion changes to readers. Cleanup is explicitly deferred until the mutex is released.
- `ClipColumnFamily()` changes durable state through flush files, version edits from file deletion, WAL/manifested range tombstones from `DeleteRange`, and later compaction output.
- Checksum verification is read-only with respect to LSM metadata, but it mutates statistics and can schedule deferred `SuperVersion` purging.
- `PrepopulateSeqnoToTimeMapping()` deliberately advances last sequence numbers in a new DB and persists that change, reserving a seqno interval for historical mapping.
- Tracing state is stored in `tracer_` under `trace_mutex_` and in `block_cache_tracer_`; trace files themselves are written by user-provided trace writers.
- `TrackOrUntrackFiles()` mutates `SstFileManagerImpl` accounting for table files, blob files, and existing but unreferenced data files.

## Dependencies And Integration Points

- External SST ingestion integrates `PrepareFileIngestion()`, `ExternalSstFileIngestionJob`, `FileIngestionHandleImpl`, write queues, memtable flush, `VersionSet::LogAndApply()`, `InstallSuperVersionAndScheduleWork()`, event listeners, perf timers, sync points, statistics, and background error handling.
- Import integrates export/import metadata, `CreateColumnFamily()`, `ImportColumnFamilyJob`, pending output file-number capture/release, and CF drop/destroy rollback APIs.
- Range clipping combines flush infrastructure, `DeleteFilesInRanges()`, write API `DeleteRange()`/`Delete()`, and manual `CompactRange()`.
- Checksum verification depends on `FileChecksumGenFactory`, `GenerateOneFileChecksum()`, `VerifySstFileChecksumInternal()`, `TableFileName()`, `BlobFileName()`, `VersionStorageInfo`, `FileMetaData`, blob metadata, `IOSTATS(bytes_read)`, and `VERIFY_CHECKSUM_READ_BYTES`.
- Trace APIs connect the `DB` public surface to `Tracer`, `TraceWriter`, `TraceReader`, `ReplayerImpl`, `BlockCacheTracer`, and block-cache analysis tooling.
- Seqno-to-time mapping integrates CF options represented by `MinAndMaxPreserveSeconds`, `VersionEdit::SetLastSequence()`, DB open logic, periodic task registration, flush/compaction table property builders, and `SuperVersion` sharing.
- Periodic compaction integrates option-derived time intervals, read-triggered compaction thresholds, `VersionStorageInfo::ComputeCompactionScore()`, `EnqueuePendingCompaction()`, and `MaybeScheduleFlushOrCompaction()`.
- File tracking integrates `DBImpl::GetAllColumnFamilyMetaData()`, table/blob metadata public structs, file-path construction conventions, and `SstFileManagerImpl::OnAddFile()`/`OnUntrackFile()`.

## Risks And Edge Cases

- The ingestion path releases `mutex_` during MANIFEST I/O. Publishing sequence numbers before the edit is durable would make snapshots unstable; the delayed `SetLast*Sequence()` ordering is critical.
- Multi-CF ingestion relies on correct atomic group numbering. A mismatch between edit count and `MarkAtomicGroup()` values could produce partial replay semantics.
- `BumpIngestSeqnoBarrier()` depends on shared ingestion locks blocking concurrent memtable conversion write locks. Lock-order regressions around `ingest_sst_lock` and `mutex_` could deadlock or admit old sequence inserts.
- On ingestion failure after `Run()`, registered ranges must be unregistered and handles must remain unconsumed so rollback cleanup can remove staged files.
- Import failure rollback creates and then drops a CF. Any failure in `DropColumnFamily()` is logged, but the API still destroys the handle after asserting that destruction succeeds.
- `ClipColumnFamily()` is destructive and depends on comparator ordering, file-boundary metadata, and correct `DeleteRange` endpoint semantics. The extra point delete for `largest_user_key` is easy to miss.
- `VerifyFileChecksums()` returns invalid argument when no file checksum factory is configured, even if metadata has stored checksum strings. `kUnknownFileChecksum` short-circuits verification for individual files.
- Checksum verification holds referenced `SuperVersion`s while doing file I/O. It avoids use-after-free but can pin old versions and delay cleanup for large DBs.
- `GetCreationTimeOfOldestFile()` is only supported with `max_open_files == -1`; legacy DBs without manifest creation times can initially return zero until async file open completes.
- Seqno-to-time prepopulation permanently advances sequence numbers in a new DB. This is intentional for preservation features but affects assumptions that a new DB starts at sequence zero after open.
- `TriggerPeriodicCompaction()` only queues CFs not already queued. If score computation or queue flags are stale, a periodic run can skip useful work until a later scheduler tick.
- `TrackOrUntrackFiles()` assumes each SST/blob filename exists in at most one path and normalizes blob names that begin with a path separator. Path-collision or metadata inconsistency would distort SstFileManager accounting.

## Test Signals

- Ingestion tests should assert atomic multi-CF visibility, handle consumption only on success, listener callbacks after success, pending-output release, last-sequence advancement after assigned global seqnos, and rollback behavior after commit failure.
- MANIFEST fault-injection tests should verify `error_handler_.SetBGError(..., kManifestWrite)` on ingestion/import descriptor write errors and no partially visible files after failed atomic ingestion.
- Concurrency tests around external ingestion should cover memtable flush decisions, unordered-write pending writes, conversion barriers, dropped CF handling, two-write-queue mode, and range registration conflicts with compaction.
- Import tests should cover comparator mismatch rejection, file-number non-reuse across simulated crash after hard link/import preparation, successful imported metadata visibility, and CF drop/destroy rollback on import job or MANIFEST failure.
- `ClipColumnFamily()` tests should verify deletion below and above the requested range, retention inside the clip range, behavior when all files are deleted by `DeleteFilesInRanges()`, and removal of range tombstones after forced compaction.
- Checksum tests should cover invalid `ReadOptions::io_activity`, missing file checksum factory, checksum mismatch producing `Status::Corruption`, `kUnknownFileChecksum` skip behavior, table checksum verification without full-file checksum, blob checksum verification, stats byte accounting, and deferred `SuperVersion` purge.
- Trace tests should cover start/end lifecycle, double-end returning `IOError`, iterator seek events guarded by `trace_mutex_`, default replayer creation, and block-cache trace option bridging.
- Seqno-to-time mapping tests should validate sample monotonicity, cadence-based append behavior, prepopulation during new DB open, MANIFEST persistence of preallocated sequence numbers, and sharing of mapping snapshots through `SuperVersion`s after CF option changes.
- Periodic compaction tests should observe `CompactionReason::kPeriodicCompaction` or read-triggered queuing when configured options are present, while dropped or already queued CFs are skipped.
- SstFileManager tests should validate tracking of live SSTs, blob files with absolute-looking names, and unreferenced existing data files during DB open/close or manager installation.

## Unresolved Cross-Chunk References

The beginning of `CommitFileIngestionHandles()` is immediately before this chunk and defines handle validation, same-CF job merging, write-thread entry, flush decisions, `Run()`, and range registration. The final per-file research should reconcile this chunk with earlier definitions for `FileIngestionHandleImpl`, `PrepareFileIngestion()`, pending output helpers, `GetAllColumnFamilyMetaData()`, and DB open logic that calls `TrackOrUntrackFiles()` and `PrepopulateSeqnoToTimeMapping()`.
