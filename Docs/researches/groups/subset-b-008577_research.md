# Research Group: subset-b-008577

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_test.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_job_test.cc

## Purpose
This file is a focused unit/integration test suite for RocksDB's `CompactionJob`. It builds real `VersionSet` and MANIFEST state, synthesizes input SST metadata with either mock tables or block-based tables, runs `CompactionJob::Prepare`, `Run`, and `Install`, and verifies the resulting files, metadata, stats, IO priority, serialization, timestamp garbage collection, and output splitting behavior. It is especially important for compaction correctness because it validates the interaction between the iterator-level compaction semantics and durable version edits.

## Important APIs, Types, and Functions
The central fixture is `CompactionJobTestBase`, which owns DB paths, options, a `VersionSet`, table cache, write controller, mock table factory, error handler, and helper state such as `full_history_ts_low_`. Key helpers include `NewDB`, `AddMockFile`, `CreateTable`, `RunCompaction`, `RunLastLevelCompaction`, `VerifyTables`, `CreateTwoFiles`, `SetLastSequence`, `KeyStr`, and blob-index helpers `BlobStr`, `BlobStrTTL`, and `BlobStrInlinedTTL`.

The anonymous namespace defines `VerifyInitializationOfCompactionJobStats` plus `MockTestWritableFile`, `MockTestRandomAccessFile`, and `MockTestFileSystem`, which assert compaction read/write IO priorities. Test classes split behavior by configuration: `CompactionJobTest` uses bytewise keys and mock tables, `CompactionJobTimestampTest` uses a U64 timestamp comparator, `CompactionJobTimestampTestWithBbTable` uses block-based tables for subcompaction anchor behavior, and `CompactionJobIOPriorityTest` exercises rate-limiter priority.

## Control Flow
Most tests call `NewDB`, create one or more input files through `AddMockFile`, set sequence state, then call `RunCompaction`. `RunCompaction` converts per-level file vectors into `CompactionInputFiles`, gathers grandparents from the level after the output level, constructs a `Compaction`, initializes a `JobContext` with snapshots and write-conflict snapshot state, constructs `CompactionJob`, checks initial stats, then runs `Prepare`, `Run`, and `Install` under the expected mutex transitions. Verification reads current version metadata and either compares mock-table outputs through `MockTableFactory` or opens block-based table files and scans them with an internal iterator.

The test cases cover basic compaction, deletions, overwritten values, last-level sequence zeroing, non-last-level sequence retention, associative and non-associative merge operands, compaction filter interactions, single-delete contracts across snapshots, blob index oldest-file metadata, per-key placement/proximal output range tracking, remote compaction input/result serialization, output cuts caused by `max_compaction_bytes`, grandparent skipping, grandparent-boundary alignment, same-user-key split safety, user-defined timestamp GC, subcompaction partitioning, and IO priorities under normal, delayed, and stopped write-controller states.

## State and Persistence Behavior
The fixture writes actual MANIFEST records, `CURRENT`, table files, and version edits into a per-thread test DB directory. `AddMockFile` computes smallest/largest keys, sequence ranges, file sizes, oldest blob file numbers, and epoch numbers before calling `VersionSet::LogAndApply`. `RunCompaction` validates installed version state by reading `LevelFiles(output_level)` after `Install`. For block-based tables, persisted SST contents are reopened through `RandomAccessFileReader` and `TableReader`, so the test covers real table bytes instead of only in-memory mocks.

Stats and metadata are persistent signals. The tests check `CompactionJobStats` initialization, input/output file counts, corrupt-key counters in disabled corruption cases, output file metadata such as `oldest_blob_file_number`, table properties preserved by remote compaction result serialization, file checksums, unique IDs, and file temperature. Timestamp tests use `full_history_ts_low_` to drive garbage collection and verify the surviving internal keys after compaction.

## Dependencies and Integration Points
The file integrates `CompactionJob` with `Compaction`, `VersionSet`, `ColumnFamilyData`, `VersionEdit`, `WritableFileWriter`, `RandomAccessFileReader`, table factories, blob index encoding, merge operators, compaction filters, `ErrorHandler`, `EventLogger`, `JobContext`, snapshot handling, custom comparators with timestamps, `WriteController`, and RocksDB's sync point framework. It also exercises `CompactionServiceInput` and `CompactionServiceResult` serialization contracts used by remote compaction service code.

