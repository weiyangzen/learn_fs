# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 1-5283

## Scope

This chunk covers the beginning of SQLite's `sqlite3.c` amalgamation as vendored under WiredTiger's test third-party tree. The range starts with the amalgamation banner for SQLite 3.50.4, enters the embedded `sqliteInt.h`, includes platform setup fragments (`msvc.h`, `vxworks.h`, large-file and compiler feature macros), and then enters the embedded public `sqlite3.h` header. It ends in the public API documentation for prepared-statement parameter lookup, just after `sqlite3_bind_parameter_name()` and before the rest of the bind-parameter APIs.

The code in this chunk is mostly declarations, public API contracts, preprocessor configuration, and generated API documentation comments. Implementations of the declared APIs appear later in the amalgamation.

## Purpose

The opening amalgamation block makes this single C file a complete SQLite core translation unit and records the upstream SQLite version and Fossil source identifier. The early `sqliteInt.h` section prepares compilation for the host platform before any system headers are included: it defines amalgamation visibility (`SQLITE_CORE`, `SQLITE_AMALGAMATION`, `SQLITE_PRIVATE`), coverage-comment conventions, Tcl calling convention defaults, MSVC warning and alignment workarounds, VxWorks feature switches, POSIX large-file support, compiler-version detection, C99 math availability, GNU/OpenBSD feature macros, fallthrough annotations, MinGW time ABI compatibility, and the optional `SQLITE_CUSTOM_INCLUDE` hook.

The embedded `sqlite3.h` section exposes the public C API used by applications and by WiredTiger's SQLite test dependency. In this range it defines version metadata, core opaque handle types, result/open/sync/lock/file-control constants, the VFS and file I/O interfaces, initialization/configuration contracts, memory allocator hooks, connection configuration constants, basic connection and statement lifecycle APIs, error reporting, limits, SQL preparation, statement inspection, value/function-context opaque types, and the first prepared-statement binding APIs.

## Important APIs, Types, and Data

- `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, and `SQLITE_SOURCE_ID`: identify this vendored SQLite as 3.50.4 from source id `2025-07-30 19:33:53 ...`; `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose the same information at runtime.
- `sqlite3`: opaque database connection handle. `sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct it; `sqlite3_close()` and `sqlite3_close_v2()` destroy it with different behavior for outstanding statements, blobs, and backups.
- `sqlite3_stmt`: opaque prepared statement handle. The documented lifecycle is prepare, bind, step, reset for reuse, and finalize; this chunk declares prepare and statement-inspection routines but not `sqlite3_step()` or finalization yet.
- `sqlite3_value` and `sqlite3_context`: opaque value and SQL-function execution context types used by later function, column, and result APIs.
- `sqlite3_int64` and `sqlite3_uint64`: portable 64-bit integer typedefs selected from `SQLITE_INT64_TYPE`, MSVC/Borland `__int64`, or `long long`.
- `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs`: core VFS ABI. `sqlite3_file` stores a `pMethods` table; `sqlite3_io_methods` defines close/read/write/truncate/sync/size/lock/unlock/file-control/sector/device/shared-memory/mmap fetch hooks; `sqlite3_vfs` defines open/delete/access/full-path/dynamic-loading/randomness/sleep/time/system-call override hooks.
- Result code constants: primary result codes (`SQLITE_OK`, `SQLITE_ERROR`, `SQLITE_BUSY`, `SQLITE_IOERR`, `SQLITE_CORRUPT`, `SQLITE_ROW`, `SQLITE_DONE`, and others) plus many extended codes for I/O, locking, busy, readonly, constraint, notice, warning, authorization, and symlink cases.
- Open, lock, sync, I/O capability, shared-memory, and file-control constants: `SQLITE_OPEN_*`, `SQLITE_LOCK_*`, `SQLITE_SYNC_*`, `SQLITE_IOCAP_*`, `SQLITE_SHM_*`, and `SQLITE_FCNTL_*` define the contract between the core, VFS implementations, and `sqlite3_file_control()`.
- Initialization and configuration APIs: `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, `sqlite3_os_end()`, `sqlite3_config()`, and `sqlite3_db_config()`. Associated constants include `SQLITE_CONFIG_*` for global allocator, mutex, page-cache, logging, URI, mmap, sorter, and memory-database settings, and `SQLITE_DBCONFIG_*` for per-connection flags such as foreign keys, triggers, load extensions, defensive mode, trusted schema, statement scanstatus, ATTACH permissions, and comment handling.
- `sqlite3_mem_methods`: application-supplied allocator vtable with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`.
- Execution and diagnostics APIs in this range: `sqlite3_exec()`, `sqlite3_compileoption_used()`, `sqlite3_compileoption_get()`, `sqlite3_threadsafe()`, `sqlite3_extended_result_codes()`, `sqlite3_last_insert_rowid()`, `sqlite3_set_last_insert_rowid()`, `sqlite3_changes()`, `sqlite3_changes64()`, `sqlite3_total_changes()`, `sqlite3_total_changes64()`, `sqlite3_interrupt()`, `sqlite3_is_interrupted()`, `sqlite3_complete()`, `sqlite3_complete16()`, `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_setlk_timeout()`, `sqlite3_get_table()`, `sqlite3_free_table()`, formatted-string helpers, allocation helpers, memory high-water APIs, `sqlite3_randomness()`, authorizer hooks, trace/progress hooks, URI filename helpers, error APIs, and runtime limit APIs.
- Preparation and binding APIs declared before the chunk boundary: `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, UTF-16 prepare variants, `sqlite3_sql()`, `sqlite3_expanded_sql()`, optionally `sqlite3_normalized_sql()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_bind_blob()`, `sqlite3_bind_blob64()`, `sqlite3_bind_double()`, `sqlite3_bind_int()`, `sqlite3_bind_int64()`, `sqlite3_bind_null()`, `sqlite3_bind_text()`, `sqlite3_bind_text16()`, `sqlite3_bind_text64()`, `sqlite3_bind_value()`, `sqlite3_bind_pointer()`, `sqlite3_bind_zeroblob()`, `sqlite3_bind_zeroblob64()`, `sqlite3_bind_parameter_count()`, and `sqlite3_bind_parameter_name()`.

