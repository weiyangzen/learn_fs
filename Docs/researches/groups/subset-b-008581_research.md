# Research Group: subset-b-008581

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.cc

## Purpose
This file implements RocksDB's universal compaction picker. It converts `VersionStorageInfo` state into a `Compaction` by treating L0 files and non-zero levels as time-ordered "sorted runs" and then selecting one of several universal strategies: periodic compaction, size amplification reduction, size-ratio/read-amplification reduction, delete-triggered compaction, or read-triggered compaction. The picker is central to universal-style LSM behavior because it chooses which files become inputs, which level receives output, whether a compaction can be trivial-moved, and which output path/compression options apply.

## Important APIs, Types, and Functions
The exported entry points are `UniversalCompactionPicker::NeedsCompaction`, `UniversalCompactionPicker::PickCompaction`, and `UniversalCompactionPicker::MaxOutputLevel` from the companion header. Most logic lives in the private `UniversalCompactionBuilder`, whose key methods are `PickCompaction`, `CalculateSortedRuns`, `PickCompactionToReduceSortedRuns`, `PickCompactionToReduceSizeAmp`, `PickIncrementalForReduceSizeAmp`, `PickDeleteTriggeredCompaction`, `PickPeriodicCompaction`, `PickReadTriggeredCompaction`, `BuildCompactionToNextLevel`, `PickCompactionWithSortedRunRange`, `IsInputFilesNonOverlapping`, `MightExcludeNewL0sToReduceWriteStop`, and `GetPathId`.

`SortedRun` represents one universal run: an L0 file or an entire non-zero level, with raw size, compensated size, compaction-in-progress state, and whether the run contains a marked standalone range tombstone file. `InputFileInfo`, `SmallestKeyHeapComparator`, and `SmallestKeyHeap` support overlap detection for trivial moves. Debug-only `GetSmallestLargestSeqno` validates input sequence ranges.

## Control Flow
`NeedsCompaction` returns true if L0's compaction score is at least one, if files are marked for periodic or deletion-triggered compaction, or if read-triggered files exist. `PickCompaction` creates a builder, which records immutable/mutable options, the internal comparator, snapshots, snapshot checker, current `VersionStorageInfo`, whether the caller requires max-level output, ingest-behind allowance, and `full_history_ts_low`.

`UniversalCompactionBuilder::PickCompaction` computes sorted runs up to the current max output level. If nothing is marked and the sorted-run count is below `level0_file_num_compaction_trigger`, it returns null. Otherwise it tries strategies in fixed priority order: periodic compaction, size amplification compaction, size-ratio compaction, sorted-run-count compaction based on `max_read_amp`, delete-triggered compaction, then read-triggered compaction. A successful compaction is checked against max-output-level requirements, optionally flagged as a trivial move when `allow_trivial_move` and non-periodic inputs are non-overlapping, registered with the base picker, and followed by compaction score recomputation.

Size-ratio compaction scans consecutive sorted runs that are not already compacting and do not contain marked standalone range tombstones. It grows a candidate under either total-size or similar-size stop style, applies `min_merge_width`/`max_merge_width`, selects output level from the next older sorted run or max output level, computes compression enablement from `compression_size_percent`, and rejects output ranges overlapping in-progress compactions. Size amplification compaction works from the oldest eligible run backward, can skip the last level under `preclude_last_level_data_seconds`, may exclude newest L0 files to reduce write-stop risk, compares newer-run size against `max_size_amplification_percent`, and optionally attempts incremental size-amp compaction before falling back to a full span.

Delete-triggered compaction handles single-level universal by picking the first eligible marked L0 file and newer contiguous runs, while multi-level universal delegates marked-file selection to `PickFilesMarkedForCompaction` and then builds a next-level compaction. Periodic compaction tries to include the oldest available suffix of sorted runs so marked files are covered by a full compaction. Read-triggered compaction expands one marked file to a clean cut, includes overlapping L0 files for one-level universal, and builds a next-level compaction.

## State and Persistence Behavior
The file does not persist data directly; it mutates scheduling state by constructing `Compaction` objects, registering selected inputs with `CompactionPicker::RegisterCompaction`, and recomputing scores in `VersionStorageInfo`. Persistent impact comes later when the selected compaction rewrites SSTs and commits a version edit. It relies on `FileMetaData` fields such as file size, compensated size, path ID, sequence range, oldest ancestor time, `being_compacted`, `marked_for_compaction`, and standalone range tombstone state.

