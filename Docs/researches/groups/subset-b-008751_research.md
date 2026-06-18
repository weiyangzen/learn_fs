# subset-b-008751 research

Grouped research for SQLite recovery and geopoly extension sources. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/sqlite3recover.c -->
# sources/storage-engines/sqlite/ext/recover/sqlite3recover.c

## Purpose

`sqlite3recover.c` implements the SQLite recovery extension behind the public `sqlite3_recover_*` API. It attempts to extract schema rows, table records, and optional orphan records from a possibly corrupt database and either writes the result to a new output database or emits equivalent SQL through a callback. The implementation is deliberately tolerant of partial corruption: failure to recover some schema or rows is not itself an error, but I/O, allocation, callback, SQLite API, and transaction failures are reported through the recover handle.

## Important APIs, Types, and Functions

The externally visible functions are `sqlite3_recover_init()`, `sqlite3_recover_init_sql()`, `sqlite3_recover_config()`, `sqlite3_recover_step()`, `sqlite3_recover_run()`, `sqlite3_recover_errmsg()`, `sqlite3_recover_errcode()`, and `sqlite3_recover_finish()`. Internally, `recoverInit()` allocates the opaque `sqlite3_recover` object and records the input database name, output URI or SQL callback, and default rowid policy.

Key state types are `RecoverTable`, `RecoverColumn`, `RecoverBitmap`, `RecoverStateW1`, `RecoverStateLAF`, and `RecoverGlobal`. `RecoverTable` stores recovered schema metadata for a table, including original root page, generated/hidden column handling, rowid binding, and intkey versus WITHOUT ROWID shape. `RecoverStateW1` owns prepared statements and accumulated `sqlite3_value` copies while recovering rows for known schema tables. `RecoverStateLAF` owns bitmap, page-map, and insert state for the optional lost-and-found pass. `RecoverGlobal` holds a temporary process-wide VFS method wrapper protected by `SQLITE_MUTEX_STATIC_APP2`.

Important helper families are:

- Error/allocation wrappers: `recoverMalloc()`, `recoverError()`, `recoverDbError()`, `recoverPrepare*()`, `recoverExec()`, `recoverFinalize()`, and `recoverMPrintf()`.
- SQL functions registered on the output handle: `getpage()`, `page_is_used()`, `read_i32()`, and `escape_crlf()`.
- Schema setup: `recoverOpenOutput()`, `recoverTransferSettings()`, `recoverOpenRecovery()`, `recoverCacheSchema()`, `recoverWriteSchema1()`, `recoverWriteSchema2()`, and `recoverAddTable()`.
- Data extraction: `recoverWriteDataInit()`, `recoverWriteDataStep()`, `recoverInsertStmt()`, and `recoverWriteDataCleanup()`.
- Lost-and-found recovery: `recoverLostAndFound1Init/Step()`, `recoverLostAndFound2Init/Step()`, `recoverLostAndFound3Init/Step()`, `recoverLostAndFoundOnePage()`, `recoverLostAndFoundFindRoot()`, and table/insert synthesis helpers.
- Header/VFS repair: `recoverIsValidPage()`, `recoverVfsDetectPagesize()`, `recoverVfsRead()`, `recoverInstallWrapper()`, and `recoverUninstallWrapper()`.

## Control Flow

`sqlite3_recover_step()` is a state machine. In `RECOVER_STATE_INIT`, it opens the output database, registers `sqlite_dbdata`/`sqlite_dbptr` and local SQL functions, begins a read transaction on the input database, transfers durable settings to the output database, attaches the temporary `recovery` database, and populates `recovery.schema` by walking page 1 with `sqlite_dbptr('getpage()')` and decoding schema records through `sqlite_dbdata('getpage()')`. A VFS wrapper is installed for the first attempt so reads of page 1 can be sanitized; if that path yields `SQLITE_NOTADB`, the code retries without the wrapper for encrypted databases.

