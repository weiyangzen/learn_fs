# subset-b-008798 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_onefile.c -->
# sources/storage-engines/sqlite/src/test_onefile.c

## Purpose
`test_onefile.c` is a demo/test VFS named `fs` that makes SQLite treat one fixed-size blob as embedded media containing both the main database and rollback journal. It demonstrates how a non-filesystem storage device could expose only block read/write/sync operations while still supporting SQLite pager semantics.

## Important APIs, Types, And Functions
The central types are `fs_vfs_t`, `fs_real_file`, `fs_file`, and `tmp_file`. `fs_register()` registers the VFS. `fsOpen()`, `fsRead()`, `fsWrite()`, `fsSync()`, `fsDelete()`, and `fsAccess()` implement the SQLite VFS and I/O methods. `tmp*()` methods back statement journals and other temporary files with heap memory. Constants `BLOCKSIZE` and `BLOBSIZE` define 512-byte sectors and a 10 MB simulated medium.

## Control Flow
Opening a main database creates or finds an `fs_real_file` backed by the parent VFS. A new parent file is extended to `BLOBSIZE`; an existing one reads the database size from the first four bytes and detects a possible journal by checking the last block. Main database offsets are translated by adding one block for the metadata header. Journal offsets are mapped backward from the end of the blob, block by block. Syncing the database writes the current database-region size into byte zero and then syncs the parent handle. Deleting the journal zeroes the first journal header area and clears volatile journal size.

## State And Persistence Behavior
Persistent state is the blob file itself: first block metadata, database content after block zero, and journal content growing backward from the end. `nDatabase` is persisted on database sync; `nJournal` is process-local and reconstructed conservatively after a crash. The VFS maintains an in-memory open-file list with reference counts. Temporary non-main files persist only in malloc-backed buffers.

## Dependencies And Integration Points
The file depends on SQLite VFS APIs and delegates path, dynamic loading, randomness, sleep, and time calls to the parent VFS. It is registered into testfixture through `SqlitetestOnefile_Init()` when `SQLITE_TEST` is enabled.

## Risks And Test Signals
Risks include no real locking, one-connection assumptions, fixed 10 MB capacity, journal-size reconstruction that intentionally over-reports after crash, no WAL/shared-memory support, and reliance on rollback-journal recovery checksums to ignore garbage past the logical journal end. Test signals include creating and reopening a database through `vfs=fs`, rollback after simulated crash with a nonzero journal tail, `SQLITE_FULL` when database and journal regions collide, zeroed journal header after delete, and temp objects staying in memory.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_onefile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_osinst.c -->
# sources/storage-engines/sqlite/src/test_osinst.c

## Purpose
`test_osinst.c` implements a VFS instrumentation wrapper plus a `vfslog` virtual table for reading the generated binary logs. It is test-only infrastructure for measuring and inspecting SQLite VFS and file-method calls with low logging overhead.

## Important APIs, Types, And Functions
Key objects are `VfslogVfs`, which wraps a parent `sqlite3_vfs` and owns a buffered log file, and `VfslogFile`, which wraps each underlying `sqlite3_file`. Public C entry points are `sqlite3_vfslog_new()`, `sqlite3_vfslog_finalize()`, `sqlite3_vfslog_annotate()`, and `sqlite3_vfslog_register()`. Wrapped methods include `vfslogOpen()`, `vfslogRead()`, `vfslogWrite()`, `vfslogSync()`, lock/unlock, and shared-memory methods. The virtual table side uses `VfslogVtab`, `VfslogCsr`, `vlogConnect()`, `vlogNext()`, and `vlogColumn()`.

## Control Flow
`sqlite3_vfslog_new()` finds the parent VFS, allocates a larger VFS object that includes the parent file storage for the log, opens a fresh log file, writes a magic header, and registers the wrapper as default. Each wrapped VFS or file method measures elapsed time, calls the real method, then appends a 24-byte big-endian record. Events carrying a path or annotation append a length-prefixed string. The virtual table opens a log file, skips the 20-byte header, decodes records sequentially, tracks file ids from `xOpen`, and exposes event name, filename, click count, return code, size, and offset columns.

