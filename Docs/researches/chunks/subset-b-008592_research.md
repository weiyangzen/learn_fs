# sources/storage-engines/rocksdb/db/db_impl/db_impl.cc lines 1-7130

## Scope

This chunk covers the first 7,130 lines of RocksDB's main `DBImpl` implementation file. It includes construction and shutdown mechanics, background-error resume, periodic tasks, statistics persistence, dynamic option mutation, WAL flush/sync/locking helpers, `SuperVersion` lifetime management, foreground read APIs, column-family create/drop, iterator and snapshot creation, property/metadata accessors, options-file persistence, database destruction, latest-sequence lookup helpers, and the beginning of external SST ingestion preparation/commit. The chunk ends inside `DBImpl::CommitFileIngestionHandles()` immediately after ingestion jobs run and register their ranges; the later commit/install/cleanup path continues beyond this chunk.

This file is one part of a split `DBImpl` implementation. Open/recovery, write-batch application, flush/compaction scheduling, file deletion details, readonly/secondary DBs, and debug/experimental APIs are implemented in sibling files such as `db_impl_open.cc`, `db_impl_write.cc`, `db_impl_compaction_flush.cc`, `db_impl_files.cc`, `db_impl_readonly.cc`, and `db_impl_secondary.cc`.

## Purpose

The code in this chunk provides the core runtime shell around a RocksDB database instance:

- initialize immutable/mutable DB state, table cache, version set, write queues, WAL manager, periodic tasks, and column-family memtable access;
- coordinate orderly shutdown, background-work cancellation, WAL closure, manifest close, obsolete-file cleanup, options persistence, and DB lock release;
- recover from background errors by stopping background work, syncing sequence state, repairing MANIFEST writer state, flushing memtables, purging obsolete files, clearing errors, and rescheduling work;
- expose the main foreground read surface (`Get`, `GetEntity`, `MultiGet`, `MultiGetEntity`, iterators, key-existence probes);
- manage `SuperVersion` references so readers see a stable view of memtables and SST metadata while flushes/compactions install newer versions;
- support user-defined timestamps, timestamped snapshots, wide columns, blob-backed values, and direct-write blob resolution;
- create/drop column families and persist option changes to MANIFEST and OPTIONS files;
- provide metadata, property, statistics, trace, approximate-size, WAL, and live-file helpers used by the public C++ DB API and tests;
- stage external SST ingestion across one or more column families before final commit.

## Important APIs, Types, And Functions

### Construction, Identity, And Shared State

- `DBImpl::DBImpl()` sanitizes options, initializes the environment/file-system wrappers, mutexes, `ErrorHandler`, `EventLogger`, table cache, write queues, write controller, WAL manager, `VersionSet`, `ColumnFamilyMemTablesImpl`, blob callback, and periodic task function map. It logs build/version/options/support information and generates a DB session ID.
- `GetCompressionFlush()` chooses flush compression based on universal-compaction options and per-level compression settings.
- `DumpSupportInfo()` and `DumpRocksDBBuildVersion()` write capability/build metadata to the info log.
- `GenerateDbSessionId()`, `SetDbSessionId()`, `GetDbIdentity()`, `GetDbIdentityFromIdentityFile()`, and `GetDbSessionId()` expose persistent DB identity and per-open session identity.

### Background Error Recovery And Shutdown

- `Resume()` is the public entry for manual recovery from stopped DB/background work. It refuses concurrent recovery and delegates to `error_handler_.RecoverFromBGError(true)`.
- `ResumeImpl()` is the recovery core. It waits for flush/compaction/pressure callbacks, synchronizes last sequence with allocated sequence for two-write-queue mode, handles fatal background errors, forces a new MANIFEST edit if recovering from MANIFEST I/O error, flushes all column families or retries error-recovery flushes, purges obsolete files, clears background error state, optionally schedules a catch-up flush, enqueues compactions for all column families, and wakes waiters.
- `WaitForBackgroundWork()` and `WaitForAsyncFileOpen()` block on scheduled background counters and async file-open state.
- `CancelAllBackgroundWork()` unregisters periodic tasks, optionally performs a final shutdown flush for unpersisted data or blob direct-write column families, cancels compaction-service jobs, sends shutdown notifications, sets `shutting_down_`, and optionally waits for background work.
- `Close()`, `CloseImpl()`, `CloseHelper()`, and `~DBImpl()` coordinate close idempotence through `closing_mutex_`/`closed_`, reject close when timestamped snapshots remain, stop background work, drain flush/compaction queues, release default/persistent-stats handles, purge obsolete files, write close-time WAL markers, clear WAL writers, delete recovered transactions, untrack SST files, close `VersionSet`/directories/info log/SST manager, and release the DB lock.
- `MaybeWriteWalMarkersToManifestOnClose()` persists close-time log-number/min-WAL markers when safe, reducing next-open recovery work for empty column families and empty/new WALs.