After initialization, `recoverWriteSchema1()` creates real tables and UNIQUE indexes early, while virtual table entries are written directly into `sqlite_schema`. Each successfully created table is inspected with `PRAGMA table_xinfo()` and possibly `PRAGMA index_xinfo()` so `RecoverTable` can map on-disk fields to insert bindings, skip generated columns, preserve INTEGER PRIMARY KEY rowids, and recognize WITHOUT ROWID layout.

In `RECOVER_STATE_WRITING`, `recoverWriteDataStep()` iterates schema table roots, recursively traverses child pages with `sqlite_dbptr()`, reads record fields with `sqlite_dbdata()`, accumulates one cell at a time, builds or reuses an insert statement matching the number of recovered fields, binds copied values, and writes `INSERT OR IGNORE` rows. SQL callback mode prepares `SELECT` statements that render insert text using `quote()` and `escape_crlf()` instead of modifying an output table directly.

If `SQLITE_RECOVER_LOST_AND_FOUND` is configured, three additional states run. The first builds a bitmap of pages already consumed by known schema trees and, unless the freelist is declared corrupt, freelist pages. The second scans all pages and child pointers to populate `recovery.map` for unclaimed pages and discover the maximum number of fields needed. The third creates a uniquely named lost-and-found table and writes rows containing inferred root page, page number, field count, rowid if present, and recovered field values.

`RECOVER_STATE_SCHEMA2` creates delayed views, triggers, and non-UNIQUE indexes, commits output work, ends the input transaction, emits final callback SQL, and frees transient state. `sqlite3_recover_run()` simply loops `sqlite3_recover_step()` until it returns a non-`SQLITE_OK` result.

## State and Persistence Behavior

The recover handle owns all per-run memory, prepared statements, duplicated SQL strings, cached page-1 bytes, table metadata, and optional lost-and-found state. The input database is held in a read transaction after initialization; `bCloseTransaction` ensures `finish()` attempts to close it even if recovery is abandoned. The output path uses a separate `sqlite3 *dbOut`; recovery begins by clobbering any existing output database through a backup from a new empty temp database, then applying selected input pragmas such as page size, encoding, auto-vacuum, user version, and application id.

The attached `recovery` database is a transient state store unless the undocumented config opcode `789` supplies a state database name for debugging. Persistent output includes recovered tables, rows, schema objects, and optionally a lost-and-found table. SQL callback mode does not persist directly to `dbOut`; it uses prepared SQL to render an equivalent script while still relying on the output handle for parsing, temp state, dbdata modules, and schema reasoning.

The VFS wrapper is process-global for the input file descriptor during a short initialization window. It rewrites page-1 reads to a known-good SQLite header, preserving selected metadata and caching both disk and synthetic copies so later `getpage(1)` can return the original disk bytes to dbdata consumers when needed.

## Dependencies and Integration Points

This file depends on SQLite core APIs, virtual table support, `sqlite_dbpage` support on the input connection, and `sqlite3_dbdata_init()` from `dbdata.c` to register `sqlite_dbdata` and `sqlite_dbptr` on the output connection. It integrates tightly with SQLite b-tree page formats, varint decoding, page headers, freelist trunk layout, `sqlite_schema`, `PRAGMA table_xinfo`, `PRAGMA index_xinfo`, backup API behavior, file-control `SQLITE_FCNTL_FILE_POINTER` and `SQLITE_FCNTL_RESET_CACHE`, and VFS method dispatch.

The public header is `sqlite3recover.h`; Tcl tests use `test_recover.c` to expose the API. Repository tests under `ext/recover` exercise normal recovery, SQL-script recovery, corrupt input, page-size/header detection, rowid policy, slow-index behavior, clobbering output databases, and OOM/fault handling.

## Risks and Edge Cases