## State And Persistence Behavior
The wrapper persists binary records to the configured log file through an 8 KB in-memory buffer. It stores per-wrapper counters, log offset, and next file id. Reader cursors maintain transient file-id-to-name mappings while scanning. In test builds, `vfslog_flush()` temporarily disables SQLite's simulated I/O and disk-full faults to avoid recursive corruption of the instrumentation log.

## Dependencies And Integration Points
It depends on SQLite VFS version 2 file methods for shared-memory logging, Tcl testfixture bindings under `SQLITE_TEST` or `TCLSH`, and virtual-table support for log reading. The Tcl command `vfslog` exposes `new`, `finalize`, `annotate`, and `register`.

## Risks And Test Signals
Risks include truncated timing to 16 bits, integer truncation of 64-bit offsets and sizes, missing logging for `xFileControl` and most VFS utility methods, assumptions about record framing, and limited validation of malformed log files. Test signals include successful wrapper creation/finalization, readable `vfslog` rows matching known SQLite operations, path association through `xOpen`, annotation records, WAL shared-memory event capture, and clean behavior under injected I/O faults.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_osinst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_pcache.c -->
# sources/storage-engines/sqlite/src/test_pcache.c

## Purpose
`test_pcache.c` is a deliberately simple application-defined pager-cache implementation used by SQLite tests. It replaces the default page cache to exercise pager behavior under cache pressure, random page discard, failed initialization, and aggressive stress paths.

## Important APIs, Types, And Functions
It implements `sqlite3_pcache_methods2` with `testpcacheInit()`, `testpcacheShutdown()`, `testpcacheCreate()`, `testpcacheFetch()`, `testpcacheUnpin()`, `testpcacheRekey()`, `testpcacheTruncate()`, and `testpcacheDestroy()`. `testpcacheGlobalType` stores installation-wide knobs: dummy allocation, instance count, discard chance, PRNG seed, and high-stress mode. `testpcache` owns a fixed array of page slots with keys and pin state.

## Control Flow
`installTestPCache()` saves or restores the default cache methods using `sqlite3_config()`. Initialization allocates a dummy block so tests can observe initialization failure and shutdown cleanup. Each cache instance allocates one block containing the instance and all page buffers. Fetch first returns an existing page, then optionally allocates a free slot, withholds reserve slots unless `createFlag==2`, may force failure in high-stress mode, and finally recycles a random unpinned page for purgeable caches. Unpin may discard based on the explicit discard flag or randomized discard probability.

## State And Persistence Behavior
All state is process-local and non-persistent. Page content is in heap memory. The fixed page array is a hard limit; `nFree` and `nPinned` track capacity and invariants. Randomness is deterministic from `prngSeed`, making stress behavior reproducible.

## Dependencies And Integration Points
The implementation plugs into SQLite through `SQLITE_CONFIG_PCACHE2` and is installed by test code before SQLite initialization. It assumes single-threaded use: the global state has no mutex protection.

## Risks And Test Signals
Risks include intentional lack of thread safety, fixed capacity differing with `SQLITE_TEMP_STORE`, reliance on asserts for invariants, and a suspicious alignment assignment in `testpcacheCreate()` where `szExtra` is rounded from `szPage` instead of its own value. Test signals include pager tests passing with random discard rates, high-stress mode invoking pager stress paths, no leaked instances on shutdown, correct rekey/truncate behavior, and deterministic failure reproduction from the same seed.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_pcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.c -->
# sources/storage-engines/sqlite/src/test_quota.c

## Purpose
`test_quota.c` implements the quota VFS shim declared by `test_quota.h`. It tracks groups of database and WAL files by full-path glob pattern, enforces aggregate size limits, invokes callbacks before rejecting growth, and exposes both SQLite VFS and stdio-like APIs for quota-managed files.

## Important APIs, Types, And Functions
Core state lives in `quotaGroup`, `quotaFile`, `quotaConn`, opaque `quota_FILE`, and global `gQuota`. Public APIs include `sqlite3_quota_initialize()`, `sqlite3_quota_shutdown()`, `sqlite3_quota_set()`, `sqlite3_quota_file()`, `sqlite3_quota_fopen()`, `sqlite3_quota_fwrite()`, `sqlite3_quota_ftruncate()`, size/mtime helpers, and `sqlite3_quota_remove()`. VFS wrappers are `quotaOpen()`, `quotaDelete()`, `quotaWrite()`, `quotaTruncate()`, and pass-through wrappers for read, sync, locks, file-control, and shared memory. Tcl commands under `SQLITE_TEST` cover setup, dumps, callbacks, and stdio operations.

