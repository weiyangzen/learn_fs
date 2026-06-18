# Group Research: subset-b-008714

Work item `subset-b-008714` covers RocksDB sorted-run builder tests, table property collectors, trace reader/replayer utilities, and pessimistic transaction lock-manager code. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder_test.cc

- **Purpose:** GTest coverage for `rocksdb/utilities/sorted_run_builder.h`, validating that `SortedRunBuilder` can accept unordered key/value input, sort and deduplicate it into external SST-style output files, iterate the result, and ingest those files into a target DB.
- **Important APIs/types/functions:** `SortedRunBuilderTest` manages per-thread temp and target DB paths. Helpers `Key()` and `Value()` build sortable fixed-width strings. Tests call `SortedRunBuilder::Create`, `Add`, `AddBatch`, `Finish`, `NewIterator`, `GetOutputFiles`, `GetNumEntries`, `GetDataSize`, and `Cleanup`; ingestion uses `DB::Open`, `IngestExternalFileOptions`, and `DB::IngestExternalFile`.
- **Control flow:** Most tests construct options, create a builder, add data in reverse/random/concurrent order, call `Finish()`, then verify iterator ordering and status. Negative-path tests intentionally call APIs in the wrong lifecycle state, such as iterator before finish, add after finish, double finish, and invalid options.
- **State and persistence behavior:** The builder persists intermediate data in a temporary RocksDB/SST area under `opts.temp_dir`; finished output files can be ingested into another RocksDB instance. Tests assert cleanup behavior both through explicit `Cleanup()` and destructor cleanup without `Finish()`.
- **Dependencies:** Depends on RocksDB DB/options/comparator APIs, `WriteBatch`, external file ingestion, `RandomShuffle`, stack trace setup, and the test harness. It assumes the implementation honors a custom comparator and small buffer/file-size options that force flushes.
- **Integration points:** This file is the behavioral contract for the sorted-run builder utility: batch ingestion, concurrent `Add()` calls, duplicate-key last-write-wins semantics, iterator seek/prev support, and generated external files accepted by RocksDB ingestion.
- **Risks:** Tests rely on filesystem cleanup and temp directory emptiness, which can be platform-sensitive. Concurrent writes use `EXPECT_OK` inside worker threads, so failures can be less direct than main-thread assertions. Duplicate-key semantics assume RocksDB overwrite ordering from the builder's internal DB/write path.
- **Test signals:** Strong signals include `BasicSortCorrectness`, `WriteBatchPath`, `ConcurrentWrites`, `IngestIntoTargetDB`, `LargeRandomDataset`, duplicate-key count/value checks, custom reverse comparator ordering, lifecycle error checks, and invalid option validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/sorted_run_builder/sorted_run_builder_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.cc -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.cc

- **Purpose:** Implements a table properties collector that marks newly created non-last-level SSTs for compaction when enough entries are older than a last-level sequence threshold, supporting tiering workflows.
- **Important APIs/types/functions:** Defines property names for eligible last-level entries and future data-age statistics. `CompactForTieringCollector::AddUserKey` counts entries whose sequence, or packed timed-put sequence from `ParsePackedValueForSeqno`, is below `last_level_inclusive_max_seqno_threshold_`. `Finish` emits `rocksdb.eligible.last.level.entries` and sets `need_compaction_`; `NeedCompact`, `GetReadableProperties`, and `Reset` expose collector state. The factory registers the mutable `compaction_trigger_ratio` option.
- **Control flow:** The factory returns `nullptr` when the ratio is disabled, the file is already being created in the last level, or tiering is disabled through `kMaxSequenceNumber`. Otherwise each added key increments total count and possibly eligible count. Finish compares eligible count to `compaction_trigger_ratio * total_entries_counter_`.
- **State and persistence behavior:** Runtime state is per-SST counters plus `need_compaction_`. The only persisted property currently written is the eligible-entry count string; age-stat property names exist but collection functions return `NotSupported()`.
- **Dependencies:** Uses `TablePropertiesCollectorFactory::Context`, `seqno_to_time_mapping` for timed-put values, RocksDB `Status`, option parsing/registration utilities, object registry types, and `UserCollectedProperties`.
- **Integration points:** Created by `NewCompactForTieringCollectorFactory` and can be loaded/configured through RocksDB's customizable table-properties collector factory flow. Compaction scheduling can call `NeedCompact()` after table build.
- **Risks:** The constructor asserts the threshold is not `kMaxSequenceNumber`, so production correctness depends on the factory guard. `collect_data_age_stats_` is accepted but unused. Ratios greater than 1 create a collector but can never trigger compaction, while `Finish` contains an assertion that only fires when compaction would trigger. Empty files with zero total entries avoid emitting properties.
- **Test signals:** Covered by `compact_for_tiering_collector_test.cc` for disabled ratios, tiering-disabled contexts, last-level exclusion, threshold ratios around 50/100 entries, and timed-put packed sequence handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.h -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.h

- **Purpose:** Declares `CompactForTieringCollector`, a `TablePropertiesCollector` used to flag SST files for tiering-related compaction based on sequence-age eligibility.
- **Important APIs/types/functions:** Exports static property-name strings for eligible entries and data-age stats; constructor takes last-level sequence threshold, compaction trigger ratio, and age-stat flag. Overrides `AddUserKey`, `Finish`, `GetReadableProperties`, `Name`, and `NeedCompact`.
- **Control flow:** The header presents the collector lifecycle expected by RocksDB table building: create collector, call `AddUserKey` for every user entry, finalize with `Finish`, then query `NeedCompact`.
- **State and persistence behavior:** Private members hold threshold, ratio, counters, finish flag, compaction decision, and currently-unused data-age collection flag. Persisted output is via `UserCollectedProperties` populated in `Finish`.
- **Dependencies:** Depends only on `rocksdb/utilities/table_properties_collectors.h`, which provides the collector base class, entry types, sequence numbers, slices, status, and property maps.
- **Integration points:** Implemented in the matching `.cc` and instantiated by `CompactForTieringCollectorFactory` declared in the public utilities collector header. It plugs into SST table creation through RocksDB's table property collector interface.
- **Risks:** `Reset()` is private and only used internally; repeated reuse of collector instances would need careful lifecycle control. The header advertises data-age property names before the implementation supports them.
- **Test signals:** Header-level API expectations are exercised indirectly by tests that create collectors through the factory and call the virtual `TablePropertiesCollector` API.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector_test.cc

