# subset-b-008752 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/rtree.c -->
# sources/storage-engines/sqlite/ext/rtree/rtree.c

## Purpose
`rtree.c` implements SQLite's R-Tree and R*-Tree virtual table modules. It exposes SQL modules named `rtree` and `rtree_i32`, supports optional auxiliary columns, stores spatial index state in SQLite shadow tables, and provides read, write, rename, transaction, integrity-check, and loadable-extension entry points.

The file owns the full on-disk node format for R-Tree tables. Each virtual table maps to `%_node`, `%_parent`, and `%_rowid` shadow tables. `%_node` stores fixed-size node blobs, `%_parent` maps child node numbers to parent node numbers, and `%_rowid` maps user rowids to leaf node numbers plus auxiliary column values. Node 1 is always the root and stores tree depth in its first two bytes.

## Important APIs, Types, And Functions
`sqlite3RtreeInit(sqlite3 *db)` registers helper SQL functions `rtreenode()`, `rtreedepth()`, `rtreecheck()`, the `rtree` module, and the integer-coordinate `rtree_i32` module. Loadable builds expose `sqlite3_rtree_init()`.

The public callback APIs implemented here are `sqlite3_rtree_geometry_callback()` and `sqlite3_rtree_query_callback()`. They register SQL scalar functions whose result is a typed `RtreeMatchArg` pointer consumed by `MATCH` constraints during R-Tree scans.

Core state types are `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeConstraint`, `RtreeSearchPoint`, `RtreeGeomCallback`, and `RtreeMatchArg`. `Rtree` owns module metadata, node size, coordinate mode, prepared statements for shadow tables, a reusable blob handle for `%_node`, a small in-memory node hash, and transaction/cursor counters. `RtreeCursor` owns scan constraints, a priority queue of `RtreeSearchPoint` objects, a small node cache, and lazy auxiliary-column state.

The SQLite virtual-table module table wires `xCreate/xConnect` to `rtreeInit()`, planning to `rtreeBestIndex()`, scanning to `rtreeFilter()`, `rtreeNext()`, `rtreeColumn()`, `rtreeRowid()`, mutation to `rtreeUpdate()`, lifecycle to `rtreeDisconnect()`/`rtreeDestroy()`, transaction hooks to `rtreeBeginTransaction()`/`rtreeEndTransaction()`/`rtreeRollback()`, rename to `rtreeRename()`, shadow-table recognition to `rtreeShadowName()`, and integrity checking to `rtreeIntegrity()`.

Low-level node IO is handled by `readInt16()`, `readCoord()`, `readInt64()`, `writeInt16()`, `writeCoord()`, `writeInt64()`, `nodeAcquire()`, `nodeWrite()`, `nodeRelease()`, `nodeInsertCell()`, `nodeDeleteCell()`, and `nodeOverwriteCell()`. Tree algorithms include `ChooseLeaf()`, `AdjustTree()`, `splitNodeStartree()`, `SplitNode()`, `deleteCell()`, `removeNode()`, `fixBoundingBox()`, `reinsertNodeContent()`, `rtreeInsertCell()`, and `rtreeDeleteRowid()`.

## Control Flow
Creation and connection enter `rtreeInit()`. It validates constructor arguments, separates coordinate columns from optional `+aux` columns, declares the virtual table schema, calculates dimension count and cell size, obtains node size with `getNodeSize()`, and calls `rtreeSqlInit()` to create or prepare shadow-table SQL. `rtreeSqlInit()` creates `%_rowid`, `%_node`, `%_parent`, inserts the root zeroblob when creating, prepares persistent statements, and prepares auxiliary-column read/write SQL if needed.

Planning in `rtreeBestIndex()` recognizes two strategies. Strategy 1 is a direct rowid lookup when there is a usable equality constraint on rowid and no `MATCH` constraint. Strategy 2 is an R-Tree scan using coordinate comparisons or callback `MATCH` constraints encoded into a two-byte-per-constraint `idxStr`. Cost is based on `sqlite_stat1` row estimates when available.

