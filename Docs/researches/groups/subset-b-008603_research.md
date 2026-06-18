# Research: subset-b-008603

Work item `subset-b-008603` covers six RocksDB DB-layer test files under `sources/storage-engines/rocksdb/db`. Each section preserves the source path and is intended to be split into the mirrored per-file research artifact.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_rate_limiter_test.cc -->
# sources/storage-engines/rocksdb/db/db_rate_limiter_test.cc

## Purpose

This file tests how RocksDB routes read, flush, compaction, WAL write, and explicit WAL flush I/O through `RateLimiter` accounting. It is not testing throttling latency directly; it verifies that the correct APIs attach rate-limiter priorities and that requests are charged to the expected `Env::IOPriority` buckets.

## Important APIs, Types, And Functions

- `DBRateLimiterOnReadTest` derives from `DBTestBase` and `WithParamInterface<std::tuple<bool, bool, bool>>`, parameterizing direct reads, block cache, and readahead.
- `GetOptions()` enables `RateLimiter::Mode::kAllIo`, `FileChecksumGenCrc32cFactory`, block-based tables, optional direct reads, and disabled automatic compaction.
- `GetReadOptions()` sets `ReadOptions::rate_limiter_priority = Env::IO_USER` and optionally sets `readahead_size`.
- Read APIs under test include `DB::Get`, both newer pointer-array `MultiGet` and older vector-returning `MultiGet`, `NewIterator`, `VerifyChecksum`, and `VerifyFileChecksums`.
- `DBRateLimiterOnWriteTest` uses `RateLimiter::Mode::kWritesOnly` and checks flush and compaction priority buckets.
- `DBRateLimiterOnWriteWALTest` parameterizes `WriteOptions::disableWAL`, `Options::manual_wal_flush`, and `WriteOptions::rate_limiter_priority`.
- `DBRateLimiterOnManualWALFlushTest` checks `FlushWALOptions::rate_limiter_priority` in manual WAL flush mode.

## Control Flow

The read fixture initializes three one-key SST files, moves them to level 1, then measures `options_.rate_limiter->GetTotalRequests(...)` before and after reads. `Get` expects one rate-limited read per first key lookup and no repeated request when block cache is enabled. `MultiGet` builds stable key buffers and slices, performs batch reads, and checks status success plus aggregate IO_USER charging. Iterator tests assert forward scans increment request counts per file/block and account for cache reuse on reverse scans. Checksum tests deliberately exercise full-table verification and raw file checksum verification, with platform/direct-IO-specific expected counts.

The write tests create overlapping files, then verify flushes charge `Env::IO_HIGH` and compaction charges `Env::IO_LOW`. WAL tests separate automatic WAL flush behavior from manual WAL flush behavior. Automatic WAL rate limiting is valid only when WAL is enabled, manual WAL flush is disabled, and priority is `Env::IO_USER`; invalid combinations must return `InvalidArgument` with an explanatory message. Manual WAL flush tests confirm writes themselves do not rate-limit WAL when `manual_wal_flush` is enabled and that `DB::FlushWAL` controls charging.

## State And Persistence Behavior

The tests persist real SST and WAL files in DBTestBase-managed directories. Read tests rely on file placement and block cache state to distinguish first reads from cached reads. Checksum tests persist CRC32c file checksums and verify rate-limited file reads. Write tests persist L0 files, compact them into L1, and inspect `FilesPerLevel` as a state signal. WAL tests persist WAL records and, depending on manual or automatic flush mode, expect rate-limiter counters to be unchanged or incremented.

## Dependencies And Integration Points

The file integrates with `db/db_test_util.h`, `rocksdb/db.h`, `rocksdb/env.h`, `util/file_checksum_helper.h`, block-based table factory configuration, direct-IO capability checks, and the generic rate limiter. It is sensitive to table reader behavior, block cache behavior, checksum verification implementation, WAL flushing semantics, and IO priority conventions used by flush/compaction/WAL code.

