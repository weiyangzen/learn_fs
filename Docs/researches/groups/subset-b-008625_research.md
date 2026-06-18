# subset-b-008625 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_set.h -->
# sources/storage-engines/rocksdb/db/version_set.h

## Purpose

`version_set.h` declares the central RocksDB metadata model for DB versions, column-family version state, MANIFEST persistence, live-file accounting, and point/range read integration over SST and blob files. The header sits on the critical boundary between LSM metadata management and the DB read/write/compaction subsystems.

At the storage layer, a `Version` is a point-in-time view of one column family's table files and blob files. A `VersionStorageInfo` owns the per-level file layout and derived indexes used for reads and compaction picking. A `VersionSet` owns all column-family versions for a DB, writes and recovers MANIFEST edits, allocates file and sequence numbers, tracks live and obsolete files, and exposes helper APIs for compaction, metadata, backup/checksum, approximate-size, and recovery flows.

The file is mostly declarations and inline guards, but it defines the public contract that `version_set.cc`, `version_builder`, `column_family`, `DBImpl`, compaction picker/job code, table cache, blob storage, and secondary/read-only recovery paths rely on.

## Important APIs, Types, and Functions

Top-level helpers provide key-range search primitives over sorted SST metadata:

- `FindFile()` returns the first file whose largest internal key is greater than or equal to a search key.
- `SomeFileOverlapsRange()` checks whether a level's files overlap a user-key interval, with optimized handling for disjoint sorted files.
- `DoGenerateLevelFilesBrief()` builds compact `LevelFilesBrief` structures from full `FileMetaData` vectors.
- `EpochNumberRequirement` records whether SST epoch numbers may be absent or must be present.
- `VersionEditParams` aliases `VersionEdit` for call sites that carry edit fields as parameters without intending to represent a valid MANIFEST record.

`VersionStorageInfo` is the main per-version layout container. It stores `files_` by level, sorted `blob_files_`, per-level briefs, a `FileIndexer`, file-number-to-location lookup, compaction-priority ordering, compaction scores and levels, round-robin compaction cursors, base-level/dynamic-level sizing state, accumulated table statistics, bottommost-file state, periodic/TTL/read-triggered/blob-GC compaction candidates, and epoch-number policy. Important methods include `AddFile()`, `AddBlobFile()`, `PrepareForVersionAppend()`, `SetFinalized()`, `ComputeCompactionScore()`, `EstimateCompactionBytesNeeded()`, `GetOverlappingInputs()`, `OverlapInLevel()`, `RecoverEpochNumbers()`, `GetFileMetaDataByNumber()`, `GetBlobFileMetaData()`, `GetBlobStats()`, `FilesMarkedForCompaction()`, `BottommostFilesMarkedForCompaction()`, `RangeMightExistAfterSortedRun()`, `MaxBytesForLevel()`, `EstimateLiveDataSize()`, and `CalculateSSTWriteHint()`.

`VersionStorageInfo::FileLocation` is a compact `(level, position)` handle for file-number lookups. `GetFileLocation()` validates the indexed location against `files_`, making the generated location map a guarded fast path for table metadata lookup.

`ObsoleteFileInfo` and `ObsoleteBlobFileInfo` represent deletion candidates after versions release references. `ObsoleteFileInfo` owns a `FileMetaData*`, path, uncache aggressiveness, a `only_delete_metadata` flag for trivial-move/shared-file cases, and optional cache-reservation release logic in `DeleteMetadata()`.

`Version` represents one column-family version. It exposes read path methods (`AddIterators()`, `AddIteratorsForLevel()`, `Get()`, `MultiGet()`, `GetBlob()`, `MultiGetBlob()`), metadata/property APIs (`GetTableProperties()`, `GetPropertiesOfAllTables()`, `GetPropertiesOfTablesInRange()`, `GetAggregatedTableProperties()`, `TablesRangeTombstoneSummary()`), lifecycle methods (`PrepareAppend()`, `Ref()`, `Unref()`), live-file accounting (`AddLiveFiles()`, `RemoveLiveFiles()`), user-facing metadata builders (`GetColumnFamilyMetaData()`, `GetSstFilesBoundaryKeys()`, `GetCreationTimeOfOldestFile()`), and test hooks. It owns a `VersionStorageInfo`, links into a per-CF version list, and caches option/table/blob/merge/operator dependencies needed by reads.