## Control Flow
Initialization copies the parent VFS, changes `xOpen` and `xDelete`, enlarges `szOsFile`, and installs version 1 and 2 I/O method tables. Opening a main DB or WAL checks the full name against configured groups; matching files are opened through the parent VFS and linked to a shared `quotaFile`. Writes that extend a tracked file compute the new group total, invoke the group's callback if over limit, and return `SQLITE_FULL` if the limit still blocks growth. File-size and truncate calls resynchronize accounting. Stdio wrappers use the same `quotaFile` records and may shorten writes to avoid crossing a limit.

## State And Persistence Behavior
Quota metadata is entirely in-memory. Persistent effects are the normal database/WAL files and files deleted by quota APIs. `quotaGroup.iSize` is maintained from open/write/truncate/filesize/delete paths but can diverge if external processes modify files; explicit `sqlite3_quota_file()` and true-size helpers reconcile or expose that drift. `deleteOnClose` defers deletion of open files until the last close.

## Dependencies And Integration Points
It depends on SQLite VFS, mutex, allocation, and full-path APIs, plus C stdio, `stat`, `ftruncate`, `fsync`, and Windows UTF-8 to MBCS conversion where applicable. It integrates with testfixture through `Sqlitequota_Init()` and Tcl callbacks that may mutate the quota limit by variable indirection.

## Risks And Test Signals
Risks include non-threadsafe initialize/shutdown, undefined behavior when patterns overlap, accounting drift from outside writers, callback reentrancy or failures, delayed delete semantics, partial stdio writes, and platform-specific path conversion. Test signals include over-limit writes returning `SQLITE_FULL`, callbacks successfully raising limits, DB and WAL sizes counted once across multiple opens, group cleanup after zero limit and close, directory-style `sqlite3_quota_remove()`, stdio short writes, truncation accounting, and Windows path tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.h -->
# sources/storage-engines/sqlite/src/test_quota.h

## Purpose
`test_quota.h` declares the public interface for SQLite's test quota VFS shim. It documents the quota model: files are grouped by full-path glob, group size is capped by a configurable limit, and a callback can raise the limit before writes fail.

## Important APIs, Types, And Functions
The header exposes lifecycle APIs `sqlite3_quota_initialize()` and `sqlite3_quota_shutdown()`, group configuration through `sqlite3_quota_set()`, and file enrollment through `sqlite3_quota_file()`. It defines opaque `quota_FILE` and declares stdio-like wrappers: `sqlite3_quota_fopen()`, `sqlite3_quota_fread()`, `sqlite3_quota_fwrite()`, `sqlite3_quota_fflush()`, `sqlite3_quota_fclose()`, `sqlite3_quota_fseek()`, `sqlite3_quota_rewind()`, `sqlite3_quota_ftell()`, `sqlite3_quota_ferror()`, `sqlite3_quota_ftruncate()`, `sqlite3_quota_file_mtime()`, size/truesize/available helpers, and `sqlite3_quota_remove()`.

## Control Flow
Callers initialize the shim once, define one or more distinct quota groups before opening participating database connections, then operate normally through the `quota` VFS or the `quota_FILE` APIs. When a write would extend a file past the group limit, the callback receives the filename, an in/out limit pointer, proposed total size, and client data. Shutdown requires all SQLite connections to be closed.

## State And Persistence Behavior
The header owns no state, but its contract describes in-memory quota accounting layered over persistent files. It explicitly warns that the quota-known size may differ from the true on-disk size if external modification or unflushed stdio writes occur.

## Dependencies And Integration Points
It includes `sqlite3.h`, stdio, and stat/time-related system headers, and is C++ friendly via `extern "C"`. `test_quota.c` implements the declarations and Tcl test bindings use the same API surface.