## Risks And Edge Cases

Direct IO is skipped when unsupported, so platform coverage differs. Exact request counts depend on block-based table read patterns, tail prefetching, readahead, block cache residency, and Windows-specific prefetch behavior. The old and new `MultiGet` APIs are intentionally both covered because they use different internal read paths. WAL priority validation is strict; new priorities or WAL mode changes can break these tests even if user-visible writes still work.

## Test Signals

Primary signals are exact `GetTotalRequests` deltas by `Env::IO_USER`, `Env::IO_HIGH`, `Env::IO_LOW`, and `Env::IO_TOTAL`, `ASSERT_OK`/`InvalidArgument` status checks, and `FilesPerLevel` assertions around compaction. The test binary installs stack traces and runs all gtest cases from `main`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_rate_limiter_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_readonly_with_timestamp_test.cc -->
# sources/storage-engines/rocksdb/db/db_readonly_with_timestamp_test.cc

## Purpose

This file validates user-defined timestamp behavior after reopening a DB in read-only mode, including compacted-read-only openings. It focuses on timestamp contract enforcement for `Get`, `MultiGet`, `NewIterator`, and `NewIterators`, and on correct historical visibility when timestamped keys are stored only in SST files.

## Important APIs, Types, And Functions

- `DBReadOnlyTestWithTimestamp` derives from `DBBasicTestWithTimestampBase`, giving access to timestamp helpers such as `Timestamp`, `Key1`, `TestComparator`, and `CheckIterUserEntry`.
- `CheckDBOpenedAsCompactedDBWithOneLevel0File()` inspects `VersionSet`, `ColumnFamilyData`, `Version`, and `VersionStorageInfo` to verify compacted-read-only layout with one L0 file.
- `CheckDBOpenedAsCompactedDBWithOnlyHighestNonEmptyLevelFiles()` verifies that only the highest non-empty level has files when read-only compacted DB opens over fully compacted data.
- Tests use `ReadOnlyReopen(options)`, `options.max_open_files = -1`, `test::NewSpecialSkipListFactory`, `BytewiseComparatorWithU64TsWrapper`, and `IncreaseFullHistoryTsLow`.
- Public read APIs under test are `Get` with and without timestamp output, `NewIterator`, `NewIterators`, and vector-returning `MultiGet` overloads with optional timestamp vectors.

## Control Flow

The first group creates timestamped or non-timestamped data, closes the primary, reopens read-only, and checks invalid combinations: read timestamp size mismatch, read timestamp specified when the DB was written without timestamp support, and timestamped data read without a read timestamp. The positive `IteratorAndGet` and `Iterators` tests write two timestamp versions over overlapping key ranges, then read at two higher timestamps and verify forward scans, reverse scans, lower/upper iterator bounds, returned values, and returned write timestamps.

`FullHistoryTsLowSanityCheckFail` uses a U64 timestamp comparator with `persist_user_defined_timestamps = false`, raises `full_history_ts_low`, flushes, reopens read-only, and confirms reads below the low watermark return `InvalidArgument` through `Get`, `NewIterator`, and `NewIterators`.

The compacted DB tests flush data to SST, then reopen read-only with `max_open_files = -1`. Some cases keep a single L0 file; others run `CompactRange` so only the highest non-empty level holds files. They repeat the same invalid timestamp contract tests and positive visibility tests for `Get` and `MultiGet`.

## State And Persistence Behavior

All data is persisted before read-only reopening, so the tests cover table-file timestamp metadata rather than mutable memtable behavior. `disable_auto_compactions` is used to control L0 file shape; explicit `CompactRange` moves data into the highest non-empty level. The compacted-read-only path pins/open table readers differently because `max_open_files = -1`, and the helper assertions ensure the intended version layout is actually active.

## Dependencies And Integration Points

