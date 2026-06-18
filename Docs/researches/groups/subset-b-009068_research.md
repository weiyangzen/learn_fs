# subset-b-009068 research

Work item: `subset-b-009068`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/debug_log_parser.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/debug_log_parser.h

Purpose: declares `model::debug_log_parser`, the adapter that reconstructs an in-memory `kv_database` from WiredTiger debug log records or a JSON printlog file. It is used after opening a database and before further writes, because the log may not describe most recent in-memory operations otherwise.

Important APIs and types: nested record structs model log entries (`col_put`, `col_remove`, `col_truncate`, `row_put`, `row_remove`, `row_truncate`, `commit_header`, `prev_lsn`, `txn_timestamp`). Static entry points `from_debug_log(kv_database &, WT_CONNECTION *)` and `from_json(kv_database &, const char *)` populate a database. Instance `apply` overloads map row/column puts, removes, truncates, timestamp records, and LSN records into model transactions and tables. `begin_transaction`, `commit_transaction`, `metadata_apply`, `metadata_checkpoint_apply`, and `table_by_fileid` support transaction and metadata reconstruction.

Control flow: callers invoke a static loader, which creates a parser, reads log entries, begins a model transaction from each commit header, applies operation records to that transaction, records timestamps, and commits/finalizes the transaction. Metadata row puts are handled specially to build table/file/checkpoint indexes before data records can be resolved by file ID.

State and persistence: the parser owns no database lifetime; it stores a reference to `kv_database`. Internal maps track metadata config maps, file-to-colgroup names, file-to-file IDs, file ID to file/table names, resolved file ID to `kv_table_ptr`, current base write generation, and accumulated checkpoint metadata keyed by transaction ID and checkpoint name. This mirrors persistent WiredTiger metadata into transient model state.

Dependencies and integration: includes `model/kv_database.h`, `model/util.h`, and `wiredtiger.h`. It integrates with `wt_print_debug_log` and `verify_using_debug_log` in test utilities, plus `kv_transaction::set_wt_metadata` and `kv_update::set_wt_transaction_metadata` for WT transaction identity.

Risks: correctness depends on metadata records being seen before data records that use their file IDs. The table/file ID maps are mutable parser state and are not advertised as thread-safe. Debug log import can be stale if called after additional writes. Buffer/config parsing errors or missing metadata produce model exceptions rather than partial verification.

Test signals: `verify_using_debug_log` opens a logged WT database, loads the model through both `from_debug_log` and JSON `from_json`, verifies every table against WT, and compares oldest/stable timestamps. A negative path injects a bogus model row and expects verification to fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/debug_log_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload.h

Purpose: defines the serializable workload language used to drive both the in-memory model and real WiredTiger. It gives tests a common operation stream for table creation, transaction lifecycle, timestamp control, checkpoint/crash/restart, and key-value operations.

Important APIs and types: `table_id_t`; mixins `with_txn_id`, `without_txn_id`, `with_table_id`, `without_table_id`; operation structs `begin_transaction`, `breakpoint`, `checkpoint`, `checkpoint_crash`, `commit_transaction`, `config`, `crash`, `create_table`, `evict`, `get`, `insert`, `nop`, `prepare_transaction`, `remove`, `restart`, `rollback_to_stable`, `rollback_transaction`, `set_commit_timestamp`, `set_oldest_timestamp`, `set_stable_timestamp`, `truncate`, and `wt_config`; `operation::any` as a `std::variant`; helpers `parse`, `transactional`, `transaction_id`, `table_op`, `table_id`; `kv_workload_operation`; and `kv_workload`.

Control flow: workload construction appends or prepends operations into an internal `std::deque`. Printing uses `std::visit` over the variant and per-operation `operator<<` overloads. Execution flows through `kv_workload::run(kv_database &)`, which delegates to the model runner, or `run_in_wiredtiger`, which delegates to the WT runner. `verify` checks stream validity before execution; `verify_noexcept` converts exceptions into boolean failure.

State and persistence: `kv_workload` is only an operation sequence and source sequence metadata; it does not own persistent data. Persistence effects are encoded by operations such as checkpoint, timestamp setting, rollback-to-stable, crash, restart, and transactional writes, then realized by the runners.

Dependencies and integration: includes `model/core.h`, `model/data_value.h`, `model/kv_database.h`, and `model/util.h`. It is consumed by `kv_workload_generator`, `kv_workload_runner`, `kv_workload_runner_wt`, and test helpers such as `verify_workload`.

Risks: adding an operation requires updating the variant, printer/parser, both runners, generator logic if applicable, and verification rules. `operation::table_id` throws if called on non-table operations. `get` operations intentionally do not encode expected values, and the model runner has a FIXME to use read values. Equality methods for stateless operations ignore the unused parameter by returning true.

Test signals: workload tests can compare return-code vectors from model and WT execution. The stream printer/parser is testable through round trips, while `verify_noexcept` offers quick rejection for invalid transaction/table ordering and timestamp ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_generator.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_generator.h

Purpose: declares the random workload generator that builds valid, dependency-aware `kv_workload` instances for model-vs-WiredTiger testing.

Important APIs and types: `kv_timing_stress_spec` holds weighted timing stress options and a `total` function. `kv_workload_generator_spec` holds probabilities and bounds for disaggregated mode, tables, sequences, concurrent transactions, record/value ranges, table type, timestamp usage, logging, operation mixes, existing-key choices, prepared transaction behavior, rollback choices, and timing stress. `kv_workload_generator::generate`, `generate_stress_configurations`, and `generate_log_configurations` are the public factories.

