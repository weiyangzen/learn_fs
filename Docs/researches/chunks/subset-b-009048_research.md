# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h lines 5213-10675

## Scope

This chunk is a public C API declaration and contract section from SQLite's amalgamated `sqlite3.h`, embedded under WiredTiger's SQLite test dependency tree. It starts at the tail of statement result-count APIs and spans the API surface for column value extraction, prepared-statement reset/finalize, application-defined SQL functions, SQL value/result objects, collations, connection hooks, extension loading, virtual tables, incremental BLOB I/O, VFS registration, mutexes, file controls, test controls, keyword/dynamic-string/status interfaces, custom page-cache methods, online backup, shared-cache unlock notifications, string matching, WAL hooks/checkpointing, virtual-table planner helper APIs, scan-status instrumentation, cache flushing, and the beginning of pre-update hooks.

The code in this range is almost entirely declarations, macros, opaque type definitions, ABI structs, and detailed API comments. Runtime behavior is implemented elsewhere in the amalgamated `sqlite3.c`; this header chunk defines the contracts that callers, extensions, VFS providers, virtual-table modules, page-cache implementations, and test harnesses must obey.

## Purpose

- Expose row/result access for the SQLite virtual machine after `sqlite3_step()` returns `SQLITE_ROW`, including type conversion, byte-count, pointer lifetime, and out-of-memory ambiguity rules.
- Define prepared-statement lifecycle endpoints: `sqlite3_finalize()` releases statement resources and returns the last execution error, while `sqlite3_reset()` rewinds execution without clearing bound parameters.
- Define registration and callback contracts for application-defined scalar, aggregate, and window SQL functions, including function flags that affect query planning and schema-safety policy.
- Provide APIs for inspecting `sqlite3_value` arguments, returning SQL function results, preserving aggregate state, caching auxiliary data, and attaching wrapper-library client data to a connection.
- Define collation registration and lazy collation lookup callbacks.
- Expose connection state, transaction state, schema/file metadata, commit/rollback/update/autovacuum hooks, shared-cache control, extension loading, and automatic extension registration.
- Define the virtual table ABI: module method table, instance/cursor superclasses, planner handshake structures, constraint operator macros, registration APIs, and later planner helper APIs.
- Define lower-level persistence integration points: incremental BLOB handles, VFS lookup/registration, file-control dispatch, WAL hook/checkpoint operations, online backup, page-cache replacement hooks, and mid-transaction cache flushing.
- Expose concurrency and instrumentation interfaces: mutex allocation/method tables, runtime/db/statement status counters, scan-status metrics, unlock notifications, keyword lookup, dynamic strings, log emission, and testing controls.

## Important APIs, Types, And Constants

### Statement row access and lifecycle

- `sqlite3_data_count(sqlite3_stmt*)` reports available result columns for the current row, with special handling around completed statements and incremental vacuum noted just before this chunk.
- Fundamental datatype constants are `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL`.
- Column accessors are `sqlite3_column_blob()`, `sqlite3_column_double()`, `sqlite3_column_int()`, `sqlite3_column_int64()`, `sqlite3_column_text()`, `sqlite3_column_text16()`, `sqlite3_column_value()`, `sqlite3_column_bytes()`, `sqlite3_column_bytes16()`, and `sqlite3_column_type()`.
- `sqlite3_finalize()` destroys a prepared statement at any point in its lifecycle and must be called for every prepared statement to avoid leaks.
- `sqlite3_reset()` rewinds a prepared statement for reuse and preserves existing bindings; callers must still inspect its return code because deferred write/locking errors can surface during reset.

### User-defined SQL functions and values

