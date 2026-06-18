# sources/storage-engines/sqlite/src/sqlite.h.in lines 1-5232

## Chunk Scope

This chunk covers the first 5,232 lines of `sources/storage-engines/sqlite/src/sqlite.h.in`, the template header used by SQLite's build to produce the public `sqlite3.h` API. It begins with linkage/calling-convention macros and version placeholders, then defines the core C API up through prepared-statement binding and result-column metadata. The range ends mid-comment in the "Declared Datatype Of A Query Result" section, so the actual `sqlite3_column_decltype()` declarations and any later column/value/step/finalize APIs are cross-chunk continuations.

## Purpose

`sqlite.h.in` is the authoritative public API contract for client programs embedding or linking SQLite. The comments are not incidental: they drive official C API documentation and specify ownership, threading, lifetime, persistence, and compatibility behavior that external code depends on. The build system substitutes version/source-control placeholders such as `--VERS--`, `--VERSION-NUMBER--`, and `--SOURCE-ID--` and emits the installed header as `sqlite3.h`.

Within this chunk the header exposes:

- Process/library metadata and diagnostics.
- Opaque handles for connections, statements, values, contexts, mutexes, VFS files, VFS objects, and extension thunks.
- Database connection construction/destruction, one-shot execution, error reporting, busy/progress/trace/authorizer hooks, connection configuration, and statement preparation.
- VFS and file I/O interfaces used by SQLite's pager/WAL/journal layers to persist database state.
- Core result, open, synchronization, locking, file-control, configuration, authorizer, trace, prepare, bind, and column metadata constants.

## Public Surface In This Chunk

### Header/linkage and version APIs

The opening block guards `SQLITE3_H`, provides C++ `extern "C"` linkage, and defines overrideable interface macros: `SQLITE_EXTERN`, `SQLITE_API`, `SQLITE_CDECL`, `SQLITE_APICALL`, `SQLITE_STDCALL`, `SQLITE_CALLBACK`, and `SQLITE_SYSAPI`. `SQLITE_DEPRECATED` and `SQLITE_EXPERIMENTAL` are retained as no-op markers to preserve source compatibility without forcing compiler warnings.

Version state is split between compile-time macros and runtime functions:

- `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, `SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, and `SQLITE_SCM_DATETIME` are generated at build time.
- `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose the linked library's identity.
- `sqlite3_compileoption_used()` and `sqlite3_compileoption_get()` are omitted or stubbed when `SQLITE_OMIT_COMPILEOPTION_DIAGS` is set.
- `sqlite3_threadsafe()` reports compile-time mutex support only, not runtime mode changes made with `sqlite3_config()`.

Risk signal: callers commonly assert that runtime and header versions match. Mismatched `sqlite3.h` and library binaries can silently alter ABI assumptions, result-code availability, and feature macros.

### Opaque handles and scalar types

The chunk introduces opaque `typedef struct` handles for `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_mutex`, `sqlite3_api_routines`, `sqlite3_vfs`, and `sqlite3_file`. It defines cross-platform signed/unsigned 64-bit integer aliases `sqlite_int64`, `sqlite_uint64`, `sqlite3_int64`, and `sqlite3_uint64`, with `SQLITE_INT64_TYPE`/`SQLITE_UINT64_TYPE` overrides and compiler-specific fallbacks. `SQLITE_OMIT_FLOATING_POINT` can replace `double` with `sqlite3_int64`.

These declarations keep object layouts private except for extension interfaces that must be subclassed or filled by embedders, especially `sqlite3_file`, `sqlite3_io_methods`, `sqlite3_vfs`, and `sqlite3_mem_methods`.

### Connection lifecycle and one-step execution

`sqlite3_close()` and `sqlite3_close_v2()` are destructors for `sqlite3` connections. The older close API returns `SQLITE_BUSY` if statements, BLOB handles, or backups remain open; `sqlite3_close_v2()` marks the connection as a zombie and defers deallocation until dependent objects are released. Any open transaction is automatically rolled back when the connection is destroyed.

`sqlite3_exec()` is the convenience wrapper around prepare/step/finalize. It accepts one or more UTF-8 SQL statements, invokes an optional row callback with result text and column names, stops on the first SQL error or callback abort, and returns an error message allocated by `sqlite3_malloc()` when requested. The caller must free that error string with `sqlite3_free()`.

Risk signals:

- Closing order is observable. `sqlite3_close_v2()` is suitable for garbage-collected host bindings, but wrappers must avoid using the zombie connection.
- `sqlite3_exec()` callbacks receive transient pointers; retaining them after callback return is invalid.
- If a callback returns non-zero, execution aborts with `SQLITE_ABORT` and remaining statements are skipped.

### Result, extended result, open, lock, sync, and I/O capability constants

The header defines primary result codes (`SQLITE_OK`, `SQLITE_ERROR`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_ROW`, `SQLITE_DONE`, etc.) and a large matrix of extended result codes created by OR-ing primary codes with subcodes shifted by 8 bits. Important families include `SQLITE_IOERR_*`, `SQLITE_LOCKED_*`, `SQLITE_BUSY_*`, `SQLITE_CANTOPEN_*`, `SQLITE_CORRUPT_*`, `SQLITE_READONLY_*`, `SQLITE_CONSTRAINT_*`, `SQLITE_NOTICE_*`, and `SQLITE_WARNING_AUTOINDEX`.

