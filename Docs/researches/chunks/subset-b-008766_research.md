# sources/storage-engines/sqlite/src/btree.c lines 7569-11600

## Scope

This chunk covers the late btree implementation in SQLite's `btree.c`. It starts inside the `CellArray` balancing data structure comments and includes page reconstruction, sibling balancing, root-depth adjustments, insert/delete paths, table creation/drop/clear helpers, btree metadata access, row counting, integrity checking, and small public utility APIs for filenames, WAL checkpointing, schema storage, shared-cache locking, incremental blob writes, file-format version changes, and cache clearing.

The code is write-path critical. Most routines assume the caller already owns the btree mutex and, for mutations, has a write transaction plus writable pager pages. Error returns from balancing and page relocation usually imply the pager transaction must roll back to avoid a half-mutated btree image.

## Purpose

The main purpose of this range is to maintain btree structural invariants while records are inserted, overwritten, deleted, tables are created/dropped, or integrity checks traverse the database. It handles:

- Redistributing cells across sibling pages after overfull or underfull page mutations.
- Growing or shrinking tree height via root split (`balance_deeper`) and root collapse (`balance_nonroot` shallower path).
- Preserving cell ordering, page free space, overflow-cell ownership, and parent divider cells during balancing.
- Creating and freeing root pages, including auto-vacuum pointer-map and largest-root-page metadata rules.
- Clearing table contents and overflow chains safely.
- Validating full database structure with `sqlite3BtreeIntegrityCheck`.
- Exposing btree-level utility hooks used by pager, schema, WAL, shared-cache, incremental blob, and VDBE layers.

## Important APIs, Types, and Functions

The central local type is `CellArray`. It is a transient view over an ordered sequence of btree cells gathered from up to three sibling pages plus parent divider cells. `apCell[]` points to cells, `szCell[]` caches cell sizes, `pRef` supplies common page parsing callbacks, and `apEnd[]`/`ixNx[]` track the source page boundaries used to detect corrupt overlapping source buffers while cells are copied.

Important balancing helpers:

- `populateCellCache()`, `computeCellSize()`, and `cachedCellSize()` lazily compute cell sizes through `MemPage.xCellSize`.
- `rebuildPage()` reconstructs a page from a `CellArray`, copying self-referential cells through pager temp space and resetting the page header, cell pointer array, fragmented-byte count, `nCell`, and `nOverflow`.
- `pageInsertArray()` incrementally inserts cell-array entries into an existing page, preferably using free slots from `pageFindSlot()`, and reports failure if defragmentation/rebuild is needed.
- `pageFreeArray()` adds existing page-resident cells back to the page free list, coalescing adjacent ranges before calling `freeSpace()`.
- `editPage()` transforms one sibling page from its old slice of the cell array to its new slice, falling back to `rebuildPage()` if in-place editing cannot fit or detects corruption.
- `balance_quick()` handles the append-only rightmost table-leaf special case by allocating a new right sibling, moving the single overflow cell there, and inserting a divider in the parent.
- `copyNodeContent()` copies a node image from one page to another and reinitializes child/overflow pointer maps for auto-vacuum.
- `balance_nonroot()` is the main sibling redistribution algorithm. It gathers old sibling cells and parent dividers, chooses page counts and per-page cell counts, allocates/reuses sibling pages, rekeys page numbers into ascending order, updates pointer maps, inserts new parent dividers, edits sibling pages in dependency-safe order, collapses an empty root when possible, and frees old pages not reused.
- `balance_deeper()` handles an overfull root by allocating a new child, copying the old root into it, installing it as the root right-child, and moving overflow-cell arrays to the child.
- `balance()` dispatches among quick, deeper, and non-root balancing while walking upward toward the root.

Important mutation APIs:

- `sqlite3BtreeInsert()` inserts or replaces a table row or index key. It saves other cursors when needed, seeks if no adjacent cursor position is supplied, uses same-size overwrite optimizations, formats cells through `fillInCell()` or preformatted transfer data, calls `insertCellFast()`, then invokes `balance()` if the page overflows.
- `btreeOverwriteContent()`, `btreeOverwriteOverflowCell()`, and `btreeOverwriteCell()` update same-size payload content in place, including overflow pages, avoiding pager writes when bytes are unchanged.
- `sqlite3BtreeTransferRow()` preformats a cell in the destination btree's temp buffer by copying local and overflow payload from a source cursor, allocating destination overflow pages as required.
- `sqlite3BtreeDelete()` removes the current cursor entry, optionally preserves cursor position, replaces internal-node cells with the predecessor leaf cell, clears overflow chains, drops page cells, and balances the affected leaf/internal paths.

