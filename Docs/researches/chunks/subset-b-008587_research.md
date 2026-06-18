# sources/storage-engines/rocksdb/db/db_compaction_test.cc lines 7098-12886

## Scope

This chunk covers the later half of RocksDB's `db_compaction_test.cc`, starting at direct-I/O compaction read stress tests and ending at the test program `main()`. It is almost entirely GoogleTest coverage for compaction behavior rather than production implementation. The tests exercise level, universal, and FIFO compaction; round-robin compaction priority; manual compaction cancellation and refit conflicts; external SST ingestion races; blob file compaction and garbage collection; checksum handoff; FIFO temperature aging; dynamic level sizing; record-count verification; table-cache cleanup on failure; output verification flags; and large-value rejection in compaction filters.

## Purpose

The code validates correctness and regression-sensitive behavior around RocksDB compaction. Most tests construct specific LSM shapes using `Put()`, `Flush()`, `MoveFilesToLevel()`, `CompactRange()`, and `CompactFiles()`, then assert on file layout, returned `Status`, metadata, internal counters, or final reads.

The major themes are:

- compactions must preserve key visibility across concurrent reads, ingestion, snapshots, and L0 ordering edge cases;
- manual compactions must return promptly and cleanly when disabled, cancelled, conflicted, or run during DB close/shutdown;
- range-conflict checks must prevent concurrent compaction or ingestion from producing overlapping output files;
- compaction metadata, cursors, blob files, checksums, temperatures, record counts, and table-cache entries must be updated or cleaned up consistently on success and failure;
- dynamic level-byte mode, round-robin picking, FIFO aging, read-triggered compaction, periodic compaction, and verification flags must integrate with the same common compaction pipeline.

## Important APIs, Types, and Functions

- `DBCompactionTest`, `DBCompactionTestWithParam`, `DBCompactionTestWithBottommostParam`, `ChangeLevelConflictsWithAuto`, and derived fixtures provide access to helper methods such as `CurrentOptions()`, `DestroyAndReopen()`, `Reopen()`, `Put()`, `Get()`, `Flush()`, `MoveFilesToLevel()`, `FilesPerLevel()`, `NumTableFilesAtLevel()`, `GenerateNewFile()`, and `GetBlobFileNumbers()`.
- `UseDirectIoForCompactionReadsConcurrentReadStress` stresses `Options::use_direct_io_for_compaction_reads` with buffered foreground reads while manual compactions run over the same SSTs.
- `CompactionPriTest` parameterizes `Options::compaction_pri` across `kByCompensatedSize`, `kOldestLargestSeqFirst`, `kOldestSmallestSeqFirst`, `kMinOverlappingRatio`, and `kRoundRobin`.
- `PersistRoundRobinCompactCursor`, `RoundRobinCutOutputAtCompactCursor`, `RoundRobinWithoutAdditionalResources`, and the disabled round-robin subcompaction tests cover round-robin cursors, clean output boundaries, and subcompaction resource accounting.
- `NoopMergeOperator` is a test merge operator used by partial/manual bottommost compaction tests.
- `DBCompactionTestWithOngoingFileIngestionParam` runs the same range-conflict scenario against auto compaction, non-refit `CompactRange`, refit-level `CompactRange`, and `CompactFiles`.
- `IngestOneKeyValue()` creates an external SST with `SstFileWriter` and ingests it into the DB. It is reused by L0 misordering tests.
- `DBCompactionTestL0FilesMisorderCorruption` configures level, universal, and FIFO compaction styles, pauses/resumes background compaction threads, marks files for periodic/delete-triggered universal compaction, installs sync points, and reads the latest L0 file's largest sequence number.
- `DBCompactionTestBlobError` parameterizes injected blob-file write failures at `BlobFileBuilder::WriteBlobToFile:AddRecord` and `AppendFooter`.
- `DBCompactionTestBlobGC` parameterizes blob GC age cutoff and whether `enable_blob_files` remains enabled during compaction.
- `VerifyTemperatureFileReadStats()` checks per-temperature read counters in both `Statistics` tickers and `IOStatsContext`.
- `PeriodicCompactionListener` records `CompactionReason::kPeriodicCompaction` through `EventListener::OnCompactionBegin`.
- Sync points are central integration hooks throughout this range: examples include `LevelCompactionPicker::PickCompaction:Return`, `CompactionJob::GenSubcompactionBoundaries:0`, `VersionSet::LogAndApply:*`, `DBImpl::CompactRange:*`, `DBImpl::RunManualCompaction:*`, `CompactionJob::Run():AfterVerifyOutputFiles`, table-builder skip hooks, and file-reader fault hooks.

## Control Flow