## Risks and Edge Cases
High-risk behavior includes preserving user-key atomicity when output files are cut, not dropping versions needed by snapshots or write-conflict snapshots, preserving merge operand order, filtering merge operands without corrupting results, handling single-delete semantics, keeping range/output boundaries compatible with grandparent overlap heuristics, propagating IO status, and using correct IO priorities under write pressure. The disabled corruption tests document known or undesirable corrupt-key edge cases rather than active pass signals. Randomized serialization tests can expose encoding drift, but failures may require reproducing random input values.

## Test Signals
This file is itself the primary test signal for the compaction job path. Passing it indicates that `CompactionJob` can be run against real version metadata and table files, installs outputs correctly, splits outputs at expected boundaries, serializes remote compaction input/results compatibly, preserves blob metadata, applies timestamp GC, partitions subcompactions, and chooses rate-limiter priorities according to write-controller state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_job_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_outputs.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_outputs.cc

## Purpose
This file implements `CompactionOutputs`, the per-subcompaction output manager used by `CompactionJob`. It owns the active table builder/file writer lifecycle, records output file metadata and stats, decides when an output file should be cut, writes point keys and range tombstones, accounts blob garbage, captures table properties, and prepares output boundary state needed by later version installation.

## Important APIs, Types, and Functions
The main methods are `NewBuilder`, `Finish`, `WriterSyncClose`, `UpdateFilesToCutForTTLStates`, `UpdateGrandparentBoundaryInfo`, `GetCurrentKeyGrandparentOverlappedBytes`, `ShouldStopBefore`, `AddToOutput`, `AddRangeDels`, `FillFilesToCutForTtl`, and the constructor. The anonymous helper `SetMaxSeqAndTs` builds internal range-deletion boundary keys with maximum timestamp bytes when user-defined timestamps are enabled.

`Finish` finalizes the table builder, attaches seqno-to-time table properties, extracts timestamp table properties into `FileMetaData`, records file size, tail size, compaction-needed flag, write/pre-compression bytes, output-file count, and worker CPU micros. `WriterSyncClose` prepares compaction IO options, syncs and closes the writer, then stores checksum metadata in the output file metadata.

## Control Flow
`AddToOutput` is called for each `CompactionIterator` output key. It first skips range deletion sentinel handling for bottommost-level cases where tombstones may be dropped. It calls `ShouldStopBefore`; if a current builder exists and a cut is needed, it invokes the caller-provided close function, resets grandparent overlap state, and records a range tombstone lower bound when the next output starts with a range tombstone sentinel. It then opens a new output through the caller-provided open function if needed. Point keys are validated by `OutputValidator`, added to the table builder, counted in stats, optionally passed through `BlobGarbageMeter`, tracked for preferred sequence numbers, and used to update `FileMetaData` boundaries.

`ShouldStopBefore` always updates grandparent and TTL-cut state for non-L0 outputs before checking the active builder. It cuts on TTL isolation, required partitioner boundaries, target file size, round-robin output split key, excessive current-output plus grandparent overlap against `max_compaction_bytes`, large skippable grandparent gaps, and dynamic pre-cuts at grandparent boundaries. It deliberately avoids splitting L0 outputs and avoids cutting before the first key because no builder exists yet.

`AddRangeDels` computes lower and upper internal-key guards for the current output file, including subcompaction start/end boundaries and next-table minimum key. It iterates a bounded `CompactionRangeDelAggregator`, filters tombstones by per-key-placement sequence range, clamps tombstone start/end keys to the output range, drops obsolete tombstones at bottommost or when no lower-level key range exists, adds surviving tombstones to the builder, updates file range boundaries, and estimates compensated range deletion size for non-bottommost output.

## State and Persistence Behavior
Persistent state produced here includes SST bytes, table properties, file checksum fields, file size/tail size, smallest/largest keys, sequence range, timestamp-persisted metadata, oldest ancestor time table properties, and compensated range deletion size. In-memory output state includes the builder, file writer, list of outputs, blob file additions, blob garbage meter, output file paths for abort cleanup, stats, partitioner state, round-robin split state, TTL-cut file cursor, grandparent overlap cursor, and level pointers for range tombstone existence checks.

