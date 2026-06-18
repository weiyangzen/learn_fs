# subset-b-008632 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_tool.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_tool.cc

## Purpose
`db_stress_tool.cc` is the `db_stress` executable entry path under `#ifdef GFLAGS`. It parses command-line flags, validates cross-feature compatibility, builds the requested RocksDB environment and test harness, then launches one stress-test runner per configured DB. Its core responsibility is orchestration: it does not implement individual operations, but selects the correct `StressTest` subclass, initializes shared global resources, and enforces option combinations that would make later correctness checks unsound.

## Important APIs, types, and functions
The primary exported function is `int db_stress_tool(int argc, char** argv)`. File-local helpers include `ValidateNumDbsFlags()`, `DestroyAllDbs()`, `RegisterCrashCallbacks()`, and `ReturnFlagValidationError()`. The file owns process-lifetime guards for custom `Env` instances (`env_guard`, `legacy_env_wrapper_guard`) and a raw-pointer vector `fault_fs_for_crash_report` used only by crash callbacks. It also defines the global `KeyGenContext key_gen_ctx`.

## Control flow
Startup registers flag validators, parses gflags, sanitizes double-valued options, configures compression/checksum globals, and creates `raw_env` from `--env_uri` or `--fs_uri`. Early-exit flags destroy DBs or delete directories before full validation. The long validation block rejects incompatible percentages, snapshot modes, WAL/reopen settings, blob direct-write combinations, trie index modes, read-only mutations, best-efforts recovery misuse, transaction constraints, wide-column constraints, and multi-DB incompatibilities. It then chooses DB, expected-value, and secondary paths, initializes shared cache/write-buffer-manager/rate-limiter resources, creates one `StressTest` per DB through `CreateCfConsistencyStressTest`, `CreateBatchedOpsStressTest`, `CreateMultiOpsTxnsStressTest`, or `CreateNonBatchedOpsStressTest`, constructs `SharedState` objects, starts per-DB threads running `RunStressTest()`, joins them, and calls `CleanUp()`.

## State and persistence behavior
The file maps CLI options into durable path layout. For `--num_dbs > 1`, it creates parent DB and expected-value directories and appends `db_N` suffixes for each instance. Secondary directories are created under `--secondaries_base` or the Env test directory. `DestroyAllDbs()` destroys each DB path and removes the parent for multi-DB mode. It also initializes process-global cache, hot-key, WBM, and rate-limiter objects that are shared by every DB runner. Crash callback state is intentionally file-static because signal handlers cannot safely capture `StressTest` objects.

## Dependencies and integration points
This file integrates the common flag definitions in `db_stress_common.h`, the stress-test factory APIs in `db_stress_driver.h`, `SharedState`, Env/FS creation through `rocksdb/convenience.h`, fault injection through `utilities/fault_injection_fs.h`, and stack-trace crash callback registration through `port/stack_trace.h`. Its option validation gates protect downstream code in the batched, non-batched, CF consistency, and multi-op transaction tests from unsupported combinations.

## Risks and test signals
The largest risk is option drift: new stress features must be added to this validation matrix or they may run in configurations whose verification logic is invalid. Multi-DB mode is intentionally limited and rejects CF clearing and multi-op transaction testing. Blob direct-write support is deliberately narrow. Crash callback handling uses raw pointers guarded by process lifetime; cleanup nulls the vector entries after worker completion. Test signals are mostly executable behavior: invalid flag combinations should fail early with explicit errors, early destroy/delete flags should return accurate status, multi-DB path construction should isolate DBs, and injected FS failures should be printed on crashes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.cc

## Purpose
`db_stress_wide_merge_operator.cc` implements the wide-column-aware merge operator used by `db_stress` when merge operands need to follow the same value-generation rules as normal writes. It is compiled only with gflags support.

## Important APIs, types, and functions
The single implementation is `DBStressWideMergeOperator::FullMergeV3(const MergeOperationInputV3&, MergeOperationOutputV3*)`. It uses `MergeOperationInputV3::operand_list`, `MergeOperationOutputV3::new_value`, `MergeOperationOutputV3::NewColumns`, `GetValueBase()`, `GenerateWideColumns()`, and the global `FLAGS_use_put_entity_one_in`.

