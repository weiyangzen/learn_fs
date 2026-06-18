# subset-b-008574 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family_test.cc -->
# sources/storage-engines/rocksdb/db/column_family_test.cc

## Purpose

This file is a large GoogleTest suite for RocksDB column-family behavior. It exercises the public `DB`/`ColumnFamilyHandle` APIs and several `DBImpl`/`ColumnFamilyData` internals across create/drop/reopen flows, WAL recovery, flushing, compaction scheduling, write stalls, per-column-family paths, option validation, and user-defined timestamp retention. The suite is parameterized over block-based table format versions so many scenarios run against both the default and latest table format.

## Important APIs, Types, and Helpers

- `EnvCounter` extends `SpecialEnv` and counts `NewWritableFile()` calls. Tests use it to detect unexpected WAL/SST/OPTIONS file creation.
- `ColumnFamilyTestBase` owns the test DB lifecycle, `EnvCounter`, `DBOptions`, `ColumnFamilyOptions`, open handles, and helper methods.
- Helper methods include `Open`, `TryOpen`, `OpenReadOnly`, `Reopen`, `Close`, `Destroy`, `CreateColumnFamilies`, `DropColumnFamilies`, `Put`, `Merge`, `Flush`, `CompactAll`, `Compact`, `Get`, `PutRandomData`, `WaitForFlush`, `WaitForCompaction`, `FilesPerLevel`, `CountLiveFiles`, `CountLiveLogFiles`, and `RecalculateWriteStallConditions`.
- `FlushEmptyCFTestWithParam` adds a `(format_version, allow_2pc)` parameter pair to validate WAL/min-log behavior with and without two-phase commit.
- `ColumnFamilyRetainUDTTest` configures a timestamp-aware comparator with `persist_user_defined_timestamps=false` and wraps timestamped `Put`/`Get` plus `CheckEffectiveCutoffTime`.
- `AutoFlushRetainUDTTest` and `ManualFlushSkipRetainUDTTest` specialize UDT-retention tests for automatic and manual flush/compaction behavior.
- Local comparators (`TestComparator`, `TestTsComparator`) validate comparator plumbing and timestamp-size restrictions.

## Control Flow and State Behavior

The fixture creates an isolated per-thread DB path, destroys prior state in `SetUp`, and destroys live handles/DB contents in the destructor. Most tests follow the pattern `Open -> create CFs -> write/flush/compact/drop -> Reopen or Close -> assert recovered state`. This makes manifest state, WAL state, and live-file state explicit test outputs.

Column-family identity and persistence tests cover:

- `DontReuseColumnFamilyID`: creates and drops CFs across reopen and `WriteSnapshot()` boundaries to ensure dropped IDs are not reused.
- `AddDrop`, `BulkAddDrop`, `DropTest`, and `CreateDropAndDestroy*`: validate create/drop APIs, handle destruction, list output, file cleanup, and behavior when file deletions are disabled.
- `EmptyNameRejected`: verifies empty CF names are rejected by single and bulk creation APIs because empty string is reserved in RocksDB metadata and older behavior lost data after reopen.
- `CreateMissingColumnFamilies`: checks `create_missing_column_families` is required, works for new and existing DBs, and avoids quadratic OPTIONS-file writes.

Recovery and WAL-oriented tests cover:

- `FlushEmptyCFTest`/`FlushEmptyCFTest2`: use `FaultInjectionTestEnv` to freeze file-system state after flush/WAL transitions, then reopen to verify sequence IDs and min-log-number metadata preserve data.
- `IgnoreRecoveredLog`: copies WALs, recovers, restores old WAL copies, and reopens again to ensure already recovered logs are ignored rather than replayed twice.
- `CrashAfterFlush`: simulates unsynced data loss after a flush and verifies cross-CF write-batch atomicity after recovery.
- `LogDeletionTest`, `DifferentWriteBufferSizes`, `FlushStaleColumnFamilies`, `FlushCloseWALFiles`, `IteratorCloseWALFile*`, `ForwardIteratorCloseWALFile`, and `LogSyncConflictFlush`: assert WAL retention, closing, deletion, and sync/flush interactions under multiple CFs, immutable memtables, and iterator-held super versions.

Compaction and flush scheduling tests use `SyncPoint`, background thread blocking, and file-per-level assertions to validate concurrency:

- `DifferentCompactionStyles` sets universal compaction for one CF and leveled compaction for another, then checks separate compaction outcomes.
- `MultipleManualCompactions`, `AutomaticAndManualCompactions`, `ManualAndAutomaticCompactions`, `SameCFManualManualCompactions`, `SameCFManualAutomaticCompactions`, `SameCFManualAutomaticCompactionsLevel`, and `SameCFAutomaticManualCompactions` orchestrate manual and automatic compactions across the same or different CFs. They verify conflict handling, no data loss, and expected level layouts.
- Write stall tests manipulate `VersionStorageInfo` counters under the DB mutex and call `ColumnFamilyData::RecalculateWriteStallConditions()` to assert delayed-write rate, stopped-write state, and allowed background compaction parallelism.
- `CompactionSpeedupForCompactionDebt` and `CompactionSpeedupForMarkedFiles` test the logic that increases background compaction capacity based on compaction debt or table-property `NeedCompact()` signals.

Iterator/read tests validate API guarantees:

- `NewIteratorsTest` tests multi-CF iterator creation with normal and tailing iterators.
- `ReadOnlyDBTest` confirms read-only open requires default CF and cannot open dropped CFs.
- `ReadDroppedColumnFamily`, `LiveIteratorWithDroppedColumnFamily`, and `FlushAndDropRaceCondition` assert handles/iterators can continue reading dropped CF data until handles are destroyed.

Option and path tests cover:

- `SanitizeCfOptions`: checks trigger ordering, minimum levels, and arena block size adjustment.
- `ValidateBlobGCCutoff`, `ValidateBlobGCForceThreshold`, and `ValidateMemtableKVChecksumOption`: validate option bounds and supported values.
- `DefaultCfPathsTest` and `MultipleCFPathsTest`: verify SSTs are written to CF-specific paths or DB paths as configured and remain readable after reopen.

UDT-retention tests cover:

- Feature incompatibilities with non-u64 timestamp comparators, atomic flush, and concurrent memtable writes.
- Automatic flush behavior when `full_history_ts_low` is unset, all keys are expired, not all keys are expired but write stall is possible, or a flush should be rescheduled.
- Manual flush and manual compaction deliberately skip the auto-retention reschedule path while still advancing the effective cutoff after garbage collection.
- Flush GC removes stale point and range-deletion entries and updates table properties.
- External SST ingestion in UDT mode rejects overlapping files and does not advance cutoff for non-overlapping ingestion.
- Concurrent manual flush/compaction operations monotonically advance the effective cutoff.

## Dependencies and Integration Points