The file depends on timestamp-aware comparators and helper utilities in `db_with_timestamp_test_util.h`, special skip-list memtables to create predictable flush boundaries, version storage internals for layout checks, and read-only DB open paths. It integrates with timestamp encoding, full-history low watermark validation, table properties that preserve timestamp state, and compacted DB read code.

## Risks And Edge Cases

Many tests depend on fixed timestamp byte widths. A comparator timestamp-size change must update both write and read timestamp construction. Compact read-only tests require exact level/file shapes; compaction heuristics or file-size defaults can change those shapes. The loops over 0..1024 keys make the assertions robust but somewhat expensive. Invalid timestamp cases intentionally expect API-level `InvalidArgument`, so changes that silently ignore timestamps would be caught.

## Test Signals

Signals include `InvalidArgument` statuses for mismatched or missing timestamp contracts, iterator validity/status checks, exact key/value/write-timestamp comparisons through `CheckIterUserEntry`, `MultiGet` status and output vector sizes, and version-layout assertions on L0 and highest non-empty levels.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_readonly_with_timestamp_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_secondary_test.cc -->
# sources/storage-engines/rocksdb/db/db_secondary_test.cc

## Purpose

This file tests RocksDB secondary-instance behavior: opening a primary DB as a secondary, catching up from MANIFEST/WAL changes, secondary-side compaction service flows, timestamped secondary reads, blob-backed entity resolution, column-family handling, live-file reporting, and failure handling around missing files or inconsistent versions.

## Important APIs, Types, And Functions

- `DBSecondaryTestBase` derives from `DBBasicTestWithTimestampBase` and owns `secondary_path_`, `handles_secondary_`, and `db_secondary_`.
- Helpers include `ReopenAsSecondary`, `TryOpenSecondary`, `OpenSecondary`, `OpenSecondaryWithColumnFamilies`, `CloseSecondary`, `db_secondary_full()`, and `CheckFileTypeCounts`.
- Core APIs include `DB::OpenAsSecondary`, `DB::TryCatchUpWithPrimary`, `DBImplSecondary::TEST_CompactWithoutInstallation`, `DB::OpenAndCompact`, `DB::GetLiveFiles`, `DBImpl::GetImpl`, `GetMergeOperands`, `GetEntity`, `PutEntity`, `PutBlobIndex`, and `TransactionDB::Open`.
- Test-specific helpers include `TraceFileEnv`, SyncPoint callbacks/dependencies, `CompactionServiceInput`, `CompactionServiceResult`, `WideColumns`, `BlobIndex`, and merge operators.

## Control Flow

The opening tests cover logger creation failures, nonexistent primaries, reopening a closed DB as secondary, and reading normal values plus wide-column entities through a secondary iterator. Internal compaction tests create L0/L1/L2 input files, build `CompactionServiceInput`, open a secondary with `max_open_files = -1`, and run `TEST_CompactWithoutInstallation`, checking output file metadata, bytes written, levels, output path, and invalid-argument behavior when files are missing or already compacted.

Read-path tests verify merge operands, blob-backed V2 entity base values in SST plus newer merge operands from catch-up, raw blob-index return through internal `GetImpl`, direct-write blob entity resolution after WAL catch-up, and `kBlockCacheTier` returning `Incomplete` instead of issuing blob I/O. Standard secondary catch-up tests write/flush/compact on the primary, call `TryCatchUpWithPrimary`, and verify `Get` and iterator views. WAL-tail tests ensure the secondary keeps tailing the current WAL even when a higher-number empty WAL exists and that repeated catch-up is stable.

MANIFEST and file-lifecycle tests exercise opening while the primary switches manifests, catching up across manifest switches, missing table files during open versus after open, primary column-family drops, opening subsets of column families, and unsupported dynamic `max_open_files` changes on secondary. Disabled WAL-switch tests document intended behavior but are not active.