The VFS wrapper is the highest-risk integration point because it mutates a live `sqlite3_file` method table and relies on a static global. The mutex narrows concurrency risk, but overlapping recovery operations on different connections still depend on correct serialized installation and removal. Header synthesis must infer page size and reserved bytes from damaged files without confusing random bytes for valid b-tree pages.

Recovered schema SQL is executed with best effort: `SQLITE_ERROR` from malformed recovered SQL is ignored, but other errors abort. This is intentional but means missing schema can cascade into lost rows. Generated columns, hidden columns, INTEGER PRIMARY KEY aliases, WITHOUT ROWID tables, `sqlite_sequence`, virtual tables, UNIQUE indexes, and delayed non-UNIQUE indexes all have special handling that can drift as SQLite schema semantics evolve.

Lost-and-found recovery trades precision for salvage. Marking the freelist corrupt can recover more records but can also resurrect deleted content. Root-page inference through `recovery.map` is heuristic for orphan pages. SQL callback mode builds SQL text with `quote()` and newline/carriage-return escaping, so correctness depends on complete literal rendering for all recovered SQLite value types.

Cleanup paths call finalizers and `sqlite3_close()` even when some state was never initialized. This matches the zeroed handle design, but future edits must preserve null-safe cleanup and avoid double-finalizing statements after state transitions.

## Test Signals

Useful test signals are the Tcl recover suites: `recover1.test`, `recoverold.test`, `recoverrowid.test`, `recoverslowidx.test`, `recoversql.test`, `recoverpgsz.test`, `recoverclobber.test`, `recoverbuild.test`, `recovercorrupt*.test`, `recoverfault.test`, and `recoverfault2.test`. These cover output database parity, SQL callback replay, lost-and-found inserts, rowid preservation toggles, delayed versus early index creation, overwritten output files, corrupted headers/pages, page-size detection, freelist assumptions, and allocation fault resilience. `test_recover.c` provides the Tcl command surface those tests drive.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/sqlite3recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/sqlite3recover.h -->
# sources/storage-engines/sqlite/ext/recover/sqlite3recover.h

## Purpose

`sqlite3recover.h` is the public C interface for SQLite's recover extension. It documents the lifecycle for recovering data from a corrupt database into either a replacement database file or a stream of SQL statements and defines the configuration options understood by the implementation.

## Important APIs, Types, and Functions

The header exposes an opaque `sqlite3_recover` type and eight API functions:

- `sqlite3_recover_init(sqlite3 *db, const char *zDb, const char *zUri)` creates a handle that writes recovered content into a new output database identified by a path or URI.
- `sqlite3_recover_init_sql(sqlite3 *db, const char *zDb, int (*xSql)(void*, const char*), void *pCtx)` creates a handle that emits a UTF-8 SQL script through a callback.
- `sqlite3_recover_config(sqlite3_recover*, int op, void *pArg)` configures a newly created, not-yet-started handle.
- `sqlite3_recover_step(sqlite3_recover*)` advances incremental recovery and returns `SQLITE_OK`, `SQLITE_DONE`, or an error code.
- `sqlite3_recover_run(sqlite3_recover*)` runs the step loop to completion.
- `sqlite3_recover_errmsg()` and `sqlite3_recover_errcode()` expose failure details.
- `sqlite3_recover_finish()` destroys the handle and returns the final error code.

The configuration constants are `SQLITE_RECOVER_LOST_AND_FOUND`, `SQLITE_RECOVER_FREELIST_CORRUPT`, `SQLITE_RECOVER_ROWIDS`, and `SQLITE_RECOVER_SLOWINDEXES`.

## Control Flow

The intended caller flow is: allocate with one of the init functions, configure before any step/run call, repeatedly call `sqlite3_recover_step()` until it stops returning `SQLITE_OK`, inspect error state if needed, then always call `sqlite3_recover_finish()`. `sqlite3_recover_run()` is documented as the convenience loop around `sqlite3_recover_step()` followed by `sqlite3_recover_errcode()`.

