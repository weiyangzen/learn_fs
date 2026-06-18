# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 114788-122462

## Work Item

- Chunk id: `subset-b-009027`
- Source range: `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c` lines 114788-122462
- Scope: tail of SQLite `expr.c`, full visible `alter.c`, and the opening/major body of `analyze.c` through `sqlite3AnalysisLoad()`, ending at the start of `attach.c`.

## Purpose

This chunk covers three high-impact SQLite subsystems inside the amalgamated SQLite copy used by WiredTiger tests:

1. Expression bytecode generation and expression reasoning helpers. These routines translate parsed `Expr` trees into VDBE instructions, support indexed-expression substitution, constant factoring, boolean jump generation, aggregate analysis, and temporary register management.
2. ALTER TABLE implementation. This code rewrites `sqlite_schema` SQL text for table rename, column rename, add column, and drop column operations, validates rewritten schema objects, and registers internal SQL helper functions used only by nested ALTER TABLE statements.
3. ANALYZE statistics generation and loading. This code creates and populates `sqlite_stat1` and optionally `sqlite_stat4`, accumulates index samples, emits VDBE programs for ANALYZE, and reloads planner statistics into `Table` and `Index` objects.

The chunk is storage-relevant indirectly: it does not implement WiredTiger storage, but it governs SQL semantics, schema mutation, planner statistics, and generated VDBE programs for the SQLite test dependency embedded under `wiredtiger/test/3rdparty`.

## Important APIs, Types, And Functions

### Expression Code Generation

