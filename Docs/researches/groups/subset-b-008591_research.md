# subset-b-008591 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_etc3_test.cc -->
# sources/storage-engines/rocksdb/db/db_etc3_test.cc

## Purpose

`db_etc3_test.cc` is a focused GoogleTest file for RocksDB MANIFEST rollover and MANIFEST-size auto-tuning behavior. It exercises DB reopen, flush, column-family create/drop, external SST ingestion, imported column-family creation, and physical file deletion by range as different classes of manifest-writing operations. The tests are less about key/value semantics and more about whether MANIFEST rotation thresholds, persisted compacted-manifest size, and foreground/background manifest-write classification remain correct.

## Important APIs, Types, and Functions

- `DBEtc3Test` derives from `DBTestBase` with fsync enabled for realistic metadata persistence.
- `ManifestRollOver` configures `max_manifest_file_size=0` and `max_manifest_space_amp_pct=0` to force a new MANIFEST on each manifest write.
- `AutoTuneManifestSize` is the main scenario test. It uses `DBOptions::max_manifest_space_amp_pct`, dynamic `SetDBOptions`, `CreateColumnFamily`, `DropColumnFamily`, `DestroyColumnFamilyHandle`, `SetOptions`, `IngestExternalFile`, `CreateColumnFamilyWithImport`, and `DeleteFilesInRanges`.
- The test builds external SSTs with `SstFileWriter` and import metadata with `LiveFileMetaData` and `ExportImportFilesMetaData`.
- It uses `dbfull()->TEST_Current_Manifest_FileNo()` as the primary internal signal for whether a write rotated the MANIFEST.

## Control Flow

`ManifestRollOver` repeatedly opens with an extra column family, writes and flushes data, verifies the flush caused a manifest file number increase, reopens with the same CF set, and verifies reopen also creates a new manifest while preserving values.

`AutoTuneManifestSize` is split into phases. Phase 1 validates that foreground manifest writes receive bounded extra headroom: several large CF-name creates fit under the relaxed threshold, then the fifth rotates. Phase 2 disables auto-tuning and shows a reduced `max_manifest_file_size` causes frequent rotation. Phase 3 enables `max_manifest_space_amp_pct`, verifies the tuned threshold allows additional manifest growth, and checks dynamic option changes recompute from the last compacted MANIFEST size. Phase 4 distinguishes foreground manifest writes from background flush writes using CF operations, `SetOptions`, external SST ingestion, imported CF creation, and `DeleteFilesInRanges`; each foreground operation should stay on the current MANIFEST until a background flush rotates it. Phase 5 closes and reopens with `reuse_manifest_on_open=true`, then verifies the persisted compacted size prevents immediate rotation of a reused large MANIFEST.

## State and Persistence Behavior

The persistent state under test is the MANIFEST file number, the compacted MANIFEST size used for auto-tuning, the set of live column-family definitions, imported/ingested file metadata, and key/value data after reopen. The test intentionally keeps many CF handles alive until the persisted-size phase, then collects names and destroys handles before `Close()` so reopen can validate reused manifest metadata. A failure in persisted compacted-size loading would show up as an unexpected manifest number change on reopen or on early post-reopen CF creation.

## Dependencies and Integration Points

This test integrates `DBTestBase`, `DBImpl` test hooks, public DB option mutation APIs, CF management APIs, external SST ingestion, column-family import metadata, file-range deletion convenience APIs, `SstFileWriter`, `rocksdb/metadata.h`, and manifest rewrite/rotation logic inside `VersionSet::LogAndApply`.

## Risks and Edge Cases

The most important risk covered is misclassifying foreground manifest writes as background writes, or giving foreground writes unbounded headroom. Either bug can cause excessive MANIFEST growth or excessive rotation. The persisted-size phase covers a subtle restart risk: if `reuse_manifest_on_open` loses the compacted-size baseline, the DB may rotate a manifest immediately and defeat reuse. The test also depends on CF-name payload sizes to make threshold crossings deterministic, so future MANIFEST encoding changes can require threshold adjustment.

## Test Signals

The test asserts manifest file-number changes, successful point reads after flush/reopen, successful ingestion/import/delete range operations, dynamic option effects, and exact CF handle counts. It is a regression signal for MANIFEST rollover, auto-tuned manifest thresholds, foreground/background manifest write policy, and persistence of the compacted-size baseline.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_etc3_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_filesnapshot.cc -->
# sources/storage-engines/rocksdb/db/db_filesnapshot.cc

