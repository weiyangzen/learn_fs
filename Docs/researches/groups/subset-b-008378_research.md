# Research Group subset-b-008378

This grouped report covers Badger storage-engine files under `sources/storage-engines/badger`. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/levels.go -->
# sources/storage-engines/badger/levels.go

## Purpose
This file implements Badger's LSM level controller: startup table loading, manifest reconciliation, compaction scheduling, table selection, subcompaction, prefix/tree dropping, lookup iteration, table/level introspection, and checksum/key-split helpers. It is the central coordinator between memtable flush output, SSTable files, manifest durability, value-log discard statistics, and background compactor goroutines.

## Important APIs, Types, And Functions
`levelsController` owns `levels`, `kv`, `nextFileID`, L0 stall accounting, and `compactStatus`. `newLevelsController` reconciles `MANIFEST` with directory contents via `revertToManifest`, opens table files concurrently with encryption/compression options, initializes `levelHandler`s, validates invariants, and syncs the directory. `dropTree` removes all tables with manifest delete changes; `dropPrefixes` uses forced compactions to remove prefix ranges.

Compaction planning uses `targets`, `levelTargets`, `compactionPriority`, `pickCompactLevels`, `compactDef`, `fillTablesL0ToLbase`, `fillTablesL0ToL0`, `fillTables`, and `fillMaxLevelTables`. Execution flows through `doCompact`, `runCompactDef`, `compactBuildTables`, `subcompact`, `buildChangeSet`, and `addSplits`. Read and inspection APIs include `get`, `appendIterators`, `getTableInfo`, `getLevelInfo`, `verifyChecksum`, and `keySplits`.

## Control Flow
Startup validates manifest table presence, deletes unreferenced SSTables, opens each manifest table under a throttle of three goroutines, then initializes sorted level handlers and validates non-overlap/range invariants. Background compaction starts `NumCompactors` workers; worker zero prioritizes L0, and worker two optionally runs Lmax-to-Lmax stale-data cleanup every roughly ten seconds. Each worker repeatedly computes dynamic level targets, derives compaction priorities, fills a `compactDef` while registering ranges in `compactStatus`, builds replacement tables, writes manifest changes, swaps new tables into the destination level, deletes source tables, and clears compaction status.

`subcompact` merges ordered iterators over top and bottom tables, skips configured dropped prefixes, enforces snapshot visibility through `discardAtOrBelow`, respects `NumVersionsToKeep`, preserves deletion markers when lower-level overlap exists, records stale value-pointer bytes for value-log GC, and emits new tables through bounded builder goroutines. `addSplits` divides compactions by bottom-table key ranges when possible. `get` searches levels from L0 upward to avoid observing post-compaction lower levels with pre-compaction upper levels.

## State And Persistence Behavior
The controller is persistence-critical. Table creation/deletion is recorded in `MANIFEST` before old files are logically removed from levels, and newly built table directory entries are synced before manifest replacement. `addLevel0Table` writes a manifest create change before exposing a new non-memory table to L0. `dropTree` writes manifest delete changes before removing table refs. Compaction updates value-log discard stats based on discarded value pointers.

Dynamic targets use the size of the last level, base/table size multipliers, L0 table count, and a guard that clamps `baseLevel` to at least L1 so very large databases do not compact L0 into itself. In-memory mode bypasses manifest-backed table creation for in-memory tables and skips discard stats. L0 stalls are tracked when `tryAddLevel0Table` cannot add because table count is above the stall threshold.

## Dependencies And Integration Points
The file depends on `table.Table`, `table.Builder`, `levelHandler`, `compactStatus`, `keyRange`, `Manifest`, `pb.ManifestChangeSet`, `Options`, `KeyRegistry`, value-log discard stats, transaction oracle discard timestamps, Badger metrics in `y`, mmap files from `z`, and OpenTelemetry spans. It integrates with DB startup, memtable flushes, range iteration, `DropAll`, `DropPrefix`, value-log GC, checksum verification, and public table/level info APIs.

## Risks And Edge Cases
The main risks are compaction-order correctness, stale version deletion while snapshots exist, deletion-marker removal when lower levels still overlap, manifest/table swap ordering, L0 starvation/stalls, and memory pressure from subcompaction builders. The checksum mismatch path logs and ignores corrupt tables, which prioritizes opening over strict recovery and needs operational caution. `dropPrefixes` returns nil after some L0 compaction errors, so callers may not receive a hard failure for that stage. Same-level and L0-to-L0 compactions have special locking/status rules and are easy to regress.

## Test Signals
`levels_test.go` heavily exercises this file: overlap checks, version dropping, tombstone retention/removal, discard timestamps, `bitDiscardEarlierVersions`, same-level stale cleanup, prefix containment, compaction status cleanup, key splits, L0/L1 stall tests currently skipped, and the base-level-zero regression for huge Lmax sizes. Manifest tests indirectly validate compaction manifest change persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/levels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/levels_test.go -->
# sources/storage-engines/badger/levels_test.go

## Purpose
This test file validates Badger LSM compaction, lookup, version-retention, range-split, and stale-data cleanup behavior. It constructs synthetic SSTables directly, installs them into levels, and runs `levelsController` operations without relying solely on background compaction.

## Important APIs, Types, And Functions
`createAndOpen` builds a table from `keyValVersion` rows, writes a manifest create change, and appends the table to a target level. `getAllAndCheck` iterates all internal versions and checks key/value/version/meta ordering. Test cases include `TestCheckOverlap`, `TestCompaction`, `TestCompactionTwoVersions`, `TestCompactionAllVersions`, `TestDiscardTs`, `TestDiscardFirstVersion`, skipped `TestL1Stall`/`TestL0Stall`, `TestLevelGet`, `TestKeyVersions`, `TestSameLevel`, `TestTableContainsPrefix`, `TestFillTableCleanup`, `TestStaleDataCleanup`, and `TestBaseLevelZeroBySize`.

