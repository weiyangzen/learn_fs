# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 5284-10756

## Scope

This chunk covers a large section of the SQLite amalgamation's public C API declarations and their embedded reference documentation. It starts in the prepared-statement binding/column API area, continues through application-defined functions, collations, hooks, virtual tables, incremental BLOB I/O, VFS and mutex APIs, status/diagnostic APIs, custom page cache, online backup, unlock notification, string helpers, WAL checkpointing, and virtual-table query-planning helpers. The chunk ends mid-comment in the prepared-statement scan-status opcode documentation, so the `SQLITE_SCANSTAT_*` definitions and scan-status functions continue in the next chunk.

This range is declaration-heavy. It does not contain implementation bodies, allocation algorithms, pager logic, B-tree logic, or WiredTiger code. Its role in this repository is to expose the SQLite C ABI used by SQLite's own test build vendored under WiredTiger's third-party test dependency.

## Purpose

The purpose of this section is to define the callable interface and behavioral contract for major SQLite subsystems:

- Prepared statement execution, reset/finalize, bind lookup, result-column metadata, and typed column extraction.
- Application-defined scalar, aggregate, and window functions, including argument access, per-aggregate state, auxiliary data caching, client-data storage, result construction, and subtype propagation.
- Collation registration and collation-needed callbacks.
- Connection and statement state inspection, including autocommit, transaction state, attached database names/files, statement enumeration, and runtime/status counters.
- Commit, rollback, update, autovacuum, WAL, unlock-notify, and extension-loading hooks.
- Virtual table module registration, cursor/table/index ABI, incremental BLOB I/O, and virtual-table planner helper APIs.
- Pluggable VFS discovery/registration, mutex implementation contracts, custom page-cache implementation contracts, online backup, and WAL checkpointing.

The declarations are part of SQLite's public ABI. Downstream C/C++ code compiles against these prototypes and constants, while the actual behavior is implemented later in the amalgamation.

## Important APIs, Types, and Constants

### Prepared Statements and Result Columns

The chunk starts with statement parameter and column APIs:

- `sqlite3_bind_parameter_index()` maps a named host parameter to a 1-based bind index.
- `sqlite3_clear_bindings()` resets all bound host parameters on a statement to SQL NULL.
- `sqlite3_column_count()` and `sqlite3_data_count()` report result-column counts for prepared statements and the current row.
- `sqlite3_column_name()` and `sqlite3_column_name16()` return UTF-8/UTF-16 result-column labels.
- `sqlite3_column_database_name*()`, `sqlite3_column_table_name*()`, and `sqlite3_column_origin_name*()` expose origin metadata when built with `SQLITE_ENABLE_COLUMN_METADATA`.
- `sqlite3_column_decltype()` and `sqlite3_column_decltype16()` expose declared table-column type text for result columns that originate directly from table columns.
- `sqlite3_step()`, `sqlite3_reset()`, and `sqlite3_finalize()` define the normal prepared-statement lifecycle.
- `sqlite3_column_blob()`, `sqlite3_column_double()`, `sqlite3_column_int()`, `sqlite3_column_int64()`, `sqlite3_column_text()`, `sqlite3_column_text16()`, `sqlite3_column_value()`, `sqlite3_column_bytes()`, `sqlite3_column_bytes16()`, and `sqlite3_column_type()` read values from the current `SQLITE_ROW`.

The type constants `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL` define the five fundamental SQL runtime value classes. The comments emphasize pointer lifetime and type-conversion hazards: text/blob pointers may be invalidated by later conversion calls, and `sqlite3_column_type()` is only meaningful before conversions.

### SQL Functions, Values, and Results

Application-defined functions are declared through:

- `sqlite3_create_function()`, `sqlite3_create_function16()`, `sqlite3_create_function_v2()`, and `sqlite3_create_window_function()`.
- Encoding constants `SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, `SQLITE_ANY`, and `SQLITE_UTF16_ALIGNED`.
- Function flags `SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_INNOCUOUS`, `SQLITE_SUBTYPE`, `SQLITE_RESULT_SUBTYPE`, and `SQLITE_SELFORDER1`.

Function argument/value APIs include `sqlite3_value_blob()`, numeric/text extractors, `sqlite3_value_pointer()`, byte-count accessors, `sqlite3_value_type()`, `sqlite3_value_numeric_type()`, `sqlite3_value_nochange()`, `sqlite3_value_frombind()`, `sqlite3_value_encoding()`, `sqlite3_value_subtype()`, `sqlite3_value_dup()`, and `sqlite3_value_free()`. These APIs operate on `sqlite3_value` objects, with strong caveats around protected versus unprotected values, thread affinity, pointer invalidation, and out-of-memory detection.

Function context APIs include:

- `sqlite3_aggregate_context()` for per-aggregate storage.
- `sqlite3_user_data()` and `sqlite3_context_db_handle()` for callback context.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` for caching data associated with function arguments.
- `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` for named connection-scoped wrapper-library data.

Result APIs include `sqlite3_result_blob*()`, `sqlite3_result_double()`, `sqlite3_result_error*()`, `sqlite3_result_error_toobig()`, `sqlite3_result_error_nomem()`, `sqlite3_result_error_code()`, integer/null/text result setters, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_zeroblob*()`, and `sqlite3_result_subtype()`. `SQLITE_STATIC` and `SQLITE_TRANSIENT` define whether SQLite borrows or copies caller-owned buffers.

### Collations, Extension Loading, Hooks, and Connection State

Collation APIs are `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, `sqlite3_create_collation16()`, `sqlite3_collation_needed()`, and `sqlite3_collation_needed16()`. The `xCompare` callback must implement stable total-order semantics; otherwise SQLite behavior is undefined.

Connection and process-level APIs in this range include:

- `sqlite3_sleep()`, `sqlite3_temp_directory`, `sqlite3_data_directory`, and Win32 directory setters.
- `sqlite3_get_autocommit()`, `sqlite3_db_handle()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, and `sqlite3_txn_state()` with `SQLITE_TXN_NONE`, `SQLITE_TXN_READ`, and `SQLITE_TXN_WRITE`.
- `sqlite3_next_stmt()` for iterating prepared statements associated with a connection.
- `sqlite3_commit_hook()`, `sqlite3_rollback_hook()`, `sqlite3_update_hook()`, and `sqlite3_autovacuum_pages()`.
- `sqlite3_enable_shared_cache()`, `sqlite3_release_memory()`, `sqlite3_db_release_memory()`, `sqlite3_soft_heap_limit64()`, `sqlite3_hard_heap_limit64()`, and deprecated `sqlite3_soft_heap_limit()`.
- `sqlite3_table_column_metadata()` for schema/type/collation/constraint metadata.
- `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, and `sqlite3_reset_auto_extension()`.

Security-sensitive warnings appear around extension loading, shared cache, and client-data exposure. The comments recommend enabling only the C extension-loading API through `SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION` when possible so SQL injection cannot call the SQL-level `load_extension()`.

### Virtual Tables and Incremental BLOB I/O

Virtual table types and ABI structs include `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`. `sqlite3_module` defines the callback table for virtual table implementations: creation/connection, best-index planning, cursor open/filter/next/eof/column/rowid, update, transaction callbacks, function overloading, rename, savepoint callbacks, shadow-name checks, and integrity checks.

`sqlite3_index_info` is the planner contract passed to `xBestIndex()`. It carries WHERE constraints, ORDER BY terms, output constraint usage, selected index number/string, cost, estimated rows, scan flags, and column-usage mask. Constants include:

- `SQLITE_INDEX_SCAN_UNIQUE` and `SQLITE_INDEX_SCAN_HEX`.
- Constraint operators such as `SQLITE_INDEX_CONSTRAINT_EQ`, range operators, `MATCH`, `LIKE`, `GLOB`, `REGEXP`, `NE`, `IS`, `ISNULL`, `ISNOTNULL`, `LIMIT`, `OFFSET`, and function constraints.

Module registration and helper APIs include `sqlite3_create_module()`, `sqlite3_create_module_v2()`, `sqlite3_drop_modules()`, `sqlite3_declare_vtab()`, `sqlite3_overload_function()`, `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_vtab_nochange()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_in_first()`, `sqlite3_vtab_in_next()`, and `sqlite3_vtab_rhs_value()`. `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS` configure virtual-table behavior.

Incremental BLOB I/O declares opaque `sqlite3_blob` plus `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, and `sqlite3_blob_write()`. These APIs expose a fixed-size BLOB handle bound to a database/table/column/row, with separate readonly/readwrite open modes and explicit offset/length checks.

### VFS, Mutex, File Control, Testing, Strings, and Status

VFS APIs `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()` manage process-global VFS objects. Mutex APIs include `sqlite3_mutex_alloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, optional debug checks `sqlite3_mutex_held()` and `sqlite3_mutex_notheld()`, `sqlite3_db_mutex()`, mutex type constants, and `sqlite3_mutex_methods` for custom mutex implementations.

Low-level and diagnostic APIs include `sqlite3_file_control()`, `sqlite3_test_control()`, many `SQLITE_TESTCTRL_*` opcodes, SQL keyword helpers, case-insensitive/string pattern helpers, and `sqlite3_log()`. `sqlite3_test_control()` and its opcodes are explicitly unstable and test-only.

Dynamic string APIs define opaque `sqlite3_str` plus `sqlite3_str_new()`, `sqlite3_str_finish()`, append/reset helpers, and status/value accessors. Runtime status APIs include `sqlite3_status()`, `sqlite3_status64()`, `sqlite3_db_status()`, and `sqlite3_stmt_status()` with `SQLITE_STATUS_*`, `SQLITE_DBSTATUS_*`, and `SQLITE_STMTSTATUS_*` constants. These counters expose memory, page-cache, parser stack, lookaside, cache hits/misses/writes/spills, deferred foreign keys, full-scan steps, sort operations, auto-indexing, VM steps, reprepare/run counts, Bloom filter hits/misses, and statement memory use.

### Page Cache, Backup, Unlock Notify, and WAL