## Purpose

`db_filesnapshot.cc` implements DBImpl file-enumeration APIs used by backup, checkpoint, live-file inspection, and WAL discovery paths. It translates current in-memory version state plus filesystem WAL scans into stable lists of live SST, blob, manifest, CURRENT, OPTIONS, and WAL files. Unlike the neighboring test files in this work item, this is production code and sits on a safety boundary: callers use its output to copy or link enough files to reconstruct a consistent DB image.

## Important APIs, Types, and Functions

- `DBImpl::FlushForGetLiveFiles(bool force_atomic_flush)` flushes all column families with `FlushReason::kGetLiveFiles`.
- `DBImpl::GetLiveFiles(std::vector<std::string>&, uint64_t*, bool flush_memtable)` returns relative live table/blob file names plus CURRENT, MANIFEST, and OPTIONS.
- `DBImpl::GetSortedWalFiles()` and `GetSortedWalFilesImpl(VectorWalPtr&, bool need_seqnos)` return sorted WAL metadata, including archived WALs when needed, and cross-check manifest-tracked WALs against directory results.
- `DBImpl::GetCurrentWalFile()` wraps `WalManager::GetLiveWalFile` for the current log number.
- `DBImpl::GetLiveFilesStorageInfo(const LiveFilesStorageInfoOptions&, std::vector<LiveFileStorageInfo>*)` returns richer per-file metadata such as directories, file numbers, types, sizes, checksum info, temperatures, replacement contents, and trim/copy requirements.

## Control Flow

`GetLiveFiles` locks `mutex_`, optionally flushes all column families, walks non-dropped column families through their current versions, appends table and blob filenames, appends CURRENT/MANIFEST/OPTIONS, captures manifest size, and unlocks. It returns names relative to the DB directory.

`GetSortedWalFilesImpl` first disables file deletions when supported, waits for pending obsolete-file purges to finish, snapshots WAL numbers required by the manifest, scans live and archived WAL directories through `wal_manager_`, re-enables deletions, and verifies every manifest-required WAL is included in the sorted scan result.

`GetLiveFilesStorageInfo` begins by deciding whether to flush based on `allow_2pc`, `wal_size_for_flush`, WAL size, and atomic-flush options. While holding `mutex_`, it rejects unsafe blob direct-write cases, flushes if allowed and needed, then records live SST and blob metadata from each non-dropped column family's `VersionStorageInfo`. It captures manifest/options/min-log/current-WAL numbers under the lock, then releases the lock and appends descriptor, CURRENT, and OPTIONS entries. It flushes WAL data, gathers open WAL sizes to identify files that must be copied/truncated rather than hard linked, scans sorted WALs, and appends eligible WAL entries bounded by `min_log_num` and the captured `max_log_num`.

## State and Persistence Behavior

The code observes persisted state from `VersionSet`, `ColumnFamilySet`, `VersionStorageInfo`, `FileMetaData`, blob metadata, WAL manager state, manifest file size, options file size, and current WAL number. It also manipulates operational state by temporarily disabling file deletions and by flushing memtables/WALs to make a snapshot copyable. It deliberately treats CURRENT as replacement contents rather than a normal hard-link candidate because CURRENT can be rewritten. For WALs, `trim_to_size` marks open, recycled, or possibly unsynced logs that must be copied to an exact safe size.

## Dependencies and Integration Points

This file integrates with `DBImpl` mutex and condition variables, `VersionSet`, `ColumnFamilyData`, `VersionStorageInfo`, `WalManager`, `JobContext` deletion state, file naming helpers, checksum constants, blob direct-write state, `LiveFileStorageInfo`, `WalFile`, `FlushWAL`, and checkpoint sync points retained for legacy checkpoint tests.

## Risks and Edge Cases

The main risks are inconsistent snapshots if flush/WAL boundaries are mishandled, file deletion races during WAL scans, omitting manifest-required WALs, hard-linking an unsynced or still-open WAL, and returning partial output after an error. The implementation mitigates these with mutex-held metadata capture, deletion disabling, purge waiting, manifest-vs-directory WAL cross-checks, `max_log_num` bounds, open-WAL size maps, and only moving results to the caller on success. Blob direct writes are a newer edge case: if active blob files cannot be safely flushed because WAL is locked or flushing is disabled, the API returns `NotSupported`.