`AtomicGroupReadBuffer` buffers `VersionEdit`s belonging to an atomic group during MANIFEST replay. It tracks how many edits in the group have been read and exposes `AddEdit()`, `Clear()`, `IsFull()`, `IsEmpty()`, and the replay buffer.

`VersionSet` is the DB-wide manager. Key APIs include:

- `LogAndApply()` overloads for one edit, a batch for one column family, and batches across multiple column families. These persist edits to MANIFEST and install new current versions.
- `Recover()`, `TryRecover()`, `TryRecoverFromOneManifest()`, `ListColumnFamilies()`, `ReduceNumberOfLevels()`, `DumpManifest()`, and `RecoverEpochNumbers()` for startup, best-effort recovery, manifest inspection, and migration-style operations.
- File/sequence-number state: `NewFileNumber()`, `FetchAddFileNumber()`, `MarkFileNumberUsed()`, `LastSequence()`, `SetLastSequence()`, `LastAllocatedSequence()`, `SetLastAllocatedSequence()`, `FetchAddLastAllocatedSequence()`, `LastPublishedSequence()`, `SetLastPublishedSequence()`, and `SyncLastSequenceWithAllocated()`.
- WAL and manifest accounting: `MarkMinLogNumberToKeep()`, `MinLogNumberWithUnflushedData()`, `PreComputeMinLogNumberWithUnflushedData()` variants, `manifest_file_number()`, `manifest_file_size()`, `pending_manifest_file_number()`, and `io_status()`.
- Compaction/read helpers: `MakeInputIterator()`, `ApproximateSize()`, protected `ApproximateOffsetOf()`, and protected file-level `ApproximateSize()`.
- Live/dead metadata: `AddLiveFiles()`, `RemoveLiveFiles()`, `GetMetadataForFile()`, `GetLiveFilesMetaData()`, `GetLiveFilesChecksumInfo()`, `AddObsoleteBlobFile()`, `GetObsoleteFiles()`, and `GetObsoleteSstFilesSize()`.
- Column-family access and option integration: `GetColumnFamilySet()`, timestamp-size maps, `GetRefedColumnFamilySet()`, `UpdatedMutableDbOptions()`, `ChangeOffpeakTimeOption()`, and DB/file option accessors.

`ReactiveVersionSet` derives from `VersionSet` for secondary/reactive users that replay MANIFEST changes instead of writing them. It adds `ReadAndApply()`, a reactive `Recover()` over a fragment-buffered manifest reader, `ApplyOneVersionEditToBuilder()`, `MaybeSwitchManifest()`, and overrides `LogAndApply()` privately to return `NotSupported`.

## Control Flow and State Behavior

New versions are built by applying `VersionEdit`s through `VersionBuilder` and then calling `PrepareAppend()`/`PrepareForVersionAppend()` before appending the version. Preparation populates derived structures such as level briefs, file indexes, bottommost file lists, file-location maps, non-empty level counts, compaction-priority order, and accumulated table stats. Many accessors assert `finalized_`, so callers must respect the prepare/finalize sequence before exposing a `Version`.

Read flow enters `Version::Get()`, `MultiGet()`, iterator construction, or blob access. These methods use `VersionStorageInfo`'s level layout and file indexer to find candidate SSTs, use `TableCache` to read SST data, use `RangeDelAggregator`/tombstone state where needed, and resolve blob indexes through `BlobSource` when values are stored externally. Reads deliberately require no DB mutex for point lookup, relying on version reference counts to keep metadata stable while iterators or reads are live.

Compaction selection flow depends on `VersionStorageInfo::ComputeCompactionScore()`. That computes per-level scores, base-level sizing, estimated compaction debt, L0 delay trigger counts, and candidate lists for explicit marks, TTL expiration, periodic compaction, bottommost compaction, forced blob GC, and read-triggered compaction. The comments repeatedly require the DB mutex for candidate access and snapshot-sensitive recomputation. `UpdateOldestSnapshot()` recomputes bottommost-file eligibility as snapshots are released.