Snapshot state is only passed to delete-triggered compactions when user-defined timestamps are not enabled. `ShouldSkipMarkedFile` delays standalone range tombstone files until the earliest snapshot definitely sees them and until a better succeeding marked range tombstone compaction can run. `full_history_ts_low` is currently passed through but not used in universal picking, with a TODO noting possible future use against infinite compaction loops.

## Dependencies and Integration Points
This implementation depends on `CompactionPicker`, `Compaction`, `VersionStorageInfo`, `FileMetaData`, `MutableCFOptions`, `MutableDBOptions`, `ImmutableOptions`, `InternalKeyComparator`, `SnapshotChecker`, logging, statistics histograms, sync points, and filename formatting. It calls shared picker utilities including `FilesRangeOverlapWithCompaction`, `ExpandInputsToCleanCut`, `SetupOtherInputs`, `GetOverlappingL0Files`, `GetGrandparents`, `GetCleanInputsWithinInterval`, and `PickFilesMarkedForCompaction`. It integrates with universal options including `size_ratio`, `min_merge_width`, `max_merge_width`, `max_read_amp`, `max_size_amplification_percent`, `compression_size_percent`, `incremental`, `allow_trivial_move`, and stop style.

## Risks and Edge Cases
The highest-risk behavior is strategy priority: periodic and size-amp choices can preempt delete/read-triggered work. Marked standalone range tombstone files are intentionally skipped by most strategies, so incorrect skip logic can delay space reclamation. Output-level selection is subtle in multi-level universal, especially when `require_max_output_level`, ingest-behind max-level reservation, or `preclude_last_level_data_seconds` apply. Incremental size-amp compaction relies on fanout estimates and clean-cut expansion, so it can fall back to full compaction or reject candidates when overlap conflicts exist. `MightExcludeNewL0sToReduceWriteStop` trades size-amp urgency against write-stop avoidance and depends on unsigned arithmetic guards around trigger and merge-width values.

Trivial-move detection merges candidate inputs by smallest key and assumes non-zero-level files are already ordered. Comparator use deliberately ignores timestamps for file-key overlap checks. Path selection is approximate and the comments note that multi-column-family space accounting is not handled.

## Test Signals
The file exposes numerous `TEST_SYNC_POINT` hooks used by compaction tests. Direct validation is spread across RocksDB compaction picker tests, universal compaction tests, and service tests that exercise universal compaction with standalone range tombstones and per-key placement. Useful signals include selected `CompactionReason`, input/output levels, sorted-run logs, `NUM_FILES_IN_SINGLE_COMPACTION`, absence of overlap with in-progress compactions, correct handling of periodic/read/delete-triggered marks, and data correctness after universal compactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h

## Purpose
This header declares the universal compaction picker class. It is the public picker interface used by RocksDB column families configured with `kCompactionStyleUniversal`, while the implementation file contains the detailed run-selection algorithms.

## Important APIs, Types, and Functions
`UniversalCompactionPicker` derives from `CompactionPicker`. Its constructor forwards immutable options and the internal comparator to the base class. `PickCompaction` overrides the base picker and accepts column-family name, mutable CF and DB options, existing snapshots, optional `SnapshotChecker`, mutable `VersionStorageInfo`, a log buffer, `full_history_ts_low`, and an optional `require_max_output_level` flag. `MaxOutputLevel` returns `NumberLevels() - 1`. `NeedsCompaction` reports whether the current version has any universal compaction trigger.

## Control Flow
Callers ask `NeedsCompaction` as a cheap scheduling predicate, then call `PickCompaction` to get a heap-allocated `Compaction` or null. The `require_max_output_level` flag is a caller-side constraint: when true, the implementation only returns a compaction whose output level satisfies the max-output-level requirement.

## State and Persistence Behavior
The class itself stores no additional state beyond the `CompactionPicker` base. It relies on the mutable `VersionStorageInfo` passed to `PickCompaction` for current LSM state and selected-file marking. Persistent effects are indirect through the returned `Compaction` and subsequent version edits committed by the compaction job.