- **Purpose:** Unit tests for the tiering collector factory and collector thresholds.
- **Important APIs/types/functions:** Uses `NewCompactForTieringCollectorFactory`, `TablePropertiesCollectorFactory::Context`, `AddUserKey`, `Finish`, `NeedCompact`, `PackValueAndSeqno`, and `kEntryTimedPut`.
- **Control flow:** Tests construct contexts representing enabled tiering, disabled tiering, and last-level file creation. Enabled tests add 100 entries, finish the collector, and check the eligible-entry property and compaction decision against ratio thresholds.
- **State and persistence behavior:** Verifies per-file collector counters and `NeedCompact()` state before and after `Finish()`. The test inspects emitted `UserCollectedProperties`, not persisted SST files.
- **Dependencies:** Depends on the collector header, sequence packing helper, table property types, RocksDB test harness, and stack trace setup.
- **Integration points:** Validates factory behavior for RocksDB table-builder contexts: no collector for disabled settings, a collector for non-last-level files with valid tiering threshold, and timed-put sequence extraction.
- **Risks:** Tests use simple numeric sequences and do not cover empty files, ratio > 1 after finish beyond non-trigger behavior, option-string parsing, or age-stat APIs that return `NotSupported`.
- **Test signals:** Strong signals are `NotEnabled`, `TieringDisabled`, `LastLevelFile`, `CollectorEnabled`, and `TimedPutEntries`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.cc -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.cc