- `exprCodeInlineFunction(Parse*, ExprList*, int, int)` handles inline SQL functions. It short-circuits `coalesce()`/`ifnull()`, lowers `iif()` to `TK_CASE`, emits `OP_Offset` for `sqlite_offset()` when enabled, and exposes test-only inline functions such as `expr_compare`, `expr_implies_expr`, `implies_nonnull_row`, and `affinity`.
- `sqlite3ExprCanReturnSubtype(Parse*, Expr*)` and `exprNodeCanReturnSubtype()` walk expression trees to conservatively decide whether a function expression might produce a SQLite subtype. This blocks expression-index substitution where subtype loss could change behavior.
- `sqlite3IndexedExprLookup(Parse*, Expr*, int)` tries to satisfy expression evaluation from an expression index rather than recomputing the expression. It checks cursor availability, self-table contexts, expression equality, affinity compatibility, NULL-row handling for outer joins, and subtype-sensitive function calls.
- `exprPartidxExprLookup(Parse*, Expr*, int)` substitutes constants from partial-index expressions for matching column references, including affinity application and `OP_IfNullRow` handling.
- `sqlite3ExprCodeTarget(Parse*, Expr*, int)` is the central expression-to-VDBE compiler. It covers literals, columns, aggregate columns/functions, function calls, comparisons, arithmetic, boolean operators, casts, subqueries, `IN`, `BETWEEN`, `CASE`, triggers, `RAISE()`, vectors, and outer-join null-row wrappers.
- `sqlite3ExprCodeRunJustOnce()`, `sqlite3ExprCodeTemp()`, `sqlite3ExprCode()`, `sqlite3ExprCodeCopy()`, `sqlite3ExprCodeFactorable()`, and `sqlite3ExprCodeExprList()` are layered helpers for constant factoring, temporary-register selection, guaranteed target-register writes, copy-preserving evaluation, and expression-list evaluation.
- `exprCodeBetween()`, `sqlite3ExprIfTrue()`, `sqlite3ExprIfFalse()`, and `sqlite3ExprIfFalseDup()` generate control-flow jumps for boolean expressions and preserve SQL NULL truth semantics.
- `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, and `sqlite3ExprCompareSkip()` implement conservative structural expression comparison used by optimizer rewrites, expression indexes, aggregate duplicate detection, and implication tests.
- `sqlite3ExprImpliesExpr()`, `sqlite3ExprImpliesNonNullRow()`, and helper walkers (`exprImpliesNotNull()`, `impliesNotNullRow()`) prove limited logical relationships used by optimizations such as LEFT JOIN to ordinary JOIN conversion.
- `sqlite3ExprCoveredByIndex()` uses `IdxCover` and a walker to determine whether an expression can be evaluated from an index alone.
- `sqlite3ReferencesSrcList()` checks whether an aggregate function expression references a particular source list, while excluding references from nested subqueries.
- Aggregate helpers include `sqlite3AggInfoPersistWalkerInit()`, `findOrCreateAggInfoColumn()`, `analyzeAggregate()`, `sqlite3ExprAnalyzeAggregates()`, and `sqlite3ExprAnalyzeAggList()`.
- Temporary register helpers include `sqlite3GetTempReg()`, `sqlite3ReleaseTempReg()`, `sqlite3GetTempRange()`, `sqlite3ReleaseTempRange()`, `sqlite3ClearTempRegCache()`, `sqlite3TouchRegister()`, and debug/stat4 helper `sqlite3FirstAvailableRegister()`.

### ALTER TABLE

- `isAlterableTable()` rejects system tables, eponymous virtual tables, and read-only shadow tables.
- `renameTestSchema()`, `renameFixQuotes()`, and `renameReloadSchema()` are reusable ALTER TABLE support routines. They validate parseability, normalize double-quoted strings in schema SQL, change schema cookies, and reparse schemas.
- `sqlite3AlterRenameTable()` implements `ALTER TABLE ... RENAME TO`, including object-name conflict checks, authorization, nested `sqlite_schema` updates, temp-schema trigger/view rewrites, virtual-table `xRename`, schema reload, and post-rename validation.
- `sqlite3AlterBeginAddColumn()` clones the target `Table` into `Parse.pNewTable` under an `sqlite_altertab_` name so the parser can append the new column definition to a temporary table model.
- `sqlite3AlterFinishAddColumn()` validates constraints for `ADD COLUMN`, updates the stored `CREATE TABLE` SQL with the new column text, upgrades the file format to at least 3 when necessary, reloads schema, and runs `pragma_quick_check()` for CHECK, generated NOT NULL, and STRICT-table validation.
- `sqlite3AlterRenameColumn()` implements parser-facing `ALTER TABLE ... RENAME COLUMN`, then delegates SQL text edits to internal `sqlite_rename_column()`.
- `RenameToken` maps parse-tree nodes or column-name storage locations back to token spans in the original SQL. `RenameCtx` collects matching tokens for a specific rename operation.
- Rename-token utilities include `sqlite3RenameTokenMap()`, `sqlite3RenameTokenRemap()`, `sqlite3RenameExprUnmap()`, `sqlite3RenameExprlistUnmap()`, `renameTokenFind()`, `renameColumnTokenNext()`, and `renameTokenFree()`.
- `renameParseSql()` reparses stored DDL in `PARSE_MODE_RENAME` while preserving token mappings and optionally marking temp schema context.
- `renameEditSql()` edits the original SQL by replacing collected token spans with the new identifier, or by converting double-quoted strings to single-quoted strings for quote-fix mode.
- `renameResolveTrigger()` resolves trigger WHEN clauses, trigger SELECTs, UPDATE target expressions, FROM clauses, and UPSERT expressions so column/table token searches can walk semantically resolved trees.
- Internal SQL functions registered by `sqlite3AlterFunctions()` are `sqlite_rename_column`, `sqlite_rename_table`, `sqlite_rename_test`, `sqlite_drop_column`, and `sqlite_rename_quotefix`.
- `dropColumnFunc()` edits a `CREATE TABLE` statement text to remove one column definition.
- `sqlite3AlterDropColumn()` validates `DROP COLUMN`, rewrites schema SQL, reloads and validates schema, then rewrites on-disk table records for non-virtual dropped columns.

### ANALYZE

- `openStatTable()` creates or clears `sqlite_stat1` and, when STAT4 is enabled, `sqlite_stat4`, then opens them for writing.
- `StatSample` stores one STAT4 sample's `nEq`, `nLt`, `nDLt`, rowid/key blob, sample classification, and tie-break hash.
- `StatAccum` is the heap state shared by internal SQL functions `stat_init()`, `stat_push()`, and `stat_get()`. It tracks row counts, distinct counts, skip-ahead state for limited analysis, current sample state, and STAT4 sample arrays.
- `statInit()`, `statPush()`, and `statGet()` implement the internal SQL functions used by generated ANALYZE bytecode.
- STAT4 helpers include `sampleClear()`, `sampleSetRowid()`, `sampleSetRowidInt64()`, `sampleCopy()`, `sampleIsBetterPost()`, `sampleIsBetter()`, `sampleInsert()`, and `samplePushPrevious()`.
- `analyzeOneTable()` emits the VDBE program that scans each index, detects key-prefix changes, calls `stat_push()`, writes `sqlite_stat1`, and optionally writes `sqlite_stat4` samples.
- `analyzeDatabase()`, `analyzeTable()`, and `sqlite3Analyze()` implement the public ANALYZE command forms for all databases, one schema, one table, or one index.
- `decodeIntArray()` parses integer lists and trailing planner flags from `sqlite_stat1`/`sqlite_stat4` text, including `unordered`, `sz=`, `noskipscan`, and optional `costmult=`.
- `analysisLoader()` loads `sqlite_stat1` rows into `Index.aiRowLogEst`, optional `Index.aiRowEst`, table row estimates, and planner flags.
- `sqlite3DeleteIndexSamples()`, `initAvgEq()`, `findIndexOrPrimaryKey()`, `loadStatTbl()`, `loadStat4()`, and `sqlite3AnalysisLoad()` clear and reload planner statistics and STAT4 samples from persistent stat tables.

## Control Flow

Expression evaluation generally enters through `sqlite3ExprCode()` or `sqlite3ExprCodeTarget()`. `sqlite3ExprCode()` guarantees the value lands in the requested register by adding `OP_Copy` or `OP_SCopy` if `sqlite3ExprCodeTarget()` returns a different register. `sqlite3ExprCodeTarget()` starts by checking for indexed-expression replacement via `sqlite3IndexedExprLookup()`, then dispatches on `Expr.op`. Simple constants become direct VDBE loads. Column references flow through self-table/generator handling, partial-index constant substitution, or `sqlite3ExprCodeGetColumn()`. Operators allocate temporary registers, emit opcode-aligned VDBE operations, and release temporaries at the shared exit.

Function calls resolve a `FuncDef`, perform constant factoring when legal, lower inline functions, enforce direct/unsafe function usability, determine collation dependencies, code arguments, optionally allow virtual-table function overloads, and finally call `sqlite3VdbeAddFunctionCall()`. Subqueries route to `sqlite3CodeSubselect()`. `CASE` and `BETWEEN` synthesize temporary expression trees and labels so SQL short-circuiting and NULL handling are preserved.

Boolean jumps use `sqlite3ExprIfTrue()` and `sqlite3ExprIfFalse()` rather than always materializing booleans. These routines recursively short-circuit `AND`/`OR`, invert `NOT`, handle `IS TRUE`/`IS FALSE`, translate comparison tokens to aligned VDBE comparison opcodes, and emit `OP_If`/`OP_IfNot` as the default path.

Aggregate analysis uses a walker. `analyzeAggregate()` turns column references in the aggregate query's source list into `TK_AGG_COLUMN` entries in `AggInfo.aCol[]`, detects duplicate aggregate functions for reuse in `AggInfo.aFunc[]`, handles expression-index references inside aggregate functions, and prunes nested aggregate functions at the appropriate walker depth.

ALTER TABLE commands follow a schema-text rewrite model. Parser-facing functions validate the target object and then use `sqlite3NestedParse()` to run internal UPDATE statements against `sqlite_schema` or `sqlite_temp_schema`. Those nested statements invoke internal SQL functions such as `sqlite_rename_table()` or `sqlite_rename_column()` to reparse each stored DDL statement, find token spans tied to the target table/column, edit the SQL text, and return the new definition. After rewrite, `renameReloadSchema()` invalidates/reloads schemas and `renameTestSchema()` validates that dependent schema objects still parse and resolve.

`DROP COLUMN` has an additional physical-record rewrite path. After schema SQL is edited and validated, `sqlite3AlterDropColumn()` opens the table for write, scans every row, constructs a new record omitting the dropped non-virtual column, preserves rowid or WITHOUT ROWID primary-key fields, and reinserts with `OPFLAG_SAVEPOSITION`.

ANALYZE generation starts at `sqlite3Analyze()`. It reads schema, chooses all databases, one database, one table, or one index, then calls `analyzeDatabase()` or `analyzeTable()`. `openStatTable()` prepares the stat tables. `analyzeOneTable()` scans each index with a generated VDBE loop, compares current index columns against previous column registers to compute the first changed prefix, calls `stat_push()`, and finally extracts stat rows with `stat_get()`. With STAT4 and no analysis limit, it then iterates samples and writes `sqlite_stat4`.

Statistics loading starts with `sqlite3AnalysisLoad()`. It clears prior in-memory statistics, reads `sqlite_stat1` through `sqlite3_exec()` and `analysisLoader()`, applies defaults to indexes without stat1 rows, and then optionally disables lookaside and loads STAT4 data via `loadStat4()`/`loadStatTbl()`.

## State And Persistence Behavior

- Expression code generation mutates `Parse` state heavily: `nMem`, `nTab`, temp-register caches, `pConstExpr`, `pIdxEpr`, `pIdxPartExpr`, `okConstFactor`, aggregate metadata, error state, and generated VDBE instruction streams.
- Constant factoring persists expressions in `Parse.pConstExpr` so repeated constant expressions can be initialized once per prepared statement. Function-containing constants are guarded by `OP_Once`.
- Expression-index lookup deliberately avoids replacement when function subtype propagation could be semantically visible or when outer-join NULL rows require original expression evaluation.
- ALTER TABLE persists schema mutations by updating rows in `sqlite_schema`, `sqlite_temp_schema`, and `sqlite_sequence` where applicable. It also changes schema cookies and reparses schema definitions.
- ALTER TABLE stores transient rename state in `Parse.pRename` as linked `RenameToken` nodes. These must be remapped or unmapped as parse trees are transformed to avoid stale token references.
- `ADD COLUMN` updates only schema SQL for most columns but may run `pragma_quick_check()` to validate existing rows. `DROP COLUMN` can rewrite actual table records.
- ANALYZE persists planner statistics in `sqlite_stat1` and `sqlite_stat4`. `sqlite_stat1` holds text row/cardinality estimates and flags. `sqlite_stat4` holds sampled key blobs plus text-encoded `neq`, `nlt`, and `ndlt` arrays.
- `sqlite3AnalysisLoad()` converts persisted stat tables back into in-memory `Table` and `Index` estimates used by the planner; STAT4 sample buffers are allocated under the database connection and freed by `sqlite3DeleteIndexSamples()`.

## Dependencies And Integration Points

- All three subsystems are tightly integrated with SQLite core types: `Parse`, `Expr`, `ExprList`, `Select`, `SrcList`, `Table`, `Index`, `AggInfo`, `NameContext`, `Walker`, `Vdbe`, `FuncDef`, `sqlite3`, `Schema`, `HashElem`, and `sqlite3_value`.
- Expression code generation depends on VDBE opcodes (`OP_Column`, `OP_Function`, `OP_If`, `OP_IfNullRow`, `OP_Once`, `OP_Param`, `OP_MakeRecord`, etc.), collation lookup, virtual-table function overloading, generated-column support, aggregate/window state, subquery code generation, and optimizer metadata.
- ALTER TABLE depends on nested SQL execution, parser modes, schema tables, name resolution, trigger/view/index parsing, virtual-table callbacks, foreign-key metadata, authorization callbacks, writable-schema behavior, schema cookies, and Btree mutex discipline.
- ANALYZE depends on Btree/table/index cursors, stat-table schemas, VDBE program construction, internal SQL functions, planner flags, preupdate hooks, schema hash tables, optional STAT4 compilation, and lookaside-memory disablement while loading samples.
- The `#ifndef SQLITE_OMIT_*` and `#ifdef SQLITE_ENABLE_*` gates are major integration boundaries. Behavior changes substantially when ALTER TABLE, ANALYZE, STAT4, virtual tables, generated columns, foreign keys, window functions, floating point, trigger support, preupdate hooks, or authorization are omitted/enabled.

