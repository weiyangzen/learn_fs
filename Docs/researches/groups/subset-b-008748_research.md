# Research Group: subset-b-008748

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfslog.c -->
# Research: sources/storage-engines/sqlite/ext/misc/vfslog.c

## Purpose

`vfslog.c` implements an SQLite VFS wrapper named `vfslog` that logs disk activity for main database files and rollback journals. It is intended for debugging and I/O analysis rather than normal application use. The wrapper delegates all real filesystem work to the process default VFS, but records CSV rows containing timestamps, elapsed time, operation name, target class, arguments, signatures of read/write buffers, and result codes.

The file is designed for embedding into the SQLite amalgamation with `SQLITE_EXTRA_INIT=sqlite3_register_vfslog` and optionally `SQLITE_USE_FCNTL_TRACE`. When registered, it becomes the default VFS and records one log file per database connection/database path, avoiding concurrent-process writes to a single shared log.

## Important APIs, Types, And Functions

- `sqlite3_register_vfslog(const char *zArg)` installs the wrapper around `sqlite3_vfs_find(0)`, sets `szOsFile` to include `VLogFile` plus the real VFS file object, and registers `vfslog` as default.
- `VLogVfs` embeds `sqlite3_vfs` and stores `pVfs`, the parent VFS.
- `VLogFile` embeds `sqlite3_file`, points to the real file object stored inline after itself, and references the relevant `VLogLog`.
- `VLogLog` tracks a shared log stream, reference count, canonical database filename length, optional filename, and list links. A paired `VLogLog[2]` allocation represents the main database and its rollback journal, with the journal entry using `zFilename==NULL` but sharing `out`.
- `vlogLogOpen()` canonicalizes journal/main database association, skips WAL and master-journal files, creates a unique `*-debuglog-<timestamp>` file, links it into `allLogs`, and emits an `IDENT` row on Unix.
- `vlogLogPrint()` formats CSV rows and uses SQLite `%w` escaping for string arguments.
- File methods `vlogRead`, `vlogWrite`, `vlogSync`, `vlogLock`, `vlogUnlock`, `vlogFileControl`, and companions time and log calls before/after delegating to `pReal->pMethods`.
- `vlogSignature()` records a full hex dump for buffers up to 16 bytes, or first-eight-bytes plus a simple 64-bit-style checksum for larger buffers.
- `bigToNative()` and the change-counter logic in `vlogRead`/`vlogWrite` add `CHNGCTR-READ` and `CHNGCTR-WRITE` rows when page-1 header bytes 24..39 are touched.

## Control Flow

Registration captures the current default VFS and publishes a wrapper VFS with version 1 I/O methods. On `xOpen`, `vlogOpen` stores the real `sqlite3_file` immediately after `VLogFile`, opens or reuses a log for main DB or main journal files, delegates to the real VFS, logs `OPEN`, and installs `vlog_io_methods` only on success. Non-main files are opened without a log pointer.

For each file call, the wrapper records `vlog_time()` before delegating, calls the real method, computes elapsed time, and writes a CSV row if a log is available. Reads and writes additionally compute a content signature, and successful accesses overlapping the SQLite database header change-counter region emit semantic change-counter rows. Most VFS-level methods (`xDelete`, `xAccess`) temporarily open a log by path, log the call, then decrement the reference.

Closing a wrapped file delegates `xClose`, logs `CLOSE`, and calls `vlogLogClose`. The log object is refcounted; the main log entry owns the list node, `FILE *`, and allocation, while the journal pair element just decrements and returns.

## State And Persistence Behavior

The persistent side effect is a CSV log file adjacent to or named from the database path: `"<db>-debuglog-<microsecond timestamp>"`. It is opened append-mode and flushed only by stdio behavior, not explicitly after every row. Each log file contains rows for one SQLite connection's main database and rollback journal traffic. WAL files and master journals are deliberately not logged.

Process-local state is held in `allLogs`, protected by `SQLITE_MUTEX_STATIC_MASTER` only while searching/linking/unlinking log objects. Reference increments happen after the mutex is released, so the code assumes SQLite's open/close sequencing and shared log reuse are sufficient for this diagnostic extension. Timing uses microseconds from `gettimeofday` on Unix, `GetSystemTimeAsFileTime` on Windows, and zero elsewhere.

## Dependencies And Integration Points

This code depends on SQLite's VFS and I/O method ABI, SQLite memory and formatting helpers, `SQLITE_FCNTL_TRACE`, `SQLITE_FCNTL_PRAGMA`, `SQLITE_FCNTL_SIZE_HINT`, and platform time/identity APIs. It integrates by becoming the default VFS, so all later SQLite connections use it unless a different VFS is chosen. It wraps `xFileControl(SQLITE_FCNTL_VFSNAME)` to prepend `vlog/` to the underlying VFS name.

## Risks And Edge Cases

- The wrapper advertises I/O method version 1 and leaves shared-memory and mmap methods NULL, so WAL-mode behavior is intentionally not instrumented and may be unavailable through this VFS depending on SQLite expectations.
- `vlogSignature()` casts arbitrary buffers to `unsigned int *` for larger signatures, which can be unaligned on strict-alignment platforms.
- Log paths are based on the raw filename prefix before `-journal`; unusual names or embedded NULs are not supported.
- The log object pair uses `zFilename==NULL` as a journal sentinel. `vlogLogClose` does not free through the journal entry, so reference accounting must stay paired with main entry lifetime.
- CSV writes are not mutex-protected around `fprintf`, but the design avoids cross-process sharing by creating unique log files.
- `vlogUnlock` logs before delegating and records result `0`, so unlock failures are not represented like other methods.
- `xDelete` and `xAccess` call `vlogLogOpen` after the real operation, which can create log files for paths that were only probed or deleted.

