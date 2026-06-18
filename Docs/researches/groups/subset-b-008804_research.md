# subset-b-008804 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeaux.c -->
# sources/storage-engines/sqlite/src/vdbeaux.c

## Purpose

`vdbeaux.c` is the auxiliary implementation for SQLite's Virtual Database Engine (VDBE), the internal object behind `sqlite3_stmt`. It handles statement creation, bytecode assembly, opcode operand ownership, statement packaging, cursor and frame cleanup, transaction halt/reset/finalize behavior, record serialization/deserialization, record comparison, index helper routines, statement expiration, and hook support. It is not the opcode interpreter itself; it supplies the compiler/runtime support code that `vdbe.c`, parser/codegen modules, btree, pager, virtual table, and public statement APIs rely on.

## Important APIs, types, and functions

- `sqlite3VdbeCreate(Parse*)`, `sqlite3VdbeParser()`, `sqlite3VdbeSetSql()`, `sqlite3VdbeSwap()` create or re-home VDBE objects and SQL text. VDBEs are linked through `sqlite3.pVdbe`, and `sqlite3VdbeCreate()` seeds each program with `OP_Init`.
- Opcode construction APIs include `sqlite3VdbeAddOp0/1/2/3()`, `sqlite3VdbeAddOp4()`, `sqlite3VdbeAddOp4Int()`, `sqlite3VdbeAddOp4Dup8()`, `sqlite3VdbeAddOpList()`, `sqlite3VdbeGoto()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeJumpHereOrPopInst()`, `sqlite3VdbeChangeOpcode/P1/P2/P3/P4/P5()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeSetP4KeyInfo()`, and `sqlite3VdbeChangeToNoop()`.
- Function-call bytecode is assembled by `sqlite3VdbeAddFunctionCall()`, which allocates a `sqlite3_context` P4 payload and chooses `OP_Function` or `OP_PureFunc` based on expression context.
- Label and jump resolution use `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, and the private `resolveP2Values()`.
- Statement packaging and execution setup use `sqlite3VdbeMakeReady()` and `sqlite3VdbeRewind()`. `ReusableSpace` and `allocSpace()` reuse slack opcode-array memory for registers, bind variables, cursor pointers, and argument arrays.
- Runtime cleanup and lifecycle APIs include `sqlite3VdbeFreeCursor()`, `sqlite3VdbeFrameRestore()`, `sqlite3VdbeFrameDelete()`, `sqlite3VdbeHalt()`, `sqlite3VdbeReset()`, `sqlite3VdbeFinalize()`, and `sqlite3VdbeDelete()`.
- Transaction/persistence logic is concentrated in `vdbeCommit()`, `vdbeCloseStatement()`, `sqlite3VdbeCheckFkImmediate()`, `sqlite3VdbeCheckFkDeferred()`, and `sqlite3VdbeHalt()`.
- Record encoding/decoding/comparison helpers include `sqlite3VdbeSerialTypeLen()`, `sqlite3VdbeSerialGet()`, `sqlite3VdbeRecordUnpack()`, `sqlite3MemCompare()`, `sqlite3BlobCompare()`, `sqlite3IntFloatCompare()`, `sqlite3VdbeRecordCompareWithSkip()`, `sqlite3VdbeRecordCompare()`, `sqlite3VdbeFindCompare()`, `sqlite3VdbeIdxRowid()`, and `sqlite3VdbeIdxKeyCompare()`.
- Index-repair/search support for expression and virtual columns uses `sqlite3VdbeFindIndexKey()`, `vdbeIsMatchingIndexKey()`, and `vdbeSkipField()`.
- Debug, explain, and instrumentation support includes `sqlite3VdbeExplain()`, `sqlite3VdbeExplainPop()`, `sqlite3VdbeDisplayP4()`, `sqlite3VdbeDisplayComment()`, `sqlite3VdbePrintOp()`, `sqlite3VdbeList()`, `sqlite3VdbeScanStatus*()`, VDBE coverage line setters, and debug-only abort/jump assertions.
- Optional hook/glue routines include `sqlite3VtabImportErrmsg()`, `sqlite3VdbePreUpdateHook()`, `sqlite3NotPureFunc()`, `sqlite3VdbeGetBoundValue()`, `sqlite3VdbeSetVarmask()`, `sqlite3VdbeSetChanges()`, and `sqlite3ExpirePreparedStatements()`.

Core types touched include `Vdbe`, `VdbeOp`, `Op`, `Parse`, `Mem`, `VdbeCursor`, `VdbeFrame`, `SubProgram`, `UnpackedRecord`, `KeyInfo`, `ScanStatus`, `AuxData`, `PreUpdate`, `Btree`, `BtCursor`, `Pager`, `Table`, `Index`, `FuncDef`, and `CollSeq`.

## Control flow

The normal compiler path starts with `sqlite3VdbeCreate()`, appends bytecode through the `sqlite3VdbeAdd*()` family, records symbolic labels, P4 payloads, comments, scanstatus metadata, btree usage masks, and result-column metadata, then calls `sqlite3VdbeMakeReady()`. `sqlite3VdbeMakeReady()` resolves labels, marks read/write behavior, computes max virtual-table argument needs, allocates `aMem`, `aVar`, `apArg`, and `apCsr`, initializes memory cells, detaches parse-owned state, and rewinds the statement to `VDBE_READY_STATE`.

Jump resolution is delayed until packaging. `resolveP2Values()` walks backwards from the final opcode to `OP_Init`, replaces negative label P2 values with real addresses, tracks whether the program reads or writes btrees, updates max virtual table argument counts, frees parse labels, and asserts that jump opcodes do not land outside the program.

Execution cleanup flows through `sqlite3VdbeHalt()` and then usually `sqlite3VdbeReset()` or `sqlite3VdbeFinalize()`. `sqlite3VdbeHalt()` closes cursors and frames first, then decides whether to release a statement savepoint, roll back a statement, roll back the full transaction, or commit. `sqlite3VdbeReset()` transfers errors back to the connection only after actual execution (`pc>=0`), releases error strings and result rows, emits optional SQL log/profile data, and returns the masked statement result. `sqlite3VdbeFinalize()` resets if needed and then deletes the object.

`vdbeCommit()` handles transaction commit. It syncs virtual tables, counts write transactions across attached databases, invokes the commit hook, chooses a simple one-database commit path or a multi-database super-journal path, performs btree commit phases, and calls virtual-table commit hooks. The complex path creates, syncs, and deletes a super-journal to make multi-file rollback-journal commits atomic.

Record comparison has a hot generic path and specialized fast paths. `sqlite3VdbeRecordCompareWithSkip()` decodes serial types directly from a serialized key, compares against an `UnpackedRecord` with integer, real, string, blob, and null handling, applies DESC and NULLS-large sort flags, detects corruption bounds, and avoids allocation. `sqlite3VdbeFindCompare()` selects integer or binary-string fast comparators when key shape allows safe overread assumptions; otherwise it returns the generic comparator.

## State and persistence behavior

VDBE state moves from `VDBE_INIT_STATE` during code generation to `VDBE_READY_STATE` after packaging, then `VDBE_RUN_STATE` during execution, then `VDBE_HALT_STATE` after `sqlite3VdbeHalt()`. `sqlite3VdbeRewind()` resets runtime fields including `pc`, `rc`, `errorAction`, `nChange`, cache counters, statement id, and FK counters.

The `sqlite3` connection tracks all VDBEs in `db->pVdbe`, plus active/read/write counters. `sqlite3VdbeHalt()` decrements `nVdbeActive`, `nVdbeWrite`, and `nVdbeRead` after commit/rollback handling and calls `sqlite3ConnectionUnlocked()` when autocommit releases locks.

P4 ownership is encoded by `p4type`. `freeP4()` dispatches destructors for dynamic strings, `KeyInfo`, function contexts, values, vtabs, table references, cursor-hint expressions, and subroutine signatures. `vdbeFreeOpArray()` walks op arrays backward, frees P4 payloads and explain comments, then frees the opcode array.

Memory-cell arrays hold dynamically allocated strings, blobs, aggregate contexts, VDBE frames, auxdata, and cursor caches. `releaseMemArray()` intentionally inlines a high-traffic release path. `closeAllCursors()` restores outer frames, closes all cursors, releases memory cells, deletes delayed frames, and clears auxdata.

Durability is handled indirectly through btree and pager APIs. This file decides when to call btree commit phases, savepoint rollback/release, rollback-all, virtual-table sync/commit/savepoint hooks, and FK checks. It also updates `sqlite3_changes()` state through `sqlite3VdbeSetChanges()` only when change counters are enabled and the statement transaction was not rolled back.

Serialized record persistence follows SQLite's serial-type format. `sqlite3VdbeSerialGet()` reconstructs `Mem` values from big-endian integer and IEEE float payloads, handles text/blob ephemeral pointers, maps NaN to NULL, and includes mixed-endian float support. `sqlite3SmallTypeSizes` and `sqlite3VdbeSerialTypeLen()` define byte sizes for serial types.

## Dependencies and integration points

This file includes `sqliteInt.h` and `vdbeInt.h` and depends on nearly every core subsystem: parser/code generator, opcode metadata generated from VDBE sources, memory allocation, mutex and shared-cache btree locking, pager journal modes and VFS I/O, virtual tables, foreign keys, schema invalidation, collations, SQL functions, EXPLAIN/bytecode virtual table, statement scanstatus, preupdate hooks, and test/debug instrumentation.

Important callers and consumers include parser/codegen modules that emit opcodes, `vdbe.c` as the opcode interpreter, public statement APIs in `vdbeapi.c`, btree search paths that call record comparison, sorter/statistics code that compares records, Tcl and C test harnesses, virtual table modules, and incremental blob code in `vdbeblob.c`.

Compile-time feature gates materially change behavior: `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_DISKIO`, `VDBE_PROFILE`, `SQLITE_DEBUG`, `SQLITE_VDBE_COVERAGE`, `SQLITE_MIXED_ENDIAN_64BIT_FLOAT`, and percentile/date-time options.

## Risks and edge cases

- `sqlite3VdbeAddOp3()` and `sqlite3VdbeAddOp4Int()` intentionally duplicate initialization fields; adding new opcode fields risks divergence unless both paths are updated.
- P4 ownership is fragile. A wrong `p4type` can leak memory, double-free, skip vtab/table unlocks, or hold stale parser-owned pointers.
- Label resolution and opcode metadata depend on generated opcode ordering from `mkopcodeh.tcl`; adding opcodes without updating generator assumptions can break `resolveP2Values()` and jump validation.
- `sqlite3VdbeMakeReady()` reuses slack opcode memory. Incorrect size/alignment math would corrupt register, variable, cursor, or argument arrays.
- `sqlite3VdbeHalt()` is high risk because it combines cursor closure, special error handling, statement savepoints, full rollback, autocommit commit, FK enforcement, virtual table callbacks, and change counters.
- Multi-database commit code must handle I/O errors without deleting a super-journal too early; wrong ordering can compromise atomicity after crash.
- Record comparison code uses performance shortcuts, direct varint reads, and bounded overread assumptions. Corruption checks, padding assumptions, and header-size limits are security-sensitive.
- Numeric comparison must preserve SQLite ordering across int, real, `IntReal`, NaN-as-NULL, text/blob classes, descending order, and NULLS-large behavior.
- `sqlite3VdbeFindIndexKey()` intentionally tolerates expression/virtual-column differences for delete/integrity paths; too much tolerance can hide corruption, too little can report false corruption after floating-point conversion drift.
- Optional hooks such as preupdate and SQL log run during sensitive lifecycle windows and must not leave connection state (`db->pPreUpdate`, error state, aux allocations) dirty.

## Test signals

Relevant existing test areas include VDBE bytecode and EXPLAIN output, malloc/OOM fault injection, statement reset/finalize behavior, transaction/savepoint rollback, multi-database atomic commit, foreign-key constraint timing, virtual table update/sync/commit paths, preupdate hooks, scanstatus, corrupt database tests, record comparison/sorter/stat4 behavior, zeroblob/blob comparison, collations, date/time deterministic function restrictions, shared-cache locking, and debug builds with `SQLITE_DEBUG`, `SQLITE_VDBE_COVERAGE`, `VDBE_PROFILE`, and `SQLITE_TEST_REALLOC_STRESS`.

Specific smoke signals for changes in this file are: no leaked prepared statements in `db->pVdbe`; active/read/write VDBE counters match busy statements; `sqlite3_reset()` and `sqlite3_finalize()` preserve correct connection error codes; `sqlite3_changes()`/`total_changes()` update only after successful statements; corrupted records return `SQLITE_CORRUPT` instead of reading out of bounds; EXPLAIN output remains stable; and OOM injection does not leak P4 payloads, cursors, auxdata, frames, or column names.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeaux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeblob.c -->
# sources/storage-engines/sqlite/src/vdbeblob.c

## Purpose

`vdbeblob.c` implements SQLite's incremental BLOB I/O API when `SQLITE_OMIT_INCRBLOB` is not defined. It provides `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, and `sqlite3_blob_reopen()`. The implementation opens a hidden VDBE program that owns transaction, locking, schema, and cursor lifetime, then lets the blob API borrow its btree cursor to read or write a fixed-size text/blob field in one row.