The file integrates with `db/db_impl/db_impl.h`, `db/db_test_util.h`, `options/options_parser.h`, `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `WriteController`, `PeriodicTaskScheduler`, `FaultInjectionTestEnv`, `SpecialEnv`, `SyncPoint`, custom comparators, merge operators, table property collectors, external SST ingestion, and RocksDB public DB/iterator/listener APIs.

## Risks and Edge Cases

- Many tests rely on precise background timing. `SyncPoint` dependencies and sleeping background tasks reduce flakiness but can deadlock if production sync-point labels change.
- WAL counting uses `GetSortedWalFiles()` with retries because concurrent deletion can make the API flaky.
- Some tests use disabled cases (`DISABLED_CreateAndDropRace`, `DISABLED_LogTruncationTest`) documenting races or recovery scenarios that are currently hard to run reliably.
- Internal API use (`TEST_*`, direct `ColumnFamilyData`/`VersionStorageInfo` mutation) gives good coverage but couples the suite tightly to implementation structure.
- UDT behavior depends on timestamp comparator format and on subtle interactions among flush scheduling, write-stall avoidance, and cutoff advancement.

## Test Signals

This file is itself a test target. Strong signals include reopen/recovery checks, live file/WAL counts, compaction level layouts, explicit status class assertions, table property assertions, sync-point-controlled races, and iteration count/value checks. It provides regression coverage for manifest persistence, WAL lifecycle, dropped-CF handle semantics, compaction scheduler conflicts, write-stall thresholds, and UDT-retention garbage collection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/column_family_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compact_files_test.cc -->
# sources/storage-engines/rocksdb/db/compact_files_test.cc

## Purpose

This GoogleTest file validates the `DB::CompactFiles()` API. It focuses on manual compaction of explicitly named SST files, including conflict handling with background compaction, output-level validation, obsolete input cleanup, compression option selection, compaction job reporting, pending-file capture, and the optimized trivial-move path.

## Important APIs, Types, and Helpers

- `CompactFilesTest` is a minimal fixture holding a per-thread DB path and default environment.
- `FlushedFileCollector` is an `EventListener` that records `FlushJobInfo::file_path` values under a mutex so tests can pass exact SST filenames to `CompactFiles()`.
- `MakeKey(prefix, index)` creates zero-padded test keys for stable range construction in trivial-move tests.
- Tests use `DB::CompactFiles(CompactionOptions, files, output_level, output_path_id, output_file_name, CompactionJobInfo*)`, `GetColumnFamilyMetaData()`, `GetPropertiesOfAllTables()`, `DBImpl::TEST_WaitForBackgroundWork()`, `DBImpl::TEST_WaitForCompact()`, and `SyncPoint`.

## Control Flow and State Behavior

Most tests disable or control background compaction, write data, flush one or more L0 files, collect their paths, and then invoke `CompactFiles()` to move or merge those files to a target level. The observable state is level metadata, deleted input files, compression/table properties, job-info fields, and data readability.

Important cases:

- `L0ConflictsFiles` creates enough L0 files to start background compaction, then uses sync points so a `CompactFiles()` L0 compaction is in progress when the background compaction checks for conflicts. It validates the background job notices the L0 conflict and avoids overlapping work.
- `MultipleLevel` creates files in L0, L3, L4, and L5, then attempts compaction of a mixed file set. Output levels below the highest input level are rejected with `InvalidArgument`; output to L5 succeeds even while another thread flushes new files.
- `ObsoleteFiles` uses `kCompactionStyleNone`, compacts collected L0 files to L1, waits for compaction cleanup, and verifies the old input filenames no longer exist.
- `NotCutOutputOnLevel0` sets a tiny `max_compaction_bytes` and compacts file sets back to L0, validating output cutting is not applied in an unsafe way for L0.
- `CapturingPendingFiles` starts `CompactFiles()` while another flush creates a new file, then reopens the DB to ensure pending-output capture and obsolete-file handling do not lose needed files.
- `CompactionFilterWithGetSv` uses a compaction filter that calls `DB::Get()` to ensure `CompactFiles()` can run filters that acquire super versions safely.
- `SentinelCompressionType` passes `kDisableCompressionOption` and checks that output compression comes from CF compression settings, using table properties to verify the encoded compression name.
- `CompressionWithBlockAlign` validates block-aligned tables reject incompatible explicit compression but accept the sentinel compression option.
- `GetCompactionJobInfo` checks `CompactionJobInfo` fields including base input level, CF id/name, reason, compression, output level, and status.
- `TrivialMoveNonOverlappingFiles` first compacts non-overlapping L0 files to L1, then moves one non-overlapping L1 file to L6 with `allow_trivial_move=true`. A sync-point callback confirms the trivial-move path, and metadata verifies the same file number moved without rewriting.
- `TrivialMoveBlockedByOverlap` creates an existing L6 range and an overlapping L1 file, then verifies `allow_trivial_move=true` falls back to full compaction when overlap exists and that updated values are visible.

## Dependencies and Integration Points

The test integrates public `DB` APIs with `DBImpl` test hooks, `EventListener` flush callbacks, `ColumnFamilyMetaData`, `TablePropertiesCollection`, compression capability helpers (`Zlib_Supported`, `Snappy_Supported`), block-based table options, and `SyncPoint` labels in compaction code. It also exercises `CompactionOptions::allow_trivial_move`, `compression`, and output-level semantics.

## Risks and Edge Cases

- Filename capture depends on listener callbacks being complete; tests call `TEST_WaitForBackgroundWork()` before consuming listener state to avoid races.
- Compression tests are conditional on library support and can skip when zlib or snappy is unavailable.
- Trivial move correctness is sensitive to file-range overlap detection and level numbering. A bad implementation could preserve metadata movement but break snapshot or overlap invariants.
- `CompactFiles()` accepts user-supplied filenames, so stale, pending, or concurrently obsolete files are an important safety boundary.

## Test Signals

This file is a direct test suite. It signals correctness through `Status` checks, metadata level counts, missing obsolete input files, table compression properties, job-info fields, sync-point callbacks, DB reopen success, and final point reads after trivial or non-trivial compactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compact_files_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/clipping_iterator.h -->
# sources/storage-engines/rocksdb/db/compaction/clipping_iterator.h

## Purpose

`ClippingIterator` is an `InternalIterator` wrapper that restricts another internal iterator to an optional half-open key range `[start, end)`. It is used when compaction or table iteration needs a local range view even if the underlying iterator may not enforce the same bounds.

## Important APIs and Types

- Constructor: `ClippingIterator(InternalIterator* iter, const Slice* start, const Slice* end, const CompareInterface* cmp)`.
- Standard iterator methods: `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `NextAndGetResult`, `Prev`, `key`, `user_key`, `value`, `status`, and `PrepareValue`.
- Bound-related methods: `MayBeOutOfLowerBound()` always returns false for valid clipped positions; `UpperBoundCheckResult()` always reports `kInbound` for valid clipped positions.
- Delegated methods: `SetPinnedItersMgr`, `IsKeyPinned`, `IsValuePinned`, `GetProperty`, and `IsDeleteRangeSentinelKey`.