Query execution starts in `rtreeFilter()`. Rowid lookup uses `%_rowid` to find the leaf node, builds one leaf search point, and locates the target cell. Normal scans acquire the root, deserialize numeric or callback constraints, enqueue the root at level `iDepth+1`, then call `rtreeStepToLeaf()`. `rtreeStepToLeaf()` repeatedly pops or expands search points, applies scalar constraints to internal or leaf cells, invokes registered geometry/query callbacks for `MATCH`, and enqueues matching children or leaf entries. The queue is score ordered for query callbacks and depth-first when scores tie.

Column retrieval in `rtreeColumn()` returns rowid, coordinate values, or lazily reads auxiliary columns from `%_rowid`. `rtreeNext()` resets any pending auxiliary read, pops the current point, and resumes the search. `rtreeRowid()` reads the current leaf cell's rowid from the active node.

Mutation in `rtreeUpdate()` handles SQLite virtual-table update conventions. It rejects writes while nodes are referenced by active readers, validates coordinate pairs, handles duplicate rowid conflicts with normal constraint or REPLACE semantics, deletes the old row when needed, chooses or allocates a new rowid, selects an insertion leaf with `ChooseLeaf()`, inserts using `rtreeInsertCell()`, and writes auxiliary values. Inserts may split nodes; deletes may condense the tree and reinsert orphaned node contents.

## State And Persistence Behavior
Persistent R-Tree state is entirely shadow-table backed. `%_node` contains fixed-size node blobs. `%_parent` is required for upward traversal during delete/update repair. `%_rowid` maps user rowids to leaf nodes and stores auxiliary columns. The root row in `%_node` always exists, even for empty trees.

In-memory nodes are reference-counted `RtreeNode` objects stored in a small hash by node id. Dirty nodes are written on final release. The module reuses one `sqlite3_blob` handle for reading node blobs and closes it on transaction boundaries, savepoints, disconnect, cursor drain, and operations that need to avoid locking shadow tables.

Insertion updates both structural blobs and mapping tables. For leaf cells, `rowidWrite()` updates `%_rowid`; for internal cells, `parentWrite()` updates `%_parent`. Split handling writes new node numbers, updates child parent mappings, and rewrites parent bounding boxes. Delete handling removes `%_rowid` entries, removes underfull nodes from `%_node` and `%_parent`, queues removed node contents in `pDeleted`, and reinserts those contents after condensation.

Coordinate persistence is big-endian 32-bit integer or 32-bit float. Floating-point writes deliberately round lower bounds down and upper bounds up via `rtreeValueDown()` and `rtreeValueUp()` so stored rectangles conservatively contain the requested values.

## Dependencies
The file depends on SQLite public/core APIs, `sqlite3ext.h` for loadable extension builds, `sqlite3rtree.h` for public callback types, and `sqlite3.h` in core builds. It uses virtual-table, blob, prepared-statement, typed pointer, value duplication, SQL string builder, and extension initialization APIs.