MANIFEST mutation flow goes through `VersionSet::LogAndApply()`. The overloads normalize one or many `VersionEdit`s into CF/edit lists and delegate to the virtual multi-CF implementation. Internally, the implementation uses manifest writer queues, `ProcessManifestWrites()`, `WriteCurrentStateToManifest()`, optional fresh MANIFEST creation, `CreateManifestWriter()`, and `AppendVersion()` to make edits durable before installing versions. It may release and reacquire the DB mutex while doing file I/O, so the header documents mutex requirements and callback slots around manifest writes.

Recovery flow reconstructs column families and current versions from MANIFEST files. Normal recovery uses the latest descriptor, while best-effort recovery can walk older MANIFESTs and retain the most recent consistent point-in-time version. `AtomicGroupReadBuffer` helps preserve atomic-edit group semantics. Secondary/reactive recovery uses `ReactiveVersionSet` and `ManifestTailer` to read and apply new edits, including manifest switching, without supporting local `LogAndApply()`.

Sequence-number flow distinguishes visible, allocated, and published sequence numbers. `last_sequence_` is what reads can see, `last_allocated_sequence_` matters when two write queues allocate WAL sequence numbers before publish, and `last_published_sequence_` tracks reader publication when publish sequence differs. `SyncLastSequenceWithAllocated()` is an explicit recovery repair hook to avoid creating new WAL/memtable state below an already allocated sequence after an error.

File-number and WAL retention flow is similarly centralized. `next_file_number_` allocates monotonically increasing file numbers; `MarkFileNumberUsed()` advances it during recovery/repair; `min_log_number_to_keep_`, per-CF log numbers, and `PreComputeMinLogNumberWithUnflushedData()` determine what WAL files can be ignored or deleted.

## State and Persistence Behavior

Persistent state represented here includes MANIFEST records, current file numbers, sequence numbers, column-family IDs and options metadata, table file metadata, blob file metadata, per-file checksums, WAL retention thresholds, and options/manifest file numbers. The header keeps a sharp distinction between durable descriptor state and in-memory derived indexes.

`VersionStorageInfo` owns memory-only acceleration structures: `LevelFilesBrief`, `FileIndexer`, `file_locations_`, compaction-priority indexes, bottommost lists, and accumulated statistics. These must be regenerated from persisted file metadata when recovering or building a new version. Bugs in regeneration do not directly corrupt the MANIFEST, but they can cause wrong read pruning, missed compaction, bad file deletion, or invalid metadata reporting.

`Version` reference counting is the in-memory persistence mechanism for snapshots and iterators. Older versions can stay alive after a newer current version is installed, preventing table/blob files from being deleted while live reads still reference them. `AddLiveFiles()` and `RemoveLiveFiles()` use all live versions to filter obsolete candidates before physical deletion.

MANIFEST state has several durability knobs: current and pending manifest file numbers, descriptor log writer, manifest size, last valid record end, last compacted manifest size, auto-tuned max manifest size, preallocation size, and close-time verification. `ReopenManifestForAppend()` distinguishes physical file size from the end of the last valid logical record to avoid appending after tolerated tail garbage.

Blob files are part of version state alongside SST files. `blob_files_` is sorted by blob file number, supports lower-bound metadata lookup, contributes to live-file lists, and provides garbage/space-amplification stats used by blob GC decisions.

Epoch numbers are tracked per file and per CF. `RecoverEpochNumbers()` can reset missing file epochs from the column-family epoch or update the CF with the maximum file epoch. This is a recovery-time consistency repair path for installations that encounter older or incomplete metadata.

## Dependencies and Integration Points

This header integrates with most major RocksDB DB internals:

- Metadata and persistence: `VersionEdit`, `VersionBuilder`, MANIFEST `log::Writer`/`log::Reader`, `ColumnFamilySet`, `ColumnFamilyData`, file naming, file checksums, and DB/options metadata.
- Read path: `TableCache`, `TableReader`, `GetContext`, `MultiGetContext`, `LookupKey`, `MergeContext`, `MergeIteratorBuilder`, range deletion aggregation, pinned iterators, read callbacks, and table properties.
- Compaction path: `Compaction`, `CompactionPicker`, compaction styles, write controller, off-peak options, file-size and overlap calculations, bottommost-file logic, TTL/periodic/read-triggered/forced-blob-GC candidates, and compaction input iterators.
- Blob path: `BlobFileMetaData`, `BlobIndex`, `BlobSource`, blob read contexts, and blob garbage accounting.
- Environment/storage: `Env`, `FileSystem`, `FSDirectory`, `FileOptions`, `SystemClock`, `IOStatus`, file-system tracing, cache reservation, and block-cache tracing.
- Concurrency and diagnostics: `InstrumentedMutex`, atomics, `Statistics`, `Logger`, `IOTracer`, `SyncPoint`-visible test hooks, and internal test helpers.
- Optional coroutine support: `DECLARE_SYNC_AND_ASYNC` for `Version::MultiGetFromSST` and coroutine-only declarations for async multiget batching.