## Control Flow

The constructor asserts non-null iterator/comparator and valid bound ordering, then initializes `valid_` by checking the current position against both bounds.

Forward operations:

- `SeekToFirst()` seeks to `start` when a lower bound exists, otherwise to the underlying first key, then enforces the upper bound.
- `Seek(target)` seeks to `start` if the target is below the lower bound, returns invalid immediately if the target is at or beyond `end`, otherwise seeks to target and enforces the upper bound.
- `Next()` and `NextAndGetResult()` advance the underlying iterator and invalidate the wrapper at `end`.

Reverse operations:

- `SeekToLast()` uses `SeekForPrev(end)` when an upper bound exists and steps back if the underlying iterator lands exactly on the exclusive end key.
- `SeekForPrev(target)` returns invalid when target is below `start`, maps targets at or past `end` to the last key strictly below `end`, otherwise delegates to `SeekForPrev(target)`.
- `Prev()` steps backward and enforces the lower bound.

The wrapper uses `UpdateValid()`, `EnforceUpperBound()`, `EnforceLowerBound()`, and `AssertBounds()` to keep `valid_` independent from the wrapped iterator's raw validity.

## State and Persistence Behavior

`ClippingIterator` owns no persistent data and does not own the wrapped iterator. It stores raw pointers to the iterator, optional `Slice` bounds, comparator, and a local `valid_` flag. Bound slices must outlive the wrapper. It has no disk, manifest, or table-state persistence behavior.

## Dependencies and Integration Points

The class depends on `rocksdb/comparator.h`, `table/internal_iterator.h`, `Slice`, `CompareInterface`, and `InternalIterator` bound-check APIs. It benefits from underlying iterators that already report `MayBeOutOfLowerBound()` and `UpperBoundCheckResult()`: when those are definitive, it avoids redundant comparisons; when they are unknown, it compares keys itself.

## Risks and Edge Cases

- The wrapper assumes bounds and comparator remain valid for its lifetime.
- `SeekToLast()` and `SeekForPrev()` must handle the exclusive upper bound carefully when a key equals `end`.
- `NextAndGetResult()` must rewrite returned `bound_check_result` to `kInbound` so callers can trust the clipped iterator's public contract.
- If the underlying iterator misreports bound checks, `ClippingIterator` can incorrectly trust inbound/out-of-bound results.
- Methods assert `valid_` before key/value/pinning operations, matching normal `InternalIterator` contracts.

## Test Signals

Coverage comes from `clipping_iterator_test.cc`, which parameterizes over plain and bounds-checking vector iterators plus many start/end windows. The test checks forward, backward, seek, seek-for-prev, `NextAndGetResult()`, lower-bound reporting, and upper-bound reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/clipping_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/clipping_iterator_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/clipping_iterator_test.cc

## Purpose

This file tests `ClippingIterator`, the range-limiting wrapper over `InternalIterator`. It validates that the wrapper returns exactly the intersection of the underlying iterator data and the clipping window `[start, end)`, for both underlying iterators that perform their own bound checks and those that do not.

## Important APIs and Types

- `BoundsCheckingVectorIterator` extends `VectorIterator` and overrides `NextAndGetResult`, `MayBeOutOfLowerBound`, and `UpperBoundCheckResult` to simulate an iterator with native bound-check knowledge.
- `ClippingIteratorTest` is parameterized by `(use_bounds_checking_vec_it, clip_start_idx, clip_window_size)`.
- The test uses `BytewiseComparator`, `VectorIterator`, `InternalIterator::IterateResult`, and all major `ClippingIterator` navigation APIs.

## Control Flow

