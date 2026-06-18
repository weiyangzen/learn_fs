# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 172669-179062

## Chunk Scope

This chunk spans the end of SQLite's `window.c` implementation inside the amalgamated `sqlite3.c`, then crosses into the generated Lemon parser file `parse.c`. The window portion covers built-in window-function registration, `Window` object resolution and query rewriting, VDBE cursor/register initialization, frame-bound validation, aggregate step/inverse/final helpers, and most of `sqlite3WindowCodeStep()`. The parser portion begins with generated parser setup, token/action tables, debug rule names, parser stack management, destructors for parser semantic values, shift/reduce lookup helpers, and the start of reduction actions through early `CREATE TABLE` grammar handling.

Because this is amalgamated generated code, the canonical sources are SQLite's `src/window.c` and `src/parse.y`/Lemon output. Local changes to this chunk should normally be made in canonical SQLite sources and regenerated, not patched directly in the amalgamation.

## Purpose And Responsibilities

The `window.c` portion implements SQLite SQL window functions after parsing and name resolution:

- Registers non-aggregate built-in window functions such as `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `last_value`, `nth_value`, `lead`, and `lag`.
- Resolves named `WINDOW` clauses and chains derived windows against base definitions.
- Rewrites a `SELECT` containing window functions into a subquery that materializes the data needed by window processing in partition/order order.
- Allocates ephemeral cursors and VDBE registers used to buffer partition rows and evaluate window frames.
- Emits VDBE bytecode to advance frame start/current/end cursors, invoke aggregate `xStep`, `xInverse`, `xValue`, and `xFinalize` callbacks, and produce one output row at a time.
- Handles special built-in behavior for min/max, `first_value`, `nth_value`, `lead`, and `lag` without relying only on the generic aggregate-window callback path.

The `parse.c` portion initializes and drives SQLite's generated LALR parser:

- Defines parser support macros and small helper routines used by grammar actions.
- Stores generated token names, grammar rule names, parser action tables, fallback token mappings, and rule metadata.
- Manages the parser stack, including optional dynamic growth, tracing, coverage collection, and cleanup of semantic objects on pop/finalize/error.
- Begins `yy_reduce()`, where grammar reductions call into SQLite semantic routines such as transaction handling and table creation.

## Important APIs, Types, And Functions

### Window function registration and resolution

- `sqlite3WindowFunctions()` registers built-in window-only functions through `sqlite3InsertBuiltinFuncs()`. It uses `WINDOWFUNCALL`, `WINDOWFUNCNOOP`, and `WINDOWFUNCX` to create `FuncDef` entries with `SQLITE_FUNC_BUILTIN`, `SQLITE_UTF8`, and `SQLITE_FUNC_WINDOW`.
- Static function-name arrays such as `row_numberName`, `leadName`, and `nth_valueName` are intentionally compared by pointer in later logic, avoiding repeated string comparisons once a `FuncDef` is selected.
- `windowFind()` searches named window definitions and reports `no such window` through `sqlite3ErrorMsg()`.
- `sqlite3WindowUpdate()` copies a named window definition into an `OVER name` clause, chains base-window inheritance through `sqlite3WindowChain()`, enforces `RANGE` offset requirements, rejects `FILTER` on built-in non-aggregate window functions, and coerces frames required by built-ins such as `row_number`, `rank`, `lead`, and `lag`.

### SELECT rewriting

- `WindowRewrite` carries rewrite state: the main window list, original source list, accumulating subquery expression list, ephemeral `Table`, and current scalar subselect.
- `selectWindowRewriteExprCb()` rewrites selected expressions, aggregate expressions, outer-column references, and out-of-list window functions into `TK_COLUMN` reads from the future ephemeral cursor. It appends deduplicated source expressions to the subquery projection and carefully avoids rewriting expressions that belong to nested scalar subqueries.
- `selectWindowRewriteSelectCb()` preserves the nested-subquery boundary while still allowing outer references to be processed.
- `selectWindowRewriteEList()` runs the walker over result and order expression lists.
- `exprListAppendList()` appends duplicated expression lists, optionally replacing integer constants with `NULL` for sort expressions used only to preserve positional shape.
- `sqlite3WindowRewrite()` is the main public rewrite hook. It detaches the original `FROM`, `WHERE`, `GROUP BY`, and `HAVING`; builds a subquery sorted by `PARTITION BY` plus window `ORDER BY`; rewrites the outer result/order expressions against an ephemeral table; appends partition/order/window-argument/filter expressions to the subquery; assigns accumulator/result registers; attaches the subquery as the new `FROM`; and preserves aggregate-depth semantics for aggregate functions moved under the extra subquery layer.

### Window object lifecycle and comparison

- `sqlite3WindowUnlinkFromSelect()`, `sqlite3WindowDelete()`, and `sqlite3WindowListDelete()` detach and free linked `Window` objects and their owned expressions/lists.
- `sqlite3WindowOffsetExpr()` converts non-constant frame offsets to `NULL` so runtime validation catches them without leaving variable expressions in the tree.
- `sqlite3WindowAlloc()` validates frame-bound ordering, records implicit frames, applies `SQLITE_WindowFunc` optimization handling for `EXCLUDE`, and owns start/end offset expressions.
- `sqlite3WindowAssemble()` attaches partition/order/base-window pieces.
- `sqlite3WindowChain()` applies base window inheritance while rejecting attempts to override partition clauses, duplicate `ORDER BY`, or inherit from a window with an explicit frame.
- `sqlite3WindowAttach()` marks function expressions with `EP_WinFunc`, sets ownership, and rejects `DISTINCT` on window functions except for filter-frame internals.
- `sqlite3WindowLink()` links compatible windows into a `Select` so identical frames can be processed in one scan; incompatible partitioning records `SF_MultiPart`.
- `sqlite3WindowCompare()` compares frame type, bounds, exclusion mode, start/end expressions, partition list, order list, and optionally filters. Return value `0` means identical, `1` different, and `2` indeterminate from expression-list comparison.
- `sqlite3WindowDup()` and `sqlite3WindowListDup()` duplicate window definitions for expression/select duplication paths.

### VDBE setup and window execution helpers

- `sqlite3WindowCodeInit()` opens the main ephemeral table and three duplicate cursors, allocates partition tracking registers, initializes `regOne`, and creates auxiliary cursors/registers for `EXCLUDE`, min/max, `first_value`, `nth_value`, `lead`, and `lag`.
- `windowCheckValue()` emits bytecode that validates frame offsets and `nth_value()`'s second argument. Integer ROWS/GROUPS offsets use `OP_MustBeInt`; RANGE offsets accept non-negative numeric values.
- `windowArgCount()` returns the SQL argument count from the owner expression.
- `WindowCsrAndReg` pairs a VDBE cursor with peer-value registers.
- `WindowCodeArg` is the stack context passed to code-generation helpers. It carries parse/VDBE state, the main window list, gosub target, argument registers, deletion policy, rowid tracking, and the start/current/end cursor-register triples.
- `windowReadPeerValues()` loads window `ORDER BY` peer values from an ephemeral cursor.
- `windowAggStep()` emits either `OP_AggStep` or `OP_AggInverse`, or inline maintenance for min/max and positional built-ins. It handles filters, subtype-expression argument evaluation, collation requirements, and special `nth_value()` argument sourcing.
- `windowAggFinal()` emits `OP_AggValue` or `OP_AggFinal`, with min/max reading from an auxiliary index and finalization resetting accumulator state.
- `windowFullScan()` evaluates frames that require `EXCLUDE` handling by scanning from `regStartRowid` through `regEndRowid`, skipping current/group/ties rows as required, and then finalizing results.
- `windowReturnOneRow()` computes built-in positional outputs for `first_value`, `nth_value`, `lead`, and `lag`, then invokes the caller's output-row subroutine with `OP_Gosub`.
- `windowInitAccum()` initializes accumulators and auxiliary state at partition start.
- `windowCacheFrame()` determines when all rows must remain cached because a built-in needs random access or an `EXCLUDE` full scan is active.
- `windowIfNewPeer()` emits `ORDER BY` peer comparison logic used by GROUPS/RANGE processing.
- `windowCodeRangeTest()` emits RANGE-bound comparisons for the single-`ORDER BY` offset case, including ASC/DESC reversal, numeric add/subtract semantics, nonnumeric pass-through behavior, collations, `NULLS FIRST/LAST` and `KEYINFO_ORDER_BIGNULL` handling.
- `windowCodeOp()` emits one logical window operation: return current row, add rows to the aggregate frame, or inverse rows out of the frame. It also handles group/peer loops, EOF jumps, range countdown tests, and safe deletion from the ephemeral table.
- `sqlite3WindowCodeStep()` is the main bytecode generator after `sqlite3WhereBegin()`. It buffers each subquery row, detects partition changes, initializes frame offsets and cursors on the first partition row, emits different loop shapes for ROWS/GROUPS/RANGE and PRECEDING/CURRENT/FOLLOWING/UNBOUNDED combinations, flushes partitions after the input loop, and calls `sqlite3WhereEnd()` before emitting flush logic.

### Parser generated structures and routines

- `struct TrigEvent` and `struct FrameBound` are semantic-value helper structs used by parser actions for triggers and window frame bounds.
- `parserSyntaxError()`, `disableLookaside()`, `updateDeleteLimitError()`, `parserDoubleLinkSelect()`, `attachWithToSelect()`, `parserStackRealloc()`, `tokenExpr()`, `binaryToUnaryIfNull()`, and `parserAddExprIdListTerm()` are `%include` helper routines embedded before generated tables.
- Token definitions (`TK_*`) include core SQL, window-specific tokens (`TK_WINDOW`, `TK_OVER`, `TK_FILTER`, `TK_RANGE`, `TK_ROWS`, `TK_GROUPS`, `TK_EXCLUDE`, `TK_TIES`), and internal expression tokens.
- `yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, and `yy_default` implement the generated parser automaton.
- `yyFallback` lets many keywords fall back to `ID` in grammar positions where they may be identifiers.
- `yyTokenName`, `yyRuleName`, `yyRuleInfoLhs`, and `yyRuleInfoNRhs` support debugging, tracing, coverage, and reductions. The visible rules include SQL statements, expressions, CTEs, DML `RETURNING`, virtual tables, and window grammar rules.
- `yyParser`, `yyStackEntry`, `sqlite3ParserInit()`, optional `sqlite3ParserAlloc()`, `sqlite3ParserFinalize()`, optional `sqlite3ParserFree()`, and optional `sqlite3ParserStackPeak()` manage parser lifetime.
- `yy_destructor()` frees semantic values by type using SQLite-specific destructors such as `sqlite3SelectDelete()`, `sqlite3ExprDelete()`, `sqlite3ExprListDelete()`, `sqlite3SrcListDelete()`, `sqlite3WithDelete()`, `sqlite3WindowListDelete()`, `sqlite3WindowDelete()`, `sqlite3IdListDelete()`, and `sqlite3DeleteTriggerStep()`.
- `yy_find_shift_action()`, `yy_find_reduce_action()`, `yyStackOverflow()`, `yyTraceShift()`, `yy_shift()`, and the beginning of `yy_reduce()` implement parser execution mechanics.

