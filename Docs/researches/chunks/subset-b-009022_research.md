# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 76299-83658

## Scope

This chunk is the main middle of SQLite's btree implementation in the WiredTiger vendored SQLite amalgamation. It starts with cursor lifecycle and payload access helpers, then covers cursor navigation, table/index search, page allocation and free-list management, cell construction, page editing, btree balancing, insert/delete/table lifecycle operations, btree metadata access, integrity checking, and the beginning of the online backup implementation.

The preceding chunk sets up the lower-level btree page parsing, cursor opening, shared-cache/transaction context, and helper types used here. The following chunk continues from the middle of `sqlite3_backup_finish()` into the rest of backup, pager integration, and later SQLite subsystems.

## Purpose

This range turns parsed btree pages into the core row/index operations used by the VDBE and schema layer. Its responsibilities are:

- Maintain `BtCursor` state while reading, seeking, and walking table or index btrees.
- Read and write payload bytes that may be split between a local cell body and linked overflow pages.
- Allocate, free, and recycle database pages through the file-header freelist and autovacuum pointer maps.
- Construct and remove cells, including overflow chains.
- Rebalance btree pages after inserts and deletes, including special root-height changes.
- Create, clear, and drop table/index root pages while preserving autovacuum root-page layout.
- Expose btree metadata, row counts, transaction/checkpoint helpers, and incremental-blob writes.
- Verify btree, freelist, overflow-chain, pointer-map, and page-coverage integrity for `PRAGMA integrity_check`.
- Begin implementing `sqlite3_backup_*` by wiring source/destination btrees and copying pages through the pager.

## Important APIs, Types, and Functions

- Cursor lifecycle and cached cell information:
  - `sqlite3BtreeCursorSize()` exposes the rounded `BtCursor` storage size to callers that preallocate opaque cursors.
  - `sqlite3BtreeCursorZero()` initializes a cursor while intentionally skipping large page/index stack arrays.
  - `sqlite3BtreeCloseCursor()` unlinks a cursor from `BtShared.pCursor`, releases held pages, clears overflow/key caches, and closes single-use btrees when appropriate.
  - `getCellInfo()` lazily fills `BtCursor.info` using `btreeParseCell()` and marks `BTCF_ValidNKey`.
  - `sqlite3BtreeCursorIsValidNN()`, `sqlite3BtreeIntegerKey()`, `sqlite3BtreeOffset()`, `sqlite3BtreePayloadSize()`, `sqlite3BtreeMaxRecordSize()`, `sqlite3BtreeCursorPin()`, and `sqlite3BtreeCursorUnpin()` expose cursor status, rowid/payload metadata, file offsets, and pin state.

- Payload and overflow access:
  - `getOverflowPage()` follows an overflow chain, using autovacuum pointer-map entries as a fast path when possible.
  - `copyPayload()` centralizes page-cache write barriers for payload copy operations.
  - `accessPayload()` reads or writes a byte range from a cursor's current payload, spanning local cell bytes and overflow pages, maintaining `BtCursor.aOverflow` as a lazy page-number cache.
  - `sqlite3BtreePayload()` and `sqlite3BtreePayloadChecked()` expose payload reads; the checked variant restores cursor position for incremental blob reads.
  - `fetchPayload()` and `sqlite3BtreePayloadFetch()` return a direct ephemeral pointer to local payload bytes for the common no-overflow case.
  - `sqlite3BtreePutData()` writes fixed-size incremental blob data through `accessPayload()` after restoring/saving cursors and validating write locks.

- Cursor movement and search:
  - `moveToChild()`, `moveToParent()`, `moveToRoot()`, `moveToLeftmost()`, and `moveToRightmost()` maintain the cursor page stack (`apPage[]`, `aiIdx[]`, `iPage`, `ix`) and validate page type consistency.
  - `sqlite3BtreeFirst()` and `sqlite3BtreeLast()` position cursors at the first/last entry, with `BTCF_AtLast` optimization for repeated last-entry checks.
  - `sqlite3BtreeTableMoveto()` performs integer-key table search with binary search per page and a fast adjacent-key/append path.
  - `sqlite3BtreeIndexMoveto()` performs index-key search using `UnpackedRecord`, `RecordCompare`, direct local-cell comparison where possible, and `accessPayload()` for overflow index keys.
  - `sqlite3BtreeNext()` and `sqlite3BtreePrevious()` implement forward/backward cursor stepping, including restoration from `CURSOR_REQUIRESEEK`/`CURSOR_SKIPNEXT`.
  - `sqlite3BtreeEof()` and `sqlite3BtreeRowCountEst()` provide EOF and approximate row-count signals.

