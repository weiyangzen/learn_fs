# subset-b-008809 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/whereInt.h -->
# sources/storage-engines/sqlite/src/whereInt.h

## Purpose

`whereInt.h` is the private interface for SQLite's WHERE-clause planner and loop code generator. It is shared by the WHERE subsystem source files, especially `where.c`, `wherecode.c`, and `whereexpr.c`, and defines the in-memory model used to decompose expressions, enumerate candidate scan loops, choose a path, and emit VDBE loop bytecode.

The header intentionally keeps these definitions out of the public API. Its types are tightly coupled to parser state (`Parse`), source lists (`SrcList`/`SrcItem`), expression trees (`Expr`, `ExprList`, `Select`), schema metadata (`Table`, `Index`), estimated costs (`LogEst`), bitmask dependency tracking (`Bitmask`), and VDBE cursors/opcodes.

## Important APIs, types, and flags

- `WhereInfo` is the top-level WHERE planning/codegen state returned by `sqlite3WhereBegin()` and consumed by `sqlite3WhereEnd()`. It owns the `WhereClause`, `WhereMaskSet`, selected `WhereLoop` list, per-level `WhereLevel` array, loop labels, distinct/order metadata, one-pass state, deferred-seek flag, star-query flags, and memory cleanup chain.
- `WhereLevel` is the emitted-loop implementation record for one FROM item. It stores table/index cursors, break/continue/body labels, skip-scan and LIKE/big-null state, Bloom filter register, optional `WhereRightJoin`, selected `WhereLoop`, `notReady` dependency mask, and loop terminator opcode operands.
- `WhereLoop` represents a candidate or selected scan algorithm. It carries dependency masks, cost estimates (`rSetup`, `rRun`, `nOut`), table position, sort-order contribution, btree or virtual-table details, `wsFlags`, and the `WhereTerm` array that drives constraints.
- `WherePath` is the solver path abstraction: a sequence of `WhereLoop`s with accumulated row/cost/order information.
- `WhereTerm` represents one analyzed WHERE subexpression. It records the original expression, operator mask (`WO_*`), flags (`TERM_*`), parent/child virtual-term relationships, cursor/column on the left side, prerequisites, truth probability, OR/AND subclause info, vector field index, and virtual-table match operator.
- `WhereClause` owns an array of `WhereTerm`s split by `AND` or `OR`. It also tracks `nBase` so original terms can be distinguished from optimizer-created virtual terms.
- `WhereScan` is a term iterator used by planner code to find compatible constraints, including equivalence-class columns.
- `WhereMaskSet` maps sparse VDBE cursor ids to dense `Bitmask` bits so prerequisite and dependency sets fit in fixed-width masks.
- `WhereLoopBuilder` is the shared state used while proposing loops, including STAT4 probe state and planner combination limit controls.
- `WhereOrCost` and `WhereOrSet` keep the best few OR-branch alternatives.
- `WhereRightJoin` stores the extra cursors/registers/subroutine addresses needed to implement unmatched-row processing for RIGHT JOIN.
- `WhereMemBlock` tracks allocations attached to a `WhereInfo` lifetime via `sqlite3WhereMalloc()` and `sqlite3WhereRealloc()`.

The header also defines the planner-facing operator masks:

- `WO_EQ`, `WO_LT`, `WO_LE`, `WO_GT`, `WO_GE`, `WO_IN`, `WO_IS`, `WO_ISNULL` for ordinary indexable terms.
- `WO_OR` and `WO_AND` for decomposed compound terms.
- `WO_EQUIV` for transitive equivalence, `WO_ROWVAL` for vector/row-value slices, `WO_AUX` for virtual-table-only operators, and `WO_NOOP`.

`WhereLoop.wsFlags` drive code-generation selection:

- Constraint shape: `WHERE_COLUMN_EQ`, `WHERE_COLUMN_RANGE`, `WHERE_COLUMN_IN`, `WHERE_COLUMN_NULL`, `WHERE_TOP_LIMIT`, `WHERE_BTM_LIMIT`.
- Access strategy: `WHERE_IPK`, `WHERE_INDEXED`, `WHERE_IDX_ONLY`, `WHERE_VIRTUALTABLE`, `WHERE_MULTI_OR`, `WHERE_AUTO_INDEX`, `WHERE_SKIPSCAN`, `WHERE_IN_SEEKSCAN`.
- Semantics and optimizations: `WHERE_ONEROW`, `WHERE_PARTIALIDX`, `WHERE_IN_EARLYOUT`, `WHERE_BIGNULL_SORT`, `WHERE_TRANSCONS`, `WHERE_BLOOMFILTER`, `WHERE_SELFCULL`, `WHERE_OMIT_OFFSET`, `WHERE_COROUTINE`, `WHERE_EXPRIDX`.