The early tests in this chunk drive direct-I/O and priority behavior. Direct-I/O testing opens the DB with `use_direct_io_for_compaction_reads=true`, creates several L0 files, starts reader threads that continuously call `Get()`, then repeatedly rewrites all keys, flushes, and manually compacts. The expected outcome is no non-OK/non-NotFound read status and all keys containing the final round's value. Priority tests write shuffled keys under each compaction-priority policy and wait for compaction to prove data remains readable.

Round-robin tests first create enough L0 pressure to force compactions between lower levels, then read `VersionStorageInfo::GetCompactCursors()` before and after reopen to verify cursor persistence. Other round-robin tests create multi-file L1/L2 shapes, use sync-point callbacks to observe chosen input files and planned subcompactions, and verify output files are split around an explicit compact cursor. Some subcompaction resource tests are disabled because the setup is known flaky, but the assertions document expected behavior around pressure tokens, background threads, and resource reservation.

Manual compaction tests create controlled LSM shapes, then force partial compaction, bottommost optimized compaction, size-limited manual compaction splits, shutdown races, read-only failure paths, and FIFO duplicate-picking regressions. `ManualCompactionMax` measures how `max_compaction_bytes` and `target_file_size_base` split a broad manual compaction into one, several, or many background compaction executions. Shutdown/read-only tests assert that failure paths return `Status` rather than hanging, and that compaction registration is cleaned up after error.

External file ingestion tests create overlapping SSTs and orchestrate races between ingestion and compaction. `FixFileIngestionCompactionDeadlock` ensures ingestion-triggered flush can proceed even during L0 write stall and auto compaction. `DBCompactionTestWithOngoingFileIngestionParam::RangeConflictCheck` pauses one thread inside ingestion's MANIFEST update and has a second thread attempt auto/manual/refit/`CompactFiles` compaction into the same output level; the compaction path must return OK, `NotSupported`, or `Aborted` as appropriate without corrupting overlapping ranges.

Consistency and L0 misordering tests deliberately perturb internal state. `ConsistencyFailTest` and `ConsistencyFailTest2` swap `FileMetaData` pointers during `VersionBuilder::CheckConsistency*` and expect corruption/frozen DB behavior. L0 misordering tests build a memtable with newer versions, ingest SST files with higher file numbers/sequence numbers, trigger intra-L0 compaction via level, universal, FIFO, `CompactFiles`, or `CompactRange`, then flush the memtable. They assert the flushed L0 file can have a lower largest seqno than the compaction output while still returning the newer user value, guarding L0 ordering rules for ingested files.

Blob tests first compact ordinary SST values after reopening with `enable_blob_files=true`, expecting the newest values to move into one blob file and compaction stats to report table/blob bytes and file counts. Error tests inject I/O at blob record writing or footer writing and check that no LSM/blob metadata is installed on failure, while stats reflect whether the SST had already been written. GC tests generate many one-blob files, force or configure blob garbage collection, optionally disable new blob files so collected values are inlined, then verify original blob-file retention by cutoff and blob read/write statistics. Corruption tests fake invalid blob indexes, inlined TTL blob indexes, and non-existent blob file references and expect compaction corruption.

Checksum handoff tests wrap the filesystem in `FaultInjectionTestFS`. With `checksum_handoff_file_types` including table files or descriptor files, they switch the injected checksum type or inject data corruption exactly before background compaction. Table-file handoff errors become unrecoverable compaction errors; MANIFEST/descriptor handoff errors become fatal errors. Companion tests leave the option unset or use `kNoChecksum` support to ensure the same faults are ignored when handoff is disabled or unsupported.

FIFO temperature tests use mock sleep and `CompactionOptionsFIFO::file_temperature_age_thresholds` to age files across temperatures. `FIFOChangeTemperature` checks cold aging with and without trivial copy and with optional default write temperature changes. `FIFOMultiTierTemperatureAging` advances files from hot to warm, cool, cold, and ice, verifies metadata temperature counts, per-temperature file creation callbacks, and read-stat counters for each tier and for all tiers after reopen.

Manual compaction cancellation and close tests block background queues with `test::SleepingBackgroundTask`, schedule one or more manual compactions, and call `DisableManualCompaction()` or `Close()` at precise sync points. They cover compactions that are queued, just started, in progress, waiting for automatic compactions to drain, or sharing the queue with auto compaction. Expected results are `Status::Incomplete` for cancelled foreground compactions, no queue deadlock, and clean DB close.

Refit/change-level tests create LSM shapes where `CompactRangeOptions::change_level` moves files between levels. Sync points force races with auto compaction or manual compaction during `ReFitLevel()`. The expected behavior is failed foreground refit/compaction (`NotSupported`, `Aborted`, `Incomplete`, or non-OK depending on path) without overlapping files or consistency failures. Error-path tests verify a failed `ReFitLevel()` clears internal state so later valid refits still succeed.