Control flow: construction stores a spec, seed, random engine, table contexts, and sequence list. `run()` creates tables and operation sequences, assigns dependencies, traverses them through `sequence_traversal`, assigns timestamps, and flattens runnable operations into a `kv_workload`. `sequence_traversal` tracks per-sequence dependency counts, runnable queues, and optional barriers such as timestamp assignment boundaries.

State and persistence: generator state is transient but models future database state through `table_context`, which records table IDs, names, formats, type, known keys, and operation counts. Key state steers selection of existing keys and removal/update effects so later generated operations stay meaningful. The produced workload may create durable WT effects when executed.

Dependencies and integration: includes `kv_workload.h`, `kv_workload_sequence.h`, and `random.h`. It depends on table type from `kv_table`, `data_value` formats, and probability macros from `random.h`. The generated workload is then consumed by both runners and `verify_workload`.

Risks: probability weights and dependency traversal must avoid invalid schedules, deadlocks, or timestamp regressions. `sequence_state` stores raw pointers under an assumption of non-concurrent traversal. Existing-key tracking is approximate relative to WT rollback/conflict behavior. Configuration strings generated for timing stress and logging must remain compatible with WT config syntax.

Test signals: useful tests check deterministic generation for a seed, validity via `kv_workload::verify`, successful model/WT return-code agreement, and coverage of prepared, rollback, crash, checkpoint, RTS, row, column, logged, and disaggregated cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner.h

Purpose: declares and mostly defines the in-memory model runner for workload operations. It translates `operation::any` entries into calls on `kv_database`, `kv_table`, and `kv_transaction`.

Important APIs and types: `kv_workload_runner(kv_database &)`, `database()`, `run(const kv_workload &)`, and `run_operation(const operation::any &)`. Protected `do_operation` overloads handle every workload operation. Helpers `restart`, `add_table`, `table`, `add_transaction`, `remove_transaction`, and `transaction` manage runner-local ID maps.

Control flow: `run` iterates workload indexes, dispatching each variant through `std::visit`. Begin creates a model transaction and maps the workload transaction ID to it. Commit/rollback remove the transaction from the active map first, then finalize it. Create table creates a `kv_table`, infers table type from key/value formats, sets formats, and records workload table ID. Writes/read/truncate call table APIs. Restart/crash clear runner transaction state and call `kv_database::restart`; checkpoint, timestamps, and RTS call database APIs.

State and persistence: runner state is only workload ID mapping for tables and live transactions. Persistent modeled state lives in `kv_database`. The transaction and table maps are protected by `std::shared_mutex`; `restart` clears live transactions because WT sessions would not survive a restart.

Dependencies and integration: includes `kv_workload.h`, `kv_database.h`, `kv_table.h`, `kv_transaction.h`, and `wiredtiger.h` for return codes. It is the implementation behind `kv_workload::run`.

Risks: workload IDs must be unique and valid or model exceptions are thrown. `config` only understands `database`; `wt_config`, `evict`, `breakpoint`, and `nop` are no-ops in the model. `get` returns WT-style codes but currently ignores the returned value. Clearing transactions on restart may mask workload streams that incorrectly reference old transactions.

Test signals: compare model runner return-code vectors to WT runner vectors in `verify_workload`. Unit tests should check duplicate/missing table and transaction IDs, timestamp errors, restart/crash behavior, and that no-op WT-only operations do not affect model state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner_wt.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner_wt.h

Purpose: declares the real WiredTiger runner for the workload language, including connection/session/cursor management and crash simulation support.

Important APIs and types: `kv_workload_runner_wt`, `k_config_base`, nested `session_context`, and C-compatible flexible `shared_state`. Public `run(const kv_workload &)` executes a workload in a WT home. Protected `do_operation` overloads implement every workload operation, plus `wiredtiger_open[_nolock]`, `wiredtiger_close[_nolock]`, `remove_local_files`, `add_table_uri`, `table_uri`, `allocate_txn_session`, `remove_txn_session`, and `txn_session`.

Control flow: `run` opens WT, prepares shared state, executes operations through `std::visit`, and records return codes. Table operations resolve workload table IDs to WT URIs. Transactional operations allocate per-transaction sessions, use cached cursors, and remove sessions at commit/rollback. Crash/checkpoint-crash use child/shared-state machinery so expected process death can be converted back into operation results and recovery can resume.

State and persistence: `_home` identifies the WT home. `_connection`, `_table_uris`, and `_sessions` are guarded by shared mutexes. `shared_state` stores crash index, expected crash flag, exception details, table URI states, database/connection/table config strings, and per-operation return codes across parent/child execution. Real persistence is WT data files in `_home`.

Dependencies and integration: includes `kv_workload.h`, `model/core.h`, and `wiredtiger.h`; it pairs with the implementation files outside this subset and is called by `kv_workload::run_in_wiredtiger` and `verify_workload`.

Risks: `shared_state` has fixed-size arrays and C strings (`tables[256]`, 256-byte configs/messages), so overlarge workloads/configs can overflow unless implementation bounds carefully. Cursor IDs assume 16 cursor slots per table. Correct lock discipline around connection/table/session maps is essential during restart/crash. Recovery must rebuild table URI state from shared memory accurately.

