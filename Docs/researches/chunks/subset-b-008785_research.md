# sources/storage-engines/sqlite/src/select.c lines 7154-8967

## Scope

This chunk covers the tail of the count-of-view rewrite, helper logic for SELECT aliases, FROM-subquery coroutine eligibility, EXISTS-to-JOIN rewriting, ON-clause validation, sort-order copying, and most of `sqlite3Select()`. The `sqlite3Select()` span includes name/prep handling, FROM-clause optimizations, compound SELECT dispatch, constant propagation, subquery implementation as coroutines/materialized tables/reused CTEs or views, DISTINCT/ORDER BY setup, non-aggregate row loops, aggregate and GROUP BY bytecode generation, simple `count(*)` and min/max fast paths, final sorting, cleanup, and debug self-checks.

## Purpose

- Rewrite simple `count(*)` over UNION ALL views into a sum of scalar subquery counts when all participating SELECTs are non-aggregate, non-DISTINCT, and unfiltered.
- Reject ambiguous `UPDATE ... FROM` source aliases before query flattening can make them harder to diagnose.
- Decide whether FROM-clause subqueries can be streamed as VDBE coroutines or must be materialized.
- Convert eligible `WHERE EXISTS (SELECT ...)` predicates into joined FROM terms with `fromExists` loop semantics.
- Validate that ON clauses and table-valued function arguments on outer joins do not reference tables to their right.
- Drive the main SELECT code-generation pipeline from resolved syntax tree to VDBE bytecode and query-plan annotations.
- Coordinate planner flags for DISTINCT, ORDER BY, GROUP BY, LIMIT, aggregate DISTINCT, min/max, and output destinations.

## Important APIs, Types, And Functions

- `countOfViewOptimization(Parse*, Select*)` is entered before this chunk and completed here. It detaches a UNION ALL subquery from the FROM item, rewrites each compound arm into `SELECT count(*) ...`, combines them with `TK_PLUS`, and clears the outer `SF_Aggregate` flag.
- `sameSrcAlias(SrcItem*, SrcList*)` recursively checks a FROM list and nested `SF_NestedFrom` subqueries for another source using the same schema table and alias.
- `fromClauseTermCanBeCoroutine(Parse*, SrcList*, int, int)` decides whether a FROM subquery may be implemented using `SRT_Coroutine`. It rejects materialized or multiply used CTEs, right-join left operands, disabled coroutine optimization, self-joined views, UPDATE FROM cases, and join-order positions that cannot safely be outer loops.
- `existsToJoin(Parse*, Select*, Expr*)` recursively walks top-level AND terms in a WHERE clause and rewrites eligible `TK_EXISTS` nodes into joined FROM terms.
- `CheckOnCtx` carries the active `SrcList`, RHS join cursor limit, table-function argument mode, and parent nested SELECT context for ON-clause validation.
- `selectCheckOnClausesExpr()` and `selectCheckOnClausesSelect()` are walker callbacks that detect invalid references to right-side tables in outer-join ON constraints and nested SELECT contexts.
- `sqlite3SelectCheckOnClauses(Parse*, Select*)` is the public validator called after ON constraints have been moved into WHERE with `SF_OnToWhere`.
- `sqlite3CopySortOrder(ExprList*, ExprList*)` copies DESC sort bits between parallel expression lists. It is used for DISTINCT-to-GROUP-BY and GROUP-BY/ORDER-BY equivalence checks.
- `sqlite3Select(Parse*, Select*, SelectDest*)` is the main SELECT bytecode generator. Its output behavior is controlled by `SelectDest` destinations such as `SRT_Output`, `SRT_EphemTab`, `SRT_Coroutine`, queues, EXISTS, discard, and aggregate inner destinations.
- Major state types in this chunk include `Select`, `SrcList`, `SrcItem`, `Subquery`, `CteUse`, `Expr`, `ExprList`, `AggInfo`, `DistinctCtx`, `SortCtx`, `WhereInfo`, `NameContext`, `Vdbe`, `KeyInfo`, `Table`, and `Index`.