Dynamic-level and range-drain tests exercise `level_compaction_dynamic_level_bytes`, universal-to-level migration, disallowing non-L0 refit to L0, and draining unneeded levels after the level-size multiplier changes or the DB becomes smaller after `DeleteRange()`. Manual compaction range tests force auto compaction to move a target level while manual compaction is in progress, verifying the manual compaction keeps going to the real bottommost level and covers all keys in the requested range.

The final tests target validation and cleanup: subcompaction event counts, input/output record-count verification, retryable file-header read errors, releasing compaction registrations during grouped MANIFEST writes, TTL newest-key-time propagation, target-file-size tail estimation, periodic and read-triggered compaction reasons, round-robin clean-cut expansion at shared boundaries, table-cache leaks after compaction/installation/atomic-flush failures, checksum/iteration output verification without paranoid file checks, and rejection of compaction-filter output values at 4GB or larger.

## State and Persistence Behavior

- LSM state is observed through file counts, `ColumnFamilyMetaData`, `LiveFileMetaData`, `FileMetaData`, `VersionSet`, `ColumnFamilyData`, `Version`, and `VersionStorageInfo`. Tests frequently assert exact `FilesPerLevel()` strings.
- Round-robin compaction persists compact cursors in `VersionStorageInfo`; the test captures `InternalKey` cursors, reopens, and compares with the internal comparator.
- Manual compaction state includes queued/running manual compaction registration, disabled-manual-compaction flags, in-progress compaction sets, background queue state, and `WriteControllerToken` pressure state. Tests check that cancellation unregisters state and does not block automatic compaction or close.
- External SST ingestion persists files through MANIFEST updates. Range-conflict tests assert concurrent compaction sees pending ingestion output ranges and aborts/conflicts before overlapping files are installed.
- L0 ordering state depends on file number, file largest sequence number, snapshot-induced global sequence assignment for ingested files, and read resolution among L0 files. The tests intentionally create cases where file-number ordering and seqno ordering differ.
- Blob compaction updates table metadata (`oldest_blob_file_number`), `VersionStorageInfo::GetBlobFiles()`, blob file counts/bytes, and `InternalStats::CompactionStats` blob counters. Failed blob compactions must leave L1 and blob metadata empty.
- FIFO temperature state is stored in file metadata and file creation options. Mock time drives age thresholds; reopening should preserve temperatures and keep read stats attributable to hot/warm/cool/cold/ice files.
- Dynamic-level state is reflected in base-level placement and MANIFEST edits from trivial moves during open or compaction. Universal-to-level migration with dynamic level bytes must produce stable MANIFEST entries across reopen.
- Record-count verification compares compaction iterator input counts and table-builder output counts against actual generated/added records; injected skips should turn into corruption statuses.
- Table-cache tests validate that output SST cache entries created during verification or flush build are released when later install steps fail and directory scans cannot find obsolete files due to injected metadata-read errors.
- Output verification state is controlled by `verify_output_flags`, `paranoid_file_checks`, and optional file checksum factories. Tests distinguish file checksum mismatch from false iteration checksum mismatches.

## Dependencies and Integration Points

