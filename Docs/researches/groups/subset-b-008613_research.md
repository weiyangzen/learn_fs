# subset-b-008613 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_test.cc -->
# sources/storage-engines/rocksdb/db/external_sst_file_test.cc

## Purpose
`external_sst_file_test.cc` is the main integration and regression suite for RocksDB external SST generation and ingestion. It exercises `SstFileWriter`, `DB::IngestExternalFile`, multi-column-family ingestion, two-phase `PrepareFileIngestion`/`CommitFileIngestionHandle`, global sequence-number assignment, ingestion-behind, DB-generated SST ingestion, timestamp-aware SSTs, cache/filter behavior, and failure atomicity around filesystem and MANIFEST updates.

## Important APIs, Types, and Functions
The test fixtures are `ExternalSSTFileTestBase`, `ExternalSSTFileTest`, `ExternSSTFileLinkFailFallbackTest`, `ExternalSSTFileWithTimestampTest`, `ExternalSSTBlockChecksumTest`, `IngestDBGeneratedFileTest`, and `IngestDBGeneratedFileTest2`. `ExternalSSTTestFS` wraps `FileSystem` and can fail `LinkFile` to test link/copy fallback. Core helpers include `GenerateOneExternalFile`, overloaded `GenerateAndAddExternalFile`, `GenerateAndAddExternalFiles`, `GenerateExternalFileOnly`, and `DeprecatedAddFile`.

The suite directly covers public and semi-public APIs such as `SstFileWriter::Open`, `Put`, `PutEntity`, `DeleteRange`, `Finish`, `FileSize`, `SstFileReader::VerifyChecksum`, `DB::IngestExternalFile`, `DB::IngestExternalFiles`, `DB::PrepareFileIngestion`, `DB::CommitFileIngestionHandle`, `DB::CommitFileIngestionHandles`, `FileIngestionHandle::Abort`, `IngestExternalFileOptions`, `IngestExternalFileArg`, `ExternalSstFileInfo`, `ExternalFileIngestionInfo`, `EventListener::OnExternalFileIngested`, and column-family handle variants. It also probes internal signals through `SyncPoint`, `FilesPerLevel`, `TEST_GetFilesMetaData`, `TEST_WaitForCompact`, table properties, histograms, and internal compaction stats.

## Control Flow
The common path creates one or more sorted SST files under `sst_files_dir_`, optionally sorts and de-duplicates test input by the active comparator, finishes the writer, builds ingestion options, then either calls direct ingestion or the two-phase prepare/commit path depending on the parameterized `two_phase_ingest_` flag. Verification normally reads DB keys, checks `FilesPerLevel`, compares against a `true_data` map, or reopens the DB to validate persisted version state.

The early tests validate writer invariants and single-file ingestion: `Basic`, `BasicWideColumn`, and `BasicMixed` confirm file metadata, range deletions, wide-column entities, mixed value/entity files, empty-file rejection, snapshot checks, tombstone overlap checks, and post-flush/compaction correctness. `AddList` and `AddListAtomicity` extend this to lists of files, user-collected table properties, internal overlap rejection, and all-or-nothing behavior if any listed file is missing.

The prepare/commit tests isolate two-phase state transitions. `PrepareThenCommit` confirms a prepared file is staged but invisible until commit. `AbortPreparedIngestion` confirms abort leaves no visible data and that a committed aborted handle is invalid. `MultiHandleAtomicCommit` commits prepared handles together across overlapping column-family sets and verifies per-CF merge semantics and later-handle sequence ordering. `MultiHandleSameColumnFamilyIncompatibleOptions` rejects merged handles with incompatible options and verifies rollback.

The level-placement and global-sequence tests create overlapping file and memtable patterns to force ingestion into bottom levels, L0, or intermediate levels. `PickedLevel`, `PickedLevelDynamic`, `IngestFileWithGlobalSeqnoAssignedLevel`, `IngestFileWithGlobalSeqnoAssignedUniversal`, `IngestFileWithGlobalSeqnoMemtableFlush`, `L0SortingIssue`, and `FIFOCompaction` validate how overlap with memtables, snapshots, compaction outputs, FIFO/universal/level compaction, and dynamic level bytes determine global sequence number and target level. `DeltaEncodingWhileGlobalSeqnoPresent` and its iterator-switch variant are regression tests for block delta decoding when a global sequence number is applied to keys with tricky shared prefixes.

