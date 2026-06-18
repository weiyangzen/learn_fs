# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 62133-68993

## Scope and Purpose

This chunk covers the tail of SQLite's pager implementation and the opening half of the WAL implementation inside the amalgamated `sqlite3.c`. The pager portion owns page-cache lifetime, rollback-journal write safety, shared-lock acquisition, page fetch/release paths, transaction begin/commit/rollback, savepoint support, journal-mode transitions, and the bridge APIs that open, checkpoint, and close WAL mode. The WAL portion defines the on-disk WAL format, the transient shared-memory wal-index format, WAL lock layout, frame checksum/encoding rules, wal-index recovery, WAL connection open/close, checkpoint iteration, and the beginning of read-transaction startup.

This is a source chunk report only. The final per-file report for `sqlite3.c` should reconcile this with other chunks.

## Important APIs, Types, and Functions

Pager close and page-cache lifecycle:

- `sqlite3PagerClose(Pager *pPager, sqlite3 *db)` releases mapped-page headers, attempts WAL close/checkpoint when allowed, rolls back or unlocks any active pager state, closes journal and database file handles, closes pcache, frees temp space, and frees `Pager`.
- `pagerReleaseMapPage()` and `pagerFreeMapHdrs()` manage `PGHDR_MMAP` page header reuse and call `sqlite3OsUnfetch()` for memory-mapped pages.
- `sqlite3PagerRef()`, `sqlite3PagerUnrefNotNull()`, `sqlite3PagerUnref()`, and `sqlite3PagerUnrefPageOne()` wrap pcache reference counting with pager-specific rules. Page 1 has a dedicated release path because releasing the last page reference may unlock and rollback the pager.
- `sqlite3PagerLookup()` returns an already cached page without disk I/O.

Rollback journal, dirty-page flushing, and write safety:

- `syncJournal(Pager*, int newHdr)` upgrades to an exclusive lock, syncs and/or patches the rollback journal header depending on `SAFE_APPEND`, `SEQUENTIAL`, and full-sync settings, clears `PGHDR_NEED_SYNC`, and moves the pager to `PAGER_WRITER_DBMOD`.
- `pager_write_pagelist()` writes dirty pages to the database file, skipping pages beyond `dbSize` and pages marked `PGHDR_DONT_WRITE`; it updates `dbFileVers`, `dbFileSize`, write stats, backup state, and page hashes.
- `openSubJournal()`, `subjournalPage()`, and `subjournalPageIfRequired()` support savepoint rollback by writing page images to the sub-journal and setting savepoint bitvecs.
- `pagerStress()` is the pcache spill callback. It prevents unsafe spills under `doNotSpill` flags, writes single WAL frames in WAL mode, or syncs the rollback journal and writes pages in rollback mode.
- `sqlite3PagerFlush()` walks the dirty list and calls `pagerStress()` for unreferenced dirty pages.
- `pager_open_journal()`, `pagerAddPageToRollbackJournal()`, `pager_write()`, `pagerWriteLargeSector()`, and `sqlite3PagerWrite()` are the core "make this page writable" path. They open the rollback journal lazily, journal original content before modification, handle savepoints, mark pages dirty/writeable, and journal all co-resident pages when sectors are larger than pages.
- `sqlite3PagerDontWrite()` marks dirty pages as not worth writing back, primarily for freelist leaf pages during large deletes.

Pager open, locking, transactions, and metadata APIs:

- `sqlite3PagerOpen()` allocates a single memory block containing `Pager`, `PCache`, database/journal/sub-journal file handles, back-pointer metadata, filename strings, URI parameters, journal filename, and WAL filename. It resolves full paths, handles memory/temp/immutable modes, opens the database file when appropriate, selects default page size from VFS characteristics, initializes pcache, and sets pager flags and methods.
- `sqlite3_database_file_object()` relies on the special filename memory layout to recover the owning `Pager` and return the main database `sqlite3_file` for a journal/WAL filename.
- `hasHotJournal()` detects rollback journals needing recovery by checking file existence, reserved locks, database size, and the first journal byte.
- `sqlite3PagerSharedLock()` obtains a shared lock, rolls back hot journals under exclusive lock, validates change counters and cache contents, opens WAL if present, starts WAL read transactions, and computes `dbSize`.
- `sqlite3PagerBegin()` obtains rollback-mode reserved/exclusive locks or a WAL write lock, initializes transaction sizes and offsets, and moves to `PAGER_WRITER_LOCKED`.
- `pager_incr_changecounter()`, `sqlite3PagerSync()`, `sqlite3PagerExclusiveLock()`, `sqlite3PagerCommitPhaseOne()`, and `sqlite3PagerCommitPhaseTwo()` implement two-phase commit. Phase one updates the change counter, optionally uses atomic or batch atomic writes, syncs the journal, writes dirty pages, grows/truncates/syncs the database, and enters `PAGER_WRITER_FINISHED`. Phase two finalizes the journal or WAL transaction.
- `sqlite3PagerRollback()` rolls back active write transactions through savepoint playback/WAL cleanup, journal playback, or transaction end paths, then persists pager errors if rollback failed.
- `pagerOpenSavepoint()`, `sqlite3PagerOpenSavepoint()`, and `sqlite3PagerSavepoint()` allocate savepoint descriptors, bitvecs, WAL savepoint data, release or rollback savepoints, truncate in-memory sub-journals, and handle journal-mode-off error behavior for ZipVFS builds.
- Metadata and control helpers include `sqlite3PagerFilename()`, `sqlite3PagerVfs()`, `sqlite3PagerFile()`, `sqlite3PagerJrnlFile()`, `sqlite3PagerJournalname()`, `sqlite3PagerGetData()`, `sqlite3PagerGetExtra()`, `sqlite3PagerLockingMode()`, `sqlite3PagerSetJournalMode()`, `sqlite3PagerGetJournalMode()`, `sqlite3PagerOkToChangeJournalMode()`, `sqlite3PagerJournalSizeLimit()`, `sqlite3PagerBackupPtr()`, `sqlite3PagerClearCache()`, and stats/refcount helpers compiled for debug/test builds.
- `sqlite3PagerMovepage()` and `sqlite3PagerRekey()` support btree/autovacuum page relocation while preserving rollback and savepoint invariants.

Pager page fetch methods:

- `getPageNormal()` fetches a page through pcache, validates page numbers, initializes cache misses from disk via `readDbPage()` or zero-fill when beyond the database image or `PAGER_GET_NOCONTENT` is set, and sets journal/savepoint bits for no-content pages.
- `getPageMMap()` tries to satisfy eligible readonly page fetches with `sqlite3OsFetch()` and mapped `PGHDR_MMAP` headers, avoiding page 1 and WAL frames.
- `getPageError()` returns the persistent pager error code.
- `sqlite3PagerGet()` dispatches through `pPager->xGet`.

WAL pager bridge APIs:

- `sqlite3PagerCheckpoint()` invokes `sqlite3WalCheckpoint()` and includes a zero-byte WAL-mode bootstrap path through `PRAGMA table_list`.
- `sqlite3PagerWalCallback()`, `sqlite3PagerWalSupported()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, and optional snapshot/ZipVFS/SEH helpers wrap WAL-layer capabilities for pager callers.
- `pagerOpenWal()` opens the WAL handle, taking an exclusive database lock for heap-memory wal-index mode.

WAL structures and constants:

- `WalIndexHdr` is the replicated shared-memory wal-index header: version, change counter, initialization flag, checksum endianness, encoded page size, `mxFrame`, database page count, last-frame checksum, salt values, and header checksum.
- `WalCkptInfo` stores checkpoint coordination state: `nBackfill`, reader marks, lock byte padding, and `nBackfillAttempted`.
- `Wal` is the per-connection WAL handle, tracking VFS/database/WAL file handles, wal-index pages (`apWiData`), page size, read/write/checkpoint locks, readonly mode, sync/padding policy, unreliable-shm mode, cached header, snapshot state, SEH recovery state, and optional blocking-lock database handle.
- `WalIterator` merges wal-index segments in database page order for checkpointing.
- Format constants include `WAL_MAX_VERSION`, `WALINDEX_MAX_VERSION`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, `WAL_RECOVER_LOCK`, `WAL_READ_LOCK(i)`, `WAL_NREADER`, `WAL_FRAME_HDRSIZE`, `WAL_HDRSIZE`, `WAL_MAGIC`, `HASHTABLE_NPAGE`, `HASHTABLE_NPAGE_ONE`, `HASHTABLE_NSLOT`, `HASHTABLE_HASH_1`, and `WALINDEX_PGSZ`.

WAL helpers in this chunk:

- `walIndexPageRealloc()` and `walIndexPage()` grow/map wal-index pages using heap memory for exclusive heap-memory mode or VFS `xShmMap()` for normal shared memory. Readonly SHM states set `WAL_SHM_RDONLY`.
- `walCkptInfo()` and `walIndexHdr()` compute typed pointers into wal-index page 0.
- `walChecksumBytes()`, `walEncodeFrame()`, and `walDecodeFrame()` implement WAL header/frame checksum mechanics, salt validation, page-number validation, and big/little-endian checksum selection.
- `walIndexWriteHdr()` writes two copies of `WalIndexHdr` with a barrier between them, intentionally ordering writes opposite of the read path.
- `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, and `walUnlockExclusive()` wrap VFS shared-memory locks, with exclusive-mode no-op behavior and SEH lock-mask tracking.
- `walHash()`, `walNextHash()`, `walHashGet()`, `walFramePage()`, `walFramePgno()`, `walCleanupHash()`, and `walIndexAppend()` maintain wal-index page-number arrays and linear-probed hash tables.
- `walIndexRecover()` rebuilds the transient wal-index by reading the WAL header and frames, validating checksums/version/page size, appending valid frame mappings, copying private scratch index pages into shared memory, writing a fresh header, and initializing checkpoint/read-mark state.
- `sqlite3WalOpen()` validates format-critical constants, allocates `Wal`, opens the WAL file, records readonly status, and sets sync/padding behavior from device capabilities.
- `sqlite3WalLimit()` changes reset truncation size.
- `walIteratorNext()`, `walMerge()`, `walMergesort()`, `walIteratorInit()`, and `walIteratorFree()` build and consume sorted per-page frame iteration for checkpointing.
- Optional `SQLITE_ENABLE_SETLK_TIMEOUT` helpers enable blocking locks and expose `sqlite3WalWriteLock()` and `sqlite3WalDb()`.
- `walBusyLock()` retries exclusive locks through the busy handler.
- `walPagesize()`, `walRestartHdr()`, `walCheckpoint()`, `walLimitSize()`, `sqlite3WalClose()`, `walIndexTryHdr()`, `walIndexReadHdr()`, `walBeginShmUnreliable()`, and the beginning of `walTryBeginRead()` implement checkpoint/reset/close and read-transaction setup.

## Control Flow and State Transitions

Pager read startup flows through `sqlite3PagerSharedLock()`. In rollback mode it waits for a shared database lock, checks `hasHotJournal()`, upgrades directly to exclusive lock if hot recovery is required, syncs and plays back the hot journal, then validates the cache by comparing the header change-counter bytes at offset 24. After this it probes for an existing WAL file and, if WAL is active, begins a WAL read transaction. On failure it unlocks and returns to `PAGER_OPEN`; on success it enters `PAGER_READER` and records that a shared lock has been held.

Page acquisition is state-dependent through `pPager->xGet`. Normal fetches first consult pcache, then either zero-fill or read from disk. Mmap fetches are used only for eligible readonly pages and fall back to normal fetches if the WAL contains the page, the page is page 1, the mapping fails, or the page must be tracked in pcache.

Write startup flows through `sqlite3PagerBegin()`. In rollback mode it obtains a reserved lock and optionally an exclusive lock; in WAL mode it obtains the WAL write lock and possibly upgrades exclusive locking mode. The first actual write to a page calls `pager_open_journal()` if still in `PAGER_WRITER_LOCKED`, writes the initial journal header, then `pager_write()` journals original page content, updates dirty/writeable flags, writes savepoint records if needed, and grows `dbSize`.

Rollback-mode commit phase one proceeds as a durability pipeline: update page-1 change counters, optionally create the journal file, write a super-journal name, `syncJournal()`, write the dirty list to the database, handle batch atomic-write fallback, ensure file growth/truncation matches the logical database image, and sync the database unless `noSync` delegates that to the caller. Commit phase two finalizes the journal using `pager_end_transaction()`, making the transaction irrevocable after rollback-journal invalidation.

Rollback paths split by mode and current state. WAL mode rolls back to savepoint `-1` then ends the WAL transaction. Rollback mode either ends a locked/no-journal transaction, enters error state for journal-mode-off cache uncertainty, or replays the rollback journal.