Open flags are shared by `sqlite3_open_v2()` and VFS `xOpen()`, but the header explicitly separates flags legal for application opens from flags reserved for the VFS layer. Application-facing flags include `SQLITE_OPEN_READONLY`, `SQLITE_OPEN_READWRITE`, `SQLITE_OPEN_CREATE`, `SQLITE_OPEN_URI`, `SQLITE_OPEN_MEMORY`, `SQLITE_OPEN_NOMUTEX`, `SQLITE_OPEN_FULLMUTEX`, `SQLITE_OPEN_SHAREDCACHE`, `SQLITE_OPEN_PRIVATECACHE`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`. VFS object-type flags include `SQLITE_OPEN_MAIN_DB`, journal/temp/subjournal/super-journal flags, and `SQLITE_OPEN_WAL`.

The chunk also defines:

- Storage capability bits such as `SQLITE_IOCAP_ATOMIC*`, `SQLITE_IOCAP_SAFE_APPEND`, `SQLITE_IOCAP_SEQUENTIAL`, `SQLITE_IOCAP_POWERSAFE_OVERWRITE`, `SQLITE_IOCAP_IMMUTABLE`, `SQLITE_IOCAP_BATCH_ATOMIC`, and `SQLITE_IOCAP_SUBPAGE_READ`.
- Lock levels from `SQLITE_LOCK_NONE` to `SQLITE_LOCK_EXCLUSIVE`.
- Sync flags `SQLITE_SYNC_NORMAL`, `SQLITE_SYNC_FULL`, and `SQLITE_SYNC_DATAONLY`.

Persistence risk: incorrect VFS capability reporting can corrupt databases. For example, failing to zero-fill short reads, overstating atomicity, or incorrectly disabling locks changes pager and WAL safety assumptions.

### VFS file methods and file-control opcodes

`struct sqlite3_file` contains only `pMethods`, allowing each VFS to subclass it with platform-specific file state. `struct sqlite3_io_methods` is the per-file method table:

- Version 1 methods: `xClose`, `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`, `xLock`, `xUnlock`, `xCheckReservedLock`, `xFileControl`, `xSectorSize`, and `xDeviceCharacteristics`.
- Version 2 WAL/shared-memory methods: `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap`.
- Version 3 memory-map methods: `xFetch` and `xUnfetch`.

The file-control section documents opcodes through `SQLITE_FCNTL_FILESTAT` and legacy aliases. It covers lock inspection, size hints and size limits, chunk sizing, file/journal pointers, sync and commit-phase notifications, Windows AV retry policy, persistent WAL, powersafe-overwrite toggling, VFS stack names/pointers, pragma interception, busy-handler access for custom VFSes, temp filename generation, mmap size control, tracing, file-moved detection, native handle access, null I/O, WAL blocking, zipvfs/RBU hooks, batch atomic write begin/commit/rollback, lock timeouts, WAL checkpoint start/done signals, external reader detection, checksum VFS support, cache reset, and file statistics.

State/persistence behavior:

- VFS `xOpen()` must set `sqlite3_file.pMethods` to either a valid method table or NULL even on failure; otherwise SQLite may call `xClose()` after a failed open.
- Journal and WAL file-control opcodes are part of transaction ordering and checkpoint coordination. Applications are warned not to issue internal opcodes such as `SQLITE_FCNTL_SYNC`, `SQLITE_FCNTL_COMMIT_PHASETWO`, or `SQLITE_FCNTL_WAL_BLOCK`.
- `SQLITE_FCNTL_PERSIST_WAL` changes whether WAL and shared-memory files remain after the last connection closes.
- Batch atomic write opcodes constrain which VFS calls SQLite may make between begin and commit/rollback.

Integration points: custom VFS implementations, VFS shims, WAL subsystem, pager, rollback journal, checkpoint code, `sqlite3_file_control()`, PRAGMA handling, zipvfs, RBU, checksum VFS, and diagnostic tooling.

### VFS object and filename helpers

`sqlite3_filename` is a `const char *` with SQLite-owned metadata attached for VFS use. `struct sqlite3_vfs` defines the registered OS interface:

- Identity/chain fields: `iVersion`, `szOsFile`, `mxPathname`, `pNext`, `zName`, `pAppData`.
- File and path methods: `xOpen`, `xDelete`, `xAccess`, `xFullPathname`.
- Dynamic loading: `xDlOpen`, `xDlError`, `xDlSym`, `xDlClose`.
- Misc OS services: `xRandomness`, `xSleep`, `xCurrentTime`, `xGetLastError`, `xCurrentTimeInt64`.
- Version 3 optional syscall override/testing hooks: `xSetSystemCall`, `xGetSystemCall`, `xNextSystemCall`.

VFS access flags (`SQLITE_ACCESS_EXISTS`, `SQLITE_ACCESS_READWRITE`, `SQLITE_ACCESS_READ`) and shared-memory lock flags (`SQLITE_SHM_UNLOCK`, `SQLITE_SHM_LOCK`, `SQLITE_SHM_SHARED`, `SQLITE_SHM_EXCLUSIVE`, `SQLITE_SHM_NLOCK`) define exact method arguments for lock coordination.

Filename helper APIs in the later open section include `sqlite3_uri_parameter()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_uri_key()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_database_file_object()`, `sqlite3_create_filename()`, and `sqlite3_free_filename()`. These are primarily for VFS and VFS shim implementations. Misusing arbitrary strings as `sqlite3_filename` values is undefined and likely a memory error.

### Library initialization and global configuration

`sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, and `sqlite3_os_end()` manage process-level SQLite state. Normal applications rely on auto-initialization, but `SQLITE_OMIT_AUTOINIT` builds require explicit initialization. `sqlite3_shutdown()` is not threadsafe and requires all connections/resources to be closed first.

