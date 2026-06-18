# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 30613-37428

## Scope

This chunk covers the latter half of SQLite's pager implementation and the opening portion of `wal.c` inside the FoundationDB vendored SQLite amalgamation. It starts in the tail of journal-header parsing, continues through rollback-journal playback, pager open/read/write/commit/rollback/savepoint APIs, WAL mode switching, and then begins WAL file and wal-index infrastructure through iterator merge-sort setup.

The range is not a complete source-file unit. It begins after earlier pager state/type definitions and helper routines have already been declared, and it ends in the middle of WAL checkpoint iterator support after `walMergesort()`. The final per-file research should reconcile this with adjacent chunks for complete pager and WAL behavior.

## Purpose

The pager code in this chunk is the transactional storage boundary between btree pages and the VFS. It manages page-cache references, database-file locks, rollback journals, sub-journals for savepoints, hot-journal recovery, commit and rollback sequencing, change-counter maintenance, page-size/cache settings, and the transition to and from WAL mode.

The WAL code that starts near the end documents and implements the durable write-ahead log format and the transient shared-memory wal-index. It defines how WAL frames are checksummed, indexed by database page number, recovered after crashes, and opened through the VFS.

FoundationDB's copy includes a notable read-only WAL optimization in `readDbPage()`: for read-only pagers using WAL, if a page is not found in WAL, it tries `xReadZeroCopy()` on the database file and marks the page `PGHDR_ZERO_COPY`; `unpinZeroCopy()` releases it with `xReleaseZeroCopy()`. This depends on nonstandard VFS methods being available in this vendored integration.

## Important APIs, Types, and Functions

### Pager transaction and recovery helpers

- `writeMasterJournal()` appends a master-journal pointer record to the end of a rollback journal for multi-database transactions. It writes `PAGER_MJ_PGNO`, the master filename, length, checksum, and journal magic, then truncates any persistent-journal tail beyond the record so hot-journal detection can find it reliably.
- `pager_unlock()`, `pager_error()`, `pager_end_transaction()`, and `pagerUnlockAndRollback()` implement pager state cleanup. They destroy journal bitvecs and savepoints, end WAL read/write transactions, unlock or downgrade database locks, finalize rollback journals according to journal mode, and move the pager back to `PAGER_OPEN` or `PAGER_READER`.
- `pager_playback_one_page()` replays one journal or sub-journal record into the database file and/or page cache. It validates page numbers, checksums main-journal records, uses a `Bitvec` to avoid duplicate savepoint replay, handles page-1 reserve-size and file-version state, honors `PGHDR_NEED_SYNC`, and reinitializes page extra data through `xReiniter`.
- `pager_playback()` performs full rollback-journal replay, including master-journal existence checks, journal header parsing, original-size truncation, hot-journal cache reset, database sync, journal finalization, optional master-journal deletion, and sector-size restoration.
- `pagerPlaybackSavepoint()` rolls back savepoint state by replaying selected portions of the main journal and sub-journal, or delegates to WAL savepoint undo for WAL databases.

### Pager read, write, and commit APIs

