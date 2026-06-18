# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 165681-172668

## Scope

This chunk covers the end of SQLite's `where.c` implementation and the beginning of `window.c` inside the amalgamated SQLite source vendored under WiredTiger tests. The range starts in the tail of automatic-index construction, includes most of the query planner loop enumeration, costing, order-by analysis, `sqlite3WhereBegin()`, and `sqlite3WhereEnd()`, then transitions into the window-function module comments and the first built-in window-function aggregate callbacks through the beginning of `last_valueInvFunc()`.

The code is compiled conditionally by feature macros such as `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_STAT4`, `WHERETRACE_ENABLED`, `SQLITE_OMIT_WINDOWFUNC`, and several debug/test configuration flags. It is not WiredTiger-specific logic; it is the upstream SQLite query planner and bytecode generator used by the embedded SQLite test dependency.

## Purpose

The `where.c` portion builds and executes SQLite's low-level plan for scanning tables in a `SELECT`, `UPDATE`, or `DELETE` statement. It:

- Describes available access paths as `WhereLoop` objects for ordinary b-tree tables, rowid lookups, indexes, automatic indexes, skip-scans, virtual tables, and multi-index OR scans.
- Estimates row counts and costs using `sqlite_stat1` and optional STAT4 samples.
- Chooses a nested-loop order with a bounded dynamic-programming solver.
- Determines whether an access path satisfies `ORDER BY`, `GROUP BY`, or `DISTINCT`.
- Opens table/index/virtual-table cursors and emits VDBE bytecode for loop starts and loop endings.
- Applies optimizations such as Bloom filters, covering-index opcode rewrites, omitted no-op LEFT JOIN tables, one-pass UPDATE/DELETE, reverse unordered scan order, automatic indexes, and indexed-expression substitution.

The `window.c` portion begins the window-function subsystem. The comments document how window queries are rewritten into ordered subqueries and how `select.c` drives `sqlite3WindowCodeStep()`. The executable code in this chunk implements state and callbacks for built-in window functions including `row_number`, `dense_rank`, `nth_value`, `first_value`, `rank`, `percent_rank`, `cume_dist`, `ntile`, and the start of `last_value`.

## Important APIs, Types, and Functions

### Bloom Filters and Automatic Index Tail

- `sqlite3ConstructBloomFilter(WhereInfo *pWInfo, int iLevel, WhereLevel *pLevel, Bitmask notReady)` emits one-time VDBE setup for a Bloom filter register. It creates an `OP_Blob` sized from `Table.nRowLogEst`, scans the table/index cursor, filters rows by single-table constraints, and adds rowid or index-prefix keys using `OP_FilterAdd`.
- The preceding automatic-index tail inserts computed records with `OP_IdxInsert`, optionally populates a Bloom filter from automatic-index keys, handles coroutine subqueries through `translateColumnToCopy()`, and records scan-status counters.

### Virtual Table Planning

- `termFromWhereClause()` maps the flattened `sqlite3_index_constraint.iTermOffset` back to a `WhereTerm`, walking outer `WhereClause` chains.
- `allocateIndexInfo()` allocates `sqlite3_index_info` plus a trailing `HiddenIndexInfo`, constraint arrays, order-by arrays, usage arrays, and cached RHS slots. It marks usable virtual-table constraints, maps SQLite `WO_*` operators to public `SQLITE_INDEX_CONSTRAINT_*` codes, exposes `colUsed`, order-by terms, `eDistinct`, and IN-clause metadata.
- `freeIdxStr()` and `freeIndexInfo()` release `idxStr`, cached RHS `sqlite3_value` objects, and the packed allocation.
- `vtabBestIndex()` invokes `xBestIndex()`, brackets the call with schema-lock accounting, reports module errors, propagates OOM, and handles virtual tables that require all schemas.
- `whereLoopAddVirtualOne()` performs one `xBestIndex()` attempt for a chosen usable-constraint mask, validates returned `argvIndex` values, handles omit masks, IN constraints, LIMIT/OFFSET retry behavior, order consumption, unique-scan flags, and inserts the resulting `WhereLoop`.
- `whereLoopAddVirtual()` calls `xBestIndex()` repeatedly with all constraints, without IN, with selected prerequisite masks, and with all external terms disabled, ensuring at least one globally usable plan exists.
- Public virtual-table helper APIs implemented here are `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_distinct()`.
- `sqlite3VtabUsesAllSchemas()` verifies or starts transactions on every attached schema when a virtual table needs cross-schema visibility.