## Test Signals

Useful signals include loading/registering the VFS, opening a database, performing reads/writes/transactions, and verifying that a `*-debuglog-*` CSV appears with `IDENT`, `OPEN`, `READ`, `WRITE`, `SYNC`, lock, file-control, and `CHNGCTR-*` rows. Error-path tests should cover failed `xOpen`, failed log file creation, rollback-journal operations sharing the main log, WAL files not being logged, `SQLITE_FCNTL_VFSNAME`, and importability of rows by the SQLite shell `.import` command.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfsstat.c -->
# Research: sources/storage-engines/sqlite/ext/misc/vfsstat.c

## Purpose

`vfsstat.c` is a loadable SQLite extension that installs a VFS shim and an eponymous virtual table named `vfsstat`. The shim counts VFS I/O and selected VFS-level calls by file category, while the virtual table exposes the counters as rows `(file, stat, count)` and allows `UPDATE` of `count` to reset or seed values.

It is diagnostic code for measuring database, journal, WAL, temporary, and miscellaneous VFS activity. The header explicitly warns that counters are incremented without mutex protection, so multi-threaded use can produce inaccurate statistics.

## Important APIs, Types, And Functions

- `sqlite3_vfsstat_init()` is the extension entry point. It initializes the extension API, wraps the default VFS, registers the wrapper as default, creates the `vfsstat` module on the current connection, registers it as an auto-extension for future connections, and returns `SQLITE_OK_LOAD_PERMANENTLY`.
- `VStatVfs` stores the wrapper `sqlite3_vfs` and parent VFS pointer.
- `VStatFile` stores the wrapper file, real file pointer, and `eFiletype`.
- `aVfsCnt[VFSSTAT_MXCNT]` is the global counter matrix indexed by `STATCNT(filetype, stat)`.
- File-type constants distinguish database, rollback journal, WAL, master journal, sub-journal, temp database, temp journal, transient DB, and `*` for VFS-level operations.
- File methods count reads, read bytes on successful reads, writes, written bytes on successful writes, syncs, opens, and lock/unlock/check-reserved-lock operations.
- VFS methods count `xAccess`, `xDelete`, `xFullPathname`, `xRandomness`, `xSleep`, and both current-time variants against the `*` file type.
- `vstattabColumn`, `vstattabFilter`, `vstattabNext`, `vstattabEof`, and `vstattabUpdate` implement the virtual-table view and reset/update behavior.

## Control Flow

When the extension is loaded, the current default VFS is captured and the `vfslog`-named wrapper is registered as the new default. Every subsequent `xOpen` delegates to the parent VFS, classifies the file from SQLite open flags, increments the `open` counter, and installs `vstat_io_methods` on success.

Wrapped I/O methods delegate first, then update counters. Successful `xRead` and `xWrite` add byte counts; request counters are incremented regardless of result. Shared-memory and mmap methods are forwarded without counting. `xFileControl(SQLITE_FCNTL_VFSNAME)` prepends `vstat/` to the underlying name.

The virtual table is eponymous and scan-only. `xFilter` starts at counter index 0, `xNext` increments the raw counter index, `xColumn` maps the index to file/stat/count labels, and `xEof` stops at `VFSSTAT_nFile * VFSSTAT_nStat`. `xUpdate` rejects inserts/deletes, rowid changes, non-integer count values, negative counts, and out-of-range rowids, then writes directly to `aVfsCnt`.

## State And Persistence Behavior

All state is process-global and in-memory. Counters are not persisted to disk and are reset when the process exits or the extension image is unloaded. `sqlite3_auto_extension()` makes the virtual-table module available to future connections in the process, but it does not make counter updates transactional; `UPDATE vfsstat SET count=0` mutates global state immediately through `xUpdate`.

The VFS wrapper remains registered permanently after load because the init function returns `SQLITE_OK_LOAD_PERMANENTLY`. Counter labels are static string arrays, and the table object/cursors contain only scan position.

## Dependencies And Integration Points

The file uses the SQLite loadable-extension ABI, VFS ABI version 2, I/O method version 3, virtual-table APIs including `sqlite3_declare_vtab`, `sqlite3_create_module`, and `sqlite3_auto_extension`, and SQLite memory helpers. It relies on SQLite open flags to infer file type. Integration is broad because the wrapper becomes the default VFS for the process after load.

## Risks And Edge Cases

- The wrapper VFS name is `"vfslog"`, not `"vfsstat"`, which can confuse diagnostics or collide with `vfslog.c` if both are loaded.
- Counter increments are unsynchronized and can race in multi-threaded use.
- Mmap `xFetch`/`xUnfetch` and WAL shared-memory methods are forwarded but not counted, so statistics are incomplete for mmap-heavy or WAL workloads.
- `vstatOpen` increments `open` even when the underlying open fails, then sets `pMethods` to NULL on failure.
- `xBestIndex` ignores constraints, so filtered queries scan all counters and SQLite applies filtering itself.
- `xUpdate` exposes raw rowid-indexed counter mutation; labels are not validated by file/stat names.
- Returning `SQLITE_OK_LOAD_PERMANENTLY` means the extension is meant to remain installed for process lifetime.

