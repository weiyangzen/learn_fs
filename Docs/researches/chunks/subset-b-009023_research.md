# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 83659-91725

## Scope

This chunk covers the tail of SQLite `backup.c`, the full amalgamated `vdbemem.c`, most of `vdbeaux.c`, and the opening of `vdbeapi.c`. It starts while `sqlite3_backup_finish()` is unwinding a backup object and ends inside `sqlite3_value_type()`'s type lookup table.

The main covered subsystems are:

- Backup progress helpers, source-page invalidation handling, backup restart, and `sqlite3BtreeCopyFile()` for VACUUM-style whole-file copies.
- VDBE `Mem` and `sqlite3_value` storage management, type conversion, string/blob ownership, aggregate finalization, rowset storage, expression-to-value extraction, STAT4 probe values, btree payload loading, and value byte/text APIs.
- VDBE program construction, opcode array growth, labels, P4 payload ownership, EXPLAIN/EQP/scanstatus support, btree usage masks, shared-cache entry/leave, register/cursor/frame allocation, VM ready/rewind/reset/finalize/delete paths, statement metadata, transaction commit/halt handling, and auxiliary-data cleanup.
- Record serialization/deserialization helpers, unpacked-record allocation, record comparison fast paths, index rowid/key comparison, change counters, statement expiration, bound-value extraction, pure-function checks, virtual-table error import, and pre-update hook dispatch.
- Public VDBE APIs at the start of `vdbeapi.c`: `sqlite3_expired()`, `sqlite3_finalize()`, `sqlite3_reset()`, `sqlite3_clear_bindings()`, and the beginning of the `sqlite3_value_*()` accessors.

## Purpose

The purpose of this range is to bridge SQLite's high-level prepared-statement API and SQL value semantics to the low-level VDBE execution engine, btree payload format, pager transaction model, and extension callbacks. It defines how an individual SQL value is represented and converted, how bytecode programs are assembled and made executable, how VM resources are owned and released, and how statement completion commits or rolls back database state.

Within WiredTiger this file is third-party SQLite test code under `test/3rdparty/sqlite3`. The implementation is not WiredTiger storage-engine logic, but it is still relevant to repository behavior because test tooling that embeds this amalgamation inherits SQLite's exact memory, transaction, and API semantics.

## Important APIs, Types, and Functions

### Backup Tail

The backup section exposes `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()` for progress reporting. `backupUpdate()` and `sqlite3BackupUpdate()` keep active backup destinations synchronized when a source page already copied by the backup is modified. `sqlite3BackupRestart()` rewinds active backup objects to page 1 when external changes make prior copied pages unreliable.

`sqlite3BtreeCopyFile()` builds a stack `sqlite3_backup` object with `pDestDb == 0` to distinguish internal use from public backup API use. It copies all pages from one btree to another in a single `sqlite3_backup_step()` call, issues an overwrite file-control hint when possible, clears the destination page-size-fixed flag on success, and clears the destination pager cache on failure.

### `Mem` and `sqlite3_value`

The `vdbemem.c` block is centered on `Mem`, SQLite's internal representation for SQL values and the implementation backing `sqlite3_value`.

Important invariant and allocation helpers include:

- `sqlite3VdbeCheckMemInvariants()` verifies dynamic ownership, type-bit exclusivity, pointer-null encoding, `zMalloc` size consistency, and string/blob ownership flags in debug builds.
- `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemNulTerminate()`, and `vdbeMemAddTerminator()` manage writable allocations and null terminators.
- `sqlite3VdbeMemRelease()`, `sqlite3VdbeMemReleaseMalloc()`, `sqlite3VdbeMemSetNull()`, and `vdbeMemClearExternAndSetNull()` release external destructors, aggregate contexts, dynamic strings, and owned allocation buffers.
- `sqlite3VdbeMemSetStr()`, `sqlite3VdbeMemSetZeroBlob()`, `sqlite3VdbeMemSetPointer()`, `sqlite3VdbeMemSetInt64()`, and `sqlite3VdbeMemSetDouble()` populate `Mem` cells using SQLite's destructor conventions (`SQLITE_STATIC`, `SQLITE_TRANSIENT`, `SQLITE_DYNAMIC`, or a custom destructor).

