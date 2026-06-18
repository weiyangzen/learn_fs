# Research: subset-b-008803

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbe.h -->
# sources/storage-engines/sqlite/src/vdbe.h

## Purpose

`vdbe.h` is the main non-public interface for building and managing SQLite VDBE bytecode programs. It keeps `Vdbe` itself opaque, but exposes the opcode representation, P4 operand ownership rules, trigger subprogram representation, code-generation helpers, bytecode patching helpers, lifecycle entry points, record comparison interfaces, and optional instrumentation hooks used by the parser, code generator, executor, explain, scanstatus, and tests.

The file sits between SQL compilation and VDBE execution. Parser/codegen modules include it to allocate a VM, append opcodes, attach typed P4 payloads, resolve labels, mark database dependencies, finalize a statement into runnable form, and later reset/finalize/delete it. Execution details and concrete runtime state live in `vdbeInt.h` and companion `.c` files.

## Important APIs, Types, and Constants

`typedef struct Vdbe Vdbe` intentionally hides the VM layout from most code. The file forward-declares `Mem`, `SubProgram`, and `SubrtnSig` because opcode payloads refer to those internal structures without exposing their full definitions here.

`SubrtnSig` describes a reusable subroutine used to materialize the right-hand side of an `IN` expression. It records the RHS SELECT id, completion flag, affinity string, generated ephemeral table, entry address, and return-register slot. The reusable-subroutine contract is stateful: codegen can share a coded RHS only after `bComplete` is true and the stored address/table/register fields are valid.

`VdbeOp` is the bytecode instruction format: `opcode`, `p1`, `p2`, `p3`, `p4`, and `p5`. `p2` is commonly a jump destination. `p4` is a tagged union whose meaning is controlled by `p4type`, and may hold integers, strings, functions, collations, `Mem`, virtual tables, `KeyInfo`, integer arrays, subprograms, schema objects, or cursor-hint expressions. Optional fields add explain comments, VDBE coverage source locations, and execution/cycle counters.

`SubProgram` stores trigger or subprogram bytecode, memory/cursor requirements, `OP_Once` state, a recursion token, and a linked-list pointer used to track visited subprograms. `VdbeOpList` is a compact literal opcode form for bulk insertion via `sqlite3VdbeAddOpList()`.

`P4_*` constants define both type and ownership semantics. Values above `P4_FREE_IF_LE` do not own resources. Values at or below it require cleanup by VDBE code. This boundary is a high-risk API contract because changing a `p4type` can silently turn a borrowed pointer into an owned allocation or vice versa.

`COLNAME_*` constants define the layout of `Vdbe.aColName`: result name, declaration type, database, table, and source column. `COLNAME_N` varies with `SQLITE_ENABLE_COLUMN_METADATA` and `SQLITE_OMIT_DECLTYPE`, so code that indexes `aColName` must use the macros rather than hard-coded counts.

`ADDR(X)` maps unresolved labels returned by `sqlite3VdbeMakeLabel()` into `Parse.aLabel[]` indexes. `opcodes.h` is generated from VDBE sources and supplies opcode numbers.

The prototypes cluster into these groups:

- Bytecode allocation/emission: `sqlite3VdbeCreate()`, `sqlite3VdbeAddOp0..4()`, `sqlite3VdbeAddOp4Dup8()`, `sqlite3VdbeAddOp4Int()`, `sqlite3VdbeAddFunctionCall()`, `sqlite3VdbeAddOpList()`, `sqlite3VdbeLoadString()`, `sqlite3VdbeMultiLoad()`, and coroutine helpers.
- Bytecode patching and labels: `sqlite3VdbeChangeOpcode()`, `sqlite3VdbeChangeP1/P2/P3/P5/P4()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeJumpHereOrPopInst()`, `sqlite3VdbeChangeToNoop()`, `sqlite3VdbeDeletePriorOpcode()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeCurrentAddr()`, and `sqlite3VdbeMakeLabel()`.
- Statement lifecycle: `sqlite3VdbeMakeReady()`, `sqlite3VdbeFinalize()`, `sqlite3VdbeReset()`, `sqlite3VdbeResetStepResult()`, `sqlite3VdbeRewind()`, `sqlite3VdbeDelete()`, `sqlite3VdbeRunOnlyOnce()`, `sqlite3VdbeReusable()`, `sqlite3VdbeTakeOpArray()`, and `sqlite3VdbeSwap()`.
- Statement metadata: `sqlite3VdbeSetNumCols()`, `sqlite3VdbeSetColName()`, `sqlite3VdbeSetSql()`, `sqlite3VdbeDb()`, `sqlite3VdbePrepareFlags()`, and optional normalized-SQL double-quote tracking.
- Runtime values and records: `sqlite3VdbeGetBoundValue()`, `sqlite3VdbeSetVarmask()`, `sqlite3MemCompare()`, `sqlite3BlobCompare()`, record unpack/compare functions, `sqlite3VdbeAllocUnpackedRecord()`, `sqlite3VdbeFindCompare()`, and `sqlite3MemSetArrayInt64()`.
- Subprograms and dependencies: `sqlite3VdbeLinkSubProgram()`, `sqlite3VdbeHasSubProgram()`, `sqlite3VdbeUsesBtree()`, `sqlite3VdbeAddParseSchemaOp()`, and `sqlite3VdbeSetP4KeyInfo()`.
- Diagnostics and instrumentation: explain helpers, comments, branch coverage macros, scanstatus registration helpers, opcode printing, cursor-hint validation, and bytecode virtual-table initialization.