The concurrency and failure tests coordinate background operations with `SyncPoint`. `PurgeObsoleteFilesBug` prevents obsolete-file deletion from racing with ingestion. `MultiThreaded` writes and ingests many files concurrently, intentionally duplicating ingests to require exactly one success. `CompactDuringAddFileRandom`, `AddFileTrivialMoveBug`, `CompactAddedFiles`, `WithUnorderedWrite`, `CompactionDeadlock`, and `IngestFilesTriggerFlushingWithTwoWriteQueue` cover compaction races, trivial move hazards, unordered-write flushing, and writer queue deadlock risks. Multi-CF tests inject failures during prepare, run/commit, and partial MANIFEST writes to verify no CF observes partial ingestion.

Timestamp tests use `test::BytewiseComparatorWithU64TsWrapper` and `persist_user_defined_timestamps` variants. They verify timestamp-bearing point/range tombstone metadata, read-time timestamp lookup, rejection of unsafe user-key overlap, compatibility between timestamp-persisted and non-persisted files, and the current lack of ingestion-behind support with user-defined timestamps.

DB-generated file tests use existing live-file metadata from another column family or DB, enable `allow_db_generated_files`, and ingest files with zero and non-zero sequence numbers. They validate rejection when metadata is unavailable, when overlap would require unsafe non-zero assignment, when `write_global_seqno` is combined with DB-generated files, when `fail_if_not_bottommost_level` cannot be honored, and when snapshot consistency would force a newer global sequence number. The larger randomized cases combine zero-seqno snapshot files and non-zero live-write files to model secondary-index rebuild workflows.

## State and Persistence Behavior
The suite validates durable version state rather than only in-memory reads. It repeatedly reopens DBs and column families, inspects MANIFEST-installed files through metadata, checks sequence numbers, and confirms ingestion files remain usable after original source CFs are dropped. External SST files start outside the DB and are copied, moved, or linked into DB-managed table files; tests check source-file existence and bytes copied/moved for link/move options. A successful no-overlap ingestion can preserve sequence number zero; overlap with memtables, live snapshots, FIFO compaction, or DB-generated non-zero files can force L0 placement or non-zero sequence handling. Multi-CF ingestion must install version edits atomically across column families, and fault-injection tests verify failed prepare/commit/MANIFEST paths do not leave visible partial data.

## Dependencies and Integration Points
The test depends on `DBTestBase`, RocksDB DB/CF APIs, `SstFileWriter`, `SstFileReader`, `IngestExternalFileOptions`, `BlockBasedTableFactory`, bloom filters, cache/statistics APIs, `FaultInjectionTestEnv`, `CompositeEnvWrapper`, `FileSystemWrapper`, `SyncPoint`, `EventListener`, `VersionSet`, `InternalStats`, compaction metadata, timestamp comparators, `VectorRepFactory`, and file-name parsing. It integrates with storage engine behavior across write path, flush, compaction picker, MANIFEST logging, table building/reading, block cache, filter construction, snapshot visibility, and file-system link/copy/move semantics.

## Risks
External ingestion has a large correctness surface: unsafe overlap detection can break snapshot isolation, wrong sequence assignment can invert version ordering, wrong level placement can violate LSM invariants, failed copies or MANIFEST writes can strand files, and concurrent compaction/obsolete-file deletion can race with installation. DB-generated files are especially risky because their internal sequence numbers must be interpreted without rewriting in many cases. Timestamp mode adds a second ordering dimension and rejects cases that could not preserve timestamp invariants. Link/move/copy behavior is environment-sensitive, including encrypted environments and filesystems without hard-link support.

## Test Signals
This file is itself the test signal. It uses parameterized coverage across `write_global_seqno`, checksum verification, two-phase ingestion, link/move fallback, DB-generated-file options, compaction styles, timestamps, and multiple option configurations from `DBTestBase::ChangeOptions`. Assertions cover visible values, snapshot reads, table properties, listener payloads, histograms (`INGEST_EXTERNAL_FILE_PREPARE_TIME`, `INGEST_EXTERNAL_FILE_RUN_TIME`), cache filter/index effects, compaction stats bytes moved/copied, exact error classes/messages, file counts per level, and reopen persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/external_sst_file_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/fault_injection_test.cc -->
# sources/storage-engines/rocksdb/db/fault_injection_test.cc

