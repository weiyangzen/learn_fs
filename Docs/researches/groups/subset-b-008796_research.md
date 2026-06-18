# Research Report: subset-b-008796

This grouped report covers SQLite test harness sources under `sources/storage-engines/sqlite/src`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test2.c -->
# sources/storage-engines/sqlite/src/test2.c

## Purpose
`test2.c` exposes low-level pager and fault-injection internals to the Tcl test harness. It is not part of the SQLite library; it lets scripts open raw `Pager` handles, fetch and mutate `DbPage` objects, control savepoint-style pager checkpoints, synthesize sparse files, and install test-control callbacks.

## Important APIs, Types, and Functions
The file registers Tcl commands in `Sqlitetest2_Init()`: `pager_open`, `pager_close`, `pager_commit`, `pager_rollback`, `pager_stmt_begin`, `pager_stmt_commit`, `pager_stmt_rollback`, `pager_stats`, `pager_pagecount`, `page_get`, `page_lookup`, `page_unref`, `page_read`, `page_write`, `page_number`, `pager_truncate`, optional `fake_big_file`, `sqlite3BitvecBuiltinTest`, `sqlite3_test_control_pending_byte`, and `sqlite3_test_control_fault_install`. It uses `Pager`, `DbPage`, `sqlite3PagerOpen()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerCommitPhaseOne/Two()`, `sqlite3PagerSavepoint()`, `sqlite3PagerStats()`, and `sqlite3_test_control()`. `test_pagesize` is a process-global pager size used by `pager_open()` and `page_write()`.

## Control Flow
`pager_open()` builds a read-write main-db pager over the default VFS, sets cache size and page size, then returns a pointer string. Page commands convert pointer strings back to native pointers with `sqlite3TestTextToPtr()`. `page_get()` first obtains a shared lock, then loads the requested page. `page_write()` marks the page writable before copying Tcl text into the page buffer. Statement commands map to one savepoint slot: open savepoint 1, rollback/release savepoint 0, or release savepoint 0. Commit performs phase one followed by phase two and returns Tcl errors on either failure.

## State and Persistence Behavior
Pager state is real database state. `page_write()` changes cached page content and persistence occurs only after commit and sync behavior in the pager. `pager_truncate()` truncates the pager image, not necessarily the on-disk file immediately. `fake_big_file()` writes at an `N` megabyte offset to create sparse storage conditions. Fault simulation stores global `faultSimInterp`, `faultSimScriptSize`, and `faultSimScript`; once installed, `sqlite3FaultSim()` calls evaluate Tcl script text with an appended integer argument.

## Dependencies and Integration Points
This file depends on internal SQLite headers `sqliteInt.h`, `tclsqlite.h`, pager internals, default VFS functions, Tcl command registration, external `sqlite3ErrName()`, and test globals for I/O and disk-full simulation. It links Tcl variables such as `sqlite_io_error_pending`, `sqlite_diskfull`, and read-only `sqlite_pending_byte`, allowing existing Tcl test scripts to observe and manipulate error simulation.

## Risks
Pointer strings expose raw `Pager` and `DbPage` addresses with no lifetime validation. Misordered Tcl calls can use pages after unref or pagers after close. `page_read()` copies 100 bytes into a stack buffer and returns it as a string, so embedded zero bytes truncate Tcl string semantics. `faultSimCallback()` mutates a shared script buffer and interpreter globals, so it is not isolated across concurrent tests. `fake_big_file()` can create very large sparse files and is disabled only for diskless builds; Windows restricts the requested size.

## Test Signals
Useful signals include pager statistics names and counters, pager page count, returned SQLite symbolic error names, linked I/O error counters, bitvec test-control return codes, and callback-driven fault results. Tests should assert correct error propagation for lock/get/write/commit paths and reset fault-control state after use.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test3.c -->
# sources/storage-engines/sqlite/src/test3.c

## Purpose
`test3.c` exposes raw btree and cursor operations to Tcl. It targets `btree.c` tests by opening Btree handles outside normal SQL execution, creating cursors, moving them, inserting records, reading pager statistics, and validating varint encode/decode routines.

## Important APIs, Types, and Functions
The central types are `Btree`, `BtCursor`, `BtreePayload`, a fake process-global `sqlite3 sDb`, and reference counter `nRefSqlite3`. Tcl commands include `btree_open`, `btree_close`, `btree_begin_transaction`, `btree_pager_stats`, `btree_cursor`, `btree_close_cursor`, `btree_next`, `btree_eof`, `btree_payload_size`, `btree_first`, `btree_varint_test`, `btree_from_db`, `btree_ismemdb`, `btree_set_cache_size`, and object command `btree_insert`.

## Control Flow
`btree_open()` lazily initializes `sDb` with the default VFS and a recursive mutex, opens a main database btree, sets cache size, and returns a pointer string. `btree_close()` closes the handle and releases the fake connection mutex when the final btree closes. Cursor creation allocates `sqlite3BtreeCursorSize()` bytes with Tcl allocation, locks the table when shared-cache support is present, opens a cursor, then returns its pointer. Cursor operations enter the btree, invoke the relevant internal routine, leave the btree, and convert results to Tcl values. `btree_insert()` builds a `BtreePayload` either for integer-key tables or key-only payloads and calls `sqlite3BtreeInsert()`.

