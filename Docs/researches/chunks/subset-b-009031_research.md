# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 144609-151744

## Purpose

This chunk spans the end of SQLite statement preparation and the opening, substantial portion of `select.c` in the vendored SQLite amalgamation used by WiredTiger tests. It is the transition from public `sqlite3_prepare*()` entry points into SELECT parsing, expansion, flattening, compound-query planning, result metadata generation, and the first aggregate-codegen helpers.

The code covers:

- Repreparing statements after schema changes and UTF-8/UTF-16 `sqlite3_prepare*()` wrappers.
- Core `Select`, `SortCtx`, `DistinctCtx`, `RowLoadInfo`, `SubstContext`, and `WhereConst` helper state.
- SELECT object construction/destruction, destination initialization, column-name/type derivation, wildcard expansion, CTE resolution, view/subquery expansion, join normalization, and result-set table synthesis.
- VDBE code generation for SELECT inner loops, DISTINCT, ORDER BY/GROUP BY sorters, LIMIT/OFFSET, recursive CTE queues, compound SELECTs, and merge-based compound ORDER BY.
- Optimizations for subquery flattening, WHERE push-down, constant propagation, unused subquery result columns, min/max aggregate short-cuts, simple `count(*)`, sorter references, indexed aggregate expressions, and aggregate ORDER BY/DISTINCT setup.

## Important APIs, Types, and Functions

