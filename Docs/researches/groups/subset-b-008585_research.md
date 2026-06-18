# subset-b-008585 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_clip_test.cc -->
# sources/storage-engines/rocksdb/db/db_clip_test.cc

## Purpose
`db_clip_test.cc` is a focused RocksDB regression test for `DB::ClipColumnFamily()`. It verifies that clipping a column family to a user-key half-open range removes all keys outside the range, preserves keys inside the range, and rewrites/retains live table metadata so every remaining file is fully contained by the clipped bounds. The scenario covers both a simple L0-only layout and a mixed-level layout after explicit compaction and new overlapping flushes.

## Important APIs, Types, And Functions
The file defines `DBClipTest`, a `DBTestBase` fixture using the database name `db_clip_test` and `env_do_fsync=true`. The only test case, `TestClipRange`, uses `Options`, `Random`, `Put`, `Flush`, `FilesPerLevel`, `ClipColumnFamily`, `Get`, `GetLiveFilesMetaData`, `CompactRange`, and the internal test helper `TEST_CompactRange`.

The key API under test is `db_->ClipColumnFamily(db_->DefaultColumnFamily(), begin_key, end_key)`. The test asserts the clipped range semantics with `ReadOptions` and direct `Get` calls, then validates physical file bounds using `LiveFileMetaData::smallestkey` and `LiveFileMetaData::largestkey`. It uses `Key(int)` from `DBTestBase`, which produces comparator-compatible encoded test keys.

## Control Flow
The test opens a DB with three levels, large write buffers, disabled automatic compaction, a level multiplier of two, and statistics enabled. It writes ten flushed L0 files covering logical ranges `[0, 100)`, `[100, 200)`, through `[900, 1000)`, storing the generated 10 KB values in a `std::map` for later verification.

The first clip keeps `[Key(251), Key(751))`. The test confirms keys `0..250` and `751..999` are not found, keys `251..750` return their original values, and all live files have smallest/largest keys within the clipped interval. It then performs a manual compact range with `change_level=true` and `target_level=2`, expecting the layout `"0,0,3"`.

The test next reintroduces even hundred-blocks into L0, compacts them to L1 with `TEST_CompactRange(0, ...)`, then reintroduces odd hundred-blocks into L0. With files now spread across L0, L1, and L2, it clips a wider `[Key(222), Key(888))` interval and repeats the logical and metadata checks.

## State And Persistence Behavior
The test models persistent table-file state rather than only point-lookups. `Flush()` creates physical SST files, `CompactRange()` moves and rewrites those files across levels, and `ClipColumnFamily()` must leave the column family in a state where out-of-range key versions are gone from reads and no live file metadata advertises a range outside the requested clip.

The two clip phases exercise different persistence shapes. The first phase starts with ten L0 files and expects clipping to prune/split/rewrite enough files that every live file is bounded by `251..750`. The second phase validates clipping after previously clipped data has been compacted to L2 and then overlapped with fresh L0/L1 data, so the API must handle file deletion and range trimming across levels.

## Dependencies And Integration Points
The fixture depends on `db/db_test_util.h` for `DBTestBase`, test key generation, reopen/destroy helpers, level/file counting, and assertion helpers. It uses RocksDB public DB APIs for column family clipping, reads, manual compaction, and live file metadata, plus the internal `DBImpl` test compaction helper exposed through `dbfull()`.

Integration points include the configured comparator, file metadata reporting, manual compaction level placement, the LSM manifest state behind `FilesPerLevel`, and `ClipColumnFamily()` behavior on the default column family handle.

## Risks
The main correctness risk is boundary handling. The expected interval is half-open: `begin_key` is retained and `end_key` is excluded. A comparator mismatch or use of raw `std::string::compare` on a non-bytewise comparator could make metadata validation misleading; the first check uses `options.comparator`, while the second uses string comparison because the test keys are byte-comparable.

Another risk is assuming file ranges align with the inserted hundred-key blocks. Compaction can merge or split files according to target file size and level state, so the test correctly verifies both logical reads and live metadata rather than relying only on expected file counts after clipping. The assertions are sensitive to changes in compaction output sizing and level placement.

## Test Signals
Passing signals include exact file counts before/after explicit compactions (`"10"`, `"0,0,3"`, `"5,0,3"`, `"0,5,3"`, `"5,5,3"`), not-found status outside clipped ranges, exact value preservation inside clipped ranges, and metadata bounds fully contained in the clip interval after each call to `ClipColumnFamily()`.