## Control Flow
Most tests disable background compactors and enable managed timestamps, create deterministic table layouts, set discard timestamps, call `runCompactDef` or `doCompact`, then verify the complete visible internal key stream. The tests cover L0-to-Lbase, level-to-next-level, same-level Lmax compaction, tombstone handling with and without lower-level overlap, split compactions, and explicit `compactStatus` add/delete behavior.

## State And Persistence Behavior
The tests mutate actual table files and manifest records under temporary DB directories, so they exercise on-disk SSTable creation and manifest bookkeeping. They verify that compaction rewrites table state without losing expected live versions, and that stale-data size on a level drops after Lmax cleanup. `TestKeyVersions` compares disk and in-memory range split counts.

## Dependencies And Integration Points
The suite uses `runBadgerTest`, `DefaultOptions`, `Open`, `table.NewTableBuilder`, `table.CreateTable`, `pb.ManifestChange`, `newCreateChange`, `levelHandler`, and internal key helpers from `y`. It validates `levels.go` together with table building, manifest persistence, iterator ordering, and managed transaction timestamp semantics.

## Risks And Edge Cases
Skipped stall tests mean L0/L1 blocking behavior is documented but not currently enforced. Some tests build tables manually and may bypass normal write-path invariants. The compaction expectations are sensitive to internal iterator ordering and version encoding, so legitimate storage layout changes require careful test updates. The base-level-zero regression test protects a large-database edge where dynamic level sizing previously left `baseLevel == 0`.

## Test Signals
Strong signals are exact internal key streams before and after compaction, absence of panic for huge Lmax sizes, zero stale data after cleanup, prefix membership truth tables, and blocked compaction status reuse after `cstatus.delete`. Failures indicate regression in snapshot safety, tombstone pruning, dynamic base-level calculation, range overlap, or same-level compaction cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/levels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/logger.go -->
# sources/storage-engines/badger/logger.go

## Purpose
This file defines Badger's pluggable logging abstraction and default stderr logger. It lets each `Options` value carry its own logger and logging threshold.

## Important APIs, Types, And Functions
`Logger` requires `Errorf`, `Warningf`, `Infof`, and `Debugf`. Methods on `*Options` forward those calls when `Options.Logger` is non-nil and silently drop messages otherwise. `loggingLevel` defines `DEBUG`, `INFO`, `WARNING`, and `ERROR`. `defaultLog` wraps `log.Logger`, and `defaultLogger` creates a logger named `badger ` writing to stderr.

## Control Flow
Callers use `opt.Errorf` and related methods throughout the DB. These methods check `opt.Logger` and delegate. The default logger methods compare the configured level against the message severity before printing with a severity prefix.

## State And Persistence Behavior
The file has no persistent state. The only mutable state is the logger implementation stored in `Options`, plus the standard logger output destination. Logging itself is side-effecting but not part of Badger durability.

## Dependencies And Integration Points
It depends only on Go's `log` and `os` packages. It is used across manifest replay, compaction, memtable recovery, subscription, and value-log code for diagnostics and error reporting.

## Risks And Edge Cases
Nil loggers intentionally suppress all logging, which can make operational diagnosis harder. The default level comparison relies on the enum order: lower numeric values are more verbose. The `Options` receiver is a pointer for log methods, so callers need an addressable options value.

## Test Signals
`logger_test.go` checks forwarding into a mock logger for error/info/warning paths. Debug forwarding and default logger level filtering are not directly tested in the listed tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/logger_test.go -->
# sources/storage-engines/badger/logger_test.go

## Purpose
This file tests the `Options` logging delegation surface using a mock logger.

## Important APIs, Types, And Functions
`mockLogger` implements `Logger` by writing the formatted severity-prefixed message into `output`. `TestDbLog` calls `Options.Errorf`, `Infof`, and `Warningf`. `TestNoDbLog` repeats the same calls after assigning a mock logger to an otherwise empty `Options`.

## Control Flow
Each test constructs an `Options` value with a mock logger, invokes logging helpers, and checks the final string in the mock after each call. The tests are simple synchronous delegation checks.

## State And Persistence Behavior
The only state is `mockLogger.output`. There is no filesystem or DB state.

## Dependencies And Integration Points
The test depends on `fmt.Sprintf`, `testing`, and `testify/require`. It validates the logging facade used by the rest of Badger.

## Risks And Edge Cases
The "no DB log" name is misleading because the test still assigns `opt.Logger = l`; it does not cover nil-logger suppression. Debug logging and default severity filtering are also not covered.

## Test Signals
The signal is exact prefix-preserving formatted output for error, info, and warning methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/managed_db.go -->
# sources/storage-engines/badger/managed_db.go

## Purpose
This file exposes Badger's managed timestamp mode for systems that need external control over read and commit timestamps.

## Important APIs, Types, And Functions
`OpenManaged` sets `Options.managedTxns` and calls `Open`. `DB.NewTransactionAt` creates a transaction with a caller-supplied read timestamp. `DB.NewWriteBatchAt` creates a managed write batch with fixed commit timestamp. `DB.NewManagedWriteBatch` creates a write batch that accepts per-entry timestamps. `Txn.CommitAt` commits at a supplied timestamp, optionally using an async callback. `DB.SetDiscardTs` tells the oracle the timestamp at or below which invalid/deleted versions may be discarded.

## Control Flow
All managed APIs panic if `db.opt.managedTxns` is false. `NewTransactionAt` starts a normal internal transaction and overwrites `readTs`. `NewWriteBatchAt` sets both `WriteBatch.commitTs` and the underlying transaction commit timestamp. `CommitAt` sets `txn.commitTs`, then either calls synchronous `Commit` or asynchronous `CommitWith`.

