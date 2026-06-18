# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 45049-52795

## Scope

This chunk spans the tail of SQLite's public VDBE API layer, SQL trace expansion, and the beginning-to-middle of the VDBE interpreter. It starts with statement finalization/reset and value/result helpers, then covers host-parameter binding, column extraction, statement metadata, `sqlite3_step()` execution, and the opcode implementations from `OP_Goto` through the start of `OP_VNext`. The requested range ends inside `OP_VNext`; virtual-table iteration completion and later VDBE halt/error epilogue code are outside this chunk.

## Purpose

The code connects public `sqlite3_stmt`, `sqlite3_value`, and `sqlite3_context` APIs to the internal `Vdbe` and `Mem` representations, then interprets compiled SQL bytecode. Its main responsibilities are:

- Manage a prepared statement's lifecycle: finalize, reset, clear bindings, step, reprepare on schema changes, expose statement metadata/status, and iterate statements on a connection.
- Convert values between SQLite storage classes and C API views, including UTF-8/UTF-16 text, blobs, integers, doubles, nulls, zeroblobs, and numeric affinity.
- Provide user-defined scalar/aggregate function result APIs, aggregate contexts, auxiliary data caches, collation context, and function error reporting.
- Bind host parameters and track whether changed bindings require automatic reprepare because query-plan-sensitive parameters changed.
- Execute VDBE opcodes for expression evaluation, row production, record encode/decode, B-tree cursor navigation, table/index mutations, transaction/savepoint control, schema maintenance, rowsets, triggers, foreign keys, aggregates, WAL/journal pragmas, vacuum, shared-cache locks, and virtual table callbacks.

## Important APIs, Types, and Functions

- Public statement APIs:
  - `sqlite3_finalize()` calls `sqlite3VdbeFinalize()` under the connection mutex and treats NULL as `SQLITE_OK`.
  - `sqlite3_reset()` calls `sqlite3VdbeReset()`, then `sqlite3VdbeMakeReady()` to return the VM to its initial executable state.
  - `sqlite3_clear_bindings()` releases every `Vdbe.aVar[]` `Mem`, sets it to NULL, and expires v2 statements if any parameter is plan-sensitive.
  - `sqlite3_step()` is the top-level C API wrapper around `sqlite3Step()`, with a bounded schema-reprepare loop.

- Value and result APIs:
  - `sqlite3_value_blob/text/text16/bytes/double/int/int64/type()` read from internal `Mem` cells and may expand zeroblobs or convert encodings.
  - `sqlite3_result_blob/text/text16/double/int/int64/null/value/zeroblob/error*()` write the function result into `sqlite3_context.s`, using `setResultStrOrError()` to translate oversized string/blob results into `SQLITE_TOOBIG`.
  - `sqlite3_result_error_nomem()` marks both the context error and `db->mallocFailed`, which is later observed by VDBE execution.

- User function context APIs:
  - `sqlite3_user_data()` and `sqlite3_context_db_handle()` expose `FuncDef.pUserData` and the owning `sqlite3 *`.
  - `sqlite3_aggregate_context()` allocates persistent per-group memory in `pCtx->pMem` and marks it `MEM_Agg`.
  - `sqlite3_get_auxdata()`/`sqlite3_set_auxdata()` manage per-argument auxiliary values in `VdbeFunc.apAux[]`, including destructor invocation on replacement or failed allocation.
  - `sqlite3InvalidFunction()` is a placeholder function body used for names that resolve but must be implemented by virtual-table overload resolution.

- Column and binding APIs:
  - `columnMem()` validates `pResultSet` and column bounds, returning a static NULL `Mem` and setting `SQLITE_RANGE` for invalid access.
  - `sqlite3_column_*()` wrappers call the corresponding `sqlite3_value_*()` conversion and then `columnMallocFailure()` so conversion allocation failures affect subsequent step/reset/finalize behavior.
  - `columnName()` reads display names, decltypes, and optional origin metadata from `Vdbe.aColName[]` with the right name slot (`COLNAME_NAME`, `COLNAME_DECLTYPE`, `COLNAME_DATABASE`, `COLNAME_TABLE`, `COLNAME_COLUMN`).
  - `vdbeUnbind()` enforces that binding happens only on idle statements, validates 1-based parameter indices, clears the old `Mem`, updates `db` error state, and marks statements expired when `expmask` says a new value may change the plan.
  - `bindText()` centralizes blob/text binding, destructor handling, encoding conversion, and error propagation.
  - `createVarMap()`, `sqlite3_bind_parameter_name()`, and `sqlite3VdbeParameterIndex()` derive named-parameter mappings from `OP_Variable` opcodes.
  - `sqlite3TransferBindings()` moves `Mem` bindings between two statements on the same connection; the deprecated public wrapper checks parameter-count equality and expires both statements if needed.

