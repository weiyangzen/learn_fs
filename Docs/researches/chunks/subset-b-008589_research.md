# sources/storage-engines/rocksdb/db/db_etc2_test.cc lines 1-7090

## Scope

This chunk covers the first 7,090 lines of RocksDB's `db_etc2_test.cc`. It is a large GoogleTest file chunk whose code is mostly regression and integration tests for secondary DB behavior: read-only open paths, column families, WAL replay filtering, shared write-buffer limits, block cache/index/filter pinning, compaction stalls/cancellation/manual pause behavior, trace/replay, prefix bloom behavior, row cache and snapshots, recovery races, file temperature metadata/statistics, point-in-time recovery, and L0 epoch-number ordering. The chunk ends at the opening of `RecoverEpochNumber`; the body of that test is outside this chunk.

The file uses `DBTestBase` helpers to create DBs, write keys, flush memtables, compact files, reopen with different options, inspect file metadata, and inject faults through sync points or test env wrappers. Most tests validate production behavior through public APIs while selectively reaching into `DBImpl` and test-only methods for deterministic scheduling and metadata assertions.

## Purpose

The tests in this chunk protect correctness contracts that are not isolated to one production module. They verify that DB open/reopen, WAL recovery, cache ownership, compaction scheduling, file metadata, trace execution, and temperature-aware I/O remain consistent under option changes, failure injection, and concurrent work.

Major themes:

- read-only open must behave predictably with missing directories, column-family descriptors, WAL paths, and cleanup during close;
- WAL filters must be able to continue, skip, stop, rewrite, or reject records without corrupting later reopen state;
- shared write-buffer accounting across column families and DB instances must pick flush victims correctly and release cache-charged memory;
- block-based table index/filter caching, prefix blooms, partitioned indexes, row cache, and pinnable slices must preserve visibility and ownership semantics across reopen, compaction, and mmap reads;
- manual and automatic compactions must pause, cancel, overlap, notify listeners, and update metadata without stale registrations or inconsistent LSM state;
- trace writing/replay must preserve operation counts, column-family mapping, iterator bounds, unsupported-record behavior, and manual execution error handling;
- file temperature hints and statistics must be persisted, repaired, surfaced through metadata/properties, used in checkpoint copy hints, and reflected in iostats/ticker counters;
- recovery paths must tolerate point-in-time corruption, failed filesystem operations, sync failures, manifest rewrite errors, and L0 epoch-number ordering.

## Important Fixtures, Helpers, and Types

- `DBTest2` derives from `DBTestBase` with test DB name `db_etc2_test` and `env_do_fsync=true`. It supplies the common DB lifecycle and helper APIs used throughout the chunk: `CurrentOptions()`, `DestroyAndReopen()`, `Reopen()`, `CreateAndReopenWithCF()`, `TryReopenWithColumnFamilies()`, `Put()`, `Merge()`, `Delete()`, `Flush()`, `Compact()`, `MoveFilesToLevel()`, `Get()`, `FilesPerLevel()`, `NumTableFilesAtLevel()`, `dbfull()`, and `handles_`.
- `PartitionedIndexTestListener` checks `FlushJobInfo::table_properties` for partitioned index metadata, especially multiple index partitions and internal-key encoding.
- `PrefixFullBloomWithReverseComparator` parameterizes prefix bloom behavior with a reverse comparator and optional cached filters.
- `DBTestSharedWriteBufferAcrossCFs` parameterizes the old `db_write_buffer_size` interface, explicit `WriteBufferManager`, and cache-charged `WriteBufferManager`.
- `ValidateKeyExistence()` uses `DB::MultiGet()` to assert recovered key presence or absence after WAL filtering.
- Several local `WalFilter` subclasses implement recovery-time behavior: record skipping/stopping/corruption, batch replacement with fewer keys, invalid addition of extra keys, and column-family/log-number observation.
- `CompactionStallTestListener`, `CancelCompactionListener`, and listener classes inside temperature tests validate compaction event metadata and file I/O temperature propagation.
- `PinL0IndexAndFilterBlocksTest` parameterizes `max_open_files` and table-reader preloading behavior for L0 index/filter pinning.
- `UniqueIdCallback` and `MockPersistentCache` implement a mock persistent cache with unique page ids, in-memory page storage, and sync-point-based unique-id support.
- `TraceExecutionResultHandler` implements `TraceRecordResult::Handler` and counts writes, gets, multigets, and iterator seeks while validating trace result timestamps/types.
- `DummyOldStats` implements the legacy `Statistics` interface to prove older stats implementations still receive tick/histogram calls.
- `RenameCurrentTest` parameterizes failures before and after `CURRENT` file rename to test distributed-filesystem no-overwrite behavior.
- File-temperature tests define local filesystem wrappers over `FileTemperatureTestFS`, including `MyTestFS` for write-option validation and `NoLinkTestFS` to force checkpoint copies instead of hard links.

