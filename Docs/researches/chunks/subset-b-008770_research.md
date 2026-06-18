# sources/storage-engines/sqlite/src/expr.c lines 7507-7727

## Scope

This chunk covers the final part of `analyzeAggregate()`, the public aggregate-analysis wrappers, and the temporary VDBE register allocator helpers in `expr.c`. The aggregate-analysis code records aggregate functions, aggregate input columns, `DISTINCT`, and aggregate-local `ORDER BY` requirements in `AggInfo`. The register helpers manage reusable scratch registers in `Parse` while expression, SELECT, DML, pragma, analyze, where, and window code emits VDBE bytecode.

## Purpose

- Detect aggregate function expressions at the correct query nesting level and map each one to an `AggInfo.aFunc[]` entry.
- De-duplicate equivalent aggregate functions so later code generation shares accumulator state.
- Record implementation details for aggregate `DISTINCT` and aggregate `ORDER BY`, including ephemeral cursor allocation, payload layout, uniqueness handling, and subtype preservation.
- Expose `sqlite3ExprAnalyzeAggregates()` and `sqlite3ExprAnalyzeAggList()` as the post-name-resolution passes that populate `AggInfo` for individual expressions and expression lists.
- Provide small, centralized helpers for allocating, releasing, clearing, touching, and debug-validating temporary VDBE registers.
- Provide `sqlite3FirstAvailableRegister()` for STAT4/debug code that must find a scratch register range after all permanent constant-expression registers.

## Important APIs, Types, And Functions

- `analyzeAggregate()` is the walker callback that recognizes `TK_AGG_FUNCTION` nodes. This chunk handles the function case after column/index-expression handling from the preceding lines.
- `sqlite3ExprAnalyzeAggregates(NameContext *pNC, Expr *pExpr)` initializes a `Walker` with `analyzeAggregate`, select-depth callbacks, the current `NameContext`, and an assertion that `pNC->pSrcList` exists before walking one expression tree.
- `sqlite3ExprAnalyzeAggList(NameContext *pNC, ExprList *pList)` iterates an `ExprList` and calls `sqlite3ExprAnalyzeAggregates()` for each item.
- `AggInfo` is the SELECT aggregate descriptor. `aFunc[]` entries hold the aggregate expression, `FuncDef`, optional distinct cursor, optional aggregate-ordering cursor, and flags consumed by SELECT code generation.
- `AggInfo_func.iOBTab` is an ephemeral cursor number used when aggregate step calls must be deferred until inputs are sorted by an aggregate-local `ORDER BY`.
- `AggInfo_func.iDistinct` is an ephemeral cursor number used to enforce `DISTINCT` for aggregate arguments when uniqueness is not already handled by the aggregate-ordering key.
- `AggInfo_func.bOBPayload`, `bOBUnique`, and `bUseSubtype` describe the record layout and semantics of the aggregate `ORDER BY` sorter.
- `sqlite3GetTempReg()` and `sqlite3ReleaseTempReg()` allocate and release single scratch registers through `Parse.aTempReg[]`, falling back to new `Parse.nMem` cells when the cache is empty.
- `sqlite3GetTempRange()` and `sqlite3ReleaseTempRange()` allocate and release consecutive scratch register ranges through the single cached range described by `Parse.iRangeReg` and `Parse.nRangeReg`.
- `sqlite3ClearTempRegCache()` invalidates both scratch caches. Callers use it after coding subroutines or coroutines whose registers must not alias their callers.
- `sqlite3TouchRegister()` advances `Parse.nMem` so a manually chosen register number is considered allocated.
- `sqlite3FirstAvailableRegister()` is compiled for `SQLITE_ENABLE_STAT4` or `SQLITE_DEBUG`. It skips registers owned by `Parse.pConstExpr`, clears scratch caches, and returns a usable lower bound.
- `sqlite3NoTempsInRange()` is debug-only and asserts that neither cached scratch registers nor factored constant-expression registers overlap a protected range.

## Control Flow

For `TK_AGG_FUNCTION`, `analyzeAggregate()` only claims the node when the walker is not currently analyzing aggregate-function arguments, the walker depth matches the expression's recorded aggregate depth, and `pExpr->pAggInfo` has not already been set. This prevents inner or outer aggregate contexts from stealing each other's expressions and avoids recursive registration while `analyzeAggFuncArgs()` analyzes aggregate arguments.

