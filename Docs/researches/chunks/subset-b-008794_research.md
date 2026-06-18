# sources/storage-engines/sqlite/src/test1.c lines 1-9088

## Purpose

This chunk is the first and largest part of SQLite's `test1.c` Tcl test extension. It is not library runtime code; it is compiled into the SQLite test fixture to expose many SQLite C APIs, selected internal test controls, and test-only helpers as Tcl commands and SQL functions. The chunk starts with pointer marshalling helpers and ends inside the beginning of `Sqlitetest1_Init()`, where the Tcl command registration table begins.

The main role of this code is to let Tcl tests exercise exact C-level behavior that the public Tcl SQLite binding normally hides: pointer lifetimes, statement handles, error-code consistency, UTF-8/UTF-16 APIs, memory limits, VFS registration and file-control paths, WAL and snapshot APIs, extension loading, collation/function registration, carray binding, db-config flags, PRNG/test-control switches, and deliberately unusual or invalid call sequences.

## Important APIs, Types, and Functions

### Pointer and handle conversion

- `struct SqliteDb` mirrors the first field of the Tcl binding's connection object so test commands can extract `sqlite3 *db` from an existing Tcl database command.
- `testHexToInt()`, `sqlite3TestTextToPtr()`, and `sqlite3TestMakePointerStr()` convert between pointer strings and native pointers. These are central to the test fixture's convention of returning C handles as Tcl strings.
- `getDbPointer()` accepts either a Tcl SQLite command name or a pointer string and returns `sqlite3 *`.
- `getStmtPointer()` converts statement pointer strings into `sqlite3_stmt *`.
- `StmtToDb(X)` maps a statement to its owning connection using `sqlite3_db_handle()`.
- `sqlite3TestErrCode()` cross-checks a returned SQLite result code against `sqlite3_errcode(db)` for non-threadsafe builds, except for `SQLITE_MISUSE` and `SQLITE_OK`.

These helpers are the integration layer used by nearly every wrapper below.

### Exec, formatting, and table-result wrappers

- `test_exec_printf()`, `test_exec_hex()`, `test_exec()`, and `test_exec_nr()` wrap `sqlite3_exec()` and encode callback output into Tcl lists. The callback `exec_printf_cb()` records column names on the first row and values for each row.
- `test_get_table_printf()` wraps `sqlite3_get_table()` when `SQLITE_OMIT_GET_TABLE` is not defined.
- `test_mprintf_z()`, `test_mprintf_n()`, `test_snprintf_int()`, and the later `sqlite3_mprintf_*()`/`sqlite3_snprintf_str()` wrappers expose SQLite's printf variants with integer, 64-bit integer, long, string, double, scaled double, string-only, and hex-encoded double inputs.
- `fpnum_compare()` is a Tcl helper for comparing floating-point textual output across Tcl versions while tolerating insignificant formatting differences.

### Connection lifecycle and basic connection state

- `test_open()`, `test_open_v2()`, and `test_open16()` expose `sqlite3_open*()` and return pointer strings.
- `sqlite_test_close()` and `sqlite_test_close_v2()` call `sqlite3_close()` and `sqlite3_close_v2()`.
- `test_last_rowid()`, `test_changes()`, `get_autocommit()`, `test_interrupt()`, `test_is_interrupted()`, `test_busy_timeout()`, `test_setlk_timeout()`, `test_extended_result_codes()`, `test_ex_errcode()`, `test_errcode()`, `test_errmsg()`, `test_error_offset()`, `test_errmsg16()`, `test_set_errmsg()`, `test_system_errno()`, `test_db_filename()`, and `test_db_readonly()` expose direct connection state and error-message APIs.
- `db_enter()` and `db_leave()` manually enter or leave `db->mutex`, allowing tests to force locking states.

### SQL functions, aggregates, collations, and callbacks

- `test_create_function()` registers many test SQL functions:
  - `x_coalesce` via `t1_ifnullFunc()`.
  - `hex8` and optional `hex16`.
  - `x_sqlite_exec` via `sqlite3ExecFunc()` to execute SQL recursively from a SQL function.
  - `tkt2213func`, `pointer_change`, `counter1`, `counter2`, `intreal`, `add_text_type`, `add_int_type`, `add_real_type`, `strtod`, `dtostr`, and `inttoptr`.