Compile-time branches cover `SQLITE_CORE`, `SQLITE_ENABLE_RTREE`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_GEOPOLY`, debug/corruption checks, byte-order optimizations, and coverage/mutation test behavior. If geopoly is enabled, `geopoly.c` is included from this compilation unit.

## Integration Points
SQLite reaches this code through the virtual-table module API. SQL users see `CREATE VIRTUAL TABLE ... USING rtree(...)`, `rtree_i32(...)`, coordinate constraints, rowid lookup, `MATCH` queries backed by callback APIs, auxiliary columns, `rtreecheck()`, `rtreenode()`, and `rtreedepth()`.

The public header `sqlite3rtree.h` defines the callback structs consumed by this file. The Tcl test file in this subset registers callbacks against these APIs. SQLite integrity check integrates through module version 4 `xIntegrity`, returning `In RTree db.table:` diagnostics when shadow tables are inconsistent.

## Risks And Edge Cases
The largest risk is hostile or corrupt shadow-table content. The code checks invalid node sizes, impossible cell counts, bad root depth, parent loops, duplicate queued nodes, missing mapping rows, and malformed blobs, but many routines still operate close to raw byte buffers and depend on correct `nBytesPerCell` and fixed node sizes.

Node reference ownership is subtle. Parent pointers are themselves reference-counted; split, delete, and cached cursor paths must release and reacquire nodes in the right order. The code explicitly refuses writes while `nNodeRef` is non-zero because rebalancing under an active reader can invalidate cursor state.

R*-Tree splitting and reinsertion are correctness-sensitive. `splitNodeStartree()` chooses dimensions and split points by margin, overlap, and area. Mapping updates must follow every movement of child cells, or `%_parent`/`%_rowid` diverge from `%_node`.

Floating-point behavior is intentionally conservative and platform-sensitive. Byte order, float rounding, very large integer comparisons in `rtreeFilter()`, and `SQLITE_RTREE_INT_ONLY` all affect exact comparison semantics. Callback queries also depend on user callbacks returning valid `eWithin` and score values.

## Test Signals
Strong tests include creating, connecting, dropping, and renaming `rtree` and `rtree_i32` tables; verifying shadow table contents; rowid lookup; coordinate range scans; `NULL` and text constraint behavior; auxiliary columns; duplicate rowid conflict modes; REPLACE updates; delete-induced condensation; root height growth and shrink; savepoint/drop interactions; and read/write locking with active cursors.

Callback tests should cover legacy geometry callbacks, query callbacks with scores and `eWithin`, destructor paths, `pUser` cleanup, SQL parameter preservation through `apSqlParam`, and callback errors. Corruption tests should feed malformed node blobs, bad parent mappings, missing rowid mappings, bad depths, and inconsistent bounds into `rtreecheck()` and module scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/rtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/rtree.h -->
# sources/storage-engines/sqlite/ext/rtree/rtree.h

## Purpose
`rtree.h` is the small internal/public bridge header for linking SQLite's R-Tree extension into a build. It declares the initializer that registers the R-Tree virtual table modules and helper functions on a database connection.

## Important APIs, Types, And Functions
The only declared function is `int sqlite3RtreeInit(sqlite3 *db);`. It takes an open SQLite connection and returns an SQLite result code. The implementation in `rtree.c` registers `rtree`, `rtree_i32`, `rtreenode()`, `rtreedepth()`, `rtreecheck()`, and optional geopoly support.

The header includes `sqlite3.h` for the `sqlite3` type. If `SQLITE_OMIT_VIRTUALTABLE` is set, it undefines `SQLITE_ENABLE_RTREE`, reflecting that R-Tree cannot be enabled without SQLite virtual tables.

## Control Flow
There is no runtime control flow in this header. Compile-time flow is limited to feature guards and C++ linkage wrapping. Consumers include the header and call `sqlite3RtreeInit()` during extension or core initialization.

## State And Persistence Behavior
The header owns no state and persists nothing. The declared function mutates only the supplied SQLite connection by registering modules and functions. Persistent shadow tables are created later by SQL `CREATE VIRTUAL TABLE` statements handled in `rtree.c`.

## Dependencies
The direct dependency is `sqlite3.h`. Link-time dependency is the R-Tree implementation object that defines `sqlite3RtreeInit()`. Builds omitting virtual tables must not expect R-Tree registration to be available.

## Integration Points
SQLite core initialization or extension bootstrap code can use this header to register R-Tree support. C++ consumers are supported through `extern "C"`.

## Risks And Edge Cases
The main risk is build configuration mismatch: including this header without compiling the implementation produces unresolved symbols, while defining `SQLITE_OMIT_VIRTUALTABLE` suppresses the feature macro. The header intentionally exposes no node, cursor, or callback internals; users needing callback APIs should include `sqlite3rtree.h`.

## Test Signals
Compilation tests should include this header from C and C++ translation units. Runtime smoke tests should call `sqlite3RtreeInit()` and then create/query a simple `rtree` and `rtree_i32` table.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/rtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/sqlite3rtree.h -->
# sources/storage-engines/sqlite/ext/rtree/sqlite3rtree.h

## Purpose
`sqlite3rtree.h` is the public API header for application-defined R-Tree geometry and query callbacks. It lets embedders register SQL functions usable on the right side of R-Tree `MATCH` constraints.

## Important APIs, Types, And Functions
The header declares opaque/structured callback types `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info`, and the coordinate scalar typedef `sqlite3_rtree_dbl`. `sqlite3_rtree_dbl` is `sqlite3_int64` when `SQLITE_RTREE_INT_ONLY` is defined and `double` otherwise.

`sqlite3_rtree_geometry_callback()` registers a legacy geometry callback. The callback receives an `sqlite3_rtree_geometry*`, coordinate count, coordinate array, and output integer indicating whether the candidate matches.

`sqlite3_rtree_query_callback()` registers the newer scored query callback. Its callback receives `sqlite3_rtree_query_info*` and can set `eWithin` and `rScore`, allowing priority-queue traversal and more expressive pruning/scoring.

`sqlite3_rtree_geometry` contains the registration context, numeric SQL parameters, and callback-owned `pUser` plus `xDelUser` cleanup hook. `sqlite3_rtree_query_info` begins with the same fields, then adds candidate coordinates, per-level queue counts, current level, max level, rowid, parent score/visibility, output score/visibility, and original SQL parameter values.

The visibility constants are `NOT_WITHIN`, `PARTLY_WITHIN`, and `FULLY_WITHIN`.

## Control Flow
Applications register a callback name against a connection. SQL then uses `WHERE coordinate_column MATCH callback_name(args...)`. The registered SQL scalar function packages callback metadata and SQL arguments into an internal typed pointer. During virtual-table filtering, `rtree.c` deserializes that pointer and invokes the callback for candidate internal nodes and leaf entries.

Legacy geometry callbacks return a boolean-like result through `*pRes`. Query callbacks can influence traversal order by writing `rScore` and can prune by writing `eWithin`. `iLevel`, `mxLevel`, `iRowid`, `rParentScore`, `eParentWithin`, and `anQueue` expose traversal context.

## State And Persistence Behavior
The header defines transient callback state only. `pContext` is the registration-time application pointer. `pUser` is per-query mutable callback state and may be cleaned with `xDelUser`. No persistent R-Tree shadow table state is defined here.

## Dependencies
The header depends on `<sqlite3.h>` and C linkage support for C++. Its ABI must match the implementation in `rtree.c`, especially the shared first fields of `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info`.

## Integration Points
This is the application-facing counterpart to `rtree.c` callback plumbing and to the Tcl tests in `test_rtreedoc.c`. Extensions and applications include it when they want custom spatial predicates or nearest-neighbor-like scoring behavior.

## Risks And Edge Cases
Callback implementations must treat `aCoord` as read-only candidate bounds and must set output fields consistently. Returning invalid `eWithin` values, negative or unordered scores, or retaining pointers beyond their lifetime can break query behavior. The `apSqlParam` field is available only in newer SQLite versions according to the header comment, so external code should account for version compatibility.

`sqlite3_rtree_dbl` changes type under `SQLITE_RTREE_INT_ONLY`; callback code compiled with mismatched settings can misinterpret coordinates and parameters.

## Test Signals
Tests should register both callback generations, invoke them with different parameter counts and types, confirm `pContext` and `pUser` cleanup, verify callback pruning and scoring, and cover integer-only builds. ABI tests should verify C++ inclusion and that the first fields of `sqlite3_rtree_query_info` remain compatible with `sqlite3_rtree_geometry`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/sqlite3rtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/test_rtreedoc.c -->
# sources/storage-engines/sqlite/ext/rtree/test_rtreedoc.c

## Purpose
`test_rtreedoc.c` is a Tcl test extension for exercising documented R-Tree callback APIs. It registers Tcl commands that install a legacy `box` geometry callback and a newer `qbox` query callback on a SQLite connection, then bridges callback invocations back into Tcl scripts for validation.

## Important APIs, Types, And Functions
`BoxGeomCtx` and `BoxQueryCtx` hold `Tcl_Interp*` plus a retained Tcl script object. `testDelUser()` exercises `sqlite3_rtree_geometry.pUser` cleanup by evaluating a saved Tcl script and freeing the context.

`invokeTclGeomCb()` constructs the Tcl callback invocation for legacy geometry callbacks. It passes the callback name, registration context pointer, parameter list, coordinate list, and geometry object pointer. It also interprets Tcl result commands such as `zero`, `user`, and `user_is_zero` to mutate or validate `sqlite3_rtree_geometry` state.

`box_geom()` is the legacy R-Tree geometry callback registered as SQL function `box`. It verifies parameter count, invokes Tcl, checks rectangle overlap against the supplied bounds, and writes the match result through `pRes`.

`register_box_geom` is the Tcl command that resolves a SQLite connection pointer, allocates a geometry context, registers `box` with `sqlite3_rtree_geometry_callback()`, and returns the context pointer string.

`box_query()` is the newer query callback registered as SQL function `qbox`. It builds a Tcl dictionary/list-like argument containing `aParam`, `aCoord`, `anQueue`, `iLevel`, `mxLevel`, `iRowid`, `rParentScore`, and textual `eParentWithin`, evaluates the script, and expects a two-element result containing visibility and score.

`box_query_destroy()` releases query callback script state, and `register_box_query` installs the query callback through `sqlite3_rtree_query_callback()`. `Sqlitetestrtreedoc_Init()` registers the two Tcl commands when R-Tree is enabled.

## Control Flow
The test extension initializes via `Sqlitetestrtreedoc_Init()`. Tcl test scripts call `register_box_geom DB SCRIPT` or `register_box_query DB SCRIPT`. Those commands capture the script and register an SQL callback function on the target database connection.

When SQL executes an R-Tree `MATCH box(...)` constraint, `rtree.c` invokes `box_geom()`. The callback forwards observable state to Tcl, optionally lets Tcl mutate callback-owned user state, then performs deterministic bounding-box overlap logic and returns a match flag.

For `MATCH qbox(...)`, `rtree.c` invokes `box_query()` for internal nodes and leaf entries. The callback forwards traversal state to Tcl and uses the Tcl result to set `pInfo->eParentWithin` and `pInfo->rScore`, allowing tests to validate scored traversal behavior and queue visibility.

## State And Persistence Behavior
The file owns only test callback state. Tcl scripts are reference-counted and freed through explicit destructor paths. Legacy geometry callbacks can allocate per-query `pUser` state via Tcl result handling; that state is later cleaned through `testDelUser()`.

No database state is persisted directly by this file. Its SQL callback registration affects only the SQLite connection used by tests.

## Dependencies
The file depends on `sqlite3.h`, `tclsqlite.h`, Tcl object APIs, and `sqliteInt.h` for `UNUSED_PARAMETER()`. It is compiled only when `SQLITE_ENABLE_RTREE` code paths are relevant; command registration is guarded accordingly.

## Integration Points
This is a test harness for `sqlite3rtree.h` and `rtree.c`. It validates documented evidence comments around legacy callback arguments and exposes internal callback fields to Tcl test scripts without adding production APIs.

## Risks And Edge Cases
There is a likely allocation-size bug in `register_box_geom`: it uses `ckalloc(sizeof(BoxGeomCtx*))` instead of `sizeof(BoxGeomCtx)`, which allocates pointer size rather than structure size. On platforms where the structure is larger than a pointer, this can corrupt memory in tests.

Callback return parsing is strict. `box_query()` expects exactly two Tcl result elements, a visibility token from `not`, `partly`, or `fully`, and a double score. Script errors propagate as `SQLITE_ERROR`. Pointer strings are used only for test visibility and should not be treated as stable external identifiers.

## Test Signals
Tests should verify legacy callback argument count and contents, rectangle match decisions, `pUser` allocation and destructor behavior, query callback traversal fields, queue counts, rowid visibility on leaf entries, score ordering, and error propagation from Tcl scripts. Memory sanitizer coverage is useful because this file crosses Tcl, SQLite, and manually allocated context objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/rtree/test_rtreedoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/changeset.c -->
# sources/storage-engines/sqlite/ext/session/changeset.c

## Purpose
`changeset.c` implements a standalone command-line utility for inspecting, transforming, and applying SQLite session extension changeset blobs. It is a developer/test tool around the `sqlite3changeset_*` APIs rather than a library component.

## Important APIs, Types, And Functions
`usage()` prints supported commands. `readFile()` reads an entire changeset file into SQLite-allocated memory. `renderValue()` formats `sqlite3_value` objects as SQL-ish literals for dumps and pseudo-SQL output. `conflictCallback()` formats apply conflicts and returns `SQLITE_CHANGESET_OMIT`.

The `main()` command dispatcher supports:
`apply DB [OPTIONS]` to apply a changeset to a database;
`concat FILE2 OUT` to concatenate two changesets;
`dump` to print detailed changeset contents;
`invert OUT` to write an inverted changeset;
`sql` to print pseudo-SQL representing the changeset.

The file exercises session APIs including `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2()`, `sqlite3changeset_concat()`, `sqlite3changeset_invert()`, `sqlite3changeset_start()`, `sqlite3changeset_next()`, `sqlite3changeset_finalize()`, `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, and `sqlite3changeset_new()`.