Test signals: `verify_workload` compares the WT runner return codes against the model runner, reopens the WT database, and verifies each table. Crash tests should exercise expected crash paths, recovery continuation, and correct preservation of table URI mappings and return-code prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_runner_wt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_sequence.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_sequence.h

Purpose: defines dependency-aware operation sequences used internally by the workload generator before flattening to a serial `kv_workload`.

Important APIs and types: `kv_workload_sequence_type` categorizes sequences (`checkpoint`, `checkpoint_crash`, `crash`, `evict`, `restart`, `rollback_to_stable`, timestamp setters, `transaction`, etc.). `kv_workload_sequence` stores a serial sequence number, type, deque of `operation::any`, dependency list, and unblock list. Methods include append operators, `size`, indexed access, `operations`, `overlaps_with`, `dependencies`, `unblocks`, and `must_finish_before`.

Control flow: the generator builds sequences, uses `overlaps_with`/`contains_key` to infer conflicts, calls `must_finish_before` to wire dependency edges, and later traverses runnable sequences through `kv_workload_generator::sequence_traversal`. `unblocks` lets completion of one sequence decrement dependency counts for followers.

State and persistence: this class has only transient scheduling state. It indirectly models persistence conflicts by identifying operations that touch overlapping table/key ranges and ensuring their relative order is preserved.

Dependencies and integration: includes `kv_workload.h`, `core.h`, and `data_value.h`. It is owned by `kv_workload_generator` and has no WT dependency.

Risks: dependency edges store raw pointers, so sequence objects must outlive traversal. `contains_key` must understand point and range operations correctly or the generator can produce invalid concurrent schedules. Sequence numbers are the equivalent serial schedule order and must remain stable for timestamp assignment.

Test signals: generator tests should create overlapping inserts/removes/truncates across tables and assert dependency detection. Non-overlapping sequences should remain independently runnable. `must_finish_before` should add reciprocal dependency/unblock relationships exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/driver/kv_workload_sequence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_checkpoint.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_checkpoint.h

Purpose: defines `kv_checkpoint`, the model snapshot object representing a WT checkpoint's name, transaction snapshot, oldest timestamp, and stable timestamp.

Important APIs and types: constructor `kv_checkpoint(const char *, kv_transaction_snapshot_ptr, timestamp_t, timestamp_t)`, accessors `name()`, `oldest_timestamp()`, `snapshot()`, and `stable_timestamp()`, plus alias `kv_checkpoint_ptr`.

Control flow: `kv_database::create_checkpoint` constructs checkpoints with a snapshot of active transactions and timestamp bounds. Table reads with a checkpoint pass `ckpt->snapshot()` and stable timestamp into `kv_table_item` visibility checks.

State and persistence: checkpoints are immutable after construction and are stored in `kv_database` by name. They model persistent checkpoint visibility rather than owning table data. The stable timestamp is used as the default checkpoint read timestamp; oldest timestamp is retained for metadata comparisons.

Dependencies and integration: includes `core.h` and `kv_transaction_snapshot.h`. Used by `kv_database`, `kv_table`, `kv_table_item`, `verify`, debug-log import, and test checkpoint helpers.

Risks: checkpoint name pointer returned by `name()` is valid only while the object lives. A null or mismatched snapshot would corrupt visibility, but constructor accepts the pointer as provided. Checkpoint semantics rely on the database creating snapshots under the right locks.

Test signals: checkpoint tests should compare model checkpoint reads against WT checkpoint cursors, verify default and named checkpoint behavior, and cover stable timestamp reads and debug checkpoint-read timestamp overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_checkpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_database.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_database.h

Purpose: declares the top-level in-memory model database containing tables, active transactions, checkpoints, configuration, and oldest/stable timestamps.

Important APIs and types: `kv_database_config` with `disaggregated` and `leader`, default constructor and `from_string`; `kv_database` constructor/destructor; table/checkpoint creation and lookup; `set_config`, `config`; timestamp setters/getters; `begin_transaction`, `remove_inactive_transaction`, `txn_snapshot`; `restart`, `crash`, `start`, and `rollback_to_stable`.

Control flow: clients create tables and transactions through the database. Transaction creation captures a snapshot. Transaction commit/rollback eventually calls `remove_inactive_transaction`. Checkpoint creation captures a checkpoint snapshot and timestamp bounds. Restart/crash paths lock tables, transactions, and checkpoints in declared order, roll back or recover state, and call `start_nolock`. RTS walks tables with a stable timestamp and optional snapshot.

State and persistence: persistent model state is `_tables`, `_checkpoints`, `_oldest_timestamp`, and `_stable_timestamp`; live state is `_active_transactions` and `_last_transaction_id`. The destructor calls `clear()` to break circular references between active transactions and updates. Timestamp setters enforce monotonicity and oldest <= stable.

Dependencies and integration: includes `kv_checkpoint.h`, `kv_table.h`, and `kv_transaction.h`. It is used by runners, debug-log parser, verification tests, and WT utility macros.

Risks: locking order is explicitly documented and must be followed to avoid deadlocks. Recursive table/transaction locks are required because restart rolls back active transactions that also touch database state. `set_config` is not locked. Timestamp getters do not lock, so concurrent mutation may be risky despite timestamp setters locking.

Test signals: model tests should exercise table uniqueness, checkpoint uniqueness, transaction cleanup, timestamp monotonic errors (`EINVAL`), clean restart, crash restart, rollback-to-stable, disaggregated config, and memory cleanup with active transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_database.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table.h

