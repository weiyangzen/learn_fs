# subset-b-008806 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/wal.c -->
# sources/storage-engines/sqlite/src/wal.c

## Purpose

`wal.c` implements SQLite's write-ahead log subsystem for `journal_mode=WAL`. It owns the on-disk `-wal` format, the transient shared-memory `-shm` wal-index, read snapshots, single-writer enforcement, checkpoint backfill into the main database, WAL reset/truncation, optional snapshot APIs, optional blocking-lock timeout support, and Windows SEH handling for faults while touching memory-mapped shared memory.

The file is excluded when `SQLITE_OMIT_WAL` is defined. Otherwise it is the implementation behind the pager-facing APIs declared in `wal.h`.

## Important APIs, Types, and Functions

The central type is `struct Wal`, which binds the database file, WAL file, VFS, shared-memory pages, cached `WalIndexHdr`, current read/write/checkpoint lock state, page size, salts, callback frame number, size limits, and feature-specific fields for SEH, snapshots, and set-lock timeouts. `WalIndexHdr` is the duplicated shared-memory header containing WAL format version, change counter, page size, `mxFrame`, database page count, frame checksums, salts, and header checksum. `WalCkptInfo` follows the two headers in shared memory and stores `nBackfill`, `nBackfillAttempted`, reader marks, and reserved lock bytes. `WalIterator` is a checkpoint helper that merges wal-index segments in page-number order while keeping only the latest frame per database page.

Public entry points include `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalLimit()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, `sqlite3WalDbsize()`, `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, `sqlite3WalFrames()`, `sqlite3WalCheckpoint()`, `sqlite3WalCallback()`, `sqlite3WalExclusiveMode()`, `sqlite3WalHeapMemory()`, `sqlite3WalFile()`, and feature-gated snapshot, ZIPVFS, SEH, and blocking-lock functions.

