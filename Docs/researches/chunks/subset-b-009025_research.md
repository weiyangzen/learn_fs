# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 99550-107363

## Scope

This chunk starts in the late body of SQLite's VDBE execution loop, continues through the full incremental BLOB implementation in `vdbeblob.c`, then covers most of `vdbesort.c` and the optional bytecode/tables-used virtual table in `vdbevtab.c`. It ends just after the `memjournal.c` file header and forward type declarations, before the in-memory journal implementation begins.

The VDBE opcode section in this chunk handles btree lookup, rowid allocation, row insert/delete, sorter iteration, schema mutation, integrity checks, rowsets, trigger subprograms, foreign-key counters, aggregate/window function dispatch, WAL/journal/vacuum opcodes, virtual table opcodes, function invocation, bloom filters, tracing, and the final VDBE error/return paths.

## Purpose

The VDBE portion is the execution engine's storage-facing and callback-heavy tail. It bridges bytecode opcodes to the btree, pager, schema, virtual table, function, trigger, rowset, and statement-status subsystems while preserving cursor state and translating low-level return codes into VDBE statement outcomes.

The incremental BLOB portion exposes `sqlite3_blob_*()` API support. It opens a row/column blob through a small generated VDBE program, borrows the resulting btree cursor, and performs range-checked payload reads/writes without rewriting the whole row.

The sorter portion implements SQLite's external merge sorter for `ORDER BY`, `CREATE INDEX`, and uniqueness checks. It starts with in-memory record accumulation, spills sorted Packed Memory Arrays (PMAs) to temporary files when needed, and builds single-threaded or worker-threaded merge trees for sorted iteration.

The bytecode virtual table portion exposes `bytecode()` and `tables_used()` table-valued modules, allowing SQL-level inspection of a prepared statement's opcodes or table/index accesses when `SQLITE_ENABLE_BYTECODE_VTAB` is enabled.

## Important APIs, Types, and Functions

- VDBE opcode cases:
  - `OP_IfNoHope`, `OP_Found`, `OP_NotFound`, `OP_NoConflict`: index key probes using `sqlite3BtreeIndexMoveto()` and cursor `seekHit`/`seekResult` state.
  - `OP_SeekRowid`, `OP_NotExists`, `OP_Rowid`, `OP_RowData`, `OP_IdxRowid`, `OP_DeferredSeek`, `OP_FinishSeek`: rowid and cursor-positioning operations over table/index cursors.
  - `OP_NewRowid`, `OP_Insert`, `OP_RowCell`, `OP_Delete`, `OP_IdxInsert`, `OP_IdxDelete`: table/index mutation paths, update/preupdate hooks, change counters, and cursor cache invalidation.
  - `OP_SorterSort`, `OP_Rewind`, `OP_Next`, `OP_Prev`, `OP_SorterNext`, `OP_SorterData`, `OP_SorterCompare`: sorter and btree scan control.
  - `OP_Destroy`, `OP_Clear`, `OP_CreateBtree`, `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_DropTable`, `OP_DropIndex`, `OP_DropTrigger`: schema and btree object lifecycle.
  - `OP_IntegrityCk`, `OP_Checkpoint`, `OP_JournalMode`, `OP_Vacuum`, `OP_IncrVacuum`, `OP_Pagecount`, `OP_MaxPgcnt`: database maintenance and pragma support.
  - `OP_Program`, `OP_Param`, `OP_AggStep`, `OP_AggInverse`, `OP_AggFinal`, `OP_AggValue`, `OP_Function`, `OP_PureFunc`: trigger frames, aggregate/window contexts, and scalar function callbacks.
  - `OP_VBegin`, `OP_VCreate`, `OP_VDestroy`, `OP_VOpen`, `OP_VFilter`, `OP_VColumn`, `OP_VNext`, `OP_VRename`, `OP_VUpdate`, `OP_VCheck`, `OP_VInitIn`: virtual table integration.
  - `OP_FilterAdd`, `OP_Filter`, `OP_Init`, `OP_Trace`, debug-only `OP_Abortable` and `OP_ReleaseReg`: optimizer bloom filters, tracing, and validation aids.