- **Purpose:** Implements tombstone-sensitive table property collection that asks RocksDB to compact a generated SST when delete density crosses either a sliding-window threshold or a whole-file deletion-ratio threshold.
- **Important APIs/types/functions:** `CompactOnDeletionCollector::AddUserKey` tracks delete, single-delete, and delete-with-timestamp entries. `Finish` finalizes ratio-based compaction. `CompactOnDeletionCollectorFactory` creates collectors and exposes mutable options `window_size`, `deletion_trigger`, `deletion_ratio`, and `min_file_size`. `TablePropertiesCollectorFactory::CreateFromString` registers both deletion and tiering collector factories in the default object library.
- **Control flow:** The collector divides the configured sliding window into 128 buckets, advances a ring buffer as entries arrive, keeps a maximum deletion count in the observation window, and sets `need_compaction_` once the trigger and minimum file size are met. Ratio mode counts all entries until finish and compares delete ratio after final file size is known.
- **State and persistence behavior:** State is per-SST in-memory counters: bucket deletion counts, current bucket position, total/deletion entries, current file size, maximum window deletions, and final `need_compaction_`. It does not write user properties; the compaction signal is through `NeedCompact()`.
- **Dependencies:** Uses RocksDB collector interfaces, option registry/load utilities, string parsing helpers, object-library registration, and atomics in the public factory state.
- **Integration points:** Plugged into table creation through `NewCompactOnDeletionCollectorFactory` or string-configured `TablePropertiesCollectorFactory::CreateFromString`. It also shares registration code for `CompactForTieringCollectorFactory`.
- **Risks:** If both `bucket_size_` and valid deletion-ratio mode are disabled, the collector silently does nothing. Bucket rounding can make the effective observation window larger than requested. `max_num_locks`-style constraints are unrelated; this collector's minimum file size can suppress compaction even with many tombstones. `Finish(nullptr)` is accepted because properties are unused.
- **Test signals:** Deletion-ratio thresholds, sliding-window randomized/deterministic cases, and minimum-file-size gating are covered by `compact_on_deletion_collector_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.h -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.h

- **Purpose:** Declares `CompactOnDeletionCollector`, a `TablePropertiesCollector` that observes delete density while an SST is built and reports whether the file should be compacted again.
- **Important APIs/types/functions:** Constructor takes `sliding_window_size`, `deletion_trigger`, `deletion_ratio`, and `min_file_size`. Overrides `AddUserKey`, `Finish`, `GetReadableProperties`, `Name`, and `NeedCompact`. `kNumBuckets` fixes the sliding window ring buffer at 128 buckets.
- **Control flow:** RocksDB calls `AddUserKey` for each emitted table entry and `Finish` when table properties are finalized. `NeedCompact` exposes the result to compaction scheduling.
- **State and persistence behavior:** The header lays out the complete in-memory state: deletion-count bucket array, current bucket counters, trigger/ratio configuration, total/delete entry counters, file-size threshold state, maximum observed window deletions, final compaction flag, and finish marker. It has no durable property output.
- **Dependencies:** Depends on the RocksDB table property collector interface and its entry-type/sequence/slice types.
- **Integration points:** Implemented and registered in the `.cc`; constructed by `CompactOnDeletionCollectorFactory` from public collector utilities APIs.
- **Risks:** `Reset()` is declared private but not implemented/used in the visible implementation, so reuse is not currently part of the lifecycle. The field `min_file_size_` is declared `size_t` while constructor accepts `uint64_t`, which can truncate on platforms where `size_t` is narrower.
- **Test signals:** API behavior is indirectly exercised by deletion-ratio, sliding-window, and minimum-size tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector_test.cc

- **Purpose:** Unit tests for tombstone-density compaction decisions in `CompactOnDeletionCollector`.
- **Important APIs/types/functions:** Uses `NewCompactOnDeletionCollectorFactory`, collector `AddUserKey`, `Finish`, `NeedCompact`, and entry types `kEntryDelete`, `kEntrySingleDelete`, and `kEntryPut`.
- **Control flow:** `DeletionRatio` checks invalid ratios disable ratio mode and valid ratios trigger only after `Finish`. `SlidingWindow` builds deterministic and randomized windows and verifies the approximation within bucket bias. `MinFileSize` checks both sliding-window and ratio triggers under file-size thresholds.
- **State and persistence behavior:** Tests focus on internal compaction state exposed by `NeedCompact()` rather than persisted properties. They simulate file size by passing `file_size` to `AddUserKey`.
- **Dependencies:** Depends on DB format entry types, table property collector interfaces, RocksDB random/test harness utilities, and stack trace setup.
- **Integration points:** Validates collector behavior expected by table-building and compaction scheduling for tombstone-heavy SSTs.
- **Risks:** Sliding-window tests tolerate bucket bias and therefore do not assert exact window behavior near thresholds. Tests do not cover delete-with-timestamp entries, option parsing, string factory loading, or `GetReadableProperties()`.
- **Test signals:** Provides broad threshold coverage, randomized window sizes/triggers, high-volume non-triggering sections, and explicit minimum-size boundary checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.cc -->
# Research: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.cc

- **Purpose:** Implements file-backed `TraceReader` and `TraceWriter` adapters used by RocksDB tracing and replay.
- **Important APIs/types/functions:** `FileTraceReader::Read` reads fixed-size trace metadata, decodes payload length with `DecodeFixed32`, and reads payload chunks through `RandomAccessFileReader`. `Reset` rewinds offset; `Close` drops the reader. `FileTraceWriter::Write` appends a slice to `WritableFileWriter`, `GetFileSize` reports writer size, and factory functions create file-backed reader/writer instances from `Env` and `EnvOptions`.
- **Control flow:** Reader starts at offset zero, reads `kTraceMetadataSize`, returns `Incomplete` on zero-byte EOF, rejects short metadata/payload as corruption, appends metadata and payload into `data`, and advances `offset_`. Writer creation opens a writable file and each write appends the already-encoded trace bytes.
- **State and persistence behavior:** Reader state is the current file offset plus a reusable 1 KB buffer; writer state is the owning writable file handle. Trace persistence is the actual trace file on the configured filesystem. Destructors call `Close().PermitUncheckedError()`.
- **Dependencies:** Uses `RandomAccessFileReader`, `WritableFileWriter`, filesystem options wrappers, `trace_replay/trace_replay.h` constants, and fixed-width coding helpers.
- **Integration points:** `NewFileTraceReader` and `NewFileTraceWriter` bridge public trace reader/writer APIs to RocksDB `Env` files. `ReplayerImpl` consumes a `TraceReader`, often this implementation.
- **Risks:** `FileTraceWriter::Write` and `GetFileSize` assume the writer is open; calling after `Close` would dereference null. Reader asserts non-null in `Read` but only `Reset` returns a clean IOError when closed. EOF currently maps to `Incomplete`, which replay treats as normal end in some paths.
- **Test signals:** Expected tests would cover full record reads, multi-chunk payloads larger than 1 KB, reset/re-read, short metadata/payload corruption, EOF handling, close behavior, and writer file-size growth.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.h -->
# Research: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.h

- **Purpose:** Declares file-based trace reader and writer classes implementing the public `TraceReader` and `TraceWriter` interfaces.
- **Important APIs/types/functions:** `FileTraceReader` owns a `RandomAccessFileReader`, offset, result slice, and fixed buffer; exposes `Read`, `Close`, and `Reset`. `FileTraceWriter` owns a `WritableFileWriter`; exposes `Write`, `Close`, and `GetFileSize`.
- **Control flow:** The header defines a simple lifecycle: construct with an already-created file reader/writer, perform reads/writes, optionally reset the reader, and close/destruct to release file handles.
- **State and persistence behavior:** State is transient file-handle and offset state; durable trace data is stored in the target trace file.
- **Dependencies:** Includes `rocksdb/trace_reader_writer.h` and forward-declares RocksDB file reader/writer classes to keep the public header lightweight.
- **Integration points:** Used by factory functions in the `.cc` and by tracing/replay code through the abstract trace interfaces.
- **Risks:** No explicit copy/move deletion is declared, but ownership through `unique_ptr` and raw buffer member prevents accidental copying. The raw `char* const buffer_` requires destructor cleanup in the implementation.
- **Test signals:** Header contract is exercised through trace-file round-trip tests and replay tests that consume `TraceReader`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/file_trace_reader_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.cc -->
# Research: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.cc

- **Purpose:** Implements `Replayer`, turning encoded trace files into `TraceRecord`s and optionally executing them against a DB with original timing scaled by replay options.
- **Important APIs/types/functions:** Constructor creates `TraceRecord::NewExecutionHandler`. `Prepare` reads and decodes the trace header and stores `trace_file_version_` and `header_ts_`. `Next` returns decoded records one at a time. `Execute` dispatches records to the execution handler. `Replay` drives timed single-threaded or thread-pool replay. `ReadHeader`, `ReadTrace`, and static `BackgroundWork` are internal helpers.
- **Control flow:** `Prepare` must run before `Next`/`Replay`. Single-thread replay reads, decodes, sleeps until scaled trace time, then executes or reports unsupported records. Multi-thread replay sleeps before scheduling supported operation types (`write`, `get`, iterator seek, multiget) on a `ThreadPoolImpl`, tracks the earliest trace-timestamped execution error, and waits for all jobs before returning.
- **State and persistence behavior:** Replayer state includes trace-reader ownership, prepared/end flags, header timestamp, trace-file version, execution handler, DB environment pointer, and a mutex protecting trace-reader access. Persistence effects are the replayed operations applied to the target DB, while trace input remains read-only.
- **Dependencies:** Depends on RocksDB DB/options/slice/env APIs, trace helpers from `trace_replay`, `TraceRecord` visitor/handler APIs, `TraceRecordResult`, system clock, C++ threads, and RocksDB thread-pool implementation.
- **Integration points:** Used by public `Replayer` utilities to inspect traces through `Next` or execute them against a DB through `Replay`. It integrates with column-family handles supplied at construction through the execution handler.
- **Risks:** `Replay` treats `Incomplete` as successful end-of-trace, including abrupt EOF without an explicit trace-end marker. Multi-thread mode can reorder operation execution relative to single-thread mode after scheduling. Result callbacks may run concurrently in background workers. Unsupported trace handling differs: single-thread attempts decode then callback with `NotSupported`; multi-thread filters by trace type before decode.
- **Test signals:** Useful tests include prepare-before-use errors, header parsing, trace-end handling, fast-forward validation, single-thread timing, multi-thread supported/unsupported dispatch, earliest-error selection by trace timestamp, callback concurrency, and EOF behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.h -->
# Research: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.h

- **Purpose:** Declares RocksDB's concrete trace replayer implementation and worker argument bundle for background replay.
- **Important APIs/types/functions:** `ReplayerImpl` overrides `Prepare`, `Next`, `Execute`, `Replay`, and `GetHeaderTimestamp`. Private helpers are `ReadHeader`, `ReadTrace`, and static `BackgroundWork`. `ReplayerWorkerArg` carries a `Trace`, file version, execution handler pointer, error callback, and result callback.
- **Control flow:** Exposes the public replayer lifecycle while keeping trace decoding and background execution internals private.
- **State and persistence behavior:** Tracks reader ownership, mutex-protected reading, atomic preparation/end flags, header timestamp, execution handler, environment pointer, and parsed trace format version. Replay persistence is performed through the execution handler against the DB supplied in the constructor.
- **Dependencies:** Includes DB/env/status/trace interfaces, trace record/result APIs, `rocksdb/utilities/replayer.h`, and trace replay helper declarations.
- **Integration points:** Concrete implementation behind public replay construction; interoperates with any `TraceReader`, including `FileTraceReader`.
- **Risks:** `exec_handler_` is shared with worker args as a raw pointer, so `Replay` must not outlive the `ReplayerImpl` object and callbacks must not retain it. Atomic booleans protect state visibility but do not make the whole replayer API safely reentrant.
- **Test signals:** Header contract should be validated through public replayer API tests for prepare/next/execute/replay lifecycle and multi-thread background execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trace/replayer_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.cc

- **Purpose:** Implements the factory function that selects the concrete lock manager for pessimistic transactions.
- **Important APIs/types/functions:** `NewLockManager(PessimisticTransactionDB* db, const TransactionDBOptions& opt)` returns a `std::shared_ptr<LockManager>`.
- **Control flow:** The function asserts a DB pointer. If `opt.lock_mgr_handle` is set, it aliases the handle-owned manager pointer into a shared pointer so the handle controls lifetime. Otherwise it chooses `PerKeyPointLockManager` when `use_per_key_point_lock_mgr` is true, or `PointLockManager` by default.
- **State and persistence behavior:** No persistent state is stored here. It determines the in-memory lock manager used by a transaction DB instance.
- **Dependencies:** Depends on the abstract lock manager header and point lock manager implementations.
- **Integration points:** Central construction point for TransactionDB pessimistic locking; callers should use it rather than directly instantiating implementations.
- **Risks:** The aliasing shared pointer for custom managers depends on `lock_mgr_handle` keeping the manager object valid. Range lock managers or external custom managers must be supplied through the handle path.
- **Test signals:** Tests should verify custom handle selection, per-key option selection, default point-lock selection, and lifetime of aliasing handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.h

- **Purpose:** Defines the abstract locking interface used by pessimistic transactions, covering point locks, range locks, lock tracking, status inspection, deadlock diagnostics, and deadlock buffer resizing.
- **Important APIs/types/functions:** `LockManager` declares `IsPointLockSupported`, `IsRangeLockSupported`, `GetLockTrackerFactory`, `AddColumnFamily`, `RemoveColumnFamily`, point/range `TryLock`, point/range/tracker `UnLock`, `GetPointLockStatus`, `GetRangeLockStatus`, `GetDeadlockInfoBuffer`, and `Resize`. It aliases point and range status multimaps.
- **Control flow:** Transactions acquire locks through `TryLock`, record them using a compatible `LockTracker`, and later release individual locks or all tracked locks. Managers are dynamically configured as column families are added or removed.
- **State and persistence behavior:** Implementations keep in-memory lock state only; the interface has no durable persistence. Status APIs expose current in-memory lock holders and wait/deadlock diagnostics.
- **Dependencies:** Depends on RocksDB transaction/TransactionDB types, column family identifiers, `Endpoint`, `KeyLockInfo`, `RangeLockInfo`, `DeadlockPath`, and `LockTracker`.
- **Integration points:** Used by `PessimisticTransactionDB` and transaction objects; concrete point and range managers implement the interface.
- **Risks:** Correctness depends on matching the manager with the tracker factory returned by `GetLockTrackerFactory`. The caller must honor column-family lifecycle preconditions documented in comments.
- **Test signals:** Any lock-manager implementation should pass common tests for capability flags, point/range unsupported behavior, lock conflict semantics, status reporting, deadlock buffer behavior, and tracker-based unlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_tracker.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_tracker.h

- **Purpose:** Defines the transaction-side lock tracking abstraction used to remember lock requests, support savepoints, and drive bulk unlock.
- **Important APIs/types/functions:** Request structs are `PointLockRequest` and `RangeLockRequest`; `PointLockStatus` reports tracked state for a key; `UntrackStatus` distinguishes not tracked, count decremented, and removed. `LockTracker` declares point/range tracking, merge/subtract, clear, savepoint delta extraction, point lock status, lock counts, and column-family/key iterators. `LockTrackerFactory` creates trackers compatible with a manager.
- **Control flow:** Transactions call `Track` after successful lock acquisition, `Untrack` on release/rollback, `Merge` and `Subtract` around savepoints, and iterate tracked column families/keys for unlock.
- **State and persistence behavior:** Trackers are in-memory, not thread-safe, and owned by transactions/savepoints. They persist only logical lock intent/acquisition metadata during transaction lifetime, including sequence numbers and read/write counters in concrete implementations.
- **Dependencies:** Uses RocksDB namespace/status/types and transaction DB endpoint definitions.
- **Integration points:** Concrete managers return a matching factory so pessimistic transactions can maintain tracker state in the right format. Optimistic transactions can use trackers as lock-intention records even without a lock manager.
- **Risks:** Several methods require the argument tracker to be the same concrete type and, for subtract/savepoint operations, to be a subset; violations are enforced by concrete casts/asserts. Iterators are caller-owned and have undefined behavior if used after the underlying tracker mutates.
- **Test signals:** Tests should cover reentrant read/write tracking, untrack counts, merge/subtract, savepoint deltas, iterator coverage, and unsupported point/range no-op behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/lock_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/any_lock_manager_test.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/any_lock_manager_test.h

- **Purpose:** Parameterized common tests for lock managers that share point-lock behavior, run against both `PointLockManager` and `PerKeyPointLockManager`.
- **Important APIs/types/functions:** `AnyLockManagerTest` extends `PointLockManagerTest` and `WithParamInterface<init_func_t>`, allowing optional setup functions. Tests use `TryLock`, `UnLock`, `GetDeadlockInfoBuffer`, `GetWaitingTxns`, and `BlockUntilWaitingTxn`.
- **Control flow:** Each test creates a mock column family, begins transactions, acquires locks, and checks reentrancy, upgrade/downgrade, conflict timeouts, shared lock coexistence, deadlock detection, and waiting transaction reporting.
- **State and persistence behavior:** Exercises in-memory lock state and transaction waiting metadata only. No DB data is written beyond opening a test TransactionDB.
- **Dependencies:** Depends on `point_lock_manager_test.h`, RocksDB test harness parameterization, mock column family handles, sync points, and pessimistic transaction objects.
- **Integration points:** Included by `point_lock_manager_test.cc` and instantiated for the base and per-key managers, giving both implementations a shared behavioral baseline.
- **Risks:** Cleanup has a special case because the base `PointLockManager` records repeated shared reentrant locks differently from `PerKeyPointLockManager`. The tests depend on sync point names shared with implementation internals.
- **Test signals:** Reentrant exclusive/shared, lock upgrade/downgrade, conflict timeout matrix, concurrent shared locks, two-transaction deadlock path content, and `GetWaitingTxns` with multiple blockers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/any_lock_manager_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench.cc

- **Purpose:** Small benchmark entry point for the point lock manager benchmark tool.
- **Important APIs/types/functions:** When `GFLAGS` is unavailable, `main()` prints an installation message and exits with 1. When available, it includes `rocksdb/point_lock_bench_tool.h` and calls `ROCKSDB_NAMESPACE::point_lock_bench_tool(argc, argv)`.
- **Control flow:** Compile-time `#ifdef GFLAGS` selects between a stub and the real tool driver.
- **State and persistence behavior:** The stub has no state. The real benchmark behavior is delegated to `point_lock_bench_tool.cc`.
- **Dependencies:** Depends conditionally on gflags support and the public bench tool header.
- **Integration points:** Provides the executable `main` for RocksDB lock benchmark builds.
- **Risks:** Without gflags the binary intentionally cannot run. Behavior and flags are not visible in this file, so updates to the tool must keep the exported `point_lock_bench_tool` signature stable.
- **Test signals:** Build configurations should verify both GFLAGS and no-GFLAGS paths compile and that the stub exits nonzero with a clear message.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench_tool.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench_tool.cc