## Control Flow

A parser creates a `Vdbe`, emits instructions through `sqlite3VdbeAddOp*()` helpers, uses labels for forward jumps, attaches P4 payloads, annotates explain/coverage/scanstatus metadata, and marks btree dependencies. Once SQL compilation is complete, `sqlite3VdbeMakeReady()` fixes memory/register/cursor requirements and makes the VM runnable. Runtime APIs in `vdbeapi.c` and execution code in `vdbe.c` then step, reset, and finalize the same object through the lifecycle prototypes declared here.

Patching helpers are central to codegen control flow. Many SQL constructs emit placeholder jumps first and call `sqlite3VdbeJumpHere()` or `sqlite3VdbeResolveLabel()` after the destination address is known. `sqlite3VdbeChangeToNoop()` and `sqlite3VdbeDeletePriorOpcode()` support late peephole/codegen corrections.

The instrumentation macros are compile-time no-ops unless their feature flags are enabled. With `SQLITE_VDBE_COVERAGE`, every branch opcode is expected to be tagged so coverage testing can detect untagged or unexercised bytecode branches. With explain comments or scanstatus enabled, extra fields and callbacks tie generated bytecode back to plan output and statement metrics.

## State and Persistence Behavior

This header does not persist data itself. It defines the contracts for in-memory VDBE bytecode and statement metadata. The important stateful contracts are P4 ownership, column-name slot layout, unresolved label encoding, subprogram linkage, saved SQL flags, btree dependency masks, and optional per-op execution counters.

`SQLITE_PREPARE_SAVESQL` is an internal prepare flag that keeps SQL text for automatic reprepare and expanded SQL. `SQLITE_PREPARE_MASK` separates public prepare flags from internal bits. `sqlite3VdbeSetVarmask()` and binding-related support interact with plan invalidation: parameters used in ways that can affect plans are tracked so a later bind can expire the VM.

## Dependencies and Integration Points

`vdbe.h` depends on types from SQLite core headers such as `Parse`, `FuncDef`, `CollSeq`, `VTable`, `KeyInfo`, `Table`, `Index`, `Expr`, `UnpackedRecord`, and `sqlite3_context`. It includes generated `opcodes.h`, so build ordering matters.

The main integration points are parser/codegen modules, `vdbe.c` execution, `vdbeaux.c` lifecycle and bytecode assembly helpers, `vdbemem.c` value handling, `vdbesort.c`, btree/pager dependencies, explain/scanstatus code, bytecode virtual table code, and test-only VDBE coverage plumbing.

## Risks and Edge Cases

The P4 type boundary is the main memory-management risk. Misclassified P4 payloads can leak, double-free, or retain stale pointers. `P4_TABLEREF`, `P4_SUBRTNSIG`, `P4_FUNCCTX`, and other typed pointers require the implementation and cleanup paths to agree exactly.

Conditional compilation changes structure size and behavior. `VdbeOp` gains counters under scanstatus/profile, comments under explain comments, cursor-hint expressions under cursor hints, and source-line coverage under VDBE coverage. Code assuming a stable binary layout across feature sets would be fragile.

