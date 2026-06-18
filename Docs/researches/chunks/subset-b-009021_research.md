# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 68994-76298

## Purpose

This chunk bridges two major SQLite subsystems in the amalgamated `sqlite3.c` vendored under WiredTiger tests:

- The end of the WAL implementation, covering read transaction snapshot selection, WAL frame lookup/read/write, savepoint undo, checkpoints, exclusive locking mode, snapshot APIs, and the WAL file accessor.
- The beginning of the btree implementation, including btree internal data structures, shared-cache mutex/table-lock logic, page/cell parsing and free-space management, pager-backed btree open/close/configuration, transaction begin/commit/rollback, auto-vacuum page relocation, and initial cursor creation.

The chunk ends in the middle of `sqlite3BtreeCursor()`: it shows the public wrapper through the `p->sharable` branch, but the non-sharable return path continues in the next chunk.

## Important APIs, Types, and Functions

### WAL APIs and helpers

- `walBeginReadTransaction()` and `sqlite3WalBeginReadTransaction()` establish a consistent WAL reader snapshot. They repeatedly call `walTryBeginRead()` until it stops returning `WAL_RETRY`, optionally validating `SQLITE_ENABLE_SNAPSHOT` snapshots under a shared checkpoint lock.
- `sqlite3WalEndReadTransaction()` releases the selected WAL read-lock and first ends any write transaction state held by the same `Wal`.
- `walFindFrame()` and `sqlite3WalFindFrame()` search WAL-index hash tables from newest relevant hash page down to `pWal->minFrame` for the latest frame for a page number not newer than the reader's `pWal->hdr.mxFrame`.
- `sqlite3WalReadFrame()` reads a page payload from the WAL file by deriving the WAL frame offset from `iRead` and page size.
- `sqlite3WalDbsize()` reports the database page count from the current WAL header snapshot.
- `sqlite3WalBeginWriteTransaction()` takes `WAL_WRITE_LOCK`, verifies the shared wal-index header has not changed, and marks `pWal->writeLock`.
- `sqlite3WalEndWriteTransaction()` releases write-lock state and clears redo-checksum state.
- `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, and `sqlite3WalSavepointUndo()` roll back uncommitted WAL frames, recompute WAL-index headers, restore savepoint frame/checksum state, and truncate the WAL on savepoint rollback.
- `walRestartLog()`, `walWriteOneFrame()`, `walRewriteChecksums()`, and `walFrames()` implement log restart, frame serialization, checksum repair after in-transaction overwrites, transaction padding/sync, WAL-index append, and commit header publication.
- `sqlite3WalFrames()` is the SEH wrapper for `walFrames()`.
- `sqlite3WalCheckpoint()` implements the public checkpoint path: it takes the checkpoint lock, optionally takes the writer lock for FULL/RESTART/TRUNCATE, refreshes the wal-index header, calls `walCheckpoint()`, reports frame/backfill counts, and releases locks.
- `sqlite3WalCallback()` returns and clears `pWal->iCallback`, the frame count to pass to a WAL hook.
- `sqlite3WalExclusiveMode()` switches the WAL subsystem between normal and exclusive locking by acquiring or releasing the current read-lock.
- `sqlite3WalHeapMemory()` identifies heap-memory WAL-index mode.
- Under `SQLITE_ENABLE_SNAPSHOT`, `sqlite3WalSnapshotRecover()`, `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, `sqlite3_snapshot_cmp()`, `sqlite3WalSnapshotCheck()`, and `sqlite3WalSnapshotUnlock()` expose snapshot capture, comparison, opening, validation, recovery of checkpoint-attempt metadata, and checkpoint-lock release.
- `sqlite3WalFramesize()` exists for `SQLITE_ENABLE_ZIPVFS`.
- `sqlite3WalFile()` returns the underlying WAL `sqlite3_file`.

### Btree types and constants