## State And Persistence Behavior
Managed mode changes transaction timestamp assignment and compaction discard eligibility. Writes still flow through the normal write path, WAL/value log, memtable, LSM, and manifest machinery. `SetDiscardTs` affects future compaction decisions and value-log reclaimability, not immediate deletion by itself.

## Dependencies And Integration Points
The file integrates with `Open`, `DB.newTransaction`, `DB.newWriteBatch`, `Txn.Commit`, `Txn.CommitWith`, write batch internals, and the transaction oracle. It is used by Dgraph-style callers and heavily by tests that need deterministic versions.

## Risks And Edge Cases
Panic-on-wrong-mode makes API misuse fail loudly. External callers must guarantee timestamp monotonicity and conflict semantics; Badger will use the supplied timestamps. Async `CommitAt` returns nil after scheduling `CommitWith`, so commit failures arrive only through the callback. Incorrect discard timestamps can make compaction drop versions still needed by external readers.

## Test Signals
`managed_db_test.go` covers managed drop-all/drop-prefix, write batches with fixed and per-entry timestamps, duplicate version handling, and value-log discard stat resets. `levels_test.go` uses managed mode to validate compaction version retention.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/managed_db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/managed_db_test.go -->
# sources/storage-engines/badger/managed_db_test.go

## Purpose
This file tests managed timestamp behavior, destructive DB operations, prefix dropping, read-only protections, races with concurrent writers/readers, write batch timestamp semantics, duplicate key/version behavior, and discard-stat cleanup.

## Important APIs, Types, And Functions
Helpers `val`, `numKeys`, and `numKeysManaged` create values and count visible keys through ordinary or managed transactions. Tests include `TestDropAllManaged`, `TestDropAll`, `TestDropAllTwice`, `TestDropAllWithPendingTxn`, `TestDropReadOnly`, `TestWriteAfterClose`, `TestDropAllRace`, `TestDropPrefix`, `TestDropPrefixWithPendingTxn`, `TestDropPrefixReadOnly`, `TestDropPrefixRace`, `TestWriteBatchManagedMode`, `TestWriteBatchManaged`, `TestWriteBatchDuplicate`, and `TestZeroDiscardStats`.

## Control Flow
The tests populate temporary DBs with many keys, call `DropAll` or `DropPrefix`, verify counts immediately and after reopen, and then write again to ensure the DB remains usable. Race tests run writer goroutines while drop operations execute. Pending-transaction tests continuously iterate/read from an old transaction while a drop operation runs. Write-batch tests flush large batches under managed timestamps and verify iterator versions.

## State And Persistence Behavior
The suite exercises persistent value-log and LSM recovery across close/reopen, including preservation of the badger head after `DropAll` in managed mode. It verifies that drop operations clear visible keys and zero relevant value-log discard stats. Read-only tests assert destructive operations panic when opened read-only, except for Windows lock limitations.

## Dependencies And Integration Points
It depends on `Open`, `OpenManaged`, `DefaultOptions`, `getTestOptions`, `WriteBatch`, managed transactions, iterators, value-log discard stats, and `z.Closer`. It integrates `managed_db.go` with drop APIs implemented elsewhere and with value-log rewrite/drop state.

## Risks And Edge Cases
The pending transaction tests intentionally run loops until a drop causes read errors, so they validate non-deadlock more than exact snapshot results. Race tests accept write errors during destructive operations and only assert key count decreases. Windows read-only behavior has a special expected error. These are broad integration tests and can be timing-sensitive.

## Test Signals
Important signals are post-drop key counts, ability to write after drops, correct reopen state, `ErrDBClosed` after close, panic on read-only drops, managed write-batch versions, duplicate collapse or retention depending on batch type, and zeroed discard stats after rewrite/drop-all.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/managed_db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/manifest.go -->
# sources/storage-engines/badger/manifest.go

## Purpose
This file implements Badger's `MANIFEST` file format and mutation logic. The manifest is the durable catalog of SSTable IDs, levels, encryption key IDs, compression type, and atomic table create/delete changes used to reconstruct the LSM tree on startup.

## Important APIs, Types, And Functions
`Manifest` holds level sets, table metadata, and creation/deletion counters. `TableManifest` stores level, `KeyID`, and compression. `manifestFile` owns the manifest file handle, append lock, current manifest snapshot, rewrite threshold, external magic, and in-memory flag. Public/internal APIs include `openOrCreateManifestFile`, `helpOpenOrCreateManifestFile`, `manifestFile.addChanges`, `ReplayManifestFile`, `applyManifestChange`, `applyChangeSet`, `newCreateChange`, and `newDeleteChange`.

## Control Flow
Opening creates a new manifest via `helpRewrite` if none exists and the DB is writable, or replays an existing file with `ReplayManifestFile`. Replay checks eight magic/version bytes, validates the external magic, then reads length+CRC-framed protobuf `ManifestChangeSet`s until EOF or a partial final record. Writable opens truncate to the last complete offset and seek to the end. `addChanges` marshals a changeset, locks appends, applies it to the in-memory manifest, either rewrites if deletion churn is high or appends length+CRC+payload, then syncs.

## State And Persistence Behavior
The manifest file begins with `B d g r`, two bytes of external magic, and the two-byte Badger magic version. Every following record is four bytes length, four bytes CRC32C, and a marshaled `pb.ManifestChangeSet`. Rewrite writes `MANIFEST-REWRITE`, fsyncs it, closes it for Windows rename compatibility, renames over `MANIFEST`, reopens, seeks to end, and syncs the directory. In-memory mode returns a no-op manifest file.