Important private routines fall into clear groups. Format and checksum helpers include `walFrameOffset()`, `walChecksumBytes()`, `walEncodeFrame()`, `walDecodeFrame()`, and `walPagesize()`. Shared-memory helpers include `walIndexPage()`, `walIndexPageRealloc()`, `walIndexHdr()`, `walCkptInfo()`, `walIndexWriteHdr()`, `walIndexTryHdr()`, and `walIndexReadHdr()`. Hash/index routines include `walHashGet()`, `walFramePage()`, `walFramePgno()`, `walCleanupHash()`, `walIndexAppend()`, and `walIndexRecover()`. Locking routines include `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, `walUnlockExclusive()`, and `walBusyLock()`. Checkpoint traversal is implemented by `walIteratorInit()`, `walIteratorNext()`, `walMerge()`, `walMergesort()`, and `walCheckpoint()`. Write sequencing is implemented by `walRestartLog()`, `walWriteToLog()`, `walWriteOneFrame()`, `walRewriteChecksums()`, and `walFrames()`.

## Control Flow

Opening starts in `sqlite3WalOpen()`, which verifies WAL layout constants, allocates `Wal` plus an embedded `sqlite3_file`, opens the `-wal` file, records read-only state, configures sync/header-padding behavior from VFS device characteristics, and chooses normal shared-memory mode or heap wal-index mode for `bNoShm`.

Read transactions run through `sqlite3WalBeginReadTransaction()`, which wraps `walBeginReadTransaction()` in SEH where enabled. `walBeginReadTransaction()` repeatedly calls `walTryBeginRead()` until transient `WAL_RETRY` races settle or a protocol limit is reached. `walTryBeginRead()` loads or recovers the wal-index header, handles unreliable read-only shared memory by falling back to heap reconstruction, decides whether the WAL can be ignored via read-lock 0, or selects a reader mark not greater than the snapshot's `mxFrame`. After acquiring the shared read lock, it rechecks both the reader mark and the live header so a concurrent writer/checkpointer cannot make the cached snapshot unsafe. Reads then use `sqlite3WalFindFrame()` to search wal-index hash blocks from newest to oldest between `minFrame` and `mxFrame`; if a frame is found, `sqlite3WalReadFrame()` reads page content from the WAL file.

Write transactions require an existing read transaction. `sqlite3WalBeginWriteTransaction()` acquires `WAL_WRITE_LOCK` and rejects the write with `SQLITE_BUSY_SNAPSHOT` if the live wal-index header differs from the reader's cached header, preventing forked WAL histories. `sqlite3WalFrames()` writes dirty pages via `walFrames()`: it may reset the log if everything is checkpointed and no reader uses WAL frames, writes a new WAL header when starting from frame 1, appends or overwrites frames, handles commit markers through `nTruncate`, syncs according to `sync_flags`, pads to sector boundaries when needed, optionally limits WAL size, appends mapping entries to the wal-index, and publishes a new wal-index header on commit. `sqlite3WalEndWriteTransaction()` releases the writer lock and clears transient checksum/truncation state.

Rollback and savepoint flow is local to wal-index state. `sqlite3WalUndo()` restores the cached header from shared memory, invokes the pager callback for uncommitted frames, and prunes hash entries beyond the restored `mxFrame`. `sqlite3WalSavepoint()` captures `mxFrame`, frame checksums, and checkpoint counter; `sqlite3WalSavepointUndo()` restores those values and cleans the hash when rolling back to a savepoint, including the special case where the WAL was restarted after the savepoint was opened.

Checkpoint flow starts in `sqlite3WalCheckpoint()`, which obtains the checkpoint lock, optionally obtains the writer lock for FULL/RESTART/TRUNCATE modes, reads the wal-index header, validates page size against the caller's buffer, and calls `walCheckpoint()`. `walCheckpoint()` computes the maximum frame safe to backfill by inspecting reader marks, builds a `WalIterator`, syncs the WAL, hints database growth, copies the latest applicable frame for each database page into the database file, truncates and syncs the database if fully checkpointed, updates `nBackfill`, and for RESTART/TRUNCATE waits for WAL readers before resetting the header or truncating the WAL.

Recovery flow is driven by `walIndexReadHdr()` when the wal-index header is missing, dirty, corrupt, or uninitialized. It obtains the write lock, calls `walIndexRecover()`, reads the WAL header, validates magic/page-size/version/checksum/salts, scans frames until the first invalid frame, appends valid frame mappings, records the last commit frame as `mxFrame`, writes the rebuilt wal-index header, resets checkpoint metadata, initializes read marks, and logs recovery when frames were found.

## State and Persistence Behavior

Persistent state lives in the main database file and `-wal` file. The WAL header is 32 bytes and stores magic, version, page size, checkpoint sequence, salts, and checksum. Each frame has a 24-byte header with page number, commit database size or zero, salts, and rolling checksums, followed by page data. A transaction commits only when a frame with nonzero database size is written and later published through the wal-index header.

The wal-index is transient shared memory, normally backed by the `-shm` file. It is native-endian and can be rebuilt from the WAL after a crash. Its duplicated header uses a checksum and memory barriers to detect dirty reads; writers copy header copy 1 then copy 0, while readers read copy 0 then copy 1. Hash blocks map page numbers to frame indexes so readers can find the newest visible frame without scanning the WAL file.

Lock state is shared through VFS `xShmLock` slots at fixed offsets: write, checkpoint, recovery, and multiple read locks. `aReadMark[]` entries bound each reader's view, while `nBackfill` and `nBackfillAttempted` coordinate checkpoint progress and snapshot validity. Read-lock 0 means the reader ignores the WAL and reads only the database file.

Durability depends on the sync mode. WAL commits may sync the WAL and may pad transactions to sector boundaries. Checkpoints sync the WAL before copying pages and sync the database when the entire WAL is backfilled. WAL reset increments/checks salts to keep old frames from being mistaken for current content after reuse. Close may checkpoint and delete or truncate persistent WAL files depending on exclusive lock acquisition, persistent-WAL file-control result, and journal size limit.

## Dependencies and Integration Points

`wal.c` depends on `wal.h` and the broader SQLite internal layer from `sqliteInt.h`: VFS I/O (`sqlite3OsOpen`, `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsShmMap`, `sqlite3OsShmLock`, `sqlite3OsShmBarrier`, `sqlite3OsShmUnmap`, file-control hints), memory allocation, random salts, atomics, byte-order helpers, pager page headers, SQLite result codes, test macros, and logging. The pager uses this module for WAL-mode read/write transaction boundaries, page lookup, frame writes, rollback, checkpoint, close, and WAL hook callbacks.

The implementation is tightly coupled to VFS shared-memory semantics and lock-byte layout. It asserts compatibility with Unix and Windows shared-memory lock offsets and handles read-only WAL or read-only SHM cases explicitly. Compile-time features add integration points for `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_ENABLE_ZIPVFS`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_USE_SEH`, `SQLITE_TEST`, and `SQLITE_DEBUG`.

