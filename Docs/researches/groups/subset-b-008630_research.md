# subset-b-008630 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_gflags.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_gflags.cc

## Purpose

`db_stress_gflags.cc` is the command-line surface for RocksDB's `db_stress` binary when built with gflags. It declares hundreds of `FLAGS_*` knobs that drive stress-test workload mix, DB option plumbing, table format options, cache and blob settings, fault injection, crash-recovery verification, compaction/flush/ingestion APIs, transaction modes, remote compaction, MultiGet/MultiScan behavior, and multi-DB execution.

The file is mostly declarative, but it is a central integration contract: other stress-tool translation units consume these globals through `DECLARE_*` and use them to construct `Options`, `ReadOptions`, `WriteOptions`, stress workloads, listener behavior, expected-state tracking, and fault-injection settings.

## Important APIs, Types, and Functions

- `ValidateUint32Range()` rejects unsigned 64-bit flag values that must later fit into `uint32_t`. It is registered for flags such as `seed`, `blob_direct_write_partitions`, `subcompactions`, `num_iterations`, `ops_per_thread`, and `log2_keys_per_lock`.
- `RegisterDbStressBdwFlagValidators()` registers the validator for `FLAGS_blob_direct_write_partitions` from inside `ROCKSDB_NAMESPACE`, allowing Blob Direct Write validation to be called from the main stress setup code.
- `ValidateInt32Positive()` enforces nonnegative integer flags such as `reopen` and `kill_random_test`.
- `ValidateInt32Percent()` enforces percent flags in `[0,100]` for read, prefix, write, delete, range-delete, no-overwrite, and iterator workload ratios.
- `ValidatePrefixSize()` enforces `prefix_size` in `[-1,8]` for hash/prefix memtable configurations.
- The `DEFINE_*` declarations use defaults from `ROCKSDB_NAMESPACE::Options`, `ColumnFamilyOptions`, `BlockBasedTableOptions`, `ReadOptions`, `WriteOptions`, `LRUCacheOptions`, `ShardedCacheOptions`, `TieredCacheOptions`, `AdvancedColumnFamilyOptions`, and BlobDB option defaults so command-line defaults track RocksDB option defaults.
- `extern "C" bool RocksDbIOUringEnable() { return true; }` opts this binary into io_uring support when the platform/build supports it.

Major flag groups include workload shape (`readpercent`, `writepercent`, `delpercent`, `iterpercent`, `customopspercent`, `ops_per_thread`, `threads`, `max_key`, key length distribution), database lifecycle (`db`, `destroy_db_initially`, `reopen`, `verification_only`, `read_only`, `num_dbs`), write path (`sync`, `disable_wal`, `manual_wal_flush_one_in`, `sync_wal_one_in`, `enable_pipelined_write`, `unordered_write`, transaction flags), compaction/flush/table settings, cache/tiered-cache settings, blob settings, compression/checksum settings, ingestion/checkpoint/backup APIs, fault injection, and expected-state/crash-recovery behavior.

## Control Flow and State Behavior

There is no runtime loop in this file. Its control flow is static initialization: gflags variables are defined before `main`, and selected validators are registered as static objects. If validation fails during flag parsing, gflags rejects the run before the stress test initializes.

The most important downstream state effects are indirect. `db_stress_test_base.cc` reads these flags while constructing DB options, registering `DbStressListener`, building table factories, enabling table-properties collectors, configuring caches/rate limiters/checksum factories, and deciding which optional operations are sampled inside `OperateDb()`. `db_stress_driver.cc` uses thread, verification, fault-injection, and multi-DB flags to orchestrate worker threads and background helpers. `db_stress_shared_state.*` uses flags such as `seed`, `max_key`, `log2_keys_per_lock`, `column_families`, `nooverwritepercent`, and expected-values settings to build the expected-state oracle and lock striping.

Several flags influence persistent artifacts. `expected_values_dir`, `sync_fault_injection`, `preserve_unverified_changes`, and `expected_state_trace_*` control external expected-state and trace files used across crash/restart runs. DB path flags and destroy/delete flags control the physical DB directory. Blob, WAL, checksum, table format, timestamp, temperature, and manifest flags influence persisted RocksDB files and metadata. `num_dbs` changes path interpretation by treating `--db` as a parent directory and creating `db_0`, `db_1`, and so on.