## Dependencies And Integration Points
The file depends on protobuf messages from `pb`, compression enums from `options`, file helpers from `y`, `syncDir`, and table metadata emitted by compaction and memtable flushes. `levels.go` consumes `Manifest.Tables` on startup and writes create/delete changes during compaction, L0 table addition, drop-tree, and drop-prefix operations.

## Risks And Edge Cases
This is a critical crash-recovery surface. Bad magic, unsupported Badger version, external magic mismatch, malformed length larger than file size, checksum mismatch, invalid operations, and duplicate creates fail open. Partial final records are tolerated by returning a truncation offset. Delete of an already-removed table is warned and removes the ID from all levels, which is tolerant but can mask duplicate delete sources. Applying changes before writing means an append/write/sync error leaves `mf.manifest` ahead of disk until close/reopen.

## Test Signals
`manifest_test.go` covers basic reopen visibility, magic/version/checksum corruption, rewrite after many deletes, and concurrent manifest compaction appends under injected slow sync. Level tests and compaction flows indirectly validate create/delete change application.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/manifest_test.go -->
# sources/storage-engines/badger/manifest_test.go

## Purpose
This file tests manifest recovery, corruption detection, rewrite compaction, and concurrent append safety.

## Important APIs, Types, And Functions
`TestManifestBasic` writes data, validates, closes, reopens, and verifies a stored key/user meta. `helpTestManifestFileCorruption` mutates bytes in `MANIFEST` to drive `TestManifestMagic`, `TestManifestVersion`, and `TestManifestChecksum`. `buildTable` constructs temporary tables. `TestManifestRewrite` forces a low deletion threshold and validates the compacted manifest contents. `TestConcurrentManifestCompaction` overrides `syncFunc` to slow syncs and runs concurrent `addChanges` calls.

## Control Flow
The tests create temp DB directories, open/close Badger, mutate manifest files directly for corruption cases, and call `helpOpenOrCreateManifestFile` where needed. Rewrite testing creates a chain of create/delete changes that should collapse to the last live table after reopen. Concurrent testing simulates two compaction threads appending identical change sets behind the manifest append lock.

## State And Persistence Behavior
The tests use actual filesystem manifests and table files. Corruption tests verify startup rejects bad header and checksum state. Rewrite testing checks durable file rewrite and replay state after the manifest was compacted. Concurrent testing validates lock-protected append/rewrite with a real file sync path.

## Dependencies And Integration Points
It depends on `Open`, transaction helpers, table builders, protobuf manifest changes, Badger options, file mutation via `os.OpenFile`, and `syncFunc` injection from `manifest.go`. It validates manifest integration with DB open/reopen and compaction-style changes.

## Risks And Edge Cases
`TestOverlappingKeyRangeError` is skipped and notes that its old premise no longer makes sense. `TestConcurrentManifestCompaction` mutates global `syncFunc` and does not restore it in this file, so test isolation depends on package ordering or later overrides. The corruption helper writes one byte at fixed offsets tied to the current manifest layout.

## Test Signals
Signals include exact error substrings for bad magic/version/checksum, replayed live table map after rewrite, no error from concurrent `addChanges`, and key/value/user-meta survival across reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/memtable.go -->
# sources/storage-engines/badger/memtable.go

## Purpose
This file implements Badger memtables and their write-ahead log files. A memtable combines an in-memory skiplist with an mmap-backed WAL that can be replayed after a crash and deleted when the memtable is flushed.

## Important APIs, Types, And Functions
`memTable` stores a `skl.Skiplist`, `logFile`, max version, options, and reusable encode buffer. DB-level functions include `openMemTables`, `openMemTable`, `newMemTable`, and `mtFilePath`. Memtable methods include `SyncWAL`, `isFull`, `Put`, `UpdateSkipList`, `IncrRef`, `DecrRef`, and `replayFunction`.

`logFile` wraps a `z.MmapFile` with locking, fid/path, size/write offsets, encryption key material, registry, and options. Core methods are `Truncate`, `encodeEntry`, `writeEntry`, `decodeEntry`, `decryptKV`, `keyID`, `encryptionEnabled`, `read`, `generateIV`, `doneWriting`, `iterate`, `zeroNextEntry`, `open`, and `bootstrap`.

## Control Flow
Startup scans `*.mem` files, sorts by fid, opens each WAL read-write or read-only, replays valid entries into a skiplist, truncates to the valid end in writable mode, and appends non-empty replayed memtables to `db.imm`. New memtables create/open the next numbered WAL with size `2*MemTableSize`. `Put` encodes the entry into WAL first, skips inserting finish markers into the skiplist, then inserts normal entries and updates `maxVersion`.

WAL iteration starts after the fixed header, decodes entries through `safeRead`, tracks multi-entry transactions until a matching `bitFinTxn`, calls a callback only for complete transactions, and stops at EOF, zero entry, truncation marker, or incomplete transaction. `doneWriting` optionally syncs, locks the mmap/file, truncates to the written offset, and leaves the file open read-write.

## State And Persistence Behavior
WAL files have a header containing an 8-byte data-key ID and 12-byte base IV. Entry records contain encoded header, key, value, and CRC32C; key/value bytes are encrypted with AES CTR-derived XOR when a data key is present. `zeroNextEntry` writes zeros after each WAL write so crash recovery can detect the end. `UpdateSkipList` truncates only in writable mode and returns `ErrTruncateNeeded` in read-only mode if dirty trailing bytes exist. Skiplist reference release deletes the WAL file after flush.

## Dependencies And Integration Points
The file depends on `skl`, `Entry`, value-pointer encoding, `safeRead`, value-log constants such as `vlogHeaderSize`, encryption key registry, `pb.DataKey`, mmap helpers from `z`, metrics in `y`, and DB fields `imm`/`nextMemFid`. It is the bridge between the write path, recovery, L0 flush pipeline, encryption, and value-log pointer reads.