## Important APIs, types, and functions

- `Incrblob` is the private blob handle. It stores the opened value length (`nByte`), byte offset within the row record (`iOffset`), target column (`iCol`), borrowed btree cursor (`pCsr`), owning prepared statement (`pStmt`), database handle, database name, and table pointer.
- `blobSeekToRow(Incrblob*, sqlite3_int64, char**)` positions the hidden VDBE cursor on the requested rowid, validates that the target field is TEXT or BLOB, caches the field offset and byte length, and registers the cursor as an incremental-blob cursor with btree.
- `sqlite3_blob_open()` validates the table and column, rejects unsupported table shapes, rejects unsafe write targets, builds and prepares the hidden VDBE, seeks to the initial row, and returns the `Incrblob` as an opaque `sqlite3_blob*`.
- `sqlite3_blob_close()` frees the `Incrblob` wrapper under the database mutex, then finalizes the hidden statement, which closes the cursor and may commit or roll back the transaction according to normal VDBE rules.
- `blobReadWrite()` is the shared range-checking, mutex, cursor-enter, read/write, error-propagation, invalidation, and optional preupdate-hook path for `sqlite3_blob_read()` and `sqlite3_blob_write()`.
- `sqlite3_blob_read()` calls `blobReadWrite()` with `sqlite3BtreePayloadChecked`; `sqlite3_blob_write()` calls it with `sqlite3BtreePutData`.
- `sqlite3_blob_bytes()` returns the fixed opened value size while the statement remains valid.
- `sqlite3_blob_reopen()` retargets an existing handle to a different row in the same table/column by reusing `blobSeekToRow()`.