## Test Signals

Coverage is indirect through checkpoint/backup/live-file tests, WAL tracking tests, blob tests, and sync-point labels named for checkpoint creation. Useful signals are complete live-file lists, absence of deleted-file races, successful checkpoints with WAL copy/link decisions, checksum metadata population, and corruption errors when manifest-required WALs are missing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_filesnapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_flush_test.cc -->
# sources/storage-engines/rocksdb/db/db_flush_test.cc

## Purpose

`db_flush_test.cc` is a large GoogleTest suite for RocksDB memtable flush behavior. It covers manual and automatic flush scheduling, WAL sync interactions, listener callbacks, memtable garbage accounting, experimental MemPurge, blob flushing, checksum handoff, atomic flush across column families, failure rollback, table-builder error propagation, super-block alignment, and range tombstone ordering. The suite uses extensive sync points and fault-injection environments because many target bugs occur only under precise background-thread interleavings.

## Important APIs, Types, and Helpers

- `DBFlushTest` derives from `DBTestBase` and adds `WaitForFlushCallbacks()` to wait for listener callbacks before closing.
- `DBFlushDirectIOTest`, `DBAtomicFlushTest`, `DBFlushTestBlobError`, and `DBFlushSuperBlockTest` are parameterized fixtures.
- `TestFlushListener` validates `OnTableFileCreated` and `OnFlushCompleted` metadata, write-stall flags, file numbers, blob file numbers, and callback thread IDs.
- `ConditionalUpdateFilter` and `ConditionalUpdateFilterFactory` test flush-time compaction filters, including MemPurge.
- The tests use `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `MockEnv`, `SyncPoint`, `SleepingBackgroundTask`, `TransactionDB`, blob options, checksum handoff options, `FlushOptions`, `ColumnFamilyHandleImpl`, and DBImpl test hooks such as `TEST_WaitForFlushMemTable`, `TEST_SwitchMemtable`, `TEST_AtomicFlushMemTables`, and `TEST_table_cache`.

## Control Flow

Early tests validate scheduler and WAL paths: concurrent flushes while writing MANIFEST, WAL sync failure/skip, low-priority flush fallback when the high-priority pool is empty, close while a low-priority flush is queued, manual flush with `min_write_buffer_number_to_merge`, and scheduling only one background thread.

The statistics tests construct overwrite/delete/range-delete workloads and compare `MEMTABLE_PAYLOAD_BYTES_AT_FLUSH` and `MEMTABLE_GARBAGE_BYTES_AT_FLUSH` against expected byte counts. Listener tests ensure flush-completed callbacks run only after flush results are committed to in-memory version state.

The MemPurge block toggles `experimental_mempurge_threshold`, checks high-garbage overwrite workloads purge in memory without creating SSTs, verifies random inserts still force SST creation, confirms atomic flush disables MemPurge, exercises delete and range-delete semantics with iterators, validates flush-time compaction filters, documents disabled WAL support, checks correct log number/SST creation after chained mempurges, and reproduces a memtable-ID ordering race when MemPurge releases and reacquires the DB mutex.

Blob and checksum sections verify flushing small values to SST and large values to blob files, blob metadata in `VersionStorageInfo`, compaction stats, table-file checksum handoff failures, disabled checksum handoff behavior, descriptor-file checksum handoff failures, and cleanup after blob builder errors.

Atomic flush tests run with `atomic_flush` true and false. They cover manual flush under 2PC, multi-CF manual atomic flush, precomputing min log number to keep, automatic flush triggered by a full memtable, rollback when some jobs complete and later fail, dropped CF races before and after scheduling, close during auto flush, picking memtables while a background flush is paused, rollback after manifest install failure, multi-CF automatic flush failure, manifest write queue wakeup after errors, and no-wait behavior when writes are stopped.

The final regression tests cover non-atomic rollback of pending flushes, aborting new flushes after background errors, avoiding a stuck DB after atomic flush errors, output record-count verification for block-based and plain tables, super-block alignment compatibility/checksums, builder IO-error propagation, table-cache eviction after flush install failure, and range tombstone insertion ordering around `SwitchMemtable`.

## State and Persistence Behavior

The suite observes mutable memtables, immutable memtable queues, WAL numbers/min-log retention, MANIFEST edits, L0 file installation, blob file metadata, table cache contents, background error state, snapshots, and recovered data after reopen. It deliberately creates retryable and fatal IO failures to ensure uninstalled flush outputs are rolled back, obsolete files are released, cached table entries are evicted, WALs remain recoverable, and atomic-flush invariants hold across column families.

## Dependencies and Integration Points

The file integrates with DBImpl flush/compaction scheduling, `VersionSet::LogAndApply`, `MemTableList`, `FlushJob`, `BuildTable`, table builders, blob file builders, `InternalStats`, event listeners, transaction DB 2PC recovery, file checksum handoff, block-based table super-block alignment, range tombstone conversion, write-stall logic, and fault-injection filesystem layers.

## Risks and Edge Cases

The tests target deadlocks, stale memtable IDs, manifest write ordering, dropped-column-family lifetime races, incomplete rollback after partial flush success, background-error recovery loops, false corruption errors that mask IO errors, table-cache leaks after failed installs, snapshot visibility of tombstones, and cross-CF atomicity gaps. Many cases depend on sync-point labels and exact interleavings, so refactors of flush internals can break tests even if external behavior remains correct. The suite also includes environment-sensitive skips for checksum handoff on memory or encrypted environments.

## Test Signals

Signals include `Status` severity checks, file counts per level, ticker counts, listener metadata assertions, sync-point callback counters, blob/table metadata, WAL/min-log values after reopen, successful/failed point reads, iterator results, table-cache entry counts, checksum verification, and absence of hangs in historically deadlocking paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_flush_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_follower_test.cc -->
# sources/storage-engines/rocksdb/db/db_follower_test.cc

## Purpose

`db_follower_test.cc` tests RocksDB's Linux-only follower mode, where a read-only follower DB catches up from a leader DB by reading the leader's MANIFEST and linking/copying needed table files into a follower directory. The suite focuses on catch-up races around flushes, compactions, MANIFEST rollover, intermediate obsolete files, and partial version recovery.

## Important APIs, Types, and Helpers

- `DBFollowerTest` derives from `DBTestBase`, creates separate leader and follower directories, and opens the leader under `dbname_/leader`.
- `OpenAsFollower()` calls `DB::OpenAsFollower(opts, follower_name_, dbname_, &follower_)` with a wrapped follower env and `follower_refresh_catchup_period_ms=100`.
- `FollowerGet()` reads with checksum verification and normalizes not-found/error statuses to strings for assertions.
- `CheckDirs()` compares table file numbers in leader and follower directories to ensure the follower has all needed SSTs.
- `DBFollowerTestFS` wraps descriptor-file sequential reads and provides barriers so tests can pause follower MANIFEST reads at controlled points.
- `DBFollowerTestSstPartitionerFactory` creates small partitioned SST outputs so partial recovery scenarios can produce multiple overlapping compaction files.

## Control Flow

`Basic` writes and flushes two keys before opening the follower, then verifies reads and directory parity. `Flush` uses sync points so the follower starts catch-up, the leader flushes a key, and the follower waits until catch-up finishes before reading it.

`RetryCatchup` creates four L0 files and compacts them while the follower is catching up. The follower can fail to instantiate versions for now-obsolete flushed files, then recover a valid version from the later compaction edit. `RetryCatchupManifestRollover` adds a leader reopen/MANIFEST rollover between flushes and compaction, requiring another refresh round because the follower does not switch manifests mid-read.

`IntermediateObsoleteFiles` uses filesystem read barriers so the follower first links four L0 files and then sees a compaction edit deleting them. It verifies those intermediate follower files are explicitly deleted and the final value remains readable.

`PartialVersionRecovery` and `PartialVersionRecoveryWithRollover` use an SST partitioner and small compaction bytes to generate overlapping compaction outputs. They verify that when some additions cannot be found or are added and deleted before catch-up installs a version, the follower still deletes obsolete files and eventually reads the correct point-in-time values. The rollover variant requires a second catch-up attempt after leader reopen.

## State and Persistence Behavior

The suite observes leader MANIFEST edits, leader table files, follower-linked table files, follower version installation, obsolete-file deletion, and persisted state after leader reopen. It deliberately creates table files that are transient in the leader but visible to the follower during catch-up. Correctness means the follower neither misses required live files nor keeps obsolete intermediate files after applying later version edits.

## Dependencies and Integration Points

The tests depend on `DB::OpenAsFollower`, follower refresh internals (`DBImplFollower::TryCatchupWithLeader` sync points), `VersionEditHandlerPointInTime`, background compaction purge points, filesystem wrappers, table-file naming helpers, checksum verification reads, manual compaction helpers, and Linux-specific file-linking behavior.

## Risks and Edge Cases

Follower catch-up is race-prone because the leader can flush, compact, purge obsolete files, and roll over the MANIFEST while the follower is reading. A follower can see edit records for files that have already disappeared, or it can link files that are later deleted by a subsequent compaction edit. MANIFEST rollover is especially subtle because a catch-up pass may end without installing a new version and must rely on the next refresh.

## Test Signals

Signals include follower point reads, checksum-verified `Get`, directory table-file-number parity, sync-point ordered catch-up completion, and successful cleanup of intermediate obsolete files. The file is compiled only under `OS_LINUX`, so cross-platform test coverage must come from other follower-mode tests or mocked behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_follower_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.cc -->
# sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.cc

## Purpose

`compacted_db_impl.cc` implements `CompactedDBImpl`, a read-only DB implementation optimized for fully compacted databases with a very simple file layout. It bypasses normal DBImpl read paths and directly chooses an SST file by key range before calling the table reader. The mode is intentionally narrow: it supports reads from the default column family when all data is in one sorted level or in a single L0 file, and rejects layouts needing normal LSM merging.

## Important APIs, Types, and Functions

- The constructor calls the `DBImpl` read-only base constructor and initializes cached column-family/version/comparator pointers.
- `FindFile(const Slice& key)` binary-searches the `LevelFilesBrief` array by largest user key.
- `Get(...)` validates `ReadOptions::io_activity`, timestamp compatibility, builds a `LookupKey` at `kMaxSequenceNumber`, chooses a file, opens/pins it through `TableCache::FindTable`, and calls `TableReader::Get`.
- `MultiGet(...)` performs the same logic per key, but is explicitly not optimized like `DBImpl::MultiGet`.
- `Init(const Options&)` recovers the default CF read-only, installs a super version, validates the compacted layout, and caches `cfd_`, `version_`, `user_comparator_`, `files_`, and `files_level_`.
- `Open(...)` validates `max_open_files=-1` and no merge operator, constructs the DB, initializes it, marks it opened, optionally schedules async file opening, starts periodic tasks, and returns the DB pointer.

## Control Flow

On open, `Init` calls `Recover` in read-only mode for the default CF, installs a super version, and examines `VersionStorageInfo`. It rejects empty DBs, more than one L0 file, a mixture of L0 and other levels, or multiple non-empty non-L0 levels. If exactly one L0 file exists, reads use L0. Otherwise the last non-empty sorted level becomes the file array.

On `Get`, the implementation normalizes IO activity to `kGet`, enforces timestamp read rules, clears an optional returned timestamp, creates `GetContext` and `BlobFetcher`, finds the candidate file, checks the key is not below that file's smallest key, opens the table with index/filter prefetch and pinned table handle, and calls `TableReader::Get`. It maps found/not-found context state to `Status::OK` or `Status::NotFound`.

`MultiGet` validates IO activity and timestamp options once, initializes all statuses on validation failure, clears returned timestamps, then loops over keys with the same file selection and direct table-reader lookup used by `Get`.

## State and Persistence Behavior

The implementation does not write persistent state. It reads recovered MANIFEST/version state and caches pointers into the default column family's current super version. All mutating operations are disabled in the header. Blob values are fetched through `BlobFetcher` using the cached version. Timestamp handling uses current CF metadata and can reject reads against collapsed history.

## Dependencies and Integration Points

This file integrates `DBImpl` recovery/open lifecycle, `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `LevelFilesBrief`, `TableCache`, `TableReader`, `GetContext`, `LookupKey`, timestamp validation helpers, `BlobFetcher`, and DB logging/periodic-task startup. It depends on sorted non-overlapping file ranges when using a non-L0 level.