- Page allocation, freelist, overflow clearing:
  - `allocateBtreePage()` obtains a page from the freelist or extends the database image. It supports `BTALLOC_ANY`, exact-page allocation, and less-than-or-equal allocation for autovacuum relocation.
  - `freePage2()` and `freePage()` put a page on the freelist, zeroing content under `BTS_SECURE_DELETE` and updating autovacuum pointer maps.
  - `clearCellOverflow()` walks and frees overflow pages for a cell, rejecting impossible page numbers and unexpected extra references.
  - `BTREE_CLEAR_CELL` parses a cell and clears overflow only when payload spills off-page.

- Cell creation and page editing:
  - `fillInCell()` serializes a `BtreePayload` into SQLite cell format, including local payload sizing, overflow-page allocation, zero-fill for zeroblobs, and pointer-map entries.
  - `dropCell()` removes a cell pointer from a page and returns its content area to the in-page freeblock list.
  - `insertCell()` and `insertCellFast()` insert local cells or stage overflow cells in `MemPage.apOvfl[]` when a page is temporarily overfull.
  - `CellArray`, `populateCellCache()`, `cachedCellSize()`, `rebuildPage()`, `pageInsertArray()`, `pageFreeArray()`, and `editPage()` are the balancing workbench: they cache ordered cell pointers/sizes and rewrite pages while avoiding overlap/corruption hazards.

- Balancing and mutation:
  - `balance_quick()` handles the append-heavy case by allocating a new right sibling for a single rightmost overflow cell.
  - `copyNodeContent()`, `balance_nonroot()`, and `balance_deeper()` handle page redistribution, root growth, root shrinking, pointer-map repair, page-number reordering, and old-page freeing.
  - `balance()` chooses among quick, deeper, and non-root balancing and walks upward until parent pages are also fixed.
  - `btreeOverwriteContent()`, `btreeOverwriteOverflowCell()`, and `btreeOverwriteCell()` optimize same-size replacements by writing only changed bytes in local and overflow storage.
  - `sqlite3BtreeInsert()` inserts or replaces table/index entries, saves other cursors, invalidates incremental blobs, builds cells or consumes preformatted transfer cells, clears replaced overflow, and rebalances.
  - `sqlite3BtreeTransferRow()` preformats a row from one btree cursor into another btree's temp cell buffer, allocating destination overflow pages as needed.
  - `sqlite3BtreeDelete()` deletes the current entry, optionally preserves cursor position, replaces internal-node separators from the predecessor leaf, frees overflow, and rebalances.

- Table, metadata, and count APIs:
  - `btreeCreateTable()` / `sqlite3BtreeCreateTable()` allocate and initialize new root pages. In autovacuum databases they keep root pages dense near the front by relocating pages and updating `BTREE_LARGEST_ROOT_PAGE`.
  - `clearDatabasePage()`, `sqlite3BtreeClearTable()`, and `sqlite3BtreeClearTableOfCursor()` recursively clear table content and optionally count deleted cells.
  - `btreeDropTable()` / `sqlite3BtreeDropTable()` clear and free a root page, relocating the maximum root page into the gap under autovacuum.
  - `sqlite3BtreeGetMeta()` and `sqlite3BtreeUpdateMeta()` read/write database header meta slots, with `BTREE_DATA_VERSION` sourced from the pager and `BTREE_INCR_VACUUM` mirrored into `BtShared.incrVacuum`.
  - `sqlite3BtreeCount()` traverses all non-overflow btree pages and counts leaf entries, with interrupt checks.
  - `sqlite3BtreePager()`, `sqlite3BtreeGetFilename()`, `sqlite3BtreeGetJournalname()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCheckpoint()`, `sqlite3BtreeIsInBackup()`, `sqlite3BtreeSchema()`, `sqlite3BtreeSchemaLocked()`, `sqlite3BtreeLockTable()`, `sqlite3BtreeSetVersion()`, `sqlite3BtreeCursorHasHint()`, `sqlite3BtreeIsReadonly()`, `sqlite3HeaderSizeBtree()`, `sqlite3BtreeClearCache()`, `sqlite3BtreeSharable()`, and `sqlite3BtreeConnectionCount()` are support APIs used by pager, WAL, schema, shared-cache, backup, tests, and higher layers.