The header also defines completion semantics: `SQLITE_DONE` means recovery finished successfully; other non-`SQLITE_OK` returns are errors; inability to recover all corrupt data is not itself an API error. After `sqlite3_recover_step()` returns anything other than `SQLITE_OK`, further step calls are no-ops returning the same non-OK state.

## State and Persistence Behavior

`sqlite3_recover` is opaque, so callers cannot mutate internal state directly. The input state is an already opened SQLite handle plus an attached database name such as `main`, `temp`, or another attached schema. In output-database mode, `zUri` identifies a database that may be overwritten. In SQL-callback mode, the callback receives statements that should reconstruct the same output if executed in order.

Options modify persistence semantics. Lost-and-found naming controls whether orphan records are materialized into a table. Freelist-corrupt mode decides whether pages that appear on the freelist are treated as recoverable candidates. Rowid mode controls preservation of non-IPK rowids versus assignment of new rowids. Slow-index mode chooses whether non-UNIQUE indexes are built before row insertion or delayed until the end.

## Dependencies and Integration Points

The only included dependency is `sqlite3.h`. The API is C++ compatible through `extern "C"`. It is implemented by `sqlite3recover.c` and test-exposed through `test_recover.c`. Users must supply a live SQLite connection with the source database attached, and they must respect the pre-run-only constraint on `sqlite3_recover_config()`.

## Risks and Edge Cases

The `void *pArg` configuration API is type-sensitive: some options expect a nullable string pointer and others expect a pointer to an `int`, not an integer cast directly through `void *`. Misuse is only partly detectable. The callback API aborts recovery if the callback returns anything other than `SQLITE_OK`; applications must avoid returning Tcl-style or application-specific error codes accidentally unless they intend to stop recovery.

The header states that abandoning recovery with `finish()` before completion is not an API error, but the output database or partial SQL stream is undefined. Callers should treat partial outputs as disposable unless they layer their own transaction handling around SQL callback replay.

## Test Signals

The Tcl test wrapper in `test_recover.c` maps the documented lifecycle into commands. The `ext/recover` tests exercise both init modes, all documented options, error reporting, finalize semantics, and incremental stepping. Header contract regressions would show up as compile errors, Tcl command argument failures, mismatched SQLite result codes, or recovery tests that can no longer configure options before running.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/sqlite3recover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/test_recover.c -->
# sources/storage-engines/sqlite/ext/recover/test_recover.c

## Purpose

`test_recover.c` is the SQLite Tcl test harness binding for the recover extension and the related `sqlite_dbdata` registration hook. It lets Tcl tests create a `sqlite3_recover` handle, configure it, step or run it, inspect errors, finalize it, and test SQL-callback mode without writing C test code for each scenario.

## Important APIs, Types, and Functions

`TestRecover` stores the active `sqlite3_recover *`, the Tcl interpreter, and an optional callback script object used by SQL-emitting recovery. `xSqlCallback()` duplicates the configured Tcl script, appends the emitted SQL statement, evaluates it, and converts an empty result to `SQLITE_OK` or a numeric result to the callback return code. `getDbPointer()` resolves a Tcl SQLite command name to its underlying `sqlite3 *` via command client data.

`test_sqlite3_recover_init()` implements both `sqlite3_recover_init DB DBNAME URI` and `sqlite3_recover_init_sql DB DBNAME SCRIPT`, distinguished by `clientData`. It allocates `TestRecover`, creates the underlying recover handle, assigns a generated Tcl command name such as `sqlite_recover1`, and registers `testRecoverCmd()` as the object command.