- VDBE support routines:
  - `doWalCallbacks()` runs registered WAL callbacks after successful statement completion.
  - `sqlite3VdbeExpandSql()` renders trace SQL with host parameters substituted as SQL literals when not nested, or comments out raw SQL when VDBE execution is nested.
  - `sqlite3VdbeMemStoreType()`, `applyNumericAffinity()`, `applyAffinity()`, `sqlite3_value_numeric_type()`, and `sqlite3ValueApplyAffinity()` maintain the public storage-class view of `Mem` cells.
  - `allocateCursor()` stores `VdbeCursor` allocations in high-numbered `Mem` registers, optionally embedding a `BtCursor` and column type/offset arrays.
  - `importVtabErrMsg()` transfers `sqlite3_vtab.zErrMsg` into `Vdbe.zErrMsg`.

## Control Flow

`sqlite3_step()` enters `db->mutex`, calls `sqlite3Step()`, and if it sees `SQLITE_SCHEMA`, tries `sqlite3Reprepare()` up to five times before returning the final API-masked code. `sqlite3Step()` performs automatic reset for already-completed statements unless `SQLITE_OMIT_AUTORESET` restores legacy misuse behavior. On first execution it resets interruption state when no other VDBE is active, increments active/write VM counters, optionally starts profiling, and dispatches to `sqlite3VdbeExec()` or `sqlite3VdbeList()` for explain output. `SQLITE_DONE` runs WAL callbacks, and v2-prepared statements return the richer stored `p->rc` on errors.

`sqlite3VdbeExec()` is a tight interpreter loop over `p->aOp[pc]`. Before the switch it enters all required B-tree mutexes, resets result-set state, initializes progress callback accounting, and optionally emits debug listings. Each iteration checks allocation failure, optional test interrupts, progress callbacks, and operand pre-release flags. Many opcodes update `pc` directly for jumps; row-producing `OP_ResultRow` sets `p->pResultSet`, stores public types on output registers, closes any statement transaction used by `SQLITE_CountRows`, sets `p->pc = pc + 1`, returns `SQLITE_ROW`, and exits through the shared return path outside this chunk.

The opcode groups in this range are:

- Control and constants: `OP_Goto`, `OP_Gosub`, `OP_Return`, `OP_Yield`, `OP_HaltIfNull`, `OP_Halt`, `OP_Integer`, `OP_Int64`, `OP_Real`, `OP_String8`, `OP_String`, `OP_Null`, `OP_Blob`, `OP_Variable`, `OP_Move`, `OP_Copy`, `OP_SCopy`, `OP_ResultRow`.
- Expression evaluation: concatenation, arithmetic, bit operations, casts, numeric/text affinity, boolean logic, null tests, comparison (`OP_Lt` through `OP_Ge`), vector comparison (`OP_Permutation`, `OP_Compare`, `OP_Jump`), scalar function invocation, and collation selection.
- Record and row access: `OP_Column`, `OP_Affinity`, `OP_MakeRecord`, `OP_RowData`/`OP_RowKey`, `OP_Rowid`, `OP_NullRow`.
- B-tree cursor and index operations: `OP_OpenRead`, `OP_OpenWrite`, `OP_OpenEphemeral`, `OP_OpenAutoindex`, `OP_OpenPseudo`, `OP_Close`, `OP_Seek*`, `OP_Seek`, `OP_Found`, `OP_NotFound`, `OP_IsUnique`, `OP_NotExists`, `OP_Sequence`, `OP_NewRowid`, `OP_Insert`, `OP_InsertInt`, `OP_Delete`, `OP_ResetCount`, `OP_Last`, `OP_Sort`, `OP_Rewind`, `OP_Next`, `OP_Prev`, `OP_IdxInsert`, `OP_IdxDelete`, `OP_IdxRowid`, `OP_IdxGE`, `OP_IdxLT`.
- Transaction and schema operations: `OP_Count`, `OP_Savepoint`, `OP_AutoCommit`, `OP_Transaction`, `OP_ReadCookie`, `OP_SetCookie`, `OP_VerifyCookie`, `OP_Destroy`, `OP_Clear`, `OP_CreateTable`, `OP_CreateIndex`, `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_DropTable`, `OP_DropIndex`, `OP_DropTrigger`, `OP_IntegrityCk`.
- Higher-level runtime features: `OP_RowSetAdd`, `OP_RowSetRead`, `OP_RowSetTest`, `OP_Program`, `OP_Param`, `OP_FkCounter`, `OP_FkIfZero`, `OP_MemMax`, integer branch opcodes, `OP_AggStep`, `OP_AggFinal`, `OP_Checkpoint`, `OP_JournalMode`, `OP_Vacuum`, `OP_IncrVacuum`, `OP_Expire`, `OP_TableLock`, and virtual-table opcodes from `OP_VBegin` through the beginning of `OP_VNext`.

