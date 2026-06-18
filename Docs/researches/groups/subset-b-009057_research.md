# subset-b-009057 Research

Grouped research report for the WiredTiger cppsuite framework, storage wrappers, utilities, and selected tests. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.cpp

## Purpose
Implements the default `database_operation` workload methods used by cppsuite tests: population, checkpointing, background compaction, custom no-op work, insert/read/remove/update loops, and default validation dispatch.

## Important APIs, Types, And Functions
Key entry points are `database_operation::populate`, `background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`, and `validate`. A file-local `populate_worker` partitions collections across `thread_worker` instances and inserts deterministic padded keys with pseudo-random values.

## Control Flow
`populate` validates collection/key/value/thread configuration, creates collections through the `database` model, starts one `thread_worker` per configured thread, joins via `thread_manager`, and deletes workers. Runtime operations loop while `thread_worker::running()` remains true. Insert workers keep one cursor per assigned collection and commit when `thread_worker::can_commit()` says the randomized operation target is reached. Read workers cache cursors per collection and walk with `next`, resetting at `WT_NOTFOUND`. Remove workers use paired random and normal cursors because random cursors cannot remove. Update workers select a random key below the model's current key count and call the generic tracked update path.

## State And Persistence Behavior
The file mutates WiredTiger tables through cursors and keeps the in-memory collection key count in sync only after successful insert commits. Transactions are explicitly begun, committed, or rolled back through `thread_worker`, which also records operation-tracking rows and timestamps. Cursor resets are used deliberately to avoid pinning pages or history. Background compact is enabled through `WT_SESSION::compact` with `background=true`; checkpointing periodically calls `WT_SESSION::checkpoint`.

## Dependencies And Integration Points
Depends on `thread_worker`, `database`, `configuration`, `timestamp_manager`, `operation_tracker`, `connection_manager`, `validator`, `random_generator`, `thread_manager`, and WiredTiger error codes such as `WT_NOTFOUND` and `WT_ROLLBACK`. It is the default behavior inherited by `test`, and concrete tests override individual methods to alter workload shape.

## Risks And Test Signals
The implementation assumes `collection_count >= thread_count` for insert/populate partitioning, so configs with too many threads assert. Key uniqueness depends on `key_count <= pow(10, key_size)`. Read operations roll back by operation count rather than committing. Update tracking uses `tracking_operation::INSERT` for value replacement, so validation treats the latest value as an upsert-style final state. Successful signals are normal thread completion, `SUCCESS` from the harness, operation tracker rows for validation, and nonzero compact/checkpoint activity where configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.h

## Purpose
Declares the polymorphic workload surface used by cppsuite tests. The class provides default database population, workload operation, and validation hooks that tests can override selectively.

## Important APIs, Types, And Functions
`class database_operation` exposes virtual methods for `populate`, `background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`, and `validate`. The API receives framework primitives such as `database`, `thread_worker`, `timestamp_manager`, `configuration`, and `operation_tracker`.

## Control Flow
The header defines the framework contract rather than direct flow. `test` inherits from this class, `workload_manager` selects operation types, and `operation_configuration` binds `thread_type` values to these virtual member functions. Override granularity is per operation type, letting a test keep the standard run lifecycle while replacing only one workload lane.

## State And Persistence Behavior
No state is stored in this class. Persistence behavior is indirect: implementations create collections, mutate WiredTiger tables, record operation tracker rows, and validate disk state. Virtual dispatch means the actual persistence behavior can differ substantially by concrete test.

## Dependencies And Integration Points
Includes `database.h` and `thread_worker.h`. It is integrated by `test.h` as a base class and by `operation_configuration.cpp` via `std::bind` dispatch.

## Risks And Test Signals
The base contract assumes override methods obey `thread_worker` transaction semantics and stop promptly when `running()` becomes false. Tests that override tracking schema should also override `validate`, because the default validation expects standard tracking table formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.cpp

## Purpose
Maps configured `thread_type` values to callable `database_operation` member functions so workload threads can execute the correct operation polymorphically.

## Important APIs, Types, And Functions
The constructor stores the source `configuration`, operation `thread_type`, and configured `THREAD_COUNT`. `get_func(database_operation *dbo)` returns a `std::function<void(thread_worker *)>` bound to the matching virtual operation method.

## Control Flow
`get_func` switches over all known `thread_type` enumerators: `BACKGROUND_COMPACT`, `CHECKPOINT`, `CUSTOM`, `INSERT`, `READ`, `REMOVE`, and `UPDATE`. Each case uses `std::bind` with the supplied `database_operation` instance and a `thread_worker *` placeholder. An unexpected enum value aborts via `testutil_die(EINVAL, ...)`.

## State And Persistence Behavior
The file does not directly mutate database state. It influences persistence by selecting which operation loop a thread will execute and therefore which WiredTiger APIs, tracking rows, and timestamps are used.

## Dependencies And Integration Points
Depends on `operation_configuration.h`, `constants.h`, `database_operation`, and `thread_worker`. It is used by the workload manager layer when converting parsed test configuration into runnable thread functions.

## Risks And Test Signals
Adding a new `thread_type` requires updating this switch; otherwise the framework aborts at runtime. The returned `std::function` captures `dbo` by pointer, so the owning `test` object must outlive operation threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.h

## Purpose
Declares a small helper that binds workload operation configuration to executable thread functions.

## Important APIs, Types, And Functions
`operation_configuration(configuration *config, thread_type type)` captures the parsed config pointer and operation type. `get_func(database_operation *dbo)` returns the operation callback. Public fields expose `config`, `type`, and `thread_count`.

## Control Flow
The header defines the dispatch object used by workload orchestration. It does not create threads itself; it supplies the thread function chosen in the `.cpp` implementation.

## State And Persistence Behavior
The class keeps a non-owning `configuration *` and immutable operation metadata. It does not persist data, but its selected callback determines database mutation behavior.

## Dependencies And Integration Points
Includes `<functional>`, `configuration.h`, `database_operation.h`, and `thread_worker.h`. It sits between workload configuration parsing and `thread_manager` thread creation.

## Risks And Test Signals
The public raw `configuration *` is non-owning and must remain valid while the operation configuration is used. `thread_count` is read at construction, so later config mutations would not be reflected.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/operation_configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.cpp

## Purpose
Implements the base cppsuite test lifecycle: parse configuration, construct framework components, open the WiredTiger connection, start components, wait for population, run for the configured duration, stop, validate, and emit performance metrics.

