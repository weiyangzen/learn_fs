# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 158972-165680

## Scope

This chunk covers SQLite's internal WHERE-planner interface (`whereInt.h`), the tail of `wherecode.c`, all of `whereexpr.c` in this slice, and the beginning of `where.c` through the opening of `constructAutomaticIndex()`. It is part of the vendored SQLite amalgamation under WiredTiger test third-party sources, so the code is SQLite query planner and VDBE code-generation logic rather than WiredTiger storage-engine code.

The range begins with planner data structures and bit flags, proceeds through VDBE generation for one WHERE loop, expression decomposition and optimization-term synthesis, WHERE-clause memory/scanner utilities, DISTINCT redundancy detection, cursor/debug helpers, outer-join compatibility checks, and the first half of automatic-index setup. The final line ends mid-call to `sqlite3GenerateIndexKey()` inside `constructAutomaticIndex()`, so automatic-index population and cleanup are completed by the following chunk.

## Purpose

The code turns SQL `WHERE` and join predicates into a planner-internal representation, then emits VDBE bytecode for the selected loop plan. The main responsibilities in this range are:

- Representing candidate loops (`WhereLoop`), chosen nested-loop implementation state (`WhereLevel`), paths through the join graph (`WherePath`), decomposed WHERE terms (`WhereTerm`/`WhereClause`), cursor-to-bitmask mappings (`WhereMaskSet`), OR-cost alternatives (`WhereOrSet`), and planner-wide state (`WhereInfo`).
- Defining planner operator masks (`WO_*`) and selected-loop flags (`WHERE_*`) that drive later planning and code generation.
- Producing `EXPLAIN QUERY PLAN`, Bloom-filter explain text, and `sqlite3_stmt_scanstatus()` ranges for generated scans.
- Emitting VDBE loop prologues for virtual tables, rowid equality/range scans, ordinary index scans, multi-index OR plans, full scans, skip-scan, `IN` loops, Bloom filters, deferred seeks, cursor hints, LIKE/GLOB range rewrites, partial-index implication, and outer joins.
- Analyzing WHERE expressions into planner-usable terms, including commuted comparisons, BETWEEN-derived ranges, OR decomposition, OR-to-IN transformations, `IS NOT NULL` virtual ranges, LIKE/GLOB prefix ranges, row-value/vector slices, vector `IN` slices, virtual-table auxiliary constraints, LIMIT/OFFSET pseudo-constraints, and table-valued-function hidden-column constraints.
- Providing the public file-scope interfaces used by the wider planner: row-count/order/distinct/one-pass query answers, WHERE break/continue labels, term lookup, memory lifetime helpers, and start of automatic-index construction.

## Important APIs And Types

Planner state types introduced or defined in `whereInt.h`:

- `WhereMemBlock` chains scratch allocations owned by a `WhereInfo`; `sqlite3WhereMalloc()` and `sqlite3WhereRealloc()` attach these blocks to `pWInfo->pMemToFree`.
- `WhereRightJoin` carries RIGHT JOIN match tracking: `iMatch` ephemeral index, `regBloom` Bloom filter, `regReturn`, and subroutine address bounds.
- `WhereLevel` is the concrete implementation state for one chosen nested loop: table/index cursors, break/continue/next labels, LIKE and big-null loop state, Bloom-filter register, right/left join state, selected `WhereLoop`, not-ready mask, and `IN`-loop metadata.
- `WhereLoop` describes a candidate access algorithm: prerequisites, table bit, cost estimates, btree or virtual-table access details, `wsFlags`, associated `WhereTerm` pointers, and optional trace metadata.
- `WherePath` is the solver path through chosen `WhereLoop` objects, with accumulated row/cost/order information.
- `WhereTerm` represents one analyzed predicate. Important fields are `pExpr`, `wtFlags`, `eOperator`, `leftCursor`, `u.x.leftColumn`/`iField`, `prereqRight`, and `prereqAll`.
- `WhereClause` owns a flat array of `WhereTerm` objects for an AND or OR split, with static inline space and optional outer-clause links.
- `WhereOrInfo` and `WhereAndInfo` hold nested decomposed subclauses for compound terms.
- `WhereMaskSet` maps sparse VDBE cursor IDs into dense `Bitmask` bits. This is the source of the default 64-table join limit.
- `WhereLoopBuilder` is the construction context for candidate loops, with STAT4 probe state when enabled and `iPlanLimit` throttling pathological index/constraint combinations.
- `WhereInfo` is the planner-wide state returned by `sqlite3WhereBegin()` and consumed by `sqlite3WhereEnd()`: parse context, FROM list, order/result lists, one-pass cursors, loop labels, selected levels, row estimates, order/distinct results, memory chain, main `WhereClause`, and cursor mask set.