## Test Signals

Tests should load the extension, open a database after load, run read/write/sync/lock-producing SQL, query `SELECT * FROM vfsstat WHERE count>0`, reset with `UPDATE vfsstat SET count=0`, and confirm counters change as expected. Coverage should include each file type flag where feasible, failed opens, WAL mode limitations, auto-extension registration for later connections, and `SQLITE_FCNTL_VFSNAME` output.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfsstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfstrace.c -->
# Research: sources/storage-engines/sqlite/ext/misc/vfstrace.c

## Purpose

`vfstrace.c` implements a configurable SQLite VFS shim that prints strace-like diagnostics for VFS and file I/O calls. Unlike `vfslog.c`, output is not hard-coded to a file; callers supply an output callback and argument when creating the trace VFS. The module is intended for embedding in applications or the SQLite shell to observe exact VFS call sequences and return codes.

Tracing is controlled by a bitmask and can be changed at runtime through `PRAGMA vfstrace(...)`, which is intercepted as `SQLITE_FCNTL_PRAGMA`. Individual VFS APIs can be enabled or disabled by name.

## Important APIs, Types, And Functions

- `vfstrace_register(zTraceName, zOldVfsName, xOut, pOutArg, makeDefault)` allocates a new `sqlite3_vfs` plus `vfstrace_info`, wraps the named or default underlying VFS, and registers the new shim.
- `vfstrace_unregister(zTraceName)` unregisters and frees a trace VFS only if its `xOpen` is `vfstraceOpen`.
- `vfstrace_info` stores the root VFS, output callback, trace mask, on/off flag, callback argument, VFS name, and pointer to the wrapper VFS.
- `vfstrace_file` stores per-open state: wrapper base, `pInfo`, display filename tail, and inline real file object.
- `VTR_*` constants define trace-mask bits for file, shared-memory, mmap, dynamic loading, randomness, sleep, time, last-error, and VFS-level operations.
- `vfstrace_printf`, `vfstrace_print_errcode`, and `vfstrace_errcode_name` centralize formatted output and symbolic SQLite result names.
- `vfstraceFileControl` decodes many `SQLITE_FCNTL_*` opcodes, implements runtime `vfstrace` pragma parsing, and wraps `SQLITE_FCNTL_VFSNAME` output.
- `vfstraceOpen` dynamically copies only the real file methods supported by the underlying file method version and installs wrappers for methods that exist.

## Control Flow

Registration finds the root VFS, allocates one block containing `sqlite3_vfs`, `vfstrace_info`, and the VFS name, copies version/path-size information, sets wrapper callbacks conditionally for optional VFS methods, initializes the trace mask to all bits, emits an `enabled_for` line, and registers the VFS.

For `xOpen`, the wrapper stores the basename-like file tail, delegates to the root VFS, then if the real file has methods, allocates a fresh `sqlite3_io_methods` table for that file. This table mirrors the underlying method version and points supported methods to trace wrappers. On successful `xClose`, the dynamically allocated method table is freed.

Each wrapped method calls `vfstraceOnOff` with its mask, prints the call and decoded arguments if enabled, delegates to the real method, and prints the result. File controls include special formatting for size hints, mmap sizes, WAL/blocking controls, pragma controls, and returned values. The `vfstrace` pragma accepts numeric masks or names with `+`/`-`, ignores non-alpha separator characters, and accepts names with optional leading `x`.

## State And Persistence Behavior

All state is process-local. A registered trace VFS persists until explicitly unregistered or process exit. `vfstrace_info::mTrace` and `bOn` are mutable through pragma calls and affect all files using that trace VFS. Per-file method tables are heap allocated at open time and freed only after successful close. Trace output persistence is entirely defined by the caller's `xOut` callback.

The wrapper does not own the underlying VFS. It stores raw pointers to the root VFS and output callback/argument, so caller-provided state must outlive the registered trace VFS.

## Dependencies And Integration Points

The implementation uses SQLite's public VFS API, file I/O API, syscall override hooks for VFS version 3, and many `SQLITE_FCNTL_*` constants. It expects `sqlite3.h` to provide SQLite typedefs/macros and relies on C library formatting, `strtoll`, `isalpha`, and string utilities. It integrates with the shell's `-vfstrace` support or any embedding application that calls `vfstrace_register`.

## Risks And Edge Cases

- The output callback is called with messages allocated by `sqlite3_vmprintf`; failures are not checked before invoking `xOut`.
- `vfstraceOpen` allocates a method table after the real open; allocation failure is not handled before `memset`, so this diagnostic code assumes allocation succeeds.
- `vfstraceCheckReservedLock` has a format string expecting an extra `%d` but does not pass `*pResOut` before delegation; this is a diagnostic formatting defect.
- A typo in the pragma keyword table uses `"shmummap"` rather than `"shmunmap"`, so the intuitive spelling may not toggle that mask.
- Runtime mask state is stored on the shared VFS info object, not per connection.
- `vfstrace_unregister` can free a VFS while clients still hold open files if called incorrectly.
- Only path tails are printed for file methods, which is concise but can be ambiguous.