## Dependencies and Integration Points
The implementation depends on `NewTableBuilder`, `WritableFileWriter`, `TableBuilderOptions`, `CompactionIterator`, `CompactionRangeDelAggregator`, `Compaction`, `VersionSet::ApproximateSize`, `OutputValidator`, blob garbage metering, user comparators with optional timestamps, internal key encoding/parsing, sync points, and compaction/job callbacks for opening and closing files. It is tightly coupled to `CompactionJob` because open/close functions own file-number allocation and manifest-facing installation while `CompactionOutputs` owns builder-local state.

## Risks and Edge Cases
The highest-risk code is boundary math. Incorrect lower/upper guards in `AddRangeDels` can lose tombstone coverage or create overlapping output files. Same-user-key grandparent boundaries must not split versions in a way that breaks reads. Blob-aware per-key placement uses sequence ranges, so tombstone filtering must match output placement. TTL cuts depend on file oldest-ancestor time and can produce extra small files if thresholds are wrong. `WriterSyncClose` only stores checksum metadata when prior status and sync/close status are OK, so error precedence matters. Range tombstone compensated size can double count tombstones spanning outputs, which is noted in comments.

## Test Signals
`compaction_job_test.cc` directly exercises output cutting for max compaction bytes, skippable grandparents, grandparent-boundary alignment, and same-key boundaries. Timestamp tests validate range/key GC interaction. Blob metadata tests cover oldest blob file tracking, and IO-priority tests validate file writer/read paths. Additional coverage likely comes from broader RocksDB compaction, range deletion, blob DB, and partitioner tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_outputs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_outputs.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_outputs.h

## Purpose
This header declares `CompactionOutputs`, the state container and control surface for files generated by a subcompaction. It defines how `CompactionJob` opens, fills, finishes, closes, accounts, and iterates output files. The header also declares callback types used to decouple output-state transitions from job-level file creation and installation logic.

## Important APIs, Types, and Functions
`CompactionFileOpenFunc` and `CompactionFileCloseFunc` are callback aliases used by `AddToOutput` and `CloseOutput`. `CompactionOutputs::Output` packages `FileMetaData`, `OutputValidator`, finished/proximal flags, and optional `TableProperties`. Public methods expose output vectors, builder/file-writer assignment, blob file additions, output file paths, blob garbage metering, stats updates, table-property updates, `Finish`, `WriterSyncClose`, `SmallestUserKey`, `LargestUserKey`, `RemoveLastEmptyOutput`, `RemoveLastOutput`, `GetMetaData`, `NumEntries`, `GetWorkerCPUMicros`, `ResetBuilder`, `AddRangeDels`, and `SetNumOutputRecords`.

The private interface, used by `SubcompactionState` and implementation code, includes `FillFilesToCutForTtl`, `SetOutputSlitKey` (a misspelled but functional setter for local output split key), `ShouldStopBefore`, `Cleanup`, TTL and grandparent state update helpers, `AddToOutput`, `CloseOutput`, and `current_output`.

`OutputIterator` is a small pre-C++20 join helper for iterating the concatenation of last-level and proximal-level outputs.

## Control Flow
The expected lifecycle is: construct with a `Compaction` and proximal-output flag, optionally assign a `WritableFileWriter`, call `NewBuilder`, repeatedly call `AddToOutput`, close the active builder through `CloseOutput` or job close callbacks, call `Finish` and `WriterSyncClose` as part of close, and then let install logic consume the output metadata and blob additions. `CloseOutput` also handles the special case where a subcompaction produced only range deletions: if no builder/output exists but the range deletion aggregator is non-empty, it opens an output before closing.

The class separates last-level and proximal-level output state. Proximal outputs assert that blob additions and blob garbage metering are not used because BlobDB does not support per-key placement there. Output file paths are tracked independently from retained outputs so abort cleanup can delete orphan files even if an empty output was removed from `outputs_`.

## State and Persistence Behavior
Persistent metadata is held in `outputs_` as `FileMetaData` plus table properties and checksum fields populated in implementation code. `stats_` accumulates output records, file counts, SST bytes, pre-compression bytes, blob output files, and blob bytes. `blob_file_additions_` records blob files created by compaction. `output_file_paths_` records SST and blob paths for cleanup on abort. Builder and writer pointers are transient and must be reset or abandoned.

Splitting state includes partitioner last key, `is_split_`, local split key, TTL file vector and cursors, grandparent index/gap/overlap counters, range tombstone lower bound, and `level_ptrs_` used for repeated `KeyRangeNotExistsBeyondOutputLevel` calls.