Custom page cache types include opaque `sqlite3_pcache`, `sqlite3_pcache_page`, `sqlite3_pcache_methods2`, and obsolete `sqlite3_pcache_methods`. The `sqlite3_pcache_methods2` table defines `xInit`, `xShutdown`, `xCreate`, `xCachesize`, `xPagecount`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`. These callbacks are registered with `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)` outside this chunk.

Online backup declares opaque `sqlite3_backup` plus `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`. The lifecycle is init, one or more step calls, then finish exactly once.

`sqlite3_unlock_notify()` registers a callback for shared-cache lock release when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled. Its documentation defines callback coalescing, immediate invocation races, deadlock detection, and the `DROP TABLE`/`DROP INDEX` special case where there may be no blocking connection.

WAL APIs include `sqlite3_wal_hook()`, `sqlite3_wal_autocheckpoint()`, `sqlite3_wal_checkpoint()`, and `sqlite3_wal_checkpoint_v2()`. Checkpoint modes are `SQLITE_CHECKPOINT_PASSIVE`, `SQLITE_CHECKPOINT_FULL`, `SQLITE_CHECKPOINT_RESTART`, and `SQLITE_CHECKPOINT_TRUNCATE`.

## Control Flow and Lifecycles

This chunk declares APIs rather than implementing control flow, but it documents several externally visible lifecycles:

- Prepared statements: prepare occurs earlier in the file, then callers bind parameters, call `sqlite3_step()` until `SQLITE_ROW`, `SQLITE_DONE`, or an error, optionally read columns while the row is valid, call `sqlite3_reset()` to run again, and eventually call `sqlite3_finalize()`.
- SQL functions: registration installs callback pointers on a connection. SQLite invokes callbacks during statement execution. Aggregate functions allocate state with `sqlite3_aggregate_context()`, scalar functions may cache argument-derived auxiliary data, and result APIs set the callback result or error.
- Collations and modules: registration stores caller-provided function tables or compare callbacks on a connection. The `_v2` variants add destructors for caller-owned context, but `sqlite3_create_collation_v2()` has a documented destructor-on-failure exception.
- Virtual tables: SQLite calls `xCreate`/`xConnect`, then `xBestIndex()` during planning, then cursor methods `xOpen`, `xFilter`, repeated `xColumn`/`xRowid`/`xNext`, and `xClose` during execution. Transaction and savepoint callbacks mirror surrounding SQL transaction state.
- Incremental BLOBs: `sqlite3_blob_open()` creates a handle, read/write calls operate within fixed blob bounds, `sqlite3_blob_reopen()` retargets the row, and `sqlite3_blob_close()` releases resources.
- Online backup: `sqlite3_backup_init()` opens the backup object and destination write transaction, repeated `sqlite3_backup_step()` calls transfer pages, and `sqlite3_backup_finish()` commits or rolls back and releases the object.
- WAL: commit hooks fire after WAL commits; autockpt is implemented as a WAL hook; explicit checkpoint modes vary in whether they wait for writers/readers and whether the WAL is reset or truncated.

## State and Persistence Behavior

Most persistent state controlled by these APIs lives in SQLite database connections, prepared statements, database files, WAL files, or application-owned callback contexts:

- Statement state includes bound values, VM execution position, current row values, cached column-name encodings, reset/finalize status, and statement counters.
- Connection state includes registered SQL functions, collations, modules, hooks, client data, extension-loading flags, autocommit/transaction state, attached database handles, page/cache/memory counters, VFS bindings, and WAL hook/autocheckpoint settings.
- Database-file state includes table contents, schema metadata, BLOB contents, journal/WAL frames, checkpoint progress, autovacuum free-page handling, and backup destination contents.
- Virtual table state is owned by module implementations through `sqlite3_vtab` and `sqlite3_vtab_cursor` subclasses. SQLite owns the ABI fields and calls into the module; the module owns any persistent backing store and must honor transaction/constraint semantics.
- Page-cache state is owned by the registered `sqlite3_pcache_methods2` implementation, which caches page buffers and per-page extras for SQLite pager users.
- Callback context pointers and auxiliary/client data carry application state and destructor responsibilities; misuse can leak memory, double free, or expose process control through scripting bindings.

The comments repeatedly document pointer lifetime. Many returned pointers are valid only until statement finalization, automatic reprepare, reset/finalize, the next call requesting a different encoding, the next string-builder mutation, or the end of a virtual-table callback. Several APIs are thread-affine or undefined if used concurrently on the same statement/connection without SQLite's required serialization.

## Dependencies and Integration Points

This chunk depends on types and result-code constants declared earlier in `sqlite3.c`, including `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_vfs`, `sqlite3_mutex`, `sqlite3_filename`, integer typedefs, result codes, open flags, and configuration opcodes.

In this repository, the source path is under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/`, so the practical integration point is WiredTiger's test-side vendored SQLite dependency rather than MongoDB's production storage engine. The declarations are still broad public SQLite ABI and may be exercised by:

- SQLite TCL/C tests or WiredTiger compatibility tests that compile the vendored amalgamation.
- Any local test harness that opens SQLite databases, prepares statements, binds values, reads result rows, registers SQL functions/collations, or uses backup/WAL APIs.
- Extension or virtual-table tests that depend on the `sqlite3_module`, `sqlite3_index_info`, BLOB, page-cache, mutex, VFS, unlock-notify, and WAL contracts.

