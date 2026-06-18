# Research: subset-b-008573

Grouped research for RocksDB column-family metadata implementation and declarations. Each section is wrapped for reconciliation into its source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family.cc -->
# sources/storage-engines/rocksdb/db/column_family.cc

## Purpose

`column_family.cc` implements RocksDB's column-family metadata layer. It turns the declarations from `column_family.h` into the runtime machinery that owns column-family handles, validates and sanitizes column-family options, manages `ColumnFamilyData` lifetimes, installs `SuperVersion` snapshots, tracks write-stall state, delegates compaction picking, creates data directories, and maintains the `ColumnFamilySet` registry.

This file is central to DB open/recovery, write-path routing, read-path snapshot stability, flush/compaction scheduling, dynamic option updates, and column-family drop cleanup. It does not itself write MANIFEST records, SST files, or WAL records, but its state is the in-memory authority consumed by `VersionSet`, `DBImpl`, memtables, compaction pickers, table/blob caches, and write throttling.

## Important APIs, Types, and Functions

Handle and utility implementations:

- `ColumnFamilyHandleImpl` refs a `ColumnFamilyData` on construction, exposes ID/name/descriptor/comparator accessors, notifies listeners on deletion, unrefs the CFD under the DB mutex, and asks `DBImpl` to find/purge obsolete files if the last dropped handle was released.
- `GetColumnFamilyID`, `GetColumnFamilyUserComparator`, and `GetImmutableOptions` are narrow helper adapters from public `ColumnFamilyHandle*` to internal metadata.
- `ColumnFamilyHandleInternal` is implemented via the base handle behavior plus a mutable internal CFD pointer declared in the header; it is used by write-batch/memtable-inserter paths without incrementing CFD refcounts.

Option support functions:

- `CheckCompressionSupportedWithManager` verifies compression types through an optional `CompressionManager` or the built-in compression registry.
- `CheckCompressionSupported` checks per-level compression, default compression, zstd dictionary training/finalization support, nonzero dictionary-size limits, and blob compression availability.
- `CheckConcurrentWritesSupported` rejects in-place updates and memtable factories that do not support concurrent insertion when concurrent memtable writes are enabled.
- `CheckCFPathsSupported` rejects multiple CF/DB paths for compaction styles other than level and universal.
- `SanitizeCfOptions` clamps and derives mutable settings such as write buffer size, arena block size, min/max write buffers, number of levels, L0 thresholds, pending-compaction byte limits, TTL, periodic compaction, blob direct-write partitions, read-only flush triggers, and DB/CF path cleanup.
- `ColumnFamilyData::ValidateOptions` performs hard compatibility checks for compression, concurrent writes, unordered writes, CF paths, TTL/periodic-compaction table format, blob direct-write restrictions, user-defined timestamp restrictions, blob GC thresholds, read-triggered compaction threshold, FIFO constraints, async file open constraints, per-key protection sizes, FIFO temperature thresholds, and universal compaction read amplification.
- `ColumnFamilyData::SetOptions` parses a mutable-options-only map, validates the resulting options, then refreshes `mutable_cf_options_` derived settings.

`SuperVersion` implementation:

- `SuperVersion::Ref` and `SuperVersion::Unref` maintain atomic references.
- `SuperVersion::Init` captures `ColumnFamilyData`, mutable memtable, immutable memtable-list version, `Version`, `full_history_ts_low`, and the optional `SeqnoToTimeMapping`; it refs all pinned objects.
- `SuperVersion::Cleanup` unrefs immutable memtables, mutable memtable, current version, and CFD, and records memtables to delete after cleanup.
- `SuperVersionUnrefHandle` is the thread-local cleanup callback and intentionally cannot run full `SuperVersion` cleanup because it may be called under the `ThreadLocalPtr` mutex.

`ColumnFamilyData` implementation:

- The constructor sanitizes options, builds immutable/mutable CF options, registers DB paths, creates internal table property collectors, internal stats, table cache, blob file cache/source, the proper compaction picker, optional file-metadata cache reservation manager, and initial write-stall state.
- The destructor removes the CFD from the live linked list and registry if needed, unrefs current versions, destroys memtables and immutable memtable list state, asserts it is not queued for flush/compaction, and unregisters DB paths.
- `UnrefAndTryDelete` owns the tricky deletion path: it deletes the CFD when the last external reference is gone, or tears down `super_version_` and thread-local superversions when only the current superversion still holds the CFD.
- `SetDropped` marks non-default CFs as dropped, releases write-controller tokens, and removes the CF from `ColumnFamilySet`.
- `OldestLogToKeep` returns the CF log number, possibly lowered to include prepared transactions still present in mutable or immutable memtables when two-phase commit is enabled.
- `ConstructNewMemtable` and `CreateNewMemtable` allocate and install a new mutable memtable, assign IDs through `SetMemtable`, and respect latest mutable options.
- `NeedsCompaction`, `PickCompaction`, `RangeOverlapWithCompaction`, and `CompactRange` are compaction picker delegation points that pass current `VersionStorageInfo`, snapshots, timestamp history low watermarks, and manual range parameters.
- `RangesOverlapWithMemtables` builds a merging iterator over mutable and immutable memtables plus a range tombstone aggregator to detect unflushed overlap with user-key ranges.
- `GetReferencedSuperVersion`, `GetThreadLocalSuperVersion`, `ReturnThreadLocalSuperVersion`, `InstallSuperVersion`, and `ResetThreadLocalSuperVersions` implement the fast read-path superversion cache and the safe replacement path under the DB mutex.
- `AddDirectories` creates or reuses `FSDirectory` handles for each CF path using a caller-provided map to avoid duplicate directory objects.
- `SetFlushSkipReschedule`, `GetAndClearFlushSkipReschedule`, and `ShouldPostponeFlushToRetainUDT` implement the user-defined timestamp in-memtable-only flush postponement policy.
- `RecoverEpochNumbers` delegates epoch recovery to `VersionStorageInfo`.

Write-stall and compaction-pressure helpers:

- `GetWriteStallConditionAndCause` classifies normal, delayed, and stopped writes from unflushed memtables, L0 delay-trigger count, pending compaction bytes, and mutable/immutable CF options.
- `SetupDelay` adjusts delayed write rates using `WriteController`, previous compaction debt, near-stop/stopped penalties, and auto-compaction-disabled behavior.
- `RecalculateWriteStallConditions` obtains stop/delay/compaction-pressure tokens, logs state transitions, updates internal stats counters, rewards recovery from delay by increasing the delayed write rate, and maintains `prev_compaction_needed_bytes_`.
- `GetL0FileCountForCompactionSpeedup`, `GetPendingCompactionBytesForCompactionSpeedup`, and `GetMarkedFileCountForCompactionSpeedup` compute non-stall pressure signals for increasing compaction threads.

`ColumnFamilySet` and write-batch lookup:

- `ColumnFamilySet` constructs a dummy circular-list CFD, owns maps from name and ID to `ColumnFamilyData`, tracks timestamp-size maps, and caches the default CF pointer.
- `CreateColumnFamily` constructs a new CFD, inserts it into maps and the circular linked list, records timestamp sizes, updates the maximum CF ID, and populates the default cache for ID 0.
- `RemoveColumnFamily` removes ID/name/timestamp entries but does not directly unlink the CFD from the circular list; the destructor handles list unlinking.
- `ColumnFamilyMemTablesImpl::Seek` selects a CFD by column-family ID, fast-paths ID 0, and updates an internal handle for write-batch callbacks. Its `GetLogNumber`, `GetMemTable`, and `GetColumnFamilyHandle` return metadata for the selected CF.

## Control Flow

Column-family creation generally flows through `VersionSet::LogAndApply`, recovery, or manifest dumping into `ColumnFamilySet::CreateColumnFamily`. Creation constructs `ColumnFamilyData`, sanitizes options, initializes caches and compaction picker state, inserts the object into registry maps, and links it into the set's circular list. Later DB code installs memtables/current versions and calls `InstallSuperVersion` to publish a readable LSM view.

