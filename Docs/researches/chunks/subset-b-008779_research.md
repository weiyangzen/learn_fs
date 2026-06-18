# sources/storage-engines/sqlite/src/pager.c lines 1-6685

## Chunk Scope

This chunk covers the first 6685 lines of SQLite's pager implementation. It includes the pager state model, rollback-journal format and playback, WAL read/write handoffs, page-cache integration, pager construction/destruction, shared-lock acquisition, page fetch/release APIs, page journaling/writeability, and the first phase of commit. The chunk stops inside the comment for `sqlite3PagerCommitPhaseTwo()`, so transaction finalization, rollback public APIs, savepoint public APIs, journal-mode switching, page move/rekey helpers, and WAL open/close/snapshot tail functions are cross-chunk continuation points.

## Purpose

The pager is the storage layer that turns database pages into durable, transactional file operations. It sits between btree/page users and the VFS/pcache/WAL subsystems, enforcing the invariants needed for atomic commit and rollback. For rollback-journal mode it writes original page images to a separate journal before overwriting database pages, detects and replays hot journals, coordinates super-journals for multi-database commits, and updates database header change counters. For WAL mode it delegates concurrency and persistence to `wal.c`, while still owning page cache state, savepoint interactions, backup notifications, mmap fetches, and transaction state.

The large design comment at the top is part of the contract: database pages are not overwritten until safely journaled or otherwise overwriteable; database writes are page-aligned; journal/database sync ordering protects rollback; exclusive locks guard database writes; shared locks guard reads; and bytes 24..39 of page 1 are used as cache invalidation/version evidence.

## Important Types, State, and Constants

- `Pager` is the central object. Its configuration fields include VFS/file handles, journal mode, sync policy, temp/memory/read-only flags, page size/reserve bytes, sector size, mmap limit, busy handler, and WAL pointers. Its mutable state includes `eState`, `eLock`, `dbSize`, `dbOrigSize`, `dbFileSize`, `dbHintSize`, `errCode`, `journalOff`, `journalHdr`, `nRec`, `pInJournal`, `aSavepoint`, `iDataVersion`, `dbFileVers`, mmap outstanding counts, and the PCache pointer.
- Pager states are `PAGER_OPEN`, `PAGER_READER`, `PAGER_WRITER_LOCKED`, `PAGER_WRITER_CACHEMOD`, `PAGER_WRITER_DBMOD`, `PAGER_WRITER_FINISHED`, and `PAGER_ERROR`. The normal rollback path is open/shared read, writer lock, cache modification after journal creation, database modification after journal sync, and finished after phase-one commit. WAL never enters DBMOD or FINISHED.
- `UNKNOWN_LOCK` records a conservative lock state after an unlock failure from error recovery, forcing later hot-journal handling to assume risk rather than trusting `xCheckReservedLock()`.
- `PagerSavepoint` arrays and bitvecs track savepoint boundaries and which pages have been captured in the sub-journal.
- `aJournalMagic`, `JOURNAL_PG_SZ()`, and `JOURNAL_HDR_SZ()` define rollback journal record/header layout. Journal records are page number, page data, and checksum; headers contain magic, record count, checksum seed, original database size, sector size, and page size.
- `MEMDB` and `USEFETCH` compile-time/runtime macros gate in-memory databases and mmap `xFetch()` access.

## Important APIs and Functions