`sqlite3_config()` changes global configuration, mostly before initialization or after shutdown. "Anytime" options documented in this chunk are limited and version-dependent. `sqlite3_db_config()` configures a single `sqlite3` connection.

`struct sqlite3_mem_methods` defines an embeddable allocator with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`. The surrounding configuration constants include:

- Threading modes: `SQLITE_CONFIG_SINGLETHREAD`, `MULTITHREAD`, `SERIALIZED`.
- Memory/allocator/page-cache controls: `MALLOC`, `GETMALLOC`, `PAGECACHE`, `HEAP`, `MEMSTATUS`, `PCACHE2`, `GETPCACHE2`, `PCACHE_HDRSZ`, `SMALL_MALLOC`, obsolete `SCRATCH`, `PCACHE`, and `GETPCACHE`.
- Mutex controls: `SQLITE_CONFIG_MUTEX`, `GETMUTEX`.
- Diagnostics/hooks: `SQLITE_CONFIG_LOG`, `SQLITE_CONFIG_SQLLOG`.
- URI/default behavior and optimizer/sorter/storage knobs: `URI`, `COVERING_INDEX_SCAN`, `MMAP_SIZE`, `WIN32_HEAPSIZE`, `PMASZ`, `STMTJRNL_SPILL`, `SORTERREF_SIZE`, `MEMDB_MAXSIZE`, `ROWID_IN_VIEW`.

Risks:

- Most `sqlite3_config()` options return `SQLITE_MISUSE` if called while initialized. Embedders need a clear startup phase.
- Custom allocators must satisfy SQLite's size, roundup, initialization, and thread-safety expectations or failures can manifest as memory corruption rather than clean errors.
- `SQLITE_CONFIG_LOG` callbacks are not reentrant and must not call SQLite APIs.

### Connection configuration constants

`SQLITE_DBCONFIG_*` options define connection-local switches for security, compatibility, planner behavior, attachment behavior, comments, loadable extension access, and display precision. This chunk includes constants from `SQLITE_DBCONFIG_MAINDBNAME` through `SQLITE_DBCONFIG_FP_DIGITS`, with `SQLITE_DBCONFIG_MAX` currently equal to the FP digits value.

Important behavioral groups:

- Security hardening: `DEFENSIVE`, `TRUSTED_SCHEMA`, `WRITABLE_SCHEMA`, `ENABLE_LOAD_EXTENSION`, `ENABLE_FTS3_TOKENIZER`, `ENABLE_ATTACH_CREATE`, `ENABLE_ATTACH_WRITE`, `ENABLE_COMMENTS`.
- SQL feature gates and compatibility: `ENABLE_FKEY`, `ENABLE_TRIGGER`, `ENABLE_VIEW`, `LEGACY_ALTER_TABLE`, `DQS_DML`, `DQS_DDL`, `LEGACY_FILE_FORMAT`, `RESET_DATABASE`.
- Planner/diagnostic behavior: `ENABLE_QPSG`, `TRIGGER_EQP`, `STMT_SCANSTATUS`, `REVERSE_SCANORDER`, `FP_DIGITS`.
- Storage lifecycle: `NO_CKPT_ON_CLOSE` affects WAL close-time checkpoint/delete behavior.
- Memory: `LOOKASIDE` sets per-connection lookaside memory.
- Naming: `MAINDBNAME` changes the schema name for the main database without copying the input string.

Risk signals:

- `RESET_DATABASE` is deliberately multi-step because it destructively resets even corrupt databases and abandons virtual tables without `xDestroy()`.
- `TRUSTED_SCHEMA` defaults to legacy-friendly behavior but should be disabled for untrusted databases to prevent unsafe functions/virtual tables inside schema objects.
- `MAINDBNAME` requires the caller-provided string to remain valid until close.

### Runtime state APIs on connections

This chunk declares connection methods for extended result codes, rowid/change counters, interruption, completeness checks, busy handling, setlk timeouts, convenience query tables, formatting, memory, randomness, authorizers, tracing, progress handlers, opening, URI filename inspection, error reporting, and manual error setting.

Notable APIs and behavior:

- `sqlite3_extended_result_codes()` toggles detailed error reporting per connection.
- `sqlite3_last_insert_rowid()` and `sqlite3_set_last_insert_rowid()` track or override the most recent successful insert into a rowid table on a connection. Trigger execution temporarily changes the observed value; rolled-back inserts still count as successful for this API.
- `sqlite3_changes()`/`sqlite3_changes64()` report rows changed by the most recently completed direct INSERT/UPDATE/DELETE; `sqlite3_total_changes()`/`sqlite3_total_changes64()` report cumulative direct plus trigger changes since open. Concurrent use of the same connection makes these values unpredictable.
- `sqlite3_interrupt()` and `sqlite3_is_interrupted()` coordinate cancellation across threads, with interrupted write operations inside explicit transactions causing transaction rollback.
- `sqlite3_complete()`, `sqlite3_complete16()`, and `sqlite3_incomplete()` check SQL text completeness, not SQL validity.
- `sqlite3_busy_handler()` installs one non-reentrant busy callback per connection; `sqlite3_busy_timeout()` replaces any existing busy handler.
- `sqlite3_setlk_timeout()` is only effective in `SQLITE_ENABLE_SETLK_TIMEOUT` builds and VFSes that support blocking locks.
- `sqlite3_get_table()` and `sqlite3_free_table()` provide a legacy/convenience full-result materialization path; returned tables must be released by the matching free routine.
- `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, and `sqlite3_vsnprintf()` provide SQLite's formatting dialect and allocator ownership rules.
- `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_realloc()`, `sqlite3_realloc64()`, `sqlite3_free()`, and `sqlite3_msize()` expose SQLite's allocator; `sqlite3_memory_used()` and `sqlite3_memory_highwater()` expose allocator statistics when enabled.
- `sqlite3_randomness()` exposes the same PRNG used by random rowid selection and SQL random functions, seeding from the default VFS when needed.