Failure signals would point to inclusive/exclusive boundary bugs, failure to remove out-of-range table data, failure to preserve in-range values through clipping, or stale live-file metadata/manifest entries after clipping a mixed-level LSM.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_clip_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_compaction_abort_test.cc -->
# sources/storage-engines/rocksdb/db/db_compaction_abort_test.cc

## Purpose
`db_compaction_abort_test.cc` is a regression and behavior test suite for RocksDB's compaction abort/resume machinery. It validates that `DBImpl::AbortAllCompactions()` can interrupt manual, automatic, `CompactRange`, `CompactFiles`, subcompacted, bottommost, and style-specific compactions, that `ResumeAllCompactions()` restores progress, and that aborted jobs do not leave visible data loss or orphan SST/blob files.

The suite is also a concurrency test harness. It uses RocksDB sync points to trigger aborts at deterministic internal compaction stages without deadlocking the compaction thread, then checks status codes, statistics, file counts, metadata/disk consistency, and post-resume correctness.

## Important APIs, Types, And Functions
`AbortSynchronizer` is the central helper. It owns an abort thread, atomic `abort_triggered_`/`abort_completed_` guards, and a `port::CondVar`. `TriggerAbort(DBImpl*)` calls `AbortAllCompactions()` on a separate thread so a sync-point callback running on the compaction thread does not block the code path that must observe the abort flag. `WaitForAbortCompletion()` and `Reset()` make repeated abort cycles deterministic.

`SyncPointAbortHelper` wraps `AbortSynchronizer` with `SyncPoint` dependencies. Its `Setup()` installs a dependency from `DBImpl::AbortAllCompactions:FlagSet` to an internal wait point and a callback on a named compaction sync point. This ensures the abort flag is actually set before the compaction code continues past the trigger point. `CleanupAndWait()` disables callbacks and waits for the abort thread.

`DBCompactionAbortTest` extends `DBTestBase` and provides `expected_values_`, optional `Statistics`, `GetOptionsWithStats()`, `PopulateData()`, `VerifyDataIntegrity()`, and `RunSyncPointAbortTest()`. `RunSyncPointAbortTest()` captures `COMPACTION_ABORTED` and `COMPACT_WRITE_BYTES`, expects `CompactRange()` to return `Incomplete` with `IsCompactionAborted()`, resumes, reruns compaction successfully, and checks stats when enabled.

Parameterized fixtures cover varying `max_subcompactions` and compaction styles. The tests directly use public and internal APIs including `CompactRange`, `CompactFiles`, `AbortAllCompactions`, `ResumeAllCompactions`, `TEST_WaitForCompact`, `GetColumnFamilyMetaData`, `IngestExternalFiles`, `SstFileWriter`, blob options, `Env::GetChildren`, and `DestroyDir`.

## Control Flow
The common flow is: configure options to create compactable L0 input, populate multiple flushed files, install a sync-point abort trigger, start compaction, assert an aborted/incomplete status, clean up sync points, wait for the abort API to finish, call `ResumeAllCompactions()`, and rerun or wait for compaction to succeed. Data integrity is verified by reading the latest expected value for each key.

The parameterized subcompaction test runs this flow with `max_subcompactions` set to 1, 2, and 4. The style test runs equivalent abort coverage under level, universal, and FIFO compaction, with FIFO configured for normal intra-L0 compaction rather than file deletion.

Individual tests broaden the timing and API surface. `AbortManualCompaction` uses exclusive manual compaction and triggers during key-value processing. `AbortAutomaticCompaction` aborts a background job triggered by flushes, waits for compaction threads, resumes, and validates later automatic compaction. `AbortScheduledAutomaticCompactionBeforePick` aborts at `BackgroundCallCompaction:0`, before a worker removes queued work, and verifies resume schedules the still-queued compaction.

Cleanup-oriented tests assert no output is installed on abort. `AbortAndVerifyNoOutputFiles` compares L0/L1 counts before and after abort. `AbortWithOutputFilesCleanup` ensures L1 remains empty after an early abort and later receives files after resume. `AbortWithInProgressFileCleanup` enables blob files and forced blob garbage collection, aborts after 100 blob writes, and compares on-disk `.blob`/`.sst` files with column-family metadata to catch orphaned in-progress output files.

Other tests cover repeated and nested control state. `MultipleAbortResumeSequence` runs three abort/resume cycles before a successful compaction. `NestedAbortResumeCalls` calls `AbortAllCompactions()` twice, verifies a single resume is insufficient, and confirms the second resume releases compaction. `AbortBeforeCompactionStarts` sets the abort state before calling `CompactRange()`.