- `Incrblob`: private handle behind public `sqlite3_blob*`, storing blob size, payload offset, target column, borrowed `BtCursor`, owning statement, database handle, database name, and table metadata.
- `blobSeekToRow()`: binds the target rowid into the generated statement, seeks the cursor, verifies the selected column is TEXT/BLOB, caches payload offset/length, and invalidates the handle on error.
- Public incremental blob API: `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, `sqlite3_blob_reopen()`.
- Sorter core types: `VdbeSorter`, `SortSubtask`, `SorterList`, `SorterRecord`, `SorterFile`, `PmaReader`, `PmaWriter`, `MergeEngine`, and `IncrMerger`.
- Sorter APIs exported to VDBE: `sqlite3VdbeSorterInit()`, `sqlite3VdbeSorterWrite()`, `sqlite3VdbeSorterRewind()`, `sqlite3VdbeSorterNext()`, `sqlite3VdbeSorterRowkey()`, `sqlite3VdbeSorterCompare()`, `sqlite3VdbeSorterReset()`, and `sqlite3VdbeSorterClose()`.
- Sorter internal helpers include `vdbePmaReadBlob()`, `vdbePmaReadVarint()`, `vdbePmaReaderInit()`, `vdbeSorterSort()`, `vdbeSorterListToPMA()`, `vdbeSorterFlushPMA()`, `vdbeMergeEngineStep()`, `vdbeSorterMergeTreeBuild()`, and `vdbeSorterSetupMerge()`.
- Bytecode virtual table types and methods: `bytecodevtab`, `bytecodevtab_cursor`, `bytecodevtabConnect()`, `bytecodevtabBestIndex()`, `bytecodevtabFilter()`, `bytecodevtabNext()`, `bytecodevtabColumn()`, and `sqlite3VdbeBytecodeVtabInit()`.

## Control Flow

The VDBE opcode switch uses direct fallthrough to share work between related opcodes. `OP_IfNoHope` falls into `OP_NotFound` when `seekHit` cannot prove a prefix match is possible. `OP_SeekRowid` converts compatible non-integer values before falling into `OP_NotExists`. `OP_SorterSort` and `OP_Sort` increment sort counters before falling into `OP_Rewind`.

Cursor-moving opcodes update `nullRow`, `deferredMoveto`, `cacheStatus`, `seekResult`, and debug `seekOp` fields before branching. Scans use `jump_to_p2`, `jump_to_p2_and_check_for_interrupt`, or `check_for_interrupt` to centralize control transfer and progress interruption checks.

Mutation opcodes increment write counters with `sqlite3VdbeIncrWriteCounter()`, call btree operations, invalidate column caches with `CACHE_STALE` and `colCacheCtr`, and invoke hooks only after the underlying btree operation succeeds. `OP_Delete` also supports pre-update-only no-op deletes used before overwriting a row.

Schema opcodes route through btree and schema helpers. `OP_Destroy` prevents unsafe root-page movement while other reader VMs are active and records moved root pages for schema reset. `OP_ParseSchema` reparses schema entries by running SQL reentrantly through `sqlite3_exec()` under initialization state.

Trigger execution via `OP_Program` allocates or reuses a `VdbeFrame`, saves the parent register/cursor/opcode state, swaps in the subprogram's memory and cursor arrays, clears `Once` bits, and restarts the execution loop at the subprogram. `OP_Param` reads parent-frame registers for `old.*` and `new.*` values.

Incremental blob open validates the target table and column, rejects virtual tables, views, WITHOUT ROWID tables, generated-column tables, and unsafe writable columns, then emits a short VDBE program with transaction, table lock, open cursor, row seek, column decode, result row, and halt. `blobSeekToRow()` runs or rewinds that statement to position the cursor. Read/write calls enter the cursor mutex, perform a bounded payload operation at `iOffset + p->iOffset`, and finalize the statement if the cursor is aborted.

Sorter write flow begins in memory. `sqlite3VdbeSorterWrite()` records the serialized key, tracks first-field type for optimized comparisons, grows either a bulk allocation or separate records, and flushes to a PMA when memory thresholds or heap pressure dictate. PMA flushing sorts the list, writes a PMA length varint, then writes each key as length varint plus blob to a temp file.

Sorter rewind either sorts the in-memory list directly or flushes the final list, joins worker threads, and constructs a merge tree. Single-threaded sorters use `VdbeSorter.pMerger`. Threaded sorters use `VdbeSorter.pReader` backed by `IncrMerger` objects that prepopulate alternating temp files so the main VDBE thread can read one segment while workers prepare the next.

Bytecode virtual table filtering requires a hidden `stmt` argument, either SQL text that is prepared and owned by the cursor or a `"stmt-pointer"` value borrowed from the caller. `bytecodevtabNext()` advances through main opcodes and optional subprograms using `sqlite3VdbeNextOpcode()`. `bytecodevtabColumn()` renders opcode fields, P4 display text, explain comments, scan-status counters, subprogram names, or table/index usage metadata depending on module mode.

## State and Persistence Behavior

The VDBE section mutates both in-memory execution state and database state. Persistent database effects include row/table/index inserts and deletes, btree creation/destruction/clearing, schema reparsing side effects, journal-mode transitions, checkpoints, vacuum operations, page-count changes, and virtual table `xCreate`/`xDestroy`/`xUpdate`/`xRename` effects.

Cursor state is central. Many opcodes deliberately mark cursor caches stale, maintain `movetoTarget` for deletes and deferred seeks, use `seekResult` as an optimization hint, and set `nullRow` when scans exhaust. Incorrect maintenance of those fields would surface later as wrong `OP_Column`, `OP_Rowid`, `OP_Next`, or update-hook behavior.

Incremental blob handles persist a prepared statement and borrowed btree cursor for the lifetime of the blob handle. The blob length is fixed in `Incrblob.nByte`; writes cannot resize the value. On seek/read/write failures that invalidate the cursor, `pStmt` is finalized and later blob API calls return `SQLITE_ABORT` except close. `sqlite3_blob_close()` finalizes the statement, which may commit or roll back statement/transaction state according to normal VDBE behavior.

Sorter state is transient but may use temporary files. `VdbeSorter.list` owns in-memory records until flushed or consumed. Each `SortSubtask` owns temp files and per-thread unpacked record state. `PmaReader` key pointers may point into an mmap, read buffer, or owned allocation and are only stable until the next read. `sqlite3VdbeSorterReset()` joins workers, frees readers/mergers/temp files/records, and returns the sorter to an empty state; close additionally frees the sorter and its bulk memory.

Bytecode virtual table state is cursor-local. It may own a prepared statement when SQL text was supplied, and it owns rendered P4 strings and a `Mem` object used to enumerate subprograms. It does not persist database content; `tables_used()` reads schema hashes to label root pages as tables or indexes.

## Dependencies and Integration Points

This chunk is tightly integrated with SQLite's btree, pager, VDBE memory, schema, parser, virtual table, function, rowset, WAL, and VFS layers. Important dependencies include `sqlite3Btree*` cursor/table/index APIs, `sqlite3Pager*` journal/WAL APIs, `sqlite3VdbeMem*` register helpers, `sqlite3VdbeRecordCompare*`, `sqlite3_exec()`, `sqlite3InitCallback()`, `sqlite3Vtab*`, `sqlite3Thread*`, `sqlite3Os*`, and fault-simulation hooks.

Compile-time options change major behavior: `SQLITE_OMIT_INCRBLOB`, `SQLITE_MAX_WORKER_THREADS`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_WAL`, `SQLITE_OMIT_PRAGMA`, `SQLITE_OMIT_VACUUM`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_BYTECODE_VTAB`, `SQLITE_ENABLE_STMT_SCANSTATUS`, and debug/test macros all include, exclude, or instrument pieces of this range.

In the WiredTiger repository context, this is vendored SQLite test/support code under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3`. It is not WiredTiger's own storage engine implementation, but it can affect test binaries or tooling that embed this SQLite amalgamation.