## Purpose
`fault_injection_test.cc` verifies RocksDB durability and recovery behavior under simulated data loss. It uses fault-injection environments/filesystems to drop unsynced data, delete unsynced files, reject invalid open patterns, and confirm that synced WAL/compacted data survives crash-like reopen sequences while unsynced data is either absent or does not corrupt reads.

## Important APIs, Types, and Functions
The central fixture is `FaultInjectionTest`, parameterized by key order and option configuration ranges. Important helpers include `CurrentOptions`, `NewDB`, `OpenDB`, `CloseDB`, `Build`, `Verify`, `ReadValue`, `DeleteAllData`, `ResetDBState`, `PartialCompactTestPreFault`, `PartialCompactTestReopenWithFault`, `NoWriteTestReopenWithFault`, and `WaitCompactionFinish`. It uses `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `MockEnv`, `DBImpl::TEST_WaitForCompact`, `WriteBatch::MarkWalTerminationPoint`, `FlushWAL`, `CompactRange`, and `SyncPoint`.

The option enum covers default operation, separate data dir, separate WAL dir, sync WAL, WAL-dir plus sync WAL, and a multi-level stress configuration. `ResetMethod` distinguishes dropping unsynced file data, dropping random unsynced data, deleting files created after the last directory sync, and doing both.

## Control Flow
Each parameterized run opens a DB through `FaultInjectionTestEnv`, writes deterministic keys and 1000-byte pseudo-random values, forces persistence either by WAL sync or compaction depending on the option mode, writes more unsynced data, closes the DB with the filesystem marked inactive, applies a reset method, reopens, and verifies that pre-sync data is found while post-sync data is either found or cleanly not found. The main `FaultTest` loops over random pre/post counts and all relevant option configurations.

Specialized tests cover narrower failure modes. `WriteOptionSyncTest` blocks background flush, rolls the log, writes with `WriteOptions::sync`, flushes WAL without sync, injects loss, and verifies both records survive. `ManualLogSyncTest` validates `FlushWAL(true)` persistence. `UninstalledCompaction` forces a compaction to finish while the filesystem becomes inactive, then verifies reopen ordering and recovery from uninstalled compaction output. `WriteBatchWalTerminationTest` writes a batch with a WAL termination point and confirms only records before the marker survive after simulated loss.

Filesystem contract tests instantiate `FaultInjectionTestFS` directly. `ReadUnsyncedData` reads files that contain synced and unsynced suffixes, optionally syncing, appending, and closing between reads. File-open-contract tests verify `kNoReadersWhileOpenForWrite`, `kNoReopenForWrite`, `SyncFile`, `ReopenWritableFile`, delete/recreate behavior, and expected `IOStatus::NotSupported` cases.

## State and Persistence Behavior
The state under test is the boundary between RocksDB-visible writes and storage-persisted bytes. `FaultInjectionTestEnv` tracks filesystem state as of last sync and can discard later writes or created files. `sync_use_wal_` and `sync_use_compact_` encode which operation is expected to make data persistent for each option configuration. Reopen always calls `env_->ResetState()` before `DB::Open`, simulating a process restart with a possibly damaged storage image. Verification permits unsynced post-fault keys to be missing but treats corruption or unexpected errors as failures.

## Dependencies and Integration Points
This file integrates DB recovery, WAL rolling/sync, flush scheduling, background compaction, directory sync assumptions, file cache behavior, DB options for `wal_dir` and `db_paths`, `MockEnv`, `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `SyncPoint`, and filesystem-level open contracts. It also depends on test utilities for per-thread DB paths, stack trace installation, custom object registration, sleeping background tasks, and deterministic random data.

## Risks
The key risk is overestimating durability: writes protected only by process memory, unsynced WAL bytes, or unsynced table/directory creation must not be required after a crash. Conversely, data that was synced through WAL or made durable through compaction must not disappear. Separate WAL/data directories and multi-level compaction add directory-sync and file-installation risks. The filesystem contract tests guard against readers observing files still open for write and against reopening append paths that the fault-injection model cannot safely track.