Label handling is intentionally encoded with bitwise complement. Passing raw negative labels or resolved addresses to the wrong helper can patch invalid jumps. Column metadata also depends on build options, so indexing `aColName` incorrectly can read the wrong metadata slot.

## Test Signals

Useful tests include SQL statements that produce forward jumps, subroutines, triggers, `IN (SELECT ...)` RHS materialization, explain and explain-query-plan output, scanstatus counters, branch coverage builds with `SQLITE_VDBE_COVERAGE`, normalized SQL builds, and statements whose host-parameter bindings trigger automatic reprepare. Memory tests should stress P4 payload ownership, subprogram deletion, statement finalization, and no-op opcode rewrites.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeInt.h -->
# sources/storage-engines/sqlite/src/vdbeInt.h

## Purpose

`vdbeInt.h` is the private runtime header for SQLite's virtual database engine. It exposes the concrete layouts that are deliberately hidden from the public and semi-public VDBE interface: cursors, frames, memory cells, aggregate/function contexts, auxdata, scanstatus entries, preupdate-hook state, value-list iterators, and the full `Vdbe` statement object.

The header is included by the VDBE implementation files that execute bytecode, manage registers, decode records, call SQL functions, maintain cursor state, run triggers, expose C APIs, and collect statement metrics. It is not a persistence layer, but it defines the in-memory state that controls reads, writes, hooks, errors, and cleanup during a prepared statement's lifetime.

## Important APIs, Types, and Constants

`SQLITE_MAX_SCHEMA_RETRY` limits how many times a statement can be automatically reprepared after `SQLITE_SCHEMA`. `VDBE_DISPLAY_P4` centralizes whether P4 explain-display logic is compiled in.

`VdbeCursor` is the polymorphic cursor wrapper used by opcodes. `eCurType` distinguishes btree, sorter, virtual-table, and pseudo cursors. Shared fields track database index, null-row status, deferred seek state, table/index identity, ephemeral state, ordering, rowid generation, seek hits, cache status, prior seek result, sequence count, and optional column-used masks. The union stores a `BtCursor`, `sqlite3_vtab_cursor`, or `VdbeSorter`; other fields carry `KeyInfo`, root page, parsed record header offsets, payload pointers, decoded serial types, alternate cursor mappings, and optional large text/blob cache state.

`SZ_VDBECURSOR(N)` gives the rounded allocation size for a cursor with at least `N` fields. `IsNullCursor()` identifies null-only pseudo cursors. `CACHE_STALE` forces decoded-column caches invalid.

`VdbeTxtBlbCache` caches a large TEXT or BLOB column for a particular row offset, column, VM cache generation, and column-cache generation. This reduces repeated payload loads from btree pages for expensive column accesses.

`VdbeFrame` captures parent execution state when `OP_Program` enters a trigger/subprogram: parent op array, registers, cursors, once flags, recursion token, last rowid, auxdata, cursor/register counts, program counter, change counters, and child resource counts. Frames are owned by parent memory cells but delayed-free through `Vdbe.pDelFrame` to avoid recursive release paths.

`Mem` (`struct sqlite3_value`) is SQLite's internal SQL value container. It may carry integer, real, string, blob, null, pointer, aggregate, or zero-blob state. The flags split into type bits (`MEM_Null`, `MEM_Str`, `MEM_Int`, `MEM_Real`, `MEM_Blob`, `MEM_IntReal`), modifiers (`MEM_Term`, `MEM_Zero`, `MEM_Subtype`, `MEM_Cleared`, `MEM_FromBind`), and ownership bits (`MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_Agg`). `MEMCELLSIZE` identifies the prefix copied by shallow value duplication.

Helper macros such as `VdbeMemDynamic()`, `MemSetTypeFlag()`, `MemNullNochng()`, `memIsValid()`, and `ExpandBlob()` encode important invariants around dynamic ownership, type replacement, no-change virtual-table values, debug validity, and incremental-blob expansion.

`AuxData` backs `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()`, associating an argument index and opcode with cached extension-owned data plus a destructor.

`sqlite3_context` is the internal function-call context. It stores the output `Mem`, function definition, aggregate memory cell, owning VDBE, opcode index, error code, desired encoding, skip flag, argument count, and argument array.

`ScanStatus` maps explain/loop metadata to opcode counters. It records explain opcode address, up to three opcode address ranges for cycle accounting, loop and visit counter opcode addresses, select id, estimated row count, and object name.