## Dependencies and Integration Points
The header includes `db/compaction/compaction_picker.h` and `db/snapshot_checker.h`, and references `ImmutableOptions`, `InternalKeyComparator`, `MutableCFOptions`, `MutableDBOptions`, `VersionStorageInfo`, `LogBuffer`, `SequenceNumber`, and `SnapshotChecker`. It integrates with the general compaction scheduling framework through virtual methods on `CompactionPicker`.

## Risks and Edge Cases
The header-level contract matters because callers own the returned `Compaction*` and because `require_max_output_level` can intentionally suppress otherwise valid universal compactions. Any signature changes affect compaction scheduling, DB open/manual compaction paths, and tests that instantiate pickers directly.

## Test Signals
Signals are indirect through tests of universal compaction picking and DB-level compaction behavior. Compile-time coverage ensures the picker remains substitutable for `CompactionPicker`; runtime coverage should verify null/non-null selection, max output level behavior, and `NeedsCompaction` scheduling triggers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_universal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc

## Purpose
This file implements RocksDB's remote compaction service bridge. On the primary DB side, it serializes a compaction request, schedules and waits on a `CompactionService`, imports remote SST outputs, reconstructs file metadata/stats, and notifies the service of installation status. On the worker side, `CompactionServiceCompactionJob` runs `DB::OpenAndCompact` work in an isolated output directory and serializes a `CompactionServiceResult`.

## Important APIs, Types, and Functions
The primary entry point is `CompactionJob::ProcessKeyValueCompactionWithCompactionService(SubcompactionState*)`. Worker-side methods include `CompactionServiceCompactionJob::Prepare`, `Run`, `CleanupCompaction`, `GetTableFileName`, and `RecordCompactionIOStats`. Serialization APIs are `CompactionServiceInput::Read/Write`, `CompactionServiceResult::Read/Write`, and debug-only `TEST_Equals` helpers.

The file defines option-style descriptors for `ColumnFamilyDescriptor`, `CompactionServiceInput`, `CompactionServiceOutputFile`, `CompactionJobStats`, `InternalStats::CompactionStats`, `InternalStats::CompactionStatsFull`, and `CompactionServiceResult`. `StatusSerializationAdapter` exposes private `Status` fields so status can be serialized through the same option framework. The only binary format version currently supported is `kOptionsString`.

## Control Flow
On the primary path, `ProcessKeyValueCompactionWithCompactionService` builds `CompactionServiceInput` from compaction output level, DB identity, input table file names, column-family name, snapshot sequence numbers, subcompaction bounds, and the pinned options file number. It serializes this request and calls `CompactionService::Schedule` with `CompactionServiceJobInfo`. Schedule responses can continue, abort, fail, or request local fallback.

After successful scheduling, the primary waits for a result. `kUseLocal` returns local fallback. `kAborted` and `kFailure` set the subcompaction status from either the returned `CompactionServiceResult` or an incomplete status. If wait succeeds but result deserialization fails, no remote output has been imported, so the primary calls `OnInstallation(kUseLocal)` and asks the caller to rerun locally. With a valid result, each remote output file is renamed from the service output path into the DB table path under a fresh primary-side file number. The code reconstructs `FileMetaData`, decodes smallest/largest internal keys, fills checksum, unique ID, temperature, table properties and tail size, adds outputs to normal or proximal `CompactionOutputs`, updates internal/job stats, records remote read/write ticks, and calls `OnInstallation(kSuccess)`.

On the worker path, `CompactionServiceCompactionJob::Prepare` converts request begin/end strings into optional slices and calls base `CompactionJob::Prepare`. `Run` logs the compaction, initializes input table properties, processes the single subcompaction locally, fsyncs the output directory, aggregates output and job stats, marks stats as remote/manual/full as appropriate, records I/O stats, and fills `CompactionServiceResult` with output file metadata and table properties.

## State and Persistence Behavior
Primary-side persistence is the atomic movement of remote-created table files into the primary DB's table namespace using new file numbers from `VersionSet`. Only after file rename and metadata reconstruction do outputs become candidates for installation into the new version. Failure during rename or file-size lookup marks the subcompaction failed and notifies `OnInstallation(kFailure)`. A deserialization failure before import is explicitly safe for local fallback because remote outputs remain isolated in the service-managed output directory.