Reads take a fast path through `ColumnFamilyData::GetThreadLocalSuperVersion`: the thread swaps the TLS slot to `kSVInUse`; if it finds a current cached `SuperVersion`, it can avoid the DB mutex. If a background install scraped the slot to `kSVObsolete`, the read path locks the DB mutex, refs `super_version_`, and proceeds. Returning the SV uses compare-and-swap; a scrape during the read causes the caller to drop its obsolete cached reference instead of returning it to TLS.

Superversion installation is DB-mutex protected. `InstallSuperVersion` creates the new snapshot from current mem/imm/version pointers, shares or installs a sequence-number-to-time mapping, recomputes write-stall state only when mem/imm/current changed, scrapes all thread-local cached superversions before unrefing the old current superversion, pushes write-stall notifications on transitions, queues old superversions for deferred free, and increments `super_version_number_`.

Write-stall recalculation reads the current version storage's L0 delay-trigger count and pending compaction bytes. It first handles hard stop cases, then delayed cases, then normal pressure cases that ask the write controller for a compaction-pressure token. The result is stored in the installed `SuperVersion` so read/write callers can observe the CF's current stall condition.

Compaction selection is deliberately thin in this file. `NeedsCompaction` checks whether auto-compaction is enabled and asks the configured picker. `PickCompaction` and `CompactRange` pass current storage, options, snapshots, range bounds, and UDT trimming state into the picker and finalize selected input info against the current version before returning the `Compaction`.

Drop and destruction are split. `SetDropped` only marks the CF, removes it from the registry, and disables write-control tokens; client handles and old superversions can still keep data alive for reads. When references finally drain through `ColumnFamilyHandleImpl::~ColumnFamilyHandleImpl` and `ColumnFamilyData::UnrefAndTryDelete`, obsolete file discovery/purge is triggered for dropped CFs and the CFD tears down its memtables, versions, caches, and paths.

## State and Persistence Behavior

The file manages in-memory state with persistence implications:

- `log_number_` and `OldestLogToKeep` determine which WALs must remain recoverable for the CF, including prepared transaction sections in 2PC mode.
- `ColumnFamilyOptions` are sanitized and validated here before they become `ImmutableOptions`, `MutableCFOptions`, compaction picker settings, and cache/table behavior.
- `full_history_ts_low_` and `flush_skip_reschedule_` affect whether flushes are postponed to retain in-memory user-defined timestamp history; `SuperVersion::Init` snapshots the low watermark for readers.
- `seqno_to_time_mapping` is published through `SuperVersion` and shared with later superversions or flush jobs, with debug assertions that it exists when time preservation is enabled.
- `next_epoch_number_` and `RecoverEpochNumbers` track the per-CF epoch numbering state used by file metadata.
- `running_ts_sz_` and `ts_sz_for_record_` in `ColumnFamilySet` track live CF timestamp sizes and the subset that must be recorded.
- `data_dirs_` caches opened `FSDirectory` handles for CF paths, while path registration/unregistration informs the environment about DB data directories.

The file does not directly serialize MANIFEST records, WAL records, table files, blob files, or OPTIONS files. Those durable actions occur in surrounding components. This code supplies the in-memory metadata and invariants those components use to decide what must be flushed, compacted, retained, recovered, or deleted.

## Dependencies

Major dependencies include:

- `db/column_family.h` for declarations and member layout.
- `db/db_impl/db_impl.h` for mutex, directory creation, obsolete file discovery, and purge integration.
- `db/version_set.h` and `VersionStorageInfo` for current version state, file sizes, pending compaction debt, epoch recovery, and live-version accounting.
- `db/memtable_list.h`, `MemTable`, and range tombstone iterators for mutable/immutable write buffers.
- `db/compaction/compaction_picker_*` for level, universal, FIFO, null, automatic, and manual compaction selection.
- `db/write_controller.h` for stop, delay, and compaction-pressure tokens.
- `db/internal_stats.h` and monitoring utilities for CF counters and runtime statistics.
- `db/blob/blob_file_cache.h`, `db/blob/blob_source.h`, and `db/blob/blob_file_partition_manager.h` for blob-read and direct-write integration.
- `options/options_helper.h`, `options/cf_options.h`, `rocksdb/convenience.h`, and `rocksdb/table.h` for option parsing, validation, and table-factory introspection.
- `util/compression.h`, `file/sst_file_manager_impl.h`, `DeleteScheduler`, `CacheReservationManager`, `ThreadLocalPtr`, `autovector`, and filesystem abstractions.

## Integration Points

`DBImpl` uses this file's objects for column-family handles, queues, superversion installation, obsolete-file cleanup, directory creation, write-stall notifications, and read/write access to current LSM state.

`VersionSet` and manifest application create/drop CFs through `ColumnFamilySet`, install `Version` objects into `ColumnFamilyData`, and rely on CFD refcounts to keep versions and files alive while old superversions are referenced.

The write path uses `ColumnFamilyMemTablesImpl` to map column-family IDs in `WriteBatch` records to `MemTable*`, log numbers, and internal handles. Memtable creation and max-write-buffer behavior here directly affect flush scheduling and write stalls.

Read paths and iterators depend on `SuperVersion` pinning mutable memtable, immutable memtable-list version, and current `Version` so files and memtables cannot disappear while a read operates.

Compaction and flush jobs share `SuperVersion` or current CFD state for snapshots, timestamp history, memtable retention, `SeqnoToTimeMapping`, blob source/cache access, and cache-reservation accounting.

Listeners configured in immutable options are called when handles start deletion, making this file part of the public lifecycle notification path.

## Risks

- Reference-count correctness is critical. `ColumnFamilyData`, `SuperVersion`, `Version`, mutable memtable, and immutable memtable-list references are interdependent; missing a ref/unref can cause leaks, premature deletion, or old reads seeing freed memory.
- Thread-local superversion caching is subtle. `kSVInUse`, `kSVObsolete`, `Swap`, `Scrape`, and compare-and-swap must preserve the invariant that TLS never owns the last SV reference and that full cleanup only happens where the DB mutex can be held.
- Many methods require the DB mutex, single-threaded write-thread context, or both. Violating those requirements around `ColumnFamilySet` maps, `SetDropped`, `CreateColumnFamily`, `RemoveColumnFamily`, `InstallSuperVersion`, and `UnrefAndTryDelete` risks registry corruption or races with column-family drop.
- Option sanitization silently adjusts user settings such as L0 thresholds, min write buffers, TTL/periodic compaction defaults, dynamic level bytes, and blob direct-write flags. Behavioral regressions here can change performance, retention, or data-loss protections across DB open.
- Write-stall control is feedback-based. Changes to thresholds or rate adjustment ratios can over-throttle writes, fail to avoid hard stops, or create cross-CF interference through shared `WriteController` tokens.
- `ColumnFamilyHandleImpl::~ColumnFamilyHandleImpl` holds a copy of initial CF options to keep shared option-owned resources alive during cleanup. Removing that pattern could create lifetime bugs with listeners, compaction filters, or factories.
- `SetDropped` removes registry visibility before old handles/readers are gone. Code that assumes a dropped CF is destroyed immediately can leak files, schedule invalid work, or reject valid reads from old handles.
- User-defined timestamp behavior is guarded by comparator timestamp size and `persist_user_defined_timestamps`. The flush-postponement path can preserve in-memory history but can also delay flush progress if timestamp low-watermark semantics are changed incorrectly.
- Blob direct-write validation rejects several write modes. Relaxing those checks without matching write-path guarantees could break ordering or recovery assumptions.

## Test Signals

Useful test signals include:

- Column-family create/drop tests where handles outlive `DropColumnFamily`, reads through old handles still work, writes fail or are ignored according to options, and obsolete files are purged only after final handle release.
- Superversion tests that install new versions/memtables, exercise thread-local cached reads, reset TLS state, and verify old versions/memtables are deleted only after all references drain.
- Dynamic option tests for `SetOptions`, including mutable-only enforcement, validation failures, refresh of derived options, and write buffer size updates on install.
- DB open/recovery tests for `SanitizeCfOptions`, CF path registration/cleanup, TTL/periodic compaction defaults, atomic flush with min-write-buffer merge, and multi-path compaction-style compatibility.
- Write-stall tests covering memtable limit, L0 file-count limit, pending compaction bytes, delay-to-normal recovery, disabled auto-compactions, and compaction-pressure token creation.
- Compaction picker tests for level/universal/FIFO/null styles, manual `CompactRange`, range-overlap conflict detection, and `FinalizeInputInfo` against the current version.
- User-defined timestamp tests for `SetFullHistoryTsLow`, `SetFlushSkipReschedule`, `ShouldPostponeFlushToRetainUDT`, non-persisted timestamp compatibility checks, and superversion low-watermark snapshots.
- Blob feature tests for blob compression validation, blob garbage-collection thresholds, blob direct-write incompatibilities, and `SetBlobPartitionManager` lifetime.
- WAL retention tests in two-phase commit mode verifying `OldestLogToKeep` accounts for prepared sections in mutable and immutable memtables.
- Stress/ASAN/TSAN tests that create/drop CFs while readers, iterators, flushes, and compactions keep old superversions alive.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family.h -->
# sources/storage-engines/rocksdb/db/column_family.h

## Purpose

`column_family.h` declares the internal column-family object model for RocksDB. It defines the handle implementation exposed through the public DB API, the `SuperVersion` snapshot type used by reads and background jobs, the `ColumnFamilyData` metadata object for each live or dropped column family, the `ColumnFamilySet` registry owned by `DBImpl`, and helper wrappers used by iteration and write-batch application.

The header is mostly an ownership and concurrency contract. It explains how `DBImpl`, `ColumnFamilyHandle`, `ColumnFamilyData`, `MemTable`, `MemTableListVersion`, `Version`, and `SuperVersion` reference each other so a point-in-time LSM view remains valid while column families are changed, flushed, compacted, or dropped.

## Important APIs, Types, and Functions

Top-level validation and option helpers:

- `CheckCompressionSupported`, `CheckConcurrentWritesSupported`, and `CheckCFPathsSupported` validate individual compatibility groups before DB open or dynamic option updates.
- `SanitizeCfOptions` normalizes `ColumnFamilyOptions` using immutable DB options and read-only state.
- `GetInternalTblPropCollFactory` wraps user table-properties collector factories in internal collector factories.
- `kIncSlowdownRatio` is exported for write-stall delay adjustment logic.

`ColumnFamilyHandleImpl`:

- Implements `ColumnFamilyHandle` and owns a reference to `ColumnFamilyData`.
- Exposes `cfd()`, `db()`, `GetID`, `GetName`, `GetDescriptor`, and `GetComparator`.
- Stores `DBImpl*` and `InstrumentedMutex*` so descriptor access and destruction can synchronize with DB state.

`ColumnFamilyHandleInternal`:

- A dummy handle used by internal write-batch/memtable paths when code expects a `ColumnFamilyHandle`.
- Overrides `cfd()` to return `internal_cfd_` and does not ref-count the CFD.

`SuperVersion`:

- Holds a `ColumnFamilyData*`, mutable `ReadOnlyMemTable*`, immutable `MemTableListVersion*`, current `Version*`, current `MutableCFOptions`, version number, write-stall condition, `full_history_ts_low`, and shared `SeqnoToTimeMapping`.
- Provides `Ref`, `Unref`, `Cleanup`, and `Init` for reference management.
- Exposes `ShareSeqnoToTimeMapping` and `GetSeqnoToTimeMapping` for read/flush users.
- Defines TLS sentinels `kSVInUse` and `kSVObsolete` for `ColumnFamilyData`'s thread-local superversion cache.