Table and metadata APIs:

- `btreeCreateTable()` / `sqlite3BtreeCreateTable()` allocate and initialize a new root page. In auto-vacuum mode, they keep root pages dense before pointer-map pages and the pending-byte page, relocating an existing page if necessary.
- `clearDatabasePage()`, `sqlite3BtreeClearTable()`, and `sqlite3BtreeClearTableOfCursor()` recursively clear a btree, free child pages and overflow chains, and leave the root page empty when requested.
- `btreeDropTable()` / `sqlite3BtreeDropTable()` clear a table and free its root. In auto-vacuum mode, dropping a non-largest root relocates the largest root page into the gap and updates meta slot 4 (`BTREE_LARGEST_ROOT_PAGE`).
- `sqlite3BtreeGetMeta()` reads database header meta slots, with `BTREE_DATA_VERSION` delegated to the pager data-version counter.
- `sqlite3BtreeUpdateMeta()` writes database header meta slots and updates `BtShared.incrVacuum` when `BTREE_INCR_VACUUM` changes.
- `sqlite3BtreeCount()` traverses all btree pages with a cursor and counts entries, honoring connection interrupts.

Integrity and utility APIs:

- `sqlite3BtreeIntegrityCheck()` orchestrates full or partial integrity checks over root pages, freelist, overflow chains, pointer maps, page coverage, row order, page references, and row counts.
- `checkTreePage()`, `checkList()`, `checkRef()`, `checkPtrmap()`, `btreeHeapInsert()`, and `btreeHeapPull()` implement recursive validation and page byte-coverage checks.
- `sqlite3BtreePager()`, `sqlite3BtreeGetFilename()`, `sqlite3BtreeGetJournalname()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCheckpoint()`, `sqlite3BtreeIsInBackup()`, `sqlite3BtreeSchema()`, `sqlite3BtreeSchemaLocked()`, `sqlite3BtreeLockTable()`, `sqlite3BtreePutData()`, `sqlite3BtreeIncrblobCursor()`, `sqlite3BtreeSetVersion()`, `sqlite3BtreeCursorHasHint()`, `sqlite3BtreeIsReadonly()`, `sqlite3HeaderSizeBtree()`, `sqlite3BtreeClearCache()`, `sqlite3BtreeSharable()`, and `sqlite3BtreeConnectionCount()` expose btree state and integration hooks to the rest of SQLite.

## Control Flow

Insertion starts by stabilizing cursor state. `sqlite3BtreeInsert()` saves peer cursor positions when the cursor can share a root with others, restores or seeks the cursor unless an adjacent position was supplied, invalidates incremental-blob cursors for table rows being replaced, and chooses between overwrite and delete-plus-insert. A same-size payload can be rewritten in place with `btreeOverwriteCell()`. Otherwise the old cell is cleared/dropped, a new cell is assembled in `BtShared.pTmpSpace`, inserted with `insertCellFast()`, and `balance()` is called if the target page now has overflow cells.

`balance()` loops upward. If a page has no overflow and less than or equal to two-thirds free space, it stops. If the root is overfull, it calls `balance_deeper()` once to copy root content into a new child and then balances that child on the next iteration. For non-root pages, it writes the parent, uses `balance_quick()` for the single rightmost append case, otherwise allocates a scratch page buffer and calls `balance_nonroot()`. After each non-root balance it releases the child page and moves the cursor to the parent because the parent may now be overfull or underfull.

`balance_nonroot()` has the densest control flow. It selects up to `NB` old siblings around the target child, removes their divider cells from the parent, gathers all sibling cells and relevant divider cells into `CellArray`, and computes a new packing. The first packing pass may bias cells left; a second pass shifts cells right to avoid empty or badly underfilled right siblings. It allocates or reuses new sibling pages, reorders page numbers for better scan locality, updates auto-vacuum pointer maps for moved cells and overflow chains, inserts new divider cells into the parent, then updates each sibling page in an order that avoids overwriting source cells before they have been copied. If the parent is the root and becomes empty with one child, it defragments the child, copies it into the parent, and frees the child to reduce tree height.

