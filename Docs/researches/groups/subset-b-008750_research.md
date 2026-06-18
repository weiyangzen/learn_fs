# subset-b-008750 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.c -->
# sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.c

## Purpose

`sqlite3rbu.c` implements SQLite's Resumable Bulk Update extension. It applies large INSERT/UPDATE/DELETE batches from a separate RBU database to a target database while keeping partial work hidden from ordinary readers, then makes the update visible by renaming an `*-oal` file to `*-wal` and incrementally checkpointing it. The same implementation also supports resumable RBU vacuum, where the target is rebuilt into a temporary database-like image and then checkpointed. The file includes the public API implementation, SQL-generation machinery for target table/index updates, persistent state handling, a Fossil-delta SQL helper, and a custom VFS shim that redirects WAL operations and captures checkpoint I/O.

## Important APIs, Types, and Functions

The opaque public handle is `struct sqlite3rbu`. It owns the target and RBU `sqlite3` handles, path/state strings, current stage, error state, object iterator, RBU VFS name, target file descriptor, checkpoint frame list, progress counters, temp-space accounting, and rename callback. `RbuState` mirrors rows in `rbu_state`; its fields store current stage, target/data table, index, row offset, progress, WAL checksum, database cookie, OAL size, and phase-one estimate. `RbuObjIter` walks all RBU source tables and associated target b-trees, caching target column metadata, PK/index shape, SQL statements, and an LRU list of generated UPDATE statements. `rbu_vfs` and `rbu_file` implement the VFS layer used to intercept WAL/OAL/shm/temp-file behavior.

