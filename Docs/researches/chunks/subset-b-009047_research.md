# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h lines 1-5212

## Chunk Scope

This chunk covers the first 5,212 lines of the bundled SQLite public C API header used under WiredTiger test third-party sources. The file identifies itself as the authoritative API surface for SQLite clients and as generated from `sqlite.h.in`. This chunk starts at the include guard and version metadata and ends in the opening documentation for `sqlite3_data_count()`, immediately after the `sqlite3_step()` declaration.

## Purpose

The covered range defines the public ABI and behavioral contracts for core SQLite library use:

- compile/runtime version checks, compile-option diagnostics, and thread-safety discovery;
- opaque handle types for database connections, statements, values, contexts, VFS files, mutexes, and extension API tables;
- primary database lifecycle calls, including initialization, shutdown, open, close, and one-shot execution;
- result-code, open-flag, device-capability, lock-level, sync, file-control, configuration, DB configuration, authorizer, trace, prepare, bind, and limit constants;
- VFS and file I/O method tables that allow SQLite to run on custom storage or OS layers;
- memory allocation and formatted string APIs that callers must pair with SQLite's allocator;
- prepared-statement construction, SQL text access, parameter binding, result-column metadata, and statement stepping.

As a header, this chunk does not implement behavior itself. Its comments are part of the public API contract and are used by SQLite to generate official C API documentation.

## Important APIs, Types, and Constants

### Linkage, Version, and Diagnostics

- `SQLITE_EXTERN`, `SQLITE_API`, `SQLITE_CDECL`, `SQLITE_APICALL`, `SQLITE_STDCALL`, `SQLITE_CALLBACK`, and `SQLITE_SYSAPI` parameterize linkage and calling conventions.
- `SQLITE_DEPRECATED` and `SQLITE_EXPERIMENTAL` are no-op markers for API stability classification.
- Version identity is fixed in this header as `SQLITE_VERSION "3.50.4"`, `SQLITE_VERSION_NUMBER 3050004`, and a Fossil-derived `SQLITE_SOURCE_ID`.
- `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose runtime version identity. The comments recommend asserting that runtime values match the compile-time macros.
- `sqlite3_compileoption_used()` and `sqlite3_compileoption_get()` expose compile-time build options unless `SQLITE_OMIT_COMPILEOPTION_DIAGS` replaces them with inert macros.
- `sqlite3_threadsafe()` reports the compile-time mutex setting only, not runtime changes made through `sqlite3_config()`.

### Core Opaque Handles and Integer Types

- `typedef struct sqlite3 sqlite3;` is the database connection handle.
- `sqlite_int64`, `sqlite_uint64`, `sqlite3_int64`, and `sqlite3_uint64` normalize 64-bit integer types across compilers.
- `typedef struct sqlite3_stmt sqlite3_stmt;` is the prepared-statement handle.
- `typedef struct sqlite3_value sqlite3_value;` represents dynamically typed SQL values. The comments distinguish protected and unprotected values by mutex ownership.
- `typedef struct sqlite3_context sqlite3_context;` is passed to application-defined SQL functions.
- `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs` define the OS/VFS abstraction.

### Connection and Execution APIs

- `sqlite3_close()` and `sqlite3_close_v2()` destroy or eventually destroy a connection. `sqlite3_close()` returns `SQLITE_BUSY` if statements, BLOBs, or backups are still outstanding; `sqlite3_close_v2()` allows a zombie connection that is freed later.
- `sqlite3_exec()` wraps prepare, step, and finalize for semicolon-separated UTF-8 SQL and invokes an optional row callback.
- `sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct database connections. `sqlite3_open_v2()` accepts open flags and an optional VFS name.
- `sqlite3_extended_result_codes()` enables extended result-code reporting for a connection.
- `sqlite3_complete()` and `sqlite3_complete16()` test whether a SQL string appears complete for command-line input.
- `sqlite3_interrupt()` and `sqlite3_is_interrupted()` coordinate cancellation of running statements on a connection.

### Result Codes and Flags

The chunk defines the primary SQLite result-code namespace:

- success and row lifecycle codes: `SQLITE_OK`, `SQLITE_ROW`, `SQLITE_DONE`;
- general failures: `SQLITE_ERROR`, `SQLITE_INTERNAL`, `SQLITE_PERM`, `SQLITE_ABORT`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_NOMEM`, `SQLITE_READONLY`, `SQLITE_INTERRUPT`, `SQLITE_IOERR`, `SQLITE_CORRUPT`, `SQLITE_FULL`, `SQLITE_CANTOPEN`, `SQLITE_SCHEMA`, `SQLITE_CONSTRAINT`, `SQLITE_MISUSE`, and related values;
- extended codes built by OR-ing a primary code with a shifted detail, including `SQLITE_IOERR_*`, `SQLITE_LOCKED_*`, `SQLITE_BUSY_*`, `SQLITE_CANTOPEN_*`, `SQLITE_CORRUPT_*`, `SQLITE_READONLY_*`, `SQLITE_CONSTRAINT_*`, `SQLITE_NOTICE_*`, `SQLITE_WARNING_AUTOINDEX`, `SQLITE_AUTH_USER`, `SQLITE_OK_LOAD_PERMANENTLY`, and `SQLITE_OK_SYMLINK`.

Open flags cover both public `sqlite3_open_v2()` bits and VFS-only bits:

- public open bits include `SQLITE_OPEN_READONLY`, `SQLITE_OPEN_READWRITE`, `SQLITE_OPEN_CREATE`, `SQLITE_OPEN_URI`, `SQLITE_OPEN_MEMORY`, `SQLITE_OPEN_NOMUTEX`, `SQLITE_OPEN_FULLMUTEX`, `SQLITE_OPEN_SHAREDCACHE`, `SQLITE_OPEN_PRIVATECACHE`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`;
- VFS-only bits include journal/temp/transient object kinds, `SQLITE_OPEN_DELETEONCLOSE`, `SQLITE_OPEN_EXCLUSIVE`, `SQLITE_OPEN_WAL`, and legacy `SQLITE_OPEN_MASTER_JOURNAL`.

Device, lock, sync, shared-memory, and access constants include:

- `SQLITE_IOCAP_*` for atomicity, safe append, sequential writes, powersafe overwrite, immutable media, batch atomic writes, and subpage reads;
- `SQLITE_LOCK_NONE`, `SQLITE_LOCK_SHARED`, `SQLITE_LOCK_RESERVED`, `SQLITE_LOCK_PENDING`, and `SQLITE_LOCK_EXCLUSIVE`;
- `SQLITE_SYNC_NORMAL`, `SQLITE_SYNC_FULL`, and `SQLITE_SYNC_DATAONLY`;
- `SQLITE_ACCESS_EXISTS`, `SQLITE_ACCESS_READWRITE`, and `SQLITE_ACCESS_READ`;
- `SQLITE_SHM_UNLOCK`, `SQLITE_SHM_LOCK`, `SQLITE_SHM_SHARED`, `SQLITE_SHM_EXCLUSIVE`, and `SQLITE_SHM_NLOCK`.

### VFS and File I/O Interfaces

`sqlite3_file` contains a pointer to an `sqlite3_io_methods` table. The method table defines the file-handle operations SQLite expects:

- version 1: close, read, write, truncate, sync, file size, lock/unlock, reserved-lock check, file-control, sector size, and device characteristics;
- version 2: shared-memory map, lock, barrier, and unmap methods used by WAL;
- version 3: memory-map fetch and unfetch methods.

The comments specify critical invariants. A VFS must set `sqlite3_file.pMethods` to either a valid method table or `NULL`, including on failed opens. Short reads returning `SQLITE_IOERR_SHORT_READ` must zero-fill unread bytes to avoid corruption. Lock calls only upgrade or downgrade according to the documented lock-order model.

`SQLITE_FCNTL_*` opcodes define the generic file-control channel shared by `sqlite3_file_control()` and `xFileControl()`. This range includes opcodes for lock-state debugging, file-size hints and limits, file and journal pointers, sync and commit-phase signals, Windows retry/handle controls, WAL persistence and blocking, powersafe-overwrite control, pragma interception, busy-handler access, temp filename generation, mmap size, VFS stack discovery, batch atomic write begin/commit/rollback, lock timeout, data version, checkpoint start/done notifications, external-reader detection, checksum VFS, reset cache, null I/O, and block-on-connect behavior.

`sqlite3_vfs` defines the virtual filesystem object. Version 1 fields cover file open/delete/access/full-pathname, dynamic library operations, randomness, sleep, current time, and last error. Version 2 adds `xCurrentTimeInt64()`. Version 3 adds system-call override/lookup/enumeration hooks used by some VFSes for testing.

### Initialization and Configuration

- `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, and `sqlite3_os_end()` define process-level setup and teardown. Applications should call only initialize/shutdown; OS init/end are called internally or supplied for custom OS builds.
- `sqlite3_config()` controls global configuration and is generally valid only before initialization or after shutdown, except for documented anytime options.
- `sqlite3_db_config()` controls per-connection settings.
- `sqlite3_mem_methods` defines a replacement allocator with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`.