## Important APIs, Types, And Functions
`test::test` wires `configuration`, `timestamp_manager`, `workload_manager`, `thread_manager`, optional `metrics_monitor`, database timestamp/config settings, and component list membership. `init_operation_tracker` creates or installs the operation tracker. `run` performs the complete test lifecycle. The destructor releases owned components.

## Control Flow
Construction prepares components but does not run them. `run` builds the `wiredtiger_open` config from compression, reverse collator, cache size, statistics, logging, background compact debug, cache wait, in-memory mode, file sweep interval, and user config. It removes the home directory, creates the connection, loads all components, starts each component on `thread_manager`, polls until `workload_manager::db_populated()`, sleeps for `DURATION_SECONDS`, calls `end_run`, joins component threads, calls `finish`, optionally validates, writes perf stats, and logs `SUCCESS`.

## State And Persistence Behavior
The class owns heap-allocated framework components and a `database` model. It recreates the test home directory before opening WiredTiger, so previous artifacts are removed. It configures collection creation behavior for compression and reverse collator. Validation uses the operation tracker table names and the workload manager database model.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `metrics_writer`, `configuration`, `timestamp_manager`, `workload_manager`, `metrics_monitor`, `operation_tracker`, `thread_manager`, and `connection_manager`. Concrete test classes usually only define a constructor and override selected `database_operation` hooks.

## Risks And Test Signals
Raw pointers require the destructor to stay aligned with constructor/init paths. `init_operation_tracker` must be called by concrete tests before `run`, otherwise `_operation_tracker` is null when validation or workload tracking is expected. Connection configuration strings are assembled manually and may be sensitive to malformed user `wt_open_config`. Test success is signaled by component completion, optional validation passing, perf file output, and final `SUCCESS` log.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.h

## Purpose
Declares the base `test` class and `test_args` struct used by cppsuite concrete tests.

## Important APIs, Types, And Functions
`test_args` carries `test_config`, `test_name`, optional `wt_open_config`, and `home`. `class test` inherits `database_operation`, deletes copy/assignment, exposes `init_operation_tracker` and virtual `run`, and stores protected `_args`, `_config`, `_timestamp_manager`, and `_operation_tracker`.

## Control Flow
The header defines ownership boundaries: framework components are private, while selected configuration and timestamp/tracker members are protected for test overrides. Concrete tests typically derive from `test`, call `init_operation_tracker` in the constructor, and override operation methods inherited from `database_operation`.

## State And Persistence Behavior
Private state includes enabled component pointers and an in-memory `database` model. Persistent WiredTiger state is managed indirectly through `run` and `connection_manager`.

## Dependencies And Integration Points
Includes `database_operation.h`, `metrics_monitor.h`, `workload_manager.h`, and `connection_manager.h`. This header is included by nearly every cppsuite test implementation.

## Risks And Test Signals
Because `_args` is stored by reference, the caller must keep the `test_args` object alive for the test lifetime. Custom tests can access protected internals, which is useful but can bypass lifecycle invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.cpp

## Purpose
Implements the per-thread execution context used by workload operations. It wraps configuration, session/cursor state, timestamps, operation tracking, transaction state, throttling, collection partitioning, and generic CRUD helpers.

## Important APIs, Types, And Functions
`type_string` formats `thread_type`. Constructors initialize config-derived fields, the session, optional barrier, tracker cursor, sleep duration, and operation-per-transaction bounds. CRUD helpers are `insert`, `update`, `remove`, and `truncate`. Transaction helpers include `begin`, `try_begin`, `commit`, `rollback`, `try_rollback`, `can_commit`, `active`, `set_commit_timestamp`, and op-count accessors.

## Control Flow
Generic mutations obtain a timestamp, set it on the active transaction when timestamping is enabled, invoke `crud` helpers or WiredTiger truncate, write an operation tracker row, and either increment operation count or mark rollback required on `WT_ROLLBACK`. `begin` randomizes the target operation count for this transaction. `can_commit` requires an active transaction, no rollback requirement, and enough operations. Collection assignment evenly divides database collections by worker id and distributes remainders to low ids.

## State And Persistence Behavior
The worker owns its `scoped_session`, optional operation tracker cursor, optional statistics cursor, transaction wrapper, sleep interval, operation counters, and running flag. Inserts/updates/removes are persisted through WiredTiger cursors and mirrored to operation tracking tables. `truncate` can operate over whole collections or cursor-bounded ranges. The worker itself does not own the `database`, timestamp manager, or tracker.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `random_generator`, `crud`, `transaction`, `scoped_session`, `scoped_cursor`, `operation_tracker`, `timestamp_manager`, and `barrier`. It is consumed by all default and custom operation loops.

## Risks And Test Signals
`op_tracker` is asserted non-null for CRUD helpers, so tests must initialize tracking even if validation is disabled. `set_commit_timestamp` intentionally accepts `EINVAL` as a rollback signal due to timestamp races with stable timestamp movement. `sync` assumes `_barrier` is non-null. The generic `update` records `tracking_operation::INSERT`, making validation model updates overwrite prior value state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.h

## Purpose
Declares `thread_worker`, the state container passed to every workload function, and `thread_type`, the operation categories supported by the framework.

## Important APIs, Types, And Functions
`enum class thread_type` covers background compact, checkpoint, custom, insert, read, remove, and update. `thread_worker` exposes CRUD wrappers, transaction wrappers, timing and barrier utilities, collection partition helpers, and public immutable config fields such as `collection_count`, `free_space_target_mb`, `key_count`, `key_size`, `value_size`, `thread_count`, `type`, and `id`.

## Control Flow
The class acts as the operation-loop context. Callers use `running()` to control loops, `sleep()` for throttling, `begin`/`commit`/`rollback` for transaction control, and `finish()` to request shutdown.

## State And Persistence Behavior
Owns a `scoped_session`, operation tracker cursor, statistics cursor, transaction object, op counters, target operation count, optional barrier pointer, and `_running` flag. Holds references or pointers to shared `database`, `timestamp_manager`, and `operation_tracker`.

## Dependencies And Integration Points
Includes `database`, `operation_tracker`, `timestamp_manager`, `configuration`, `scoped_cursor`, `scoped_session`, `transaction`, and `barrier`. This is the common integration object for `database_operation`, workload manager, and test overrides.

## Risks And Test Signals
The class has many public fields to simplify tests, so invariants are convention-based. A moved `scoped_session` is expected to be valid before cursor use. Long-running operations must check `running()` frequently or test shutdown will block on joins.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.cpp