## Control flow

Opening begins by zeroing `*ppBlob`, entering `db->mutex`, allocating `Incrblob`, and initializing a stack `Parse`. The loop around `sqlite3LocateTable()` and `blobSeekToRow()` retries on `SQLITE_SCHEMA` up to `SQLITE_MAX_SCHEMA_RETRY`. The table must be a rowid ordinary table; virtual tables, WITHOUT ROWID tables, tables with generated columns, and views are rejected.

For write handles, `sqlite3_blob_open()` rejects columns that are part of a child foreign key when foreign keys are enabled, and rejects indexed columns. Expression indexes cause conservative rejection because the code cannot prove whether the expression depends on the target column. This preserves index and foreign-key consistency because incremental writes bypass normal SQL expression and constraint update machinery.

The hidden bytecode program starts with `OP_Transaction`, then a small `openBlob` program: optional `OP_TableLock`, `OP_OpenRead` or `OP_OpenWrite`, `OP_NotExists`, `OP_Column`, `OP_ResultRow`, and `OP_Halt`. The `OP_Column` reads an artificial column (`pTab->nCol`) to populate cursor type/offset cache without reading the actual payload. `sqlite3VdbeUsesBtree()` records btree usage for locking, and `sqlite3VdbeMakeReady()` packages the statement with one memory register and one cursor.