## Control Flow
Startup requires at least a file and command. The input changeset is read before command dispatch. `apply` parses flags, opens the target database, optionally enables foreign keys, begins a transaction, applies the changeset with conflict handling, and commits only if there are no conflicts, no dry-run request, and no apply error.

`concat` reads a second file, calls `sqlite3changeset_concat()`, and writes the output. `invert` calls `sqlite3changeset_invert()` and writes the result. `dump` iterates through changes, prints operation metadata, primary-key flags, and old/new values. `sql` iterates through changes and emits a simple transaction containing DELETE, UPDATE, or INSERT statements with synthetic column names `c1`, `c2`, and so on.

## State And Persistence Behavior
The tool keeps the input and generated changesets in memory. `apply` is the only command that mutates a database, and it wraps the operation in an explicit transaction. Conflicts, dry-run mode, and apply errors cause rollback. `concat` and `invert` overwrite their output file if opened successfully.

`nConflict` is a process-global counter reset before apply. Conflict handling always returns omit, leaving final commit/rollback policy to `main()`.

## Dependencies
The file depends on SQLite with the session extension APIs enabled, standard C file IO, string handling, ctype, and assertions. It relies on SQLite memory allocation for buffers returned by changeset APIs.

## Integration Points
This utility is useful in session extension tests and debugging pipelines. It can render changesets for human inspection, combine generated changesets, invert them for undo-style testing, and apply them to fixture databases while exposing conflict diagnostics.