- `MemPage` is the pager-extra structure for one database page. It caches decoded btree-page fields such as page number, page type, header offset, local payload limits, free bytes, cell count, cell pointers, overflow-cell arrays, and function pointers for cell parsing and cell sizing.
- `Btree` is a connection-owned handle. It references a shared `BtShared`, tracks this handle's transaction state, shared-cache linked-list membership, backup count, incremental blob state, and the schema-root `BtLock`.
- `BtShared` owns the underlying pager, page-1 reference, cursor list, schema pointer, mutex, page-size/usable-size, transaction counters, auto-vacuum state, shared-cache locks, writer pointer, temporary cell buffer, and flags such as `BTS_READ_ONLY`, `BTS_PAGESIZE_FIXED`, `BTS_SECURE_DELETE`, `BTS_NO_WAL`, `BTS_EXCLUSIVE`, and `BTS_PENDING`.
- `BtCursor` represents a btree cursor. It stores cursor state, flags, root page, key cache, current page stack, parsed `CellInfo`, page indexes, and optional index `KeyInfo`.
- `BtLock` represents shared-cache table-level locks (`READ_LOCK` or `WRITE_LOCK`) on root pages.
- `CellInfo` describes a parsed cell: key or payload size, payload pointer, local payload bytes, and total local cell size.
- Btree page flags `PTF_INTKEY`, `PTF_ZERODATA`, `PTF_LEAFDATA`, and `PTF_LEAF` encode on-disk page type combinations.
- Cursor states `CURSOR_VALID`, `CURSOR_INVALID`, `CURSOR_SKIPNEXT`, `CURSOR_REQUIRESEEK`, and `CURSOR_FAULT` encode whether a cursor is usable, needs repositioning, or is poisoned by an error.
- Pointer-map macros and constants (`PTRMAP_PAGENO`, `PTRMAP_PTROFFSET`, `PTRMAP_ISPAGE`, `PTRMAP_ROOTPAGE`, `PTRMAP_FREEPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`, `PTRMAP_BTREE`) support auto-vacuum page relocation.

### Btree mutex and shared-cache lock APIs