`TEST_P(ClippingIteratorTest, Clip)` defines ten ordered keys but only supplies `key1`, `key2`, and `key3` as underlying data. Test parameters choose a clipping start index in `[0,4]` and a window size in `[0,5]`, giving an end index of `start + size`.

The expected returned range is computed as:

- `data_start_idx = max(clip_start_idx, 1)`
- `data_end_idx = min(clip_end_idx, 4)`

If the expected range is empty, the test asserts `SeekToFirst`, `SeekToLast`, every `Seek`, and every `SeekForPrev` are invalid.

If non-empty, the test:

- Seeks to first and iterates forward with `Next()`.
- Repeats forward iteration with `NextAndGetResult()`.
- Seeks to last and iterates backward with `Prev()`.
- Calls `Seek()` and `SeekForPrev()` for every key in the ten-key universe and checks exact landing behavior.
- Verifies `MayBeOutOfLowerBound()` is false and `UpperBoundCheckResult()` is `kInbound` for every valid clipped position.

The instantiation combines both iterator modes, five starts, and six window sizes, covering empty, partial, exact, and beyond-data windows.

## State and Persistence Behavior

The test is entirely in-memory. It owns vectors of keys/values, an optional `BoundsCheckingVectorIterator`, and a `ClippingIterator` wrapping that iterator. It does not open a DB or persist files.

## Dependencies and Integration Points

The file depends on `db/compaction/clipping_iterator.h`, `db/dbformat.h`, `rocksdb/comparator.h`, `test_util/testharness.h`, `test_util/testutil.h`, and `util/vector_iterator.h`. It directly validates the `InternalIterator` bound-check contract used by compaction and table iteration paths.

## Risks and Edge Cases

- The reverse iteration loop uses unsigned `size_t`; it relies on the loop body and post-loop invalidation pattern being reached only when `data_start_idx < data_end_idx`. Changes should be careful around underflow.
- The test covers optional bounds through computed windows, but it always constructs both `start` and `end`; null-bound cases are indirectly covered by code inspection rather than this matrix.
- Correctness depends on `BytewiseComparator` ordering matching the constructed key sequence.

## Test Signals

The suite is the direct regression signal for clipping semantics. It verifies exact keys and values, invalidation at bounds, bound-check return values, `NextAndGetResult()` behavior, and parity between bounds-aware and plain underlying iterators.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/clipping_iterator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction.cc

## Purpose

This file implements the `Compaction` metadata object declared in `compaction.h`. A `Compaction` captures the selected input files, output level/path/compression/temperature decisions, snapshot and range-deletion filtering context, per-key placement metadata, blob GC settings, and helper operations used by compaction jobs, pickers, and version edits.

## Important Functions and Methods

- `sstableKeyCompare(...)`: compares SST boundary internal keys by user key without timestamp, with special ordering for range tombstone sentinel footers.
- `TotalFileSize(files)`: sums file sizes until a null entry.
- `Compaction::FinalizeInputInfo(Version*)`: attaches the owning `Version`/`ColumnFamilyData`, refs both, and sets the `VersionEdit` CF id.
- `GetBoundaryKeys()` and `GetBoundaryInternalKeys()`: compute overall user/internal key ranges for inputs, with special handling for L0 overlap.
- `PopulateWithAtomicBoundaries()`: computes atomic compaction unit boundaries for non-L0 neighboring files whose boundary user keys overlap.
- `IsBottommostLevel()` and `IsFullCompaction()`: derive bottommost/full-compaction flags from `VersionStorageInfo`.
- `InitInputTableProperties()`: lazily loads table properties for all input files.
- Constructor: initializes immutable compaction metadata, marks input files as being compacted, populates input-level briefs, computes output split key, and computes proximal output range.
- `PopulateProximalLevelOutputRange()`, `SupportsPerKeyPlacement()`, `GetProximalLevel()`, `OverlapProximalLevelOutputRange()`, `TEST_AssertWithinProximalLevelOutputRange()`, and `EvaluateProximalLevel()`: implement metadata for per-key placement when `preclude_last_level_data_seconds` allows some output to go to the proximal level.
- `IsTrivialMove()`: determines whether compaction can be represented as file movement rather than rewrite.
- `AddInputDeletions()`, `ReleaseCompactionFiles()`, `ResetNextCompactionIndex()`, `Summary()`, `InputLevelSummary()`, and `CalculateTotalInputSize()`: support version edits, picker state, logging, and accounting.
- `KeyNotExistsBeyondOutputLevel()` and `KeyRangeNotExistsBeyondOutputLevel()`: provide deletion/drop optimizations when no lower-level overlap exists.
- `OutputFilePreallocationSize()`, `CreateCompactionFilter()`, `CreateSstPartitioner()`, `IsOutputLevelEmpty()`, `ShouldFormSubcompactions()`, `DoesInputReferenceBlobFiles()`, `MaxInputFileNewestKeyTime()`, `MinInputFileOldestAncesterTime()`, `MinInputFileEpochNumber()`, and `GetOutputTemperature()`: expose compaction-job decisions and statistics inputs.
- `FilterInputsForCompactionIterator()`: excludes non-start-level input files completely shadowed by a standalone range deletion file when snapshot conditions prove it safe.

