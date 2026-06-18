# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.h lines 1-5491

## Scope And Purpose

This chunk is the public C API declaration surface for the FoundationDB vendored SQLite 3.7.6 header, from the file preamble through the start of the runtime database-status section. The header states that APIs not declared here are not published SQLite APIs, so this file is the ABI and integration contract for code embedding or extending this SQLite copy.

The range covers version identity, exported symbol macros, connection and statement handles, result-code constants, VFS/file abstractions, initialization/configuration hooks, memory and mutex customization, connection lifecycle, statement preparation/execution/binding/result extraction, SQL function and collation extension points, virtual table declarations, incremental BLOB I/O, VFS registration, file-control, test-control, and global runtime status counters. Line 5491 only begins the `sqlite3_db_status` documentation; the detailed per-connection status API belongs to the following chunk.

This FoundationDB copy is not a pristine upstream header. It defines `SQLITE_HAS_CODEC` and `SQLITE_HAS_CODEC_NO_ENCRYPTION` near the top, exposes `sqlite3BtreePagerSetCodec()`, and extends `sqlite3_io_methods` with zero-copy file-read hooks. Those are the most visible local integration seams in this slice.

## Important APIs, Types, And Functions

Core versioning and library identity:

- `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, and `SQLITE_SOURCE_ID` identify SQLite 3.7.6 with source id `2011-03-17 01:58:21 ...`.
- `sqlite3_version`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose equivalent runtime identity.
- `sqlite3_compileoption_used()` and `sqlite3_compileoption_get()` provide compile-option diagnostics unless omitted.
- `sqlite3_threadsafe()` reports compile-time mutex support, not runtime threading mode changes.

Fundamental public handles and scalar types:

- `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_blob`, `sqlite3_file`, `sqlite3_vfs`, `sqlite3_mutex`, `sqlite3_module`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, and `sqlite3_index_info` are the major opaque or semi-opaque API objects.
- `sqlite3_int64` and `sqlite3_uint64` abstract signed/unsigned 64-bit values.
- `sqlite3_destructor_type`, `SQLITE_STATIC`, and `SQLITE_TRANSIENT` define ownership behavior for bound and returned text/blob buffers.

Connection and statement lifecycle:

- `sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` create connections, with open flags such as `SQLITE_OPEN_READONLY`, `SQLITE_OPEN_READWRITE`, `SQLITE_OPEN_CREATE`, mutex mode flags, shared/private cache flags, and VFS selection.
- `sqlite3_close()` destroys a connection only after prepared statements and BLOB handles are finalized/closed; open transactions are rolled back.
- `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare16()`, and `sqlite3_prepare16_v2()` compile SQL to `sqlite3_stmt`. The v2 forms retain SQL text and support automatic reprepare and more specific `sqlite3_step()` errors.
- `sqlite3_step()`, `sqlite3_reset()`, and `sqlite3_finalize()` drive and clean up statement execution.
- `sqlite3_sql()` returns saved SQL for v2 statements, and `sqlite3_stmt_readonly()` classifies direct database writes.

Result and error codes:

- Primary result codes include `SQLITE_OK`, `SQLITE_ERROR`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_NOMEM`, `SQLITE_READONLY`, `SQLITE_INTERRUPT`, `SQLITE_IOERR`, `SQLITE_CORRUPT`, `SQLITE_CONSTRAINT`, `SQLITE_MISUSE`, `SQLITE_ROW`, and `SQLITE_DONE`.
- Extended codes covered here include detailed I/O failures such as `SQLITE_IOERR_READ`, `SQLITE_IOERR_WRITE`, shared-memory failures, `SQLITE_LOCKED_SHAREDCACHE`, `SQLITE_BUSY_RECOVERY`, and `SQLITE_CANTOPEN_NOTEMPDIR`.
- `sqlite3_extended_result_codes()` toggles extended result-code reporting per connection.
- `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_errmsg()`, and `sqlite3_errmsg16()` expose the most recent connection error.

Binding and result extraction:

- `sqlite3_bind_blob()`, `sqlite3_bind_double()`, `sqlite3_bind_int()`, `sqlite3_bind_int64()`, `sqlite3_bind_null()`, `sqlite3_bind_text()`, `sqlite3_bind_text16()`, `sqlite3_bind_value()`, and `sqlite3_bind_zeroblob()` bind host parameters.
- `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3_bind_parameter_index()`, and `sqlite3_clear_bindings()` inspect or clear parameter state.
- `sqlite3_column_count()`, `sqlite3_data_count()`, column-name/origin/declared-type APIs, and `sqlite3_column_blob()/bytes()/double()/int()/int64()/text()/text16()/type()/value()` expose result rows after `SQLITE_ROW`.
- Fundamental runtime value types are `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL`.

Extension callbacks:

- `sqlite3_create_function()`, `sqlite3_create_function16()`, and `sqlite3_create_function_v2()` register scalar and aggregate SQL functions.
- `sqlite3_value_*()` reads protected SQL-function arguments; `sqlite3_result_*()` writes scalar, blob, text, zeroblob, error, OOM, and copied-value results.
- `sqlite3_aggregate_context()`, `sqlite3_user_data()`, `sqlite3_context_db_handle()`, `sqlite3_get_auxdata()`, and `sqlite3_set_auxdata()` manage function-local and argument-local state.
- `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, `sqlite3_create_collation16()`, `sqlite3_collation_needed()`, and `sqlite3_collation_needed16()` register comparison behavior and lazy collation resolution.
- `sqlite3_set_authorizer()`, authorizer return codes, and action codes gate compile-time SQL operations.
- `sqlite3_trace()`, `sqlite3_profile()`, and `sqlite3_progress_handler()` provide execution tracing, profiling, and cancellation callbacks.

VFS, file, and persistence contracts:

- `sqlite3_io_methods` defines file operations: close/read/write/truncate/sync/filesize/lock/unlock/check-reserved-lock/file-control/sector-size/device-characteristics, plus WAL shared-memory methods.
- This vendored header adds `xReadZeroCopy()` and `xReleaseZeroCopy()` after the version-2 I/O methods. Any local VFS implementation must account for this layout extension.
- `sqlite3_vfs` defines open/delete/access/full-pathname/dynamic-loading/randomness/sleep/current-time/error/system-call hooks.
- `SQLITE_IOCAP_*`, `SQLITE_LOCK_*`, `SQLITE_SYNC_*`, `SQLITE_FCNTL_*`, `SQLITE_ACCESS_*`, and `SQLITE_SHM_*` constants describe storage guarantees, lock levels, sync behavior, file controls, access probes, and shared-memory lock operations.
- `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()` manage VFS registration.
- `sqlite3_file_control()` forwards low-level operations to the underlying open database file.

Initialization, configuration, memory, and mutexes:

- `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, and `sqlite3_os_end()` manage process-level initialization and OS abstraction setup.
- `sqlite3_config()` controls global threading, allocators, scratch/pagecache/heap memory, mutex implementation, lookaside defaults, page cache implementation, and logging.
- `sqlite3_db_config()` currently covers per-connection lookaside memory.
- `sqlite3_mem_methods` and `sqlite3_mutex_methods` are application-supplied allocator and mutex vtables.
- `sqlite3_malloc()`, `sqlite3_realloc()`, `sqlite3_free()`, `sqlite3_memory_used()`, `sqlite3_memory_highwater()`, `sqlite3_release_memory()`, `sqlite3_soft_heap_limit64()`, and deprecated `sqlite3_soft_heap_limit()` expose memory allocation and memory-pressure controls.
- `sqlite3_mutex_alloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, debug-only mutex verification, mutex type constants, and `sqlite3_db_mutex()` expose SQLite mutexes.
- `sqlite3_status()` and `SQLITE_STATUS_*` constants report process-level memory, pagecache, scratch, allocation, and parser-stack statistics.

Connection-observable state and utility APIs:

- `sqlite3_last_insert_rowid()`, `sqlite3_changes()`, and `sqlite3_total_changes()` report connection-local write state.
- `sqlite3_interrupt()`, `sqlite3_complete()`, `sqlite3_complete16()`, `sqlite3_busy_handler()`, and `sqlite3_busy_timeout()` control cancellation, SQL completeness checks, and lock contention behavior.
- `sqlite3_get_table()` and `sqlite3_free_table()` are legacy convenience wrappers over `sqlite3_exec()`.
- `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, and `sqlite3_vsnprintf()` provide SQLite-owned string formatting with SQL escaping formats.
- `sqlite3_randomness()`, `sqlite3_sleep()`, `sqlite3_temp_directory`, `sqlite3_get_autocommit()`, `sqlite3_db_handle()`, `sqlite3_next_stmt()`, commit/rollback/update hooks, and `sqlite3_enable_shared_cache()` expose utility and connection-management behavior.
- `sqlite3_table_column_metadata()`, `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3_auto_extension()`, and `sqlite3_reset_auto_extension()` integrate metadata lookup and extension loading.