## Control flow
The method asserts non-empty operands and a valid output pointer, selects the last operand as the merge result basis, and rejects operands smaller than a `uint32_t` because they cannot encode a value base. It extracts `value_base` from the latest operand. If wide-entity generation is disabled (`FLAGS_use_put_entity_one_in == 0`) or the value base is not a selected multiple, the output is the raw latest operand. Otherwise it generates wide columns for that value base, switches `new_value` to the `NewColumns` variant, reserves space, and copies each column name/value into owned strings.

## State and persistence behavior
The operator is stateless. It has no persistent data and bases the merge result solely on the current operand list and the process-wide stress flag. Persistence effects happen later in RocksDB when the merged value or entity is materialized.

## Dependencies and integration points
It depends on the declaration in `db_stress_wide_merge_operator.h`, stress helpers in `db_stress_common.h`, and RocksDB's merge operator V3 API. It integrates with the validation logic that expects values derived from merge operands to match `GenerateValue`/wide-column generation behavior.

## Risks and test signals
The important correctness constraint is that the merge result must match the rules used by puts; otherwise validation reads would see a value shape the expected-state logic cannot explain. Returning false for malformed short operands is a corruption signal. Tests should cover raw value output, wide-column output, last-operand-wins semantics, and disabled wide-entity generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.h -->
# sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.h

## Purpose
`db_stress_wide_merge_operator.h` declares the test merge operator that lets `db_stress` exercise `MergeOperator::FullMergeV3` with both plain values and wide-column entities.

## Important APIs, types, and functions
The key type is `DBStressWideMergeOperator`, derived from `rocksdb::MergeOperator`. It overrides `FullMergeV3()` and `Name()`, returning `"DBStressWideMergeOperator"`. The comments document the essential semantic contract: like put-style merge operators, the result is based on the last merge operand, but may become a wide-column entity depending on the encoded value base and `use_put_entity_one_in`.

## Control flow
The header itself has no runtime control flow. Its declaration selects the V3 merge interface so the `.cc` file can return either a raw value or a wide-column result through the variant output type.

## State and persistence behavior
The class carries no fields. Merge behavior is entirely functional from the input operand list and global stress options, so instances can be shared without per-instance state.

## Dependencies and integration points
It includes `rocksdb/merge_operator.h` and lives in `ROCKSDB_NAMESPACE`. It is consumed by the stress option assembly path when merge testing and wide-column testing intersect. The declared behavior is also coupled to `GenerateWideColumns()` and value-base encoding in `db_stress_common.h`.

## Risks and test signals
Any future change to the expected value encoding or wide-column generation must keep this operator in sync. Because the class uses the V3 API, tests should ensure build configurations with `GFLAGS` still compile and that old merge interfaces are not accidentally selected for wide-column stress.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_wide_merge_operator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_state.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/expected_state.cc

## Purpose
`expected_state.cc` implements the expected-value state store used by `db_stress` to compare logical DB contents against what the stress workload believes should exist. It supports an anonymous in-memory mode and a file-backed, mmap-based mode with crash-recovery history. The file-backed manager can snapshot expected values at a DB sequence number, trace later writes, and restore expected values after recovery by replaying traced write batches.

## Important APIs, types, and functions
Core implementations include `ExpectedState::{PreparePut,PrepareDelete,PrepareDeleteRange,SyncPut,SyncDelete,Reset}`, `FileExpectedState::Open()`, `AnonExpectedState::Open()`, `FileExpectedStateManager::{Open,SaveAtAndAfter,HasHistory,Restore,Clean}`, and `AnonExpectedStateManager::Open()`. The internal `ExpectedStateTraceRecordHandler` implements both `TraceRecord::Handler` and `WriteBatch::Handler` to replay traced puts, timed puts, entities, deletes, single deletes, ranges, merges, blob index writes, and prepared-transaction markers.