## Risks and Edge Cases

The highest-risk behavior is concurrency across processes. Correctness depends on fixed lock ordering, atomic 32-bit shared-memory loads/stores, barriers around duplicated headers, retry loops for transient races, and conservative handling when a header changes between observation and lock acquisition. Breaking any of these can expose corrupt snapshots, forked histories, or unsafe checkpoint backfill.

Crash recovery and persistence are also delicate. Header checksums, frame rolling checksums, salts, checkpoint counters, and WAL reset logic must agree. A missed checksum rewrite after overwriting frames, an incorrect `minFrame`, or an unsafe `nBackfill` update can make readers fetch the wrong page version. The code has several defensive corruptions checks, including page-size validation, WAL version validation, hash collision bounds, and database growth sanity checks during checkpoint.

Read-only and unreliable-shared-memory paths are specialized and easy to regress. `SQLITE_READONLY_CANTINIT`, heap wal-index reconstruction, retry when a writer fixes shared memory, and salt/frame checks are all necessary to avoid reading a stale WAL image. Snapshot APIs add another layer: snapshots are invalid if salts change or if a checkpoint has attempted frames beyond the snapshot.

Platform feature paths carry specific risk. Windows SEH must release transient locks and restore heap/shared-memory bookkeeping after in-page errors. Blocking-lock timeout builds must normalize `SQLITE_BUSY_TIMEOUT` and avoid unintended long waits in passive checkpoints. ZIPVFS relies on frame-size reporting under a live read lock.

## Test Signals

Strong tests should exercise concurrent readers and writers with snapshot isolation, `SQLITE_BUSY_SNAPSHOT` when a reader tries to upgrade after another writer commits, passive/full/restart/truncate checkpoints with active readers, WAL reset only after all frames are backfilled and no WAL readers remain, rollback and savepoint undo across appended and overwritten frames, WAL recovery after simulated crashes at header/frame/index-update boundaries, and read-only WAL/SHM cases.

Existing in-file signals include TH3/testcase annotations for corrupt page sizes, large offsets, checkpoint busy-handler requirements, WAL format assertions, `sqlite3FaultSim()` hooks for allocation and shared-memory faults, expensive assertions that compare hash lookup with linear search, and debug WAL tracing. Tests should cover sync modes, persistent WAL deletion/truncation policy, journal size limit, snapshot get/open/check/recover, SEH in-page-error handling where enabled, and set-lock timeout behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/wal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/wal.h -->
# sources/storage-engines/sqlite/src/wal.h

## Purpose

`wal.h` defines the internal interface between SQLite's pager and the write-ahead log implementation. It declares the opaque `Wal` handle, sync-flag extraction macros, savepoint data size, and all pager-facing WAL operations. It also supplies no-op macro substitutes when SQLite is compiled with `SQLITE_OMIT_WAL`.

## Important APIs, Types, and Functions

`WAL_SYNC_FLAGS(X)` extracts commit-sync flags from the low two bits of a combined sync flag word, while `CKPT_SYNC_FLAGS(X)` extracts checkpoint-sync flags from bits 2 and 3. `WAL_SAVEPOINT_NDATA` is `4`, matching the four `u32` values saved by `sqlite3WalSavepoint()` in `wal.c`.

The header forward-declares `typedef struct Wal Wal`, keeping the implementation private. Core lifecycle APIs are `sqlite3WalOpen()`, `sqlite3WalClose()`, and `sqlite3WalLimit()`. Reader APIs are `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, and `sqlite3WalDbsize()`. Writer APIs are `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, and `sqlite3WalFrames()`. Checkpoint and notification APIs are `sqlite3WalCheckpoint()` and `sqlite3WalCallback()`. Mode and inspection APIs are `sqlite3WalExclusiveMode()`, `sqlite3WalHeapMemory()`, and `sqlite3WalFile()`.