- **Purpose:** Implements the gflags-driven point lock manager benchmark using the same randomized validation runner as stress tests.
- **Important APIs/types/functions:** Defines flags for DB directory, stripe count, manager type, thread/key counts, max locks per transaction, execution time, lock type mix, lock/deadlock/expiration timeouts, allowed error policy, simulated work sleep, and stuck-thread checks. `PointLockManagerBenchmark` opens a TransactionDB, constructs either `PointLockManager` or `PerKeyPointLockManager`, and invokes `PointLockValidationTestRunner`.
- **Control flow:** `point_lock_bench_tool` installs stack traces, parses flags, prints the tool-local flag values, constructs the benchmark object, runs it, and returns zero. Constructor sets DB and transaction options; destructor deletes DB and destroys the benchmark directory.
- **State and persistence behavior:** Creates a temporary/on-disk TransactionDB under `FLAGS_db_dir` for the benchmark lifetime, while lock-manager state is in-memory. The validation runner mutates in-memory counters but not meaningful persisted application data.
- **Dependencies:** Requires `GFLAGS`, RocksDB convenience/env/TransactionDB APIs, point lock managers, validation runner, pessimistic transaction DB types, and stack trace support.
- **Integration points:** Used by the benchmark executable in `point_lock_bench.cc`; mirrors stress-test parameters for local performance and correctness experiments.
- **Risks:** `env_->CreateDir` status is not checked. The default `/tmp` directory is destroyed in the destructor, so flag misuse can delete an unintended benchmark directory. Assertions are used for open/destroy failures.
- **Test signals:** Manual/CI benchmark signals include lock throughput, deadlock counts, timeout behavior, and validation-runner assertions across manager types and lock mixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_bench_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.cc