- Function registration APIs are `sqlite3_create_function()`, `sqlite3_create_function16()`, `sqlite3_create_function_v2()`, and `sqlite3_create_window_function()`.
- Text encoding constants are `SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, deprecated `SQLITE_ANY`, and collation-only `SQLITE_UTF16_ALIGNED`.
- Function property flags include `SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_SUBTYPE`, `SQLITE_INNOCUOUS`, `SQLITE_RESULT_SUBTYPE`, and `SQLITE_SELFORDER1`.
- Deprecated compatibility APIs in this chunk include `sqlite3_aggregate_count()`, `sqlite3_expired()`, `sqlite3_transfer_bindings()`, `sqlite3_global_recover()`, `sqlite3_thread_cleanup()`, and `sqlite3_memory_alarm()`.
- `sqlite3_value_*()` APIs inspect protected SQL values passed to functions and virtual tables: blob, double, integer, int64, pointer, UTF-8/UTF-16 text, byte counts, original/numeric type, no-change marker, from-bind marker, encoding, subtype, duplication, and free.
- `sqlite3_aggregate_context()` allocates per-group aggregate state, `sqlite3_user_data()` retrieves the registration `pApp`, and `sqlite3_context_db_handle()` reaches the owning connection.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` cache per-argument function data, often for compiled regex or parser state. `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` attach named wrapper-private pointers to a connection.
- `sqlite3_destructor_type`, `SQLITE_STATIC`, and `SQLITE_TRANSIENT` define ownership transfer semantics for result and binding buffers.
- Result APIs include `sqlite3_result_blob()`, `sqlite3_result_blob64()`, `sqlite3_result_double()`, `sqlite3_result_error*()`, `sqlite3_result_int*()`, `sqlite3_result_null()`, `sqlite3_result_text*()`, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_zeroblob*()`, and `sqlite3_result_subtype()`.

### Collations, connection state, hooks, and extensions

- Collation registration uses `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, and `sqlite3_create_collation16()`. Lazy registration uses `sqlite3_collation_needed()` and `sqlite3_collation_needed16()`.
- Directory and platform hooks include `sqlite3_sleep()`, global `sqlite3_temp_directory`, global `sqlite3_data_directory`, `sqlite3_win32_set_directory*()`, and `SQLITE_WIN32_*_DIRECTORY_TYPE`.
- Connection and schema introspection APIs include `sqlite3_get_autocommit()`, `sqlite3_db_handle()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, `sqlite3_txn_state()`, and `sqlite3_next_stmt()`.
- Transaction state constants are `SQLITE_TXN_NONE`, `SQLITE_TXN_READ`, and `SQLITE_TXN_WRITE`.
- Hook APIs include `sqlite3_commit_hook()`, `sqlite3_rollback_hook()`, `sqlite3_autovacuum_pages()`, and `sqlite3_update_hook()`.
- Shared cache and memory pressure APIs include `sqlite3_enable_shared_cache()`, `sqlite3_release_memory()`, `sqlite3_db_release_memory()`, `sqlite3_soft_heap_limit64()`, `sqlite3_hard_heap_limit64()`, and deprecated `sqlite3_soft_heap_limit()`.
- `sqlite3_table_column_metadata()` forces schema loading/parsing as needed to report declared type, collation, not-null, primary-key, and autoincrement metadata.
- Extension APIs include `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, and `sqlite3_reset_auto_extension()`.

### Virtual table ABI

