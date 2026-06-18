# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 151745-158971

## Scope

This chunk covers a large middle section of SQLite's amalgamated `sqlite3.c`. It starts in the tail of `select.c` aggregate accumulator code, then includes complete or partial embedded source-file sections for:

- `select.c`: the end of aggregate step generation, simple `count(*)` explain output, HAVING-to-WHERE movement, self-join view detection, count-of-UNION-ALL view optimization, subquery coroutine eligibility, and almost all of `sqlite3Select()`.
- `table.c`: `sqlite3_get_table()` and `sqlite3_free_table()` wrappers over `sqlite3_exec()`.
- `trigger.c`: trigger object creation, trigger-step builders, trigger lookup/drop/unlink, RETURNING handling, trigger subprogram generation, trigger invocation, and old/new column mask calculation.
- `update.c`: ordinary table/view/UPDATE-FROM/UPSERT UPDATE code generation plus virtual-table UPDATE support.
- `upsert.c`: `Upsert` lifetime, target analysis, index matching, and DO UPDATE dispatch.
- `vacuum.c`: VACUUM opcode generation and most of `sqlite3RunVacuum()`.
- `vtab.c`: virtual table module registration, constructor calls, schema declaration, transaction hooks, savepoint hooks, function overloads, writable marking, eponymous table setup, and vtab configuration APIs.
- The chunk ends at the beginning of `wherecode.c` and included `whereInt.h` comments. WHERE loop code generation itself continues in the next chunk.

This is executable core database engine code, not a test harness despite living under WiredTiger's third-party SQLite test copy.

## Purpose

The covered code translates parsed SQL constructs into SQLite VDBE bytecode and manages several public or extension-facing APIs. The main responsibilities are:

- Generate SELECT bytecode for ordinary scans, DISTINCT, ORDER BY, aggregate queries, GROUP BY, subqueries, views, CTEs, window-rewritten selects, and simple `count(*)` fast paths.
- Materialize `sqlite3_get_table()` result arrays for legacy callers.
- Build, store, delete, and execute triggers, including inline RETURNING support and trigger subprogram caching.
- Generate UPDATE bytecode for rowid tables, WITHOUT ROWID tables, views with triggers, virtual tables, UPDATE-FROM, limited UPDATE builds, foreign keys, generated columns, conflict policies, and UPSERT DO UPDATE.
- Analyze UPSERT conflict targets and route failed unique constraints to matching `ON CONFLICT` clauses.
- Implement VACUUM by attaching a transient database, recreating schema/data, copying btree content back or into a named output, and restoring connection state.
- Register and manage virtual table modules, call `xCreate`/`xConnect`/`xDestroy`, handle `sqlite3_declare_vtab()`, and coordinate virtual table transaction/savepoint callbacks.

## Important APIs, Types, and Functions

### SELECT and Aggregate Code Generation

- `updateAccumulator()` tail at the start of the chunk emits `OP_AggStep`, ORDER BY aggregate sorter inserts, DISTINCT filtering through `codeDistinct()`, collation selection for aggregate functions needing collations, and accumulator column refresh logic.
- `explainSimpleCount()` emits an `EXPLAIN QUERY PLAN` scan line for optimized `SELECT count(*) FROM table`.
- `havingToWhereExprCb()` and `havingToWhere()` move HAVING terms that are constant or GROUP BY-equivalent into WHERE, replacing the HAVING term with integer `1`.
- `isSelfJoinView()` detects repeated materialized view/subquery instances that can share a materialization, while rejecting push-down-modified views, coroutine views, and ambiguous CTE copies.
- `agginfoFree()` releases `AggInfo` arrays registered with parser cleanup.
- `countOfViewOptimization()` rewrites `SELECT count(*) FROM (SELECT ... UNION ALL SELECT ...)` into a sum of per-arm `count(*)` scalar subqueries when the compound subquery has no WHERE, LIMIT, GROUP BY/HAVING, aggregate, or DISTINCT terms.
- `sameSrcAlias()` supports UPDATE-FROM validation by finding duplicate target aliases in nested FROM sources.
- `fromClauseTermCanBeCoroutine()` decides whether a FROM-subquery can run as a coroutine instead of being materialized, excluding materialized or multiply-used CTEs, RIGHT/FULL join left operands, disabled coroutine optimization, self-joined views, UPDATE-FROM cases, and join shapes that cannot put the subquery in an outer loop.
- `sqlite3Select()` is the central SELECT compiler. It performs preparation, name resolution, window rewriting, FROM-clause optimization, compound SELECT dispatch, constant propagation, count-of-view rewriting, subquery code generation, DISTINCT-to-GROUP-BY rewriting, sorter/distinct setup, LIMIT setup, scan generation, aggregate/GROUP BY generation, result output, ORDER BY tail generation, and debug self-checks.