## Dependencies and Integration Points

The file depends on gflags compatibility macros, RocksDB public option classes, cache and backup headers, blob option types, and shared constants from `db_stress_common.h`. It is compiled only under `#ifdef GFLAGS`; without gflags, this translation unit contributes nothing.

Integration is broad:

- `db_stress_test_base.cc` consumes option flags and operation sampling flags.
- `db_stress_listener.h` consumes `seed`, fault-injection rates, `inject_error_severity`, and `compact_files_one_in`.
- `db_stress_shared_state.*` consumes expected-state, locking, fault-injection, and workload flags.
- `db_stress_table_properties_collector.h` consumes `mark_for_compaction_one_file_in`.
- Stress variants such as no-batched ops, batched ops, multi-ops transactions, and CF consistency consume workload and API feature flags.
- RocksDB option parsing and option files interact with this file through `options_file`; when an options file is specified, stress setup ignores flag values for options that are represented in that file.

## Risks and Edge Cases

Because this is the main CLI contract, incompatible defaults or missing validators can make stress runs invalid, ineffective, or misleading. Many flags are declared as wide integer types but later cast to narrower option fields; validator coverage matters for avoiding truncation. Percent flags are individually bounded, but this file does not enforce that workload percentages sum to a particular value; operation selection code must handle the configured mix.

Some flags are documented as mutually exclusive or requiring stable values across runs (`env_uri` vs `fs_uri`, `expected_values_dir` with fixed `seed`, `max_key`, `column_families`, and `nooverwritepercent`), but cross-flag compatibility is mostly enforced later. Release/debug differences matter for fault injection: read fault handling depends on debug-only sync-point behavior in `SharedState`.

Static initialization order is a residual risk around validators and gflags globals, especially for validators registered outside this file. Adding new flags that are consumed in headers requires matching `DECLARE_*` declarations and careful type alignment.

## Test Signals

Primary signals are successful `db_stress` startup with flag parsing/validation, stress runs covering selected APIs, and absence of assertions from consumers. Targeted useful configurations include fault-injection crash-recovery runs with `expected_values_dir`, compaction and ingestion sampling runs, transaction modes, table-properties collector runs with `mark_for_compaction_one_file_in`, blob/cache/tiered-cache combinations, and multi-DB runs through `num_dbs`.

Regression signals include gflags validation failures for out-of-range values, startup failures from incompatible expected-state settings, and downstream assertions in listener/shared-state code when a flag combination exposes invalid state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_gflags.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.cc

## Purpose

`db_stress_listener.cc` implements the non-inline parts of `DbStressListener` and `UniqueIdVerifier`. Together they make the stress test observe RocksDB event callbacks and verify that every generated SST extended unique ID remains unique across the current run and prior runs that share the same DB or expected-values directory.

The file is compiled only with gflags and complements the callback-heavy header. It handles persistent bookkeeping for `.unique_ids`, extracts extended unique IDs from table properties, and routes listener construction to shared stress-test state.

## Important APIs, Types, and Functions

- `DbStressListener::DbStressListener(...)` captures the DB name, DB paths, column-family descriptors, `SharedState`, and optional `FaultInjectionTestFS`. It chooses the unique-ID bookkeeping directory as `expected_values_dir` when present, otherwise the DB directory.
- `UniqueIdVerifier::UniqueIdVerifier(const std::string& dir)` creates `dir/.unique_ids`, loads any prior 24-byte IDs through a temporary rename/copy sequence, and verifies previously observed partial IDs.
- `UniqueIdVerifier::~UniqueIdVerifier()` closes the `WritableFileWriter` while temporarily clearing thread operation tracking to avoid reporting close work as a RocksDB operation.
- `UniqueIdVerifier::VerifyNoWrite()` decodes an 8-byte subsequence from a 24-byte ID and inserts it into an in-memory `unordered_set`; duplicates assert.
- `UniqueIdVerifier::Verify()` appends and flushes a new 24-byte ID to `.unique_ids`, then checks uniqueness under a mutex. It stops checking after roughly 4.29 million IDs to bound natural collision risk.
- `DbStressListener::VerifyTableFileUniqueId()` calls `GetExtendedUniqueIdFromTableProperties()` and passes the 24-byte result to `UniqueIdVerifier`.