## Test Signals
The suite asserts exact value equality for persisted keys, allows only `NotFound` for potentially lost keys, waits for compaction completion, and checks open-contract failures with `IsNotSupported`. It is parameterized for sequential and scrambled key orders and split across option ranges so long-running fault combinations remain bounded. The tests use randomized lengths and resets, making them useful signals for recovery regressions and for bugs in the fault-injection layer itself.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/fault_injection_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer.cc -->
# sources/storage-engines/rocksdb/db/file_indexer.cc

## Purpose
`file_indexer.cc` implements `FileIndexer`, a precomputed hint structure used by `Version::Get()`-style searches to narrow the file-index range that must be binary-searched in the next level. It reuses comparisons between a target key and the current upper-level file's smallest/largest keys to skip lower-level files that cannot contain the key.

## Important APIs, Types, and Functions
The implemented methods are `FileIndexer::FileIndexer`, `NumLevelIndex`, `LevelIndexSize`, `GetNextLevelIndex`, `UpdateIndex`, `CalculateLB`, and `CalculateRB`. `UpdateIndex` consumes `std::vector<FileMetaData*>* files`, the number of levels, and an `Arena` for persistent allocation. It uses `Comparator::CompareWithoutTimestamp` against `FileMetaData::smallest.user_key()` and `largest.user_key()` to fill `IndexUnit` fields declared in the header.

## Control Flow
`UpdateIndex` is called after a version's file tree is known. It initializes `num_levels_`, allocates `level_rb_`, records each level's rightmost file index, and for levels `1` through `num_levels - 2` allocates an `IndexUnit` array when the upper level is non-empty. Four scans then populate lower-bound and right-bound hints: upper smallest versus lower largest, upper largest versus lower largest, upper smallest versus lower smallest, and upper largest versus lower smallest.

`CalculateLB` scans upper and lower files from left to right. When lower files are definitely smaller, it advances `lower_idx`; otherwise it records the first lower index that may still contain a key greater than the relevant upper key. If lower files are exhausted, remaining upper files receive `lower_size`, an empty interval marker beyond the last lower file. `CalculateRB` mirrors this from right to left, recording the last lower index that may contain a key smaller than the relevant upper key and using `-1` when all lower files are too large.

`GetNextLevelIndex` receives comparison outcomes from the caller: target key versus current file's smallest and largest. For the last level it returns an empty hint interval `[0, -1]`. Otherwise it chooses among the precomputed fields to return candidate lower-level bounds. If the key is below the current smallest, it may reuse the previous upper file's `largest_lb` for the left bound and `smallest_rb` for the right bound. If the key is inside the current file range, it uses smallest/largest combinations. If the key is above the current largest, it uses `largest_lb` and the next level's rightmost file.

## State and Persistence Behavior
All state is in-memory and version-scoped. `next_level_index_` stores one `IndexLevel` per level, each pointing to arena-allocated `IndexUnit` arrays; `level_rb_` is also arena allocated. The class does not own or persist `FileMetaData`; it assumes the file arrays and comparator ordering remain stable for the life of the owning version. There is no disk format impact.

## Dependencies and Integration Points
`FileIndexer` depends on `db/version_edit.h` for `FileMetaData`, `rocksdb/comparator.h`, `memory/arena.h`, and `util/autovector`. It is part of the version/file-search path and integrates with the LSM invariant that non-L0 levels are sorted by non-overlapping key ranges. Timestamp-aware comparators are handled through `CompareWithoutTimestamp`, so the index is based on user-key range overlap rather than timestamp suffixes.

## Risks
The implementation assumes sorted file metadata per level and valid non-overlapping lower-level ranges. Incorrect ordering or comparator mismatch would produce unsafe bounds and missed reads. The bounds use `int32_t`; very large file counts must not exceed `kLevelMaxIndex`. `UpdateIndex` asserts `level_rb_ == nullptr`, so it is not a reusable mutating builder. Empty lower levels intentionally produce intervals such as `[0, -1]` or `[lower_size, lower_size - 1]`, and callers must treat `left > right` as no candidate files.