## Risks and Edge Cases

- VDBE opcode fallthrough is intentional and fragile. Adding a `break`, changing opcode ordering, or altering assertions around shared cases can change semantics.
- Cursor state bugs are high risk because later opcodes rely on `nullRow`, `deferredMoveto`, `movetoTarget`, `seekResult`, `seekHit`, and cache invalidation rather than always re-seeking.
- `OP_NewRowid` has separate sequential, random, and AUTOINCREMENT paths. Boundary handling at `MAX_ROWID`, 100 random attempts, and root-frame autoincrement registers can produce `SQLITE_FULL`.
- Hook behavior is subtle. Insert/delete/preupdate hooks are conditional on table metadata, no-op flags, update flags, rowid availability, and compile-time features. The incremental blob write path intentionally reports a preupdate delete-like event for session-module convenience.
- `OP_JournalMode` must reject WAL transitions inside transactions or with active readers and must handle temporary files, VFS shared-memory support, and MEMORY-to-WAL transitions carefully.
- `OP_ParseSchema` runs SQL reentrantly while initialization flags are set; error paths reset schema state and need to preserve malloc failure handling.
- Incremental blob writes reject indexed/FK child columns but conservatively reject expression indexes too. Generated-column tables are entirely rejected. `blobSeekToRow()` invalidates the handle on type mismatch or missing row.
- `blobReadWrite()` range checks `n`, `iOffset`, and `iOffset+n` against the fixed blob size; integer overflow is avoided by casting the sum to `sqlite3_int64`.
- Sorter code mixes bulk-memory offsets, linked pointers, mmap pointers, temp-file buffers, and worker-owned task state. Ownership bugs can cause use-after-free, double-free, leaked temp files, or stale pointer comparisons.
- PMA format depends on exact varint sizes and file offsets. Corrupt offsets or size accounting would cascade into bad reads during merge-tree construction.
- Threaded sorter paths rely on `bDone`, `pThread`, task assignment, and join ordering. There are comments noting intentionally weak synchronization for `bDone`; correctness relies on always joining before consuming worker results.
- Optimized integer/text comparators assume specific record encoding and only activate under constrained `KeyInfo` conditions. Any change to record layout, collation assumptions, or sort flags would need careful validation.
- Bytecode virtual table accepts raw statement pointers via `sqlite3_value_pointer()`. It must not finalize borrowed statements, and callers must ensure pointer lifetime and connection compatibility.
- The final `memjournal.c` lines in this chunk are only introductory comments and type forward declarations; behavior for the in-memory rollback journal begins in a later chunk.