- Integrity checking:
  - `checkOom()`, `checkProgress()`, `checkAppendMsg()`, `getPageReferenced()`, `setPageReferenced()`, `checkRef()`, `checkPtrmap()`, `checkList()`, `btreeHeapInsert()`, `btreeHeapPull()`, `checkTreePage()`, and `sqlite3BtreeIntegrityCheck()` implement btree integrity validation.
  - The checker tracks page references in a bitmap, verifies freelist and overflow chains, checks autovacuum pointer maps, enforces rowid ordering and balanced tree depth, and uses a min-heap of byte ranges to detect overlapping cell/freeblock storage and fragmentation-count mismatches.

- Backup API beginning:
  - `struct sqlite3_backup` stores source/destination handles, current page number, error state, page counts, and pager-callback linkage.
  - `findBtree()`, `setDestPgsz()`, `checkReadTransaction()`, `sqlite3_backup_init()`, `isFatalError()`, `backupOnePage()`, `backupTruncateFile()`, `attachBackupObject()`, and the opening of `sqlite3_backup_step()` begin the online backup implementation.

## Control Flow

Cursor reads start by ensuring the cursor is valid and that its page and cell index are coherent. `getCellInfo()` parses the cell only once per cursor position. Local payload bytes are copied directly from the current page. If the requested range extends past `nLocal`, `accessPayload()` follows the overflow chain, optionally jumping through `aOverflow[]` when prior calls have cached page numbers. Reads may use direct file I/O for full overflow pages when `SQLITE_DIRECT_OVERFLOW_READ` is enabled and pager conditions permit. Writes always go through `sqlite3PagerWrite()` before modifying page bytes.

Search and traversal are layered. `moveToRoot()` restores or obtains the root page, handles virtual root page 1, validates table-vs-index page type, and sets `CURSOR_VALID` or `CURSOR_INVALID`. Table seeks (`sqlite3BtreeTableMoveto()`) binary-search integer keys on each page and descend through child pointers until a leaf. Index seeks (`sqlite3BtreeIndexMoveto()`) compare serialized records against `UnpackedRecord`; small local keys avoid extra allocation, while overflow keys are copied into a padded heap buffer before record comparison. `Next` and `Previous` use fast leaf-local index increments/decrements when possible and fall back to parent/child stack navigation otherwise.

Page allocation first tries the freelist recorded in page 1 header fields at offsets 32 and 36. It can extract a trunk page, a leaf page from a trunk, or search for a requested page in autovacuum modes. If no freelist page is available, it extends `BtShared.nPage`, skips the pending-byte page, creates pointer-map pages when needed, updates the database size in page 1, obtains the new page from the pager, and marks it writable. Freeing a page increments the freelist count, optionally zeroes content for secure delete, writes pointer-map state, and either appends the page as a freelist leaf or turns it into a new trunk.

Insertion builds a new cell in `BtShared.pTmpSpace` unless `BTREE_PREFORMAT` is supplied. Same-key, same-size replacements can use in-place overwrite, including overflow pages. Otherwise old overflow is cleared, the old cell is dropped, and the new cell is inserted into the leaf or temporarily staged in `apOvfl[]` if the page does not have room. If a page overflows, `balance()` repairs the tree, possibly growing the root first with `balance_deeper()`, using `balance_quick()` for rightmost append patterns, or redistributing siblings with `balance_nonroot()`.

`balance_nonroot()` is the densest control-flow block in this range. It selects up to three old sibling pages plus divider cells from the parent, removes relevant parent divider cells, creates a `CellArray` containing all sibling/divider/overflow cells in sort order, computes how many pages are needed, adjusts cell packing from right to left so pages are legal and reasonably balanced, allocates or reuses pages, optionally reorders page numbers for scan locality, repairs pointer maps, reinserts divider cells into the parent, rewrites sibling pages in an order that avoids overwriting source cells before they are copied, handles root-shrink when a root has a single child, and frees old pages that are no longer reused.