## Control Flow Notes

Window execution has three major phases:

1. During parsing/name resolution, `Window` objects are allocated, assembled, attached to function expressions, linked into a `Select`, and updated against named/base windows.
2. Before planning/execution, `sqlite3WindowRewrite()` converts the original `SELECT` into a subquery-driven form. The subquery produces all columns, partition keys, order keys, function arguments, and filter values required by the window engine. The outer query reads from the ephemeral cursor instead of directly re-evaluating those expressions.
3. During VDBE generation, `sqlite3WindowCodeInit()` opens cursors and registers, while `sqlite3WindowCodeStep()` emits the row-processing loops. Input rows are inserted into a temporary table. Partition changes call a generated flush subroutine. Depending on frame type and bounds, the code advances `start`, `current`, and `end` cursors, calls `windowAggStep()` for xStep/xInverse, calls `windowAggFinal()` or built-in positional logic to populate result registers, and returns rows through the caller-provided gosub.

The frame loop structure is deliberately specialized:

- ROWS frames count physical rows.
- GROUPS frames process peer groups, using `windowIfNewPeer()` to detect new groups.
- RANGE frames compare order-key values through `windowCodeRangeTest()` and only allow offset RANGE frames with exactly one `ORDER BY` expression.
- `UNBOUNDED`, `CURRENT ROW`, `PRECEDING`, and `FOLLOWING` combinations are optimized by omitting impossible branches and by choosing when rows can be discarded from the ephemeral table.
- `EXCLUDE` handling switches to rowid-bound full scans through `windowFullScan()`.