`blobSeekToRow()` writes the target rowid directly into VDBE register 1. On first use it calls `sqlite3_step()`. On reopen, if the VM is paused at `OP_ResultRow`, it moves `v->pc` back to the `OP_NotExists` opcode and calls `sqlite3VdbeExec()` directly. A successful row caches `pCsr`, `iOffset`, and `nByte`; a non-blob/text value or missing row finalizes the hidden statement, clears `pStmt`, and returns an error.

Reads and writes check null handle, negative sizes or offsets, and range overflow against the immutable `nByte`. A valid operation enters the btree cursor, calls the selected btree payload routine at `iOffset + p->iOffset`, leaves the cursor, stores the result in `v->rc`, and converts `SQLITE_ABORT` into permanent handle invalidation by finalizing the statement and setting `pStmt` to NULL.

## State and persistence behavior

The blob handle is valid only while `Incrblob.pStmt` is non-NULL. Errors from missing rows, wrong value type, btree aborts, or failed reopen invalidate the handle for future read/write/reopen calls, which then return `SQLITE_ABORT` until close.

The blob size is fixed for the lifetime of the opened row value. `sqlite3_blob_write()` can modify bytes in place but cannot grow or shrink the field. `sqlite3_blob_bytes()` deliberately needs no mutex because `nByte` is immutable after a successful seek, although it returns zero if the handle or hidden statement is invalid.