## Risks And Edge Cases
Mmap truncation/remap needs locking to avoid readers touching invalid memory. WAL replay must distinguish complete transactions from partially written batches. A read-only DB with dirty WAL tail fails because it cannot truncate. The arena/skiplist size and WAL size thresholds can diverge; `isFull` considers both. The `read` method checks actual `lf.size` to avoid returning bytes past a concurrent drop/truncate.

## Test Signals
The listed subset does not include dedicated memtable tests, but managed/drop/reopen tests exercise WAL replay and truncation indirectly. Metrics tests observe writes into L0. Failure signals include lost data after reopen, read-only truncate errors, corrupted transaction replay, or WAL deletion/refcount leaks after flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/memtable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/merge.go -->
# sources/storage-engines/badger/merge.go

## Purpose
This file implements Badger's per-key merge operator. It lets callers append merge operands as separate versions and periodically compact them into a single value using a caller-supplied merge function.

## Important APIs, Types, And Functions
`MergeOperator` stores the merge function, DB, key, close signal, and a read/write lock. `MergeFunc` merges an older value and newer accumulated value. `DB.GetMergeOperator` starts a background compaction goroutine. `iterateAndMerge` scans all versions for the key and applies the merge function. `compact` writes the merged value back with `bitDiscardEarlierVersions`. `runCompactions`, `Add`, `Get`, and `Stop` provide lifecycle and user operations.

## Control Flow
`Add` writes a normal transaction entry with the merge bit set. `Get` locks against background compaction and calls `iterateAndMerge` to synthesize a value on demand. `runCompactions` ticks at the configured duration and runs `compact`; on stop it runs one final compaction before exiting. `compact` ignores not-found or single-version states and asynchronously writes the merged value at the latest version key.

## State And Persistence Behavior
Each add creates a Badger version for the same logical key. Periodic compaction writes one merged value marked `bitDiscardEarlierVersions`, and normal LSM compaction can later drop older merge entries. Durability is the normal Badger write path; merge state is not stored separately from the key versions.

## Dependencies And Integration Points
The file uses transactions, key iterators with `AllVersions`, item metadata helpers, `NewEntry(...).withMergeBit`, `batchSetAsync`, key timestamp encoding in `y`, and `z.Closer`. It relies on LSM compaction in `levels.go` to eventually remove obsolete merged entries.

## Risks And Edge Cases
The merge function must be associative enough for version-order folding. `iterateAndMerge` stops at deleted/expired items and at `DiscardEarlierVersions`, so delete and compaction markers affect results. `compact` writes asynchronously, so errors are logged rather than returned to callers. `Stop` can block until the final compaction completes. The lock prevents concurrent `Get`/`compact` interleaving but not concurrent `Add` writes.

## Test Signals
`merge_test.go` covers not found before add, numeric and slice merges, immediate get before timer compaction, delete/reset behavior, get after stop, and old-version removal after close-triggered compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/merge_test.go -->
# sources/storage-engines/badger/merge_test.go

## Purpose
This file tests the merge operator API and its interaction with deletes, stopping, and LSM compaction cleanup.

## Important APIs, Types, And Functions
`TestGetMergeOperator` contains subtests for get-before-add, add/get, byte-slice append, get before background compaction, delete reset, get after stop, and old-key cleanup. Helpers `uint64ToBytes`, `bytesToUint64`, and `add` encode/decode big-endian counters and implement sum merging.

## Control Flow
Tests create a merge operator, call `Add` several times, call `Get`, and compare merged output. Some subtests stop the operator to force final compaction. The cleanup test writes thousands of merge entries, closes with `CompactL0OnClose`, reopens, then iterates all versions for the merge key and expects one remaining version.

## State And Persistence Behavior
The tests cover merge values stored as Badger versions, delete tombstone behavior, final compaction on `Stop`, and persistent LSM compaction cleanup across close/reopen.

## Dependencies And Integration Points
It uses `runBadgerTest`, `Open`, `getTestOptions`, `CompactL0OnClose`, transactions, iterators with `AllVersions`, and the merge API from `merge.go`.

## Risks And Edge Cases
Timer-based background compaction can make tests sensitive to timing, though most assertions use synchronous `Get` or `Stop`. The old-key cleanup test depends on close-time L0 compaction behavior and exact one-version cleanup.

## Test Signals
Signals include `ErrKeyNotFound` before writes, correct merged values, reset after delete, valid get after `Stop`, and only one persisted version after forced compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/merge_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/metrics_test.go -->
# sources/storage-engines/badger/metrics_test.go

## Purpose
This file tests Badger's expvar metrics for user writes, value-log writes/reads, L0/LSM writes, compaction output, gets, bloom-filter hits, LSM read bytes, and iterator creation.

## Important APIs, Types, And Functions
`clearAllMetrics` iterates over `expvar` variables and resets supported metric types. `TestWriteMetrics` checks user write, put, L0 write, and compaction write metrics. `TestVlogMetrics` checks value-log write/read counters and bytes. `TestReadMetrics` checks get counters, memtable/LSM metrics, bloom-filter map keys, LSM read bytes, and iterator metrics.

## Control Flow
Tests use managed options with close-time compaction, clear global metrics, write random keys/values, inspect expvar counters, sometimes close/reopen to force LSM compaction, then perform reads and missing-key lookups to trigger read metrics.

## State And Persistence Behavior
The metrics are global expvar state, not DB-local state. Some tests perform close/reopen to transition data from memtable/L0 into lower levels and make compaction/LSM metrics observable. Large values are used to force value-log storage.

## Dependencies And Integration Points
The tests depend on metrics functions in `y`, Badger write/read paths, managed write batches, value-log threshold behavior, bloom-filter lookups, close-time compaction, and expvar's process-global registry.