## Control flow and state model

The state model is deliberately split into analysis, planning, and codegen phases:

1. `whereexpr.c` initializes and fills `WhereClause` with `WhereTerm`s, splitting the SQL WHERE tree, deriving virtual terms, computing dependency masks, and setting `WO_*`/`TERM_*`.
2. Planner code in `where.c` uses `WhereLoopBuilder`, `WhereScan`, `WhereLoop`, `WhereOrSet`, and `WherePath` to enumerate scan choices and choose loop order.
3. `wherecode.c` consumes the selected `WhereInfo.a[]` `WhereLevel`s and `WhereLoop`s to emit VDBE opcodes for table/index/virtual-table loops, IN loops, skip scans, OR subplans, Bloom filters, and outer joins.
4. `sqlite3WhereEnd()` uses the `WhereLevel` fields populated during start-code generation to close loops, resolve labels, emit unmatched outer-join rows, and release WHERE-owned memory.

`WhereTerm` parent-child flags are central. Optimizer-created children such as BETWEEN bounds, LIKE range constraints, transitive/commuted terms, and vector slices can mark original terms as already satisfied when all children are coded. Conversely, an original term can remain available as a correctness check if children are only range approximations.

Dependency masks are the other central control mechanism. `prereqRight`, `prereqAll`, `notReady`, `maskSelf`, and `prereq` prevent terms from being evaluated before all referenced FROM items are available and prevent ON-clause constraints from being incorrectly pushed across outer joins.

## State and persistence behavior

All state described here is transient planning/code-generation state for one SQL statement. It does not persist to the database. Persistence-like effects are limited to:

- VDBE bytecode emitted into the current prepared statement.
- Planner memory allocations attached to `WhereInfo.pMemToFree`.
- Temporary VDBE cursors/registers for rowsets, ephemeral indexes, Bloom filters, IN RHS materialization, RIGHT JOIN match tracking, and auto indexes.
- Optional scanstatus and EXPLAIN metadata embedded in VDBE opcodes.

The header's memory ownership signals are important. `TERM_DYNAMIC` means `WhereClauseClear()` must delete the expression. `TERM_ORINFO`/`TERM_ANDINFO` mean nested clauses must be recursively cleared. `WhereLoop.u.vtab.needFree` indicates ownership of `idxStr` returned by virtual-table planning.

## Dependencies and integration points

The header depends on core SQLite internal definitions from `sqliteInt.h`, including `Parse`, `SrcList`, `Expr`, `ExprList`, `Select`, `Index`, `Table`, `Vdbe`, `Bitmask`, `LogEst`, and many opcode/token/join constants. It integrates with:

- `whereexpr.c`: `sqlite3WhereClauseInit()`, `sqlite3WhereSplit()`, `sqlite3WhereExprAnalyze()`, usage-mask helpers, table-valued-function argument conversion, and LIMIT/OFFSET virtual-table constraints.
- `wherecode.c`: EXPLAIN text, scanstatus, loop-start bytecode emission, RIGHT JOIN unmatched-row loop generation.
- `where.c` and related planner files: mask lookup, term search, loop enumeration, loop printing, memory management, chosen path construction.
- VDBE: cursor ids, labels, registers, opcode operands, scanstatus ranges, `OP_Explain`, `OP_Filter`, `OP_DeferredSeek`, `OP_Next`/`OP_Prev`, and join subroutines.
- Virtual table API: `sqlite3_index_constraint` operator values are intentionally aligned with selected `WO_*` values and stored in `WhereLoop.u.vtab`.

## Risks and edge cases