### Blob Direct Write

- `MaybeInitBlobDirectWriteColumnFamily()` creates a `BlobFilePartitionManager` for column families with blob direct-write enabled and registers the CF in an atomic counter.
- `HasAnyBlobDirectWriteColumnFamily*()`, `HasInFlightBlobDirectWriteFilesWithLockHeld()`, `RegisterBlobDirectWriteColumnFamily()`, and `UnregisterBlobDirectWriteColumnFamily()` track blob direct-write shutdown requirements.
- `ResolveDirectWritePlainValue()`, `ResolveDirectWriteWideColumns()`, and `MaybeResolveDirectWriteValue()` resolve blob indexes that may exist in memtables before flush/manifest registration makes the blob files visible through normal `Version` metadata. They reject resolution under `kBlockCacheTier` because it can require blob file I/O.
- `MaybeResolveMemtableBlobValue()` and `PostprocessMemtableValueRead()` handle blob-backed memtable values and maintain correct `PinnableSlice`/wide-column output state after reads.

### Periodic Tasks And Statistics

- `ComputeTriggerCompactionPeriod()` picks a periodic compaction wakeup interval from DB-level stats periods and per-CF time-based compaction settings.
- `StartPeriodicTaskScheduler()`, `CancelPeriodicTaskScheduler()`, and `RegisterRecordSeqnoTimeWorker()` register/unregister dump-stats, persist-stats, info-log flush, periodic compaction, and sequence-number-to-time tasks.
- `PersistStats()` writes ticker deltas either to the persistent stats column family or to in-memory `stats_history_`, purging old in-memory snapshots when over budget.
- `GetStatsHistory()` selects persistent or in-memory stats iterators. `FindStatsByTime()` supports in-memory iterator lookup.
- `DumpStats()` collects DB/CF stats, probes distinct block caches for problems, optionally dumps malloc stats, and logs statistics.
- `FlushInfoLog()` periodically flushes the info log to improve crash/hang diagnostics.

### Options, WAL, And Manifest Helpers

- `SetOptions()` mutates per-CF mutable options under `options_mutex_`, uses a no-manifest dummy `VersionEdit` to update versions atomically with DB mutex held, installs new `SuperVersion`s, persists OPTIONS files, and refreshes sequence-time worker registration when relevant options change.
- `SetDBOptions()` mutates DB-level options, validates all CFs against the new options, increases background threads if needed, updates periodic stats tasks, table-cache capacity, fast-SST-open behavior, delayed write rate, WAL size limits, compaction file options, and may switch WALs when WAL settings change. It then persists an OPTIONS file.
- `WriteOptionsFile()`, `RenameTempFileToOptionsFile()`, `DeleteObsoleteOptionsFiles()`, `CaptureOptionsFileNumber()`, and `ReleaseOptionsFileNumber()` maintain current OPTIONS files and retain only recent obsolete options files.
- `FlushWAL()`, `SyncWAL()`, `SyncWalImpl()`, `ApplyWALToManifest()`, `MarkLogsSynced()`, and `MarkLogsNotSynced()` flush/sync active and inactive WALs, optionally record WAL metadata in MANIFEST, sync WAL directories, close/reclaim inactive WALs, and update WAL sync state under `wal_write_mutex_`.
- `LockWAL()` and `UnlockWAL()` implement a nested WAL lock by entering write queues, acquiring a write-controller stop token, flushing WAL buffers, and waiting for write-stall state to clear before unlock returns.
- `GetOpenWalSizes()`, `WALBufferIsEmpty()`, `GetUpdatesSince()`, `GetLatestSequenceNumber()`, and `SetLastPublishedSequence()` expose WAL and sequence-number state.

### SuperVersion, Iterators, And Reads