## Risks And Test Signals
Risks include misuse of initialize/shutdown ordering, overlapping glob patterns, callers assuming UTF-8 globbing is character-aware rather than byte-based, and using truncate to extend a quota-managed file despite documented undefined behavior. Test signals include API compile coverage from C and C++, callback limit mutation, unmanaged-file no-ops, true-size versus quota-size checks, and removal of managed files and managed directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_rtree.c -->
# sources/storage-engines/sqlite/src/test_rtree.c

## Purpose
`test_rtree.c` registers test geometry and query callbacks for SQLite R-Tree modules. It validates both first-generation geometry callbacks and second-generation query callbacks with scoring and `eWithin` pruning behavior.

## Important APIs, Types, And Functions
Important types are `Circle` and `Cube`. Callback functions include `circle_geom()`, `circle_query_func()`, `bfs_query_func()`, and `cube_geom()`, with destructors for cached user data. Tcl registration commands are `register_circle_geom` and `register_cube_geom`, implemented by `register_circle_geom()` and `register_cube_geom()`, and the initializer is `Sqlitetestrtree_Init()`.

## Control Flow
For `circle`, the first invocation validates dimensions and parameters, allocates a cached `Circle`, derives center/radius and two helper boxes, then evaluates each R-Tree rectangle by corner inclusion and cross-box coverage. `Qcircle` supports either four numeric arguments or a single parsed string and sets scores for depth-first, breadth-first, leaf-area ordering, and odd-rowid exclusion cases. `breadthfirstsearch` compares candidate rectangles with a query rectangle and propagates `FULLY_WITHIN` from parents. `cube` validates six coordinates and checks 3D interval overlap.

## State And Persistence Behavior
Callback state is per-query and cached in `pUser`, then freed by `xDelUser`. There is no persistent storage beyond the R-Tree tables operated on by tests. `cube_geom()` asserts that the registered context pointer equals `&gHere`, making context delivery part of the test surface.

## Dependencies And Integration Points
The code is active only with `SQLITE_ENABLE_RTREE`. It uses SQLite's `sqlite3_rtree_geometry_callback()` and `sqlite3_rtree_query_callback()` APIs and Tcl's database-pointer helper. If R-Tree is omitted, registration commands are harmless stubs.

## Risks And Test Signals
Risks include floating-point boundary decisions, manual string parsing via `atof()`, returning `SQLITE_NOMEM` for a negative `Qcircle` radius after freeing cached memory, and tests depending on exact callback scoring order. Test signals include correct intersection results for circle and cube boundaries, parameter validation failures, destructor calls, query order changes for each score type, `FULLY_WITHIN` pruning, and omitted-build behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_rtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_schema.c -->
# sources/storage-engines/sqlite/src/test_schema.c

## Purpose
`test_schema.c` defines a read-only virtual table module named `schema` that exposes one row per column in all attached database schemas. It is used by SQLite tests and can also be built as a loadable extension outside `SQLITE_TEST`.

## Important APIs, Types, And Functions
The virtual table schema has columns `database`, `tablename`, `cid`, `name`, `type`, `not_null`, `dflt_value`, and `pk`. Types `schema_vtab` and `schema_cursor` hold the database handle and three nested statements. Virtual table methods include `schemaCreate()`, `schemaOpen()`, `schemaFilter()`, `schemaNext()`, `schemaColumn()`, `schemaRowid()`, and `schemaClose()`. Registration is via Tcl `register_schema_module` or extension entry point `sqlite3_schema_init()`.

## Control Flow
Filtering prepares `PRAGMA database_list` and immediately advances to the first column. `schemaNext()` walks a nested loop: databases from `database_list`, tables from each schema's `sqlite_schema` or `sqlite_temp_schema`, then columns from `PRAGMA <db>.table_info(<table>)`. `schemaColumn()` maps virtual table columns to the active database-list, table-list, or column-list statement. End-of-scan is represented by a null `pDbList`.

## State And Persistence Behavior
The module is read-only and persists no data. Cursor state is a set of prepared statements and a monotonically increasing rowid. Statements are finalized as each loop level is exhausted or when the cursor closes.

## Dependencies And Integration Points
It depends on virtual-table support, SQLite prepare/step/finalize APIs, `%Q` quoting through `sqlite3_mprintf()`, and Tcl helpers in test builds. Outside test builds it uses `sqlite3ext.h` and `SQLITE_EXTENSION_INIT`.