`DblquoteStr` tracks double-quoted string literals for normalized SQL builds.

`Vdbe` is the full prepared-statement object. Major fields include the owning `sqlite3`, statement linked-list pointers, parse context, bind count, register/cursor counts, cache generation, program counter, result code, change counts, current time, foreign-key counters, memory/register arrays, cursor array, bound variables, opcode array, result column metadata, current row, error message, variable-name list, trace start time, result column counts, write/read/explain flags, state enum, btree and lock masks, statement-status counters, saved SQL text, normalized SQL state, subprograms, frame lists, auxdata, and scanstatus array.

`VDBE_INIT_STATE`, `VDBE_READY_STATE`, `VDBE_RUN_STATE`, and `VDBE_HALT_STATE` define the allowed statement lifecycle states.

`PreUpdate` stores state for `sqlite3_preupdate_*()` APIs: current VM, cursor, operation, old record bytes, key info, unpacked old/new records, new-value register, blob-write column, old/new keys, cached old integer primary key, table and primary-key metadata, default-value cache, and inline keyinfo storage.

`ValueList` is passed to virtual tables as a typed pointer for `IN` constraints. It stores a btree cursor over ephemeral RHS values and a reusable output register.

The prototypes cover private VDBE behavior: cursor free/restore/moveto, serial-type handling, auxdata deletion, btree/index comparison, main execution and halt, encoding conversion, `Mem` copy/move/stringify/cast/grow/release/finalize operations, btree-to-Mem reads, frame restore/delete, preupdate hook dispatch, sorter operations, value-list free, write-counter assertions, shared-cache enter/leave, memory invariant checks, FK checks, debug printing, UTF-16 translation, and zeroblob expansion.

## Control Flow

During preparation, `Vdbe` starts in `VDBE_INIT_STATE` and accumulates opcodes, metadata, bind slots, and resource counts. `sqlite3VdbeMakeReady()` transitions it to ready state after allocating registers/cursors and setting execution metadata. `sqlite3_step()` then transitions ready statements to run state, `sqlite3VdbeExec()` interprets `aOp`, and `sqlite3VdbeHalt()`/reset logic returns the statement to halt or ready state.

Bytecode execution mutates `Vdbe.aMem`, `Vdbe.apCsr`, `Vdbe.pc`, `Vdbe.pResultRow`, change counters, foreign-key counters, and error fields. Cursor opcodes keep parsed-record caches in `VdbeCursor` synchronized with `Vdbe.cacheCtr`; deferred seeks allow seek operations to be postponed until data is actually needed.

Trigger and subprogram execution pushes `VdbeFrame` objects. The frame saves parent instruction/register/cursor arrays and counters, swaps in child arrays, then restores parent state when the subprogram returns. Frame deletion is deliberately delayed through `pDelFrame`.

SQL function opcodes populate `sqlite3_context` and `Mem` arguments, then extension code writes results back through result APIs. Aggregate functions keep their context in a `Mem` flagged `MEM_Agg`; auxdata persists on `Vdbe.pAuxData` until invalidated or halted.

Preupdate hooks are transient. DML opcodes populate `PreUpdate`, callbacks may request old/new values, and those APIs lazily unpack records or copy new registers into stable `Mem` arrays before returning pointers.

## State and Persistence Behavior

All structures in this header describe in-memory state. Persistent database effects are performed through btree/pager calls elsewhere, but this header defines the state that decides which btrees are touched (`btreeMask`, `lockMask`), whether a statement writes (`readOnly`, `nWrite`, `usesStmtJournal`), how changes are counted, and how constraints are tracked.

`Mem` ownership flags are persistence-like within a statement lifetime: dynamic strings, aggregates, zero-blobs, ephemeral pointers, and static pointers require different cleanup/copy behavior. The `MEM_FromBind` flag marks host-parameter origin, and `MEM_Null|MEM_Zero` is used as a no-change marker for virtual-table updates.

The cursor cache state (`cacheStatus`, `aOffset`, `aType`, `aRow`, `payloadSize`, `pCache`) persists across opcode executions until invalidated by cache generation changes, cursor movement, or row changes. `iCurrentTime` caches `now` for stable time values within one statement run.

## Dependencies and Integration Points