### Authorization, tracing, and progress callbacks

`sqlite3_set_authorizer()` installs a compile-time authorization callback invoked during prepare/reprepare. Return values are `SQLITE_OK`, `SQLITE_DENY`, or `SQLITE_IGNORE`; action codes cover schema creation/deletion, table reads/writes, pragma, transaction, attach/detach, virtual table creation/drop, function calls, savepoints, and recursive trigger/view activity.

Security integration: the authorizer is relevant when preparing SQL from untrusted sources and should be paired with `sqlite3_limit()` and storage-size limits for defense in depth. It is not a runtime row-level security hook; it fires during preparation and can fire again if `sqlite3_step()` triggers automatic reprepare.

Tracing APIs include deprecated `sqlite3_trace()`/`sqlite3_profile()` and replacement `sqlite3_trace_v2()` with event masks `SQLITE_TRACE_STMT`, `SQLITE_TRACE_PROFILE`, `SQLITE_TRACE_ROW`, and `SQLITE_TRACE_CLOSE`. A connection can have at most one trace callback.

`sqlite3_progress_handler()` installs one progress callback per connection, invoked during long-running prepare/step work. Returning non-zero interrupts the operation. The callback must not modify the invoking connection.

Risk signals: authorizer, busy, trace, log, and progress callbacks have strict reentrancy limits. Wrappers should document which callbacks may call back into SQLite and should serialize callback state if connections are shared across threads.

