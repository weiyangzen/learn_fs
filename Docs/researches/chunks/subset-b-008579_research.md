# sources/storage-engines/rocksdb/db/compaction/compaction_picker_test.cc lines 1-6131

## Scope

This chunk covers almost all of RocksDB's `compaction_picker_test.cc`: test fixtures, helpers, and unit tests from the file header through the `FIFORatioBasedCompactionPickingTest` helper class. It stops just before the concrete `FIFORatioBasedCompactionPickingTest` simulation test cases, which begin in the following chunk.

## Purpose

The code is a C++ test suite for RocksDB compaction picking behavior. It builds synthetic `VersionStorageInfo` states and validates how level, universal, and FIFO compaction pickers decide whether compaction is needed, which files and levels are selected, what output level and compaction reason are assigned, when trivial moves are allowed, how active compactions block new work, and how newer features such as user-defined timestamps, per-key placement, tiered storage, read-triggered compaction, file temperature migration, FIFO ratio-based compaction, and blob-aware FIFO sizing interact with older picker rules.

The tests do not execute full compaction jobs. They focus on picker contracts: given file metadata, column-family options, immutable options, blob metadata, timestamps, and compaction state, the picker must return either `nullptr` or a `Compaction` whose inputs and metadata match expected invariants.

## Important APIs, Types, and Functions

- `CountingLogger` is a minimal `Logger` implementation whose `Logv()` increments `log_count`; it backs the `LogBuffer` passed into picker calls.
- `CompactionPickerTestBase` owns the shared test state: comparator, `InternalKeyComparator`, `Options`, `ImmutableOptions`, `MutableCFOptions`, `MutableDBOptions`, `LevelCompactionPicker`, column family name, FIFO options, `VersionStorageInfo`, allocated `FileMetaData`, file-number map, and manual compaction input vectors.
- `NewVersionStorage()` constructs a fresh `VersionStorageInfo` for a compaction style and number of levels, then prepares it for appends.
- `AddVersionStorage()` creates a temporary `VersionStorageInfo` layered on the current version to simulate appending new files while preserving existing state.
- `DeleteVersionStorage()` resets version state, file ownership, file map, and constructed compaction inputs.
- `Add()` is the central fixture helper. It creates `InternalKey` bounds, optional user-defined timestamp suffixes, `FileMetaData`, compensated size, temperature, oldest ancestor time, newest key time through a `mock::MockTableReader`, min/max timestamps, and epoch number, then registers the file in `VersionStorageInfo` and the test map.
- `UpdateVersionStorageInfo()` and `UpdateVersionStorageInfoWithTsLow()` merge temporary version state through `VersionBuilder` when present, call `PrepareForVersionAppend()`, compute compaction score, and finalize storage. The timestamp variant passes `full_history_ts_low`.
- `AddBlobFile()` injects `BlobFileMetaData` into `VersionStorageInfo`, with optional linked SST metadata omitted in this chunk's tests.
- `SetupFIFORatioBased()` sets FIFO style, creates version storage, and configures `CompactionOptionsFIFO` fields for ratio-based intra-L0 tests.
- `PickFIFOCompaction()` finalizes version state and calls `FIFOCompactionPicker::PickCompaction()`.
- `CompactionPickerTest` uses the bytewise comparator and clears `SyncPoint` callbacks in its destructor.
- `CompactionPickerU64TsTest` uses a bytewise comparator with 64-bit user-defined timestamps and provides `MakeU64Timestamp()`, `SetupBottommostFileWithTimestamps()`, and `AddL0FilesWithTimestamps()`.
- `PerKeyPlacementCompactionPickerTest` is parameterized on a boolean and uses `SyncPoint` callback `Compaction::SupportsPerKeyPlacement:Enabled` to force per-key-placement support on or off.
- `FIFORatioBasedCompactionPickingTest` starts in this chunk. It defines an L0 simulation model, picker-to-vector-index mapping, simulated compaction execution, file-size statistics, write-amplification tracking, flush-and-compact loop, and assertion helpers. Its concrete tests are outside this chunk.

Primary picker APIs exercised include `NeedsCompaction()`, `PickCompaction()`, `PickCompactionForCompactFiles()`, `PickCompactionForCompactRange()`, `GetCompactionInputsFromFileNumbers()`, `RangeOverlapWithCompaction()`, `FilesRangeOverlapWithCompaction()`, `UnregisterCompaction()`, `Compaction::TEST_IsBottommostLevel()`, `Compaction::EvaluateProximalLevel()`, and `ColumnFamilyData::ValidateOptions()`.

## Control Flow

Most tests follow the same pattern. A test configures mutable or immutable compaction options, calls `NewVersionStorage()`, uses `Add()` and sometimes `AddBlobFile()` to create a synthetic LSM shape, marks selected files as `being_compacted` or `marked_for_compaction`, finalizes with `UpdateVersionStorageInfo()`, invokes a picker, and asserts the resulting `Compaction` fields.