- `sqlite3PagerOpen()` allocates one contiguous block containing `Pager`, `PCache`, database fd, sub-journal fd, main journal fd, and pathname buffers. It opens the database unless it is temp or memory-backed, chooses default page size from defaults, sector size, and optional atomic-write capabilities, initializes `PCache`, lock state, journal mode, sync flags, and WAL path.
- `sqlite3PagerSharedLock()` opens a read transaction. In rollback mode it obtains a shared lock, detects and rolls back hot journals, validates the cached file-version bytes at offset 24, opens WAL mode if a `-wal` file is present, and computes `dbSize`. In WAL mode it starts a WAL read transaction snapshot.
- `sqlite3PagerAcquire()`, `sqlite3PagerLookup()`, `sqlite3PagerRef()`, and `sqlite3PagerUnref()` manage page-cache references. `Acquire` either returns an existing initialized page, zero-fills out-of-range/no-content pages, or reads from WAL/database using `readDbPage()`. Releasing the last reference may trigger rollback and unlock.
- `readDbPage()` reads a page from WAL if present, otherwise from the database file. It treats short reads as zero-filled tail, updates `dbFileVers` from page 1, applies the pager codec, increments read counters, and includes the FoundationDB zero-copy read path for read-only WAL misses.
- `pager_open_journal()`, `pager_write()`, and `sqlite3PagerWrite()` start rollback-journal logging and mark pages writable. They allocate `pInJournal`, write journal headers and page records with checksums, update savepoint bitvecs, set `PGHDR_NEED_SYNC`, and handle the special case where multiple pages share a disk sector.
- `syncJournal()` upgrades to an exclusive lock, syncs or updates journal headers based on `SQLITE_IOCAP_SAFE_APPEND` and `SQLITE_IOCAP_SEQUENTIAL`, clears stale future journal headers in persistent mode, and transitions from `PAGER_WRITER_CACHEMOD` to `PAGER_WRITER_DBMOD`.
- `pager_write_pagelist()` writes dirty cache pages to the database file in page order, skipping pages beyond the current image or flagged `PGHDR_DONT_WRITE`, updating page 1 file-version bytes and backup consumers.
- `sqlite3PagerCommitPhaseOne()` implements the durable part of commit: update change counters, ensure truncation victims are journaled for auto-vacuum, write master-journal name, sync journal, write dirty pages, resize database file, and sync the database. In WAL mode it writes dirty pages as WAL frames and cleans the cache.
- `sqlite3PagerCommitPhaseTwo()` makes rollback-mode commit irrevocable by finalizing the journal using `pager_end_transaction()`. `sqlite3PagerRollback()` restores rollback-mode state with journal playback or WAL-mode state with savepoint/WAL undo.

### Pager configuration, savepoints, and integration APIs

- `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSafetyLevel()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerReadFileheader()`, and `sqlite3PagerPagecount()` expose cache, synchronous, page-size, size-limit, header-read, and page-count controls to upper layers.
- `sqlite3PagerOpenSavepoint()` and `sqlite3PagerSavepoint()` create, release, and roll back pager savepoints. Savepoints store original database size, main-journal offsets, sub-journal record counts, per-savepoint bitvecs, and WAL savepoint data.
- `sqlite3PagerDontWrite()` optimizes pages whose contents no longer matter, typically freelist leaves, by marking dirty pages as `PGHDR_DONT_WRITE` when there are no savepoints.
- `sqlite3PagerMovepage()` supports auto-vacuum page relocation. It preserves rollback semantics by sub-journaling dirty moved pages, moves/evicts colliding cache entries, preserves `PGHDR_NEED_SYNC` hazards, and in memory databases keeps the original page available for rollback.
- `sqlite3PagerSetJournalMode()`, `sqlite3PagerLockingMode()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, `sqlite3PagerCheckpoint()`, and related accessors bridge btree pragmas and APIs to pager state, rollback journal deletion, WAL opening/closing, and checkpointing.
- Optional codec hooks (`sqlite3PagerSetCodec()`, `sqlite3BtreePagerSetCodec()`, `sqlite3PagerGetCodec()`, `sqlite3PagerCodec()`) transform page bytes when reading, writing journals, writing database pages, and writing WAL frames.

### WAL structures and helpers

- `WalIndexHdr` is the shared wal-index header copied twice in shared memory. It stores version, initialization flag, checksum byte order, page size, `mxFrame`, database page count, last-frame checksum, salts, and header checksum.
- `WalCkptInfo` tracks checkpoint backfill progress and per-reader read marks. `READMARK_NOT_USED` marks unused reader slots.
- `Wal` stores VFS and file handles, shared wal-index mappings, page size, lock/read-only/exclusive state, current wal-index header, WAL filename, and checkpoint sequence.
- `WalIterator` and nested `WalSegment` describe checkpoint iteration over the latest WAL frame per database page in page-number order.
- WAL constants define file format versions, locking-byte indexes, header and frame sizes, magic number, wal-index layout, hash-table sizes, and `walFrameOffset()`.
- `walIndexPage()`, `walCkptInfo()`, `walIndexHdr()`, `walHashGet()`, `walFramePage()`, and `walFramePgno()` map shared-memory wal-index pages and expose page-number arrays/hash tables.
- `walChecksumBytes()`, `walEncodeFrame()`, and `walDecodeFrame()` implement WAL header/frame checksum and frame validation using salts, page number, commit-size field, and byte-order-dependent checksum accumulation.
- `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, and `walUnlockExclusive()` wrap VFS shared-memory locking and become no-ops in exclusive heap-memory WAL mode.
- `walCleanupHash()`, `walIndexAppend()`, and `walIndexRecover()` maintain/rebuild wal-index hash tables. Recovery scans the WAL file under exclusive recovery locks, validates the WAL header and frames, records only committed frames in `hdr.mxFrame`/`hdr.nPage`, resets checkpoint/read marks, and logs recovery when frames are recovered.
- `sqlite3WalOpen()` allocates a `Wal` handle plus WAL fd storage, opens the `-wal` file, records read-only status, and selects heap-memory wal-index mode when requested.
- `walIteratorNext()`, `walMerge()`, and `walMergesort()` begin checkpoint iterator support by merging sorted frame-index lists while keeping the latest frame for duplicate database-page keys.