Worker-side persistence is isolated to the output directory passed to `OpenAndCompact`. The result records every output file's name, size, sequence range, internal key bounds, ancestor/creation times, epoch, checksum information, paranoid hash, marked-for-compaction bit, unique ID, table properties, proximal-output flag, and file temperature. Serialization prepends a 32-bit format version and then uses option string serialization with unknown-option tolerance on read for forward compatibility.

## Dependencies and Integration Points
The file depends on `CompactionJob`, `CompactionState`, `SubcompactionState`, `CompactionOutputs`, `VersionSet`, table/file naming, `FileSystem` rename and size APIs, table properties, `OptionTypeInfo`, `ConfigOptions`, `Status`, statistics tickers, histograms, log buffers, thread status, and I/O stats. It integrates with public `CompactionService`, `CompactionServiceJobInfo`, `CompactionServiceOptionsOverride`, `OpenAndCompactOptions`, and DB secondary/open-and-compact code. It also coordinates with output verification, paranoid hash validation, per-key placement/proximal outputs, and local fallback behavior in `compaction_job.cc`.

## Risks and Edge Cases
Remote compaction has several sharp edges: malformed results must not install partial output, remote failures must preserve meaningful status, file-number collisions are avoided by allocating fresh primary numbers, and missing `file_size` from older workers is backfilled from the filesystem. The result serialization is broad and must stay compatible with `CompactionJobStats`, table properties, status representation, and `CompactionReason` count arrays. Whole-file input filtering can make iterator-count verification inaccurate, so the worker explicitly clears `has_accurate_num_input_records` when filtered input levels are present.

The TODO about abort/resume support notes that the service API cannot fully signal remote abort/resume yet. There is also a compatibility risk around arrays sized to `CompactionReason::kNumOfReasons - 1`, called out in a comment as a release workaround.

## Test Signals
`compaction_service_test.cc` is the primary behavioral suite for this file. `compaction_job_test.cc` has serialization round-trip coverage for `CompactionServiceInput` and `CompactionServiceResult`. Strong signals include successful local fallback on invalid result, failed installation on rename/verification errors, correct remote read/write statistics, preserved options-file behavior, correct proximal output stats, correct status propagation for schedule/wait failures, and successful checksum/table-property propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc

## Purpose
This file is the main DB-level regression suite for RocksDB compaction service behavior. It installs an in-process `CompactionService` implementation that calls `DB::OpenAndCompact`, then validates remote compaction scheduling, result installation, correctness under options/listeners/filters/merge/snapshots, failure handling, local fallback, corrupt output detection, concurrent compactions, and resumable remote compactions.

## Important APIs, Types, and Functions
`MyTestCompactionService` implements `CompactionService::Schedule`, `Wait`, `CancelAwaitingJobs`, and `OnInstallation`. It stores scheduled input blobs by generated job ID, runs `DB::OpenAndCompact`, propagates selected option overrides, supports injected schedule/wait/result statuses, counts compactions, records start/wait `CompactionServiceJobInfo`, and exposes the last deserialized `CompactionServiceResult`.

`CompactionServiceTest` derives from `DBTestBase` and provides `ReopenWithCompactionService`, `GenerateTestData`, `VerifyTestData`, statistics accessors, and optional remote listeners/table-property collectors. Helper test classes include `EventVerifier`, `PartialDeleteCompactionFilter`, `ResumableCompactionService`, `ResumableCompactionServiceTest`, and `ResumableCompactionKeyTypeTest`.

## Control Flow
Most tests reopen a DB with the test compaction service, create overlapping SSTs through `GenerateTestData`, trigger automatic or manual compaction, wait for compaction, and assert both logical data and service/result metadata. `BasicCompactions` validates ordinary remote execution and remote-vs-primary statistics, then injects worker failure and validates result status and unique ID verification after reopen. `ManualCompaction` exercises bounded and unbounded `CompactRange` plus non-default column families. Standalone range tombstone tests compare universal and leveled behavior and ensure whole-file filtering marks input record counts inaccurate.

Failure-oriented tests inject output file I/O errors, malformed remote result strings, schedule failures, wait aborts, corrupt remote output bytes, truncated output files, and verification flag combinations. Fallback tests force `kUseLocal` from schedule or wait and verify local compaction stats and data correctness. Cancellation tests cover remote-side cancellation, primary-side `CancelAllBackgroundWork`, and service `CancelAwaitingJobs`.

