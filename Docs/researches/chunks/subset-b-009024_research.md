# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 91726-99549

## Purpose

This chunk spans the end of SQLite's value API, most of `vdbeapi.c`, all of `vdbetrace.c`, and the opening portion of `vdbe.c` in the amalgamated SQLite source vendored under WiredTiger tests. It is the bridge between public `sqlite3_*` statement/function APIs and the VDBE interpreter that executes prepared-statement bytecode.

The code covers:

- `sqlite3_value_*`, `sqlite3_result_*`, `sqlite3_column_*`, and `sqlite3_bind_*` entry points backed by internal `Mem` cells.
- Top-level stepping/reprepare control around `sqlite3VdbeExec()`.
- User-defined-function support: context lookup, aggregate contexts, auxdata, result subtype/pointer handling, virtual-table `IN` iteration, and preupdate callbacks.
- Statement metadata/status APIs, expanded SQL trace rendering, and scan-status counters.
- The first interpreter opcodes for control flow, register movement, expression evaluation, record encoding/decoding, transaction/savepoint handling, cursor opening, and btree seeking.

## Important APIs, Types, and Functions

- `sqlite3_value_encoding()`, `sqlite3_value_nochange()`, `sqlite3_value_frombind()`, `sqlite3_value_dup()`, `sqlite3_value_free()` expose value metadata and safe duplication/freeing of `sqlite3_value`/`Mem` instances.
- `sqlite3_result_blob*()`, `sqlite3_result_text*()`, `sqlite3_result_int*()`, `sqlite3_result_double()`, `sqlite3_result_null()`, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_subtype()`, `sqlite3_result_zeroblob*()`, `sqlite3_result_error*()` populate `sqlite3_context.pOut` for SQL functions and signal function-level errors.
- `sqlite3Step()` and `sqlite3_step()` drive VDBE execution, manage state transitions (`VDBE_READY_STATE`, `VDBE_RUN_STATE`, `VDBE_HALT_STATE`), auto-reset behavior, schema-change reprepare, tracing/profile callbacks, WAL callbacks, and API error masking.
- `sqlite3_user_data()`, `sqlite3_context_db_handle()`, `sqlite3_vtab_nochange()`, `sqlite3_aggregate_context()`, `sqlite3_get_auxdata()`, `sqlite3_set_auxdata()` provide function-context side channels and persistent per-aggregate/per-argument storage.
- `valueFromValueList()`, `sqlite3_vtab_in_first()`, and `sqlite3_vtab_in_next()` iterate a protected internal `ValueList` object for virtual-table `IN` RHS processing.
- `sqlite3_column_count()`, `sqlite3_data_count()`, `columnMem()`, `columnMallocFailure()`, `sqlite3_column_*()`, and `columnName()` expose result row values, names, decltypes, and optional metadata from the current `Vdbe`.
- `vdbeUnbind()`, `bindText()`, `sqlite3_bind_*()`, `sqlite3_bind_parameter_*()`, `sqlite3TransferBindings()`, and deprecated `sqlite3_transfer_bindings()` manage host parameters in `Vdbe.aVar`.
- Statement utility APIs include `sqlite3_db_handle()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_next_stmt()`, `sqlite3_stmt_status()`, `sqlite3_sql()`, `sqlite3_expanded_sql()`, and optional `sqlite3_normalized_sql()`.
- Optional hooks/status APIs include `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, `sqlite3_preupdate_blobwrite()`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus()`, and `sqlite3_stmt_scanstatus_reset()`.
- `sqlite3VdbeExpandSql()` tokenizes SQL and substitutes bound parameter renderings for trace output, respecting `SQLITE_TRACE_SIZE_LIMIT`.
- VDBE helpers in this chunk include `allocateCursor()`, `applyNumericAffinity()`, `applyAffinity()`, `sqlite3_value_numeric_type()`, `sqlite3ValueApplyAffinity()`, `numericType()`, `out2Prerelease()`, `filterHash()`, `vdbeColumnFromOverflow()`, and debug trace/coverage helpers.
- `sqlite3VdbeExec()` begins in this range and handles opcodes through `OP_IfNotOpen`; `OP_Found` starts at the chunk boundary and continues in the next chunk.

## Control Flow

`sqlite3_step()` validates the statement, enters the database mutex, then repeatedly calls `sqlite3Step()` while schema errors can be repaired by `sqlite3Reprepare()`. `sqlite3Step()` initializes a ready VM by clearing stale interrupts, bumping active/read/write VM counters, setting `pc=0`, optionally starting profile timers, then calls either `sqlite3VdbeList()` for explain output or `sqlite3VdbeExec()` for normal execution. `SQLITE_ROW` returns immediately with `pResultRow` set by `OP_ResultRow`; completion invokes profile callbacks and WAL callbacks for autocommit transactions. Errors may be transferred from the VDBE to the database handle when saved SQL is available.

`sqlite3VdbeExec()` is a large opcode dispatch loop. The portion in this chunk initializes interpreter-local state, checks progress callbacks/interrupts, maintains profiling counters, and then implements early opcodes:

- Control-transfer opcodes (`OP_Goto`, `OP_Gosub`, `OP_Return`, `OP_InitCoroutine`, `OP_EndCoroutine`, `OP_Yield`, `OP_Once`, `OP_If`, `OP_IfNot`, `OP_IsNull`, `OP_NotNull`, `OP_IfNullRow`, `OP_IfNotOpen`) mutate `pOp`/program counter and use `VdbeBranchTaken()` for coverage.
- Halt opcodes (`OP_HaltIfNull`, `OP_Halt`) set `p->rc`, build constraint/error messages, unwind subprogram frames, invoke `sqlite3VdbeHalt()`, and return `SQLITE_DONE`, `SQLITE_ERROR`, or `SQLITE_BUSY`.
- Register/value opcodes (`OP_Integer`, `OP_Int64`, `OP_Real`, `OP_String8`, `OP_String`, `OP_Null`, `OP_SoftNull`, `OP_Blob`, `OP_Variable`, `OP_Move`, `OP_Copy`, `OP_SCopy`, `OP_IntCopy`) update `Mem` flags, ownership, and shallow-copy invariants.
- Expression opcodes (`OP_Concat`, arithmetic ops, bit ops, `OP_AddImm`, `OP_MustBeInt`, `OP_RealAffinity`, `OP_Cast`, comparisons, `OP_And`, `OP_Or`, `OP_IsTrue`, `OP_Not`, `OP_BitNot`) enforce SQLite's dynamic typing, NULL propagation, affinity rules, and collation-aware comparison behavior.
- Row-format opcodes (`OP_Column`, `OP_TypeCheck`, `OP_Affinity`, `OP_MakeRecord`) decode and encode SQLite record format, apply strict table type checks, and update register/cache state.
- Transaction and cursor opcodes (`OP_Count`, `OP_Savepoint`, `OP_AutoCommit`, `OP_Transaction`, `OP_ReadCookie`, `OP_SetCookie`, `OP_OpenRead`, `OP_ReopenIdx`, `OP_OpenWrite`, `OP_OpenDup`, `OP_OpenEphemeral`, `OP_OpenAutoindex`, `OP_SorterOpen`, `OP_SequenceTest`, `OP_OpenPseudo`, `OP_Close`, optional `OP_ColumnsUsed`, seek opcodes, `OP_SeekScan`, `OP_SeekHit`) interact with btrees, pagers, schemas, savepoint lists, transient btrees, sorter state, and cursor caches.

## State and Persistence Behavior

The dominant mutable state is `Mem` cell state: flags (`MEM_Null`, `MEM_Int`, `MEM_Real`, `MEM_Str`, `MEM_Blob`, `MEM_Zero`, `MEM_Ephem`, `MEM_Static`, `MEM_Dyn`, `MEM_IntReal`, `MEM_Subtype`, `MEM_FromBind`), text encoding, destructor ownership, subtype, cached integer/real values, and buffer allocation. Result, column, bind, and opcode paths all depend on preserving these flags exactly to avoid leaks, dangling shallow copies, wrong affinity, or incorrect public API types.

`Vdbe` state includes execution state, program counter, statement return code, saved SQL, result row pointer, active frame stack, registers, host parameters, cursors, auxdata, scan counters, profiling counters, current time cache, expired/reprepare flags, and statement-journal bookkeeping. `sqlite3_step()` and opcodes update database connection counters (`nVdbeActive`, `nVdbeWrite`, `nVdbeRead`, `nVdbeExec`), error codes, interrupt state, schema flags, deferred-constraint counts, savepoint lists, and autocommit state.

Persistent database behavior appears in btree/pager-facing opcodes:

- `OP_Transaction` starts read/write/exclusive btree transactions, opens statement transactions when rollback granularity is needed, checks schema cookies/generation, and can expire statements on schema mismatch.
- `OP_Savepoint` creates, releases, or rolls back savepoints across all attached btrees and virtual tables, restoring deferred-constraint counters on rollback.
- `OP_AutoCommit` commits or rolls back the current transaction and halts the VM.
- `OP_SetCookie` writes database header metadata, updates in-memory schema cookie/file-format state, clears FK trigger cache, and expires TEMP-schema statements.
- `OP_OpenRead`/`OP_OpenWrite` open persistent btree cursors; `OP_OpenEphemeral`/`OP_OpenAutoindex`/`OP_SorterOpen` create transient btrees/sorters with delete-on-close or sorter-managed storage.
- `OP_Column` lazily reads record payloads from btree pages and overflow pages. Large overflow text/blob values may be cached in a cursor-local `VdbeTxtBlbCache` using reference-counted strings.

## Dependencies and Integration Points

This code depends heavily on internal SQLite subsystems:

- VDBE memory helpers: `sqlite3VdbeMemSetStr()`, `sqlite3VdbeMemSetInt64()`, `sqlite3VdbeMemSetDouble()`, `sqlite3VdbeMemCopy()`, `sqlite3VdbeMemMove()`, `sqlite3VdbeMemShallowCopy()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemRelease()`, `ExpandBlob()`, and serial-type helpers.
- Btree/pager APIs: `sqlite3BtreeBeginTrans()`, `sqlite3BtreeBeginStmt()`, `sqlite3BtreeCursor()`, `sqlite3BtreePayload*()`, `sqlite3BtreePayloadFetch()`, `sqlite3BtreeTableMoveto()`, `sqlite3BtreeIndexMoveto()`, `sqlite3BtreeNext()`, `sqlite3BtreePrevious()`, `sqlite3BtreeSavepoint()`, `sqlite3BtreeUpdateMeta()`, `sqlite3PagerWalCallback()`.
- Schema/parser/query-plan objects: `Table`, `Column`, `KeyInfo`, `CollSeq`, `UnpackedRecord`, `VList`, schema cookies, column metadata, and explain metadata.
- Connection-level features: mutexes, lookaside accounting, error APIs, VFS current-time calls, WAL hooks, trace/profile callbacks, preupdate/update hooks, virtual-table savepoint hooks, and optional scanstatus/normalize/UTF16/test/debug builds.
- Public API contracts: many comments are tagged `IMPLEMENTATION-OF` or `EVIDENCE-OF`, indicating that SQLite's Tcl/TH3-style test suites likely verify exact behavior.

For WiredTiger, this vendored file is not part of WiredTiger's storage engine implementation; it is a bundled SQLite amalgamation under test third-party sources. Integration risk is mostly in keeping the vendored SQLite behavior intact for tests or tools that build against this copy.

## Risks and Edge Cases

- Memory ownership is subtle. `SQLITE_STATIC`, `SQLITE_TRANSIENT`, custom destructors, `MEM_Ephem`, `MEM_Static`, `MEM_Dyn`, RCStr caches, and shallow `OP_SCopy` all have different lifetimes. Incorrect flag transitions can cause leaks, double frees, or use-after-free.
- Mutex discipline matters. Public APIs often assert the database mutex is held; column APIs enter it via `columnMem()` and must release through `columnMallocFailure()`.
- `sqlite3_bind_zeroblob64()` enters the DB mutex and then calls `sqlite3_bind_zeroblob()`, which uses `vdbeUnbind()` and also enters/leaves the mutex. SQLite mutexes are recursive in normal builds, but this pattern is sensitive to mutex configuration.
- `sqlite3_stmt_status(SQLITE_STMTSTATUS_MEMUSED)` computes memory by temporarily arranging for `sqlite3VdbeDelete()` to count freed bytes. Misuse after finalization or against an invalid statement is guarded only by API armor/build assumptions.
- `OP_Column` tolerates some historically accepted corrupt record shapes, but still performs explicit header-length/payload-size checks. The parser intentionally avoids loading overflow payload for `typeof()` and some `length()` cases; changes here can alter I/O and corruption behavior.
- Numeric conversion and comparison preserve or temporarily restore flags in several places. Affinity can persist in registers for some opcodes but is undone for comparison inputs after `applyAffinity()`. This distinction is observable through later opcode behavior.
- `OP_MakeRecord` encodes virtual-table no-change values with internal serial type 10 and trims trailing NULLs only under compile-time conditions. This affects `sqlite3_value_nochange()` and virtual-table `xUpdate`.
- Transaction/savepoint opcodes are tightly coupled to active VM counts, statement journals, virtual table callbacks, schema invalidation, and deferred FK counters. Early returns on `SQLITE_BUSY` preserve `pc` for retry.
- Optional compilation flags (`SQLITE_OMIT_UTF16`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_TRACE`, `SQLITE_ENABLE_NULL_TRIM`, debug/test flags) significantly alter available APIs and control paths.
- The assigned chunk ends at the opening comment for `OP_Found`; its implementation is unresolved in this chunk and belongs to the following source slice.