`testRecoverCmd()` implements subcommands `config`, `run`, `errmsg`, `errcode`, `finish`, and `step`. Config options map Tcl names to recover opcodes: `testdb` uses the undocumented implementation opcode `789`, `lostandfound` maps to `SQLITE_RECOVER_LOST_AND_FOUND`, `freelistcorrupt` to `SQLITE_RECOVER_FREELIST_CORRUPT`, `rowids` to `SQLITE_RECOVER_ROWIDS`, `slowindexes` to `SQLITE_RECOVER_SLOWINDEXES`, and `invalid` deliberately sends an unknown opcode. `test_sqlite3_dbdata_init()` registers `sqlite_dbdata`/`sqlite_dbptr` against a Tcl database handle. `TestRecover_Init()` installs the top-level Tcl commands.

## Control Flow

Tests call `sqlite3_recover_init` or `sqlite3_recover_init_sql` with a Tcl DB handle and database name. The returned Tcl command wraps one C recover handle. A typical test then invokes `$R config ...`, `$R run` or repeated `$R step`, `$R errcode`/`$R errmsg`, and `$R finish`.

In SQL-callback mode, every SQL statement emitted by `sqlite3recover.c` re-enters Tcl through `xSqlCallback()`. The script receives the statement as an appended argument, so tests can collect SQL text, replay it into another database, inject callback errors, or filter for specific statements such as lost-and-found inserts. If Tcl evaluation fails or returns a non-integer non-empty result, `Tcl_BackgroundError()` is used and the recover callback reports `TCL_ERROR`.

## State and Persistence Behavior

The wrapper keeps the C recover handle alive until the Tcl subcommand `finish` is called. `finish` first checks `sqlite3_recover_errcode()`, exposes the error message as the Tcl result if non-OK, calls `sqlite3_recover_finish()`, asserts the returned code matches the prior error code, and returns a Tcl error when recovery failed. SQL callback scripts are refcounted with `Tcl_IncrRefCount()` when the handle is created, but this file does not define a Tcl command delete callback to release `TestRecover` if a command is deleted without `finish`.

The output database or SQL replay persistence is controlled by the underlying recover implementation. This shim itself persists no database state except by invoking recover APIs and optional `sqlite3_dbdata_init()`.

## Dependencies and Integration Points

The file includes `sqlite3recover.h`, `sqliteInt.h`, and `tclsqlite.h`, so it is part of SQLite's internal test build rather than a standalone public extension. It depends on the Tcl command representation used by the SQLite test harness, where `objClientData` points at a `sqlite3 *`. It also declares `sqlite3_dbdata_init()` so tests can load dbdata virtual tables independently.

## Risks and Edge Cases

The wrapper is intentionally thin and test-oriented. It does not validate that `sqlite3_recover_init()` returned non-NULL before registering a Tcl command, so OOM paths depend on subsequent recover APIs returning `SQLITE_NOMEM` for null handles or on tests not dereferencing invalid wrapper state. The absence of a command deletion callback means abnormal Tcl command deletion can leak the `TestRecover` allocation and retained callback script. The `testdb` option uses a magic opcode that is explicitly implementation-private.

Callback result conversion is another risk: an empty Tcl result means success, an integer result is passed through to recover, and non-integer text becomes a Tcl background error. This is useful for fault injection but can mask script mistakes as callback failures.

## Test Signals

This file is exercised by the recover Tcl suites under `ext/recover`. Signals include successful command creation, exact SQLite integer return codes from `config`, `run`, and `step`, error message propagation through `finish`, callback SQL collection in `recover1.test`, `recoverold.test`, and `recoversql.test`, invalid config opcode coverage, and independent `sqlite3_dbdata_init` setup for low-level dbdata tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/recover/test_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/geopoly.c -->
# sources/storage-engines/sqlite/ext/rtree/geopoly.c

## Purpose

`geopoly.c` implements SQLite's `geopoly` virtual table module and its polygon SQL functions. The module is an R-Tree-backed table specialized for two-dimensional polygons: it stores the original polygon in an auxiliary `_shape` column and indexes each shape by its bounding box. The file is included at the end of `rtree.c`, giving it direct access to internal R-Tree types, helpers, cursor logic, shadow-table handling, and integrity routines.