Integration tests validate preserved OPTIONS files for remote workers, event listener behavior on the worker, table property collectors, compaction filters, merge operators, snapshots, per-key placement/precluding last level, job info fields, subcompaction count, and concurrent `CompactFiles`. Resumable tests run multi-phase `OpenAndCompact` with `allow_resumption` toggled, forced file cuts, cancellation at specific keys/sequence numbers, and verification across delete, merge, single delete, range delete, file-boundary multi-version keys, wide columns, and timed puts.

## State and Persistence Behavior
The test service stages output under `dbname_/scheduled_job_id`, mirroring real remote output isolation. Primary installation is then validated through DB metadata, checksums, file existence, and data reads. Options-file tests ensure the primary pins the original options file number for remote compaction even when live options change and obsolete-file cleanup runs. Corruption/truncation tests mutate remote SST bytes before primary import to ensure primary-side verification catches bad output without treating the worker compaction itself as failed.

Resumable tests persist partial compaction progress in the output directory across `OpenAndCompact` calls when `allow_resumption` is true, or deliberately remove/recreate the directory for fresh-start phases. They use `REMOTE_COMPACT_RESUMED_BYTES` and file-write histograms to distinguish resumed work from full reprocessing.

## Dependencies and Integration Points
The suite depends on `DBTestBase`, `DB::OpenAndCompact`, `CompactionService`, `CompactionServiceInput/Result`, statistics tickers/histograms, sync points, file utilities, `SstFileWriter`, external ingestion, event listeners, table property collectors, merge operators, custom checksum factories, block-based table options, unique ID verification, and C++ threading. It exercises compaction service paths through normal DB APIs: automatic compaction, `CompactRange`, `CompactFiles`, `WaitForCompact`, external file ingestion, flush, delete range, snapshots, and column families.

## Risks and Edge Cases
The tests intentionally rely on sync points and in-process remote execution, so timing or callback ordering changes can make failures subtle. Some assertions depend on generated LSM shape, file counts, and stats values; tests pin compression or move files manually where needed. The fake service shares process state with the primary, so comments explicitly simulate file-number collisions and remote output directories that would be separate in production. Resumable tests force one key per output file for measurement simplicity, which is useful but not a production workload shape.

## Test Signals
This file is itself the strongest signal for `compaction_service_job.cc`. Passing it indicates remote compaction preserves data, propagates options and callbacks, imports metadata/stats correctly, handles local fallback, rejects corrupt output under configured verification, supports cancellation semantics, and resumes compaction only when requested and possible. The final `main` registers custom objects and installs stack traces before running all GoogleTests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_state.cc

## Purpose
This file implements the small aggregation helpers for `CompactionState`, the job-wide state container shared by local and remote compaction jobs. It computes global output key bounds and rolls subcompaction stats into job-level structures.

## Important APIs, Types, and Functions
Implemented methods are `CompactionState::SmallestUserKey`, `LargestUserKey`, and `AggregateCompactionStats`. Each delegates to ordered `SubcompactionState` entries stored in `sub_compact_states`.

## Control Flow
`SmallestUserKey` scans subcompactions in increasing key-range order and returns the first non-empty subcompaction output bound. `LargestUserKey` scans in reverse order and returns the last non-empty output bound. `AggregateCompactionStats` iterates every subcompaction, calls `AggregateCompactionOutputStats` into `InternalStats::CompactionStatsFull`, and adds each `CompactionJobStats` into the job aggregate.

## State and Persistence Behavior
No state is persisted here. The functions read output metadata already accumulated in each subcompaction and write aggregate in-memory stats used later for event listeners, compaction result serialization, and internal metrics. Empty output returns `Slice{nullptr, 0}` to distinguish no finished output from a real key.

## Dependencies and Integration Points
The file depends on `compaction_state.h` and, through it, `Compaction`, `SubcompactionState`, `InternalStats`, and `CompactionJobStats`. It integrates with `CompactionJob` and `CompactionServiceCompactionJob` after subcompaction execution.