### `sqlite3_get_table()`

- `TabResult` accumulates `char **azResult`, row/column counts, allocated slots, used slots, error message, and callback return code.
- `sqlite3_get_table_cb()` appends column names on the first row, validates consistent column counts, copies row values, expands the result pointer array, and records out-of-memory or incompatible-query errors.
- `sqlite3_get_table()` initializes `TabResult`, runs `sqlite3_exec()`, handles aborts from the callback, shrinks the pointer array, returns row/column counts, and stores the slot count in the hidden element immediately before the public result pointer.
- `sqlite3_free_table()` walks that hidden slot count and frees all copied strings and the pointer array.

### Trigger Handling

- `sqlite3DeleteTriggerStep()`, `sqlite3DeleteTrigger()`, and `sqlite3UnlinkAndDeleteTrigger()` free trigger steps, trigger objects, and schema hash/table links.
- `sqlite3TriggerList()` merges TEMP triggers with persistent table triggers and also binds the synthetic RETURNING trigger to the current target table.
- `sqlite3BeginTrigger()` validates CREATE TRIGGER names, schema qualification, target table/view rules, virtual/shadow/system-table restrictions, authorization, orphan TEMP triggers, and initializes `pParse->pNewTrigger`.
- `sqlite3FinishTrigger()` fixes trigger-step schema references, writes the `sqlite_schema` row for new triggers, changes schema cookies, and installs triggers into schema hashes during schema load.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` construct `TriggerStep` nodes, duplicating parse trees unless rename processing requires preserving original pointers.
- `sqlite3TriggersExist()` and `triggersReallyExist()` filter trigger lists by operation, UPDATE OF columns, enabled-trigger configuration, RETURNING triggers, virtual table restrictions, and BEFORE/AFTER masks.
- `sqlite3TriggerStepSrc()` converts a trigger step target name and optional UPDATE-FROM list into a `SrcList`, schema-pinning non-TEMP triggers to their owning database.
- `sqlite3ExpandReturning()`, `sqlite3ProcessReturningSubqueries()`, and `codeReturningTrigger()` expand RETURNING expressions, mark self-referencing subqueries as correlated, resolve RETURNING names against OLD/NEW-style base registers, and store RETURNING rows in an ephemeral result cursor.
- `codeTriggerProgram()`, `codeRowTrigger()`, `getRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, and `sqlite3CodeRowTrigger()` compile trigger bodies into reusable `SubProgram` bytecode and emit `OP_Program` calls or inline RETURNING code.
- `sqlite3TriggerColmask()` returns old/new column-use masks by compiling or retrieving trigger programs, allowing UPDATE/DELETE callers to avoid loading columns that triggers do not reference.

### UPDATE and UPSERT