### STAT4 and Cost Estimation

- `whereKeyStats()` binary-searches STAT4 samples and effective prefixes to estimate rows less than and equal to an `UnpackedRecord`.
- `whereRangeAdjust()` applies likelihood and default range-selectivity heuristics.
- `sqlite3IndexColumnAffinity()` returns index-column affinity for STAT4 probing.
- `whereRangeSkipScanEst()` estimates skip-scan range selectivity by comparing lower/upper extracted values against STAT4 sample columns.
- `whereRangeScanEst()` adjusts `WhereLoop.nOut` for range scans using STAT4 when possible, including descending-index bound swapping, vector bound probing, fallback open/closed range heuristics, and default 1/4 or 1/64 selectivity.
- `whereEqualScanEst()` and `whereInScanEst()` estimate equality and list-IN result sizes from STAT4 histograms.
- `whereLoopOutputAdjust()` reduces output estimates for post-index WHERE terms, using explicit `likelihood()` values, self-culling flags, and heuristics for equality-like predicates.

### WhereLoop Lifecycle and Enumeration

- Debug helpers `sqlite3WhereTermPrint()`, `sqlite3WhereClausePrint()`, `sqlite3WhereLoopPrint()`, and related show functions emit planner diagnostics when tracing is compiled in.
- `whereLoopInit()`, `whereLoopClearUnion()`, `whereLoopClear()`, `whereLoopResize()`, `whereLoopXfer()`, `whereLoopDelete()`, and `whereInfoFree()` manage planner objects and their owned arrays, automatic indexes, virtual-table `idxStr` allocations, and `WhereInfo` memory blocks.
- `whereLoopCheaperProperSubset()` and `whereLoopAdjustCost()` enforce monotonic cost relationships between loops that use subsets/supersets of the same constraints.
- `whereLoopFindLesser()` and `whereLoopInsert()` prune dominated loops, replace inferior loops, track OR-subplan costs in `WhereOrSet`, and enforce the planner search limit.
- `whereRangeVectorLen()` determines how many vector inequality components can be used with the current index prefix.
- `whereLoopAddBtreeIndex()` recursively builds constrained b-tree loops for equality, `IS`, `IS NULL`, IN, range, LIKE-optimized ranges, vector ranges, and skip-scans. It computes run costs, seek multipliers for IN, STAT4 estimates, one-row flags, transitive-constraint flags, and optional seek-scan handling for large IN lists.
- `indexMightHelpWithOrderBy()`, `whereUsablePartialIndex()`, `exprIsCoveredByIndex()`, `whereIsCoveringIndexWalkCallback()`, `whereIsCoveringIndex()`, `wherePartIdxExpr()`, and `whereAddIndexedExpr()` support covering-index detection, partial-index implication, expression-index substitution, and generated-column/expression index handling.
- `whereLoopAddBtree()` adds full scans, covering/non-covering index scans, rowid fake-index scans, automatic-index loops, partial-index loops, and all constrained index loops for one b-tree table.
- `whereLoopAddOr()` recursively builds subplans for OR terms and combines their costs into `WHERE_MULTI_OR` loops.
- `whereLoopAddAll()` iterates FROM terms, applies join-order barriers for CROSS/outer/RIGHT joins, calls b-tree or virtual-table loop builders, and adds OR loops.

