# sources/storage-engines/sqlite/src/vdbe.c lines 7601-9437

## Scope

This chunk covers the final portion of `sqlite3VdbeExec()`, SQLite's virtual database engine bytecode interpreter. The slice starts inside the `OP_Program` trigger/subprogram handoff, then covers opcodes for trigger parameters, foreign-key counters, LIMIT/OFFSET counters, aggregate and scalar functions, WAL/journal/vacuum pragmas, virtual-table execution, bloom filters, tracing and initialization, debug-only register validation, no-op explain records, and the common error/return exits for the interpreter loop.

## Purpose

- Complete execution of high-level SQL features that are lowered into VDBE opcodes late in the opcode switch: triggers, foreign keys, autoincrement bookkeeping, aggregates/window functions, pragmas, virtual tables, scalar functions, bloom filters, and statement tracing.
- Bridge the VDBE register machine to external subsystems: pager/WAL checkpointing, btree page-count and autovacuum calls, virtual table module callbacks, user-defined SQL functions, and tracing/file-control hooks.
- Preserve interpreter state across nested trigger programs by saving the current `Vdbe` frame and replacing `p->aMem`, `p->apCsr`, `p->aOp`, `p->nMem`, and `p->nCursor` with the subprogram frame.
- Normalize error handling through shared labels (`abort_due_to_error`, `too_big`, `no_mem`, `abort_due_to_interrupt`, and `vdbe_return`) so opcode bodies can jump out consistently after setting `rc` and, when relevant, `p->zErrMsg`.
- Maintain runtime instrumentation signals such as statement status counters, branch-coverage markers, VDBE traces, profile/scanstatus cycle accounting, VM-step counts, and debug register dumps.

## Important APIs, Types, And Functions

- `sqlite3VdbeExec(Vdbe *p)` is the enclosing interpreter. This chunk is still inside its opcode dispatch loop and uses shared interpreter locals such as `db`, `aMem`, `aOp`, `pOp`, `rc`, `encoding`, `nVmStep`, `nProgressLimit`, and `resetSchemaOnFault`.
- `VdbeFrame`, `SubProgram`, and `Mem` support trigger/subprogram execution. The frame stores the parent program, cursors, registers, `lastRowid`, change counters, and auxiliary function data before the interpreter switches to the child bytecode.
- `OP_Param` copies `old.*` and `new.*` trigger values from the parent frame into the current frame using the calling `OP_Program` operand offset.
- `OP_FkCounter` and `OP_FkIfZero` update and test foreign-key violation counters split across statement-local immediate constraints (`p->nFkConstraint`), connection deferred constraints (`db->nDeferredCons`), and deferred immediate constraints under `SQLITE_DeferFKs` (`db->nDeferredImmCons`).
- `OP_MemMax` updates a register in the root frame for autoincrement maximum-rowid tracking even when execution is inside nested trigger frames.
- `OP_IfPos`, `OP_IfNotZero`, `OP_DecrJumpZero`, and `OP_OffsetLimit` implement integer loop counters and LIMIT/OFFSET accounting directly in VDBE registers.
- `OP_AggStep`, `OP_AggInverse`, and `OP_AggStep1` allocate and cache an `sqlite3_context` in `pOp->p4`, bind argument registers to `sqlite3_context.argv`, and call `FuncDef.xSFunc` or, for window inverse steps, `FuncDef.xInverse`.
- `OP_AggFinal` and `OP_AggValue` call `sqlite3VdbeMemFinalize()` or `sqlite3VdbeMemAggValue()` to materialize aggregate/window results, then normalize result encoding and blob-size accounting.
- `OP_Checkpoint`, `OP_JournalMode`, `OP_Vacuum`, `OP_IncrVacuum`, `OP_Pagecount`, and `OP_MaxPgcnt` are pragma/storage opcodes that call into WAL, pager, vacuum, and btree APIs.
- `OP_Expire`, `OP_CursorLock`, `OP_CursorUnlock`, and `OP_TableLock` coordinate statement expiration, btree cursor pinning, and shared-cache table locks.
- Virtual-table opcodes include `OP_VBegin`, `OP_VCreate`, `OP_VDestroy`, `OP_VOpen`, `OP_VCheck`, `OP_VInitIn`, `OP_VFilter`, `OP_VColumn`, `OP_VNext`, `OP_VRename`, and `OP_VUpdate`. They call module methods such as `xBegin`, `xCreate`, `xDestroy`, `xOpen`, `xIntegrity`, `xFilter`, `xColumn`, `xNext`, `xRename`, and `xUpdate`.
- `OP_Function` and `OP_PureFunc` invoke scalar SQL functions using cached `sqlite3_context` objects, update auxdata lifetime with `sqlite3VdbeDeleteAuxData()` on errors, and enforce output-size and encoding invariants.
- `OP_ClrSubtype`, `OP_GetSubtype`, and `OP_SetSubtype` manipulate the `MEM_Subtype` flag and `Mem.eSubtype` byte used by subtype-aware SQL functions.
- `OP_FilterAdd` and `OP_Filter` use the file-local `filterHash()` helper to implement VDBE bloom-filter tests over register keys, updating `SQLITE_STMTSTATUS_FILTER_HIT` and `SQLITE_STMTSTATUS_FILTER_MISS`.
- `OP_Trace` and `OP_Init` emit statement trace callbacks, manage `OP_Once` reset epochs, increment `SQLITE_STMTSTATUS_RUN`, and jump to the program start address.
- Debug/test opcodes `OP_CursorHint`, `OP_Abortable`, and `OP_ReleaseReg` integrate with btree cursor hints, abort-safety assertions, and debug detection of stale register reads.
- The default opcode case handles `OP_Noop` and `OP_Explain`, preserving query-plan explanation records without runtime work.

