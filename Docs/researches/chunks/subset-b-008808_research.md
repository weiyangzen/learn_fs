# sources/storage-engines/sqlite/src/where.c lines 6956-7886

## Scope

This chunk covers the final 931 lines of `where.c`. It starts inside `sqlite3WhereBegin()` after the `WhereInfo`, `WhereClause`, and `WhereLoopBuilder` scaffolding has already been allocated and the WHERE expression has been split into terms. It continues through the rest of `sqlite3WhereBegin()`, the debug-only opcode rewrite trace helper, and the complete `sqlite3WhereEnd()` implementation.

The slice is the handoff point between query planning and VDBE bytecode generation. It assigns FROM-clause masks, analyzes WHERE terms, builds and solves candidate `WhereLoop` plans, opens table/index cursors, emits the start of each nested loop, then later emits loop termination code and post-generation rewrites that turn table reads into index reads when a covering index or expression-index plan permits it.

## Purpose

- Finish planning a SELECT, UPDATE, or DELETE scan after earlier setup has initialized the `WhereInfo` object.
- Translate analyzed WHERE terms, ORDER BY or GROUP BY requirements, DISTINCT requirements, LIMIT estimates, join constraints, and optimization flags into selected nested-loop `WhereLevel` entries.
- Generate VDBE opcodes that open all required table, index, virtual table, ephemeral RIGHT JOIN, automatic-index, and Bloom-filter cursors.
- Emit the bytecode prologue for each nested loop using `sqlite3WhereCodeOneLoopStart()`, leaving callers to generate the loop body between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`.
- Generate the bytecode epilogue in `sqlite3WhereEnd()`, including `Next`/`Prev`/`VNext` instructions, IN-loop iteration, skip-scan continuation, LIKE range repetition, LEFT JOIN null-row fallback, RIGHT JOIN unmatched-row handling, and final break-label resolution.
- Perform late VDBE opcode rewriting so result-body code that initially reads from a table cursor can instead read from the selected index cursor when the plan is covering or potentially covering.
- Maintain query-planner bookkeeping such as `pParse->nQueryLoop`, `pWInfo->eOnePass`, `pWInfo->eDistinct`, `pWInfo->nOBSat`, cursor ids, labels, scan status, and debug/trace output.

## Important APIs, Types, And Functions

- `sqlite3WhereBegin(Parse*, SrcList*, Expr*, ExprList*, ExprList*, Select*, u16, int)` is the main entry point whose tail is covered here. It returns a populated `WhereInfo *` on success or `0` on allocation/planning/codegen error.
- `sqlite3WhereEnd(WhereInfo *pWInfo)` is the paired close-out API. Callers generate the SELECT/UPDATE/DELETE loop body after `sqlite3WhereBegin()` returns, then call this function to finish all nested loops and free `WhereInfo`.
- `WhereInfo` is the continuity object spanning begin/end. Fields used heavily in this chunk include `pParse`, `pTabList`, `pOrderBy`, `pResultSet`, `pSelect`, `aiCurOnePass`, `iBreak`, `iContinue`, `savedNQueryLoop`, `wctrlFlags`, `iLimit`, `nLevel`, `nOBSat`, `eOnePass`, `eDistinct`, `nRowOut`, `iTop`, `iEndWhere`, `pLoops`, `sWC`, `sMaskSet`, `revMask`, and `a[]`.
- `WhereLevel` describes the implementation state for one selected nested loop. This chunk fills or consumes `iFrom`, `iTabCur`, `iIdxCur`, `addrBrk`, `addrHalt`, `addrCont`, `addrFirst`, `addrBody`, `addrNxt`, `addrSkip`, `regBignull`, `addrBignull`, `iLeftJoin`, `pRJ`, `u.in`, `u.pCoveringIdx`, and the loop-ending opcode fields `op/p1/p2/p3/p5`.
- `WhereLoop` is the selected algorithm for a `WhereLevel`. This chunk consumes `wsFlags` and `u.btree.pIndex` to decide cursor opens, one-pass eligibility, index-only behavior, OR optimization behavior, DISTINCT skip-ahead, IN-loop cleanup, and covering-index rewrites.
- `WhereLoopBuilder sWLB` carries the candidate-loop builder state. This chunk calls `whereLoopAddAll(&sWLB)`, may discard and rebuild `pWInfo->pLoops` for the STAT4 second pass, and then calls `wherePathSolver()`.
- `WhereRightJoin` is allocated for RIGHT JOIN levels. It stores an ephemeral match cursor, a Bloom-filter register, a return register, and subroutine addresses used later by `sqlite3WhereRightJoinLoop()`.
- `createMask()`, `sqlite3WhereGetMask()`, and `WhereMaskSet` assign stable bitmasks to FROM cursors. The ordering invariant is important for LEFT and RIGHT join dependency tests elsewhere in the planner.
- `sqlite3WhereTabFuncArgs()` adds hidden function-argument constraints for table-valued functions before expression analysis.
- `sqlite3WhereExprAnalyze()` annotates `WhereTerm` objects with operator classes, prerequisite masks, virtual terms, and other planner metadata. `sqlite3WhereAddLimit()` adds LIMIT-derived planner information when applicable.
- `sqlite3ExprIfFalse()` emits an early bypass jump for constant-relative false WHERE terms. It targets `pWInfo->iBreak` and marks the term `TERM_CODED`.
- `isDistinctRedundant()`, `wherePathSatisfiesOrderBy()`, `whereInterstageHeuristic()`, and `wherePathSolver()` determine DISTINCT and ordering modes and choose a lowest-cost loop path.
- `whereShortCut()` can bypass the full loop-building solver for a simple single-table case.
- `whereOmitNoopJoin()` can delete join levels that do not affect the result when join and DISTINCT semantics allow it.
- `whereCheckIfBloomFilterIsUseful()` marks selected search loops that should use a Bloom filter before code generation.
- `sqlite3OpenTable()`, `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP4()`, `sqlite3VdbeChangeP5()`, `sqlite3VdbeSetP4KeyInfo()`, `sqlite3TableLock()`, and `sqlite3CodeVerifySchema()` are the main codegen and schema-validation APIs used to open cursors.
- `whereAddIndexedExpr()` and `wherePartIdxExpr()` install expression-index and partial-index metadata for later code generation when a new index cursor is opened.
- `constructAutomaticIndex()` and `sqlite3ConstructBloomFilter()` emit transient access structures just before the corresponding loop begins.
- `sqlite3WhereExplainOneScan()`, `sqlite3WhereAddScanStatus()`, and `sqlite3WhereAddExplainText()` maintain EXPLAIN QUERY PLAN and scan-status instrumentation.
- `sqlite3WhereCodeOneLoopStart()` emits the body-entry code for one nested scan and updates `WhereLevel` fields that `sqlite3WhereEnd()` later relies on.
- `translateColumnToCopy()` rewrites coroutine table reads to register copies in `sqlite3WhereEnd()`.
- `sqlite3TableColumnToIndex()`, `sqlite3StorageColumnToTable()`, and `sqlite3PrimaryKeyIndex()` map table column numbers to index column numbers for covering-index opcode rewriting.
- `OpcodeRewriteTrace()` is a macro. In non-debug builds it is a no-op; in debug builds it maps to `sqlite3WhereOpcodeRewriteTrace()`, which prints rewritten VDBE opcodes when `SQLITE_VdbeAddopTrace` is active.

## Control Flow

The chunk begins with the no-FROM case emitting an EXPLAIN QUERY PLAN row for a constant-row scan. For real FROM clauses, it assigns a bitmask to every `SrcItem` cursor in the full `pTabList`, even if `WHERE_OR_SUBCLAUSE` means only the first source is being coded. It also calls `sqlite3WhereTabFuncArgs()` for each source, allowing table-valued-function arguments to become WHERE-clause constraints.

After mask creation, `sqlite3WhereExprAnalyze()` analyzes all split terms and `sqlite3WhereAddLimit()` may inject LIMIT information. The false-WHERE-term bypass optimization then scans base WHERE terms for non-virtual terms with no local table prerequisites. If such a term is safe with respect to ON-clause and outer-join semantics, and is deterministic for a non-empty FROM clause, bytecode is emitted to jump directly to `pWInfo->iBreak` when the term is false or NULL. This avoids generating rows for impossible predicates while preserving legacy behavior for nondeterministic functions.

DISTINCT handling is normalized next. If `SQLITE_DistinctOpt` is disabled, the DISTINCT-specific flag is cleared. If DISTINCT is provably redundant, `pWInfo->eDistinct` becomes `WHERE_DISTINCT_UNIQUE`. Otherwise, if there is no caller-supplied ORDER BY, the planner treats the result set as an ordering target using `WHERE_DISTINCTBY` so duplicates can become adjacent.

Planner tracing can print the select tree and WHERE terms. The main planner path then either uses `whereShortCut()` for a qualifying one-table query or calls `whereLoopAddAll()` to build candidate loops for all FROM terms. Under `SQLITE_ENABLE_STAT4`, a builder flag can request a second full pass if STAT4-derived truth probabilities changed while later loops were being computed; the old `WhereLoop` list is deleted and rebuilt before solving.

`wherePathSolver(pWInfo, 0)` selects the initial loop order and access methods. If ordering is relevant, `whereInterstageHeuristic()` can adjust state between solver passes, then `wherePathSolver()` runs again with an output-row estimate. For DISTINCT queries, the selected row estimate is tuned down by `30` LogEst units, matching an assumed factor of eight reduction. If there is no ORDER BY and the connection has `SQLITE_ReverseOrder`, `whereReverseScanOrder()` reverses eligible scan directions.

After a solution is selected, optional optimizer passes run before cursor opening. `whereOmitNoopJoin()` can shrink `pWInfo->nLevel` and `nTabList` for joins whose tables do not affect the result. `whereCheckIfBloomFilterIsUseful()` can mark search loops for Bloom-filter construction. Tracing then prints the final WHERE clause and solution, and `pParse->nQueryLoop` is incremented by the estimated output rows.

For one-pass UPDATE/DELETE callers, the code checks that the selected single-level plan is either one-row or a safe multi-row plan. Multi-row one-pass requires `WHERE_ONEPASS_MULTIROW`, a non-virtual table, no OR optimization unless duplicates are acceptable, and the `SQLITE_OnePass` optimization. If a rowid table plan was index-only, index-only is cleared so the writable table cursor is opened and `OPFLAG_FORDELETE` can be set for multi-row delete.

The cursor-opening loop iterates over selected `WhereLevel` entries. It chooses `addrHalt` based on outer-loop and join state, opens virtual table cursors with `OP_VOpen`, opens ordinary tables with `sqlite3OpenTable()` unless an index-only plan can avoid them, and still opens tables for RIGHT JOIN and LEFT-of-RIGHT-JOIN cases where null-row or unmatched-row handling needs table state. For table opens, it can reduce the column count in the open opcode P4 operand based on `colUsed`, set cursor hints and `OPFLAG_FORDELETE`, emit `OP_ColumnsUsed`, and add an `OP_IfEmpty` early-exit for some deeper inner tables.

If the selected loop uses an index, the code chooses the index cursor. WITHOUT ROWID primary-key OR subclauses reuse the table cursor. One-pass uses the caller-provided auxiliary cursor range. OR subclauses may reopen the caller-provided index cursor. Otherwise a new cursor number is allocated and expression-index or partial-index metadata is registered. When an actual open opcode is needed, `OP_OpenRead`, `OP_OpenWrite`, or `OP_ReopenIdx` is emitted with key info, optional `OPFLAG_SEEKEQ`, comments, and optional index column-used masks.

RIGHT JOIN setup allocates a `WhereRightJoin` object, reserves an ephemeral match cursor, creates a Bloom filter blob register, initializes the return register, and opens an ephemeral btree keyed by rowid or by the WITHOUT ROWID primary key. It then clears `WHERE_IDX_ONLY` for the loop and disables ORDER BY/GROUP BY and ordered DISTINCT satisfaction because RIGHT JOIN unmatched-row output disrupts ordering.

After all opens, `pWInfo->iTop` records the VDBE address at the top of WHERE execution. The second `sqlite3WhereBegin()` loop emits actual loop starts. Materialized subqueries are populated once for non-correlated sources or every time for correlated sources. Automatic indexes and Bloom filters are constructed just before the scan that consumes them. EXPLAIN QUERY PLAN text is emitted, `addrBody` is recorded, `sqlite3WhereCodeOneLoopStart()` emits the start of the scan, and scan-status instrumentation is added for ordinary non-OR loops. `pWInfo->iEndWhere` is saved immediately before returning `pWInfo`.

If any error or allocation failure occurs after `pWInfo` allocation, control jumps to `whereBeginError`, restores `pParse->nQueryLoop`, frees `WhereInfo` with `whereInfoFree()`, touches debug-only routines to avoid compiler warnings, and returns `0`.

`sqlite3WhereEnd()` starts by recording the current VDBE address as `iEnd`, then iterates `WhereLevel` entries from inner to outer. RIGHT JOIN levels first close the interior subroutine by resolving the old continue label, replacing it with a dummy label, saving the subroutine end address, and emitting `OP_Return`. DISTINCT ordered scans may emit a skip-ahead seek (`OP_SeekLT` or `OP_SeekGT`) for the innermost indexed loop when statistics show enough duplicates. EXISTS-to-JOIN converted sources emit a break jump after one successful row.

The loop terminator then resolves `addrCont`, emits the level's ending opcode if it is not `OP_Noop`, resolves bignull and DISTINCT skip-ahead labels, and closes any nested IN loops in reverse order. IN-loop cleanup retargets null checks, optionally emits `OP_IfNotOpen` for LEFT JOIN cases whose IN cursor may not have opened, and can emit `OP_IfNoHope` for early-out index probes before adding `OP_Next` or `OP_Prev` for the IN cursor.

After `addrBrk` is resolved, RIGHT JOIN subroutine bodies return to the stored return register. Skip-scan and LIKE range repetition labels are wired up. LEFT JOIN levels then check their match flag; if no row matched, table and index cursors are moved to null rows, coroutine result registers may be nulled, and control jumps or gosubs back to the loop body so the caller body runs once with NULL right-side values.

The second `sqlite3WhereEnd()` pass iterates outer to inner for post-body rewrites. RIGHT JOIN levels delegate unmatched-row generation to `sqlite3WhereRightJoinLoop()` and skip normal rewriting. Coroutine subqueries call `translateColumnToCopy()` to turn table-column reads into register copies. Indexed loops select either `pLoop->u.btree.pIndex` or `pLevel->u.pCoveringIdx` for multi-index OR. If an index exists and no malloc failure has occurred, the code scans VDBE opcodes from just after the loop body marker to either `iEnd` or `pWInfo->iEndWhere` for one-pass rowid tables.

During rewrite, expression-index cache entries for this index cursor are disabled because the code is about to rewrite direct table references. `OP_Column` and optional `OP_Offset` against the table cursor are mapped through storage-column and index-column mappings. If the column is present in the index, the opcode cursor and column number are changed to use `iIdxCur`. If a covering-index plan cannot satisfy a referenced column, an internal planner error is reported. If the weaker `WHERE_EXPRIDX` flag was optimistic, it is cleared and EXPLAIN text is rewritten. `OP_Rowid` becomes `OP_IdxRowid`, and `OP_IfNullRow` is retargeted to the index cursor.

Finally, `sqlite3WhereEnd()` resolves the global break label, restores `pParse->nQueryLoop`, frees `WhereInfo`, subtracts the number of RIGHT JOIN subroutines from `pParse->withinRJSubrtn`, and returns.

## State And Persistence Behavior

- The central persistent-in-call state is `WhereInfo`, allocated by `sqlite3WhereBegin()` and freed by `sqlite3WhereEnd()` or the begin-error path.
- `pWInfo->sMaskSet` stores cursor-to-bitmask assignments. The assignments are transient but determine join-order legality, ON-clause applicability, and outer-join dependency handling throughout planning and code generation.
- `pWInfo->sWC` stores analyzed `WhereTerm` state. This chunk mutates term flags such as `TERM_CODED` when a false-term bypass is emitted.
- `pWInfo->pLoops` owns the candidate `WhereLoop` list. In the STAT4 second-pass case, all old loop objects are explicitly deleted and regenerated before solving.
- `pWInfo->a[]` stores selected `WhereLevel` implementation state. This chunk fills cursor ids, labels, selected loop pointers, right-join metadata, loop-ending opcodes, IN-loop metadata, and body addresses consumed later by `sqlite3WhereEnd()`.
- `pParse->nQueryLoop` is saved before this chunk by the earlier `WhereInfo` setup, incremented by selected row estimates during planning, and restored in both normal `sqlite3WhereEnd()` cleanup and `whereBeginError`.
- `pParse->nTab` is incremented for new index cursors, RIGHT JOIN match cursors, and other generated cursors. Those cursor numbers persist in the generated VDBE program, not in database storage.
- `pParse->nMem` is incremented for RIGHT JOIN Bloom and return registers and for DISTINCT skip-ahead register ranges in `sqlite3WhereEnd()`.
- `pWInfo->aiCurOnePass[]` records writable table and index cursors for one-pass UPDATE/DELETE callers. This is an observable contract through `sqlite3WhereOkOnePass()` outside this chunk.
- VDBE bytecode is appended to `pParse->pVdbe`. The generated opcodes are persistent within the prepared statement until the statement is finalized, but this chunk does not write database content by itself.
- Schema-read verification is recorded with `sqlite3CodeVerifySchema()` for every opened table/index database. This ties the prepared statement to schema-cookie validation at execution time.
- RIGHT JOIN setup creates ephemeral runtime structures and a blob-backed Bloom filter in registers. These structures live for statement execution and are not stored in database files.
- Covering-index rewrites mutate already-emitted VDBE opcodes between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`. This late mutation is deliberate: caller-generated loop-body code initially references table cursors without needing to know whether the table will be omitted.
- Debug and scan-status state is conditional. With `WHERETRACE_ENABLED`, trace output reads global `sqlite3WhereTrace`; with `SQLITE_ENABLE_STMT_SCANSTATUS`, scan status opcodes and addresses become visible to statement scan-status APIs.

