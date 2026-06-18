# sources/storage-engines/foundationdb/contrib/sqlite/btree.c lines 7897-8795

## Scope And Purpose

This chunk covers the end of SQLite's btree implementation in the FoundationDB-contrib SQLite tree. It starts inside `sqlite3BtreeCount()`, then implements the btree integrity-check machinery, and ends with small public btree accessors and maintenance helpers for filenames, transaction state, WAL checkpointing, schema storage, shared-cache table locks, incremental blob writes, overflow-page caching, and database header format-version changes.

The largest behavioral surface is the integrity checker used by `PRAGMA integrity_check` through `sqlite3BtreeIntegrityCheck()`. It walks freelists, overflow chains, root btrees, and FoundationDB's lazy-delete freetable, marks page references, validates auto-vacuum pointer-map entries, checks rowid ordering for intkey pages, validates overflow ownership, checks child depths, and detects overlapping or missing byte coverage within each btree page.

This span is also where the local FoundationDB fork diverges from stock SQLite semantics. It has a global `g_expect_full_pointermap`, an extended pointer-map type `PTRMAP_LAZYFREE`, a lazy-delete table validator, and a disabled underfull-page check annotated as failing for this fork. Those changes make the integrity check aware of deferred subtree deletion and relaxed page fullness expectations.

## Important APIs, Types, And Functions

`sqlite3BtreeCount(BtCursor *pCur, i64 *pnEntry)` counts entries in the btree addressed by a cursor. The covered portion performs a depth-first page traversal using `moveToRoot()`, `moveToChild()`, and `moveToParent()`. Leaf pages and non-intkey pages contribute `pPage->nCell` to the count. Interior intkey pages do not count interior separator cells as table entries.

`sqlite3BtreePager(Btree *p)` returns the underlying `Pager *` from `p->pBt`. The comment marks it as testing/debug-only, but it is still exported as `SQLITE_PRIVATE`.

`IntegrityCk` is the integrity-check context shared across helper routines. The structure is defined in the btree internals and carries `BtShared *pBt`, `Pager *pPager`, total page count, the `anRef[]` page-reference count array, remaining error budget `mxErr`, accumulated error count `nErr`, `mallocFailed`, and a `StrAccum errMsg`.

`checkAppendMsg()` is the shared error recorder. It decrements the remaining error budget, increments `nErr`, appends an optional context prefix and formatted message to `IntegrityCk.errMsg`, and propagates `StrAccum` allocation failure into `IntegrityCk.mallocFailed`.

`checkRef()` validates a page number and increments `anRef[iPage]`. It reports out-of-range page numbers and a second reference to the same page, returning nonzero when the page is invalid or already referenced.

`checkPtrmap()` is compiled when auto-vacuum support is present. It reads a pointer-map entry with `ptrmapGet()` and checks that the child page maps to the expected pointer-map type and parent page. This chunk uses stock pointer-map categories like `PTRMAP_BTREE`, `PTRMAP_ROOTPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`, `PTRMAP_FREEPAGE`, and `PTRMAP_FREELEAF`, plus this fork's `PTRMAP_LAZYFREE`.

`checkList()` validates either the main freelist or an overflow-page chain. For freelists, each trunk page is read through the pager, its leaf count is range checked against usable page size, free leaves are marked in `anRef[]`, and pointer-map entries are optionally checked when `pBt->autoVacuum && g_expect_full_pointermap`. For overflow lists, it verifies chained overflow pointer-map ownership and uses the expected page count to detect missing or extra list pages.

`checkTreePage()` recursively validates one btree page and its descendants. It loads and initializes the page, checks cell payloads and overflow chains, validates intkey rowid ordering within a page and against parent bounds, verifies auto-vacuum pointer-map ownership for child pages and overflow roots, checks equal child depth, optionally prints a verbose tree view, and then builds a byte-hit map to ensure cells, freeblocks, header/cell-pointer area, content area, and fragmented bytes account for the page without overlap.

`checkLazyDeleteTable()` is a FoundationDB-specific integrity extension. It opens a read cursor on the lazy-delete table root, iterates each intkey record, reads an `int` page number from the record payload, checks that the page has pointer-map type `PTRMAP_LAZYFREE`, and runs `checkTreePage()` on that lazily deleted subtree.