## Risks And Edge Cases
Because expvar is global, test isolation depends on `clearAllMetrics` and no concurrent metric-producing tests. Several byte assertions use `GreaterOrEqual` due to compression/overhead variability. Random data is used to reduce compression effects, but exact sizes remain implementation-sensitive.

## Test Signals
Signals include exact counts for writes, puts, value-log writes/reads, gets, memtable hits, iterator creation, and expected map entries for LSM/bloom metrics after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options.go -->
# sources/storage-engines/badger/options.go

## Purpose
This file defines Badger's main `Options` struct, defaults, table-option derivation, LSM-only mode, superflag parsing/serialization, and fluent option setters.

## Important APIs, Types, And Functions
`Options` includes directory, sync, versioning, read-only, logging, compression, in-memory, metrics, goroutine count, LSM sizing, value-log sizing, compaction, encryption, checksum, cache, conflict detection, namespace, external magic, and internal managed/test-only fields. `DefaultOptions` provides production defaults. `buildTableOptions` converts DB options into `table.Options`. `LSMOnlyOptions` raises value threshold. `parseCompression`, `generateSuperFlag`, and `Options.FromSuperFlag` handle string configuration. Numerous `WithX` methods return modified option values.

## Control Flow
Callers start with `DefaultOptions` or `LSMOnlyOptions`, then chain `WithX` methods. DB opening consumes the options and `buildTableOptions` supplies table builders/openers with current compression, checksum, cache, block, encryption, and allocation settings. `FromSuperFlag` generates a default map from current options, merges input flags, reflectively sets exported scalar fields, and specially parses compression strings such as `zstd:3`.

## State And Persistence Behavior
Options determine persistent layout and recovery behavior: `Dir`/`ValueDir`, value threshold, value-log file size, compression for new tables, encryption keys, checksum verification, external magic, LSM level sizing, and read-only/in-memory mode. Some options affect only new tables (`Compression`) while existing tables carry their own manifest/table metadata. `getFileFlags` maps read-only mode to file open flags.

## Dependencies And Integration Points
The file imports Badger `options` enums, `table.Options`, logger types, key registry usage through `buildTableOptions`, `z.SuperFlag`, and filesystem flags. Nearly every DB subsystem consumes this struct.

## Risks And Edge Cases
Reflection-based superflag handling excludes unexported or non-scalar fields and does not support logger/encryption key. `parseCompression` calls `y.Check` on bad numeric levels, which can panic rather than return an error. Some options are dangerous if misused: `BypassLockGuard`, wrong `ExternalMagicVersion`, managed transactions, or incorrect conflict detection settings. Changing size/threshold options affects compaction and storage behavior significantly.

## Test Signals
`options_test.go` verifies default options round-trip through superflag generation/parsing and special compression parsing for `zstd:2`. Broader tests exercise option effects indirectly through compaction, metrics, in-memory mode, read-only mode, managed mode, and close-time compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options/options.go -->
# sources/storage-engines/badger/options/options.go

## Purpose
This file defines small public enum types used to configure SSTable checksum verification and block compression.

## Important APIs, Types, And Functions
`ChecksumVerificationMode` supports `NoVerification`, `OnTableRead`, `OnBlockRead`, and `OnTableAndBlockRead`. `CompressionType` supports `None`, `Snappy`, and `ZSTD`.

## Control Flow
There is no runtime control flow in this file; consumers compare enum values and pass them into DB/table options.

## State And Persistence Behavior
Compression type is persisted indirectly for SSTables through manifest/table metadata and determines how table blocks are encoded. Checksum verification mode affects read/open validation behavior but is not itself persisted.

## Dependencies And Integration Points
The package is imported by `badger/options.go`, `manifest.go`, table builders/openers, tests, and any external callers configuring Badger.

## Risks And Edge Cases
Enum numeric values are part of the public API and compression values are persisted in manifest changes, so changing them would break compatibility. Adding values requires updates to parsing, docs, tests, and table handling.

## Test Signals
`options_test.go` exercises compression enum parsing through superflags. Manifest and table-opening paths indirectly rely on these values.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options_test.go -->
# sources/storage-engines/badger/options_test.go

## Purpose
This file tests option superflag serialization and parsing.

## Important APIs, Types, And Functions
`TestOptions` has default round-trip and special-flag subtests. `optionsEqual` reflectively compares exported scalar option fields for bool, int/int64, uint32/uint64, float64, and string kinds.

## Control Flow
The default test serializes `DefaultOptions("")` with `generateSuperFlag`, parses into an empty `Options`, and checks equality with defaults. It also verifies a simple override of `numgoroutines`. The special-flags test configures namespace offset, ZSTD compression, compression level, and goroutine count, then parses the equivalent superflag and compares.

## State And Persistence Behavior
There is no DB persistence. The tests validate configuration state translation before DB open.

## Dependencies And Integration Points
The test depends on `reflect`, `testing`, and the `options` enum package. It covers `options.go` helper functions rather than runtime DB behavior.

## Risks And Edge Cases
`optionsEqual` ignores non-scalar/exported unsupported fields such as logger and byte slices, matching superflag limitations. Invalid compression strings, numeric compression fallback, and panic paths are not covered.

## Test Signals
Signals are equality after default superflag round-trip and correct parsing of `compression=zstd:2`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.pb.go -->
# sources/storage-engines/badger/pb/badgerpb4.pb.go

## Purpose
This generated file provides Go protobuf bindings for `badgerpb4.proto`. It defines the wire-compatible message and enum types used by Badger manifest records, stream/subscription payloads, checksums, encryption keys, and trie match rules.