## Control Flow and State Behavior

Construction first initializes listener fields, then constructs `UniqueIdVerifier`. The verifier uses the default local filesystem even if the tested DB uses a remote or warm filesystem. It creates the bookkeeping directory, renames an existing `.unique_ids` file to `.unique_ids.tmp` when possible, reads fixed 24-byte records, clears corrupt partial records as a non-DB warning, creates a fresh `.unique_ids`, copies old contents back with fsync, and deletes the temporary file.

On new table-file events, header callbacks call `VerifyTableFileUniqueId()`. That function extracts the extended unique ID from the reported `TableProperties`. `Verify()` appends the ID, flushes it, and then inserts the selected 64-bit subsequence into the process-local set. The append-before-check ordering preserves the new ID for future process executions even if a later assertion terminates the test.

Persistent state is limited to `.unique_ids` under either the expected-values directory or DB directory. It is intentionally local and separate from the DB filesystem to avoid weaker durability semantics from remote filesystems.

## Dependencies and Integration Points

The implementation uses `db_stress_listener.h`, `db_stress_test_base.h`, `file/file_util.h`, `rocksdb/file_system.h`, `util/coding_lean.h`, `WritableFileWriter`, `Env::Default()`, `CopyFile`, `Random::GetTLSInstance()`, `ThreadStatusUtil`, `TableProperties`, and `GetExtendedUniqueIdFromTableProperties()`.

It integrates with event callbacks defined inline in `db_stress_listener.h`, which invoke unique-ID verification on table creation and external file ingestion. `db_stress_test_base.cc` installs `DbStressListener` into DB options, making this verifier active during normal stress runs.

## Risks and Edge Cases

The `.unique_ids` file format is append-only fixed-width binary records. Any partial trailing record is treated as corrupt process-crash residue and clears the in-memory set after deleting the temp file. That avoids false DB failures from weak OS crash guarantees, but it also loses previous uniqueness evidence after corruption.

Only one 64-bit slice of each 24-byte ID is tracked in memory, with a random offset from 0 through 16. This is intentionally stronger than checking a predictable slice but still probabilistic. The verifier stops after a large threshold to keep the chance of natural collision acceptable.

Most failures assert or call `exit(1)`, which is appropriate for a stress binary but not recoverable library behavior. The local filesystem choice is deliberate but means the verifier can fail due to local path issues even when the DB filesystem itself is functional.

## Test Signals

Strong signals are `(Re-)verified N unique IDs` on startup, absence of duplicate-ID assertions, successful flush/compaction/external-ingestion events that call `VerifyTableFileUniqueId()`, and persistence of `.unique_ids` across repeated crash-test invocations. Failure signals include fixed-width read errors, copy/create failures, malformed unique IDs, and duplicate partial unique ID assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.h -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.h

## Purpose

`db_stress_listener.h` declares `UniqueIdVerifier` and defines almost all `DbStressListener` event callbacks inline. The listener is an active stress-test instrument: it validates event metadata, injects sleeps to perturb callback timing, toggles fault injection around background work, tracks compaction callback ordering, records persisted flush sequence numbers, verifies table-file paths, and checks SST unique IDs.

The file turns RocksDB's `EventListener` API into a broad callback correctness test. It is not passive logging; many callbacks assert invariants or abort on ordering bugs.

## Important APIs, Types, and Functions