Important flags and constants:

- `TERM_*` flags control predicate lifecycle and generated terms: dynamic expression ownership, virtual/derived terms, already-coded terms, parent-child relationships, OR/AND subinfo ownership, LIKE optimization state, correlated subquery tracking, row-value slices, and null-range virtual terms.
- `WO_*` flags encode indexable operators and planner-only categories: `WO_IN`, `WO_EQ`, inequalities, `WO_AUX`, `WO_IS`, `WO_ISNULL`, `WO_OR`, `WO_AND`, `WO_EQUIV`, `WO_NOOP`, and `WO_ROWVAL`.
- `WHERE_*` flags describe selected loop algorithms and constraints: equality/range/IN/null constraints, top/bottom range bounds, covering index use, integer-primary-key access, virtual-table access, multi-index OR, automatic index, skip-scan, partial index, IN early-out/seek-scan, transitive constraints, Bloom filters, coroutine access, and expression-index use.
- `N_OR_COST` is fixed at 3, keeping only the best few OR-subplan cost alternatives.
- `SQLITE_QUERY_PLANNER_LIMIT` and `SQLITE_QUERY_PLANNER_LIMIT_INCR` cap candidate generation to avoid runaway planning.

Key functions in this chunk:

- Explain and instrumentation: `explainIndexColumnName()`, `explainAppendTerm()`, `explainIndexRange()`, `sqlite3WhereAddExplainText()`, `sqlite3WhereExplainOneScan()`, `sqlite3WhereExplainBloomFilter()`, `sqlite3WhereAddScanStatus()`, `whereTraceIndexInfoInputs()`, and `whereTraceIndexInfoOutputs()`.
- Loop-code helpers: `disableTerm()`, `codeApplyAffinity()`, `updateRangeAffinityStr()`, `adjustOrderByCol()`, `removeUnindexableInClauseTerms()`, `codeINTerm()`, `codeEqualityTerm()`, `codeAllEqualityTerms()`, `whereLikeOptimizationStringFixup()`, `codeCursorHint()`, `codeDeferredSeek()`, `codeExprOrVector()`, `whereApplyPartialIndexConstraints()`, `filterPullDown()`, and `whereLoopIsOneRow()`.
- Main loop codegen: `sqlite3WhereCodeOneLoopStart()` and `sqlite3WhereRightJoinLoop()`.
- WHERE expression analysis: `whereOrInfoDelete()`, `whereAndInfoDelete()`, `whereClauseInsert()`, `allowedOp()`, `exprCommute()`, `operatorMask()`, `isLikeOrGlob()`, `isAuxiliaryVtabOperator()`, `transferJoinMarkings()`, `markTermAsChild()`, `whereNthSubterm()`, `whereCombineDisjuncts()`, `exprAnalyzeOrTerm()`, `termIsEquivalence()`, `exprSelectUsage()`, `exprMightBeIndexed()`, and `exprAnalyze()`.
- Public where-expression utilities: `sqlite3WhereSplit()`, `whereAddLimitExpr()`, `sqlite3WhereAddLimit()`, `sqlite3WhereClauseInit()`, `sqlite3WhereClauseClear()`, `sqlite3WhereExprUsageNN()`, `sqlite3WhereExprUsage()`, `sqlite3WhereExprListUsage()`, `sqlite3WhereExprAnalyze()`, and `sqlite3WhereTabFuncArgs()`.
- Beginning of `where.c`: `sqlite3WhereOutputRowCount()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereOrderByLimitOptLabel()`, `sqlite3WhereMinMaxOptEarlyOut()`, `sqlite3WhereContinueLabel()`, `sqlite3WhereBreakLabel()`, `sqlite3WhereOkOnePass()`, `sqlite3WhereUsesDeferredSeek()`, `whereOrMove()`, `whereOrInsert()`, `sqlite3WhereGetMask()`, `sqlite3WhereMalloc()`, `sqlite3WhereRealloc()`, `createMask()`, `whereRightSubexprIsColumn()`, `indexInAffinityOk()`, `whereScanNext()`, `whereScanInit()`, `sqlite3WhereFindTerm()`, `findIndexCol()`, `indexColumnNotNull()`, `isDistinctRedundant()`, `estLog()`, `translateColumnToCopy()`, `constraintCompatibleWithOuterJoin()`, `columnIsGoodIndexCandidate()`, `termCanDriveIndex()`, `explainAutomaticIndex()`, and the opening part of `constructAutomaticIndex()`.

