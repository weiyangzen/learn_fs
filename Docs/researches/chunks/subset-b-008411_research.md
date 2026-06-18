# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 37429-45048

## Scope And Purpose

This chunk spans the end of SQLite's WAL implementation, the Btree mutex support block, the online backup API, VDBE memory/value helpers, VDBE construction and teardown helpers, record serialization/comparison helpers, and the opening safety checks for the VDBE public API layer.

The WAL section is responsible for checkpointing frames back into the database, opening consistent reader snapshots, writing committed frames, rolling back uncommitted WAL writes, savepoint state, WAL close/delete behavior, and locking-mode transitions. The backup section implements `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, progress accessors, and pager callbacks that keep an incremental backup consistent while the source changes. The VDBE sections manage `Mem` values, statement bytecode construction, statement halt/reset/finalize semantics, cursor cleanup, multi-database commit orchestration, record encoding/decoding, and index key comparison.

This chunk is persistence-critical: it controls when WAL data becomes durable database-file content, when database snapshots are considered safe, how backup copies are committed, how VM execution commits or rolls back transactions, and how on-disk record bytes are interpreted.

## Important APIs, Types, And Functions

WAL entry points in this range include `sqlite3WalClose`, `sqlite3WalBeginReadTransaction`, `sqlite3WalEndReadTransaction`, `sqlite3WalRead`, `sqlite3WalDbsize`, `sqlite3WalBeginWriteTransaction`, `sqlite3WalEndWriteTransaction`, `sqlite3WalUndo`, `sqlite3WalSavepoint`, `sqlite3WalSavepointUndo`, `sqlite3WalFrames`, `sqlite3WalCheckpoint`, `sqlite3WalCallback`, `sqlite3WalExclusiveMode`, and `sqlite3WalHeapMemory`.

Important WAL helpers include `walIteratorInit`, `walIteratorFree`, `walBusyLock`, `walPagesize`, `walCheckpoint`, `walIndexTryHdr`, `walIndexReadHdr`, `walTryBeginRead`, and `walRestartLog`. They operate on `Wal`, `WalIterator`, `WalIndexHdr`, `WalCkptInfo`, hash-table segments, read marks, WAL locks, checksums, salt values, and VFS file handles.

The Btree mutex block defines `MemPage`, `BtLock`, `Btree`, and mutex-array routines used to lock shared btrees in stable pointer order. These functions are integrated later with VDBE bytecode execution through `sqlite3VdbeUsesBtree()` and `sqlite3VdbeMutexArrayEnter()`.

Backup APIs and helpers include `sqlite3_backup_init`, `sqlite3_backup_step`, `sqlite3_backup_finish`, `sqlite3_backup_remaining`, `sqlite3_backup_pagecount`, `sqlite3BackupUpdate`, `sqlite3BackupRestart`, `sqlite3BtreeCopyFile`, `findBtree`, `setDestPgsz`, `backupOnePage`, `backupTruncateFile`, and `attachBackupObject`. The central state object is `struct sqlite3_backup`, with source/destination handles, btrees, progress counters, current page, destination lock state, schema cookie, error code, and pager callback linkage.

VDBE `Mem` helpers include `sqlite3VdbeChangeEncoding`, `sqlite3VdbeMemGrow`, `sqlite3VdbeMemMakeWriteable`, `sqlite3VdbeMemExpandBlob`, `sqlite3VdbeMemNulTerminate`, `sqlite3VdbeMemStringify`, `sqlite3VdbeMemFinalize`, `sqlite3VdbeMemReleaseExternal`, `sqlite3VdbeMemRelease`, numeric conversion helpers, setters for NULL/int/double/zeroblob/rowset/string, copy/move helpers, `sqlite3MemCompare`, `sqlite3VdbeMemFromBtree`, and `sqlite3ValueText`/`sqlite3ValueNew`/`sqlite3ValueFromExpr`/`sqlite3ValueSetStr`/`sqlite3ValueFree`/`sqlite3ValueBytes`.

VDBE construction and lifecycle helpers include `sqlite3VdbeCreate`, `sqlite3VdbeSetSql`, `sqlite3_sql`, opcode add/change helpers, label resolution, `sqlite3VdbeTakeOpArray`, `sqlite3VdbeUsesBtree`, debug/explain printing, `sqlite3VdbeMakeReady`, `sqlite3VdbeFreeCursor`, `sqlite3VdbeFrameRestore`, `sqlite3VdbeSetNumCols`, `sqlite3VdbeSetColName`, `sqlite3VdbeCloseStatement`, `sqlite3VdbeCheckFk`, `sqlite3VdbeHalt`, `sqlite3VdbeReset`, `sqlite3VdbeFinalize`, `sqlite3VdbeDeleteObject`, `sqlite3VdbeDelete`, and `sqlite3VdbeCursorMoveto`.

Record helpers include `sqlite3VdbeSerialType`, `sqlite3VdbeSerialTypeLen`, `sqlite3VdbeSerialPut`, `sqlite3VdbeSerialGet`, `sqlite3VdbeRecordUnpack`, `sqlite3VdbeDeleteUnpackedRecord`, `sqlite3VdbeRecordCompare`, `sqlite3VdbeIdxRowid`, and `sqlite3VdbeIdxKeyCompare`. This amalgamation has a notable extended `sqlite3VdbeRecordCompare()` signature with `startField` and `pRestartField`, allowing comparison to resume after loading more partial key data.

The chunk ends at `sqlite3_expired`, `vdbeSafety`, and `vdbeSafetyNotNull`, which guard public statement APIs against finalized or NULL prepared statements.

## Control Flow

WAL checkpointing starts with `sqlite3WalCheckpoint()`: it obtains `WAL_CKPT_LOCK`, optionally obtains `WAL_WRITE_LOCK` for full/restart checkpoints, reads or reconstructs the wal-index header, validates the page-size buffer, calls `walCheckpoint()`, reports log/backfill counts, clears a stale local header if needed, and releases locks.

`walCheckpoint()` builds a sorted `WalIterator` over WAL frames, computes `mxSafeFrame` from active reader marks, takes `WAL_READ_LOCK(0)` while backfilling, optionally syncs the WAL, hints database file size, copies eligible frame payloads from WAL offsets to database page offsets, truncates and syncs the database if all frames are checkpointed, then advances `nBackfill`. Passive checkpoints tolerate busy readers by limiting safe backfill and converting reader-related `SQLITE_BUSY` to success. Restart checkpoints additionally wait for all read locks so the next writer can wrap the WAL.

Read transaction startup flows through `sqlite3WalBeginReadTransaction()` and repeated `walTryBeginRead()` calls. It reads the wal-index header without a lock, retries with `WAL_WRITE_LOCK` and recovery if the header is dirty/corrupt, may bypass the WAL with `WAL_READ_LOCK(0)` if all frames are backfilled, otherwise chooses a read-mark slot not greater than `mxFrame`, locks it shared, and verifies both the read mark and wal-index header after a memory barrier. Transient races return `WAL_RETRY`; excessive retries sleep with increasing delay and eventually return `SQLITE_PROTOCOL`.

WAL page reads use the snapshot header's `mxFrame`, skip WAL access when the snapshot is empty or read-lock 0 is held, search wal-index hash tables from newest segment to oldest, bound matches to frames visible to the reader, detect excessive hash collisions as corruption, and read the selected frame payload from the WAL file.

WAL writes start with `sqlite3WalBeginWriteTransaction()` requiring an existing read transaction and a matching wal-index header snapshot to avoid forked histories. `sqlite3WalFrames()` may reset the log with `walRestartLog()`, writes a new WAL header for the first frame, writes frame headers and page data, may pad to a sector boundary before syncing, appends frame/page mappings to the wal-index, updates `mxFrame`, `nPage`, checksums, and `iCallback`, and writes the wal-index header on commit. Undo and savepoint rollback restore `mxFrame`/checksums and clean hash entries.

Backup control begins with `sqlite3_backup_init()` resolving source and destination btrees, setting destination page size to source page size, and incrementing the source backup count. `sqlite3_backup_step()` locks source/destination state, starts a destination write transaction and source read transaction as needed, copies up to `nPage` pages through `backupOnePage()`, attaches to the source pager if incremental work remains, and on completion updates the destination schema version, handles page-size/pending-byte truncation details, commits the destination transaction, and records progress. `sqlite3_backup_finish()` detaches the object, rolls back any unfinished destination work, stores the final error on the destination handle, and frees user-created backup handles.

`sqlite3BackupUpdate()` is the live consistency hook: if a source page already copied by an active backup changes, it re-copies the new page image into the destination. `sqlite3BackupRestart()` resets `iNext` to page 1 when external source changes make previously copied pages untrustworthy. `sqlite3BtreeCopyFile()` wraps the backup machinery for VACUUM-style complete btree copies using a stack `sqlite3_backup` object.

VDBE compilation builds bytecode with add-op helpers, negative labels, P4 ownership types, and optional debug comments. `resolveP2Values()` resolves labels, marks op flags, determines read-only status, and records maximum function argument count. `sqlite3VdbeMakeReady()` transitions the VM from init to run state and allocates registers, bound variables, cursor slots, function argument arrays, and variable-name arrays, first reusing unused opcode-array tail space and then falling back to a single heap allocation.

VDBE halt/reset flow is the transaction boundary for statement execution. `sqlite3VdbeHalt()` closes cursors, locks required btrees, classifies special errors, performs statement rollback or full transaction rollback when pager/cache state may be inconsistent, checks immediate and deferred foreign keys, commits autocommit transactions through `vdbeCommit()`, releases or rolls back statement savepoints, updates change counts, resets schema state on failed internal changes, releases btree mutexes, marks the VM halted, and invokes unlock-notify callbacks. `sqlite3VdbeReset()` transfers VM error state to the database handle, cleans result memory, profiles if enabled, and returns to init state. Finalize calls reset if needed and unlinks/frees the VM.

Record comparison flow unpacks serialized records into `Mem` cells, compares storage classes with SQLite ordering (`NULL`, numeric, text with collation, blob), handles DESC sort inversion, rowid-ignoring index comparisons, prefix/incremental-key flags, and corruption checks. The extended partial-record path in `sqlite3VdbeRecordCompare()` returns equality plus `pRestartField` when the left key buffer is incomplete and more bytes are required to decide the comparison.

## State And Persistence Behavior

WAL persistence is guarded by explicit fsync order. During checkpoint, the WAL is synced before frames are copied to the database file, and the database file is synced only when all WAL content has been copied and the database can safely replace the WAL as durable state. `nBackfill` is the persistent shared-memory progress marker for checkpointed frames; it only increases in `walCheckpoint()` except resets/recovery.

WAL read state is snapshot-based. `pWal->hdr` caches a verified wal-index header, `pWal->readLock` selects either database-only reads or a WAL read-mark slot, and memory barriers plus duplicated wal-index headers defend against torn concurrent reads. `pWal->writeLock`, `pWal->ckptLock`, `exclusiveMode`, `nCkpt`, salts, frame checksums, and `iCallback` model writer/checkpointer ownership and callback state.

`walRestartLog()` is a key persistence transition. When every frame has been backfilled and all nonzero reader locks can be obtained, it increments checkpoint salt state, resets `mxFrame` to zero, writes a new wal-index header, clears `nBackfill`, marks reader slots unused, and reacquires a WAL-using read snapshot for the writer.

Backup state is persistent at the destination pager/btree level. Page copies are journaled via normal pager writes, completion updates the schema cookie, truncation is coordinated with pager image truncation and commit phase one, and a destination transaction is committed only after all source pages are copied. Until finish or successful completion, `sqlite3_backup.rc`, `iNext`, `nRemaining`, `nPagecount`, `bDestLocked`, and `isAttached` describe resumable copy state.

VDBE `Mem` state is intensely ownership-sensitive. Flags distinguish NULL, integer, real, text, blob, rowset, aggregate, frame, static, ephemeral, dynamic, zero-filled blob tail, and nul-terminated storage. Helpers centralize destructor calls, `zMalloc` reuse, encoding conversion, shallow vs full copies, and length-limit checks. Incorrect flags can leak memory, double-free, compare invalid bytes, or return a pointer with the wrong lifetime.

VDBE transaction state lives in `db->autoCommit`, active/write VDBE counts, `db->nStatement`, `p->iStatement`, deferred FK counters, change counters, savepoints, btree transaction state, and virtual table sync/commit hooks. `vdbeCommit()` uses a master journal for atomic multi-file rollback-mode commits, while simple single-file or in-memory/temp cases commit each btree directly.

Record serialization persists SQLite storage classes to disk. The serial type table maps NULL, integer widths, IEEE float, integer constants 0/1, blob, and text to compact byte formats. Integer and float byte order are normalized; mixed-endian 64-bit float configurations have explicit swap logic and debug assertions.

## Dependencies And Integration Points

The WAL code integrates with the VFS and pager through `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsTruncate`, `sqlite3OsFileSize`, `sqlite3OsFileControl`, `sqlite3OsSleep`, WAL shared-memory mapping/locking primitives, and pager-provided buffers. It depends on hash-table helpers and constants defined earlier in `wal.c`, including `WAL_READ_LOCK`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, `WAL_RECOVER_LOCK`, `WAL_NREADER`, `HASHTABLE_NPAGE`, and `READMARK_NOT_USED`.

The backup API integrates database handles, btrees, pagers, source-pager backup callback lists, schema metadata, journal modes, pending-byte handling, page-size constraints, and the public `sqlite3_backup_*` API. It must cooperate with WAL mode, in-memory databases, codecs, and VACUUM's full-file copy path.

Btree mutex routines bridge connection-level mutexes, shared cache `BtShared` mutexes, and VDBE execution. They sort locks by `BtShared*` to avoid deadlock and maintain `wantToLock`/`locked` nesting state.

VDBE construction integrates parser/code generator output with execution. Opcode P4 ownership types reference collations, functions, key info, virtual tables, subprograms, memory values, integer arrays, and allocated strings. `sqlite3VdbeUsesBtree()` records which attached btrees a statement may touch so execution can acquire mutexes in the same global order.

VDBE halt integrates with pager/btree transaction phases, virtual table `xSync`/commit/rollback hooks, commit hooks, rollback hooks, foreign key enforcement, savepoints, schema invalidation, unlock-notify, and statement error propagation to `sqlite3_errcode()`/`sqlite3_errmsg()`.

Record helpers integrate the btree cursor layer, collation sequences, `KeyInfo`, `UnpackedRecord`, OP_MakeRecord output, OP_IsUnique prefix search, index rowid extraction, and cursor movement. They are central to table/index lookup correctness.

## Risks And Edge Cases

WAL checkpointing is concurrency- and crash-safety sensitive. A wrong `mxSafeFrame`, missed read-mark check, or premature database sync/truncate can overwrite pages needed by active readers or leave the database file ahead of durable WAL state after power loss.

The wal-index header is read lock-free first, so the duplicate-header checksum protocol and memory barriers are non-negotiable. Weakening `walIndexTryHdr()` or skipping the retry/recovery path can accept torn shared-memory state.

Read transaction startup intentionally has many `WAL_RETRY` paths. Changes around read-lock 0, read-mark selection, or post-lock header comparison can create snapshot corruption that appears only under concurrent writer/checkpointer races.

`sqlite3WalFrames()` writes frame bytes before appending wal-index entries and before publishing the commit header. Reordering those updates risks readers seeing incomplete frames or checkpointers missing committed frames. Sector-padding copies of the last frame are also subtle because they affect durable commit behavior under `sync_flags`.

Backup with differing source/destination page sizes is especially risky near the pending-byte page. The code skips pending-byte pages, may manually write source pages that straddle the destination pending-byte area, truncates the destination file outside normal page writes, and relies on pager phase-one journaling before direct file writes.

`sqlite3_backup_finish()` always rolls back an unfinished destination btree. Callers must not assume partially copied data is usable unless `sqlite3_backup_step()` reached `SQLITE_DONE` and finish returns `SQLITE_OK`.

`Mem` ownership flags are a persistent source of hazards. Shallow copies must not outlive their source bytes, dynamic destructors must be called exactly once, zero blobs must be expanded before mutation, and conversion helpers assume the database mutex is held when a `db` pointer exists.

`sqlite3VdbeHalt()` encodes SQLite's statement and transaction semantics. Small changes can regress conflict actions, autocommit behavior, deferred FK enforcement, active VDBE counters, statement journal rollback, virtual table commit ordering, or multi-database atomic commit.

The record comparison extension for partial keys is a local divergence from stock SQLite behavior. `startField`/`pRestartField` must remain synchronized with btree/pager callers that provide partial record buffers; returning a definitive comparison too early can misorder keys, while returning restart fields incorrectly can cause repeated work or missed comparisons.

Serialization/deserialization uses aliasing and byte-order-sensitive casts for integer and floating-point values. Compiler, architecture, or sanitizer changes should be tested around signed 6-byte/8-byte integers, NaN handling, and mixed-endian float builds.

## Test Signals

WAL test signals should include concurrent readers, writers, and checkpointers under PASSIVE, FULL, and RESTART modes; wal-index dirty-header recovery; WAL wrap/restart; active reader limiting of `nBackfill`; large-page and 65536-byte page sizes; injected `SQLITE_BUSY`, I/O errors, sync failures, and crash-recovery cases around checkpoint/write ordering.

Backup test signals should cover incremental and all-at-once backups, source changes after pages are copied, external source changes forcing restart, WAL-mode destination page-size mismatch returning `SQLITE_READONLY`, in-memory destination page-size mismatch, pending-byte-page handling with differing page sizes, finish after errors, and VACUUM `sqlite3BtreeCopyFile()` behavior.

VDBE memory tests should exercise text/blob ownership modes (`STATIC`, `TRANSIENT`, `DYNAMIC`, ephemeral), UTF-8/UTF-16 conversion, BOM handling, zero-blob expansion, rowset release, aggregate finalization, shallow/full copy lifetimes, length-limit `SQLITE_TOOBIG`, OOM behavior, and collation comparisons across encodings.

VDBE lifecycle tests should cover successful autocommit commit, statement rollback on `OE_Abort`, `OE_Fail` conflict handling, special errors (`NOMEM`, `IOERR`, `FULL`, `INTERRUPT`), deferred and immediate FK violations, commit hook failure, virtual table sync/commit ordering, multi-database master-journal commit, reset/finalize after partial execution, expired/run-only-once statements, and cursor invalidation after rollback.

Record helper tests should cover every serial type, integer boundary widths, file-format 4 integer constants, NaN deserialization, mixed text/blob comparisons, DESC sort order, prefix and incremental key flags, rowid extraction corruption checks, `UNPACKED_IGNORE_ROWID`, and the partial-record `pRestartField` path added to `sqlite3VdbeRecordCompare()`.

Static review signals in the code include many `assert()`, `testcase()`, `NEVER()`, and corruption returns (`SQLITE_CORRUPT_BKPT`) around boundary conditions. These mark intended fuzz/injection targets for this chunk.