- RocksDB public APIs: `DB::CompactRange`, `DB::CompactFiles`, `DB::SetOptions`, `DB::SetDBOptions`, `DB::GetProperty`, `DB::GetColumnFamilyMetaData`, `DB::GetLiveFilesMetaData`, `DB::WaitForCompact`, `IngestExternalFile`, `SstFileWriter`, snapshots, column-family handles, merge operators, compaction filters, and `EventListener`.
- Internal DB APIs: `DBImpl`, `dbfull()`, `TEST_WaitForCompact`, `TEST_CompactRange`, `TEST_GetFilesMetaData`, `TEST_write_controler`, `TEST_table_cache`, `VersionSet`, `VersionStorageInfo`, `ColumnFamilyData`, `InternalStats`, `LevelCompactionPicker`, `UniversalCompactionBuilder`, `CompactionJob`, `CompactionOutputs`, `TableCache`, and `WriteBatchInternal::PutBlobIndex`.
- Configuration types: `Options`, `CompactRangeOptions`, `CompactionOptions`, `CompactionOptionsFIFO`, `CompactionOptionsUniversal`, `BlockBasedTableOptions`, `PlainTableOptions`, `IngestExternalFileOptions`, `BottommostLevelCompaction`, `CompactionStyle`, `CompactionPri`, `Temperature`, `BlobGarbageCollectionPolicy`, and `VerifyOutputFlags`.
- Fault and concurrency utilities: `SyncPoint`, `port::Thread`, `std::thread`, atomics, `test::SleepingBackgroundTask`, `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `CompositeEnvWrapper`, `MockSystemClock`, and mock sleep.
- Table/blob/checksum internals: `BlobIndex`, `BlobFileBuilder`, `FileChecksumGenCrc32cFactory`, `ChecksumType`, `FileType::kTableFile`, `FileType::kDescriptorFile`, table factories/builders, `RandomAccessFileReader`, and `ParseFileName`.
- Statistics and observability: ticker counters such as `HOT_FILE_READ_BYTES`, `COLD_FILE_READ_COUNT`, `IOStatsContext::file_io_stats_by_temperature`, compaction stats, subcompaction completion events, compaction reasons, and file temperatures in metadata.

## Risks and Edge Cases

- Direct-I/O compaction reads use separate ephemeral direct handles while foreground reads use table-cache buffered handles. Incorrect cache-mode coexistence can produce I/O errors, corruption, or lifetime bugs under concurrent reads.
- Round-robin cursor persistence and clean-cut expansion are sensitive to internal-key comparison, shared user-key file boundaries, and duplicated input-file handling. Small mistakes can skip ranges or create overlapping output.
- Manual compaction cancellation spans queued, just-scheduled, running, waiting-for-drain, and close paths. Missing unregister/notify steps can hang future compactions or DB close.
- `change_level` refit must be isolated from auto/manual compactions targeting the same output level. A race can install overlapping non-L0 files or leave manual compaction disabled after an error path.
- External file ingestion releases the DB mutex during MANIFEST updates. Range-conflict checks must account for files being ingested but not fully installed, otherwise compaction can pick a conflicting output level/range.
- L0 files from ingestion can have sequence/file-order relationships that differ from flushed files. Intra-L0 compaction must not reorder visibility so an older ingested value hides a newer memtable flush.
- Blob GC behavior changes when `enable_blob_files` is dynamically turned off: collected values are inlined instead of rewritten to blob files. Stats and file-retention assertions rely on this distinction.
- Checksum handoff is filesystem-dependent. Tests skip memory/encrypted environments because the required low-level file-system behavior is not available.
- FIFO temperature aging depends on mock time and file creation metadata. Trivial-copy and full-compaction paths must both preserve the intended new temperature and not misattribute non-SST files.
- Record-count verification uses internal sync points to simulate impossible table-builder/iterator bugs. The returned corruption text is part of the test signal.
- Failure cleanup around compaction output verification, MANIFEST install, and atomic flush install is subtle because output files can be present in table cache without being reachable from any live `Version`. Faulted metadata scans remove the usual cleanup backstop, exposing leaks.
- `CompactionFilterLargeValueRejected` requires very large memory because it creates near-4GB values; it is guarded by `test::HasBigMem()`.

## Test Signals

- Successful value reads after compaction are the dominant end-to-end signal: tests repeatedly assert `Get()` returns the latest value after direct-I/O stress, L0 misordering scenarios, blob GC, refit conflicts, read-triggered compaction, and output verification.
- Exact file-layout assertions such as `"0,0,1"`, `"1,0,1"`, `"0,5"`, or per-level file counts validate compaction placement, trivial moves, dynamic level draining, and bottommost/manual behavior.
- `Status` assertions distinguish expected paths: `OK`, `Incomplete` for disabled/cancelled manual compactions, `Aborted` or `NotSupported` for range/refit conflicts, `IOError` for injected file/blob failures, `Corruption` for consistency/record-count/blob-index/output-checksum failures, and fatal/unrecoverable severities for checksum handoff.
- Sync-point callback booleans and counters prove specific picker/compaction paths were hit, including intra-L0 level/universal/FIFO picking, round-robin subcompaction planning, read-triggered compaction, periodic compaction, and compaction release during MANIFEST grouping.
- Internal stats checks cover blob bytes read/written, table bytes written, output file counts, subcompaction completion count, per-temperature read counters, and newest-key-time propagation.
- Fault-injection tests verify retry and cleanup behavior by running the same compaction again after a retryable read error, closing the DB after failed output install, or disabling injected faults before close.
- Reopen checks validate persistence for round-robin compact cursors, dynamic-level migration MANIFEST edits, FIFO temperature metadata, blob files, and data visibility after option changes.

## Unresolved Cross-Chunk References

This range assumes fixture definitions, helper methods, earlier compaction tests, and several parameterized fixture classes were defined before line 7098. The final per-file research should connect this chunk's regression tests with earlier chunks that define `DBCompactionTest`, helper constants such as `KNumKeysByGenerateNewFile`, parameterized fixture setup, and earlier coverage for basic compaction picking, universal/FIFO behavior, snapshots, and manual compaction fundamentals.