### Order, Sorting, and Path Solving

- `wherePathMatchSubqueryOB()` lets an ordered materialized subquery or CTE satisfy an outer `ORDER BY` prefix when result columns and directions line up.
- `wherePathSatisfiesOrderBy()` tests whether a candidate path and appended loop satisfy `ORDER BY`, `GROUP BY`, or `DISTINCT`, including equality-constrained order terms, virtual-table ordering, unique/order-distinct loops, expression-index columns, collation matching, reverse-scan masks, NULLS ordering, and block-sort prefixes.
- `sqlite3WhereIsSorted()` reports whether `WHERE_SORTBYGROUP` planning actually preserves sorted order.
- `whereSortingCost()` estimates full or partial sort cost, accounting for row count, number of output columns, LIMIT, and DISTINCT.
- `computeMxChoice()` chooses solver beam width and applies the star-schema heuristic. For detected fact/dimension star queries it raises full-scan costs of dimension tables so fact-table outer-loop paths are not pruned too early.
- `whereLoopIsNoBetter()` breaks exact ties between indexed loops by preferring smaller index rows.
- `wherePathSolver()` is the bounded dynamic-programming join-order solver. It allocates path buffers on the stack, iteratively extends paths with legal `WhereLoop` candidates, includes setup/run/sort costs, keeps at most `mxChoice` best paths, then installs the selected loops into `WhereInfo.a[]`, sets order/distinct metadata, row estimates, reverse masks, and ordered-inner-loop flags.
- `whereInterstageHeuristic()` runs between the two solver passes and disables full scans for tables already chosen with indexed equality constraints, preventing an ORDER BY-oriented second pass from replacing a selective search with a dangerous full scan.
- `whereShortCut()` handles the simplest one-table primary-key or unique-index equality lookups without running the full planner.

### WHERE Bytecode Generation and Cleanup

- `exprNodeIsDeterministic()` and `exprIsDeterministic()` support the false-WHERE-term bypass by rejecting non-deterministic scalar functions while ignoring subselect contents.
- `whereOmitNoopJoin()` removes unused LEFT JOIN RHS tables when the result, ordering, and ON/USING terms prove they cannot affect output.
- `whereCheckIfBloomFilterIsUseful()` marks equality search loops for Bloom-filter construction when earlier loops imply many lookups into a smaller self-culling table with statistics.
- `whereReverseScanOrder()` implements `reverse_unordered_selects` by setting reverse bits except for materialized CTEs with their own ordering.
- `sqlite3WhereBegin()` is the main planner/codegen entry point. It allocates `WhereInfo`, splits/analyzes WHERE terms, adds LIMIT constraints, handles constant false terms, configures DISTINCT-as-ordering, builds loops, solves paths, opens cursors, handles one-pass UPDATE/DELETE eligibility, builds RIGHT JOIN bookkeeping, emits automatic-index/Bloom-filter setup, emits explain and scan-status metadata, and calls `sqlite3WhereCodeOneLoopStart()` for each selected loop.
- `sqlite3WhereEnd()` emits loop-advance and break/continue code in reverse nesting order, handles RIGHT JOIN subroutines, skip-ahead DISTINCT, IN-loop tails and early-out checks, LIKE repeat counters, LEFT JOIN null-row output, RIGHT JOIN unmatched-row processing, coroutine column rewrites, covering-index opcode rewrites, final break-label resolution, and `WhereInfo` cleanup.
- `OpcodeRewriteTrace` is a debug-only wrapper around `sqlite3WhereOpcodeRewriteTrace()` for tracing post-generation opcode rewrites.

### Window-Function Callbacks