The function first scans `pAggInfo->aFunc[]` for an equivalent aggregate expression using `sqlite3ExprCompare(..., -1)`. If a match is found, the current expression reuses that entry. If the index would exceed `SQLITE_LIMIT_COLUMN`, the parser records "more than %d aggregate terms" and clamps to the limit. Otherwise `addAggInfoFunc()` appends a new entry, `sqlite3FindFunction()` resolves the aggregate implementation for the database encoding and arity, and the entry is initialized.

Aggregate-local `ORDER BY` is represented by `pExpr->pLeft` with `TK_ORDER`. The code allocates a new VDBE cursor number from `pParse->nTab` when an order list exists and the aggregate function does not require collation through `SQLITE_FUNC_NEEDCOLL`; the comment notes that this ignores aggregate `ORDER BY` for `min()` and `max()`. If the order list is a single expression identical to the single aggregate argument, `bOBPayload` is false and `DISTINCT` can be enforced by unique ordering keys through `bOBUnique`. Otherwise the sorter needs payload columns. Subtype preservation is enabled only for functions with `SQLITE_SUBTYPE`.

After the ordering setup, the distinct path allocates another ephemeral cursor from `pParse->nTab` only when the aggregate has `EP_Distinct` and uniqueness was not already folded into the ordering cursor. The expression is marked `EP_NoReduce`, its `iAgg` index is set, `pExpr->pAggInfo` points back to the shared `AggInfo`, and the walker prunes the subtree because this aggregate node has been classified.

`sqlite3ExprAnalyzeAggregates()` is a thin walker setup. Its select callbacks increment and decrement `walkerDepth` so aggregate functions inside nested SELECTs are compared against the correct `Expr.op2` depth. `sqlite3ExprAnalyzeAggList()` provides the same analysis over result lists, `ORDER BY`, `GROUP BY`, `HAVING`, aggregate argument lists, and filter expressions used by callers in `select.c`.

The temporary-register helpers are intentionally simple. Single-register allocation pops the last cached value from `aTempReg[]` or creates a new cell by incrementing `nMem`. Releasing a non-zero register first tells the VDBE layer that the register is no longer live with `sqlite3VdbeReleaseRegisters()`, then caches it if the fixed-size holding area has room. Range allocation either consumes the front of the one cached range or appends `nReg` cells to `nMem`; range release records the released block only if it is larger than the existing cached block. Clearing resets both cache counts without changing `nMem`.

## State And Persistence Behavior

This chunk does not write database storage. It mutates parser-time structures that determine later bytecode:

- `AggInfo.aFunc[]` grows with aggregate function descriptors. `Expr.iAgg` and `Expr.pAggInfo` create reverse links from expression nodes to those descriptors.
- `AggInfo_func.pFunc` stores the `FuncDef` selected by name, arity, and database encoding.
- `AggInfo_func.iOBTab` and `iDistinct` reserve VDBE cursor numbers by incrementing `Parse.nTab`; later SELECT code opens ephemeral tables for these cursors.
- `AggInfo_func.bOBPayload`, `bOBUnique`, and `bUseSubtype` persist decisions needed by aggregate step/finalization bytecode, especially `ORDER BY` extraction and subtype propagation.
- `Expr` nodes are marked `EP_NoReduce` under VVA/debug property handling to prevent memory reduction from removing fields needed during aggregate code generation.
- `Parse.nMem` is the high-water mark for VDBE memory registers. The scratch helpers increase it but never shrink it.
- `Parse.aTempReg[]`, `nTempReg`, `iRangeReg`, and `nRangeReg` are compile-time caches only. They do not imply persistent VDBE state and may be invalidated by `sqlite3ClearTempRegCache()` or by `sqlite3FirstAvailableRegister()`.
- `Parse.pConstExpr` is treated as a set of permanent registers for factored constant expressions. The debug/STAT4 helper skips these when searching for available registers.

## Dependencies And Integration Points