## Control Flow

There is very little runtime control flow in this chunk because it is largely header material. The active compile-time control flow is preprocessor-driven:

1. The amalgamation guard defines SQLite core/amalgamation symbols and default static linkage for private symbols.
2. Platform sections select MSVC warning suppressions and allocator alignment behavior, VxWorks-specific mutex/load-extension/locking defaults, POSIX large-file macros, compiler version macros, C99 math availability, GNU/OpenBSD feature macros, and MinGW `_USE_32BIT_TIME_T` compatibility.
3. If `SQLITE_CUSTOM_INCLUDE` is defined, a caller-specified header is included after platform setup but before most SQLite feature options take effect.
4. Public API declarations are conditionally exposed or stubbed based on build macros such as `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_FLOATING_POINT`, and `SQLITE_ENABLE_NORMALIZE`.

The documented runtime flows are contracts for later implementations. `sqlite3_exec()` is described as prepare/step/finalize over one or more SQL statements, stopping on errors or callback aborts. `sqlite3_open_v2()` maps flags and URI parameters into connection and VFS behavior. Busy handlers loop by retrying while the callback returns nonzero, unless SQLite detects a deadlock risk. Prepared statements are documented as a lifecycle of prepare, bind, step, reset, and finalize. Binding routines are documented to validate parameter indexes, handle destructor/static/transient lifetimes, copy or reference inputs according to the destructor argument, and leave bindings intact across `sqlite3_reset()`.

## State and Persistence Behavior

The declarations in this chunk define several state domains but do not implement their mutation directly:

- Global process state: initialization/shutdown state, global configuration set by `sqlite3_config()`, threading mode, custom memory allocator/mutex/page-cache/log hooks, URI defaults, mmap defaults, memory status tracking, PRNG seeding, and VFS registration state. Many global configuration options are only valid before `sqlite3_initialize()` or after `sqlite3_shutdown()`.
- Per-connection state: open database handles, lookaside configuration, foreign-key/trigger/view/load-extension flags, defensive and trusted-schema flags, busy and setlk timeouts, last-insert rowid, change counters, interrupt state, authorizer callback, trace callback, progress handler, error code/message/offset, runtime limits, and statement lists.
- VFS/file state: open-file method tables, lock state transitions, shared-memory locks, device capability declarations, file-control operations, WAL/journal/database filename associations, URI query metadata, and optional system-call override tables for testing.
- Persistent storage effects: this chunk itself does not write durable state, but it defines the contracts used later for database creation/opening, rollback journals, WAL files, shared-memory files, checkpoint-on-close behavior, file synchronization, atomic-write controls, powersafe-overwrite behavior, mmap limits, temporary files, and destructive reset-via-VACUUM workflows.

Several documented persistence-sensitive behaviors are important: closing a connection with an open transaction rolls it back; `sqlite3_close_v2()` can defer destruction until outstanding objects finish; WAL files may persist or be removed based on file-control and connection-close settings; `immutable=1` disables locking/change detection and is only safe for truly immutable files; `nolock=1` can corrupt a database if concurrent writers exist; `sqlite3_interrupt()` can roll back an interrupted write transaction; and VFS short reads must zero-fill unread bytes or corruption can follow.

## Dependencies and Integration Points

This vendored file is an upstream SQLite amalgamation embedded under WiredTiger's test tree. WiredTiger code should treat it as third-party source and rely on the SQLite C API rather than editing internal declarations.

The chunk depends on C preprocessor configuration from compiler flags and optional custom includes. It expects platform headers and ABI details for MSVC, MinGW, VxWorks, POSIX large-file support, C99 math, GNU extensions, OpenBSD feature macros, and optional Tcl/test integration. It exposes integration points for application code through the stable SQLite C API, and for lower layers through the VFS and memory/mutex/page-cache vtables.