The early level-compaction tests cover empty/single-file cases, L0 file-count triggers, large L1/L2 score triggers, dynamic level bytes and base-level selection, and `NeedsCompaction()` score thresholds. Later level tests explore compaction priority: by compensated size, minimum overlapping ratio, round-robin cursor position, multiple-file round-robin, files marked for compaction, and suppression of lower-priority L1 work when higher-priority L0 work is blocked.

Universal compaction tests check `NeedsCompaction()` in a one-level layout, ingest-behind reserved levels, trivial move eligibility across multi-level universal layouts, periodic compaction selection, incremental space amplification, read-triggered compaction, marked-file/delete-triggered compactions, size-amplification and size-ratio compaction under tiered-storage options, max read amplification, and standalone range-deletion handling.

FIFO tests first validate classic max-size and TTL-style behavior, then add temperature migration and blob-aware/ration-based paths. FIFO temperature tests set current-time-relative `newest_key_time` or `oldest_ancestor_time` and assert `CompactionReason::kChangeTemperature`, output temperature, and single-file older-first picking. FIFO ratio tests configure `use_kv_ratio_compaction`, table/data size limits, trigger count, explicit `max_compaction_bytes`, migration with non-L0 files, and invalid-config fallback paths.

Manual and forced compaction paths use `GetCompactionInputsFromFileNumbers()` plus `PickCompactionForCompactFiles()` or `PickCompactionForCompactRange()`. They verify output temperature overrides, manual range byte limits, manual universal compaction clearing `FilesMarkedForCompaction()`, and overlap detection with existing compactions.

Timestamp tests build user keys with 64-bit timestamp suffixes, then verify overlap checks use timestamp-stripped equality at boundaries, bottommost file marking respects `full_history_ts_low`, and both level and universal pickers accept/pass the timestamp lower bound.

The parameterized per-key-placement tests set a sync-point callback, create active compactions through manual compact-files calls, then ask whether candidate inputs overlap with existing compactions under normal level, universal, proximal-level, and last-level-only scenarios. Expected overlap changes with the boolean parameter when per-key placement or tiered last-level behavior is enabled.

## State and Persistence Behavior

This is test code, so it does not persist data to disk. Its important state is in-memory `VersionStorageInfo`, `FileMetaData`, `BlobFileMetaData`, picker registration state, and option objects.

`CompactionPickerTestBase` owns all allocated file metadata through `files_`. `ClearFiles()` deletes any pinned mock table readers before clearing the unique pointers. `file_map_` is non-owning and maps file number to `FileMetaData*` plus level for direct test mutation and manual input construction.

`VersionStorageInfo` is rebuilt frequently. `NewVersionStorage()` discards previous state; `AddVersionStorage()` plus `UpdateVersionStorageInfo()` uses `VersionBuilder::SaveTo()` to merge staged files into the current version. After every mutation to synthetic state, tests must recompute compaction score and finalize storage or picker decisions will not reflect the intended layout.

File metadata fields are deliberately overloaded for picker behavior: `file_size` and `compensated_file_size` drive scores and priority; `smallest`/`largest` and sequence numbers drive overlap expansion and clean boundaries; `being_compacted` blocks selection; `marked_for_compaction` drives delete-triggered paths; `temperature`, `oldest_ancester_time`, and table-property `newest_key_time` drive FIFO temperature migration; `epoch_number` drives universal sorted-run ordering; `min_timestamp` and `max_timestamp` drive UDT bottommost marking; `num_entries` and `num_range_deletions` simulate standalone range-tombstone files.

Blob state is represented by `VersionStorageInfo::AddBlobFile()` and is used by FIFO scoring, size dropping, TTL estimation, and ratio-based target calculation. The tests generally add aggregate blob totals rather than realistic SST-to-blob linkage, which is enough for picker-level size accounting.

Picker state is observable through active compaction registration. `PickCompactionForCompactFiles()` and normal `PickCompaction()` mark input files as `being_compacted`; later picker calls should detect conflicts. The FIFO simulation helper explicitly calls `UnregisterCompaction()` after mapping inputs so repeated simulated cycles can proceed.

## Dependencies and Integration Points

- RocksDB compaction internals: `Compaction`, `CompactionInputFiles`, `LevelCompactionPicker`, `UniversalCompactionPicker`, `FIFOCompactionPicker`, `FileTtlBooster`, and compaction reasons.
- Version metadata: `VersionStorageInfo`, `VersionBuilder`, `FileMetaData`, `TableProperties`, `BlobFileMetaData`, and `SharedBlobFileMetaData`.
- Options and comparators: `Options`, `ImmutableOptions`, `MutableCFOptions`, `MutableDBOptions`, `CompactionOptions`, `CompactionOptionsFIFO`, bytewise comparator, timestamp-aware bytewise comparator, and SST partitioner factory.
- Test infrastructure: `test_util/testharness.h`, `test_util/testutil.h`, `SyncPoint`, `ASSERT_*` macros, `SCOPED_TRACE`, and parameterized GoogleTest APIs.
- Mock table integration: `mock::MockTableReader` supplies `newest_key_time` through table properties without building real SST files.
- Time and environment integration: FIFO temperature/TTL tests read `Env::Default()->GetCurrentTime()` or `time(nullptr)` and compare file ages to TTL or temperature thresholds.
- Option validation integration: `ColumnFamilyData::ValidateOptions()` is tested directly for FIFO ratio-related configuration acceptance.

