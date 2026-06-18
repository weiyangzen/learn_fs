# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 107364-114787

Chunk id: `subset-b-009026`

## Purpose

This chunk covers four adjacent SQLite amalgamation modules:

- The tail of `memjournal.c`, implementing SQLite's rollback journal handle that can start in memory and optionally spill to the real VFS.
- `walker.c`, the generic parse-tree walker for expressions, SELECT statements, FROM-subqueries, and window definitions.
- `resolve.c`, the name resolver that turns SQL identifiers into resolved column/register/trigger/UPSERT references and validates aggregate, window, function, ORDER BY, GROUP BY, and self-reference rules.
- The beginning of `expr.c`, expression metadata, allocation, duplication, deletion, constant analysis, vector/subquery/IN handling, and early VDBE code generation helpers.

Within WiredTiger this is vendored SQLite test code, but the chunk is core SQLite compiler/runtime support. It bridges parsed SQL ASTs into semantically resolved expression trees and early VDBE bytecode.

## Important APIs, Types, and Functions

### Memory journal

- `FileChunk`, `FilePoint`, and `MemJournal` implement a `sqlite3_file` subclass backed by a linked list of fixed-size heap chunks until spill.
- `sqlite3JournalOpen()` initializes a journal handle. `nSpill==0` opens the real VFS immediately, `nSpill<0` keeps all content in memory, and `nSpill>0` buffers until the threshold or explicit creation.
- `sqlite3MemJournalOpen()` opens a permanent in-memory journal.
- `sqlite3JournalCreate()` forces a memory-backed journal onto disk for atomic or batch-atomic write paths when enabled.
- `sqlite3JournalIsInMemory()` and `sqlite3JournalSize()` expose journal storage mode and required handle size.
- Internal methods `memjrnlRead()`, `memjrnlWrite()`, `memjrnlTruncate()`, `memjrnlCreateFile()`, `memjrnlClose()`, and `memjrnlFileSize()` populate `MemJournalMethods`.

### Tree walking

- `sqlite3WalkExprNN()`, `sqlite3WalkExpr()`, and `sqlite3WalkExprList()` traverse expression trees/lists using `Walker.xExprCallback`, pruning or aborting according to `WRC_*` return values.
- `sqlite3WalkSelectExpr()`, `sqlite3WalkSelectFrom()`, and `sqlite3WalkSelect()` traverse SELECT result/WHERE/GROUP/HAVING/ORDER/LIMIT expressions, FROM-clause subqueries/table-valued function args, compound SELECT chains, and optional post callbacks.
- `walkWindowList()` and `sqlite3WalkWinDefnDummyCallback()` support window-function expression traversal when window functions are compiled in.
- `sqlite3WalkerDepthIncrease()` / `sqlite3WalkerDepthDecrease()` adjust `Walker.walkerDepth`; `sqlite3ExprWalkNoop()` and `sqlite3SelectWalkNoop()` are reusable no-op callbacks.

### Name resolution

- `lookupName()` is the central identifier resolver for `Z`, `Y.Z`, and `X.Y.Z`. It searches nested `NameContext` scopes, FROM terms, nested-from result columns, rowid aliases, triggers, UPSERT `excluded`, RETURNING rows, and SELECT aliases.
- `resolveExprStep()` is the expression-walker callback that handles identifier resolution, function lookup/validation, aggregate/window classification, subquery correlation marking, parameter restrictions, truth tests, vector-size checks, and NOT NULL strength reduction in WHERE clauses.
- `resolveSelectStep()` resolves expanded SELECT trees, including LIMIT, FROM subqueries, result expressions, HAVING/WHERE, table-valued function arguments, ORDER BY, GROUP BY, compounds, aggregate flags, and correlated-subquery state.
- `sqlite3ResolveExprNames()`, `sqlite3ResolveExprListNames()`, `sqlite3ResolveSelectNames()`, and `sqlite3ResolveSelfReference()` are the public resolver entry points used by parser/codegen paths.
- Helpers include `resolveAlias()`, `sqlite3MatchEName()`, `sqlite3ExprColUsed()`, `extendFJMatch()`, `isValidSchemaTableName()`, `resolveAsName()`, `resolveOrderByTermToExprList()`, `resolveCompoundOrderBy()`, `sqlite3ResolveOrderGroupBy()`, and `resolveOrderGroupBy()`.