Global `SQLITE_CONFIG_*` options in this chunk include threading modes, allocator/memory status/page cache/static heap/mutex/lookaside/page-cache replacement/logging/URI/covering-index scan/SQL log/mmap/Windows heap/page-cache header size/sorter PMA/statement journal spill/small malloc/sorter reference size/memory DB max size/rowid-in-view options.

Per-connection `SQLITE_DBCONFIG_*` options include main DB name, lookaside, foreign keys, triggers, FTS3 tokenizer, load extension, no checkpoint on close, QPSG, trigger EQP, reset database, defensive mode, writable schema, legacy alter table and file format, double-quoted string handling, views, trusted schema, statement scan status, reverse scan order, ATTACH create/write controls, SQL comments, and `SQLITE_DBCONFIG_MAX`.

### Connection State APIs

- `sqlite3_last_insert_rowid()` and `sqlite3_set_last_insert_rowid()` expose and override the most recent rowid state for a connection.
- `sqlite3_changes()`/`sqlite3_changes64()` report rows modified by the most recent qualifying statement, excluding triggers, foreign-key side effects, REPLACE side effects, and view changes intercepted by INSTEAD OF triggers.
- `sqlite3_total_changes()`/`sqlite3_total_changes64()` report cumulative direct and trigger changes since the connection opened, with caveats for foreign-key actions and REPLACE.
- `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, and `sqlite3_setlk_timeout()` configure lock contention behavior. `SQLITE_SETLK_BLOCK_ON_CONNECT` controls blocking connection behavior for WAL-mode blocking locks in supported builds.

### Utility, Memory, and Authorization APIs

- `sqlite3_get_table()` and `sqlite3_free_table()` are legacy result-table helpers built around `sqlite3_exec()`.
- `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, and `sqlite3_vsnprintf()` provide SQLite-managed formatting utilities.
- `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_realloc()`, `sqlite3_realloc64()`, `sqlite3_free()`, and `sqlite3_msize()` expose SQLite allocator calls. Returned memory must be managed through SQLite, not the system allocator.
- `sqlite3_memory_used()` and `sqlite3_memory_highwater()` expose allocator statistics when memory status is enabled.
- `sqlite3_randomness()` exposes the internal PRNG and seeds from the default VFS randomness method when needed.
- `sqlite3_set_authorizer()` registers a compile-time SQL authorization callback. `SQLITE_DENY`, `SQLITE_IGNORE`, and many `SQLITE_*` action codes define callback behavior for schema changes, DML, PRAGMA, reads, transactions, attach/detach, virtual tables, functions, savepoints, and recursion.

### Trace, Progress, and Open/URI APIs

- Deprecated `sqlite3_trace()` and `sqlite3_profile()` are retained for compatibility.
- `SQLITE_TRACE_STMT`, `SQLITE_TRACE_PROFILE`, `SQLITE_TRACE_ROW`, and `SQLITE_TRACE_CLOSE` classify `sqlite3_trace_v2()` callbacks.
- `sqlite3_trace_v2()` registers the preferred tracing hook for one connection; only one trace callback may be active per connection.
- `sqlite3_progress_handler()` registers a periodic callback during long `sqlite3_step()` or prepare activity; a nonzero return interrupts the operation.
- URI helpers `sqlite3_uri_parameter()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_uri_key()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_database_file_object()`, `sqlite3_create_filename()`, and `sqlite3_free_filename()` support VFS and VFS-shim interpretation of filenames and associated journal/WAL names.
- Error APIs `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_errstr()`, and `sqlite3_error_offset()` report the latest connection error, error text, or SQL token offset.

### Prepared Statements, Limits, Binding, and Columns

Prepared statement lifecycle in this range is:

1. construct using `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, or `sqlite3_prepare16_v3()`;
2. bind values with `sqlite3_bind_*()`;
3. run with `sqlite3_step()`;
4. reset with `sqlite3_reset()` in later header sections, then optionally rebind and step again;
5. destroy with `sqlite3_finalize()` in later header sections.

This chunk defines `sqlite3_limit()` plus `SQLITE_LIMIT_*` categories for string/blob/row length, SQL length, column count, expression depth, compound select terms, VDBE op count, function arguments, attached DB count, LIKE/GLOB pattern length, variable number, trigger depth, and worker threads.

Prepare flags include `SQLITE_PREPARE_PERSISTENT`, `SQLITE_PREPARE_NORMALIZE`, `SQLITE_PREPARE_NO_VTAB`, and `SQLITE_PREPARE_DONT_LOG`.

Statement-inspection APIs include `sqlite3_sql()`, `sqlite3_expanded_sql()`, optional `sqlite3_normalized_sql()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, and `sqlite3_stmt_busy()`.