## Control Flow

Read transactions enter through `sqlite3PagerSharedLock()`. In rollback mode, the pager moves from `PAGER_OPEN` toward `PAGER_READER` by acquiring `SHARED_LOCK`, checking `hasHotJournal()`, and if necessary upgrading directly to `EXCLUSIVE_LOCK` to run `pagerSyncHotJournal()` and `pager_playback()`. Once any hot journal is settled, the cache is invalidated if the database version bytes changed, WAL is opened if a valid `-wal` file exists, and `dbSize` is populated. In WAL mode, the read path calls `pagerBeginReadTransaction()`, which ends any previous read transaction, starts a snapshot with `sqlite3WalBeginReadTransaction()`, and resets the pager cache if the WAL snapshot changed.

Page acquisition flows through `sqlite3PagerAcquire()`. It first asks `PCache` for the page. Existing initialized pages return immediately; new pages are either zeroed for `noContent`, memory DB, or beyond-end reads, or filled by `readDbPage()`. WAL reads consult `sqlite3WalRead()` before the database file. The FoundationDB read-only WAL branch tries a zero-copy database read for non-WAL frames and marks the page so later page-cache release logic can unpin it.

Write transactions start in `sqlite3PagerBegin()`. Rollback mode obtains a `RESERVED_LOCK`, optionally upgrades to exclusive, and snapshots `dbOrigSize`, `dbFileSize`, and `journalOff`. WAL mode obtains the WAL write lock and may also force database-file exclusive mode for exclusive locking. The first `sqlite3PagerWrite()` on a page opens the journal with `pager_open_journal()`, writes the original page image to the journal if needed, updates journal/savepoint bitvecs, and marks the page dirty. Spill pressure calls `pagerStress()`, which either appends a WAL frame or syncs the journal before writing a dirty page to the database file.

Rollback-mode commit is two-phase. `sqlite3PagerCommitPhaseOne()` updates page-1 change counters, journals truncation victims, writes any master-journal pointer, syncs the rollback journal, writes dirty pages, truncates or extends the database image, and syncs the database file. `sqlite3PagerCommitPhaseTwo()` then finalizes the journal by close/delete, truncate-to-zero, or zero-header depending on journal mode and exclusive mode; this is the point where rollback-mode commit becomes permanent. WAL-mode commit writes dirty pages as frames through `pagerWalFrames()`; final transaction cleanup goes through `pager_end_transaction()` and `sqlite3WalEndWriteTransaction()`.

Rollback has separate paths. Full rollback calls `sqlite3PagerRollback()`, which uses `pager_playback()` for rollback journals, `pagerPlaybackSavepoint()` and `sqlite3WalUndo()` for WAL, or finalizes an unopened/no-change journal directly. Savepoint rollback uses `pagerPlaybackSavepoint()` to replay the relevant main-journal segments and then sub-journal records, using `Bitvec` state so each page is restored once.