`sqlite3BtreeIntegrityCheck(Btree *p, int *aRoot, int nRoot, int mxErr, int *pnErr, int verbose)` is the exported integrity-check entry point. It initializes `IntegrityCk`, allocates and zeroes `anRef[]`, reserves the pending-byte page as referenced, validates the freelist, checks each root in `aRoot[]`, checks the lazy-delete freetable at `aRoot[nRoot - 1]`, reports unreferenced pages and referenced pointer-map pages, verifies pager refcount stability, and returns either a malloc-owned error string or `NULL`.

The remaining exported helpers are narrower:

- `sqlite3BtreeGetFilename()` and `sqlite3BtreeGetJournalname()` return pager file and journal paths.
- `sqlite3BtreeIsInTrans()`, `sqlite3BtreeIsInReadTrans()`, and `sqlite3BtreeIsInBackup()` expose write/read transaction and backup state.
- `sqlite3BtreeCheckpoint()` gates WAL checkpoints on there being no active shared-btree transaction, then delegates to `sqlite3PagerCheckpoint()`.
- `sqlite3BtreeSchema()` lazily allocates per-`BtShared` schema memory and stores its destructor.
- `sqlite3BtreeSchemaLocked()` checks for a shared-cache read lock conflict on `MASTER_ROOT`.
- `sqlite3BtreeLockTable()` takes a shared-cache read or write table lock when the btree handle is sharable.
- `sqlite3BtreePutData()` writes into an existing intkey row payload for incremental blob handles without changing payload length.
- `sqlite3BtreeCacheOverflow()` marks a cursor as an incremental blob handle and invalidates any old overflow-page cache.
- `sqlite3BtreeSetVersion()` updates database header bytes 18 and 19 to read/write version 1 or 2, using a two-phase transaction escalation if the header actually needs modification.

## Control Flow

The `sqlite3BtreeCount()` traversal is an explicit depth-first walk over btree pages. Starting from the root, it counts entries on countable pages, backs up from leaves until it finds an unvisited parent branch, advances the parent index, and descends either through a cell's left-child page number or the right-child pointer at `hdrOffset + 8`. Completion is detected when the traversal backs up from a leaf to the root with no remaining branches.

The integrity-check entry flow begins in `sqlite3BtreeIntegrityCheck()`. It enters the btree mutex, asserts that at least a read transaction is open, snapshots the pager reference count, derives the current database page count, and returns immediately for an empty database. It then allocates `anRef[]`, initializes the error accumulator with a small stack buffer and heap growth limit, marks the pending-byte page, and starts structural checks.

Freelist checking goes through `checkList(isFreeList=1, firstTrunk, totalFreePages, "Main freelist: ")`. Each trunk page is marked, read, and parsed. The first 4 bytes link to the next trunk and the next 4 bytes hold the number of free leaf page numbers stored in the trunk. The routine decrements the expected remaining page count for both trunk and valid leaf entries, reports too many leaves for the usable page size, and reports missing, extra, or excessive pages after the traversal.

Root btree checking loops over `aRoot[0..nRoot-1]`. Root page 0 is skipped. Under auto-vacuum, non-page-1 roots are checked as `PTRMAP_ROOTPAGE`. `checkTreePage()` then recursively descends through each interior cell's child pointer and finally the right-child pointer. For each cell it parses payload metadata with `btreeParseCellPtr()`, checks local versus overflow payload size, verifies the first overflow page pointer when the payload spills, recursively checks the overflow chain through `checkList(isFreeList=0, ...)`, and recurses into child pages for non-leaf nodes.

The byte-coverage portion of `checkTreePage()` allocates a `hit` array with one byte per database-page byte. It marks the header/cell-pointer area and the unused space before the content area, then increments the hit count over each cell body and each freeblock. Any zero hit indicates a byte not covered by known page regions; multiple hits indicate overlapping use. The zero-hit count must match the page header's fragmentation byte count. This catches page-local corruption independently of cross-page reference checks.

After ordinary roots, `sqlite3BtreeIntegrityCheck()` calls `checkLazyDeleteTable()` using the last root entry as the lazy-delete freetable. This helper opens a cursor with `sqlite3BtreeCursor()`, seeks to the first entry, and iterates with `sqlite3BtreeNext()`. For each record, `sqlite3BtreeKeySize()` retrieves the intkey rowid, `sqlite3BtreeDataFetch()` returns the stored page number, and the page is checked both as a lazy-free pointer-map entry and as a btree subtree.