## Purpose
Implements a small transaction state machine over `WT_SESSION` transaction APIs for use by `thread_worker`.

## Important APIs, Types, And Functions
`active`, `begin`, `commit`, `rollback`, `set_needs_rollback`, and `needs_rollback` manage `_in_txn` and `_needs_rollback`.

## Control Flow
`begin` asserts no active transaction, calls `begin_transaction`, and clears rollback state. `commit` asserts the transaction is active and not marked for rollback, calls `commit_transaction`, accepts `0`, `EINVAL`, or `WT_ROLLBACK`, logs nonzero failures, clears `_in_txn`, and returns success status. `rollback` asserts active, calls `rollback_transaction`, clears rollback state, and marks inactive.

## State And Persistence Behavior
State is in-memory only, but it gates all persisted WiredTiger writes done by `thread_worker`. WiredTiger may internally roll back a transaction when commit returns `WT_ROLLBACK`; this wrapper treats the transaction as inactive afterward.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `scoped_session`, and `test_util`. Used exclusively by `thread_worker` as its transaction member.

## Risks And Test Signals
`EINVAL` during commit is tolerated because timestamp races can make a commit timestamp older than the stable timestamp. Callers must not call `commit` after `set_needs_rollback`; `thread_worker::can_commit` enforces that. Unexpected begin/rollback failures abort via `testutil_check`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.h

## Purpose
Declares the transaction wrapper used by worker operations to track active and rollback-required state around WiredTiger transactions.

## Important APIs, Types, And Functions
Public methods are `active`, `begin`, `commit`, `rollback`, `set_needs_rollback`, and `needs_rollback`. Private fields are `_in_txn` and `_needs_rollback`.

## Control Flow
The header provides the state-machine interface. Workers begin a transaction, mutate via CRUD helpers, set rollback-needed on recoverable conflicts, and then either commit or rollback based on the wrapper state.

## State And Persistence Behavior
The wrapper does not own sessions or cursors; it receives `scoped_session &` per call. It only stores transaction state flags, while the actual persisted state lives in WiredTiger.

## Dependencies And Integration Points
Includes `scoped_session.h` and `wiredtiger.h`. Integrated by `thread_worker` and indirectly by all workload operation implementations.

## Risks And Test Signals
The interface relies on correct sequencing by callers. It does not expose a reset other than successful rollback or commit, so callers should not abandon an active transaction without resolving it.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.cpp

## Purpose
Implements default cppsuite validation by replaying operation-tracking rows into an in-memory model and comparing that model with on-disk WiredTiger collections.

## Important APIs, Types, And Functions
Primary method is `validator::validate`. Helpers are `parse_schema_tracking_table`, `update_data_model`, `verify_collection`, `verify_collection_file_state`, and `verify_key_value`.

## Control Flow
Validation opens a session and operation tracking cursor, checks that the tracking table schema matches default expected key/value formats, parses schema tracking rows to build created/deleted collection lists, verifies deleted collections are absent, compares created collection ids with the database model, then walks the operation tracking table sorted by collection id. When the collection id changes, the current reconstructed map is verified against disk before processing the next collection.

## State And Persistence Behavior
The validator reads operation and schema tracking tables and table files but does not intentionally mutate them. It builds a `validation_collection` map from tracked keys to existence/value state. `DELETE_KEY` requires the key to exist and not already be deleted; `INSERT` creates or replaces the current model value.

## Dependencies And Integration Points
Depends on `logger`, `connection_manager`, `database`, standard containers, `tracking_operation`, and default operation-tracking schema constants. Called by `database_operation::validate` when operation tracking is enabled and the test has not supplied custom validation.

## Risks And Test Signals
Default validation aborts if a test uses a custom tracking schema, so such tests must override `validate`. The implementation assumes operation tracking rows are ordered by collection id and that dropping is not generally supported by the standard database model. It validates only tracked final state; missing tracker rows can make disk state appear valid incorrectly. Success is absence of `testutil_die`/assert failures after all collections and keys are checked.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.h

## Purpose
Declares the default validation algorithm and supporting data structures for replaying tracked operations.

## Important APIs, Types, And Functions
`key_state` stores expected existence and value. `validation_collection` aliases `std::map<key_value_t, key_state>`. `validator::validate` is public; helper methods for schema parsing, model updates, collection/file verification, and key/value verification are private.

## Control Flow
The public API receives operation tracker table name, schema tracker table name, and the in-memory `database` model. Private helpers reconstruct expected state and compare it to on-disk records.

## State And Persistence Behavior
`validator` itself is stateless. Temporary maps model expected collection contents during validation.

## Dependencies And Integration Points
Includes `database.h` for collection names and key/value type aliases. Used by `database_operation.cpp` as the default validation backend.

## Risks And Test Signals
Validation is designed for the default operation tracker schema only. The map is sorted by key, which aligns with deterministic verification but may become memory-heavy for very large tracked workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/main/validator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.cpp

## Purpose
Implements a singleton owner for the active WiredTiger connection and factory for RAII sessions.

## Important APIs, Types, And Functions
`connection_manager::instance`, destructor, `close`, `create`, `reopen`, `create_session`, `get_connection`, `set_timestamp`, and private constructor are implemented here.

## Control Flow
`create` rejects reopening when `_conn` is non-null, logs the open config, asserts the home path does not already exist, creates the home directory, optionally creates a journal directory and nested subdirectories, then calls `wiredtiger_open`. `reopen` opens an existing home without creating it. `create_session` validates `_conn`, locks `_conn_mutex`, constructs a `scoped_session`, and returns it by move. `set_timestamp` serializes calls with the same mutex.

## State And Persistence Behavior
Owns the process-wide `WT_CONNECTION *`. `create` creates filesystem directories for WiredTiger homes and opens persistent database state. `close` closes the connection and nulls the pointer. The singleton destructor closes any remaining connection.

## Dependencies And Integration Points
Depends on `logger`, `test_util`, `scoped_session`, WiredTiger C API, and `SUB_DIR` constants. Used by `test::run`, population, validation, and custom tests needing sessions or direct connection APIs.

## Risks And Test Signals
Only session creation and timestamp setting are mutex-protected; callers using `get_connection` directly must handle their own synchronization where necessary. `create` asserts the home path is absent, while `test::run` removes it first. A failed close/open aborts through test utility checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.h