Type conversion is handled by `sqlite3VdbeIntValue()`, `sqlite3VdbeRealValue()`, `sqlite3VdbeBooleanValue()`, `sqlite3VdbeIntegerAffinity()`, `sqlite3VdbeMemIntegerify()`, `sqlite3VdbeMemRealify()`, `sqlite3VdbeMemNumerify()`, `sqlite3VdbeMemCast()`, `sqlite3VdbeMemStringify()`, `sqlite3VdbeChangeEncoding()`, and `sqlite3ValueText()`. These functions preserve SQLite's dynamic typing rules, including `MEM_IntReal`, NaN-as-NULL behavior, integer/real round-trip safeguards, UTF-8/UTF-16 conversion, and forced `CAST` semantics.

Aggregate and window function values are finalized by `sqlite3VdbeMemFinalize()` and `sqlite3VdbeMemAggValue()`, which construct a `sqlite3_context`, invoke `xFinalize` or `xValue`, and replace or populate result `Mem` cells.

Copy and movement APIs include `sqlite3VdbeMemShallowCopy()`, `sqlite3VdbeMemCopy()`, and `sqlite3VdbeMemMove()`. Shallow copies deliberately convert dynamic source storage into ephemeral/static references, while full copies call `sqlite3VdbeMemMakeWriteable()` when a string/blob needs independent storage.

`sqlite3VdbeMemFromBtree()` and `sqlite3VdbeMemFromBtreeZeroOffset()` load btree payload bytes into `Mem` objects, either by copying or by using an ephemeral pointer returned by the btree cursor when enough bytes are locally available.

Expression and STAT4 helpers (`valueFromExpr()`, `sqlite3ValueFromExpr()`, `stat4ValueFromExpr()`, `sqlite3Stat4ProbeSetValue()`, `sqlite3Stat4ValueFromExpr()`, `sqlite3Stat4Column()`, and `sqlite3Stat4ProbeFree()`) convert literal, bound-variable, vector, and limited deterministic-function expressions into `sqlite3_value` or `UnpackedRecord` probe values for planning.

### VDBE Program Construction and Metadata

`sqlite3VdbeCreate()` allocates and links a new VM into `sqlite3.pVdbe`, initializes it in `VDBE_INIT_STATE`, and emits the initial `OP_Init`. `sqlite3VdbeSetSql()` stores SQL text and prepare flags. Optional normalization helpers track double-quoted strings.

Opcode construction is handled by `growOpArray()`, `sqlite3VdbeAddOp0/1/2/3()`, `sqlite3VdbeAddOp4()`, `sqlite3VdbeAddOp4Int()`, `sqlite3VdbeAddOp4Dup8()`, `sqlite3VdbeAddOpList()`, `sqlite3VdbeGoto()`, `sqlite3VdbeLoadString()`, `sqlite3VdbeMultiLoad()`, and `sqlite3VdbeAddFunctionCall()`. These functions allocate opcode slots, initialize profiling/coverage/comment fields, and attach P4 payloads such as function contexts, strings, integers, reals, key info, tables, subprograms, and virtual tables.