## Risks And Edge Cases

- Expression comparison routines are intentionally conservative. Incorrect false equality can cause wrong query results, while false inequality generally only disables optimizations.
- Indexed-expression substitution is risky around generated-column affinity, outer joins, and function subtypes. The code includes explicit guards for these cases because replacing expression evaluation with index reads can otherwise change visible SQL values.
- Boolean and comparison code relies on token values matching VDBE opcode values. The assertions protect debug builds, but changes to opcode/token definitions are high risk.
- Constant factoring must be disabled in contexts where an opcode such as `OP_IfNullRow` can overwrite a supposedly constant target register.
- Rename-token mapping uses pointers into parse tree nodes and original SQL text. The debug-only `renameTokenCheckAll()` exists because stale pointer comparisons are undefined behavior after objects are freed or transformed.
- ALTER TABLE schema rewriting is fragile by design: it reparses stored SQL text, edits token spans, then validates the full schema. `PRAGMA writable_schema=ON` weakens error handling by allowing some malformed schema SQL to pass through unchanged.
- `ADD COLUMN` constraints have compatibility restrictions: cannot add PRIMARY KEY or UNIQUE columns, cannot add NOT NULL without non-NULL default to non-empty tables, cannot add REFERENCES with non-NULL default under foreign keys, cannot add STORED generated columns to non-empty tables.
- `DROP COLUMN` must reject primary-key, unique, last-column, view, virtual-table, and system-table cases. The physical rewrite path must preserve WITHOUT ROWID primary keys and virtual/generated column semantics.
- ANALYZE sample memory layout is manually packed. Miscomputed sizes or alignment would corrupt sample arrays; the code uses `ROUND8`, `EIGHT_BYTE_ALIGNMENT`, and asserts to control this.
- Loading STAT4 sample blobs intentionally allocates 8 extra zero bytes to avoid overread when corrupted records are compared later.
- Limited analysis (`db->nAnalysisLimit`) uses skip-ahead behavior from `stat_push()` and disables STAT4 accumulation by setting `mxSample` to zero.