## State and Persistence Behavior
The fake `sqlite3` connection and its mutex are shared by all Btrees opened with this harness. Btree changes persist through the pager backing the opened file after transactions and pager commit behavior are exercised elsewhere. Cursors are manually allocated and must be closed to avoid leaks. `btree_from_db()` returns the main or selected attached database's existing Btree pointer from a live Tcl SQLite handle; subsequent operations must honor the owning database mutex.

## Dependencies and Integration Points
The file depends on `sqliteInt.h`, `btreeInt.h`, `tclsqlite.h`, `sqlite3ErrName()`, pointer conversion helpers, SQLite mutex APIs, pager stats through `sqlite3BtreePager()`, varint helpers `putVarint()`, `getVarint()`, and `getVarint32()`. It integrates with shared-cache tests through `sqlite3BtreeLockTable()` when available.

## Risks
The harness intentionally bypasses SQL-layer validation. It can pass stale or arbitrary pointer strings to internal APIs, leak the fake `sDb` mutex if open/close counts become unbalanced, or close cursors after the owning Btree has gone away. Some cursor movement routines enter the Btree but do not always enter the owning db mutex, unlike stats and creation paths; this reflects historical test assumptions and is risky outside controlled tests.

## Test Signals
Signals include symbolic SQLite error names, pager stats with read/write counters, boolean EOF and memory-db results, payload size, and varint self-test failures with exact mismatch text. Tests should pair opens/closes and cursor allocation/freeing, and should validate both integer-key and index-style insertion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test4.c -->
# sources/storage-engines/sqlite/src/test4.c

## Purpose
`test4.c` provides a Unix pthread-based Tcl harness for multithreaded SQLite tests. It allows Tcl scripts to create named worker threads, issue prepare/step/finalize operations, inspect row results and errors, swap or transfer SQLite handles, and halt threads.

## Important APIs, Types, and Functions
The `Thread` structure stores leader-written command fields (`zFilename`, `xOp`, `zArg`, `opnum`, `busy`) and worker-written result fields (`completed`, `db`, `pStmt`, `zErr`, `rc`, `argc`, `argv`, `colv`). `threadset[26]` maps IDs `A` through `Z`. Registered commands include `thread_create`, `thread_wait`, `thread_halt`, `thread_argc`, `thread_argv`, `thread_colname`, `thread_result`, `thread_error`, `thread_compile`, `thread_step`, `thread_finalize`, `thread_swap`, `thread_db_get`, `thread_db_put`, and `thread_stmt_get`.

## Control Flow
`thread_create` initializes a slot and launches a detached pthread running `test_thread_main()`. The worker opens the database, reports initial completion, then spins until the leader increments `opnum`. Each requested operation is a function pointer (`do_compile`, `do_step`, or `do_finalize`) executed in the worker thread. `test_thread_wait()` uses a static SQLite app mutex as a memory barrier and busy-waits until `completed` catches up. Halt sets `xOp` to null, advances `opnum`, waits for final cleanup, and releases stored strings.

## State and Persistence Behavior
Each thread owns an SQLite connection and optionally a prepared statement. Step results hold pointers returned by SQLite column APIs; they remain valid only while the statement remains positioned and unfinalized. `thread_db_get()` and `thread_stmt_get()` remove ownership from the worker and return pointer strings to Tcl, while `thread_db_put()` injects a pointer back into a worker slot. `thread_swap()` exchanges live `sqlite3*` handles between two idle worker threads.

## Dependencies and Integration Points
The file compiles only when `SQLITE_OS_UNIX && SQLITE_THREADSAFE`. It uses pthreads, `sched_yield()`, Tcl command APIs, `sqlite3_open()`, `sqlite3_prepare()`, `sqlite3_step()`, `sqlite3_finalize()`, `sqlite3_close()`, `sqlite3_thread_cleanup()` when not omitted, `sqlite3ErrName()`, and pointer-string helpers from the test harness.

## Risks
The synchronization model is intentionally primitive: shared fields are ordinary memory plus busy waiting and app-mutex barriers, not condition variables. Detached threads mean lifecycle mistakes can leak or race. Result column pointers are not copied. Pointer transfer commands can move database and statement ownership across threads in ways that would be unsafe outside misuse tests. `zErr` ownership is mixed between heap strings and static strings and depends on `zStaticErr`.

## Test Signals
Tests observe per-thread `SQLITE_*` result names, error text, column count, column values, and column names. Important coverage includes concurrent open/prepare/step/finalize behavior, handle handoff between worker and main thread, swapped connections, and clean shutdown of all busy slots with `thread_halt *`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test5.c -->
# sources/storage-engines/sqlite/src/test5.c

## Purpose
`test5.c` supports UTF and value conversion tests. It gives Tcl scripts byte-level access to UTF encodings, measures `sqlite3_value_text()` overhead on a constructed `Mem`, and calls the internal UTF self-test.