Label and jump resolution is split across `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `resolveP2Values()`, `sqlite3VdbeJumpHere()`, and `sqlite3VdbeJumpHereOrPopInst()`. `resolveP2Values()` also computes read-only and reader flags and maximum virtual-table argument counts, making it a critical finalization pass before a VM is packaged.

`freeP4()`, `vdbeFreeOpArray()`, `sqlite3VdbeChangeP4()`, `sqlite3VdbeAppendP4()`, and `sqlite3VdbeChangeToNoop()` define opcode P4 ownership. P4 payloads can own memory, references, function definitions, `KeyInfo`, `Mem`, virtual tables, table references, subprogram signatures, or function contexts, and each P4 type has distinct destructor rules.

Metadata and diagnostics include `sqlite3VdbeExplain()`, `sqlite3VdbeExplainPop()`, `sqlite3VdbeDisplayP4()`, `sqlite3VdbeDisplayComment()`, `sqlite3VdbeList()`, `sqlite3VdbeNextOpcode()`, `sqlite3VdbeScanStatus*()`, `sqlite3VdbePrintOp()`, `sqlite3VdbePrintSql()`, and `sqlite3VdbeIOTraceSql()`.

### VM Runtime State, Cleanup, and Transactions

`sqlite3VdbeMakeReady()` packages a constructed VM by resolving labels, computing statement-journal needs, allocating `aMem`, `aVar`, `apArg`, and `apCsr`, initializing memory arrays, and rewinding the VM. It reuses unused opcode-array tail space before allocating a separate `pFree` block.

Cursor and frame cleanup is centralized in `sqlite3VdbeFreeCursorNN()`, `closeCursorsInFrame()`, `sqlite3VdbeFrameRestore()`, `closeAllCursors()`, `sqlite3VdbeFrameDelete()`, and `sqlite3VdbeFrameMemDel()`. Cursors may own btree cursors, sorter state, virtual-table cursors, or text/blob cache objects. Trigger subprogram frames restore the parent VM's opcodes, registers, cursors, rowid/change counters, and auxdata.

`vdbeCommit()` is the main transaction commit helper. It syncs virtual tables, invokes commit hooks, detects multi-file write transactions, performs simple one-phase/two-phase btree commits when possible, and uses a super-journal for atomic multi-database rollback-journal commits when required. WAL, in-memory, temporary, OFF, and MEMORY journal modes bypass super-journal use.

`sqlite3VdbeHalt()` is the high-risk state machine that moves a VM from run state to halt state. It closes cursors, handles special errors (`NOMEM`, `IOERR`, `FULL`, `INTERRUPT`), rolls back statements or whole transactions as needed, checks immediate and deferred foreign keys, commits autocommit transactions when legal, updates change counters, releases btree locks, adjusts active VM counters, and triggers unlock-notify callbacks.

`sqlite3VdbeReset()`, `sqlite3VdbeFinalize()`, `sqlite3VdbeClearObject()`, and `sqlite3VdbeDelete()` reset or destroy VM state. They transfer VM errors to the database handle, invoke SQL log/profile hooks where enabled, release registers, variables, subprograms, column names, scanstatus data, normalized SQL state, opcode arrays, and unlink the VM from the connection list.

### Record Serialization and Comparison

The record-format section defines serial type lengths and deserialization helpers. `sqlite3SmallTypeSizes[]`, `sqlite3VdbeSerialTypeLen()`, `sqlite3VdbeOneByteSerialTypeLen()`, `serialGet()`, `serialGet7()`, and `sqlite3VdbeSerialGet()` decode SQLite record fields into `Mem` values. Integers are big-endian two's-complement encodings, serial type 7 is IEEE 754 double, serial types 8 and 9 are integer constants 0 and 1, and serial types >=12 encode blob/text lengths.

`sqlite3VdbeAllocUnpackedRecord()` and `sqlite3VdbeRecordUnpack()` allocate and populate `UnpackedRecord` objects used by btree comparisons. Corrupt records that overrun the key buffer are detected and sanitized to avoid using uninitialized memory.

Comparison helpers include `sqlite3MemCompare()`, `sqlite3BlobCompare()`, `sqlite3IntFloatCompare()`, `vdbeCompareMemString()`, `sqlite3VdbeRecordCompareWithSkip()`, `sqlite3VdbeRecordCompare()`, `vdbeRecordCompareInt()`, `vdbeRecordCompareString()`, and `sqlite3VdbeFindCompare()`. The optimized integer and binary-string comparators are selected only for safe header-size and key-shape cases; otherwise the generic comparator handles null, numeric, text collation, blob, sort-order, and big-null rules.

`sqlite3VdbeIdxRowid()` extracts the rowid stored at the end of an index record with corruption checks, and `sqlite3VdbeIdxKeyCompare()` compares an index cursor's key payload against an unpacked key.

### Public API Entry Points in This Chunk

The beginning of `vdbeapi.c` defines statement safety checks and public APIs:

- `sqlite3_expired()` reports whether a statement needs recompilation.
- `sqlite3_finalize()` resets and deletes a statement under the database mutex, then closes zombie connections if needed.
- `sqlite3_reset()` resets a statement, rewinds it for reuse, and returns the prior execution result.
- `sqlite3_clear_bindings()` releases all bound parameter values, sets them to NULL, and marks statements expired when binding-sensitive query planning is enabled.
- `sqlite3_value_blob()`, `sqlite3_value_bytes()`, `sqlite3_value_bytes16()`, `sqlite3_value_double()`, `sqlite3_value_int()`, `sqlite3_value_int64()`, `sqlite3_value_subtype()`, `sqlite3_value_pointer()`, `sqlite3_value_text()`, and UTF-16 variants expose `Mem` contents through the extension API.

The chunk ends before `sqlite3_value_type()` completes.

## Control Flow and State Behavior

The value-management control flow is mostly defensive and flag-driven. `Mem.flags` determines the active representations and ownership model. Functions often fast-path existing representations, then fall back to allocation, encoding conversion, blob expansion, or destructor invocation. On allocation failure, many helpers reset the value to NULL or propagate `SQLITE_NOMEM_BKPT`, and callers rely on `db->mallocFailed` to make subsequent operations safe.

VDBE construction flows from `sqlite3VdbeCreate()` through repeated opcode additions, label creation/resolution, P4 attachment, explain/comment/scanstatus metadata, and then `sqlite3VdbeMakeReady()`. After `MakeReady`, the VM leaves `VDBE_INIT_STATE`; opcode additions are no longer valid. `sqlite3VdbeRewind()` prepares a ready or halted VM for execution by resetting program counter, result code, change counters, cache counters, statement id, and foreign-key counters.

VDBE halt/reset/finalize flow is transaction-sensitive. `sqlite3VdbeHalt()` first closes execution resources, then decides whether to roll back a statement savepoint, roll back the whole transaction, commit an autocommit transaction, or leave surrounding transaction state open. It distinguishes ordinary constraint failures from special errors that may leave pager or journal state inconsistent. `sqlite3VdbeReset()` can call `sqlite3VdbeHalt()` if the VM is still running, transfers errors to the connection after any real execution, and leaves the VM reusable.

Persistent state affected by this range includes:

- `Mem` cell content, flags, encoding, subtype, destructor, aggregate context, rowset pointer, zero-blob tail, and owned allocation.
- Prepared statement fields such as opcode arrays, register arrays, cursor arrays, variable bindings, SQL text, explain state, scanstatus data, VM state, expiration masks, result-column names, auxdata, subprograms, and active-frame stacks.
- Connection state such as active VM counters, write/read VM counters, deferred foreign-key counters, change counters, error objects, commit hooks, virtual-table sync/commit state, auto-commit state, savepoint counts, and unlock-notify state.
- Btree/pager transaction state, including statement savepoints, phase-one/phase-two commit state, exclusive locks, rollback journals, and super-journals.

Record comparison is deliberately allocation-free in hot paths. Serialized record bytes are decoded only as far as needed, corruption checks guard buffer overreads, and optimized comparators avoid generic `Mem` comparison where the first field is an integer or binary-collated string with a small header.

## Dependencies and Integration Points

This code depends on core SQLite internals defined elsewhere in the amalgamation:

- `sqliteInt.h`, `vdbeInt.h`, and `opcodes.h` definitions for `sqlite3`, `Vdbe`, `VdbeOp`, `Mem`, `FuncDef`, `Parse`, `Btree`, `BtCursor`, `Pager`, `KeyInfo`, `UnpackedRecord`, `VdbeCursor`, `VdbeFrame`, `AuxData`, `PreUpdate`, opcodes, flags, limits, and mutex macros.
- Btree and pager APIs such as `sqlite3BtreePayload()`, `sqlite3BtreePayloadFetch()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCommitPhaseOne/Two()`, `sqlite3BtreeSavepoint()`, `sqlite3BtreeCloseCursor()`, and pager journal-mode/file-control helpers.
- Memory and string APIs including `sqlite3DbMalloc*`, `sqlite3DbFree*`, `sqlite3DbRealloc*`, `sqlite3VdbeMemTranslate()`, `sqlite3Atoi64()`, `sqlite3AtoF()`, `sqlite3Int64ToText()`, `sqlite3StrAccum*`, and encoding/BOM helpers.
- Function, collation, virtual-table, rowset, STAT4, pre-update hook, scanstatus, tracing, and normalize subsystems.
- OS and VFS APIs used by commit logic: file open/write/sync/delete, randomness, file suffixing, device characteristics, and current-time/profile calls.

External integration points are the public SQLite C APIs touched by this range (`sqlite3_backup_*`, `sqlite3_finalize`, `sqlite3_reset`, `sqlite3_clear_bindings`, `sqlite3_value_*`) and extension callbacks (`xFinalize`, `xValue`, scalar `xSFunc`, collation `xCmp`, virtual-table `xClose`/sync/commit, pre-update callback, commit hook, profile/trace callbacks).

For WiredTiger, the direct integration is via any tests or utilities that compile or execute this third-party SQLite amalgamation. Behavior changes here would affect embedded SQLite statement execution, extension compatibility, record comparisons, and transaction semantics within those tests rather than the WiredTiger data path itself.

## Risks

- `Mem` ownership flags are subtle. Incorrect transitions between `MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `zMalloc`, and `xDel` can cause leaks, double frees, stale pointers, or use-after-free in SQL functions and result accessors.
- Type conversion semantics are compatibility-sensitive. Integer/real/text/blob conversion, NaN handling, `MEM_IntReal`, zero-blob expansion, pointer subtypes, and UTF-16 termination all affect public SQLite API behavior and SQL comparison results.
- Destructor paths can re-enter extension code through aggregate finalizers, custom value destructors, virtual-table close methods, auxdata destructors, and pre-update callbacks. Resource cleanup order must remain stable.
- VDBE P4 payload ownership is type-specific. Mislabeling P4 types or changing `freeP4()` rules can leak `KeyInfo`, free static memory, drop virtual-table locks, or lose function contexts.
- Transaction halt logic is high blast radius. Errors in `sqlite3VdbeHalt()`, `vdbeCommit()`, or statement savepoint handling can corrupt rollback semantics, break autocommit behavior, lose change-counter updates, or mishandle foreign-key constraints.
- Super-journal handling is filesystem-sensitive. Name collisions, sync ordering, delete errors, and phase-one failures are carefully sequenced to preserve atomic multi-database commits.
- Record decoding and comparison are corruption-facing. Bounds checks around headers, serial types, rowid extraction, string/blob lengths, and optimized overread assumptions are essential for safe handling of malformed database pages.
- Debug-only invariants and coverage helpers mask many assumptions. Builds without `SQLITE_DEBUG`, STAT4, UTF16, virtual tables, pre-update hooks, or scanstatus compile different paths.
- This is an amalgamated third-party file. Local edits are hard to maintain unless they are test-only or mirrored from the upstream SQLite source used by this repository.