Binding APIs include blob, blob64, double, int, int64, null, text, text16, text64, value, pointer, zeroblob, and zeroblob64 variants. Parameter metadata helpers are `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3_bind_parameter_index()`, and `sqlite3_clear_bindings()`.

Column/result metadata covered before the chunk boundary includes `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_name16()`, the optional origin metadata family `sqlite3_column_database_name*`, `sqlite3_column_table_name*`, `sqlite3_column_origin_name*`, and declared-type APIs `sqlite3_column_decltype()` and `sqlite3_column_decltype16()`.

The chunk ends after `sqlite3_step()` and at the start of `sqlite3_data_count()` documentation, so row-value extraction APIs are expected to continue in the next chunk.

## Control Flow and Lifecycle Contracts

The most important control flows are API lifecycles rather than in-file executable control flow:

- Library lifecycle: optional `sqlite3_initialize()` establishes static resources and OS/VFS setup; `sqlite3_shutdown()` deallocates resources after all connections and other SQLite objects are gone. Many APIs auto-initialize unless `SQLITE_OMIT_AUTOINIT` is used.
- Connection lifecycle: `sqlite3_open*()` creates a connection, `sqlite3_db_config()` and other connection methods mutate connection settings, and `sqlite3_close()`/`sqlite3_close_v2()` release it. Open transactions are rolled back on connection destruction.
- SQL execution via `sqlite3_exec()`: prepare each statement, step rows, call user callback for each row, stop on callback abort or error, then finalize. Error messages returned through the output pointer must be released with `sqlite3_free()`.
- Prepared statement lifecycle: prepare creates a bytecode program; bind attaches parameter values; step returns `SQLITE_ROW`, `SQLITE_DONE`, `SQLITE_BUSY`, `SQLITE_ERROR`, `SQLITE_MISUSE`, or extended result codes; reset/finalize handling is described across this and later chunks.
- VFS lifecycle: SQLite calls `sqlite3_vfs.xOpen()` to populate a caller-allocated `sqlite3_file`; thereafter core code dispatches through `sqlite3_io_methods` for I/O, locking, sync, WAL shared-memory, mmap, and file-control operations.
- Busy handling: lock contention may invoke a connection-specific busy callback repeatedly, but SQLite may bypass it to avoid deadlock.
- Authorization and tracing: authorizer callbacks run during prepare/reprepare, while trace/progress callbacks run around statement execution and, in recent versions, sometimes during prepare.

## State and Persistence Behavior

This header chunk names several state layers:

- process-global state: initialization status, global threading mode, global allocator/mutex/page-cache/log/URI/mmap settings, compile options, PRNG seed, memory statistics, registered VFS chain, and optional system-call override tables inside VFS implementations;
- connection state: open database handles, attached schema names, busy handler, authorizer, trace/progress callbacks, last-insert rowid, change counters, interrupt flag, extended result-code mode, DB config flags, connection-specific limits, and error state;
- statement state: saved SQL text for v2/v3 prepare APIs, current bindings, busy/active state, explain mode, result-column metadata, and automatic reprepare behavior;
- file-system persistence: VFS device characteristics, lock state, WAL/journal file handling, persistent WAL mode, checkpoint behavior, mmap size, atomic-write controls, powersafe-overwrite settings, and URI-driven read/write/memory/cache/immutable/nolock modes.

Several contracts are persistence-critical:

- failed or short VFS reads must obey zero-fill requirements to avoid database corruption;
- file locking flags and busy/setlk behavior coordinate interprocess consistency;
- `immutable=1` disables locking and change detection and is only correct for truly immutable files;
- `nolock=1` can corrupt databases when multiple writers access the same file;
- `SQLITE_DBCONFIG_RESET_DATABASE` is intentionally multi-step and destructive;
- close-on-last-WAL-connection may checkpoint and delete WAL files unless disabled or changed by related controls;
- `SQLITE_FCNTL_DATA_VERSION` and `PRAGMA data_version` integrate with cross-connection change detection.

## Dependencies and Integration Points