### Expression analysis, allocation, copying, and deletion

- Affinity/collation APIs: `sqlite3TableColumnAffinity()`, `sqlite3ExprAffinity()`, `sqlite3ExprDataType()`, `sqlite3ExprAddCollateToken()`, `sqlite3ExprAddCollateString()`, `sqlite3ExprSkipCollate()`, `sqlite3ExprSkipCollateAndLikely()`, `sqlite3ExprCollSeq()`, `sqlite3ExprNNCollSeq()`, `sqlite3ExprCollSeqMatch()`, `sqlite3CompareAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3BinaryCompareCollSeq()`, and `sqlite3ExprCompareCollSeq()`.
- Vector and comparison helpers: `sqlite3ExprVectorSize()`, `sqlite3ExprIsVector()`, `sqlite3VectorFieldSubexpr()`, `sqlite3ExprForVectorField()`, `exprVectorRegister()`, `codeVectorCompare()`, and `codeCompare()`.
- Allocation/build APIs: `sqlite3ExprAlloc()`, `sqlite3Expr()`, `sqlite3ExprAttachSubtrees()`, `sqlite3PExpr()`, `sqlite3PExprAddSelect()`, `sqlite3ExprListToValues()`, `sqlite3ExprAnd()`, `sqlite3ExprFunction()`, `sqlite3ExprAddFunctionOrderBy()`, and `sqlite3ExprAssignVarNumber()`.
- Destruction/copy APIs: `sqlite3ExprDelete()`, `sqlite3ExprDeleteGeneric()`, `sqlite3ClearOnOrUsing()`, `sqlite3ExprDeferredDelete()`, `sqlite3ExprUnmapAndDelete()`, `sqlite3ExprDup()`, `sqlite3ExprListDup()`, `sqlite3SrcListDup()`, `sqlite3IdListDup()`, `sqlite3SelectDup()`, and `sqlite3WithDup()`.
- Expression-list APIs: `sqlite3ExprListAppend*()`, `sqlite3ExprListAppendVector()`, `sqlite3ExprListSetSortOrder()`, `sqlite3ExprListSetName()`, `sqlite3ExprListSetSpan()`, `sqlite3ExprListCheckLength()`, `sqlite3ExprListDelete()`, and `sqlite3ExprListFlags()`.
- Constant/nullability APIs: `sqlite3IsTrueOrFalse()`, `sqlite3ExprIdToTrueFalse()`, `sqlite3ExprTruthValue()`, `sqlite3ExprSimplifiedAndOr()`, `sqlite3ExprIsConstant()`, `sqlite3ExprIsConstantOrFunction()`, `sqlite3ExprIsConstantOrGroupBy()`, `sqlite3ExprContainsSubquery()`, `sqlite3ExprIsInteger()`, `sqlite3ExprCanBeNull()`, `sqlite3ExprNeedsNoAffinityChange()`, `sqlite3ExprIsSingleTableConstraint()`, `sqlite3IsRowid()`, and `sqlite3RowidAlias()`.

### IN/subquery and early codegen helpers