- `UniqueIdVerifier` persists and checks 24-byte SST unique IDs through `Verify()`.
- `DbStressListener : public EventListener` overrides callbacks including `OnDBShutdownBegin`, `OnFlushBegin`, `OnFlushCompleted`, `OnTableFileDeleted`, `OnCompactionBegin`, `OnCompactionPreCommit`, `OnCompactionCompleted`, `OnSubcompactionBegin`, `OnSubcompactionCompleted`, `OnTableFileCreationStarted`, `OnTableFileCreated`, `OnExternalFileIngested`, file IO callbacks, background error/stall/pressure callbacks, and error recovery callbacks.
- `VerifyFileDir()`, `VerifyFileName()`, and `VerifyFilePath()` assert that table-file paths point at the configured DB paths, CF paths, or remote compaction temp output directories, and that filenames parse as `kTableFile`.
- `RandomSleep()` sleeps up to 5 ms using thread-local random state to expose lock ordering and callback timing issues.
- `FileNumberFromPath()` extracts SST file numbers from paths for compaction tracking.

Important internal state includes `num_pending_file_creations_`, `unique_ids_`, `shared_`, `db_fault_injection_fs_`, `last_bg_pressure_`, `compacting_files_`, `precommitted_jobs_`, and `shutting_down_`.

## Control Flow and State Behavior

Flush callbacks bracket background work. `OnFlushBegin()` enables thread-local read/write/metadata fault injection when a fault-injection filesystem exists. `OnFlushCompleted()` validates the CF and output path, sleeps, disables thread-local injection, and updates `SharedState` persisted sequence number to the flush job's largest sequence number.

Compaction callbacks enforce ordering. `OnCompactionBegin()` inserts each input file number into `compacting_files_` and aborts if another concurrent compaction already owns it. `OnCompactionPreCommit()` removes those file numbers and records them by `job_id` in `precommitted_jobs_`. `OnCompactionCompleted()` validates file paths and asserts the job had a matching PreCommit record. `OnTableFileDeleted()` aborts if a table file is deleted while still tracked as being compacted, except during DB shutdown when compaction callbacks can be skipped and tracking may be stale.

Table creation callbacks count pending creations, validate DB/CF/job metadata, verify table properties for successful creations, and run unique-ID checks. External ingestion similarly verifies the ingested table's unique ID.

Error recovery callbacks optionally disable all thread-local fault injection and exclude flush IO activities while recovery runs, then restore injection afterward. File read/write finish callbacks randomly sleep, with guaranteed sleeps for large IO, and `ShouldBeNotifiedOnFileIO()` always returns true through a `OneIn(1)` call after sleeping.

## Dependencies and Integration Points

The header depends on RocksDB listener APIs, table properties and unique-ID APIs, filename parsing, writable file writer support, `SharedState`, remote compaction service constants, fault-injection filesystem utilities, gflags declarations, atomic wrappers, and random utilities.

`db_stress_test_base.cc` installs the listener in DB options. `db_stress_listener.cc` implements construction and unique-ID verification. `SharedState` receives persisted sequence numbers and provides access to the stress test and fault-injection filesystem. Remote compaction temp path validation depends on `DbStressCompactionService::kTempOutputDirectoryPrefix`.

## Risks and Edge Cases

The listener intentionally runs assertions inside RocksDB callbacks. That gives strong signal but means false positives can terminate long stress runs. Shutdown is a known edge case: the listener suppresses deletion-vs-compaction checks after `OnDBShutdownBegin()` because compaction notifications may be skipped.

Compaction tracking assumes `job_id` uniqueness while jobs are between PreCommit and Completed and assumes input file info is complete in both callbacks. Changes to listener callback ordering, delayed deletion behavior, or compaction picker semantics can trip these invariants.

`num_pending_file_creations_` is an atomic counter and the destructor asserts it is zero. Missing `OnTableFileCreated()` callbacks or exceptional creation paths can leave it nonzero. Debug-only path validation is compiled out under `NDEBUG`, so release runs lose that signal.

Fault-injection toggling is thread-local in begin/end callbacks. Bugs in callback pairing could leave injection enabled or disabled for the wrong scope, and `OnErrorRecoveryBegin()` currently disables all thread-local injection rather than just a flush thread as noted by the TODO.

## Test Signals

Useful signals include no assertions from file-path validation, no duplicate SST unique IDs, no concurrent compaction of the same input file, every completed compaction having a prior PreCommit, no deletion while an SST is between Begin and PreCommit, and clean listener destruction with zero pending table creations. Fault-injection stress configurations should also show that recovery callbacks can temporarily suppress injection without leaving it disabled afterward.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.cc