## Control flow
`ExpectedState` stores one atomic `uint32_t` per `(cf,key)` plus an atomic persisted sequence number. Prepare methods load the current value, derive original/pending/final `ExpectedValue` states, precommit the pending state with a release fence, and return a `PendingExpectedValue` that must later commit or roll back. Sync methods directly force expected values during recovery or scan. `FileExpectedState::Open()` optionally creates zeroed files, mmaps state and persisted-seqno files, and resets new state to deleted. `FileExpectedStateManager::Open()` discovers prior `<seqno>.state` files, creates missing empty trace files for interrupted saves, cleans stale temps, creates `LATEST.state`/`PERSIST.seqno` if absent, then opens the latest mmap.

`SaveAtAndAfter()` copies `LATEST.state` to an atomic `<seqno>.state`, starts an unbuffered trace at `<seqno>.trace` with write order preserved, updates `saved_seqno_`, and removes the previous history pair. `Restore()` computes `db->GetLatestSequenceNumber() - saved_seqno_`, copies the saved state to a temp latest file, replays trace records until that many write operations have been applied, atomically renames the temp latest, reopens it, and deletes old state/trace files. Trace replay tolerates corrupt tail records only after enough writes have already been applied.

## State and persistence behavior
File-backed state uses `LATEST.state`, `PERSIST.seqno`, `<seqno>.state`, `<seqno>.trace`, and hidden `.<name>.tmp` files. Atomic rename is used for state publication. Traces must be an ordered superset of writes that can survive recovery: missing entries are fatal, extra suffix entries are allowed. Prepared transaction replay buffers writes between prepare markers, applies them on commit, and drops them on rollback. `Clean()` removes temp files and stale histories older than the selected saved sequence.

## Dependencies and integration points
This file depends on `ExpectedValue`, DB sequence numbers, file utilities, Env/FileSystem APIs, trace reader/writer/replayer APIs, wide-column serialization helpers, timestamp stripping helpers, `db_stress_common` key/value helpers, and `SharedState` flags for debug behavior. It is the persistence backing for crash-test expected values used by broader db_stress workloads.

## Risks and test signals
The main risks are replay/count mismatches, trace truncation, key parsing failures, timestamp stripping errors, and inconsistency between logical write effects and expected-value updates. Blob direct-write replay derives the next value base because traces store blob indexes rather than original values. DeleteRange replay treats the operation as one write op while mutating many expected keys. Debug counters for key decode failures, roundtrip mismatches, focus-key hits, emitted logs, and suppressed logs are useful test signals. Crash tests should exercise interrupted open/save/restore, prepared transaction commit/rollback, wide entities, timed puts, merges, blob indexes, and corrupted trace tails.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_state.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_state.h -->
# sources/storage-engines/rocksdb/db_stress_tool/expected_state.h

## Purpose
`expected_state.h` defines the abstraction for tracking db_stress expected values across keys and column families. It separates the logical API for expected-value mutation from the storage backing, allowing in-memory state for normal runs and file-backed state for crash/recovery tests.

## Important APIs, types, and functions
`ExpectedState` exposes `Open()`, `ClearColumnFamily()`, persisted-seqno accessors, `PreparePut()`, `PrepareDelete()`, `PrepareSingleDelete()`, `PrepareDeleteRange()`, `Get()`, `Exists()`, and sync methods. `FileExpectedState` adds mmap-backed state and persisted-seqno files. `AnonExpectedState` allocates atomics in memory. `ExpectedStateManager` wraps the latest state and exposes the same mutation APIs plus history APIs `SaveAtAndAfter()`, `HasHistory()`, and `Restore()`. `FileExpectedStateManager` persists history in a directory; `AnonExpectedStateManager` reports history unsupported.

## Control flow
Callers interact through `ExpectedStateManager`. The manager opens a concrete latest state, forwards per-key operations, and delegates save/restore behavior to the concrete subclass. Prepare APIs return `PendingExpectedValue` tokens so the caller can bracket DB writes: mark expected state pending before the DB write and commit/rollback the token after knowing the write outcome.