## Risks And Edge Cases
`readFile()` stores file size in `sqlite3_int64` but returns it through `int`, so very large files can truncate. It only closes the file on successful non-empty reads; empty files and read-error exits do not consistently close before exit, though process termination masks most leaks.

The `apply` option parser normalizes long options by skipping one leading dash, so both `--invert` and `-invert` work, but unsupported spellings fail. Pseudo-SQL output is diagnostic only: column names are synthetic, table quoting is simple, and values are rendered for readability rather than guaranteed replay across all schemas.

`renderValue()` iterates text byte-by-byte and only doubles single quotes; it does not attempt full SQL encoding for all encodings. Conflict handling always omits conflicting changes, so `apply` with conflicts never partially commits because the wrapper rolls back when `nConflict` is non-zero.

## Test Signals
Tests should cover all commands, output file failures, invalid changesets, apply flags (`--dryrun`, `--enablefk`, `--nosavepoint`, `--invert`, `--ignorenoop`, `--fknoaction`), conflict classes, old/new value rendering for NULL, integer, float, text with quotes, and blobs. Transaction tests should verify rollback on conflict and dry-run and commit on clean apply.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/changeset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/changesetfuzz.c -->
# sources/storage-engines/sqlite/ext/session/changesetfuzz.c

## Purpose
`changesetfuzz.c` implements a standalone fuzzer for SQLite session changeset and patchset blobs. It either dumps a human-readable representation of an input changeset or produces deterministic mutated changesets that remain structurally well-formed.