- `sqlite3ColumnDefault()` attaches literal ALTER TABLE default values to `OP_Column` and emits `OP_RealAffinity` for REAL columns from ordinary tables.
- `indexColumnIsBeingUpdated()` and `indexWhereClauseMightChange()` conservatively decide whether an index or partial-index predicate depends on changing columns or rowid.
- `updateFromSelect()` builds a SELECT that writes candidate row identifiers, primary keys, view columns, and SET expressions into an ephemeral table for UPDATE-FROM or limited UPDATE flows.
- `sqlite3Update()` is the UPDATE compiler. It resolves target columns, generated-column dependencies, authorization, triggers, foreign keys, index update needs, cursor allocation, one-pass eligibility, row collection, old/new register loading, BEFORE/AFTER triggers, constraint checks, FK actions, row/index deletion and insertion, change counts, and cleanup.
- `updateVirtualTable()` emits `OP_VUpdate` for virtual tables, using a one-pass path when the virtual table scan can match at most one row and an ephemeral table otherwise. It passes `OPFLAG_NOCHNG` values so `sqlite3_vtab_nochange()` can observe unchanged columns.
- `sqlite3UpsertDelete()`, `sqlite3UpsertDup()`, and `sqlite3UpsertNew()` manage `Upsert` object lifetime.
- `sqlite3UpsertAnalyzeTarget()` resolves conflict targets, matches them to rowid or unique indexes including partial-index WHERE clauses and expression indexes, marks duplicate ON CONFLICT clauses, and reports unmatched targets.
- `sqlite3UpsertNextIsIPK()` and `sqlite3UpsertOfIndex()` help the INSERT constraint checker find the next relevant upsert clause.
- `sqlite3UpsertDoUpdate()` seeks from a failed unique index cursor to the table row if needed, applies REAL affinity to `excluded.*` data, and calls `sqlite3Update()` with the upsert's SET and WHERE expressions.

### VACUUM

- `execSql()` prepares and runs SQL, recursively executing single-column SELECT results only if the generated text starts with `CRE` or `INS`, which prevents corrupted schema SQL from executing arbitrary statement classes during VACUUM.
- `execSqlF()` formats SQL using SQLite allocation and calls `execSql()`.
- `sqlite3Vacuum()` emits `OP_Vacuum` after resolving an optional database name and optional VACUUM INTO expression.
- `sqlite3RunVacuum()` enforces autocommit and no-other-active-statement constraints, saves connection flags/counters/tracing/open flags, attaches a randomized transient database or output file, mirrors schema and data, copies btree metadata/content, commits the transient btree, restores flags, closes and detaches the transient database, and resets schemas.

### Virtual Tables

- `struct VtabCtx` tracks the active `xCreate`/`xConnect` constructor context, the in-progress `VTable`, the owning `Table`, and whether `sqlite3_declare_vtab()` has been called.
- `sqlite3VtabCreateModule()`, `createModule()`, `sqlite3_create_module()`, `sqlite3_create_module_v2()`, and `sqlite3_drop_modules()` register, replace, unregister, or bulk-drop virtual table modules.
- `sqlite3VtabModuleUnref()`, `sqlite3VtabLock()`, `sqlite3VtabUnlock()`, `sqlite3GetVTable()`, `vtabDisconnectAll()`, `sqlite3VtabDisconnect()`, `sqlite3VtabUnlockList()`, and `sqlite3VtabClear()` manage per-connection `VTable` references and deferred disconnect lists.
- `sqlite3VtabBeginParse()`, `addArgumentToVtab()`, `sqlite3VtabArgInit()`, `sqlite3VtabArgExtend()`, and `sqlite3VtabFinishParse()` parse `CREATE VIRTUAL TABLE`, store module arguments, write schema rows, issue `OP_VCreate`, and install schema-loaded virtual tables.
- `vtabCallConstructor()`, `sqlite3VtabCallConnect()`, and `sqlite3VtabCallCreate()` call module constructors, guard against recursive constructor calls, verify schema declaration, copy declared columns/index metadata, identify hidden columns, and enroll created vtabs in transaction tracking.
- `sqlite3_declare_vtab()` validates and parses the supplied CREATE TABLE statement, transfers columns/index metadata into the virtual table, and rejects writable WITHOUT ROWID virtual tables with multi-column primary keys.
- `sqlite3VtabCallDestroy()`, `sqlite3VtabSync()`, `sqlite3VtabRollback()`, `sqlite3VtabCommit()`, `sqlite3VtabBegin()`, and `sqlite3VtabSavepoint()` bridge DROP TABLE, commit, rollback, xSync, xBegin, xSavepoint, xRollbackTo, and xRelease module callbacks.
- `sqlite3VtabOverloadFunction()` lets modules overload MATCH, LIKE, GLOB, and REGEXP-style functions for virtual table columns through `xFindFunction`.
- `sqlite3VtabMakeWritable()` records virtual tables needing `OP_VBegin`.
- `sqlite3VtabEponymousTableInit()` and `sqlite3VtabEponymousTableClear()` create and destroy eponymous virtual table instances for modules whose `xCreate` is absent or aliases `xConnect`.
- `sqlite3_vtab_on_conflict()` exposes the active conflict mode to `xUpdate()`.
- `sqlite3_vtab_config()` records constraint support, innocuous/direct-only risk, and all-schema usage during constructor execution.