## Control Flow

The slice begins as `OP_Program` has either allocated a new `VdbeFrame` or recovered one cached in a trigger register. The interpreter increments `p->nFrame`, links the new frame to the parent, snapshots parent rowid and change counters, moves `p->pAuxData` into the frame, clears child change state, and then replaces the active memory/cursor/opcode arrays with the subprogram arrays. Debug builds mark all child registers undefined before setting `pOp = &aOp[-1]` and jumping to `check_for_interrupt`, causing the normal dispatch loop to begin executing child opcodes.

Trigger code then uses `OP_Param` to read parent-frame registers. The register address is computed from the opcode's `P1` plus the `P1` operand of the parent `OP_Program`, and the value is shallow-copied into the child output register as ephemeral data.

Counter opcodes are mostly straight-line register mutations with conditional jumps. `OP_FkCounter` selects the right foreign-key counter based on deferred/immediate mode. `OP_FkIfZero` branches to `P2` only when the relevant counters are clear. `OP_IfPos`, `OP_IfNotZero`, and `OP_DecrJumpZero` mutate integer registers before optionally jumping; `OP_OffsetLimit` computes the number of rows a LIMIT/OFFSET loop must visit and uses `-1` as the no-limit sentinel.

Aggregate execution has a two-phase flow. The first `OP_AggStep` or `OP_AggInverse` sees a `P4_FUNCDEF`, allocates an `sqlite3_context` plus a private `Mem` output cell, rewrites the opcode to `OP_AggStep1`, and falls through. Later executions reuse the cached context. Each step refreshes argument pointers if trigger frame reuse changed `aMem`, calls the step or inverse callback, handles function errors and collation skip flags, and restores `pCtx->pOut` to NULL state before continuing. Final/value opcodes then call the appropriate VDBE memory helper and jump to the common abort path on callback errors.