## Important APIs, Types, and Functions

`GeoCoord` is a `float`; `GeoPoly` is the in-memory and on-disk polygon representation with a 4-byte endian/count header followed by X/Y coordinate pairs. The on-disk polygon omits the repeated closing vertex required by GeoJSON. `GeoParse` tracks JSON parsing state. `GeoBBox` is aggregate state for `geopoly_group_bbox()`. `GeoEvent`, `GeoSegment`, and `GeoOverlap` implement a sweep-line overlap classifier.

Polygon parsing and conversion are handled by `geopolyParseJson()` and `geopolyFuncParam()`. They accept GeoJSON-like text arrays or geopoly blobs, normalize blob endianness, validate vertex counts and blob sizes, and allocate a `GeoPoly`. Scalar/aggregate SQL functions include `geopoly_blob`, `geopoly_json`, `geopoly_svg`, `geopoly_xform`, `geopoly_area`, `geopoly_ccw`, `geopoly_regular`, `geopoly_bbox`, `geopoly_group_bbox`, `geopoly_contains_point`, `geopoly_within`, `geopoly_overlap`, and optional `geopoly_debug`.

Virtual table entry points are `geopolyCreate()`, `geopolyConnect()`, `geopolyBestIndex()`, `geopolyFilter()`, `geopolyColumn()`, `geopolyUpdate()`, and `geopolyFindFunction()`, packaged in `geopolyModule`. Other module slots delegate to R-Tree implementations such as `rtreeOpen`, `rtreeNext`, `rtreeEof`, `rtreeRowid`, `rtreeDestroy`, transaction hooks, rename, shadow-name, and integrity checks. `sqlite3_geopoly_init()` registers functions, the aggregate, and the module.

## Control Flow

Scalar functions first decode their polygon arguments through `geopolyFuncParam()`. JSON parsing scans a strict array of coordinate arrays, requires at least four vertices including a closing vertex equal to the first, then removes the duplicate close point for storage. Blob parsing checks the endian flag and byte length, copies data into a mutable `GeoPoly`, and byte-swaps coordinates if the blob endian differs from the host.

Geometry helpers then operate on that normalized representation. `geopolyArea()` computes signed area and `geopolyCcwFunc()` reverses vertices except the first when winding is clockwise. `geopolyBBox()` computes min/max X/Y and either fills R-Tree coordinates or returns a four-vertex bounding-box polygon. `geopolyContainsPointFunc()` uses a ray-crossing style `pointBeneathLine()` test and reports outside, boundary, or inside. `geopolyOverlap()` builds non-vertical segments for both polygons, sorts add/remove events by X, maintains an active list sorted by Y and slope, detects crossings, and classifies disjoint, overlap, containment, or equality based on side masks.

For virtual tables, `geopolyInit()` declares a schema beginning with `_shape` plus user-specified auxiliary columns, configures the backing `Rtree` for two real32 dimensions, initializes shadow storage through R-Tree helpers, and marks `_shape` as not-null auxiliary data. `geopolyBestIndex()` prefers rowid equality, then overloaded `geopoly_overlap(_shape, ?)` or `geopoly_within(_shape, ?)` constraints, then full scan. `geopolyFindFunction()` maps those function names to special constraint opcodes so `xBestIndex` can see them.

`geopolyFilter()` turns an overlap or within function argument into four bounding-box constraints and then uses the normal R-Tree search machinery. The SQL function itself is not omitted, so exact polygon filtering still runs after the bounding-box prefilter. `geopolyColumn()` reads `_shape` and auxiliary columns from the R-Tree aux table using prepared read SQL. `geopolyUpdate()` handles deletes, inserts, rowid changes, shape updates, conflict handling, R-Tree cell insertion/deletion, and auxiliary table writes. Text shapes are converted to canonical geopoly blobs before storage.