- `row_numberStepFunc()` increments an aggregate `i64`; `row_numberValueFunc()` returns it.
- `struct CallCount` carries `nValue`, `nStep`, and `nTotal` for rank-like functions.
- `dense_rankStepFunc()` marks a peer-group step; `dense_rankValueFunc()` increments rank only once per peer group.
- `struct NthValueCtx`, `nth_valueStepFunc()`, and `nth_valueFinalizeFunc()` implement slow-mode `nth_value()`, validating that the second argument is a positive integer and duplicating the selected `sqlite3_value`.
- `first_valueStepFunc()` and `first_valueFinalizeFunc()` reuse `NthValueCtx` to retain the first duplicated value.
- `rankStepFunc()` and `rankValueFunc()` track total stepped rows and report the first row number in each peer group.
- `percent_rankStepFunc()`, `percent_rankInvFunc()`, and `percent_rankValueFunc()` compute `(rank-1)/(partition_rows-1)` with a zero result for singleton partitions.
- `cume_distStepFunc()`, `cume_distInvFunc()`, and `cume_distValueFunc()` compute rows up to the current peer group divided by total partition rows.
- `struct NtileCtx`, `ntileStepFunc()`, `ntileInvFunc()`, and `ntileValueFunc()` divide a partition into `N` buckets, validating `N > 0` and assigning larger buckets first.
- `struct LastValueCtx` and `last_valueStepFunc()` retain the latest duplicated value. The chunk ends at the beginning of `last_valueInvFunc()`.

## Control Flow

Planner construction starts with `sqlite3WhereBegin()`. It normalizes inputs, builds bitmasks for FROM terms, splits and analyzes WHERE terms, optionally adds LIMIT-derived terms, applies false-term bypasses, and then either uses `whereShortCut()` or builds full loop candidates with `whereLoopAddAll()`. Candidate construction dispatches by table type: b-tree tables use `whereLoopAddBtree()` and recursive `whereLoopAddBtreeIndex()`, virtual tables use `allocateIndexInfo()` plus repeated `whereLoopAddVirtualOne()` calls, and OR terms use nested builders through `whereLoopAddOr()`.

Path selection occurs in one or two `wherePathSolver()` passes. The first pass finds the cheapest path without considering output order. If `ORDER BY` or related ordering constraints exist, `whereInterstageHeuristic()` may disable risky full scans before a second solver pass scores sort-aware paths. `computeMxChoice()` can adjust beam width and costs for star-schema joins before the solver begins.