The final integrity pass scans all page numbers from 1 to `nPage`. Without auto-vacuum, any unreferenced page is an error. With auto-vacuum, unreferenced pointer-map pages are allowed, but unreferenced ordinary pages are reported along with pointer-map metadata if readable, and referenced pointer-map pages are reported as corruption. Before returning, the function compares the pager refcount to the saved value to catch leaks in the checker itself, leaves the btree mutex, frees `anRef[]`, and finalizes or resets the accumulated error text.

The late utility functions are mostly direct wrappers. They enter the btree mutex only when reading mutable shared-btree state or invoking pager/shared-cache operations. `sqlite3BtreePutData()` first restores the cursor position, validates writable incremental-blob preconditions, then delegates to `accessPayload()` with the write flag. `sqlite3BtreeSetVersion()` opens a read transaction first, temporarily suppresses automatic WAL use when forcing version 1, escalates to a write transaction only if bytes 18 or 19 differ, writes page 1 through the pager, updates the header bytes, and clears `doNotUseWAL`.

## State And Persistence Behavior

The integrity checker is read-oriented but stateful. Its durable inputs are database pages, page-1 metadata, btree page headers, overflow chains, freelist trunks, auto-vacuum pointer-map pages, and lazy-delete records. Its in-memory state is `IntegrityCk`, especially `anRef[]`, which tracks whether each database page has been seen and detects duplicate ownership.

`checkTreePage()` deliberately clears `MemPage.isInit` before calling `btreeInitPage()` so that page-format corruption checks run even if the page had already been initialized in cache. It releases every `MemPage` or `DbPage` it acquires through `releasePage()` or `sqlite3PagerUnref()`, and the outer integrity check verifies that pager reference counts return to their entry value.

The checker mutates only diagnostic state during normal operation: `mxErr`, `nErr`, `mallocFailed`, and the accumulated string. It may also alter cached page initialization flags, but it does not call pager-write APIs and does not persist page changes.

`sqlite3BtreeSchema()` persists schema-side state for the lifetime of `BtShared`, not to disk. The first nonzero allocation request creates zeroed memory stored in `pBt->pSchema` and records `pBt->xFreeSchema`; later calls return the same pointer and ignore `nBytes`.

`sqlite3BtreePutData()` is durable mutation. It writes a byte range into the existing payload of the row under an incremental blob cursor. It depends on an active write transaction, a valid intkey-table row, no conflicting read locks, and `accessPayload()` to route writes through local cell payload or overflow pages. It cannot resize the row; attempts beyond the stored payload are expected to fail through the payload-access path.

`sqlite3BtreeSetVersion()` is also durable mutation. It writes database header fields for read and write file-format versions. The `doNotUseWAL` flag is a transient guard so that forcing version 1 does not automatically open WAL because the current header still says version 2.

WAL checkpointing persists pager/WAL state but not btree pages directly. `sqlite3BtreeCheckpoint()` refuses to checkpoint while the shared btree has an active transaction and otherwise delegates to the pager.

## Dependencies And Integration Points

This chunk is tightly integrated with btree cursor navigation (`moveToRoot`, `moveToChild`, `moveToParent`, `findCell`, `cellSizePtr`, `btreeParseCellPtr`), page lifecycle helpers (`btreeGetPage`, `getAndInitPage`, `btreeInitPage`, `releasePage`), overflow cleanup/list logic (`clearCell`, `checkList`), big-endian page-field helpers (`get2byte`, `get2byteNotZero`, `get4byte`), and pager APIs (`sqlite3PagerGet`, `sqlite3PagerGetData`, `sqlite3PagerUnref`, `sqlite3PagerRefcount`, `sqlite3PagerFilename`, `sqlite3PagerJournalname`, `sqlite3PagerCheckpoint`, `sqlite3PagerWrite`).

The integrity entry point is used by the VDBE `OP_IntegrityCk` path generated for `PRAGMA integrity_check` and `PRAGMA quick_check`. The SQL layer supplies the root-page array and error budget; this function returns a newline-separated message string and writes the number of reported errors to `pnErr`.

Auto-vacuum integration depends on pointer-map primitives (`ptrmapGet`, `ptrmapPut` elsewhere) and pointer-map page-number calculations through `PTRMAP_PAGENO()`. The FoundationDB lazy-delete extension integrates with `sqlite3BtreeLazyDelete()` from the preceding chunk: that code stores lazily deleted subtree roots in a table and marks them `PTRMAP_LAZYFREE`; this chunk validates those records and subtrees.