## Test Signals

- The chunk contains many `testcase()`, `VdbeCoverage()`, `VdbeCoverageIf()`, and `VdbeCoverageNeverTaken()` markers. These are direct SQLite test-suite hooks for boolean branches, comparison opcodes, join NULL-row behavior, aggregate handling, STAT4 register allocation, and ALTER TABLE edge cases.
- Comments cite specific fuzz or regression signals, including OSSFuzz recursion prevention for collate/uplus nodes, a dbsqlfuzz `DROP COLUMN` empty-field case, and SQLite forum/regression references around subtype-preserving expression-index substitution and STAT4 temp-register cache clearing.
- Useful SQL-level tests for this range include expression-index queries with subtype-returning functions, generated columns, outer joins with expression indexes, `CASE`/`BETWEEN`/`IN` NULL semantics, aggregate duplicate detection, ALTER TABLE rename across views/triggers/foreign keys, ADD COLUMN constraint failures on non-empty tables, DROP COLUMN on rowid and WITHOUT ROWID tables, and ANALYZE with and without STAT4.
- Runtime verification signals include schema cookie changes, successful reparsing by `sqlite_rename_test`, `pragma_quick_check()` failures during ADD COLUMN, `sqlite_stat1` row contents, `sqlite_stat4` sample counts, and planner state after `OP_LoadAnalysis`.

## Cross-Chunk Notes

- This range begins in the middle of `expr.c`; some helper definitions used here, such as `codeCompare()`, `exprCodeVector()`, `sqlite3ExprCodeIN()`, `sqlite3ExprCodeGetColumn()`, and AST/type definitions, are defined earlier in the amalgamation.
- This range ends at the start of `attach.c`; ATTACH/DETACH implementation continues in the next chunk and should be researched separately.
- The final per-file report should reconcile this chunk with earlier `expr.c` chunks and later `analyze.c`/`attach.c` chunks to describe the full SQLite amalgamation file coherently.