## Test Signals

Tests should register a trace VFS with a buffer-backed callback, open a database through it, and assert expected call lines and symbolic result names. Specific signals include `xOpen` method-table wrapping, `xClose` freeing, `xFileControl(SQLITE_FCNTL_VFSNAME)`, `PRAGMA vfstrace('-all,+Lock,Unlock')`, WAL shared-memory calls when supported, mmap fetch/unfetch when supported, unregister behavior, and preservation of root VFS return codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vfstrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vtablog.c -->
# Research: sources/storage-engines/sqlite/ext/misc/vtablog.c

## Purpose

`vtablog.c` implements a loadable virtual table module named `vtablog` that prints diagnostic messages to stdout whenever SQLite calls key virtual-table methods. It is an interactive teaching and debugging aid for understanding SQLite's virtual table planning, scanning, update, transaction, rename, shadow-name, and integrity callbacks.

The virtual table returns synthetic rows. Its behavior can be configured at `CREATE VIRTUAL TABLE` time with a declared schema, row count, and optional `ORDER BY` consumption rule.

## Important APIs, Types, And Functions

- `sqlite3_vtablog_init()` registers the `vtablog` module.
- `vtablog_vtab` stores schema/table names, configured row count, cursor counter, and `consume_order_by` setting.
- `vtablog_cursor` stores a cursor identifier and current rowid.
- `vtablogConnectCreate()` handles both `xCreate` and `xConnect`, prints argv details, parses `schema=`, `rows=`, and `consume_order_by=`, declares the requested schema, and initializes table state.
- `vtablogBestIndex()` prints `colUsed`, constraints, RHS values from `sqlite3_vtab_rhs_value`, collations from `sqlite3_vtab_collation`, order-by terms, `sqlite3_vtab_distinct`, and chosen estimates. It may set `orderByConsumed`.
- `vtablogFilter`, `vtablogNext`, `vtablogEof`, `vtablogColumn`, and `vtablogRowid` implement a simple rowid scan from 0 to `nRow-1` while printing each callback.
- `vtablogUpdate` prints INSERT/UPDATE/DELETE arguments but does not change table content.
- Transaction methods (`xBegin`, `xSync`, `xCommit`, `xRollback`, savepoint methods), `xFindMethod`, `xRename`, `xShadowName`, and `xIntegrity` are implemented for observability.

## Control Flow

Creating or connecting prints module arguments and parses options from arguments 3 onward. If no schema is supplied, it declares `CREATE TABLE x(a,b);`. The table object stores `argv[1]` and `argv[2]` as display names and defaults to ten rows.

Planning prints all constraint/order metadata and assigns a fixed estimated cost and row count. If `consume_order_by=N` was configured and the first order-by term matches column `N-1` ascending, or `-N` descending, `orderByConsumed` is set.

Scanning allocates a cursor with a unique display id, initializes rowid to zero on `xFilter`, increments on `xNext`, reports EOF when `iRowid >= nRow`, returns generated text values for each column, and returns rowid equal to `iRowid`. Updates and transaction callbacks only log invocation.

## State And Persistence Behavior

The module has no durable storage. `nRow`, `iConsumeOB`, and display names live in each virtual-table object. `nCursor` monotonically increases for the table object's lifetime. Rows are generated on demand and all writes are no-ops that return success. `xRename` updates only the in-memory display name used in later log messages.

All diagnostic output goes to stdout through `printf`, so callers must manage stdout capture if using it in automated tests.

## Dependencies And Integration Points

The file uses the SQLite loadable-extension ABI and virtual-table API version 4, including newer callbacks such as `xShadowName` and `xIntegrity`, and planner helpers `sqlite3_vtab_rhs_value`, `sqlite3_vtab_collation`, and `sqlite3_vtab_distinct`. It depends on standard C stdio, string, ctype, assert, and stdlib.

## Risks And Edge Cases

- `vtablog_trim_whitespace()` checks `z[n]` instead of `z[n-1]` in its loop, so trailing whitespace trimming is ineffective for the last real character.
- Output is synchronous stdout logging with no mutexing or structured log sink.
- `vtablogColumn` uses the string `"abcdefghijklmnopqrstuvwyz"`, which omits `x`; generated labels are only diagnostic.
- `xUpdate` reports success without modifying any state, which can surprise users treating it as a real writable table.
- `xBestIndex` does not use constraints to improve scans; it only demonstrates planner metadata.
- `xShadowName` classifies any name containing `"shadow"` as a shadow table, purely for testing interface behavior.

## Test Signals

Useful tests load the extension, create a table with custom schema/row count, run SELECTs with constraints, collations, RHS constants, order-by terms, updates, transactions, savepoints, rename, integrity checks, and table names containing `"shadow"`. Expected stdout should show method order and planner metadata. Result tests should verify generated rows and `orderByConsumed` behavior when configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vtablog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vtshim.c -->
# Research: sources/storage-engines/sqlite/ext/misc/vtshim.c

## Purpose

`vtshim.c` provides a shim between SQLite's virtual table interface and runtimes with garbage-collected or externally managed module lifetimes. It exposes `sqlite3_create_disposable_module()` and `sqlite3_dispose_module()` so a host can register a module, later mark it disposed, close/disconnect active child objects, and prevent further calls into freed managed code.