The suite also verifies non-compaction interactions. `AbortDoesNotAffectFlush` confirms memtable flushes still work while compactions are aborted. `AbortCompactFilesAPI` validates abort semantics through `CompactFiles()`. `AbortBottommostLevelCompaction` forces bottommost compaction after creating lower-level data. `AbortThenAtomicRangeReplace` performs `IngestExternalFiles()` with `atomic_replace_range` while compactions remain aborted, then checks replacement/deletion semantics.

## State And Persistence Behavior
The tests treat abort as a durable-state boundary. An aborted compaction must return an aborted status, increment abort stats when configured, avoid installing output files into the manifest, remove or account for any in-progress files on disk, preserve all committed input data, and leave the DB able to compact successfully after `ResumeAllCompactions()`.

`expected_values_` tracks the latest value for overlapping writes so data integrity checks validate logical state across aborted and resumed compactions. File-count assertions inspect level state before and after abort to ensure manifest state did not change as if compaction succeeded. Metadata/disk comparisons in the in-progress cleanup test are stronger: every live `.blob` and `.sst` file left on disk after abort must be represented in column-family metadata, preventing orphan files that are outside normal obsolete-file cleanup.

Nested abort state behaves like a counter or hold count. The suite expects two abort calls to require two resume calls before compactions can proceed. Scheduled automatic compaction state is also persistent in memory: aborting before pick must not lose the queued compaction, and `ResumeAllCompactions()` must re-enable background scheduling.

The atomic range replace test validates that the global compaction-aborted state is scoped to compaction work. External-file ingestion with `atomic_replace_range` installs a replacement version edit while compaction remains aborted; after resume, reads must reflect only the ingested keys and not the replaced range tail.

## Dependencies And Integration Points
This file integrates public RocksDB DB APIs, DBImpl internals, compaction job internals, blob-file writing, external SST ingestion, sync-point instrumentation, and statistics. Required headers include `db/compaction/compaction_job.h`, `db/db_impl/db_impl_secondary.h`, `db/db_test_util.h`, `options/options_helper.h`, `rocksdb/db.h`, `rocksdb/sst_file_writer.h`, and `test_util/sync_point.h`.

Important sync points include `CompactionJob::RunSubcompactions:BeforeStart`, `CompactionJob::ProcessKeyValueCompaction:Start`, `BackgroundCallCompaction:0`, `DBImpl::AbortAllCompactions:FlagSet`, and `BlobFileBuilder::WriteBlobToFile:AddRecord`. The tests depend on compaction code checking the abort flag at those stages and returning a status distinguishable by `IsCompactionAborted()`.

Integration points also include compaction-style options, FIFO-specific settings, `CompactRangeOptions` such as `exclusive_manual_compaction` and `bottommost_level_compaction`, blob garbage collection options, metadata APIs for table/blob files, and external SST writer/ingestion APIs.

## Risks
The largest risk is concurrency. Sync-point callbacks execute on compaction or background threads, while `AbortAllCompactions()` is blocking; calling it inline would deadlock. The helper avoids that but still relies on correct callback cleanup and waiting before resume. Missing `CleanupSyncPoints()` or `WaitForAbortCompletion()` would create cross-test contamination or races.

Abort timing is subtle. Some sync points fire once per subcompaction, so `AbortSynchronizer` guards against spawning multiple abort threads. Tests that assume a particular sync point is reached can become flaky if compaction picking, file sizes, or option defaults change enough that the target path is skipped.

The file-cleanup tests rely on metadata/directory naming conventions for `.sst` and `.blob` files and on file-number parsing from table names. Changes to filename formats, blob metadata exposure, or delayed obsolete-file deletion could require test updates while preserving the same correctness invariant.

`VerifyDataIntegrity()` checks keys present in `expected_values_`, but in tests that write random data without updating `expected_values_` it mostly verifies successful reads. That is intentional for some flows, but stronger value assertions depend on using `PopulateData()`.

## Test Signals
Primary success signals are `Status::IsIncomplete()` plus `IsCompactionAborted()` for aborted compactions, successful compaction after resume, unchanged input file counts immediately after abort where expected, nonzero output files after successful rerun, increased `COMPACTION_ABORTED` and `COMPACT_WRITE_BYTES` tickers, and successful reads of all expected keys.