## Purpose

`db_stress_shared_state.cc` implements `SharedState` construction and beginning-verification policy. It wires global stress flags into shared thread coordination state, the expected-state oracle, key-level locking, crash-recovery compatibility checks, and debug-only read-fault sync-point behavior.

The file is small, but it is the constructor path that determines whether a stress run uses anonymous in-memory expected state or durable expected-state files.

## Important APIs, Types, and Functions

- `thread_local bool SharedState::ignore_read_error` stores per-thread read-fault information used by debug sync-point callbacks.
- `SharedState::SharedState(Env*, StressTest*)` initializes counters, flags, atomics, no-overwrite key selection, expected-state manager, key locks, and optional read-fault callbacks.
- `SharedState::ShouldVerifyAtBeginning()` returns true when the stress test has a nonempty expected-values directory, enabling crash-recovery verification before new operations.

## Control Flow and State Behavior

The constructor initializes synchronization primitives and counters, seeds `GenerateNoOverwriteIds()` from `FLAGS_seed`, and records the start timestamp. If `expected_values_dir` is nonempty, it first checks that `std::atomic<uint32_t>` and `std::atomic<uint64_t>` are lock-free and rejects `clear_column_family_one_in > 0`, since persistent expected-state tracking cannot safely support that mode.

If compatibility checks pass, the constructor creates either `AnonExpectedStateManager` for normal in-process state or `FileExpectedStateManager` for crash-recovery state, then calls `Open()`. Any failure prints the status and exits.

When `FLAGS_test_batches_snapshots` is set, the constructor skips creating key locks because that mode performs limited batch verification and avoids the preallocated array locking scheme. Otherwise it computes the number of lock stripes from `max_key >> log2_keys_per_lock`, rounds up for leftover keys, creates one lock array per column family, and reports the total lock count.

For read or metadata read fault injection in debug builds, it installs a `SyncPoint` callback named `FaultInjectionIgnoreError` that sets `ignore_read_error`, then enables sync-point processing. In release mode, read fault injection exits as unsupported because the expected `IGNORE_STATUS_IF_ERROR` path is debug-only.

## Dependencies and Integration Points

The implementation depends on `db_stress_shared_state.h`, `db_stress_test_base.h`, expected-state manager classes, `FLAGS_*` globals from `db_stress_gflags.cc`, `Env::Default()->NowNanos()`, and `SyncPoint`.

`db_stress_driver.cc` uses the constructed `SharedState` to coordinate worker startup, operation, verification, and background thread shutdown. Operation implementations use its expected-state manager methods and key locks. `DbStressListener` updates persisted sequence number through it after flush completion.

## Risks and Edge Cases

The lock count calculation uses bit shifts derived from `log2_keys_per_lock`; invalidly large values are range-validated only as `uint32_t`, not necessarily bounded to avoid impractical stripe sizes or all keys mapping unexpectedly. `LockColumnFamily()` in the header iterates `max_key_ >> log2_keys_per_lock_` and does not include the rounded-up extra lock, so callers relying on whole-CF locking need attention when `max_key` is not an exact multiple.

Persistent expected-state mode has strict compatibility requirements. Changing `seed`, `max_key`, `column_families`, or no-overwrite settings across runs can invalidate recovery expectations even if construction succeeds. Unsupported read fault injection in release mode is enforced at startup.

Constructor failures call `exit(1)`, appropriate for the stress binary but abrupt. The `Env*` parameter is unused, so all timestamping uses the default environment rather than a custom environment.

## Test Signals

Good signals are successful expected-state `Open()`, lock creation messages with plausible counts, early crash-recovery verification when `expected_values_dir` is configured, and correct failure on unsupported combinations such as persistent expected state with column-family clearing. Debug read-fault runs should show ignored injected read errors through sync-point behavior rather than verification false positives.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.h -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.h

## Purpose

`db_stress_shared_state.h` defines the shared and per-thread state model for `db_stress`. It provides worker-thread barriers, key-range locking, expected-state accessors, remote compaction queues/results, verification failure flags, background-thread shutdown coordination, and per-thread random/stat/snapshot state.