Deletion starts in `sqlite3BtreeDelete()`. If position preservation is requested and balancing may happen, the key is saved into `CURSOR_REQUIRESEEK` state. Internal-node deletion first moves to the predecessor leaf entry, then the leaf cell is inserted into the internal node with the appropriate child pointer before the leaf copy is dropped. The affected page is balanced only if free space exceeds the two-thirds threshold. If an internal-node replacement left the cursor below the original depth, the code climbs back and balances the original internal level as well.

Table creation and drop integrate page allocation with auto-vacuum invariants. Creation chooses the next largest root page, skipping pointer-map and pending-byte pages, then may relocate the page currently occupying that root slot. Drop clears the table first, then either frees the largest root or moves the largest root into the dropped root slot and decrements the largest-root metadata while skipping reserved pages.

Integrity checking allocates a bitset for referenced pages plus a page-sized heap. It optionally checks the freelist, then recurses into each requested root through `checkTreePage()`. That routine reinitializes each page to exercise corruption checks, validates cell offsets and payload/overflow chains, checks rowid ordering, recurses through child pointers, verifies child depths match, then uses a min-heap of cell and freeblock byte ranges to detect overlap and fragmentation-count mismatches. A final full check reports unreferenced pages and pointer-map pages that were incorrectly referenced.

## State and Persistence Behavior

Balancing mutates persistent page images through pager-managed dirty pages. It rewrites btree page headers, cell pointer arrays, cell content areas, freeblock chains, fragmented-byte counters, right-child pointers, parent divider cells, and overflow-chain pointer maps. `MemPage.nFree` is deliberately invalid after low-level page editing until the caller resets it from computed sizes.

The pager is the durability boundary. Mutating functions call `sqlite3PagerWrite()` or operate only on pages already made writable. If a balancing or pointer-map update fails after page content has been changed, the transaction must roll back; comments in this range explicitly rely on rollback for partially mutated parent/sibling state.

Auto-vacuum adds persistent pointer-map and metadata state. New btree pages, moved root pages, child pointers, overflow first pages, overflow continuation pages, free pages, and root pages must all have correct pointer-map entries. `BTREE_LARGEST_ROOT_PAGE` in page-1 metadata is updated during create/drop, and `BTREE_INCR_VACUUM` updates both the file header and `BtShared.incrVacuum`.

Cursor state is heavily managed. Insert/delete may invalidate cursor page stacks, save keys for later reseek, leave a cursor in `CURSOR_SKIPNEXT`, or release all cursor pages after balancing. Incremental blob cursors are invalidated when their row may be replaced, deleted, or a table is cleared. Overflow cache entries are invalidated when pages might be relocated or overflow chains changed.

Integrity checking is mostly read-only but temporarily clears and restores `MemPage.isInit` to force page validation. It also temporarily clears `SQLITE_CellSizeCk` from database flags while scanning, accumulates error text in a `StrAccum`, and writes per-root row counts into caller-provided `Mem` values.

Small utility routines expose or mutate shared btree state: `sqlite3BtreeSchema()` allocates `BtShared.pSchema` and records its destructor; `sqlite3BtreeSetVersion()` writes header bytes 18 and 19 and temporarily sets `BTS_NO_WAL` when forcing rollback-journal format; `sqlite3BtreeClearCache()` asks the pager to drop cache only when no transaction is active.

## Dependencies and Integration Points

This chunk depends on earlier `btree.c` machinery: `MemPage`, `BtShared`, `BtCursor`, `CellInfo`, `BtreePayload`, page parsing callbacks, `findCell()`, `insertCell()`, `insertCellFast()`, `dropCell()`, `freeSpace()`, `defragmentPage()`, `zeroPage()`, `fillInCell()`, `clearCell`, `allocateBtreePage()`, `freePage()`, `relocatePage()`, cursor navigation, and shared-cache lock helpers.

Pager integration is pervasive. The code uses pager temp space, page refcounts, `sqlite3PagerWrite()`, `sqlite3PagerRekey()`, `sqlite3PagerGet()`, `sqlite3PagerUnref()`, `sqlite3PagerFilename()`, `sqlite3PagerJournalname()`, `sqlite3PagerCheckpoint()`, `sqlite3PagerDataVersion()`, `sqlite3PagerRefcount()`, and cache clearing. Page refcount checks are treated as corruption signals in balancing and clearing when a page appears as its own ancestor or is unexpectedly held.