The shim wraps a caller-supplied `sqlite3_module`, forwarding calls while the module is active and returning errors or EOF-like values after disposal.

## Important APIs, Types, And Functions

- `sqlite3_create_disposable_module(db, zName, p, pClientData, xDestroy)` copies the child module, builds a wrapper module, registers it with `sqlite3_create_module_v2`, and returns a `vtshim_aux *` handle.
- `sqlite3_dispose_module(void *pX)` closes all active child cursors, disconnects all active child vtabs, marks the module disposed, and invokes the child auxiliary destructor once.
- `vtshim_aux` owns child aux data/destructor, copied child module, database pointer, module name, disposed flag, list of active wrapper vtabs, and the wrapper `sqlite3_module`.
- `vtshim_vtab` tracks the child vtab and list links back to the owning aux plus active cursors.
- `vtshim_cursor` tracks the child cursor and cursor-list links.
- `VTSHIM_COPY_ERRMSG()` copies child `zErrMsg` into the wrapper vtab error message after forwarded failures.
- Wrapper methods from `xCreate` through `xRollbackTo` forward to corresponding child callbacks when present and not disposed.
- `vtshimAuxDestructor()` is registered with SQLite to release copied module state and child aux data after SQLite no longer references the module.

## Control Flow

Module creation allocates aux state, copies the supplied module, stores the caller's aux/destructor, creates a wrapper module with callbacks only where the child module has callbacks, caps wrapper `iVersion` at 2, and registers the wrapper with SQLite. If allocation or registration fails, it attempts to clean up and returns NULL.

`xCreate`/`xConnect` reject calls after disposal, allocate a wrapper vtab, call the child method with child aux data, and link the wrapper into `pAllVtab`. `xOpen` allocates a wrapper cursor, calls child `xOpen`, sets the child cursor's `pVtab` to the child vtab, returns the wrapper cursor, and links it into the vtab cursor list.

Most cursor/table methods check `bDisposed`, forward to the child, and copy errors on non-OK results. `xDisconnect`/`xDestroy` and `xClose` skip child calls after disposal but always unlink and free wrapper objects. `sqlite3_dispose_module` walks all active vtabs/cursors and calls the child close/disconnect methods directly, then flips `bDisposed`, preventing later wrapper calls from re-entering child code.

## State And Persistence Behavior

State is connection-local and heap-allocated. The shim persists as a registered SQLite module until SQLite invokes the `sqlite3_create_module_v2` destructor. Disposal is not transactional and has immediate effects on all active wrapper objects. Active wrapper cursor/vtab allocations remain until SQLite closes/disconnects them, but their child objects are closed/disconnected during disposal and future calls are blocked or treated as EOF.

The child module is copied by value, so the original `sqlite3_module` memory may be reclaimed by the caller after successful registration. Child aux data is owned by the shim after creation and destroyed at disposal or final aux destruction.

## Dependencies And Integration Points

The code depends on SQLite loadable-extension and virtual-table APIs and is compiled out if `SQLITE_OMIT_VIRTUALTABLE` is defined. It integrates with managed bindings or extension systems that need a deterministic unregister/dispose signal without relying on SQLite to stop calling function pointers immediately.

## Risks And Edge Cases

- `sqlite3_dispose_module` calls child `xClose`/`xDisconnect` but does not null child pointers. Later wrapper `xClose`/`xDisconnect` skips child calls due to `bDisposed`, so this is intentional but relies on the disposed flag.
- Disposal walks linked lists while child close/disconnect code could theoretically interact with SQLite and mutate lists; this is a reentrancy risk.
- `vtshimAuxDestructor` asserts `pAllVtab==0`; if SQLite destroys the module while wrappers remain, this assertion indicates lifecycle misuse.
- If `vtshimCopyModule` fails after aux allocation, the child destructor is not invoked in that branch, unlike the first allocation-failure path.
- Wrapper `iVersion` is capped at 2, so newer module callbacks such as `xShadowName` and `xIntegrity` are not forwarded.
- Some methods copy child error messages even when the child callback's boolean return semantics are not SQLite status codes, such as `xEof` and `xFindFunction`.

## Test Signals

Tests should wrap a mock module, verify normal forwarding for create/connect/open/filter/next/column/rowid/update/transaction callbacks, then call `sqlite3_dispose_module` with active cursors and vtabs and assert child close/disconnect/destructor calls occur once. After disposal, new creates/connects should fail with a clear error, scans should return EOF or errors as coded, and later SQLite close/disconnect should not call child methods again.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/vtshim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/wholenumber.c -->
# Research: sources/storage-engines/sqlite/ext/misc/wholenumber.c

## Purpose

`wholenumber.c` implements a simple virtual table named `wholenumber` that generates integer values from 1 through 4,294,967,295. It is explicitly marked testing/debug-only, with guidance to use `generate_series()` for real applications.

The table has one column, `value`, and supports simple range constraints and ascending order-by consumption.

## Important APIs, Types, And Functions

- `sqlite3_wholenumber_init()` registers the module when virtual tables are enabled.
- `wholenumber_cursor` stores current `iValue` and maximum `mxValue`.
- `wholenumberConnect()` allocates a minimal `sqlite3_vtab`, declares `CREATE TABLE x(value)`, and marks it `SQLITE_VTAB_INNOCUOUS`.
- `wholenumberBestIndex()` recognizes usable `value >`, `>=`, `<`, and `<=` constraints, assigns argument indexes, omits handled constraints, consumes a single ascending order-by, and sets rough estimated costs.
- `wholenumberFilter()` converts `idxNum` bits and constraint arguments into inclusive cursor start/end bounds.
- `wholenumberNext`, `wholenumberEof`, `wholenumberColumn`, and `wholenumberRowid` implement the generator.