## Important APIs, Types, And Functions
Enums are `EncryptionAlgo`, `ManifestChange_Operation`, and `Checksum_Algorithm`. Messages are `KV`, `KVList`, `ManifestChangeSet`, `ManifestChange`, `Checksum`, `DataKey`, and `Match`, each with `Reset`, `String`, `ProtoReflect`, descriptor methods, and getters. `File_badgerpb4_proto`, raw descriptors, enum/message info, dependency indexes, and `file_badgerpb4_proto_init` register the protobuf schema.

## Control Flow
The generated init path builds a protobuf file descriptor once, installs exporter functions when unsafe operations are disabled, and clears raw descriptor/go type slices after build. Runtime use is through protobuf marshal/unmarshal, reflection, and getters.

## State And Persistence Behavior
The wire schema is persistence-critical. `ManifestChangeSet` and `ManifestChange` are written into `MANIFEST`; `DataKey` is used by encryption key registry/log headers; `KV` and `KVList` carry streamed or subscription updates. Field numbers and enum numeric values must remain stable for existing databases and clients.

## Dependencies And Integration Points
The file depends on `google.golang.org/protobuf` reflection/runtime packages. It is imported by Badger manifest, publisher/subscriber, stream, encryption/key-registry, checksum, and tests. It is regenerated by `pb/gen.sh` from `badgerpb4.proto`.

## Risks And Edge Cases
Manual edits will be overwritten and can desynchronize from the `.proto`. Any field renumbering or enum numeric change is a compatibility break. Generated getters return zero/nil defaults, so callers must distinguish missing fields where that matters.

## Test Signals
`pb/protos_test.go` regenerates the file and requires `git diff --quiet` to ensure generated output is current. Manifest tests exercise protobuf manifest marshal/unmarshal indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.proto -->
# sources/storage-engines/badger/pb/badgerpb4.proto

## Purpose
This file is the source protobuf schema for Badger v4 internal and external wire messages.

## Important APIs, Types, And Functions
Messages: `KV`, `KVList`, `ManifestChangeSet`, `ManifestChange`, `Checksum`, `DataKey`, and `Match`. Enums: `EncryptionAlgo`, nested `ManifestChange.Operation`, and nested `Checksum.Algorithm`. The `go_package` is `github.com/dgraph-io/badger/v4/pb`.

## Control Flow
There is no runtime control flow. `protoc` plus `protoc-gen-go` consumes this schema to generate `badgerpb4.pb.go`.

## State And Persistence Behavior
`ManifestChangeSet` atomically groups table creates/deletes for the manifest. `ManifestChange` stores table ID, operation, level, encryption key ID, encryption algorithm, and compression. `KV`/`KVList` represent key/value data, stream IDs, stream completion, and allocation refs. `DataKey` stores encryption key metadata. `Match` stores subscription prefix filters and ignored byte ranges.

## Dependencies And Integration Points
The schema drives generated Go code used by manifest persistence, subscriptions/publisher, streams, key registry, and checksum code. `pb/gen.sh` regenerates bindings.

## Risks And Edge Cases
Field numbers are durable API. Renaming is less dangerous than renumbering, but removing/reusing fields or changing enum numbers would break existing manifests, streams, or key registry data. `EncryptionAlgo` currently contains only AES, so adding algorithms requires implementation support beyond the schema.

## Test Signals
`pb/protos_test.go` verifies generated Go stays in sync with this schema.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/gen.sh -->
# sources/storage-engines/badger/pb/gen.sh

## Purpose
This script regenerates Go protobuf bindings for `badgerpb4.proto`.

## Important APIs, Types, And Functions
It installs `google.golang.org/protobuf/cmd/protoc-gen-go@v1.31.0` and runs `protoc --go_out=. --go_opt=paths=source_relative badgerpb4.proto`.

## Control Flow
The script assumes it is run from its own directory so the proto file is in the current working directory. It first ensures the requested generator version is installed, then invokes `protoc` to write `badgerpb4.pb.go` beside the proto.

## State And Persistence Behavior
The script mutates the developer's Go tool installation/cache by installing `protoc-gen-go`, and rewrites generated source in the repository. It does not touch database files.

## Dependencies And Integration Points
It requires Bash, Go tooling, `protoc`, network/module availability if the generator is not cached, and the proto source file. It is called by `pb/protos_test.go`.

## Risks And Edge Cases
Running from another directory will fail because the proto path is relative. Different `protoc` binary versions can change generated output details, though the generator version is pinned. Environments without `protoc` or network access fail regeneration.

## Test Signals
`TestProtosRegenerate` runs this script and then checks that `badgerpb4.pb.go` has no git diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/gen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/protos_test.go -->
# sources/storage-engines/badger/pb/protos_test.go

## Purpose
This file enforces that generated protobuf Go code is current with the checked-in `.proto` schema and generation script.

## Important APIs, Types, And Functions
`Exec` starts and waits for a command. `TestProtosRegenerate` runs `./gen.sh`, then `git diff --quiet -- badgerpb4.pb.go`.

## Control Flow
The test invokes the generator script from the test working directory, then asks Git whether the generated file changed. Any generator failure or resulting diff fails the test.

## State And Persistence Behavior
The test can rewrite `badgerpb4.pb.go` during execution and can install/update the protobuf generator through `gen.sh`. It relies on the repository being a Git checkout.

## Dependencies And Integration Points
It depends on `os/exec`, `testing`, `testify/require`, Bash, Go, `protoc`, and Git. It validates `badgerpb4.proto`, `gen.sh`, and `badgerpb4.pb.go` as a set.

## Risks And Edge Cases
This test is environment-sensitive: missing `protoc`, missing Git, no network/module cache, or running outside the expected directory can fail it. It has side effects on generated files and local tool installation.