- `GetAndRefSuperVersion()`, `ReturnAndCleanupSuperVersion()`, `CleanupSuperVersion()`, `CleanupIteratorSuperVersion()`, `SuperVersionHandle`, and `GetMergeOperandsState` manage stable read views across memtables and SST metadata. Cleanup can be synchronous or deferred through purge queues when `avoid_unnecessary_blocking_io` or iterator cleanup options request background cleanup.
- `NewInternalIterator()` builds a merged internal iterator over mutable memtable, immutable memtables, range tombstones, and SST files. It supports multiscan pruning and registers cleanup for the referenced `SuperVersion`.
- `Get()`, `GetImpl()`, and `GetEntity()` validate read `io_activity`, timestamp compatibility, snapshots/read callbacks, acquire `SuperVersion`, check mutable and immutable memtables, fall back to current version SSTs, resolve merges/blobs/wide columns, record stats, and clean up the `SuperVersion`.
- `ShouldReferenceSuperVersion()` chooses whether `GetMergeOperands()` results should retain a `SuperVersion` reference rather than copying many/large merge operands.
- `MultiCFSnapshot()` obtains a consistent snapshot and `SuperVersion`s across one or more column families. It has a single-CF fast path and a multi-CF retry path that takes the DB mutex on the last try or for persisted-tier reads.
- `MultiGet()`, `MultiGetCommon()`, `PrepareMultiGetKeys()`, `MultiGetWithCallback()`, `MultiGetImpl()`, and `MultiGetEntity()` sort keys by CF and comparator order, batch in `MultiGetContext` chunks, read memtables then SSTs, honor deadlines and value-size soft limits, resolve direct-write blob values, and report per-key statuses.
- `KeyMayExist()` performs a cache-tier `GetImpl()` and treats `Incomplete` as “may exist.”
- `NewIterator()`, `NewIteratorImpl()`, `NewIterators()`, `NewCoalescingIterator()`, `NewAttributeGroupIterator()`, and `NewMultiCfIterator()` create arena-wrapped DB iterators, tailing `ForwardIterator`s, multi-CF coalescing iterators, and attribute-group iterators. They validate timestamp use, disallow persisted-tier iterators, and require comparator compatibility for multi-CF iteration.

### Column Families And Snapshots

- `CreateColumnFamily()`, `CreateColumnFamilies()`, `CreateColumnFamilyImpl()`, and `WrapUpCreateColumnFamilies()` validate options and names, create CF directories, write a MANIFEST `AddColumnFamily` edit while holding the write thread, initialize blob direct-write if needed, install a `SuperVersion`, update snapshot support, persist OPTIONS, and create thread-status metadata.
- `DropColumnFamily()`, `DropColumnFamilies()`, and `DropColumnFamilyImpl()` reject dropping the default CF, write a MANIFEST drop edit, unregister blob direct-write, update memory-state/snapshot-support bookkeeping, optionally refresh sequence-time worker registration, persist OPTIONS, and erase thread-status metadata.
- Base `DB::CreateColumnFamily*()` and `DB::DropColumnFamily*()` return `NotSupported`; `DBImpl` supplies the implementation. `DB::DestroyColumnFamilyHandle()` rejects the default handle and deletes non-default handles.
- `GetSnapshot()`, `GetSnapshotForWriteConflictBoundary()`, `GetSnapshotImpl()`, `CreateTimestampedSnapshot()`, `CreateTimestampedSnapshotImpl()`, `GetTimestampedSnapshot()`, `GetTimestampedSnapshots()`, `ReleaseTimestampedSnapshotsOlderThan()`, and `ReleaseSnapshot()` manage regular and timestamped snapshots. Snapshot release can update oldest-snapshot markers, mark bottommost files/range-tombstone files for compaction, enqueue compactions, and recalculate thresholds.

### Properties, Metadata, Approximation, And Destruction