- `test_create_aggregate()` registers `x_count` and, when deprecated APIs are enabled, `legacy_count`.
- `test_register_func()` registers a generic `testFunc()` that returns values in selected result formats.
- `test_create_collation_v2()` verifies invalid encoding detection and then installs a Tcl-backed collation with a destructor.
- `test_create_function_v2()` tests the destructor path of `sqlite3_create_function_v2()` using `CreateFunctionV2`.
- UTF-16 conditional helpers register test collations/functions across encodings: `test_collate()`, `test_utf16bin_collate()`, `test_collate_needed()`, `add_alignment_test_collations()`, and the `test_function_utf*()` callbacks visible in this chunk.
- `test_autovacuum_pages()` installs or clears a Tcl-script-backed `sqlite3_autovacuum_pages()` callback using `AutovacPageData`.

### Statement preparation, stepping, introspection, and binding

- `test_prepare()`, `test_prepare_v2()`, `test_prepare_v3()`, `test_prepare_tkt3134()`, `test_prepare16()`, and `test_prepare16_v2()` compile SQL and return statement pointer strings. The v2/v3 wrappers copy SQL into malloc-backed buffers to help memory tools detect overreads.
- `test_step()`, `test_reset()`, `test_finalize()`, `test_next_stmt()`, `test_stmt_readonly()`, `test_stmt_isexplain()`, `test_stmt_explain()`, `test_stmt_busy()`, `uses_stmt_journal()`, `test_expired()`, and `test_transfer_bind()` expose statement lifecycle and metadata.
- `test_stmt_status()`, `test_stmt_scanstatus()`, and `test_stmt_scanstatus_reset()` expose statement counters and optional scanstatus details. The debug scanstatus path reads the internal `Vdbe`/`ScanStatus` layout directly.
- `test_sql()`, `test_ex_sql()`, and optional `test_norm_sql()` expose original, expanded, and normalized SQL.
- `test_column_count()`, `test_column_type()`, `test_column_int64()`, `test_column_blob()`, `test_column_double()`, `test_data_count()`, `test_stmt_utf8()`, `test_stmt_utf16()`, and `test_stmt_int()` expose column-value and metadata APIs.
- `test_bind()`, `test_bind_zeroblob()`, `test_bind_zeroblob64()`, `test_bind_int()`, `test_bind_int64()`, `test_bind_double()`, `test_bind_null()`, `test_bind_text()`, `test_bind_text16()`, `test_bind_blob()`, `test_bind_value_from_preupdate()`, `test_bind_value_from_select()`, `test_bind_parameter_count()`, `test_bind_parameter_name()`, `test_bind_parameter_index()`, and `test_clear_bindings()` cover parameter binding surfaces.
- `test_intarray_addr()`, `test_int64array_addr()`, `test_doublearray_addr()`, `test_textarray_addr()`, `inttoptrFunc()`, `bind_carray_intptr()`, and `test_carray_bind()` support carray-related tests and pointer-valued SQL data.

### Virtual tables, extensions, snapshots, WAL, and db config

- `test_drop_modules()`, `test_create_null_module()`, `test_load_extension()`, `test_enable_load()`, `tclLoadStaticExtensionCmd()`, and `test_register_dbstat_vtab()` exercise module and extension availability.
- Conditional snapshot commands `test_snapshot_get()`, `test_snapshot_recover()`, `test_snapshot_open()`, `test_snapshot_free()`, `test_snapshot_cmp()`, and blob equivalents expose `sqlite3_snapshot_*()`.
- `test_wal_checkpoint()`, `test_wal_checkpoint_v2()`, and `test_wal_autocheckpoint()` expose WAL checkpoint APIs.
- `test_sqlite3_db_config()` maps Tcl setting names to many `SQLITE_DBCONFIG_*` options. `test_sqlite3_txn_state()`, `test_dbconfig_maindbname_icecube()`, and `test_mmap_warm()` cover additional per-connection behavior.

### VFS, file-control, IO, memory, PRNG, and test-control helpers