## Test and Validation Signals

Useful validation signals for this chunk include:

- SQLite API tests covering `sqlite3_finalize(NULL)`, reset after success/error, clearing bindings, statement expiration after parameter-sensitive planning, and `sqlite3_value_*()` conversions for NULL, integer, real, text, blob, zero-blob, pointer subtype, and UTF-16 text.
- VDBE memory tests that exercise transient/static/dynamic string destructors, aggregate finalization, window `xValue`, rowset cells, shallow/full copy behavior, blob expansion, out-of-memory injection, and API armor paths.
- SQL semantic tests for `CAST`, numeric affinity, integer/real comparison boundaries, NaN treatment, boolean conversion, UTF-8/UTF-16 conversion, and blob/text byte counts.
- STAT4 planner tests with literal expressions, bound variables during reprepare, vector probes, deterministic constant functions, corrupt stat records, and `sqlite3Stat4Column()` extraction.
- EXPLAIN, EXPLAIN QUERY PLAN, bytecode virtual table, scanstatus, trace/profile, and normalized-SQL tests to cover opcode display, comments, P4 rendering, subprogram iteration, and profiling callbacks.
- Transaction tests for autocommit writes, `OR FAIL`, immediate and deferred foreign keys, statement rollback vs release, nested savepoints, virtual-table commit/sync failures, commit hooks, lock contention, `SQLITE_BUSY`, `SQLITE_INTERRUPT`, `SQLITE_FULL`, `SQLITE_IOERR`, and OOM.
- Multi-database rollback-journal tests that force super-journal creation, sync failures, name collisions, phase-one failures, and cleanup of cold journals.
- Record-format tests for every serial type, corrupt record headers, truncated payloads, index rowid extraction, collated text comparison, zero-blob comparison, DESC and big-null sort flags, optimized integer/string record comparators, and fallback generic comparator behavior.
- Pre-update hook tests for rowid tables and WITHOUT ROWID tables, INSERT/UPDATE/DELETE operations, blob writes, default values, old/new unpacked records, and cleanup after callback invocation.