Virtual table and BLOB APIs:

- `sqlite3_module` defines virtual table module methods from create/connect through scan, update, transaction hooks, function override, and rename.
- `sqlite3_index_info` transfers constraint and order-by information into `xBestIndex()` and receives virtual table planning decisions.
- `sqlite3_create_module()`, `sqlite3_create_module_v2()`, `sqlite3_declare_vtab()`, and `sqlite3_overload_function()` register and support virtual tables.
- `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, and `sqlite3_blob_write()` support fixed-size incremental BLOB access.

FoundationDB codec seam:

- `typedef struct Btree Btree` and `typedef unsigned int Pgno` are exposed only to support codec installation.
- `sqlite3BtreePagerSetCodec()` installs page codec, codec-size-change, codec-free callbacks, and codec context on a Btree pager.
- Because `SQLITE_HAS_CODEC_NO_ENCRYPTION` is defined, public SEE-style `sqlite3_key()`, `sqlite3_rekey()`, and `sqlite3_activate_see()` declarations are excluded even though codec plumbing remains enabled.

## Control Flow

The normal connection flow is: initialize the library explicitly or implicitly, open a connection, configure connection-local behavior if needed, prepare SQL, bind parameters, step until `SQLITE_ROW` or completion/error, read column values while the row is current, reset for reuse or finalize, close BLOB handles, then close the connection. `sqlite3_exec()` and `sqlite3_get_table()` collapse parts of this flow into convenience wrappers, but they still rely on prepare/step/finalize behavior underneath.

Statement execution is stateful. Bindings survive `sqlite3_reset()` and must be cleared with `sqlite3_clear_bindings()` when callers want parameters to become NULL. Column pointers remain valid only until a type conversion, `sqlite3_step()`, `sqlite3_reset()`, or `sqlite3_finalize()`. The v2 prepare APIs are the preferred path because they keep original SQL for reprepare and return more specific step errors.

Lock contention flows through the busy handler. If SQLite determines that invoking the handler may deadlock, it returns `SQLITE_BUSY` or `SQLITE_IOERR_BLOCKED` directly. Interrupts are connection-wide for currently running statements and can automatically roll back an explicit transaction for interrupted writes.

The VFS control flow is layered. SQLite calls `sqlite3_vfs.xOpen()` to populate a `sqlite3_file`, then calls the file's `sqlite3_io_methods` for reads, writes, locks, shared memory, syncs, and file controls. File open flags distinguish main databases, journals, temp databases, WAL files, subjournals, and other storage roles. Short reads must zero-fill unread bytes, and lock transitions must respect SQLite's shared/reserved/pending/exclusive lock model.

Initialization and configuration are phase-sensitive. `sqlite3_config()` is valid before `sqlite3_initialize()` or after `sqlite3_shutdown()`; using it while initialized generally returns `SQLITE_MISUSE`. `sqlite3_db_config()` is intended immediately after open. Allocator and mutex vtables are copied into SQLite during configuration and then participate in all later memory and synchronization paths.

Extension callbacks are installed per connection except for automatic extensions. Function callbacks read arguments through protected `sqlite3_value` objects and write results through `sqlite3_result_*`. Aggregate callbacks allocate per-aggregate state with `sqlite3_aggregate_context()`. Collations and virtual table modules must remain stable while registered.

Virtual table query planning flows from SQLite into `xBestIndex()`, which receives constraints and order terms, marks which constraints should become `xFilter()` arguments, optionally supplies an index string to be freed by `sqlite3_free()`, and estimates cost/order satisfaction. Runtime scanning then uses `xOpen()`, `xFilter()`, `xNext()`, `xEof()`, `xColumn()`, and `xRowid()`.

Incremental BLOB flow is: open a handle to one row/column, use `sqlite3_blob_bytes()` to find fixed size, read/write offsets within that size, optionally reopen on another row, and close. Row updates/deletes or conflict side effects expire the handle, causing later reads/writes to return `SQLITE_ABORT`.

## State And Persistence Behavior

Persistent database state is mediated by connections, prepared statements, BLOB handles, VFS files, journals/WAL/shared memory, and transactions. `sqlite3_close()` rolls back an open transaction. `sqlite3_blob_close()` may commit an autocommit transaction if no other statements or BLOBs are pending, and I/O errors can surface at close because cached BLOB writes may flush then.

Connection-local state includes last-insert rowid, direct change counters, total change counters, autocommit mode, busy handler, authorizer, trace/profile/progress callbacks, commit/rollback/update hooks, registered functions, collations, modules, extension-loading state, lookaside memory, and prepared statement lists. Several APIs warn that concurrent use of the same connection can make returned values undefined unless the caller serializes with `sqlite3_db_mutex()`.

Process-global state includes initialization status, default VFS, VFS registry, global threading mode, memory allocator, mutex implementation, scratch/pagecache/heap configuration, soft heap limit, PRNG state, automatic extensions, shared-cache default for subsequently opened connections, the error-log callback, runtime status counters, and `sqlite3_temp_directory`. `sqlite3_temp_directory` is explicitly unsafe to mutate concurrently and may be freed by the temp-store-directory pragma if it points to SQLite-allocated memory.

VFS implementations persist state in subclasses of `sqlite3_file` and in their own registered `sqlite3_vfs` object. Registered VFS objects are linked internally by SQLite through `pNext`; applications and VFS implementations should not mutate `pNext` or other fields after registration.

Virtual table implementations persist per-table state in subclasses of `sqlite3_vtab` and per-scan state in subclasses of `sqlite3_vtab_cursor`. Error messages from virtual table methods must be allocated with `sqlite3_mprintf()` and are freed by SQLite after delivery.

Function, collation, and module registrations persist until overwritten or connection close. Destructor behavior is API-specific: `sqlite3_create_function_v2()` and `sqlite3_create_module_v2()` invoke destructors on failure, but `sqlite3_create_collation_v2()` does not invoke `xDestroy` if registration fails.

The FoundationDB codec hook stores codec callbacks and `pCodec` state on a Btree pager. Because encryption key APIs are omitted by `SQLITE_HAS_CODEC_NO_ENCRYPTION`, this chunk suggests local use of codec plumbing without exposing upstream SEE-style database encryption control to ordinary clients.

## Dependencies And Integration Points

The header depends only on `<stdarg.h>` in this range and uses C linkage guards for C++ consumers. Most declarations are controlled by compile-time feature macros such as `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_DEPRECATED`, `SQLITE_HAS_CODEC`, `SQLITE_HAS_CODEC_NO_ENCRYPTION`, `SQLITE_ENABLE_CEROD`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_THREADSAFE`, `SQLITE_MUTEX_APPDEF`, and `NDEBUG`.