- Opaque/superclass types are `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`.
- `struct sqlite3_module` is the core virtual-table method table. Versioned methods cover create/connect, best-index planning, disconnect/destroy, cursor open/close/filter/next/eof/column/rowid, updates, transaction callbacks, function overloading, rename, savepoint/release/rollback-to, shadow-table naming, and integrity checking.
- `struct sqlite3_index_info` is the `xBestIndex()` planner contract with input constraints/order-by/column-use fields and output constraint usage, strategy identifiers, order consumption, estimated cost/rows, and scan flags.
- Scan flags are `SQLITE_INDEX_SCAN_UNIQUE` and `SQLITE_INDEX_SCAN_HEX`.
- Constraint operators include equality/range operators, `MATCH`, `LIKE`, `GLOB`, `REGEXP`, `NE`, `IS`, null tests, `LIMIT`, `OFFSET`, and `SQLITE_INDEX_CONSTRAINT_FUNCTION`.
- Module registration/removal APIs are `sqlite3_create_module()`, `sqlite3_create_module_v2()`, and `sqlite3_drop_modules()`.
- `sqlite3_declare_vtab()` declares the schema from `xCreate`/`xConnect`; `sqlite3_overload_function()` installs placeholder functions that virtual tables may override.
- Later vtab helper APIs include `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_vtab_nochange()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_in_first()`, `sqlite3_vtab_in_next()`, and `sqlite3_vtab_rhs_value()`.
- Virtual-table configuration constants are `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- Conflict return constants exposed here are `SQLITE_ROLLBACK`, `SQLITE_FAIL`, and `SQLITE_REPLACE`; comments cross-reference `SQLITE_IGNORE` and `SQLITE_ABORT` because those are defined for other callback/result-code roles.

### BLOB, VFS, mutex, file-control, and test interfaces

- `sqlite3_blob` is the opaque incremental BLOB handle. Operations are `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, and `sqlite3_blob_write()`.
- VFS registry APIs are `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()`.
- Mutex APIs are `sqlite3_mutex_alloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, debug-only `sqlite3_mutex_held()`, and `sqlite3_mutex_notheld()`.
- `struct sqlite3_mutex_methods` is the app-defined mutex provider table for `SQLITE_CONFIG_MUTEX` and `SQLITE_CONFIG_GETMUTEX`.
- Mutex type constants include dynamic `SQLITE_MUTEX_FAST`/`SQLITE_MUTEX_RECURSIVE`, static internal mutex IDs, app/VFS static mutexes, and legacy `SQLITE_MUTEX_STATIC_MASTER`.
- `sqlite3_db_mutex()` returns the connection mutex in serialized mode.
- `sqlite3_file_control()` dispatches low-level opcodes to a database file's `xFileControl` or handles selected opcodes directly in SQLite core.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` constants expose unstable internal testing/fault-injection controls.

### String, status, page cache, backup, WAL, and preupdate APIs

- Keyword helpers are `sqlite3_keyword_count()`, `sqlite3_keyword_name()`, and `sqlite3_keyword_check()`.
- Dynamic string APIs revolve around opaque `sqlite3_str`: `sqlite3_str_new()`, `sqlite3_str_finish()`, append/reset methods, and status/value methods.
- Process-wide status APIs are `sqlite3_status()` and `sqlite3_status64()` with `SQLITE_STATUS_*` verbs for memory, page-cache, malloc, and parser stack metrics.
- Connection status uses `sqlite3_db_status()` and `SQLITE_DBSTATUS_*` verbs for lookaside, pager cache, schema, statement memory, cache hit/miss/write/spill, and deferred foreign keys.
- Statement status uses `sqlite3_stmt_status()` and `SQLITE_STMTSTATUS_*` counters for full scans, sorts, automatic indexes, VM steps, reprepare, run count, Bloom-filter hits/misses, and memory used.
- Custom page cache types are `sqlite3_pcache`, `sqlite3_pcache_page`, `struct sqlite3_pcache_methods2`, and obsolete `struct sqlite3_pcache_methods`.
- Online backup uses opaque `sqlite3_backup` and `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`.
- Shared-cache unlock notification is `sqlite3_unlock_notify()` behind `SQLITE_ENABLE_UNLOCK_NOTIFY`.
- Utility string/log APIs are `sqlite3_stricmp()`, `sqlite3_strnicmp()`, `sqlite3_strglob()`, `sqlite3_strlike()`, and `sqlite3_log()`.
- WAL APIs are `sqlite3_wal_hook()`, `sqlite3_wal_autocheckpoint()`, `sqlite3_wal_checkpoint()`, `sqlite3_wal_checkpoint_v2()`, and checkpoint mode constants `SQLITE_CHECKPOINT_PASSIVE`, `SQLITE_CHECKPOINT_FULL`, `SQLITE_CHECKPOINT_RESTART`, and `SQLITE_CHECKPOINT_TRUNCATE`.
- Scan-status APIs are `sqlite3_stmt_scanstatus()`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus_reset()`, `SQLITE_SCANSTAT_*` opcodes, and `SQLITE_SCANSTAT_COMPLEX`.
- `sqlite3_db_cacheflush()` flushes dirty pager-cache pages mid-transaction.
- The pre-update hook section begins with `sqlite3_preupdate_hook()` behavior and describes companion APIs `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and blob-write-specific handling that continues beyond this chunk.