`ColumnFamilyData`:

- Represents one column family and owns its immutable/mutable options, comparator, table/blob caches, internal stats, memtable, immutable memtable list, current version pointer, current superversion pointer, compaction picker, path directories, write-stall token, timestamp history state, and queue flags.
- Public identity and lifetime APIs: `GetID`, `GetName`, `Ref`, `UnrefAndTryDelete`, `SetDropped`, `IsDropped`, `set_initialized`, and `initialized`.
- Option APIs: `soptions`, `ioptions`, `GetCurrentMutableCFOptions`, `GetLatestMutableCFOptions`, `GetLatestCFOptions`, static `ValidateOptions`, and `SetOptions`.
- LSM state APIs: `imm`, `mem`, `IsEmpty`, `dummy_versions`, `current`, `SetCurrent`, live/SST/blob size accessors, `OldestLogToKeep`, `ConstructNewMemtable`, `CreateNewMemtable`, and `SetMemtable`.
- Cache/blob APIs: `table_cache`, `blob_file_cache`, `blob_source`, `blob_partition_manager`, `blob_partition_manager_handle`, and `SetBlobPartitionManager`.
- Compaction APIs: `NeedsCompaction`, `PickCompaction`, `RangeOverlapWithCompaction`, `RangesOverlapWithMemtables`, `CompactRange`, `compaction_picker`, `kCompactAllLevels`, and `kCompactToBaseLevel`.
- Comparator and table-properties APIs: `user_comparator`, `internal_comparator`, and `internal_tbl_prop_coll_factories`.
- Superversion APIs: `GetSuperVersion`, `GetReferencedSuperVersion`, `GetThreadLocalSuperVersion`, `ReturnThreadLocalSuperVersion`, `GetSuperVersionNumber`, `InstallSuperVersion`, and `ResetThreadLocalSuperVersions`.
- Queue and write-stall APIs: `set_queued_for_flush`, `set_queued_for_compaction`, `queued_for_flush`, `queued_for_compaction`, `GetWriteStallConditionAndCause`, and `RecalculateWriteStallConditions`.
- Directory and timestamp APIs: `AddDirectories`, `GetDataDir`, `SetFullHistoryTsLow`, `GetFullHistoryTsLow`, `ShouldPostponeFlushToRetainUDT`, `SetFlushSkipReschedule`, and `GetAndClearFlushSkipReschedule`.
- Miscellaneous state APIs: `write_buffer_mgr`, `GetFileMetadataCacheReservationManager`, `SetMempurgeUsed`, `GetMempurgeUsed`, `NewEpochNumber`, `GetNextEpochNumber`, `SetNextEpochNumber`, `ResetNextEpochNumber`, `RecoverEpochNumbers`, `GetUnflushedMemTableCountForWriteStallCheck`, `AllowIngestBehind`, and `GetIngestSstLock`.

`ColumnFamilySet`:

- Owns all running `ColumnFamilyData` instances in maps keyed by name and ID, plus a circular linked list for iteration.
- Provides `GetDefault`, `GetColumnFamily` by ID/name, ID allocation/update helpers, `NumberOfColumnFamilies`, `CreateColumnFamily`, timestamp-size maps, iterators, access to shared table cache/write buffer manager/write controller, and fast-SST-open flags.
- Declares strict thread-safety rules: creation/removal require DB mutex plus single-threaded write thread; iteration requires DB mutex unless wrapped by `RefedColumnFamilySet`; lookup is allowed under DB mutex or write thread.

`RefedColumnFamilySet`:

- Wraps `ColumnFamilySet` iteration so each visited CFD is refed while visible to caller code that may release the DB mutex inside the loop body.

`ColumnFamilyMemTablesImpl`:

- Implements `ColumnFamilyMemTables` for write-batch application.
- `Seek` selects a CFD by ID, `GetLogNumber` returns the selected CF's log number, `GetMemTable` returns the current mutable memtable, `GetColumnFamilyHandle` returns an internal handle, and `current` exposes the selected CFD.