## Control Flow

Planning scans constraints once, selecting at most one lower-bound operator and one upper-bound operator. It encodes the selected operators into `idxNum` bits: `1` for `>`, `2` for `>=`, `4` for `<`, and `8` for `<=`. The lower-bound constraint is assigned argv slot 1 and the upper-bound slot 2 when both exist.

Filtering initializes the cursor to `[1, 0xffffffff]`, then applies lower and upper bounds. Exclusive lower bounds increment the value; exclusive upper bounds decrement the maximum. Scanning increments by one until the current value exceeds the maximum or becomes zero.

## State And Persistence Behavior

There is no persistent state. Each cursor holds its current range. The virtual table object has no custom fields beyond the base allocation. Results are deterministic for a given constraint set.

## Dependencies And Integration Points

The file uses SQLite extension and virtual-table APIs, including `sqlite3_declare_vtab`, `sqlite3_vtab_config(SQLITE_VTAB_INNOCUOUS)`, and planner structures. It is compiled out when `SQLITE_OMIT_VIRTUALTABLE` is defined.

## Risks And Edge Cases

- Unbounded scans are enormous; without an upper bound, estimated cost is set very high but the table can still generate billions of rows.
- Constraint variable names `ltIdx` and `gtIdx` are semantically reversed for lower/upper bounds, which can confuse maintenance.
- Values less than or equal to zero and bounds above `0xffffffff` are clamped through filter logic rather than reported as errors.
- Only ascending order is consumed; descending output is not supported.
- It is not production-oriented and may lag behind `generate_series()` features and safety.

## Test Signals

Tests should query unconstrained and constrained ranges, including `value<10`, `value<=1`, `value>4294967294`, empty ranges, combined exclusive/inclusive bounds, ascending order-by plans, and behavior with negative or oversized bounds. `EXPLAIN QUERY PLAN` can verify constraint omission and order-by consumption.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/wholenumber.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/windirent.h -->
# Research: sources/storage-engines/sqlite/ext/misc/windirent.h

## Purpose

`windirent.h` is a Windows/MSVC-only compatibility header that provides static `opendir()`, `readdir()`, and `closedir()` implementations using Win32 `_wfindfirst`, `_wfindnext`, and `_findclose`. On non-Windows or non-MSVC builds it is a no-op.

The shim allows SQLite extension code that expects POSIX-like directory iteration to compile on Windows while using UTF-8 directory names externally.

## Important APIs, Types, And Functions

- The header is enabled only when `_WIN32`, `_MSC_VER`, and not `SQLITE_WINDIRENT_H` are defined.
- It defines missing POSIX-like macros `S_ISREG`, `S_ISDIR`, `S_ISLNK`, a `mode_t` typedef, and a compact `struct dirent` with `d_ino`, `d_attributes`, and `d_name`.
- `DIR` stores a Win32 find handle and current `dirent`.
- `WindowsFileToIgnore()` filters hidden and system files.
- `opendir(const char *zDirName)` converts a UTF-8 path to UTF-16, appends `\*`, opens `_wfindfirst`, skips hidden/system entries, and returns a heap-allocated `DIR`.
- `readdir(DIR *pDir)` returns the cached first entry on first call, then loops `_wfindnext` skipping hidden/system entries and converting names back to UTF-8.
- `closedir(DIR *pDir)` closes the find handle when valid and frees the `DIR`.

## Control Flow

`opendir` allocates and clears a `DIR`, converts the supplied UTF-8 directory path to a wide string, appends a wildcard, copies it into `_wfinddata_t.name`, and starts iteration. It skips ignored entries immediately so the first `readdir` returns the first visible entry. `readdir` uses `d_ino` as a first-read sentinel/counter: the first call returns the cached entry and later calls fetch from the Win32 iterator.

## State And Persistence Behavior

State is entirely per-`DIR` and process-local. No directory contents are persisted. Returned `struct dirent *` points into the `DIR` and remains valid only until the next `readdir` or `closedir`.

## Dependencies And Integration Points

The header depends on Windows headers, MSVC/CRT `_wfinddata_t`, `_wfindfirst`, `_wfindnext`, `_findclose`, UTF conversion APIs, and SQLite memory allocation (`sqlite3_malloc64`, `sqlite3_free`). It is meant to be included inside C modules that already include SQLite definitions.

## Risks And Edge Cases

- Hidden and system files are silently skipped, which differs from POSIX `readdir`.
- `MultiByteToWideChar` is called with `sz` as both input length and output capacity after allocating `sz+3`; non-ASCII expansion is safe for UTF-16 code units in normal cases but conversion failure is not checked.
- Paths longer than `_wfinddata_t.name` capacity fail.
- `closedir(NULL)` returns `EINVAL` directly rather than `-1` with `errno`.
- `d_ino` is synthetic and used as an internal counter; applications cannot rely on inode semantics.
- The implementation uses backslash wildcard appending and may not handle paths already ending in a slash uniformly.