- Bitmask width limits join size. `WhereMaskSet` compresses cursor ids, but the number of simultaneously tracked FROM terms is still bounded by `Bitmask` width.
- `WhereLevel` is both a codegen scratchpad and a contract with `sqlite3WhereEnd()`. Incorrect label/opcode fields can produce malformed VDBE control flow.
- Parent-child `TERM_*` state is correctness-critical for LIKE, BETWEEN, vector comparisons, and outer joins. Premature `TERM_CODED` can drop required runtime checks.
- `WO_*` values intentionally match virtual-table constraint constants for equality/range operators. Changing token or mask ordering can silently break xBestIndex integration.
- RIGHT JOIN and LEFT JOIN markings interact with prerequisite masks and `WhereRightJoin`; constraints must not be pushed to the wrong side of an outer join.
- `WHERE_IDX_ONLY`, `WHERE_MULTI_OR`, deferred seek, and covering-index fields determine whether table cursors are read. Mistakes can read stale/null rows or miss needed columns.
- `WhereLoop` copy boundaries such as `WHERE_LOOP_XFER_SZ` are fragile when fields are inserted.
- STAT4, scanstatus, WHERETRACE, virtual-table, LIKE, OR optimization, and window-function compile-time options create many conditional structure fields and behavioral paths.

## Test signals

Useful test coverage should include:

- EXPLAIN QUERY PLAN strings for rowid, covering-index, expression-index, partial-index, virtual-table, automatic-index, skip-scan, multi-index OR, and Bloom-filter scans.
- WHERE terms involving BETWEEN, LIKE/GLOB prefixes, vector equality, vector IN, `IS NULL`, `IS`, transitive equality, collations, expression indexes, and generated virtual terms.
- LEFT, RIGHT, and mixed outer joins with ON/WHERE constraints that can and cannot be pushed down.
- Virtual-table `xBestIndex` constraints for MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, `NOT NULL`, LIMIT, OFFSET, and IN handling.
- Large joins near `Bitmask` capacity.
- OOM/fault-injection runs around `WhereClause` growth, `WhereLoop` allocation, vtab `idxStr`, and OR/AND nested clause allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/whereInt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/wherecode.c -->
# sources/storage-engines/sqlite/src/wherecode.c

## Purpose

`wherecode.c` emits the VDBE bytecode that implements the query plan selected by SQLite's WHERE planner. It is the code-generation half of the WHERE subsystem: planner analysis chooses `WhereLoop`s and loop order, then this file turns each selected `WhereLevel` into concrete cursor seeks, scans, constraint checks, IN loops, virtual-table calls, Bloom-filter checks, OR subplans, deferred seeks, and outer-join bookkeeping.

The file also owns WHERE-loop EXPLAIN text and scanstatus instrumentation. It was split from `where.c` so planner enumeration and bytecode generation could evolve independently.

## Important APIs and functions

Public-to-the-WHERE-subsystem entry points:

- `sqlite3WhereExplainOneScan()` optionally emits an `OP_Explain` for a scan loop and returns its address.
- `sqlite3WhereExplainBloomFilter()` emits an `OP_Explain` describing a Bloom filter.
- `sqlite3WhereAddExplainText()` fills an existing `OP_Explain` P4 string with `SCAN`/`SEARCH`, table name, index name, rowid range, virtual-table index, LEFT-JOIN marker, and optional row estimate.
- `sqlite3WhereAddScanStatus()` records `sqlite3_stmt_scanstatus()` metadata and cursor address ranges.
- `sqlite3WhereCodeOneLoopStart()` is the main loop-start generator for one `WhereLevel`.
- `sqlite3WhereRightJoinLoop()` emits the second pass that outputs unmatched RHS rows for RIGHT JOIN.

Important internal helpers:

- `disableTerm()` marks a `WhereTerm` or its parent as coded, while respecting LEFT OUTER JOIN ON/WHERE semantics and LIKE two-pass checks.
- `codeApplyAffinity()` trims no-op affinity bytes and emits `OP_Affinity`.
- `updateRangeAffinityStr()` suppresses affinity changes that are unnecessary or unsafe for range RHS values.
- `removeUnindexableInClauseTerms()` rewrites vector `IN (SELECT...)` expressions to only the components usable by the selected index.
- `codeINTerm()` materializes or opens an IN RHS and sets up `WhereLevel.u.in.aInLoop`.
- `codeEqualityTerm()` evaluates equality, `IS NULL`, or IN constraints into registers and disables terms where safe.
- `codeAllEqualityTerms()` allocates key registers, handles skip-scan prefixes, evaluates equality constraints, and returns index affinity text.
- `whereLikeOptimizationStringFixup()` supports two-pass LIKE optimization when BLOBs can match LIKE.
- Cursor-hint helpers under `SQLITE_ENABLE_CURSOR_HINTS` build `OP_CursorHint` expressions that can be safely pushed to btree cursors.
- `codeDeferredSeek()` emits `OP_DeferredSeek` and optional column map data for OR/RIGHT-JOIN read avoidance.
- `codeExprOrVector()` evaluates scalar or vector RHS expressions into registers.
- `whereApplyPartialIndexConstraints()` marks WHERE terms implied by a partial index predicate as coded.
- `filterPullDown()` evaluates available inner Bloom filters before an outer index lookup.
- `whereLoopIsOneRow()` detects unique index equality scans that produce at most one row per IN key.

## Main control flow

`sqlite3WhereCodeOneLoopStart()` is the center of the file. It receives `pWInfo`, `iLevel`, `pLevel`, and a `notReady` mask, initializes break/continue/IN labels, detects reverse scan order from `revMask`, initializes LEFT JOIN match registers, and then dispatches by selected loop strategy:

1. Coroutine subquery: emits `OP_InitCoroutine` and `OP_Yield`, then records `OP_Goto` as the loop terminator.
2. Virtual table: evaluates xFilter constraints into a register block, handles virtual-table IN constraints either through `OP_VInitIn` or generated IN loops, emits `OP_VFilter`, sets up `OP_VNext`, reloads IN values that xFilter might mutate, and optionally emits post-filter equality checks for IN terms not handled by the virtual table.
3. Rowid equality/IN (`WHERE_IPK` with equality or IN): evaluates the rowid key, optionally checks a Bloom filter, emits `OP_SeekRowid`, and uses no iterative step.
4. Rowid range: computes start/end rowid bounds, emits `OP_SeekGT`/`OP_SeekGE`/`OP_SeekLT`/`OP_SeekLE` or full rewind/last, emits end-bound checks, and records `OP_Next`/`OP_Prev`.
5. Indexed btree scan: computes equality and range key registers, handles skip-scan, LIKE range two-pass setup, NULLS FIRST/LAST big-null scan, Bloom filters, `OP_SeekScan`, start seek, end-bound opcodes, deferred table seek or WITHOUT ROWID primary-key lookup, partial-index term elimination, and loop terminator selection.
6. Multi-index OR: recursively calls `sqlite3WhereBegin()` for each OR branch, uses `RowSetTest` for rowid tables or an ephemeral primary-key index for WITHOUT ROWID tables to suppress duplicates, invokes the main loop body via `OP_Gosub`, tracks a possible covering index, and propagates untested-term/deferred-seek state.
7. Full scan: emits `OP_Rewind`/`OP_Last` and `OP_Next`/`OP_Prev`, except recursive pseudo-cursors which need no iteration opcodes.

After opening/seeking the loop, the function emits residual WHERE-term tests in up to three passes: terms covered by the index first, then remaining terms without correlated subqueries, then correlated-subquery terms. It then emits transitive-equivalence checks that are not otherwise usable because a referenced table is not ready. Finally it records RIGHT JOIN matches, LEFT JOIN hits, and creates the RIGHT JOIN interior subroutine when needed.

`sqlite3WhereRightJoinLoop()` is a later second-pass generator. It nulls all tables to the left of the RIGHT JOIN, builds a single-table scan over the RHS, filters out rows already recorded in `WhereRightJoin.iMatch`/`regBloom`, and invokes the stored subroutine for unmatched rows.

## State and persistence behavior

This file mutates transient compilation state and emits persistent prepared-statement bytecode:

- `Parse.nMem` and `Parse.nTab` are incremented for registers and cursors used by constraints, rowsets, ephemeral indexes, Bloom filters, and subroutines.
- `WhereLevel` fields are populated with VDBE addresses (`addrBrk`, `addrCont`, `addrNxt`, `addrSkip`, `addrBody`, `addrFirst`, `addrBignull`), loop terminator opcode operands, IN-loop arrays, LIKE counters, Bloom filter registers, and scanstatus visit addresses.
- `WhereTerm.wtFlags` is changed with `TERM_CODED` and `TERM_LIKECOND` to avoid redundant or unsafe residual checks.
- `WhereInfo.bDeferredSeek` is set when generated code uses deferred table seeks.
- `WhereRightJoin` match structures are populated through generated VDBE operations (`OP_IdxInsert`, `OP_FilterAdd`, `OP_Filter`, `OP_Found`) at runtime.
- VDBE bytecode becomes part of the prepared statement and is later executed by the VM. No database file state is changed during compilation.

Runtime temporary state emitted by this file includes IN RHS cursors, RowSet registers, ephemeral duplicate-suppression indexes, Bloom filter registers, LEFT JOIN match flags, and RIGHT JOIN match indexes.

## Dependencies and integration points

`wherecode.c` depends heavily on structures and flags from `whereInt.h` and the rest of SQLite internals:

- Planner input: `WhereInfo`, `WhereLevel`, `WhereLoop`, `WhereTerm`, `WhereClause`, `WhereRightJoin`.
- Expression/codegen APIs: `sqlite3ExprCode*()`, `sqlite3ExprIfFalse()`, `sqlite3ExprCompare()`, `sqlite3ExprCoveredByIndex()`, `sqlite3CodeRhsOfIN()`, `sqlite3FindInIndex()`.
- VDBE APIs: `sqlite3VdbeAddOp*()`, labels, coverage annotations, P4 ownership, `sqlite3VdbeScanStatus*()`, `sqlite3VdbeNoJumpsOutsideSubrtn()`.
- Planner recursion: `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereContinueLabel()`, and `sqlite3WhereUsesDeferredSeek()` for OR subplans and RIGHT JOIN unmatched scans.
- Schema and storage metadata: rowid vs WITHOUT ROWID tables, primary-key indexes, covering indexes, expression indexes, partial indexes, collations, affinity strings, sort-order flags.
- Virtual-table integration: xBestIndex output stored in `WhereLoop.u.vtab`, `OP_VFilter`, `OP_VNext`, `OP_VInitIn`, omitted constraints, `idxNum`, `idxStr`, LIMIT/OFFSET omission.
- Conditional features: `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_OMIT_OR_OPTIMIZATION`.

## Risks and edge cases

- Outer join semantics are fragile. `disableTerm()`, residual term passes, cursor hints, partial-index implication, and RIGHT JOIN subroutines all need to distinguish ON terms from WHERE terms and LEFT/RIGHT/JT_LTORJ positions.
- Term disabling is an optimization with correctness consequences. Transitive constraints, LIKE range children, partial-index predicates, and virtual-table omitted constraints must only suppress checks when logically guaranteed.
- IN-loop state is spread across generated opcodes and `WhereLevel.u.in.aInLoop`; multi-column vector IN and virtual-table IN reloads are particularly sensitive to register and cursor ordering.
- Range seek opcodes depend on token ordering and reverse-order/sort-order swaps. Mistakes lead to off-by-one range inclusion errors.
- LIKE optimization may require two passes when BLOBs can match; the loop counter is packed into `iLikeRepCntr` and later affects `OP_String8` P3/P5 and residual LIKE evaluation.
- Big-null sort handling splits NULL and non-NULL scans and interacts with LEFT JOIN match flags.
- Bloom-filter pull-down clears `regFilter` after moving the check; doing so too early or with incorrect dependencies can skip valid rows.
- Deferred seek and covering-index logic can avoid table reads only when all later consumers can read from the index or tolerate null-row state.
- Recursive multi-index OR planning must avoid pushing down subqueries, row-value slices, or outer-join ON terms incorrectly.
- Virtual-table `OP_VFilter` P4 ownership and `idxStr` nulling after OOM avoid double-free/use-after-free issues; this path needs fault-injection coverage.

## Test signals

Good regression tests should inspect both results and generated plans:

- `EXPLAIN QUERY PLAN` for `SCAN`, `SEARCH`, covering indexes, rowid ranges, expression indexes, partial indexes, auto indexes, virtual-table indexes, multi-index OR, Bloom filters, LEFT JOIN, and RIGHT JOIN.
- Bytecode-level tests for `OP_SeekRowid`, `OP_SeekGE`/`LE`, `OP_IdxGT`/`GE`, `OP_SeekScan`, `OP_DeferredSeek`, `OP_CursorHint`, `OP_VFilter`, `OP_RowSetTest`, `OP_Filter`, and `OP_FilterAdd`.
- Query result tests for equality/range scans, reverse scans, skip scans, IN and vector IN, LIKE/GLOB prefixes, NULLS FIRST/LAST order, WITHOUT ROWID tables, expression and partial indexes.
- Multi-index OR tests with duplicate row suppression, outer joins, subqueries, row-value comparisons, covering-index eligibility, and `WHERE_DUPLICATES_OK`.
- Virtual-table tests for omitted constraints, handled and unhandled IN constraints, LIMIT/OFFSET pushdown, `idxStr` lifetime, and OFFSET counter zeroing.
- RIGHT JOIN tests with matched and unmatched rows, additional WHERE constraints, indexes on RHS, coroutines to the left, Bloom false positives, and WITHOUT ROWID RHS tables.
- OOM/fault-injection tests around vector-IN rewrite, IN-loop array allocation, `idxStr`, OR subplan SrcList allocation, scanstatus/explain strings, and deferred-seek column maps.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/wherecode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/whereexpr.c -->
# sources/storage-engines/sqlite/src/whereexpr.c

## Purpose

`whereexpr.c` analyzes SQL expression trees for the WHERE planner. It turns raw `Expr` trees into `WhereClause`/`WhereTerm` records with operator masks, prerequisite masks, cursor/column bindings, virtual terms, OR/AND subclauses, virtual-table auxiliary constraints, LIMIT/OFFSET constraints, and table-valued-function argument constraints.

This file does not choose final plans or emit most loop bytecode. Its output is the normalized and annotated term set consumed by planner enumeration and by `wherecode.c`.

## Important APIs and functions

WHERE-clause lifecycle:

- `sqlite3WhereClauseInit()` initializes a `WhereClause` with static term storage.
- `sqlite3WhereSplit()` recursively splits an expression tree by `AND` or `OR` into `WhereTerm` slots.
- `sqlite3WhereExprAnalyze()` walks base terms from end to beginning and calls `exprAnalyze()`; this ordering prevents newly appended virtual terms from being processed as base terms.
- `sqlite3WhereClauseClear()` frees dynamic expressions and nested `WhereOrInfo`/`WhereAndInfo` clauses.

Term insertion and normalization:

- `whereClauseInsert()` appends a term, grows storage with `sqlite3WhereMalloc()`, initializes truth probability from `EP_Unlikely`, and updates `nBase` for non-virtual terms.
- `allowedOp()` and `operatorMask()` identify operators that can become `WO_*` planner constraints.
- `exprCommute()` swaps comparison sides and fixes operator direction while preserving collation/vector semantics through `EP_Commuted`.
- `termIsEquivalence()` decides whether a column-column equality/IS term can be used for transitive substitution.
- `exprMightBeIndexed()` and `exprMightBeIndexed2()` determine whether an operand is a table column or expression-index candidate.

Derived/virtual-term analysis:

- `exprAnalyze()` is the main analyzer. It computes prerequisite masks, identifies left cursor/column, creates commuted terms, creates BETWEEN bounds, analyzes OR clauses, rewrites `IS NOT NULL`, adds LIKE/GLOB range terms, splits vector equality, slices vector IN, adds virtual-table auxiliary terms, and adjusts outer-join prerequisites.
- `exprAnalyzeOrTerm()` decomposes OR terms into `WhereOrInfo`, detects OR-to-IN transformations, recognizes indexable OR branches, creates nested `WhereAndInfo`, and creates helper conjuncts such as `x>=A` from `x>A OR (x=A AND ...)`.
- `whereCombineDisjuncts()` creates compatible virtual conjuncts from two OR branches.
- `markTermAsChild()` and `transferJoinMarkings()` preserve parent/child disabling behavior and outer-join ON markings.
- `whereNthSubterm()` iterates nested AND subterms under OR analysis.

LIKE, virtual-table, and usage helpers:

- `isLikeOrGlob()` detects optimizable LIKE/GLOB prefixes, including bound-parameter reprepare handling, escape removal, UTF-8 safety, numeric-prefix hazards, and collation/case decisions.
- `sqlite3ExprIsLikeOperator()` maps `match`, `glob`, `like`, and `regexp` function names to virtual-table constraint codes.
- `isAuxiliaryVtabOperator()` recognizes virtual-table-only constraints such as MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, and `NOT NULL`.
- `sqlite3WhereExprUsage()`, `sqlite3WhereExprUsageNN()`, `sqlite3WhereExprListUsage()`, and `sqlite3WhereExprUsageFull()` compute dependency bitmasks for expressions, subqueries, lists, table functions, and window-function components.
- `sqlite3WhereAddLimit()` and `whereAddLimitExpr()` add LIMIT/OFFSET pseudo-constraints for eligible single-virtual-table SELECTs.
- `sqlite3WhereTabFuncArgs()` converts table-valued-function arguments into equality terms against hidden columns.

## Control flow

The typical flow is:

1. `sqlite3WhereClauseInit()` prepares a `WhereClause`.
2. `sqlite3WhereSplit()` fills it with pointers into the original WHERE expression, split on `AND` for the top-level clause or `OR` for OR subclauses.
3. `sqlite3WhereTabFuncArgs()` may append hidden-column equality terms for table-valued functions.
4. `sqlite3WhereExprAnalyze()` calls `exprAnalyze()` for each base term.
5. `exprAnalyze()` computes `prereqLeft`, `prereqRight`, and `prereqAll`, adjusts for outer-join markings, and then applies specialized transformations:
   - Ordinary indexable comparisons get `leftCursor`, `leftColumn`, and `eOperator`.
   - If both sides are indexable, a commuted virtual term is appended and linked as a child.
   - BETWEEN becomes two virtual range terms.
   - OR terms are recursively split and analyzed into `WhereOrInfo`, possibly also producing IN or range-helper virtual terms.
   - `x IS NOT NULL` on ordinary columns can produce a virtual `x>NULL` range term tagged `TERM_VNULL`.
   - LIKE/GLOB prefix patterns produce lower and upper range terms tagged `TERM_LIKEOPT`.
   - Vector equality produces per-field slice terms and disables the original row-value term.
   - Vector IN with eligible SELECT RHS produces per-field virtual slices that share the original expression and use `u.x.iField`.
   - Virtual-table-only operators produce `WO_AUX` terms with `eMatchOp`.
6. Later planner code reads these terms to build loops, and `wherecode.c` may mark terms `TERM_CODED` when constraints are implemented.
7. `sqlite3WhereClauseClear()` recursively releases owned dynamic expressions and subclauses at teardown.

OR analysis has its own nested flow. `exprAnalyzeOrTerm()` first builds a `WhereOrInfo.wc`, analyzes all OR branches, tracks which tables are indexable, optionally builds nested `WhereAndInfo` clauses, marks the parent term `WO_OR`, tries two-way disjunct combination, and then tries OR-to-IN conversion when all equality branches share the same table column or compatible expression-index operand.

## State and persistence behavior

All state is compile-time planning state for a prepared statement:

- `WhereClause.a[]` may grow from static storage to `sqlite3WhereMalloc()`-managed storage owned by `WhereInfo`.
- Dynamic `Expr` copies are owned by terms tagged `TERM_DYNAMIC`.
- Nested OR/AND analysis allocates `WhereOrInfo`/`WhereAndInfo`, recursively containing `WhereClause` instances.
- `WhereTerm` fields are populated with dependencies, operator masks, child counts, parent indexes, truth probability, cursor/column ids, and special flags such as `TERM_VARSELECT`, `TERM_COPIED`, `TERM_VIRTUAL`, `TERM_SLICE`, `TERM_LIKE`, `TERM_LIKEOPT`, `TERM_VNULL`, `TERM_IS`, and `TERM_ORINFO`.
- Bound LIKE parameters mark VDBE variable masks to force reprepare when the pattern changes.
- Table-valued-function arguments and LIMIT/OFFSET pushdown append synthetic terms but do not change database state.

No database file state is persisted. The analyzed term structures live only for the statement compilation and are later encoded into a plan and VDBE program by other WHERE subsystem code.

## Dependencies and integration points

This file sits between parser expression trees and WHERE planner internals:

- Input expression structures come from `sqliteInt.h`: `Expr`, `ExprList`, `Select`, `SrcList`, `SrcItem`, `Table`, `Index`, join flags, expression flags, token codes, affinity/collation helpers, and virtual-table metadata.
- Output structures and flags come from `whereInt.h`: `WhereClause`, `WhereTerm`, `WhereOrInfo`, `WhereAndInfo`, `WhereMaskSet`, `WO_*`, `TERM_*`.
- Planner integration relies on `sqlite3WhereGetMask()` to translate cursor ids into bitmask dependencies and on `WhereTerm` fields consumed by loop builders.
- Codegen integration relies on `TERM_DYNAMIC`, parent-child relationships, `TERM_LIKECOND`, `TERM_SLICE`, `u.x.iField`, `WO_AUX`, and `eMatchOp`.
- Virtual-table integration uses `sqlite3ExprIsLikeOperator()`, `isAuxiliaryVtabOperator()`, hidden-column table-function terms, and LIMIT/OFFSET pseudo-constraints so `xBestIndex` can see nonstandard constraints.
- LIKE/GLOB optimization integrates with VDBE reprepare machinery for bound parameters and with `wherecode.c` two-pass LIKE/BLOB logic.
- Window-function and subquery usage analysis affects term scheduling because correlated subqueries are delayed in `wherecode.c`.

## Risks and edge cases

- `whereClauseInsert()` warns that term-array reallocation invalidates existing `WhereTerm *` pointers. Callers must reacquire pointers after inserting virtual terms.
- Outer-join markings are correctness-critical. `extraRight`, `EP_OuterON`, `EP_InnerON`, and `w.iJoin` prevent ON-clause terms from driving indexes on the wrong side of LEFT/RIGHT joins.
- OR-to-IN and transitive equivalence must respect affinity, collation, expression indexes, commuted expressions, and right joins. Incorrect `WO_EQUIV` can produce wrong answers.
- LIKE/GLOB prefix optimization has many hazards: UTF-8 malformed input, escape characters, numeric-looking prefixes on non-TEXT affinity, case folding, EBCDIC builds, bound parameters, and patterns that appear complete but still require runtime LIKE checks.
- Vector comparison slicing must not overrun child counters; the code explicitly guards vector IN child count against a 2026-06-04 bug. Row-value slices also must not be pushed into OR branches where RHS initialization might not run.
- `IS NOT NULL` to `x>NULL` is only safe for non-IPK ordinary columns and not for outer-join ON terms.
- Virtual-table auxiliary terms must avoid constraints where the RHS depends on the same table as the LHS.
- LIMIT/OFFSET pushdown is intentionally narrow. It is disabled for aggregate, DISTINCT, multi-source, unsupported ORDER BY, big-null ordering, and WHERE terms not fully passable to the virtual table.
- Usage-mask recursion through subqueries, table functions, and window expressions controls dependency scheduling. Missing a dependency can evaluate a term too early.

## Test signals

Regression coverage should include:

- Basic indexable terms for `=`, `<`, `<=`, `>`, `>=`, `IN`, `IS`, and `IS NULL`, including commuted forms.
- Column-column equality with transitive optimization on/off, mixed affinity, explicit collations, expression indexes, and RIGHT JOIN queries.
- BETWEEN expansion and parent-child disabling behavior.
- OR optimization cases: OR-to-IN, multi-index OR, nested AND branches, two-way disjunct range combination, expression-index OR terms, and OR terms with subqueries or row-value slices.
- LIKE/GLOB prefix optimization with bound parameters, escapes, non-ASCII, malformed UTF-8, numeric-looking prefixes, TEXT vs non-TEXT affinity, `NOCASE`, and BLOB-matching builds.
- Vector equality and vector IN with simple SELECT, VALUES, compound SELECT, window functions, large vectors, and OOM/fault injection.
- Virtual-table constraints for MATCH, LIKE, GLOB, REGEXP, `!=`, `IS NOT`, `NOT NULL`, overloaded functions, LIMIT/OFFSET, table-valued-function hidden columns, and omitted OFFSET.
- Outer join ON/WHERE combinations for LEFT, RIGHT, and JT_LTORJ joins, especially terms that would be legal inner-join pushdowns but illegal outer-join pushdowns.
- `WhereClauseClear()` under nested OR/AND and failed allocations to verify ownership and cleanup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/whereexpr.c -->