Storage-management opcodes call out to subsystem APIs and translate their return codes into VDBE register results or control-flow jumps. `OP_Checkpoint` writes three result registers and treats `SQLITE_BUSY` as a non-fatal busy flag. `OP_JournalMode` validates the requested pager mode, rejects illegal WAL transitions from inside transactions or unsupported storage, possibly changes the database file-format version through `sqlite3BtreeSetVersion()`, and writes the final mode name to the output register. `OP_IncrVacuum` jumps when btree incremental vacuum returns `SQLITE_DONE`; `OP_Vacuum` aborts on any non-OK vacuum result.

Virtual-table control flow mirrors the SQLite module API. `OP_VOpen` opens or reuses a virtual cursor and installs it in a `VdbeCursor`. `OP_VFilter` reads the query plan and argv count from registers, populates `p->apArg`, calls `xFilter`, then jumps to `P2` if `xEof` reports no rows. `OP_VColumn` sets up a stack `sqlite3_context`, handles NULL-row and no-change cases, calls `xColumn`, and stores the result in a VDBE register. `OP_VNext` calls `xNext` and jumps back to the loop body while rows remain. `OP_VUpdate` prepares argv pointers, temporarily sets `db->vtabOnConflict`, calls `xUpdate`, updates `lastRowid` and change counters, and converts virtual-table constraint failures according to the opcode conflict policy.

Function and filter opcodes resume straight-line interpreter flow unless they branch or fail. `OP_Function` and `OP_PureFunc` refresh cached context pointers when register arrays change, clear the output, invoke the SQL function, delete auxdata on error, then trace and size-check the result. Bloom-filter opcodes compute a bit position from the key hash; `OP_FilterAdd` sets the bit and `OP_Filter` jumps only when the bit is absent.

`OP_Trace`/`OP_Init` is the entry opcode path. It emits legacy or v2 trace callbacks when enabled, optionally sends `SQLITE_FCNTL_TRACE` to active database files, resets `OP_Once` operands when the once epoch reaches `sqlite3GlobalConfig.iOnceResetThreshold`, increments the run counter, and jumps to `P2`. `OP_Trace` can stop after trace output when the reset threshold case applies.

After each opcode, profiling or scanstatus cycle counters are finalized for the opcode. In debug builds, the loop asserts that `pOp` remains within the opcode array and optionally prints output-register traces based on `sqlite3OpcodeProperty`. Leaving the dispatch loop without a normal `vdbe_return` means an error occurred and execution continues at `abort_due_to_error`.

The shared error path rewrites malloc and corrupt-filesystem codes, ensures an error message exists, stores `p->rc`, reports system errors, logs the abort with `sqlite3VdbeLogAbort()`, halts a running VM with `sqlite3VdbeHalt()`, marks corrupt read-only transaction state when appropriate, resets affected schema state, and then falls through to `vdbe_return`. The return path accounts for remaining profile cycles, runs the progress callback if pending, updates `SQLITE_STMTSTATUS_VM_STEP`, releases btree mutexes with `sqlite3VdbeLeave()` when locks were held, and returns the final `rc`. Dedicated labels set messages and result codes for oversized values, OOM, and interrupts before reusing the common abort path.

## State And Persistence Behavior