Purpose: declares `kv_table`, the sorted key-value table model with timestamped versions, transactional write APIs, non-transactional convenience APIs, rollback-to-stable, and WT verification.

Important APIs and types: `kv_table_type` (`column`, `row`), `kv_table_config` (`log_enabled`, `type`), `kv_table::type_by_key_value_format`, name/type/format accessors, `timestamped`, `contains_any`, `get`/`get_ext`, `insert`, `update`, `remove`, `truncate`, `fix_timestamps`, `rollback_updates`, `clear`, `rollback_to_stable`, `verify`, `verify_noexcept`, and `verify_cursor`.

Control flow: table operations resolve or create `kv_table_item` entries in a sorted `std::map`. Transactional writes create `kv_update` objects tied to a transaction, add them to the item chain, and register them with the transaction. Non-transactional APIs use `with_transaction` to create a short transaction and commit/rollback. Reads delegate visibility to `kv_table_item`. Verification builds a `kv_table_verify_cursor` and compares WT cursor output.

State and persistence: `_data` is sorted by `data_value` and intentionally never removes map entries so references remain stable after releasing the table map lock. Each key's versions live in `kv_table_item`. `_config.log_enabled` disables timestamp semantics by forcing timestamps to none.

Dependencies and integration: includes `data_value.h`, `kv_table_item.h`, `kv_update.h`, `verify.h`, and `wiredtiger.h`; holds a `kv_database &` for transaction creation and disaggregated config. Used by runners, debug parser, and tests.

Risks: key/value formats must be set before WT integration calls `key_format()`/`value_format()`. Map entries are retained after removal, so long tests can accumulate tombstone items. `verify_cursor` is explicitly not thread-safe. Non-timestamped tables silently rewrite update timestamps to none.

Test signals: table tests compare model and WT behavior for insert/update/remove/truncate, overwrite false, row and column formats, timestamps, checkpoints, prepared conflicts, rollback, RTS, and verification failure cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table_item.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table_item.h

Purpose: declares the per-key version chain for a table, including visibility, prepared update detection, rollback, and timestamp repair.

Important APIs and types: `add_update`, `contains_any`, `exists`, `exists_opt`, checkpoint/transaction/latest `get` overloads, `get_latest`, `fix_timestamps`, `has_prepared`, `rollback_to_stable`, and `rollback_updates`. Protected helpers include `add_update_nolock`, `fail_with_rollback`, internal `contains_any`, internal `get`, and `has_prepared_nolock`.

Control flow: table writes append sorted `kv_update` instances through `add_update`. Reads pass transaction snapshot, transaction ID, read timestamp, and optional stable timestamp into internal `get`, which chooses the visible update or returns `NONE`. Checkpoint reads use stable timestamp and compare durable timestamps. RTS removes or rolls back updates newer than the stable timestamp or not visible to the supplied snapshot.

State and persistence: `_updates` is a deque of `shared_ptr<kv_update>` sorted by update ordering. A mutex protects per-key operations. The chain stores tombstones as updates with `NONE` values and may keep committed, prepared, and in-progress updates until rollback/cleanup.

Dependencies and integration: includes `data_value.h`, `kv_checkpoint.h`, and `kv_update.h`. It is embedded in `kv_table::_data` and depends on transaction snapshots from `kv_checkpoint` and `kv_transaction`.

Risks: update ordering and comparator semantics are central; incorrect insertion can break visibility. Prepared updates may cause conflicts at timestamps before commit. `fail_with_rollback` intentionally marks update failure and throws to simulate WT rollback. Durable timestamp handling differs from commit timestamp for checkpoint reads.

Test signals: tests should verify latest and timestamped reads, checkpoint reads, prepared conflict behavior, duplicate/no-overwrite failures, truncate tombstones, transaction rollback cleanup, RTS filtering, and `contains_any` across duplicate timestamp values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction.h

Purpose: declares model transactions, including state transitions, timestamps, snapshots, update ownership, rollback/commit behavior, and optional WT debug-log metadata.

Important APIs and types: `kv_transaction_state` (`in_progress`, `prepared`, `committed`, `rolled_back`), `k_initial_commit_timestamp`, constructor, accessors for ID/timestamps/state/snapshot/failure, `visible_update`, `add_update`, `commit`, `prepare`, `fail`, `reset_snapshot`, `rollback`, `set_commit_timestamp`, `set_wt_metadata`, `wt_id`, and `wt_base_write_gen`.

Control flow: a transaction starts in progress with a database snapshot and a temporary max commit timestamp. Writes are incorporated into table item chains first, then registered through `add_update`. Prepare records a prepare timestamp and changes state. Commit fixes timestamps on registered updates, removes itself from the database active set, and marks committed. Rollback asks tables to roll back each update and marks rolled back. Reset snapshot obtains a new database snapshot.

State and persistence: the transaction stores commit/durable/prepare/read timestamps, snapshot pointer, database reference, update lists, nontimestamped update list, failed flag, atomic state, and WT transaction metadata. It must not outlive its database. Update lists create shared-pointer cycles with updates until commit/rollback cleanup.

Dependencies and integration: includes `core.h`, `data_value.h`, `kv_transaction_snapshot.h`, and `kv_transaction_update.h`; interacts with `kv_database`, `kv_table`, and `kv_update`. Runners and WT test macros drive lifecycle methods.