## Risks and Edge Cases

- The suite relies on precise L0 ordering by sequence number, epoch number, and file number. Small changes in file ordering logic can alter expected selected files even when the same broad compaction is chosen.
- Many assertions depend on inclusive user-key boundaries and sequence-number overlap behavior. Off-by-one key comparisons or comparator-with-timestamp changes can create unsafe trivial moves or missed overlap conflicts.
- `Add()` sets mock table readers manually and `ClearFiles()` deletes them. Reader ownership assumptions are test-specific and can become fragile if `FileMetaData` or pinned-reader ownership semantics change.
- `UpdateVersionStorageInfo()` is required after synthetic metadata changes. Several tests mutate `being_compacted` or marked-file lists around score recomputation; picker behavior can differ before and after recomputing scores.
- Dynamic-level-byte and tiered universal tests assume exact base/proximal/output level computations. Changes to `level_compaction_dynamic_level_bytes`, `preclude_last_level_data_seconds`, or max-read-amp estimation may break precise expected levels.
- File-temperature tests depend on wall-clock time and fallback ordering between `newest_key_time` and `oldest_ancester_time`; unknown timestamps must be interpreted consistently.
- Marked-file universal tests combine `marked_for_compaction`, epoch ordering, and existing active compactions. Incorrect conflict detection can allow overlapping compactions or starve marked files.
- FIFO ratio tests use simplified blob totals instead of precise linked-SST blob metadata. They are good picker signals but may not catch bugs requiring per-SST blob ownership.
- FIFO multi-level migration tests intentionally allow fallback to the old cost-based path when ratio picking is skipped; this preserves compatibility but makes the exact chosen path less strict in migration scenarios.
- The FIFO simulation helper computes the ratio target independently in `AssertGraduatedNotPicked()`. If production target calculation changes, that helper can become a stale duplicate oracle.
- Per-key-placement tests are controlled by `SyncPoint`; leaking callbacks would corrupt later tests, so the fixture destructor's cleanup is important.
- Some tests assert `compaction` fields but not every input ordering detail. A picker regression could still pass if it preserves only the asserted subset.

## Test Signals

- Basic compaction signals: `Empty`, `Single`, `Level0Trigger`, `Level1Trigger`, `Level1Trigger2`, `LevelMaxScore`, and `NeedsCompactionLevel` verify score thresholds and simple picked inputs.
- Dynamic-level signals: `Level0TriggerDynamic*` and `LevelTriggerDynamic4` verify base-level movement and output level selection under dynamic level bytes.
- Universal signals: `NeedsCompactionUniversal`, ingest-behind reserved-level handling, universal trivial move tests, periodic compaction tests, incremental space amplification tests, size-amp/ratio tiered tests, max-read-amp tests, and standalone range-deletion selection.
- Read-triggered signals: disabled, below-threshold, above-threshold, `NeedsCompactionReadTriggered`, level picking, universal picking, last-level skip, not-marked no-op, and intra-L0 universal read-triggered selection.
- FIFO signals: size/TTL need detection, temperature changes to cold/warm/hot, max compaction bytes limiting, existing-temperature skipping, output temperature override, ratio-based file count threshold, no-blob fallback, no recompaction of graduated files, explicit target override, invalid-config fallback, multi-level migration skip/resume, blob-aware TTL/size dropping, and blob-aware score computation.
- Priority and overlap signals: minimum-overlap-ratio tests, round-robin cursor tests, many-file priority, parent-index regression, overlapping-user-key expansion cases, locked-file avoidance, file-TTL booster, and L0-vs-L1 scheduling priority.
- Trivial move signals: L0 and non-L0 trivial moves, empty-output-level moves, SST partitioner disabling trivial move, multiple-file clean-boundary cases, active-file stopping, and intra-L0 byte-limit behavior.
- Manual compaction signals: compact-files output temperature, compact-range max bytes, universal marked manual compaction, and active-compaction overlap checks.
- Timestamp signals: U64 timestamp range overlap at boundary-equivalent user keys, universal non-trivial move with timestamp-only overlap, bottommost full-history timestamp low marking, and passing `full_history_ts_low` through level/universal pickers.
- Per-key-placement signals: normal and universal overlap checks under enabled/disabled support, proximal-level locking, last-level-only overlap/failure/no-conflict cases, and parameterized execution for both boolean modes.