## Control Flow

The count-of-view tail first validates every UNION ALL arm, rejecting WHERE, LIMIT, aggregate, and DISTINCT subqueries. It then detaches the compound subquery, deletes the original outer FROM list, creates an empty one-source list, rewrites each arm as an aggregate count SELECT, wraps each arm in a scalar `TK_SELECT` expression, and chains the scalar counts with `TK_PLUS`. Ownership of old expression lists and SELECT nodes is transferred to parser cleanup hooks so early cleanup remains safe.

`fromClauseTermCanBeCoroutine()` is a pure eligibility gate used later by `sqlite3Select()`. It handles CTE materialization policy first, then global join/optimization exclusions, then join-position tests. A leftmost single FROM term or leftmost term followed by CROSS JOIN can stream. A later term can stream only if no earlier term is another subquery and intervening join flags do not force an incompatible outer or CROSS join order.

`existsToJoin()` only runs when parsing saw EXISTS and the optimizer flag is enabled. It ignores ON-clause expression trees, requires available FROM bitmap space, and avoids OFFSET-containing LIMITs. For each eligible EXISTS subquery, it requires one non-subquery FROM item, no aggregate, no LIMIT, and no compound. It allocates a cursor renumbering map so copied EXISTS expressions get unique cursor numbers, turns the original EXISTS expression into integer `1`, appends the subquery source to the outer FROM list, marks the new source `fromExists`, moves the subquery WHERE term into the outer WHERE with AND, and schedules the now-empty subquery for cleanup.

ON-clause checking starts from `sqlite3SelectCheckOnClauses()`. The expression walker treats `EP_OuterON` expressions and `EP_InnerON` expressions inside FROM lists containing RIGHT/FULL joins as roots that must be checked. While an `iJoin` cursor limit is active, `TK_COLUMN` nodes are resolved against the current or parent `CheckOnCtx`; if the referenced cursor is greater than the join RHS cursor, the parser emits either "ON clause references tables to its right" or "table-function argument references tables to its right". Nested SELECTs get their own child context and have `SF_OnToWhere` cleared after validation.

`sqlite3Select()` begins with authorization and optional tree tracing. During tag-select-0100 it drops DISTINCT and ORDER BY when the destination can ignore them, runs `sqlite3SelectPrep()`, checks duplicate UPDATE FROM target aliases with `sameSrcAlias()`, emits column names for `SRT_Output`, rewrites window queries, and snapshots core local pointers.

The first FROM scan performs join and subquery optimizations. OUTER JOIN strength reduction changes LEFT/FULL/RIGHT join flags when WHERE terms imply the nullable side cannot actually be NULL. For subqueries, it checks view column counts, respects materialized CTE optimization fences, skips aggregate subquery flattening, removes harmless subquery ORDER BY clauses when allowed, preserves ORDER BY/LIMIT coroutine behavior for complex outer result sets, and calls `flattenSubquery()`. If the SELECT is compound after this, control returns through `multiSelect()`.

Before generating the main loops, `sqlite3Select()` attempts EXISTS-to-JOIN, WHERE constant propagation, and count-of-view rewriting. It then performs a second FROM scan to authorize unreferenced tables and generate bytecode for FROM subqueries. Subqueries are implemented as one of four paths: coroutine (`OP_InitCoroutine`, recursive `sqlite3Select()` with `SRT_Coroutine`, `OP_EndCoroutine`), already materialized CTE reuse (`OP_Gosub`, `OP_OpenDup`), self-join view reuse (`OP_Gosub` and `OP_OpenDup` from the prior source), or materialization into an ephemeral table via `SRT_EphemTab`, optionally guarded by `OP_Once` for uncorrelated subqueries. The code records CTE materialization addresses and cursor metadata for later reuses.

After FROM analysis, DISTINCT plus ORDER BY can be transformed into GROUP BY if the select list and ORDER BY list match and there are no aggregate/window blockers. The function then opens a provisional ORDER BY ephemeral index or sorter, opens destination ephemeral tables for `SRT_EphemTab`, computes LIMIT/OFFSET registers, and opens a DISTINCT ephemeral index if needed.