- **Purpose:** Implements RocksDB pessimistic point-key locking for transactions, including shared/exclusive locks, reentrancy, timeouts, lock expiration stealing, deadlock detection, lock status reporting, and a per-key waiter-queue variant.
- **Important APIs/types/functions:** Internal types include `KeyLockWaiter`, `KeyLockWaiterContext`, `LockInfo`, `LockMapStripe`, and `LockMap`. Core `PointLockManager` methods include `AddColumnFamily`, `RemoveColumnFamily`, `TryLock`, `AcquireWithTimeout`, `AcquireLocked`, `UnLockKey`, `UnLock`, `GetPointLockStatus`, `IncrementWaiters`, `DecrementWaiters`, `GetDeadlockInfoBuffer`, and `Resize`. `PerKeyPointLockManager` overrides acquisition/unlock with per-key waiter queues and adds `CalculateWaitEndTime`, `FillWaitIds`, and its own `AcquireLocked`.
- **Control flow:** A point lock maps from column-family id to a `LockMap`, then hashes the key to a stripe. The base manager waits on a stripe-wide condvar and retries acquisition until timeout, expiration, or deadlock. The per-key manager joins a FIFO waiter queue stored in `LockInfo`, wakes either the first exclusive waiter or batches leading shared waiters, prioritizes upgrades before later exclusive waiters, and can delay expensive deadlock detection with `deadlock_timeout_us`.
- **State and persistence behavior:** All lock state is in-memory: per-CF maps, stripe key maps, holders, waiter queues, lock counts, thread-local lock-map caches, thread-local key waiters, wait-for graph maps, reverse waiter counts, and a bounded deadlock path buffer. There is no durable lock persistence, but replay/transaction correctness depends on this state.
- **Dependencies:** Uses RocksDB instrumented mutexes/condvars from `TransactionDBMutexFactory`, perf counters/timers, hash helpers, thread-local storage, sync points, pessimistic transaction DB APIs for stealing expired locks, and transaction wait/deadlock metadata.
- **Integration points:** Constructed by `NewLockManager` for `TransactionDB`. `PessimisticTransaction` calls `TryLock` and `UnLock`; lock trackers drive bulk unlock. `GetPointLockStatus` feeds diagnostics and tests. Deadlock information is exposed through public transaction DB APIs.
- **Risks:** Correctness depends on strict lock ordering: lock-map mutex, then stripes by ascending CF/stripe, then wait-map mutex. The base manager's stripe-wide notification is less efficient and may wake unrelated waiters. Lock expiration uses a single max expiration for shared holders, which can extend effective lock lifetime. Per-key wait queues use raw thread-local waiter pointers and must remove them through `KeyLockWaiterContext` on all failure paths. Tests rely on internal sync point names.
- **Test signals:** Extensive tests cover non-existing CF errors, status reporting, unlock/relock, reentrancy, shared/exclusive conflicts, deadlocks and depth limits, upgrade prioritization, FIFO fairness, downgrade wakeups, expiration stealing, race conditions around woken shared waiters and upgrades, and randomized/stress validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.h