The parser control flow is table-driven:

1. The tokenizer calls the generated parser with tokens and semantic minor values.
2. `yy_find_shift_action()` selects a shift, shift-reduce, reduce, accept, or error action from generated tables, applying fallback tokens when configured.
3. `yy_shift()` pushes tokens and grows the stack if allowed.
4. `yy_reduce()` executes grammar-specific semantic actions, pops the right-hand side, then finds and shifts the resulting nonterminal state.
5. Stack pops and parser finalization route owned semantic values through `yy_destructor()`, which is critical for freeing partially built AST objects after syntax errors or OOM.

## State And Persistence Behavior

The code in this chunk does not directly persist database file state. It builds transient parser, AST, and VDBE state that later execution may use to read or write the database.

Important transient state includes:

- `Window` fields such as `pPartition`, `pOrderBy`, frame bounds, exclusion mode, owner expression, function definition, buffer-column count, argument-column offset, accumulator/result registers, auxiliary cursors/registers, partition registers, and ephemeral cursor numbers.
- Parse-level counters `pParse->nTab` and `pParse->nMem`, which allocate VDBE cursor ids and register numbers for window processing.
- Ephemeral btree/table contents created by `OP_OpenEphemeral`, `OP_OpenDup`, `OP_Insert`, `OP_Delete`, and `OP_ResetSorter`; these hold partition rows only for statement execution.
- Aggregate contexts owned by VDBE aggregate opcodes and function implementations, finalized or reset as frame processing requires.
- Parser stack entries and semantic values, which own partially constructed `Select`, `Expr`, `ExprList`, `SrcList`, `With`, `Window`, `IdList`, and trigger-step objects until reductions transfer ownership or destructors free them.
- Optional debug globals `yyTraceFILE` and `yyTracePrompt`, plus optional parser coverage matrix `yycoverage`.