Risks: state transitions must be serialized by `_lock` and atomic state. `set_wt_metadata` is only valid before updates are added. A failed transaction should be rolled back by guards. The initial commit timestamp of max makes pre-commit updates sort late and must be repaired before visibility becomes final.

Test signals: transaction tests should cover commit with/without timestamps, durable timestamp, prepare/commit/rollback, reset snapshot visibility, failed guard rollback, WT metadata import, and invalid state transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_snapshot.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_snapshot.h

Purpose: declares snapshot polymorphism used to decide whether an update is visible to a transaction or checkpoint.

Important APIs and types: abstract `kv_transaction_snapshot` with virtual `contains(const kv_update &)`. `kv_transaction_snapshot_by_exclusion` stores `exclude_after` plus a set of excluded transaction IDs. `kv_transaction_snapshot_wt` stores WT write generation, min/max transaction IDs, and excluded WT snapshot IDs. Alias `kv_transaction_snapshot_ptr`.

Control flow: database snapshot creation returns one of these implementations. Reads call `snapshot->contains(update)`. Exclusion snapshots hide updates from transactions newer than the snapshot boundary or explicitly active/excluded. WT snapshots emulate WiredTiger visibility using write generation and WT transaction metadata imported from debug logs.

State and persistence: snapshots are immutable value objects held by transactions and checkpoints. They do not mutate database state, but they preserve a point-in-time view even after active transactions change.

Dependencies and integration: includes `core.h` and forward-declares `kv_update`. Used by `kv_database`, `kv_transaction`, `kv_checkpoint`, `kv_table_item`, and debug-log parser.

Risks: snapshot correctness depends on `kv_update` retaining model transaction IDs and optional WT transaction metadata after commit. Imported WT snapshots need accurate write generation, min/max, and exclusion lists. A wrong `contains` implementation would affect all visibility, checkpoint, and RTS behavior.

Test signals: tests should create concurrent transactions with active exclusions, verify snapshot reads before and after commits, compare WT debug-log imported visibility, and cover checkpoint snapshots with committed and active transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_update.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_update.h

Purpose: defines the lightweight record connecting a transaction to one table/key/update entry.

Important APIs and types: constructor `kv_transaction_update(const char *table_name, const data_value &key, std::shared_ptr<kv_update> &update)`, `key()`, `table_name()`, and `update()`.

Control flow: when a table adds an update for a transaction, the transaction stores a `kv_transaction_update` record. Later commit fixes timestamps through the update pointer, and rollback locates the table/key to remove the update chain entry.

State and persistence: stores table name as a string, key as a copied `data_value`, and shared pointer to `kv_update`. It intentionally avoids a table pointer because table ownership/lifetime and circular references are more complex.

Dependencies and integration: includes `data_value.h` and forward-declares `kv_update`. Owned by `kv_transaction` update lists and created by table write paths.

Risks: table name lookup during rollback/commit assumes the table still exists. Returning `update()` as a shared pointer can extend update lifetime. The constructor takes a shared pointer reference but stores a copy, so callers must still handle cycles.

Test signals: transaction commit/rollback tests implicitly cover this wrapper by verifying all touched keys have timestamps fixed or updates removed, especially multi-table transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_update.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_update.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/kv_update.h

Purpose: declares the stored version object for a table item, carrying value, timestamps, transaction state, and WT debug-log transaction metadata.

Important APIs and types: comparators `commit_timestamp_comparator` and `prepare_timestamp_comparator`; constructors for timestamped standalone update and transaction-backed update; comparison operators; `value`, `global`, `commit_timestamp`, `durable_timestamp`, `committed`, `prepared`, `txn`, `txn_id`, `txn_state`, `set_timestamps`, `remove_txn`, `set_wt_transaction_metadata`, `wt_txn_id`, and `wt_base_write_gen`.

Control flow: table writes create updates with either immediate timestamps or a transaction pointer. Visibility checks inspect commit/durable timestamps, transaction state, snapshot membership, and prepared state. Commit repairs timestamps, then may drop the transaction pointer through `remove_txn` while preserving transaction ID. Debug-log import sets WT metadata for WT snapshot emulation.

State and persistence: stores commit timestamp, durable timestamp, `data_value`, model transaction ID, optional `kv_transaction_ptr`, WT transaction ID, and WT base write generation. A value of `NONE` represents deletion/tombstone. `global()` means non-timestamped update.

Dependencies and integration: includes `data_value.h` and `kv_transaction.h`. Used by `kv_table_item`, `kv_transaction`, and `kv_transaction_snapshot`.

Risks: `operator<` returns true after all equality-like comparisons fall through, which is unusual and relies on callers checking equality separately; changes could affect sorted update chains. Prepared comparator uses prepare timestamp when available. Dropping the transaction pointer too early would lose state needed by prepared/commit checks.

Test signals: tests should cover update ordering by commit timestamp, duplicate timestamp/value cases, prepared visibility, durable timestamp checkpoint reads, global updates for logged tables, transaction pointer removal after commit, and WT metadata snapshot behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/kv_update.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/random.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/random.h

Purpose: provides a thin deterministic random wrapper around WiredTiger's `WT_RAND_STATE` plus probability/weight macros used by workload generation.

Important APIs and types: `random(uint64_t seed)`, static `next_seed`, `next_double`, `next_float`, `next_index`, `next_uint64()` overloads, and private `_random_state`. Macros `probability_switch`, `probability_case`, `probability_default`, `weight_init_block`, and `weight_init` implement compact weighted selection and total-weight initialization.