- **Purpose:** Declares the point-key lock manager implementations used by pessimistic transactions and their deadlock diagnostics.
- **Important APIs/types/functions:** `DeadlockInfoBufferTempl` stores a ring of recent deadlock paths with resize/normalization. `TrackedTrxInfo` captures wait graph neighbors and the key/CF/mode being waited on. `PointLockManager` implements the `LockManager` interface for point locks only. `PerKeyPointLockManager` derives from it and overrides acquisition/unlock to use per-key queues.
- **Control flow:** The declarations define the public manager lifecycle: add/remove column families, try point locks, reject range locks, unlock by key/tracker, report statuses, and resize deadlock buffers. Protected/private hooks split common point-lock logic from per-key behavior.
- **State and persistence behavior:** Declared state includes transaction DB pointer, stripe/lock-count configuration, lock-map mutex/map/cache, key waiter thread-local, wait-for graph maps, deadlock ring buffer, and mutex factory. All state is in-memory and transaction-lifetime scoped.
- **Dependencies:** Depends on transaction APIs, instrumented mutexes, RocksDB hash containers, thread-local utilities, lock manager interface, and point lock tracker factory.
- **Integration points:** Included by `lock_manager.cc`, tests, benchmark tool, and transaction internals. Its `GetLockTrackerFactory` binds point locks to `PointLockTracker`.
- **Risks:** Subclass overrides depend on internal forward-declared `LockMap`, `LockMapStripe`, and `LockInfo` semantics from the `.cc`. The ring buffer `Normalize()` assumes default-constructed empty paths distinguish unused slots.
- **Test signals:** Header-level contracts are tested through manager instantiations, common lock tests, deadlock buffer resize tests, and per-key fairness/efficiency tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_stress_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_stress_test.cc

- **Purpose:** Parameterized long-running correctness stress tests for both point lock manager implementations using randomized multi-threaded lock acquisition.
- **Important APIs/types/functions:** `PointLockCorrectnessCheckTestParam` configures manager type, thread/key counts, max keys per transaction, execution duration, lock type, lock timeout, lock expiration, allowed errors, and simulated work. `PointLockCorrectnessCheckTest` constructs the selected manager and invokes `PointLockValidationTestRunner`.
- **Control flow:** Each parameter opens the base `PointLockManagerTest` fixture, selects per-key or base manager, sets transaction options, then runs the validation runner for the configured duration and workload.
- **State and persistence behavior:** Exercises in-memory lock state heavily while the fixture owns a temporary TransactionDB. The runner maintains in-memory counters to validate exclusive/shared guarantees.
- **Dependencies:** Depends on the test fixture, validation runner, point lock managers, transaction DB options, and GTest parameterization.
- **Integration points:** Complements targeted unit tests with randomized stress coverage across myrocks-like timeout settings, short-expiration lock stealing, long-timeout deadlock detection, and low-contention workloads.
- **Risks:** Ten-second parameter cases can be expensive in CI. Some parameter sets allow non-deadlock errors to avoid false failures under short timeouts/expiration, so they are broader liveness/correctness signals rather than exact error-code assertions.
- **Test signals:** Validation runner asserts progress, no remaining locks, exclusive counter/value consistency, shared-lock read stability, and successful operation across both managers and lock type mixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_stress_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.cc