- Trigger/subprogram state is persistent across nested calls through `VdbeFrame`. Parent `aMem`, `apCsr`, `aOp`, `nMem`, `nCursor`, `lastRowid`, `nChange`, `db->nChange`, and auxdata are saved so execution can later unwind without losing parent VM state.
- `OP_Param` does not deep-copy trigger values. It creates an ephemeral shallow copy, so the parent frame must outlive the child register use.
- Foreign-key counters live partly on the `sqlite3` connection and partly on the running `Vdbe`. Deferred violations can persist across statement boundaries until transaction commit, while immediate counters are statement-scoped unless `SQLITE_DeferFKs` redirects them.
- Autoincrement maximum tracking intentionally reaches the root frame from nested trigger execution, preserving a single maximum value for the outer statement.
- Aggregate contexts are allocated on first execution and cached in the mutable opcode `P4` union as `P4_FUNCCTX`; the opcode itself is rewritten to `OP_AggStep1`. This is persistent bytecode state within the prepared statement.
- Aggregate step state is stored in `Mem` cells flagged for aggregate use. Finalization or value extraction can allocate result memory, change encodings, and set errors returned by SQL function callbacks.
- WAL checkpoint, journal mode, vacuum, incremental vacuum, max page count, and page-count opcodes read or mutate database-file state through pager and btree APIs. `OP_JournalMode` can change persistent file format version when entering or leaving WAL.
- `OP_Expire` mutates prepared-statement validity state. It can expire all statements on a connection or mark only the current VDBE as expiring after completion.
- Cursor pin/unpin and shared-cache table locks affect concurrent access state in btree cursors and shared-cache locking, but do not by themselves write database pages.
- Virtual-table opcodes call extension-provided methods that may allocate cursors, write external storage, update database-like state outside SQLite's pager, set error messages, and choose rowids. `OP_VDestroy` increments `db->nVDestroy` around module destruction for nested-state tracking.
- `db->lastRowid`, `p->nChange`, `p->errorAction`, and `db->vtabOnConflict` are updated around virtual-table updates so module callbacks integrate with SQLite row-change semantics and conflict handling.
- Scalar function calls may retain auxdata across invocations based on the `P1` constant-argument bitmask; on function errors this chunk deletes selected auxdata for the opcode.
- Subtype opcodes mutate only in-memory `Mem` flags and subtype bytes. They are visible to later subtype-aware functions but are not persisted unless a function serializes them elsewhere.
- Bloom filters are stored as blob registers. `OP_FilterAdd` mutates the blob bytes in place, and `OP_Filter` updates statement-status counters but does not affect query correctness if it conservatively falls through.
- Trace callbacks, debug traces, statement counters, profile cycles, scanstatus cycles, and VM-step counters mutate connection or VDBE instrumentation state used by tests and APIs such as `sqlite3_stmt_status()`.

## Dependencies And Integration Points

