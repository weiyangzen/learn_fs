# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 83002-89544

## Scope And Purpose

This chunk covers the tail of SQLite's `where.c` query-planner and WHERE-loop code generator, followed by the beginning of the generated Lemon parser implementation in `parse.c`. In this vendored amalgamation, the first part analyzes WHERE terms, chooses table/index access plans, emits VDBE loops for rowid, index, virtual-table, OR, and full-table scans, and closes/freezes the `WhereInfo` state. The second part defines parser helper structures, parser action tables, parser stack mechanics, destructors, token/rule tracing metadata, and the first grammar reduction actions for transaction, schema, constraint, and SELECT syntax.

The WHERE planner/codegen section is responsible for turning parsed SQL predicates into executable VDBE cursor loops. It recognizes OR-to-IN transformations, BETWEEN/LIKE/MATCH/STAT2 virtual terms, ORDER BY satisfied by indexes, automatic transient covering indexes, virtual-table `xBestIndex` plans, range selectivity estimates, join ordering, LEFT JOIN null-row handling, EXPLAIN QUERY PLAN output, and cleanup of cursors and temporary planner state.

The parser section is generated infrastructure. It does not choose query plans itself, but it is the entry point that builds parse-tree objects and invokes semantic actions such as `sqlite3BeginTransaction()`, `sqlite3StartTable()`, `sqlite3AddColumn()`, `sqlite3CreateIndex()`, `sqlite3SelectNew()`, and `sqlite3Select()`. The chunk ends mid-`yy_reduce()` after the `orderby_opt` empty-rule case begins, so many later grammar reductions are outside this work item.

## Important APIs, Types, And Functions

`exprAnalyzeOrTerm()` breaks an OR expression into subterms, analyzes each subterm, and classifies the OR as either optimizable through a virtual `IN` term or through multi-index OR rowid union. It allocates `WhereOrInfo`, stores a nested `WhereClause`, computes `WhereOrInfo.indexable`, and may insert a virtual `TK_IN` term with `TERM_VIRTUAL|TERM_DYNAMIC`.

`exprAnalyze()` is the main WHERE-term analyzer for one `WhereTerm`. It fills prerequisite bitmasks, `leftCursor`, `u.leftColumn`, and `eOperator`; commutes column comparisons by adding virtual terms; expands BETWEEN into `>=` and `<=`; dispatches OR analysis; creates LIKE/GLOB range terms; creates MATCH terms for virtual tables; and, under `SQLITE_ENABLE_STAT2`, creates a `x>NULL` virtual term for `x IS NOT NULL`.

`referencesOtherTables()` and `isSortingIndex()` determine whether an index scan can satisfy an ORDER BY clause. `isSortingIndex()` matches ORDER BY column/collation/sort-order terms against index columns, allows equality-constrained index prefixes to be skipped, treats rowid uniqueness specially, and sets the reverse-scan flag through `pbRev`.

`bestOrClauseIndex()` estimates and records a `WHERE_MULTI_OR` plan by recursively pricing each OR subterm with `bestIndex()`, summing costs/row counts, adding sort cost if needed, and storing the chosen OR `WhereTerm` in `WhereCost.plan.u.pTerm`.

`termCanDriveIndex()`, `bestAutomaticIndex()`, and `constructAutomaticIndex()` implement automatic transient indexes. The planner only considers equality terms with compatible affinity, estimates whether building the temporary covering index beats a full scan, and later emits VDBE code to open `OP_OpenAutoindex`, fill it with `sqlite3GenerateIndexKey()`, and insert entries with `OP_IdxInsert`.

Virtual-table integration is handled by `allocateIndexInfo()`, `vtabBestIndex()`, and `bestVirtualIndex()`. They build/reuse `sqlite3_index_info`, map `WhereTerm` constraints into `aConstraint[]`, expose ORDER BY columns when all terms are on the virtual table, recompute constraint `usable` flags per join order, call module `xBestIndex`, validate `argvIndex` use, and transfer estimated cost/order consumption into `WhereCost`.

Range and histogram estimation uses `whereRangeRegion()`, `valueFromExpr()`, `whereRangeScanEst()`, `whereEqualScanEst()`, and `whereInScanEst()` when `SQLITE_ENABLE_STAT2` is enabled. These functions derive literal or bound-parameter values, compare them against `Index.aSample[]`, account for collation/encoding, and refine selectivity for range, equality, and `IN (...)` constraints. Without STAT2, range selectivity falls back to quartering the candidate row set per bound.