The timestamp section mirrors the read-only timestamp file, but reopens with `ReopenAsSecondary` instead of `ReadOnlyReopen`. It checks invalid read timestamp size, read timestamp without write timestamps, read without timestamp over timestamped data, full-history-low sanity failures, and positive iterator/Get/NewIterators behavior.

## State And Persistence Behavior

The primary DB owns durable WAL, SST, CURRENT, MANIFEST, OPTIONS, blob files, and column-family metadata. The secondary maintains its own secondary path while reading primary files and tailing primary metadata/logs. Catch-up refreshes secondary versions and memtables without accepting direct writes through the secondary. Compaction-service tests produce output under `secondary_path_` without installing it into the primary. Blob and wide-column tests rely on persisted SST blob references plus WAL-replayed memtable entries.

## Dependencies And Integration Points

This file reaches into secondary implementation internals via `db_impl_secondary.h`, regular DB internals via `DBImpl`, filename parsing, write-batch internals, blob index encoding, wide-column helpers, transaction DB, string-append merge operators, and SyncPoint scheduling. It also integrates with timestamp utilities, compaction service serialization/options override, file cache closure, live-file enumeration, and corruption/status propagation from `VersionBuilder`.

## Risks And Edge Cases

Secondary DB correctness is sensitive to races with primary manifest rollover, WAL numbering, precreated future WALs, missing or compacted-away table files, and column-family changes. Tests that use `max_open_files = -1` assume all relevant table readers are loaded. Blob direct-write tests distinguish resolving blob values from exposing encoded blob indexes, and the block-cache-tier test prevents accidental I/O. SyncPoint-driven tests can become brittle if internal point names move.

## Test Signals

Signals include exact status classes (`OK`, `IOError`, `TryAgain`, `InvalidArgument`, `Corruption`, `Incomplete`, `NotSupported`), primary/secondary `Get` and iterator value equality, output compaction metadata, file-type counts, SyncPoint-observed option overrides, file-close counters, live-file list contents and growth, timestamped entry checks, and blob/wide-column equality assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_secondary_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_sst_test.cc -->
# sources/storage-engines/rocksdb/db/db_sst_test.cc

## Purpose

This file tests SST/WAL file lifecycle behavior around creation, deletion, trash scheduling, `SstFileManager` accounting, blob-file tracking, maximum-space enforcement, compaction cancellation, table-reader opening, and total SST size properties. It focuses on persistence side effects and storage accounting more than key/value semantics.

## Important APIs, Types, And Functions

- `DBSSTTest` derives from `DBTestBase` with fsync enabled.
- `FlushedFileCollector` is an `EventListener` that records flushed file paths for later manual `CompactFiles` calls.
- `SstFileManager`, `SstFileManagerImpl`, and `DeleteScheduler` are central to tracking file sizes, delete rates, trash ratios, and background deletion.
- Tests use `OnFileDeletionListener`, `SyncPoint`, `MockEnv` time controls, `FaultInjectionTestFS`, `NewCompositeEnv`, blob-file APIs, `GetAllDataFiles`, `GetBlobFileNumbers`, `GetLiveFilesMetaData`, and `rocksdb.total-sst-files-size`.
- Parameterized fixtures cover rate-limited delete with separate WAL dirs and obsolete deletion `max_trash_db_ratio` settings.

## Control Flow

Early tests guard file deletion correctness: pending compaction outputs must not be purged while being written, `.sst` files renamed to `.ldb` must still reopen and read, moved files from move compaction must not be deleted, and obsolete files blocked by `pending_outputs_` must be retried later. Empty flushes must not create phantom SST deletion events, while non-empty flushes create one live file without deletion.

`DBWithSstFileManager` and blob variants create many SST/blob files, flush and compact, compare `SstFileManagerImpl::GetTrackedFiles()` and `GetTotalSize()` with filesystem scans, then close/reopen or destroy the DB to verify tracking is repopulated and untracked correctly. Blob GC and atomic flush tests assert blob files are added, scheduled, deleted, or preserved according to garbage-collection cutoffs and atomic flush behavior.