- The chunk depends on core VDBE types and helpers: `Vdbe`, `VdbeFrame`, `VdbeCursor`, `VdbeOp`, `Mem`, `FuncDef`, `sqlite3_context`, `ValueList`, `out2Prerelease()`, `memAboutToChange()`, `REGISTER_TRACE`, `UPDATE_MAX_BLOBSIZE`, `VdbeBranchTaken`, and the shared jump labels in `sqlite3VdbeExec()`.
- Trigger integration depends on `SQLITE_OMIT_TRIGGER`, `OP_Program`, `sqlite3VdbeFrameMemDel`, `VdbeFrameMem()`, and debug-only `SQLITE_FRAME_MAGIC` checks.
- Foreign-key and autoincrement behavior is conditionally compiled behind `SQLITE_OMIT_FOREIGN_KEY` and `SQLITE_OMIT_AUTOINCREMENT`.
- Function execution integrates with SQLite's application-defined function API through `sqlite3_context`, `FuncDef.xSFunc`, `FuncDef.xInverse`, `sqlite3VdbeMemFinalize()`, `sqlite3VdbeMemAggValue()`, `sqlite3_result_*` side effects on `pCtx->pOut`, auxdata lifetime, and collation skip flags.
- WAL and pager behavior depends on `sqlite3Checkpoint()`, `sqlite3PagerGetJournalMode()`, `sqlite3PagerOkToChangeJournalMode()`, `sqlite3PagerWalSupported()`, `sqlite3PagerCloseWal()`, `sqlite3PagerSetJournalMode()`, `sqlite3JournalModename()`, and pager journal-mode constants.
- Btree integration includes `sqlite3BtreePager()`, `sqlite3BtreeHoldsMutex()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeSetVersion()`, `sqlite3BtreeIncrVacuum()`, `sqlite3BtreeLastPage()`, `sqlite3BtreeMaxPageCount()`, `sqlite3BtreeCursorPin()`, `sqlite3BtreeCursorUnpin()`, `sqlite3BtreeLockTable()`, and optional `sqlite3BtreeCursorHint()`.
- Vacuum integration depends on `sqlite3RunVacuum()` and is omitted when vacuum or attached databases are unavailable.
- Shared-cache locking is compiled behind `SQLITE_OMIT_SHARED_CACHE` and respects `SQLITE_ReadUncommit` for read locks.
- Virtual-table integration is behind `SQLITE_OMIT_VIRTUALTABLE` and relies on `VTable`, `Table`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, `sqlite3_module`, `sqlite3VtabBegin()`, `sqlite3VtabCallCreate()`, `sqlite3VtabCallDestroy()`, `sqlite3VtabLock()`, `sqlite3VtabUnlock()`, `sqlite3VtabImportErrmsg()`, `sqlite3VdbeValueListFree()`, and all relevant module callbacks.
- Trace integration depends on `SQLITE_OMIT_TRACE`, `SQLITE_OMIT_DEPRECATED`, `SQLITE_USE_FCNTL_TRACE`, `sqlite3VdbeExpandSql()`, `sqlite3_file_control()`, `SQLITE_TRACE_STMT`, `SQLITE_TRACE_LEGACY`, and debug `SQLITE_SqlTrace`.
- Debug and profiling integrations depend on `SQLITE_DEBUG`, `NDEBUG`, `VDBE_PROFILE`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_CURSOR_HINTS`, opcode property tables, and debug-only helpers such as `sqlite3VdbeAssertAbortable()` and `registerTrace()`.
- The common exit path integrates with connection-level interruption, progress callbacks, system-error reporting, schema reset, btree mutex release, and VDBE halt semantics through `sqlite3SystemError()`, `sqlite3VdbeLogAbort()`, `sqlite3VdbeHalt()`, `sqlite3OomFault()`, `sqlite3ResetOneSchema()`, `sqlite3VdbeLeave()`, and `db->xProgress`.

## Risks And Edge Cases

- The `OP_Program` frame switch mutates the active interpreter arrays. Any mismatch in frame sizing, cursor count, or auxdata ownership can corrupt parent execution when nested triggers return.
- `OP_Param` relies on shallow ephemeral copies from parent registers. Incorrect lifetime assumptions around parent frame memory would expose stale pointers to trigger bytecode.
- Foreign-key counters are split across multiple fields and mode flags. Bugs in counter routing can make immediate constraints behave deferred, or make deferred violations disappear before commit.
- `OP_MemMax` intentionally climbs to the root frame. A local-frame update would break autoincrement behavior in trigger bodies that insert rows.
- LIMIT/OFFSET overflow is intentionally mapped to the no-limit sentinel `-1`. This preserves historical behavior but means arithmetic overflow does not terminate loops early.
- Aggregate contexts are stored by rewriting opcode state. Prepared statements reused across executions depend on this cached context being reset/freed by VDBE teardown code outside this chunk.
- Window inverse calls assert in debug builds that a step call happened first. Release builds depend on bytecode generation maintaining the same invariant.
- Function and virtual-table callbacks are extension code. They can return errors, set malformed messages, allocate large values, or mutate connection state during VDBE execution.
- `OP_JournalMode` contains sensitive transaction-state checks for WAL transitions. Allowing WAL changes inside a transaction or while multiple readers exist could violate pager locking and file-format assumptions.
- Leaving WAL mode can checkpoint/delete WAL files and may leave exclusive locks. Error recovery must keep the output journal mode consistent with the actual pager mode.
- Virtual-table `OP_VUpdate` increments `p->nChange` in the non-constraint path even for module-defined behavior. Modules must return accurate constraint codes and set `bConstraint` correctly for conflict handling to match SQL expectations.
- `OP_VRename` temporarily forces `SQLITE_LegacyAlter`; failure to restore flags on all paths would leak altered ALTER TABLE semantics. In this code the flag is restored after `xRename()` only when `isLegacy==0`, before aborting on `rc`.
- `OP_VNext` notes that virtual-table implementations may defer errors until a later `xColumn` or other method. Tests that only exercise iteration may miss module-level error propagation bugs.
- Scalar function auxdata deletion on error uses the opcode's constant-argument mask. Incorrect `P1` masks from code generation can leak auxdata or discard reusable auxdata too aggressively.
- Bloom-filter false positives would be correctness bugs because they cause a jump that should not occur; false negatives only reduce performance. Hashing and bit addressing must remain deterministic over the same register representation.
- `OP_Init` mutates `OP_Once` state using a threshold reset. Any code that manually edits `OP_Once` operands must preserve this epoch mechanism for statement reuse.
- The common error path maps the final return to `SQLITE_ERROR` after storing detailed `p->rc`. Callers must inspect VDBE state when they need the specific root cause.
- Progress callbacks are checked on return as well as during execution. A callback interrupt at the return path jumps back into error handling, so code near `vdbe_return` must remain reentrant with respect to `abort_due_to_error`.

## Test Signals

- Trigger tests should cover nested triggers that read `old.*` and `new.*`, exercise multiple executions of the same subprogram, and verify parent `last_insert_rowid()`, change counts, and auxdata survive frame switches.
- Foreign-key tests should cover immediate constraints, deferred constraints, `PRAGMA defer_foreign_keys`, nested trigger effects, and `OP_FkIfZero` branches at statement and transaction boundaries.
- Autoincrement tests should insert from trigger bodies and verify the outer statement updates `sqlite_sequence` using the maximum rowid seen in root-frame tracking.
- LIMIT/OFFSET tests should cover positive, zero, negative, and near-`INT64_MAX` limit/offset combinations, including overflow behavior that maps to no-limit execution.
- Aggregate/window tests should cover first-use context allocation, statement reuse, aggregate errors, collation skip flags, `xValue`, `xInverse`, and finalization of an aggregate whose step function never ran.
- WAL/journal pragma tests should cover checkpoint result registers, busy checkpoints, rollback-mode transitions, WAL entry and exit, temp databases, VFS without shared-memory support, and attempts to change WAL mode inside transactions.
- Vacuum tests should exercise full vacuum with and without an output filename and incremental vacuum completion versus continued work.
- Statement-expiration tests should verify schema changes expire either all statements or only the current statement according to `P1/P2`.
- Shared-cache tests should cover read-uncommitted read-lock suppression, write locks, locked-table error messages, and builds with shared cache omitted.
- Virtual-table tests should cover open/filter/eof/column/next/update/rename/destroy/integrity flows, module error-message import, constraint conflict modes (`OE_Ignore`, `OE_Replace`, `OE_Fail`, `OE_Rollback`, `OE_Abort`), `sqlite3_vtab_nochange()`, `sqlite3_vtab_in_first/next()` via `ValueList`, and last-rowid updates.
- Scalar-function tests should cover deterministic and non-deterministic function paths, subtype get/set/clear behavior, auxdata reuse and deletion, oversized return values, encoding conversion, and error returns from application-defined functions.
- Bloom-filter tests should verify that `OP_FilterAdd` followed by matching `OP_Filter` falls through, missing keys jump, and `SQLITE_STMTSTATUS_FILTER_HIT/MISS` counters move as expected.
- Trace/init tests should cover legacy and v2 trace callbacks, nested VDBE execution trace text, file-control tracing, SQL debug trace output, `OP_Once` reset threshold behavior, and `SQLITE_STMTSTATUS_RUN`.
- Debug builds should exercise `OP_CursorHint`, `OP_Abortable`, and `OP_ReleaseReg` with assertions enabled to catch stale register use and unsafe abort points.
- Error-path tests should inject OOM, interrupt, progress-callback interruption, corrupt-schema reset, virtual-table callback errors, and function callback errors, then verify `p->rc`, user-visible error text, VM halt state, and btree mutex release.