Free helper functions:

- `GetColumnFamilyID` maps a nullable handle to a CF ID, returning default ID 0 for null.
- `GetColumnFamilyUserComparator` returns a handle's user comparator if present.
- `GetImmutableOptions` returns immutable options from an internal handle.

## Control Flow

The declared lifecycle starts when `ColumnFamilySet::CreateColumnFamily` constructs a `ColumnFamilyData` and inserts it into the set. DB recovery or MANIFEST application then connects it to versions, memtables, and superversions. Public users hold `ColumnFamilyHandleImpl`, which increments the CFD refcount and can outlive a dropped CF.

At read time, callers acquire a `SuperVersion` from `ColumnFamilyData`. The superversion refs the mutable memtable, immutable memtable-list version, and current version, which pins the exact LSM view for iterators, gets, compactions, and flushes. The thread-local superversion API lets repeated reads avoid the DB mutex until `InstallSuperVersion` marks cached entries obsolete.

At write time, `ColumnFamilyMemTablesImpl` maps write-batch CF IDs to the current mutable memtable and log number. If a memtable rotates, `CreateNewMemtable` and `InstallSuperVersion` publish the new mutable memtable while older superversions preserve the old view.

When a CF is dropped, `SetDropped` removes it from the running registry but does not destroy the data immediately. Existing handles, superversions, reads, and compactions can keep refs. `UnrefAndTryDelete` eventually destroys the object once only self/superversion references remain and cleanup can safely unref all pinned objects.

Compaction control flows through `NeedsCompaction`, `PickCompaction`, and `CompactRange`, but the actual algorithms live in the compaction picker classes. The header exposes enough state for `DBImpl` and background jobs to schedule work while honoring mutex requirements.

## State and Persistence Behavior

The header defines the primary in-memory state that reflects durable RocksDB metadata:

- `id_`, `name_`, `log_number_`, and `max_column_family_` connect running CF objects to MANIFEST/WAL metadata.
- `dummy_versions_`, `current_`, `Version`, and `VersionStorageInfo` model durable SST/blob file state for a CF.
- `mem_` and `imm_` model unflushed data that may be WAL-protected and later flushed.
- `SuperVersion` snapshots combine memtable, immutable memtable list, current version, mutable options, timestamp history low watermark, and sequence-number-to-time mapping for point-in-time reads.
- `initial_cf_options_`, `ioptions_`, and `mutable_cf_options_` split persisted/configured options into immutable and dynamically changeable runtime forms.
- `data_dirs_` and CF paths connect a column family to filesystem directories.
- `full_history_ts_low_`, `flush_skip_reschedule_`, and timestamp-size maps express user-defined timestamp retention state.
- `next_epoch_number_` tracks per-CF epoch assignment for file metadata.

The declarations do not directly persist this state. They define the interfaces used by `VersionSet`, DB open/recovery, flush, compaction, and options code to translate persisted metadata into live state and back.

## Dependencies

The header depends on core RocksDB internals and public APIs:

- Memtable and versioning: `db/memtable_list.h`, `Version`, `VersionSet`, `VersionStorageInfo`, and `db/write_batch_internal.h`.
- Options and public API types: `options/cf_options.h`, `rocksdb/db.h`, `rocksdb/env.h`, and `rocksdb/options.h`.
- Caches and collectors: `db/table_cache.h`, `cache/cache_reservation_manager.h`, and `db/table_properties_collector.h`.
- Write and compaction coordination: `db/write_controller.h`, `rocksdb/compaction_job_stats.h`, `SnapshotChecker`, `CompactionPicker`, and `Compaction`.
- Observability/tracing: `trace_replay/block_cache_tracer.h`, `IOTracer`, and internal stats declarations.
- Infrastructure: `util/thread_local.h`, `util/hash_containers.h`, `util/cast_util.h`, `port::RWMutex`, atomics, strings, vectors, and unordered maps.