## Dependencies And Integration Points

- The chunk depends on planner internals from earlier `where.c` sections: WHERE-term analysis, loop enumeration, OR-loop handling, automatic-index planning, Bloom-filter planning, path solving, join omission, reverse scan order, and loop-start code generation.
- It depends on internal definitions in `whereInt.h`, especially `WhereInfo`, `WhereLevel`, `WhereLoop`, `WhereLoopBuilder`, `WhereRightJoin`, `WhereClause`, `WhereTerm`, and the `WHERE_*` loop flags such as `WHERE_IDX_ONLY`, `WHERE_INDEXED`, `WHERE_VIRTUALTABLE`, `WHERE_MULTI_OR`, `WHERE_AUTO_INDEX`, `WHERE_BLOOMFILTER`, `WHERE_IN_ABLE`, `WHERE_ONEROW`, `WHERE_SKIPSCAN`, `WHERE_EXPRIDX`, `WHERE_BIGNULL_SORT`, and `WHERE_IN_SEEKSCAN`.
- It depends on public-ish planner control flags from `sqliteInt.h`, including `WHERE_WANT_DISTINCT`, `WHERE_DISTINCTBY`, `WHERE_GROUPBY`, `WHERE_AGG_DISTINCT`, `WHERE_KEEP_ALL_JOINS`, `WHERE_OR_SUBCLAUSE`, `WHERE_ONEPASS_DESIRED`, `WHERE_ONEPASS_MULTIROW`, `WHERE_DUPLICATES_OK`, `WHERE_ORDERBY_MIN`, and `WHERE_USE_LIMIT`.
- It integrates with SELECT code generation through the begin/end contract: `sqlite3WhereBegin()` opens cursors and positions rows, caller code emits result/update/delete logic, and `sqlite3WhereEnd()` closes the loop structure and rewrites body opcodes.
- It integrates with UPDATE and DELETE through one-pass state. Callers that request one-pass inspect `pWInfo->eOnePass` and `aiCurOnePass[]` to decide whether rowids must be collected first or whether the table can be modified in place.
- It integrates with virtual tables by emitting `OP_VOpen` for loops marked `WHERE_VIRTUALTABLE` and by avoiding ordinary table open behavior for virtual sources that are not selected as virtual-table loops.
- It integrates with table-valued functions through `sqlite3WhereTabFuncArgs()`, which makes function arguments participate in WHERE analysis before loops are built.
- It integrates with the VDBE opcode layer broadly: cursor opens, labels, jumps, null-row handling, IN-loop iteration, rowid/index-rowid reads, ephemeral btrees, subroutines, and key-info P4 payloads all use VDBE APIs.
- It integrates with schema management through `sqlite3SchemaToIndex()`, `sqlite3CodeVerifySchema()`, `sqlite3TableLock()`, and btree table/index root page numbers.
- It integrates with optional compile-time features: `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, `SQLITE_ENABLE_OFFSET_SQL_FUNC`, `SQLITE_DISABLE_SKIPAHEAD_DISTINCT`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_DEBUG`, and `WHERETRACE_ENABLED`.
- It integrates with RIGHT JOIN support through `JT_RIGHT`, `JT_LTORJ`, `WhereRightJoin`, `sqlite3WhereRightJoinLoop()`, and `pParse->withinRJSubrtn`.
- It integrates with ORDER BY, GROUP BY, and DISTINCT satisfaction by updating `pWInfo->nOBSat`, `revMask`, and `eDistinct`, and by disabling those optimizations when RIGHT JOIN makes the produced order unreliable.
- It integrates with EXPLAIN and statement scan status through `ExplainQueryPlan`, `sqlite3WhereExplainOneScan()`, `sqlite3WhereAddExplainText()`, `VdbeComment()`, `VdbeModuleComment()`, and `sqlite3WhereAddScanStatus()`.