## Risks And Test Signals
Risks include schema changes while scanning, no constraint pushdown, errors during `schemaNext()` only surfaced as return codes, and memory allocation failures while building PRAGMA SQL. Test signals include rows for main, temp, and attached schemas; correct `table_info` column values; clean finalization on early close; loadable-extension registration; and no rows or harmless registration when virtual tables are omitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_schema.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_sqllog.c -->
# sources/storage-engines/sqlite/src/test_sqllog.c

## Purpose
`test_sqllog.c` implements an experimental `SQLITE_CONFIG_SQLLOG` callback that captures initial database contents and expanded SQL statements from live applications for offline analysis, replay, and performance investigation.

## Important APIs, Types, And Functions
State is stored in `SLConn` per logged connection and singleton `SLGlobal`. `sqlite3_init_sqllog()` installs the callback when `SQLITE_SQLLOG_DIR` is set. Core helpers include `sqllogOpenlog()`, `sqllogCopydb()`, `sqllogFindAttached()`, `sqllogFindFile()`, `testSqllogStmt()`, `sqllogTraceDb()`, and callback `testSqllog()`. Environment variables are `SQLITE_SQLLOG_DIR`, `SQLITE_SQLLOG_REUSE_FILES`, and `SQLITE_SQLLOG_CONDITIONAL`.

## Control Flow
On connection open, the callback lazily initializes global mutex state, optionally checks for a sibling `-sqllog` trigger file, allocates an `SLConn`, opens a per-connection SQL log, and backs up the main database into the log directory. On statement completion, non-`ATTACH` SQL is written with a clock comment; `ATTACH` causes the newly attached database to be copied and an `ATTACH '<copy>' AS '<name>'` statement to be logged. On close, the connection log is closed and the array compacted.

## State And Persistence Behavior
The module persists `sqllog_<pid>_<n>.sql`, database copy files, and an index file mapping database-copy ids to original paths. Global counters allocate log names and logical clock values. `bRec` suppresses recursive logging while PRAGMA and backup operations run. Reuse mode avoids duplicate database copies by consulting the index.

## Dependencies And Integration Points
It depends on `SQLITE_ENABLE_SQLLOG`, environment variables, SQLite backup APIs, mutexes, `sqlite3_log()`, stdio, process id lookup, and filesystem access checks. It integrates before or during SQLite initialization through `sqlite3_config(SQLITE_CONFIG_SQLLOG, ...)`.

## Risks And Test Signals
Risks include fixed path buffers, `MAX_CONNECTIONS` bounds without graceful expansion, best-effort error handling, reliance on expanded SQL text, conditional logging path assumptions, and replay differences for application-defined functions or external side effects. Test signals include creation of SQL, DB, and index files; correct handling of repeated opens with and without reuse; `ATTACH` capture; no recursive self-logging; close cleanup; and logged errors rather than crashes when output files fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_sqllog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_superlock.c -->
# sources/storage-engines/sqlite/src/test_superlock.c

## Purpose
`test_superlock.c` is example and test code for obtaining a strong exclusive lock on a SQLite database in both rollback and WAL journal modes. It exposes `sqlite3demo_superlock()` and `sqlite3demo_superunlock()` plus Tcl bindings for testfixture.

## Important APIs, Types, And Functions
`Superlock` stores the locking database handle and WAL-mode flag. `SuperlockBusy` wraps a busy callback and counts invocations. Important functions are `superlockIsWal()`, `superlockShmLock()`, `superlockWalLock()`, `sqlite3demo_superlock()`, and `sqlite3demo_superunlock()`. Tcl commands are created by `SqliteSuperlock_Init()`.

## Control Flow
`sqlite3demo_superlock()` opens the target database, installs a wrapped busy handler, and executes `BEGIN EXCLUSIVE`. For rollback mode that is sufficient. For WAL mode it detects journal mode, commits the exclusive transaction to drop SQLite's own WAL locks, obtains the recovery shared-memory lock, zeroes the start of the first shared-memory page to force future clients into recovery, then locks all read-lock slots exclusively. Unlocking reverses the WAL shared-memory locks if needed and closes the private database handle.