## Purpose
Declares the connection singleton used by the framework to manage one WiredTiger connection and create sessions.

## Important APIs, Types, And Functions
Public singleton API includes `instance`, deleted copy/assignment, destructor, `close`, `create`, `reopen`, `create_session`, `get_connection`, and `set_timestamp`. Private state is `_conn` and `_conn_mutex`.

## Control Flow
The header defines controlled construction through `instance()` and prevents copies. Callers open a connection with `create` or `reopen`, then request sessions or direct connection access.

## State And Persistence Behavior
The manager owns the active `WT_CONNECTION *` and mediates access to session creation and global timestamp mutation. Persistent data lives under the configured WiredTiger home.

## Dependencies And Integration Points
Includes `scoped_session.h` and mutex support. This type is referenced by the base harness and tests that need direct `WT_CONNECTION` APIs such as compiled configurations or cache reconfiguration.

## Risks And Test Signals
Direct `get_connection` access bypasses the mutex and returns a raw pointer. Because it is a singleton, tests in the same process must close or isolate connections carefully to avoid "connection is not NULL" failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/connection_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.cpp

## Purpose
Implements RAII ownership and move semantics for `WT_CURSOR *`.

## Important APIs, Types, And Functions
Constructor opens a cursor through `reinit`. Move constructor and move assignment transfer cursor ownership by swapping. Destructor closes the cursor. Pointer-like access is exposed through `operator*`, `operator->`, and `get`.

## Control Flow
`reinit` asserts a non-empty URI, closes any currently owned cursor, and opens a new one when a non-null session is supplied. Move assignment constructs a temporary from the source and swaps internals so the old cursor closes when the temporary is destroyed.

## State And Persistence Behavior
Owns a single cursor pointer. The wrapper does not persist by itself but all cursor operations performed through it may read or mutate WiredTiger state. Destruction closes the cursor and can release pinned pages/resources.

## Dependencies And Integration Points
Depends on `test_util` and WiredTiger session/cursor APIs. Returned by `scoped_session::open_scoped_cursor` and stored widely in workers and tests.

## Risks And Test Signals
`operator->` and `operator*` assume `_cursor` is non-null; callers must check `get()` when using default-constructed or moved-from objects. Closing errors abort through `testutil_check`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.h

## Purpose
Declares the move-only RAII cursor wrapper used throughout cppsuite.

## Important APIs, Types, And Functions
`scoped_cursor` supports default construction, construction from `WT_SESSION *`, URI, and config, move construction, move assignment, `reinit`, pointer-like operators, and `get`. Copy construction and copy assignment are deleted.

## Control Flow
The interface lets tests treat the wrapper like a `WT_CURSOR *` while preserving single ownership and automatic close behavior.

## State And Persistence Behavior
Private state is `_cursor`. Persistence effects depend on the cursor methods invoked by callers.

## Dependencies And Integration Points
Includes `wiredtiger.h`. It is the common cursor type in `thread_worker`, storage wrappers, validators, and test overrides.

## Risks And Test Signals
Moved-from cursors become null and must not be dereferenced. Default construction is useful for optional cursors such as worker stats cursors but requires later initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.cpp

## Purpose
Implements RAII ownership and move semantics for `WT_SESSION *`, plus a helper to open `scoped_cursor` objects.

## Important APIs, Types, And Functions
Constructor calls `reinit`, destructor closes the session, move constructor and assignment swap ownership, `close_session` explicitly closes, `reinit` opens a session from a connection, pointer-like operators expose the session, and `open_scoped_cursor` returns a cursor wrapper.

## Control Flow
`reinit` closes any existing session, then calls `WT_CONNECTION::open_session` when a non-null connection is supplied. Move assignment mirrors the cursor wrapper: move-construct a temporary and swap so old state closes at scope exit.

## State And Persistence Behavior
Owns one session pointer. Session lifetime controls implicit cursor cleanup in WiredTiger and transaction context. `close_session` sets the wrapper to null after close.

## Dependencies And Integration Points
Depends on `test_util`, `scoped_cursor`, and WiredTiger APIs. Created by `connection_manager::create_session` and stored in `thread_worker`.

## Risks And Test Signals
Pointer-like operators assume a valid session. `close_session` does not guard against null before calling close, so callers should only use it on an initialized wrapper. Session close errors abort.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.h

## Purpose
Declares the move-only RAII session wrapper used for WiredTiger session lifetime management.

## Important APIs, Types, And Functions
`scoped_session` supports default construction, construction from `WT_CONNECTION *`, move construction, move assignment, `reinit`, pointer-like operators, `get`, `open_scoped_cursor`, and `close_session`. Copy operations are deleted.

## Control Flow
The interface encourages session ownership transfer into workers and local validation scopes while keeping cursor opening concise.

## State And Persistence Behavior
Private state is `_session`. Persistent effects are through transaction, cursor, checkpoint, compact, and truncate calls made by users of the session.

## Dependencies And Integration Points
Includes `scoped_cursor.h` and `wiredtiger.h`. It is returned by `connection_manager` and used in nearly all cppsuite database interactions.

## Risks And Test Signals
Moved-from or default sessions have null `_session`; dereferencing them is invalid. Cursor wrappers created from a session should not outlive the session.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/storage/scoped_session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.cpp

## Purpose
Implements a reusable thread barrier for cppsuite environments that do not rely on C++20 `std::barrier`.

## Important APIs, Types, And Functions
`barrier::barrier(std::size_t thread_count)` initializes threshold, count, and generation. `barrier::wait` blocks until enough threads arrive or logs a timeout.

## Control Flow
`wait` takes the mutex, decrements `_count`, and if the arriving thread is last, increments `_generation`, resets `_count`, and notifies all. Otherwise it waits up to `_sync_timeout` and logs `Barrier timed out!` on timeout.

## State And Persistence Behavior
State is in-memory synchronization state only. It does not affect database persistence except by coordinating when worker threads proceed.

## Dependencies And Integration Points
Depends on `barrier.h` and `logger`. Used by `thread_worker::sync` when a barrier pointer was supplied.

## Risks And Test Signals
The current wait call does not use `_generation` as a predicate, so spurious wakeups are not explicitly filtered. A timeout logs a warning but does not abort or keep waiting, so tests using it should treat timeout logs as suspicious.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.h

## Purpose
Declares a simple reusable synchronization barrier for multiple worker threads.

## Important APIs, Types, And Functions
`barrier` deletes copy/assignment, provides `barrier(std::size_t thread_count)`, `wait`, and default destructor. Private fields include mutex, condition variable, threshold, current count, generation, and a 600-second timeout.