## Test Signals

Windows/MSVC tests should include UTF-8 directory names, first-entry caching, hidden/system file filtering, end-of-directory handling, long-path rejection, repeated open/close, and compatibility with code expecting only `d_name`. Non-Windows builds should verify including the header does not define symbols or change behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/windirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/zipfile.c -->
# Research: sources/storage-engines/sqlite/ext/misc/zipfile.c

## Purpose

`zipfile.c` implements SQLite's `zipfile` extension: a virtual table for reading and writing ZIP archives and an aggregate SQL function that builds an archive blob from rows. It exposes archive entries as rows with name, POSIX mode, modification time, uncompressed size, raw compressed data, uncompressed data, compression method, and hidden archive argument/cursor id.

The implementation supports ordinary single-file ZIP archives with classic 32-bit fields and methods 0 (stored) and 8 (deflate). It explicitly does not support encryption, split archives, zip64, or compression methods beyond inflate/deflate.

## Important APIs, Types, And Functions

- `sqlite3_zipfile_init()` registers the module and aggregate through `zipfileRegister`.
- `ZIPFILE_SCHEMA` declares `name PRIMARY KEY, mode, mtime, sz, rawdata, data, method, z HIDDEN` as a WITHOUT ROWID virtual table.
- `ZipfileEOCD`, `ZipfileCDS`, and `ZipfileLFH` model ZIP end-of-central-directory, central-directory, and local-file-header records.
- `ZipfileEntry` stores parsed central-directory metadata, Unix mtime, extra/comment data, compressed data offset or in-memory bytes, and linked-list state.
- `ZipfileTab` stores the archive filename, DB handle, scratch buffer, active cursors, and write-transaction state (`pFirstEntry`, `pWriteFd`, `szCurrent`, `szOrig`).
- `ZipfileCsr` stores file-backed scan state, in-memory scan state, current entry, and cursor id.
- Parsing helpers include `zipfileReadEOCD`, `zipfileReadCDS`, `zipfileReadLFH`, `zipfileGetEntry`, `zipfileScanExtra`, and endian read/write helpers.
- Compression helpers `zipfileInflate` and `zipfileDeflate` use zlib raw deflate streams (`windowBits=-15`).
- Write helpers include `zipfileBegin`, `zipfileUpdate`, `zipfileAppendEntry`, `zipfileSerializeLFH`, `zipfileSerializeCDS`, `zipfileCommit`, and `zipfileRollback`.
- `zipfileStep`/`zipfileFinal` implement the aggregate `zipfile()` builder.
- `zipfileFindFunction` exposes `zipfile_cds(cursor_id)` for rows of this virtual table.

## Control Flow

Connecting validates constructor usage: an eponymous `zipfile` table may be called without a fixed filename, but a differently named virtual table must supply exactly one filename argument. It declares the schema, allocates one table object plus a 200 KiB scratch buffer, dequotes a fixed filename when present, and marks the table `SQLITE_VTAB_DIRECTONLY`.

Planning looks for an equality constraint on hidden column `z`. Eponymous use such as `zipfile($filename)` passes the archive filename/blob as this hidden argument. If a hidden-column constraint is present but unusable, planning returns `SQLITE_CONSTRAINT`.

Filtering resets the cursor, determines whether to read a fixed table filename, a filename argument, or a BLOB containing an entire archive image, then loads or scans the central directory. File-backed scans open the archive read-only, locate EOCD by scanning backward over the last up to 200 KiB, set `iNextOff` to the central directory offset, and parse entries lazily with `zipfileNext`. Blob-backed scans load entries into memory and copy compressed data into each entry.

Column access returns metadata directly, reads raw compressed bytes from the archive when needed, inflates data for `data` when method is 8, returns stored data directly for method 0, and returns SQL NULL for directories. Zero-length non-directories return an empty blob.

Writes begin lazily from `xUpdate` if no write transaction is active. `zipfileBegin` opens the archive `ab+`, records original/current size, and loads the existing central directory into memory. `zipfileUpdate` handles DELETE, INSERT, and UPDATE by removing old list entries, validating `sz`/`rawdata` are NULL for writes, deriving directory status from `data IS NULL`, validating mode, normalizing directory names to end in `/`, choosing/storing compression, writing the new local header and data at the current end, and inserting a new central-directory entry in memory. `zipfileCommit` appends all central-directory records plus EOCD, then cleans transaction state. `zipfileRollback` currently calls `zipfileCommit`, so transaction rollback does not restore the original archive.

The aggregate builder follows the same entry serialization rules but accumulates body and central-directory buffers in memory, then returns a single blob containing body, CDS records, and EOCD.

## State And Persistence Behavior

Read-only scans maintain either an open `FILE *` with lazy current-entry parsing or an in-memory linked list derived from a blob. A fixed-filename virtual table stores `zFile`; eponymous calls pass filename/blob through the hidden column. The hidden `z` output for scanned rows is a cursor id used by `zipfile_cds()`.

Write transactions append new local file headers and data immediately to the archive file, while central-directory state is kept in memory until commit. Existing entries remain physically present in the file when deleted or replaced; they are omitted from the newly appended central directory. This append-only rewrite style can grow archives and depends on readers honoring the last EOCD. `szOrig` is recorded but not used to truncate on rollback, and `xRollback` commits, so SQLite rollback semantics are not durable for archive file side effects.