## Control Flow And Call Sequences

The statement result sequence is: prepare a statement elsewhere, call `sqlite3_step()`, and only while the latest step result is `SQLITE_ROW` call the `sqlite3_column_*()` APIs. A caller may force conversion by calling a text/blob accessor and then call the matching byte-count accessor. Calling `sqlite3_step()`, `sqlite3_reset()`, or `sqlite3_finalize()` invalidates returned pointers. `sqlite3_reset()` returns completion status for the prior run and prepares the statement for another run without clearing bindings; `sqlite3_finalize()` ends the lifecycle.

The user-defined function path starts with registration on each `sqlite3*` connection. During expression evaluation, SQLite invokes scalar `xFunc`, aggregate `xStep`/`xFinal`, or window `xStep`/`xFinal`/`xValue`/`xInverse` callbacks. The callback reads protected `sqlite3_value**` arguments, optionally uses aggregate context or auxdata, then emits exactly one result or error through `sqlite3_result_*()`. Destructor callbacks associated with function registration, result buffers, auxdata, pointer values, and client data form important cleanup edges.

Collation lookup is a connection-local dispatch. Callers may register explicit collations up front or install a collation-needed callback that registers a missing collation when the parser or VM asks for it. SQLite chooses the registered implementation that minimizes string encoding conversion, but all implementations for the same collation name must impose equivalent ordering.

Connection hooks form callback paths out of transaction execution. Commit hooks may veto a commit by returning non-zero, converting it into a rollback. Rollback hooks report explicit or implicit rollbacks except close-time rollback. Update hooks report rowid-table changes after/before timing that is intentionally unspecified. Autovacuum page callbacks run during commit-time autovacuum and must be simple, non-reentrant arithmetic decisions.

Extension loading is disabled by default. The safer flow is to enable only the C API via `sqlite3_db_config(...SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION...)` outside this chunk, then call `sqlite3_load_extension()`. `sqlite3_enable_load_extension()` enables both C loading and the SQL `load_extension()` function, which broadens SQL-injection impact. Automatic extensions register process-wide entry points that run for subsequent database opens.

Virtual table control flow is a multi-stage handshake. The application registers a stable `sqlite3_module` with a connection. SQLite invokes `xCreate` or `xConnect`, the module declares a schema with `sqlite3_declare_vtab()`, then queries call `xBestIndex()` with `sqlite3_index_info` inputs. `xBestIndex()` selects constraints, ordering, estimated cost/rows, and strategy IDs. Execution then opens a cursor, calls `xFilter()` with argv values selected by `xBestIndex()`, iterates through `xNext()`/`xEof()`, returns columns/rowids, and performs updates through `xUpdate()` when needed. Transaction and savepoint methods mirror SQLite transaction control.

Incremental BLOB flow opens a rowid-table text/blob cell using `sqlite3_blob_open()`, optionally repositions within the same table/column using `sqlite3_blob_reopen()`, reads/writes fixed-size slices, and closes with `sqlite3_blob_close()`. Writes cannot change blob length. Updating or deleting the underlying row expires the handle, causing later reads/writes to return `SQLITE_ABORT`.

Online backup flow is explicit: `sqlite3_backup_init()` creates state and opens a write transaction on the destination, repeated `sqlite3_backup_step()` calls copy pages, and exactly one `sqlite3_backup_finish()` releases resources and either commits or rolls back destination work. Source read locks are held only during each step, so source writes can proceed between steps and may restart copying.

WAL flow uses either a custom `sqlite3_wal_hook()` or the convenience `sqlite3_wal_autocheckpoint()`, which installs a hook that runs passive checkpoints after a frame threshold. Manual checkpointing uses `sqlite3_wal_checkpoint_v2()` with increasing blocking behavior from PASSIVE to FULL to RESTART to TRUNCATE. Hook and autocheckpoint installation overwrite each other because both occupy the single WAL callback slot on a connection.

