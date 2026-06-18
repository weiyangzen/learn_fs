# sources/storage-engines/foundationdb/contrib/sqlite/btree.c lines 1-7896

## Scope And Purpose

This chunk implements almost all of SQLite's disk-backed b-tree layer as vendored under FoundationDB's SQLite integration. It sits between the SQL/VDBE layer and the pager layer, translating table/index cursor operations into page reads, page writes, cell layout changes, overflow-page management, freelist updates, auto-vacuum pointer-map maintenance, and transaction/savepoint boundaries.

The covered range starts at the file header and runs through metadata update and the beginning of `sqlite3BtreeCount()`. It excludes the later integrity-check and auxiliary tail of the file, but includes the operational core: open/close, shared-cache table locks, page decoding, cursor positioning, payload access, page allocation/freeing, insert/delete, balancing, lazy delete/range delete additions, table create/clear/drop, and b-tree metadata access.

This copy is not a byte-for-byte upstream SQLite file. FoundationDB-specific or nonstandard changes are visible in the database-open page-size handling, disabled/altered pointer-map traversal checks, augmented freelist pointer-map states, partial index-record comparison, and added lazy-delete/range-delete APIs.

## Important APIs, Types, And Functions

Public b-tree entry points in this chunk include `sqlite3_enable_shared_cache`, `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreeBeginTrans`, `sqlite3BtreeCommitPhaseOne`, `sqlite3BtreeCommitPhaseTwo`, `sqlite3BtreeCommit`, `sqlite3BtreeRollback`, `sqlite3BtreeBeginStmt`, `sqlite3BtreeSavepoint`, `sqlite3BtreeCursor`, `sqlite3BtreeCloseCursor`, `sqlite3BtreeFirst`, `sqlite3BtreeLast`, `sqlite3BtreeMovetoUnpacked`, `sqlite3BtreeNext`, `sqlite3BtreePrevious`, `sqlite3BtreeInsert`, `sqlite3BtreeDelete`, `sqlite3BtreeCreateTable`, `sqlite3BtreeClearTable`, `sqlite3BtreeDropTable`, `sqlite3BtreeGetMeta`, and `sqlite3BtreeUpdateMeta`.

The core local types are defined elsewhere but used throughout: `Btree` is the connection-local handle, `BtShared` is the shared pager/cache state, `BtCursor` tracks a cursor stack of `MemPage` references and cell indexes, `MemPage` is the b-tree view of a pager page, `CellInfo` caches decoded cell layout, and `BtLock` represents shared-cache table locks.

Shared-cache locking is handled by `querySharedCacheTableLock`, `setSharedCacheTableLock`, `clearAllSharedCacheTableLocks`, `downgradeAllSharedCacheTableLocks`, and debug-only `hasSharedCacheTableLock`/`hasReadConflicts`. These enforce one writer per shared b-tree and table-level read/write compatibility between `Btree` handles.

Page and cell primitives include `btreeParseCellPtr`, `cellSizePtr`, `defragmentPage`, `allocateSpace`, `freeSpace`, `decodeFlags`, `btreeInitPage`, `zeroPage`, `btreeGetPage`, `getAndInitPage`, `releasePage`, and `pageReinit`. Together these validate on-disk page headers, maintain cell pointer arrays and freeblocks, and keep `MemPage` metadata synchronized with pager data.

Cursor and payload routines include `saveCursorPosition`, `saveAllCursors`, `btreeMoveto`, `btreeRestoreCursorPosition`, `sqlite3BtreeCursorHasMoved`, `accessPayload`, `sqlite3BtreeKey`, `sqlite3BtreeData`, `sqlite3BtreeKeyFetch`, `sqlite3BtreeDataFetch`, `moveToRoot`, `moveToChild`, `moveToParent`, `moveToLeftmost`, and `moveToRightmost`. These preserve cursor semantics while tree pages are modified, support direct local payload access, and traverse overflow chains when payload spills off-page.

Write-path page management is centered on `allocateBtreePage`, `freePage2`, `freePage`, `clearCell`, `fillInCell`, `dropCell`, `insertCell`, `assemblePage`, `balance_quick`, `balance_nonroot`, `balance_deeper`, and `balance`. These functions allocate cells and overflow pages, release overflow chains, manipulate freelist trunks/leaves, split or merge pages, and propagate balancing up toward the root.

Auto-vacuum and pointer-map support is handled by `ptrmapPageno`, `ptrmapPut`, `ptrmapGet`, `ptrmapPutOvflPtr`, `setChildPtrmaps`, `modifyPagePointer`, `relocatePage`, `incrVacuumStep`, `sqlite3BtreeIncrVacuum`, and `autoVacuumCommit`. This chunk adds `PTRMAP_LAZYFREE` and distinguishes `PTRMAP_FREEPAGE` from `PTRMAP_FREELEAF` in several freelist paths.