For non-aggregate SELECTs without GROUP BY, the function calls `sqlite3WhereBegin()` with ORDER BY and DISTINCT hints, adjusts `nSelectRow`, records whether WHERE satisfied DISTINCT or ORDER BY, no-ops unused sort opens, and emits either the window step path or the standard `selectInnerLoop()` followed by `sqlite3WhereEnd()`.

Aggregate handling first clears aliases between the result list and GROUP BY, estimates output rows, allocates `AggInfo`, and analyzes aggregate columns/functions across the result list, ORDER BY, HAVING, and aggregate arguments. HAVING terms that can be pushed to WHERE are handled by `havingToWhere()`. For a single aggregate without GROUP BY/HAVING, `minMaxQuery()` may synthesize a one-term ORDER BY to let WHERE choose an early-out min/max plan.

GROUP BY aggregate code opens a sorter cursor speculatively, allocates accumulator and comparison registers, and calls `sqlite3WhereBegin()` with GROUP BY, DISTINCT, and sort-by-group flags. If WHERE can deliver rows in group order, the sorter open is converted to a no-op later. Otherwise, it writes group keys and needed aggregate columns into the sorter with `OP_MakeRecord` and `OP_SorterInsert`, then reads sorted records back through `OP_SorterData` and an `OP_OpenPseudo` cursor. The loop compares current group registers against prior group registers with `OP_Compare`/`OP_Jump`, emits the prior group through an output subroutine on group change, resets accumulators, updates accumulators for the current row, and finally emits the last group. Separate subroutines handle output, HAVING filtering, destination emission, abort signaling, and accumulator reset.

Non-GROUP aggregate code has two major paths. `isSimpleCount()` enables a direct `SELECT count(*) FROM table` fast path: it verifies schema and table locks, chooses a smaller usable non-partial ordered index when possible, opens a read cursor, emits `OP_Count` into the aggregate result register, closes the cursor, and annotates the plan. Otherwise, the general aggregate path resets accumulators, optionally prepares a first-row accumulator guard register, passes min/max or aggregate-DISTINCT hints to `sqlite3WhereBegin()`, calls `updateAccumulator()`, patches distinct ephemeral opens with `fixDistinctOpenEph()`, emits min/max early-out if selected, finalizes aggregate functions, evaluates HAVING, and calls `selectInnerLoop()` once for the single aggregate output row.

The tail explains unordered DISTINCT temp tables, emits deferred ORDER BY output with `generateSortTail()`, resolves the query end label, sets the return code from `Parse.nErr`, frees synthesized min/max ORDER BY lists, runs debug `AggInfo` consistency checks, pops explain-plan context, and returns.

## State And Persistence Behavior

This code does not directly persist rows into user tables except through emitted VDBE programs whose destinations may write into temporary or caller-provided destinations. Its direct mutations are mostly parser and bytecode-generation state:

- `Select.selFlags` is rewritten for DISTINCT elimination, aggregate conversion, count-of-view, `SF_UFSrcCheck`, `SF_OnToWhere`, `SF_PushDown`, and DISTINCT-to-GROUP-BY.
- `Select.pSrc`, `Select.pWhere`, `Select.pGroupBy`, `Select.pOrderBy`, `Select.pEList`, `Select.nSelectRow`, `Select.iLimit`, and subquery SELECT fields are mutated as optimizations rewrite the tree.
- `SrcItem.fg.jointype` is changed by OUTER JOIN strength reduction. `SrcItem.fg.fromExists`, `viaCoroutine`, and `isMaterialized` record later WHERE-loop and scan behavior.
- `Subquery.addrFillSub`, `regReturn`, and `regResult` capture coroutine/materialization subprogram entry points and output registers.
- `CteUse.addrM9e`, `regRtn`, `iCur`, and `nRowEst` cache uncorrelated CTE materialization bytecode for reuse.
- `Parse.nTab` allocates VDBE cursor numbers for subqueries, sorters, DISTINCT tables, GROUP BY sorters, simple count cursors, and pseudo tables.
- `Parse.nMem` allocates VDBE registers for coroutine returns, LIMIT registers, group key comparisons, abort/use flags, accumulator state, output subroutine return addresses, and min/max/aggregate guards.
- `AggInfo` records aggregate columns, functions, accumulator registers, sorting cursor metadata, GROUP BY expression linkage, and debug back-pointers. It is registered with parser cleanup via `agginfoFree()`.
- Ephemeral b-trees and sorters are opened in generated bytecode for ORDER BY, DISTINCT, GROUP BY, aggregate DISTINCT, subquery materialization, and `SRT_EphemTab` destinations. These are statement-local runtime structures, not durable database storage.
- Real database access is coordinated through schema verification, table locks, read authorization callbacks, `sqlite3WhereBegin()` scan plans, and `OP_OpenRead` in the simple-count fast path.