- `test_io_trace()` installs/removes the global `sqlite3IoTrace` callback when tracing support is compiled in.
- `vfsCurrentTimeInt64()`, `vfs_unlink_test()`, `vfs_initfail_test()`, `vfs_unregister_all()`, `vfs_reregister_all()`, and `vfs_list()` test VFS registration, default-VFS behavior, and the current-time method.
- `file_control_test()` and the `file_control_*()` family cover `SQLITE_FCNTL_*` opcodes including last errno, data version, chunk size, size hint, lock proxy, Win32 retry/handle controls, persistent WAL, powersafe overwrite, VFS name, reserve bytes, temp filename, and external-reader detection.
- `test_atomic_batch_write()` opens a database, gets its file pointer via `SQLITE_FCNTL_FILE_POINTER`, and checks `SQLITE_IOCAP_BATCH_ATOMIC`.
- `test_write_db()` directly invokes the main database file's `xWrite()` method.
- `test_release_memory()`, `test_db_release_memory()`, `test_db_cacheflush()`, `test_soft_heap_limit()`, `test_hard_heap_limit()`, `test_thread_cleanup()`, `test_pager_refcounts()`, `test_pcache_stats()`, and `sorter_test_fakeheap()` expose memory, pager, and cache behaviors.
- `save_prng_state()`, `restore_prng_state()`, `reset_prng_state()`, `prng_seed()`, `extra_schema_checks()`, `database_may_be_corrupt()`, `database_never_corrupt()`, `test_treetrace()`, and `test_test_control()` wrap selected `sqlite3_test_control()` paths.
- `test_delete_database()`, `test_register_cksumvfs()`, `test_unregister_cksumvfs()`, and `test_decode_hexdb()` integrate with other test utilities and VFS fixtures.
- `test_getrusage()` is UNIX-only. Win32-only helpers include file-handle controls and `win32_file_lock()`.
- `guess_number_of_cores()` uses platform APIs to report processor count for tests.

## Control Flow

Most Tcl commands follow a repeated pattern:

1. Validate `argc`/`objc` and report Tcl usage errors.
2. Decode handles with `getDbPointer()` or `getStmtPointer()`, or parse Tcl integers, byte arrays, lists, and option strings.
3. Call one SQLite public C API, an internal test-control API, or a selected internal helper.
4. Convert C results into Tcl result strings, integers, byte arrays, or lists.
5. Where applicable, call `sqlite3TestErrCode()` to ensure result-code and connection error-code consistency.

The SQL-function and callback code reverses the direction: SQLite invokes a C callback, which may inspect `sqlite3_value` arguments, call Tcl scripts, call SQLite APIs recursively, or produce special result values. Several functions deliberately create unusual states, such as pointer invalidation checks, `MEM_IntReal` output, multiple-type values, recursive `sqlite3_exec()`, UTF-16 error strings, or destructor callbacks.

The lower chunk flows into `Sqlitetest1_Init()`, which declares external test counters and begins the `aCmd[]` registration table mapping Tcl command names to C command functions. The requested slice ends partway through that table, so later command registrations and final initialization logic are outside this chunk.

## State and Persistence Behavior

This file mostly manipulates SQLite test process state and database handles rather than owning persistent application data. Important stateful areas include:

- Global or static test state:
  - `iotrace_file` and `sqlite3IoTrace` for IO tracing.
  - `sqlite_static_bind_value` and `sqlite_static_bind_nbyte` for static binding tests.
  - static arrays in `test_intarray_addr()`, `test_int64array_addr()`, `test_doublearray_addr()`, and `test_textarray_addr()`.
  - static carray data in `test_carray_bind()`.
  - `pTestCollateInterp`, `zNeededCollation`, and `unaligned_string_counter` for collation tests.
  - saved VFS pointers `apVfs[]`/`nVfs`.
  - `logcallback` for `SQLITE_CONFIG_LOG`.
  - `nondeterministicFunction()`'s static counter.
- Database-visible state:
  - Opening/closing connections and statements.
  - Registering/removing functions, collations, modules, and autovacuum callbacks on a connection.
  - Changing db-config flags, transaction-related settings, busy/setlk timeouts, heap limits, PRNG state, and test-control flags.
  - WAL checkpoints, snapshot handles, file-control operations, and direct database-file writes.
- Persistence risks:
  - `test_write_db()` and `test_delete_database()` can mutate or remove database files.
  - VFS unregister/reregister helpers alter global VFS registration order.
  - `sqlite_abort()` intentionally terminates the process to test crash recovery.

The chunk contains no durable schema or repository metadata. It creates only in-memory fixture state, except when invoked Tcl tests direct SQLite or VFS APIs to modify database files.

## Dependencies and Integration Points

This code depends on SQLite internal and test headers:

- `sqliteInt.h`, `vdbeInt.h`, and `tclsqlite.h` provide internal structures, macros, Tcl binding layout assumptions, and test-only APIs.
- Platform headers provide UNIX, Apple, and Windows behavior for VFS and file-lock tests.
- Tcl C APIs (`Tcl_Interp`, `Tcl_Obj`, `Tcl_CreateCommand` later in init, channels, byte arrays, script evaluation) are the command transport.
- SQLite public APIs dominate the wrappers: open/close, prepare/step/finalize, bind, column, error, WAL, snapshot, db-config, extension, collation, function, memory, VFS, and file-control APIs.
- Internal SQLite APIs are also used intentionally: `sqlite3ValueNew()`, `sqlite3ValueSetStr()`, `sqlite3ValueText()`, `sqlite3ValueFree()`, `sqlite3PagerStats()`, `sqlite3BtreePager()`, `sqlite3PcacheStats()`, `sqlite3DbstatRegister()`, `sqlite3_test_control()`, and internal `Vdbe` fields.
- Other test files provide external hooks such as `sqlite3_delete_database()`, cksum VFS registration, static extension init functions, and possibly `sqlite3_mmap_warm()`.

The primary integration point is `Sqlitetest1_Init()`: once called by the test fixture, it registers this chunk's C functions as Tcl commands used throughout SQLite's Tcl test suite. This chunk also registers SQL functions/collations on individual SQLite connections when Tcl scripts request them.

## Risks and Edge Cases

- Pointer strings are trusted. Many commands accept raw pointer text and cast it to SQLite handles; invalid input can crash the test process. That is acceptable for testfixture code but would be unsafe in production.
- Several helpers rely on SQLite internal structure details, such as `Vdbe` scanstatus fields, `db->mutex`, `db->aDb`, pager access, and Tcl binding client data layout.
- Global/static state is not generally thread-isolated. Examples include IO tracing, log callback, VFS state arrays, carray static storage, collation interpreter pointers, and static test arrays.
- Some routines intentionally invoke undefined or dangerous operational scenarios for tests: recursive SQL execution from a function, manual mutex entry, direct file writes, global VFS unregistration, process abort, and test-control changes.
- Conditional compilation means command availability and behavior vary heavily by build flags: UTF-16, snapshot, unlock-notify, scanstatus, sqllog, virtual table, load extension, Win32, UNIX, Apple locking style, memory management, deprecated APIs, and normalize support.
- Memory ownership is deliberately varied to test destructor paths. `SQLITE_STATIC`, `SQLITE_TRANSIENT`, custom carray destructors, Tcl refcounts, `sqlite3_free`, `free`, and `ckfree` are all used, so regressions can manifest as leaks, double-frees, stale pointers, or allocator mismatches.
- `test_carray_bind()` contains complex option-dependent cleanup for text/blob/static/transient/malloc data; it is a high-risk area for edge cases because ownership changes depending on flags and API version.
- `test_prepare_v3()` computes `zTail = &zSql[(zTail - zCopy)]` unconditionally after `sqlite3_prepare_v3()`, so its assumptions depend on SQLite setting the tail pointer in the tested cases.
- Some commands ignore result codes after internal calls or only assert them, matching test-fixture assumptions but making them unsuitable for resilient runtime use.

## Test Signals

This file is itself test infrastructure. Useful signals from this chunk are:

- Tcl tests can call the registered commands and compare exact SQLite result-code names, Tcl lists, byte arrays, and pointer strings.
- `sqlite3TestErrCode()` failures signal mismatches between direct API return values and connection error state.
- Sanitizer and misuse-sensitive tests can use `clang_sanitize_address`, `OMIT_MISUSE`, manual mutex commands, recursive exec helpers, and process-abort helpers.
- UTF-8/UTF-16 tests use dedicated functions, collations, error-message paths, and prepare/open/column variants to confirm encoding selection and conversion behavior.
- Statement tests can observe status counters, scanstatus metrics, readonly/explain/busy flags, SQL text, normalized/expanded SQL, parameter metadata, column values, and lifecycle return codes.
- VFS/file-control tests can validate VFS registration ordering, file-control opcodes, temporary filenames, batch atomic write capability, lock-proxy behavior, Win32 handle behavior, and direct `xWrite()` error propagation.
- WAL/snapshot/autovacuum/db-config tests can validate feature-specific return codes and callback behavior under build configurations that enable those APIs.
- Memory and PRNG helpers provide deterministic setup/teardown signals for broader SQLite tests.

## Chunk Boundary Notes

This report covers only `sources/storage-engines/sqlite/src/test1.c` lines 1-9088. The file continues after this chunk with the rest of `Sqlitetest1_Init()` and likely additional command/object-command registrations, linked variables, and final initialization behavior. The per-file merge lane should combine this report with later chunk reports before producing a complete file-level research document.