The fuzzer deliberately mutates values, changes, groups, and table schemas while preserving core format invariants such as non-NULL primary keys, valid record encodings, and at least one change per table group.

## Important APIs, Types, And Functions
Fuzz operation constants range from value substitution/modification/randomization through change duplication/deletion/type changes, update field removal, indirect flag toggles, group duplication/deletion/swap, and column add/add-PK/delete mutations.

`FuzzChangeset` stores parsed global state: patchset flag, group array, all value pointers, group/change counts, and update count. `FuzzChangesetGroup` stores one table header and its raw change buffer. `FuzzChange` describes one selected mutation and carries replacement value buffers and iteration state.

File and memory helpers include `fuzzReadFile()`, `fuzzWriteFile()`, `fuzzMalloc()`, and `fuzzFree()`. Deterministic pseudo-random generation is provided by a copied RC4-like SQLite PRNG block: `fuzzRandomByte()`, `fuzzRandomBlob()`, `fuzzRandomInt()`, `fuzzRandomU64()`, and `fuzzRandomSeed()`.

Format helpers include `fuzzGetVarint()`, `fuzzPutVarint()`, `fuzzGetI64()`, `fuzzPutU64()`, `fuzzParseHeader()`, `fuzzChangeSize()`, `fuzzParseRecord()`, `fuzzParseChanges()`, and `fuzzParseChangeset()`. Output/dump helpers are `fuzzPrintRecord()` and `fuzzPrintGroup()`. Mutation is selected by `fuzzSelectChange()`, copied/applied by `fuzzCopyChange()`, and emitted by `fuzzDoOneFuzz()`.