## Test Signals

Important test signals visible in this range include:

- Debug assertions for `Mem` type masks, shallow-copy validity, cursor types, opcode adjacency, savepoint counts, schema mutex ownership, and valid program-counter targets.
- `testcase()` calls around boundary values: varint/header sizes, integer packing thresholds, affinity conversions, schema-cookie outcomes, busy result variants, and opcode flag combinations.
- `VdbeBranchTaken()` and optional `SQLITE_VDBE_COVERAGE` instrumentation for branch coverage of comparisons, jumps, NULL behavior, seek/seekscan outcomes, and control-flow opcodes.
- `SQLITE_TEST` counters such as `sqlite3_search_count`, `sqlite3_interrupt_count`, `sqlite3_sort_count`, `sqlite3_max_blobsize`, and `sqlite3_found_count`.
- Trace/profile hooks: `SQLITE_TRACE_ROW`, profile callbacks, expanded SQL output, and VDBE register dump helpers under debug builds.
- API armor paths returning `SQLITE_MISUSE_BKPT`, `SQLITE_RANGE`, `SQLITE_TOOBIG`, or NULL instead of asserting on invalid public API inputs.
- Error propagation tests should exercise OOM in string conversion, too-large blob/text paths, schema-change reprepare, WAL callback failures after autocommit, preupdate default-value loading, strict type-check failures, savepoint rollback/release edge cases, and btree seek behavior for integer/real/string/NULL keys.