## Important APIs, Types, and Functions
Commands registered by `Sqlitetest5_Init()` are `binarize`, `test_value_overhead`, `test_translate`, and `translate_selftest`. The implementation uses `Mem` from `vdbeInt.h`, `sqlite3_value`, `sqlite3ValueNew()`, `sqlite3ValueSetStr()`, `sqlite3ValueText()`, `sqlite3ValueBytes()`, `sqlite3ValueFree()`, and internal `sqlite3UtfSelfTest()`. `name_to_enc()` maps Tcl names `UTF8`, `UTF16LE`, `UTF16BE`, and `UTF16` to SQLite encoding constants.

## Control Flow
`binarize()` converts a Tcl UTF-8 string to a Tcl byte-array including its terminating zero byte. `test_value_overhead()` creates a static UTF-8 `Mem` containing `hello world` and loops `repeat_count` times, optionally invoking `sqlite3_value_text()`. `test_translate()` constructs a `sqlite3_value` from either Tcl string text or byte-array data in the requested source encoding, converts it to the target encoding, returns the converted bytes plus terminator, and frees the value. The optional fifth argument forces transient allocation with `sqlite3_free` as destructor.

## State and Persistence Behavior
The file has no durable state. It creates short-lived SQLite value objects and returns Tcl byte arrays. The transient path tests destructor ownership by allocating a separate SQLite buffer. `translate_selftest` runs internal asserts when UTF16 support is compiled in.

## Dependencies and Integration Points
This harness depends on SQLite VDBE memory internals, encoding constants, Tcl object byte-array APIs, and compile-time `SQLITE_OMIT_UTF16`. It directly exercises APIs below the public SQL interface, making it useful for encoding regressions that normal SQL tests may hide.

## Risks
`test_value_overhead()` manually initializes only the `Mem` fields it needs; changes to `Mem` invariants can make this test stale. `test_translate()` passes `-1` byte counts for UTF16 byte arrays, which relies on SQLite string routines finding terminators. The optional transient branch allocates exactly `len` bytes for non-UTF8 input, so tests must supply properly terminated encoded byte arrays when required.

## Test Signals
Expected signals are byte-for-byte translated output including terminators, invalid encoding names returning Tcl errors, performance/no-op behavior of repeated value-text calls, and assertion failures from `sqlite3UtfSelfTest()` in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test6.c -->
# sources/storage-engines/sqlite/src/test6.c

## Purpose
`test6.c` implements crash and device-simulation support for SQLite tests. It registers a VFS named `crash` that wraps a real VFS, buffers writes in memory, and on sync either flushes, drops, corrupts, truncates, or exits to emulate power failure and device characteristics.

## Important APIs, Types, and Functions
Key types are `WriteBuffer`, `CrashFile`, and global `CrashGlobal g`. `CrashFileVtab` implements SQLite I/O methods version 2, including WAL shared-memory pass-throughs. Tcl commands include `sqlite3_crash_enable`, `sqlite3_crashparams`, `sqlite3_crash_now`, `sqlite3_simulate_device`, `sqlite3_crash_on_write`, `unregister_devsim`, `register_jt_vfs`, and `unregister_jt_vfs`. Core routines are `writeListAppend()`, `writeListSync()`, `cfOpen()`, `cfWrite()`, `cfRead()`, `cfSync()`, and `processDevSymArgs()`.

## Control Flow
When crash VFS is enabled, `cfOpen()` opens the real file via the parent VFS and caches its contents into `CrashFile.zData`. `cfWrite()` updates the cache and appends a write buffer instead of writing through immediately. `cfRead()` reads from the cache. `cfSync()` checks whether the file name matches `g.zCrashFile`, decrements `g.iCrash`, and calls `writeListSync()` with crash mode when the configured sync count reaches zero. `writeListSync()` walks the global write list, choosing actions according to `SQLITE_IOCAP_*` flags and randomness; in crash mode it exits the process after replay/corruption.

## State and Persistence Behavior
All pending writes are held in process-global `g.pWriteList`, ordered across file handles. Non-crash sync flushes relevant buffers, while sequential-device simulation may flush writes before the synced handle. Crash sync may leave writes omitted or garbage sectors written. `cfClose()` flushes pending writes for that handle. `cfFileControl(SQLITE_FCNTL_SIZE_HINT)` can append a truncate-style buffer and extend cached size. Device characteristics and sector size are mutable globals configured by Tcl.

## Dependencies and Integration Points
The file is active only for `SQLITE_TEST` and not `SQLITE_OMIT_DISKIO`. It uses internal VFS wrappers `sqlite3Os*`, Tcl allocation, `sqlite3_randomness()`, SQLite I/O capability flags, external devsym and journal-test VFS registration functions, and the default VFS as parent. WAL shared-memory methods are delegated to the real file handle.

## Risks
The crash path calls `exit(-1)` by design. The global write list is not protected for concurrent use. `CrashFile.zName` stores the VFS `zName` pointer rather than owning a copy. File sizes are narrowed to `int` in cached fields. Random corruption can write whole simulated sectors, so tests must run against disposable files. The VFS models selected device guarantees, not a complete filesystem.