WAL recovery starts when a writer with the appropriate locks calls `walIndexRecover()`. It locks all shared-memory lock bytes other than already-held writer/checkpoint bytes, validates the WAL header, scans frames in file order, appends valid frames to wal-index hash tables, and only advances the durable snapshot when it sees commit frames. It then writes a fresh wal-index header and resets checkpoint metadata.

## State and Persistence Behavior

Persistent rollback-journal state includes journal headers, page records, checksums, master-journal pointers, and journal finalization mode. `PAGER_JOURNALMODE_DELETE` removes the journal, `TRUNCATE` truncates it, `PERSIST` zeroes the first header, `MEMORY` uses an in-memory journal descriptor, and `OFF` weakens rollback guarantees. `journalOff`, `journalHdr`, `nRec`, `setMaster`, `pInJournal`, and savepoint bitvecs track what has been recorded and what must be synced before database pages can be overwritten.

Persistent database state includes page content, database size, page-1 change counter at offset 24, version-valid-for counter at offset 92, SQLite version at offset 96, file truncation/extension state, and cached `dbFileVers` bytes used for cache invalidation. `dbSize`, `dbOrigSize`, `dbFileSize`, `dbHintSize`, and `mxPgno` are the pager's in-memory model of that state.

WAL persistent state is the `-wal` file: a 32-byte header plus 24-byte frame headers and page data. Frames become part of a committed snapshot only when the frame header's truncate/database-size field is nonzero. Salts and checksums prevent old frames and partially written frames from being accepted after crash or checkpoint reuse.

The wal-index is intentionally transient shared memory or heap memory in exclusive mode. It is rebuilt from the WAL by `walIndexRecover()`, stores native-endian metadata, duplicated headers with checksums, reader marks, checkpoint backfill count, frame-to-page arrays, and hash tables. It is not a persistent cross-platform format.

Pager error state is conservative. `pager_error()` moves the pager to `PAGER_ERROR` for `SQLITE_FULL` or `SQLITE_IOERR` class errors, causing major APIs to return the saved error until the cache is discarded and locks/journals are cleaned up. This prevents possibly corrupt cache contents from being reused after failed I/O.

## Dependencies and Integration Points

This chunk depends on earlier pager definitions in the same amalgamation: `Pager`, `PgHdr`, `PagerSavepoint`, pager state constants, lock constants, journal helpers such as `readJournalHdr()`, `writeJournalHdr()`, `zeroJournalHdr()`, `readMasterJournal()`, `pageInJournal()`, `subjRequiresPage()`, `pagerUseWal()`, `pagerLockDb()`, and `pagerUnlockDb()`.

It integrates heavily with the VFS layer through `sqlite3OsOpen`, `Read`, `Write`, `Sync`, `Truncate`, `FileSize`, `Access`, `Delete`, `FileControl`, `ShmMap`, `ShmLock`, `ShmBarrier`, and `ShmUnmap`. Correctness depends on VFS device-characteristic flags such as `SQLITE_IOCAP_SAFE_APPEND`, `SEQUENTIAL`, `ATOMIC`, and `UNDELETABLE_WHEN_OPEN`, plus FoundationDB's additional zero-copy methods.

It depends on PCache APIs for cache allocation, dirty-list handling, refcounts, page movement, clean/dirty flags, sync-flag clearing, truncation, and stress callbacks. It also integrates with backup APIs (`sqlite3BackupRestart()`, `sqlite3BackupUpdate()`), bitvec allocation for journal/savepoint membership, optional codec transforms, malloc fault injection/test macros, and btree-facing pager APIs.