Once a path is selected, `sqlite3WhereBegin()` performs late optimizations and bytecode generation: omitted joins shrink `WhereInfo.a[]`, Bloom-filter flags are computed, table/index/virtual cursors are opened, automatic indexes and Bloom filters are materialized as needed, and `sqlite3WhereCodeOneLoopStart()` emits the body entry for each loop. The caller emits the SELECT/UPDATE/DELETE body between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`.

`sqlite3WhereEnd()` closes the control-flow shape. It emits next/prev/virtual-next operations, resolves continue and break labels, completes IN-loop subloops, emits null-row passes for unmatched LEFT JOIN rows, invokes RIGHT JOIN unmatched-row generation, and then scans already-generated bytecode to replace table cursor reads with index cursor reads when a covering index or expression index can provide the data.

The window-function code in this chunk uses SQLite's aggregate/window callback control flow. The VDBE calls step/inverse/value/final callbacks according to the rewritten window frame. Each callback uses `sqlite3_aggregate_context()` to retain per-window state and uses `sqlite3_result_*()` APIs to return values or errors.

## State and Persistence Behavior

Most state in the `where.c` portion is per-prepare transient planner state. `WhereInfo`, `WhereLoop`, `WhereLevel`, `WhereClause`, `WhereTerm`, `WhereLoopBuilder`, `WherePath`, and related arrays live only while generating one statement's VDBE program. They are allocated from the parse connection (`sqlite3DbMalloc*()`), stack scratch space (`sqlite3StackAllocRawNN()`), or `WhereInfo` memory blocks, and are released by `whereInfoFree()` or parser cleanup callbacks.

Persistent database state is read but not changed in normal planning: table/index schemas, `Table.nRowLogEst`, `Index.aiRowLogEst`, STAT4 samples, partial-index WHERE expressions, index collations, and table flags drive estimates and plan choices. Some table flags are marked as advisory state during planning, such as `TF_MaybeReanalyze`, to indicate that better statistics could matter.

Generated VDBE bytecode persists for the lifetime of the prepared statement. The planner encodes access-path choices as cursor openings, seek/scan opcodes, automatic-index setup, Bloom-filter blobs held in VM registers, RIGHT JOIN match tracking ephemeral tables and Bloom registers, and opcode rewrites for covering-index access. One-pass UPDATE/DELETE state is recorded in `WhereInfo.eOnePass` and `aiCurOnePass` before being translated into writable cursors.

Virtual-table planning state crosses the module boundary through `sqlite3_index_info`. The virtual table may allocate `idxStr`, request constraint omission, indicate ORDER BY consumption, mark unique scans, request IN handling, and expose estimated cost/rows. This state is copied into `WhereLoop.u.vtab` and must be freed correctly if ownership is transferred.

Window-function state is per aggregate/window instance. It is stored in contexts allocated by `sqlite3_aggregate_context()` and may own duplicated `sqlite3_value` objects for `nth_value`, `first_value`, and `last_value`. Finalizers free duplicated values after returning them. Errors such as OOM or invalid arguments are reported through the SQLite function context rather than persistent global state.

## Dependencies and Integration Points

This code depends heavily on SQLite internal planner, parser, schema, expression, VDBE, and virtual-table APIs. Important dependencies include `Parse`, `sqlite3`, `Vdbe`, `VdbeOp`, `SrcList`, `SrcItem`, `Table`, `Index`, `WhereInfo`, `WhereLoop`, `WhereLevel`, `WhereClause`, `WhereTerm`, `WhereScan`, `WherePath`, `Expr`, `ExprList`, `Select`, `Walker`, `CollSeq`, `UnpackedRecord`, `IndexSample`, and virtual-table structs.

Major internal API integrations include:

- VDBE emission: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeGetOp()`, `sqlite3VdbeSetP4KeyInfo()`, scan-status helpers, and explain helpers.
- Expression and WHERE analysis: `sqlite3WhereExprAnalyze()`, `sqlite3WhereSplit()`, `sqlite3WhereFindTerm()`, `sqlite3ExprIfFalse()`, expression walkers, implication checks, collation/affinity helpers, STAT4 probe helpers, and indexed-expression helpers.
- Schema/table/index services: `sqlite3OpenTable()`, `sqlite3TableLock()`, `sqlite3SchemaToIndex()`, `sqlite3PrimaryKeyIndex()`, `sqlite3TableColumnToIndex()`, `sqlite3StorageColumnToTable()`, and schema-verification/write-operation helpers.
- Virtual-table module ABI: `sqlite3_index_info`, `xBestIndex`, `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_distinct()`.
- Window function ABI: `sqlite3_context`, `sqlite3_value`, `sqlite3_aggregate_context()`, `sqlite3_result_int64()`, `sqlite3_result_double()`, `sqlite3_result_value()`, `sqlite3_result_error()`, `sqlite3_result_error_nomem()`, `sqlite3_value_dup()`, and `sqlite3_value_free()`.

Upstream callers are primarily `select.c`, `update.c`, and `delete.c`, which call `sqlite3WhereBegin()` and `sqlite3WhereEnd()` around generated statement bodies. The window subsystem is integrated with SELECT rewriting (`sqlite3WindowRewrite()`), `select.c` coroutine scans, and later `sqlite3WindowCodeStep()` logic outside this chunk.

## Risks