## Test Signals
Signals include process termination at the configured sync, recovery behavior after reopening databases, Tcl errors for bad device options, and visible effects of `atomic`, `safe_append`, `sequential`, and sector-size settings. Tests should reset/unregister simulated VFS layers and avoid sharing crash-global state between cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test8.c -->
# sources/storage-engines/sqlite/src/test8.c

## Purpose
`test8.c` implements the `echo` and `echo_v2` virtual table test modules. An echo table mirrors a real backing table, logs module calls into Tcl variables, can inject method failures, and exercises virtual table planning, scanning, writing, transaction, function-overload, rename, and savepoint hooks.

## Important APIs, Types, and Functions
Key types are `echo_vtab`, `echo_cursor`, and `EchoModule`. Major callbacks include `echoCreate`, `echoConnect`, `echoBestIndex`, `echoOpen`, `echoFilter`, `echoNext`, `echoColumn`, `echoRowid`, `echoUpdate`, `echoBegin`, `echoSync`, `echoCommit`, `echoRollback`, `echoFindFunction`, `echoRename`, and v2 savepoint callbacks. Tcl commands are `register_echo_module` and `sqlite3_declare_vtab`.

## Control Flow
Connect/create allocate `echo_vtab`, dequote arguments, derive the backing table name, log arguments, and call `echoDeclareVtab()`. That routine reads the real table SQL from `sqlite_schema`, calls `sqlite3_declare_vtab()`, captures column names, and marks left-most indexed columns. `echoBestIndex()` builds an SQL query in `idxStr` using usable constraints on rowid or indexed columns, sets `argvIndex`, `omit`, `orderByConsumed`, and estimated cost. `echoFilter()` verifies `idxNum` is the hash of `idxStr`, prepares the generated query, binds supplied constraint values, and advances to the first row.

## State and Persistence Behavior
Each virtual table keeps copied backing-table metadata, optional log table name, transaction flag, and Tcl interpreter pointer. Reads come from prepared SELECT statements over the real table. `echoUpdate()` converts virtual table INSERT, UPDATE, DELETE operations into real-table SQL and writes through to the backing table, returning `last_insert_rowid()` for inserts. Transaction callbacks maintain `inTransaction` and log calls. Pattern mode can rename the backing table when the virtual table is renamed.

## Dependencies and Integration Points
The module depends on virtual table APIs, SQLite SQL execution and prepare/bind/finalize, Tcl globals `echo_module`, `echo_module_fail(method,table)`, `echo_module_sync_fail`, `echo_module_begin_fail`, `echo_module_cost`, and optional Tcl procedure `::echo_glob_overload`. `moduleDestroy()` also exercises module destructor behavior by calling `sqlite3_create_function()` during destruction.

## Risks
SQL generated from metadata is quoted in many places but not uniformly for every constructed identifier path, especially pattern rename behavior. Tcl globals drive failure injection and cost behavior, so tests must clean them up. `echoColumn()` assumes SELECT layout with rowid at column zero and data columns offset by one. Transaction assertions require SQLite to invoke hooks in expected order; misuse can abort debug builds.

## Test Signals
Primary signals are entries appended to `::echo_module`, generated `idxStr` SQL, virtual table query plans, injected `echo-vtab-error` messages, real backing table mutations, transaction hook ordering, overloaded `glob` behavior, rename side effects, and v2 savepoint callback coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test9.c -->
# sources/storage-engines/sqlite/src/test9.c

## Purpose
`test9.c` contains small C-only tests for obscure public C API behavior that would be awkward or meaningless to expose through generic Tcl bindings. It validates misuse handling, negative realloc semantics, and invalid collation encoding handling.

## Important APIs, Types, and Functions
`Sqlitetest9_Init()` registers `c_misuse_test`, `c_realloc_test`, and `c_collation_test`. These functions exercise `sqlite3_open()`, `sqlite3_close()`, `sqlite3_errcode()`, `sqlite3_prepare()`, `sqlite3_prepare_v2()`, UTF16 prepare variants when enabled, `sqlite3_malloc()`, `sqlite3_realloc()`, and `sqlite3_create_collation()`.

## Control Flow
`c_collation_test()` opens an in-memory database and calls `sqlite3_create_collation()` with an invalid encoding value `456`, expecting `SQLITE_MISUSE`. `c_realloc_test()` allocates five bytes and expects `sqlite3_realloc(p, -1)` to free the allocation and return null. `c_misuse_test()` opens then closes an in-memory handle, invokes selected APIs on the closed handle, and verifies they return `SQLITE_MISUSE`; prepare tests also assert that the statement output pointer is zeroed.

## State and Persistence Behavior
All databases are in-memory and temporary. The misuse test deliberately keeps a closed database pointer to validate API armor or misuse detection. No durable files are touched. Memory state is checked by observing that negative realloc releases ownership.

## Dependencies and Integration Points
The file uses `sqliteInt.h`, `tclsqlite.h`, public SQLite APIs, Tcl object command registration, and compile-time `SQLITE_OMIT_UTF16`. It integrates with the broader testfixture as commands returning Tcl success or an error naming the failing function.

## Risks
The closed-handle misuse checks depend on SQLite preserving enough sentinel state after `sqlite3_close()` for misuse detection. That is intentional but fragile if allocator/debug settings change. The tests assert pointer-zeroing, so release builds without assertions still rely on return-code checks while debug builds catch stronger invariants.