## Control Flow

Construction is the central control point:

1. Store levels, target sizes, options, grandparents, snapshot state, reason, trim timestamp, blob GC policy, and input files.
2. Call `PopulateWithAtomicBoundaries()` before storing inputs, so each non-L0 input file can carry the atomic range needed by range tombstone aggregation.
3. Compute `bottommost_level_` unless the reason is external SST ingestion or refit level.
4. Compute full-compaction/manual-compaction flags and blob GC enablement/cutoff.
5. Evaluate proximal level support. It is only possible for leveled/universal compactions outputting to the last level, with a positive `preclude_last_level_data_seconds`, and with a valid proximal level greater than L0.
6. Mark all input files `being_compacted=true`.
7. Determine max subcompactions and max output file size.
8. Build `LevelFilesBrief` arrays. If `earliest_snapshot_` is set, run `FilterInputsForCompactionIterator()` to omit files shadowed by a standalone range tombstone; otherwise include all input files.
9. Compute smallest/largest user keys and an optional output split cursor for round-robin leveled compaction.
10. Populate proximal output key range and sequence-number restrictions.

Destruction unreferences `input_version_` and `cfd_`. Actual release of `being_compacted` flags is done through `ReleaseCompactionFiles(status)`, which also informs the column family's compaction picker.

Trivial move logic rejects unsafe cases: overlapping L0 inputs, manual compactions with filters, same-level compactions, temperature-change compactions, compression/path mismatches, excessive grandparent overlap, disallowing SST partitioner decisions, and any per-key-placement compaction. Universal compaction has a separate `allow_trivial_move` path using `is_trivial_move_`.

Range-existence checks walk lower levels using monotonic `level_ptrs`, making repeated calls efficient during compaction iteration. They account for user-defined timestamps by using `CompareWithoutTimestamp()` where exact timestamp ordering would be too strict.

## State and Persistence Behavior

`Compaction` itself is in-memory metadata, but it mutates important live state:

- Input `FileMetaData::being_compacted` flags are set in the constructor and cleared in `ReleaseCompactionFiles()`.
- `edit_` records file deletions and is tagged with the column family id once `FinalizeInputInfo()` is called.
- `input_version_` and `cfd_` are reference-counted while the compaction object is active.
- Lazily loaded `input_table_properties_` and job-filled `output_table_properties_` are stored in memory and feed filters, listeners, and reports.
- Blob GC, output temperature, output path, compression, and proximal-level flags affect the physical output files written by compaction jobs, although the file does not write SSTs itself.

## Dependencies and Integration Points