- `sqlite3FindInIndex()` chooses the RHS storage strategy for `IN`: direct rowid lookup, existing index, ephemeral b-tree, or comparison sequence (`IN_INDEX_NOOP`).
- `sqlite3CodeRhsOfIN()` materializes or reuses the RHS of `IN`, using `OP_BeginSubrtn`, `OP_Once`, `OP_OpenEphemeral`, `OP_OpenDup`, and optional Bloom filter wiring.
- `sqlite3ExprCodeIN()` emits the optimized seven-step IN-operator membership algorithm, including LHS vector coding, RHS probing, NULL handling, and fallbacks.
- `sqlite3CodeSubselect()` emits scalar subquery/EXISTS subroutines with implicit `LIMIT 1` and result-register initialization.
- `sqlite3ExprCheckIN()`, `sqlite3SubselectError()`, and `sqlite3VectorErrorMsg()` validate vector/subquery arity.
- `codeReal()`, `codeInteger()`, `sqlite3ExprCodeLoadIndexColumn()`, `sqlite3ExprCodeGeneratedColumn()`, `sqlite3ExprCodeGetColumnOfTable()`, `sqlite3ExprCodeGetColumn()`, `sqlite3ExprCodeMove()`, `sqlite3ExprToRegister()`, `exprCodeVector()`, and `setDoNotMergeFlagOnCopy()` start the general expression-to-VDBE codegen section.

## Control Flow

The memory journal code first attempts to satisfy reads and writes from `FileChunk` linked-list storage. Writes append to `endpoint`; a non-append write truncates back to the write offset except for the special atomic-write header rewrite at offset zero. If a write crosses `nSpill`, `memjrnlCreateFile()` opens the real VFS journal, writes all chunks in order, frees memory only after all writes succeed, and restores the copied in-memory state on error.

The walker layer provides the generic traversal engine used by later modules. `sqlite3WalkExprNN()` invokes the expression callback pre-order, then recurses into left/right children, subselects, expression lists, or window definitions. `sqlite3WalkSelect()` invokes the SELECT callback, walks expressions/FROM sources, invokes the optional post callback, and follows compound chains through `pPrior`.

Name resolution is a layered pass over already-expanded SELECT trees. `sqlite3ResolveSelectNames()` configures a `Walker` with `resolveExprStep()` and `resolveSelectStep()`. For each SELECT, the resolver handles subqueries first so correlation can be detected via `NameContext.nRef`. It then resolves result-set expressions, records aggregate/window flags, adds result aliases to the local `NameContext`, resolves HAVING/WHERE/table-valued function arguments/window definitions, and resolves ORDER BY/GROUP BY. Compound SELECT ORDER BY terms are resolved after all terms have compatible result-column counts.

`lookupName()` is the most branch-heavy path. It searches FROM sources in the innermost `NameContext`, with special treatment for nested FROM items, schema-table aliases, JOIN USING semantics, RIGHT/FULL JOIN precedence, rowid fallback, trigger `old`/`new`, UPSERT `excluded`, RETURNING base-register references, SELECT-list aliases, double-quoted string compatibility, and `true`/`false` identifiers. On success it mutates the AST node into a `TK_COLUMN`, `TK_REGISTER`, `TK_TRIGGER`, `TK_FUNCTION`/`coalesce` for FULL JOIN USING, `TK_NULL`, or related operator, then updates auth checks and scope reference counts.

Function resolution in `resolveExprStep()` looks up a `FuncDef`, enforces authorization and direct/unsafe/internal-function restrictions, propagates subtype requirements to arguments, marks constant/slow-changing functions, blocks non-deterministic functions in index/generated/partial-index contexts, rejects aggregate/window misuse, walks arguments with aggregate/window allowances temporarily narrowed, and converts aggregate calls to `TK_AGG_FUNCTION` with `op2` depth information.

Expression construction/deletion code follows SQLite's compact AST ownership rules. `Expr.x` may be a list or SELECT; `Expr.y` may hold a table, window, subquery data, etc. Deletion is recursive but optimized to avoid unnecessary recursion on unary left-deep chains. Duplication can allocate full-size or reduced/token-only expression nodes, and `TK_SELECT_COLUMN` copies preserve shared subquery ownership by using `pRight` for the one owner.

IN-code generation first validates vector arity, picks RHS representation with `sqlite3FindInIndex()`, codes/reorders the LHS vector, then either emits direct comparisons for small/non-constant lists or probes a b-tree/index. The generated bytecode distinguishes true, false, and NULL outcomes using separate false/null destinations. If an RHS b-tree exists, code checks LHS NULLs, performs rowid/index lookup, optionally checks RHS NULL status, and only scans RHS rows when needed to distinguish NULL from false.