## Test Signals
Success is silent Tcl OK. Failures return `Error testing function: <api>`. Useful coverage includes `SQLITE_MISUSE` for invalid collation encodings and closed handles, null return from negative realloc, and statement pointer nullification after prepare misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_autoext.c -->
# sources/storage-engines/sqlite/src/test_autoext.c

## Purpose
`test_autoext.c` tests the process-global `sqlite3_auto_extension()` registry. It defines two successful auto-extensions that install SQL functions and one failing extension that returns an error message, then exposes Tcl commands to register, cancel, and reset them.

## Important APIs, Types, and Functions
When loadable extensions are enabled, the file uses `SQLITE_EXTENSION_INIT1/2`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, `sqlite3_create_function()`, `sqlite3_mprintf()`, and SQL function callbacks `sqrFunc()` and `cubeFunc()`. Tcl commands include `sqlite3_auto_extension_sqr`, `sqlite3_auto_extension_cube`, `sqlite3_auto_extension_broken`, matching cancel commands, and always `sqlite3_reset_auto_extension`.

## Control Flow
Register commands cast extension initializer functions to the generic auto-extension callback type and return the integer SQLite result. `sqr_init()` and `cube_init()` initialize the extension API table and register `sqr(x)` or `cube(x)`. `broken_init()` initializes the API table, allocates the error string `broken autoext!`, stores it through `pzErrMsg`, and returns non-zero. Cancel commands remove the corresponding initializer from the global registry. Reset clears all registered auto-extensions.

## State and Persistence Behavior
The auto-extension registry is process-global SQLite state, affecting subsequently opened database connections. The SQL functions are registered per connection during extension initialization. The broken initializer tests propagation and freeing of extension error messages. No database files are modified by registration alone.

## Dependencies and Integration Points
The file depends on `sqlite3ext.h`, `tclsqlite.h`, and compile-time `SQLITE_OMIT_LOAD_EXTENSION`. It integrates with connection-open tests that expect new connections to automatically receive `sqr` or `cube`, or fail when the broken extension is active.

## Risks
Global auto-extension state leaks across tests unless reset or canceled. Function pointer casts are standard for this SQLite API but bypass C type checking. The command wrappers do not validate argument count, so extra Tcl arguments are ignored by these object commands. Broken extension registration can intentionally make later opens fail.

## Test Signals
Signals include integer return values from register/cancel, availability of `sqr()` and `cube()` on new connections, failure text from the broken extension, and successful cleanup by `sqlite3_reset_auto_extension`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_autoext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_backup.c -->
# sources/storage-engines/sqlite/src/test_backup.c

## Purpose
`test_backup.c` wraps the incremental backup API in Tcl. It creates a Tcl command representing a live `sqlite3_backup*` handle so scripts can step, inspect, and finish backups explicitly.

## Important APIs, Types, and Functions
The main command `sqlite3_backup` is registered by `Sqlitetestbackup_Init()`. `backupTestInit()` calls `sqlite3_backup_init()` and creates a per-backup Tcl command handled by `backupTestCmd()`. Subcommands are `step npage`, `finish`, `remaining`, and `pagecount`. Cleanup uses `backupTestFinish()` as the Tcl command delete proc. It depends on `getDbPointer()` and `sqlite3ErrName()`.

## Control Flow
`sqlite3_backup CMDNAME DESTHANDLE DESTNAME SRCHANDLE SRCNAME` resolves Tcl database handles to `sqlite3*`, starts the backup, and registers `CMDNAME` with the backup pointer as client data. The `step` subcommand parses a page count and returns the symbolic result of `sqlite3_backup_step()`. `finish` removes the Tcl command's delete proc, deletes the command, calls `sqlite3_backup_finish()`, and returns the symbolic result. Query subcommands return `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()`.

## State and Persistence Behavior
The live backup object is owned by the generated Tcl command. If the command is deleted without explicit `finish`, `backupTestFinish()` finalizes it. Backup operations move pages from the source database to the destination database according to SQLite's backup API and may persist changes in destination files.

## Dependencies and Integration Points
This file integrates with Tcl SQLite database command handles, public backup APIs, Tcl command lifecycle hooks, and symbolic error names. It supports tests that need to interleave backup steps with writes, locks, or schema changes.

## Risks
The initializer does not check return values from `getDbPointer()` before using the output pointers. The `finish` path carefully disables the delete proc before deleting the Tcl command to avoid double finish; changes there would risk use-after-free. A failed `sqlite3_backup_init()` reports a generic message rather than the destination connection error.

## Test Signals
Signals include `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_BUSY`, or other symbolic step/finish results, changing remaining/pagecount values, and automatic cleanup if the Tcl command is deleted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_bestindex.c -->
# sources/storage-engines/sqlite/src/test_bestindex.c

## Purpose
`test_bestindex.c` implements a Tcl-scripted virtual table module named `tcl` for planner and xBestIndex testing. It lets Tcl code declare schemas, inspect `sqlite3_index_info`, choose constraint usage, provide scan SQL, test `IN` handling and RHS extraction, and optionally implement xUpdate and xFindFunction behavior.

