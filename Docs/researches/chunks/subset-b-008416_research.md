# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 75678-83001

## Scope

This chunk covers the tail of SQLite `select.c`, then full or partial sections of `table.c`, `trigger.c`, `update.c`, `vacuum.c`, `vtab.c`, and the opening of `where.c` in the FoundationDB-vendored SQLite 3.7.6 amalgamation. The code is almost entirely parser/code-generator and schema/virtual-table infrastructure: it converts resolved parse trees into VDBE programs, manages trigger and virtual-table metadata, implements UPDATE and VACUUM code paths, and starts WHERE-clause optimizer analysis.

The covered line range is not a self-contained feature boundary. It begins inside result-column derivation for SELECT statements and ends inside the comments for OR-clause analysis in the WHERE optimizer.

## Purpose

The main purpose of this chunk is to bridge high-level SQL constructs to lower-level VDBE and B-tree behavior:

- SELECT result metadata, compound SELECT execution, query flattening, aggregate execution, DISTINCT, ORDER BY, GROUP BY, LIMIT, and simple count/min/max optimizations.
- The legacy `sqlite3_get_table()` wrapper that materializes callback results into a heap-allocated table.
- CREATE/DROP trigger parsing, trigger-step representation, trigger subprogram compilation, trigger invocation, and old/new column mask discovery.
- UPDATE statement code generation for ordinary tables, views with INSTEAD OF triggers, foreign keys, rowid changes, index maintenance, one-pass updates, and virtual table updates.
- VACUUM implementation by copying the main database into an attached temporary database and then copying the compacted B-tree file back.
- Virtual table module registration, CREATE VIRTUAL TABLE parsing, schema declaration, xCreate/xConnect/xDestroy, vtab transaction hooks, function overloading, and write-lock tracking.
- Initial WHERE optimizer structures and helper routines that decompose predicates into indexable terms.

For the FoundationDB integration, the persistence-sensitive code in this chunk is especially relevant around UPDATE, VACUUM, virtual table callbacks, schema cookies, temporary B-trees, and VDBE opcodes that open/write/delete records.

## SELECT Code Generation

The opening functions build SELECT result metadata:

- `selectColumnsFromExprList()` derives a `Column[]` list from a SELECT expression list. It chooses names from explicit `AS` aliases, source-table column names, identifiers, or expression spans, then appends `:N` suffixes to make names unique.
- `selectAddColumnTypeAndCollation()` fills in result column type strings, affinity, and collation by inspecting resolved expressions.
- `sqlite3ResultSetOfSelect()` prepares a SELECT, forces short column names while deriving metadata, allocates a transient `Table`, and populates `Table.aCol`, `Table.nCol`, `Table.nRowEst`, and `Table.iPKey`.
- `sqlite3GetVdbe()` lazily allocates the statement VDBE and adds `OP_Trace` when tracing is enabled.
- `computeLimitRegisters()` emits VDBE code to evaluate `LIMIT` and `OFFSET`, stores counters in `Select.iLimit` and `Select.iOffset`, clamps row estimates for integer limits, and jumps to the query end for `LIMIT 0`.

Compound SELECTs are handled by `multiSelect()` and `multiSelectOrderBy()`:

- `multiSelect()` validates that only the rightmost SELECT has `ORDER BY` or `LIMIT`, checks result-column count compatibility, and handles `UNION ALL`, `UNION`, `EXCEPT`, and `INTERSECT`.
- `UNION ALL` reuses the same LIMIT/OFFSET registers across the left and right SELECTs, allowing the right side to be skipped once the limit is reached.
- `UNION` and `EXCEPT` use an ephemeral table keyed by result rows. The left query inserts rows, the right query either inserts more (`UNION`) or removes matching rows (`EXCEPT`), and a final scan converts the temporary table into the requested destination.
- `INTERSECT` uses two ephemeral tables, scans the first, checks each record against the second with `OP_NotFound`, and emits only common rows.
- `multiSelectOrderBy()` implements ordered compound queries with two coroutines, one for the left input and one for the right input. It creates comparison `KeyInfo`, ORDER BY permutations, duplicate-removal state, output subroutines, EOF handlers, and a merge loop driven by `OP_Compare` and `OP_Jump`.