## Control Flow

The data flow starts with `sqlite3WhereSplit()`, which recursively decomposes an expression tree into `WhereClause.a[]` entries by AND or OR separators. `sqlite3WhereExprAnalyze()` then invokes `exprAnalyze()` for each term. Analysis computes dependency bitmasks, recognizes indexable operators, normalizes comparison direction with `exprCommute()`, adds commuted virtual copies for column-to-column comparisons, identifies equivalence terms for transitive use, and attaches operator masks used by later scans.

Expression analysis also synthesizes additional terms. BETWEEN becomes two range comparisons. `x IS NOT NULL` can become a virtual `x>NULL` term. LIKE/GLOB with a constant or currently bound prefix becomes lower/upper range terms and may mark the original function term skippable when the prefix is complete. Row-value equality/IS terms become per-column slice terms and disable the original row-value expression. Vector `IN (SELECT...)` terms become per-field virtual terms when the RHS is a simple select. OR terms are recursively analyzed, record the set of indexable tables, may combine disjuncts, and may be transformed into an equivalent virtual `IN` term when every disjunct compares the same table column/expression to compatible RHS values.

After the planner selects loops, `sqlite3WhereCodeOneLoopStart()` emits bytecode for one `WhereLevel`. It initializes labels, left-join match registers, right-join safe break addresses, and then selects one of several access paths based on `WhereLoop.wsFlags`:

- Coroutine subquery tables initialize and yield from the subquery fill program.
- Virtual tables allocate argument registers, code constraints, handle virtual-table-managed `IN`, emit `OP_VFilter`, install `OP_VNext`, and conditionally recheck `IN` constraints that the virtual table did not accept as handled.
- Rowid equality or rowid `IN` paths code a single equality value, optionally run a Bloom filter and inner filter pull-down, then `OP_SeekRowid`.
- Rowid range paths choose seek operations from the expression operator, code start/end values, handle forward/reverse scans, and install rowid end tests.
- Ordinary index paths code equality and `IN` values, optional skip-scan prefixes, LIKE range fixups, seek-scan, big-null two-pass handling, Bloom filters, start and end index seeks, deferred table seeks, WITHOUT ROWID PK lookups, partial-index constraint elimination, and the terminating `OP_Next`/`OP_Prev`/`OP_Noop`.
- Multi-index OR plans recursively call `sqlite3WhereBegin()` for each OR branch, use a RowSet for rowid tables or an ephemeral PK index for WITHOUT ROWID tables to suppress duplicates, invoke the outer loop body through `OP_Gosub`, and keep a candidate covering index only if every OR branch uses the same index cursor.
- Full scans issue `OP_Rewind`/`OP_Last` and `OP_Next`/`OP_Prev` unless the source is a recursive pseudo-cursor.