## Important APIs, Types, and Functions
Core types are `tcl_vtab`, `tcl_cursor`, `TestFindFunction`, and `TestVtabContext`. Important callbacks are `tclConnect`, `tclBestIndex`, `tclFilter`, `tclNext`, `tclColumn`, `tclRowid`, `tclFindFunction`, `tclFunction`, and `tclUpdate`. `testBestIndexObj()` exposes subcommands `constraints`, `orderby`, `mask`, `distinct`, `in`, `rhs_value`, and `collation`. `register_tcl_module` installs either read-only `tclModule` or update-capable `tclModuleUpdate`.

## Control Flow
Connect/create dequote the module argument or use a default Tcl command, call that command with `xConnect`, and pass its result to `sqlite3_declare_vtab()`. During planning, `tclBestIndex()` creates a temporary Tcl command handle over the live `sqlite3_index_info`, calls the script with `xBestIndex <handle>`, deletes the handle, then interprets the script result as key/value pairs for cost, rows, orderby, idxnum, idxstr, used/omitted constraints, or constraint errors. During scanning, `tclFilter()` calls the script with idx data and argument values, including expanded `sqlite3_vtab_in_first/next()` lists, then prepares returned SQL and advances to the first row.

## State and Persistence Behavior
Each vtab owns a retained Tcl command object, a database pointer, and a list of dynamically allocated function-overload records. Cursors own a prepared statement returned by the script's scan SQL. The update-capable module delegates xUpdate to Tcl and uses the script result as the rowid. No storage is owned by the module itself; persistence depends on SQL the Tcl scripts return or execute.

## Dependencies and Integration Points
The file depends on virtual table APIs including newer planner helpers `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_collation()`, plus Tcl object APIs and `getDbPointer()`. It is compiled out when virtual tables are omitted and is registered by `Sqlitetesttcl_Init()`.

## Risks
The module intentionally trusts Tcl scripts to return well-formed even-length key/value lists and valid SQL. `tclBestIndex()` indexes `apElem[ii+1]` while stepping by two, so malformed odd-length results are hazardous unless Tcl list parsing or surrounding tests prevent them. `tclUpdate()` returns a Tcl error code directly as a SQLite virtual table result on failure, which may not map to SQLite codes. Script-controlled SQL can produce column layouts inconsistent with `tclColumn()` expectations.

## Test Signals
Signals include the Tcl callback transcripts, planner handle output for constraints/orderby/colUsed, `idxNum`/`idxStr` received by xFilter, expanded IN-list argument values, returned scan rows, function overload callback results, xUpdate rowids, and virtual table error messages from script failures or `constraint` directives.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_bestindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_blob.c -->
# sources/storage-engines/sqlite/src/test_blob.c

## Purpose
`test_blob.c` exposes incremental BLOB APIs to Tcl in ways that supplement the normal Tcl channel interface. It can open blob handles, close them, read/write arbitrary offsets and sizes, and accept either raw pointer strings or Tcl incrblob channel names.

