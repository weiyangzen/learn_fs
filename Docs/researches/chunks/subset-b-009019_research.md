# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 55195-62132

## Scope

This chunk covers four adjacent pieces of the SQLite amalgamation embedded under WiredTiger tests:

- The end of `pcache.c`, SQLite's pager-facing page-cache middleware over the pluggable `sqlite3_pcache_methods2` interface.
- All of `pcache1.c`, the built-in default page-cache implementation and the allocator support behind `SQLITE_CONFIG_PAGECACHE`, `sqlite3PageMalloc()`, and memory-pressure recycling.
- All of `rowset.c`, a transient rowid collection used by the virtual machine to insert, test, and later enumerate rowids.
- The opening and early implementation section of `pager.c`, including WAL declarations, pager state/type definitions, rollback-journal header handling, hot-journal playback, WAL wrappers, savepoint playback, cache/page-size settings, and the beginning of mmap page acquisition.

The final function in this slice, `pagerAcquireMapPage()`, is truncated at line 62132 and continues in the next chunk. Notes below describe only the portion visible here.

## Purpose

The page-cache code provides the in-memory database page lifecycle used by the pager and btree layers. `pcache.c` owns `PgHdr` state, dirty-list ordering, reference counts, cache spill decisions, and the public internal APIs such as `sqlite3PcacheFetch()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheDirtyList()`, and cache-size tuning. `pcache1.c` supplies the default low-level cache implementation: page allocation, hash lookup by page number, LRU recycling of unpinned pages, cross-cache page-group accounting, and use of configured static page-cache memory.

`rowset.c` implements a memory-efficient rowid set. It accepts unordered inserts, can test membership by insert batch, or can switch to sorted extraction of the smallest rowid. It avoids per-entry malloc by allocating chunks of `RowSetEntry` objects and builds sorted lists or balanced trees as needed.

The pager section is the beginning of SQLite's durability and locking layer. It defines the `Pager` state machine, rollback-journal format, hot-journal recovery, savepoint rollback, WAL integration points, file locking helpers, page-size/cache/mmap configuration, and several test/debug hooks. This layer is responsible for making database page reads and writes atomic, durable according to synchronous settings, and safe across process locks.

## Important APIs, Types, and Data

### Page Cache Middleware (`pcache.c`)