## Risks And Edge Cases

- The false-WHERE-term bypass is semantically delicate. It must not move nondeterministic functions out of per-row evaluation in FROM queries, and it must respect ON-clause behavior for LEFT, RIGHT, and FULL joins.
- Mask assignment intentionally uses the full `pTabList->nSrc`, not only `nTabList`, because OR subclause planning may code one table while still needing stable masks for all FROM terms. A change here could break join prerequisite reasoning.
- The STAT4 second pass deletes and rebuilds all candidate loops. Any new loop-owned allocation must be freed correctly by `whereLoopDelete()` or the second-pass path can leak memory or reuse stale estimates.
- One-pass UPDATE/DELETE is constrained by OR optimization, virtual tables, and covering-index behavior. Marking `ONEPASS_MULTI` too aggressively can corrupt update/delete semantics, while clearing `WHERE_IDX_ONLY` too late can leave no writable table cursor.
- RIGHT JOIN processing intentionally clears index-only mode and disables ordering optimizations. Re-enabling covering behavior or ORDER BY elimination for RIGHT JOIN without matching unmatched-row logic can produce wrong rows or wrong ordering.
- The table-open elision for index-only scans is balanced by late opcode rewriting. If `sqlite3WhereEnd()` misses a table cursor reference, the VDBE may read from an unopened cursor. If it rewrites too much, it can read the wrong column from an index.
- Expression-index covering detection is intentionally optimistic under `WHERE_EXPRIDX`. The fallback path clears the flag and rewrites EXPLAIN text, but true `WHERE_IDX_ONLY` failures are internal planner errors.
- Column-number mapping differs for rowid tables, WITHOUT ROWID tables, generated columns, storage columns, and `OP_Offset`. The rewrite path must preserve all of these mappings.
- `pLastOp = pOp + (last - k)` assumes the VDBE address range is valid and that the first instruction of the loop body is not a table read. Debug assertions check part of this, but release builds depend on the surrounding codegen contract.
- LEFT JOIN null-row fallback has special coroutine and multi-OR index handling. Missing a cursor/register nulling case can emit non-NULL values for unmatched outer-join rows.
- IN-loop cleanup contains several label retargeting operations around `OP_IsNull`, `OP_Affinity`, and `OP_IfNoHope`. Small ordering changes can cause NULL handling or early-out probes to skip required affinity or loop steps.
- The DISTINCT skip-ahead optimization depends on statistics (`hasStat1`, `aiRowLogEst`) and applies only to the innermost indexed loop. Broader application could skip valid rows.
- `OP_IfEmpty` early exit is only emitted for selected inner levels with compatible join state. Applying it across LEFT or LEFT-of-RIGHT join boundaries would suppress required NULL-extended rows.
- Compile-time feature guards split behavior significantly. Builds without automatic indexes, virtual tables, cursor hints, column-used masks, offset SQL functions, or skip-ahead DISTINCT need separate coverage because opcode sequences differ.
- Error paths rely on `db->mallocFailed`, `pParse->nErr`, and explicit `rc` checks. Any helper that records an error without these signals may allow code generation to continue with partially initialized planner state.