The hidden VDBE owns transaction and cursor persistence. Closing the blob finalizes the VDBE; if the blob was opened for writing, finalize/reset/halt logic in `vdbeaux.c` is responsible for committing, rolling back, invoking hooks, and releasing locks.

Btree invalidation protects against concurrent row deletion or movement. The cursor is registered with `sqlite3BtreeIncrblobCursor()`. If later btree operations invalidate it, read/write may receive `SQLITE_ABORT`; the handle then finalizes its statement and becomes permanently aborted.

When preupdate hooks are enabled, blob writes call `sqlite3VdbePreUpdateHook()` before writing, after restoring the cursor if necessary. The operation is reported as `SQLITE_DELETE` with `iBlobWrite` identifying the blob column, matching existing session/preupdate expectations in this code path.

## Dependencies and integration points

`vdbeblob.c` includes `sqliteInt.h` and `vdbeInt.h`. It depends on schema lookup (`sqlite3LocateTable`, `sqlite3ColumnIndex`, schema-to-index mapping), table metadata (`Table`, `Index`, `FKey`, generated/view/virtual/rowid flags), VDBE construction and finalization, btree cursor APIs, shared-cache table locks, transaction opcodes, memory/error APIs, mutex discipline, API armor, preupdate hooks, and public extension API tables.

It integrates with Tcl and C test wrappers in `test_blob.c`, `test1.c`, and `tclsqlite.c`, with btree invalidation logic for incremental blob cursors, with zeroblob-producing SQL functions and bind APIs, and with VDBE lifecycle code in `vdbeaux.c` for statement close/commit behavior.

Feature gates that change behavior include `SQLITE_OMIT_INCRBLOB`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_SHARED_CACHE`, and `SQLITE_ENABLE_PREUPDATE_HOOK`.

## Risks and edge cases

- `blobSeekToRow()` depends on hard-coded bytecode layout: it resets `v->pc` to opcode index 4 and asserts that the opcode is `OP_NotExists`. Changes to `openBlob` instruction order require coordinated updates.
- The hidden `OP_Column` deliberately uses an artificial column to populate offset/type caches. Changes to cursor header parsing could break incremental blob offset discovery.
- Write-safety checks are conservative but critical. Allowing writes to indexed, foreign-key, generated-column, view, virtual, or WITHOUT ROWID targets would bypass normal SQL maintenance paths.
- Range checking must avoid signed overflow; the code casts offset plus length through `sqlite3_int64` before comparing against `nByte`.
- `sqlite3_blob_close()` frees the wrapper before finalizing the statement. It saves `pStmt` first, so this is intentional, but any future close-time use of `Incrblob` fields after the free would be unsafe.
- Reopen after an error must not leave a half-valid cursor. The code asserts that failures leave `pStmt==0`.
- Preupdate hook semantics use `SQLITE_DELETE` for writes even though the logical operation is an update; consumers must understand this special case through `iBlobWrite`.
- Schema retry must reset parse state correctly on each attempt to avoid stale errors or leaked parse allocations.

## Test signals

Relevant tests include `test/incrblob*.test`, `test/e_blobopen.test`, `test/e_blobclose.test`, `test/e_blobwrite.test`, `test/savepoint.test`, `test/fkey2.test`, `test/fkey7.test`, `test/without_rowid*.test`, `test/tkt2332.test`, `test/corruptK.test`, and blob wrappers in `src/test_blob.c` and `src/test1.c`. Useful coverage signals are successful open/read/write/reopen/close, correct errors for missing rows and non-blob values, rejected writes to indexed or FK columns, correct behavior after row deletion/invalidation, correct readonly write failure, stable `sqlite3_blob_bytes()`, close with NULL handle returning OK, schema-change retry behavior, preupdate hook observations, and OOM/API-armor paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/vdbeblob.c -->