## State and Persistence Behavior

The persistent runtime state is mostly on `sqlite3`, `Vdbe`, `VdbeCursor`, `Mem`, and the B-tree/pager layers:

- Statement lifecycle fields such as `Vdbe.magic`, `pc`, `rc`, `expired`, `isPrepareV2`, `readOnly`, `pResultSet`, `zErrMsg`, `aCounter[]`, `nChange`, and binding array `aVar[]` determine public API behavior across calls.
- Connection-level counters and flags such as `activeVdbeCnt`, `writeVdbeCnt`, `autoCommit`, `isTransactionSavepoint`, `nSavepoint`, `nStatement`, `nDeferredCons`, `lastRowid`, `mallocFailed`, `errCode`, `u1.isInterrupted`, and callbacks are mutated by stepping, transaction opcodes, row modification opcodes, and error paths.
- `Mem` flags (`MEM_Null`, `MEM_Int`, `MEM_Real`, `MEM_Str`, `MEM_Blob`, `MEM_Zero`, `MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_RowSet`, `MEM_Agg`, `MEM_Frame`) encode ownership, storage class, and runtime object type. Many opcodes deliberately shallow-copy or deep-copy these cells and must keep ownership flags correct.
- Record persistence uses SQLite's serial record format: `OP_MakeRecord` writes a varint header of serial types followed by field bytes, while `OP_Column` parses and caches type/offset arrays in `VdbeCursor`.
- Table and index persistence is through `sqlite3Btree*` APIs. `OP_Insert`, `OP_Delete`, `OP_IdxInsert`, `OP_IdxDelete`, `OP_Clear`, `OP_Destroy`, and `OP_Create*` mutate database B-trees; `OP_Transaction`, `OP_Savepoint`, `OP_AutoCommit`, `OP_JournalMode`, `OP_Checkpoint`, `OP_Vacuum`, and `OP_IncrVacuum` affect transaction, journal, WAL, and vacuum state.
- Schema persistence and in-memory schema state are coordinated by cookie reads/writes and schema mutation opcodes. `OP_VerifyCookie` expires statements and resets in-memory schema on cookie mismatch; `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_Drop*`, and `OP_Expire` update or invalidate schema-derived state.
- Trigger execution persists a call stack in `VdbeFrame` objects stored inside `MEM_Frame` registers. `OP_Program` swaps the active register/cursor/opcode arrays to the subprogram and restores later in `OP_Halt` outside this range's main entry point.
- Virtual table state is externalized through module cursors and callbacks. The interpreter sets `p->inVtabMethod` around selected calls to avoid unsafe schema invalidation and imports module error messages back into the VDBE.

## Dependencies and Integration Points

- Mutexing and thread-safety depend on `sqlite3_mutex_enter/leave`, `sqlite3VdbeMutexArrayEnter()`, and B-tree shared mutex helpers. Several opcodes assume the prepare path has declared B-tree usage in `p->btreeMask`.
- Memory management depends on `sqlite3DbMalloc*`, `sqlite3DbRealloc`, `sqlite3DbFree`, `sqlite3VdbeMemGrow`, `sqlite3VdbeMemRelease*`, `sqlite3VdbeMemMove`, and API-exit handling through `sqlite3ApiExit()`.
- Parser/code-generator contracts are encoded directly in opcode comments and assertions: operand flags, register ranges, `P4` union type (`P4_KEYINFO`, `P4_INT32`, `P4_FUNCDEF`, `P4_VDBEFUNC`, `P4_COLLSEQ`, `P4_MEM`, `P4_SUBPROGRAM`), and opcode ordering assumptions such as `OP_SeekLt` through `OP_SeekGt`.
- B-tree and pager integration includes cursor movement/fetching, transaction begin/statement begin/savepoint, root-page creation/drop/clear, autovacuum root moves, WAL checkpoint/close/set-version paths, journal mode switching, and table locks under shared cache.
- User-defined function integration flows through `FuncDef`, `sqlite3_context`, `sqlite3_value`, `VdbeFunc`, collation (`OP_CollSeq`), scalar `xFunc`, aggregate `xStep`/finalizer, and destructor semantics for result and auxdata ownership.
- Callback integration includes WAL hooks, profile callbacks, progress callbacks, update hooks, trace SQL expansion, and virtual-table module methods (`xBegin`, `xCreate`, `xDestroy`, `xOpen`, `xFilter`, `xColumn`, partial `xNext` setup).
- Compile-time feature gates materially change behavior: UTF-16, floating point, casts, trace, explain, deprecated APIs, WAL, pragma, vacuum/attach, autovacuum, analyze, integrity check, trigger, foreign key, autoincrement, shared-cache, virtual tables, test instrumentation, and debug/profile support.