`vdbeInt.h` ties VDBE execution to most of SQLite core: btree cursors, pagers, virtual tables, sorters, schema objects, `KeyInfo`, unpacked records, parser structures, functions, collations, foreign-key logic, hooks, mutex/shared-cache control, UTF conversion, memory allocation, error handling, and optional scanstatus/profile/debug instrumentation.

It is consumed by `vdbe.c`, `vdbeapi.c`, `vdbeaux.c`, `vdbemem.c`, `vdbesort.c`, `vdbetrace.c`, record comparison logic, preupdate hook logic, virtual table integration, and debug/test builds.

## Risks and Edge Cases

The highest-risk surface is `Mem` flag consistency. Many operations depend on exact combinations of type, subtype, zero-blob, no-change, and ownership bits. Incorrect flag transitions can produce stale text encodings, missed destructors, double frees, invalid pointer values, or wrong SQL type results.

`VdbeCursor` has a split initialization contract: only early fields are zeroed on allocation, while later fields must be individually initialized before use. This saves work but makes new cursor paths sensitive to missed initialization. Flexible-array sizing through `SZ_VDBECURSOR()` must match `nField`.

Deferred frame deletion avoids recursion but means frame-owned resources survive until reset/halt. Bugs here can look like leaks or use-after-free when subprogram registers contain frame destructors.

Build flags change structure fields and APIs. `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, `SQLITE_DEBUG`, `SQLITE_OMIT_FLOATING_POINT`, UTF-16 options, and incremental-blob options all alter behavior. Tests need to cover representative feature matrices.

## Test Signals

Strong coverage comes from statements using btree, sorter, virtual-table, and pseudo cursors; large TEXT/BLOB column reads; deferred seeks; triggers and recursive triggers; aggregate functions and auxdata; pointer-valued SQL functions; virtual-table `xUpdate` no-change markers; `IN` constraints delivered to virtual tables; preupdate hooks for rowid and WITHOUT ROWID tables; foreign-key checks; UTF-16 conversion; zeroblob/incremental blob behavior; scanstatus metrics; and debug builds with memory invariant assertions enabled.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeInt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeapi.c -->
# sources/storage-engines/sqlite/src/vdbeapi.c

## Purpose

`vdbeapi.c` implements public and extension-facing APIs that operate on VDBE-backed prepared statements, SQL values, function contexts, result values, bindings, column accessors, statement metadata, virtual-table helper APIs, preupdate-hook value access, and scanstatus reporting. It is the bridge between SQLite's stable C API and the private `Vdbe`, `Mem`, cursor, frame, and scanstatus structures defined in `vdbeInt.h`.

The file does not implement the bytecode interpreter itself. Instead, it validates API usage, enters the connection mutex, translates C API operations into `Mem` and `Vdbe` state mutations, calls private execution/lifecycle helpers such as `sqlite3VdbeExec()`, `sqlite3VdbeReset()`, `sqlite3VdbeDelete()`, `sqlite3Reprepare()`, `sqlite3VdbeMem*()` functions, and returns public SQLite result codes.

## Important APIs and Functions

Statement lifecycle APIs:

- `sqlite3_finalize()` validates the statement, enters the connection mutex, fires any pending profile callback, resets execution state, deletes the VDBE, exits through `sqlite3ApiExit()`, and handles zombie connection close.
- `sqlite3_reset()` resets a statement to reusable state, rewinds it, fires profile callbacks, and returns the prior execution result.
- `sqlite3_clear_bindings()` releases every bind slot in `Vdbe.aVar`, sets each to NULL, and expires the VM if binding-sensitive plan bits are present.
- Deprecated `sqlite3_expired()` reports whether a statement needs recompile.

Safety and profiling helpers:

- `vdbeSafety()` and `vdbeSafetyNotNull()` detect NULL or finalized statements and log `SQLITE_MISUSE`.
- `invokeProfileCallback()` and `checkProfileCallback()` implement legacy profile and trace-v2 profile callbacks using elapsed VFS time when tracing is enabled.

Value APIs:

- `sqlite3_value_blob/text/text16/bytes/int/int64/double/type/subtype/encoding/nochange/frombind/pointer()` read `Mem` values, converting encodings or expanding zeroblobs as needed.
- `sqlite3_value_dup()` deep-copies string/blob values into an independent heap `sqlite3_value`, strips pointer subtypes from NULL pointer values, and avoids carrying dynamic ownership from the original. `sqlite3_value_free()` releases such copies.

Result APIs:

- `setResultStrOrError()` centralizes string/blob result storage, encoding conversion, length checks, and TOOBIG/NOMEM error propagation.
- `invokeValueDestructor()` calls application destructors for rejected inputs and sets TOOBIG when appropriate.
- `sqlite3_result_blob/blob64/text/text64/text16*()`, numeric/null/pointer/subtype/value/zeroblob result APIs, and error APIs write into `sqlite3_context.pOut`.
- `sqlite3_result_error_code()`, `sqlite3_result_error_toobig()`, and `sqlite3_result_error_nomem()` set `sqlite3_context.isError`, result text/null, debug app result code, and OOM state.
- `sqlite3ResultIntReal()` is a test-only hook to force `MEM_IntReal`.

Stepping APIs:

- `doWalCallbacks()` calls per-database WAL hooks after successful autocommit statement completion.
- `sqlite3Step()` performs the core `sqlite3_step()` state machine: starts ready statements, handles expiration, resets interrupts, starts trace timing, updates active/read/write counters, dispatches explain listing or `sqlite3VdbeExec()`, handles `SQLITE_ROW`, completion, WAL callbacks, saved-SQL error transfer, NOMEM normalization, and public result masking.
- `sqlite3_step()` wraps `sqlite3Step()` with statement validation, mutex entry, automatic schema reprepare up to `SQLITE_MAX_SCHEMA_RETRY`, reset after successful reprepare, and parser-error preservation on failed reprepare.

Function context and virtual-table helpers:

- `sqlite3_user_data()` and `sqlite3_context_db_handle()` expose function registration data and database handle.
- `sqlite3_vtab_nochange()` reports the virtual-table no-change marker in the function output slot.
- `sqlite3VdbeValueListFree()`, `valueFromValueList()`, `sqlite3_vtab_in_first()`, and `sqlite3_vtab_in_next()` implement typed-pointer iteration over ephemeral RHS values for virtual-table `IN` constraints.
- `sqlite3StmtCurrentTime()` caches statement time in `Vdbe.iCurrentTime`.
- `sqlite3_aggregate_context()` and `createAggContext()` allocate or return aggregate state stored in a `MEM_Agg` memory cell.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` manage per-function/per-argument cached auxdata on `Vdbe.pAuxData`, with negative `iArg` acting as statement-wide undocumented cache scope.
- Deprecated `sqlite3_aggregate_count()` returns aggregate step count.