Public entry points are `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_step()`, `sqlite3rbu_savestate()`, `sqlite3rbu_close()`, `sqlite3rbu_db()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, `sqlite3rbu_state()`, `sqlite3rbu_rename_handler()`, `sqlite3rbu_create_vfs()`, `sqlite3rbu_destroy_vfs()`, `sqlite3rbu_temp_size_limit()`, and `sqlite3rbu_temp_size()`. `openRbuHandle()` is the central constructor used by both open modes.

Major internal subsystems include Fossil-delta helpers (`rbuDeltaGetInt()`, `rbuDeltaApply()`, `rbuFossilDeltaFunc()`), object iteration (`rbuObjIterFirst()`, `rbuObjIterNext()`, `rbuObjIterPrepareAll()`), target metadata discovery (`rbuTableType()`, `rbuObjIterCacheTableInfo()`, `rbuObjIterCacheIndexedCols()`), imposter-table creation (`rbuCreateImposterTable()`, `rbuCreateImposterTable2()`), SQL list generation (`rbuObjIterGetCollist()`, `rbuObjIterGetWhere()`, `rbuObjIterGetSetlist()`, `rbuObjIterGetIndexCols()`), statement execution (`rbuStepType()`, `rbuStepOneOp()`, `rbuStep()`), state persistence (`rbuLoadState()`, `rbuSaveState()`, `rbuSetupOal()`), and checkpoint preparation (`rbuSetupCheckpoint()`, `rbuCaptureWalRead()`, `rbuCaptureDbWrite()`, `rbuCheckpointFrame()`).

## Control Flow

`sqlite3rbu_open()` validates arguments and calls `openRbuHandle()`, which creates a private RBU VFS, opens the RBU/state/target databases through it, creates or attaches the `rbu_state` table, registers helper SQL functions, loads saved state, checks the database cookie, and configures the first stage. New updates start in `RBU_STAGE_OAL`; resumed updates may restart in OAL, move, checkpoint, or done state. WAL-mode target databases are rejected for normal updates because RBU needs to build a hidden OAL before exposing WAL content.

During `RBU_STAGE_OAL`, each `sqlite3rbu_step()` advances the `RbuObjIter`. For each source `data_*` table, the iterator visits the target table b-tree, then each auxiliary index b-tree, then a cleanup state. `rbuObjIterPrepareAll()` lazily builds the SQL needed for the current object. Table b-trees are modified through imposter tables unless the target is a virtual table. Index b-trees are updated by creating a WITHOUT ROWID imposter table over the index root page and selecting sorted keys from `data_*` or state temp tables. `rbuStep()` interprets `rbu_control` as insert, delete, replace, index delete, index insert, or update mask and executes one logical operation. When all objects are processed, RBU saves move-stage state, increments the schema cookie, commits both databases, and advances to `RBU_STAGE_MOVE`.

During `RBU_STAGE_MOVE`, `rbuMoveOalFile()` closes and reopens handles, obtains an exclusive lock, renames `*-oal` to `*-wal` through either the default or user-supplied rename callback, then reopens the database and initializes checkpoint capture. In `RBU_STAGE_CKPT`, each `sqlite3rbu_step()` copies WAL frames into the database file. It checkpoints enough adjacent frames to avoid saving state mid-sector when the sector size is larger than the page size, syncs the database at completion, updates WAL-index backfill, sets `RBU_STAGE_DONE`, and returns `SQLITE_DONE`.

`sqlite3rbu_close()` commits any pending OAL transaction, syncs during checkpoint state, saves `rbu_state`, closes statements and database handles, tears down the private VFS, returns or frees the error message, and releases all allocations. `sqlite3rbu_savestate()` is an explicit mid-run checkpoint: it commits OAL work, syncs if checkpointing, writes `rbu_state`, and reopens transactions so further `step()` calls may continue.

## State and Persistence Behavior

The durable state table is `%s.rbu_state(k INTEGER PRIMARY KEY, v)`. Keys encode stage, target table, index, row offset, progress, checkpoint checksum, database change-counter cookie, OAL size, phase-one step estimate, and current RBU data table. This lets a later process resume within a table/index by skipping rows with `LIMIT -1 OFFSET n` or, for RBU vacuum, by deriving key-range starts when possible.

The target database is not modified directly in rollback journal mode. OAL-stage modifications are written through SQLite WAL machinery to an `*-oal` file whose existence is hidden from ordinary clients. The VFS records the original page-1 change-counter cookie and rejects resume if it no longer matches, which detects an external writer between suspend and resume. Once OAL is renamed to WAL, the update becomes visible to ordinary readers before checkpointing finishes.

Checkpoint persistence uses the saved row count (`RBU_STATE_ROW`) as the number of already checkpointed frame entries plus a saved WAL-index checksum. On resume, `rbuSetupCheckpoint()` captures the would-be checkpoint frame list again and compares the WAL-index checksum to the saved value. If another client has appended frames, RBU treats the operation as done rather than continuing a stale incremental checkpoint.

Temp-file state is tracked per VFS file via `rbuUpdateTempSize()` and aggregated in `sqlite3rbu.szTemp`; the public limit API can force `SQLITE_FULL` if temporary files grow beyond the configured threshold. RBU vacuum may create a state database and an internal `-vactmp` target and copies target schema plus selected PRAGMAs into the rebuilt database.

## Dependencies and Integration Points

This file depends heavily on SQLite's public C API and a small number of SQLite-specific extension hooks: `SQLITE_TESTCTRL_IMPOSTER` for writing directly to table/index b-trees, `SQLITE_FCNTL_RBU` and `SQLITE_FCNTL_RBUCNT` for VFS file-control plumbing, `SQLITE_FCNTL_ZIPVFS` and a copied ZipVFS file-pointer control for ZipVFS compatibility checks, WAL shared-memory locking conventions, URI options, and schema/PRAGMA introspection. It registers SQL functions `rbu_target_name`, `rbu_tmp_insert`, `rbu_fossil_delta`, and optionally `rbu_index_cnt`.

Input integration is through RBU database tables or views named `data_<target>` or `dataNNN_<target>`, optional `rbu_count`, and `rbu_control` values. Target integration covers ordinary rowid tables, INTEGER PRIMARY KEY tables, external primary-key tables, WITHOUT ROWID tables, and virtual tables. For virtual tables and no-PK tables, `rbu_rowid` is required. For partial indexes and expression indexes, the code reads `sqlite_schema.sql` and `PRAGMA index_xinfo` to generate the right sorted data streams and imposter table shape.

The VFS layer integrates by wrapping a parent VFS and proxying all normal operations except when RBU stage-specific behavior is required. It can be automatically private per handle or explicitly created for ZipVFS stacks. Rename integration is injectable via `sqlite3rbu_rename_handler()`, which is important for tests and for non-POSIX storage layers.

## Risks and Edge Cases

The file itself documents risks around non-portable rename behavior, lack of atomicity between OAL commits and RBU-state commits, and unclear recovery when an external writer changes the target mid-update. The implementation mitigates some of this with page-1 cookie checks and checkpoint checksums, but the OAL/state split still leaves crash windows where replay may see constraint errors or already-applied work.

The VFS shim is highly sensitive to SQLite WAL internals: WAL lock numbers, page-header offsets, WAL frame layout, shared-memory checksum offsets, and file-name pointer identity are assumed stable. Bugs in this layer could expose partial updates, accidentally checkpoint OAL content, leak SHM locks, or mis-handle stacked VFS configurations. `rbuVfsAccess()` deliberately returns `SQLITE_CANTOPEN` if an existing WAL is detected during OAL stage, so damaged page-1 state or unusual VFS behavior can surface as open failures.

SQL generation is complex for expression indexes, partial indexes, external primary keys, WITHOUT ROWID tables, virtual tables, update masks, and `rbu_delta`/`rbu_fossil_delta`. Invalid `rbu_control` values produce `SQLITE_ERROR`; NULL explicit INTEGER PRIMARY KEY insertions produce `SQLITE_MISMATCH`. If a user-defined `rbu_delta()` is not registered when a mask uses `d`, execution fails through SQLite statement errors.

RBU vacuum has additional risk because it synthesizes page-1 reads and creates a target schema under `PRAGMA writable_schema=1`. It refuses WAL-mode vacuum cases and reserves state names ending in `-vactmp`, but any mismatch between source schema, state database, and VFS stack can leave an error state and reset vacuum state tables.

## Test Signals

The companion `test_rbu.c` exposes the public API to Tcl tests. The surrounding RBU test suite in `ext/rbu` exercises ordinary updates, vacuum, resumption, busy handling, crashes, faults, rename handling, progress, temp-size limits, FTS/virtual tables, collations, partial indexes, split state databases, and VFS behavior. Implementation-level assertions also signal invariants around iterator state, WAL locks, stage transitions, and imposter-table assumptions.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.h -->
# sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.h

## Purpose

`sqlite3rbu.h` declares the public C interface and user-facing contract for the RBU extension. Its long header comments define what an RBU update is, how an RBU database must be laid out, how resumable updates and RBU vacuum work, which SQL features are intentionally unsupported, what locking behavior callers should expect, and how applications should drive the API.

## Important APIs, Types, and Constants

The only public type is opaque `sqlite3rbu`. Applications allocate it with `sqlite3rbu_open()` for update mode or `sqlite3rbu_vacuum()` for vacuum mode, drive work with `sqlite3rbu_step()`, optionally force state persistence with `sqlite3rbu_savestate()`, and release it with `sqlite3rbu_close()`.

`sqlite3rbu_db()` exposes the internal target or RBU database handle so callers can register virtual table modules or SQL functions such as `rbu_delta()`. `sqlite3rbu_progress()` returns a monotonically increasing count of key-value operations. `sqlite3rbu_bp_progress()` reports two permyriad progress values: phase one for building OAL/WAL content and phase two for checkpointing. `sqlite3rbu_state()` returns `SQLITE_RBU_STATE_OAL`, `SQLITE_RBU_STATE_MOVE`, `SQLITE_RBU_STATE_CHECKPOINT`, `SQLITE_RBU_STATE_DONE`, or `SQLITE_RBU_STATE_ERROR`.

`sqlite3rbu_rename_handler()` allows callers to replace the default filesystem rename used when moving `*-oal` to `*-wal`. `sqlite3rbu_create_vfs()` and `sqlite3rbu_destroy_vfs()` expose the RBU VFS shim for explicit VFS stack construction, especially with ZipVFS. `sqlite3rbu_temp_size_limit()` and `sqlite3rbu_temp_size()` configure and report aggregate temporary-file usage.

## Control Flow

The intended update loop is: open a handle, register required modules/functions on handles returned by `sqlite3rbu_db()`, call `sqlite3rbu_step()` until it returns something other than `SQLITE_OK`, then call `sqlite3rbu_close()` and inspect both return code and optional error message. A partial run can be stopped with `sqlite3rbu_close()` or `sqlite3rbu_savestate()`; later callers use the same target/RBU/state paths to resume.

The header divides execution into visible stages. In OAL state, RBU is building a hidden `*-oal` file and ordinary clients keep reading the old database. In MOVE state, the next step renames the OAL to WAL and makes the update visible. In CHECKPOINT state, RBU copies WAL pages back into the database incrementally. DONE and ERROR are terminal states for the current handle.

For RBU vacuum, callers open with `sqlite3rbu_vacuum(target, state)`, repeatedly step, and close. The state database may be explicit or default to `<database>-vacuum`. State database names ending in `-vactmp` are reserved for internal use.

## State and Persistence Behavior

If `zState` is NULL for update mode, state is stored inside the RBU database. If non-NULL, it names a separate state database that must be reused for resumption. For vacuum mode, the state database is not automatically deleted on success; if close returns an error, the implementation clears the state tables so the next vacuum begins from scratch.

The header emphasizes that a suspended update may be resumed after process exit or crash from the most recently saved state. It also documents that if an external client writes to the target database between suspension and resumption, resuming returns `SQLITE_BUSY`.

Temp-space state is exposed as a per-handle aggregate. A nonzero limit causes `SQLITE_FULL` if RBU's temporary files exceed it. Progress state depends on optional `rbu_count`; if present and correctly populated, phase-one progress can be estimated, otherwise phase one reports `-1`.

## Dependencies and Integration Points

The header includes `sqlite3.h` for SQLite types and result codes and supports C++ callers with `extern "C"`. It requires callers to create RBU source tables named `data_<target>` or `dataNNN_<target>`, each with target columns plus `rbu_control` and sometimes `rbu_rowid`. `rbu_control` integer values represent insert/delete/replace, while text masks with `x`, `.`, `d`, and `f` describe updates and delta application.

Target virtual tables require callers to register modules on the target handle. RBU source virtual tables or views require modules on the RBU handle. Use of `d` update masks requires a caller-provided `rbu_delta()` function. Fossil-delta masks use the built-in implementation from the C file. ZipVFS integration requires an explicit VFS stack with the RBU VFS below ZipVFS and above lower storage layers.

## Risks and Contract Limits

RBU transactions are limited to INSERT, UPDATE, and DELETE semantics. Defaults, triggers, foreign-key checks, CHECK constraints, and most conflict handling are not supported. UPDATE and DELETE must identify rows by non-NULL primary-key values or rowid, and UPDATE may not modify primary-key columns. RBU does not run a general SQL transaction engine over arbitrary statements; callers must encode data exactly as documented.

The API returns stable SQLite result codes, but database handles from `sqlite3rbu_db()` are only valid until the next RBU API call other than another `sqlite3rbu_db()`. Destroying an RBU VFS while database handles still use it is undefined. Once `sqlite3rbu_step()` returns a non-`SQLITE_OK` value, later step calls on the same handle return the same value without doing work.

## Test Signals

The header's documented APIs are directly wrapped by `test_rbu.c`, making Tcl tests able to drive update/vacuum loops, inspect state/progress, register delta functions, inject rename callbacks, and manipulate temp-size limits. The extensive examples and constraints in this header are the behavioral oracle for the `ext/rbu/*.test` suite.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/sqlite3rbu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/test_rbu.c -->
# sources/storage-engines/sqlite/ext/rbu/test_rbu.c

## Purpose

`test_rbu.c` is the SQLite test harness glue for the RBU extension. When compiled with `SQLITE_TEST` and RBU support, it registers Tcl commands that construct RBU handles, expose handle methods, create or destroy RBU VFS instances, and run small internal tests. It lets the Tcl test suite exercise the C API, observe return codes, inject rename failures, register a Tcl-backed `rbu_delta()` SQL function, and inspect progress/temp-space behavior.

## Important APIs, Types, and Functions

`TestRbu` binds a `sqlite3rbu *`, a `Tcl_Interp *`, and an optional Tcl rename script. `test_rbu_delta()` implements a SQL function that calls the Tcl command `rbu_delta` with the SQL arguments and returns the Tcl result as text. `xRenameCallback()` adapts a Tcl script to the `sqlite3rbu_rename_handler()` callback signature.

`test_sqlite3rbu_cmd()` is the per-handle Tcl object command. It supports `step`, `close`, `close_no_error`, `create_rbu_delta`, `savestate`, `dbMain_eval`, `dbRbu_eval`, `bp_progress`, `db`, `state`, `progress`, `temp_size_limit`, `temp_size`, and `rename_handler`. `createRbuWrapper()` allocates `TestRbu` and registers this object command for a new handle.

Top-level Tcl commands are implemented by `test_sqlite3rbu()` (`sqlite3rbu NAME TARGET-DB RBU-DB ?STATE-DB?`), `test_sqlite3rbu_vacuum()` (`sqlite3rbu_vacuum NAME TARGET-DB ?STATE-DB?`), `test_sqlite3rbu_create_vfs()`, `test_sqlite3rbu_destroy_vfs()`, and `test_sqlite3rbu_internal_test()`. `SqliteRbu_Init()` registers them with the Tcl interpreter.

## Control Flow

Tests create a handle command by invoking `sqlite3rbu` or `sqlite3rbu_vacuum`. The wrapper immediately calls `sqlite3rbu_open()` or `sqlite3rbu_vacuum()`, stores the handle in `TestRbu`, and returns the Tcl command name. Tests then drive the object command one method at a time. `step` returns a symbolic SQLite error name via `sqlite3ErrName()`. `close` deletes the Tcl command first, calls `sqlite3rbu_close()`, reports the result and optional error message, decrements any rename script reference, and frees the wrapper.

The `create_rbu_delta` method obtains the target database handle through `sqlite3rbu_db(pRbu, 0)` and registers `test_rbu_delta()` as `rbu_delta`. The `dbMain_eval` and `dbRbu_eval` methods execute SQL directly against the corresponding internal handle. The `db` method returns a pointer string for lower-level Tcl tests. The `rename_handler` method either restores default rename handling with an empty script or duplicates a Tcl script and registers `xRenameCallback()`.

`sqlite3rbu_create_vfs ?-default? NAME PARENT` calls the public VFS constructor and optionally registers the new VFS as default. `sqlite3rbu_destroy_vfs NAME` calls the public destructor. If RBU is not compiled in, `SqliteRbu_Init()` is a no-op that returns `TCL_OK`.

## State and Persistence Behavior

The harness owns wrapper lifetime, not RBU persistence. It frees `TestRbu` only during `close`/`close_no_error`; tests that do not close a command would leak the wrapper for the interpreter lifetime. Any persistent RBU state is stored by the implementation in the RBU or state database, and this harness exposes `savestate` and `close` to force those paths.

The optional rename script is reference-counted as a Tcl object. Registering a non-empty script stores a duplicate and increments its refcount; closing decrements it. The current implementation does not decrement a previous script when `rename_handler` is called repeatedly with a different non-empty script, so tests should avoid repeated replacement without close or be aware of the leak.

## Dependencies and Integration Points

This file depends on the SQLite test harness (`SQLITE_TEST`, `tclsqlite.h`, `sqlite3ErrName()`, `sqlite3TestMakePointerStr()`), Tcl APIs, and the RBU public header. It is not part of normal production builds unless the test configuration enables it. Its returned strings and method names are consumed by the Tcl tests under `sources/storage-engines/sqlite/ext/rbu`.

The harness is intentionally thin: it does not simulate RBU behavior, but delegates to the real public API. This makes it a reliable integration layer for testing VFS creation/destruction, progress APIs, state transitions, rename callbacks, temp-size accounting, and direct SQL interactions with RBU-owned database handles.

## Risks and Test Signals

Because Tcl scripts can execute arbitrary code during `rbu_delta` or rename callbacks, tests can create timing, error, and reentrancy scenarios that normal callers might not. `xRenameCallback()` maps any Tcl error to `SQLITE_IOERR`, which is useful for fault tests but loses detailed Tcl error information at the RBU layer. `dbMain_eval` and `dbRbu_eval` ignore result rows and only surface `sqlite3_exec()` errors, so they are best for setup/fault injection rather than query assertions.

The internal test checks only that `sqlite3rbu_db(0, 0)` returns NULL. Broader behavioral coverage comes from Tcl tests invoking this harness, especially tests for crash/resume, busy handling, rename failure, progress reporting, delta updates, temp-size limits, VFS stacking, and close error propagation.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rbu/test_rbu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/dbdata.c -->
# sources/storage-engines/sqlite/ext/recover/dbdata.c

## Purpose

`dbdata.c` implements two eponymous virtual tables used by SQLite recovery tooling: `sqlite_dbdata` and `sqlite_dbptr`. Both read raw database pages through the `sqlite_dbpage` virtual table and bypass normal b-tree decoding. `sqlite_dbdata` extracts record fields from b-tree cells, tolerating corruption and returning as much data as possible. `sqlite_dbptr` emits parent-to-child page pointers from interior b-tree pages.

## Important APIs, Types, and Functions

`DbdataTable` is the virtual table object; it stores the SQLite connection, a reusable page-fetch statement, and `bPtr` to distinguish `sqlite_dbptr` from `sqlite_dbdata`. `DbdataCursor` stores scan position (`iPgno`, `iCell`, `iField`, `iRowid`), page buffer, page/cell counts, one-page mode, database size, encoding, record payload buffer, header/data pointers, and intkey rowid. `DbdataBuffer` is a reallocating byte buffer for record payloads.

Virtual table methods are registered in `sqlite3DbdataRegister()`. Core callbacks are `dbdataConnect()`, `dbdataDisconnect()`, `dbdataBestIndex()`, `dbdataOpen()`, `dbdataClose()`, `dbdataFilter()`, `dbdataNext()`, `dbdataEof()`, `dbdataColumn()`, and `dbdataRowid()`. The load/decode helpers are `dbdataLoadPage()`, `dbdataGetVarint()`, `dbdataGetVarintU32()`, `dbdataValueBytes()`, `dbdataValue()`, `dbdataDbsize()`, and `dbdataGetEncoding()`.

Schemas are declared as `sqlite_dbdata(pgno, cell, field, value, schema HIDDEN)` and `sqlite_dbptr(pgno, child, schema HIDDEN)`. `sqlite3_dbdata_init()` is the extension initializer and registers both modules unless virtual tables are omitted.

## Control Flow

`dbdataBestIndex()` recognizes equality constraints on hidden `schema` and visible `pgno`. With `schema=?`, the scan reads an attached database name or a special function-like schema source. With `pgno=?`, it switches to one-page mode and lowers estimated cost/rows. For `sqlite_dbdata`, it can also consume simple ascending ORDER BY clauses on `pgno` and `cell` when a page constraint exists.

`dbdataFilter()` resets the cursor, chooses the schema (default `main`), determines database size unless scanning one page, prepares or reuses a statement to fetch page bytes, binds the schema, reads page 1 to determine text encoding, and calls `dbdataNext()` to position on the first row. Normal page reads use `SELECT data FROM sqlite_dbpage(?) WHERE pgno=?`; function-like schema strings ending in `()` are treated as callbacks invoked as `name(?2)` and `name(0)` for page data and size.

`dbdataNext()` is the main parser. It loads pages in page-number order, skips missing or too-small pages, reads the b-tree page type at offset 100 for page 1 or offset 0 otherwise, clamps cell counts to a copy of SQLite's maximum-cell formula, and then either emits child pointers (`sqlite_dbptr`) or decodes record payload (`sqlite_dbdata`). For data records it handles leaf table pages, leaf index pages, and interior index pages with a child pointer prefix. It decodes payload size varints, optional intkey rowid, local payload size, overflow chain pages, record header size, serial types, and field data pointers.

`dbdataColumn()` returns the current page/cell/field/value for `sqlite_dbdata`, using field `-1` for intkey rowids. For `sqlite_dbptr`, it returns the parent page and either the right-child pointer or each cell child pointer. `dbdataRowid()` returns an internal incrementing rowid unrelated to source table rowids.

## State and Persistence Behavior

The module is read-only and creates no persistent tables. Cursor state is entirely in memory. Page buffers are allocated per loaded page and freed when moving to the next page or closing. Record payload buffers are retained and grown as needed, then freed on cursor reset/close. `DbdataTable.pStmt` caches one page-fetch statement across cursor resets to reduce prepare churn; if a second cursor has a statement while the table cache is occupied, the cursor statement is finalized.

The design intentionally tolerates corrupt content. It pads page and record buffers with `DBDATA_PADDING_BYTES`, clamps out-of-range varints and cell counts, substitutes benign zero/empty values if a field's bytes are truncated, stops following invalid/missing overflow chains, and skips pages that do not look parseable. Most corruption is represented as missing or partial rows instead of SQLite errors.

## Dependencies and Integration Points

The module depends on SQLite virtual table APIs, `sqlite_dbpage`, SQLite record-format constants, b-tree page layout, varint encoding, text encoding constants, and extension initialization conventions. It calls `sqlite3_vtab_config(db, SQLITE_VTAB_USES_ALL_SCHEMAS)` so the hidden `schema` column may target attached databases. It is compiled out when `SQLITE_OMIT_VIRTUALTABLE` is defined.

It integrates with recovery code by exposing low-level data through SQL. `sqlite_dbdata` can recover values from damaged tables even when normal b-tree traversal fails. `sqlite_dbptr` can reconstruct or inspect page graph relationships. The function-like schema mode lets recovery tooling provide alternate page sources, not only attached database names.

## Risks and Edge Cases

The parser manually mirrors SQLite file-format rules, so page-layout changes would require updates here. It assumes page sizes and offsets are sane enough after basic checks. It deliberately masks many corrupt conditions, which is useful for recovery but risky if callers expect complete or integrity-checked output. Rows may be omitted, values may be defaulted to zero or empty, and overflow payloads may be truncated without an error.

Integer and floating-point decoding relies on serial types and big-endian assembly. The double path copies the assembled 64-bit value into a `double`, which follows SQLite's stored IEEE representation but remains low-level and architecture-sensitive in appearance. `dbdataBestIndex()` assigns both schema and pgno arguments by position; bugs in constraint handling could bind page numbers incorrectly, but the `idxNum` bit protocol keeps the current mapping straightforward.

The hidden `schema` value can be treated as a SQL function name if it ends in `()`. This is powerful for recovery workflows but means callers should not pass untrusted arbitrary strings as schema selectors in contexts where preparing `SELECT <name>(...)` would be unsafe.

## Test Signals

The surrounding recover tests (`recover*.test`, `recover_common.tcl`, and related fault/corruption tests) are the likely consumers. Important signals include scans over normal databases, corrupt pages, overflow chains, attached schemas, one-page scans with `pgno=?`, child-pointer extraction, UTF-16 text decoding, and operation when `sqlite_dbpage` supplies missing or malformed pages.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/dbdata.c -->