## Test Signals
`file_indexer_test.cc` directly verifies empty DBs, upper files entirely left or right of lower files, an empty middle level, and mixed overlaps. Assertions exercise all comparison cases passed to `GetNextLevelIndex`: less than smallest, equal smallest, between smallest/largest, equal largest, and greater than largest. Broader signal is indirect through DB point lookup correctness and performance in version searches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer.h -->
# sources/storage-engines/rocksdb/db/file_indexer.h

## Purpose
`file_indexer.h` declares the `FileIndexer` class and documents the search-hint model used to speed lower-level file lookup. The key idea is that comparisons already made against an upper-level file can be translated into a narrower candidate interval in the next level, avoiding repeated full binary searches across increasingly large lower levels.

## Important APIs, Types, and Functions
The public API is `FileIndexer(const Comparator*)`, `NumLevelIndex`, `LevelIndexSize`, `GetNextLevelIndex`, and `UpdateIndex`. `kLevelMaxIndex` records the maximum supported index value. Private types are `IndexUnit`, which stores four precomputed hints (`smallest_lb`, `largest_lb`, `smallest_rb`, `largest_rb`), and `IndexLevel`, which stores an array of `IndexUnit` entries for one level.

The private helpers `CalculateLB` and `CalculateRB` are declared with comparator and setter callbacks so the implementation can reuse the same scan logic for smallest/largest combinations.

## Control Flow
Clients build the index with the complete per-level `FileMetaData` vectors. During lookup, a caller compares a key with the current file's smallest and largest user keys, passes the comparison results to `GetNextLevelIndex`, and receives left/right bounds for the next-level search. Header comments enumerate the three major comparison outcomes: key below the current file, key inside its range, and key above its range.

## State and Persistence Behavior
`FileIndexer` stores `num_levels_`, a non-owning `Comparator` pointer, `next_level_index_`, and `level_rb_`. It uses arena allocation, so lifetime is tied to the arena supplied to `UpdateIndex`, typically the owning version's arena. It is a derived in-memory structure and is not serialized.

## Dependencies and Integration Points
The declaration depends on `Comparator`, `FileMetaData`, `Arena`, `autovector`, and standard functional/vector types. It sits between version metadata construction and the read path. It is designed for the sorted levels below L0, which is why `GetNextLevelIndex` asserts `level > 0`; L0 overlap semantics are different.

## Risks
The header exposes a low-level API that relies on callers passing comparison signs consistent with the same comparator used at build time. Bounds are signed `int32_t` values where `right_bound == -1` and `left_bound == right_bound + 1` are valid empty ranges. Misinterpreting those sentinels can cause invalid array access or missed files. Since arrays are arena-backed and there is no destructor cleanup, the arena lifetime contract is critical.

## Test Signals
The focused test file checks `LevelIndexSize`, empty input behavior, and expected next-level ranges for synthetic integer-key levels. Production signal comes from point lookups and compaction/version metadata tests that would fail if file search skipped candidate SSTs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer_test.cc -->
# sources/storage-engines/rocksdb/db/file_indexer_test.cc

## Purpose
`file_indexer_test.cc` unit-tests `FileIndexer` with deterministic integer key ranges. It verifies that precomputed lower-level search bounds are correct for empty state, non-overlap on either side, empty intermediate levels, and mixed overlap patterns.

## Important APIs, Types, and Functions
`IntComparator` implements `Comparator` over 8-byte integer slices. `FileIndexerTest` owns a four-level `std::vector<FileMetaData*>` array, helper `AddFile`, helper `IntKey`, cleanup through `ClearFiles`, and a wrapper for `FileIndexer::GetNextLevelIndex` that resets output sentinels. Tests are `Empty`, `no_overlap_left`, `no_overlap_right`, `empty_L2`, and `mixed`.

## Control Flow
Each non-empty test allocates an `Arena`, creates a `FileIndexer`, adds synthetic file ranges to levels 1 through 3, calls `UpdateIndex`, and then invokes `GetNextLevelIndex` with representative comparison outcomes. The tests check exact left/right bounds for each current file. The comparison arguments model whether a target key is below the file's smallest key, equal to the smallest key, inside the range, equal to largest, or above largest.

`no_overlap_left` verifies upper-level files that all sit left of next-level files, producing empty right bounds until the target is greater than the upper largest. `no_overlap_right` verifies the inverse, where lower files can be skipped on the left and empty intervals appear as `left == lower_size`, `right == lower_size - 1`. `empty_L2` confirms an empty next level produces `[0, -1]`. `mixed` checks exact overlapping windows across L1-to-L2 and L2-to-L3.