- The only direct C standard include in this slice is `<stdarg.h>` for `va_list`.
- The header is C++ compatible through `extern "C"`.
- Most APIs depend on definitions implemented in the SQLite library or amalgamation source, not in this header.
- WiredTiger test code can include this header to compile against the bundled SQLite API without depending on a system SQLite install.
- Custom storage integration happens through `sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, `SQLITE_OPEN_*`, `SQLITE_IOCAP_*`, `SQLITE_FCNTL_*`, and URI helper APIs.
- Extension integration is signaled by `sqlite3_api_routines`, pointer binding, authorizer/action codes, trace APIs, SQL function context/value types, and the explicit load-extension DB config option.
- Memory integration uses `sqlite3_mem_methods`, global allocator configuration, and SQLite-owned allocation/free APIs.
- Threading integration is controlled by compile-time `SQLITE_THREADSAFE`, global `SQLITE_CONFIG_*` threading modes, per-open mutex flags, protected/unprotected value rules, and documented per-connection threading hazards.

## Risks and Edge Cases

- Header/library mismatch is a concrete ABI risk; the comments recommend runtime assertions against `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, and `SQLITE_VERSION`.
- Many varargs APIs (`sqlite3_config()`, `sqlite3_db_config()`, formatting functions) rely on exact argument shapes implied by integer opcodes; wrong types are undefined behavior in C.
- `sqlite3_close_v2()` can leave zombie connections alive until statements/BLOBs/backups finish, which can hide lifecycle bugs in host-language bindings.
- `sqlite3_exec()` callback pointers and result strings are transient; retaining them after callback return is unsafe.
- `sqlite3_get_table()` result storage must be released with `sqlite3_free_table()`, not `sqlite3_free()`.
- `sqlite3_malloc()` memory must be released with SQLite allocation APIs. Passing foreign or already-freed pointers to `sqlite3_free()`, `sqlite3_realloc()`, or `sqlite3_msize()` is explicitly dangerous.
- Busy handlers, authorizers, progress handlers, and log callbacks have reentrancy restrictions and must not modify or close the invoking connection/statement.
- Shared-cache mode is discouraged and may be omitted from builds.
- URI parameters such as `immutable` and `nolock` trade correctness checks for performance or unusual filesystem support and can yield corruption or stale results if misused.
- Legacy prepare APIs produce less specific `sqlite3_step()` errors and are discouraged; v2/v3 APIs store SQL text and enable automatic reprepare.
- Binding APIs contain lifetime traps: `SQLITE_STATIC` requires caller storage to outlive the binding, `SQLITE_TRANSIENT` copies before return, and destructors are invoked under specific error/NULL/negative-length exceptions.
- Some APIs are conditional on compile options, including compile-option diagnostics, column metadata, statement scan status, normalization, setlk timeout, SQL logging, and memory statistics.
- Several APIs state undefined behavior for invalid handles, finalized statements, invalid filenames, concurrent same-connection access, incorrect encodings, negative blob lengths, and bad VFS method implementations.

## Test Signals

Useful tests or validation signals for code using this chunk include:

- assert runtime version APIs match the compile-time macros when linking the bundled library;
- verify `sqlite3_compileoption_used()`/`get()` behavior under builds with and without `SQLITE_OMIT_COMPILEOPTION_DIAGS`;
- exercise open modes, URI parameters, VFS selection, and error reporting through `sqlite3_open_v2()`;
- confirm custom VFS implementations fill `pMethods` correctly on success/failure, zero-fill short reads, implement lock transitions, and return expected `SQLITE_FCNTL_*` results;
- test WAL persistence/checkpoint/locking behaviors through `SQLITE_FCNTL_PERSIST_WAL`, `SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE`, busy timeout, and setlk timeout where enabled;
- check allocator replacement with `SQLITE_CONFIG_MALLOC` and memory statistics with `sqlite3_memory_used()`/`sqlite3_memory_highwater()`;
- validate authorizer, trace, and progress callbacks for correct invocation timing and non-reentrant behavior;
- run prepared-statement lifecycle tests covering prepare v2/v3, binding all supported value kinds, stepping to `SQLITE_ROW`/`SQLITE_DONE`, automatic reprepare on schema change, and error-code differences from legacy prepare;
- test parameter metadata, column metadata, declared type, and statement SQL retrieval APIs under UTF-8 and UTF-16 prepares;
- verify destructive or security-sensitive DB config settings, especially defensive mode, trusted schema, reset database, load extension, writable schema, and ATTACH controls.

## Cross-Chunk Notes

- This chunk is the beginning of a much larger header. APIs referenced here but declared later include reset/finalize, column value extraction, BLOB I/O, backup, virtual table, extension, serialization, and many other SQLite interfaces.
- The line 5,212 boundary cuts into the `sqlite3_data_count()` documentation. The declaration and related column-access APIs should be researched in the following chunk before producing the merged per-file report.