WAL integration points include pager calls into `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalRead()`, `sqlite3WalFrames()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, `sqlite3WalCheckpoint()`, and related exclusive-mode helpers defined elsewhere in `wal.c`.

The public surface to upper SQLite layers is the `SQLITE_PRIVATE sqlite3Pager*` API set, used primarily by btree, pragma/opcode handling, backup, WAL checkpoint APIs, and codec-enabled builds.

## Risks

- Pager state transitions are crash-safety critical. Moving to `WRITER_DBMOD` before the journal is durable, clearing `PGHDR_NEED_SYNC` too early, or finalizing the journal before database sync can corrupt the database after power loss.
- Journal-header and `nRec` handling is subtle. Incorrect handling of persistent-journal tails, safe-append assumptions, full-sync ordering, or the ticket #2565 zero-record case can cause recovery to replay stale or incomplete records.
- Savepoint rollback depends on correct bitvec accounting across main journal, sub-journal, moved pages, and truncation. Missing a `subjournalPage()` call can make `ROLLBACK TO` restore the wrong image or fail after cache spill.
- Page movement and auto-vacuum are high risk because cache page numbers, dirty flags, `PGHDR_NEED_SYNC`, journal membership, and in-memory database rollback copies must remain coherent.
- WAL checksum, salt, and byte-order code defines the boundary between valid committed frames and garbage. Any drift in `walEncodeFrame()`, `walDecodeFrame()`, or recovery can accept torn writes or reject valid commits.
- WAL shared-memory locking is concurrency-sensitive. Reader marks, recovery locks, checkpoint locks, writer locks, and exclusive heap-memory mode must match VFS semantics or readers/checkpointers/writers can observe inconsistent snapshots.
- `walIndexAppend()` and `walCleanupHash()` must preserve hash-table reachability and last-frame lookup semantics. Off-by-one errors around `HASHTABLE_NPAGE_ONE` and later blocks can make reads find stale page versions.
- Read-only zero-copy integration assumes `xReadZeroCopy()` and `xReleaseZeroCopy()` obey pager lifetime, alignment, and immutability expectations. Incorrect VFS behavior could leave cache pages pointing at invalid memory or bypass codec expectations.
- `journal_mode=OFF`, `noSync`, and temp-file paths intentionally weaken durability. Callers and tests need to distinguish expected data-loss windows from corruption in default durable modes.
- Codec-enabled builds increase risk because bytes are transformed at journal write/read, database write/read, WAL frame write, and backup update boundaries.

## Test and Validation Signals

Useful validation should include pager crash-recovery, savepoint, WAL, and VFS-behavior tests:

- Rollback-journal commit/rollback tests across `DELETE`, `TRUNCATE`, `PERSIST`, `MEMORY`, and `OFF` journal modes, including exclusive and normal locking modes.
- Power-failure or fault-injection tests around journal header writes, `nRec` updates, journal sync, database page writes, database truncation, and journal finalization.
- Hot-journal recovery tests where a journal exists with and without a master-journal pointer, with stale persistent-journal tail data, with short reads, and with invalid checksums.
- Savepoint tests that combine page modifications before/after savepoints, cache spills, page moves, database truncation/auto-vacuum, WAL savepoints, and nested release/rollback operations.
- WAL tests for read snapshots, writer rollback, WAL frame checksums, salt changes after checkpoint/reset, wal-index rebuild after deleting shared memory, read-only WAL access, and checkpoints with active readers.
- Concurrency tests with multiple readers, writers, and checkpointers exercising `WAL_READ_LOCK`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, and `WAL_RECOVER_LOCK`.
- VFS matrix tests for `SAFE_APPEND`, `SEQUENTIAL`, `ATOMIC`, `UNDELETABLE_WHEN_OPEN`, shared-memory support, read-only WAL open, and temp-file behavior.
- FoundationDB-specific zero-copy tests that verify read-only WAL misses can use `xReadZeroCopy()`, fall back cleanly on failure or short/funny-length reads, release pins exactly once, and do not run through incompatible codec paths.
- Codec builds should validate encrypted or transformed page content through database reads/writes, rollback journals, sub-journals, WAL frames, and backup update hooks.
- Existing SQLite debug/test signals in this chunk include `assert_pager_state()`, `testcase()` coverage points, `SQLITE_CHECK_PAGES` page hashes, `SQLITE_ENABLE_EXPENSIVE_ASSERT` WAL hash reachability checks, `PAGERTRACE`, `IOTRACE`, `WALTRACE`, and simulated I/O error controls.