## State And Persistence Behavior
The active lock is process state held by the private `sqlite3` connection and WAL shared-memory locks. In WAL mode the code intentionally writes zeros into the first shared-memory page, a transient coordination area, not the database file itself. The opaque lock handle must be released through `sqlite3demo_superunlock()`.

## Dependencies And Integration Points
It depends on SQLite busy-handler, open, exec, file-control, and VFS shared-memory methods. The Tcl wrapper creates a command whose deletion releases the lock and can call a Tcl busy script.

## Risks And Test Signals
Risks include VFSes lacking shared-memory support, stale or incompatible WAL lock constants, effects of zeroing shared memory on concurrent clients, and cleanup paths calling unlock on partially acquired locks. Test signals include blocking other readers/writers/checkpointers while locked, busy-handler count continuity across SQL and WAL-lock phases, successful rollback-mode locking with only `BEGIN EXCLUSIVE`, command deletion releasing locks, and clean error returns on busy or unsupported VFS paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_superlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_syscall.c -->
# sources/storage-engines/sqlite/src/test_syscall.c

## Purpose
`test_syscall.c` provides Tcl-controlled fault injection for Unix VFS system calls. It tests error handling in `os_unix.c` by installing wrapper functions through VFS `xSetSystemCall()` and configuring transient or persistent failures.

## Important APIs, Types, And Functions
The global `gSyscall` stores failure countdown, persistence, failure count, fake page size, and original `getpagesize`. `aSyscall[]` maps syscall names to wrapper pointers, original pointers, and errno defaults. Wrappers include `ts_open()`, `ts_close()`, `ts_ftruncate()`, `ts_fcntl()`, `ts_read()`, `ts_pread()`, `ts_write()`, `ts_pwrite()`, `ts_fallocate()`, `ts_mmap()`, and `ts_mremap()`. Tcl subcommands are implemented by `test_syscall_install()`, `uninstall`, `reset`, `fault`, `errno`, `exists`, `list`, `defaultvfs`, and `pagesize`.

## Control Flow
Tests install selected wrappers by saving the original syscall pointer from the default VFS and replacing it. Each wrapper calls `tsIsFail()` or `tsIsFailErrno()` to decrement the countdown and decide whether to fail. `fault COUNT PERSIST` configures when failure starts and whether all later wrapped calls fail. `errno CALL ERRNO` changes the error reported by a wrapper. Reset/uninstall restore original calls individually or through the VFS reset hook. Page-size testing replaces `getpagesize` with a wrapper returning a configured power-of-two size.

## State And Persistence Behavior
All state is process-local and only active on Unix builds. Installed wrappers mutate the default VFS syscall table until reset. The close wrapper deliberately closes the real file descriptor even when simulating an error to avoid descriptor leaks during long tests.

## Dependencies And Integration Points
The file is compiled meaningfully only when `SQLITE_OS_UNIX` is true and the VFS supports version 3 syscall hooks. It depends on Tcl, errno names, Unix system headers, and SQLite's `sqlite3_syscall_ptr` interface.

## Risks And Test Signals
Risks include global process-wide effects, varargs wrapper mismatches, platform-specific syscall availability, default errno values of zero for some wrappers, and failure countdowns consumed by unexpected internal calls. Test signals include install/list/exists matching VFS support, deterministic one-shot and persistent failures, expected SQLite error codes for each injected errno, `EINTR` write partial-write simulation, page-size override behavior, and full reset restoring normal VFS operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclsh.c -->
# sources/storage-engines/sqlite/src/test_tclsh.c

## Purpose
`test_tclsh.c` is the bootstrap layer for SQLite's enhanced Tcl test shell, commonly `testfixture`. It keeps test-only extension registration out of `tclsqlite.c` and centralizes initialization of the SQLite Tcl command plus the many `test_*.c` modules linked into the test binary.

## Important APIs, Types, And Functions
The main export is `sqlite3TestInit(Tcl_Interp *interp)`. It declares external initializers for SQLite Tcl bindings, config/test modules, R-Tree, quota, multiplex, superlock, syscall, RBU, FTS, session, expert, recover, integrity-check, and related test helpers. `load_testfixture_extensions()` initializes a named slave interpreter.