## Dependencies And Integration Points

- Name resolution, SELECT expansion, window rewrite, and ON-to-WHERE movement must run before much of this chunk. The public ON-clause checker is called from `resolve.c`.
- Authorization uses `sqlite3AuthCheck()` both for SELECT authorization and for empty-column READ callbacks on unreferenced tables.
- Optimizer feature flags include `SQLITE_Coroutines`, `SQLITE_ExistsToJoin`, `SQLITE_PropagateConst`, `SQLITE_QueryFlattener`, `SQLITE_CountOfView`, `SQLITE_SimplifyJoin`, `SQLITE_OmitOrderBy`, `SQLITE_NullUnusedCols`, `SQLITE_PushDown`, and `SQLITE_GroupByOrder`.
- Query planner integration is through `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereIsSorted()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereOutputRowCount()`, `sqlite3WhereOrderByLimitOptLabel()`, and `sqlite3WhereMinMaxOptEarlyOut()`.
- WHERE and WHERE-code paths consume `SrcItem.fg.fromExists` to lower row estimates and exit the EXISTS-derived loop after the first match.
- Expression infrastructure supplies aggregate analysis, HAVING pushdown, constant propagation, implication checks for non-null join rows, expression code generation, expression-list comparison, sort key metadata, cleanup registration, and tree walking.
- VDBE integration uses opcodes including `OP_InitCoroutine`, `OP_EndCoroutine`, `OP_Gosub`, `OP_Return`, `OP_OpenDup`, `OP_Once`, `OP_OpenEphemeral`, `OP_SorterOpen`, `OP_SorterInsert`, `OP_SorterSort`, `OP_SorterData`, `OP_SorterNext`, `OP_OpenPseudo`, `OP_MakeRecord`, `OP_Compare`, `OP_Jump`, `OP_IfPos`, `OP_Integer`, `OP_Null`, `OP_OpenRead`, `OP_Count`, `OP_Close`, and `OP_Goto`.
- Explain and scan-status integration uses `ExplainQueryPlan`, `ExplainQueryPlan2`, `ExplainQueryPlanPop`, `sqlite3VdbeScanStatusCounters()`, and `sqlite3VdbeScanStatusRange()`.
- Debug/tracing hooks include `TREETRACE`, `sqlite3TreeViewSelect()`, `sqlite3ShowSelect()`, `printAggInfo()`, `testcase()`, `VdbeCoverage()`, and final `AggInfo` assertions.

## Risks And Edge Cases