## Important APIs, Types, and Functions
Registered commands are `sqlite3_blob_open`, `sqlite3_blob_close`, `sqlite3_blob_bytes`, `sqlite3_blob_read`, and `sqlite3_blob_write`. Helpers include `ptrToText()`, `blobHandleFromObj()`, and `blobStringFromObj()`. The file uses `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `getDbPointer()`, and `sqlite3TestTextToPtr()`.

## Control Flow
`test_blob_open()` resolves a database handle, parses database/table/column/rowid/flags, and either stores the opened `sqlite3_blob*` pointer string in a Tcl variable or deliberately calls `sqlite3_blob_open()` with a null output pointer when the variable name is empty. `blobHandleFromObj()` recognizes `incrblob_` channel names, flushes and seeks the channel, extracts its instance data, or decodes a pointer string. Read allocates a Tcl buffer, calls `sqlite3_blob_read()`, and returns a byte array. Write takes a Tcl byte array and optional override length and calls `sqlite3_blob_write()`.

## State and Persistence Behavior
Open blob handles are external resources that must be closed. Handles obtained from Tcl channels remain owned by the channel, although this test code can operate on the underlying pointer. Writes mutate the referenced row's BLOB storage through SQLite's incremental blob mechanism and are constrained by the blob size and transaction state.

## Dependencies and Integration Points
The file compiles only when incremental blob support is present. It integrates with Tcl SQLite database handles, the Tcl channel implementation for `[db incrblob]`, SQLite pointer-string utilities, and symbolic error names.

## Risks
The static buffer in `ptrToText()` is overwritten by each call. Pointer-string blob handles have no lifetime checks. Channel extraction assumes Tcl channel instance data layout used by SQLite's incrblob channel. The optional `NDATA` argument to write can exceed the Tcl byte-array length, causing SQLite to read past the supplied buffer if misused; tests should use it only for deliberate misuse coverage.

## Test Signals
Signals include stored pointer text, `SQLITE_*` error names for invalid offsets or closed handles, byte-exact read results, byte count from `sqlite3_blob_bytes()`, and persistence of writes observed by SQL queries or subsequent blob reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_blob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_btree.c -->
# sources/storage-engines/sqlite/src/test_btree.c

## Purpose
`test_btree.c` contains small btree debug/test helpers not covered by the larger Tcl btree harness. It reports shared-cache participants and can print active cursor state in debug builds.

## Important APIs, Types, and Functions
`sqlite3BtreeSharedCacheReport()` is a Tcl command-style function that returns pairs of pager filename and `BtShared.nRef`. `sqlite3BtreeCursorList(Btree *p)` prints cursor diagnostics using `sqlite3DebugPrintf()` when `SQLITE_DEBUG` is enabled. It uses `BtShared`, `BtCursor`, `MemPage`, `sqlite3SharedCacheList`, `sqlite3PagerFilename()`, cursor flags, and cursor state.

## Control Flow
The shared-cache report allocates a Tcl list and, when shared cache is not omitted, iterates the global shared-cache list via `GLOBAL(BtShared*, sqlite3SharedCacheList)`. For each shared btree it appends the pager filename and reference count. The cursor-list function walks `p->pBt->pCursor`, reads the current page and index from each cursor, formats root page, read/write mode, current page/index, and EOF state, then prints to debug output.

## State and Persistence Behavior
The file does not mutate btree state. It observes process-global shared-cache structures and live cursor lists. Results are snapshots and may become stale immediately if other code opens/closes shared btrees or cursors.

## Dependencies and Integration Points
It depends on `btreeInt.h`, `tclsqlite.h`, SQLite debug printing, shared-cache internals, and Tcl result construction. It is useful alongside tests that enable shared cache or need internal cursor diagnostics.

## Risks
The helpers read internal global lists without taking explicit locks in this file, so they assume the surrounding test context is serialized or otherwise safe. `sqlite3BtreeCursorList()` is a debug diagnostic and not a stable API. Shared-cache output is absent but still returns Tcl OK when shared cache is omitted.

## Test Signals
Signals are Tcl list pairs for shared-cache filename/reference count and debug log lines for cursor state. Tests can assert that expected databases appear in the shared-cache report and that reference counts change with connection lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_config.c -->
# sources/storage-engines/sqlite/src/test_config.c

## Purpose
`test_config.c` publishes SQLite compile-time configuration to the Tcl test environment. It fills the global `sqlite_options` array and links selected numeric limits/constants as read-only Tcl variables so tests can skip or adapt to the current build.

## Important APIs, Types, and Functions
The main routine is `set_options(Tcl_Interp*)`, called by `Sqliteconfig_Init()`. It uses `Tcl_SetVar2()` for many feature flags and `Tcl_LinkVar()` through the `LINKVAR` macro for constants such as `SQLITE_MAX_LENGTH`, `SQLITE_MAX_COLUMN`, `SQLITE_DEFAULT_PAGE_SIZE`, `SQLITE_MAX_PAGE_COUNT`, `SQLITE_MAX_WORKER_THREADS`, and `TEMP_STORE`. `STRINGVALUE()` stringifies numeric macros.

## Control Flow
Initialization executes a long series of `#ifdef`, `#ifndef`, and numeric macro checks. Each branch writes a string value, usually `"1"` or `"0"`, into `sqlite_options(feature)`. Some options write macro values, such as `CONFIG_SLOWDOWN_FACTOR`, default autovacuum, worker thread limit, and `SQLITE_ENABLE_SETLK_TIMEOUT`. After feature publication, constant variables are linked as read-only Tcl integers, followed by compiler markers for `_MSC_VER` or `__GNUC__` when present.

## State and Persistence Behavior
State is entirely in the Tcl interpreter: the global `sqlite_options` array and linked read-only variables. There is no database persistence. The values reflect compile-time and platform settings for the loaded testfixture process and do not change after initialization.

## Dependencies and Integration Points
The file depends on `sqliteLimit.h`, `sqliteInt.h`, optional `os_win.h`, `tclsqlite.h`, and a broad set of SQLite compile-time macros. It is a central integration point for Tcl tests that use `$sqlite_options(name)` guards to determine whether features such as JSON, FTS, WAL, virtual tables, loadable extensions, shared cache, UTF16, snapshots, sessions, or debug options are available.

## Risks
Because this file mirrors many build macros manually, it can drift from the actual build surface when features are added, renamed, or combined. Some options are derived from compound conditions, for example session requires both session and preupdate hook. Linked variables point to static const locals declared inside the function block, which is safe because they have static storage but easy to misread. Incorrect flags can cause tests to run in unsupported builds or be skipped accidentally.

## Test Signals
Signals are the contents of `sqlite_options`, read-only Tcl constants, and the assertion that `sqlite3_threadsafe()` matches `SQLITE_THREADSAFE`. Tests typically consume this file indirectly by checking options before executing feature-specific cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_delete.c -->
# sources/storage-engines/sqlite/src/test_delete.c

## Purpose
`test_delete.c` implements `sqlite3_delete_database()`, a test utility that removes an SQLite database and associated sidecar files, including journal, WAL, shared-memory, 8.3-name variants, and multiplexor chunk files.