Deletion restores the cursor if needed, may save the current key to preserve position, and for internal-node cells first moves to the predecessor leaf. It writes the target page, frees overflow, drops the cell, then for internal-node deletes copies the predecessor cell into the internal page and removes it from the leaf. It balances the leaf first and then, when necessary, climbs back to balance the original internal page. Depending on `BTREE_SAVEPOSITION`, it leaves the cursor invalid, in `CURSOR_REQUIRESEEK`, or in `CURSOR_SKIPNEXT`.

Table creation and drop are autovacuum-aware. Creation chooses a root page after the current largest root page, avoiding pointer-map and pending-byte pages. If the allocated page differs from the desired root page, it relocates the current page at the root slot elsewhere, updates pointer maps, then zeroes the new root with table or index page flags. Drop clears all descendants first, then either frees the root directly or moves the highest-numbered root page into the dropped root slot and decrements the header's largest-root-page metadata.

The integrity-check path starts by allocating a page-reference bitmap and a page-sized heap, marks the pending-byte page as referenced, optionally scans the freelist, then recursively checks each requested root. `checkTreePage()` reinitializes each page to exercise corruption detection, verifies rowid ordering from right to left, validates overflow-chain lengths, checks child depths, and uses heap-sorted byte spans to ensure page header/cell-pointer area, cells, and freeblocks do not overlap and that untracked fragmented bytes match the page header.

The backup path begins by validating source/destination handles, rejecting same-connection source/destination pairs, resolving database names to btrees, ensuring the destination has no open transaction, and incrementing the source btree's backup count. `sqlite3_backup_step()` locks source and destination, opens a source read transaction if needed, starts a destination write transaction, enforces WAL/memory page-size constraints, copies source pages through `backupOnePage()`, attaches the backup object to the source pager when incomplete, and on completion updates the destination schema cookie and begins page-size-sensitive truncation/commit handling. This chunk ends inside `sqlite3_backup_finish()`.

## State and Persistence Behavior

`BtCursor` state is highly transient but correctness-critical. Movement invalidates `BtCursor.info.nSize`, `BTCF_ValidNKey`, and `BTCF_ValidOvfl`. `apPage[]` and `aiIdx[]` retain the ancestry stack for navigation and balancing. `BTCF_AtLast` is an optimization flag that must be cleared on movement except when explicitly set by last-entry positioning. `CURSOR_REQUIRESEEK`, `CURSOR_SKIPNEXT`, and `CURSOR_INVALID` encode deferred restoration after writes or deletes.

Payload persistence is split between page-local cell bytes and overflow pages. Overflow pages store a 4-byte next-page number followed by payload bytes. `BtCursor.aOverflow` is only a cache; it must be invalidated after cursor movement, writes by other cursors, table changes, and autovacuum page moves. The durable state is the cell body plus overflow-chain pages and, in autovacuum databases, pointer-map entries for `PTRMAP_OVERFLOW1` and `PTRMAP_OVERFLOW2`.

Free-space and page-allocation state is durable in page 1 and freelist trunk/leaf pages. Header offset 32 stores the first freelist trunk, offset 36 stores the free-page count, offset 28 stores the database page count, and metadata slot 4 stores the largest root page. Allocation and free operations journal/write page 1 and affected trunk pages through the pager before mutation.

Balancing persists changes across multiple sibling pages, parent divider cells, right-child pointers, pointer maps, and freed pages. Because an error during balancing can leave pages partially modified, callers rely on the surrounding write transaction and pager rollback to restore consistency. This code therefore returns errors promptly but does not try to manually undo every partial page edit.

Table lifecycle operations mutate persistent btree shape and schema-facing metadata. `sqlite3BtreeClearTable()` leaves the root page allocated but empty. `sqlite3BtreeDropTable()` frees or relocates root pages. `sqlite3BtreeUpdateMeta()` writes header metadata and mirrors incremental-vacuum state into memory. `sqlite3BtreeSetVersion()` writes the database header read/write version bytes at offsets 18 and 19, opening a write transaction only if values need changing.