This implementation depends on `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `VersionEdit`, `FileMetaData`, internal key comparators, table property loading, `CompactionFilterFactory`, `SstPartitionerFactory`, `MutableCFOptions`, `ImmutableOptions`, blob-file metadata, `SnapshotChecker`, and `SyncPoint` test hooks. It is consumed by compaction pickers, `CompactionJob`, flush/compaction scheduling, listener notification code, and deletion/range-tombstone optimization paths.

## Risks and Edge Cases

- `sstableKeyCompare()` must distinguish range tombstone sentinel boundaries without treating adjacent SSTs as overlapping incorrectly.
- Failing to call `ReleaseCompactionFiles()` would leave input files marked as compacting and block future picks.
- `FilterInputsForCompactionIterator()` is intentionally limited: it requires no user-defined timestamp, a standalone range-deletion file, safe snapshot visibility, and does not support older-L0-by-newer-L0 filtering.
- Proximal-level placement has explicit FIXME notes: some ranges may disable proximal output because smallest/largest proximal keys are not populated, and `proximal_output_range_type_` is not fully used.
- Trivial move must consider filters, path id, compression, grandparent overlap, partitioner constraints, L0 overlap, temperature changes, and per-key placement.
- Lazy table property loading logs and clears all cached properties on the first read failure.

## Test Signals

Relevant test coverage appears across compaction and DB tests, including compact-files trivial-move tests, column-family manual/automatic compaction conflict tests, write-stall and speedup tests, range-deletion/UDT flush and compaction tests, and sync-point hooks such as `Compaction::InputCompressionMatchesOutput:*` and `Compaction::SupportsPerKeyPlacement:Enabled`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction.h

## Purpose

This header declares the core `Compaction` metadata class and related helper structures for RocksDB compaction. It defines how selected input files, output placement, compression, snapshots, deletion optimizations, table properties, blob GC, temperature, subcompaction eligibility, and per-key placement metadata are represented for a compaction job.

## Important APIs and Types

- `sstableKeyCompare(...)`: overload set for comparing SST boundary keys using user keys and range tombstone sentinel awareness.
- `AtomicCompactionUnitBoundary`: stores smallest/largest internal-key pointers spanning one or more neighboring SSTs that must be treated atomically for range tombstone truncation.
- `CompactionInputFiles`: groups input files by physical level and stores per-file atomic boundaries. Provides `empty`, `size`, `clear`, and index access.
- `Compaction`: non-copyable class encapsulating all compaction metadata.
- `Compaction::ProximalOutputRangeType`: classifies whether per-key placement to the proximal level is unsupported, full-range, non-last-level range, or disabled.
- `PerKeyPlacementContext`: debug-only helper carrying key/value/seqno and an output flag for per-key placement tests.
- `TotalFileSize(files)`: helper declaration for summing input sizes.

## Key `Compaction` Surface

Selection and file access:

- `level`, `start_level`, `output_level`, `num_input_levels`, `num_input_files`, `input`, `inputs`, `input_levels`, `filtered_input_levels`, and `boundaries`.
- `input_version`, `column_family_data`, and `edit`.

Output configuration:

- `max_output_file_size`, `target_output_file_size`, `output_compression`, `output_compression_opts`, `output_path_id`, `output_temperature_override` through `GetOutputTemperature`, `max_compaction_bytes`, and `max_subcompactions`.
- `GetOutputSplitKey` supports round-robin compaction output splitting.
- `OutputFilePreallocationSize()` estimates file preallocation.

Optimization and lifecycle:

- `IsTrivialMove`, `deletion_compaction`, `AddInputDeletions`, `ReleaseCompactionFiles`, `ResetNextCompactionIndex`, `MarkFilesBeingCompacted`, `CalculateTotalInputSize`, `InputLevelSummary`, and `Summary`.
- `KeyNotExistsBeyondOutputLevel` and `KeyRangeNotExistsBeyondOutputLevel` support deletion/range tombstone dropping.
- `IsOutputLevelEmpty`, `ShouldFormSubcompactions`, and `DoesInputReferenceBlobFiles`.

Filtering, factories, and properties:

- `CreateCompactionFilter`, `CreateSstPartitioner`, `GetOrInitInputTableProperties`, `GetInputTableProperties`, `SetOutputTableProperties`, and `GetOutputTableProperties`.

Compaction classification and telemetry:

- `score`, `bottommost_level`, `is_last_level`, `is_full_compaction`, `is_manual_compaction`, `trim_ts`, `compaction_reason`, `grandparents`, `MaxInputFileNewestKeyTime`, `MinInputFileOldestAncesterTime`, and `MinInputFileEpochNumber`.
- Listener state guards: `SetNotifyOnCompactionCompleted`, `ShouldNotifyOnCompactionCompleted`, `SetNotifyOnCompactionPreCommitCalled`, and `WasNotifyOnCompactionPreCommitCalled`.

Blob GC and per-key placement:

- `enable_blob_garbage_collection`, `blob_garbage_collection_age_cutoff`, `SupportsPerKeyPlacement`, `GetProximalLevel`, `OverlapProximalLevelOutputRange`, `TEST_AssertWithinProximalLevelOutputRange`, `EvaluateProximalLevel`, `GetKeepInLastLevelThroughSeqno`, and `OutputToNonZeroMaxOutputLevel`.

## State and Persistence Behavior

The header exposes in-memory state that drives persistent LSM changes. `Compaction` owns input metadata vectors and cached table-property maps, refs a `Version`/`ColumnFamilyData` after finalization, and owns a `VersionEdit` used to remove input files from the manifest. It stores output level/path/compression/temperature and blob GC decisions that determine newly written SST metadata. It also tracks transient flags for listener notification and file `being_compacted` lifecycle.

## Dependencies and Integration Points

The class is tightly integrated with `db/version_set.h`, `db/snapshot_checker.h`, `options/cf_options.h`, `memory/arena.h`, `rocksdb/sst_partitioner.h`, `ColumnFamilyData`, `VersionStorageInfo`, `CompactionFilter`, `TablePropertiesCollection`, internal key format, and RocksDB option structures. It is a central bridge between compaction picker decisions and compaction job execution.

## Risks and Edge Cases

- The constructor takes many parameters; callers must keep level ordering, output level, path id, compression, snapshot checker, and reason consistent.
- The header makes clear that `GetOrInitInputTableProperties()` may open/read table files and must not be called under the DB mutex.
- `filtered_input_levels()` is meaningful only when non-start-level files are filtered due to standalone range tombstones.
- Per-key placement is still guarded by internal checks and debug-only helpers, with output range semantics split across enum state, key boundaries, and keep-in-last-level sequence numbers.
- `MarkFilesBeingCompacted()` asserts the target state differs, so double marking or double release is a correctness bug.

## Test Signals

Tests reach this API through DB compaction jobs, compact-files tests, column-family compaction scheduling tests, UDT/range-deletion tests, and debug sync points. Header-specific helper behavior is also exercised by internal unit tests that call `TEST_IsBottommostLevel`, proximal placement hooks, trivial-move decisions, and table-property/filter/partitioner paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iteration_stats.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_iteration_stats.h

## Purpose

This header defines `CompactionIterationStats`, a plain statistics accumulator used while iterating compaction input records. It groups counters for dropped records, input records/bytes, SingleDelete diagnostics, blob reads/relocations, and TimedPut preferred-sequence-number handling.

## Important Fields

Drop/filter counters:

- `num_record_drop_user`: records removed by user compaction filter decisions, excluding `kRemoveAndSkipUntil` skipped records.
- `num_record_drop_hidden`: records hidden by newer versions.
- `num_record_drop_obsolete`: obsolete records dropped.
- `num_record_drop_range_del`: point records dropped by range deletion.
- `num_range_del_drop_obsolete`: obsolete range deletions dropped.
- `num_optimized_del_drop_obsolete`: deletions obsoleted before bottom level due to file-gap optimization.
- `total_filter_time`: accumulated compaction filter time.

Input counters:

- `num_input_records`, `num_input_deletion_records`, `num_input_corrupt_records`.
- `total_input_raw_key_bytes`, `total_input_raw_value_bytes`.

Diagnostics:

- `num_single_del_fallthru` and `num_single_del_mismatch` track exceptional SingleDelete behavior.
- `num_blobs_read`, `total_blob_bytes_read`, `num_blobs_relocated`, `total_blob_bytes_relocated` track blob handling during compaction.
- `num_input_timed_put_records` and `num_timed_put_swap_preferred_seqno` track `kTypeValuePreferredSeqno` handling.

## Control Flow and State Behavior

The struct has no methods and no constructor logic beyond in-class zero initialization. Compaction iterator/job code can allocate it by value and increment fields as records are consumed, filtered, dropped, or rewritten. It has no persistence behavior on its own; callers decide how to export the counters into internal stats, event listeners, logs, or job info.

## Dependencies and Integration Points

The header only includes `<cstdint>` and `rocksdb/rocksdb_namespace.h`. It is intentionally lightweight so compaction iterator code can include it without pulling in DB internals. Its counters correspond to compaction filter decisions, merge/input scanning, range deletion handling, blob-file processing, SingleDelete semantics, and TimedPut record handling.

## Risks and Edge Cases

- A TODO notes input stats are incomplete because they do not include everything consumed by `MergeHelper`.
- Counter type choices vary between signed `int64_t` drop counters and unsigned `uint64_t` input/blob diagnostics; callers should avoid underflow and preserve semantics when aggregating.
- Because the struct is passive, missing increments in compaction code are easy to introduce and hard to catch without targeted stats tests.

## Test Signals

This header has no direct tests in the researched set. Indirect signals come from compaction tests and any assertions on compaction statistics, job info, blob GC counters, SingleDelete diagnostics, or TimedPut behavior elsewhere in RocksDB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_iteration_stats.h -->