Status and scan-status APIs are observational. Global status, connection status, statement counters, and scan-status measurements expose counters/high-water marks with reset flags. Scan status is build-conditional and indexes query-plan elements, enabling applications to compare planner estimates with measured loop visits.

## State And Persistence Behavior

Most declarations in this header manipulate opaque state owned by SQLite. Prepared statements hold current row values, converted value buffers, bindings, execution counters, and VM state. The chunk's comments repeatedly define pointer validity: column text/blob pointers live only until conversion or statement advancement/reset/finalize; `sqlite3_column_value()` returns an unprotected value; byte counts exclude zero terminators; `sqlite3_column_type()` is meaningful before conversions.

User-defined function state is split across connection-local function registries, per-call `sqlite3_context`, protected input values, aggregate context memory, auxdata cached on expression arguments, and optional connection client data. Auxdata can be discarded earlier than a caller expects, including immediately during `sqlite3_set_auxdata()` on allocation failure or planner-time evaluation, so destructors and post-call pointer use are central correctness concerns.

Function flags and virtual-table flags feed persistent schema safety. `SQLITE_DIRECTONLY`, `SQLITE_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_INNOCUOUS` determine whether application-defined behavior may run from views, triggers, constraints, generated columns, expression indexes, partial indexes, or untrusted schemas. Misclassification can turn a database file's schema into a vehicle for invoking application code.

Connection-global and process-global variables affect persistence locations. `sqlite3_temp_directory` controls temporary file placement for built-in VFSes, while `sqlite3_data_directory` affects relative database file resolution on Windows VFSes. The comments warn that changing these while connections are active is unsafe and, for `sqlite3_data_directory`, can corrupt databases.

Transaction and persistence state are exposed by `sqlite3_get_autocommit()`, `sqlite3_txn_state()`, hooks, autovacuum callbacks, BLOB handles, backup handles, WAL checkpoints, and cache flushing. Some APIs directly affect on-disk state: incremental BLOB writes modify existing cell content, online backup writes destination database pages, WAL checkpoints move WAL frames into database files and may truncate WAL files, autovacuum callbacks choose how many free pages to remove, and `sqlite3_db_cacheflush()` writes dirty cache pages mid-transaction.

Virtual table implementations own their own persistence behind `sqlite3_vtab` subclasses. SQLite relies on the module's claims, such as constraint support and unique scans, to decide rollback behavior and query planning. If a module claims `SQLITE_VTAB_CONSTRAINT_SUPPORT`, it promises constraint failures are reported before modifying internal or persistent data structures.

Custom page-cache state is process and cache-instance state supplied via `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)`. SQLite copies the method table, calls `xInit()` during initialization, creates per-database cache instances through `xCreate()`, pins/unpins pages through `xFetch()` and `xUnpin()`, and expects `xDestroy()`/`xShutdown()` to release resources. Because this sits under pager behavior, mistakes can corrupt cache coherence or cause memory leaks.

Mutex state may be SQLite-provided or application-provided. Static mutex IDs are ABI-visible but primarily internal; applications should allocate dynamic fast/recursive mutexes if they use this subsystem directly. Custom mutex providers must initialize without using SQLite allocation in `xMutexInit()` and support all static mutex types SQLite may request.

## Dependencies And Integration Points

- This header depends on earlier declarations of `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_int64`, `sqlite3_uint64`, `sqlite3_filename`, `sqlite3_vfs`, `sqlite3_mutex`, result codes, open flags, config flags, and many cross-linked constants.
- The statement APIs integrate with prepared-statement creation/binding/stepping APIs declared in other chunks and implemented in the VDBE.
- Function, aggregate, window, collation, auxdata, subtype, and pointer-passing APIs integrate application C callbacks with SQL expression evaluation.
- Virtual table definitions are a major extension ABI. They integrate with the parser (`CREATE VIRTUAL TABLE`), planner (`xBestIndex`), VM execution (`xFilter`/`xColumn`/`xUpdate`), transaction manager, savepoints, integrity checks, and optional shadow-table handling.
- BLOB APIs integrate with rowid table storage, constraints, foreign-key rules, transaction commit, and pre-update hook behavior.
- VFS APIs and file-control dispatch integrate SQLite with OS-specific filesystem implementations, custom VFS providers, and storage-engine-specific controls.
- Mutex and page-cache methods integrate embedders with SQLite's process initialization, pager cache, and memory pressure mechanisms.
- Backup, WAL, checkpoint, autovacuum, and cache-flush APIs integrate with pager locking, journal/WAL files, database page persistence, and busy handlers.
- Status, scan-status, keyword, dynamic-string, string match, and logging APIs integrate with diagnostics, query tuning, extension code, and test harnesses.
- Test-control constants integrate with SQLite's internal fault-injection and coverage tests, not stable application logic.