- `GetProperty()`, `GetMapProperty()`, `GetIntProperty()`, `GetIntPropertyInternal()`, `GetAggregatedIntProperty()`, `GetPropertyHandleOptionsStatistics()`, and `ResetStats()` expose DB/CF properties and internal stats, sometimes releasing the DB mutex to compute version-dependent values outside the mutex.
- `GetPropertiesOfAllTables()`, `GetPropertiesOfTablesInRange()`, and `GetPropertiesOfTablesByLevel()` pin the current version while reading table properties.
- `GetApproximateMemTableStats()` and `GetApproximateSizes()` estimate entry count/bytes over memtables, SSTs, and optionally prorated blob files, with timestamp-aware range conversion.
- `DeleteFilesInRanges()` deletes clean fully-covered non-L0 files through a foreground `VersionEdit`, installs a new `SuperVersion`, and purges obsolete files outside the mutex.
- `GetLiveFilesMetaData()`, `GetLiveFilesChecksumInfo()`, `GetColumnFamilyMetaData()`, and `GetAllColumnFamilyMetaData()` expose live-file and CF metadata. `GetColumnFamilyMetaData()` takes the DB mutex because file metadata fields such as `being_compacted` are not race-free for lockless reads.
- `DestroyDB()` locks the DB, enumerates DB paths, CF paths, WAL/archive paths, deletes table/WAL/blob/meta files through `DeleteUnaccountedDBFile()` where needed, waits for SST manager trash buckets, removes the lock file and directories, and intentionally ignores some directory-delete failures after state deletion.

### External File Ingestion

- `IngestExternalFile()` wraps a single-CF ingestion request into `IngestExternalFiles()`.
- `FileIngestionHandleImpl` is a prepared-ingestion handle containing one or more `ExternalSstFileIngestionJob`s, a pending-output file-number reservation, a `fill_cache_` setting, and a `consumed_` guard. Its destructor rolls back uncommitted/unaborted prepared files as a safety net.
- `PrepareFileIngestion()` validates arguments, duplicate CFs, non-empty external file lists, consistent `fill_cache`, `ingest_behind`, `atomic_replace_range`, generated-file/global-seqno combinations, and move/link exclusivity. It reserves file numbers, prepares per-CF ingestion jobs, cleans up on failure, and returns a handle on success.
- `RollbackPreparedFileIngestion()` aborts staged ingestion jobs, releases pending-output protection, marks the handle consumed, and decrements outstanding prepared-ingestion count.
- `CommitFileIngestionHandles()` begins by validating handles, merging same-CF jobs, acquiring per-CF ingest read locks before the DB mutex, entering write queues, waiting for pending writes, determining whether flushes are needed, flushing relevant memtables or atomically flushing all, running ingestion jobs, and registering ingestion ranges. The chunk stops at line 7130 before the sequence-barrier update and MANIFEST commit logic complete.

## Control Flow

Constructor flow builds long-lived dependencies first (`ImmutableDBOptions`, file system, mutexes, error handler, table cache, version set, CF memtables), then logs state and initializes optional write-buffer-manager stall integration. It does not perform DB recovery in this file; recovery/opening is in sibling open code.

Foreground reads use a consistent pattern. Validate `ReadOptions` and timestamp constraints, trace if enabled, acquire a `SuperVersion`, choose a snapshot sequence after the `SuperVersion` is referenced, read mutable memtable, read immutable memtables, then read SSTs through `Version`. Merge operands, range tombstones, blob indexes, direct-write blobs, wide columns, and user-defined timestamps are handled in post-processing before stats are recorded and the `SuperVersion` is returned or cleaned.

`MultiGet` adds grouping and snapshot coordination. It builds `KeyContext`s, sorts keys by CF ID and comparator order unless the input is already sorted, obtains one consistent sequence number and `SuperVersion` set across CFs, then processes keys in bounded `MultiGetContext` batches. Deadline expiration and soft value-size limit abort the remaining key range with per-key statuses.

Iterator creation pins a `SuperVersion` for each iterator. Non-tailing iterators use `NewArenaWrappedDbIterator()` so the DB iterator, merging iterator, and child iterators live in one arena-backed allocation. Tailing iterators use `ForwardIterator`. Multi-CF iterators first create per-CF child iterators, then wrap them in coalescing or attribute-group iterator implementations.

Option mutation is serialized through `options_mutex_`. Per-CF option changes use a dummy no-manifest `VersionEdit` to keep option application and `SuperVersion` installation ordered with the in-memory `Version`. DB option changes validate all active CFs, update scheduler/background/thread/table-cache/WAL state, possibly switch WALs under the write thread, and persist an OPTIONS file.

Shutdown flow is intentionally staged. It first prevents background-error recovery races, then publishes shutdown/cancellation, unschedules env work, drains background counters and queues, cleans handles and obsolete files, writes optional close-time WAL markers, releases WAL writers, closes `VersionSet`, waits for late purge work, erases cache entries, resets the version set, unlocks DB lock, closes owned resources, and converts abort-style resource errors into `Incomplete`.