Rate-limited deletion tests set delete rates, use SyncPoints to observe penalty sleeps, compact files into trash, wait for empty trash, and validate `FILES_MARKED_TRASH` versus `FILES_DELETED_IMMEDIATELY`. WAL trash cleanup tests create or preserve `.log.trash` files across reopen and ensure they are removed. Obsolete deletion-on-open tests seed `.sst.trash` and obsolete SST files before open and verify background deletion policy under different trash ratios.

Space-limit and cancellation tests set `SstFileManager::SetMaxAllowedSpaceUsage`, then cause flushes or compactions to exceed the limit. They verify failed flushes, blob cleanup after failed flushes, automatic and manual compaction cancellation, `COMPACTION_CANCELLED`, and that reserved compaction size returns to zero. The randomized test keeps writing until the configured space limit is exceeded via both flush and compaction paths.

Open and size-property tests exercise `max_open_files = -1`, multi-threaded file opening, table-reader cache memory charging failures, and `rocksdb.total-sst-files-size` across live files, obsolete-but-version-pinned files, trivial moves, iterator-held versions, deletes, and compactions. The final fault-injection test verifies fallback/error behavior when SST file-size queries fail through random-access or filesystem APIs.

## State And Persistence Behavior

The file creates real SST, WAL, blob, trash, obsolete, and multi-path DB files. It intentionally closes and reopens DBs to test recovery-time tracking and cleanup. Iterator-held versions pin obsolete files and influence `total-sst-files-size`. DeleteScheduler may rename files into trash and delete asynchronously; tests frequently call `WaitForEmptyTrash`, `TEST_WaitForCompact`, `TEST_WaitForFlushMemTable`, and `TEST_WaitForPurge` to synchronize persistent side effects.

## Dependencies And Integration Points

The tests integrate with compaction, flush jobs, blob GC, file manager accounting, DeleteScheduler, table cache/table readers, cache capacity enforcement, filesystem wrappers, DB properties, DB destruction, WAL directory handling, and RocksDB statistics. They depend on `SyncPoint` names in flush, compaction, build-table, delete-scheduler, and SstFileManager internals.

## Risks And Edge Cases

These tests are timing- and filesystem-sensitive. Rate-limited deletion uses mocked time and SyncPoints to make expected penalties deterministic. File-size and total-size checks assume stable table property encoding in some cases, with an explicit workaround for oldest-key-time. Trash ratio heuristics can route files to immediate deletion or background deletion. Encrypted environments alter file-size fallback behavior. Space-limit tests intentionally trigger background errors and cancellation paths that can be affected by compaction scheduling changes.

## Test Signals

Signals include `FilesPerLevel`, live-file metadata counts and sizes, filesystem existence checks, deletion listener counts, SyncPoint counters, `SstFileManager` tracked file maps and totals, delete-scheduler trash size, statistics tickers, `IsCompactionTooLarge`, `IsMemoryLimit`, exact DB property values, and successful reads after reopen or fault injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_sst_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_statistics_test.cc -->
# sources/storage-engines/rocksdb/db/db_statistics_test.cc

## Purpose

This file validates RocksDB statistics counters and histograms for compression, mutex wait timing, reset semantics, stats-level exclusions, checksum verification reads, block checksum accounting, and bytes-written accounting for normal and transactional writes.

## Important APIs, Types, And Functions