Integrity-check state is in-memory only except for temporary pager page references. It intentionally restores `db->flags` after temporarily disabling `SQLITE_CellSizeCk`, frees `aPgRef` and heap buffers, and asserts that pager reference counts match their entry value.

Backup state persists in `sqlite3_backup` across calls. The destination btree may remain locked after partial backup progress, `iNext` records the next page to copy, `nRemaining` and `nPagecount` report progress, `isAttached` indicates pager callback registration, and `pSrc->nBackup` prevents unsafe source lifecycle changes.

## Dependencies and Integration Points

This code is tightly integrated with SQLite's pager layer: `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerUnref()`, `sqlite3PagerGetData()`, `sqlite3PagerDirectReadOk()`, `sqlite3PagerRekey()`, `sqlite3PagerPageRefcount()`, `sqlite3PagerDontWrite()`, `sqlite3PagerCheckpoint()`, `sqlite3PagerClearCache()`, `sqlite3PagerFilename()`, `sqlite3PagerJournalname()`, `sqlite3PagerDataVersion()`, `sqlite3PagerTempSpace()`, `sqlite3PagerCommitPhaseOne()`, `sqlite3PagerTruncateImage()`, and related file APIs (`sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsTruncate()`, `sqlite3OsFileSize()`, `sqlite3PagerSync()`) enforce journaling, rollback, direct reads, and file-size changes.

Autovacuum support depends on pointer-map helpers (`ptrmapGet()`, `ptrmapPut()`, `ptrmapPutOvflPtr()`, `setChildPtrmaps()`, `relocatePage()`, `PTRMAP_ISPAGE()`, `PTRMAP_PAGENO()`, `PTRMAP_BTREE`, `PTRMAP_ROOTPAGE`, `PTRMAP_FREEPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`). These links are updated whenever cells, child pages, overflow pages, or root pages move.

The VDBE and SQL layers consume table/index cursor APIs for opcodes such as seek, next/prev, insert, delete, count, rowid, payload read, incremental blob, and schema/table creation. Index comparison depends on `UnpackedRecord`, `RecordCompare`, `sqlite3VdbeFindCompare()`, `sqlite3VdbeRecordCompare()`, `KeyInfo`, and record-encoding assumptions.