## State and persistence behavior
State layout is a flat array indexed by `cf * max_key + key`. Each cell is an atomic `uint32_t` encoding the value base, deletion counter, pending-write bit, pending-delete bit, and deleted bit. `persisted_seqno_` is tracked separately. File-backed state stores the array and persisted sequence number in mmap files; anonymous state uses heap allocations. File manager constants define the on-disk naming scheme: `LATEST.state`, `<seqno>.state`, `<seqno>.trace`, `PERSIST.seqno`, and temp-file wrappers.

## Dependencies and integration points
The header includes RocksDB DB, Env, FileSystem, dbformat sequence-number types, file utilities, `ExpectedValue`, and string utilities. It is used by stress-test operation implementations that need expected-state tracking and by crash-test paths that need history restoration.

## Risks and test signals
Thread-safety is intentionally external: most mutation methods require callers to lock relevant keys or entire column families. Incorrect locking can produce expected-state races independent of DB correctness. The file-backed implementation assumes the mmap file sizes match exactly and that atomics are valid over mapped storage. Tests should verify prepare-token lifecycle assertions, CF clearing, range deletes, persisted sequence monotonicity, fresh anonymous open, file-backed reopen, and unsupported history methods on anonymous managers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_value.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/expected_value.cc

## Purpose
`expected_value.cc` implements transitions and helper predicates for the compact `ExpectedValue` bitfield used by db_stress expected-state tracking.

## Important APIs, types, and functions
The file implements `ExpectedValue::Put()`, `Delete()`, `SyncPut()`, `SyncPendingPut()`, `SyncDelete()`, `GetFinalValueBase()`, `GetFinalDelCounter()`, and the `ExpectedValueHelper` predicates `MustHaveNotExisted()`, `MustHaveExisted()`, and `InExpectedValueBaseRange()`.

## Control flow
`Put(true)` only marks pending write. `Put(false)` advances the value base, clears deleted, and clears pending write. `Delete(true)` refuses to create a pending delete when the key does not currently exist; otherwise it marks pending delete. `Delete(false)` advances the deletion counter, marks deleted, and clears pending delete. `SyncPut()` overwrites the value base from recovery/scan input, clears deleted and pending write, and also clears pending delete to recover from crashes during delete. `SyncDelete()` performs a final delete and clears pending write to recover from crashes during put.

Helper predicates compare a pre-read and post-read expected value. `MustHaveNotExisted()` requires the key to be deleted before the read and no write to have completed through the post-read final value base. `MustHaveExisted()` requires the key to be not deleted before the read and no delete to have completed through the post-read final delete counter. `InExpectedValueBaseRange()` accepts value-base wraparound at the 15-bit mask boundary.

## State and persistence behavior
All state is stored in the caller-owned `uint32_t` bitfield. This file does not persist directly, but its transitions determine the bytes stored by `ExpectedState` in memory or mmap files. The final-value helpers intentionally account for pending operations so readers can validate concurrent observations.

## Dependencies and integration points
The implementation depends on `expected_value.h` and `<atomic>` for fences used in the companion pending-value class. It is used by expected-state preparation, DB read validation, trace replay, and crash-recovery reconciliation.

## Risks and test signals
Boundary behavior matters: value bases wrap inside `VALUE_BASE_MASK` and deletion counters wrap inside `DEL_COUNTER_MASK`. Pending state must be cleared correctly on sync recovery paths or verification can report false positives after crashes. Unit tests should cover missing-key pending delete rejection, pending/final transitions, crash sync helpers, helper predicates across concurrent write/delete windows, and value-base wraparound.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_value.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_value.h -->
# sources/storage-engines/rocksdb/db_stress_tool/expected_value.h

## Purpose
`expected_value.h` defines the compact expected-value representation for db_stress. It encodes existence, value generation, delete generation, and pending operation state in one 32-bit word so expected state can be stored as a dense atomic array.