The most important external consumers are `DBImpl` for writes/recovery/cleanup, read APIs for point and iterator lookup, compaction picker/job code for scoring and input iteration, backup/checkpoint/live-file APIs, secondary DBs through `ReactiveVersionSet`, and tests that inspect version state through `TEST_` hooks and DB properties.

## Risks and Edge Cases

Many methods depend on strict mutex and lifecycle preconditions. Accessing compaction candidate vectors without the DB mutex, reading `VersionStorageInfo` before finalization, or modifying versions without respecting reference counts can create subtle use-after-free, missed compaction, or file-deletion bugs.

The file-location index and level briefs are derived from `files_`. If file ordering differs from the assumptions (L0 by decreasing epoch/newest first; lower levels sorted by non-overlapping key ranges), `FindFile()`, overlap checks, file index pruning, and `GetFileMetaDataByNumber()` can return wrong candidates.

Bottommost-file marking is snapshot-sensitive and timestamp-sensitive. Incorrect `oldest_snapshot_seqnum_`, `full_history_ts_low`, range-tombstone thresholds, or ingest-behind handling can compact away versions/timestamps that should remain visible, or leave compaction debt unaddressed.

Sequence-number handling is high risk with `two_write_queues`. The header explicitly calls out recovery corruption if allocated-but-unpublished sequence numbers are ignored. Changes to write recovery must preserve the `last_sequence_ <= last_published_sequence_ <= last_allocated_sequence_` style invariants documented here.

MANIFEST append/reuse is sensitive to partial records, tail garbage, preallocation, rotation, writer queue wakeups, and DB mutex release windows. A bug can leave durable state ahead of in-memory state, in-memory state ahead of durable state, or append new edits after corrupted bytes.

Obsolete-file cleanup must account for live old versions, blob files, trivial moves with shared physical files, pending outputs, cache reservations, and shutdown state. Over-deletion risks data loss; under-deletion leaks disk/cache memory.

Best-effort recovery and reactive/secondary replay intentionally tolerate more states than normal writable recovery. They need to detect missing files, manifest switches, atomic groups, and dropped CFs without installing inconsistent versions.

## Test Signals

Relevant test signals are broad because this header defines shared infrastructure. Strong coverage comes from RocksDB DB, version, compaction, recovery, and blob tests that assert:

- Point reads, iterators, and `MultiGet` return correct values across flushes, compactions, snapshots, range tombstones, blob values, and table-cache states.
- Compaction scores, base levels, L0 delay triggers, bottommost files, TTL/periodic/read-triggered/blob-GC candidates, and overlap calculations match expected DB properties and compaction picker choices.
- MANIFEST recovery, dump/list-column-family APIs, best-effort recovery, manifest reuse, atomic-group replay, and secondary/reactive replay reconstruct consistent versions.
- File-number, WAL-retention, and sequence-number monotonicity survive normal writes, recovery, repair, two-write-queue errors, and restart.
- Live-file and obsolete-file APIs do not delete files referenced by old versions, snapshots, blob metadata, or pending outputs, while eventually reporting reclaimable SST/blob/manifest files.
- Table properties, aggregated properties, range tombstone summaries, live-file metadata, checksum metadata, approximate size, and column-family metadata reflect the current version state.

Targeted `TEST_` hooks in the header indicate additional unit signals around references, synthetic version append, estimated compaction debt, compaction candidate insertion, manifest tuning parameters, and atomic group replay counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_set_sync_and_async.h -->
# sources/storage-engines/rocksdb/db/version_set_sync_and_async.h

## Purpose