`bestBtreeIndex()` is the main b-tree access planner. It walks the rowid pseudo-index and real indexes, counts usable equality and IN constraints, finds one range-constrained column, estimates row count and cost, accounts for IN loop multipliers, covering-index status, ORDER BY sort avoidance, table lookup cost, full-scan penalties, additional non-index predicate selectivity, `INDEXED BY`/`NOT INDEXED`, and then applies OR and automatic-index alternatives.

`bestIndex()` chooses between `bestVirtualIndex()` and `bestBtreeIndex()` based on `IsVirtual(pSrc->pTab)`.

`disableTerm()` marks index-satisfied terms as `TERM_CODED` while preserving correctness for LEFT JOIN terms that originated outside the join's ON/USING clause. It also walks parent/child virtual-term relationships so a parent expression is disabled once all children are satisfied.

`codeApplyAffinity()`, `codeEqualityTerm()`, and `codeAllEqualityTerms()` emit VDBE code for equality constraints used by index loops. They handle scalar equality, `IS NULL`, and `IN` loops, allocate registers, apply affinity strings, skip unnecessary affinity conversions, and record IN-loop metadata for `sqlite3WhereEnd()`.

`explainAppendTerm()`, `explainIndexRange()`, and `explainOneScan()` build EXPLAIN QUERY PLAN messages for scan/search choices, including automatic/covering indexes, rowid constraints, virtual-table index numbers/strings, aliases, subqueries, and estimated rows.

`codeOneLoopStart()` emits the actual VDBE loop prefix for one selected `WhereLevel`. It handles virtual tables with `OP_VFilter`/`OP_VNext`, rowid equality with `OP_NotExists`, rowid ranges with seek and end tests, index equality/range scans with `OP_Seek*` and `OP_Idx*` checks, multi-index OR scans with recursive `sqlite3WhereBegin()` calls and `OP_RowSetTest`, and fallback full scans with `OP_Rewind`/`OP_Next` or `OP_Last`/`OP_Prev`. It also emits row predicate tests and LEFT JOIN hit flags.

`sqlite3WhereBegin()` owns the top-level WHERE-loop setup. It allocates `WhereInfo`, `WhereClause`, and `WhereMaskSet`; splits and analyzes WHERE terms; assigns table bitmasks; greedily chooses join order with an "optimal first" pass; enforces `INDEXED BY`; handles one-pass UPDATE/DELETE eligibility; opens table, index, virtual-table, and automatic-index cursors; emits EXPLAIN rows; calls `codeOneLoopStart()` for each loop; and returns the `WhereInfo` consumed by `sqlite3WhereEnd()`.

`sqlite3WhereEnd()` emits loop tails, resolves break/continue labels, unwinds IN loops, synthesizes LEFT JOIN null-row iterations, closes opened cursors, rewrites table `OP_Column`/`OP_Rowid` opcodes into index reads for indexed scans where possible, frees planner state, and restores `pParse->nQueryLoop`.