## Risks and Edge Cases

`FindFile` assumes `files_.num_files > 0` and sorted file ranges; incorrect layout validation would make direct lookup unsafe. The binary search passes `files_.files + right`, which excludes the last slot as the upper bound expression relies on `right = num_files - 1`; this makes layout assumptions worth test attention around first/last files. The implementation supports only default CF and no merge operator, so callers expecting full DB semantics must use normal read-only DB modes. Timestamp and blob behavior add risk because this optimized path must preserve normal read semantics while bypassing DBImpl's richer read machinery.

## Test Signals

Expected test signals are successful `DB::OpenForReadOnly`/compacted-mode opens for fully compacted layouts, `InvalidArgument` for unsupported options, `NotSupported` for unsupported layouts, point-read parity with normal DB reads, blob-value reads, timestamp mismatch/collapsed-history errors, and failed write/flush/compaction calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.h -->
# sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.h

## Purpose

`compacted_db_impl.h` declares `CompactedDBImpl`, a specialized read-only subclass of `DBImpl` for fully compacted DBs. The header documents the public contract: only read APIs are implemented, most write/maintenance APIs return `NotSupported`, and live-file enumeration is allowed without forcing a memtable flush.

## Important APIs, Types, and Members

- `CompactedDBImpl(const DBOptions&, const std::string&)`, deleted copy operations, and virtual destructor define ownership/lifetime.
- `static Status Open(const Options&, const std::string&, std::unique_ptr<DB>*)` is the construction entry point.
- `Get` and `MultiGet` override DB read APIs while exposing base overloads with `using DB::Get` and `using DB::MultiGet`.
- Mutating overrides return `Status::NotSupported`: `Put`, `PutEntity`, `Merge`, `Delete`, `Write`, `CompactRange`, `DisableFileDeletions`, `EnableFileDeletions`, `Flush`, `SyncWAL`, `IngestExternalFile`, `CreateColumnFamilyWithImport`, and `ClipColumnFamily`.
- `GetLiveFiles` delegates to `DBImpl::GetLiveFiles(..., false)` so compacted read-only mode can enumerate live files without flushing.
- Private state includes `ColumnFamilyData* cfd_`, `Version* version_`, `const Comparator* user_comparator_`, `LevelFilesBrief files_`, and `int files_level_`.