## Test Signals

- Basic SELECT tests should confirm that no-FROM queries produce a constant-row plan and that ordinary FROM queries open the expected table or covering-index cursors under `EXPLAIN` and `EXPLAIN QUERY PLAN`.
- WHERE constant-false tests should cover deterministic false predicates, outer-query references, nondeterministic functions such as `random()`, scalar subqueries with nondeterminism, and ON-clause predicates under LEFT, RIGHT, and FULL join forms.
- DISTINCT and ORDER BY tests should cover redundant DISTINCT, DISTINCT-by-result-set ordering, ordered DISTINCT skip-ahead, reverse scan order, and RIGHT JOIN cases where ordering satisfaction is deliberately disabled.
- STAT4-enabled builds should exercise queries whose term truth probabilities change after STAT4 probing, verifying that the second loop-building pass changes estimates without leaking or crashing.
- One-pass UPDATE and DELETE tests should cover one-row rowid updates, multi-row one-pass deletes, OR-optimized scans with and without duplicates allowed, virtual tables, rowid versus WITHOUT ROWID tables, and index-only plans that must reopen the table for writing.
- Cursor-opening tests should inspect VDBE bytecode for `OP_OpenRead`, `OP_OpenWrite`, `OP_ReopenIdx`, `OP_VOpen`, `OP_OpenEphemeral`, `OP_ColumnsUsed`, `OP_IfEmpty`, and `OPFLAG_SEEKEQ` across rowid, WITHOUT ROWID, virtual, partial-index, expression-index, and OR-subclause plans.
- RIGHT JOIN tests should assert that matched rows are tracked, unmatched right-side rows are emitted with left-side NULLs, ordering optimizations are not incorrectly reported as satisfied, and rowid and WITHOUT ROWID match keys both work.
- Bloom-filter and automatic-index tests should verify that marked loops emit `sqlite3ConstructBloomFilter()` or `constructAutomaticIndex()` before `sqlite3WhereCodeOneLoopStart()` and that malloc failures in those paths abort cleanly.
- LEFT JOIN tests should cover null-row fallback for table scans, index scans, multi-OR covering indexes, and coroutine subqueries.
- IN operator tests should include multi-column IN, NULL left operands, LEFT JOIN cases where an IN cursor is not opened, virtual-table exclusions from `OP_IfNoHope`, and early-out behavior under `WHERE_IN_EARLYOUT`.
- Skip-scan, bignull sort, and LIKE range tests should inspect generated loop-tail bytecode for correct label wiring and repeat counters.
- Covering-index tests should execute queries whose result body reads only indexed columns and confirm table cursors are not opened or table opcodes are rewritten to index opcodes. Negative tests should cover expression-index plans that look covering in EQP text but later prove non-covering.
- WITHOUT ROWID tests should verify primary-key column mapping during covering-index rewrite and OR-subclause primary-key cursor reuse.
- Debug builds should exercise `PRAGMA vdbe_addoptrace=on` or equivalent trace paths so `OpcodeRewriteTrace()` output is covered without changing release behavior.
- Scan-status-enabled tests should verify that `sqlite3WhereAddScanStatus()` is omitted for OR-subclauses and multi-OR loops but present for ordinary loops.
- Failure-injection tests should simulate allocation failures around loop rebuilding, cursor opens, RIGHT JOIN allocation, key-info allocation, automatic index/Bloom construction, and opcode rewriting, then confirm `pParse->nQueryLoop` is restored and `WhereInfo` memory is freed.