## Test Signals
The signal is no error from regeneration and no diff in `badgerpb4.pb.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/protos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/publisher.go -->
# sources/storage-engines/badger/publisher.go

## Purpose
This file implements Badger's update publisher for subscriptions. It tracks subscribers and prefix match rules, batches committed write requests, and delivers matching key/value updates as protobuf `KVList`s.

## Important APIs, Types, And Functions
`subscriber` stores ID, match rules, send channel, closer, and atomic active flag. `publisher` stores a mutex, buffered publication channel, subscriber map, next ID, and trie indexer. APIs include `newPublisher`, `listenForUpdates`, `publishUpdates`, `newSubscriber`, `cleanSubscribers`, `deleteSubscriber`, `sendUpdates`, and `noOfSubscribers`.

## Control Flow
Writers call `sendUpdates`, which increments request refs and queues requests only when subscribers exist. `listenForUpdates` drains one or more queued request batches with `slurp`, then calls `publishUpdates`. Publishing locks the subscriber/index state, builds per-subscriber `KVList`s by matching each entry key against the trie, copies key/value bytes, strips timestamps from keys, includes version and expires-at, and sends to active subscribers. Cleanup removes trie matches, deletes subscribers, and signals subscriber closers.

## State And Persistence Behavior
Publisher state is in-memory only. It does not affect DB durability, but it must respect request reference counting: `publishUpdates` decrements refs after delivering. Delivered `KV` values are safe copies of committed entries and include version metadata parsed from internal keys.

## Dependencies And Integration Points
It depends on `pb.KVList`, `pb.Match`, the trie matcher, `requests` refcounting, `Entry`, key parsing helpers in `y`, and `z.Closer`. It backs the DB subscription API and is fed by the write path after commits.

## Risks And Edge Cases
Publishing holds the mutex while sending to buffered subscriber channels; full subscriber channels can block all publishing while the lock is held. `newSubscriber` inserts the subscriber before adding all matches, so an `AddMatch` error can leave partial state unless callers handle cleanup. The active flag is checked before send but deletion/close races require careful ordering. Batching preserves queue order but coalesces multiple request slices into one publish pass.

## Test Signals
`publisher_test.go` covers a previous deadlock scenario, delivery ordering for sequential writes, and multiple prefix subscriptions. Tests focus on liveness and ordering rather than channel backpressure or partial match-add errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/publisher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/publisher_test.go -->
# sources/storage-engines/badger/publisher_test.go

## Purpose
This file tests subscription publisher liveness, ordering, and multiple-prefix matching.

## Important APIs, Types, And Functions
`TestPublisherDeadlock` verifies a subscriber callback that blocks and returns an error does not deadlock commits. `TestPublisherOrdering` verifies five sequential updates arrive in order. `TestMultiplePrefix` verifies one subscriber with two prefix matches receives both matching updates.

## Control Flow
Each test starts a subscription goroutine, waits until it is active, performs DB updates, and uses wait groups or atomics to coordinate callback progress. The deadlock test floods 1,109 concurrent updates while the subscriber callback is blocked after the first update, then releases it and expects the subscription to exit with the callback error.

## State And Persistence Behavior
The tests use transient DB writes and subscription callbacks; they do not assert persistence after reopen. State of interest is in-memory publisher queues, subscriber channels, and callback-observed order.

## Dependencies And Integration Points
It depends on `DB.Subscribe`, `DB.Update`, `NewEntry`, `pb.Match`, contexts, goroutine scheduling, and publisher internals indirectly.

## Risks And Edge Cases
Concurrency-heavy tests can be timing-sensitive. Ordering is asserted for sequential single-key writes but not for concurrent writes. The deadlock test validates graceful exit but not exact delivery count after the first blocked callback.

## Test Signals
Signals include no deadlock under callback blockage, callback error propagation, ordered values `value0` through `value4`, and correct delivery for `ke` and `hel` prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/publisher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/skl/arena.go -->
# sources/storage-engines/badger/skl/arena.go

## Purpose
This file implements the lock-free byte arena used by Badger's skiplist. It allocates nodes, keys, and encoded values from a contiguous byte slice and uses integer offsets instead of Go pointers for compact storage.

## Important APIs, Types, And Functions
`Arena` holds an atomic allocation cursor and backing buffer. Constants `offsetSize` and `nodeAlign` support node tower sizing and 64-bit alignment. `newArena`, `size`, `putNode`, `putVal`, `putKey`, `getNode`, `getKey`, `getVal`, and `getNodeOffset` allocate and decode skiplist arena data.

## Control Flow
Allocation methods atomically add the required byte count to the cursor, assert the new total fits the buffer, and return the starting offset. `putNode` overallocates by alignment padding, subtracts unused tower slots for shorter nodes, and returns an aligned offset. `putVal` encodes a `y.ValueStruct` into the buffer. `putKey` copies key bytes. Getters slice the buffer or convert an aligned offset back to a `*node` via `unsafe.Pointer`.

## State And Persistence Behavior
Arena state is process memory only and is not persisted directly. WAL replay and normal writes repopulate skiplists into arenas. Offset zero is reserved as nil, so allocations start at one.

## Dependencies And Integration Points
It depends on `sync/atomic`, `unsafe`, and `y.ValueStruct` encoding. It is used by `skl.Skiplist`, which is used by `memTable` for write buffering and recovery.

## Risks And Edge Cases
The arena relies on unsafe pointer conversion and correct 64-bit alignment for atomic loads from node values. It panics via assertions on arena exhaustion rather than returning allocation errors. Returned key/value slices alias the arena buffer and must not outlive the skiplist. Node offset calculation assumes the node pointer belongs to the arena buffer.

## Test Signals
No direct arena test is included in this subset. Indirect signals come from memtable/skiplist behavior across writes, reads, WAL replay, and concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/skl/arena.go -->