### Opening databases and URI behavior

`sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct database connections. `sqlite3_open()` and `sqlite3_open_v2()` take UTF-8 filenames; `sqlite3_open16()` takes native-endian UTF-16. Even failed opens usually return a connection handle that must be closed, except allocation failure can set `*ppDb` to NULL.

`sqlite3_open_v2()` requires one of three base access modes: read-only, read-write existing, or read-write/create. It accepts optional flags for URI interpretation, in-memory databases, mutex mode, shared/private cache, extended result-code mode on open, and no-follow symlink protection. The VFS name parameter can select a custom registered VFS.

Special filenames and URI parameters affect persistence:

- `":memory:"` creates a private in-memory database that disappears at close.
- An empty filename creates a private temporary on-disk database deleted at close.
- URI parameter `mode` can request `ro`, `rw`, `rwc`, or `memory`.
- `cache` selects shared/private cache.
- `vfs` selects a VFS by name.
- `psow` provides powersafe-overwrite metadata.
- `nolock=1` disables rollback-mode file locking and can corrupt databases if multiple writers exist.
- `immutable=1` disables locking/change detection and opens read-only under the assumption the file cannot change; using it on a changing file can produce incorrect results or `SQLITE_CORRUPT`.

### Error reporting

`sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_errstr()`, and `sqlite3_error_offset()` expose the most recent error for a connection or a result-code string. Error strings are SQLite-owned and can be overwritten by later API calls. In serialized mode, another thread using the same connection can replace the error before the caller retrieves it unless the caller holds the connection mutex.

`sqlite3_set_errmsg()` lets extensions or wrappers set the connection's error code/message so they behave more like core features. It returns `SQLITE_OK`, `SQLITE_NOMEM`, or `SQLITE_MISUSE`.

### Prepared statement lifecycle, limits, prepare flags, and compile APIs

`sqlite3_stmt` is an opaque compiled SQL program. The documented lifecycle is prepare, bind, step, reset/rebind as needed, and finalize. The chunk declares `sqlite3_limit()` and limit constants for string/blob/row size, SQL length, columns, expression depth, compound select terms, VDBE op count, function arguments, attached databases, LIKE/GLOB pattern size, variable number, trigger depth, worker threads, and parser stack depth.

Prepare flags for `sqlite3_prepare_v3()`/`sqlite3_prepare16_v3()` include:

- `SQLITE_PREPARE_PERSISTENT`: hint that the statement will be reused and should avoid lookaside depletion.
- `SQLITE_PREPARE_NORMALIZE`: retained as a no-op compatibility flag.
- `SQLITE_PREPARE_NO_VTAB`: fail if virtual tables are used.
- `SQLITE_PREPARE_DONT_LOG`: suppress compiler errors from the configured error log.
- `SQLITE_PREPARE_FROM_DDL`: apply schema-sourced security restrictions, especially with `TRUSTED_SCHEMA` disabled.

Compile APIs declared here are `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`. New code should use the v2/v3 family because prepared statements retain original SQL text, enabling automatic reprepare on schema changes, more precise step errors, and plan recompile when bound parameters can influence query planning.

Risk signals:

- `ppStmt` must not be NULL.
- Only the first statement in input SQL is compiled; `pzTail` points to the remainder.
- UTF-16 prepare paths convert to UTF-8 internally.
- Legacy prepare statements may fail operations that require saved SQL text, such as later explain-mode changes.

### Statement SQL, explain mode, busy state, values, contexts, and bindings

The statement-inspection APIs include `sqlite3_sql()`, `sqlite3_expanded_sql()`, and conditionally `sqlite3_normalized_sql()`. `sqlite3_expanded_sql()` allocates with `sqlite3_malloc()` and must be freed by the application; the others are statement-owned.

Statement property APIs include:

- `sqlite3_stmt_readonly()` to detect direct database writes.
- `sqlite3_stmt_isexplain()` to distinguish normal, EXPLAIN, and EXPLAIN QUERY PLAN statements.
- `sqlite3_stmt_explain()` to change explain mode when possible, requiring reset/inactive state and possibly saved SQL text.
- `sqlite3_stmt_busy()` to detect statements stepped but not completed or reset.

`sqlite3_value` is the dynamic typed SQL value object. The chunk distinguishes protected values, which have an internal mutex held, from unprotected values. Function arguments and `sqlite3_vtab_rhs_value()` results are protected; `sqlite3_column_value()` returns unprotected values that may only be passed to selected APIs. `sqlite3_context` is the SQL-function execution context used by application-defined functions and aggregate/window state APIs declared in later chunks.

Binding APIs declared here include blob, blob64, double, int, int64, null, text, text16, text64, value, pointer, zeroblob, and zeroblob64 variants. Parameter metadata APIs include `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3_bind_parameter_index()`, and `sqlite3_clear_bindings()`.

Important binding semantics:

- Host parameters are 1-indexed and may be anonymous (`?`), numbered (`?NNN`), or named (`:VVV`, `@VVV`, `$VVV`).
- `sqlite3_reset()` does not clear bindings.
- Length arguments are byte counts, not character counts.
- Negative blob length is undefined; negative text length means scan to terminator.
- `SQLITE_STATIC`, `SQLITE_TRANSIENT`, or a destructor define object lifetime for text/blob pointers.
- `sqlite3_bind_pointer()` binds SQL NULL plus a typed pointer for the pointer-passing interface; `SQLITE_TRANSIENT` as its destructor value is undefined.
- `zeroblob` placeholders are memory-efficient and intended for incremental BLOB writes.

Test signals: binding tests should cover destructor invocation on failure, embedded NUL behavior, text encoding and BOM handling, out-of-range indexes (`SQLITE_RANGE`), oversized values (`SQLITE_TOOBIG`), OOM (`SQLITE_NOMEM`), binding after step without reset (`SQLITE_MISUSE`), and parameter name/index handling for repeated named parameters and sparse `?NNN` slots.

### Result column metadata at chunk end

The chunk declares `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_name16()`, and, when compiled with `SQLITE_ENABLE_COLUMN_METADATA`, origin metadata APIs:

- `sqlite3_column_database_name()` / `sqlite3_column_database_name16()`
- `sqlite3_column_table_name()` / `sqlite3_column_table_name16()`
- `sqlite3_column_origin_name()` / `sqlite3_column_origin_name16()`

These functions return statement-owned pointers valid until finalize, automatic reprepare, or a later same-column metadata request in another encoding. They return NULL for expressions/subqueries or allocation failures. Concurrent metadata calls against the same statement/result column have undefined results.

Line 5,207 starts documentation for declared datatype lookup. The range stops at line 5,232 before completing the documentation or declarations, so the merge lane should expect the corresponding APIs to be covered in the next chunk.

## Control Flow and State Model

This header chunk describes a layered API flow rather than implementation bodies:

1. Process startup optionally calls `sqlite3_config()` before `sqlite3_initialize()`.
2. `sqlite3_initialize()` initializes mutexes, memory, global state, and the default VFS via `sqlite3_os_init()`.
3. Applications open a `sqlite3` connection with `sqlite3_open*()`, optionally selecting flags, URI parameters, mutex mode, cache mode, and VFS.
4. Connection-local behavior is adjusted with `sqlite3_db_config()`, limits, busy handlers, authorizers, trace/progress hooks, or extended result-code mode.
5. SQL is compiled with `sqlite3_prepare_v2()`/`v3()`, optionally invoking authorizer/progress callbacks and using limits/security flags.
6. Applications bind values, step statements, inspect results/metadata/errors, reset and reuse statements, and finalize them in later API sections.
7. VFS and file method tables mediate persistence, locking, shared memory, WAL/journal files, syncs, and file-control signals.
8. Connections are closed with `sqlite3_close()` or `sqlite3_close_v2()`, rolling back open transactions and handling dependent objects according to close variant.
9. Process shutdown may call `sqlite3_shutdown()` only after all resources are released.

State is scoped at several levels:

- Global: initialization state, threading mode, allocator/mutex/page-cache/log/URI defaults, memory statistics, PRNG seed, registered VFS list.
- Connection: open database files, error state, last insert rowid, change counters, busy handler, authorizer, trace callback, progress callback, runtime limits, DBCONFIG flags, mutex mode, cache mode, URI state.
- Statement: original SQL, bytecode, bindings, activity/reset state, explain mode, result-column metadata, automatic reprepare state.
- VFS/file: OS file handles, lock state, WAL shared-memory mappings, device capabilities, sync behavior, filesystem-specific configuration.

## Dependencies and Integration Points

Internal SQLite modules implied by this API include the parser/code generator, VDBE bytecode engine, pager, btree, WAL, rollback journal, mutex subsystem, memory allocator, page cache, pragma processor, virtual table layer, extension loading, error logging, and platform VFS implementations.

External integration points include:

- Host-language wrappers that map `sqlite3`, `sqlite3_stmt`, and callback lifetimes into managed runtimes.
- Custom VFS implementations or shims that implement `sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, URI metadata, and file-control opcodes.
- Embedded systems that configure static allocators, custom mutexes, or nonstandard OS initialization with `SQLITE_OS_OTHER`.
- Security-sensitive applications that combine authorizers, DBCONFIG defensive/trusted-schema flags, prepare flags, limits, immutable/nolock choices, and extension loading controls.
- Diagnostics/observability through compile options, runtime version checks, error codes, error offsets, trace/profile/progress callbacks, memory statistics, file statistics, and VFS names.