- `sqlite3Reprepare()` recompiles a saved-SQL VDBE after schema invalidation by calling `sqlite3LockAndPrepare()`, swapping the new VDBE into the old object, transferring bindings, and finalizing the temporary VDBE.
- Public prepare wrappers include `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, and, when UTF-16 support is enabled, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`. The v2/v3 forms set `SQLITE_PREPARE_SAVESQL` so later `sqlite3_step()` can auto-reprepare.
- `sqlite3Prepare16()` converts UTF-16 SQL to UTF-8 under the database mutex, calls `sqlite3LockAndPrepare()`, and maps the returned UTF-8 tail pointer back to the original UTF-16 buffer by counting parsed characters.
- `DistinctCtx` carries DISTINCT strategy state: whether DISTINCT is active, the `WHERE_DISTINCT_*` strategy, the ephemeral cursor, and the delayed `OP_OpenEphemeral` address.
- `SortCtx` carries ORDER BY/GROUP BY sorter state: order list, satisfied prefix count, sorter cursor, block-output labels, sorter flags, deferred row-load data, optional sorter-reference cursors, and optional scan-status push ranges.
- `clearSelect()`, `sqlite3SelectNew()`, `sqlite3SelectDelete()`, and `sqlite3SelectDeleteGeneric()` allocate and tear down `Select` trees, including expression lists, source lists, WHERE/GROUP/HAVING/ORDER/LIMIT expressions, WITH clauses, window definitions, and compound `pPrior` chains.
- `sqlite3SelectDestInit()` initializes `SelectDest` output routing for result rows, transient tables, scalar subqueries, recursive queues, coroutines, and compound temporaries.
- `sqlite3JoinType()` parses permissive SQLite join keyword combinations into `JT_*` bitmasks, including RIGHT/FULL join support and compatibility with historical nonsensical join phrases.
- `sqlite3ColumnIndex()`, `sqlite3SrcItemColumnUsed()`, and `tableAndColumnIndex()` resolve column names in `Table`/`SrcList` objects and mark nested-FROM output columns as used.
- `sqlite3SetJoinExpr()` and `unsetJoinExpr()` annotate or remove `EP_OuterON`/`EP_InnerON` and `Expr.w.iJoin` metadata so WHERE processing knows which ON/USING expressions must be delayed for outer joins.
- `sqlite3ProcessJoin()` rewrites NATURAL joins into USING lists, validates USING columns, builds equality predicates, handles RIGHT/FULL join coalesce behavior for repeated USING names, and appends ON expressions to the SELECT WHERE clause with join-origin tags.
- `innerLoopLoadRow()`, `makeSorterRecord()`, `pushOntoSorter()`, `codeOffset()`, `codeDistinct()`, `fixDistinctOpenEph()`, and optional `selectExprDefer()` build the VDBE instructions for SELECT row materialization, ORDER BY insertion, LIMIT optimization, DISTINCT filtering, and sorter-reference payload deferral.
- `selectInnerLoop()` is the central SELECT row-output code generator. It routes each row to destinations such as `SRT_Output`, `SRT_Coroutine`, `SRT_Table`, `SRT_EphemTab`, `SRT_Set`, `SRT_Union`, `SRT_Except`, `SRT_Queue`, `SRT_DistQueue`, `SRT_Fifo`, `SRT_DistFifo`, `SRT_Mem`, `SRT_Exists`, and `SRT_Upfrom`.
- `sqlite3KeyInfoAlloc()`, `sqlite3KeyInfoRef()`, `sqlite3KeyInfoUnref()`, and `sqlite3KeyInfoFromExprList()` allocate/refcount collation and sort-order metadata for ephemeral btrees and sorters.
- `generateSortTail()` drains a sorter after scan completion, reconstructs result columns, applies OFFSET, supports sorter-reference row reloads, and emits rows to the final `SelectDest`.
- `columnTypeImpl()`, `generateColumnTypes()`, `sqlite3GenerateColumnNames()`, `sqlite3ColumnsFromExprList()`, `sqlite3SubqueryColumnTypes()`, and `sqlite3ResultSetOfSelect()` derive user-visible result-column names, declared types, origin metadata, collations, affinities, and transient `Table` structures for views/subqueries.
- `computeLimitRegisters()` emits VDBE code for LIMIT/OFFSET counters and updates row estimates when LIMIT is a non-negative integer constant.
- `generateWithRecursiveQuery()` implements recursive CTE execution using a current pseudo-table, a queue table, an optional distinct table, optional ORDER BY priority ordering, and LIMIT/OFFSET accounting.
- `multiSelectValues()`, `multiSelect()`, `sqlite3SelectWrongNumTermsError()`, `generateOutputSubroutine()`, and `multiSelectOrderBy()` implement VALUES compounds, UNION/UNION ALL/EXCEPT/INTERSECT without ORDER BY, wrong-column-count diagnostics, coroutine merge output, and ORDER BY merge logic.
- `SubstContext`, `substExpr()`, `substExprList()`, and `substSelect()` replace references to a flattened subquery cursor with duplicated result expressions, preserving collation and outer-join null-row behavior.
- `recomputeColumnsUsed()`, `renumberCursors()`, `findLeftmostExprlist()`, `compoundHasDifferentAffinities()`, and `flattenSubquery()` support subquery flattening, cursor remapping, compound UNION ALL flattening, and post-flattening column-use recalculation.
- `WhereConst`, `findConstInWhere()`, `propagateConstantExprRewrite()`, and `propagateConstants()` implement constant propagation by tagging matching column expressions with `EP_FixedCol` and attaching the constant expression rather than naively replacing affinity-sensitive comparisons.
- `pushDownWhereTerms()` duplicates safe outer WHERE predicates into subqueries, with restrictions for LIMIT, recursive CTEs, LEFT/RIGHT/FULL joins, window partitions, VALUES clauses, and non-BINARY compound operators.
- `disableUnusedSubqueryResultColumns()`, `minMaxQuery()`, `isSimpleCount()`, `sqlite3IndexedByLookup()`, `convertCompoundSelectToSubquery()`, `cannotBeFunction()`, `searchWith()`, `sqlite3WithPush()`, `resolveFromTermToCte()`, `sqlite3SelectPopWith()`, and `sqlite3ExpandSubquery()` handle smaller but important SELECT preparation and optimization tasks.
- `selectExpander()`, `sqlite3SelectExpand()`, `selectAddSubqueryTypeInfo()`, `sqlite3SelectAddTypeInfo()`, and `sqlite3SelectPrep()` are the high-level expansion pipeline before name resolution and type-info finalization.
- Aggregate helpers at the end of the chunk include `analyzeAggFuncArgs()`, `optimizeAggregateUseOfIndexedExpr()`, `aggregateConvertIndexedExprRefToColumn()`, `assignAggregateRegisters()`, `resetAccumulator()`, `finalizeAggFunctions()`, and the start of `updateAccumulator()`.