## Control Flow
The program accepts either `changesetfuzz INPUT` or `changesetfuzz INPUT SEED N`. It reads and parses the input into borrowed pointers into the original buffer. With one argument, it prints each table group and change. With seed and count, it allocates an output buffer sized to roughly twice the input plus slack, seeds the PRNG, and writes `N` fuzzed files named `INPUT-0`, `INPUT-1`, and so on.

Parsing loops over table headers beginning with `T` for changesets or `P` for patchsets. Each header supplies column count, primary-key array, and table name. Changes are parsed until the next group header. UPDATE changes have old and new records in changesets; patchset DELETE records may include only primary-key fields.

Fuzz selection randomly chooses an operation and target. Invalid choices return negative status, causing the caller to select again. Examples include trying to delete the only group, deleting the only primary-key column, or reducing an UPDATE that only has one updated non-PK column.

Emission recreates group headers and changes while applying the selected mutation. Column additions append NULL or non-NULL PK values as appropriate. Column deletion rewrites PK indexes when needed and drops UPDATE changes that would no longer update any non-PK field. Change type conversions add or remove old/new records according to session format rules.

## State And Persistence Behavior
Parsed state mostly points into the original input changeset; the program does not deep-copy group names, PK arrays, changes, or values. Generated fuzz outputs are written to new files derived from the input filename and overwrite existing files with the same names.

The PRNG is deterministic and single-threaded. Runs with the same input, seed, and count should produce the same output sequence. No database is opened and no changeset is applied in this file.

## Dependencies
The file depends on `sqlite3.h` for op constants, integer typedefs, and memory allocation, plus standard C file/string/assert/ctype headers. It implements changeset binary parsing itself rather than using `sqlite3changeset_start()`, because it needs pointer-level mutation and rewriting.

## Integration Points
This is a fuzzing support utility for the sessions extension. Outputs are intended to feed changeset parsers and appliers while remaining well-formed enough to exercise semantic and conflict paths instead of being rejected immediately as corrupt.

## Risks And Edge Cases
Manual binary parsing is the key risk. `fuzzGetVarint()` assumes available bytes, and several routines rely on earlier bounds checks. Large varints, huge text/blob lengths, malformed table names, and truncated records must consistently return `SQLITE_CORRUPT` without overread.

Output buffer sizing is heuristic (`input*2 + 1024`). Most mutations are bounded, but repeated or unexpectedly large schema/value changes could exceed assumptions if future mutation modes are added. `fuzzPutVarint()` asserts the encoded value is positive and below `2^21`, so extremely wide schemas are not supported.

Value mutation must preserve session invariants. The code avoids setting primary keys to NULL, avoids replacing undefined values incorrectly, and rejects mutations that make updates empty. These constraints are subtle, especially for patchset DELETE records and type conversions between INSERT, DELETE, and UPDATE.