## Risks and Edge Cases

- The file is a generated-header template. Research and downstream reports should preserve the distinction between `sqlite.h.in` placeholders and emitted `sqlite3.h` constants.
- ABI/source compatibility depends on opaque handles staying opaque and on public struct append-only versioning for VFS and I/O method tables.
- Many APIs are intentionally not reentrant from callbacks. Busy, authorizer, progress, trace, and log callbacks can deadlock or corrupt state if they call mutating SQLite APIs on the invoking connection.
- Shared connections across threads require attention even in serialized mode because per-connection error state and counters can change between API calls.
- VFS implementers can cause silent corruption by mishandling short reads, locks, sync ordering, shared-memory locks, atomic-write opcodes, file-control opcodes, or immutable/nolock semantics.
- `SQLITE_OPEN_EXCLUSIVE` is VFS-only and does not mean application-level exclusive open in `sqlite3_open_v2()`.
- `sqlite3_open*()` failure handling still usually requires `sqlite3_close()` on the returned handle.
- Text/blob binding length and lifetime rules are a frequent source of use-after-free, embedded-NUL surprises, destructor double-free assumptions, and undefined behavior.
- Security options are interdependent: `TRUSTED_SCHEMA`, `PREPARE_FROM_DDL`, extension loading, FTS tokenizer exposure, writable schema, attach-create/write, comments, and defensive mode each cover different attack surfaces.
- This chunk ends mid-section; declared-type APIs and the rest of the column/value/step/finalize surface must be reconciled with later chunk reports.