Key integration surfaces include:

- Application SQL access: connection open/close, `sqlite3_exec()`, prepare APIs, statement binding, and result/error APIs.
- Host resource management: custom memory allocators, page-cache configuration, static heap/pagecache buffers, and memory accounting.
- Concurrency and locking: compile-time thread safety, runtime threading modes, per-connection busy handlers, blocking lock timeouts, VFS lock transitions, and shared-memory WAL locks.
- Filesystem abstraction: `sqlite3_vfs` registration and file method callbacks for database, journal, WAL, temp, transient, and subjournal files.
- Security controls: authorizer callbacks, run-time limits, defensive mode, trusted schema, load-extension gating, ATTACH create/write gating, and SQL comment gating.
- Testing hooks: coverage annotation comments, VFS system-call override hooks, `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_CONFIG_SQLLOG`, custom allocators for out-of-memory simulation, and compile-option diagnostics.

## Risks and Edge Cases

- This file is third-party amalgamated source. Local modifications risk diverging from upstream SQLite and can break subtle ABI, macro, and generated-documentation assumptions.
- Header/library mismatch is explicitly guarded by version APIs; embedding code must ensure the paired `sqlite3.h` declarations and compiled `sqlite3.c` implementation are from the same SQLite source id.
- Many APIs have undefined behavior for invalid handles, finalized statements, invalid `sqlite3_filename` pointers, wrong VFS method versions, invalid `sqlite3_open_v2()` flag combinations, negative BLOB lengths, bad text encodings, or incorrect bind destructor lifetimes.
- Threading behavior is easy to misuse. `sqlite3_threadsafe()` reports only compile-time mutex availability, not runtime `sqlite3_config()` changes. Shared connection access can make last-insert rowid, change counts, and error reporting unpredictable unless serialized.
- VFS implementations must honor ABI details exactly: set `sqlite3_file.pMethods` on failed opens, zero-fill short reads, respect lock transition rules, avoid reserved file-control opcode conflicts, implement shared-memory locks consistently, and return `SQLITE_NOTFOUND` for unsupported file controls.
- Configuration timing matters. Most `sqlite3_config()` options return `SQLITE_MISUSE` after initialization, and `sqlite3_db_config(SQLITE_DBCONFIG_LOOKASIDE)` can fail with `SQLITE_BUSY` if lookaside memory is in use.
- URI filename options can change durability or safety. `immutable=1` and `nolock=1` trade correctness guarantees for special deployment assumptions; wrong use can produce stale reads or corruption.
- Error strings and expanded SQL strings have different ownership. `sqlite3_errmsg()` memory is SQLite-owned and volatile, while `sqlite3_exec()` error strings and `sqlite3_expanded_sql()` results require `sqlite3_free()`.
- Busy handlers, authorizers, trace callbacks, logger callbacks, and progress handlers are constrained against reentrant modification of the invoking connection; violating that contract is undefined or explicitly unsupported.

## Test Signals

Useful validation signals for this chunk are mostly compile/API compatibility and behavioral tests that exercise the declarations later implemented in the amalgamation:

- Build the SQLite amalgamation in the WiredTiger test configuration and confirm no platform macro regressions, missing prototypes, or calling-convention mismatches.
- Assert version consistency using `sqlite3_libversion_number() == SQLITE_VERSION_NUMBER`, `sqlite3_libversion()`, and `sqlite3_sourceid()` when tests link this vendored SQLite.
- Exercise connection lifecycle: open/close, close with outstanding statements returning `SQLITE_BUSY`, `sqlite3_close_v2()` deferred cleanup, and automatic rollback on close with an open transaction.
- Exercise VFS contracts with a custom or shim VFS: failed `xOpen()` cleanup behavior, zero-filled short reads, lock transitions, URI parameter retrieval, WAL/journal filename translation, file-control pass-through, mmap fetch/unfetch, and shared-memory locking.
- Exercise configuration timing: successful pre-initialize `sqlite3_config()` calls, `SQLITE_MISUSE` for non-anytime options after initialization, lookaside reconfiguration returning `SQLITE_BUSY` while in use, and no-op/unsupported behavior for omitted features.
- Exercise safety controls: authorizer deny/ignore paths, lowered `sqlite3_limit()` values for untrusted SQL, `SQLITE_DBCONFIG_DEFENSIVE`, trusted-schema restrictions, load-extension gating, and ATTACH create/write controls.
- Exercise statement flow: prepare variants, SQL text introspection, expanded SQL ownership, readonly/explain/busy reporting, binding all scalar/blob/text/pointer/zeroblob variants, destructor invocation on bind failures where specified, index range errors, and persistence of bindings across reset.
- Exercise concurrency and interruption: busy timeout behavior, deadlock-avoidance returning `SQLITE_BUSY`, blocking-lock timeout where enabled, `sqlite3_interrupt()` from another thread, and stable error reporting when callers hold the database mutex.