## Important APIs, types, and functions
`ExpectedValue` exposes bit-mask metadata, constructors, `Exists()`, `Read()`, mutation APIs, value-base and delete-counter accessors, pending-bit accessors, deleted-bit accessors, and final-state helpers. `PendingExpectedValue` is an RAII-like token that owns an in-flight transition and must be closed by `Commit()`, `Rollback()`, or `PermitUnclosedPendingState()`. `ExpectedValueHelper` provides read-validation predicates for concurrent operations.

## Control flow
Callers typically load an `ExpectedValue`, derive pending and final variants, store the pending variant before writing the DB, and then use `PendingExpectedValue` to publish either the final or original value. Copy/move constructors and assignment close the source token's pending state to preserve the invariant that only one live token is responsible for assertion closure. The destructor asserts that pending state was closed.

## State and persistence behavior
The 32-bit layout is: bits 0-14 value base, bit 15 pending write, bits 16-29 delete counter, bit 30 pending delete, bit 31 deleted. Initial construction defaults to deleted. `Commit()` and `Rollback()` use a release fence before storing final or original raw values into the atomic pointer. This prevents expected-state publication from being reordered before the corresponding DB write boundary.

## Dependencies and integration points
The header depends on standard atomics and RocksDB namespace configuration. It is directly embedded in `ExpectedState` cells, used by validation helpers in db_stress operations, and interpreted by recovery trace replay.

## Risks and test signals
Because fields share one word, all setters must validate masked values and clear old bits before setting new ones. `Exists()` asserts no pending state, so callers must not use it for ambiguous concurrent windows. The copy/move behavior is unusual and should be tested because it mutates the source token's closure state. Tests should cover bitfield masks, wraparound, pending token commit/rollback, destructor assertions in debug builds, and helper behavior during pending writes/deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/expected_value.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.cc -->
# sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.cc

## Purpose
`multi_ops_txns_stress.cc` implements a specialized db_stress workload for RocksDB `TransactionDB`. It models a simple table with primary index `(a)` and secondary index `(c,a)` and stresses multi-operation transactions that must keep both indexes mutually consistent.

## Important APIs, types, and functions
The file defines flags for key ranges, key-space persistence, snapshot-read delay, rollback probability, and write-prepared commit-cache eviction. It implements `KeyGenerator`, `Record` encode/decode helpers, `FinishInitDb()`, `ReopenAndPreloadDbIfNeeded()`, operation overrides (`TestGet`, `TestIterate`, `TestCustomOperations`, etc.), transaction bodies (`PrimaryKeyUpdateTxn`, `SecondaryKeyUpdateTxn`, `UpdatePrimaryIndexValueTxn`, `PointLookupTxn`, `RangeScanTxn`), verification (`VerifyDb`, `VerifyPkSkFast`), recovered prepared transaction handling, commit-time write batch injection, timestamped snapshot support, preload/scan routines, factory creation, and option validation.

## Control flow
Initialization processes recovered prepared transactions, checks whether the DB is empty, preloads fresh records or scans existing records, then finalizes per-thread key generators. Preload partitions `[lb_a,ub_a)` and `[lb_c,ub_c)` by thread, reserves one missing value per range, writes paired primary/secondary entries, and persists the key-space descriptor. Existing DB scan reads that descriptor, walks the primary index, reconstructs existing/missing key sets, and asserts the thread/key-space shape matches the prior run.

Runtime operation dispatch maps normal db_stress percentages to transaction scenarios: `TestGet` performs point lookup by primary key, `TestIterate` performs range scan over a secondary key prefix, and `TestCustomOperations` randomly chooses primary-key update, secondary-key update, or primary value update. Write transactions create a `Transaction`, lock/read required primary rows with `GetForUpdate`, modify primary and secondary index entries, prepare, optionally simulate application rollback via `Status::Incomplete`, write metadata to the commit-time write batch, and commit. Cleanup lambdas update stats on success and roll back plus undo key allocation on failure.