## Dependencies and Integration Points
The header pulls in `Compaction`, `CompactionIterator`, `BlobGarbageMeter`, `InternalStats`, `OutputValidator`, `FileMetaData`, `TableBuilder`, `WritableFileWriter`, `SstPartitioner`, `CompactionRangeDelAggregator`, and table/blob metadata types. `CompactionJob` and `SubcompactionState` are the main consumers. The class also integrates with remote compaction through explicit `UpdateTableProperties` from pre-populated properties.

## Risks and Edge Cases
State ownership is subtle: builder and writer lifetimes are independent but coordinated by job callbacks. Removing empty outputs must not lose file paths needed for cleanup. Proximal-output assertions prevent unsupported blob placement, but callers must preserve that invariant. `OutputIterator` implements a minimal iterator protocol and assumes simple range-for usage; it is not a general STL iterator. The misspelled `SetOutputSlitKey` name is a maintainability risk because it can hide call-site searches for "Split".

## Test Signals
Tests that validate compaction output counts, file boundaries, blob metadata, aborted/empty output cleanup, remote compaction table properties, and proximal-level output ranges are the relevant signals. `compaction_job_test.cc` covers many of these through real `CompactionJob` execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_outputs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker.cc

## Purpose
This file implements the compaction picker base-class logic shared by RocksDB compaction styles. It does not contain the full level/universal picker policies, but it provides common machinery for compression selection, intra-L0 cost-based selection, clean-cut expansion, conflict detection against running compactions, manual compact-range and compact-files creation, sanitizing user-specified file sets, registering/unregistering running compactions, and selecting files marked for compaction.

## Important APIs, Types, and Functions
Top-level helpers are `PickCostBasedIntraL0Compaction`, `GetCompressionType`, and `GetCompressionOptions`. `CompactionPicker` methods implemented here include `ReleaseCompactionFiles`, three `GetRange` overloads, `ExpandInputsToCleanCut`, `RangeOverlapWithCompaction`, `FilesRangeOverlapWithCompaction`, `AreFilesInCompaction`, `PickCompactionForCompactFiles`, `GetCompactionInputsFromFileNumbers`, `IsRangeInCompaction`, `SetupOtherInputs`, `GetGrandparents`, `PickCompactionForCompactRange`, `SanitizeCompactionInputFilesForAllLevels`, `SanitizeAndConvertCompactionInputFiles`, `RegisterCompaction`, `UnregisterCompaction`, `PickFilesMarkedForCompaction`, and `GetOverlappingL0Files`.

In debug builds, `AssertCleanCut` verifies that expanded non-L0 inputs do not leave adjacent same-user-key files unselected. The local helper `HaveOverlappingKeyRanges` is used when sanitizing manually specified file numbers against column-family metadata.

## Control Flow
Manual file compaction starts with `SanitizeAndConvertCompactionInputFiles`: it validates output level bounds, ensures inputs are non-empty, expands the input set through `SanitizeCompactionInputFilesForAllLevels`, rejects missing files, files already compacting, and upward compactions, converts file numbers into `CompactionInputFiles`, then rejects overlap with running output compactions. `PickCompactionForCompactFiles` assumes the sanitized set is still protected by the DB mutex, chooses compression, constructs a `Compaction`, and registers it.

Manual range compaction through `PickCompactionForCompactRange` has a special universal all-level path and a normal path. The normal path finds overlapping input-level files, optionally limits non-L0 range size to `max_compaction_bytes`, handles bottommost optimized compaction file-number filtering, expands to a clean cut, computes `compaction_end` for partial progress, sets output level, calls `SetupOtherInputs` to include overlapping output-level files, checks running compaction conflicts, computes grandparents, constructs/registers the `Compaction`, and recomputes compaction score.

Automatic or style-specific pickers use shared helpers. `SetupOtherInputs` includes output-level overlaps, expands them to clean cuts, then opportunistically expands start-level inputs when doing so does not increase output-level inputs and stays under a softened size limit. `PickFilesMarkedForCompaction` tries a random marked file first, then sequentially, skipping files according to a caller predicate and respecting level-0 conflicts. `GetOverlappingL0Files` expands an L0 seed to all overlapping L0 files and checks output-level conflict.