- **Purpose:** Main targeted unit test suite for `PointLockManager` and `PerKeyPointLockManager`, covering diagnostics, wait ordering, upgrade/downgrade behavior, expiration, and race conditions.
- **Important APIs/types/functions:** Defines `SpotLockManagerTestParam`, `SpotLockManagerTest`, and `PerKeyPointLockManagerTest`. Uses `BlockUntilWaitingTxn`, `TryBlockUntilWaitingTxn`, sync point dependencies/callbacks, `TryLock`, `UnLock`, `GetPointLockStatus`, and `GetDeadlockInfoBuffer`.
- **Control flow:** Parameterized spot tests run both managers with selected deadlock timeouts. Per-key-specific tests set up precise waiter queues and use sync points to stop threads between wakeup and lock acquisition, creating deterministic race windows.
- **State and persistence behavior:** Tests in-memory manager state and transaction waiting/deadlock metadata; the fixture opens a temporary TransactionDB but does not validate persisted data.
- **Dependencies:** Includes `point_lock_manager_test.h` and `any_lock_manager_test.h`, plus sync point/test harness threading utilities.
- **Integration points:** Instantiates common `AnyLockManagerTest` for base and per-key managers, and a larger `PointLockCorrectnessCheckTestSuite` for combinations of per-key flag and deadlock timeout.
- **Risks:** Several tests intentionally depend on implementation-specific sync point names and thread scheduling. Retry loops reduce flakiness around lock expiration. The file assumes `joinable()` is a meaningful proxy for blocked test threads after controlled sync points.
- **Test signals:** Covers missing CF errors, status inspection, unlock/relock, depth-exceeded deadlocks, upgrade prioritization with exclusive/shared waiters, multiple-upgrade deadlocks, per-key FIFO/fairness/efficiency, lock timeout, expiration stealing, waiter deadlocks, shared-lock and upgrade race conditions, catch-22 overhead, upgrade ordering, and downgrade wakeups.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.h

- **Purpose:** Shared GTest fixture and synchronization helper for point lock manager tests.
- **Important APIs/types/functions:** `PointLockManagerTest::init` creates a per-thread DB path, opens `TransactionDB`, configures four stripes and zero DB lock timeout, and records the wait sync point name. `SetUp` creates a separate `PointLockManager`; `TearDown` verifies no locks remain and destroys the DB. `NewTxn` starts a `PessimisticTransaction`. `UsePerKeyPointLockManager` swaps implementations. `BlockUntilWaitingTxn` starts a thread and waits until a sync point is reached.
- **Control flow:** Test cases inherit the fixture, add mock column families, create transactions with adjusted options, and use `BlockUntilWaitingTxn` to make a thread block inside lock acquisition before asserting intermediate state.
- **State and persistence behavior:** Fixture owns temp directory, `TransactionDB`, lock-manager shared pointer, environment pointer, and deadlock timeout override. Persistence is limited to temporary DB files destroyed at teardown.
- **Dependencies:** Depends on RocksDB file utilities, transaction DB APIs, test harness, point lock manager classes, common test helpers, and pessimistic transaction DB internals.
- **Integration points:** Used by `any_lock_manager_test.h`, `point_lock_manager_test.cc`, and stress tests.
- **Risks:** Tests create a lock manager separate from the DB's own manager, so fixture comments warn that this is intentional. `BlockUntilWaitingTxn` has a 30-second polling timeout to avoid hangs but may still be sensitive on very slow machines.
- **Test signals:** Provides standardized setup/teardown and lock-leak detection for all point-lock test files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test_common.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test_common.h

- **Purpose:** Common fixtures/helpers for point lock manager tests and benchmarks.
- **Important APIs/types/functions:** Defines long/short timeout constants, `MockColumnFamilyHandle`, and `verifyNoLocksHeld`. The mock handle returns a fixed column-family id, name, OK descriptor status, and bytewise comparator.
- **Control flow:** Tests create mock handles to add/remove lock manager column families without needing real column-family handles. Teardown and validation runner call `verifyNoLocksHeld` to collect diagnostic text if any locks remain.
- **State and persistence behavior:** Mock handle stores only id/name. `verifyNoLocksHeld` reads in-memory `GetPointLockStatus()` and formats current key/mode/transaction ids.
- **Dependencies:** Depends on RocksDB DB/column-family APIs and the lock manager interface.
- **Integration points:** Shared by unit tests, stress tests, and validation runner.
- **Risks:** Mock handles do not represent real column-family lifecycle beyond id/comparator. `verifyNoLocksHeld` only checks point locks; range-lock managers would need separate validation.
- **Test signals:** Lock leak reports include CF id, key, mode, and holder ids, which is important for diagnosing failed concurrent tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_manager_test_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.cc -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.cc