- The count-of-view rewrite is only correct for UNION ALL, not UNION, DISTINCT, aggregate, filtered, limited, grouped, or HAVING-bearing arms. The explicit DISTINCT exclusion addresses a 2025 forum-post regression note in the source comment.
- Cursor renumbering in EXISTS-to-JOIN is critical because EXISTS expressions may be copied. Reusing a cursor number could bind moved predicates to the wrong table instance.
- `fromExists` changes WHERE-loop semantics to one-match behavior. If the rewrite admits a subquery with duplicate-sensitive semantics, results can change.
- ON-clause validation compares cursor numbers, so it depends on cursor allocation preserving FROM-order assumptions for the relevant source list and nested contexts.
- Materialized CTE policy must respect `AS MATERIALIZED`, multiple references, and `NOT MATERIALIZED`; otherwise optimization fences and reuse semantics break.
- Coroutine eligibility is tightly coupled to join order. Streaming a subquery that cannot be the outer loop can make generated bytecode request rows in an invalid order.
- OUTER JOIN strength reduction must clear or preserve join expression annotations consistently with `unsetJoinExpr()`, especially around RIGHT and FULL joins.
- Subquery ORDER BY removal is deliberately conservative around LIMIT, window rewrites, UPDATE FROM, aggregates other than simple count/min/max, joins, and recursive CTEs. Removing ORDER BY from one of those cases can affect observable behavior.
- The DISTINCT-to-GROUP-BY rewrite relies on copied sort order and structural equality. Collation or DESC mismatches would cause wrong result order or duplicate handling.
- Many `OP_OpenEphemeral`/`OP_SorterOpen` instructions are emitted speculatively and later changed to no-ops. Missed no-op conversion is usually a performance issue, but premature conversion is a correctness bug.
- GROUP BY code has two very different input paths: planner-ordered rows and sorter-ordered rows. Register layout for group keys and aggregate columns must stay aligned across both.
- Aggregate DISTINCT optimization builds composite distinct keys from GROUP BY plus the aggregate argument. Incorrect `pDistinct` construction or `fixDistinctOpenEph()` patching can over-count or under-count per group.
- The simple `count(*)` path must avoid unordered and partial indexes and respect `NOT INDEXED`; otherwise `OP_Count` could scan an incomplete or unsuitable b-tree.
- The min/max path depends on WHERE ordering flags and early-out support. It must still finalize aggregates correctly for empty inputs and FILTER/min/max interactions.
- Cleanup paths assume parser cleanup hooks own allocations such as detached expression lists, rewritten SELECT nodes, and `AggInfo`. Early exits must leave `Parse.nHeight` and `zAuthContext` restored after subquery generation.

## Test Signals

- `sources/storage-engines/sqlite/test/countofview.test` and the count-of-view cases in `pushdown.test` are direct signals for the UNION ALL count rewrite, including CTE and HAVING disqualifiers.
- `join2.test`, `join8.test`, `joinH.test`, and `joinI.test` cover ON-clause right-reference errors for RIGHT/FULL/outer joins.
- `tabfunc01.test` and `carray01.test` cover the table-function argument variant of the same right-reference validation.
- `count.test` and `eqp.test` cover `OP_Count` behavior and explain-query-plan output for simple `SELECT count(*) FROM tbl` plans.
- `select5.test`, `select6.test`, `select7.test`, `distinctagg.test`, `orderby1.test`, `orderby2.test`, `orderby4.test`, and `distinct2.test` exercise GROUP BY, HAVING, DISTINCT, ORDER BY elimination, DISTINCT-to-GROUP-BY, and aggregate DISTINCT paths.
- `joinE.test` and related RIGHT/FULL JOIN tests are key signals for strength reduction and join flag preservation.
- `with*.test` files, especially materialized/NOT MATERIALIZED CTE cases, should exercise CTE materialization reuse and coroutine/materialization choices.
- EQP assertions containing `CO-ROUTINE`, `MATERIALIZE`, `USE TEMP B-TREE FOR GROUP BY`, `USE TEMP B-TREE FOR DISTINCT`, and `USE TEMP B-TREE FOR ORDER BY` are useful for detecting plan-shape regressions in this chunk.
- Optimizer-disabling tests through `SQLITE_TESTCTRL_OPTIMIZER` names such as `groupby-order`, `exists-to-join`, `count-of-view`, `omit-orderby`, and `simplify-join` should preserve both results and expected plan changes when individual optimizations are disabled.
- OOM and fault-injection tests around SELECT preparation, subquery materialization, expression duplication, sorter/key-info allocation, and aggregate analysis should verify that `select_end` cleanup remains balanced and no parser state is left inconsistent.