- Planner cost heuristics are intentionally approximate. Small changes to `LogEst` constants, STAT4 use, skip-scan thresholds, IN seek-scan decisions, sorting costs, or star-query adjustments can cause large query-plan shifts and performance regressions.
- Dominance pruning in `whereLoopInsert()` and path pruning in `wherePathSolver()` are correctness-sensitive. Discarding a path with different prerequisites, ordering, or outer-join constraints can produce wrong results, not just slower plans.
- Outer join and RIGHT/FULL join handling is fragile. `constraintCompatibleWithOuterJoin()`, omitted no-op joins, null-row generation, RIGHT JOIN match tracking, and order-elimination disabling must preserve SQL null-extension semantics.
- Virtual-table `xBestIndex()` validation protects against malformed modules. Relaxing `argvIndex`, omit-mask, LIMIT/OFFSET, or IN-handling checks can admit invalid plans or wrong ORDER BY behavior.
- Covering-index and expression-index opcode rewrites run after other code has emitted table reads. Incorrect column mapping, WITHOUT ROWID handling, partial-index constant substitution, or expression-index certainty can create invalid bytecode. The code explicitly reports an internal planner error if a claimed covering index misses a required table column.
- Automatic-index and Bloom-filter setup create extra VDBE work and memory. Incorrect selectivity checks can waste prepare/runtime time, while incorrect key composition can filter out valid rows.
- STAT4 probes allocate `sqlite3_value` objects and depend on collations and affinities. OOM, missing collation, vector bounds, descending-index bound swaps, or stale statistics can alter plans or trigger prepare errors.
- The false-WHERE-term bypass deliberately preserves legacy behavior for non-deterministic functions. Broadening it to expressions containing `random()`-like functions would change observable behavior.
- Window callbacks that duplicate values must free them exactly once. Invalid `nth_value()` or `ntile()` arguments must remain error paths, and divide-by-zero behavior for singleton partitions must stay guarded.

## Test and Validation Signals

Relevant validation should exercise both correctness and plan stability:

- SQLite query-planner test suites covering indexed equality/range scans, skip-scan, IN-list and IN-subquery plans, LIKE range optimization, automatic indexes, covering indexes, expression indexes, partial indexes, STAT1/STAT4 estimates, and ANALYZE-dependent planning.
- Virtual-table tests for `xBestIndex()` constraint usability, omitted constraints, `sqlite3_vtab_rhs_value()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, LIMIT/OFFSET constraints, `orderByConsumed`, `estimatedRows`, `SQLITE_INDEX_SCAN_UNIQUE`, and malformed `argvIndex` responses.
- Join tests for CROSS JOIN barriers, LEFT/RIGHT/FULL join constraints, no-op LEFT JOIN omission, RIGHT JOIN unmatched rows, OR optimization under joins, and one-pass UPDATE/DELETE eligibility.
- ORDER BY/GROUP BY/DISTINCT tests for index-order satisfaction, reverse scan masks, NULLS FIRST/LAST, collations, partial sorting, subquery ORDER BY reuse, DISTINCT ordered/noop/unique modes, and `reverse_unordered_selects`.
- Regression tests for star-schema planning and planner search-limit behavior, including evidence from `EXPLAIN QUERY PLAN` and runtime comparisons on representative schemas.
- VDBE bytecode validation through `EXPLAIN`, `PRAGMA vdbe_addoptrace`, and debug builds to catch opcode rewrite assertions and covering-index mismatches.
- OOM/fault-injection tests around `sqlite3DbMalloc*()`, STAT4 value extraction, virtual-table `idxStr` ownership, automatic-index generation, Bloom-filter registers, and window value duplication.
- Window-function tests for `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `nth_value`, and `last_value` across partitions, peer groups, frame modes, EXCLUDE modes, invalid arguments, NULL inputs, and OOM paths.
- Build-matrix coverage with and without `SQLITE_ENABLE_STAT4`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_OMIT_WINDOWFUNC`, debug tracing, cursor hints, column-used masks, and offset SQL function support.