## State and Persistence Behavior
This file does not persist data directly. Its state changes are in-memory scheduling state: `level0_compactions_in_progress_`, `compactions_in_progress_`, `being_compacted` conflict decisions, compaction score recomputation, and `Compaction` objects whose later execution will write version edits. Compression selection persists indirectly by configuring output files. Sanitization uses manifest-derived `ColumnFamilyMetaData` and `VersionStorageInfo` to keep user-selected compactions legal.

## Dependencies and Integration Points
The implementation depends on `VersionStorageInfo`, `Version`, `ColumnFamilyMetaData`, `FileMetaData`, `Compaction`, `MutableCFOptions`, `MutableDBOptions`, `CompactRangeOptions`, `CompactionOptions`, comparators with timestamp-insensitive comparisons, file-name parsing, logging, sync points, and random selection. It is called by DB manual compaction APIs, automatic compaction-style pickers, external SST ingestion conflict checks, and compaction scheduling logic guarded by the DB mutex.

## Risks and Edge Cases
Clean-cut expansion is critical: leaving one version of a user key behind while compacting another can return stale values or reorder merge operands. Running-output overlap checks must include proximal-level outputs when per-key placement is enabled. L0 is special because files overlap and are ordered by recency, so range calculations and conflict rules differ. Manual range compactions can be partial, and incorrect `compaction_end` handling can stall or skip work. Sanitization based on external file numbers must reject missing, compacting, upward, and overlapping files with clear errors.

## Test Signals
Signals come from compact-range, compact-files, level compaction, universal compaction, FIFO, marked-file, ingestion, and per-key-placement tests. `compaction_job_test.cc` covers downstream consequences of grandparent choice and output splitting, while picker-specific tests elsewhere should validate clean cuts, conflict status, manual compaction partial progress, and sanitization errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker.h

## Purpose
This header defines the abstract `CompactionPicker` interface and common picker helpers for RocksDB's LSM compaction scheduling. It is the contract implemented by concrete compaction styles and used by DB scheduling/manual compaction code to ask whether compaction is needed, pick automatic compactions, pick manual range/file compactions, track running compactions, and validate user-selected input files.

## Important APIs, Types, and Functions
The primary abstract methods are `PickCompaction` and `NeedsCompaction`; `PickCompactionForCompactRange` is virtual with a shared default implementation. `MaxOutputLevel` defaults to the last configured level. Non-virtual APIs include `SanitizeAndConvertCompactionInputFiles`, `ReleaseCompactionFiles`, `AreFilesInCompaction`, `PickCompactionForCompactFiles`, `GetCompactionInputsFromFileNumbers`, `IsLevel0CompactionInProgress`, `IsCompactionInProgress`, `RangeOverlapWithCompaction`, three `GetRange` overloads, `ExpandInputsToCleanCut`, `IsRangeInCompaction`, `FilesRangeOverlapWithCompaction`, `SetupOtherInputs`, `GetGrandparents`, `PickFilesMarkedForCompaction`, `GetOverlappingL0Files`, `RegisterCompaction`, and `UnregisterCompaction`.

`NullCompactionPicker` is a concrete no-op picker that always returns no compaction and `NeedsCompaction == false`. Free functions `PickCostBasedIntraL0Compaction`, `GetCompressionType`, and `GetCompressionOptions` expose shared policy helpers.

## Control Flow
Concrete style pickers call protected/common helpers to build legal `Compaction` instances. A typical style-specific flow chooses start-level files, calls `ExpandInputsToCleanCut`, calls `SetupOtherInputs`, optionally gathers grandparents, constructs a `Compaction`, and registers it. Manual compaction flows use `SanitizeAndConvertCompactionInputFiles` followed by `PickCompactionForCompactFiles`, or call `PickCompactionForCompactRange` directly.

The running compaction sets are part of the picker contract. Any created compaction should be registered so future picks avoid overlapping output ranges and avoid concurrent L0 compactions where unsupported. `ReleaseCompactionFiles` unregisters and resets next-compaction index on failure.

## State and Persistence Behavior
The header's state is transient scheduler state, not durable storage. `level0_compactions_in_progress_` and `compactions_in_progress_` are protected by the DB mutex. Durable effects occur only after returned `Compaction` objects are executed by compaction jobs and installed into the manifest. The picker does, however, decide output level, compression settings, output path, target file size, max compaction bytes, and input file sets, which shape persistent SST layout.