## Test Signals

Useful tests for this chunk include:

- VDBE lookup tests for `Found`, `NotFound`, `NoConflict`, `IfNoHope`, rowid seeks, and `IdxGE`/`IdxGT`/`IdxLT`/`IdxLE`, including NULL key fields and multi-column IN optimizations.
- Rowid allocation tests at empty table, normal append, explicit AUTOINCREMENT high-water mark, `MAX_ROWID`, and random-rowid exhaustion boundaries.
- Insert/delete/update-hook and preupdate-hook tests covering normal rowid tables, no-op delete-before-insert, auxiliary index deletes, and change counter behavior.
- Sorter tests for all-memory sorting, PMA spill, multi-PMA merge, unique-index duplicate detection through `OP_SorterCompare`, stable CREATE INDEX sorting in single-threaded mode, and worker-threaded sorting when `PRAGMA threads` is enabled.
- Fault injection for sorter temp-file open/read/write, mmap fetch, PMA reader allocation, merge-engine allocation, and background thread return codes.
- Incremental blob tests for read-only and read/write handles, reopen to another row, out-of-range reads/writes, missing rowid, NULL/integer/real column rejection, indexed/FK/generated/WITHOUT ROWID/virtual/view table rejection, and invalidation after abort.
- Schema and maintenance tests for `DROP`, `CREATE`, `VACUUM`, `incremental_vacuum`, `integrity_check`, WAL checkpoints, and journal-mode transitions inside and outside transactions.
- Virtual table opcode tests for `xOpen`, `xFilter`, `xColumn`, `xNext`, `xUpdate`, constraint handling, `xIntegrity`, and error-message import from modules.
- Bytecode virtual table tests with SQL text and `stmt-pointer` inputs, hidden `stmt` constraint enforcement, subprogram inclusion/exclusion, scan-status columns with and without `SQLITE_ENABLE_STMT_SCANSTATUS`, and `tables_used()` root-page labeling.