## Covered APIs and Integration Points

- Public DB APIs: `DB::Open`, `DB::OpenForReadOnly`, `DB::Close`, `Put`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `Write`, `Flush`, `CompactRange`, `CompactFiles`, `IngestExternalFile`, `SetOptions`, `GetOptions`, `GetSnapshot`, `ReleaseSnapshot`, `NewIterator`, `Get`, `MultiGet`, `GetProperty`, `GetMapProperty`, `GetColumnFamilyMetaData`, `GetLiveFilesStorageInfo`, `DisableFileDeletions`, `EnableFileDeletions`, `GetSortedWalFiles`, `StartTrace`, `EndTrace`, and `NewDefaultReplayer`.
- Column-family APIs: `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `CreateColumnFamily`, `GetColumnFamilyHandleUnlocked`, `DestroyColumnFamilyHandle`, and per-CF flush/read/write helpers.
- Recovery and WAL APIs: `WalFilter`, `WalFilter::LogRecord`, `WalFilter::LogRecordFound`, `WalFilter::ColumnFamilyLogNumberMap`, `WALRecoveryMode::kPointInTimeRecovery`, `WriteBatch`, `WriteBatch::Handler`, `OptionsForLogIterTest()`, and log corruption/fault injection hooks.
- Table/cache APIs: `BlockBasedTableOptions`, `NewBlockBasedTableFactory`, `NewBloomFilterPolicy`, `NewLRUCache`, `PersistentCache`, partitioned index settings, prefix extractors, row cache, block cache ticker counters, and pinnable slice reads.
- Compaction APIs and internals: `CompactRangeOptions`, `CompactionOptions`, `BottommostLevelCompaction`, `CompactionReason`, `CompactionJobInfo`, `TEST_CompactRange`, `TEST_WaitForCompact`, `TEST_WaitForBackgroundWork`, `TEST_WaitForFlushMemTable`, `TEST_write_controler`, and `GetLevelFileMetadatas`.
- Trace/replay APIs: `TraceOptions`, `TraceFilterType`, `TraceReader`, `TraceWriter`, `NewFileTraceReader`, `NewFileTraceWriter`, `Replayer`, `ReplayOptions`, trace record types, trace result types, and `TraceRecordResult::Accept`.
- File metadata and admin APIs: `SstFileWriter`, `Checkpoint`, `experimental::UpdateManifestForFilesState`, `LiveFileStorageInfo`, `LiveFileMetaData`, `SstFileMetaData`, `ColumnFamilyMetaData`, `ParseFileName`, `LogFileName`, and DB properties such as live SST size at temperature.
- Fault/concurrency utilities: `SyncPoint`, `FaultInjectionTestEnv`, `CompositeEnvWrapper`, test file systems, `port::Thread`, `std::thread`, `test::SleepingBackgroundTask`, atomics, test environment read/write counters, random-read failure injection, and sync-failure corruption flags.
- Observability: `Statistics` tickers for block cache, row cache, read amplification, file temperatures, persistent cache, and last/non-last level reads; `IOStatsContext::file_io_stats_by_temperature`; `PerfContext` CPU-time counters.

## Control Flow and Behavioral Areas

### Read-only open and basic DB metadata

`OpenForReadOnly` and `OpenForReadOnlyWithColumnFamilies` test failed read-only opens against a missing DB path. With `create_if_missing=true`, `OpenForReadOnly` fails but creates the DB directory, so the tests enumerate and delete its contents before removing the directory. With `create_if_missing=false`, the open fails without creating a directory. The column-family variant repeats the same behavior with default and named CF descriptors.

`ReadOnlyDBWalInDbPathInitialized` creates a normal DB with WAL/data, then opens it read-only in default and column-family forms. The important regression signal is that closing the read-only DB must initialize and read `wal_in_db_path_` safely while `CloseHelper` triggers obsolete-file cleanup.

`IteratorPropertyVersionNumber` creates iterators before and after writes/flushes and reads `rocksdb.iterator.super-version-number`. It expects the super-version number to increase after a flush but not after a later memtable-only write, and an old iterator must keep reporting its original version number after seeking.

`CacheIndexAndFilterWithDBRestart` and `MaxSuccessiveMergesChangeWithDBRecovery` are small reopen smoke tests for cached index/filter options and changing `max_successive_merges` during recovery after merge operands were written with a put-style merge operator.

### Index/filter, prefix bloom, row cache, and table-reader behavior

`PartitionedIndexUserToInternalKey` writes many versions of a small distinct key set while holding snapshots and flushing under two-level index search. The listener asserts partitioned index properties use internal keys rather than user keys.

`PrefixFullBloomWithReverseComparator` configures `ReverseBytewiseComparator`, a capped prefix extractor, whole-key filtering disabled, and optional filter caching. It verifies seek order and prefix bloom interactions for reverse-sorted data, including missing prefix behavior.

The `PinL0IndexAndFilterBlocksTest` suite creates L0 and L1 files with cached index/filter blocks and `pin_l0_filter_and_index_blocks_in_cache=true`. It asserts freshly flushed L0 index/filter blocks are added to cache and pinned, L0 reads do not change hit/miss counters, L1 reads/prefetches do change counters, and non-L0 prefetching is disabled during `DB::Open()` while L0 behavior depends on table-reader preloading and `max_open_files`.

`PrefixBloomReseek` and `PrefixBloomFilteredOut` build L1 files whose prefixes interact with bloom filters. They protect iterator reseek behavior when a bloom-filtered file iterator is invalidated and the cursor later needs to move backward, and they document legacy prefix seek versus `prefix_seek_opt_in_only`.

`ChangePrefixExtractor` creates data under one fixed-prefix length, reopens with another, and proves prefix blooms are only used when seek key and bounds make the new prefix extractor safe. It runs both partitioned and non-partitioned filters and asserts filter-match counters only where expected.

`BlockBasedTablePrefixIndexSeekForPrev` and `BlockBasedTablePrefixGetIndexNotFound` cover hash index/prefix index edge cases: `SeekForPrev()` with existing and non-existing prefixes, empty hash buckets, hash conflicts, and point lookup across several files where some files do not contain the requested prefix.

`AutoPrefixMode1` is a broad test of `ReadOptions::auto_prefix_mode` with bytewise and reverse comparators, changing upper bounds, `Seek`, `SeekForPrev`, `SeekToFirst`, and `SeekToLast`. It documents both valid optimizations and a known bug section involving short keys and upper bounds where auto-prefix filtering can hide a valid next key that total-order seek finds.

`RowCacheSnapshot` shows row cache keys include snapshot sequence semantics. It writes multiple versions, takes snapshots before and after flushes, and verifies row-cache misses/hits for current and snapshot reads without returning the wrong version.

`PinnableSliceAndMmapReads` validates that mmap-backed reads do not pin data when files may be unmapped by compaction or evicted from table cache, but read-only mode with `max_open_files=-1` can safely return a pinned value. The disabled iterator pinned-memory test documents desired data-block pinning limits for iterators and compaction input iterators.

### Shared write buffer and memory accounting

`SharedWriteBufferAcrossCFs` configures deterministic arena allocation through sync points, disables WAL, and writes across default plus three user CFs. It validates shared write-buffer soft-limit behavior under old `db_write_buffer_size`, explicit `WriteBufferManager`, and cache-charged write-buffer manager modes. The expected flush victim is tied to mutable memtable sizes and CF flush history; file counts after each phase prove the correct CF was flushed. When cache charging is enabled, cache usage should rise while memtables are charged and fall after closing and clearing write-buffer manager ownership.

`SharedWriteBufferLimitAcrossDB` repeats the shared write-buffer limit across two DB instances using the same `WriteBufferManager`. It writes large values to DB1 CFs and DB2 default, waits for flushes/background work, and asserts global pressure chooses flushes across DB boundaries without over-flushing unrelated CFs.

`TestWriteBufferNoLimitWithCache` configures `WriteBufferManager(0, cache)`, where zero means no memory limit but cache accounting is still used. A single write should charge significant dummy memory to the cache.

`BackgroundPurgeTest` ties write-buffer memory usage to iterator lifetime and background purge. After flush, a live iterator holds memory above the base usage. Deleting the iterator while a high-priority background task sleeps should not immediately free the memory; after scheduled high-priority work drains, usage returns to the base.

### WAL filtering and recovery semantics

`WalFilterTest` writes three WAL batches, then reopens with a filter that returns each `WalProcessingOption` at a selected record index. It verifies `kContinueProcessing` and `kCorruptedRecord` replay all records in point-in-time/non-paranoid recovery cases, `kIgnoreCurrentRecord` skips only that batch, and `kStopReplay` drops that and later batches. A second reopen without the filter proves skipped WALs are not replayed later.

`WalFilterTestWithChangeBatch` uses a `WriteBatch::Handler` to copy only a prefix of each batch into `new_batch` after a selected index. Recovery should preserve earlier batches unchanged and only the first key of later batches.

`WalFilterTestWithChangeBatchExtraKeys` tries to rewrite a batch by adding an extra key. The recovery path returns `NotSupported`, and a later reopen without the filter must recover the original DB unchanged. This protects against WAL filters expanding write batches beyond their original key set.

`WalFilterTestWithColumnFamilies` observes `ColumnFamilyLogNumberMap()` and `LogRecordFound()` to determine which WAL records are relevant per CF after one CF was flushed. It validates the filter receives enough log-number and CF-id/name information to attribute pre-flush and post-flush keys correctly: default CF only sees post-flush records, while the unflushed user CF sees all records.

`CrashInRecoveryMultipleCF`, `PointInTimeRecoveryWithIOErrorWhileReadingWal`, and `PointInTimeRecoveryWithSyncFailureInCFCreation` cover point-in-time recovery failure behavior. They corrupt logs, freeze the filesystem at recovery flush/manifest write sync points, inject read errors while reading WAL, and corrupt sync during CF creation/flush interleavings. Expected outcomes are controlled non-OK reopen for injected read/freeze failures and successful later reopen once the fault is removed.

### Compaction scheduling, cancellation, and races

`CompactionStall` creates enough L0 files to schedule multiple compactions while holding sync points around background compaction and listener notification unlocks. It validates compaction listener begin/end counts, compaction reason `kLevelL0FilesNum`, L0 file reduction, and no mismatch between compacting and compacted file counts.

`AutomaticCompactionOverlapManualCompaction` and `ManualCompactionOverlapManualCompaction` create overlapping ranges and force auto/manual or manual/manual compactions to run concurrently. Sync-point callbacks inject additional L0 files during compaction start. The tests ensure non-exclusive manual compactions and automatic compactions do not install overlapping lower-level files or break stats/LSM consistency.

`PausingManualCompaction1` through `PausingManualCompaction4` and `CancelManualCompaction1`/`2` test several manual compaction pause paths. They set cancellation atomics or call `DisableManualCompaction()`, then assert `CompactRange()` or `CompactFiles()` returns `IsManualCompactionPaused()`, files remain unchanged when paused before real work, and later compactions succeed after clearing cancellation. Sync points distinguish pausing before scheduling, at compaction job run, after some levels, and after processing a few key-values.

`CancelManualCompactionWithListener` adds an event listener and verifies begin/end notifications and statuses under cancellation before work, cancellation before notifications, and cancellation after a compaction job has effectively succeeded. Listener status expectations differ between `kIncomplete/kManualCompactionPaused` and `kOk/kNone`.

`CompactionOnBottomPriorityWithListener` configures universal compaction with only a bottom-priority thread available and asserts compaction is forwarded to the bottom-priority pool, exactly one compaction job runs, and listener begin/end callbacks match.

`LowPriWrite` uses compaction pressure tokens and blocked compaction to prove low-priority writes are rate-limited under compaction pressure while normal writes are not. After releasing compaction and waiting, both write classes should avoid rate limiting.

`RateLimitedCompactionReads` configures a reads-only rate limiter, optional compaction readahead, optional direct I/O, and blocked compaction scheduling. It measures bytes charged to `IO_LOW`/`IO_USER` during compaction reads, allowing direct-I/O footer overhead, and confirms foreground iterator reads after compaction do not add to the compaction read-rate-limiter totals.

`ReduceLevel` verifies the DB can reopen with fewer levels after manually compacting files down so no file remains above the new `num_levels`.

`TestCompactFiles` and `TestCancelCompactFiles` create external SSTs, ingest them, run `CompactFiles()` concurrently with another ingestion, and exercise `CompactionOptions::canceled` plus `DisableManualCompaction()`. They assert conflict/cancellation behavior does not lose files and that cancellation after the final check may still allow compaction to complete.

`SwitchMemtableRaceWithNewManifest` forces frequent manifest rollover while flushing a default CF concurrently with compaction triggered by another CF. It guards a race between memtable switching and new manifest creation.

`SameSmallestInSameLevel` builds several files containing the same user key and uses string-append merge operands to validate cascading/overlap logic when same smallest keys exist in one level.

`FileConsistencyCheckInOpen` injects a corruption status in `VersionBuilder::CheckConsistencyBeforeReturn` and expects reopen to fail when `force_consistency_checks=true`.

### Snapshot, visibility, iterator, and Get races

`FirstSnapshotTest` creates an initial snapshot with sequence number zero before writes and flushes, preserving the expected behavior of the first snapshot in an empty DB.

`DuplicateSnapshot` takes duplicate snapshots and write-conflict-boundary snapshots around writes, then inspects `SnapshotList::GetAll()` under DB mutex. Duplicates should not be counted, and the oldest write-conflict snapshot should match the first write-conflict-boundary snapshot.

`IterRaceFlush1`, `IterRaceFlush2`, and `IterRefreshRaceFlush` use sync points inside iterator creation/refresh to interleave a second write plus flush. Depending on when the iterator sequence number is assigned, the iterator must see either `v2` or `v1`; refreshed iterator must use the later sequence. `GetRaceFlush1` and `GetRaceFlush2` define a looser contract for `Get()` during the same race: it may see either version, but must not return not found.

`MemtableOnlyIterator` configures `ReadOptions::read_tier=kMemtableTier` and checks point lookups can read from memtable/immutable state, while iterators only enumerate current memtable entries. After flush the iterator returns nothing, and after a new write it returns only that new key.

`ReadCallbackTest` writes many versions of one key across two bottom-level SSTs, an L0 file, and a live memtable while holding snapshots. It calls internal `DBImpl::GetImpl()` with a custom `ReadCallback` for each sequence number and expects the value visible at that sequence. This guards callback visibility checks across memtable and SST reads.

`LiveFilesOmitObsoleteFiles` uses sync points and sleep to reproduce a race where obsolete WAL files could be returned by `GetSortedWalFiles()` after file deletions were disabled but before purge finished. It asserts every returned log still exists.

`SeekFileRangeDeleteTail` combines prefix extractor, snapshots, `DeleteRange`, flushes, and level movement to validate total-order seek skips a deleted tail and lands on the next live file range.

### Performance context, persistent cache, read amplification, and I/O counters

Linux-only `TestPerfContextGetCpuTime` and `TestPerfContextIterCpuTime` distinguish wall-clock `NowNanos()` timing from CPU-time `NowCPUNanos()` in perf-context counters. Sync points add huge mock wall time while CPU timing should remain below that injected wall-clock value; `find_table_nanos` should include it.

`PersistentCache` runs with compressed and uncompressed mock persistent cache, with and without block cache, and separate table options per CF. It writes many compressible values, flushes, reads all keys, and expects both persistent-cache hits and misses.

`ReadAmpBitmap` calculates expected useful bytes for randomly read internal key/value entries and compares it with `READ_AMP_ESTIMATE_USEFUL_BYTES` and `READ_AMP_TOTAL_READ_BYTES`, allowing less than 2 percent error. After iterating the whole DB, useful bytes should approximate total read bytes.

`ReadAmpBitmapLiveInCacheAfterDBClose` first verifies the filesystem supports stable unique IDs. It reads even keys to populate cache and read-amp bitmap, closes the DB, destroys the old statistics object, reopens with the same cache and new stats, reads odd keys, and verifies read-amplification accounting remains correct even when cached blocks outlive the original DB/statistics object.

`TestNumPread` uses the test env's random-read and random-file-open counters. It distinguishes prefetch-supported and non-prefetch-supported paths for flush verification, normal Get reads, compaction reads, and post-compaction Get reads.

`OldStatsInterface` installs `DummyOldStats` and verifies RocksDB still calls legacy `recordTick()` and `measureTime()` paths during writes, reads, and flushes.

### Trace and replay

`TraceAndReplay` starts a DB trace, records eight writes across default/user CFs, three gets, and two iterator seeks, then ends tracing and performs post-trace writes that must not appear. It opens another DB with matching CFs, creates a default replayer, asserts `Replay()` before `Prepare()` is incomplete, and replays at different thread counts and speeds. `TraceExecutionResultHandler` checks operation counts and non-negative latency. Replayed data must exist, while post-trace keys must remain absent.

`TraceAndManualReplay` repeats the trace with additional iterator operations using lower/upper bounds. It manually calls `Next()`/`Execute()` twice after `Prepare()` to prove trace replay can restart. For iterator trace results, it validates decoded bounds, valid result keys within bounds, and empty key/value for invalid iterator results. It then executes artificially constructed write/get/iterator/multiget trace records, checking success for valid CF ids, corruption for invalid CF ids, invalid argument for empty or size-mismatched `MultiGet`, and correct result/status/value arrays for mixed found/not-found multigets.

`TraceWithLimit` configures `max_trace_file_size=5`, writes several keys, and replays. Because the trace limit is too low, none of the writes should replay into the target DB.

`TraceWithSampling` sets `sampling_frequency=2`, writes five keys, and expects only every second sampled write (`b` and `d`) to replay.

`TraceWithFilter` first filters write records, so replaying into another DB leaves all data absent. It then filters get records in a separate DB and counts raw trace-reader records; only four writes plus header/footer should be present.

### File rename, manifest, and filesystem fault behavior

`RenameCurrentTest` injects IO errors before or after `SetCurrentFile` rename while the env disallows overwriting files. The `Open`, `Flush`, and `Compaction` cases ensure failed `CURRENT` updates leave the DB reopenable, writes after failure fail as expected, and previously persisted keys remain visible while later failed writes remain absent.

`MultiDBParallelOpenTest` creates and recovers two DBs in parallel threads. It verifies both empty DB creation and non-empty WAL recovery can safely happen concurrently.

`CloseWithUnreleasedSnapshot` asserts `DB::Close()` fails while a snapshot remains unreleased after all CF handles are destroyed, then succeeds after releasing the snapshot.

`PartitionedIndexPrefetchFailure` forces table cache capacity to zero, partitioned indexes, cached index/filter blocks, and random read failures while opening/preloading an SST. If injected reads fail, `Get()` should fail; otherwise it should succeed. This protects failure propagation during partitioned index prefetch.

### File temperatures and tiering statistics

`VariousFileTemperatures` wraps the file system to check write temperatures on WAL, MANIFEST, and other metadata files. It runs combinations of filesystem optimization callbacks and RocksDB temperature options, then verifies startup file counts, SST temperatures after flush and compaction, WAL/table file creation during operation, and new files created during recovery. It also checks `default_write_temperature` and `last_level_temperature` interactions.

`LastLevelTemperature` installs a file-I/O listener that records table-file temperatures from read/write/flush/sync/close events. With dynamic level bytes and `last_level_temperature=kWarm`, it verifies bottommost files are warm, non-bottommost L0 files remain unknown, metadata persists across reopen, `GetSstSizeHelper()` reports sizes per temperature, and `IOStatsContext` plus `Statistics` warm-file counters increase after reads.

`LastLevelTemperatureUniversal` covers universal compaction. Initially last-level temperature is unknown; after setting `last_level_temperature=kWarm` and compacting, newly generated bottommost files are warm while existing files are unchanged. A later dynamic `SetOptions({{"last_level_temperature","kCold"}})` changes only future compacted files. `Temperature::kLastTemperature` is rejected on reopen.

`LastLevelStatistics` tests the mapping of last-level versus non-last-level read tickers to temperature tickers under either write-time default temperature or read-time default temperature mapping. It resets stats across reopen and verifies explicit manifest-persisted warm last-level files remain warm while unknown non-last-level file mapping follows the chosen default semantics.

`UnknownLastLevelStatistics` leaves temperatures unset, reads a level-0 unknown file and expects unknown non-last-level iostats, then compacts/moves it to the last level, reopens, reads again, and expects unknown last-level iostats.

`CheckpointFileTemperature` forces checkpoint copy rather than link and inspects requested source-file temperature hints. The checkpoint code should request the manifest-recorded temperature for each SST it copies, with distinct requests per file.

`FileTemperatureManifestFixup` modifies the filesystem's current temperature view outside RocksDB metadata, then calls `experimental::UpdateManifestForFilesState(update_temperatures=true)` while the DB is closed. Reopen should reflect cold bottommost files and later hot formerly-unknown files in manifest metadata and `GetSstSizeHelper()` results.

### L0 epoch-number ordering

`SortL0FilesByEpochNumber` uses universal compaction with one level, writes one flushed SST, ingests two external SSTs, and verifies L0 files are sorted by descending `epoch_number` rather than largest sequence number. After compaction, the output file should carry the minimum epoch number among inputs.

`SameEpochNumberAfterCompactRangeChangeLevel` moves a file from L1 back to L0 through `CompactRangeOptions::change_level=true` and `target_level=0`. It verifies the file's original epoch number is preserved after the metadata move.

`RecoverEpochNumber` starts at the chunk boundary with a loop over `allow_ingest_behind` and obtains current options. Its actual setup and assertions are outside lines 1-7090, so this chunk can only identify it as an unresolved continuation related to epoch-number recovery.

## State and Persistence Behavior

- Read-only open state includes filesystem side effects of failed open attempts, initialized WAL-path flags, and cleanup during read-only DB destruction.
- WAL recovery state depends on record order, column-family log-number cutoffs, write-batch replacement semantics, paranoid checks, and whether a failed filter open leaves WAL files untouched for later normal recovery.
- Shared write-buffer state is global across CFs or DBs when a `WriteBufferManager` is shared; tests observe flush results through SST file counts and cache memory usage.
- Block cache/index/filter state is tracked through ticker counters and pinned cache entries. L0 pinning, table-reader preloading, and reopened block-cache replacement determine whether reads become cache hits/misses.
- Snapshot and iterator state is sequence-number sensitive. Tests assert first snapshot sequence zero, duplicate snapshot elision, write-conflict snapshot boundaries, and iterator sequence assignment during races.
- Compaction state includes background job queues, pressure tokens, manual compaction disabled/canceled flags, listener notifications, input/output file metadata, and file layout strings. Tests repeatedly verify cancellation/pausing leaves files unchanged and later compactions can proceed.
- Trace state is stored in trace files with header/footer, sampling, size limits, filters, CF ids, iterator bounds, and operation timestamps. Replayer `Prepare()` resets scan state for repeated replay.
- Row cache and read-amp state must include snapshot/version identity and survive DB close when block cache entries outlive DB/statistics objects.
- File temperature is persisted in MANIFEST entries for SST files, propagated through file operation callbacks, exposed through live-file metadata and DB properties, and repaired by manifest update tooling. Temperature statistics distinguish explicit hot/warm/cold values from unknown last/non-last-level categories.
- L0 epoch-number state is metadata independent from largest sequence number; ingestion and compaction must preserve ordering and output epoch-number derivation across compaction/change-level operations.

## Dependencies

This chunk depends on RocksDB's internal testing infrastructure and many production modules:

- `db/db_test_util.h` and `DBTestBase` for lifecycle, CF helpers, generated keys/files, compact/flush helpers, snapshots, and internal DB access.
- `db/read_callback.h`, `db/version_edit.h`, `DBImpl`, `VersionSet`, `VersionStorageInfo`, `FileMetaData`, and `InternalStats` for internal reads, metadata, and compaction/test hooks.
- `env/fs_readonly.h`, `utilities/fault_injection_env.h`, test file-system wrappers, and test env counters for filesystem errors, direct/mmap support, random-read failures, file temperatures, and sync corruption.
- `rocksdb/wal_filter.h`, `WriteBatch`, log reader recovery, and WAL recovery modes.
- Block-based table code, bloom filters, persistent cache, row cache, table cache, prefix extractors, comparators, and block-cache statistics.
- `rocksdb/trace_record.h`, `rocksdb/trace_record_result.h`, and `rocksdb/utilities/replayer.h` for tracing and replay execution.
- `rocksdb/experimental.h` and checkpoint utilities for manifest temperature fixup and checkpoint file copying.
- `SyncPoint`, atomics, threads, sleeping background tasks, mock sleep/time, and platform guards such as `OS_LINUX`, `OS_SOLARIS`, direct I/O support, and mmap support.

## Risks and Invariants Captured

- A read-only open failure can still create directories; cleanup and later missing-path semantics must remain intentional.
- Read-only close must initialize all fields read by obsolete-file deletion, including WAL path state.
- WAL filters are dangerous because they mutate recovery stream semantics. Adding keys, mishandling CF log numbers, or replaying skipped logs on the next reopen can silently corrupt recovered state.
- Shared write-buffer flush victim selection depends on precise memtable accounting; arena allocation nondeterminism is controlled by sync points because size drift changes expected flushes.
- Cache-charged write buffers must release charges when write-buffer manager ownership is cleared, or cache capacity accounting leaks.
- Prefix bloom and auto-prefix optimizations can incorrectly filter out valid next keys when prefix extractors change, reverse comparators are used, or bounds do not imply a safe prefix range.
- Pinned mmap values are unsafe unless table-cache lifetime guarantees prevent unmapping; the test distinguishes safe read-only/infinite-open-files mode from unsafe modes.
- Manual compaction cancellation must unregister in every path. Missing cleanup can block future compaction, DB close, or listener notification consistency.
- Non-exclusive manual compactions and auto compactions can overlap; range conflict handling and statistics updates must prevent overlapping lower-level files.
- `GetColumnFamilyHandleUnlocked()` is race-sensitive because callers use returned handles outside the DB mutex.
- Trace replay depends on matching CF ids and operation encoding. Invalid CF ids, empty multigets, and mismatched vector sizes must fail without producing bogus results.
- Partitioned index prefetch must propagate random read failures instead of serving partial metadata.
- File temperature metadata can diverge from filesystem state; manifest fixup must be explicit, closed-DB, CF-aware, and preserve all CF descriptors.
- Last-level temperature changes must not retroactively rewrite existing metadata; only newly compacted files receive the new temperature.
- L0 epoch-number order can differ from sequence-number order after ingestion; compaction and read resolution must use the intended epoch ordering.

## Test Signals

- `ASSERT_OK`, `ASSERT_NOK`, and status-class checks (`IsNotFound`, `IsNotSupported`, `IsCorruption`, `IsIOError`, `IsManualCompactionPaused`, `IsIncomplete`) are the dominant pass/fail signals.
- Exact key/value reads validate visibility after WAL replay, snapshots, compaction, prefix filtering, trace replay, row-cache hits, and recovery faults.
- File layout signals include `FilesPerLevel()`, `NumTableFilesAtLevel()`, `GetNumberOfSstFilesForColumnFamily()`, `ColumnFamilyMetaData`, `LiveFileStorageInfo`, `GetLevelFileMetadatas()`, and SST size by temperature.
- Ticker and context counters validate block-cache hits/misses/adds, row-cache hits/misses, persistent-cache hits/misses, read amplification, CPU-time perf counters, rate-limiter bytes, per-temperature file reads, last/non-last-level reads, and old statistics interface calls.
- Listener callbacks validate compaction begin/end metadata, flush reasons, file-operation temperatures, and compaction statuses.
- Sync-point counters and injected statuses prove specific race windows and failure paths were hit: WAL read errors, manifest write freezes, compaction job cancellation, table prefetch failures, `CURRENT` rename errors, random read failures, and background purge scheduling.
- Trace result handlers count writes, gets, multigets, and iterator seeks and validate operation-specific result types/timestamps.
- Reopen checks are essential: many tests close and reopen to prove manifest/WAL/temperature/epoch/cache-independent state remains durable and old failed attempts did not alter persistent state.

## Unresolved Cross-Chunk References

- The source file continues past line 7090. The body of `RecoverEpochNumber` and all later tests belong to a later chunk and must be merged before producing the final per-file report.
- This chunk uses helper methods and test infrastructure from `DBTestBase`, `db_test_util.h`, RocksDB test env wrappers, and production internals defined outside this file.
- Some disabled or FIXME-documented tests describe known or historical behavior rather than active pass/fail coverage; the final per-file synthesis should distinguish active regression tests from documented disabled/known-bug cases.