## Risks and Edge Cases

- Binding while a statement is busy is explicit misuse. `vdbeUnbind()` logs this and returns `SQLITE_MISUSE_BKPT`; callers that pass custom destructors still need the destructor path to run on failed text/blob binding.
- Column accessor conversions can allocate after a row has been produced. `columnMallocFailure()` must convert `db->mallocFailed` into statement `SQLITE_NOMEM`; otherwise later `sqlite3_step()`/`finalize()` would hide conversion failure.
- `OP_Column` is a high-risk corruption boundary. It limits oversized headers, minimizes allocation for corrupt records, handles short records by returning NULL or a default `P4_MEM`, and validates header/data offsets before deserializing.
- `Mem` ownership flags are subtle. `OP_SCopy`, `OP_Copy`, `OP_ResultRow`, `OP_Function`, `OP_VColumn`, `OP_MakeRecord`, and `OP_Column` must avoid dangling ephemeral pointers, double frees, or losing dynamic allocations.
- Transaction opcodes reject commits, rollbacks, savepoint operations, and WAL mode transitions when other statements are active in incompatible ways. Mistakes here can produce overlapping statement transactions, locks held across callbacks, or inconsistent `autoCommit` state.
- `OP_NewRowid` has multiple edge cases: cached rowid use, `MAX_ROWID`, random rowid fallback, AUTOINCREMENT ceiling enforcement, root-frame register updates, and `SQLITE_FULL` after repeated random collisions.
- Schema-cookie handling deliberately treats normal SQL and virtual-table method execution differently to avoid invalidating a virtual table structure while its module is running prepared statements internally.
- Virtual table callbacks are external code. The interpreter imports module error strings, sets `inVtabMethod`, and must clean up cursors on allocation failure; module misuse or reentrancy can still surface as `SQLITE_LOCKED`, callback errors, or malloc state.
- `sqlite3VdbeExpandSql()` renders values for tracing and must avoid mis-tokenizing parameters inside comments, strings, and quoted identifiers. It also emits blob hex and escaped text, so length limits and encoding conversion failures matter.
- This chunk ends before the shared VDBE error labels (`no_mem`, `too_big`, `abort_due_to_error`, `vdbe_return`) and before completing `OP_VNext`; those paths are essential for full lifecycle analysis but are not in the requested range.

## Test Signals

- Public API behavior: finalizing/resetting NULL statements, resetting after `SQLITE_ROW`/`SQLITE_DONE`, clearing bindings, binding out-of-range indexes, binding while busy, parameter name/index lookup, binding transfer, statement readonly/status counters, and `sqlite3_next_stmt()` iteration.
- Value conversion: UTF-8/UTF-16 text accessors, blob/zeroblob expansion, numeric affinity, casts, arithmetic overflow fallback to floating point, divide/remainder by zero returning NULL, NaN to NULL, and string/blob length limit failures.
- Function APIs: scalar result setters, oversized result to `SQLITE_TOOBIG`, `sqlite3_result_error_nomem()`, aggregate context allocation and reuse, aggregate finalization, auxdata destructor order, collation-sensitive functions, and invalid overloaded functions.
- Step execution: autorereset compatibility, schema-change reprepare limit, profile/progress callback firing, interrupt handling, WAL callback invocation after `SQLITE_DONE`, and API error masking.
- Record/cursor behavior: `OP_MakeRecord`/`OP_Column` round trips, corrupt record detection, short record defaults, rowdata/rowkey reads, pseudo-table column extraction, deferred seek, and cursor cache invalidation after movements or writes.
- Persistence operations: read/write transaction start, statement journal creation, savepoint begin/release/rollback, autocommit commit/rollback busy cases, insert/update/delete hooks, row count changes, root page create/drop/clear, schema cookie verify/set, pragma journal mode transitions, WAL checkpoint result registers, vacuum/incremental vacuum, and shared-cache table locks.
- Query execution opcodes: comparison with collations and NULL flags, vector compare/permutation, rowset duplicate suppression, trigger recursion limit and `old/new` parameter copying, foreign-key counters, AUTOINCREMENT max tracking, and aggregate step/final error propagation.
- Virtual table behavior in this range: `xBegin`, `xCreate`, `xDestroy`, `xOpen`, `xFilter`, `xColumn`, error-message import, empty-filter jump, null-row handling, and setup for `xNext` in `OP_VNext` with the remaining body covered by the next chunk.