## Control Flow

Statement preparation at the top of the chunk is wrapper-oriented. `sqlite3_prepare*()` validates pointers through `sqlite3LockAndPrepare()`, which holds the database mutex and all btree mutexes while retrying `sqlite3Prepare()` for `SQLITE_ERROR_RETRY` and one schema reset for `SQLITE_SCHEMA`. `sqlite3Reprepare()` assumes the database mutex is already held, obtains saved SQL from the VDBE, recompiles with the original prepare flags and old VDBE context, swaps bytecode/data structures, transfers bindings, resets the temporary VDBE step result, and finalizes the temporary VDBE.

SELECT processing starts with AST construction and expansion:

- Parser actions allocate `Select` objects with `sqlite3SelectNew()`, defaulting an absent result list to `*` and an absent source list to an empty `SrcList`.
- `sqlite3SelectPrep()` calls `sqlite3SelectExpand()`, then name resolution, then `sqlite3SelectAddTypeInfo()`.
- `sqlite3SelectExpand()` first rewrites compound SELECTs with problematic `ORDER BY ... COLLATE` into a wrapper subquery when needed, then walks every SELECT with `selectExpander()`.
- `selectExpander()` pushes WITH context, assigns source cursors, resolves each FROM item as a subquery, CTE, table, view, or virtual table, resolves `INDEXED BY`, processes joins, expands `*` and `table.*`, enforces the result-column limit, and records complex-result flags.
- `sqlite3SelectAddTypeInfo()` walks resolved FROM-clause subqueries and fills their transient table columns with declaration type, affinity, and collation data.

Join processing is intentionally lowered early. NATURAL joins synthesize USING lists by intersecting visible column names on the left and right. USING terms become equality expressions between left and right columns. For RIGHT/FULL joins, repeated left-side USING names can become a `coalesce()` expression and ambiguous non-USING references produce errors. ON terms are moved into `p->pWhere` and tagged so later WHERE planning preserves outer-join semantics.

Row generation flows through `selectInnerLoop()`. It allocates result registers, optionally reserves ORDER BY prefix registers, loads expression output unless a LIMIT/sorter optimization defers it, applies DISTINCT filtering through `codeDistinct()`, then emits destination-specific VDBE instructions. Without a sorter it writes directly to result rows, scalar registers, ephemeral tables, queues, sets, or compound temp indexes. With a sorter it calls `pushOntoSorter()` so `generateSortTail()` can later output sorted rows.

Sorter control has several branches:

- `pushOntoSorter()` computes ORDER BY keys, optional sequence numbers, payload columns, and records. It supports a partial ORDER BY prefix already satisfied by an index (`nOBSat`), block-sort reset logic, and LIMIT/OFFSET top-N pruning that avoids storing rows larger than the current largest retained entry.
- `makeSorterRecord()` forces deferred row loading just before packing a sorter record.
- `generateSortTail()` emits `OP_Sort` or `OP_SorterSort`, reloads deferred table rows if `SQLITE_ENABLE_SORTER_REFERENCES` is active, reconstructs output columns either from ORDER BY keys, sorter payload columns, or table lookups, and writes to the requested destination.