- `struct PCache`: middleware cache object containing dirty-list heads/tails, `pSynced`, aggregate reference count `nRefSum`, cache/spill sizing, page and extra sizes, purgeability, stress callback, and lower-level `sqlite3_pcache *pCache`.
- `pcacheManageDirtyList(PgHdr *pPage, u8 addRemove)`: central dirty-list mutator. It removes, adds, or moves pages to the front while maintaining `pDirty`, `pDirtyTail`, `pDirtyPrev`, `pDirtyNext`, `pSynced`, and `eCreate`.
- `sqlite3PcacheInitialize()` / `sqlite3PcacheShutdown()`: initialize or tear down the configured pcache module, installing the default `pcache1` implementation when none is supplied.
- `sqlite3PcacheOpen()` / `sqlite3PcacheSetPageSize()` / `sqlite3PcacheClose()`: create middleware state, create or replace the underlying pluggable cache, and destroy it.
- `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, and `sqlite3PcacheFetchFinish()`: fetch raw `sqlite3_pcache_page` entries, spill a dirty page under memory pressure if needed, then initialize or reference-count the owning `PgHdr`.
- `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheDrop()`: reference lifecycle. Clean unreferenced pages are unpinned to the lower cache; dirty unreferenced pages stay on the dirty LRU list.
- `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheClearSyncFlags()`: transitions among clean, dirty, writable, and journal-sync-needed states.
- `sqlite3PcacheMove()` and `sqlite3PcacheTruncate()`: rekey a cached page to a new page number or discard pages above a limit.
- `sqlite3PcacheDirtyList()`: returns dirty pages sorted by page number using `pDirty` links and a merge-sort helper, for journal/WAL write ordering.
- Cache instrumentation/tuning: `sqlite3PcacheRefCount()`, `sqlite3PcachePagecount()`, `sqlite3PcacheSetCachesize()`, `sqlite3PcacheSetSpillsize()`, `sqlite3PcacheShrink()`, `sqlite3PCachePercentDirty()`, `sqlite3PcacheIterateDirty()`, and debug-only `sqlite3PcachePageSanity()`.

### Default Page Cache (`pcache1.c`)

- `struct PgHdr1`: default-cache page header. It embeds `sqlite3_pcache_page` first, stores page key `iKey`, ownership, hash-chain link, and LRU links. The database page buffer is allocated immediately before the header to make small btree overreads harmless.
- `struct PGroup`: a page-cache group used for LRU recycling. Depending on configuration, every cache has its own `PGroup` or all purgeable caches share the global `pcache1.grp`.
- `struct PCache1`: low-level cache containing size configuration, purgeability, local free/bulk allocations, hash table, recyclable count, and group pointer.
- `struct PCacheGlobal pcache1`: process-global page-cache allocator state, including configured pagecache slot memory, free-slot list, reserve count, mutexes, and memory-pressure flag.
- `sqlite3PCacheBufferSetup()`: converts a configured static page-cache buffer into a free-list of `PgFreeslot` entries.
- `pcache1InitBulk()`: optional per-cache bulk allocation used for initial pages when `SQLITE_CONFIG_PAGECACHE` has requested local bulk memory.
- `pcache1Alloc()` / `pcache1Free()`: allocate from the configured pagecache slot pool when possible, otherwise fall back to `sqlite3Malloc()`, updating SQLite status counters and memory-debug tags.
- `pcache1AllocPage()` / `pcache1FreePage()`: allocate and free `PgHdr1` page records, using cache-local free pages, bulk memory, global slots, or heap.
- `pcache1ResizeHash()`, `pcache1FetchNoMutex()`, `pcache1FetchWithMutex()`, `pcache1FetchStage2()`: page lookup and allocation algorithm. Existing pages are found by hash; misses can fail cheaply, recycle LRU pages, or allocate new memory depending on `createFlag`.
- `pcache1Unpin()`, `pcache1PinPage()`, `pcache1RemoveFromHash()`, `pcache1TruncateUnsafe()`, `pcache1EnforceMaxPage()`: maintain pinned/unpinned state, LRU membership, hash membership, and configured page limits.
- `sqlite3PCacheSetDefault()`: installs the default `sqlite3_pcache_methods2` vtable with `xInit`, `xCreate`, `xCachesize`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`.
- Optional/testing APIs: `sqlite3PcacheReleaseMemory()` under `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `sqlite3PcacheStats()` under `SQLITE_TEST`, `sqlite3HeaderSizePcache1()`, and `sqlite3Pcache1Mutex()`.

### RowSet

- `struct RowSetEntry`: rowid node reused as list node, tree node, and forest-list node.
- `struct RowSetChunk`: chunk allocation containing many entries.
- `struct RowSet`: owns chunks, pending insertion list `pEntry`, last entry, fresh-entry pool, forest of trees for membership testing, sorted/next flags, and current batch id.
- `sqlite3RowSetInit()`, `sqlite3RowSetClear()`, `sqlite3RowSetDelete()`: lifecycle.
- `sqlite3RowSetInsert()`: append a rowid to the pending list, preserving a sorted flag when inserts are increasing.
- `sqlite3RowSetNext()`: sort once if needed, then emit rowids in ascending order; after extraction begins, no more inserts are allowed.
- `sqlite3RowSetTest()`: on each new batch, sorts pending inserts and merges them into a forest of balanced trees; then searches all trees for a prior-batch rowid.
- Helpers `rowSetEntryMerge()`, `rowSetEntrySort()`, `rowSetTreeToList()`, `rowSetNDeepTree()`, and `rowSetListToTree()` implement merge sorting, duplicate removal, and balanced-tree construction.

### Pager And WAL Interfaces

- WAL declarations: `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, `sqlite3WalFrames()`, `sqlite3WalCheckpoint()`, savepoint helpers, snapshot helpers, and lock helpers under feature macros. These are forward interfaces used by pager code when `journal_mode=WAL`.
- Pager states: `PAGER_OPEN`, `PAGER_READER`, `PAGER_WRITER_LOCKED`, `PAGER_WRITER_CACHEMOD`, `PAGER_WRITER_DBMOD`, `PAGER_WRITER_FINISHED`, `PAGER_ERROR`.
- `PagerSavepoint`: rollback-journal offsets, per-savepoint bitvec, original db size, sub-journal record index, release behavior, and WAL savepoint data.
- `struct Pager`: core state for VFS handles, locks, journal mode, sync options, dirty/spill controls, page counts, journal offsets, savepoints, cache pointer, backup pointer, mmap state, WAL pointer, and statistics.
- Journal constants/data: `aJournalMagic`, `JOURNAL_PG_SZ()`, `JOURNAL_HDR_SZ()`, `MAX_SECTOR_SIZE`, `UNKNOWN_LOCK`, and `SPILLFLAG_*`.
- Durability helpers: `read32bits()`, `write32bits()`, `journalHdrOffset()`, `writeJournalHdr()`, `readJournalHdr()`, `zeroJournalHdr()`, `readSuperJournal()`, `writeSuperJournal()`, `pager_cksum()`, `pagerSyncHotJournal()`, `pager_playback()`, and `pager_playback_one_page()`.
- Lock/state helpers: `assert_pager_state()`, `pagerLockDb()`, `pagerUnlockDb()`, `pager_wait_on_lock()`, `pager_unlock()`, `pager_error()`, `pager_end_transaction()`, `pagerUnlockAndRollback()`.
- WAL wrappers: `pagerRollbackWal()`, `pagerWalFrames()`, `pagerBeginReadTransaction()`, `pagerOpenWalIfPresent()`, and `pagerUndoCallback()`.
- Public internal pager APIs visible here: `sqlite3PagerDirectReadOk()`, `sqlite3PagerDataVersion()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, `sqlite3PagerShrink()`, `sqlite3PagerSetFlags()`, `sqlite3PagerSetBusyHandler()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerTempSpace()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerReadFileheader()`, `sqlite3PagerPagecount()`, `sqlite3PagerTruncateImage()`, and `sqlite3SectorSize()`.

## Control Flow

### Page Fetch, Dirtying, And Spill

`sqlite3PcacheFetch()` maps the caller's create request onto the underlying `xFetch()` create mode. A missing page can be fetched only if allowed by `createFlag` and by `PCache.eCreate`, which is optimized according to whether purgeable dirty pages exist. The caller then uses `sqlite3PcacheFetchFinish()` to convert the lower page into a `PgHdr`; first-use initialization zeroes page metadata, sets `pData`, `pExtra`, cache pointer, page number, and `PGHDR_CLEAN`, then re-enters the normal finish path to increment references.

If a cheap fetch fails because the cache is full of dirty pages, `sqlite3PcacheFetchStress()` searches for an unreferenced dirty page to spill. It prefers the oldest unreferenced page without `PGHDR_NEED_SYNC`, using `pSynced` as an approximate cursor, then falls back to the oldest unreferenced dirty page. The pager-provided stress callback writes or journals that page. Only after the stress attempt does it call lower `xFetch(..., 2)` to allocate aggressively.

Dirty-list transitions are centralized in `pcacheManageDirtyList()`. `sqlite3PcacheMakeDirty()` changes a clean page to dirty and adds it to the list. `sqlite3PcacheRelease()` moves an unreferenced dirty page to the front, preserving LRU order used for spill. `sqlite3PcacheMakeClean()` removes from the dirty list, clears write/sync flags, marks clean, and unpins if no references remain.

### Default Cache Lookup And Recycling

`pcache1Fetch()` dispatches to a mutex or no-mutex path depending on group configuration. Lookup first searches `PCache1.apHash[iKey % nHash]`. If found and unpinned, `pcache1PinPage()` removes it from the group LRU before returning it. If not found and creation is allowed, `pcache1FetchStage2()` applies the multi-step policy documented in the code: refuse cheap allocation when too many pages are pinned or memory is pressured, resize the hash if needed, recycle an LRU page when the cache/group is full or pressured, and otherwise allocate a fresh page.

Recycled pages are removed from their old cache's hash table and pinned. They are reused only if allocation sizes match; otherwise they are freed and a fresh page is allocated. New or recycled pages are inserted into the requesting cache's hash table, keyed by page number, marked pinned, and initialized by clearing the first pointer-sized field of `page.pExtra`, which lets the middleware detect uninitialized `PgHdr` state.

`pcache1Unpin()` either frees a page immediately when reuse is unlikely or the group is above its maximum, or links it at the front of the group LRU for later recycling. `pcache1EnforceMaxPage()` trims the oldest LRU pages until global purgeable allocation is within limits and releases cache-local bulk memory when a cache becomes empty.

### RowSet Modes

RowSet has two mutually exclusive read modes. `sqlite3RowSetNext()` is extraction mode: on first call it sorts the pending insertion list if needed, marks `ROWSET_NEXT`, and then advances through `pEntry` in ascending rowid order. When the list is exhausted it clears chunks immediately.

`sqlite3RowSetTest()` is membership mode. When the batch number changes, all pending entries become visible to future tests: the pending list is sorted if needed, then merged into a forest of balanced trees. A tree-list node with empty `pLeft` can accept a new tree directly; otherwise the existing tree is flattened and merged with the new list, carrying duplicate removal through `rowSetEntryMerge()`. The actual lookup is a binary search in each tree in the forest. Inserts between tests with the same batch remain invisible until the batch changes.

### Pager Rollback Journal Flow

The rollback-journal writer uses `writeJournalHdr()` to align to the next sector boundary, update active savepoint header offsets, write the magic, record count placeholder or `0xffffffff`, checksum initializer, original db size, sector size, and page size, then pad to the journal header sector size. `zeroJournalHdr()` finalizes persistent journals either by truncating to zero or zeroing the first 28 bytes, syncing unless `noSync` is set, and optionally enforcing `journalSizeLimit`.

`pager_playback()` is the hot-journal and rollback playback loop. It reads the journal size, checks for a super-journal reference, and skips playback if the referenced super-journal no longer exists. It then repeatedly calls `readJournalHdr()` and plays back `nRec` records with `pager_playback_one_page()`. The first valid header triggers truncation of the database file back to the original page count. `nRec==0xffffffff` means records are inferred from journal size; a zero `nRec` in the final unsynced chunk of a local rollback can also be inferred from remaining file size. Short reads or detected corruption stop playback without treating the database as worse than a partially written journal.

`pager_playback_one_page()` reads page number, page bytes, and optional checksum, rejects illegal page numbers, skips pages outside the rollback target size or already restored in `pDone`, restores page-1 reserve bytes, writes to the database file when the pager state and sync guarantees allow it, updates backups, updates cached copies if present, and reinvokes the page reinitializer. For savepoint rollback where the page is not in cache and cannot be safely written to disk, it temporarily disables spill, fetches the page into cache, and marks it dirty so future reads see the restored content.

`pager_end_transaction()` finalizes an active write transaction. It releases savepoints, finalizes or closes/deletes the journal according to mode (`MEMORY`, `TRUNCATE`, `PERSIST`, `DELETE`, or exclusive-mode behavior), cleans or clears writable cache pages depending on commit/temporary-file policy, truncates cache entries beyond `dbSize`, releases WAL write locks when in WAL mode, truncates the database file after rollback-mode commit when needed, calls `SQLITE_FCNTL_COMMIT_PHASETWO`, and downgrades locks to shared in non-exclusive mode.

### WAL And Savepoint Flow

When WAL is active, read transactions begin through `pagerBeginReadTransaction()`, which ends any previous WAL read transaction, starts a new snapshot, and resets the pager cache if the snapshot changed. Page reads in `readDbPage()` first ask WAL for a frame containing the page and read from the WAL frame if present; otherwise they read from the database file.

`pagerWalFrames()` writes sorted dirty pages to the WAL. On commit it drops pages above the truncate size, updates the change-counter if page 1 is present, calls `sqlite3WalFrames()` with the pager's WAL sync flags, and updates backup destinations. `pagerRollbackWal()` uses `sqlite3WalUndo()` plus a walk of dirty cache pages to discard or reload uncommitted pages via `pagerUndoCallback()`.

`pagerPlaybackSavepoint()` implements rollback to savepoints. For rollback-journal mode it may replay three ranges: main-journal records from the savepoint offset to the next header, later main-journal records after that header, and sub-journal records from the savepoint's sub-record index. A `Bitvec` ensures each page is restored once. For WAL savepoints it delegates WAL position restore to `sqlite3WalSavepointUndo()` and still replays sub-journal pages as needed.

## State And Persistence Behavior

Page-cache state is in-memory but directly affects persistence timing. Dirty pages are not durable until pager code writes them to a rollback journal, WAL, or database file. `PGHDR_NEED_SYNC` prevents unsafe database writes before the rollback journal is synced, and `pSynced` is an optimization for selecting pages that can be spilled without forcing a journal sync. `PCache.nRefSum` controls whether pages are in active use; unreferenced clean pages can be recycled, while unreferenced dirty pages remain tracked for writeback.

The default cache may persist page buffers only for the lifetime of a connection/cache. It can allocate from a process-static pagecache buffer, cache-local bulk allocation, or heap. The persistent database image is never stored in `pcache1`; it is only cached there. `PGroup` LRU behavior affects memory reuse across caches and therefore performance and spill pressure, but not database format.

RowSet state is also transient. It stores rowids in memory associated with a SQLite connection and does not write to disk. The batch semantics are logical state used by query execution: rowids inserted after a test for the same batch are intentionally invisible to that batch.

Pager state is durability-critical. `Pager.eState`, `eLock`, `journalMode`, `journalOff`, `journalHdr`, `dbSize`, `dbOrigSize`, `dbFileSize`, `pInJournal`, `aSavepoint`, `pWal`, sync flags, and spill flags collectively determine whether a transaction can be committed, rolled back, recovered as a hot journal, or left in `PAGER_ERROR`. Journal files encode page records with big-endian fields and checksums seeded by `cksumInit`; super-journal pointers coordinate multi-database atomic commit. Hot-journal rollback syncs the journal before playback so a crash during recovery leaves future recoverers seeing the same journal content.

Temporary and in-memory databases relax persistence. Temporary files default to no-sync and may keep dirty pages in memory on commit if the backing file is not present or dirty percentage is low. `MEMDB` disables normal file I/O and cannot enter persistent pager error paths. WAL mode moves durability decisions to WAL frame appends and checkpoint sync flags, while rollback-journal mode uses journal finalization and database truncation.

## Dependencies And Integration Points

- Pager and btree layers: `pcache.c` exposes `PgHdr` pages to the pager; btree uses the extra page storage immediately after pager/cache headers for `MemPage`.
- Pluggable cache API: `pcache.c` depends on `sqlite3GlobalConfig.pcache2`; `pcache1.c` installs the default implementation through `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)`.
- SQLite memory subsystem: page-cache allocation uses `sqlite3Malloc`, `sqlite3MallocZero`, `sqlite3_free`, `sqlite3DbMallocRawNN`, memory-debug tags, benign malloc sections, and status counters.
- Mutex and atomic primitives: global and group page-cache state uses `sqlite3_mutex_enter/leave`, `AtomicStore`, and `AtomicLoad`; no-mutex mode relies on single-cache groups.
- VFS and OS I/O: pager code depends on `sqlite3OsOpen`, `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsTruncate`, `sqlite3OsFileSize`, `sqlite3OsLock`, `sqlite3OsUnlock`, `sqlite3OsAccess`, `sqlite3OsDelete`, `sqlite3OsFileControl`, and device-characteristic flags such as `SQLITE_IOCAP_SAFE_APPEND`, `SQLITE_IOCAP_BATCH_ATOMIC`, `SQLITE_IOCAP_POWERSAFE_OVERWRITE`, and `SQLITE_IOCAP_SUBPAGE_READ`.
- WAL subsystem: pager uses the WAL API for snapshots, frame reads/writes, write-lock release, rollback undo, savepoints, database size, and mode switching.
- Backup subsystem: rollback and WAL writes notify or restart `sqlite3_backup` state through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`.
- Bitvec and savepoint infrastructure: rollback uses `Bitvec` to track journaled or restored pages and prevent duplicate savepoint playback.
- PRAGMA/configuration surfaces: cache size, cache spill, page size, mmap limit, synchronous flags, locking behavior, and busy handler settings are wired through these functions from higher-level SQL pragmas or connection configuration.
- Test/debug builds: `SQLITE_TEST`, `SQLITE_DEBUG`, `SQLITE_CHECK_PAGES`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_MAX_MMAP_SIZE`, and WAL feature macros alter available APIs, assertions, and code paths.

## Risks And Maintenance Notes

- Dirty-list invariants are fragile. A page must not be both clean and dirty; `WRITEABLE` implies dirty; `NEED_SYNC` must survive some transitions to avoid writing database pages before the rollback journal is durable.
- `PCache.eCreate` is a performance-sensitive mirror of whether purgeable dirty pages exist. Incorrect updates can cause unnecessary spill searches or overly aggressive allocation.
- `pSynced` is deliberately approximate. Bugs that assume it is exact could choose unsafe spill candidates; current code rechecks reference and `PGHDR_NEED_SYNC` flags before using it.
- `pcache1FetchStage2()` mixes cache-local and group-global limits, memory pressure, and recycling across caches. Incorrect `nPurgeable`, `nRecyclable`, `nPage`, or LRU updates can leak pages, double-free pages, or break cache limits.
- Configured static pagecache memory requires slot-size checks. Allocations larger than `pcache1.szSlot` must fall back to heap; returning too-small slots would corrupt memory because page buffers and headers are packed together.
- RowSet mode assertions matter. Inserts after `sqlite3RowSetNext()` or mixing `Next` with `Test` violate the intended lifecycle. The code relies on assertions rather than runtime error returns.
- RowSet batch semantics are subtle: same-batch tests intentionally ignore inserts performed since the last batch transition. Query logic must choose batch ids correctly.
- Pager error-state handling protects against further corruption after `SQLITE_FULL` or `SQLITE_IOERR`. Clearing `PAGER_ERROR` without discarding cache or leaving a hot journal recoverable would risk stale page data.
- Journal-header parsing treats many corrupt or partial states as `SQLITE_DONE` rather than fatal. This is intentional for crash recovery but makes boundary checks, checksum behavior, and sector-size/page-size validation critical.
- `UNKNOWN_LOCK` exists because failed unlocks can leave the process holding an exclusive lock unbeknownst to SQLite. Hot-journal detection must honor that state to avoid reading an unrolled-back database.
- Super-journal handling allocates and scans child journal names. If a child journal still references the super-journal, the super-journal must not be deleted; deleting too early would break multi-database atomic recovery.
- `pager_playback_one_page()` has an important savepoint path that fetches a page into cache rather than writing the database file. Removing or weakening this can corrupt rollback-to-savepoint behavior for moved or freelist pages.
- WAL and rollback journal paths share pager state but have different persistence guarantees. Code that assumes rollback journal files exist in WAL mode, or assumes WAL rollback rewrites the database file, will be wrong.
- Page-size changes require no outstanding page references and must reset the cache, allocate new temp space with overrun bytes, update lock-page number, and refresh mmap limits.
- This chunk ends inside `pagerAcquireMapPage()`. Any analysis of mmap page lifecycle is incomplete without the following lines, including release behavior and final field initialization.

## Test Signals

Useful validation signals for this chunk include:

- SQLite pager crash-recovery tests that simulate partial journal headers, short reads, checksum mismatches, hot journals, persistent journals, truncate journals, and super-journal multi-database recovery.
- Savepoint rollback tests involving pages moved by incremental vacuum, pages above the current db size, and duplicate records across main journal and sub-journal.
- WAL tests for read-snapshot changes, frame reads, transaction rollback via `sqlite3WalUndo()`, savepoint undo, commit truncation, backup update propagation, and synchronous flag combinations.
- Cache-spill tests that force `sqlite3PcacheFetchStress()` with dirty pages both with and without `PGHDR_NEED_SYNC`, including referenced dirty pages that should not be spilled.
- Page-cache memory tests for `SQLITE_CONFIG_PAGECACHE` slot allocation, heap fallback, local bulk allocation, memory-pressure behavior, `sqlite3_release_memory()` under memory-management builds, and `sqlite3_status()` pagecache counters.
- Cache invariant/debug runs with `SQLITE_DEBUG`, `SQLITE_ENABLE_EXPENSIVE_ASSERT`, and `SQLITE_CHECK_PAGES` to exercise `sqlite3PcachePageSanity()`, dirty-list membership, page hashes, and truncate constraints.
- RowSet tests that cover unordered insert sorting, duplicate elimination, sorted `sqlite3RowSetNext()` extraction, batch visibility in `sqlite3RowSetTest()`, OOM paths during chunk allocation, and lifecycle clearing.
- VFS-focused tests for lock transition busy-handler behavior, sector-size sanitization, powersafe-overwrite sector reduction, `SQLITE_IOCAP_SAFE_APPEND`, batch atomic write eligibility, and direct overflow-read gating.
- Page-size and mmap tests that verify cache reset, temp-space allocation, reserve-byte handling, mmap limit propagation, and page-1 header/version tracking.