This header is a central concurrency and state contract for the stress tool. Most operations go through `SharedState` before mutating expected values or coordinating with other threads.

## Important APIs, Types, and Functions

- `RemoteCompactionQueueItem` packages a remote compaction job id, `CompactionServiceJobInfo`, serialized input, output directory, and cancellation flag.
- `SharedState` exposes global mutex/condition variable access, thread count/counter methods (`IncInitialized`, `AllOperated`, `IncDone`, etc.), start flags, verification failure and stop flags, background thread counters, and `SafeTerminate()`.
- Key locking APIs include `GetMutexForKey()`, `LockColumnFamily()`, `UnlockColumnFamily()`, and `GetLocksForKeyRange()`.
- Expected-state APIs wrap the active manager: `SaveAtAndAfter()`, `Restore()`, `ClearColumnFamily()`, `SetPersistedSeqno()`, `GetPersistedSeqno()`, `PreparePut()`, `PrepareDelete()`, `PrepareSingleDelete()`, `PrepareDeleteRange()`, `Get()`, `Exists()`, `SyncPut()`, `SyncPendingPut()`, and `SyncDelete()`.
- Remote compaction APIs include `EnqueueRemoteCompaction()`, `DequeueRemoteCompaction()`, `AddRemoteCompactionResult()`, `GetRemoteCompactionResult()`, and `RemoveRemoteCompactionResult()`.
- `GenerateNoOverwriteIds()` deterministically chooses no-overwrite keys from `FLAGS_seed`, `FLAGS_max_key`, and `FLAGS_nooverwritepercent`.
- `ThreadState` stores worker id, per-thread `Random`, pointer to `SharedState`, `Stats`, and a queue of snapshot records.

## Control Flow and State Behavior

`SharedState` is constructed once per DB stress instance and then shared by all worker and helper threads. `db_stress_driver.cc` uses its mutex and condition variable to implement phases: worker initialization, operation start, operation completion, verification start, verification completion, and background-thread shutdown.

Expected-state methods are mostly thin dispatchers to `ExpectedStateManager`. Many write-preparation methods require callers to hold the relevant key or range locks, while read access can be lock-free depending on the manager method. `SetPersistedSeqno()` and `GetPersistedSeqno()` add a dedicated mutex around expected-state persisted sequence updates because listener callbacks and worker logic can access that value concurrently.

Key locks are striped by `key >> log2_keys_per_lock_` and stored per column family. `GetLocksForKeyRange()` computes all stripes covering `[start,end)`, using RAII `MutexLock` objects in ascending stripe order. This gives range deletes and scans a consistent locking strategy.

Remote compaction uses a mutex-protected FIFO queue for work and a mutex-protected result map keyed by scheduled job id. Producers enqueue compaction service jobs, worker threads dequeue them, and results are later looked up and removed.

`ThreadState` seeds each worker with `1000 + tid + shared seed`, giving repeatable but distinct random streams. Its snapshot queue tracks snapshots, associated CF/key/status/value, optional full key-vector state, and optional timestamp for later release/verification.

## Dependencies and Integration Points

The header depends on `db_stress_stat.h`, `expected_state.h`, optional `SyncPoint`, gflags declarations, RocksDB `Status`, `DB`, `Snapshot`, compaction service types, port mutex/condition variable primitives, `MutexLock`, and random utilities.

Integration points are widespread:

- `db_stress_driver.cc` owns phase coordination and final stats merging.
- `db_stress_test_base.cc` calls expected-state restore/save, thread operation loops, reopen barriers, and background helpers.
- `no_batched_ops_stress.cc`, `batched_ops_stress.cc`, `cf_consistency_stress.cc`, and transaction stress code use expected-state and stats APIs.
- `DbStressListener` updates persisted sequence number after flush callbacks.
- Remote compaction helpers use the queue/result methods to simulate service workers.

## Risks and Edge Cases

Most phase counters and start flags are protected only by the shared mutex by convention; callers must hold it when mutating or waiting. Atomics cover verification failure and stop flags, but not all counters. Misuse outside the expected lock discipline can cause missed wakeups or races.