Window row-deletion policy (`WindowCodeArg.eDelete`) is a key memory behavior: rows may be retained for the whole partition, deleted after returning, deleted after entering the aggregate, or deleted after inverse processing. The selected policy depends on frame bounds and whether built-ins require random access to buffered rows.

## Dependencies And Integration Points

The window code integrates tightly with SQLite internals:

- Parser and AST types: `Parse`, `Select`, `Window`, `Expr`, `ExprList`, `SrcList`, `Table`, `FuncDef`, `Walker`, and `WhereInfo`.
- Expression and select helpers: `sqlite3ExprDup()`, `sqlite3ExprDelete()`, `sqlite3ExprListDup()`, `sqlite3ExprListAppend()`, `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, `sqlite3SelectNew()`, `sqlite3SrcListAppend()`, `sqlite3SrcItemAttachSubquery()`, `sqlite3ResultSetOfSelect()`, `sqlite3WalkSelect()`, `sqlite3WalkExprList()`, and parser cleanup hooks.
- VDBE APIs and opcodes: `sqlite3GetVdbe()`, `sqlite3VdbeAddOp*()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeChangeP5()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `OP_OpenEphemeral`, `OP_OpenDup`, `OP_AggStep`, `OP_AggInverse`, `OP_AggValue`, `OP_AggFinal`, `OP_Gosub`, `OP_Return`, `OP_Compare`, `OP_Jump`, `OP_SeekRowid`, `OP_SeekGE`, `OP_Next`, and others.
- Planner/codegen integration: `sqlite3WindowRewrite()` runs before normal SELECT generation, `sqlite3WindowCodeInit()` is called before stepping subquery rows, and `sqlite3WindowCodeStep()` is called around `sqlite3WhereBegin()`/`sqlite3WhereEnd()` flow from select code.
- Collation/key helpers: `sqlite3KeyInfoFromExprList()` and `sqlite3ExprNNCollSeq()` preserve SQL ordering and comparison semantics.
- Parser integration: the generated parser actions call semantic routines from many SQLite modules, including transaction, schema, expression, select, trigger, CTE, virtual table, upsert, returning, and window-definition construction code. The window grammar rules visible here feed `Window` objects into the `window.c` APIs.

## Risks And Edge Cases