Compound SELECTs have two major paths. Without ORDER BY, `multiSelect()` creates ephemeral tables for UNION/EXCEPT/INTERSECT as needed, streams UNION ALL arms directly when possible, and converts the final temp table back through `selectInnerLoop()`. Recursive CTEs are special-cased by `generateWithRecursiveQuery()`, which alternates between queue extraction, output of the current row, and recursive-step insertion back into the queue. With ORDER BY, `multiSelectOrderBy()` compiles the left and right sides as coroutines and emits a merge routine driven by `OP_Compare`, `OP_Permutation`, `OP_Yield`, and output subroutines; duplicate removal for UNION/EXCEPT/INTERSECT is handled by comparing against a previous-output register vector.

Subquery flattening and predicate movement run as SELECT-shape rewrites. `flattenSubquery()` enforces a long list of semantic restrictions, detaches the subquery, optionally duplicates parent SELECT arms for compound UNION ALL subqueries, moves subquery FROM terms into the parent FROM list, transfers WHERE/ORDER/LIMIT pieces where legal, substitutes result expressions for references to the old subquery cursor, recomputes `colUsed`, and schedules stale table structures for cleanup. `pushDownWhereTerms()` duplicates eligible predicates into subquery WHERE/HAVING clauses. `propagateConstants()` iteratively tags column references that are known equal to constants, stopping when no new changes occur.

The aggregate code at the chunk end prepares state rather than completing the full aggregate update loop. It analyzes aggregate arguments, adjusts `AggInfo` when indexed expressions can cover GROUP BY aggregate inputs, converts indexed expression references into aggregate-column opcodes, reserves accumulator registers, opens ephemeral distinct/order-by aggregate btrees in `resetAccumulator()`, and emits finalization code in `finalizeAggFunctions()`. The actual `updateAccumulator()` implementation begins at the boundary and continues in the next chunk.

## State and Persistence Behavior

Most persistent state in this chunk is compile-time/query-plan state rather than database page data. Key mutable structures include:

- `Select`: result expressions, FROM list, WHERE/GROUP/HAVING/ORDER/LIMIT, compound links, WITH/window lists, flags such as `SF_Expanded`, `SF_Resolved`, `SF_HasTypeInfo`, `SF_Compound`, `SF_Recursive`, `SF_Distinct`, `SF_Aggregate`, `SF_PushDown`, `SF_UsesEphemeral`, and row-estimate/register fields.
- `SrcItem`: resolved `Table` pointers, cursor numbers, join flags, ON/USING data, CTE/materialization state, subquery references, aliases, `colUsed` masks, INDEXED BY state, and recursive-CTE markers.
- `Expr` and `ExprList` metadata: join-origin flags, collations, `iOrderByCol`, `bSorterRef`, `bUsed`, `bNoExpand`, output names, aggregate mappings, and fixed-column constant substitutions.
- `Table`/`Column` objects synthesized for views, subqueries, and CTEs. These are transient schema objects with `TF_Ephemeral`, rowid visibility flags, generated column names, affinity/type/collation metadata, and parser-cleanup ownership.
- `KeyInfo` objects attached to ephemeral btree/sorter open opcodes. They are refcounted and contain collation pointers, sort flags, key-field counts, and payload-field counts.
- `Parse` state: VDBE pointer, current WITH stack, cursor/register counters, SELECT id counter, error/OOM flags, authorization context, cleanup callbacks, and optimization flags.
- `AggInfo`: aggregate column/function arrays, accumulator counts, sorting column count, first register, aggregate function definitions, distinct/order-by cursors, and subtype/order payload flags.

VDBE bytecode emitted here affects runtime persistence through transient btrees and sorters. DISTINCT, UNION, EXCEPT, INTERSECT, recursive CTE queues, recursive duplicate filters, aggregate DISTINCT, aggregate ORDER BY, and ORDER BY/GROUP BY all allocate ephemeral cursors. These objects live for statement execution and are closed by the VDBE or replaced with no-ops when an optimization proves them unnecessary. Persistent database state is not modified by this code directly except through generated SELECT destinations such as `SRT_Table`, `SRT_EphemTab`, and `SRT_Upfrom`, which emit `OP_Insert`/`OP_IdxInsert` into statement-local or caller-provided cursors.