## Test Signals
Good tests should parse and dump changesets and patchsets with integers, reals, NULL, undefined, text, and blobs; verify deterministic output for fixed seeds; and feed generated outputs to SQLite's changeset parser/applier. Mutation-specific tests should cover each `FUZZ_*` mode, PK column deletion rejection, group deletion rejection for single-group inputs, UPDATE field reduction, patchset DELETE handling, and schema column add/delete transformations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/changesetfuzz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/session_speed_test.c -->
# sources/storage-engines/sqlite/ext/session/session_speed_test.c

## Purpose
`session_speed_test.c` is a standalone benchmark-style test program for SQLite's sessions module. It creates two databases with the same schema, captures insert/update/delete workloads from one database as changesets, and applies those changesets to the second database.

## Important APIs, Types, And Functions
The file contains a small generic command-line parser built around `CmdLineOption` and option type constants. Parser helpers include `option_requires_argument_error()`, `ambiguous_option_error()`, `unknown_option_error()`, `get_integer_option()`, `get_boolean_option()`, and `parse_command_line()`.

SQLite helpers are `abort_due_to_error()`, `execsql()`, and `xConflict()`. `run_test()` is the benchmark core: it creates a session, attaches all tables, prepares one parameterized SQL statement, runs it `nRow` times in a transaction, extracts a changeset with `sqlite3session_changeset()`, commits, and applies the changeset to the second database with `sqlite3changeset_apply()`.

`main()` parses options, defines rowid and WITHOUT ROWID schemas, text/blob and integer workloads, opens two fresh database files, creates schema in both, and runs insert, update, and delete phases.

## Control Flow
The parser supports abbreviated unambiguous options. Recognized options are `-rows`, `-without-rowid`, `-integer`, `-all`, `-database`, and `-cmdline:verbose`.

For each selected combination, `main()` unlinks old database files, opens the primary and replica databases, creates table `t1`, then calls `run_test()` three times using insert, update, and delete SQL. Each `run_test()` captures only the changes made by that phase and applies the resulting changeset immediately to the replica database.

`xConflict()` always returns `SQLITE_CHANGESET_ABORT`, so any apply conflict aborts the benchmark. Errors are intended to terminate the process through `abort_due_to_error()`.

## State And Persistence Behavior
The program writes two database files: the configured `-database` path and a second path with `2` appended. Existing files at those paths are unlinked before each selected run. It does not persist benchmark results beyond stdout and the final database files.

Session state is transient per phase. Each phase creates and deletes its own `sqlite3_session`, changeset buffer, and prepared statement. Database mutations are committed before applying the captured changeset to the second database.

## Dependencies
The file depends on SQLite with sessions enabled, standard C libraries, `<stddef.h>` for `offsetof`, and `<unistd.h>` for `unlink`. It uses `sqlite3_session`, changeset extraction, and changeset apply APIs.

## Integration Points
This utility is a performance and smoke-test harness for the session extension. It exercises rowid and WITHOUT ROWID tables, text/blob payloads and integer payloads, and the full capture/apply path for inserts, updates, and deletes.

## Risks And Edge Cases
There are two notable defects. `abort_due_to_error()` calls `fprintf(stderr, "Error: %d\n");` without passing `rc`, which is undefined behavior and loses the actual error code. In the `-all` loop, the printed/filter loop variables are `bWithoutRowid` and `bInteger`, but schema and SQL arrays are indexed with `o.bWithoutRowid` and `o.bInteger`; as a result, `-all` appears to repeat the option defaults instead of exercising all four combinations.

The program does not time operations directly despite being a speed test; it depends on external timing. It also does not validate that the two databases are equivalent after apply. Option abbreviation is convenient but can become ambiguous if new options share prefixes.

## Test Signals
Tests should run each option combination explicitly and with `-all`, verify database equivalence after insert/update/delete phases, force apply conflicts to validate abort behavior, and run under sanitizers to catch the `fprintf` varargs bug. Parser tests should cover abbreviations, ambiguity, missing arguments, boolean parsing, and verbose command-line echo.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/session/session_speed_test.c -->