## Test Signals

Useful tests or review checks for this chunk include:

- Header/library version mismatch checks using `sqlite3_libversion_number()`, `sqlite3_sourceid()`, and compile-time macros.
- Build matrix tests with `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_THREADSAFE=0/1/2`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_SETLK_TIMEOUT`, and custom allocator/VFS builds.
- Connection lifecycle tests for unfinalized statements, `sqlite3_close()` returning `SQLITE_BUSY`, `sqlite3_close_v2()` zombie behavior, and transaction rollback on close.
- VFS contract tests for `xOpen()` failure cleanup, short-read zero fill, lock transition legality, `xShmLock()` legal combinations, sync flags, mmap fetch/unfetch, persistent WAL, atomic write opcodes, and URI filename metadata helpers.
- Configuration ordering tests proving pre-init-only options reject with `SQLITE_MISUSE` after initialization while documented anytime options still work.
- Security tests combining `sqlite3_set_authorizer()`, `sqlite3_limit()`, `SQLITE_PREPARE_NO_VTAB`, `SQLITE_PREPARE_FROM_DDL`, `SQLITE_DBCONFIG_TRUSTED_SCHEMA`, `SQLITE_DBCONFIG_DEFENSIVE`, and load-extension controls.
- Busy/progress/interrupt tests for lock contention, timeout replacement of custom busy handlers, deadlock avoidance, progress cancellation during prepare and step, and transaction rollback after interrupt.
- Open/URI tests for `:memory:`, empty temporary filename, `mode=ro/rw/rwc/memory`, VFS precedence, `cache=shared/private`, `immutable=1`, `nolock=1`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`.
- Error reporting tests for extended result-code mode, `sqlite3_error_offset()`, `sqlite3_set_errmsg()`, and thread interleaving of per-connection error state.
- Statement tests for v2/v3 automatic reprepare, `pzTail`, UTF-16 conversion, prepare flags, limit truncation, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, expanded SQL ownership, and normalized SQL conditional availability.
- Binding and metadata tests for 1-indexed parameters, repeated named parameters, sparse numbered parameters, destructor/lifetime modes, text64 encoding validation assumptions, zeroblob placeholders, clear-bindings behavior, column-count/name lifetime, and column-origin metadata under `SQLITE_ENABLE_COLUMN_METADATA`.