- Diagnostics and state guards: `assert_pager_state()` validates state/lock/file/cache invariants in debug builds. `print_pager_state()` formats pager internals for debugger use.
- File integer helpers: `read32bits()`, `write32bits()`, and `put32bits` encode journal fields as big-endian values.
- Lock wrappers: `pagerLockDb()`, `pagerUnlockDb()`, and `pager_wait_on_lock()` centralize VFS lock transitions and busy-handler retry behavior.
- Journal format helpers: `journalHdrOffset()`, `writeJournalHdr()`, `readJournalHdr()`, `zeroJournalHdr()`, `readSuperJournal()`, `writeSuperJournal()`, and `pager_cksum()` construct, parse, invalidate, and validate rollback-journal data.
- Transaction cleanup/error paths: `pager_end_transaction()`, `pager_unlock()`, `pager_error()`, `pagerUnlockAndRollback()`, `pager_reset()`, and `pager_truncate()` release savepoints, finalize journals, drop locks, discard stale cache, enter/leave error state, and resize the database file.
- Rollback playback: `pager_playback_one_page()`, `pager_playback()`, `pagerPlaybackSavepoint()`, and `pager_delsuper()` restore pages from main journals/sub-journals and clean up super-journals once all child journals are safe.
- WAL integration: `pagerBeginReadTransaction()`, `pagerRollbackWal()`, `pagerUndoCallback()`, `pagerWalFrames()`, `pagerOpenWalIfPresent()`, and `sqlite3PagerDirectReadOk()` bridge pager state/cache behavior to WAL snapshots, WAL undo, WAL frame writes, and direct overflow reads.
- Page and cache APIs: `sqlite3PagerGet()`, `getPageNormal()`, `getPageMMap()`, `getPageError()`, `sqlite3PagerLookup()`, `sqlite3PagerUnref*()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, and `sqlite3PagerShrink()` provide page fetch/release and cache tuning behavior.
- Pager lifecycle and metadata: `sqlite3PagerOpen()`, `sqlite3PagerClose()`, `sqlite3PagerSetFlags()`, `sqlite3PagerSetBusyHandler()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerReadFileheader()`, `sqlite3PagerPagecount()`, `sqlite3PagerDataVersion()`, `sqlite3PagerTempSpace()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerPagenumber()`, and `sqlite3_database_file_object()`.
- Write path: `sqlite3PagerSharedLock()`, `sqlite3PagerBegin()`, `pager_open_journal()`, `pagerAddPageToRollbackJournal()`, `pager_write()`, `pagerWriteLargeSector()`, `sqlite3PagerWrite()`, `subjournalPage()`, `pagerStress()`, `sqlite3PagerFlush()`, `sqlite3PagerDontWrite()`, `pager_incr_changecounter()`, `syncJournal()`, `pager_write_pagelist()`, `sqlite3PagerSync()`, `sqlite3PagerExclusiveLock()`, and `sqlite3PagerCommitPhaseOne()` implement read-lock acquisition, write transaction start, page journaling, cache spill, dirty-page flush, and phase-one commit durability.

## Control Flow

Opening a pager with `sqlite3PagerOpen()` computes canonical paths and adjacent journal/WAL names, allocates one contiguous block for `Pager`, PCache, VFS file handles, filename strings, and journal names, opens the database if non-temporary, chooses defaults from sector/device characteristics, sets the page size and PCache, initializes journal mode and sync policy, and installs the page getter method. Temporary, immutable, and memory-like databases are treated as already locked/exclusive where appropriate.

Reads begin through `sqlite3PagerSharedLock()`. In rollback mode, the pager obtains a SHARED lock from OPEN, checks for a hot journal with `hasHotJournal()`, escalates directly to EXCLUSIVE if recovery is required, opens/syncs/replays the journal with `pager_playback()`, then validates the cached file-version bytes and discards cache/mmap mappings if another connection changed the file. It then opens WAL mode if a WAL file is present. In WAL mode it starts a WAL read transaction and resets cache if the snapshot changed. Finally it determines `dbSize` and enters READER.

Page fetches dispatch through `pPager->xGet`. `getPageNormal()` returns cached pages when possible, otherwise allocates/fetches from PCache, zero-fills pages beyond `dbSize` or requested with `PAGER_GET_NOCONTENT`, or reads from database/WAL via `readDbPage()`. `getPageMMap()` uses VFS `xFetch()` for eligible read-only pages outside page 1, falling back to normal fetch if WAL contains the page, mmap is unavailable, or a writable/cache copy is needed. `getPageError()` returns the stored persistent pager error.

Writes start with `sqlite3PagerBegin()`. Rollback mode obtains RESERVED or EXCLUSIVE locks and records `dbOrigSize`, `dbFileSize`, and `dbHintSize`; WAL mode begins the WAL write transaction and optionally acquires an exclusive database lock for exclusive-mode connections. The first page modification calls `sqlite3PagerWrite()`, which opens/writes the rollback journal header through `pager_open_journal()` if still in WRITER_LOCKED. `pager_write()` marks the page dirty only after the journal path is ready, journals original page content if the page existed at transaction start, marks append pages as needing sync where required, sets `PGHDR_WRITEABLE` only after safe journaling, records savepoint sub-journal content if needed, and expands `dbSize`.

Dirty cache spill is handled by `pagerStress()`. It refuses to spill during rollback, user-disabled spill, no-sync-sensitive windows, or error state. In WAL mode it sub-journals for savepoints then emits a single WAL frame. In rollback mode it creates the journal if batch-atomic support requires it, syncs the journal before database writes when `PGHDR_NEED_SYNC` or still CACHEMOD, writes the page list to the database, and marks the page clean only on success.

Rollback and recovery use `pager_playback()` and `pager_playback_one_page()`. The main playback loop reads journal headers, uses the journal record count unless no-sync/safe-append rules require deriving it from file size, truncates the database to the original size on the first header, then replays page records. A replayed page may update only cache, update both cache and database, or be skipped if out of range/already done. Savepoint rollback uses a `Bitvec` to avoid duplicate restores across main journal segments and the sub-journal, and WAL savepoint rollback delegates to `sqlite3WalSavepointUndo()`.

Phase-one commit through `sqlite3PagerCommitPhaseOne()` is the durable write phase. WAL mode writes dirty pages as WAL frames with a commit mark, creating a page-1 frame if needed so the commit can be represented. Rollback mode updates the change counter, writes a super-journal pointer if supplied, syncs the rollback journal, writes dirty pages to the database, grows/truncates the file image if needed, and syncs the database unless `noSync` is requested. On success, non-WAL mode enters `PAGER_WRITER_FINISHED`; final journal deletion/truncation is intentionally left to phase two outside this chunk.

## State and Persistence Behavior

The pager treats `dbSize` as the current logical database image, `dbOrigSize` as the size at write-transaction start, and `dbFileSize` as the known on-disk page count. `dbHintSize` throttles size-hint file-control calls. Page 1 bytes 24..39 are cached in `dbFileVers` and used to invalidate cache after locks are reacquired.

Rollback-journal persistence depends on strict ordering: original pages are written to the journal before they are made writable; journal data is synced before database overwrites; database data is synced before the journal is finalized; and hot journals are synced before playback so repeated crash recovery sees stable recovery input. `PGHDR_NEED_SYNC` is the page-local marker that database writes must not occur until the relevant journal content is durable.

Journal modes alter finalization and storage: MEMORY journals are closed; TRUNCATE journals are truncated; PERSIST journals zero the first header unless a super-journal pointer or temp behavior requires truncation; DELETE journals are closed and deleted; OFF skips rollback-journal protection; WAL routes writes to the log instead of directly modifying the database file during the transaction.

Savepoints persist original page images in the sub-journal when a page might need to roll back to the savepoint state rather than transaction start. `PagerSavepoint.pInSavepoint` bitvecs prevent duplicate sub-journal records, while `iOffset`, `iHdrOffset`, and `iSubRec` delimit replay ranges.

Error state is intentionally sticky for I/O and full errors that may leave cache inconsistent. Major page APIs return `errCode` until all references are dropped and `pager_unlock()` can discard cache, reset mmap fetches, and return to OPEN. In-memory pagers cannot enter this persistent error state.

## Dependencies and Integration Points

- VFS/OS integration goes through `sqlite3OsOpen`, `Read`, `Write`, `Sync`, `Truncate`, `FileSize`, `Lock`, `Unlock`, `Access`, `Delete`, `FileControl`, `xFetch`, and `xUnfetch`. Device characteristics such as safe append, sequential writes, powersafe overwrite, atomic write, batch atomic write, immutable files, and undeletable-open files materially change pager behavior.
- PCache integration goes through `sqlite3PcacheOpen`, `Fetch`, `FetchStress`, `FetchFinish`, `MakeDirty`, `MakeClean`, `DirtyList`, `CleanAll`, `ClearWritable`, `Truncate`, `Clear`, `Ref`, and reference-count queries.
- WAL integration goes through `sqlite3WalBeginReadTransaction`, `sqlite3WalBeginWriteTransaction`, `sqlite3WalFrames`, `sqlite3WalFindFrame`, `sqlite3WalReadFrame`, `sqlite3WalUndo`, `sqlite3WalSavepointUndo`, `sqlite3WalDbsize`, `sqlite3WalClose`, `sqlite3WalEndReadTransaction`, and `sqlite3WalEndWriteTransaction`.
- Backup integration uses `sqlite3BackupUpdate()` when pages are restored/written and `sqlite3BackupRestart()` when cache-wide invalidation or WAL rollback makes incremental backup state stale.
- Btree integration is implied by page APIs and comments: btree calls shared-lock acquisition before fetching, holds page 1 until transaction/read end, uses `sqlite3PagerWrite()` before mutating page memory, reads headers with `sqlite3PagerReadFileheader()`, and uses `sqlite3PagerDontWrite()` for freelist leaf optimization.
- Compile-time feature flags (`SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_TEST`, `SQLITE_CHECK_PAGES`) change substantial paths and test-only counters/assertions.

## Risks and Edge Cases

- Lock-state conservatism is critical. Mishandling `UNKNOWN_LOCK` or direct SHARED-to-EXCLUSIVE hot-journal recovery can let another connection read a database before recovery or misclassify a hot journal.
- Journal header parsing must reject invalid sector/page sizes and corrupted magic/checksums without replaying garbage. The chunk contains several crash-window comments where using file size instead of `nRec`, or failing to zero a stale persistent-journal header, could corrupt a database after power loss.
- `PGHDR_NEED_SYNC`, `SPILLFLAG_NOSYNC`, and large-sector journaling are subtle. If pages sharing a physical sector are not all journaled and marked consistently, a torn sector write can invalidate rollback.
- `pagerStress()` can be invoked from memory pressure during otherwise read-like operations inside a transaction. Its errors call `pager_error()` because returning an I/O error without rollback would leave dirty cache and database state ambiguous.
- `sqlite3PagerDontWrite()` is deliberately disallowed for temp files and savepoints. Using it when original content may be needed for rollback would lose restore data.
- Super-journal cleanup reads child journal files and only deletes the super-journal when no live child still points to it. False deletion can break multi-file atomicity; false retention leaves harmless stale files.
- Mmap fetches must never serve page 1 and must be unfetched when cache invalidation or external truncate/extend cycles may make mappings stale.
- `sqlite3_database_file_object()` depends on the exact filename memory layout created by `sqlite3PagerOpen()`, and comments note external software depends on this layout. Any allocation-format refactor has compatibility risk.
- Batch-atomic and atomic-write paths rely on VFS file-control semantics. Failure fallback must recreate a journal or roll back atomic-write state correctly.

## Test Signals

- Debug builds should exercise `assert_pager_state()` across every state transition: OPEN->READER, READER->WRITER_LOCKED, journal open to CACHEMOD, journal sync to DBMOD, phase-one commit to FINISHED, error entry, and unlock recovery.
- Crash-recovery tests should cover hot journals with valid and invalid headers, no-sync `0xffffffff` record counts, persistent journals containing stale trailing headers, super-journal presence/absence, short reads, checksum mismatch, and recovery after sync/write/truncate failures.
- Locking tests should cover busy-handler retry only for NO_LOCK->SHARED and RESERVED->EXCLUSIVE, not SHARED->RESERVED or hot-journal SHARED->EXCLUSIVE.
- Savepoint tests should cover repeated modifications to the same page, pages beyond original size, sub-journal rollback after page movement, and WAL savepoint undo.
- Cache-spill tests should simulate memory pressure with `PGHDR_NEED_SYNC`, disabled spill, rollback spill inhibition, temp-file thresholds, and I/O errors from `pagerStress()`.
- WAL tests should cover read snapshot changes resetting cache, WAL commit with no dirty pages requiring page 1, WAL rollback reloading referenced pages, and backup restart/update notifications.
- Mmap tests should cover `xFetch()` success/fallback, page 1 exclusion, cache invalidation after file-version changes, and release of outstanding mmap headers on close.
- Compile-time matrix tests should include `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_OMIT_WAL`, mmap disabled/enabled, `SQLITE_CHECK_PAGES`, and `SQLITE_TEST` I/O fault simulation (`sqlite3FaultSim(400)` and simulated I/O disable/enable regions).

## Cross-Chunk Continuation Notes

Line 6685 ends before the implementation of `sqlite3PagerCommitPhaseTwo()`. The next chunk should connect this phase-one durable state to journal finalization, public rollback, savepoint opening/release/rollback APIs, page move/rekey operations, journal-mode transitions, and the remaining WAL management/snapshot APIs. It should also verify how `pager_end_transaction()` is invoked after successful phase two and how `pager_error()` is applied when finalization fails.