## Control Flow

`sqlite3Select()` has the densest control flow in this chunk. It first rejects invalid parse state and authorizes `SQLITE_SELECT`, drops ignorable ORDER BY/DISTINCT for certain destinations, runs `sqlite3SelectPrep()`, validates UPDATE-FROM aliases, generates output column names, and optionally rewrites window functions. It then loops through FROM terms to reduce outer joins, remove harmless subquery ORDER BY clauses, and flatten eligible subqueries. Compound SELECTs dispatch to `multiSelect()` and return early.

For simple SELECTs, `sqlite3Select()` may propagate constants, rewrite count-of-UNION-ALL views, authorize unreferenced tables, push WHERE terms into subqueries, null unused subquery columns, and generate subquery implementations. Subqueries may become coroutines, reuse existing CTE materialization, reuse a self-joined view's materialization, or be materialized into ephemeral tables/subroutines. After this, DISTINCT plus matching ORDER BY may become GROUP BY, sort and distinct ephemeral tables are opened, LIMIT registers are prepared, and execution splits into non-aggregate and aggregate paths.

The non-aggregate path starts `sqlite3WhereBegin()`, imports planner signals for distinctness and ordering, no-ops unneeded sorters, optionally delegates window step generation, runs `selectInnerLoop()`, and closes the WHERE loop. The aggregate path builds `AggInfo`, analyzes result/ORDER BY/HAVING expressions, optionally moves HAVING terms into WHERE, handles min/max and DISTINCT aggregate optimizations, and then either performs GROUP BY processing with sorted or already-grouped input, or the no-GROUP-BY path with a special `OP_Count` fast path for `SELECT count(*) FROM table` and a general accumulator scan otherwise. Output subroutines finalize aggregates, apply HAVING, and invoke `selectInnerLoop()`.

`sqlite3Update()` first resolves the target table, triggers, view status, UPDATE-FROM shape, limits, read-only checks, cursors, and update column mapping. It computes generated-column dependency propagation, FK requirements, indexes that need recomputation, REPLACE risk, registers, and optional view materialization. Virtual tables branch to `updateVirtualTable()`. Ordinary tables choose between collecting keys in an ephemeral table and one-pass WHERE updates. Per row, it computes new rowid/PK values, loads old values needed by FKs/triggers, builds `NEW.*`, computes generated columns, fires BEFORE triggers, reloads unmodified columns after BEFORE triggers, checks constraints and FKs, deletes old index entries/row as needed, inserts new records/index entries, runs FK actions, counts changes, fires AFTER triggers, and advances the loop.

Trigger execution has two paths. Ordinary triggers are compiled once per top-level parse/or-conflict pair into `SubProgram` bytecode through `codeRowTrigger()` and then invoked by `OP_Program`. RETURNING triggers are not subprograms; `codeReturningTrigger()` builds and resolves RETURNING expressions inline and inserts each RETURNING row into a cursor owned by the current statement.