## State and Persistence Behavior
The test manually allocates `FileMetaData` and deletes it after each case. `FileIndexer` allocations use a stack `Arena`, matching production lifetime style. There is no persistence; the test validates in-memory derived indexes over metadata.

## Dependencies and Integration Points
The test includes `db/file_indexer.h`, `db/dbformat.h`, `db/version_edit.h`, RocksDB comparator APIs, stack trace installation, and the RocksDB test harness. It provides direct coverage for the file-indexer component used by version lookup.

## Risks
The comparator uses `reinterpret_cast<const int64_t*>` and asserts 8-byte keys, which is acceptable for this controlled test but not a general key encoding. The synthetic ranges assume sorted files; the tests do not cover unsorted metadata because production should not provide it. The assertions are brittle by design: a small change in bound semantics will surface immediately.

## Test Signals
The exact `ASSERT_EQ` matrices are the primary signal. They cover both valid non-empty intervals and empty intervals where `left > right`, and they check that `LevelIndexSize` returns zero before indexing. A failure here indicates either unsafe file skipping or lost optimization precision in `FileIndexer`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/file_indexer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/filename_test.cc -->
# sources/storage-engines/rocksdb/db/filename_test.cc

## Purpose
`filename_test.cc` validates RocksDB file-name parsing, construction, info-log naming, and path normalization. It ensures durable file naming conventions remain compatible for WALs, SSTs, MANIFESTs, CURRENT, LOCK, temp files, metadata DB files, and info logs in default or separate log directories.

## Important APIs, Types, and Functions
The test fixture is `FileNameTest`. It exercises `ParseFileName`, `InfoLogPrefix`, `InfoLogFileName`, `OldInfoLogFileName`, `CurrentFileName`, `LockFileName`, `LogFileName`, `TableFileName`, `DescriptorFileName`, `TempFileName`, `MetaDatabaseName`, and `NormalizePath`. It checks returned `FileType` values such as `kWalFile`, `kTableFile`, `kCurrentFile`, `kDBLockFile`, `kDescriptorFile`, `kMetaDatabase`, `kInfoLogFile`, and `kTempFile`.

## Control Flow
`Parse` loops over successful cases for three modes: default info-log directory, different info-log directory with a generated prefix, and no log-dir prefix checking. It verifies file number and type, including the maximum `uint64_t` WAL number. It then loops over malformed names and overflowed numbers that must fail.

`InfoLogFileName` computes an absolute DB path, verifies normal `LOG`/`LOG.old.N` naming under the DB directory, and verifies prefixed log names under a separate info-log directory. `Construction` generates each canonical file name, strips the directory prefix, parses it, and checks type/number. It also checks `TableFileName` path selection from one or multiple `DbPath` entries. `NormalizePath` checks duplicate separator collapse while preserving important UNC/server-prefix behavior.

## State and Persistence Behavior
The file does not mutate DB state, but it protects persisted naming contracts. These names are how RocksDB discovers WALs, table files, descriptors, lock files, and logs on restart or cleanup. Incorrect parsing can cause recovery to ignore live files or treat unrelated files as DB files. Incorrect construction can place table files in the wrong DB path or make generated names unparsable.

## Dependencies and Integration Points
The test depends on `file/filename.h`, `db/dbformat.h`, `Env::GetAbsolutePath`, `DbPath`, path separator constants, and the RocksDB test harness. It integrates with DB open/recovery, MANIFEST management, WAL discovery, obsolete-file cleanup, multi-path table placement, and info-log rotation.

## Risks
Filename parsing must reject partial prefixes, wrong suffixes, and numeric overflows. Info-log parsing is sensitive because separate log directories use DB-path-derived prefixes, so tests distinguish default, different-dir, and unchecked modes. Path normalization must collapse redundant separators without destroying root or UNC semantics.

## Test Signals
The test provides table-driven positive and negative parse coverage, round-trip construction coverage, separate log-dir naming checks, and platform-aware separator normalization. The `main` function installs the stack trace handler and runs the RocksDB test harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/filename_test.cc -->