## Risks and Edge Cases
Correctness depends on the invariant that `sub_compact_states` are ordered by increasing key range. If a subcompaction produces no output, the bound scans skip it. Stats aggregation includes whatever each subcompaction reports, so abandoned-output stat caveats from `SubcompactionState` can flow upward.

## Test Signals
Signals are indirect through compaction job tests, event-listener stats checks, compaction service result stats, and any assertions on smallest/largest output key prefixes. Multi-subcompaction tests are particularly relevant because they validate ordered bound aggregation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_state.h

## Purpose
This header defines `CompactionState`, the job-wide holder for a `Compaction`, its subcompaction states, and the aggregate status. It is used by both `CompactionJob` and `CompactionServiceCompactionJob` to keep sub-job outputs and stats under one compaction-level object.

## Important APIs, Types, and Functions
`CompactionState` exposes `Compaction* const compaction`, `std::vector<SubcompactionState> sub_compact_states`, and `Status status`. Its methods are `AggregateCompactionStats`, `SmallestUserKey`, and `LargestUserKey`. The constructor requires a non-owning `Compaction*`.

## Control Flow
The header establishes the ordering contract: subcompaction states must be stored in increasing key-range order. Callers fill `sub_compact_states` during compaction preparation, execute them, and then use the declared aggregation/bound helpers after output files close.

## State and Persistence Behavior
`CompactionState` owns the vector of `SubcompactionState` objects but not the `Compaction` pointer. It carries in-memory execution status and output metadata until the compaction job commits or cleans up. Persistence occurs elsewhere through version edits and output file installation.

## Dependencies and Integration Points
The header includes `compaction.h`, `subcompaction_state.h`, and `internal_stats.h`. It integrates with local compaction jobs, compaction service jobs, event listener construction, stats aggregation, and output metadata installation.

## Risks and Edge Cases
Because `compaction` is a raw non-owning pointer, lifetime must be managed by the owning compaction job. The ordered-subcompaction invariant is not enforced by the type system but is required for key-bound helpers. Any move behavior of subcompaction state must preserve output pointers, which is handled in `SubcompactionState`.

## Test Signals
Coverage comes from successful local/remote compactions, subcompaction tests, compaction-service stats checks, and assertions on output key prefixes. Bugs usually appear as wrong aggregate stats, wrong smallest/largest output keys, or cleanup/install behavior failing after one subcompaction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/file_pri.h -->
# sources/storage-engines/rocksdb/db/compaction/file_pri.h

## Purpose
This header defines `FileTtlBooster`, a helper that boosts compaction priority for files approaching TTL-based compaction thresholds. It avoids overloading `FileMetaData::compensated_file_size` for TTL urgency, because that size is broadly used as a file-size proxy.

## Important APIs, Types, and Functions
`FileTtlBooster` has a constructor taking current time, TTL, number of non-empty levels, and the candidate level. `GetBoostScore(FileMetaData*)` returns an integer multiplier-like score: `1` when disabled or not old enough, and a linearly increasing value after the level-specific boost start age. Private fields are `enabled_`, `current_time_`, `boost_age_start_`, and `boost_step_`.

## Control Flow
Boosting is disabled when TTL is zero, the level is L0, or the level is at/after the last non-empty level. Otherwise, the constructor starts boosting after half the TTL plus a level-dependent range, with lower levels starting later. The range shrinks by right-shifting according to distance from the last non-empty level, and `boost_step_` is guarded to at least one. `GetBoostScore` reads the file's oldest ancestor time, computes age if it is in the past, and returns `(age - boost_age_start_) / boost_step_ + 1` once the file is old enough.

## State and Persistence Behavior
The class is stateless beyond constructor-derived thresholds and does not persist anything. It reads `FileMetaData::TryGetOldestAncesterTime`, so its behavior reflects persisted or propagated file creation/ancestor timestamps.

## Dependencies and Integration Points
The header includes `<algorithm>` and `db/version_edit.h` for `FileMetaData`. It is intended for compaction priority calculations where file ordering can incorporate TTL urgency without changing file-size accounting.

## Risks and Edge Cases
The comments acknowledge the formula is intentionally simple and production-tunable. Shifting is capped at 63 to avoid undefined behavior for many levels. Very large or manipulated current times can overflow boost arithmetic, which the code explicitly ignores for simplicity. Misspellings in comments and the `TryGetOldestAncesterTime` API name are existing code style, not functional issues.