The main integration boundary is the SQLite ABI itself. Code in the FoundationDB repository can include this header to compile against SQLite's public API, but any dependency on declarations outside this file is, by the header's own contract, non-public and unstable.

The storage boundary is the VFS API. FoundationDB-specific or platform-specific file backends integrate by implementing `sqlite3_vfs` and `sqlite3_io_methods`, including the local zero-copy read extension. WAL support depends on the shared-memory methods in `sqlite3_io_methods` version 2.

The extension boundary includes application-defined SQL functions, aggregates, collations, authorizers, progress handlers, loadable/static extensions, and virtual table modules. These callbacks must respect reentrancy restrictions: many may not modify or close the invoking connection, reset/finalize the active statement, or call SQLite in ways that reenter non-reentrant logging paths.

The memory and synchronization boundary lets embedders replace allocators, page caches, mutexes, and logging before initialization. This is useful for embedded systems and fault-injection tests, but it makes initialization order and ABI-compatible structure layout important.

The codec boundary is an internal-adjacent integration point. `Btree`, `Pgno`, and `sqlite3BtreePagerSetCodec()` expose pager codec installation despite Btree normally being internal. That is likely consumed by FoundationDB's SQLite storage adaptation rather than ordinary SQLite applications.

## Risks And Edge Cases

The file is a public ABI contract, so structure layout changes are high risk. The local addition of `xReadZeroCopy()` and `xReleaseZeroCopy()` to `sqlite3_io_methods` can break assumptions made by code expecting upstream SQLite 3.7.6 layout, especially custom VFS modules compiled with a different header.