- `DBStatisticsTest` derives from `DBTestBase`.
- Tests use `CreateDBStatistics`, `Statistics::set_stats_level`, `getTickerCount`, `getAndResetTickerCount`, `histogramData`, and `Statistics::Reset`.
- Compression tests iterate `GetSupportedCompressions`, configure block-based tables with uncompressed indexes, and inspect compression/decompression tickers.
- Mutex tests use `ThreadStatusUtil::TEST_SetStateDelay`.
- Checksum tests use `VerifyFileChecksums`, `VerifyChecksum`, `GetFileChecksumGenCrc32cFactory`, file corruption helpers, and checksum-related tickers.
- Transaction write accounting uses `TransactionDB`, `TxnDBWritePolicy::WRITE_COMMITTED`, `Transaction::Prepare`, `Transaction::Commit`, and `WriteBatchInternal::kHeader`.

## Control Flow

`CompressionStatsTest` loops over supported compression algorithms except no-compression and bzip2, writes compressible values, flushes, and checks compressed block counts and byte estimates. It then reads all keys to trigger decompression stats. The test reopens with random incompressible values to verify compression-rejected counters, then reopens with `kNoCompression` to verify compression-bypassed counters.

Mutex wait tests create a DB with statistics, inject artificial mutex wait delay, and show that default stats levels do not count `DB_MUTEX_WAIT_MICROS` while `StatsLevel::kAll` does. `ResetStats` checks an arbitrary ticker and histogram before and after `Put`, then calls `Reset` and verifies counters return to zero. `ExcludeTickers` switches between excluding tickers and allowing ticker collection.

Checksum tests separate WAL-only data from SST-backed data. `VerifyChecksumReadStat` expects no verify-read bytes before flush, exact file-size reads for `VerifyFileChecksums`, and at least file size for block-level `VerifyChecksum`. `BlockChecksumStats` checks block checksum compute/mismatch counters, then corrupts a table data block and expects one mismatch.

`BytesWrittenStats` compares `WAL_FILE_BYTES` and `BYTES_WRITTEN` for ordinary writes, then recreates the DB as `TransactionDB` with and without pipelined writes. It verifies `Prepare` writes WAL bytes but not `BYTES_WRITTEN`, while `Commit` makes total WAL bytes equal memtable bytes plus one write-batch header.

## State And Persistence Behavior

The tests persist SST files via flushes, reset or recreate DBs to isolate statistic windows, corrupt an SST on disk, and recreate as `TransactionDB` for transactional persistence behavior. Counters live in the shared `Statistics` object attached to `Options`, so reopen/reset boundaries are part of the test design.

## Dependencies And Integration Points

This file connects monitoring/statistics, compression managers/codecs, block-based table building/reading, checksum verification, thread status instrumentation, transaction DB WAL/memtable paths, write-batch encoding, and file corruption helpers. It depends on stable block counts for the chosen block size and generated value lengths.

## Risks And Edge Cases

Compression counts are approximate for byte totals but exact for expected block counts; codec behavior changes can shift counts. BZip2 is skipped due to known odd behavior. Checksum counters intentionally bypass `PerfLevel` and must remain populated even with perf disabled. Transaction write accounting is guarding against double-counting issue patterns; WAL headers make exact equality non-obvious.

## Test Signals

Signals are ticker values, reset ticker deltas, histogram maxima, checksum status, corrupted-file mismatch counts, and transactional WAL-versus-memtable byte relationships. Assertions use both exact equality and tolerance macros where compression byte estimates vary.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_statistics_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_table_properties_test.cc -->
# sources/storage-engines/rocksdb/db/db_table_properties_test.cc

## Purpose

This file tests reading, validating, and interpreting RocksDB table properties. It covers all-table and by-level property retrieval, in-range property queries with and without user-defined timestamps, table identity properties, collector factory behavior, deletion-triggered compaction metadata, sequence-number properties, host identifiers, and compression display-name parsing.

## Important APIs, Types, And Functions