The highest-value regression signals are absence of orphan SST/blob files after aborting while output files are open, queued automatic compaction still running after resume, nested abort/resume count behavior, flush operations succeeding while compactions are aborted, and atomic range replace correctly replacing the full column family despite the compaction-aborted state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_compaction_abort_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_compaction_filter_test.cc -->
# sources/storage-engines/rocksdb/db/db_compaction_filter_test.cc

## Purpose
`db_compaction_filter_test.cc` verifies RocksDB compaction filter behavior across compaction, flush, recovery, snapshots, merge operands, range-skip decisions, column-family context, and unsupported filter configurations. It exercises both direct `CompactionFilter` instances and `CompactionFilterFactory` implementations, including the newer `FilterV2` decision API.

The suite establishes the expected contract for filtering table-file creation reasons: compaction filters may keep, delete, change, purge, or skip keys during eligible table creation, but their use is constrained by snapshots, merge semantics, manual/automatic compaction context, and `IgnoreSnapshots()` support.

## Important APIs, Types, And Functions
Global counters `cfilter_count` and `cfilter_skips` track filter invocation and skip behavior. `NEW_VALUE` is the replacement value used by `ChangeFilter`.

`DBTestCompactionFilter` is the base fixture. `DBTestCompactionFilterWithCompactParam` parameterizes selected tests over option configs: default, universal compaction, universal multi-level, level subcompactions, and universal subcompactions, with a reduced set under non-full Valgrind.

The file defines several filter implementations. `KeepFilter` counts and preserves keys. `DeleteFilter` removes values and merge operands. `DeleteISFilter` removes keys in a numeric range and returns `IgnoreSnapshots()=true`. `SkipEvenFilter` implements `FilterV2()` and returns `kRemoveAndSkipUntil` for zero-padded key ranges whose tens bucket is even. `ConditionalFilter` removes values equal to a configured byte string. `ChangeFilter` replaces values with `NEW_VALUE`.

Factory types include `KeepFilterFactory`, `DeleteFilterFactory`, `DeleteISFilterFactory`, `SkipEvenFilterFactory`, `ConditionalFilterFactory`, `ChangeFilterFactory`, and `TestNotSupportedFilterFactory`. `KeepFilterFactory` can assert fields in `CompactionFilter::Context`, including full/manual flags, column-family ID, input start level, and input table properties. `DeleteFilterFactory` is parameterized by `TableFileCreationReason` and opts in through `ShouldFilterTableFileCreation()`.

## Control Flow
The main `CompactionFilter` test first writes 100,000 keys to a non-default column family, manually compacts from L0 to L1 and L1 to L2 with a keep filter, and asserts every key passes through the filter at each level. It then inspects internal keys at the bottom level to confirm sequence numbers are zeroed where allowed. After overwriting the same keys, it repeats the compaction path and invocation counts. The second half reopens with a delete filter for compaction-created files, compacts, and verifies the database is empty.

`CompactionFilterDeletesAll` covers the edge case where compaction output contains no keys. It writes several flushed files, compacts with a delete filter, expects zero live files, reopens, and scans an empty DB, ensuring the version edit can contain deletes without adds.

`CompactionFilterFlush` and `CompactionFilterRecovery` configure the same delete factory for `kFlush` or `kRecovery`. They prove filtering is applied only to the selected table-file creation reason: flush filtering deletes puts/merges during flush but not recovery or compaction, while recovery filtering deletes WAL-recovered records but not flushed or compacted records.

`CompactionFilterWithValueChange` runs under the parameterized option configs. It writes 100,001 keys, compacts them down, rewrites them, compacts again with `ChangeFilterFactory`, and verifies every key reads as `NEW_VALUE`. The extra key and compaction style branches exercise snapshot/sequence constraints and universal compaction paths.

`CompactionFilterWithMergeOperator` uses the uint64-add merge operator and `ConditionalFilterFactory` to validate merge interactions. It confirms filter removal of a base value is ignored when merge operands for the same key must be preserved in the same compaction, a lone value can be deleted before later merges, filters do not apply to merge keys, and combined value/merge histories still resolve correctly.

Context tests verify factory inputs. `CompactionFilterContextManual` uses universal compaction, manual full compaction, input table property capture, and internal iteration to assert 700 keys and zeroed sequences after compaction. `CompactionFilterContextCfId` checks the non-default column family ID in automatic compaction context.

Snapshot and skip tests exercise advanced decisions. `CompactionFilterIgnoreSnapshot` keeps a snapshot after the first flush, deletes selected numeric keys despite snapshots because the filter ignores snapshots, validates snapshot and latest iterator counts, then releases the snapshot. `SkipUntil` and `SkipUntilWithBloomFilter` use `FilterV2::kRemoveAndSkipUntil` to delete even tens buckets and skip scanning to the next boundary, including a prefix Bloom configuration.