## State and persistence behavior
The workload does not use the normal expected-state array (`IsStateTracked()` returns false). Its logical state is the DB itself plus per-thread `KeyGenerator` objects tracking existing and non-existing `a` and `c` values. The key-space descriptor is a 16-byte file containing four fixed32 bounds. Transactions also write a monotonic metadata value via `GetCommitTimeWriteBatch()` under a fixed metadata key. Optional timestamped snapshots are created at commit time and old ones are periodically released.

## Dependencies and integration points
The implementation depends on `multi_ops_txns_stress.h`, `db_stress_common.h`, `WriteBatchWithIndex`, `Defer`, fault-injection infrastructure, `WritePreparedTxnDB` test hook, TransactionDB APIs, iterators, snapshots, CRC32C, fixed-width encoding helpers, and `SharedState` error processing. It integrates with flush/compaction listeners through `VerifyPkSkFast()` and with the main tool through `CreateMultiOpsTxnsStressTest()` and `CheckAndSetOptionsForMultiOpsTxnStressTest()`.

## Risks and test signals
Correctness hinges on maintaining pk/sk bidirectional consistency under conflicts, rollbacks, prepared transaction recovery, snapshot reads, and background verification. Key-generator state is per thread and assumes stable thread count and key-space partitions across restarts. `SecondaryKeyUpdateTxn()` relies on snapshot plus conflict checking to ensure iterator-observed secondary entries match locked primary rows. Verification aborts on decode failures, missing counterpart entries, CRC mismatches, c-value mismatches, or count mismatches. Tests should exercise all three write transaction types, read-only transactions, rollback injection, recovered prepared transactions, timestamped snapshots, existing-DB scan, preload invariants, listener-triggered fast verification, and rejected option combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.h -->
# sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.h

## Purpose
`multi_ops_txns_stress.h` declares the multi-operation transaction stress workload. The header documents the table model, key/value encodings, and transaction scenarios used to validate TransactionDB consistency through paired primary and secondary indexes.

## Important APIs, types, and functions
The central type is `MultiOpsTxnsStressTest : public StressTest`. Nested `Record` owns encoding/decoding for primary keys, primary values, secondary keys, and secondary CRC values. `KeyGenerator` tracks existing and non-existing values within a per-thread subrange. Public overrides map the generic stress-test interface to this workload. Protected helpers choose/generate `a` and `c` values, process recovered prepared transactions, write commit-time metadata, commit with optional timestamped snapshot, and set up read snapshots. Private `KeySpaces` serializes persisted range bounds. `InvariantChecker` validates field widths, and `MultiOpsTxnsStressListener` verifies pk/sk consistency after flush and compaction.

## Control flow
The comments specify five logical transactions: primary-key update, secondary-key update, primary-index-value update, point lookup, and range scan. The class overrides generic write/delete/range-delete/ingest paths as unsupported or no-op because this workload only mutates through its custom transaction bodies. Listener callbacks short-circuit after shutdown starts and otherwise call fast verification for CF 0.

## State and persistence behavior
Record format is persisted directly in RocksDB: primary key is index id plus big-endian `a`, primary value is little-endian fixed32 `b,c`, secondary key is index id plus big-endian `c,a`, and secondary value is CRC32 of the secondary key. The `KeySpaces` struct persists lower/upper bounds for `a` and `c` in an external file. Runtime key-generator vectors are in-memory only and rebuilt by preload or scan.

## Dependencies and integration points
The header depends on `db_stress_common.h`, `util/atomic.h`, `StressTest`, `EventListener`, RocksDB transaction abstractions from the broader include graph, and thread/status/stat interfaces from db_stress. Factory functions are implemented in the `.cc` file and selected by the main tool when `FLAGS_test_multi_ops_txns` is set.

## Risks and test signals
The header captures several constraints that must remain true: index IDs must sort primary before secondary, record fields must stay 4 bytes, and current implementation uses only the default CF. Listener verification can run while `TransactionDB::Open()` is still completing, so the implementation must tolerate `db_` not yet being published. Tests should validate encode/decode round trips, CRC checks, unsupported generic operations, per-thread key generator invariants, listener shutdown behavior, and option gates for one-CF TransactionDB operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.h -->