- **Purpose:** Implements `PointLockTracker`, the transaction-side record of point locks acquired or intended by a transaction.
- **Important APIs/types/functions:** Internal iterators `TrackedKeysColumnFamilyIterator` and `TrackedKeysIterator` expose tracked CFs/keys. `Track` records reads/writes, earliest sequence, and exclusiveness. `Untrack` decrements read/write counters and removes empty keys/CFs. `Merge`, `Subtract`, `GetTrackedLocksSinceSavePoint`, `GetPointLockStatus`, `GetNumPointLocks`, iterator factories, and `Clear` implement the `LockTracker` contract.
- **Control flow:** Tracking uses `tracked_keys_[cf][key]`. Repeated tracks increment read or write counts; untrack decrements the matching count. Merge copies or combines counters; subtract removes savepoint-scoped counts. Savepoint delta extraction returns a new tracker containing keys whose current counts are exactly those tracked since the savepoint.
- **State and persistence behavior:** State is an in-memory nested map from column-family id to key to `TrackedKeyInfo` with sequence, read/write counts, and exclusive flag. It is not thread-safe and has no durable persistence.
- **Dependencies:** Depends on `point_lock_tracker.h` and the abstract `LockTracker` API.
- **Integration points:** Created by `PointLockTrackerFactory`, returned by point lock managers, and consumed by transaction code for savepoints and bulk unlock.
- **Risks:** Concrete casts assume same tracker type. `TrackedKeyInfo::Merge` asserts the current sequence is earlier or equal; callers must preserve stronger sequence guarantees. `Subtract` does not erase empty CF maps after removing all keys. `GetKeyIterator` asserts the CF exists.
- **Test signals:** Tests should cover repeated read/write tracking, read/write untracking distinctions, exclusive flag merging, savepoint deltas, iterator traversal, and lock status queries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.h

- **Purpose:** Declares the concrete point-lock tracker and its singleton factory.
- **Important APIs/types/functions:** `TrackedKeyInfo` stores earliest sequence number, read/write counters, and exclusive flag, with a `Merge` helper. Type aliases define `TrackedKeyInfos` and `TrackedKeys`. `PointLockTracker` implements point tracking, no-op range tracking, merge/subtract/clear/savepoint delta, status, count, and iterators. `PointLockTrackerFactory::Get()` returns a singleton factory.
- **Control flow:** The tracker records point locks by column family and key, while range methods intentionally report unsupported/no-op behavior.
- **State and persistence behavior:** All tracked lock metadata is in-memory transaction state. Sequence numbers represent conflict-check guarantees rather than persisted records.
- **Dependencies:** Depends on C++ memory/string/unordered_map and the abstract `lock_tracker.h`.
- **Integration points:** `PointLockManager::GetLockTrackerFactory` returns this factory, binding point manager acquisitions to this tracker implementation.
- **Risks:** `TrackedKeyInfo::Merge` relies on sequence ordering asserted in debug builds only. Read/write counters are `uint32_t`, so pathological reentrant lock counts could overflow. Unsupported range methods can hide misuse unless callers check capability flags.
- **Test signals:** Header contracts are exercised by transaction savepoint and point-lock manager tests that use tracker-based unlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_validation_test_runner.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_validation_test_runner.h

- **Purpose:** Reusable randomized validation runner for point lock manager correctness, used by both stress tests and the benchmark tool.
- **Important APIs/types/functions:** Defines `LockTypeToTest`, `KeyStatus`, assertion/debug macros that work with or without GTest, and `PointLockValidationTestRunner`. Key methods are the constructor, `DecideLockType`, and `run`.
- **Control flow:** `run` adds a mock CF, starts worker threads, and each thread repeatedly starts with a transaction, randomly selects keys and lock modes, handles upgrade/downgrade decisions, attempts locks, optionally sleeps, validates protected state, releases all held locks, and repeats until shutdown. The main thread checks progress once per second and joins workers.
- **State and persistence behavior:** Uses in-memory vectors of counters, values, exclusive-status flags, shared-lock counts, per-thread progress counters, and aggregate acquisition/deadlock counters. A temporary TransactionDB supplies transaction objects, but validation state is local memory.
- **Dependencies:** Depends on RocksDB DB/env/TransactionDB APIs, lock manager interface, common test helpers, pessimistic transaction APIs, and RocksDB random utilities.
- **Integration points:** Shared by `point_lock_manager_stress_test.cc` and `point_lock_bench_tool.cc`, making stress and benchmark behavior consistent.
- **Risks:** `shutdown_` is an atomic flag but some validation arrays are intentionally protected by the lock manager under test; failures indicate lock correctness bugs. Lock status validation is disabled when expiration/stealing is enabled because expired-lock stealing can invalidate simple local invariants. Progress assertions can be sensitive under heavy sanitizers or CPU starvation.
- **Test signals:** Detects exclusive-lock mutual exclusion violations via atomic counter versus protected value, shared-lock stability violations by comparing observed values while holding shared locks, deadlock handling, per-thread progress, and final lock leaks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/point/point_lock_validation_test_runner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_lock_manager.h -->
# Research: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_lock_manager.h

- **Purpose:** Declares a base class for range-capable lock managers, reducing point-key locks to single-point range locks.
- **Important APIs/types/functions:** `RangeLockManagerBase` derives from `LockManager` and overrides point-key `TryLock` by constructing an `Endpoint` from the key and calling the range `TryLock(txn, cf, start, end, env, exclusive)` overload.
- **Control flow:** A point lock request becomes an inclusive range request where start and end are the same endpoint. Concrete range managers implement the range overload and inherit this point adapter.
- **State and persistence behavior:** The base class stores no state. Any lock state belongs to concrete range manager implementations.
- **Dependencies:** Depends on the abstract lock manager interface and transaction DB `Endpoint` type.
- **Integration points:** Used by range-lock-manager implementations and by custom range lock manager handles described in `transaction_db.h`.
- **Risks:** Endpoint construction uses `key.data()` and `key.size()` for the duration of the call; concrete implementations must not retain raw endpoint memory without copying. The comment has a spelling typo but no behavior impact.
- **Test signals:** Range manager tests should verify that point-key `TryLock` delegates to a single-key inclusive range and respects exclusive/shared semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_lock_manager.h -->