- `sqlite3BtreeEnter()`, `sqlite3BtreeLeave()`, `sqlite3BtreeEnterAll()`, and `sqlite3BtreeLeaveAll()` lock and unlock `BtShared` mutexes in a stable address order for shared-cache btrees. The careful path handles recursive enter attempts and out-of-order sibling locks.
- `sqlite3BtreeHoldsMutex()`, `sqlite3BtreeHoldsAllMutexes()`, and `sqlite3SchemaMutexHeld()` are assert helpers for mutex discipline.
- `sqlite3BtreeEnterCursor()` and `sqlite3BtreeLeaveCursor()` are incremental-blob cursor lock wrappers.
- `sqlite3_enable_shared_cache()` toggles the process-global default for future shared-cache opens.
- `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `clearAllSharedCacheTableLocks()`, and `downgradeAllSharedCacheTableLocks()` implement table-level shared-cache locking and writer-starvation prevention.
- Debug-only `hasSharedCacheTableLock()` and `hasReadConflicts()` verify callers hold the right table locks and that write cursors do not conflict with other read cursors.

### Btree page, cell, and cursor-position helpers

- `invalidateAllOverflowCache()` and `invalidateIncrblobCursors()` clear cached overflow paths or invalidate incremental blob cursors when rows/pages may change.
- `btreeSetHasContent()`, `btreeGetHasContent()`, and `btreeClearHasContent()` manage the per-transaction bitvec used to preserve rollback correctness for pages moved to and reused from the freelist.
- `saveCursorKey()`, `saveCursorPosition()`, `saveAllCursors()`, `saveCursorsOnList()`, `btreeRestoreCursorPosition()`, `sqlite3BtreeCursorHasMoved()`, `sqlite3BtreeFakeValidCursor()`, and `sqlite3BtreeCursorRestore()` preserve and restore cursor positions across btree modifications or rollback.
- `btreeMoveto()` dispatches to table or index seek after unpacking index records.
- `btreePayloadToLocal()`, `btreeParseCellPtrNoPayload()`, `btreeParseCellPtr()`, `btreeParseCellPtrIndex()`, `btreeParseCell()`, `cellSizePtr()`, `cellSizePtrIdxLeaf()`, `cellSizePtrNoPayload()`, and `cellSizePtrTableLeaf()` decode btree cells and compute local cell sizes. They implement SQLite's overflow payload distribution formula and contain optimized varint scanning for high-frequency paths.
- `ptrmapPageno()`, `ptrmapPut()`, `ptrmapGet()`, and `ptrmapPutOvflPtr()` read and write auto-vacuum pointer-map entries.
- `defragmentPage()`, `pageFindSlot()`, `allocateSpace()`, and `freeSpace()` manage in-page cell-content storage, freeblock chains, fragmentation counts, coalescing, and secure-delete zeroing.
- `decodeFlags()`, `btreeComputeFreeSpace()`, `btreeCellSizeCheck()`, `btreeInitPage()`, and `zeroPage()` initialize and validate `MemPage` metadata from on-disk page bytes.

### Pager-backed btree APIs and transaction functions

- `btreePageFromDbPage()`, `btreeGetPage()`, `btreePageLookup()`, `getAndInitPage()`, `releasePage*()`, and `btreeGetUnusedPage()` bridge pager `DbPage` objects to btree `MemPage` metadata.
- `pageReinit()` is the pager rollback callback that clears and optionally reinitializes btree page metadata after page content is restored.
- `sqlite3BtreeOpen()` opens or reuses a `BtShared`, opens the pager, reads the file header, initializes page size/reserve/autovacuum state, links shared-cache structures, installs busy handlers, and returns a `Btree` handle.
- `sqlite3BtreeClose()` rolls back active work, removes shared-cache references, closes the pager, frees schema and temporary storage, and unlinks the connection handle.
- `sqlite3BtreeSetCacheSize()`, `sqlite3BtreeSetSpillSize()`, `sqlite3BtreeSetMmapLimit()`, `sqlite3BtreeSetPagerFlags()`, `sqlite3BtreeSetPageSize()`, `sqlite3BtreeGetPageSize()`, `sqlite3BtreeGetReserveNoMutex()`, `sqlite3BtreeGetRequestedReserve()`, `sqlite3BtreeMaxPageCount()`, `sqlite3BtreeSecureDelete()`, `sqlite3BtreeSetAutoVacuum()`, and `sqlite3BtreeGetAutoVacuum()` expose pager and btree tuning/configuration.
- `lockBtree()` obtains the pager shared lock, reads and validates page 1, opens WAL if the file header demands WAL mode, adapts page size, computes payload thresholds, and sets `pBt->pPage1`.
- `newDatabase()` and `sqlite3BtreeNewDb()` initialize an empty file as a valid SQLite database page 1.
- `btreeBeginTrans()` and `sqlite3BtreeBeginTrans()` start read/write/exclusive transactions, resolve shared-cache conflicts, invoke busy handling, coordinate WAL writer locks when configured, open pager savepoints, and update transaction state.
- Auto-vacuum functions `setChildPtrmaps()`, `modifyPagePointer()`, `relocatePage()`, `incrVacuumStep()`, `finalDbSize()`, `sqlite3BtreeIncrVacuum()`, and `autoVacuumCommit()` maintain pointer maps and move pages so free pages at the end of the file can be truncated.
- `sqlite3BtreeCommitPhaseOne()`, `btreeEndTransaction()`, `sqlite3BtreeCommitPhaseTwo()`, and `sqlite3BtreeCommit()` implement the two-phase btree commit path over the pager.
- `sqlite3BtreeTripAllCursors()`, `btreeSetNPage()`, `sqlite3BtreeRollback()`, `sqlite3BtreeBeginStmt()`, and `sqlite3BtreeSavepoint()` handle rollback, cursor invalidation or preservation, statement savepoints, and nested savepoint release/rollback.
- `btreeCursor()`, `btreeCursorWithLock()`, and the beginning of `sqlite3BtreeCursor()` initialize cursor structures, assert transaction/lock preconditions, link cursors into `BtShared.pCursor`, mark multiple cursors on the same root, and allocate write-cursor temp space.

## Control Flow

### WAL read/write/checkpoint flow

WAL readers begin by loading a wal-index header and attempting to choose a stable read mark. If the WAL is fully checkpointed or empty, the reader tries read-lock 0 and verifies the live wal-index header still matches the cached header; otherwise it selects the highest suitable read mark not exceeding the current `mxFrame` or requested snapshot frame. If lock acquisition or validation races a writer/checkpointer, `WAL_RETRY` drives the caller loop. Snapshot mode adds a shared checkpoint lock and checks salts plus `nBackfillAttempted` to reject snapshots invalidated by WAL reset or checkpoint progress.

WAL frame lookup is hash-table based. `walFindFrame()` searches hash pages backward from the reader's last frame to `minFrame`, ignores entries newer than the reader snapshot, verifies page-number matches, and stops on the newest match. Reads use the found frame number to compute the WAL frame payload offset.

Writers take `WAL_WRITE_LOCK`, verify the wal-index header is unchanged, optionally restart the log if no readers need old frames, write a WAL header for a new log, serialize dirty pages as frames, pad/sync commit frames as required by synchronous settings, append frame/page mappings to the wal-index, and publish the updated header on commit. If a page is overwritten within the same transaction, the code writes into the earlier frame and later rewrites checksums from `pWal->iReCksum`.

Checkpointing takes the checkpoint lock, optionally takes the writer lock for non-passive modes, refreshes the wal-index header, backfills frames to the database through `walCheckpoint()`, reports log and checkpoint counts, clears the cached header if the pager cache is stale, and releases all locks. Passive checkpoints explicitly disable blocking behavior before reading the header to preserve passive semantics.

### Btree open and transaction flow

`sqlite3BtreeOpen()` allocates a connection-level `Btree`. In shared-cache mode it canonicalizes the filename and looks for an existing `BtShared` with the same VFS and path; otherwise it allocates a new `BtShared`, opens the pager, reads the first 100 bytes of the file, initializes page-size/reserve/autovacuum guesses, and links the shared object into the global shared-cache list. The pager owns page cache and journaling; btree owns page interpretation, schema association, and cursor/transaction state.

`lockBtree()` is the first-page gate. It obtains the pager shared lock, reads page 1, validates the SQLite header, file-format versions, payload fractions, page size, reserve size, and page count. If the file is WAL-mode, it opens WAL and may return with `pPage1` unset so the caller can retry after the pager has access to the latest page-1 image. Once valid, it computes local payload thresholds and pins `pBt->pPage1`.

`btreeBeginTrans()` is the main transaction state machine. It rejects illegal shared-cache conflicts, checks read-only write attempts, queries schema-root shared-cache locks, loops through `lockBtree()` and pager begin while invoking the busy handler only for safe cases, updates `pBt->nTransaction`, table locks, `p->inTrans`, `pBt->inTransaction`, writer ownership, and page-1 database-size metadata, then opens pager savepoints for active SQL savepoints.

Commit phase one runs auto-vacuum if enabled, applies a pending truncate image, and delegates durable journal/database flushing to `sqlite3PagerCommitPhaseOne()`. Commit phase two finalizes the pager journal, downgrades shared state to read, clears `pHasContent`, then `btreeEndTransaction()` releases table locks or downgrades them if other VDBE readers still need a read transaction. Rollback saves or trips cursors, rolls back the pager, reloads page-1 metadata, clears write-transaction state, and ends the btree transaction.

### Btree page and cursor flow

Pager pages are converted into `MemPage` objects stored in pager extra memory. `btreeInitPage()` decodes the page type, initializes offsets and function pointers, records the cell count, and optionally performs cell-size checks. Cell parsing distinguishes table leaf cells, table interior cells without payload, and index cells; overflow sizing follows SQLite's fixed local/overflow distribution formula.

Page allocation inside a btree page uses the freeblock chain first, then defragments if needed, then allocates by lowering the cell-content top pointer. Freeing coalesces adjacent freeblocks, updates fragment counts, optionally zeroes deleted bytes under secure-delete flags, and maintains `nFree`.

Before modifying pages, the code saves cursor positions. Table cursors save rowid only; index cursors copy the full packed key with padding to tolerate later unpacking. Saved cursors release page references and move to `CURSOR_REQUIRESEEK`; restoration later seeks back and may become `CURSOR_SKIPNEXT` if the exact row moved or disappeared.

`btreeCursor()` validates transaction and write preconditions, handles empty database root cases, initializes the caller-provided cursor memory, marks cursors as `BTCF_Multiple` when another cursor uses the same root, links into `BtShared.pCursor`, chooses pager readonly flags for read cursors, and allocates temporary cell space for the first write cursor.

## State and Persistence Behavior

- WAL state is split between the persistent WAL file, the shared-memory wal-index, lock bytes, and private `Wal` fields. Important private fields in this chunk include `hdr`, `readLock`, `writeLock`, `ckptLock`, `minFrame`, `iCallback`, `iReCksum`, `truncateOnCommit`, and snapshot pointers/flags.
- WAL persistence is guarded by frame checksums, salts, sync policy, checkpoint backfill counters, and header comparison after locks are obtained. The code is careful to retry instead of trusting a snapshot if a writer or checkpointer may have changed the log between observing and locking.
- Btree persistent state is the SQLite database file page format: page 1 file header, btree page headers, cell pointer arrays, cell content/freeblock areas, overflow chains, freelist trunk/leaf pages, and optional pointer-map pages.
- `BtShared` holds process-local interpretation of a database file: page size, usable size, payload limits, transaction counters, read-only/fixed-page-size/secure-delete flags, and the page-1 reference. These fields are guarded by `BtShared.mutex`.
- Shared-cache table locks are in-memory only (`BtShared.pLock`, `pWriter`, `BTS_PENDING`, `BTS_EXCLUSIVE`) and are cleared/downgraded on transaction end.
- `pHasContent` is a transient transaction bitvec used so rollback journaling remains correct when a page is freed and then reused in the same write transaction.
- Auto-vacuum pointer maps are persistent pages. Relocation updates both child/overflow pointer maps and the parent page pointer before shrinking the database image.
- Pager integration is responsible for durable journaling, rollback, savepoint storage, WAL opening, page reference counts, syncing, file-size/page-count discovery, mmap/cache/spill settings, and busy-handler invocation.

## Dependencies and Integration Points

- The WAL code depends on SQLite VFS and pager-adjacent primitives: `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsFileSize()`, `sqlite3OsUnfetch()`, WAL lock helpers, wal-index hash/page helpers, atomic shared-memory access, and `SEH_TRY` wrappers.
- The btree layer depends heavily on the pager API: `sqlite3PagerOpen()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerBegin()`, `sqlite3PagerRollback()`, `sqlite3PagerCommitPhaseOne/Two()`, `sqlite3PagerOpenSavepoint()`, `sqlite3PagerSavepoint()`, `sqlite3PagerMovepage()`, cache/mmap/spill setters, WAL open/write-lock helpers, page refcount/unref functions, and the `pageReinit()` callback.
- Shared-cache behavior integrates with `sqlite3` connection mutexes, `sqlite3ConnectionBlocked()`, `sqlite3GlobalConfig.sharedCacheEnabled`, `SQLITE_MUTEX_STATIC_OPEN`, `SQLITE_MUTEX_STATIC_MAIN`, and database handle lists.
- Cursor movement integrates with VDBE record handling through `sqlite3VdbeAllocUnpackedRecord()`, `sqlite3VdbeRecordUnpack()`, `sqlite3BtreeIndexMoveto()`, and `sqlite3BtreeTableMoveto()`.
- Database file interpretation depends on endian helpers (`get2byte`, `get4byte`, `put2byte`, `put4byte`), varint decoders, corruption reporting macros, and compile-time options such as `SQLITE_OMIT_WAL`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_ENABLE_CURSOR_HINTS`, and `SQLITE_SECURE_DELETE`.
- WiredTiger uses this SQLite amalgamation as third-party test code, so integration risk is mostly inherited SQLite behavior and compile-option compatibility rather than direct WiredTiger storage-engine code.