Subquery flattening is implemented by `substExpr()`, `substExprList()`, `substSelect()`, and `flattenSubquery()`. `flattenSubquery()` enforces SQLite's long list of safety restrictions, including aggregate/DISTINCT/LIMIT/ORDER BY interactions, left-join restrictions, compound-subquery restrictions, and OFFSET exclusion. When permitted, it rewrites the outer query's FROM list and expressions so references to the subquery result cursor are replaced with copies of the subquery result expressions. For compound `UNION ALL` subqueries, it duplicates the parent SELECT into a matching compound chain.

`sqlite3Select()` is the central SELECT code generator in this chunk. Its major control flow is:

1. Authorize SELECT and call `sqlite3SelectPrep()`.
2. Expand/materialize FROM subqueries, attempting `flattenSubquery()` before falling back to `SRT_EphemTab`.
3. Route compound SELECTs through `multiSelect()`.
4. Rewrite simple `DISTINCT` to `GROUP BY` when possible, because GROUP BY may use indexes.
5. Open ORDER BY and DISTINCT ephemeral structures when needed.
6. For non-aggregate queries, call `sqlite3WhereBegin()`, run `selectInnerLoop()`, then `sqlite3WhereEnd()`.
7. For aggregate queries, analyze aggregate expressions into `AggInfo`, then choose GROUP BY or single-group logic.
8. Generate sort tail and output metadata as needed.

Aggregate helpers include:

- `resetAccumulator()` initializes aggregate memory registers and opens per-aggregate DISTINCT ephemeral tables.
- `updateAccumulator()` evaluates aggregate arguments, handles DISTINCT filtering, emits `OP_CollSeq` for collation-sensitive aggregates, and emits `OP_AggStep`.
- `finalizeAggFunctions()` emits `OP_AggFinal`.
- `isSimpleCount()` recognizes `SELECT count(*) FROM table` with no WHERE/GROUP BY/subquery/view/virtual table and enables `OP_Count`.
- `minMaxQuery()` recognizes single `min(column)` or `max(column)` aggregate forms so the WHERE planner can try an ordered scan and break after the first useful row.

Important VDBE opcodes emitted here include `OP_OpenEphemeral`, `OP_Rewind`, `OP_Next`, `OP_Sort`, `OP_Compare`, `OP_Permutation`, `OP_Yield`, `OP_Gosub`, `OP_Return`, `OP_If`, `OP_IfZero`, `OP_IfPos`, `OP_AggStep`, `OP_AggFinal`, `OP_Count`, `OP_ResultRow`, and `OP_Close`.

## Table API Wrapper

`table.c` implements the optional `sqlite3_get_table()` and `sqlite3_free_table()` APIs:

- `TabResult` accumulates all callback output from `sqlite3_exec()`.
- `sqlite3_get_table_cb()` allocates/expands a `char **` result array, stores column names as the first row, copies row values, rejects incompatible column counts across multiple statements, and maps allocation failure to `SQLITE_NOMEM`.
- `sqlite3_get_table()` initializes `TabResult`, runs `sqlite3_exec()`, stores the element count in the hidden slot immediately before the returned pointer, shrinks the result array when possible, and returns row/column counts.
- `sqlite3_free_table()` walks the hidden element count and frees every non-null string and the containing array.

This is a convenience API layered on normal statement execution. It persists no database state, but it is sensitive to memory ownership conventions because callers free the shifted pointer returned by `sqlite3_get_table()`.

## Trigger Infrastructure

The trigger section manages both persistent trigger schema entries and per-statement executable subprograms.

Schema and parsing functions:

- `sqlite3TriggerList()` combines table-local triggers with TEMP triggers that target the same table.
- `sqlite3BeginTrigger()` validates trigger name/database placement, target table existence, virtual-table exclusion, system-table exclusion, view/table timing rules, authorization, and duplicate names. It builds `Parse.pNewTrigger`.
- `sqlite3FinishTrigger()` attaches parsed steps, fixes database qualifications, writes the `sqlite_master` entry for new triggers, reparses schema, or inserts the trigger into the schema hash during initialization.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` build reduced copies of trigger body statements.
- `sqlite3DeleteTriggerStep()` and `sqlite3DeleteTrigger()` free trigger trees and trigger-step lists.
- `sqlite3DropTrigger()` resolves a trigger name, preferring TEMP before MAIN for unqualified names.
- `sqlite3DropTriggerPtr()` emits VDBE code that deletes the matching `sqlite_master` row, changes the schema cookie, and emits `OP_DropTrigger`.
- `sqlite3UnlinkAndDeleteTrigger()` removes an in-memory trigger from the schema hash and table trigger list.

Execution functions:

- `sqlite3TriggersExist()` returns the trigger list only if at least one trigger matches operation, timing, and UPDATE column overlap.
- `targetSrcList()` builds a trigger-step target `SrcList`, qualifying it with the trigger database unless the trigger is TEMP.
- `codeTriggerProgram()` walks trigger steps and emits nested INSERT/UPDATE/DELETE/SELECT code. Statement-level ON CONFLICT overrides trigger-step conflict policy.
- `codeRowTrigger()` compiles a trigger into a `SubProgram`, resolving the WHEN clause, emitting an early halt if it is false/null, compiling body statements, and recording old/new column masks.
- `getRowTrigger()` caches compiled trigger programs by trigger pointer and conflict policy in the top-level `Parse`.
- `sqlite3CodeRowTriggerDirect()` emits parent `OP_Program` with the trigger subprogram and sets P5 to block recursive trigger invocation when recursive triggers are disabled.
- `sqlite3CodeRowTrigger()` filters a trigger list by operation, timing, and UPDATE column overlap, then emits each matching trigger.
- `sqlite3TriggerColmask()` compiles or reuses trigger programs to discover which `old.*` or `new.*` columns are read, allowing UPDATE/DELETE code to avoid loading unused columns.

State is split between durable schema rows in `sqlite_master`, in-memory `Schema.trigHash` and `Table.pTrigger`, parse-time `TriggerStep` trees, and VDBE `SubProgram` objects linked from the parent statement.

## UPDATE Code Generation

`sqlite3ColumnDefault()` annotates the most recent `OP_Column` with a P4 default value for columns added by ALTER TABLE and emits `OP_RealAffinity` when a REAL-affinity column may be read from integer storage.

`sqlite3Update()` is the main UPDATE compiler. Its key stages are:

1. Resolve the target table, trigger mask, view status, read-only status, and UPDATE column mapping `aXRef`.
2. Resolve SET expressions and detect rowid changes via INTEGER PRIMARY KEY or rowid aliases.
3. Ask foreign-key code whether old/new FK checks are required.
4. Allocate table/index cursors and per-index registers only for indexes affected by changed columns, unless rowid changes or REPLACE conflict handling require broader access.
5. For virtual tables, delegate to `updateVirtualTable()`.
6. Allocate old rowid, new rowid, old column, and new column registers.
7. Materialize views when updating a view with INSTEAD OF triggers.
8. Use `sqlite3WhereBegin()` to find candidate rows. If one-pass update is not possible, store candidate rowids in a `RowSet`.
9. Open the table and needed indexes for write.
10. Loop candidate rows, recompute rowid when needed, load old columns required by triggers/FKs, compute new column values, fire BEFORE triggers, reload unchanged columns after BEFORE triggers, check constraints and foreign keys, delete old index entries, delete or update the table row, insert new indexes/record, run FK actions, increment row count, and fire AFTER triggers.
11. Close cursors, finish autoincrement bookkeeping, optionally return `"rows updated"`, and free parse-owned inputs.

The one-pass path uses a WHERE plan that can update as it scans without first materializing rowids. The fallback path avoids scan invalidation by collecting rowids first. BEFORE trigger behavior is explicitly documented as undefined if the trigger deletes or renames the row being updated; the generated code checks `OP_NotExists` and skips further work for deleted rows.

`updateVirtualTable()` builds a synthetic SELECT that returns the original rowid, optional new rowid, and all post-update column values. It stores these rows in an ephemeral table, then scans it and emits `OP_VUpdate` for each row. It calls `sqlite3VtabMakeWritable()` so an `OP_VBegin` will be generated for the virtual table transaction.

Persistence-facing UPDATE behavior includes schema write checks, table locks, index B-tree updates, rowid mutation, constraint enforcement, FK checks/actions, autoincrement finalization, and trigger subprogram execution.

## VACUUM

`sqlite3Vacuum()` emits `OP_Vacuum`; `sqlite3RunVacuum()` implements that opcode.

`sqlite3RunVacuum()` requires autocommit mode and no other active SQL statements. It saves connection flags, change counters, and tracing, then temporarily enables writable schema, ignores CHECK constraints, prefers built-ins, disables foreign keys, disables reverse-order scans, and suppresses tracing.

The algorithm is:

1. Attach a temporary database as `vacuum_db`, either in memory or as a temp file.
2. Unlock the temporary B-tree left locked by schema reading.
3. Copy page-size/reserve settings from main, except that encrypted and WAL databases cannot change page size through VACUUM.
4. Set temp synchronous to OFF and mirror auto-vacuum mode.
5. Begin an exclusive transaction.
6. Recreate tables and indexes in `vacuum_db` from `main.sqlite_master`.
7. Copy table contents with generated `INSERT INTO vacuum_db.X SELECT * FROM main.X`.
8. Copy `sqlite_sequence` content when present.
9. Copy view, trigger, and virtual-table `sqlite_master` rows directly.
10. Preserve selected B-tree meta values, incrementing the schema cookie.
11. Copy the compacted temporary B-tree file back into the main B-tree with `sqlite3BtreeCopyFile()`.
12. Commit the temp B-tree, copy auto-vacuum mode/page size back, restore flags/counters/tracing, detach the temp database manually, and reset internal schema.

Risks are concentrated around transaction boundaries and file format metadata. VACUUM directly manipulates B-tree page size, reserve bytes, schema cookies, auto-vacuum state, and the entire main database file image. In this FoundationDB vendored copy, any custom pager/VFS behavior must preserve the assumptions behind attach, temp database creation, B-tree copy, journal cleanup, and schema reset.

## Virtual Tables

The virtual table section implements registration, schema construction, lifecycle, transactions, and function overloading.

Module registration:

- `createModule()` installs a `Module` into `db->aModule`, replacing an existing module and calling its destructor when appropriate.
- `sqlite3_create_module()` and `sqlite3_create_module_v2()` are public API wrappers.

Connection-specific virtual table objects:

- `sqlite3GetVTable()` finds the `VTable` object for a given `sqlite3*` connection.
- `sqlite3VtabLock()`/`sqlite3VtabUnlock()` manage nested reference counts and call module `xDisconnect()` when the count reaches zero.
- `vtabDisconnectAll()` moves per-connection `VTable` objects from `Table.pVTable` to each connection's deferred disconnect list, except optionally preserving the current connection's entry.
- `sqlite3VtabUnlockList()` drains `db->pDisconnect` while holding all required B-tree/database mutexes and expires prepared statements.
- `sqlite3VtabClear()` clears virtual-table module arguments and schedules/disconnects VTable objects before deleting the `Table`.

CREATE VIRTUAL TABLE parsing:

- `sqlite3VtabBeginParse()` starts a virtual table definition, marks the table `TF_Virtual`, and seeds module arguments with module name, database name, and table name.
- `sqlite3VtabArgInit()`/`sqlite3VtabArgExtend()` collect raw module argument token ranges.
- `sqlite3VtabFinishParse()` stores the complete CREATE VIRTUAL TABLE SQL in `sqlite_master`, emits `OP_VCreate`, expires statements, and reparses schema for real creation. During schema load, it installs the in-memory table without calling `xConnect()`.
- `addModuleArgument()` owns argument strings through `Table.azModuleArg`.

Constructors and schema declaration:

- `vtabCallConstructor()` allocates a `VTable`, sets `db->pVTab`, invokes `xCreate` or `xConnect`, requires the module to call `sqlite3_declare_vtab()`, links the VTable into `Table.pVTable`, and processes `"hidden"` column type tokens.
- `sqlite3VtabCallConnect()` lazily connects a loaded virtual table the first time it is used.
- `sqlite3VtabCallCreate()` invokes module `xCreate` for a newly created virtual table and adds it to the virtual table transaction list.
- `sqlite3_declare_vtab()` parses a CREATE TABLE statement supplied by the module and transfers its column definitions to the pending virtual table.
- `sqlite3VtabCallDestroy()` invokes `xDestroy()` on DROP TABLE and removes the VTable from `Table.pVTable`.

Virtual-table transaction hooks:

- `addToVTrans()` grows `db->aVTrans` and locks each participating VTable.
- `sqlite3VtabBegin()` calls `xBegin()` once per virtual table per transaction, unless called while virtual tables are syncing, in which case it returns `SQLITE_LOCKED`.
- `sqlite3VtabSync()` calls `xSync()` on each transaction participant and preserves the first error and message.
- `sqlite3VtabCommit()` and `sqlite3VtabRollback()` use `callFinaliser()` to call `xCommit()` or `xRollback()` and clear `db->aVTrans`.
- `sqlite3VtabMakeWritable()` records tables needing an eventual `OP_VBegin`.

`sqlite3VtabOverloadFunction()` lets a virtual table override functions such as MATCH/LIKE/GLOB/REGEXP for expressions whose first argument is a column of that virtual table. It calls module `xFindFunction()` and creates an ephemeral `FuncDef` when overloaded.

## WHERE Optimizer Opening

The start of `where.c` defines predicate-analysis structures and helpers used later by `sqlite3WhereBegin()`.

Important types:

- `WhereTerm` records one WHERE subexpression, its operator mask, left cursor/column, prerequisite table masks, parent/child relationships for virtual terms, and optional OR/AND analysis payloads.
- `WhereClause` owns an array of `WhereTerm` values and a `WhereMaskSet`.
- `WhereOrInfo` holds decomposed OR terms and the set of tables for which the OR is indexable.
- `WhereAndInfo` holds decomposed AND terms inside a larger OR term.
- `WhereMaskSet` maps sparse VDBE cursor numbers to dense `Bitmask` bits.
- `WhereCost` stores a candidate `WherePlan`, total cost, and used table mask.

Operator and plan flags:

- `WO_*` masks represent exploitable term operators: `IN`, equality, inequalities, `MATCH`, `IS NULL`, compound OR/AND, and no-op terms.
- `WHERE_*` flags represent chosen strategies: rowid equality/range, column equality/range/IN/NULL, index-only scans, ORDER BY satisfaction, reverse scans, uniqueness, virtual table processing, multi-index OR, and temporary indexes.

Helper routines:

- `whereClauseInit()`, `whereClauseClear()`, `whereClauseInsert()`, `whereOrInfoDelete()`, and `whereAndInfoDelete()` manage `WhereClause` storage and ownership of dynamic/virtual expressions.
- `whereSplit()` recursively decomposes a predicate by `TK_AND` or `TK_OR`.
- `initMaskSet`, `getMask()`, and `createMask()` maintain cursor-to-bit mappings.
- `exprTableUsage()`, `exprListTableUsage()`, and `exprSelectTableUsage()` compute table dependency masks after name resolution.
- `allowedOp()` and `operatorMask()` decide which expression operators are indexable and map token operators to `WO_*`.
- `exprCommute()` rewrites `X op Y` into `Y op X` while preserving comparison collation semantics and flipping inequality direction.
- `findTerm()` searches analyzed terms for constraints usable by a given cursor/column/operator set and, when an index is provided, checks affinity and collation compatibility.
- `exprAnalyzeAll()` applies the later `exprAnalyze()` routine to every term.
- `isLikeOrGlob()` recognizes LIKE/GLOB calls that can be transformed into prefix range constraints. It requires a TEXT-affinity column on the left and a literal or bound string pattern on the right that does not begin with a wildcard.
- `isMatchOfColumn()` recognizes virtual-table `column MATCH expr` forms.
- `transferJoinMarkings()` carries outer-join origin metadata to derived optimizer expressions.

The chunk ends as the comments introduce OR-clause analysis. The described optimization creates either an equivalent virtual `IN` term for same-column OR equality chains or marks indexable OR subterms for multi-index OR planning.

## State and Persistence Behavior

Key mutable state in this chunk includes:

- `Parse` counters for VDBE memory registers, cursor numbers, labels, nested parse contexts, and trigger programs.
- `Select` fields such as `pPrior`, `pOrderBy`, `pLimit`, `pOffset`, `iLimit`, `iOffset`, `nSelectRow`, `selFlags`, and ephemeral cursor addresses.
- `AggInfo` arrays and accumulator registers for aggregate queries.
- Schema structures for triggers and virtual tables: `Schema.trigHash`, `Table.pTrigger`, `Table.pVTable`, `Table.azModuleArg`, `sqlite3.aModule`, `sqlite3.aVTrans`, and `sqlite3.pDisconnect`.
- VDBE ephemeral B-trees for compound SELECTs, GROUP BY, DISTINCT, ORDER BY, virtual-table UPDATE staging, and trigger/drop schema scans.
- Persistent tables and indexes modified by UPDATE via `OP_OpenWrite`, index-delete helpers, table deletes, completed insertions, FK checks/actions, and autoincrement finalization.
- `sqlite_master` rows and schema cookies modified by trigger creation/drop, CREATE VIRTUAL TABLE, and VACUUM.
- Whole-file B-tree page layout and metadata modified by VACUUM.

Most code here does not directly call the pager. It emits VDBE operations or uses B-tree APIs, so persistence effects occur later during VDBE execution or through B-tree helper calls in VACUUM.

## Dependencies and Integration Points

This chunk depends heavily on earlier declarations and helper subsystems:

- Expression analysis/codegen: `sqlite3ResolveExprNames()`, `sqlite3ExprCode*()`, `sqlite3ExprAnalyzeAggList()`, `sqlite3ExprCollSeq()`, `sqlite3ExprAffinity()`, expression/list duplication and deletion.
- VDBE construction: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, labels, comments, `OP_*` opcodes, `KeyInfo`, and subprograms.
- WHERE planner: `sqlite3WhereBegin()` and `sqlite3WhereEnd()` are called by SELECT and UPDATE; their internal term-analysis structures begin at the end of this chunk.
- Schema and authorization: schema hash tables, `sqlite3ReadSchema()`, `sqlite3FindTable()`, `sqlite3SrcListLookup()`, `sqlite3Fix*()` routines, `sqlite3AuthCheck()`, schema cookies, and `OP_ParseSchema`.
- DML helpers: insert/delete/update support, row/index delete generation, constraint checks, complete insertion, autoincrement, FK checks/actions.
- Virtual table public API: `sqlite3_module`, `sqlite3_vtab`, `sqlite3_index_info`, `xCreate`, `xConnect`, `xDisconnect`, `xDestroy`, `xBegin`, `xSync`, `xCommit`, `xRollback`, and `xFindFunction`.
- B-tree/pager layer: VACUUM uses `sqlite3Btree*()` and pager journal-mode/page-size APIs directly.

## Risks and Edge Cases

- Subquery flattening is intentionally conservative. Incorrectly relaxing restrictions can change LEFT JOIN null-extension semantics, LIMIT/OFFSET behavior, DISTINCT/aggregate ordering, or compound SELECT results.
- Compound SELECT code mutates `Select` links and LIMIT/OFFSET pointers temporarily. Error paths must restore ownership enough for `sqlite3SelectDelete()` to free the tree correctly.
- Aggregate code relies on clearing expression caches before accumulator writes. The comment references ticket `[883034dcb5]`, where shallow copies of cached text/blob values could be invalidated.
- Trigger compilation caches `SubProgram` objects by trigger pointer and conflict policy. Recursive trigger behavior depends on `SQLITE_RecTriggers` and OP_Program P5.
- UPDATE with BEFORE triggers deliberately has undefined behavior when the trigger deletes or renames the row being updated. The generated code detects deletion and skips the remaining work.
- UPDATE authorization handling can set `aXRef[j] = -1` for ignored columns; code paths must not later assume every SET target remains active.
- `sqlite3Update()` allocates `aRegIdx` with `sizeof(Index*) * nIdx` even though the variable type is `int *`. On platforms where pointer size exceeds int size this overallocates, but it is a noteworthy local oddity.
- VACUUM is not allowed inside a transaction or with other active statements. It temporarily disables foreign keys and checks, manipulates schema directly, and copies the full B-tree file image; any custom storage backend must match SQLite's assumptions around attach/temp DBs, B-tree copy, and journal cleanup.
- Virtual table constructors must call `sqlite3_declare_vtab()`. If they return success without declaring schema, SQLite reports an error.
- Virtual table transaction writes during `xSync()` are blocked with `SQLITE_LOCKED`.
- `sqlite3VtabUnlockList()` relies on specific mutex ownership. In this FoundationDB build, earlier chunk settings indicate SQLite mutexes may be omitted, so the embedding layer must preserve equivalent serialization.
- LIKE/GLOB optimization depends on bound parameter values at prepare/reprepare time and marks variables with `sqlite3VdbeSetVarmask()` so changes force replanning.
- WHERE term arrays can reallocate in `whereClauseInsert()`, invalidating saved `WhereTerm *` pointers.

## Test Signals

Useful test coverage for this chunk should include:

- SELECT column-name derivation with duplicate aliases, source columns, rowid expressions, expressions without aliases, and collations/types from views/subqueries.
- Compound SELECT variants: `UNION ALL`, `UNION`, `EXCEPT`, `INTERSECT`, with and without `ORDER BY`, `LIMIT`, `OFFSET`, duplicate rows, and collation-sensitive ordering.
- Subquery flattening cases that should flatten and cases blocked by DISTINCT, aggregate, LEFT JOIN right operand, LIMIT/OFFSET, parent WHERE, parent DISTINCT, and compound-subquery restrictions.
- Aggregate paths: GROUP BY with and without sort, DISTINCT aggregate argument count errors, `count(*)` fast path, `min()`/`max()` by index, HAVING filtering, and ORDER BY tail generation.
- `sqlite3_get_table()` with empty results, multiple statements with incompatible column counts, NULL values, allocation failures, and free-table ownership.
- Trigger creation/drop for TEMP vs main schemas, triggers on views vs tables, prohibited virtual/system tables, WHEN clauses, UPDATE OF column filtering, recursive trigger settings, and schema reparse effects.
- UPDATE scenarios covering rowid changes, indexed and non-indexed columns, REPLACE conflicts, one-pass and RowSet plans, BEFORE/AFTER triggers, FK checks/actions, views with INSTEAD OF triggers, count-rows output, and virtual table UPDATE.
- VACUUM with normal file DBs, in-memory temp vacuum DBs, WAL mode page-size preservation, `sqlite_sequence`, triggers/views/virtual tables in schema, active statement rejection, transaction rejection, and schema-cookie changes.
- Virtual table module replacement/destructors, lazy xConnect, xCreate/xDestroy, schema declaration failures, hidden columns, vtab transaction begin/sync/commit/rollback, xFindFunction overloading, and writes attempted during xSync.
- WHERE-analysis unit coverage through query plans for equality, range, IN, IS NULL, LIKE/GLOB prefix optimization, MATCH on virtual tables, OR-to-IN transformation, multi-index OR, collation mismatches, and affinity mismatches.