Control flow: generator code seeds `random`, asks for uniform floats/doubles or integers, and uses probability macros to choose operations. Weight macros build a closure that sums mutable weight fields in a spec object.

State and persistence: state is only the `WT_RAND_STATE`; no persistent data. Deterministic seeds create reproducible workloads and generated WT configs.

Dependencies and integration: includes `model/core.h` and WT internal header `wt_internal.h`, so it is tied to WiredTiger internals rather than standard C++ random. Used by `kv_workload_generator`.

Risks: `next_uint64(max)` multiplies a double by `max`, so distribution/bounds depend on floating-point behavior and assumes `max > 0`. `next_uint64(min,max)` assumes `max >= min`. Macros rely on hidden names and are sensitive to nesting.

Test signals: generator reproducibility tests should fix seeds. Unit checks should cover range bounds, `next_index(0)` handling if implementation rejects it, and probability branches with edge weights.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/util.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/util.h

Purpose: declares common RAII guards, configuration parsing, shared memory support, string/path helpers, and WT cursor/utility adapters used by the model and tests.

Important APIs and types: guards `wiredtiger_connection_guard`, `wiredtiger_cursor_guard`, `wiredtiger_session_guard`, and `kv_transaction_guard`; `config_map` with parsing, merge, typed getters, and keys; `shared_memory`; `at_cleanup`; string/path helpers `decode_utf8`, `directory_path`, `executable_path`, `model_library_path`, `ends_with`, `starts_with`, `parse_uint64`, `join`, `quote`; WT cursor helpers `wt_cursor_insert/remove/search/truncate/update`; build/disagg/table helpers `wt_build_dir_path`, `wt_disagg_config_string`, `wt_disagg_pick_up_latest_checkpoint`, `wt_evict`, `wt_extension_path`, `wt_list_tables`.

Control flow: guards close resources in destructors. `kv_transaction_guard` commits unless the transaction is failed, in which case it rolls back; destructor exceptions are logged to stderr. `config_map::from_string` parses WT-style nested configs into variant values. Cursor helpers set keys/values via `data_value` conversion then call WT APIs.

State and persistence: guards hold raw WT pointers but do not own data beyond closing resources. `shared_memory` owns a named shared-memory block for subprocess/runner communication. `config_map` stores parsed configuration in an unordered map.

Dependencies and integration: includes `core.h`, `data_value.h`, `kv_transaction.h`, and `wiredtiger.h`. Used throughout debug parsing, runners, generator config parsing, test utilities, and verification.

Risks: destructors swallow or log close/commit errors, which can hide cleanup failures. `config_map` typed getters throw `std::bad_variant_access` or runtime errors on bad keys/types. Shared memory lifetime depends on implementation cleanup. Cursor helpers assume cursor formats match `data_value` content.

Test signals: tests should cover config parser nesting/arrays/merge, RAII close paths, transaction guard commit/rollback, quote/decode parsing, path helpers, table listing, disaggregated config helpers, and WT cursor adapters through model/WT comparison tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/verify.h -->
## sources/storage-engines/wiredtiger/test/model/src/include/model/verify.h

Purpose: declares verification primitives that compare modeled table contents against WiredTiger table or checkpoint cursors.

Important APIs and types: `verify_exception`; `kv_table_verify_cursor` with `has_next`, `set_checkpoint`, `verify_next`, and `get_prev`; `kv_table_verifier` with `verify` and `verify_noexcept`.

Control flow: a table creates a verification cursor over its sorted map. Optional checkpoint must be set before iteration. `has_next` skips non-visible/tombstone model items; `verify_next` compares WT key/value pairs to expected model pairs and advances; `get_prev` supports diagnostics. `kv_table_verifier::verify` opens WT cursors and walks both sides.

State and persistence: verification cursor holds references to the table's map, an iterator, optional previous iterator, and optional checkpoint pointer. It does not persist data. `kv_table_verifier` stores a table reference and verbose flag.

Dependencies and integration: includes `data_value.h` and `wiredtiger.h`; uses `kv_table`, `kv_table_item`, and `kv_checkpoint` through declarations from included headers. Called by `kv_table::verify`, `verify_noexcept`, `verify_workload`, and `verify_using_debug_log`.

Risks: `verify_cursor` is documented as not thread-safe; the referenced table map must remain stable during verification. Checkpoint must be set at the beginning only. Diagnostic quality depends on `get_prev` and data value printing. WT cursor configuration must match table/checkpoint modes.

Test signals: positive tests compare model and WT after workloads; negative tests mutate the model and expect `verify_noexcept` false. Checkpoint verification should be tested separately from live table verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/verify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/test/model/test/CMakeLists.txt

Purpose: defines the CMake build wiring for model tests and shared test utilities.

Important APIs and targets: includes `cmake/helpers.cmake`; creates shared library `wiredtiger_model_test_common` from `common/subprocess.cpp`, `common/util.cpp`, and `common/wiredtiger_util.cpp`; sets public include directory `common/include`; sets private include directories for WT source include, test utility, and generated config; links `wiredtiger_model`, `wt::wiredtiger`, and `test_util`; creates test executables `test_model_basic`, `test_model_checkpoint`, `test_model_rts`, `test_model_transaction`, and `test_model_workload`; adds copy command/target for `test_model.sh`.