Unsupported behavior is explicit. `IgnoreSnapshotsFalse`, `IgnoreSnapshotsFalseDuringFlush`, and `IgnoreSnapshotsFalseRecovery` configure filters whose `IgnoreSnapshots()` returns false and expect compaction, flush, or recovery to return `NotSupported`. `DropKeyWithSingleDelete` verifies a `FilterV2` that purges key `b` and removes other keys can coexist with later `SingleDelete` and bottommost compaction without corrupting single-delete semantics.

## State And Persistence Behavior
The suite repeatedly writes, flushes, compacts, reopens, and scans to distinguish transient read behavior from persisted table state. Delete filters should remove keys from output SSTs and manifest state, including the all-deleted case where no new table files are added. Keep filters should preserve keys while allowing bottom-level sequence number zeroing. Change filters must persist rewritten values into compacted output files.

Creation reason filtering changes when data becomes persistent. A filter for `kFlush` affects memtable-to-SST output but not WAL recovery; a filter for `kRecovery` affects recovered WAL contents but not normal flush; a filter for `kCompaction` applies to manual compaction-created files in these tests while automatic compaction may be deliberately skipped by `DeleteFilterFactory`.

Snapshot handling is a persistence contract. Ordinary compaction filtering cannot ignore snapshots unless `IgnoreSnapshots()` is true; unsupported filters must fail rather than dropping data still visible to snapshots. `DeleteISFilter` shows the opposite contract: a filter that explicitly ignores snapshots can remove records regardless of snapshot visibility, changing what snapshot iterators see according to the tested count expectations.

Merge persistence is constrained by merge semantics. Compaction filters are not allowed to blindly delete merge operands or base values when that would alter the resolved merged value for visible history. The merge test encodes those cases with fixed64 values and an additive merge operator.

## Dependencies And Integration Points
This file depends on `db/db_test_util.h` for DB fixtures, compaction helpers, internal iterators, column-family helpers, key/value operations, and utility assertions. It also uses `port/stack_trace.h`, GoogleTest parameterization, RocksDB `CompactionFilter` and `CompactionFilterFactory` APIs, `CompactionFilter::Context`, `TableFileCreationReason`, merge operators, table factories, Bloom filter policy, prefix extractors, snapshots, internal key parsing, and `CompactRangeOptions`.

Integration points include manual/internal compaction helpers (`TEST_CompactRange`, `CompactRange`), sequence-number zeroing at bottom levels, column family handles and IDs, universal and level compaction styles, subcompactions, block-based table prefix Bloom filters, WAL recovery, flush, merge resolution, single-delete correctness, and table property collection passed into filter context.

## Risks
The global counters are intentionally simple but require each test to reset them before assertions. Parallel test execution within the same process would be unsafe unless RocksDB test runners isolate these tests appropriately.

Several tests depend on exact filter invocation counts, sequence-number zeroing, level placement, and manual compaction behavior. Changes to compaction picking, universal compaction layout, or bottommost sequence optimization can break assertions even when user-visible data remains correct, so failures should be interpreted against the intended internal contract.

Snapshot and merge interactions are correctness-sensitive. Allowing a filter with `IgnoreSnapshots()=false` to proceed during compaction/flush/recovery could silently drop visible data. Applying filters to merge operands incorrectly could change merge results. `DropKeyWithSingleDelete` covers a narrow single-delete hazard where purging/removing keys must not leave an invalid tombstone/value pairing.

`SkipEvenFilter` assumes zero-padded numeric keys and constructs `skip_until` boundaries with `snprintf`. It is a targeted test for `FilterV2` skip semantics, not a general parser-safe filter pattern for arbitrary user keys.

## Test Signals
Useful success signals include exact `cfilter_count` values for manual level compactions, `cfilter_skips` values for skip-until tests, expected live-file counts after all-delete compaction, empty scans after deletion filters, persisted `NEW_VALUE` reads after value-changing compaction, correct context fields in factory creation, expected snapshot/latest iterator counts after snapshot-ignoring deletes, `NotSupported` statuses for unsupported filters, and successful reopen/compaction after single-delete purge scenarios.

Regression failures identify specific contracts: creation-reason routing, merge operand preservation, sequence-number zeroing, column-family context propagation, skip-until range pruning, snapshot safety checks, and cleanup/manifest handling when a compaction filter produces no output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_compaction_filter_test.cc -->