## Control Flow
On Unix, initialization raises the core-file size soft limit to the hard limit to aid crash debugging. If the interpreter does not already have `sqlite3`, it calls `Sqlite3_Init()`. It then invokes each linked module initializer in a fixed order, respecting compile-time feature guards for ZipVFS, sessions, and FTS3/4. Finally it registers `load_testfixture_extensions`, whose command looks up a Tcl slave interpreter and recursively calls `sqlite3TestInit()` on it.

## State And Persistence Behavior
This file persists no application data. It mutates Tcl interpreter state by adding commands, modules, functions, and linked variables. On Unix it also changes the process resource limit for core dumps. Repeated initialization is partly guarded only for the base `sqlite3` command; most test module initializers are expected to tolerate registration calls.

## Dependencies And Integration Points
It depends on Tcl, `sqlite3.h`, `tclsqlite.h`, many linked SQLite test modules, and feature macros controlling optional initializers. It integrates all files in this work item into testfixture by calling `SqlitetestOnefile_Init()`, `SqlitetestOsinst_Init()`, `Sqlitetestschema_Init()`, `Sqlitetesttclvar_Init()`, `Sqlitetestrtree_Init()`, `Sqlitequota_Init()`, `SqliteSuperlock_Init()`, and `SqlitetestSyscall_Init()`.

## Risks And Test Signals
Risks include missing linker symbols when build feature macros and object lists diverge, duplicate command registration on repeated init, initializer order dependencies, and Unix-only resource-limit side effects. Test signals include a working testfixture startup, all expected Tcl commands present, slave interpreter initialization, feature-gated commands appearing only when compiled, and no duplicate-registration errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclsh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclvar.c -->
# sources/storage-engines/sqlite/src/test_tclvar.c

## Purpose
`test_tclvar.c` implements a Tcl-backed virtual table module named `tclvar`. It lets SQLite tests query and mutate Tcl global variables through SQL, exercising virtual table scan planning, constraint handling, and update paths.

## Important APIs, Types, And Functions
The virtual table schema is `name`, `arrayname`, `value`, and `fullname PRIMARY KEY WITHOUT ROWID`. Types `tclvar_vtab` and `tclvar_cursor` hold the Tcl interpreter and iteration lists. Core methods are `tclvarConnect()`, `tclvarOpen()`, `tclvarFilter()`, `tclvarNext()`, `tclvarColumn()`, `tclvarBestIndex()`, and `tclvarUpdate()`. Registration is via Tcl command `register_tclvar_module`, which also creates helper Tcl procs `like` and `tclvar_filter_cmd`.

## Control Flow
`xBestIndex` recognizes `name =`, `name MATCH`, and `value GLOB/REGEXP/LIKE` constraints and encodes selected constraints into `idxStr`. `xFilter` calls Tcl `tclvar_filter_cmd` with constraint values to get a list of matching variable names. Cursor iteration walks scalar variables and array entries using `info vars` and `array names`. `xColumn` reconstructs `name`, `arrayname`, current Tcl value, and `fullname`. `xUpdate` deletes, inserts, renames, or changes variables using `Tcl_UnsetVar()` and `Tcl_SetVar()`, with `NULL` value meaning delete.

## State And Persistence Behavior
State is the Tcl global namespace of the registered interpreter. Cursor lists are Tcl objects with reference counts and are released on cursor close or refilter. SQL writes immediately mutate Tcl variables; there is no transaction rollback integration for Tcl state.

## Dependencies And Integration Points
It requires virtual-table support, `sqliteInt.h`, `tclsqlite.h`, Tcl command evaluation, and `getDbPointer()`. It is registered into testfixture by `Sqlitetesttclvar_Init()`.

## Risks And Test Signals
Risks include SQL transaction semantics not matching Tcl variable side effects, `tclvarColumn()` assuming non-null Tcl values, constraint omission controlled by global `::tclvar_set_omit`, helper Tcl proc redefinition, no meaningful rowids, and possible Tcl errors during filtering being ignored. Test signals include scalar and array variables scanning correctly, constraints reducing candidate variables, `omit` behavior for value constraints, insert/update/delete of `fullname`, `NULL` value deletion, and clean reference counting across repeated scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclvar.c -->