After the access path is opened, `sqlite3WhereCodeOneLoopStart()` codes residual WHERE terms in priority passes: terms covered by an index first, then non-correlated terms, then correlated subquery terms. It observes outer-join markings so ON-clause constraints and WHERE-clause constraints are evaluated at the correct phase. It also codes transitive constraints such as using `t1.a=123` when the original terms imply `t1.a=t2.b` and `t2.b=123`.

RIGHT JOIN handling has two phases. During ordinary matched-row processing, the code records the right-table PK/rowid in `WhereRightJoin.iMatch` and `regBloom`. For unmatched rows, `sqlite3WhereRightJoinLoop()` nulls all tables to the left, builds a one-table sub-WHERE for the right table, scans right rows, skips those found by the Bloom filter/match index, and calls the saved right-join subroutine for rows that had no match.

The `where.c` utilities expose planner answers after loop selection. `sqlite3WhereIsOrdered()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereOutputRowCount()`, `sqlite3WhereOkOnePass()`, and label helpers are read-side APIs used by SELECT/UPDATE/DELETE code generation. `whereScanInit()` and `whereScanNext()` implement the core term search primitive used by index matching and DISTINCT redundancy checks; they walk equivalence chains up to the fixed `WhereScan.aiCur[]`/`aiColumn[]` capacity.

The automatic-index setup begins by checking equality/IS terms with `termCanDriveIndex()`, rejecting terms from the wrong cursor, unsafe outer-join terms, not-ready RHS dependencies, non-column/expression columns, and affinity-incompatible terms. `constructAutomaticIndex()` emits `OP_Once`, gathers driving columns, logs `SQLITE_WARNING_AUTOINDEX`, marks the selected `WhereLoop` as `WHERE_AUTO_INDEX | WHERE_INDEXED | WHERE_IDX_ONLY`, adds all extra columns required for a covering index, creates an ephemeral `Index` object and `OP_OpenAutoindex`, optionally creates a Bloom filter, then starts scanning either the source table or coroutine to fill the transient index. The chunk ends at the call that generates index keys for that fill loop.

## State And Persistence Behavior

Most state here is per-prepare, per-statement planner state rather than database persistence. `WhereInfo`, `WhereClause`, `WhereLevel`, `WhereLoop`, and `WhereScan` are transient and live only while compiling a statement. `sqlite3WhereMalloc()` chains allocations to `WhereInfo` so they are freed when the WHERE object is destroyed; this is important because `whereClauseInsert()` may reallocate `WhereTerm` arrays and invalidate raw term pointers.

The code emits VDBE state that persists for the lifetime of the prepared statement execution. Examples include registers for equality values, `IN` loop state, left-join match flags, RIGHT JOIN match indexes and Bloom filters, cursor-hint expressions, scanstatus metadata, RowSets/ephemeral indexes for OR duplicate elimination, and automatic index cursors. These are runtime structures inside the VDBE, not durable database objects.

Automatic indexes are query-time transient btrees. `constructAutomaticIndex()` allocates an `Index` descriptor with name `"auto-index"`, opens it with `OP_OpenAutoindex`, fills it from the source table or subquery coroutine, and forces it to be covering because it is not maintained if the base table changes during statement execution. It may also create a partial automatic index by combining single-table constraints and setting `WHERE_PARTIALIDX`.

Outer-join state is correctness-critical. LEFT JOINs use a memory cell to remember whether the right side matched. RIGHT JOINs use a match index and Bloom filter keyed by right-table PK/rowid. Predicate disabling and cursor hints explicitly avoid pushing unsafe WHERE constraints below outer-join null-extension points.

## Dependencies

This slice depends heavily on SQLite internal planner, parser, expression, table/index, and VDBE APIs:

- Parser and schema objects: `Parse`, `Select`, `SrcList`, `SrcItem`, `Table`, `Index`, `Expr`, `ExprList`, `CollSeq`, `Subquery`, `UnpackedRecord`, and `sqlite3`.
- Expression analysis/codegen: `sqlite3WhereExprUsage*()`, `sqlite3ExprCode*()`, `sqlite3ExprCompare*()`, `sqlite3ExprAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3ExprIsVector()`, `sqlite3ExprForVectorField()`, `sqlite3ExprDup()`, `sqlite3PExpr()`, `sqlite3ExprAnd()`, `sqlite3ExprIfFalse()`, `sqlite3ExprCanBeNull()`, and `sqlite3CodeSubselect()`.
- VDBE construction: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeGetOp()`, `sqlite3VdbeGetLastOp()`, `sqlite3VdbeCurrentAddr()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeSetP4KeyInfo()`, `sqlite3VdbeScanStatus*()`, and many opcodes such as `OP_Explain`, `OP_VFilter`, `OP_SeekRowid`, `OP_SeekGE`, `OP_IdxGE`, `OP_DeferredSeek`, `OP_Filter`, `OP_FilterAdd`, `OP_RowSetTest`, `OP_OpenEphemeral`, and `OP_OpenAutoindex`.
- Planner options and compile-time switches: `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_OR_OPTIMIZATION`, `SQLITE_OMIT_LIKE_OPTIMIZATION`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_STAT4`, `SQLITE_OMIT_AUTOMATIC_INDEX`, and `WHERETRACE_ENABLED`.
- Runtime knobs and heuristics: `SQLITE_CursorHints`, `SQLITE_BloomFilter`, `SQLITE_Transitive`, `SQLITE_EnableQPSG`, `SQLITE_WARNING_AUTOINDEX`, `SQLITE_STMTSTATUS_FULLSCAN_STEP`, and `SQLITE_STMTSTATUS_AUTOINDEX`.
- Virtual table API contracts: `sqlite3_index_info`, `xBestIndex` constraint/operator codes, `sqlite3_vtab_collation()`, `sqlite3_vtab_rhs_value()`, and virtual-table `LIMIT`/`OFFSET` pseudo-constraints.

## Integration Points

This code is the glue between high-level SQL compilation and low-level VDBE execution. SELECT, UPDATE, DELETE, aggregate/min-max, DISTINCT, ORDER BY, LIMIT, virtual table, table-valued function, and outer join code generation all consume the planner state and labels produced here.

Virtual tables integrate in two places. Expression analysis creates `WO_AUX` terms for MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, and `IS NOT NULL` forms that ordinary btree planning does not use but `xBestIndex` may. Loop code then passes selected constraints through `OP_VFilter`, supports virtual-table-managed `IN` terms, rechecks unhandled `IN` values, and can push `LIMIT`/`OFFSET` values with `sqlite3WhereAddLimit()`.

Indexes integrate through `WhereScan`, affinity/collation checks, expression-index matching, skip-scan support, partial-index implication, deferred seek, covering-index detection, DISTINCT redundancy checks, and automatic-index construction. The `findIndexCol()`/`indexColumnNotNull()`/`isDistinctRedundant()` path lets the SELECT layer suppress DISTINCT work when uniqueness and nullability prove it redundant.

Instrumentation surfaces are integrated directly into planner output. `EXPLAIN QUERY PLAN` receives human-readable scan text, Bloom-filter text, and OR-branch labels. `sqlite3_stmt_scanstatus()` receives scan ranges and row estimates, including special handling for coroutine sources and automatic index explain records.

WiredTiger's repository consumes this as vendored SQLite test infrastructure. Behavioral changes in this area would affect any SQLite-backed test utility or imported SQLite conformance behavior, but not WiredTiger's production storage engine directly unless the vendored SQLite is executed by tests.

## Risks And Edge Cases