Control flow: common library is built first and linked into each test executable. The custom command copies the shell test script into the binary tree, and `wiredtiger_model_test_common` depends on that copy target.

State and persistence: no runtime model state. Build output is the shared utility library, test binaries, and copied script in the build directory.

Dependencies and integration: depends on project-level helper macros, WT targets, `wiredtiger_model`, and `test_util`. The `CXX NO_TEST_UTIL` options signal C++ test executables without default test utility wiring beyond explicit libs.

Risks: adding a new common source or test executable requires this file. The copy target dependency names `test_model.sh` as output/dep target and may need care if script location changes. Include directory visibility controls whether tests can include common headers.

Test signals: successful configuration/build should produce all five model test executables and the common shared library. CTest/script integration depends on copied `test_model.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/subprocess.h -->
## sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/subprocess.h

Purpose: declares a small subprocess harness for tests that need to isolate expected exits or crashes.

Important APIs and types: macros `in_subprocess` and `in_subprocess_abort`; class `subprocess_helper` with constructor/destructor, deleted copy/assign, `abort_if_child`, `exit_if_child`, `wait_if_parent`, `child`, and `parent`.

Control flow: the macros create a `subprocess_helper`, branch parent and child execution, wait in the parent, and exit or abort at the end of child scope. The helper constructor forks and installs monitoring; child code executes in the loop body; parent waits and then breaks.

State and persistence: stores child PID, sentinel path used to distinguish expected from unexpected child death, and previous SIGCHLD action. Persistent effects are temporary sentinel files under `/tmp`.

Dependencies and integration: includes POSIX process/signal headers and C `test_util.h`. Used by test code and indirectly by WT workload runner crash paths.

Risks: signal handling is process-global, so nested or concurrent subprocess helpers are sensitive. The macros rely on for-loop control flow and should be used carefully around returns/exceptions. Temporary sentinel cleanup must run in parent and child paths.

Test signals: tests should validate normal child exit, expected abort, unexpected child death failure, and restoration of prior SIGCHLD handler.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/subprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/util.h -->
## sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/util.h

Purpose: declares general model test helper utilities and assertions.

Important APIs and types: macro `model_testutil_assert_exception`; functions `create_tmp_file`, `current_time`, test-level `parse_uint64`, `parse_uint64_range`, `trim`, `verify_using_debug_log`, and `verify_workload`.

Control flow: exception assertion executes a call and fails via `testutil_die` unless the requested exception type is thrown. Parsing and trim helpers are direct utilities. `verify_using_debug_log` and `verify_workload` orchestrate full model/WT comparison flows implemented in `common/util.cpp`.

State and persistence: temporary files are created by `create_tmp_file`; verification helpers create or open WT homes and may generate debug-log JSON files. No global model state is stored in the header.

Dependencies and integration: includes `kv_workload.h`, `model/util.h`, and C `test_util.h`. It is part of `wiredtiger_model_test_common` public includes.

Risks: `parse_uint64` duplicates model namespace functionality for convenience until refactoring. Verification helpers assume valid WT test options and home paths. Temporary file helper creates a file even when only a name is needed.

Test signals: used across model tests for exception checks, workload validation, debug-log validation, range parsing, and timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/wiredtiger_util.h -->
## sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/wiredtiger_util.h

Purpose: declares WT-side test helper functions and macros that mirror model operations and assert model/WT equivalence.

Important APIs and types: functions `wt_get`, `wt_insert`, `wt_remove`, `wt_truncate`, `wt_update`; transaction helpers `wt_txn_begin`, `wt_txn_commit`, `wt_txn_prepare`, `wt_txn_reset_snapshot`, `wt_txn_rollback`, `wt_txn_set_commit_timestamp`, `wt_txn_get`, `wt_txn_insert`, `wt_txn_remove`; checkpoint/timestamp/debug helpers `wt_ckpt_get`, `wt_ckpt_create`, `wt_get_timestamp`, `wt_set_timestamp`, `wt_get_oldest_timestamp`, `wt_set_oldest_timestamp`, `wt_get_stable_timestamp`, `wt_set_stable_timestamp`, `wt_print_debug_log`, `wt_rollback_to_stable`; assertion and paired-operation macros.

Control flow: helper functions wrap WT sessions/cursors/transactions and return WT error codes for expected conflicts/not-found/rollback cases. Macros perform the same operation on model and WT, then compare return codes and values.

State and persistence: the helpers mutate the WT database via sessions and transactions. Macros rely on in-scope names such as `database`, `conn`, and `session`. Timestamps and checkpoints persist in WT metadata.

Dependencies and integration: includes `data_value.h`, `kv_database.h`, `wiredtiger.h`, and `test_util.h`. Implemented by `common/wiredtiger_util.cpp` and used by model unit tests.

Risks: macro scope assumptions can produce confusing errors. Helpers treat selected WT return codes as expected while `testutil_check` aborts on others. Config buffers are fixed-size in implementations. Paired macros must preserve operation order exactly to avoid model/WT divergence.

Test signals: these helpers are themselves exercised by all model/WT comparison tests; failures show as assertion differences in return codes or `data_value` output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/wiredtiger_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/subprocess.cpp -->
## sources/storage-engines/wiredtiger/test/model/test/common/subprocess.cpp

Purpose: implements `subprocess_helper`, including fork setup, SIGCHLD monitoring, sentinel-file handling, expected abort/exit paths, and parent wait.

Important APIs and functions: static `sentinel_stack`, static `handler_sigchld`, constructor, destructor, `abort_if_child`, `exit_if_child`, and `wait_if_parent`.

Control flow: construction creates a sentinel file in `/tmp`, pushes it on a stack, installs `handler_sigchld`, and forks. The signal handler waits for a child and, if the current sentinel still exists, treats child death as unexpected and fails the parent. Expected child exits remove the sentinel before exiting or killing self. The parent destructor removes the sentinel and restores the previous SIGCHLD handler.

State and persistence: global `sentinel_stack` supports nested helpers. Each helper owns one sentinel path and previous signal action. The only filesystem state is a temporary sentinel file.

Dependencies and integration: uses POSIX `fork`, `wait`, `waitpid`, `sigaction`, `kill`, `getpid`, `exit`, and `abort`; uses `test_util.h` assertions and `create_tmp_file`.

Risks: `handler_sigchld` calls functions from a signal handler that may not be async-signal-safe, but this is test code. Destructor assumes stack top matches the helper's sentinel. `wait_if_parent` only asserts `waitpid` success and does not inspect exit status, relying on sentinel/SIGCHLD for unexpected death.

Test signals: expected abort tests should remove the sentinel and not fail the parent. Unexpected child crashes should trigger `testutil_die`. Nested usage should preserve stack behavior and restore prior handlers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/subprocess.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/util.cpp -->
## sources/storage-engines/wiredtiger/test/model/test/common/util.cpp

Purpose: implements general model test utilities, including temp file creation, time/range/string helpers, debug-log verification, and workload model-vs-WT verification.

Important APIs and functions: `create_tmp_file`, `current_time`, `parse_uint64_range`, `trim`, `verify_using_debug_log`, and `verify_workload`.

Control flow: `create_tmp_file` builds a `mkstemps` template, creates/closes the file, and returns the path. `verify_using_debug_log` opens WT with logging, lists tables, loads a model from the live debug log, verifies each table, compares timestamps, prints the debug log to JSON, loads another model from JSON, verifies again, optionally injects a bogus model row to prove verification can fail, then closes session/connection. `verify_workload` runs the workload in the model, restarts the model to mimic recovery, recreates the WT home, runs the workload in WT, compares return-code vectors, opens WT, verifies all tables, and closes.

State and persistence: creates temporary JSON files and WT homes. Verification creates transient `kv_database` instances and opens/closes WT resources.

Dependencies and integration: includes `debug_log_parser.h`, `model/test/util.h`, `model/test/wiredtiger_util.h`, and `model/util.h`; uses `test_util.h` WT open/recreate helpers.

Risks: temp file paths use `alloca` and fixed suffix template assumptions. Debug-log verification requires logging enabled and no second WT instance mutating the database while printing. The negative verification path only works for string-key tables. `verify_workload` assumes model restart semantics line up with WT recovery.

Test signals: this file is the main integration signal for workload correctness and debug-log parser correctness: return-code equality, table verification success, timestamp equality, and intentional verification failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/wiredtiger_util.cpp -->
## sources/storage-engines/wiredtiger/test/model/test/common/wiredtiger_util.cpp

Purpose: implements WT test wrappers declared in `wiredtiger_util.h`, giving model tests concise WT operations with consistent timestamp, transaction, checkpoint, and debug-log behavior.

Important APIs and functions: `wt_get`, `wt_insert`, `wt_remove`, `wt_truncate`, `wt_update`, `wt_txn_begin`, `wt_txn_commit`, `wt_txn_prepare`, `wt_txn_reset_snapshot`, `wt_txn_rollback`, `wt_txn_set_commit_timestamp`, `wt_txn_get`, `wt_txn_insert`, `wt_txn_remove`, `wt_ckpt_get`, `wt_ckpt_create`, `wt_get_timestamp`, `wt_set_timestamp`, and `wt_print_debug_log`.

Control flow: simple operations begin a WT transaction, open cursors, set key/value via model helpers, execute cursor calls, tolerate expected return codes (`WT_NOTFOUND`, `WT_DUPLICATE_KEY`, `WT_PREPARE_CONFLICT`, `WT_ROLLBACK` depending on operation), close cursors, and commit or rollback with timestamp configs. Transaction helpers operate on an already active session transaction. Checkpoint reads open checkpoint cursors with optional debug read timestamp. Debug log printing opens a session, obtains the first LSN from WT internals, and calls `__wt_txn_printlog`.

State and persistence: mutates WT tables and connection timestamps. Checkpoints and debug logs are WT persistent artifacts. `wt_print_debug_log` reads internal WT connection state and writes a JSON/debug log file.

Dependencies and integration: includes `wiredtiger.h`, C `test_util.h`, WT log private header, `model/test/wiredtiger_util.h`, and `model/util.h`. Used by paired model/WT test macros and debug-log verification.

Risks: many config strings use 64-byte buffers; large timestamp formatting is safe for hex `uint64_t` but adding options could overflow if not resized. Some wrappers commit even after operation-level WT errors unless handled specially; truncate rolls back on `WT_ROLLBACK`. Direct use of WT internals (`WT_CONNECTION_IMPL`, `__wt_txn_printlog`) is version-sensitive.

Test signals: every paired macro depends on these wrappers. Failures show as unexpected `testutil_check` aborts, mismatched return codes, mismatched read values, timestamp mismatch, or inability to print debug logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/common/wiredtiger_util.cpp -->