The CTE path maintains shared `CteUse` state across references, including materialization preference, use count, and recursive error strings. Recursive references temporarily attach the CTE table to self-referential source items, assign a dedicated cursor for the recursive table, and manipulate `pParse->pWith` while walking recursive terms to detect circular or illegal recursive references.

## Dependencies and Integration Points

This chunk depends on broad SQLite internals:

- Parser and AST helpers: `sqlite3Expr*`, `sqlite3ExprList*`, `sqlite3SrcList*`, `sqlite3SelectDup()`, `sqlite3SubqueryDetach()`, `sqlite3SrcItemAttachSubquery()`, `sqlite3WalkSelect()`, `sqlite3ResolveSelectNames()`, `sqlite3ResolveOrderGroupBy()`, and token/name helpers.
- VDBE codegen APIs: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeGoto()`, `sqlite3VdbeScanStatusRange()`, `sqlite3VdbeScanStatusCounters()`, and opcode constants such as `OP_OpenEphemeral`, `OP_SorterOpen`, `OP_MakeRecord`, `OP_IdxInsert`, `OP_ResultRow`, `OP_Yield`, `OP_AggStep`, and `OP_AggFinal`.
- Schema/catalog helpers: `sqlite3LocateTableItem()`, `sqlite3ViewGetColumnNames()`, `sqlite3IndexedByLookup()`, `sqlite3SchemaToIndex()`, `sqlite3PrimaryKeyIndex()`, `sqlite3ColumnType()`, `sqlite3ColumnSetColl()`, `sqlite3ColumnPropertiesFromName()`, and table/view/virtual-table predicates.
- Name/collation/affinity logic: `sqlite3ExprCollSeq()`, `sqlite3ExprNNCollSeq()`, `sqlite3ExprAffinity()`, `sqlite3AffinityType()`, `sqlite3ExprDataType()`, `sqlite3ExprCompareCollSeq()`, `sqlite3IsBinary()`, and standard type tables.
- Planner-facing interfaces: join flags (`JT_*`), `WHERE_DISTINCT_*`, `WHERE_ORDERBY_*`, optimization toggles (`SQLITE_QueryFlattener`, `SQLITE_FlttnUnionAll`, `SQLITE_BalancedMerge`, `SQLITE_MinMaxOpt`, `SQLITE_FactorOutConst`), `ExplainQueryPlan` macros, and scan-status hooks.
- Optional compilation blocks: `SQLITE_OMIT_UTF16`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_CTE`, `SQLITE_OMIT_COMPOUND_SELECT`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ALLOW_ROWID_IN_VIEW`, `SQLITE_OMIT_DECLTYPE`, `SQLITE_OMIT_VIRTUALTABLE`, and debug/tree-trace flags.

For WiredTiger, this remains third-party SQLite test code rather than WiredTiger storage-engine logic. The integration point is build/test compatibility: modifications to this amalgamated file can alter vendored SQLite behavior visible to any tests or helper binaries compiled against this source.

## Risks and Edge Cases

- Public prepare APIs rely on exact mutex and btree-enter ordering. `sqlite3Prepare16()` enters `db->mutex` and then calls `sqlite3LockAndPrepare()`, which also enters the same mutex; this assumes SQLite's configured mutex behavior supports the internal pattern.
- UTF-16 tail mapping depends on correctly counting UTF-8 characters and UTF-16 bytes. Odd `nBytes`, missing terminators for negative `nBytes`, or malformed input are sensitive edge cases.
- Join tags are semantic, not cosmetic. Dropping `EP_OuterON`, `EP_InnerON`, `EP_CanBeNull`, or `w.iJoin` at the wrong time can turn LEFT/RIGHT/FULL joins into inner joins or filter null-extended rows too early.
- USING processing with RIGHT/FULL joins is delicate. The coalesce path is needed when multiple left-side USING columns may contribute, while ambiguous non-USING duplicates must remain errors.
- `selectInnerLoop()` has many destination-specific assumptions. Register layout, `nResultCol`, `nPrefixReg`, `regOrig`, and deferred row loading must remain consistent or sorter records will be decoded incorrectly.
- DISTINCT optimization rewrites delayed `OP_OpenEphemeral` opcodes into no-ops or `OP_Null`. This requires `codeDistinct()` and `fixDistinctOpenEph()` to agree on strategy and register initialization, especially for all-NULL first rows.
- Sorter LIMIT optimization changes memory and CPU behavior by keeping only the best LIMIT+OFFSET rows. Incorrect comparisons against partial ORDER BY prefixes or stale `labelOBLopt` labels can silently lose rows.
- Column-name behavior is compatibility-sensitive. Comments explicitly warn that legacy applications depend on undocumented naming details. `short_column_names`, `full_column_names`, AS-name precedence, duplicate suffixing, and `COLFLAG_NOEXPAND` need careful preservation.
- Flattening restrictions are correctness guards. Relaxing LIMIT, DISTINCT, aggregate, compound, window, recursive CTE, MATERIALIZED CTE, LEFT/RIGHT/FULL join, or affinity restrictions can produce wrong answers rather than just worse plans.
- Constant propagation intentionally avoids direct expression replacement for affinity/collation-sensitive comparisons. The `EP_FixedCol` representation is required to preserve cases such as numeric equality versus text `LIKE`.
- WHERE push-down across window functions is safe only for predicates that filter whole partitions. Pushing row-level predicates into a window subquery changes window results.
- CTE resolution mutates parser WITH-stack state and CTE error strings while walking. Missed restoration of `pParse->pWith` or `pCte->zCteErr` can produce bogus circular-reference errors or allow illegal recursion.
- Aggregate ORDER BY and DISTINCT use ephemeral btrees with `KeyInfo` built from expression lists. Wrong payload counts, sequence-column handling, or subtype preservation will change ordered aggregate results.
- The chunk ends immediately after `updateAccumulator()` initializes `directMode`; the logic that evaluates aggregate filters, DISTINCT checks, ORDER BY aggregate payload insertion, `OP_AggStep`, min/max hit tracking, and accumulator column loading is in the following chunk.

## Test Signals

Useful test signals in this range include:

- `assert()` checks for mutex ownership, parser state, SELECT flags, cursor mappings, result-column counts, KeyInfo writeability, aggregate register allocation, recursive CTE structure, and impossible walker callbacks.
- `testcase()` markers around join keyword combinations, compound operators, DISTINCT strategies, destination variants, LEFT/RIGHT/FULL join branches, OOM/name-collision paths, aggregate DISTINCT/window flags, and optimization-specific cases.
- `VdbeCoverage()` annotations on generated branches such as OFFSET, DISTINCT comparisons, LIMIT exits, sorter pruning, recursive queue iteration, compound merge yields, and temp-table membership tests.
- `ExplainQueryPlan()` output for temporary btrees, recursive CTE setup/step, compound query arms, merge plans, aggregate DISTINCT/ORDER BY temp storage, Bloom filter creation, and sorter usage.
- Debug-only tree tracing via `TREETRACE()` and `printAggInfo()` for SELECT expansion, flattening, compound processing, column-name generation, aggregate indexed-expression adjustment, and wildcard expansion.
- API armor and misuse checks in prepare wrappers: null `ppStmt`, invalid database handles, null SQL text, OOM during UTF-16 conversion, and prepare-flag masking.
- Error-message paths worth covering: unknown join type, NATURAL join with ON/USING, missing USING columns, ambiguous USING references, no such table for `table.*`, too many result columns, compound SELECT result-count mismatch, no such INDEXED BY index, unsafe view/virtual-table usage in untrusted schema, circular/multiple recursive CTE references, bad CTE column counts, and invalid DISTINCT aggregate arity.