Shared-cache integration uses `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `hasSharedCacheTableLock()`, and `hasReadConflicts()` to enforce schema/table lock rules around schema access, explicit table locks, and incremental blob writes.

The mutex contract is split by API. Integrity checking, schema allocation, schema-lock queries, table locking, checkpointing, and version changes enter the btree mutex or assert the caller holds the database mutex. Filename and journal-name access avoid entering the btree mutex because pager filenames are documented as invariant while the pager is open.

## Risks And Edge Cases

`checkLazyDeleteTable()` assumes the last element of `aRoot[]` is the lazy-delete freetable root. If callers provide ordinary SQLite root arrays without that convention, the checker will open and interpret the wrong table as the lazy-delete table.

`checkLazyDeleteTable()` reads each payload as `sizeof(int)` and casts `sqlite3BtreeDataFetch()` to `int *`. This matches the local `sqlite3BtreeLazyDelete()` writer, but it is endian- and ABI-width-sensitive if database files move across platforms with different integer layout or alignment behavior.

The underfull-page check in `checkTreePage()` is commented out with a note that it fails for this fork. That suppresses a traditional btree balance invariant and makes integrity-check success less strict about space utilization. It may be intentional for lazy deletion or FoundationDB behavior, but it narrows what `integrity_check` can prove.

Pointer-map validation for freelist pages is conditional on both auto-vacuum and `g_expect_full_pointermap`. When the global is false, the checker skips some freelist pointer-map expectations even in auto-vacuum databases. Tests need to cover both modes because corruption can be hidden in the default mode.

The rowid ordering checks only apply to intkey pages, and the detailed parent-bound propagation is strongest for intkey leaf pages. Non-intkey index key ordering is explicitly listed as not checked in the function comment.

The recursive `checkTreePage()` walk can be expensive on large databases and consumes C stack proportional to tree depth. SQLite btrees are shallow under normal page sizes, but corrupted child cycles are guarded mainly by `checkRef()` duplicate detection and the error budget.

`checkList()` continues to parse freelist leaf entries only if the free page number is `<= nPage`; it does not emit a direct error for an out-of-range free leaf in that inner loop. Trunk page bounds and duplicate checks are stricter.

`sqlite3BtreePutData()` relies on asserts for several write-transaction and locking invariants, while only `wrFlag`, restored cursor state, and valid cursor state are runtime-checked. Misuse in non-assert builds can become corruption risk if callers violate the expected btree-layer contract.

`sqlite3BtreeSetVersion()` asserts there is no active transaction before it starts. It temporarily sets `pBt->doNotUseWAL`; any early return path must clear it. This implementation clears it after the transaction attempts, but future edits should preserve that cleanup.

## Test Signals

The primary end-to-end signal is `PRAGMA integrity_check` or the VDBE `OP_IntegrityCk` path on databases with normal tables, indexes, overflow payloads, freelist pages, auto-vacuum pointer maps, WAL mode, and FoundationDB lazy-delete state.

Focused corruption tests should exercise duplicate page references, invalid page numbers, malformed freelist trunk leaf counts, missing and extra overflow pages, incorrect `PTRMAP_OVERFLOW1` and `PTRMAP_OVERFLOW2` entries, incorrect root and btree child pointer-map entries, referenced pointer-map pages, unreferenced ordinary pages, and page byte-overlap or fragmentation mismatches.

FoundationDB-specific tests should create lazy-delete table records through `sqlite3BtreeLazyDelete()`, then verify that integrity check accepts `PTRMAP_LAZYFREE` subtrees and rejects records whose payload is not exactly `sizeof(int)`, whose page is not marked `PTRMAP_LAZYFREE`, or whose lazily deleted subtree is structurally corrupt.

Incremental blob tests should validate `sqlite3BtreePutData()` on local payload and overflow payload rows, including writes at the end boundary, writes past the end returning an error without mutation, non-writable cursors returning `SQLITE_READONLY`, invalid cursor state returning `SQLITE_ABORT`, and overflow-cache invalidation through `sqlite3BtreeCacheOverflow()`.

Version and WAL tests should verify that `sqlite3BtreeSetVersion()` updates header bytes 18 and 19 only inside a write transaction, does not leave `doNotUseWAL` set, and interacts correctly with checkpoint refusal in `sqlite3BtreeCheckpoint()` when a transaction is active.
