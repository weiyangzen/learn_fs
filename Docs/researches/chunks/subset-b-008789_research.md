# sources/storage-engines/sqlite/src/sqlite.h.in lines 5233-10716

## Scope and Purpose

This chunk is the middle public C API reference section of SQLite's generated-header template. It declares and documents runtime interfaces for prepared statement execution, result and function value handling, application-defined SQL functions, collations, extension loading, virtual tables, incremental BLOB I/O, VFS registration, mutexes, runtime status counters, custom page-cache hooks, online backup, unlock notification, WAL hooks/checkpointing, and the beginning of prepared-statement scan-status support.

The file is a header input (`sqlite.h.in`), so the code here is mostly declarations, macros, typedefs, and API contracts rather than implementation bodies. Its implementation dependencies are the SQLite core objects declared elsewhere in the header (`sqlite3`, `sqlite3_stmt`, `sqlite3_context`, `sqlite3_value`, `sqlite3_vfs`, `sqlite3_mutex`, `sqlite3_file`, result codes, config opcodes, limits, and VFS/file-control opcodes). This chunk starts immediately after `sqlite3_column_decltype()` declarations and ends in the opening prose for `sqlite3_stmt_scanstatus()`, so scan-status function prototypes and remaining details continue in the next chunk.

## Major API Areas

### Prepared Statement Execution and Results

- `sqlite3_step(sqlite3_stmt*)` drives a prepared statement VM. Its return protocol distinguishes row production (`SQLITE_ROW`), completion (`SQLITE_DONE`), lock contention (`SQLITE_BUSY`), misuse, and richer `v2`/`v3` prepare-time errors. Legacy prepare APIs collapse many errors to `SQLITE_ERROR` until `sqlite3_reset()` or `sqlite3_finalize()`.
- `sqlite3_data_count(sqlite3_stmt*)` reports the number of columns in the current `SQLITE_ROW`, returning 0 for NULL statements, no current row, `SQLITE_DONE`, and special pragmas such as incremental vacuum.
- Datatype macros define the public dynamic type tags: `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL`.
- Column accessors (`sqlite3_column_blob`, `_double`, `_int`, `_int64`, `_text`, `_text16`, `_value`, `_bytes`, `_bytes16`, `_type`) expose the current row. Their core control-flow precondition is strict: the latest statement operation must have produced `SQLITE_ROW`, with no intervening reset/finalize, and no concurrent step/reset/finalize from another thread.
- `sqlite3_finalize()` is the required destructor for every prepared statement. It can be called at any point in statement lifetime and returns the most recent evaluation error if one occurred.
- `sqlite3_reset()` rewinds a prepared statement for re-execution without clearing bindings. Its return value reports the status of the prior evaluation, including late errors such as commit/locking failure after a statement that returned rows.

Important state behavior: column text/BLOB pointers are owned by SQLite and are valid only until type conversion, `sqlite3_step()`, `sqlite3_reset()`, or `sqlite3_finalize()`. Calls that force conversion between UTF-8/UTF-16/text/BLOB can invalidate earlier pointers. OOM during conversion can look like SQL NULL, so callers must consult `sqlite3_errcode()` immediately before making another SQLite call.

### Application-Defined SQL Functions and Values