- Name resolution must run before this pass; the comment explicitly limits `sqlite3ExprAnalyzeAggregates()` to expressions already processed by `sqlite3ResolveExprNames()`.
- The aggregate walker depends on `NameContext` flags such as `NC_UAggInfo` and `NC_InAggFunc`, `NameContext.uNC.pAggInfo`, `NameContext.pSrcList`, and `Parse.nErr`.
- `addAggInfoFunc()`, `findOrCreateAggInfoColumn()`, and `addAggInfoColumn()` from the surrounding code own `AggInfo` array growth and column mapping.
- `sqlite3ExprCompare()` is used both for aggregate-function de-duplication and for the aggregate-`ORDER BY` single-key/single-argument identity check.
- `sqlite3FindFunction()` resolves the function implementation and exposes flags such as `SQLITE_FUNC_NEEDCOLL` and `SQLITE_SUBTYPE`.
- SELECT aggregate code generation in `select.c` consumes the fields set here. `finalizeAggFunctions()` uses `iOBTab`, `bOBPayload`, `bOBUnique`, and `bUseSubtype` to replay sorted aggregate inputs before `OP_AggFinal`.
- `analyzeAggFuncArgs()` in `select.c` sets `NC_InAggFunc` and calls these wrappers on aggregate arguments, aggregate-local `ORDER BY` terms, and window aggregate filters.
- The register allocator is used broadly by expression evaluation, DML, WHERE-loop code, window functions, pragmas, `ANALYZE`, and SELECT output code. It integrates with `sqlite3VdbeReleaseRegisters()` so VDBE register lifetime metadata stays consistent.
- Debug callers such as `ANALYZE` use `sqlite3NoTempsInRange()` and `sqlite3FirstAvailableRegister()` to protect long-lived register ranges from accidental scratch-register reuse.

## Risks And Edge Cases

- The aggregate-function term-limit check uses `i>mxTerm`, while a new entry is added when `i>=pAggInfo->nFunc`. The surrounding assumptions that `mxTerm` fits in `i16` and existing entries remain valid are important because `Expr.iAgg` is a 16-bit field.
- Aggregate de-duplication depends on expression structural comparison. If comparison ignores or over-weights a semantic property, unrelated aggregate calls could share state or equivalent calls could get duplicate accumulators.
- The walker-depth and `NC_InAggFunc` gates are correctness boundaries for nested SELECTs and aggregate arguments. A regression here can attach expressions to the wrong aggregate context.
- Aggregate `ORDER BY` is deliberately ignored for functions with `SQLITE_FUNC_NEEDCOLL`, including `min()` and `max()` per the in-code comment. Tests should treat this as an intentional compatibility behavior, not missing sorter setup.
- The `bOBUnique` optimization is valid only when the single ordering expression exactly matches the single aggregate argument. Incorrectly enabling it would make the ordering table enforce distinctness on the wrong key.
- `pItem->pFunc` is assumed available after `sqlite3FindFunction()`; earlier resolution is expected to have rejected unknown aggregate functions. The assertion-style flow relies on that pipeline.
- Releasing the same temporary register twice, releasing a register still referenced by future bytecode, or clearing caches too late can cause subtle register aliasing in generated VDBE programs.
- `sqlite3ReleaseTempRange()` keeps only the largest returned range. Smaller returned ranges are intentionally discarded, so callers cannot assume every released block will be reused.
- `sqlite3TouchRegister()` only raises `nMem`; it does not remove overlapping scratch-cache entries. Callers that protect manually assigned ranges may need `sqlite3ClearTempRegCache()` or debug assertions.
- `sqlite3NoTempsInRange()` is debug-only. Release builds rely on callers following the scratch-register ownership protocol.

## Test Signals

- Aggregate queries should reuse duplicate aggregate expressions in generated plans/results while still producing correct answers for syntactically or semantically different aggregates.
- Nested aggregate contexts should be covered with subqueries in SELECT lists, HAVING clauses, aggregate arguments, and window filters to verify walker-depth handling.
- Aggregate `DISTINCT` should be tested with and without aggregate-local `ORDER BY`, especially the one-argument/one-order-key case where `bOBUnique` replaces a separate distinct table.
- Ordered aggregates such as `string_agg()`/`group_concat()` with one key, multiple keys, payload columns, duplicate inputs, and subtype-bearing values should exercise `iOBTab`, `bOBPayload`, and `bUseSubtype`.
- `min()` and `max()` with aggregate-local `ORDER BY` should preserve the documented behavior implied by the `SQLITE_FUNC_NEEDCOLL` exclusion.
- Limit tests should drive many aggregate terms to verify the `SQLITE_LIMIT_COLUMN` error path and that no out-of-range `Expr.iAgg` values are generated.
- OOM tests around `addAggInfoFunc()` and function analysis should leave `Parse.nErr`/malloc failure state consistent and avoid dereferencing missing `AggInfo` entries.
- Register-allocation tests are mostly indirect: expression-heavy SELECT, INSERT, UPDATE, WHERE, pragma, window, and ANALYZE tests should run under debug builds with `sqlite3NoTempsInRange()` assertions enabled.
- Subroutine and coroutine paths should continue to call `sqlite3ClearTempRegCache()` before reusable code can be invoked from multiple places, preventing scratch-register aliasing between caller and callee.
- STAT4/debug builds should cover `sqlite3FirstAvailableRegister()` with factored constant expressions so it skips `Parse.pConstExpr` registers before allocating analysis memory.