Shared-cache and transaction correctness use mutexes and locks: `sqlite3BtreeEnter()/Leave()`, `cursorOwnsBtShared()`, `cursorHoldsMutex()`, `hasSharedCacheTableLock()`, `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `hasReadConflicts()`, transaction states (`TRANS_NONE`, `TRANS_READ`, `TRANS_WRITE`), and read-only flags (`BTS_READ_ONLY`).

Memory allocation uses SQLite allocators and stack/page allocators (`sqlite3Malloc()`, `sqlite3MallocZero()`, `sqlite3Realloc()`, `sqlite3_free()`, `sqlite3StackAllocRaw()`, `sqlite3StackFree()`, `sqlite3PageMalloc()`, `sqlite3PageFree()`, `sqlite3DbMallocZero()`). Fault-simulation hooks (`sqlite3FaultSim(412/413)`) intentionally exercise rare corruption/OOM paths.

Integrity check integrates with connection progress and interrupt hooks (`db->xProgress`, `db->nProgressOps`, `AtomicLoad(&db->u1.isInterrupted)`), `sqlite3_str` accumulation, `Mem` counters for per-root row counts, and compile-time gates such as `SQLITE_OMIT_INTEGRITY_CHECK` and `SQLITE_OMIT_AUTOVACUUM`.

Backup integrates with public SQLite handles and parser/database lookup helpers (`sqlite3FindDbName()`, `sqlite3OpenTempDatabase()`, `sqlite3ParseObjectInit()`, `sqlite3ParseObjectReset()`, `sqlite3ErrorWithMsg()`), btree transaction APIs, pager backup callback lists, WAL mode, schema cookie updates, and destination schema reset.

## Risks and Edge Cases

- Cursor cache invalidation is subtle. Reusing `BtCursor.info` or `aOverflow` after movement, writes, balancing, autovacuum relocation, or table creation can read stale page numbers or payload sizes.
- Overflow-chain code must guard integer overflow and corrupt page numbers. This chunk checks payload bounds, premature chain termination, page numbers greater than `nPage`, page 0/1 misuse for overflow, and reference counts before freeing overflow pages.
- Direct overflow reads bypass the page cache only under strict pager conditions. Incorrect conditions could return stale WAL content or miss dirty cache pages.
- `balance_nonroot()` has a large blast radius: it mutates parent cells, sibling pages, pointer maps, page numbers, and freelist state. Any bug can corrupt btree ordering or orphan pages. Its read-before-write ordering and `CellArray.apEnd[]` checks exist to avoid overwriting source cells before they are copied.
- Secure-delete and fast-secure-delete modes affect whether divider cells can be referenced in-place after `dropCell()`. This code copies divider cells to temporary space when zeroing would destroy bytes needed later.
- Autovacuum root-page movement is fragile. Creating or dropping tables can relocate arbitrary pages, including pages that open cursors may have fetched. The code saves all cursors and invalidates overflow caches to avoid stale xFetch references.
- Same-size overwrite optimizations avoid full drop/insert and balancing. They must only be used when pointer-map and overflow invariants remain valid; autovacuum cases with new overflow pages are excluded from the simple overwrite path.
- Incremental blob writes cannot change payload length. They rely on the cursor still pointing to an intkey row and on `accessPayload()` returning corruption instead of partial writes for out-of-range offsets.
- Integrity checking is intentionally tolerant of partial checks. When `aRoot[0]==0`, it skips global freelist/all-pages coverage except for the special root-1 case, so partial integrity checks cannot prove every page is reachable.
- Backup page-size conversion has special pending-byte and WAL/memory-database restrictions. The destination cannot be WAL or in-memory with mismatched page sizes, and final truncation must journal trailing destination pages before destructive file truncation.
- Many branches are compile-time gated (`SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_INCRBLOB`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_WAL`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_OMIT_QUICKBALANCE`), so behavior and test coverage vary by build.

## Test Signals

- Cursor tests should cover first/last, forward/backward iteration over leaf and interior pages, empty tables, virtual root page 1, cursor restoration after writes, `CURSOR_SKIPNEXT`, `CURSOR_REQUIRESEEK`, and repeated `sqlite3BtreeLast()` using `BTCF_AtLast`.
- Payload tests should exercise local-only payloads, single and multi-page overflow chains, partial reads/writes at local/overflow boundaries, direct-overflow-read builds, corrupted overflow next pointers, premature chains, and invalid cell payload offsets.
- Table/index seek tests should cover exact and inexact rowid searches, append-biased inserts, adjacent-key optimization, index keys with local and overflow storage, custom collations/record compares, and OOM while copying overflow index keys.
- Allocation/free tests should cover empty freelists, trunk extraction, leaf extraction, exact-page autovacuum allocation, `BTALLOC_LE`, pending-byte skips, pointer-map pages at file extension, secure-delete zeroing, and invalid freelist counts or leaf counts.
- Balancing tests should force quick balance, root growth, root shrink, sibling redistribution with one/two/three pages, overflow parent cells, page-number reordering, autovacuum pointer-map updates, and rollback after injected pager/OOM errors.
- Insert/delete tests should cover in-place same-size overwrite, replacement with different payload size, index overwrite, rowid table insert with incremental blob invalidation, delete from leaf and internal pages, delete with position preservation, and schema-corrupt duplicate-root cursor cases.
- Table lifecycle tests should cover create/drop under normal and autovacuum modes, max-root-page metadata updates, relocation of highest root page, clearing tables with row-count output, and rejection of out-of-range page numbers.
- Integrity-check tests should detect double page references, invalid child/overflow/freelist page numbers, bad pointer-map entries, rowid ordering errors, child-depth mismatches, overlapping cell/freeblock byte ranges, fragmentation-count mismatches, max-root-page header disagreement, and interrupt/progress-handler cancellation.
- Backup tests should cover same-source/destination rejection, missing database names, opening temp database on demand, destination-in-use rejection, partial step/resume progress, source busy during write transaction, page-size mismatch behavior under WAL/memory destinations, final schema-cookie bump, truncation when source pages are smaller than destination pages, and error persistence through `sqlite3_backup` state.