## State and Persistence Behavior

Persistent state follows the R-Tree shadow-table model created by `rtreeSqlInit()`: nodes store rowid and four bounding coordinates, while auxiliary storage stores `_shape` and user columns. `_shape` is always counted as an auxiliary not-null column. Insert and update operations derive `cell.aCoord` from the polygon bounding box; if `_shape` is unchanged, coordinate updates can be skipped and only auxiliary values are updated. If `_shape` changes or the rowid changes, the old R-Tree row is deleted and a new cell is inserted.

Function calls allocate temporary `GeoPoly` objects and free them before return. Aggregation uses SQLite aggregate context to accumulate one bounding box. The virtual table maintains standard R-Tree cursor, node reference, and prepared-statement state through the surrounding `rtree.c` infrastructure.

## Dependencies and Integration Points

This file depends on SQLite core function APIs, `sqlite3_str`, deterministic/innocuous/direct-only function flags, virtual table APIs including overloaded function constraints, and many private R-Tree definitions from `rtree.c`: `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeCoord`, `RtreeConstraint`, `rtreeModule`, `getNodeSize()`, `rtreeSqlInit()`, `rtreeReference()`, `rtreeRelease()`, `findLeafNode()`, `nodeAcquire()`, `nodeRelease()`, `rtreeSearchPointNew()`, `rtreeStepToLeaf()`, `nodeGetRowid()`, `rtreeDeleteRowid()`, `rtreeNewRowid()`, `ChooseLeaf()`, `rtreeInsertCell()`, and related transaction/integrity helpers.

The module integrates with SQL through `CREATE VIRTUAL TABLE ... USING geopoly(...)`, scalar geometry functions, aggregate bbox computation, and query planning for `geopoly_overlap()`/`geopoly_within()` predicates. Compile-time integration is controlled by SQLite R-Tree/geopoly capability flags, and debug output is conditional on `GEOPOLY_ENABLE_DEBUG`.

## Risks and Edge Cases

Geometry uses 32-bit floats for stored coordinates and exact equality comparisons in several places, including closing-vertex validation, boundary detection, and segment ordering. That keeps storage compact and matches R-Tree real32 coordinates, but precision-sensitive polygons can classify differently from double-precision GIS engines. The JSON parser is intentionally narrow: it accepts a simple coordinate-ring array and does not implement full GeoJSON objects, holes, multipolygons, or property containers.

The overlap algorithm ignores vertical segments in the sweep-line event set and handles containment/equality through side-mask intervals. Boundary-heavy or degenerate polygons are therefore important regression targets. `geopoly_contains_point()` documentation comments and implementation differ in wording: the code returns `1` for boundary and `2` for inside.

Because this file reaches into R-Tree internals, changes to `rtree.c` private struct layout, aux-column SQL generation, node locking, shadow-name policy, or constraint op encoding can break geopoly without changing this file. `geopolyUpdate()` must preserve R-Tree constraints while also storing canonical blob data; conflict handling depends on `sqlite3_vtab_on_conflict()` and the existing `pReadRowid` statement.

`geopoly_svg()` appends caller-supplied attribute text directly into the generated SVG fragment. It is an SQL rendering helper, not an HTML sanitizer.

## Test Signals

Direct signals include geopoly-capable R-Tree tests, especially `ext/rtree/rtreefuzz001.test`, which creates geopoly data and queries `geopoly_overlap()` with rendered SVG output. Broader R-Tree tests exercise shared cursor, update, integrity, shadow table, and query-planning behavior used by geopoly because the module delegates most virtual table mechanics to `rtree.c`. Useful checks are canonical blob/json round trips, bbox values, point containment return codes, overlap and within classifications, rowid lookup plans, function-constraint plans, insert/update/delete behavior, conflict replacement, and `rtreecheck`/integrity validation of geopoly shadow storage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/geopoly.c -->