## Control Flow and Integration Contract

The header establishes that `Open` and `Init` are responsible for populating cached read state before any read call. `FindFile` is an inline private helper used by implementation reads to map a user key to a file in `files_`. All inherited write APIs that might mutate memtables, WALs, MANIFESTs, compaction state, file deletion state, or external-file state are blocked at the interface boundary.

The class is a friend of `DB`, matching other RocksDB implementation classes that are constructed through public factory functions. The TODO comments note overlap with `DBImplSecondary` and `DBImplReadOnly`, suggesting this class duplicates some read-only policy that might later be shared.

## State and Persistence Behavior

The header declares no owned persistent resources beyond the base `DBImpl` machinery. Its member pointers are non-owning references into DBImpl-managed column-family/version/super-version state. Since flush, WAL sync, writes, compaction, ingestion, import, and deletion control are disabled, this mode should not create new persistent DB files after open. Live-file listing is observational only.

## Dependencies and Integration Points

The class depends on `db/db_impl/db_impl.h` for the base implementation, `ColumnFamilyData`, `Version`, `Comparator`, and `LevelFilesBrief` declarations. It integrates with the public `DB` API by overriding methods rather than introducing a separate interface, allowing callers to hold a `std::unique_ptr<DB>` while receiving compacted-mode behavior.

## Risks and Edge Cases

Because the header blocks many but not necessarily every mutating DB API, the `FIXME` about missing write-function overrides is significant. Any inherited mutating API accidentally left enabled would violate read-only compacted-mode assumptions. The non-owning cached pointers require the implementation to preserve super-version lifetime correctly. The `GetLiveFiles` override ignores the caller's `flush_memtable` intent, which is appropriate for read-only mode but could surprise generic code expecting a flush attempt.

## Test Signals

Useful tests should assert write-like APIs return `NotSupported`, `GetLiveFiles(..., flush_memtable=true)` does not attempt a flush, open rejects unsupported DB layouts/options, and read APIs work through the normal `DB` interface despite the specialized implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.h -->