- `VerifyTableProperties` calls `DB::GetPropertiesOfAllTables`, validates unique `num_entries`, total entries, and SST unique IDs.
- `ParseCompressionDisplayNameManager` is a custom `CompressionManagerWrapper` used to test custom compression display names and object registry lookup.
- `DBTablePropertiesTest` is parameterized by compaction style for deletion-triggered compaction tests.
- `DBTablePropertiesInRangeTest` is parameterized by user-defined timestamp enablement and wraps `Put`, `Get`, and `GetPropertiesOfTablesInRange` with timestamp-aware ranges.
- APIs under test include `GetPropertiesOfAllTables`, `GetPropertiesOfTablesByLevel`, `GetPropertiesOfTablesInRange`, table-property collector factory creation, `NewCompactOnDeletionCollectorFactory`, `ParseCompressionNameForDisplay`, and DB identity/session/host property accessors.

## Control Flow

`GetPropertiesOfAllTablesTest` creates four tables with different entry counts, records the DB session id, then tests property retrieval when no table readers are cached, when some readers are cached, and when all are cached. It corrupts a table properties block by mutating the stored session id and verifies corruption is reported both by direct property reads and through table reader access on `Get`.

`InvalidReportedAsCorruption` injects invalid properties-block data through SyncPoint and expects flush to return corruption. `CreateOnDeletionCollectorFactory` parses collector factory strings with default, window/deletion-trigger, and deletion-ratio settings. `GetPropertiesOfTablesByLevelTest` builds a multi-level LSM and checks each returned per-level collection size against `ColumnFamilyMetaData`.

`DBTablePropertiesInRangeTest` builds a multi-level LSM and queries all, empty, middle, and random key ranges. When timestamps are enabled, it uses `MaybeAddTimestampsToRange` and comparator timestamp size to verify file overlap against user-key ranges with appended timestamps.

Column-family, DB identifier, and host tests flush per-CF tables and verify table properties preserve `column_family_name`, `column_family_id`, `db_id`, `db_session_id`, and `db_host_id`. `FactoryReturnsNull` alternates a custom collector factory between returning a collector and `nullptr`, across block-based and plain table factories, and verifies one table has the user property and one does not.

Deletion-triggered compaction tests add `CompactOnDeletionCollectorFactory`, create tombstone-heavy files, and verify files are marked for compaction by count-window and ratio-based policies under level and universal compaction. `KeyLargestSmallestSeqno` checks sequence-number table properties before and after bottommost compaction. `ParseCompressionNameForDisplay` exhaustively validates old/new compression strings, standard/custom/reserved hex values, registry-backed custom manager names, disabled compression markers, future fields, and malformed inputs.

## State And Persistence Behavior

The tests create real SST files and rely on table properties persisted in meta blocks. Reopens and table-cache erasure force direct file property reads versus cached-reader reads. Corruption is written to the SST file and then undone for reuse. LSM-building tests pause background work after compaction reaches useful L0/L1/L2 shapes. Deletion-triggered compaction persists collector-derived metadata that causes subsequent compaction scheduling.

## Dependencies And Integration Points

The file integrates with block-based and plain table formats, meta block parsing, table property collectors, object registry, advanced compression managers, DB identity/session/host metadata, timestamp-aware comparators, live-file metadata, compaction reason reporting, statistics tickers for marked compaction bytes, and SyncPoint injection in table building/loading.

## Risks And Edge Cases

Property retrieval must work with and without table readers in cache. Range overlap logic is comparator-sensitive, especially with user-defined timestamps. Corruption tests assume the session id is present in table properties and that mutating one byte causes checksum failure. Deletion-triggered compaction relies on tombstones not being dropped during flush, so setup adds lower-level files. Compression display parsing is intentionally broad and can fail when serialization format or compatibility names change.

## Test Signals

Signals include table property collection sizes, unique IDs, entry sums, corruption statuses, per-level collection counts, range overlap validation against live-file metadata, CF/DB/host property equality, user-collected property presence/absence, compaction listener reasons, `COMPACT_*_BYTES_MARKED` tickers, key sequence-number fields, and exact display-name strings for compression parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_table_properties_test.cc -->