Feature-gated declarations expose `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, `sqlite3WalSnapshotRecover()`, `sqlite3WalSnapshotCheck()`, and `sqlite3WalSnapshotUnlock()` under `SQLITE_ENABLE_SNAPSHOT`; `sqlite3WalFramesize()` under `SQLITE_ENABLE_ZIPVFS`; `sqlite3WalWriteLock()` and `sqlite3WalDb()` under `SQLITE_ENABLE_SETLK_TIMEOUT`; and `sqlite3WalSystemErrno()` under `SQLITE_USE_SEH`.

## Control Flow

There is no executable control flow in this header, but the declarations describe the pager's WAL sequence. The pager opens a `Wal` object for a database file, begins and ends read transactions around page-cache access, asks whether a page has a visible WAL frame, reads that frame if present, upgrades a read transaction to a write transaction, writes dirty page frames, records or rolls back savepoints, checkpoints frames into the database, and closes the WAL on pager shutdown.

When `SQLITE_OMIT_WAL` is defined, the same call sites compile against macros returning benign defaults such as `SQLITE_OK`-like zero values, zero database size, and null WAL file pointers. This keeps WAL-free builds from needing alternate pager code for most calls.

## State and Persistence Behavior

The header itself stores no state. It defines the contract for state stored by `wal.c`: the opaque `Wal` object, reader snapshots, writer lock ownership, uncommitted frame positions, checkpoint progress, and WAL hook callback frame counts. Persistence effects are delegated to the implementation: frame writes to the `-wal` file, checkpoint writes to the database file, shared-memory wal-index updates, and possible WAL deletion or truncation on close.

`sync_flags` parameters deliberately combine commit and checkpoint sync policy in one integer. Callers must use the macros consistently so commits and checkpoint backfills use the correct VFS sync flags.

## Dependencies and Integration Points

`wal.h` includes `sqliteInt.h`, so it depends on SQLite internal types such as `sqlite3_vfs`, `sqlite3_file`, `sqlite3`, `PgHdr`, `Pgno`, `u8`, and `i64`. Its main consumer is the pager layer, with additional reach from public snapshot APIs and WAL-hook/checkpoint plumbing. `sqlite3WalFile()` exposes the WAL `sqlite3_file` for lower-level pager/VFS integration.

Compile-time flags shape the ABI visible inside SQLite. Builds without WAL get macro stubs and undefine `SQLITE_USE_SEH`; snapshot, ZIPVFS, blocking locks, and SEH declarations appear only when their feature macros are enabled.

## Risks and Edge Cases

Because this header is an internal boundary, signature drift between `wal.h` and `wal.c` would break pager integration. The no-op `SQLITE_OMIT_WAL` macros must preserve enough type and value compatibility that callers remain correct in WAL-free builds. `WAL_SAVEPOINT_NDATA` must match the implementation's savepoint payload exactly.

`sqlite3WalCheckpoint()` has many pointer and buffer parameters, so caller mistakes around `nBuf`, `zBuf`, or output pointers can surface as corruption checks or I/O errors in the implementation. Feature-gated declarations require call sites to be equally gated.

## Test Signals

Build tests should cover normal WAL-enabled builds, `SQLITE_OMIT_WAL`, snapshot-enabled builds, ZIPVFS builds, set-lock-timeout builds, and SEH builds where applicable. Pager-level tests should confirm the declared transaction sequence: begin read, find/read frame, begin write, frames, savepoint rollback, checkpoint, callback, exclusive mode transitions, and close. Compile-only tests are especially useful for the macro-stub path.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/wal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/walker.c -->
# sources/storage-engines/sqlite/src/walker.c

## Purpose

`walker.c` implements SQLite's generic parse-tree walker for SQL expressions and `SELECT` statements. It centralizes traversal order and callback dispatch so semantic analysis, name resolution, aggregate/window processing, rewrite passes, and validation code can inspect or transform parse trees without duplicating recursion logic.

## Important APIs, Types, and Functions

The file operates on the `Walker` type declared in `sqliteInt.h`. A `Walker` supplies `xExprCallback`, `xSelectCallback`, optional `xSelectCallback2`, parser context, and depth bookkeeping. Callback return values are `WRC_Continue`, `WRC_Prune`, and `WRC_Abort`.

`sqlite3WalkExprNN()` is the non-null expression walker. It invokes `xExprCallback()` before children, prunes children if the callback returns `WRC_Prune`, aborts on `WRC_Abort`, and otherwise descends into left/right children, subqueries, expression lists, and window-function metadata. `sqlite3WalkExpr()` is the null-safe wrapper. `sqlite3WalkExprList()` walks every expression in an `ExprList`.

`sqlite3WalkSelectExpr()` walks expressions attached to a `Select`: result list, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT, and conditionally window definitions. `sqlite3WalkSelectFrom()` walks subqueries and table-function arguments in the FROM clause. `sqlite3WalkSelect()` performs full SELECT traversal: pre-order select callback, expressions, FROM subqueries, optional post-order callback, and then the compound-select `pPrior` chain.

Window support is compiled unless `SQLITE_OMIT_WINDOWFUNC` is set. The private `walkWindowList()` walks ORDER BY, PARTITION BY, FILTER, frame start, and frame end expressions for a linked list of `Window` objects. `sqlite3WalkWinDefnDummyCallback()` is a no-op marker callback that causes `sqlite3WalkSelectExpr()` to traverse `Select.pWinDefn`.

Utility callbacks include `sqlite3WalkerDepthIncrease()`, `sqlite3WalkerDepthDecrease()`, `sqlite3ExprWalkNoop()`, and `sqlite3SelectWalkNoop()`.

## Control Flow

Expression traversal is pre-order. `sqlite3WalkExprNN()` calls the expression callback first; a nonzero callback result is masked with `WRC_Abort`, meaning `WRC_Prune` stops descent into that expression's children but lets sibling traversal continue. The function avoids recursion on the right child by tail-recursing through a loop when `pRight` exists. It asserts that an expression uses either `x.pList` or `pRight`, not both, and does not descend into token-only or leaf expressions.

Select traversal is also pre-order for the select callback. If no `xSelectCallback` is configured, `sqlite3WalkSelect()` is a no-op. Otherwise, for each select in the compound chain, it invokes `xSelectCallback()`, walks local expressions and FROM subqueries, then invokes `xSelectCallback2()` if present. `sqlite3WalkSelectExpr()` deliberately does not invoke the select callback for the current select; it only walks expressions and may walk window definitions when the callback state indicates rename processing, WITH-pop cleanup, or explicit window-definition traversal.

FROM traversal visits subquery SELECTs recursively and table-function argument expression lists. Compound SELECT traversal proceeds through `pPrior` after each current select is processed.

## State and Persistence Behavior

`walker.c` does not persist data and performs no I/O. Its only direct state mutation is through callbacks and `Walker.walkerDepth`. `sqlite3WalkerDepthIncrease()` increments depth on subquery entry and `sqlite3WalkerDepthDecrease()` decrements it on exit. The generic walker may indirectly mutate parse-tree nodes if caller-provided callbacks do so.

Because callbacks can abort, prune, or mutate, traversal state is intentionally simple and synchronous. Return values propagate `WRC_Abort` upward immediately to stop the full walk.

## Dependencies and Integration Points

The file depends on `sqliteInt.h` for all parse-tree types and macros, plus standard headers. It is integrated with expression structures (`Expr`, `ExprList`), SELECT structures (`Select`, `SrcList`, `SrcItem`), subquery wrappers, table-valued function arguments, window definitions, parser rename state (`IN_RENAME_OBJECT`), and CTE cleanup (`sqlite3SelectPopWith`) when CTE support is compiled.

Many SQLite subsystems use these traversal APIs indirectly through prototypes in `sqliteInt.h`. The walker provides consistent traversal semantics for name resolution, aggregate analysis, window handling, expression rewriting, authorization checks, and other parse-analysis passes.

## Risks and Edge Cases

The walker assumes parse-tree invariants such as non-null input to `sqlite3WalkExprNN()`, no simultaneous `x.pList` and `pRight`, and valid `SrcList` for a `Select`. Callers must use `sqlite3WalkExpr()` for nullable expressions. A callback returning the wrong `WRC_*` value can accidentally abort traversal or skip required children.

Window-definition traversal is intentionally conditional. A new caller that needs `pWinDefn` walked must use the recognized callback setup or update this logic. The `rc & WRC_Abort` masking behavior is subtle but important: `WRC_Prune` is returned as continue from the top-level walk after children are skipped. Changes here could break many semantic passes.

Deep parse trees still recurse through left children, expression lists, subqueries, and SELECT chains, so stack depth remains a consideration even with the right-child loop optimization. Mutating callbacks must account for traversal order and avoid invalidating nodes that the walker will visit later.

## Test Signals

Tests should cover expression callbacks that continue, prune, and abort; null expressions and empty expression lists; left/right expression trees; subquery expressions; FROM-clause subqueries; table-valued function arguments; compound SELECT chains; post-order select callbacks; window-function expressions and named window definitions; rename-object traversal; and walker-depth increment/decrement pairing.

Regression signals include name-resolution tests, aggregate/window query tests, ALTER TABLE rename tests, CTE tests, and parser fuzzing. Sanitizer or debug builds should catch invariant violations in malformed or transformed parse trees.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/walker.c -->