## State and Persistence Behavior

- `MemJournal` persists journal bytes in heap chunks until forced to disk. Its durable state changes only when `memjrnlCreateFile()` successfully opens and writes through the underlying VFS. On failure it restores the original in-memory copy to preserve rollback capability.
- Resolver state is held in mutable AST nodes (`Expr`, `ExprList`, `Select`, `SrcItem`) and `NameContext` flags/counters. Important persisted semantic annotations include `Expr.op`, `iTable`, `iColumn`, `y.pTab`, `affExpr`, `op2`, `EP_*` flags, `Select.selFlags`, `SrcItem.colUsed`, `rowidUsed`, `isCorrelated`, and trigger masks `oldmask`/`newmask`.
- Expression allocator/copy/delete routines own heap memory through SQLite database allocators (`sqlite3DbMalloc*`, `sqlite3DbFree`, `sqlite3_free`) and parser cleanup registration (`sqlite3ParserAddCleanup`) for deferred deletes.
- Subquery and IN codegen persists reusable bytecode subroutines in `Expr.y.sub` plus `EP_Subrtn`, with result cursor/register locations in `Expr.iTable`. Compatible IN RHS subroutines are detected by scanning prior VDBE ops for `P4_SUBRTNSIG`.
- VDBE codegen state mutates `Parse` counters such as `nMem`, `nTab`, `nErr`, `nQueryLoop`, `okConstFactor`, `iSelfTab`, and scan-status/explain annotations.

## Dependencies and Integration Points