## Control Flow
Callers construct it with the number of participating threads and each calls `wait` at synchronization points.

## State And Persistence Behavior
Only transient synchronization state is stored. There is no filesystem or WiredTiger persistence.

## Dependencies And Integration Points
Includes condition variable and mutex headers. Integrated through `thread_worker` optional shared barrier pointer.

## Risks And Test Signals
All expected participants must call `wait`; otherwise waiters time out. Because the barrier is reusable, callers must avoid destroying it while workers can still call it.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.cpp

## Purpose
Implements aggregation of operation timing samples into a metrics writer statistic.

## Important APIs, Types, And Functions
`execution_timer::execution_timer` stores metric id and test name. `append_stats` sorts recorded nanosecond timings and records the 90th percentile as `<id>_nanoseconds_90th_percentile`. The destructor appends stats when samples exist.

## Control Flow
The templated `track` method in the header records samples. The `.cpp` destructor emits metrics at object lifetime end, typically when a custom operation exits.

## State And Persistence Behavior
Stores timing samples in memory. Persists only through `metrics_writer::instance().add_stat`, later emitted by the test harness perf output.

## Dependencies And Integration Points
Depends on `<algorithm>`, `<cmath>`, `execution_timer.h`, and `metrics_writer`. Used by API timing and bounded cursor performance tests.

## Risks And Test Signals
`append_stats` indexes `floor(size * 0.9)` after sorting; it is guarded by destructor sample-count check but direct callers should avoid empty data. `_test_name` is stored but not used in this implementation. The metric reflects percentile latency, not average despite the class comment.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.h

## Purpose
Declares a timing helper for benchmark tests that wraps a callable, records elapsed nanoseconds, and emits metrics at destruction.

## Important APIs, Types, And Functions
`execution_timer(const std::string &id, const std::string &test_name)`, destructor, `append_stats`, and templated `track(T lambda)` are the main API. Private fields are `_id`, `_test_name`, and `_time_recordings`.

## Control Flow
`track` captures `steady_clock::now()` before and after the callable, stores elapsed nanoseconds, and returns the callable's integer return code so test code can apply normal WiredTiger checks.

## State And Persistence Behavior
Samples live in a vector until stats are appended. Persistence occurs through the metrics writer in the `.cpp`.

## Dependencies And Integration Points
Includes chrono/string/vector and `test.h`. Used by `api_timing_benchmarks.cpp` and bounded cursor perf tests.

## Risks And Test Signals
The timer measures the lambda and any surrounding capture overhead. Tests should keep lambdas minimal and should be aware that destructor timing controls metric emission.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/execution_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.cpp

## Purpose
Implements setup and metric emission for Linux hardware instruction counting.

## Important APIs, Types, And Functions
Constructor initializes `perf_event_attr` for `PERF_TYPE_HARDWARE` and `PERF_COUNT_HW_INSTRUCTIONS`, excluding kernel and hypervisor counts. `append_stats` records `<id>_instructions`. Destructor always appends the last captured count.

## Control Flow
Actual counting happens in the header's templated `track`. The `.cpp` sets static perf configuration and sends the final value to `metrics_writer`.

## State And Persistence Behavior
Stores one instruction count in `_instruction_count`. Persists a metric through `metrics_writer`.

## Dependencies And Integration Points
Depends on Linux perf event headers through the header, `instruction_counter.h`, and `metrics_writer`. Used by `api_instruction_count_benchmarks.cpp`.

## Risks And Test Signals
The utility requires Linux perf permissions; `perf_event_open` failure asserts in `track`. Only the most recent tracked lambda is retained, so one counter object is intended for one measured operation in these tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.h

## Purpose
Declares a benchmark helper that measures hardware instruction counts for a callable using Linux `perf_event_open`.

## Important APIs, Types, And Functions
`instruction_counter` exposes constructor, destructor, `append_stats`, and templated `track(T lambda)`. Private state includes metric id/test name, last instruction count, and `perf_event_attr`.

## Control Flow
`track` opens a perf event for the calling thread, resets and enables it, invokes the lambda, disables the counter, reads the count, stores it, closes the fd, and returns the lambda return code.

## State And Persistence Behavior
No database state is changed by the counter itself. Metrics persist via `append_stats` in the `.cpp`.

## Dependencies And Integration Points
Includes Linux perf/syscall/ioctl/unistd headers and `test.h` for test utilities. Used by instruction-count benchmark tests around low-level WiredTiger API calls.

## Risks And Test Signals
The helper is Linux-specific and permission-sensitive. It asserts `fd != -1` and exact read size. It does not aggregate multiple samples; later `track` calls overwrite `_instruction_count`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/instruction_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.cpp

## Purpose
Implements two minimal command-line helpers for detecting an option and reading the following argument as its value.

## Important APIs, Types, And Functions
`option_exists(const std::string &opt, int argc, char *argv[])` and `value_for_opt(const std::string &opt, int argc, char *argv[])`.

## Control Flow
Both functions loop over `argv`, convert each argument to `std::string`, and use substring `find(opt)`. `option_exists` returns true on first match. `value_for_opt` returns the next argv element for the first match, or empty string if the match is last or absent.

## State And Persistence Behavior
No state is stored and no persistence occurs.

## Dependencies And Integration Points
Depends only on `options_parser.h`. Intended for cppsuite test runners or utilities that parse simple flags.

## Risks And Test Signals
Substring matching can produce false positives, for example `--home` matching `--homepage`. Values are positional and cannot distinguish `--opt=value` formats. Empty string can mean absent option or present-without-value.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.h -->
# sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.h

## Purpose
Declares minimal command-line option parsing helpers.

## Important APIs, Types, And Functions
`option_exists` checks for an option in `argv`; `value_for_opt` retrieves the following argument as a string.

## Control Flow
The header has no implementation flow; it exposes the parser utilities globally rather than inside `test_harness`.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Includes `<string>`. Used by command-line entry points that need simple option handling.

## Risks And Test Signals
Because functions are global, names may collide in larger binaries. Semantics are intentionally simple and should not be treated as a full option parser.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/src/util/options_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/api_instruction_count_benchmarks.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/api_instruction_count_benchmarks.cpp

## Purpose
Defines a cppsuite benchmark test that counts hardware instructions for selected WiredTiger cursor and session API calls under controlled low-noise conditions.