## Test Signals
Signals should come from compaction-priority tests that configure TTL compaction and inspect picked files by age/level. Important cases are TTL zero, L0, last level, files newer than boost start, and files very close to the TTL threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/file_pri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc -->
# sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc

## Purpose
This file implements the fixed-prefix SST partitioner and factory registration. The partitioner requests output file boundaries when adjacent user keys differ in their first `len_` bytes, enabling compaction output files to be partitioned by fixed key prefix.

## Important APIs, Types, and Functions
`SstPartitionerFixedPrefixFactory` registers the configurable `length` option in its constructor, creates `SstPartitionerFixedPrefix` instances, and is exposed through `NewSstPartitionerFixedPrefixFactory`. `SstPartitionerFixedPrefix::ShouldPartition` compares truncated previous/current user keys and returns `kRequired` or `kNotRequired`. `CanDoTrivialMove` reuses the same logic to determine whether an input file's smallest/largest keys remain within one fixed prefix. `SstPartitionerFactory::CreateFromString` registers built-in factories once and loads a shared object/factory from string.

## Control Flow
`ShouldPartition` copies the previous and current user key slices, caps each slice size at `len_`, compares them, and requires a split when the fixed prefixes differ. `CanDoTrivialMove` builds a `PartitionerRequest` from smallest/largest user keys and treats no required split as trivial-move-compatible. Factory string creation uses `std::call_once` to register `SstPartitionerFixedPrefixFactory::kClassName()` with the default `ObjectLibrary`, then calls `LoadSharedObject`.

## State and Persistence Behavior
The only persistent configuration is the factory's `len_` option as part of RocksDB options serialization/configuration. The partitioner itself has no durable state; it influences how compaction/table-builder output is split into SST files.

## Dependencies and Integration Points
The file depends on `rocksdb/sst_partitioner.h`, customizable utilities, object registry, and options type descriptors. It integrates with compaction output file cutting, trivial move decisions, options parsing, custom object loading, and any user configuration that names the fixed-prefix partitioner.

## Risks and Edge Cases
A zero prefix length means all keys share the empty prefix, so partitioning is never required. If keys are shorter than `len_`, their full key is compared. The implementation mutates local `Slice::size_` copies, not underlying keys. Trivial-move eligibility is only prefix-based and does not check other compaction constraints.

## Test Signals
Relevant tests should assert partition decisions across equal/different prefixes, short keys, zero length, options-string factory creation, and trivial-move compatibility. Downstream compaction tests can observe output file boundaries created by the partitioner.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc -->
# sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc

## Purpose
This file implements behavior for `SubcompactionState`, the per-key-range state object used by each subcompaction. It aggregates output stats, exposes combined normal/proximal outputs, cleans up abandoned files, computes output key bounds, and routes iterator output into the correct output group.

## Important APIs, Types, and Functions
Implemented methods are `AggregateCompactionOutputStats`, `GetOutputs`, `Cleanup`, `SmallestUserKey`, `LargestUserKey`, and `AddToOutput`. The methods operate on the two `CompactionOutputs` members declared in the header: normal output-level files and optional proximal-level files for per-key placement.

## Control Flow
`AggregateCompactionOutputStats` asserts builders are closed, adds normal output stats to `internal_stats.output_level_stats`, and, when proximal outputs exist, marks `has_proximal_level_output` and adds proximal stats. `GetOutputs` returns an `OutputIterator` spanning proximal then normal outputs. `Cleanup` closes/clears output builders, and if either subcompaction or overall compaction failed, releases any output files from table cache as obsolete using the compaction's uncache aggressiveness.

`SmallestUserKey` and `LargestUserKey` compare bounds from normal and proximal outputs when both exist, using the column family's user comparator. `AddToOutput` switches `current_outputs_` based on the caller's `use_proximal_output` decision and delegates to `CompactionOutputs::AddToOutput`.

## State and Persistence Behavior
The file manages in-memory output metadata and cache cleanup, not manifest persistence. Successful outputs are later added to a `VersionEdit`; failed outputs are cleaned up and evicted from table cache so uncommitted files are not served. `io_status.PermitUncheckedError()` intentionally suppresses unchecked-status diagnostics during cleanup; the comment notes `io_status` is not handled like `status`.