Forward declarations reduce include weight for heavy classes such as `DBImpl`, `BlobFileCache`, `BlobFilePartitionManager`, `BlobSource`, and `InternalStats`.

## Integration Points

`DBImpl` owns a `ColumnFamilySet`, creates user handles, uses `ColumnFamilyData` for read/write/flush/compaction queues, and calls `InstallSuperVersion` when memtables or versions change.

`VersionSet` and MANIFEST application create/drop CFs, maintain `Version` chains under each CFD's dummy version list, and use CF IDs to tie durable file edits to runtime objects.

The write batch path uses `ColumnFamilyMemTablesImpl` to find the right memtable for each record by column-family ID. A null external handle maps to default CF ID 0 through `GetColumnFamilyID`.

Read paths, iterators, compactions, and flush jobs use `SuperVersion` to keep old memtables and SST metadata alive while concurrent state changes publish newer views.

Compaction pickers, blob file components, table caches, cache reservation managers, write buffer manager, write controller, and table property collectors are all owned or accessed through `ColumnFamilyData`.

User-defined timestamp support integrates through comparator timestamp size, `full_history_ts_low`, timestamp-size maps in `ColumnFamilySet`, and flush postponement APIs.

External file ingestion and range tombstone conversion coordinate through the per-CF `ingest_sst_lock_`.

## Risks

- The header's mutex/write-thread requirements are part of the correctness contract. Callers that mutate `ColumnFamilySet` maps or CFD queue/drop state outside those contexts can race with drop, recovery, or write-batch lookup.
- `ColumnFamilyHandleInternal` intentionally does not ref-count. It is safe only when the caller already guarantees the selected CFD lifetime through DB mutex or write-thread serialization.
- `SuperVersion` stores raw pointers and uses manual reference counting. Any new field with ownership semantics must participate in `Init`, `Cleanup`, installation, and TLS invalidation.
- `ColumnFamilyData` has many raw pointers whose lifetimes are externally constrained: current version, memtable, `ColumnFamilySet`, `WriteBufferManager`, DB options, table cache, and write controller. Ownership must remain clear when adding APIs.
- Dropped column families remain readable while handles exist, so registry absence is not equivalent to object destruction.
- `GetCurrentMutableCFOptions` and `GetLatestMutableCFOptions` intentionally differ. Code that uses the latest options before a superversion install can observe settings not yet published to readers.
- `SetFullHistoryTsLow` ignores persisted UDT low-watermarks if the comparator no longer has timestamps. This protects reopen-after-disable cases but makes timestamp support sensitive to comparator behavior.
- `RefedColumnFamilySet` unrefs on iterator increment/destruction. Misusing copied iterators or holding returned raw pointers beyond the protected scope can invalidate the safety it provides.
- The circular linked list relies on destructor unlinking and dummy sentinel invariants; partial construction/destruction bugs can break iteration across all CFs.

## Test Signals

High-value tests exercising this header's contracts include:

- Compile-time and unit coverage for public handle methods, descriptor retrieval under mutex, null/default handle ID mapping, and internal handle behavior.
- Column-family set tests for create, lookup by name/ID, default cache, max-ID tracking, timestamp-size maps, iteration, and removal on drop/destruction.
- Refcount/lifetime tests where old handles, iterators, superversions, flushes, and compactions keep a dropped CF alive until the final unref.
- Read-path tests proving `SuperVersion` pins old memtables/versions while new superversions are installed and thread-local caches are invalidated.
- Dynamic option tests distinguishing latest mutable options from the mutable options captured in the current superversion.
- Write-batch tests that route records to the proper memtable through `ColumnFamilyMemTablesImpl`, including missing CF behavior.
- User-defined timestamp tests for timestamp-size maps, `full_history_ts_low` monotonicity, flush postponement, and disabled-UDT reopen behavior.
- External file ingestion/range tombstone conversion tests that exercise the per-CF RW lock.
- TSAN/stress coverage around DB mutex release during `RefedColumnFamilySet` iteration and concurrent drop/flush/compaction scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family.h -->
