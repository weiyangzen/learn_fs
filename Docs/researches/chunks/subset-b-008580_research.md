# sources/storage-engines/rocksdb/db/compaction/compaction_picker_test.cc lines 6132-6256

## Scope

This chunk is the end of `compaction_picker_test.cc`. It covers the final scenario tests in `FIFORatioBasedCompactionPickingTest`, closes `ROCKSDB_NAMESPACE`, and defines the GoogleTest `main()` entry point. The tests exercise repeated flush, real FIFO compaction picking, and simulated compaction execution for RocksDB's FIFO + BlobDB ratio-based intra-L0 algorithm. The helper class and core loop are defined immediately before this chunk in the same file; this chunk contains the high-level behavioral scenarios and assertions.

## Purpose

The tests validate that the ratio-based FIFO intra-L0 picker remains stable across long-running streams of L0 flushes with blob data. The covered scenarios stress variable flush sizes, FIFO size-based dropping, prevention of re-compacting already "graduated" files, early memtable flushes, changing SST/blob ratios, logarithmic write amplification under large target-to-flush ratios, and tier progression from small files into larger compacted outputs.

The production picker under test is `FIFOCompactionPicker::PickCompaction` with `compaction_options_fifo.use_kv_ratio_compaction = true`, `allow_compaction = true`, FIFO compaction style, and a configured `level0_file_num_compaction_trigger`. The surrounding file-list mutation is a test simulation: selected input files are either erased for FIFO drop reasons or merged into one synthetic `L0File` for intra-L0 compaction.

## Important APIs, Types, And Helpers

- `TEST_F(FIFORatioBasedCompactionPickingTest, ...)` registers each scenario against the fixture derived from `CompactionPickerTest`.
- `RunFlushAndCompact(TestState&, int num_rounds, int trigger, uint64_t max_data_files_size, const FlushGenerator&)` drives the shared simulation. Each round inserts a new flush file at the front of `TestState::files`, calls the real `FIFOCompactionPicker`, and updates test state according to the compaction reason.
- `FlushGenerator` returns `{sst_size, blob_size}` for each synthetic flush. This chunk uses both deterministic lambdas and seeded `Random` instances to produce reproducible variable workloads.
- `TestState` carries the synthetic L0 list, global creation order, write-amplification tracker, compaction count, and maximum file count observed by the loop.
- `L0File` models an L0 SST with `size`, associated `blob_size`, `age`, and `is_compacted`. It is not persistent RocksDB metadata; it is converted into `FileMetaData` plus aggregate blob metadata on each picker call.
- `AssertStandardGoals` combines file count, compacted-size uniformity, and write-amplification checks.
- `AssertGraduatedNotPicked` reruns the picker over the final synthetic file set and asserts that any `kFIFOReduceNumFiles` inputs remain below the computed target size, i.e. files that reached or exceeded target size are not selected again.
- `AssertLowWriteAmp`, `AssertFileCountBounded`, `AssertCompactedUniform`, and `ComputeStats` provide targeted signals for bounded write cost, bounded L0 fanout, and approximate uniformity of compacted outputs.
- `Random` from `util/random.h` provides deterministic pseudo-random variation in flush sizes and blob sizes.
- `CompactionReason::kFIFOReduceNumFiles`, `kFIFOMaxSize`, and `kFIFOTtl` distinguish intra-L0 compaction from FIFO dropping paths in the helper loop.

## Scenario Coverage

`VariableFlushWithFIFODropping` runs 200 rounds with a 500 MiB data cap, trigger 10, SST sizes from 32 KiB to 128 KiB, and blob sizes from 32 MiB to 96 MiB. Because the blob-heavy workload can exceed the cap, this scenario intentionally covers both intra-L0 compaction and FIFO size-based dropping. The final state must satisfy standard goals with compacted-file coefficient of variation at most 0.40.

`NoCascadingReCompaction` uses 200 uniform rounds with 64 KiB SSTs and 64 MiB blobs under a 10 GiB cap and trigger 10. It verifies that the tiered algorithm may merge intermediate files at higher tier boundaries, but must not reselect files that have already reached the final target size. It also caps SST write amplification at 4.0.

`EarlyMemtableFlush` simulates very small flushes under a 1 GiB cap. Most flushes are 8-32 KiB SSTs, while one in five is 64-128 KiB; each carries 32 MiB of blob data. The looser standard goals allow compacted-size CV up to 0.50, write amplification up to 4.0, and file count up to five times the trigger, reflecting higher variance from early flushes.

`BlobCompressionVariation` fixes SST size at 64 KiB but varies blob size from 20 MiB to 80 MiB. This shifts the global SST/blob ratio over time. The expected behavior is that target sizing is recomputed on every pick rather than cached, producing compacted files that remain reasonably uniform with CV at most 0.30.

`TieredLargeRatio` creates a large target-to-flush ratio: 1 KiB SSTs with 1 MiB blobs, a 10 GiB cap, and trigger 10. Comments document the expected approximate target and tier boundaries. The key assertion is logarithmic write amplification: the tiered picker should stay below 6.0 instead of behaving like a flat merge with very high rewrite cost. File count is also bounded to `trigger * 6`.

`TieredProgression` uses trigger 4, 10 KiB SSTs, 1 MiB blobs, and a 100 MiB cap. It targets multiple intermediate tiers with approximate boundaries around 16 KiB, 62 KiB, and 248 KiB. The test checks that at least one compacted file exists after 200 rounds and that write amplification remains below 5.0.