Header/library mismatch is a concrete risk. The header encourages asserting runtime version/source-id equality with compile-time macros. Mismatches would be especially dangerous here because of local codec and zero-copy declarations.

VFS correctness is critical for durability. The comments call out several corruption risks: short reads must zero-fill, sync flags must be honored according to storage guarantees, lock levels must transition correctly, and file-control opcodes below 100 are reserved for SQLite. Device-characteristic flags such as atomic write and safe append directly influence journaling assumptions.

Threading mode is subtle. `sqlite3_threadsafe()` reports compile-time mutex inclusion only, while runtime mode can be changed before initialization and individual connections can use no/full mutex flags. Many connection, statement, callback, column, metadata, and hook APIs have undefined behavior when used concurrently on the same object without proper serialization.

Ownership rules are easy to violate. Error messages from `sqlite3_exec()`, `sqlite3_get_table()` result tables, `sqlite3_mprintf()` strings, extension error messages, virtual table `zErrMsg`, bound/result buffer destructors, and collation/module/function destructors all have different lifetime rules. Misusing `SQLITE_STATIC` or `SQLITE_TRANSIENT` can cause use-after-free or excess copying.

Prepared statement and column APIs have narrow valid windows. Column access is only defined after `sqlite3_step()` returns `SQLITE_ROW`; type conversions can invalidate previous pointers; `sqlite3_finalize()` must be called for every statement before close; and use-after-finalize is undefined.

Callback reentrancy is constrained. Busy handlers, authorizers, progress callbacks, commit/rollback/update hooks, function callbacks, and log callbacks document operations that must not modify or close the invoking connection. Violating those rules can lead to undefined behavior or deadlocks.

Extension loading is a security-sensitive surface and is off by default. Applications that evaluate untrusted SQL need explicit controls around `sqlite3_enable_load_extension()`, authorizers, limits, and database-size pragmas.

Virtual table constraints require mathematical consistency. Collations must be transitive and stable; virtual table `xBestIndex()` must correctly describe constraints it handles; and `idxStr` ownership must match `needToFreeIdxStr`.

Incremental BLOB handles can expire if the row changes. Writes before expiration are not automatically rolled back just because the handle later expires, which matters for transaction semantics and error recovery.

The chunk boundary is a minor research risk. It ends immediately after the opening sentence of the `sqlite3_db_status` section, so detailed per-connection status counters and later APIs should not be inferred from this document.

## Test Signals

Useful tests for this API surface should include:

- Header/library identity checks using `sqlite3_libversion_number()`, `sqlite3_sourceid()`, and compile-time macros.
- Open/close lifecycle tests that verify `SQLITE_BUSY` on close with unfinalized statements or open BLOBs, and rollback on close with active transactions.
- Statement lifecycle tests for prepare v2 reprepare behavior, bind/reset/clear semantics, column pointer invalidation, and finalize/reset error propagation.
- Result-code tests with extended result codes enabled and disabled.
- VFS conformance tests for lock transitions, short-read zero filling, sync flag handling, xFileControl opcodes, WAL shared-memory methods, and the FoundationDB zero-copy methods.
- Codec integration tests that confirm `sqlite3BtreePagerSetCodec()` installs callbacks without exposing `sqlite3_key()`/`sqlite3_rekey()` when `SQLITE_HAS_CODEC_NO_ENCRYPTION` is defined.
- Allocator, lookaside, scratch/pagecache, soft-heap-limit, status-counter, and OOM injection tests through `sqlite3_config()`, `sqlite3_db_config()`, `sqlite3_status()`, and `sqlite3_test_control()`.
- Mutex/threading tests for single-thread, multithread, serialized, per-connection `SQLITE_OPEN_NOMUTEX`/`SQLITE_OPEN_FULLMUTEX`, and `sqlite3_db_mutex()` behavior.
- Callback tests for authorizer decisions, busy timeout, interrupt handling, trace/profile/progress hooks, commit rollback conversion, update hook omissions, and reentrancy restrictions.
- Extension tests for SQL functions, aggregate contexts, auxdata destructor timing, collation destructor failure behavior, virtual table planning contracts, and extension loading disabled-by-default behavior.
- Incremental BLOB tests for fixed-size reads/writes, bounds failures, readonly handles, reopen behavior, expiration after row mutation, and error reporting on close.