`version_set_sync_and_async.h` defines the sync/async implementation body for `Version::MultiGetFromSST`, the helper that looks up a batch of keys in one SST file during `Version::MultiGet`. It is included through RocksDB's coroutine compatibility machinery so the same logic can be compiled as a synchronous function or coroutine-backed asynchronous function.

The file is narrowly focused but performance-critical: it bridges version-level multiget batching, table-cache SST reads, per-level performance accounting, blob-index deferral, range-tombstone early stopping, and value-size soft-limit enforcement.

## Important APIs, Types, and Functions

The only defined function is:

`DEFINE_SYNC_AND_ASYNC(Status, Version::MultiGetFromSST)(const ReadOptions& read_options, MultiGetRange file_range, int hit_file_level, bool skip_filters, bool skip_range_deletions, FdWithKeyRange* f, std::unordered_map<uint64_t, BlobReadContexts>& blob_ctxs, TableCache::TypedHandle* table_handle, uint64_t& num_filter_read, uint64_t& num_index_read, uint64_t& num_sst_read)`.

Important inputs and collaborators are:

- `MultiGetRange`, an iterator range over `KeyContext` entries being searched in this SST.
- `FdWithKeyRange* f`, whose `file_metadata` identifies the target SST.
- `TableCache::MultiGet`, called through `CO_AWAIT(table_cache_->MultiGet)` to perform the SST lookup.
- `BlobReadContexts`, grouped by blob file number, used to defer blob value retrieval after blob indexes are decoded.
- `GetContext`, which carries table lookup state, sampled-read flags, returned value/columns, range tombstone coverage, and per-context read counters.
- `ReadOptions::value_size_soft_limit`, used as a batch abort threshold after accumulating returned non-blob value sizes.
- Perf/statistics hooks such as `StopWatchNano`, `PERF_COUNTER_BY_LEVEL_ADD`, `RecordTick`, `RecordInHistogram`, `GET_HIT_L0`, `GET_HIT_L1`, `GET_HIT_L2_AND_UP`, and `SST_BATCH_SIZE`.
- `TEST_SYNC_POINT_CALLBACK("Version::MultiGet::TamperWithBlobIndex", &(*iter))`, which allows tests to corrupt or alter blob-index handling.

The function is compiled only under the sync/async wrapper condition:
`defined(WITHOUT_COROUTINES) || (defined(USE_COROUTINES) && defined(WITH_COROUTINES))`.

## Control Flow and State Behavior

The function first enables a per-level timer when the RocksDB perf level includes non-mutex timing and per-level perf context is active. It then calls `table_cache_->MultiGet()` with the internal comparator, target file metadata, mutable CF options, the file-read histogram for `hit_file_level`, filter/range-deletion skip flags, and an optional table handle.

If the table-cache lookup returns a non-OK status, the function assigns that status to every key in `file_range`, marks each key done, and returns immediately. This treats SST-level read failure as applying to all keys in the file batch.

For each key context after a successful table-cache call, the function gives the existing `KeyContext` status priority over `GetContext` state. Non-OK per-key statuses are marked done and skipped. For OK statuses, sampled reads update file-read sampling counters, including collapsible-entry sampling when the state is not found, merge, or deleted.

The function accumulates index/filter/SST read counters from each `GetContext`, adds them to the caller-provided per-file/per-level totals, and resets the per-key counters so later levels do not double count them. It reports `GetContext` counters immediately for found/non-merge results when DB statistics are enabled.

Range tombstone coverage affects the search. If a key remains not-found or merge and `max_covering_tombstone_seq > 0`, the remaining files can only contain covered versions for that key, so the key is skipped from further file searches.

The main state machine branches on `GetContext::State()`:

- `kNotFound` keeps the key in the search.
- `kMerge` keeps searching so operands can be resolved or merged by higher-level logic.
- `kFound` records per-level hit statistics, marks the key done, and either decodes a `BlobIndex` into `blob_ctxs` or accumulates value/column serialized size. If accumulated returned value size exceeds `value_size_soft_limit`, the function returns `Status::Aborted()`.
- `kDeleted` converts the status to `NotFound`, marks done, and stops searching the key.
- `kCorrupt` converts the status to corruption for the user key and marks done.
- `kUnexpectedBlobIndex` logs an error, returns a `NotSupported` status explaining BlobDB expectations, and marks done.
- `kMergeOperatorFailed` converts the status to corruption with the merge-operator-failed subcode and marks done.