- This is generated amalgamation code. Direct edits are easy to lose and can desynchronize from `window.c`, `parse.y`, and Lemon-generated tables.
- The window rewrite path mutates the `Select` tree extensively. Ownership mistakes around `pSrc`, `pWhere`, `pGroupBy`, `pHaving`, `pSublist`, and temporary `Table` objects can cause leaks or use-after-free, especially on OOM paths.
- Built-in window functions are identified partly by pointer equality against static name strings. Any alternate registration path that does not preserve these name pointers would bypass specialized behavior.
- `RANGE` offset frames are valid only with one `ORDER BY` expression; the code enforces this in `sqlite3WindowUpdate()`. Missing this restriction would make generated RANGE comparisons ambiguous.
- Frame offsets are validated at runtime. Non-constant offsets are converted to `NULL` earlier, then rejected by generated bytecode. Tests must cover both parse-time and runtime error paths.
- `windowCodeRangeTest()` handles DESC order, nonnumeric values, collations, and `NULLS FIRST/LAST`/BIGNULL semantics. Small changes can silently alter SQL-standard window frame membership.
- The ephemeral-table deletion policy is performance-sensitive and correctness-sensitive. Deleting too early breaks `lead`, `lag`, `first_value`, `nth_value`, `EXCLUDE`, or inverse processing; never deleting increases memory use for large partitions.
- `EXCLUDE` mode forces full-frame scans and rowid boundary tracking, which can be much more expensive than incremental aggregate/inverse processing.
- Min/max inline window maintenance uses an auxiliary ephemeral index and special delete logic. Duplicate values and NULL handling need coverage.
- Parser destructors are critical for syntax-error and OOM safety. A wrong semantic-type mapping can leak AST nodes or double-free them.
- Fallback keyword behavior affects SQL compatibility. Changing token tables or fallback mappings can make previously valid identifiers fail to parse.
- Parser stack behavior differs by build: amalgamation uses stack allocation for the engine object, while non-amalgamation builds may allocate/free parser objects and optionally grow stacks. OOM behavior must remain consistent in both modes.
- This chunk ends inside `yy_reduce()` at early table-option handling; most grammar semantic actions continue in later chunks, so parser behavior cannot be fully audited from this range alone.

## Test Signals

Useful tests and coverage signals for this chunk include:

- Window function SQL covering all built-ins registered here: `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `last_value`, `nth_value`, `lead`, and `lag`.
- Named and inherited windows: base-window lookup success/failure, prohibited overrides of `PARTITION BY`, duplicate `ORDER BY`, and explicit inherited frame specifications.
- `FILTER` behavior: allowed on aggregate window functions and rejected on built-in non-aggregate window functions.
- Frame variants across `ROWS`, `GROUPS`, and `RANGE`, including `UNBOUNDED`, `CURRENT ROW`, `PRECEDING`, `FOLLOWING`, empty frames, equal-bound FOLLOWING/PRECEDING cases, and runtime cases where start/end expressions make a frame empty.
- `RANGE` offset validation: no `ORDER BY`, multiple `ORDER BY` terms, DESC ordering, numeric/text/blob/NULL peer values, `NULLS FIRST`, `NULLS LAST`, and BIGNULL ordering.
- `EXCLUDE CURRENT ROW`, `EXCLUDE GROUP`, `EXCLUDE TIES`, and `EXCLUDE NO OTHERS` against peer groups and partitions of size zero/one/many.
- Sliding aggregate tests that require xInverse and compare results against equivalent correlated subqueries.
- min/max window frames with duplicates, NULLs, descending/ascending collation effects, and moving frame boundaries.
- `first_value`, `nth_value`, `lead`, and `lag` tests with default arguments, explicit offsets, invalid offsets, out-of-range offsets, and partitions with sparse row counts.
- OOM/fault-injection tests around `sqlite3WindowRewrite()`, `sqlite3WindowAlloc()`, expression duplication, `sqlite3ResultSetOfSelect()`, key-info allocation, parser stack allocation, and parser semantic destructors.
- Parser tests for visible grammar features: transactions/savepoints, `CREATE TABLE` table options (`STRICT`, `WITHOUT ROWID`, invalid options), CTEs with materialization modifiers, DML with `RETURNING`, virtual table declarations, expression operators, and window grammar productions.
- Debug/coverage builds using parser tracing and `YYCOVERAGE` should report exercised parser state/lookahead combinations, especially around `WINDOW`, `FILTER`, `OVER`, `RANGE`, `ROWS`, `GROUPS`, and frame exclusion tokens.