- The planner relies on many bit flags with overlapping semantics. Incorrect `TERM_CODED`, `TERM_VIRTUAL`, `WO_EQUIV`, `WHERE_IDX_ONLY`, or outer-join markings can silently produce wrong answers rather than crashes.
- Outer joins are especially sensitive. The code deliberately defers WHERE constraints until after null-extension, rejects unsafe automatic-index terms with `constraintCompatibleWithOuterJoin()`, and excludes unsafe cursor hints. Reordering or over-disabling terms can change LEFT/RIGHT/FULL JOIN semantics.
- Transitive constraints are guarded by affinity, collation, and join checks. Returning true from `termIsEquivalence()` too broadly risks substituting values where SQL comparison semantics differ.
- LIKE/GLOB optimization has many text encoding and numeric-affinity pitfalls. The prefix range optimization is disabled for malformed UTF-8, UTF16LE-sensitive cases, numeric-looking prefixes on non-TEXT left sides, and complete-prefix edge cases. The two-pass BLOB/string logic depends on `SQLITE_LIKE_DOESNT_MATCH_BLOBS`.
- Vector and row-value optimization is deliberately limited. Vector `IN` slicing only supports simple non-window SELECT RHS cases, and OR pushdown skips row-value slices and subqueries to avoid uninitialized RHS values or invalid index cursor references inside subroutines.
- `whereClauseInsert()` may reallocate the term array. Callers must refresh `WhereTerm *` pointers after insertion; many comments and local resets exist because stale pointers would corrupt planning.
- `WhereMaskSet` depends on the fixed `Bitmask` width. Joins over the supported table count must be rejected before mask overflow; equivalence scanning also has a fixed 11-entry chain limit.
- Multi-index OR duplicate suppression differs for rowid and WITHOUT ROWID tables. RowSet and ephemeral PK index behavior must stay aligned, especially when `WHERE_DUPLICATES_OK` is set.
- Deferred seeks and covering-index substitutions are disabled or adjusted in write statements and OR/RIGHT JOIN subclauses. Enabling them too broadly could read columns from an index when the table cursor is required.
- Automatic indexes are intentionally covering and transient. If a generated automatic index omitted a needed column or failed to include WITHOUT ROWID primary-key columns, subsequent code could read stale or unavailable data.
- Automatic-index Bloom filters are heuristic and only enabled for non-TEXT-capable key columns. Incorrect hashing assumptions or filter placement could cause performance regressions; false negatives would be correctness bugs.
- The chunk ends before `constructAutomaticIndex()` finishes. Research consumers should combine this document with the following chunk before assessing full automatic-index population, `OP_FilterAdd`, scanstatus counters, cleanup, and error paths.

## Test Signals

Useful validation signals for this code include:

- SQLite planner regression tests covering EXPLAIN QUERY PLAN text for full scans, covering index scans, automatic covering/partial indexes, virtual tables, Bloom filters, rowid scans, skip-scans, multi-index OR, and LEFT/RIGHT JOINs.
- `sqlite3_stmt_scanstatus()` tests for normal table/index scans, coroutine subqueries, automatic indexes, Bloom filters, and OR subplans.
- WHERE expression tests for commuted comparisons, column equivalence/transitive constraints, incompatible affinities/collations, `IS` versus `=`, `IS NULL` on non-null columns, BETWEEN virtual terms, row-value equality, vector `IN`, OR-to-IN conversion, OR duplicate suppression, and expression indexes.
- LIKE/GLOB optimization tests for case-sensitive and case-insensitive patterns, bound parameters and repreparation, escaped wildcards, malformed UTF-8, UTF16LE databases, numeric-looking prefixes, BLOB behavior with and without `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, and complete-prefix skipping.
- Outer join tests ensuring ON-clause and WHERE-clause terms are evaluated at the correct phase for LEFT, RIGHT, and mixed left-to-right joins, including constraints that imply non-null values on the wrong side.
- Virtual-table tests for `xBestIndex` inputs and outputs, auxiliary operators, handled and unhandled `IN` constraints, `LIMIT`/`OFFSET` pseudo-constraints, collation names, and omitted constraints.
- Automatic-index tests for warning logs, covering-column selection, WITHOUT ROWID primary-key inclusion, partial automatic indexes, coroutine-backed subqueries, Bloom-filter creation, affinity/collation checks, and unsafe outer-join term rejection.
- Fuzz and TH3-style tests around pointer invalidation after virtual-term insertion, nested OR/AND decomposition, subqueries in OR branches, cursor-hint safety, deferred seek with OR branches, and DISTINCT redundancy with unique non-null indexes.