FoundationDB-added deletion helpers include `sqlite3BtreeLazyDelete`, `deleteCellRange`, `swapChildren`, and `sqlite3BtreeDeleteRange`. They use an integer stack and a cursor-backed lazy-free table to delete whole page subtrees incrementally rather than synchronously walking and freeing all descendant pages in one call.

## Control Flow

Opening starts in `sqlite3BtreeOpen`. It creates a `Btree`, optionally attaches to an existing `BtShared` via shared cache, otherwise opens a pager and reads the first 100-byte database header. This version deliberately sets `pBt->pageSize = 0` instead of trusting a valid-looking initial header field, with comments explaining that a correct page 1 may exist in WAL and a checksumming pager codec can fail if initialized with a corrupt stale header's page size. `lockBtree` later reads page 1 through the pager, validates the magic header and format bytes, opens WAL if required, adjusts page size/reserve size, computes local payload thresholds, and pins `pBt->pPage1`.

Transactions flow through `sqlite3BtreeBeginTrans`. It checks read-only and shared-cache conflicts, obtains a page-1 read lock, repeatedly calls `lockBtree` until page 1 is initialized, begins the pager write transaction for write cases, creates a new database image if the file is empty, updates `Btree`/`BtShared` transaction state, and ensures pager savepoint slots match the connection's active savepoints. Commit phase one optionally runs full auto-vacuum compaction before `sqlite3PagerCommitPhaseOne`; phase two commits the pager and calls `btreeEndTransaction` to clear locks, free `pHasContent`, downgrade or close transactions, and release page 1 when no cursors remain. Rollback saves/trips cursors, rolls the pager back, reloads page count from page 1, and ends the transaction.

Cursor open and movement are layered. `btreeCursor` links a zeroed cursor into `BtShared.pCursor` after checking lock and transaction invariants. `moveToRoot` positions on the root or virtual root, verifies expected table/index page type, and marks empty trees invalid. `sqlite3BtreeMovetoUnpacked` performs a binary search on each page, comparing integer rowids directly for table b-trees and unpacked records for index b-trees, then descends through child pointers until a leaf or exact match is found. `sqlite3BtreeNext` and `sqlite3BtreePrevious` restore deferred cursor positions, step within the current page, and walk up/down the page stack as needed.

Payload reads and writes start with decoded `CellInfo`. If requested bytes are local, `copyPayload` reads or writes the page directly. If bytes spill to overflow pages, `accessPayload` follows the overflow chain, optionally using `BtCursor.aOverflow` for incremental blob cursors. The pointer-map shortcut in `getOverflowPage` is compiled out in this copy, and comments say traversal should validate child-parent links; however `verifyParentChildLink` itself is currently compiled as a no-op macro, so that intended validation is not active in this chunk.

Insertion calls `saveAllCursors`, seeks if the caller did not provide a prior search result, builds the new cell with `fillInCell`, deletes the old cell on replace, inserts the new cell or records it as an overflow cell, and calls `balance` if the page overflowed. `fillInCell` writes the cell header, decides local versus overflow payload bytes, allocates overflow pages, links overflow pages together, and populates pointer-map entries for auto-vacuum databases.

Deletion in `sqlite3BtreeDelete` verifies a writable cursor, invalidates incremental blob cursors, replaces internal-node cells with predecessor leaf cells when needed, frees overflow pages with `clearCell`, drops the cell from the page, and calls `balance` on the affected leaf and possibly the original internal node. `balance` chooses between root deepening, quick right-edge split, or full non-root sibling redistribution. `balance_nonroot` collects cells from up to three siblings plus parent dividers, repacks them into old or newly allocated pages, frees unused pages, inserts new divider cells, and repairs pointer-map entries for moved children and overflow chains.

Table creation, clearing, and dropping are page-management wrappers. `btreeCreateTable` allocates a root page, moves pages as needed in auto-vacuum mode so root pages remain compact, marks the root in pointer-map metadata, updates largest-root metadata, and initializes the page as either intkey table or zerodata index. `clearDatabasePage` recursively clears cells, overflow chains, and child pages. `btreeDropTable` clears the table, frees or moves root pages, and updates largest-root metadata when auto-vacuum is enabled.

## State And Persistence Behavior

Persistent database state is stored in pager pages. Page 1 contains the file header, page count at offset 28, freelist trunk pointer/count at offsets 32 and 36, and metadata slots beginning at offset 36. This chunk reads and writes those fields through `get4byte`/`put4byte` and always marks page 1 writable before mutating them.