External SST ingestion is a two-phase local workflow. Prepare reserves file numbers and stages internal files without changing DB metadata. Commit later blocks writes, flushes conflicting memtable ranges, runs ingestion jobs, and, after this chunk, will persist version edits and install superversions. Dropping a handle before commit/abort rolls back prepared files.

## State And Persistence Behavior

Persistent state changes in this chunk occur through MANIFEST edits, OPTIONS files, WAL sync markers, persisted stats writes, external SST ingestion staging/commit, column-family create/drop, range file deletions, snapshots indirectly influencing compaction metadata, and full DB destruction.

MANIFEST state is updated by `VersionSet::LogAndApply()` for CF creation/drop, close-time WAL markers, foreground file deletion, WAL metadata application, and ingestion commit. MANIFEST write failures are routed to `error_handler_` as `BackgroundErrorReason::kManifestWrite` when visible through `versions_->io_status()`.

WAL state is tracked in `logs_`, `cur_wal_number_`, `wal_dir_synced_`, and WAL metadata edits. `SyncWalImpl()` distinguishes active WAL `SyncWithoutFlush()` from inactive WAL `Sync()`, can close inactive WALs, marks WALs synced/not-synced under `wal_write_mutex_`, and may add WAL metadata to a `VersionEdit` for MANIFEST tracking.

Snapshot state lives in `snapshots_` and `timestamped_snapshots_`. Regular snapshots must be released. Timestamped snapshots are shared pointers with a `DBImpl::ReleaseSnapshot` deleter and are also subject to close-time leak checks through `MaybeReleaseTimestampedSnapshotsAndCheck()`.

`SuperVersion` state is a central read-stability contract. Readers hold references while accessing memtables/current versions; cleanup may delete old superversions and purge obsolete files. Thread-local `SuperVersion` return paths reduce ref churn, while iterator and merge-operand outputs can retain cleanup callbacks.

Options persistence is best-effort but surfaced to callers when a mutation succeeds in memory but the OPTIONS file fails to persist. Temporary options files are renamed to numbered OPTIONS files and directory-synced; older options files are pruned.

Persistent stats may be written through the normal `Write()` path into the persistent stats CF. In-memory stats history is volatile and bounded by `stats_history_buffer_size`.

DestroyDB removes persistent DB files and directories while holding the DB lock. It uses SST file manager trash buckets for accounted data files and waits for trash cleanup before returning.

## Dependencies And Integration Points

This chunk depends heavily on:

- `db_impl.h` for member declarations and cross-file helpers;
- `VersionSet`, `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `VersionEdit`, and `ColumnFamilySet` for MANIFEST/version state;
- `MemTable`, `MemTableList`, `SuperVersion`, `LookupKey`, `MergeContext`, `ReadCallback`, and `PinnedIteratorsManager` for read paths;
- `WriteThread`, `WriteController`, `WriteContext`, and write queues for WAL locking, option mutation, and ingestion;
- `log::Writer`, `WritableFileWriter`, `WALManager`, `FSDirectory`, `FileSystem`, and `Env` for WAL/file operations;
- `PeriodicTaskScheduler`, `Statistics`, `InternalStats`, stats history iterators, and thread-status utilities;
- blob components including `BlobFilePartitionManager`, `BlobFetcher`, `BlobIndex`, blob file cache, and wide-column serialization;
- iterator implementations including `ArenaWrappedDBIter`, `DBIter`, `ForwardIterator`, `CoalescingIterator`, `AttributeGroupIteratorImpl`, and merge/two-level iterators;
- external ingestion machinery in `ExternalSstFileIngestionJob`;
- local helpers from sibling files such as `FindObsoleteFiles()`, `PurgeObsoleteFiles()`, `FlushAllColumnFamilies()`, `FlushMemTable()`, `AtomicFlushMemTables()`, `MaybeScheduleFlushOrCompaction()`, `SwitchWAL()`, `InstallSuperVersion*()`, and `WaitForPendingWrites()`.

Public integration points are `rocksdb::DB` methods, `ColumnFamilyHandle`, `Snapshot`, `Iterator`, `MultiScan`, `FileIngestionHandle`, trace APIs, property APIs, and admin helpers such as `DestroyDB()` and `ListColumnFamilies()`.

## Risks And Edge Cases

- The close path has many mutex-unlocked windows. Late iterator/Get cleanup can schedule purge work after the early background wait, so the final purge drain is required before object destruction.
- Close-time WAL marker optimization must not advance log numbers for CFs with unflushed memtables or immutable memtables, or recovery could skip needed WAL records.
- Two-write-queue recovery must synchronize last sequence with allocated sequence before new WAL/memtable creation to avoid sequence-number regression on later recovery.
- Direct-write blob reads before flush can require fallback blob I/O. `kBlockCacheTier` returns `Incomplete`, and callers must distinguish “may exist” behavior from hard failures.
- `PinnableSlice` and merge-operand outputs can depend on `SuperVersion`, pinned iterators, or merge contexts. Incorrect cleanup attachment would create dangling reads or excessive copying.
- `MultiCFSnapshot()` can retry without the mutex and eventually take the mutex; mistakes in earliest memtable sequence checks can produce inconsistent multi-CF snapshots.
- Timestamp support rejects reads without matching timestamp options and rejects reads older than collapsed history. Timestamped snapshots enforce monotonic timestamp/sequence relationships.
- Column-family creation rejects empty names to avoid non-persisted ambiguous CFs; dropping the default CF is rejected. Partial multi-create/drop can leave earlier CFs changed and later ones not applied.
- Dynamic option updates mutate memory before persisting OPTIONS files; callers can observe an error when in-memory changes succeeded but file persistence failed.
- WAL locking uses nested count state and write-controller stop tokens. A failed `FlushWAL(false)` during lock acquisition must unlock to avoid leaving writes stalled.
- `DeleteFilesInRanges()` only deletes clean non-L0 files and skips files being compacted or largest-key-equal-to-exclusive-end. It must clear `being_compacted` after MANIFEST application.
- `DestroyDB()` ignores some delete-dir failures after deleting state. It also has to delete files from DB paths, CF paths, WAL dirs, archives, and meta DB directories consistently.
- Prepared file-ingestion handles are RAII rollback objects. Double commit/abort is rejected, and destructor rollback prevents leaked staged files, but users must not rely on commit behavior after a handle is dropped.
- This chunk ends mid-`CommitFileIngestionHandles()`, so complete risk analysis for ingestion commit persistence, sequence-number publication, and cleanup requires the next chunk.

## Test Signals

Relevant tests in the RocksDB tree should exercise:

- DB open/close/destructor behavior, including unreleased snapshot close failure, background work cancellation, WAL close errors, and info-log/SST-manager shutdown;
- background-error recovery paths for flush/MANIFEST/WAL errors and resume sequencing;
- WAL APIs: manual WAL flush, sync, lock/unlock nesting, WAL metadata tracking, inactive WAL close/recycle, and `GetUpdatesSince()`;
- direct reads: `Get`, `GetEntity`, merge operands, timestamp reads, blob-backed values, direct-write blob pre-flush reads, `KeyMayExist`, and block-cache-tier incomplete behavior;
- `MultiGet`/`MultiGetEntity` across one and multiple column families, sorted-input behavior, deadlines, value-size soft limits, merge-operand thresholds, timestamp validation, and direct-write blob resolution;
- iterator creation for normal, tailing, multi-CF coalescing, and attribute-group iterators, including comparator mismatch and persisted-tier rejection;
- column-family create/drop, duplicate/empty names, default-CF drop rejection, option persistence, blob direct-write registration, and thread-status metadata cleanup;
- `SetOptions()` and `SetDBOptions()` behavior around scheduler changes, background-thread increases, table-cache capacity, WAL switching, and OPTIONS file persistence failures;
- regular and timestamped snapshots, monotonic timestamp constraints, release-triggered compaction marking, and close with outstanding timestamped snapshots;
- approximate sizes/memtable stats, live-file metadata, table properties, DB/CF metadata, and property aggregation;
- `DestroyDB()` cleanup across DB path, WAL dir, archive dir, CF paths, blob files, table files, lock file, and SST manager trash;
- external SST ingestion prepare/abort/destructor rollback and the visible first half of commit: duplicate CF validation, fill-cache consistency, ingest-behind constraints, file-number reservation, flush-before-ingest decisions, dropped-CF rejection, and ingestion job `Run()`/range registration.

The many `TEST_SYNC_POINT` hooks in this chunk are important signals for race-sensitive tests. They target resume sequencing, close waiting, WAL sync, option changes, reads after `SuperVersion` acquisition, `MultiCFSnapshot` retry behavior, iterator snapshot assignment, ingestion flush/run ordering, and DB session ID generation.