## Dependencies and Integration Points
The interface depends on `Compaction`, `VersionStorageInfo`, `Version`, `CompactionInputFiles`, `SnapshotChecker`, `LogBuffer`, `CompactRangeOptions`, `CompactionOptions`, `MutableCFOptions`, `MutableDBOptions`, `ImmutableOptions`, and RocksDB `Status`. It is consumed by DBImpl scheduling paths, manual `CompactRange` and `CompactFiles`, concrete level/universal/FIFO pickers, and tests that inspect running compaction state.

## Risks and Edge Cases
API users must hold the DB mutex for methods that inspect or mutate running compaction state. Clean-cut requirements are easy to violate when adding new picker styles. `FilesRangeOverlapWithCompaction` requires both output and proximal level awareness for per-key placement. `PickCompactionForCompactFiles` assumes no mutex release between sanitization and compaction creation; violating that assumption can race with other compactions. `NullCompactionPicker` is useful for disabled compactions but can hide required manual behavior if used accidentally.

## Test Signals
Expected coverage includes style-specific picker tests, DB manual compaction tests, compact-files input validation tests, and conflict tests for concurrent compactions. Public signals are returned `Status` messages from sanitization, absence/presence of picked `Compaction`, and correct registration/unregistration of running work.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.cc

## Purpose
This file implements `FIFOCompactionPicker`, the compaction picker for FIFO-style column families. FIFO compaction primarily deletes old files instead of merging levels, but this implementation also supports TTL-based deletion, size/capacity deletion, multi-level migration cleanup, file-temperature changes, and optional intra-L0 compaction to reduce file count. Local behavior includes blob-aware capacity accounting through `max_data_files_size` and a ratio-based intra-L0 compaction strategy for BlobDB-like workloads.

## Important APIs, Types, and Functions
Local helpers are `GetTotalFilesSize`, `GetEffectiveSizeAndLimit`, and `GetEffectiveMax`. Public overrides are `NeedsCompaction`, `PickCompaction`, and `PickCompactionForCompactRange`. Private pickers are `PickTTLCompaction`, `PickSizeCompaction`, `PickTemperatureChangeCompaction`, `PickIntraL0Compaction`, and `PickRatioBasedIntraL0Compaction`.

`NeedsCompaction` uses level-0 compaction score. `PickCompaction` tries TTL deletion first, then size deletion, intra-L0 file reduction, and temperature-change compaction. It registers the selected compaction, if any. FIFO manual compact-range delegates to the same automatic picking flow and only supports input/output level 0.

## Control Flow
`PickTTLCompaction` scans L0 from oldest to newest, using table properties and `FileMetaData::TryGetNewestKeyTime` to find files whose estimated newest key time is older than `ttl`. It computes remaining effective size. In blob-aware mode it estimates remaining total data as remaining SST across all levels plus a proportional share of blob bytes, then only picks TTL deletion when expired files exist and the remaining effective data is within the configured effective maximum.

`PickSizeCompaction` computes total SST size across all levels and combines it with blob size when `max_data_files_size` is configured. For regular L0 FIFO it drops oldest L0 files until remaining effective size is below the limit, using proportional data-per-file accounting in blob-aware mode. During migration from level/universal to FIFO, it picks from the last non-empty non-L0 level, deleting leftmost files under the assumption that smaller keys often represent older data.

`PickIntraL0Compaction` is enabled by `compaction_options_fifo.allow_compaction`. It dispatches to ratio-based compaction when `use_kv_ratio_compaction` is valid with `max_data_files_size >= max_table_files_size`; otherwise it falls back to cost-based intra-L0 compaction. The fallback uses `PickCostBasedIntraL0Compaction` with `level0_file_num_compaction_trigger`, a max average bytes per deleted file based on write buffer size, and `max_compaction_bytes`.

`PickRatioBasedIntraL0Compaction` skips while non-L0 levels remain, rejects concurrent L0 compaction, requires trigger greater than one, computes a target compacted SST size from user `max_compaction_bytes` or from `max_data_files_size * sst_ratio / trigger`, builds geometric tier boundaries down to 10 KB, and picks contiguous oldest L0 batches smaller than a boundary whose accumulated bytes reach that boundary. The output file size limit is the selected boundary.

`PickTemperatureChangeCompaction` only applies to single-level FIFO. It scans oldest files by age thresholds, chooses one file whose target temperature differs from current temperature, and creates a one-file compaction with `CompactionReason::kChangeTemperature`.