## Important APIs, Types, And Functions
`class api_instruction_count_benchmarks : public test` overrides `custom_operation`. It uses `instruction_counter` instances for transaction begin/commit/rollback, cursor insert/update/modify/remove/reset/search, open cursor cached/uncached, and `timestamp_transaction_uint`.

## Control Flow
The constructor initializes default operation tracking. `custom_operation` asserts one collection and in-memory mode, opens one cursor, extracts raw `WT_CURSOR *` and `WT_SESSION *`, then measures APIs one by one with carefully prepared cursor/transaction state. It avoids measuring implicit search work where possible by positioning the cursor before update/modify/remove, toggles cursor caching for open-cursor measurements, and closes explicitly opened raw cursors.

## State And Persistence Behavior
The test mutates one in-memory collection while measuring operations. It uses normal transaction calls for benchmark setup and cleanup. Metrics are recorded when instruction counter objects are destroyed at the end of `custom_operation`.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `test`, and `instruction_counter`. It relies on cppsuite population to create data before custom operation runs and on in-memory WiredTiger config to reduce I/O and background server noise.

## Risks And Test Signals
Requires Linux perf event availability and permissions. It assumes background noise is minimized by config. Because each counter stores one value, repeated measurements are not averaged. Correct signals are successful `testutil_check` calls and generated `<api>_instructions` metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/api_instruction_count_benchmarks.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/api_timing_benchmarks.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/api_timing_benchmarks.cpp

## Purpose
Defines a timing benchmark for frequently called WiredTiger session APIs.

## Important APIs, Types, And Functions
`class api_timing_benchmarks : public test` overrides `custom_operation` and uses `execution_timer` for begin transaction, commit transaction, rollback transaction, timestamp transaction uint, cursor reset, and cursor search. `_LOOP_COUNTER` is 1000.

## Control Flow
The constructor initializes operation tracking. The custom operation asserts one collection, opens a cursor, then times begin/commit with real inserts for `_LOOP_COUNTER / 10` iterations. It times rollback in a larger loop, then times many `timestamp_transaction_uint` calls inside one transaction and rolls it back.

## State And Persistence Behavior
The benchmark inserts additional keys during commit timing and uses the operation tracker through `thread_worker::insert`. Timings are persisted as 90th percentile metrics by `execution_timer` destructors.

## Dependencies And Integration Points
Depends on `execution_timer`, `instruction_counter` include presence, constants/logger, and the base `test` harness. It relies on pre-populated collection state and timestamp manager availability.

## Risks And Test Signals
The file creates timers for cursor reset/search but does not use them in the shown implementation, so no cursor timing metric is emitted unless future code adds samples. Timing includes lambda overhead and any transaction side effects. Successful signals are completed loops and perf stats from populated timers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/api_timing_benchmarks.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/background_compact.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/background_compact.cpp

## Purpose
Defines a workload that encourages and validates WiredTiger background compaction by alternating insert/truncate activity with maintenance windows and compact enable/disable cycles.

## Important APIs, Types, And Functions
`class background_compact : public test` overrides `custom_operation`, `remove_operation`, `insert_operation`, `background_compact_operation`, and `validate`. It uses a volatile `maintenance_window` flag, metrics monitor statistics, random cursors, truncate ranges, and compact configuration strings.

## Control Flow
The custom operation toggles the maintenance window after sleeping. Remove operation pauses during maintenance, samples collection statistics, skips truncation if reusable space already exceeds a threshold, otherwise repeatedly chooses random keys and truncates small ranges until roughly 20 percent of entries are removed or retries are exhausted, then checkpoints. Insert operation mirrors default insertion but also pauses during maintenance. Background compact operation toggles `session->compact` between `background=true` with a free-space target and `background=false`.

## State And Persistence Behavior
The test mutates collections through inserts and truncates, forces checkpoints, and changes background compact server state. It uses operation tracking for mutations but supplies custom validation focused on compaction statistics rather than full data replay.

## Dependencies And Integration Points
Depends on constants/logger/random generator, base test, validator include, `metrics_monitor`, `connection_manager`, and WiredTiger statistics. It integrates with configured background compact debug mode and free-space target.

## Risks And Test Signals
`maintenance_window` is volatile rather than atomic, so it is a lightweight coordination flag but not a strong synchronization primitive. Validation asserts multiple background compact statistics are greater than zero: bytes recovered, EMA, compact writes, files tracked, skipped, and success. Workload effectiveness depends on file statistics, checkpoint timing, and enough runtime for compact to act.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/background_compact.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_perf.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_perf.cpp

## Purpose
Benchmarks normal versus bounded cursor traversal and bound-setting cost.

## Important APIs, Types, And Functions
`class bounded_cursor_perf : public test` overrides `read_operation`. Static helpers `set_bound_key_lower` and `set_bound_key_upper` apply lower and upper bounds while timing `WT_CURSOR::bound`.

## Control Flow
The read operation asserts a single read thread, compiles bound configuration strings with `WT_CONNECTION::compile_configuration`, creates timers, opens normal next/prev cursors and bounded next/prev cursors, alternates compiled and non-compiled bound application, then advances all cursors. When any cursor reaches `WT_NOTFOUND`, it asserts all reached the end together, resets cursors, and reapplies bounds.

## State And Persistence Behavior
The test is read-only after default population. It records traversal and bound-setting timing metrics through `execution_timer`.

## Dependencies And Integration Points
Depends on `execution_timer`, base test, `connection_manager`, and WiredTiger compiled configuration API. It assumes contiguous populated keys and one collection.

## Risks And Test Signals
The synthetic bounds are outside the key range to keep bounded traversal semantically identical to unbounded traversal. Misconfigured multiple read threads assert. Successful signals are matching end-of-range returns and emitted timing metrics for bounded/default traversal and compiled/non-compiled bound setup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_perf.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_indices.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_indices.cpp