Key-lock indexing assumes `key` is in range and the lock arrays were created. In `test_batches_snapshots` mode no locks are created, so lock APIs must not be used. Whole-column-family locking currently iterates the truncated stripe count, while constructor allocation rounds up when there is a partial final stripe.

Remote compaction result insertion uses `emplace`; duplicate job ids will preserve the first result silently. `GetRemoteCompactionResult()` performs a map lookup and then `at()` under the same lock, which is safe but assumes result strings are copied while locked.

Persistent expected-state correctness depends on stable flags across process executions and correct pairing of `Prepare*` and `Sync*` calls around DB mutations. Incorrect caller locking can corrupt the expected oracle even when RocksDB behaves correctly.

## Test Signals

Signals include all worker phases completing without deadlock, deterministic no-overwrite behavior for fixed seeds, correct crash-recovery verification from file-backed expected state, no verification failures, remote compaction workers draining queued jobs and returning results, and final merged stats reporting. Stress runs with `continuous_verification_interval`, remote compaction workers, fault injection, range deletes, and snapshots exercise the highest-risk paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_shared_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_stat.h -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_stat.h

## Purpose

`db_stress_stat.h` defines the `Stats` accumulator used by each stress worker and by the final merged report. It tracks operation counts, read/write/delete/iteration mix, bytes written, errors, CompactFiles outcomes, optional per-operation latency histograms, progress reports, and formatted throughput output.

The class is deliberately lightweight and lives in a header so worker code can update counters directly without a separate library component.

## Important APIs, Types, and Functions

- `Start()` resets all counters, clears the histogram, initializes progress reporting thresholds, and records start/last/finish timestamps from `SystemClock`.
- `Merge(const Stats&)` folds another thread's counters and histogram into the receiver and adjusts the aggregate start/finish time window.
- `Stop()` records finish time and elapsed seconds.
- `FinishedSingleOp()` optionally records latency since the previous operation, prints long-operation notices over 20 ms, increments `done_`, and emits progress messages according to an increasing threshold schedule.
- Counter helpers include `AddBytesForWrites`, `AddGets`, `AddPrefixes`, `AddIterations`, `AddDeletes`, `AddSingleDeletes`, `AddRangeDeletions`, `AddCoveredByRangeDeletions`, `AddErrors`, `AddVerifiedErrors`, `AddNumCompactFilesSucceed`, and `AddNumCompactFilesFailed`.
- `Report(const char*)` prints micros/op, ops/sec, write MB/sec, operation counts, error counts, CompactFiles counts, and optional histogram output under a static report mutex.

## Control Flow and State Behavior

Each `ThreadState` owns a `Stats` object. Worker operation loops call `Start()` before operations, update counters as operations execute, call `FinishedSingleOp()` per operation, and call `Stop()` when a run ends. `db_stress_driver.cc` merges all worker stats into thread zero and calls `Report()` unless the run is verification-only.

`FinishedSingleOp()` uses time since the last operation rather than operation-local start/stop spans. This measures inter-operation interval, including stress code overhead and blocking. Progress output begins at 100 operations and then increases thresholds gradually to reduce output volume for long runs.

`Report()` refuses to print normal throughput if either `bytes_` or `done_` is less than one. That avoids divide-by-zero but also means read-only or verification-only workloads without writes can print `No writes or ops?`.

## Dependencies and Integration Points

The class depends on RocksDB histogram implementation, port mutexes, `SystemClock`, gflags `histogram` and `progress_reports`, and RocksDB format macros for `size_t` printing.

It is embedded in `ThreadState` from `db_stress_shared_state.h`. Operation implementations in batched, no-batched, CF-consistency, and transaction stress files update the counters. Final aggregation is performed in `db_stress_driver.cc`.

## Risks and Edge Cases

`Stats` is not internally synchronized except for final report output. It assumes one thread mutates a given instance and merge happens after workers finish. Sharing a `Stats` instance concurrently would race.