## Important APIs, Types, and Functions
The public function is `sqlite3_delete_database(const char *zFile)`. Helpers are `sqlite3Delete83Name()` and `sqlite3DeleteUnlinkIfExists()`. It uses SQLite allocation and formatting APIs, POSIX `access()` and `unlink()` on non-Windows, and the `win32` VFS `xDelete()` on Windows. It copies multiplex constants `MX_CHUNK_NUMBER`, `SQLITE_MULTIPLEX_JOURNAL_8_3_OFFSET`, and `SQLITE_MULTIPLEX_WAL_8_3_OFFSET`.

## Control Flow
The function allocates a filename buffer sized from the input path. It first deletes base files generated from `%s`, `%s-journal`, `%s-wal`, and `%s-shm`, and for sidecars also tries the 8.3-transformed name. It then scans multiplex chunk patterns for database, journal, and WAL chunks, both normal and 8.3 forms, stopping each sequence when a chunk no longer exists or an error occurs. Any system/VFS error maps to `SQLITE_ERROR`, while allocation failure returns `SQLITE_NOMEM`.

## State and Persistence Behavior
This function destructively deletes files from the filesystem. It assumes `zFile` is a plain filename, not a URI. It does not coordinate with live SQLite connections or locks; callers must ensure the database is not in use.

## Dependencies and Integration Points
It integrates with test code that needs a stronger cleanup primitive than deleting only the main database file. On Windows it routes through the SQLite VFS to match platform delete behavior; on POSIX it uses direct filesystem calls and asserts no VFS pointer is used.

## Risks
The function is destructive and broad: multiplex scans can remove many numbered files derived from the input name. It collapses most OS errors to `SQLITE_ERROR`, losing diagnostics. It has no locking or safety checks for open databases. `sqlite3Delete83Name()` intentionally mimics internal 8.3 suffix logic, so any divergence from SQLite's filename algorithm could leave files behind or target the wrong transformed path.

## Test Signals
Signals include `SQLITE_OK`, `SQLITE_NOMEM`, or `SQLITE_ERROR`, and the absence of main, journal, WAL, SHM, 8.3, and multiplex files after cleanup. Tests should use disposable paths and verify no live connection holds the target database.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_demovfs.c -->
# sources/storage-engines/sqlite/src/test_demovfs.c

## Purpose
`test_demovfs.c` implements a minimal POSIX-like SQLite VFS named `demo`. It is both example code and a test fixture for embedded-style VFS behavior, especially rollback-journal write buffering and omission of locking, temporary files, dynamic loading, and real truncation.

## Important APIs, Types, and Functions
The core type is `DemoFile`, containing `sqlite3_file base`, a POSIX file descriptor, and optional journal write buffer fields. File methods include `demoClose`, `demoRead`, `demoWrite`, `demoTruncate`, `demoSync`, `demoFileSize`, lock no-ops, `demoFileControl`, `demoSectorSize`, and `demoDeviceCharacteristics`. VFS methods include `demoOpen`, `demoDelete`, `demoAccess`, `demoFullPathname`, dynamic-loading stubs, `demoRandomness`, `demoSleep`, and `demoCurrentTime`. `sqlite3_demovfs()` returns the static VFS, and test builds register Tcl commands `register_demovfs` and `unregister_demovfs`.

## Control Flow
`demoOpen()` rejects temporary files, allocates an 8192-byte buffer for main journal files, maps SQLite open flags to POSIX `open()` flags, initializes `DemoFile`, and installs `demoio`. `demoWrite()` coalesces sequential journal writes into the fixed buffer, flushing when full or when writes are non-contiguous; non-buffered files write directly with `lseek()` and `write()`. Reads and file-size checks flush the buffer first. `demoSync()` flushes then calls `fsync()`. Delete optionally syncs the containing directory.

## State and Persistence Behavior
Database and journal state persists through POSIX file descriptors. Journal data may remain only in `DemoFile.aBuffer` until read, file-size, sync, close, or a non-contiguous/full-buffer write forces `demoFlushBuffer()`. Locking is not implemented, so SQLite is told no reserved lock exists and multi-connection use is outside the VFS contract. `demoTruncate()` is a no-op, making journal modes requiring truncation unsuitable.

## Dependencies and Integration Points
The file uses public `sqlite3.h`, POSIX calls (`open`, `read`, `write`, `fsync`, `close`, `fstat`, `access`, `unlink`, `getcwd`, `sleep`, `usleep`, `time`), and Tcl registration in `SQLITE_TEST` Unix builds. It assumes Unix path syntax, maximum path length 512, and in-memory temp storage for correct use.

## Risks
No locking means concurrent independent connections can corrupt databases. No temp-file support and no real truncate limit supported SQLite modes. `demoRandomness()` returns OK without filling bytes, so consumers should not rely on strong randomness. `demoCurrentTime()` has second precision and 32-bit time caveats. Direct writes do not retry partial writes or EINTR. Path handling is intentionally simple and Unix-specific.

## Test Signals
Signals include successful registration/unregistration, correct operation under `vfs=demo`, fewer journal write system calls by buffering, expected failure for temp files or unsupported extension loading, hot-journal rollback behavior due to no reserved lock, and correct persistence after sync/close.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_demovfs.c -->