## Risks and Edge Cases

- WAL reader correctness depends on rechecking read marks and wal-index headers after locks. Missing those retries could let a reader combine database pages and WAL frames from incompatible snapshots.
- Snapshot mode is sensitive to races with checkpointers. The code takes a shared checkpoint lock and uses `nBackfillAttempted`, but older snapshot availability still depends on checkpoint progress and WAL salts.
- WAL checksum repair after overwriting frames in the current transaction is subtle: `pWal->iReCksum` must cover the earliest overwritten frame before commit.
- Passive checkpoint semantics are fragile: it must not invoke busy handlers or block on locks except as allowed, while FULL/RESTART/TRUNCATE may downgrade to passive behavior if writer-lock acquisition fails.
- Btree page parsing is security- and corruption-sensitive. The code checks freeblock order, cell offsets, usable-size bounds, max cell count, valid page flags, overflow pointer bounds, and 65536-byte page special cases.
- Free-space management must maintain exact fragment counts and ordered freeblock chains. Incorrect coalescing or allocation can corrupt page layout or break later integrity checks.
- Cursor preservation is memory-sensitive for index keys: the code allocates padding because later record unpacking may overread corrupt keys by a bounded amount.
- Shared-cache locking has deadlock and starvation risks. `BTS_PENDING` prevents new transactions while a writer waits, and `btreeBeginTrans()` deliberately avoids busy-handler invocation for read-to-write upgrade deadlock cases.
- Auto-vacuum relocation must update parent pointers, overflow pointers, and pointer-map entries consistently. A missed pointer-map update can make subsequent vacuum or integrity checks fail.
- Page-size and WAL-mode negotiation in `lockBtree()` may require retrying with `pBt->pPage1==0`; callers must preserve that loop.
- The chunk ends mid-function, so any analysis of `sqlite3BtreeCursor()` must be reconciled with the next chunk before producing a final per-file report.