The aggregate function stores all generated archive bytes in memory until finalization. ZIP timestamps are stored in both DOS date/time fields and a 0x5455 extended timestamp extra field for new entries.

## Dependencies And Integration Points

The file depends on SQLite extension, virtual-table, aggregate-function, memory, VFS time, conflict-policy, and overload-function APIs; zlib for `crc32`, `deflate`, and `inflate`; stdio for file I/O; and optional `sqlite3_stdio.h` remapping for CLI builds. It includes local POSIX mode constants to avoid platform header dependencies.

Integration points are SQL queries against `zipfile(...)`, writable virtual tables created with a fixed archive filename, the `zipfile()` aggregate, `zipfile_cds()` virtual-table function, SQLite conflict policies for duplicate names (`IGNORE`, `REPLACE`, default constraint), and the default VFS clock for write mtimes.

## Risks And Edge Cases

- Zip64, encryption, split archives, and unsupported compression methods are rejected or misread by design.
- File I/O uses `fseek`/`ftell` with casts to `long`, which can limit very large archive support on some platforms.
- EOCD scanning only covers the last 200 KiB, enough for normal comments but still bounded.
- Embedded NULs in filenames are copied safely into allocated buffers, but most later path handling uses C-string functions, so such names remain risky.
- `zipfileRollback()` calls `zipfileCommit()`, so SQL rollback does not undo writes to the archive; this is the most important persistence hazard.
- Deletes/replaces append a new central directory but do not reclaim old file bytes.
- `zipfileGetMode` requires mode/data consistency; callers must use `data NULL` for directories and non-NULL for files/symlinks.
- Duplicate detection ignores trailing `/`, so directory/file naming collisions are treated specially.
- New entries cap filename length at 250 bytes for Windows compatibility.
- `zipfileInflate` assumes the uncompressed size from headers and returns errors if zlib does not end exactly as expected.

## Test Signals

Tests should cover reading file-backed and blob-backed archives, empty archives, central-directory corruption, malformed LFH/CDS signatures, extended timestamps, DOS timestamp fallback, directory entries, zero-length files, stored and deflated entries, unsupported compression methods, `rawdata` vs `data`, and `zipfile_cds()`. Write tests should cover insert/update/delete, duplicate names with default/IGNORE/REPLACE conflict policies, directory slash normalization, mode parsing in numeric and string forms, aggregate construction for 2/4/5 argument forms, large filenames rejection, and the documented rollback/append-only behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/zipfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/zorder.c -->
# Research: sources/storage-engines/sqlite/ext/misc/zorder.c

## Purpose

`zorder.c` implements two scalar SQL functions for Morton/Z-order transformations. `zorder(X0, X1, ..., XN)` interleaves bits from 2 to 24 integer dimensions into one signed 64-bit Morton code. `unzorder(Z, N, K)` extracts dimension `K` from an `N`-dimensional Morton code.

The extension is useful for compact spatial indexing experiments where multiple integer dimensions need to be mapped into a single sortable key.

## Important APIs, Types, And Functions

- `sqlite3_zorder_init()` registers `zorder` with variable arity and `unzorder` with arity 3.
- `zorderFunc()` validates argument count, reads up to 24 integer coordinates, interleaves the low 63 bits round-robin by dimension, returns the Morton code, then reports an error if any coordinate had remaining high bits.
- `unzorderFunc()` validates `N` in `[2,24]` and `K` in `[0,N-1]`, then collects every `N`th bit from `Z` starting at bit `K` into the result coordinate.

## Control Flow

`zorderFunc` initializes `z` to zero and copies all inputs to a local array. For bit positions 0 through 62, it selects dimension `i % argc`, ORs that dimension's low bit into output bit `i`, then shifts the dimension right. After returning the integer result, it scans dimensions for leftover bits and sets an error if any input was too large to fit in the 63-bit interleaving budget.

`unzorderFunc` performs straightforward validation, then loops `j=K; j<63; j+=N`, moving bits from the Morton code into consecutive bits of `x`.

## State And Persistence Behavior

There is no persistent state. Both functions are pure with respect to SQLite database contents, although they are not registered with deterministic/innocuous flags in this file.

## Dependencies And Integration Points

The file uses SQLite's loadable-extension ABI and scalar function API. It depends only on SQLite integer conversion/result/error helpers and standard string/assert headers. It integrates by registering functions into the current database connection.

## Risks And Edge Cases

- The error message says `"arguments4"`, which appears to be a typo.
- `zorderFunc` calls `sqlite3_result_int64` before checking overflow and then may overwrite it with an error; SQLite should report the later error, but the ordering is unusual.
- Negative inputs shift arithmetically on many C implementations, leaving high bits set and causing a "too large" error after constructing an intermediate code.
- Only 63 bits are used to avoid signed 64-bit sign-bit complications, so capacity per dimension shrinks as dimensions increase.
- Inputs are coerced with `sqlite3_value_int64`; non-integer SQL values follow SQLite conversion rules.

## Test Signals

Tests should verify round trips for 2D, 3D, and 24D values; boundary values that exactly fit the available bit budget; oversized and negative input errors; invalid argument counts for `zorder`; invalid `N` and `K` for `unzorder`; and SQL type coercion behavior. Sorting by `zorder()` over grid points can validate expected Morton ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/misc/zorder.c -->