## Risks And Edge Cases

- The column access APIs have strict validity windows. Calling them outside a current `SQLITE_ROW`, mixing UTF-8 and UTF-16 accessors in the wrong order, or retaining returned pointers after conversions/reset/finalize can yield undefined behavior or stale pointers.
- `sqlite3_column_value()` returns an unprotected `sqlite3_value`; using it with general `sqlite3_value_*()` APIs in multithreaded application code is not safe. The intended use is mainly inside functions and virtual tables.
- `sqlite3_reset()` can report errors even when previous `sqlite3_step()` returned `SQLITE_ROW`, notably for `RETURNING` statements whose write completion is deferred.
- User-defined functions must not close the database connection or finalize/reset the running statement. Function result and auxdata destructors can run immediately on failure, so implementations must not use a pointer after giving it to SQLite with a destructor.
- Incorrect function flags are security-sensitive. Omitting `SQLITE_DIRECTONLY` from side-effecting or information-revealing functions may allow malicious schema objects to invoke application code. Marking a non-innocuous function as innocuous can bypass trusted-schema protections.
- Collation callbacks must implement a stable total ordering. Violating symmetry or transitivity makes SQLite behavior undefined and can corrupt query answers or indexes that depend on that collation.
- `sqlite3_create_collation_v2()` is an API exception: its destructor is not called if registration fails, so callers must clean up `pArg` themselves on error.
- Global directory variables are legacy, not thread-safe, and interact with pragmas that assume `sqlite3_malloc()` ownership. Directly assigning static or stack memory can later lead to invalid frees if the corresponding pragma is used.
- Commit, rollback, update, autovacuum, unlock-notify, and preupdate callbacks have non-reentrancy constraints. Calling back into SQLite in prohibited ways can deadlock, corrupt state, or produce undefined behavior.
- Shared cache is discouraged. Unlock-notify exists for shared-cache lock waits and includes deadlock detection, but callback timing can be immediate and the DROP TABLE/INDEX same-connection exception can cause retry loops.
- Extension loading is a direct code-loading surface. Enabling the SQL `load_extension()` function broadens exposure to SQL injection, so connection-specific C-only enabling is safer.
- Virtual table modules are ABI-sensitive. The `sqlite3_module` object must remain stable while registered, `sqlite3_index_info` fields added in later SQLite versions must not be used against older libraries, and invalid `orderByConsumed`, `omit`, `UNIQUE`, `DISTINCT`, or constraint-support claims can produce wrong query results or unsafe rollback behavior.
- Incremental BLOB writes cannot change blob size and are not automatically rolled back just because a handle later expires. Applications must reason about transaction boundaries and row modifications carefully.
- VFS registration with duplicate names or empty names is undefined. Unregistering the default VFS picks an arbitrary new default.
- Custom mutex and page-cache implementations sit below core invariants. Missing static mutex handling, non-threadsafe cache methods, incorrect pin/unpin semantics, or stale page rekey/truncate behavior can destabilize the entire library.
- `sqlite3_file_control()` can return `SQLITE_ERROR` for either an unknown database name or a VFS-level error, with no reliable distinction.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` are explicitly unstable and should not be used by applications.
- Status counters and scan-status values are conditional or approximate. Some high-water/current fields are undefined for specific opcodes, and scan status is only compiled with `SQLITE_ENABLE_STMT_SCANSTATUS`.
- WAL hooks and autocheckpointing occupy the same single callback slot. Installing one silently disables the other.
- Checkpoint modes differ materially in lock acquisition and busy-handler behavior. PASSIVE never invokes the busy handler; FULL/RESTART/TRUNCATE may block writers and wait for readers; all modes need the checkpoint lock and can return `SQLITE_BUSY`.
- `sqlite3_db_cacheflush()` intentionally does not set the connection error code/message, so callers must use the direct return code rather than later `sqlite3_errcode()` state.
- Preupdate value pointers are only valid until the callback returns, and old/new accessors are only valid for particular operation kinds. BLOB writes are reported through a special preupdate path that can appear as `SQLITE_DELETE` before new values are available.

## Test Signals

- SQLite's API documentation comments include requirement tags and method/destructor annotations that upstream tests often validate through documentation generation and API conformance checks.
- Unit and integration coverage for this header surface should exercise statement value extraction order, OOM during type conversion, pointer invalidation, reset/finalize return codes, and NULL/failure handling.
- Function tests should cover scalar/aggregate/window callback registration, destructor invocation on success/failure/overload/close, auxdata lifetime, subtype propagation, direct-only and innocuous restrictions, pointer passing, aggregate context allocation, and no-change/from-bind value flags.
- Collation tests should cover UTF-8/UTF-16 registrations, lazy collation-needed callbacks, deletion/replacement, v2 destructor asymmetry on failure, and equivalent ordering across encodings.
- Hook tests should verify commit veto rollback, rollback-hook omissions on close-time rollback, update-hook exclusions for system/WITHOUT ROWID/truncate/replace cases, autovacuum callback page counts, and callback non-reentrancy expectations.
- Extension tests should ensure loading is disabled by default, C-only enabling works independently from SQL `load_extension()`, auto-extension entry points run once per opened connection, and cancellation/reset works.
- Virtual table tests should cover the full `sqlite3_module` lifecycle, `xBestIndex` constraint mapping, `omit` behavior, order-by consumption, estimated rows/cost, unique scan rollback semantics, IN all-at-once handling, RHS literal extraction, collation lookup, distinct modes, no-change update optimization, conflict policy, direct-only/innocuous flags, all-schema read transactions, savepoints, and integrity callbacks.
- BLOB tests should cover row/table/column validation errors, read-only/write modes, indexed/PK/FK write restrictions, expiration after row modification, reopen failure abort state, offset bounds, close-time autocommit, and zeroblob workflows.
- VFS, mutex, and page-cache tests should cover duplicate/default VFS registration behavior, file-control core opcodes, app-defined mutex methods under debug assertions, page-cache create/fetch/unpin/rekey/truncate/destroy/shrink semantics, and memory pressure release hooks.
- Backup tests should cover destination transaction conflicts, step return codes, retryable `BUSY`/`LOCKED`, fatal IO/NOMEM/READONLY errors, source mutation restart, destination-handle exclusivity, shared-cache restrictions, remaining/pagecount updates, and finish behavior after incomplete backups.
- WAL tests should cover hook replacement by autocheckpoint, default autocheckpoint thresholds, all checkpoint modes, attached database handling, not-in-WAL outputs, busy-handler behavior, and truncation outputs.
- Instrumentation tests should cover process/db/statement status opcodes, unsupported opcode failures, high-water reset, scan-status build gating, `SQLITE_SCANSTAT_COMPLEX`, and cacheflush return behavior without connection error-state mutation.

## Unresolved Cross-Chunk References

- The tail of the pre-update hook declaration block continues after line 10675, including the final prototypes and the remainder of `sqlite3_preupdate_blobwrite()` behavior.
- Implementations for all APIs in this header chunk live in `sqlite3.c` and other portions of the amalgamation; this chunk documents ABI contracts rather than executable logic.
- Several referenced constants and APIs are declared outside this line range, including bind APIs, prepare/step APIs, `sqlite3_db_config()` options, VFS/file-control opcode structs, result codes, open flags, and `sqlite3_api_routines`.