`Merge()` assigns `covered_by_range_deletions_ = other.covered_by_range_deletions_` rather than adding it, which can underreport aggregate range-delete coverage across multiple threads. Other counters are additive.

The default constructor does not initialize fields; callers must call `Start()` before use. `Report()` depends on `finish_` and `start_` being set by `Start()`/`Stop()` and can produce misleading rates if `Stop()` was not called or if no writes occurred.

## Test Signals

Useful signals are progress messages during operation loops, final `Stress Test` throughput output, optional histogram output with `--histogram`, long-op notices for high-latency operations, and plausible aggregate counts matching configured workload percentages. Read-only or verification-only runs should be checked separately because the normal report path expects write bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_table_properties_collector.h -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_table_properties_collector.h

## Purpose

`db_stress_table_properties_collector.h` defines a stress-only table-properties collector and factory. The collector ignores actual key/value content for semantic purposes, emits one synthetic user-collected property, and randomly marks whole SST files as needing compaction based on `FLAGS_mark_for_compaction_one_file_in`.

Its main purpose is to exercise RocksDB's `TablePropertiesCollector` callback contract, user-collected properties path, and `NeedCompact()` plumbing under normal stress workloads.

## Important APIs, Types, and Functions

- `DbStressTablePropertiesCollector : public TablePropertiesCollector` implements `AddUserKey()`, `BlockAdd()`, `Finish()`, `GetReadableProperties()`, `Name()`, and `NeedCompact()`.
- The constructor samples `need_compact_` once with `Random::GetTLSInstance()->OneInOpt(FLAGS_mark_for_compaction_one_file_in)`.
- `Finish()` writes `db_stress_collector_property` as `keys_added;blocks_added;all_calls`.
- `GetReadableProperties()` returns the same property by calling `Finish()` through `const_cast`.
- `NeedCompact()` increments the mutable call counter and returns the pre-sampled `need_compact_`.
- `DbStressTablePropertiesCollectorFactory : public TablePropertiesCollectorFactory` creates a new collector per table build and reports its factory name.

## Control Flow and State Behavior

When RocksDB builds an SST, the factory creates one collector. As keys are added, `AddUserKey()` increments key and total-call counters. As data blocks are produced, `BlockAdd()` increments block and total-call counters. At finish or when readable properties are requested, the collector emits its synthesized counts. Whenever RocksDB asks whether the table should be compacted, `NeedCompact()` returns the constructor's fixed random decision.

The collector deliberately has unsynchronized mutable counters. The comments state this is meant to catch race conditions if RocksDB invokes collector methods concurrently despite collectors not being required to be thread-safe.

## Dependencies and Integration Points

The header depends on `rocksdb/table.h`, gflags compatibility, and thread-local random utilities. `db_stress_test_base.cc` clears and installs this factory in `options.table_properties_collector_factories` for stress runs, optionally adding other factories such as SstQueryFilter or CompactOnDeletion collectors afterward.

`FLAGS_mark_for_compaction_one_file_in` is defined in `db_stress_gflags.cc`. When nonzero, this collector can cause generated SSTs to request compaction, exercising read-triggered/collector-driven compaction paths.

## Risks and Edge Cases

`GetReadableProperties()` mutates state through `const_cast` by calling `Finish()`, so repeated readable-property requests increase `all_calls` and can change the emitted count. This is intentional stress behavior but may surprise code expecting idempotent readable properties.

The collector returns a raw pointer from the factory, matching the RocksDB API, so ownership transfer to RocksDB must remain correct. Because counters are unsynchronized, any future concurrent collector invocation may manifest as data races; that is part of the stress signal rather than a collector bug.

`OneInOpt()` behavior for zero or negative values determines whether compaction marking is disabled. The flag text says zero or negative means `NeedCompact()` always returns false, so changes to `OneInOpt()` semantics would affect this collector.

## Test Signals

Signals include successful SST builds with the synthetic property present, no sanitizer/race failures in collector callbacks, and compactions triggered when `--mark_for_compaction_one_file_in` is positive. The property value can also indicate whether `AddUserKey()`, `BlockAdd()`, `Finish()`, and `NeedCompact()` were called in expected proportions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_table_properties_collector.h -->