`GraduatedFilesNotRecompacted` builds a final state where the computed target is around 156 KiB while compacted files can reach or exceed that size. It reruns the graduation invariant with trigger 4 and a 500 MiB cap, ensuring final target-sized files are not recycled into further `kFIFOReduceNumFiles` picks.

The `main()` function installs RocksDB's stack trace handler, initializes GoogleTest, and runs all tests in the binary.

## Control Flow

Each scenario follows the same pattern:

1. Choose a data cap and trigger.
2. Create a fresh `TestState`.
3. Call `RunFlushAndCompact` for a fixed number of rounds with a workload-specific flush generator.
4. Assert the final synthetic state using scenario-specific invariants.

Inside the shared loop, the picker is invoked once per flush. `PickCompactionFromFiles` rebuilds a `VersionStorageInfo` from the current synthetic file vector, sets FIFO options, inserts L0 files newest-first using descending file numbers, adds a single aggregate blob file when blob data exists, computes compaction scores, then calls `FIFOCompactionPicker::PickCompaction`. Returned input file numbers are mapped back to vector indices. The picker is unregistered after each pick so subsequent simulated rounds can select more compactions.

When the picker returns `kFIFOMaxSize` or `kFIFOTtl`, the loop treats the result as a drop and erases the selected files. For other non-empty results, it treats the pick as intra-L0 compaction: it adds selected SST bytes to the write-amplification tracker, removes selected files, and inserts one compacted output with summed SST and blob sizes. This preserves the relative age/order shape needed by later picker calls without invoking `CompactionJob` or writing actual SST files.

## State And Persistence Behavior

The tests do not create a RocksDB database or persist files. All persistent-looking state is in-memory test state:

- `TestState::files` is the evolving synthetic L0 file list.
- `WriteAmpTracker::bytes_flushed` accumulates original SST flush bytes.
- `WriteAmpTracker::bytes_compacted` accumulates SST bytes rewritten by simulated intra-L0 compactions.
- `global_age` and vector position model ordering, while real picker ordering is represented by generated file numbers during `VersionStorageInfo` reconstruction.
- Blob state is reduced to total bytes attached to a single `BlobFileMetaData` per picker call. This is sufficient for ratio and cap calculations but does not test per-SST blob-file linking or garbage accounting.

The only global side effect in the chunk is the test binary entry point calling `InstallStackTraceHandler()` and `RUN_ALL_TESTS()`.

## Dependencies And Integration Points

This chunk integrates with the earlier fixture code in the same file and with RocksDB compaction internals:

- `db/compaction/compaction_picker_fifo.h` supplies `FIFOCompactionPicker` and the ratio-based intra-L0 selection path.
- `db/compaction/compaction.h` supplies `Compaction` and `CompactionReason`.
- `VersionStorageInfo`, `FileMetaData`, and blob metadata are used through the base fixture to present realistic picker inputs.
- `MutableCFOptions::compaction_options_fifo` controls FIFO caps, `allow_compaction`, and `use_kv_ratio_compaction`.
- GoogleTest macros (`ASSERT_LE`, `ASSERT_GE`, `ASSERT_LT`) turn scenario invariants into test failures.
- `util/random.h` gives deterministic workload variation, so failures are reproducible.

The tests are an integration point between newly added or modified FIFO ratio-based picking logic and RocksDB's existing `compaction_picker_test` suite. They are especially relevant to changes in target-size computation, blob-aware data-size estimation, tier-boundary selection, graduated-file skipping, and FIFO drop priority relative to intra-L0 compaction.

## Risks And Edge Cases

- The workload loop calls the real picker but simulates execution. Bugs in `CompactionJob`, manifest edits, actual output file metadata, blob-file linking, or sequence-number handling are outside this chunk's coverage.
- Blob metadata is represented by one aggregate blob file, so the tests validate total-byte ratio behavior rather than precise blob-file association behavior.
- `AssertGraduatedNotPicked` recomputes the target in test code using `max_data_files_size * sst_ratio / trigger`. If production target computation changes, this assertion must be updated in lockstep or it can become a stale oracle.
- Random workloads are deterministic due to fixed seeds, but threshold-based assertions on CV and write amplification may need adjustment if legitimate picker heuristics change.
- File count bounds are final-state checks in these tests; transient file count is tracked in `max_file_count_seen` but not asserted in this chunk.
- The tests assume single-level FIFO behavior in the simulation. Multi-level migration cases are covered earlier in the file, not in this final scenario block.
- Because `RunFlushAndCompact` performs at most one picker action per flush, it may not model production scheduling that drains multiple queued compactions before later flushes.
- The test comments encode expected tier counts and approximate targets. These are valuable design documentation but also create maintenance risk if constants such as tier floors, cap semantics, or blob-ratio formulas evolve.

## Test Signals

Strong signals from this chunk include:

- Repeated picker invocations over 60-500 rounds catch feedback-loop bugs that single-pick unit tests miss.
- `VariableFlushWithFIFODropping` validates coexistence of intra-L0 compaction with FIFO size dropping under blob-heavy cap pressure.
- Graduation assertions catch cascading recompaction regressions that would inflate write amplification after files reach target size.
- Write-amplification assertions detect loss of tiered/logarithmic behavior, especially in `TieredLargeRatio`.
- Uniformity checks detect poor target adaptation when flush sizes or blob sizes vary.
- Bounded file-count checks detect failure to compact enough files under the trigger policy.
- The final `main()` makes this source a self-contained GoogleTest binary test file, so all scenario failures surface through normal RocksDB test execution.