The parser portion defines small semantic helper types `LimitVal`, `LikeOp`, `TrigEvent`, and `AttachKey`; expression-span helpers `spanSet()`, `spanExpr()`, `spanBinaryExpr()`, `spanUnaryPostfix()`, `binaryToUnaryIfNull()`, and `spanUnaryPrefix()`; generated parser constants (`YYNSTATE`, `YYNRULE`, `YYFALLBACK`, action code ranges, `YYMINORTYPE`); action tables (`yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, `yy_default`); fallback-token mappings; `yyStackEntry` and `yyParser`; tracing metadata `yyTokenName[]` and `yyRuleName[]`; parser allocation/free/stack helpers; `yy_destructor()`; `yy_find_shift_action()`; `yy_find_reduce_action()`; `yy_shift()`; `yyRuleInfo[]`; and the start of `yy_reduce()`.

## Control Flow

WHERE analysis starts after the parser has produced a `SrcList`, `Expr *pWhere`, and optional `ExprList *pOrderBy`. `sqlite3WhereBegin()` initializes bitmask state, folds constants, splits the WHERE expression on top-level AND, assigns one bit per FROM term, records which bits represent virtual tables, then calls `exprAnalyzeAll()` so each term can record prerequisite tables and any indexable operator.

`exprAnalyze()` may mutate the working `WhereClause` by appending virtual terms. Column-to-column comparisons get a commuted copy so either side can be considered as an indexed column. BETWEEN adds two child range terms. OR clauses delegate to `exprAnalyzeOrTerm()`, which recursively analyzes OR subclauses and AND subclauses inside OR branches. LIKE/GLOB adds lower and upper string-prefix range terms. MATCH adds a virtual-table constraint term. These child terms use `iParent`, `nChild`, and flags like `TERM_VIRTUAL`, `TERM_DYNAMIC`, `TERM_COPIED`, `TERM_ORINFO`, and `TERM_ANDINFO` to preserve cleanup and disabling semantics.

Plan selection in `sqlite3WhereBegin()` is a loop over desired nesting levels. For each level it tests remaining FROM terms, honoring LEFT JOIN and CROSS JOIN reorder barriers. The first pass looks for "optimal" scans whose chosen plan does not depend on not-yet-ready tables; if none is found, a second pass picks the lowest-cost usable scan. `bestBtreeIndex()` or `bestVirtualIndex()` computes each candidate's `WhereCost`, and the winner becomes the current `WhereLevel`.

For b-tree tables, `bestBtreeIndex()` considers a fake rowid primary-key index first, then real indexes unless `NOT INDEXED` forbids them or `INDEXED BY` fixes a single index. For each candidate it finds contiguous equality/IN terms, at most one range column, possible ORDER BY satisfaction, covering-index status, row estimates, and CPU/search/sort cost. It records flags such as `WHERE_ROWID_EQ`, `WHERE_ROWID_RANGE`, `WHERE_COLUMN_EQ`, `WHERE_COLUMN_RANGE`, `WHERE_COLUMN_IN`, `WHERE_IDX_ONLY`, `WHERE_ORDERBY`, `WHERE_REVERSE`, `WHERE_UNIQUE`, and `WHERE_TEMP_INDEX`.

For virtual tables, `bestVirtualIndex()` creates or reuses one `sqlite3_index_info` per source item, updates per-join-order `usable` flags, clears previous output, calls `xBestIndex`, validates that unusable constraints were not selected, charges extra cost if ORDER BY is not consumed, and stores `WHERE_VIRTUALTABLE` plus `WHERE_ORDERBY` when applicable.

After join order is fixed, `sqlite3WhereBegin()` opens required cursors. Normal tables use `sqlite3OpenTable()` unless an index-only plan can omit the table cursor. Virtual tables use `OP_VOpen`. Real indexes use `OP_OpenRead` with `KeyInfo`. Temporary automatic indexes are constructed by scanning the table once, generating index keys, and inserting them into an autoindex cursor. Schema cookies are verified before and after cursor opening.

`codeOneLoopStart()` then emits one loop per chosen level. It sets break/continue labels, initializes LEFT JOIN match flags, emits the appropriate seek/scan opcodes, and inserts any row-level tests that were not fully satisfied by index constraints. Multi-index OR is special: it recursively calls `sqlite3WhereBegin()` for each OR branch, optionally de-duplicates rowids through a RowSet register, and uses `OP_Gosub`/`OP_Return` to share the parent loop body.

`sqlite3WhereEnd()` emits loop termination in reverse nesting order. It resolves continue labels, emits the saved loop-step opcode, unwinds nested IN iterators, resolves break labels, and generates LEFT JOIN null-row fallback execution when no right-side row matched. It then closes cursors unless the caller requested omission, rewrites table reads to index reads for indexed plans, and frees `WhereInfo`, virtual-table index info, automatic-index objects, and nested WHERE clauses.

The parser flow begins with `sqlite3ParserAlloc()`, then repeated calls to the parser driver outside this chunk push tokens through `yy_shift()` and reduce through `yy_reduce()`. `yy_find_shift_action()` uses `yy_shift_ofst`, `yy_action`, `yy_lookahead`, fallback tokens, wildcard token support, and `yy_default` to pick actions for terminal lookahead. `yy_find_reduce_action()` performs the equivalent lookup for non-terminals after a reduction. If parsing fails or the parser is freed, `yy_destructor()` releases semantic objects that were not consumed into a larger AST.

The covered `yy_reduce()` cases execute early grammar actions: begin EXPLAIN modes, finish code generation at command boundaries, begin/commit/rollback transactions, process savepoints, start and finish CREATE TABLE, add columns/types/defaults/constraints, create primary-key/unique indexes, create foreign keys, create/drop views and tables, build SELECT objects, and link compound SELECTs. Later expression, trigger, pragma, and virtual-table reductions continue past this chunk boundary.

## State And Persistence Behavior

The WHERE planner's main state is transient compile-time state. `WhereClause` owns analyzed `WhereTerm` objects and any dynamically allocated virtual expressions. `WhereInfo` owns the selected `WhereLevel` array, per-level virtual-table index info, automatic-index descriptors, labels/registers used by generated bytecode, and saved query-loop estimate. It is freed by `whereInfoFree()` after `sqlite3WhereEnd()` or on setup error.

Planner bitmasks are central. `WhereMaskSet` maps table cursors to bits; `prereqAll`, `prereqRight`, `notReady`, `notValid`, `used`, and `vmask` decide join dependencies, usable constraints, LEFT JOIN safety, OR-to-IN eligibility, and when row tests can be emitted. The bit assignment invariant that all tables to the left of a FROM term are `(mask - 1)` is required for LEFT JOIN ON-clause handling.

No user table rows are persisted during planning itself, but code generation emits durable operations when the final VDBE is executed. Automatic indexes are transient per statement. They are not database schema objects and are populated into an `OP_OpenAutoindex` cursor at runtime. The planner-generated VDBE may open read or write table cursors depending on one-pass UPDATE/DELETE, but this chunk only generates bytecode; transaction persistence is managed elsewhere.

`sqlite3WhereEnd()` mutates previously emitted VDBE opcodes between `pWInfo->iTop` and the current address. For indexed scans it can replace table-column reads with index-column reads and rowid reads with `OP_IdxRowid`. This is a compile-time bytecode optimization that relies on stable cursor and index-column metadata.

Virtual-table planning state crosses planner/codegen phases through `sqlite3_index_info`. If `xBestIndex` returns an allocated `idxStr`, ownership is tracked by `needToFreeIdxStr`; code generation passes it to `OP_VFilter` using `P4_MPRINTF` or `P4_STATIC` and clears the free flag after handoff. Mismanaging this ownership would leak or double-free parser/VM memory.

STAT2 estimation reads schema statistics already loaded into `Index.aSample` and bound values available during reprepare through `sqlite3VdbeGetValue()`. It does not persist changes; it influences only cost estimates and selected plans. Parameter values used for estimates are marked with `sqlite3VdbeSetVarmask()` so the statement can be reprepared when bindings change.

Parser state is also compile-time. `yyParser` holds the parser stack, error-recovery counter, optional max-depth counter, and the extra `Parse *pParse` argument. `YYMINORTYPE` is a tagged union only by convention; the generated grammar tables and rule actions decide which union member is live for a symbol. Destructors free `Select`, `ExprSpan`, `ExprList`, `SrcList`, `Expr`, `IdList`, `TriggerStep`, and trigger event lists when stack entries are discarded.

The parser semantic actions in this chunk do create persistent schema or transaction effects indirectly by invoking higher-level SQLite routines. For example, transaction grammar actions call transaction APIs, CREATE TABLE/VIEW/index/foreign-key reductions populate schema parse objects and VDBE work, and SELECT reductions allocate `Select` trees or immediately generate output code for top-level SELECT statements. Actual database persistence still occurs later when the VDBE executes.

## Dependencies And Integration Points

The WHERE code depends on expression analysis helpers (`exprTableUsage`, `exprListTableUsage`, `exprSelectTableUsage`, `sqlite3ExprAffinity`, `sqlite3ExprCollSeq`, `sqlite3BinaryCompareCollSeq`, `sqlite3IndexAffinityOk`, `sqlite3CompareAffinity`, `sqlite3ExprNeedsNoAffinityChange`), expression allocation/deletion (`sqlite3ExprDup`, `sqlite3PExpr`, `sqlite3ExprListAppend`, `sqlite3ExprDelete`), and WHERE helpers defined earlier in `where.c` (`whereClauseInit`, `whereSplit`, `whereClauseInsert`, `whereClauseClear`, `findTerm`, `getMask`, `createMask`, `allowedOp`, `operatorMask`, `transferJoinMarkings`).

It integrates with VDBE bytecode generation through many opcodes: `OP_If`, `OP_Integer`, `OP_OpenAutoindex`, `OP_Rewind`, `OP_IdxInsert`, `OP_VOpen`, `OP_VFilter`, `OP_VNext`, `OP_MustBeInt`, `OP_NotExists`, `OP_SeekGt`, `OP_SeekGe`, `OP_SeekLt`, `OP_SeekLe`, `OP_Last`, `OP_Next`, `OP_Prev`, `OP_Rowid`, `OP_Column`, `OP_IdxRowid`, `OP_Seek`, `OP_IdxGE`, `OP_IdxLT`, `OP_RowSetTest`, `OP_Gosub`, `OP_Return`, `OP_NullRow`, `OP_Close`, `OP_Explain`, and `OP_Affinity`.

It also depends on schema/catalog objects (`Table`, `Index`, `Column`, `CollSeq`, `KeyInfo`), source-list metadata (`SrcList_item` fields like `iCursor`, `pTab`, `pIndex`, `notIndexed`, `jointype`, `colUsed`, aliases, subquery ids), parser connection state (`Parse`, `sqlite3`, `pVdbe`, `nMem`, `nTab`, `nQueryLoop`, `nErr`, `mallocFailed`), and compile-time feature gates (`SQLITE_OMIT_OR_OPTIMIZATION`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_BETWEEN_OPTIMIZATION`, `SQLITE_OMIT_LIKE_OPTIMIZATION`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_ENABLE_STAT2`, `SQLITE_OMIT_EXPLAIN`, `SQLITE_TEST`, `SQLITE_DEBUG`).

Virtual-table integration is through the public module API: `sqlite3_index_info`, `sqlite3_index_constraint`, `sqlite3_index_orderby`, `sqlite3_index_constraint_usage`, `sqlite3_vtab`, `xBestIndex`, `idxNum`, `idxStr`, `estimatedCost`, and `orderByConsumed`. The optimizer assumes `WO_*` operator codes match `SQLITE_INDEX_CONSTRAINT_*` constants and asserts that mapping.

ORDER BY and min/max optimization integrate through `ppOrderBy` and `wctrlFlags` values such as `WHERE_ORDERBY_MIN`, `WHERE_ORDERBY_MAX`, `WHERE_ONETABLE_ONLY`, `WHERE_OMIT_OPEN`, `WHERE_OMIT_CLOSE`, `WHERE_FORCE_TABLE`, `WHERE_DUPLICATES_OK`, and `WHERE_ONEPASS_DESIRED`.

The parser section depends on Lemon-generated conventions and SQLite grammar semantic helpers. It integrates with tokenizer token codes, `Parse` state, `Token`, `ExprSpan`, `Select`, `ExprList`, `SrcList`, `IdList`, trigger-step structures, and many schema/codegen functions used in reduction actions. Debug integration is through `sqlite3ParserTrace()`, `yyTokenName[]`, `yyRuleName[]`, and `yytestcase()`.

## Risks And Edge Cases

OR optimization is correctness-sensitive. OR-to-IN conversion must preserve affinity and table/column identity across all OR arms, especially for `t1.a=t2.b` cases with virtual commuted terms. Multi-index OR must avoid duplicate rows unless `WHERE_DUPLICATES_OK` is set and must propagate `untestedTerms` when a recursive OR branch cannot evaluate predicates involving later join tables.

LEFT JOIN handling appears in several places and is easy to regress. `extraRight` prevents ON-clause terms from driving indexes on left-side tables, `disableTerm()` avoids disabling WHERE-clause terms that should filter null-extended rows, `codeOneLoopStart()` records right-table hits, and `sqlite3WhereEnd()` synthesizes null-row iterations. Small changes to prerequisite masks or `EP_FromJoin` checks can produce wrong results.

Automatic indexes are transient but high impact. They must be covering because table and automatic index cannot be kept in sync after the build phase. `constructAutomaticIndex()` must include all referenced columns, skip duplicate equality columns, allocate contiguous `Index` metadata correctly, and emit fill-loop code exactly once per statement execution.

Cost estimates are heuristic and can mis-plan queries. Full scans get a 4x penalty, range constraints use 1/4 selectivity without STAT2, extra equality/range/non-index predicates reduce `nRow` by fixed factors, and `x IN (SELECT ...)` assumes 25 values. These choices affect performance rather than direct correctness, but plan changes can expose latent bugs in codegen paths.

`bestIndex()` for virtual tables frees the `sqlite3_index_info` immediately in its wrapper path, while `sqlite3WhereBegin()` caches per-source `pIdxInfo` for chosen virtual-table plans. Ownership differs by caller path, so edits need to preserve which `sqlite3_index_info` survives to `codeOneLoopStart()`.

Expression affinity/collation handling is a recurring edge case. LIKE range bounds choose `NOCASE` or `BINARY` collation and increment the final prefix byte. Index range bounds and equality keys suppress affinity when conversion would be incorrect. STAT2 string comparisons may allocate UTF-16 conversions. Bugs here can cause missing or extra rows for mixed-type comparisons.

The VDBE rewrite in `sqlite3WhereEnd()` assumes every table column used by an index-only plan appears in the selected index. The assert catches this in debug builds, but in release builds a bad `WHERE_IDX_ONLY` decision could leave invalid table reads or wrong index-column mappings.

Parser tables are generated and dense. Manual edits to `YYNSTATE`, `YYNRULE`, action arrays, fallback mappings, `YYMINORTYPE`, rule names, or `yyRuleInfo[]` can desynchronize parser action lookup from semantic reductions. The chunk already includes a defensive zero-initialization of `yygotominor` because some reduce paths leave it otherwise uninitialized.

Parser destructors must match grammar symbol ownership. If a semantic action consumes a pointer but the destructor still runs on the same stack symbol, it can double-free. If a symbol is missing from `yy_destructor()`, parse errors or stack pops can leak AST objects.

The chunk boundary cuts off `yy_reduce()` mid-switch. Research for later chunks must reconcile subsequent grammar actions, accept/error handling, parser driver entry point, and public parser free/finalization behavior before making file-level conclusions about parser completeness.

## Test Signals

Planner/codegen tests should cover OR-to-IN rewrites, multi-index OR scans over rowid and composite indexes, OR terms containing AND subterms, duplicate suppression through RowSet, and OR branches involving later join tables.

WHERE-term analysis tests should cover column-to-column commutation, BETWEEN virtual range terms, LIKE/GLOB prefix ranges with `BINARY` and `NOCASE` collations, `MATCH` constraints for virtual tables, `IS NULL` on the right side of LEFT JOINs, and STAT2-only `IS NOT NULL` conversion when enabled.

Index planning tests should exercise rowid equality/range, real index equality/range, composite indexes with skipped equality-prefix ORDER BY terms, descending indexes and reverse scans, covering versus non-covering indexes, `INDEXED BY` success/failure, `NOT INDEXED`, unique index row estimates, and ORDER BY elimination.

Automatic-index tests should use joins with no useful persistent index, equality predicates that can drive an index, affinity-incompatible predicates that must not, tables with columns beyond the bitmask cutoff, and statements that execute multiple times to ensure the autoindex initialization guard works.

Virtual-table tests should use custom modules that inspect `xBestIndex` inputs, reject unusable constraints, consume ORDER BY, return allocated and static `idxStr` values, set high estimated costs, and set invalid `argvIndex` values to confirm planner error handling.

LEFT JOIN tests should distinguish terms in ON clauses from terms in WHERE clauses, include indexes on both sides of the join, include null-producing unmatched right rows, and include OR and virtual terms inside the join condition.

VDBE/codegen tests should inspect `EXPLAIN QUERY PLAN` output for SCAN versus SEARCH, automatic covering indexes, rowid constraints, virtual-table indexes, estimated rows, and hidden one-table OR branch explain rows. Runtime tests should also verify IN-loop nesting and NULL handling for index keys.

Parser tests for this chunk should cover EXPLAIN and EXPLAIN QUERY PLAN, BEGIN/COMMIT/ROLLBACK/SAVEPOINT/RELEASE, CREATE TABLE with column and table constraints, defaults with signed literals and identifiers, foreign-key actions and deferrability, CREATE TABLE AS SELECT, CREATE/DROP VIEW, DROP TABLE, simple and compound SELECT, and the early ORDER BY empty-rule case at the chunk boundary.

Error-path tests should include parser stack overflow with a small `YYSTACKDEPTH`, syntax errors that discard partially built SELECT/Expr/ExprList/SrcList/IdList/TriggerStep objects, malloc failures in planner allocation and parser semantic actions, and virtual-table `xBestIndex` returning `SQLITE_NOMEM` or an error message.