- `sqlite3_create_function`, `sqlite3_create_function16`, `sqlite3_create_function_v2`, and `sqlite3_create_window_function` register scalar, aggregate, and window functions on a single database connection. They bind function name, arity, preferred text encoding, flags, user data, callbacks, and optional destructor.
- Text encoding constants (`SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, deprecated `SQLITE_ANY`, `SQLITE_UTF16_ALIGNED`, `SQLITE_UTF8_ZT`) are reused by function, collation, result, and bind APIs.
- Function flags (`SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_SUBTYPE`, `SQLITE_INNOCUOUS`, `SQLITE_RESULT_SUBTYPE`, `SQLITE_SELFORDER1`) feed planner optimization and schema-security policy. `DIRECTONLY` and `INNOCUOUS` are explicitly security-relevant for trusted-schema and injection-resistance scenarios.
- Deprecated APIs guarded by `SQLITE_OMIT_DEPRECATED` include `sqlite3_aggregate_count`, `sqlite3_expired`, `sqlite3_transfer_bindings`, `sqlite3_global_recover`, `sqlite3_thread_cleanup`, and `sqlite3_memory_alarm`.
- Value readers (`sqlite3_value_blob`, `_double`, `_int`, `_int64`, `_pointer`, `_text`, `_text16*`, `_bytes*`, `_type`, `_numeric_type`, `_nochange`, `_frombind`) expose `sqlite3_value` objects inside SQL function and virtual-table callbacks. They share pointer invalidation and same-thread requirements with column accessors.
- `sqlite3_value_encoding`, `sqlite3_value_subtype`, `sqlite3_value_dup`, and `sqlite3_value_free` expose internal text encoding, subtype metadata, and managed copies of values.
- Function-context APIs include `sqlite3_aggregate_context`, `sqlite3_user_data`, `sqlite3_context_db_handle`, `sqlite3_get_auxdata`, `sqlite3_set_auxdata`, `sqlite3_get_clientdata`, and `sqlite3_set_clientdata`.
- Result setters (`sqlite3_result_blob*`, `_double`, `_error*`, `_error_toobig`, `_error_nomem`, `_error_code`, `_int*`, `_null`, `_text*`, `_value`, `_pointer`, `_zeroblob*`) construct SQL function results and errors. `sqlite3_result_subtype()` attaches limited subtype metadata to a result.

State and lifecycle details are central here. Aggregate context memory is allocated once per aggregate instance, zeroed, reused for later xStep/xFinal calls, and freed when the aggregate query concludes. Auxdata and clientdata have destructor rules that may run on overwrite, reset/finalize, connection close, OOM, or even immediately during `sqlite3_set_auxdata()` when planning-time evaluation or allocation failure occurs. Result and pointer APIs use SQLite-owned copies or caller-provided destructors via `SQLITE_STATIC` and `SQLITE_TRANSIENT`.

### Collation, Sleep, Directories, Connection Metadata, and Hooks

- Collation APIs (`sqlite3_create_collation`, `_v2`, `_collation16`, `sqlite3_collation_needed`, `_needed16`) register comparison callbacks per connection and encoding. Comparison callbacks must define a stable total ordering; violating equality/transitivity/ordering constraints yields undefined SQLite behavior.
- `sqlite3_sleep()` delegates to the default VFS `xSleep`, with negative arguments normalized to zero in SQLite 3.42.0 and later.
- Global directory variables `sqlite3_temp_directory` and `sqlite3_data_directory` are legacy process-global knobs. They are unsafe to mutate concurrently, should be set during initialization, may be modified/freed by their PRAGMA counterparts, and are especially dangerous while connections are open (`sqlite3_data_directory` can contribute to corruption).
- Win32-specific helpers (`sqlite3_win32_set_directory`, `_directory8`, `_directory16`) and `SQLITE_WIN32_DATA_DIRECTORY_TYPE`/`SQLITE_WIN32_TEMP_DIRECTORY_TYPE` configure Windows directory state when enabled.
- Connection/statement introspection APIs include `sqlite3_get_autocommit`, `sqlite3_db_handle`, `sqlite3_db_name`, `sqlite3_db_filename`, `sqlite3_db_readonly`, `sqlite3_txn_state`, `SQLITE_TXN_NONE/READ/WRITE`, and `sqlite3_next_stmt`.
- Commit, rollback, autovacuum, and update hooks (`sqlite3_commit_hook`, `sqlite3_rollback_hook`, `sqlite3_autovacuum_pages`, `sqlite3_update_hook`) register callback behavior on a connection. The update hook excludes internal tables, WITHOUT ROWID tables, some REPLACE deletes, and truncate optimization deletes.

The hook APIs are integration points for host applications and extensions, but several callbacks are explicitly not reentrant or must not modify the invoking connection. `sqlite3_autovacuum_pages()` is particularly restrictive: its callback must not call other SQLite APIs because doing so can crash or corrupt database files.

### Memory, Metadata, Extension Loading, and Shared Cache

- `sqlite3_enable_shared_cache()` toggles process-wide shared-cache behavior for future connections, but shared cache use is discouraged and may be omitted by compile options.
- Memory APIs include `sqlite3_release_memory`, `sqlite3_db_release_memory`, `sqlite3_soft_heap_limit64`, `sqlite3_hard_heap_limit64`, and deprecated `sqlite3_soft_heap_limit`. Soft limits are advisory; hard limits fail allocations. Enforcement depends on memory accounting, page-cache configuration, and compile-time options.
- `sqlite3_table_column_metadata()` reads schema metadata for a table column, including type, collation, NOT NULL, primary-key, and autoincrement attributes. It can force schema loading/parsing and returns view/column/table existence errors.
- Extension loading APIs include `sqlite3_load_extension`, `sqlite3_enable_load_extension`, `sqlite3_auto_extension`, `sqlite3_cancel_auto_extension`, and `sqlite3_reset_auto_extension`.

Security risks are strong in this area. Extension loading is off by default; the C API recommends enabling only the C loading interface via `SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION` rather than `sqlite3_enable_load_extension()`, because the latter also enables the SQL `load_extension()` function and can turn SQL injection into arbitrary native-code loading. Automatic extensions run for every newly opened connection and can cause `sqlite3_open*()` to fail if an entry point returns an error.

### Virtual Table Core Interfaces

- Opaque typedefs introduce `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`.
- `struct sqlite3_module` defines the virtual table module callback surface: create/connect, best-index planning, disconnect/destroy, cursor open/close/filter/next/eof/column/rowid, update, transaction hooks, function overloading, rename, savepoint/release/rollback-to, shadow-table naming, and integrity checking.
- `struct sqlite3_index_info` is the xBestIndex planner contract. Inputs describe constraints, ORDER BY terms, and used columns; outputs describe argv mapping, omitted constraints, chosen index number/string, ordering, estimated cost/rows, and scan flags.
- Scan and constraint macros include `SQLITE_INDEX_SCAN_UNIQUE`, `SQLITE_INDEX_SCAN_HEX`, and operator codes for equality/range/match/LIKE/GLOB/REGEXP/IS/ISNULL/ISNOTNULL/LIMIT/OFFSET/function constraints.
- Module registration APIs (`sqlite3_create_module`, `_v2`, `sqlite3_drop_modules`) attach module implementations to a connection and define destructor behavior for module client data.
- `sqlite3_vtab` and `sqlite3_vtab_cursor` are documented as superclasses for implementation-specific instances. Virtual table methods set `zErrMsg` with `sqlite3_mprintf()` and must free previous messages.
- `sqlite3_declare_vtab` declares the virtual table schema, and `sqlite3_overload_function` allows a virtual table to overload SQL functions.

Planner correctness risk is high. If xBestIndex sets `omit`, `orderByConsumed`, `estimatedRows`, `idxFlags`, or constraint argv mappings incorrectly, SQLite may generate inefficient plans or return incorrect results. The `estimatedRows`, `idxFlags`, and `colUsed` fields are version-gated by SQLite version; old runtimes cannot safely access fields added after their ABI version.

### Incremental BLOB, VFS, Mutex, File-Control, and Test-Control APIs

- `sqlite3_blob` is the handle for incremental BLOB I/O. `sqlite3_blob_open` opens a row/column blob, `sqlite3_blob_reopen` retargets to another row, `sqlite3_blob_close` releases it, `sqlite3_blob_bytes` reports size, and `sqlite3_blob_read`/`sqlite3_blob_write` move bytes.
- BLOB handles expire when the target row is updated, deleted, or affected by conflict side effects. Reads/writes on expired handles return `SQLITE_ABORT`; writes cannot resize a BLOB and require a write-opened handle.
- VFS registration APIs (`sqlite3_vfs_find`, `sqlite3_vfs_register`, `sqlite3_vfs_unregister`) manage process-level VFS instances and the default VFS.
- Mutex APIs (`sqlite3_mutex_alloc`, `_free`, `_enter`, `_try`, `_leave`) expose SQLite's synchronization layer. `sqlite3_mutex_methods` lets applications install custom mutex implementations through `sqlite3_config()`. Debug verification APIs `sqlite3_mutex_held` and `sqlite3_mutex_notheld` are available under `!NDEBUG`.
- Mutex type macros define dynamic (`SQLITE_MUTEX_FAST`, `SQLITE_MUTEX_RECURSIVE`) and static internal/application/VFS mutex IDs.
- `sqlite3_db_mutex()` returns the connection mutex in serialized mode.
- `sqlite3_file_control()` passes low-level opcodes and payloads through to a database file's VFS `xFileControl`.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` opcodes expose unstable internal testing/fault-injection hooks.
- SQL keyword helpers (`sqlite3_keyword_count`, `sqlite3_keyword_name`, `sqlite3_keyword_check`) expose parser keyword knowledge, which depends on compile-time options.

Risk signals here are mostly misuse and portability. Passing stale or foreign handles to BLOB, mutex, file-control, or test-control routines is undefined. `sqlite3_test_control()` is expressly not application-stable. VFS names must be unique and non-empty; conflicting registrations are undefined. Static mutexes are for SQLite internals and can change across releases.

### Dynamic Strings and Runtime Status

- `sqlite3_str` is an incremental string builder created with `sqlite3_str_new`, appended via `sqlite3_str_appendf`, `_vappendf`, `_append`, `_appendall`, `_appendchar`, reset/truncated, and finalized with `sqlite3_str_finish` or freed with `sqlite3_str_free`.
- `sqlite3_str_errcode`, `_length`, and `_value` report builder status. OOM and too-big conditions are sticky in the object; pointers returned by `_value` are invalidated by later string operations.
- Runtime status APIs `sqlite3_status`/`sqlite3_status64`, database status APIs `sqlite3_db_status`/`sqlite3_db_status64`, and statement status API `sqlite3_stmt_status` expose current/highwater counters with optional resets.
- Status macros cover heap memory use/counts, page-cache use/overflow/size, parser stack, lookaside usage/misses, pager cache use/hit/miss/write/spill, deferred foreign keys, temp-buffer spill, and statement-level counters such as full-scan steps, sorts, automatic indexes, VM steps, reprepare count, run count, bloom-filter hits/misses, and statement memory use.

Test signals for this area include checking that counters reset when requested, 64-bit APIs preserve large values, unsupported status verbs return non-OK, and highwater-only/current-only counters match documented behavior.

### Page Cache, Online Backup, Unlock Notify, Strings, and WAL

- `sqlite3_pcache` and `sqlite3_pcache_page` are opaque page-cache structures. `sqlite3_pcache_page` exposes page content (`pBuf`) and extra metadata storage (`pExtra`).
- `sqlite3_pcache_methods2` defines application-provided page-cache callbacks for init/shutdown/create/cache-size/page-count/fetch/unpin/rekey/truncate/destroy/shrink. The older `sqlite3_pcache_methods` is retained only for compatibility and is not used by current SQLite.
- `sqlite3_backup` and backup APIs (`sqlite3_backup_init`, `_step`, `_finish`, `_remaining`, `_pagecount`) implement online copying between source and destination databases.
- `sqlite3_unlock_notify()` coordinates shared-cache `SQLITE_LOCKED` failures by registering non-reentrant callbacks, detecting direct and indirect deadlocks, and documenting the DROP TABLE/INDEX same-connection exception.
- String utility APIs (`sqlite3_stricmp`, `_strnicmp`, `_strglob`, `_strlike`) provide SQLite-compatible case folding and pattern behavior. Match routines return zero on match.
- `sqlite3_log()` writes to the configured SQLite error log without dynamic allocation.
- WAL APIs include `sqlite3_wal_hook`, `sqlite3_wal_autocheckpoint`, `sqlite3_wal_checkpoint`, `sqlite3_wal_checkpoint_v2`, and checkpoint mode macros `SQLITE_CHECKPOINT_NOOP`, `PASSIVE`, `FULL`, `RESTART`, and `TRUNCATE`.

State and persistence behavior are especially explicit for backups and WAL. Backups hold a write transaction on the destination for the operation, read-lock the source only during step calls, can be retried for `BUSY`/`LOCKED`, and may restart if the source changes externally. The destination connection must not be used by other APIs until `sqlite3_backup_finish()`. WAL hooks run after commit and can read/write/checkpoint, but overriding auto-checkpoint hooks can allow WAL files to grow without periodic checkpoints. Checkpoint modes vary in locking, busy-handler use, reader/writer blocking, and whether the WAL is reset or truncated.

### Virtual Table Advanced Configuration and Scan Status Opening

- `sqlite3_vtab_config()` is callable only from xCreate/xConnect and accepts options such as `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- `sqlite3_vtab_on_conflict`, `sqlite3_vtab_nochange`, `sqlite3_vtab_collation`, `sqlite3_vtab_distinct`, `sqlite3_vtab_in`, `sqlite3_vtab_in_first`, `sqlite3_vtab_in_next`, and `sqlite3_vtab_rhs_value` support virtual table update policy, xColumn no-change optimization, collation discovery, DISTINCT/GROUP BY/order planning, all-at-once IN handling, and literal RHS constraint access.
- Conflict macros `SQLITE_ROLLBACK`, `SQLITE_FAIL`, and `SQLITE_REPLACE` supplement existing `SQLITE_IGNORE` and `SQLITE_ABORT` constants.
- Scan-status opcodes begin here: `SQLITE_SCANSTAT_NLOOP`, `NVISIT`, `EST`, `NAME`, `EXPLAIN`, `SELECTID`, `PARENTID`, and `NCYCLE`. The chunk ends before the full `sqlite3_stmt_scanstatus()` declaration/details, which continue in the following chunk.

These advanced virtual-table APIs have narrow call-context requirements. Calling them outside xBestIndex, xFilter, xColumn, xUpdate, or xCreate/xConnect as documented is undefined and likely harmful. `sqlite3_vtab_distinct()` and `orderByConsumed` are correctness-sensitive: claiming ordering/distinctness guarantees that the virtual table cannot actually meet can produce wrong query answers.

## Dependencies and Integration Points

- Core database and VM handles: `sqlite3`, `sqlite3_stmt`, `sqlite3_context`, `sqlite3_value`, and `sqlite3_blob`.
- Error/result-code system: APIs rely heavily on `SQLITE_OK`, `SQLITE_ROW`, `SQLITE_DONE`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_MISUSE`, `SQLITE_NOMEM`, `SQLITE_READONLY`, `SQLITE_ABORT`, `SQLITE_ERROR`, `SQLITE_NOTFOUND`, and extended IO/locked codes.
- Memory API integration: destructors and ownership rules depend on `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_mprintf`, and `sqlite3_free`.
- VFS and pager integration: sleep, temp/data directories, file control, VFS registration, page cache methods, BLOB I/O, backup, WAL hooks/checkpoints, and shared cache all depend on lower-level VFS, pager, lock, and journaling subsystems.
- Planner integration: application functions, deterministic/innocuous/direct-only flags, virtual table xBestIndex output, RHS values, collation lookup, DISTINCT handling, IN handling, and statement/scan status all feed or observe the query planner and VDBE.
- Build-option integration: many APIs or semantics depend on compile options such as `SQLITE_OMIT_DEPRECATED`, `SQLITE_ENABLE_CEROD`, `SQLITE_ENABLE_UNLOCK_NOTIFY`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_ENABLE_ORDERED_SET_AGGREGATES`, `SQLITE_STRICT_SUBTYPE`, debug/NDEBUG settings, and platform VFS choices.

## Control Flow and Lifecycle Themes

- Prepared statement lifecycle: prepare (previous chunk), step repeatedly, read current-row columns only after `SQLITE_ROW`, reset for reuse while retaining bindings, finalize exactly once.
- SQL function lifecycle: register callbacks per connection, SQLite invokes callbacks during statement execution or sometimes planning, callbacks use `sqlite3_value` inputs and `sqlite3_result_*` outputs, destructors run on close/overwrite/failure according to API-specific rules.
- Virtual table lifecycle: register module, create/connect instance, planner calls xBestIndex, executor opens cursor and runs filter/next/eof/column/rowid, update and transaction callbacks participate in writes, disconnect/destroy releases instance state.
- BLOB lifecycle: open handle to a row/column, read/write within fixed byte length, optionally reopen to a different row, close handle; handle can expire due to row changes.
- Backup lifecycle: initialize, step pages in bounded increments, inspect remaining/pagecount after steps, finish to commit or roll back destination transaction and release resources.
- WAL lifecycle: commits may invoke WAL hook/autocheckpoint, manual checkpoints transfer frames from WAL to database with mode-dependent locks, periodic checkpointing is required to keep WAL size bounded.

## Risks and Edge Cases

- Undefined behavior is common for wrong call order, stale handles, cross-thread use, invalid pointers, out-of-range column indexes, and calling virtual-table helpers outside their documented callback.
- Pointer invalidation after text/blob/value conversion is a major API hazard; callers must copy data they need beyond the documented lifetime.
- Security-sensitive APIs include extension loading, application-defined SQL functions reachable from schema objects, clientdata exposure, direct access to global directory variables, and virtual tables marked innocuous/direct-only incorrectly.
- Reentrant callbacks can deadlock or corrupt state: autovacuum callbacks, unlock-notify callbacks, update hooks, and some function/virtual-table callbacks restrict which SQLite APIs may be called.
- Process-global knobs (`sqlite3_temp_directory`, `sqlite3_data_directory`, shared cache, VFS registration, auto extensions, heap limits) can affect unrelated connections and threads.
- Version and compile-option skew affect ABI fields, available APIs, keyword sets, status counters, unlock notify, ordered-set aggregates, strict subtype enforcement, memory management, and deprecated symbols.
- Backup and WAL APIs interact directly with filesystem locks; busy/locked responses are sometimes retryable and sometimes fatal depending on the exact operation and code.

## Test Signals

- Statement tests should cover legacy versus v2/v3 prepare error propagation, automatic reset behavior after terminal step results, reset returning late write errors, and column pointer invalidation after conversions.
- Function tests should exercise deterministic/direct-only/innocuous/subtype flags, destructor invocation on success/failure/overwrite/close, auxdata immediate destructor paths, aggregate context allocation from xFinal with no rows, and same-thread constraints.
- Extension-loading tests should verify disabled-by-default behavior, C-only enablement through db-config, SQL `load_extension()` isolation, auto-extension duplicate registration, cancellation, reset, and error propagation through `sqlite3_open*()`.
- Virtual table tests should validate xBestIndex argv mapping, omit semantics, `orderByConsumed`, estimated rows/flags under version gates, IN all-at-once iteration, RHS literal extraction, no-change optimization, and conflict-policy reporting.
- BLOB tests should include fixed-size writes, bounds errors, readonly handles, expiration after row update/delete, reopen behavior, and error-code propagation.
- VFS/mutex/page-cache tests should use custom implementations to verify init/shutdown, static versus dynamic mutex behavior, file-control forwarding, VFS default replacement, page fetch/unpin/rekey/truncate semantics, and shrink calls.
- Status tests should check current/highwater behavior, reset flags, large-value preservation in 64-bit APIs, unsupported op return codes, and statement counters across step/reset/finalize.
- Backup/WAL/unlock tests should cover retryable `BUSY`/`LOCKED`, fatal backup errors, destination-handle exclusivity, source modification restart, checkpoint mode locking differences, autocheckpoint hook replacement, and unlock-notify deadlock detection.

## Cross-Chunk Notes

- Lines before 5233 define earlier declaration context for column metadata and many base types/macros referenced here.
- Lines after 10716 continue the `sqlite3_stmt_scanstatus()` CAPI section, so this chunk only captures scan-status opcode definitions and the start of the API prose.