## Purpose
Tests prefix-bounded `search_near` behavior in a unique-index-like insertion pattern and verifies duplicate-prefix insertion attempts fail without changing table cardinality.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_indices : public test` overrides `populate`, `insert_operation`, and `read_operation`. Static helpers include `perform_unique_index_insertions`, `populate_worker`, and `get_prefix_from_key`. State includes `prefixes_map`.

## Control Flow
Population creates collections, starts one populate worker per collection, and each worker inserts random prefixes using a sequence that inserts a prefix, removes it, applies prefix bounds, verifies `search_near` does not find an existing prefix, and inserts `prefix,id`. After population, it scans each collection into `prefixes_map`. Runtime insert threads pick existing prefixes and assert that the same unique-index insertion procedure fails. Read threads count records across all collections and assert total size remains equal to the populated prefix map size.

## State And Persistence Behavior
The test persists unique-index-shaped keys and tracks operations through the standard tracker. Runtime insert attempts intentionally roll back after verifying duplicate-prefix rejection. `prefixes_map` is in-memory state used for duplicate selection and cardinality validation.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, `thread_manager`, `connection_manager`, and the base test harness. It validates the bounded cursor prefix path against unique index semantics.

## Risks And Test Signals
Population retries rollbacks up to `MAX_ROLLBACKS`. `get_prefix_from_key` returns empty when no comma exists, so it assumes populated keys use the `prefix,id` shape. Read validation assumes each collection receives the same number of prefixes. Success is stable record count and failed duplicate-prefix insertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_indices.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_search_near.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_search_near.cpp

## Purpose
Validates that prefix-bounded `search_near` returns keys consistent with unbounded `search_near` under concurrent random inserts.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_search_near : public test` overrides `populate`, `insert_operation`, and `read_operation`. Private validation helpers are `validate_prefix_search_near`, `validate_successful_calls`, and `validate_unsuccessful_prefix_call`.

## Control Flow
Population only creates empty collections. Insert threads distribute collections across workers and insert random alphabetic keys with random values in timestamped transactions. Read threads choose random collections, begin a rounded read transaction at a valid read timestamp when available, generate random prefixes, apply `bound_set(prefix)`, call bounded `search_near`, then open a default cursor and validate bounded results against unbounded search-near behavior.

## State And Persistence Behavior
Writers persist random keys and operation tracker rows. Readers use read timestamps and rollback read transactions after their target operation count. Bounds are applied per cached cursor and reset after use.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, `timestamp_manager`, and base test. It exercises WiredTiger cursor bounds, search-near exact values, and timestamp visibility.

## Risks And Test Signals
Concurrent inserts can make visibility dependent on read timestamp; the test mitigates timestamp invalidation with `roundup_timestamps=(read=true)` and skips `read_timestamp=0`. Validation has detailed branches for bounded success, bounded not found, exact values, and neighboring keys. Success is absence of assertion failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_search_near.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_stat.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_stat.cpp