WAL recovery begins when `walIndexReadHdr()` cannot cleanly read the double wal-index header. It obtains the write lock, maps page 0, retries the header read, and if still bad calls `walIndexRecover()`. Recovery parses the WAL header, validates version and checksum, reads frames sequentially until invalid or EOF, updates `mxFrame` only on commit frames, writes wal-index mappings, and initializes `nBackfill`, `nBackfillAttempted`, and reader marks.

Checkpoint control in `walCheckpoint()` computes `mxSafeFrame` from reader marks, optionally adjusts read marks under exclusive read locks, builds a `WalIterator` over frames newer than `nBackfill`, syncs the WAL, copies safe frame payloads into database pages in page order, truncates/syncs the database if the whole WAL is checkpointed, advances `nBackfill`, and for restart/truncate modes waits for all non-zero readers before resetting or truncating the WAL.

The read-transaction path at the chunk boundary starts in `walTryBeginRead()`. It bounds retry loops with `WAL_RETRY_PROTOCOL_LIMIT`, sleeps with increasing delays after repeated transient races, optionally uses blocking locks, reads or recovers the wal-index header unless `useWal` is forced, handles unreliable readonly SHM by building/validating a heap-memory index, and then begins selecting a read-mark slot.

## State and Persistence Behavior

Pager persistent state spans database pages, rollback journals, sub-journals, WAL files, and transient/shared page cache state. `Pager` fields such as `eState`, `eLock`, `errCode`, `dbSize`, `dbOrigSize`, `dbFileSize`, `journalOff`, `journalHdr`, `nRec`, `pInJournal`, `aSavepoint`, `nSubRec`, `dbFileVers`, `changeCountDone`, `journalMode`, and `exclusiveMode` define whether page-cache content can be trusted and what must be persisted before database writes.

Rollback-journal safety is centered on writing original page images before setting `PGHDR_WRITEABLE`, syncing the journal before database writes when `PGHDR_NEED_SYNC` is present, and clearing stale persistent-journal headers that could otherwise be mistaken for hot-journal content after a crash. Savepoint state persists page images in the sub-journal plus bitvec membership in each `PagerSavepoint`.

WAL persistence uses a durable WAL file plus transient wal-index shared memory. The WAL file is cross-platform big-endian for headers and frame metadata. The wal-index is native-endian shared memory and is explicitly recoverable from the WAL file after crashes. `WalIndexHdr` is duplicated and checksummed to tolerate concurrent dirty reads. Checkpoint progress is persisted in shared memory through `nBackfill` and read marks, and durable database persistence only becomes complete after WAL sync, database writes, optional database truncate, and database sync.

Memory-mapped pager pages are reference-counted separately from pcache pages and are returned to `pMmapFreelist` after `sqlite3OsUnfetch()`. This means mapped pages are not normal dirty/writeable pages and are rejected by `sqlite3PagerWrite()`.

The pager filename allocation layout is intentionally persistent as an ABI compatibility detail for code that discovers database filenames from WAL/journal filenames. `sqlite3_database_file_object()` depends on the embedded back-pointer immediately before the filename region.

## Dependencies and Integration Points

This code depends heavily on SQLite's VFS and OS abstraction methods: `sqlite3OsOpen()`, `sqlite3OsClose()`, `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsTruncate()`, `sqlite3OsFileSize()`, `sqlite3OsFileControl()`, `sqlite3OsFileControlHint()`, `sqlite3OsAccess()`, `sqlite3OsDelete()`, `sqlite3OsFetch()`, `sqlite3OsUnfetch()`, `sqlite3OsShmMap()`, `sqlite3OsShmLock()`, `sqlite3OsShmBarrier()`, and `sqlite3OsShmUnmap()`.

The pager integrates with:

- `PCache` through fetch, stress, dirty-list, clean/drop/move/refcount/stat APIs.
- The btree layer through page data/extra APIs, transaction begin/commit/rollback, savepoints, page movement, locking mode, journal mode, and page writability.
- The backup subsystem through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`.
- The WAL subsystem through pager bridge calls for open/close/checkpoint/read/write/snapshot behavior.
- URI and filename APIs through preserved filename memory layout and `sqlite3_uri_boolean()`.
- Test/debug infrastructure through `testcase()`, `sqlite3FaultSim()`, counters, trace macros, and optional `SQLITE_TEST` stats.

The WAL layer integrates with:

- VFS shared-memory primitives and lock bytes compatible with unix/windows SHM base offsets.
- Pager via `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalCheckpoint()`, `sqlite3WalBeginWriteTransaction()` outside this chunk, read transactions, and frame lookup.
- Busy handlers for checkpoint and lock acquisition.
- Optional builds for SEH, snapshots, blocking locks, ZipVFS, mmap, atomic write, batch atomic write, debug, and test modes.

## Risks and Edge Cases

- Crash consistency depends on subtle ordering: journal header update after data sync, WAL sync before checkpoint database writes, database sync before WAL deletion/truncation, and barrier-separated wal-index header writes. Small reorderings can create corruption windows.
- Persistent rollback journals can contain old valid-looking headers beyond `journalOff`; `syncJournal()` deliberately zeros a following header to avoid hot-journal playback of stale transactions.
- `sqlite3PagerOpen()` embeds compatibility-sensitive filename ordering and a back-pointer. Changing this layout can break external consumers and SQLite filename helper APIs.
- Hot-journal detection intentionally tolerates races and false positives. Recovery code must continue to handle cases where another process rolled back or deleted a journal between existence checks and lock acquisition.
- Page 1 has special lifetime and mmap restrictions. Using normal unref paths for the final page-1 reference would violate pager unlock assumptions.
- `PAGER_GET_NOCONTENT` marks journal/savepoint bitvecs to skip later journaling; misuse can suppress rollback data for pages whose content actually matters.
- Large-sector handling must prevent journal-header insertion between co-resident pages. The `SPILLFLAG_NOSYNC` guard is critical during `pagerWriteLargeSector()`.
- WAL shared-memory reads are intentionally lock-free in places and rely on duplicated headers, checksums, atomic 32-bit loads/stores, and memory barriers. Thread sanitizers may flag benign races.
- Readonly or unreliable SHM mode is complex: heap-memory wal-index fallback must detect writers that checkpoint, truncate, or wrap the WAL between checks.
- WAL checkpointing must respect active reader marks; overwriting database pages newer than a reader's snapshot would break snapshot isolation.
- Retry logic in `walTryBeginRead()` assumes retry races are transient. Persistent protocol violations eventually surface as `SQLITE_PROTOCOL`.
- Build-option branches (`SQLITE_OMIT_WAL`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_USE_SEH`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_ENABLE_SNAPSHOT`) materially change control flow and need configuration-specific testing.

## Test Signals and Verification Hooks

Visible test/debug signals include:

- `sqlite3FaultSim(400)`, `sqlite3FaultSim(600)`, and `sqlite3FaultSim(650)` for commit I/O, wal-index page allocation, and SEH fault injection.
- `testcase()` coverage points around short reads, page-size boundaries, atomic-write paths, read marks, mmap behavior, and journal/sync flags.
- `assert_pager_state()`, `CHECK_PAGE()`, lock-state asserts, wal-index format-size asserts, and expensive hash-table reachability asserts.
- `PAGERTRACE`, `IOTRACE`, `WALTRACE`, and pager/WAL counters for tracing commits, page writes, journal writes, checkpoints, and lock activity.
- `sqlite3PagerStats()`, `sqlite3PagerCacheStat()`, `sqlite3PagerMemUsed()`, refcount helpers, and WAL recovery notices via `sqlite3_log(SQLITE_NOTICE_RECOVER_WAL, ...)`.

High-value behavioral tests for this chunk would exercise:

- Hot-journal recovery after simulated crash, including readonly rollback failure and persistent-journal stale-header handling.
- Commit phase one/two under normal rollback, full-sync, no-sync, journal-mode-off, WAL, atomic-write, and batch atomic-write configurations.
- Savepoint release/rollback with sub-journal truncation and page movement across savepoint boundaries.
- Page cache spill under `PGHDR_NEED_SYNC`, `doNotSpill`, WAL mode, and rollback mode.
- WAL recovery from missing/corrupt/stale `-shm`, partial WAL frames, invalid checksums, unsupported WAL versions, and readonly SHM fallback.
- Checkpoint behavior with active readers, passive/full/restart/truncate modes, busy handlers, interrupts, database growth, WAL truncation, and persistent-WAL file-control responses.

## Chunk Boundary Notes

The chunk begins in the middle of mmap page acquisition cleanup just before `pagerReleaseMapPage()` and ends inside `walTryBeginRead()` while it is selecting read marks. Cross-chunk reconciliation should connect this start to earlier pager mmap allocation logic and connect the end to the remainder of WAL read-transaction setup, frame lookup, writer/commit paths, snapshot APIs, and checkpoint public wrappers.