## Dependencies and Integration Points
It depends on `subcompaction_state.h`, `rocksdb/sst_partitioner.h`, `TableCache::ReleaseObsolete`, `CompactionOutputs`, `OutputIterator`, `CompactionIterator`, range deletion aggregation, and `InternalStats`. It integrates with local compaction jobs, compaction service jobs, per-key placement, cache eviction, and event/job stats.

## Risks and Edge Cases
Stats can include abandoned output files, as noted by the FIXME. Bound calculations must handle either output group being empty. Cleanup only releases cache entries on status failure; durable file deletion is handled elsewhere by obsolete-file processing. `current_outputs_` must remain valid after moves, which is handled in the move constructor in the header.

## Test Signals
Signals include remote per-key placement tests that check output/proximal stats, subcompaction tests that require multiple outputs, failed compaction tests that ensure uncommitted outputs are not installed, and data correctness tests after proximal and normal outputs are mixed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h -->
# sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h

## Purpose
This header defines `SubcompactionState`, the state and output container for one subcompaction key range. It is shared by normal compaction and compaction service jobs and supports both ordinary output-level files and proximal-level outputs for per-key placement.

## Important APIs, Types, and Functions
Public fields include the non-owning `const Compaction* compaction`, optional inclusive `start` and exclusive `end` bounds, `Status status`, `IOStatus io_status`, notification flag, `CompactionJobStats`, and `sub_job_id`. Output methods include `GetOutputs`, mutable output accessors, `Outputs`, `OutputStats`, `Current`, `AddOutputsEdit`, `AddToOutput`, `CloseCompactionFiles`, `RemoveLastEmptyOutput`, `CleanupOutputs`, and `Cleanup`. Range tombstone support is exposed through `AssignRangeDelAggregator`, `RangeDelAgg`, and `HasRangeDel`. Job-event helpers include `BuildSubcompactionJobInfo`, `GetWorkerCPUMicros`, and progress getters/setters.

## Control Flow
Construction initializes normal and proximal `CompactionOutputs` and sets an output split key on normal outputs for round-robin support. Copy is disabled; move construction transfers outputs, aggregator, status, stats, and resets `current_outputs_` to point at the moved-to normal or proximal member. `AddToOutput` chooses the active output group for each compaction iterator key. `CloseCompactionFiles` closes proximal outputs first when per-key placement is enabled, then normal outputs, always attempting close even when current status is non-OK so builders are not leaked.

`AddOutputsEdit` writes proximal outputs to `compaction->GetProximalLevel()` and normal outputs to `compaction->output_level()`. `BuildSubcompactionJobInfo` packages column-family, level, reason, compression, stats, and blob compression information for event listeners.

## State and Persistence Behavior
The class owns `CompactionOutputs` objects that hold builders, output metadata, table properties, validators, and stats until the compaction is installed or cleaned up. It owns a `CompactionRangeDelAggregator` used to route range tombstones to the appropriate output. It does not own the `Compaction` pointer. Persistence happens when output files are closed and later added to `VersionEdit`; cleanup abandons builders and cache entries for failed work.

## Dependencies and Integration Points
The header depends on blob file additions and garbage metering, `Compaction`, `CompactionIterator`, `CompactionOutputs`, `InternalStats`, `OutputValidator`, and `CompactionRangeDelAggregator`. It integrates with compaction job preparation/execution, event listener begin/completion notifications, range deletion handling, per-key placement/preclude-last-level logic, output validation, and compaction service result import/export.

## Risks and Edge Cases
The two-output-group design makes pointer correctness important: `current_outputs_` must always point to a member of the current object, especially after moves. Proximal-output access asserts that the compaction supports per-key placement. Range deletion aggregators are single-assignment. Output closing can open new files while finalizing range deletions, so it must run even after earlier errors. The `start`/`end` optional slices are non-owning views, so their source storage must outlive preparation/use.

## Test Signals
Coverage comes from subcompaction tests, per-key placement tests, compaction service `PrecludeLastLevel`, remote event listener tests, range deletion compaction tests, and failure cleanup tests. Key signals are correct output levels in version edits, accurate normal/proximal stats, valid subcompaction job info, no stale cache use after failed compactions, and correct key bounds from mixed output groups.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/subcompaction_state.h -->