- The memory journal depends on the SQLite VFS abstraction (`sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, `sqlite3OsOpen`, `sqlite3OsWrite`, `sqlite3OsClose`) and memory allocation APIs.
- Walker and resolver code depend on parser AST structures (`Expr`, `ExprList`, `Select`, `SrcList`, `SrcItem`, `NameContext`, `Window`, `Table`, `Index`, `Column`, `Parse`) and flags/macros from `sqliteInt.h`.
- Name resolution integrates with ALTER TABLE rename-token tracking (`IN_RENAME_OBJECT`, `sqlite3RenameTokenRemap`, `sqlite3RenameExprUnmap`), authorization (`sqlite3AuthRead`, `sqlite3AuthCheck`), trigger/upsert handling, generated columns, partial indexes, CHECK constraints, trusted schema/direct-only function policy, and window-function linking.
- Expression codegen integrates with the VDBE API (`sqlite3VdbeAddOp*`, `OP_*`, labels, P4 encodings, coverage macros), query planner/index metadata (`Index`, `KeyInfo`, collation and affinity), SELECT codegen (`sqlite3Select`, `SelectDest`), and optimizer features such as Bloom filters and constant factoring.
- Compile-time feature switches heavily shape behavior: `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_GENERATED_COLUMNS`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, and floating-point/hex integer options.

## Risks and Edge Cases

- `memjrnlRead()` assumes requested bytes are within `endpoint` and relies on chunk traversal/readpoint caching; off-by-one errors around chunk boundaries would cause short reads or stale chunk access. The function intentionally returns `SQLITE_IOERR_SHORT_READ` if asked past EOF.
- `memjrnlCreateFile()` zeroes the live `MemJournal` before opening the real file. Its restore-on-error path is critical: losing the copied chunk list would break rollback after spill failure.
- The resolver mutates AST nodes in place. Incorrect ownership handling when replacing aliases or FULL JOIN `coalesce()` expressions can leak or double-free subtrees.
- Double-quoted string fallback preserves legacy behavior but can silently turn misspelled identifiers into strings when DQS is enabled; the code logs warnings and normalizes when enabled.
- JOIN USING/FULL JOIN resolution is subtle. `pFJMatch`, `JT_RIGHT`, `JT_LEFT`, and `JT_LTORJ` handling control whether duplicate names are ambiguous, left/right-preferred, or converted to `coalesce()`.
- Column-use masks saturate at `BMS-1` and generated columns mark all table columns used. These are conservative by design; false negatives in covering-index analysis would be correctness bugs, while extra bits are acceptable but may reduce optimization.
- Aggregate/window resolution must maintain `NC_AllowAgg`, `NC_AllowWin`, `NC_HasAgg`, `NC_HasWin`, and aggregate-depth `op2` correctly across nested SELECTs. Misclassification can allow illegal SQL or generate wrong aggregate scope.
- Constant/nullability predicates are deliberately conservative. Several comments call out that false positives are dangerous, especially in `sqlite3ExprCanBeNull()`, affinity-elision checks, single-table constraint tests, and WHERE-only NOT NULL strength reduction.
- IN-operator optimization depends on matching affinity, collation, uniqueness, vector arity, and NULL semantics. Existing index reuse must not be chosen if comparison semantics differ from the SQL expression.
- Subroutine reuse for IN RHS/subqueries depends on signatures, SELECT ids, affinity strings, and completed `OP_BeginSubrtn` metadata. Incorrect reuse could bind a later expression to incompatible ephemeral data.
- Generated-column code uses `COLFLAG_BUSY` to detect loops and temporarily changes `Parse.iSelfTab`; missing restoration would corrupt later column-codegen context.

## Test Signals

Relevant test coverage should exercise:

- Journal modes: pure in-memory journal, immediate VFS journal (`nSpill==0`), spill threshold crossing, explicit `sqlite3JournalCreate()`, write/truncate/read across chunk boundaries, offset-zero atomic header rewrite, OOM during chunk allocation, and disk-open/write failure recovery.
- Walker behavior: callback abort/prune/continue paths, right-recursive expression trees, subqueries in expressions and FROM, compound SELECT traversal, and window definitions.
- Name resolution: unqualified/qualified/fully-qualified columns, aliases in WHERE/ORDER/GROUP/HAVING, schema table legacy names, rowid aliases, hidden/generated columns, nested FROM items, natural/USING/LEFT/RIGHT/FULL joins, trigger `old`/`new`, RETURNING references, UPSERT `excluded`, DQS fallback, true/false identifiers, and authorization failures.
- Function validation: no-such/wrong-arity functions, aggregate misuse, window misuse, FILTER on non-aggregate, ORDER BY inside non-aggregate functions, direct-only/unsafe functions in schema objects, internal functions, subtype-sensitive functions, `likely`/`unlikely` probability argument validation, and non-deterministic functions in partial indexes/generated columns/index expressions.
- SELECT resolution: correlated subqueries, aggregate detection, HAVING on non-aggregate queries, GROUP BY aggregate rejection, compound SELECT term count mismatch, compound ORDER BY integer/alias/expression matching, converted compound subquery ORDER BY handling, and table-valued function arguments.
- Expression utilities: affinity/collation precedence, reduced/full/token-only expression duplication, `TK_SELECT_COLUMN` ownership, expression-list vector assignment, constant-expression detection, default-expression parameter handling, row-value misuse diagnostics, integer literal bounds, NULLability inference, and generated-column loop detection.
- IN/subquery codegen: scalar and vector `IN`, RHS lists of one/two/many values, constant versus non-constant lists, rowid/index/ephemeral/noop RHS selection, affinity/collation mismatch blocking index reuse, NULL on LHS/RHS, correlated RHS, subquery reuse, Bloom-filter path, EXISTS/scalar subquery `LIMIT 1`, and arity mismatch errors.

## Chunk Boundaries and Cross-Chunk Notes

- The chunk begins inside the `memjournal.c` module after preceding declarations/comments and ends in the middle of `expr.c` at the start of `exprCodeInlineFunction()`. Later expression codegen behavior is outside this chunk.
- Types, flags, opcodes, and many helper routines used here are declared or implemented elsewhere in the amalgamation, including parser structures, VDBE APIs, SELECT expansion/codegen, window functions, authorization, rename support, table/index metadata, and memory allocation internals.
- This chunk does not define public SQLite C API entry points. Most symbols are `SQLITE_PRIVATE` or `static` internal compiler/runtime helpers consumed by surrounding SQLite modules.