`sqlite3RunVacuum()` uses SQL execution as orchestration: attach transient database, create mirrored schema from selected schema SQL, copy table data with generated INSERT statements, copy views/triggers/virtual table schema rows directly, then copy btree metadata and content. All exits converge through `end_of_vacuum`, which restores saved connection state, closes the transient btree, resets schemas, and returns the saved error code.

Virtual table constructors flow through `vtabCallConstructor()`. The active context is pushed on `db->pVtabCtx`, `xCreate` or `xConnect` is called, the constructor must call `sqlite3_declare_vtab()`, and then the resulting `sqlite3_vtab` is wired to a `VTable` with module reference counts and hidden-column metadata. Transaction hooks are tracked in `db->aVTrans`; commit/rollback/finalizer paths lock and unlock each `VTable` around callbacks and clear the transaction array.

## State and Persistence Behavior

This chunk manipulates several layers of state:

- Parser/codegen state: `Parse` fields such as `nMem`, `nTab`, `nErr`, `zAuthContext`, `pTriggerPrg`, `pNewTrigger`, `eTriggerOp`, `pTriggerTab`, `bReturning`, and cleanup lists are updated heavily. Many AST nodes are duplicated or registered for parser cleanup to avoid leaks on early exits.
- VDBE state: bytecode cursors, registers, labels, ephemeral btrees, sorters, coroutines, subprograms, and P4 payloads are emitted for SELECT, triggers, UPDATE, VACUUM, and virtual tables.
- Schema state: triggers are inserted into or removed from schema hashes and table trigger lists; virtual tables are stored in `sqlite_schema` with `rootpage=0`; VACUUM resets all connection schemas after replacing or copying database content.
- Table/index persistence: UPDATE emits record and index deletion/insertion bytecode, enforces constraints, updates autoincrement state, and may cascade foreign key actions. VACUUM rewrites the database image and selected btree metadata.
- Trigger persistence: CREATE TRIGGER writes a `sqlite_schema` row outside schema initialization and installs trigger objects during schema reload. DROP TRIGGER removes schema rows and emits `OP_DropTrigger`.
- `sqlite3_get_table()` persistence is caller-owned heap state. It stores a hidden element count before the returned pointer and requires `sqlite3_free_table()`.
- Virtual table connection state: registered modules live in `db->aModule`; per-connection `VTable` objects hang off `Table.u.vtab.p` or `db->pDisconnect`; transaction participants live in `db->aVTrans`; constructor context lives temporarily in `db->pVtabCtx`.
- VACUUM temporarily changes connection flags such as writable schema, disabled checks/FKs/defensive/count rows/reverse order, trace settings, open flags, change counters, `db->init.iDb`, and `db->autoCommit`, then restores them on exit.

The code is allocation-heavy but uses SQLite's ownership conventions: parse-tree inputs are usually consumed and freed by cleanup labels, duplicated when needed for deferred compilation, and protected by `db->mallocFailed` checks.

## Dependencies and Integration Points

The code depends on SQLite's internal AST, schema, planner, VDBE, btree, pager, and authorization subsystems. Important internal integration points include:

- Name resolution and expression walkers: `sqlite3SelectPrep()`, `sqlite3ResolveExprNames()`, `sqlite3ResolveExprListNames()`, `sqlite3WalkExpr()`, aggregate analyzers, collation lookup, and generated-column expression helpers.
- Planner and WHERE code: `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereOkOnePass()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereOutputRowCount()`, min/max early-out, and ORDER BY LIMIT optimization labels.
- VDBE builders: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChange*()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeTakeOpArray()`, `OP_AggStep`, `OP_Count`, `OP_Program`, `OP_VUpdate`, `OP_Vacuum`, and many cursor/sorter opcodes.
- Schema/auth APIs: `sqlite3AuthCheck()`, `sqlite3CodeVerifySchema()`, `sqlite3NestedParse()`, schema cookies, schema hash tables, `sqlite3Fix*()` database-name fixers, and rename token remapping.
- Constraint and write paths: `sqlite3GenerateConstraintChecks()`, `sqlite3CompleteInsertion()`, `sqlite3GenerateRowIndexDelete()`, `sqlite3FkRequired()`, `sqlite3FkCheck()`, `sqlite3FkActions()`, autoincrement finalization, and pre-update hook support.
- Btree/pager/VFS layers: VACUUM calls `sqlite3BtreeBeginTrans()`, page-size/autovacuum setters, metadata getters/updaters, `sqlite3BtreeCopyFile()`, `sqlite3BtreeCommit()`, pager journal-mode checks, and file-size checks for VACUUM INTO output.
- Virtual table module ABI: public module methods `xCreate`, `xConnect`, `xDestroy`, `xDisconnect`, `xUpdate`, `xBegin`, `xSync`, `xCommit`, `xRollback`, `xSavepoint`, `xRollbackTo`, `xRelease`, and `xFindFunction`, plus public APIs `sqlite3_create_module*()`, `sqlite3_declare_vtab()`, `sqlite3_vtab_config()`, and `sqlite3_vtab_on_conflict()`.
- Compile-time feature gates: `SQLITE_OMIT_GET_TABLE`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_VACUUM`, `SQLITE_OMIT_ATTACH`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ALLOW_ROWID_IN_VIEW`, and tracing/debug macros.

In this repository, the immediate consumer is WiredTiger's vendored SQLite copy used by tests. Behavioral changes here would affect SQLite SQL execution semantics inside that embedded test dependency rather than WiredTiger storage-engine code directly.

## Risks and Edge Cases

- SELECT codegen is high-risk because many optimizations mutate the AST in place. Incorrect HAVING pushdown, ORDER BY omission, subquery flattening, coroutine choice, or count-of-view rewriting can silently change query results.
- Aggregate handling is sensitive to first-row behavior, min/max accumulator "magnet" registers, FILTER clauses, DISTINCT aggregate handling, and ORDER BY aggregate sorters. Register or label mistakes can produce wrong aggregates only for narrow query shapes.
- GROUP BY code has two paths: naturally grouped planner output and sorter-backed grouping. Bugs can appear only when planner ordering changes, when DISTINCT combines with GROUP BY, or when ORDER BY is considered redundant.
- Trigger code must carefully duplicate parse trees or retain originals during ALTER TABLE rename processing. Ownership mistakes lead to leaks, double frees, or stale rename-token mappings.
- RETURNING is implemented as a synthetic trigger but generated inline. It must only run for the current statement and must correctly expand `*`, reject `TABLE.*`, resolve self-referencing subqueries as variable, and avoid firing in nested statements where disallowed.
- UPDATE one-pass optimization is correctness-sensitive. It deliberately falls back when triggers, FKs, key changes, REPLACE, nested updates, subqueries, or updated scan indexes might invalidate the current cursor or cause loops.
- UPDATE-FROM uses ephemeral tables to separate row discovery from modification. Wrong primary-key/rowid packing can update the wrong row or mishandle duplicate join matches.
- Generated columns are not directly updatable but may become implicitly changed by dependencies. Missed dependency propagation can leave stored/generated values or constraints inconsistent.
- WITHOUT ROWID paths use composite PK records and index cursors instead of rowid. Many UPDATE, UPSERT, and virtual-table paths have separate handling and stricter assumptions.
- `sqlite3_get_table()` stores metadata before the returned pointer. Any caller freeing it directly or passing an offset pointer other than the returned value will corrupt memory; the code relies on `sqlite3_free_table()`.
- VACUUM executes SQL text from `sqlite_schema` but restricts recursive generated statements to CREATE/INSERT prefixes. Any relaxation there would re-open historical schema-corruption attack surfaces.
- VACUUM temporarily disables defensive mode, FKs, checks, count rows, and tracing. Failure exits must restore every saved flag and close the transient database; leaks here would affect subsequent statements on the same connection.
- Virtual table constructor handling is reentrancy-sensitive. Recursive constructor calls return `SQLITE_LOCKED`, and constructors must call `sqlite3_declare_vtab()`. Bad reference counts can leak modules or disconnect live vtabs.
- Virtual table transaction/savepoint callbacks run while manipulating `db->aVTrans`; writes during xSync are explicitly rejected by `sqlite3VtabInSync()` behavior checked in `sqlite3VtabBegin()`.
- Security/risk flags from `sqlite3_vtab_config()` affect whether a vtab is treated as innocuous, direct-only, all-schema-using, or constraint-supporting. Incorrect propagation can alter trusted-schema and planner behavior.

## Test and Validation Signals

Useful validation for this chunk should exercise SQL behavior rather than line-level unit tests:

- SELECT regression suites covering subquery flattening, FROM-subquery materialization, coroutine subqueries, self-joined views, CTE materialization hints, UPDATE-FROM alias rejection, DISTINCT ORDER BY rewrite, GROUP BY sorting vs index grouping, HAVING pushdown, min/max optimization, simple count optimization, window-rewritten SELECTs, and aggregate FILTER/DISTINCT/ORDER BY combinations.
- `sqlite3_get_table()` tests for zero rows, column-name row construction, NULL values, multiple statements with incompatible column counts, callback abort, OOM paths, and correct `sqlite3_free_table()` behavior.
- Trigger tests for TEMP triggers, orphan TEMP triggers during schema load, triggers on views vs tables, virtual/shadow/system table restrictions, CREATE/DROP schema updates, BEFORE trigger row deletion/modification, UPDATE OF column filtering, recursive-trigger configuration, conflict policy inheritance, and trigger subprogram reuse.
- RETURNING tests for INSERT/UPDATE/DELETE, UPSERT UPDATE firing, wildcard expansion, rejection of `TABLE.*`, virtual table restrictions, subqueries that reference the modified table, generated column expressions, and nested trigger interactions.
- UPDATE tests for rowid changes, INTEGER PRIMARY KEY aliases, WITHOUT ROWID primary key changes, generated columns, partial/expression index updates, REPLACE conflicts, foreign keys, pre-update hook behavior, UPDATE-FROM, limited UPDATE builds, one-pass vs two-pass plans, and views with INSTEAD OF triggers.
- Virtual table UPDATE tests for one-pass and ephemeral strategies, rowid and WITHOUT ROWID virtual tables, `sqlite3_vtab_nochange()`, conflict policy reporting, `xUpdate` error propagation, and writable marking via `OP_VBegin`.
- UPSERT tests for rowid targets, unique indexes, expression indexes, partial unique indexes, duplicate ON CONFLICT clauses, unmatched conflict targets, DO NOTHING vs DO UPDATE, and seeking from secondary unique indexes to table rows.
- VACUUM tests for ordinary VACUUM, VACUUM INTO existing/non-text output paths, WAL page-size behavior, autovacuum/page-size metadata preservation, schema cookie increment, corrupted schema SQL safety, in-transaction rejection, active-statement rejection, and cleanup after attach/copy failures.
- Virtual table API tests for module registration/replacement/drop, destructor invocation on failed registration, `sqlite3_declare_vtab()` misuse and syntax validation, hidden-column parsing, eponymous virtual tables, recursive constructor locking, `xDestroy` lock handling, xSync/xCommit/xRollback/xSavepoint ordering, xFindFunction overloads, and `sqlite3_vtab_config()` option handling.

## Chunk Boundary Notes

The chunk begins inside aggregate accumulator update generation, so surrounding setup for `updateAccumulator()` and related `AggInfo` helpers is in the previous chunk. It ends after the `wherecode.c` and `whereInt.h` opening comments, before the WHERE planner/codegen structures and routines continue. The later merge lane should connect this report with adjacent chunks to present whole-file SELECT/update/where interactions coherently.