Each b-tree page stores a compact on-disk header, a cell pointer array, cell content at the end of the usable page region, and a linked list of freeblocks. `btreeInitPage` reconstructs volatile `MemPage` fields from that image. `dropCell`, `insertCell`, `freeSpace`, `allocateSpace`, and `defragmentPage` update both the raw bytes and `MemPage` counters such as `nCell`, `nFree`, and `nOverflow`.

Overflow payload is persisted as linked overflow pages with the next-page number in the first four bytes. `clearCell` must free every overflow page when a cell is deleted or replaced. `fillInCell` must write all overflow links before the new cell is installed. In auto-vacuum mode, first overflow pages are recorded as `PTRMAP_OVERFLOW1` and subsequent pages as `PTRMAP_OVERFLOW2`.

The freelist is stored as trunk pages with arrays of leaf page numbers. `freePage2` increments the free count and either appends a page as a leaf of the first trunk or makes it the new trunk. `allocateBtreePage` decrements the count and reuses a requested or nearby free page where possible, otherwise extends the file and skips pointer-map or pending-byte pages. This copy adds logic for truncated freelist leaves and pointer-map entries that can point from free leaves to their parent trunk.

`BtShared.pHasContent` is a transaction-local bitvec that records pages that had meaningful content before becoming freelist leaves. It prevents no-content pager optimizations from making rollback unable to restore a page that is freed and then reused in the same transaction. It is cleared at transaction end.

Auto-vacuum persistence depends on pointer-map pages. `relocatePage` moves a page at the pager layer, updates child pointer-map entries, and rewrites the parent pointer that referenced the old page number. `autoVacuumCommit` repeatedly moves pages out of the tail of the file, clears the freelist, truncates the pager image, and updates page count.

Cursor state is partly persistent only by reference: cursors hold page references and cell indexes but do not persist to disk. Before structural mutations, `saveAllCursors` stores keys for other valid cursors and releases page references so they can be restored later with `btreeRestoreCursorPosition`.

`sqlite3BtreeLazyDelete` persists pending subtree roots in a cursor table as integer payloads keyed by monotonically increasing rowids. It also marks roots in pointer-map entries as `PTRMAP_LAZYFREE` so vacuum/allocation code can recognize lazily freed pages.

## Dependencies And Integration Points

The b-tree layer depends heavily on the pager API: `sqlite3PagerOpen`, `sqlite3PagerAcquire`, `sqlite3PagerGet`, `sqlite3PagerWrite`, `sqlite3PagerBegin`, `sqlite3PagerCommitPhaseOne`, `sqlite3PagerCommitPhaseTwo`, `sqlite3PagerRollback`, `sqlite3PagerMovepage`, `sqlite3PagerTruncateImage`, WAL open/checkpoint behavior, page refcounts, and pager temp/scratch space.

It integrates with SQLite connection state through `sqlite3`, database mutexes, busy handlers, `sqlite3GlobalConfig.sharedCacheEnabled`, VFS lookup, savepoint counts, active VDBE counts, read-uncommitted flags, and memory allocation failure propagation.

The VDBE/index layer integrates through cursor APIs, key/data fetch APIs, `UnpackedRecord`, `KeyInfo`, `sqlite3VdbeRecordUnpack`, `sqlite3VdbeRecordCompare`, and `sqlite3VdbeDeleteUnpackedRecord`. This copy's `sqlite3BtreeMovetoUnpacked` adds a partial-record comparison path for overflow index keys: it compares local bytes first and only loads full payload if the comparator reports that more data is required.

Shared-cache integration uses connection-blocking diagnostics via `sqlite3ConnectionBlocked` and table-level locks rooted at page numbers. Schema/index assertions in debug builds use `Schema`, `Index`, and SQLite hash iteration to verify that index writes hold locks on the owning table root.

Auto-vacuum integration depends on file-format metadata, pointer-map page placement, `PENDING_BYTE_PAGE`, and root-page compaction rules. Table create/drop paths update `BTREE_LARGEST_ROOT_PAGE`; metadata APIs read/write the schema-layer cookies and incremental-vacuum flag.

Incremental blob support integrates through cursor flags and overflow-cache invalidation. Any table modification, auto-vacuum move, create table, or full auto-vacuum commit can invalidate open incremental blob cursors or their cached overflow lists.

FoundationDB integration signals are visible in comments and APIs rather than direct FoundationDB calls in this chunk. The b-tree remains pager-backed SQLite code, but with modifications likely serving FoundationDB's SQLite storage semantics: cautious page-size initialization for WAL/codecs, augmented pointer-map expectations (`g_expect_full_pointermap`), lazy-free state, and range deletion helpers.

## Risks And Edge Cases