## State and Persistence Behavior
The picker itself persists nothing. It creates `Compaction` objects whose execution either deletes input files, rewrites selected L0 files, or changes file temperature. It reads durable metadata from `VersionStorageInfo`, file sizes, blob stats, table properties, newest key times, file creation times, file temperature, and current time. Output compactions use no compression for deletion-style FIFO paths and configured compression for intra-L0 or temperature-change rewrites.

## Dependencies and Integration Points
Dependencies include `CompactionPicker`, `VersionStorageInfo`, `CompactionOptionsFIFO`, `MutableCFOptions`, `MutableDBOptions`, `FileMetaData`, table readers/properties, blob stats, logging, statistics/status utilities, temperature options, and shared `PickCostBasedIntraL0Compaction`. It integrates with DB scheduling through compaction score and with manual compact range by asserting FIFO level constraints.

## Risks and Edge Cases
Blob-aware accounting is approximate and assumes proportional blob ownership by SST bytes; skewed blob references can over-delete or under-delete relative to true data size. TTL compaction depends on newest key time and creation time being available and meaningful. Multi-level FIFO migration deletion by key order is only an approximation of FIFO age order. Ratio-based intra-L0 compaction trades higher L0 file count for lower write amplification and depends on trigger, target, and tier-boundary math. Concurrent L0 compactions are intentionally avoided. Temperature-change compaction returns only one file at a time and does not apply to multi-level FIFO.

## Test Signals
Relevant tests should cover FIFO TTL deletion, max table/data size deletion, blob-aware capacity behavior, migration from non-FIFO levels, `allow_compaction` fallback, ratio-based tiering, invalid ratio-based configurations, file-temperature thresholds, and manual compact-range behavior. Logs emitted through `LogBuffer` are useful diagnostic signals for why a FIFO pick was skipped or selected.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.h -->
# sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.h

## Purpose
This header declares `FIFOCompactionPicker`, the concrete `CompactionPicker` subclass for FIFO compaction style. It constrains compaction output to level 0 and exposes FIFO-specific picking paths for automatic and manual compaction.

## Important APIs, Types, and Functions
The public constructor accepts `ImmutableOptions` and an internal key comparator. Overrides are `PickCompaction`, `PickCompactionForCompactRange`, `MaxOutputLevel`, and `NeedsCompaction`. `MaxOutputLevel` always returns 0 because FIFO creates/deletes L0 files rather than cascading output into lower levels.

Private helpers declared here are `PickTTLCompaction`, `PickSizeCompaction`, `PickIntraL0Compaction`, `PickRatioBasedIntraL0Compaction`, and `PickTemperatureChangeCompaction`. The comments document that intra-L0 compaction is optional, ratio-based compaction is BlobDB-oriented, and the cost-based path is the original fallback.

## Control Flow
Callers use the standard picker interface. `PickCompaction` decides among FIFO policies and returns a registered `Compaction` or null. `PickCompactionForCompactRange` is FIFO-specific and ultimately reuses normal FIFO picking with level 0 assertions. The private method split makes policy order explicit in the implementation: expiration, capacity, file-count reduction, and temperature change.

## State and Persistence Behavior
The class introduces no new member state beyond `CompactionPicker`'s running compaction sets. It reads FIFO options and current version metadata during picking. Persistent effects are deferred to the returned `Compaction`: files may be deleted, compacted within L0, or rewritten with a target temperature.

## Dependencies and Integration Points
The header depends on `compaction_picker.h` and therefore on the base picker contract, `Compaction`, `VersionStorageInfo`, `MutableCFOptions`, `MutableDBOptions`, `LogBuffer`, snapshot placeholders, and compact range options. It is selected when a column family uses `kCompactionStyleFIFO`.

## Risks and Edge Cases
Because FIFO only permits output level 0, callers that expect normal level progression must use another picker. The manual compact-range override ignores begin/end range semantics in favor of FIFO policy picking, so it is not a general range compactor. Ratio-based intra-L0 compaction is configuration-sensitive and should be validated carefully when `max_data_files_size`, `max_table_files_size`, and `level0_file_num_compaction_trigger` change.

## Test Signals
Header-level behavior is validated indirectly by FIFO picker tests and DB tests that instantiate FIFO column families. Important observable signals are `MaxOutputLevel() == 0`, no compaction when score is below threshold, and correct compaction reasons from the implementation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.h -->