Auto-vacuum integration is through `ptrmapPut()`, `ptrmapGet()`, `ptrmapPutOvflPtr()`, `setChildPtrmaps()`, `PTRMAP_*` types, `PTRMAP_PAGENO()`, and `PTRMAP_ISPAGE()`. Correctness here affects vacuum, page relocation, and corruption detection.

Higher SQLite layers call the public `sqlite3Btree*` APIs from VDBE opcodes, schema management, pager/WAL control, backup handling, incremental blob APIs, and shared-cache table locking. The insert/delete paths rely on VDBE-provided flags such as `BTREE_APPEND`, `BTREE_SAVEPOSITION`, `BTREE_PREFORMAT`, and `BTREE_AUXDELETE`.

Compile-time feature gates shape behavior: `SQLITE_OMIT_QUICKBALANCE`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_INTEGRITY_CHECK`, `SQLITE_OMIT_WAL`, `SQLITE_OMIT_SHARED_CACHE`, and `SQLITE_OMIT_INCRBLOB` include or remove significant branches.

## Risks

- `balance_nonroot()` is high risk because it changes parent and sibling pages together. Off-by-one errors in `cntNew`, `cntOld`, `leafCorrection`, or divider-cell handling can break key ordering or child ownership.
- Source/destination overlap is a recurring corruption hazard. `CellArray.apEnd`/`ixNx`, temp-space copies, and careful page edit ordering protect against reading cells after their source page is overwritten.
- `MemPage.nFree` must be recomputed or explicitly assigned after low-level edits. Using stale free-space values can skip required balancing or corrupt later insertions.
- Auto-vacuum pointer-map updates are security- and durability-sensitive. Missing updates after page rekeying, overflow-chain allocation, table create/drop, root collapse, or transfer-row overflow allocation can make later vacuum relocate the wrong page or report corruption.
- Same-size overwrite optimizations deliberately bypass full drop/insert. They are safe only when payload sizes and local/overflow conditions match and when auto-vacuum does not require a new overflow pointer-map entry.
- Cursor preservation is subtle. Insert/delete can leave cursors invalid, require reseek, or use skip-next semantics; missing a state transition can make subsequent VDBE cursor movement skip or duplicate rows.
- Table create/drop in auto-vacuum mode relocates real pages to keep root pages packed. Errors in reserved-page skipping or largest-root metadata updates can make the database structurally inconsistent.
- Integrity checking recurses through database-controlled page numbers and must cap errors, detect duplicate references, and avoid trusting initialized `MemPage` state from prior use.
- Several routines treat unexpected pager refcounts as corruption. Changes in pager ownership or cursor lifetime rules must keep these assumptions aligned.

## Test and Validation Signals

Useful validation for this chunk includes:

- SQLite btree insert/delete regression tests with random rowid inserts, append-heavy inserts, index inserts, replacements with same-size and different-size payloads, and large payloads using overflow pages.
- Delete tests that remove internal-node separator keys, delete from underfull pages, preserve cursor positions, and exercise `BTREE_SAVEPOSITION`.
- Auto-vacuum and incremental-vacuum tests that create/drop many tables, relocate root pages, allocate/free overflow pages, and run `PRAGMA integrity_check` after each phase.
- Fuzz and corruption tests that target malformed cell offsets, overlapping cells/freeblocks, bad overflow chains, duplicate page references, bad pointer maps, and page refcount anomalies.
- `PRAGMA integrity_check` and `quick_check` coverage for full checks and partial single-table checks, including databases with freelist pages, pointer-map pages, overflow chains, and mixed rowid/WITHOUT ROWID trees.
- WAL checkpoint tests verifying `sqlite3BtreeCheckpoint()` returns `SQLITE_LOCKED` while a shared btree transaction is active and delegates to pager checkpointing otherwise.
- Incremental blob tests that write fixed-length blob slices, reject invalid cursor states, and verify row replacement/delete/table clear invalidates active blob cursors.
- Header metadata tests around schema cookies, data version, largest root page, incremental-vacuum flag, and `sqlite3BtreeSetVersion()` transitions between rollback and WAL file-format version bytes.
- Interrupt/progress tests for `sqlite3BtreeCount()` and integrity checking to verify `SQLITE_INTERRUPT` propagation and bounded error reporting.