Page-format corruption handling is pervasive and security-sensitive. Many routines return `SQLITE_CORRUPT_BKPT` on impossible offsets, invalid freeblock chains, too many cells, overflow pages outside the file, root-page misuse, incompatible page flags, or pointer-map inconsistencies. Small mistakes in cell-size calculation, freeblock coalescing, or pointer-array movement can corrupt the database image.

The disabled `verifyParentChildLink` is a notable risk. Comments in `getOverflowPage`, `accessPayload`, `moveToChild`, and `clearCell` describe validating child-parent links before following pointers, but the helper is compiled out. If FoundationDB relies on full pointer-map validation, this chunk does not currently enforce it.

Pointer-map state is more complex than upstream SQLite because `PTRMAP_FREELEAF` and `PTRMAP_LAZYFREE` are accepted in addition to normal states. `allocateBtreePage`, `incrVacuumStep`, and lazy delete must agree on these values. A stale or partially populated pointer map can cause wrong freelist searches, premature vacuum completion, or allocation of the wrong page.

`allocateBtreePage` has high blast radius. It mutates page-1 freelist count before walking trunks, may skip to a parent trunk using pointer-map data, compacts truncated leaves, can promote a freelist leaf into a trunk, and must release every page reference along error paths. Regression here can leak pages, double-allocate pages, or leave the freelist count inconsistent with its trunk chain.

Balancing is another high-risk area. `balance_nonroot` relies on scratch memory layouts, copied page images, divider-cell transformations, leaf/non-leaf differences, and parent overflow-cell handling. It intentionally may leave the database corrupt on error with the expectation that the caller rolls back. Tests should treat any new error path in balancing as transaction-rollback-sensitive.

`sqlite3BtreeDeleteRange` returns literal `201` after a successful modified range delete rather than a standard `SQLITE_OK`. Callers must intentionally understand this sentinel. It also has commented-out cursor invalidation and save-all-cursors logic, so concurrent open cursors on the same table may be more fragile than with normal single-row delete.

`sqlite3BtreeLazyDelete` stores page numbers as `int` payloads and reads them through `sqlite3BtreeDataFetch`, expecting exactly `sizeof(int)` bytes. It assumes page numbers fit that representation and that the cursor table is well-formed. Stack overflow is reported as `SQLITE_FULL`.

The open path deliberately ignores the initial header page size. This protects against stale/corrupt headers in WAL/codec scenarios, but it means default page-size and auto-vacuum defaults are used temporarily until page 1 is read through the pager. Code that observes these fields too early would see provisional values.

The partial index comparison optimization depends on `sqlite3VdbeRecordCompare` accurately reporting whether more bytes are required. The `SQLITE3_BTREE_FORCE_FULL_COMPARISONS` debug switch can compare partial and full results, but it is disabled by default.

The chunk ends at the start of `sqlite3BtreeCount`; its full tree-walk implementation and later integrity-check APIs are outside this work item, so count/integrity behavior should be reconciled by the later chunk merge.

## Test Signals

Useful direct tests for this chunk should exercise:

- opening databases with valid page 1 in WAL but misleading initial database-header bytes, especially with pager codecs or checksums;
- shared-cache lock conflicts across read cursors, write cursors, schema table locks, read-uncommitted mode, and exclusive transactions;
- page initialization and corruption detection for malformed headers, invalid cell offsets, overlapping freeblocks, oversized cells, and invalid page flags;
- insert/replace/delete with small local payloads, overflow payloads, integer table keys, index keys, append-biased inserts, root splits, right-edge quick balance, non-root redistribution, and root shallowing;
- cursor stability when other cursors are saved/restored around inserts, deletes, clear-table, rollback, and savepoint rollback;
- freelist allocation/freeing with empty freelists, full trunk pages, exact-page allocation, nearby allocation, truncated leaves, secure delete, and same-transaction free/reuse rollback;
- auto-vacuum relocation, incremental vacuum, full auto-vacuum commit, root-page create/drop movement, and pointer-map updates for b-tree children and overflow pages;
- incremental blob reads/writes and overflow-cache invalidation after row replacement, delete, create table, auto-vacuum, and rollback;
- `sqlite3BtreeLazyDelete` and `sqlite3BtreeDeleteRange` on leaf-only and multi-level trees, including stack exhaustion, pointer-map `PTRMAP_LAZYFREE`, resumed lazy deletion from the cursor table, and the nonstandard `201` return from modified range deletes;
- metadata reads/writes for free-page count, schema cookies, largest root page, and incremental-vacuum flag.

Existing test signals elsewhere in the SQLite suite that should be relevant include btree corruption tests, pager rollback/journal tests, auto-vacuum and incremental-vacuum tests, shared-cache lock tests, overflow payload tests, savepoint tests, and rowid/index cursor movement tests. FoundationDB-specific coverage should add assertions around the modified pointer-map and lazy-delete behavior because upstream SQLite tests will not cover those changes.