At the end, it records the observed SST batch size in `SST_BATCH_SIZE` and returns the final status, which is usually OK unless the value-size soft limit aborted the batch.

## State and Persistence Behavior

This helper does not mutate persistent metadata or install versions. Its state changes are per-read and in-memory:

- `file_range` is updated to mark keys done, skipped, or still pending.
- Per-key `Status` objects are filled for errors, deletes, corrupt keys, unexpected blob indexes, or table-read failures.
- `GetContext` read counters are drained into `num_filter_read`, `num_index_read`, and `num_sst_read`.
- Sample-read counters on `FileMetaData` are incremented through `sample_file_read_inc()` and `sample_collapsible_entry_file_read_inc()`.
- Blob-index results are grouped into `blob_ctxs` for later `MultiGetBlob()` resolution rather than reading blobs inline.
- Statistics, histograms, and perf counters are updated for observability.

The persistent SST and blob files are read-only participants. Blob file contents are not fetched here; only encoded blob references are decoded and validated enough to schedule later blob reads.

## Dependencies and Integration Points

The implementation depends on `util/coro_utils.h` for `DEFINE_SYNC_AND_ASYNC`, `CO_AWAIT`, and `CO_RETURN`. It is paired with the `DECLARE_SYNC_AND_ASYNC` declaration in `version_set.h`, and coroutine builds can use it from the async multiget path while non-coroutine builds get equivalent synchronous behavior.

Primary integration points are:

- `Version::MultiGet` and `Version::MultiGetAsync`, which partition user keys by candidate SST/level and call this helper.
- `TableCache::MultiGet`, which performs the actual table-reader lookup.
- `GetContext` and `KeyContext`, which encode per-key result state, values/wide columns, merge/delete/corruption/blob flags, tombstone coverage, and statistics.
- Blob read flow through `BlobIndex`, `BlobReadContexts`, and later `MultiGetBlob()`.
- Perf and statistics subsystems for per-level table-read latency, user-key return counts, L0/L1/L2+ hit ticks, and batch-size histograms.
- SyncPoint-based tests that tamper with blob indexes.

## Risks and Edge Cases

The function relies on the invariant that per-key `Status` is not `NotFound()` after the table-cache call; not-found is represented by `GetContext::kNotFound`. Violating that split would break status precedence and search continuation.

Value-size soft-limit behavior aborts the whole file-range processing once accumulated non-blob result size crosses the threshold. Callers must treat `Status::Aborted()` as a soft-limit signal rather than an SST corruption signal.

Blob-index decoding has two paths: normal values and wide-column default-column values. Missing or malformed data changes the per-key status but does not necessarily fail the entire batch. Unexpected blob indexes are treated as unsupported for non-BlobDB usage and logged.

Range-tombstone skipping depends on `max_covering_tombstone_seq` being set correctly by earlier range-deletion processing. If it is stale or missing, multiget can either waste work searching covered keys or incorrectly stop before a visible older value.

The function resets per-key read counters after adding them to aggregate totals. If a future change forgets the reset, per-level stats can be double counted across levels; if it resets too early, observability loses IO accounting.

Because the file is compiled through sync/async macros, signature drift between `DECLARE_SYNC_AND_ASYNC` in `version_set.h` and this definition will break both build modes. Changes must also preserve coroutine-safe lifetime assumptions for `file_range`, `blob_ctxs`, and table handles.

## Test Signals

Strong test signals include multiget tests covering:

- Correct point lookup across L0/L1/L2+ files with expected per-level hit counters.
- Table-cache read errors propagating to all keys in the affected SST batch.
- Mixed batches where some keys are found, deleted, merged, corrupt, not found, skipped by tombstones, or represented by blob indexes.
- Wide-column values and blob indexes stored in the default wide column.
- `value_size_soft_limit` returning `Status::Aborted()` after enough value bytes are accumulated.
- Blob index tampering via `Version::MultiGet::TamperWithBlobIndex`.
- Per-level perf/stat counters and `SST_BATCH_SIZE` histograms remaining sane after multiple files and levels.
- Async-IO builds producing the same statuses and values as synchronous multiget builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/version_set_sync_and_async.h -->