## Purpose
Verifies that prefix-bounded `search_near` limits tree traversal by checking WiredTiger cursor statistics after controlled invisible-data searches.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_stat : public test` overrides `populate` and `read_operation`. Static helpers are `populate_worker` and `perform_search_near`. State includes `keys_per_prefix`, `srchkey_len`, alphabet constants, prefix length, and minimum expected entries.

## Control Flow
Population creates collections, starts 26 workers, and each worker inserts keys for one first-letter prefix across all two-letter suffixes, committing at timestamp 100. It then force-evicts pages via `debug=(release_evict=true)` and chooses a random search prefix length. Read operation asserts a single read thread, opens a connection statistics cursor, spawns configured `search_near_threads`, and each search worker performs a bounded search at read timestamp 10 where no populated keys are visible. After joining, it compares statistic deltas against expected skipped-entry upper bounds and early-exit counts.

## State And Persistence Behavior
Populated data is committed at timestamp 100 so read timestamp 10 sees none of it. The test uses statistics as its primary validation state and does not rely on value-level validation. Worker objects are allocated per spawned search thread and deleted after join.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, base test, metrics monitor stats, timestamp manager, and `thread_manager`.

## Risks And Test Signals
The `z`, `zz`, `zzz` edge case is tracked because those prefixes can run to the end of the keyspace without early exit. Expected-entry math depends on `keys_per_prefix`, alphabet size, and prefix length. Success requires bounded early-exit stats to increase by thread count minus z-key searches and skipped entries to stay under the calculated upper limit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_stat.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_stress.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_stress.cpp

## Purpose
Defines a comprehensive concurrent stress test for WiredTiger cursor bounds, covering bounded `search`, `search_near`, `next`, and `prev` while inserts, updates, removes, timestamps, and optional reverse collation are active.

## Important APIs, Types, And Functions
`class bounded_cursor_stress : public test` overrides `insert_operation`, `update_operation`, `read_operation`, and `custom_operation`. Key helpers include `custom_lexicographical_compare`, `set_random_bounds`, `validate_bound_search`, `validate_bound_search_near`, `validate_successful_search_near_inside_range`, `validate_successful_search_near_outside_range`, `validate_search_near_not_found`, `cursor_traversal`, and `cursor_traversal_walk`.

## Control Flow
`set_random_bounds` randomly clears bounds, sets lower, upper, or both, ensuring non-overlap when both are set and respecting reverse collator order. Insert threads add random keys. Update threads use random cursors to pick existing keys and update values. Read threads set random bounds, begin rounded timestamped read transactions, run bounded `search_near`, validate with a normal cursor, then validate bounded `search` on the returned key. Custom threads traverse forward and backward through bounded ranges and compare each key with a normal cursor positioned at the relevant bound.

## State And Persistence Behavior
The test persists random inserts and updates through standard worker CRUD and operation tracking. Read/custom validation uses read transactions with valid read timestamps where available. Cursor bounds are transient per cursor and reset or cleared as needed.

## Dependencies And Integration Points
Depends on `bound`, `bound_set`, constants, random generator, base test, timestamp manager, and operation tracker. It integrates reverse-collator configuration into comparison logic.

## Risks And Test Signals
The test has many assertion-heavy validation paths and tolerates `WT_ROLLBACK` in concurrent read/traversal branches. Reverse collator order changes bound comparisons, so `_reverse_collator_enabled` is captured at construction. Potential failure signals include returned keys outside bounds, normal/bounded cursor mismatch, traversal missing keys, or rollback retry exhaustion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_stress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/burst_inserts.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/burst_inserts.cpp

## Purpose
Implements a workload that simulates bursty bulk insertion with simultaneous random reads to create cache pressure.

## Important APIs, Types, And Functions
`class burst_inserts : public test` overrides `insert_operation`. It reads `_burst_duration` from configuration and uses a local `collection_cursor` struct containing collection reference, write cursor, and random read cursor.

## Control Flow
Each insert worker opens one write cursor and one `next_random=true` read cursor per assigned collection. For each collection, it inserts continuously for `_burst_duration` seconds without per-operation throttling, periodically commits when `can_commit` is true, walks the random reader to generate cache activity, then sleeps for the configured operation rate before moving to the next collection.

## State And Persistence Behavior
The workload persists many new keys, updates the in-memory collection key count after successful commits, and records operation-tracker entries through `thread_worker::insert`. Random reads do not persist data but can affect cache behavior.

## Dependencies And Integration Points
Depends on `random_generator` and base test. It uses the standard population, transaction, timestamp, and tracking machinery from `thread_worker`.

## Risks And Test Signals
The local struct's member order differs from its constructor parameter order, which is easy to misread, but initialization still places the normal cursor in `write_cursor` and the `next_random=true` cursor in `read_cursor`. Operational risks include `added_count` reset on rollback, large unthrottled bursts, and intentionally high cache pressure. Success is sustained commits and no unhandled cursor errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/burst_inserts.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/cache_resize.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/cache_resize.cpp

## Purpose
Tests behavior while the WiredTiger connection cache size alternates between very small and large values, and records enough tracker state for custom validation of accepted transactions.

## Important APIs, Types, And Functions
`operation_tracker_cache_resize` overrides `set_tracking_cursor` to write timestamp, transaction id, operation type, and cache size. `class cache_resize : public test` overrides `custom_operation`, `insert_operation`, and `validate`.

## Control Flow
The custom operation alternates `WT_CONNECTION::reconfigure` between `cache_size=1MB` and `cache_size=500MB`, reads the internal `conn_impl->cache_size`, and records a custom operation with the new cache size. Insert operation writes random keys into the last collection with the current cache size as the value, relying on transaction acceptance/rejection under cache pressure. Validation scans the operation tracking table, accepts only `CUSTOM` and `INSERT` operation types, skips cache-change rows, groups inserts by transaction id, and currently asserts only that at least one insert record exists.

## State And Persistence Behavior
The test mutates connection cache configuration and persists insert rows. The custom tracker uses internal WiredTiger session/connection structs to capture transaction id and cache size atomically with tracked operations. Several intended cache-size assertions are disabled by `FIXME-WT-12931`.

## Dependencies And Integration Points
Depends on constants/logger/random generator, `operation_tracker`, base test, `connection_manager`, and WiredTiger internal implementation structs `WT_SESSION_IMPL` and `WT_CONNECTION_IMPL`.

## Risks And Test Signals
This test reaches into internal WiredTiger structs, making it sensitive to implementation changes. Validation currently has weakened checks due to WT-12931, so its main signal is that tracked insert records exist and tracking format is parseable. Saving cache reconfiguration rows can itself roll back under pressure and is logged as a warning.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/cache_resize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/csuite_style_example_test.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/csuite_style_example_test.cpp

## Purpose
Provides a standalone example of writing a C++ test using cppsuite utilities without the full `test` framework lifecycle.

## Important APIs, Types, And Functions
Global flags `do_inserts` and `do_reads` drive thread loops. Static `insert_op` and `read_op` use raw `WT_CURSOR *`. `main` demonstrates logging, connection creation, session/cursor management, simple CRUD checks, thread manager use, and cleanup.

## Control Flow
`main` sets program name and log level, removes the test home, creates a connection, opens insert/read sessions and cursors, creates a table, inserts and searches sample keys, starts insert and read threads for five seconds, stops them by flipping globals, joins, closes cursors, and exits.

## State And Persistence Behavior
Creates a WiredTiger home and table, inserts random data concurrently, and searches random keys. It uses raw WiredTiger resources rather than RAII wrappers for sessions/cursors, except for the singleton connection manager.

## Dependencies And Integration Points
Depends on constants/logger/random generator/thread manager/connection manager and WiredTiger/test utility C headers. It is more of a template/demo than a framework-managed workload.

## Risks And Test Signals
Global bool flags are unsynchronized and suitable only for a simple example. Insert and read loops share raw cursors with their owning sessions and depend on the main thread closing after join. Duplicate random keys may cause insert errors depending on table overwrite behavior. Test signals are the initial expected search results and lack of runtime API failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/csuite_style_example_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/hs_cleanup.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/hs_cleanup.cpp

## Purpose
Defines a workload intended to age out full pages and drive history store cleanup by repeatedly updating ranges of existing keys at advancing timestamps.

## Important APIs, Types, And Functions
`class hs_cleanup : public test` overrides `update_operation`.

## Control Flow
Each update thread asserts the number of collections equals the number of threads, selects the collection matching its thread id, opens one cursor, then loops while running. It sleeps, begins a transaction if needed, advances the cursor, resets at `WT_NOTFOUND`, rolls back on `WT_ROLLBACK`, copies the current key, updates it with a random pseudo-random value, and commits when `can_commit` is true.

## State And Persistence Behavior
The test persists repeated value updates over existing keys and records them through the operation tracker. Advancing timestamps from `thread_worker::update` should create obsolete historical versions that history store cleanup can remove when globally visible.

## Dependencies And Integration Points
Depends on logger/random generator and the base test. Validation and statistic monitoring are expected to be provided by the framework configuration, especially metrics monitor stats referenced in the file comment.

## Risks And Test Signals
The comment notes key range uncertainty, so the workload walks sequentially rather than targeting precise ranges. It asserts fewer than 100 rollback retries. The retrieved key pointer is passed to update; the comment says it should be copied for buffer validity, but the code passes `key_tmp` directly to a `std::string` parameter, which copies at call construction. Success is sustained updates and expected history-store cleanup statistics externally.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/hs_cleanup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/operations_test.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/operations_test.cpp

## Purpose
Defines the baseline cppsuite operations test that uses all default `database_operation` behavior without overriding workload methods.

## Important APIs, Types, And Functions
`class operations_test : public test` has a constructor that calls `init_operation_tracker()`.

## Control Flow
All control flow is inherited from `test::run`, workload manager, and `database_operation`. Configuration determines which operation threads run, while default populate/insert/read/remove/update/checkpoint/custom/background compact/validation logic applies.

## State And Persistence Behavior
Uses the standard database model, operation tracker, timestamp manager, and validation behavior. Persistent effects depend entirely on the selected configuration file, such as insert-heavy or stress configurations.

## Dependencies And Integration Points
Includes `test.h` and uses the `test_harness` namespace. It is the simplest concrete class used by the test runner for standard stress workloads.

## Risks And Test Signals
Because no hooks are overridden, any special tracking schema or workload-specific validation is unavailable. It is useful as a broad signal for the base framework: successful population, configured operations, default validation, metrics output, and final success log.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/operations_test.cpp -->