Because this is an amalgamation, implementations for these declarations live later in the same file. Merge-level research should connect this chunk to adjacent chunks containing earlier type definitions and later function bodies, scan-status declarations, pager/VDBE/virtual-table implementation details, and compile-option guards.

## Risks

- This range is public ABI surface. Changing prototypes, constants, struct layouts, or callback signatures can break source or binary compatibility for SQLite consumers and extensions.
- Pointer lifetime is a major hazard. Column values, `sqlite3_value` text/blob data, dynamic-string buffers, metadata strings, virtual-table RHS values, and backup/status pointers can become invalid after later SQLite API calls.
- Many APIs are thread-sensitive. Misusing unprotected `sqlite3_value` objects, invoking SQLite APIs inside unlock-notify callbacks, sharing a destination backup connection concurrently, or using statement column APIs across reset/finalize/step boundaries can produce undefined behavior or deadlock.
- Extension loading and client-data APIs are security-sensitive. Exposing them to untrusted scripting or enabling SQL-level `load_extension()` can permit arbitrary native code execution.
- Virtual-table planning flags are correctness-sensitive. Incorrect `xBestIndex()` `omit`, `orderByConsumed`, `SQLITE_INDEX_SCAN_UNIQUE`, `sqlite3_vtab_distinct()`, IN handling, or constraint-support decisions can yield wrong query answers or incorrect rollback behavior.
- WAL checkpoint modes change concurrency behavior. FULL/RESTART/TRUNCATE can block on writers/readers and invoke busy handlers; PASSIVE may leave work incomplete. Hook replacement between `sqlite3_wal_hook()` and `sqlite3_wal_autocheckpoint()` is easy to miss.
- Custom mutex and page-cache methods are low-level extension points. Violating initialization, thread-safety, fetch/unpin/rekey/truncate, or memory-allocation requirements can corrupt database state or crash the process.
- The chunk ends mid scan-status documentation, so a final per-file report must reconcile this boundary with the following chunk before claiming full scan-status API coverage.

## Test and Validation Signals

Useful validation signals for this chunk are API, ABI, and behavioral tests rather than unit tests for local implementation bodies:

- Compile tests should include `sqlite3.c` and representative consumers that call prepared-statement, function, collation, hook, virtual-table, BLOB, backup, WAL, and status APIs.
- Statement lifecycle tests should cover bind lookup/clear, repeated `sqlite3_step()`, column type conversion, `sqlite3_data_count()`, `sqlite3_reset()`, and `sqlite3_finalize()` error propagation.
- Function tests should register scalar, aggregate, and window functions; exercise `sqlite3_value_*`, aggregate context, auxdata caching/destructors, pointer passing, subtypes, error result codes, and text/blob destructor modes.
- Virtual-table tests should cover `xBestIndex()` constraint mapping, `orderByConsumed`, DISTINCT/GROUP BY modes, RHS literal extraction, all-at-once IN constraints, `xUpdate()` conflict policy, `sqlite3_vtab_nochange()`, and module destruction.
- BLOB tests should validate readonly/readwrite handles, row retargeting, out-of-range reads/writes, schema-change expiry, and handle closure.
- Backup tests should cover incremental stepping, retryable `SQLITE_BUSY`/`SQLITE_LOCKED`, fatal IO/NOMEM/READONLY paths, source changes during backup, and destination connection isolation.
- WAL tests should cover hook replacement, autocheckpoint threshold behavior, PASSIVE/FULL/RESTART/TRUNCATE checkpoint modes, attached-database checkpointing, busy-handler behavior, and output frame counts.
- Extension-loading tests should verify default-disabled behavior and the difference between `sqlite3_enable_load_extension()` and connection-level database configuration.
- Status and diagnostic tests should query/reset `sqlite3_status*`, `sqlite3_db_status()`, `sqlite3_stmt_status()`, keyword helpers, string comparison/pattern helpers, and log callback behavior.