Column APIs:

- `sqlite3_column_count()` and `sqlite3_data_count()` report result shape and current-row availability.
- `columnNullValue()` returns a static aligned NULL `Mem` for invalid accesses.
- `columnMem()` validates row/column availability under mutex and returns either the row cell or static NULL while setting `SQLITE_RANGE`.
- `columnMallocFailure()` converts conversion-time allocation failure into statement `SQLITE_NOMEM` state and releases the mutex.
- `sqlite3_column_blob/bytes/bytes16/double/int/int64/text/text16/value/type()` call matching value APIs over `columnMem()`.
- `columnName()` returns result names, declaration types, origin metadata, or special EXPLAIN/EQP column names with UTF-8/UTF-16 conversion and OOM cleanup. The public `sqlite3_column_name*`, `sqlite3_column_decltype*`, and optional metadata name APIs are thin wrappers.

Binding APIs:

- `vdbeUnbind()` validates statement state, rejects busy statements, checks parameter range, releases the existing bind value, sets NULL, clears db error state, and expires the VM if that parameter affects query planning.
- `bindText()` handles common text/blob binding, destructor ownership, encoding conversion, API-exit error normalization, and mutex release.
- `sqlite3_bind_blob/blob64/double/int/int64/null/pointer/text/text64/text16/value/zeroblob/zeroblob64()` populate `Vdbe.aVar`.
- `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3VdbeParameterIndex()`, and `sqlite3_bind_parameter_index()` expose bind slot metadata via `VList`.
- `sqlite3TransferBindings()` and deprecated `sqlite3_transfer_bindings()` move bind `Mem` values between compatible statements and expire both statements when needed.

Statement metadata APIs:

- `sqlite3_db_handle()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_next_stmt()`, `sqlite3_stmt_status()`, `sqlite3_sql()`, `sqlite3_expanded_sql()`, and optional `sqlite3_normalized_sql()` expose statement ownership, mutability, explain mode, execution state, connection statement list, counters, SQL text, expanded SQL, and normalized SQL.
- `sqlite3_stmt_explain()` can switch modes without reprepare if enough memory and EQP ops are already available; otherwise it reprepares saved SQL.
- `sqlite3_stmt_status(SQLITE_STMTSTATUS_MEMUSED)` uses `sqlite3VdbeDelete()` with `db->pnBytesFreed` and temporarily disables lookaside end pointers to measure memory without actually finalizing in the normal path.

Preupdate and scanstatus APIs:

- With `SQLITE_ENABLE_PREUPDATE_HOOK`, `vdbeUnpackRecord()`, `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()` lazily decode old/new row values for preupdate callbacks, handle rowid versus WITHOUT ROWID mappings, default values for added columns, and update-depth/blob-write metadata.
- With `SQLITE_ENABLE_STMT_SCANSTATUS`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus()`, and `sqlite3_stmt_scanstatus_reset()` expose loop counts, visit counts, estimates, names, explain text, select/parent ids, and cycle counts from `ScanStatus` and per-op counters.

## Control Flow

Most APIs follow a common shape: cast `sqlite3_stmt*` or `sqlite3_value*` to private `Vdbe*`/`Mem*`, validate misuse when API armor is enabled or where required, enter the owning database mutex, mutate or read private state, normalize errors through `sqlite3Error()`/`sqlite3ApiExit()`, and leave the mutex. The file assumes public SQLite threading semantics: prepared-statement operations are serialized by the connection mutex.

`sqlite3_step()` is the central control-flow path. It validates the VDBE, enters the mutex, calls `sqlite3Step()`, and loops only on `SQLITE_SCHEMA`. Reprepare copies compiler errors into the statement if recompilation fails; if recompilation succeeds, reset prepares the statement for another attempt and suppresses duplicate trace-statement emission by setting `minWriteFileFormat` to a sentinel value when appropriate.

`sqlite3Step()` itself enforces VDBE lifecycle transitions. READY statements may become RUN, HALT statements may auto-reset unless legacy `SQLITE_OMIT_AUTORESET` behavior applies, EXPLAIN statements route through `sqlite3VdbeList()`, and normal statements route through `sqlite3VdbeExec()`. `SQLITE_ROW` returns immediately with `pResultRow` populated. Completion clears `pResultRow`, invokes profile callbacks, runs WAL callbacks on autocommit success, and transfers saved-SQL errors.

Binding control flow is careful about mutex ownership. `vdbeUnbind()` enters the mutex and returns with it still held on success so the caller can install the new value atomically. On error it releases the mutex. `bindText()` and scalar bind wrappers must therefore release the mutex only after successful value installation, and must call application destructors themselves if unbind failed before SQLite took ownership.

Column access control flow is the inverse: `columnMem()` enters the mutex and returns a pointer while the mutex is still held; each public column accessor performs conversion and then calls `columnMallocFailure()` to handle OOM and release the mutex. This means every new column accessor must preserve the enter/leave pairing.

Preupdate old/new access lazily decodes data. Old values are unpacked from the btree payload only on first request. New INSERT values are unpacked from the serialized record register only on first request. New UPDATE values are copied into `PreUpdate.aNew` because returning a direct register pointer would let callers mutate encoding/state needed by the running VM.

## State and Persistence Behavior

`vdbeapi.c` mutates statement state but persists no database pages itself. Persistent database changes happen in the bytecode interpreter and btree/pager layers. This file controls when those changes are committed from the API perspective by stepping, resetting, finalizing, invoking WAL callbacks, and surfacing errors.

Important state transitions include `Vdbe.eVdbeState`, `pc`, `rc`, `pResultRow`, `expired`, active/read/write counters on `sqlite3`, saved SQL and normalized SQL caches, `aVar` bind values, `aCounter` statement-status counters, `aScan`/opcode execution counters, function aggregate `MEM_Agg` storage, auxdata linked lists, and preupdate caches.

Destructor ownership is a recurring persistence concern. Result and bind APIs must call application destructors if SQLite rejects input or cannot assume ownership. `SQLITE_STATIC`, `SQLITE_TRANSIENT`, and custom destructors have different behavior. Pointer values are represented as NULL values with subtype and terminator flags, so duplication deliberately removes pointer identity.

Statement time is stable within one run through `Vdbe.iCurrentTime`. Binding changes can set `expired` when `expmask` indicates the parameter may affect planning. Clear-bindings and transfer-bindings also honor this invalidation path.

## Dependencies and Integration Points

This file depends on `sqliteInt.h`, `vdbeInt.h`, and generated `opcodes.h`. It calls VDBE lifecycle/execution helpers, memory-cell helpers, btree payload and cursor operations, VFS time, WAL pager callbacks, schema reprepare, SQL expansion/normalization, virtual-table typed-pointer conventions, table/index column mapping helpers, record unpacking, default-expression evaluation, mutex/error/OOM utilities, and optional trace/profile hooks.

External integration surfaces include the public SQLite C API, application-defined SQL functions, virtual-table implementations, preupdate hooks, WAL hooks, trace/profile callbacks, statement scanstatus consumers, and deprecated compatibility APIs.

## Risks and Edge Cases

Mutex pairing is subtle. `vdbeUnbind()` and `columnMem()` intentionally return with the mutex held on success, leaving release to their callers. Any new path that returns early after these helpers risks deadlock. Conversely, releasing the mutex twice after a conversion failure would corrupt threading behavior.

`sqlite3_bind_zeroblob64()` enters the database mutex, then may call `sqlite3_bind_zeroblob()`, whose `vdbeUnbind()` also enters the same connection mutex. This relies on SQLite's mutex implementation and existing API pattern; changes to mutex kind or helper ownership would be risky.

`sqlite3_step()` automatic reprepare is bounded by `SQLITE_MAX_SCHEMA_RETRY`. Failure paths must preserve compiler error messages on the VDBE so later reset/finalize and `sqlite3_errmsg()` report the right condition. Saved SQL is required for many enhanced behaviors; legacy prepared statements without `SQLITE_PREPARE_SAVESQL` have narrower result-code contracts.

Value flags are security-sensitive. Pointer values require exact `MEM_Null|MEM_Term|MEM_Subtype`, subtype `'p'`, and matching pointer type string. `sqlite3_vtab_in_first/next()` additionally verifies the destructor is `sqlite3VdbeValueListFree()` to reject hostile fake typed pointers.

Text/blob length handling must respect 32-bit limits and UTF-16 even-byte truncation. Oversized `sqlite3_result_*64()` and bind paths must call destructors for rejected custom buffers. Encoding conversions can fail after returning column pointers, so `columnMallocFailure()` must set statement NOMEM state consistently.

Preupdate APIs have complex table mapping. Rowid tables, WITHOUT ROWID tables, generated storage column ordering, added columns with defaults, integer primary key aliases, and REAL affinity conversions all affect returned values. Mis-mapping can expose wrong old/new values to hooks.

Scanstatus cycle accounting supports direct address ranges and negative markers that search opcode properties. It must account for subprogram frames by walking to the root frame when a statement is currently inside triggers.

## Test Signals

High-value tests include finalizing NULL and valid statements, reset after row/done/error, profile and trace callbacks, auto-reset behavior after DONE, automatic reprepare after schema changes and binding-sensitive plan changes, WAL hook invocation after autocommit, and OOM during reprepare error copying.

Value/result tests should cover all storage classes, UTF-8 and UTF-16 conversion, subtype and pointer APIs, zeroblob expansion, oversized 64-bit lengths, destructor invocation on rejected inputs, strict subtype enforcement, `sqlite3_value_dup()` for strings/blobs/pointers, aggregate contexts, auxdata replacement/destruction, and stable `now` values.

Column/binding tests should cover out-of-range columns, calls before/after `SQLITE_ROW`, malloc failure during column text conversion, EXPLAIN/EQP column names, metadata APIs, binding while busy, out-of-range bind indexes, named parameters, binding transfer, clear-bindings expiration, pointer binding destructors, and zeroblob limit checks.

Virtual-table/preupdate/scanstatus tests should exercise `sqlite3_vtab_nochange()`, virtual-table `IN` iteration, hostile typed-pointer rejection, preupdate old/new values for INSERT/UPDATE/DELETE on rowid and WITHOUT ROWID tables, added-column defaults, update depth through triggers/FK actions, blob-write column reporting, scanstatus simple and complex modes, NCYCLE aggregation, reset of opcode counters, and feature-disabled builds.

<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeapi.c -->