## Test Signals

- WAL evidence/test macros in this chunk include `testcase()` branches for busy, IO, protocol, page-size bounds, WAL sync padding, and checkpoint return cases; `WALTRACE()` emits frame/checkpoint/read/write tracing in debug/test builds.
- `SQLITE_ENABLE_EXPENSIVE_ASSERT` in `walFindFrame()` linearly scans WAL frames to assert that hash-table lookup found the same result.
- Many Btree paths use `testcase()` and TH3 references around corrupt database page layouts, such as corrupt page flags, bad freeblock chains, cell offsets, page size, and WAL/database page-size mismatches.
- Debug-only functions and asserts check mutex ownership, shared-cache table locks, read conflicts, cursor ownership, cell-size parse equivalence, transaction-state integrity, and open cursor counts.
- Fault-injection hooks include `SEH_TRY`/`SEH_EXCEPT`, `SEH_INJECT_FAULT`, `sqlite3FaultSim(410)`, and malloc failure branches.
- Runtime validation signals include return codes `SQLITE_CORRUPT_BKPT`, `SQLITE_CORRUPT_PAGE`, `SQLITE_NOTADB`, `SQLITE_BUSY`, `SQLITE_BUSY_SNAPSHOT`, `SQLITE_LOCKED_SHAREDCACHE`, `SQLITE_READONLY`, `SQLITE_NOMEM_BKPT`, `SQLITE_DONE`, and `SQLITE_ERROR_SNAPSHOT`.
- User-visible SQL exercises that would traverse this chunk include WAL-mode reads/writes/checkpoints/snapshots, shared-cache reads and write conflicts, `PRAGMA page_size`, `PRAGMA secure_delete`, `PRAGMA auto_vacuum`, `VACUUM`/incremental vacuum, transaction commit/rollback/savepoint behavior, incremental blob invalidation, and opening cursors on tables/indexes.
