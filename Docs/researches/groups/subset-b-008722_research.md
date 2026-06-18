# subset-b-008722 research

Grouped research report for the write-prepared transaction implementation and its main regression test coverage. Each section preserves the original source path and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_transaction_test.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_transaction_test.cc

## Purpose

This file is the primary unit and regression test suite for RocksDB's write-prepared transaction mode. It validates the visibility contract where prepared data is already written to the memtable and WAL, but readers must treat it as invisible until a commit marker publishes the prepare sequence through the write-prepared commit map. The tests cover one-write-queue and two-write-queue configurations, ordered and unordered write ordering, optional point-lock-manager modes, crash recovery, compaction behavior, snapshot maintenance, iterator visibility, rollback, direct non-transactional writes through `TransactionDB::Write`, and compatibility with write-committed policy.

The suite also directly tests internal helper structures exposed through friends in `WritePreparedTxnDB`: `PreparedHeap`, `CommitEntry64b`, `AddCommitted`, `RemovePrepared`, `AdvanceMaxEvictedSeq`, `MaybeUpdateOldCommitMap`, `CheckAgainstSnapshots`, `SmallestUnCommittedSeq`, and the snapshot and old-commit data structures. It is therefore both black-box transaction coverage and white-box validation for the data structures that make write-prepared visibility safe under concurrent writes and compaction.

## Important APIs, types, and fixtures

Key type aliases map to `WritePreparedTxnDB::CommitEntry`, `CommitEntry64b`, and `CommitEntry64bFormat`, allowing direct tests of the fixed-size atomic commit cache encoding.

`WritePreparedTxnDBMock` subclasses `WritePreparedTxnDB` and overrides `GetSnapshotListFromDB()` so tests can supply synthetic snapshot lists without using a full DB snapshot list. It also exposes helpers such as `SetDBSnapshots()` and `TakeSnapshot()` to drive `AdvanceMaxEvictedSeq()` and old-commit-map cases.

`WritePreparedTransactionTestBase` extends the shared `TransactionTestBase`. It provides option helpers for `wp_snapshot_cache_bits` and `wp_commit_cache_bits`, `MaybeUpdateOldCommitMapTestWithNext()` for validating snapshot-search pruning, `SnapshotConcurrentAccessTestInternal()` for interleaving `CheckAgainstSnapshots()` and `UpdateSnapshots()`, `VerifyKeys()` for DB and `MultiGet` visibility checks, and `VerifyInternalKeys()` for inspecting exact internal key versions after compaction.

`WritePreparedTransactionTest`, `SnapshotConcurrentAccessTest`, and `SeqAdvanceConcurrentTest` are parameterized fixtures. The main parameter matrix exercises stackable DB disabled, one or two write queues, write-prepared policy, ordered or unordered write ordering, optional per-key point lock managers, and lock timeout variants. Long concurrency tests are split across parameter shards using `split_id_` and `split_cnt_` to keep each instantiation bounded.

## Control flow and coverage map

The early tests validate building blocks. `PreparedHeap.BasicsTest`, `EmptyAtTheEnd`, and `Concurrent` assert that the heap supports monotonic push, O(1)-style deferred erase through an erased heap, resilience to erase-without-push, and concurrent push/erase patterns. `WriteBatchWithIndex.SubBatchCnt` validates duplicate-key sub-batch counting and savepoint rollback behavior, then cross-checks it with `SubBatchCounter`. `CommitEntry64b.BasicTest` exhaustively samples index and delta encodings to ensure compact entries parse back to the original prepare and commit sequences.

Commit map and snapshot tests then cover the core visibility rules. `CommitMap` tests cache add, lookup, CAS exchange, eviction, and index collisions. `MaybeUpdateOldCommitMap`, `OldCommitMapGC`, and `CheckAgainstSnapshots` validate when evicted commit entries must be retained for snapshots satisfying `prepare_seq <= snapshot_seq < commit_seq`. `SnapshotConcurrentAccess` drives all selected interleavings between snapshot-cache readers and writers to ensure live snapshots are not missed while `UpdateSnapshots()` is replacing the cache.

Sequence advancement tests stress the `max_evicted_seq_` frontier. `AdvanceMaxEvictedSeqBasic` verifies that prepared entries at or below the new max move into `delayed_prepared_`, newer prepares remain in `prepared_txns_`, and live snapshots below max are cached. `NewSnapshotLargerThanMax`, `MaxCatchupWithNewSnapshot`, and `MaxCatchupWithUnbackedSnapshot` validate that new snapshots are not allowed to sit at or below `future_max_evicted_seq_`, and that unbacked reads return `TryAgain` instead of using an invalid visibility window. `AdvanceSeqByOne` ensures the dummy transaction trick can bump the last visible/published sequence.

Recovery tests validate persistence. `BasicRecovery` prepares transactions, crashes after WAL flush, reopens, and checks that recovered prepared transactions below max enter `delayed_prepared_`; after committing recovered transactions and reopening again, the delayed set is empty and data is visible. `DisableGCDuringRecovery` ensures recovery does not garbage-collect historical key versions while replaying many entries with a smaller write buffer. `SequenceNumberZero` validates compaction output with sequence number 0 is treated as visible to any snapshot.

Rollback coverage exercises prepared data cancellation. `Rollback` checks rollback before and after crash for Put, Merge, Delete, and SingleDelete cases, including old values and not-found states. `RollbackPreparedAfterCommitWriteFailure` injects retryable write failures into commit and rollback paths, resumes the DB, and verifies rollback can be retried so prepared state is removed before teardown. `BasicRollbackDeletionTypeCb` and `SingleDeleteAfterRollback` validate the optional rollback deletion callback that chooses `SingleDelete` when rolling back a prepared `Put`.

Compaction tests assert that the compaction iterator consults write-prepared visibility rather than just raw sequence ordering. `CompactionShouldKeepUncommittedKeys` and `CompactionShouldKeepSnapshotVisibleKeys` verify uncommitted versions and snapshot-visible older versions survive compaction. The `ReleaseSnapshotDuringCompaction*`, `ReleaseEarliestSnapshotDuringCompaction*`, `ReleaseSnapshotBetweenSDAndPutDuringCompaction`, `ReleaseEarliestWriteConflictSnapshot_SingleDelete`, and `ReleaseEarliestSnapshotAfterSeqZeroing*` tests use sync points to release snapshots while compaction is choosing which keys, deletes, and single-deletes can be dropped or sequence-zeroed. `CompactionKeepSnapshotVisibleKeysRandomized` runs a randomized transaction/snapshot workload and checks all snapshots before and after flush and compaction.

Non-atomic race tests cover the cases where visibility metadata changes in multiple steps. `NonAtomicCommitOfDelayedPrepared` splits reads and commits around delayed prepared cleanup and commit-cache updates. `NonAtomicUpdateOfDelayedPrepared` splits around `delayed_prepared_empty_` and max advancement. `NonAtomicUpdateOfMaxEvictedSeq` splits after reading max but before cache lookup. `AddPreparedBeforeMax` targets the two-write-queue race where a prepare is added while max is being advanced past it. `CommitOfDelayedPrepared` repeatedly takes snapshots between publish and prepared cleanup for delayed prepares with varying commit cache size and sub-batch counts.

The tail of the file covers iterators, policy compatibility, and range tombstone insertion. `Iterate` verifies DB and transaction iterators see the same write-prepared view before and after commit, while `IteratorRefreshNotSupported` documents unsupported refresh. Cross-compatibility tests verify clean write-policy switches and WAL incompatibility failures. The range tombstone tests check that read-path tombstone synthesis is allowed only when it cannot hide prepared entries and includes a regression for sequence-number bumping that could shadow a later committed prepared write.

## State and persistence behavior under test

The test suite repeatedly observes `prepared_txns_`, `delayed_prepared_`, `delayed_prepared_empty_`, `commit_cache_`, `old_commit_map_`, `snapshot_cache_`, `snapshots_all_`, `max_evicted_seq_`, and `future_max_evicted_seq_`. Persistence behavior is centered on WAL markers: prepared batches survive crashes as recovered transactions, commit markers determine whether recovered prepared entries are removed, and sequence number state is checked after WAL flush, reopen, memtable flush, and compaction.

Many tests intentionally shrink `wp_commit_cache_bits` and `wp_snapshot_cache_bits` to force normally rare paths: commit-cache eviction, old-commit-map retention, snapshot cache overflow into the slower vector, and max-evicted advancement. This makes the tests strong signals for bugs that only appear under long-running snapshots, frequent evictions, duplicate-key sub-batches, or two-write-queue commit publishing.

## Dependencies and integration points

The file depends on the transaction test framework (`transaction_test.h`, `transaction_test_util.h`), DB internals (`DBImpl`, internal key inspection, compaction sync points), `FaultInjectionEnv`, merge operators, mock table helpers, `SyncPoint`, perf context counters, and RocksDB public transaction APIs. It integrates with `WritePreparedTxnDB` internals through friend classes and `dynamic_cast`, and with compaction through named sync points in `CompactionIterator`.

## Risks and maintenance notes

The tests rely on internal sequence-number expectations that differ between one-write-queue and two-write-queue modes, so changes to publish semantics or empty commit accounting can require careful updates. Sync-point-heavy tests are sensitive to renamed sync point labels and control-flow restructuring. Several tests intentionally simulate non-recommended use such as erasing non-existent prepared heap entries; those are regression guards and should not be removed just because they look unnatural. Range tombstone tests indicate a newer integration risk: read-path optimization must account for `min_uncommitted` and prepared entries, not only committed tombstone ranges.

## Test signals

This file itself is the test signal for `write_prepared_txn.cc`, `write_prepared_txn.h`, and `write_prepared_txn_db.cc`. High-value signals include crash/reopen cycles, `FaultInjectionTestFS` retryable write failures, small commit/snapshot cache settings, `SyncPoint` race schedules, exact internal-key assertions after compaction, DB and transaction iterator comparisons, `MultiGet` cross-checks, and policy compatibility tests for clean and dirty WAL transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_transaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.cc

## Purpose

This file implements `WritePreparedTxn`, the per-transaction object for RocksDB's write-prepared transaction policy. In write-prepared 2PC, `Prepare()` writes user data to WAL and memtable immediately, but that data is not visible until `Commit()` writes a commit marker and the DB publishes the prepare sequence through the write-prepared commit map. This implementation adapts pessimistic transaction behavior to that policy by overriding reads, prepare, commit, rollback, snapshot validation, snapshot creation, and rebuild-from-WAL/batch behavior.

## Important APIs and functions

The constructor stores the owning `WritePreparedTxnDB*` and calls `Initialize()` after the base constructor so virtual overrides such as `SetSnapshot()` can be used correctly. `Initialize()` delegates to `PessimisticTransaction::Initialize()` and resets `prepare_batch_cnt_`.

`Get()`, `GetImpl()`, and `MultiGet()` wrap reads with `WritePreparedTxnReadCallback`. They call `wpt_db_->AssignMinMaxSeqs()` to get the read snapshot sequence and the smallest uncommitted sequence, then read through `write_batch_` plus DB. Callback validity and `wpt_db_->ValidateSnapshot()` are checked afterward; invalid unbacked snapshots return `Status::TryAgain()` and record `TXN_GET_TRY_AGAIN`.

`GetIterator()` deliberately obtains the base iterator from `WritePreparedTxnDB::NewIterator()` rather than the root DB, then overlays the transaction write batch with `NewIteratorWithBase()`. `GetCoalescingIterator()` and `GetAttributeGroupIterator()` return `NotSupported` error iterators for write-prepared/write-unprepared transactions.

`PrepareInternal()` marks the write batch with `MarkEndPrepare`, computes duplicate-key sub-batches via `SubBatchCnt()`, and writes the batch to WAL and memtable through `DBImpl::WriteImpl()`. It installs `AddPreparedCallback` as a pre-release callback so prepared sequences are added to `prepared_txns_` in sequence order before the write is released to readers. The returned sequence becomes the transaction id and prepare sequence.

`CommitInternal()` writes a commit marker and updates the commit map. For the normal case where the commit-time batch is empty, it writes WAL-only with memtable disabled and uses `WritePreparedCommitEntryPreReleaseCallback` to add commit entries and publish sequence numbers. If the commit-time batch contains data, the code only permits it for `use_only_the_last_commit_time_batch_for_recovery_`; otherwise it rejects the transaction because commit-time data can create two uncommitted versions of a key and break compaction invariants. In two-write-queue mode with commit-time data, it may perform a second empty write to the nonmem queue to publish the sequence and commit both the prepare batch and auxiliary data batch.

`CommitWithoutPrepareInternal()` and `CommitBatchInternal()` support non-2PC direct commits by computing the sub-batch count and delegating to `WritePreparedTxnDB::WriteInternal()`.

`RollbackInternal()` constructs a rollback batch that restores each written key to the value visible before the transaction, or deletes/single-deletes it if no prior value exists. It reads prior values using a max snapshot and a write-prepared read callback, adds a rollback marker, writes the rollback batch to memtable, and then commits both the original prepared sequence and rollback sequence in the commit map so snapshots and compaction can treat the canceled prepared data consistently. Two-write-queue rollback uses an extra empty WAL-only write and `WritePreparedRollbackPreReleaseCallback` to publish.

`ValidateSnapshot()` performs write-conflict validation for a tracked key by using the transaction snapshot's `min_uncommitted_`, a `WritePreparedTxnReadCallback`, and `TransactionUtil::CheckKeyForConflicts()`. `SetSnapshot()` obtains an enhanced snapshot from `WritePreparedTxnDB::GetSnapshotInternal()` so it includes `min_uncommitted_`. `RebuildFromWriteBatch()` delegates to the base class and refreshes `prepare_batch_cnt_`.

## Control flow

Read flow starts with io-activity validation, fills a read callback with `snap_seq` and `min_uncommitted`, reads from the transaction batch and DB, then checks that the callback never saw a released unbacked snapshot. For DB-backed snapshots validation is always true; for unbacked reads the snapshot sequence must still be above `max_evicted_seq_`.

Prepare flow is one write: mark end prepare, count sub-batches, install `AddPreparedCallback`, call `WriteImpl()` with memtable enabled, record `seq_used` as the transaction id. Commit flow is normally one WAL-only write: mark commit, install commit-entry callback, call `WriteImpl()` with memtable disabled, and let the callback add commit entries, publish `LastPublishedSequence`, and remove prepared state. The less common commit-time-data flow can be two writes so data insertion and sequence publishing remain correctly ordered.

Rollback flow is more complex: build compensating mutations by iterating the prepared write batch, read previous committed values with a write-prepared callback, append rollback marker, write the rollback mutations, then publish commit metadata that makes the original prepared versions invisible and the rollback batch visible. Cleanup of prepared entries is carefully delayed until after publishing in paths where `SmallestUnCommittedSeq()` depends on the ordering.

## State and persistence behavior

`prepare_batch_cnt_` is the key per-transaction state added by this class. It records how many sequence-number slots the prepared batch occupies when duplicate keys require multiple sub-batches. The value is used by commit and rollback callbacks to add or remove all relevant prepare sequences from the DB's prepared structures.

Prepare data is durable because `PrepareInternal()` forces WAL enabled. Commit markers are durable WAL records but usually do not touch memtables. Rollback writes compensating data and a rollback marker. The transaction id is set to the prepare sequence and later used as the primary key into commit metadata and recovered transaction lookup.

## Dependencies and integration points

This file depends on `DBImpl::WriteImpl`, `WriteBatchInternal` marker helpers, `WriteBatchWithIndex` read-overlay methods, `WritePreparedTxnDB` visibility helpers, pre-release callbacks declared in `write_prepared_txn_db.h`, `TransactionUtil::CheckKeyForConflicts`, and pessimistic transaction base behavior. It integrates with two-write-queue publishing through `DBImpl::immutable_db_options().two_write_queues`, `SetLastPublishedSequence`, and memtable-disabled WAL-only writes.

## Risks

The largest risks are ordering bugs around pre-release callbacks. `AddPrepared` must happen before readers can see a prepared sequence; `AddCommitted` and `SetLastPublishedSequence` must happen before a commit is visible; `RemovePrepared` must happen after publishing or `SmallestUnCommittedSeq()` can move too far forward. Commit-time batches are risky enough that this file rejects them unless the recovery-only option is enabled. Rollback is also sensitive because it synthesizes user mutations from old values and must avoid double-processing duplicate keys.

## Test signals

Coverage comes mainly from `write_prepared_transaction_test.cc`: prepare/commit/recovery in `BasicRecovery`, rollback in `Rollback` and `RollbackPreparedAfterCommitWriteFailure`, duplicate-key sub-batch behavior in `WriteBatchWithIndex.SubBatchCnt` and `AdvanceMaxEvictedSeqWithDuplicates`, commit-time sequence ordering in `SeqAdvanceConcurrent`, visibility reads in `IsInSnapshot` and `Iterate`, compaction interaction in the compaction tests, and two-write-queue races in `AddPreparedBeforeMax` and `CommitOfDelayedPrepared`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.h -->
# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.h

## Purpose

This header declares `WritePreparedTxn`, the transaction object used by `WritePreparedTxnDB`. Its extensive file-level comment documents the core design: write-prepared 2PC writes user data to memtable and WAL during prepare, records the prepare sequence as uncommitted, and later commits by writing a WAL-only commit marker whose sequence becomes the commit timestamp. Readers use `LastPublishedSequence` plus the write-prepared commit map to distinguish committed and uncommitted memtable entries.

The header also explains why two write queues are useful. Prepare goes through the main write queue because it inserts into memtables, while commit can often go through a nonmem WAL-only queue. This lets serial commit markers avoid waiting behind heavier prepare-time memtable insertion, especially in MySQL-style 2PC workloads.

## Public API surface

`WritePreparedTxn` derives from `PessimisticTransaction`. It deletes copying, has a virtual destructor, and exposes overridden transaction APIs:

- `Get()` and `MultiGet()` use write-prepared snapshot semantics where read visibility is based on the last published WAL sequence rather than simply the latest memtable sequence.
- `GetIterator()` overloads return iterators that combine a write-prepared DB iterator with the transaction's local write batch.
- `GetCoalescingIterator()` and `GetAttributeGroupIterator()` are declared but implemented as unsupported for write-prepared/write-unprepared transactions.
- `SetSnapshot()` is overridden so transaction snapshots are enhanced with `min_uncommitted_`.

The protected `Initialize()` override ensures transaction-specific state is reset, and `SetId()` is made visible to friend classes while still routing to `Transaction::SetId()`.

## Private API surface and state

Private overrides define the lifecycle:

- `GetImpl()` applies write-prepared read callbacks for single-key reads.
- `PrepareInternal()` writes the prepared batch to WAL and memtable and registers prepared sequence numbers.
- `CommitWithoutPrepareInternal()` and `CommitBatchInternal()` support single-phase writes through the write-prepared DB.
- `CommitInternal()` writes commit metadata and publishes the prepared data.
- `RollbackInternal()` writes compensating rollback data and publishes both rollback and prepared entries consistently.
- `ValidateSnapshot()` checks write conflicts using write-prepared visibility.
- `RebuildFromWriteBatch()` rebuilds local transaction state and recalculates sub-batch count.

The class stores `WritePreparedTxnDB* wpt_db_` and `size_t prepare_batch_cnt_`. The DB pointer is the gateway to visibility state, snapshot creation, commit map updates, and comparator maps. `prepare_batch_cnt_` records how many prepare sequence slots the transaction owns when duplicate keys split a write batch into sub-batches.

Friend declarations allow the DB implementation, write-unprepared variants, and selected tests to access internals needed for recovery and white-box validation.

## Control flow documented by the header

The comment's sequence-number table is the clearest contract. Before prepare, last sequence, allocated sequence, and published sequence are equal. Prepare allocates a new sequence, writes WAL and memtable, advances last sequence, but does not advance published sequence because the data is uncommitted. Commit allocates another sequence, writes only a commit marker to WAL in the usual case, updates the commit cache in a pre-release callback, then advances published sequence so readers can observe the commit.

This distinction means snapshots and readers must use `LastPublishedSequence` and write-prepared callbacks, not just the latest assigned sequence. It also means commit ordering and callback ordering are part of correctness, not just performance.

## Dependencies and integration points

The header includes RocksDB public APIs (`db.h`, `snapshot.h`, `transaction.h`, `transaction_db.h`, `write_batch_with_index.h`) and internal transaction infrastructure (`pessimistic_transaction.h`, `pessimistic_transaction_db.h`, `transaction_base.h`, `transaction_util.h`) plus write callback support. It forward-declares `WritePreparedTxnDB` to avoid a circular dependency while allowing the implementation file to connect transaction lifecycle operations to DB-level state.

## State and persistence behavior

The header describes a persistent marker protocol: prepared data is durable after phase 1 because WAL is enabled and memtable data exists at `prepare_seq`; commit is durable after phase 2 because a commit marker is written at `commit_seq`; the in-memory commit map publishes `prepare_seq -> commit_seq` for reads, compaction, and snapshot checks. The class state itself is small because most persistence and visibility state lives in `WritePreparedTxnDB`.

## Risks

Any change that makes reads use ordinary DB snapshots without `LastPublishedSequence` can expose prepared-but-uncommitted data. Any change that routes prepare away from memtable insertion or commit toward unnecessary memtable insertion changes the write-prepared performance and correctness model. The comment also points to two-write-queue ordering: if commit markers are published out of order, readers may observe gaps where prior sequences are not yet publishable.

## Test signals

The design declared here is validated by `write_prepared_transaction_test.cc`. Important signals are `TxnInitialize` for virtual initialization and enhanced snapshots, `Iterate` for iterator behavior, `BasicRecovery` for marker persistence, `SeqAdvanceConcurrent` for sequence accounting, and `MaxCatchupWithNewSnapshot` for the published-sequence versus max-evicted sequence invariant.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.cc

## Purpose

This file implements `WritePreparedTxnDB`, the DB-level transaction engine for write-prepared mode. It owns the visibility metadata that lets RocksDB store uncommitted prepared data in memtables and SSTs while presenting snapshot-correct committed views to readers and compaction. The implementation manages recovery initialization, direct writes, reads and iterators with visibility callbacks, prepared sequence tracking, commit-cache insertion and eviction, snapshot-cache maintenance, old-commit retention for long-running snapshots, and duplicate-key sub-batch counting.

## Important APIs and functions

`Initialize()` rebuilds prepared state from `DBImpl::recovered_transactions()`, adds each recovered prepare sequence in order, advances `max_evicted_seq_` to the latest sequence, creates a sequence gap after recovery, installs `WritePreparedSnapshotChecker`, installs a recoverable-state pre-release callback for flush-time recovered state, and delegates remaining setup to `PessimisticTransactionDB::Initialize()`.

`VerifyCFOptions()` extends the pessimistic DB checks by requiring a memtable factory that can handle duplicated keys. This is required because prepared/uncommitted and committed versions of the same user key can coexist.

`BeginTransaction()` creates or reinitializes `WritePreparedTxn`. `Write()` overloads route direct writes either through pessimistic locking or through `WriteInternal()` when concurrency control is explicitly skipped.

`WriteInternal()` handles non-2PC writes under write-prepared visibility. It updates per-key protection info if needed, computes `batch_cnt` with `SubBatchCounter` when not provided, inserts a noop separator, writes the batch with memtable enabled, and in two-write-queue mode performs a second empty memtable-disabled write that publishes the commit sequence. Pre-release callbacks either add prepared state before the publish step or directly update the commit map in one-write-queue mode.

`Get()`, `GetImpl()`, and `MultiGet()` run reads through `WritePreparedTxnReadCallback`. `GetImpl()` returns `TryAgain` if an unbacked snapshot became invalid because `max_evicted_seq_` advanced during the read. Timestamp-returning overloads are explicitly unsupported.

`NewIterator()` and `NewIterators()` create DB iterators with write-prepared callbacks. If the caller did not provide a snapshot, the DB takes an owned snapshot and stores it in `IteratorState` so commit-map entries needed by the iterator cannot be garbage-collected before iterator cleanup. Iterator refresh is disabled by passing `allow_refresh = false`.

`Init()` sizes and zero-initializes the snapshot cache and commit cache from transaction DB options, sets the dummy max snapshot, and stores the rollback deletion callback.

`AddPrepared()`, `CheckPreparedAgainstMax()`, `RemovePrepared()`, and `SmallestUnCommittedSeq()` manage prepared state. Recent prepared entries live in `prepared_txns_`, a monotonic heap optimized for cheap top reads and deferred erase. When `max_evicted_seq_` advances past prepared entries, `CheckPreparedAgainstMax()` moves them to `delayed_prepared_` so `IsInSnapshot()` can still detect them without searching the heap for old sequences. `RemovePrepared()` clears both structures and any delayed commit metadata for all sub-batches.

`AddCommitted()` inserts a `prepare_seq -> commit_seq` entry into the fixed-size atomic commit cache. When the target cache slot already contains another valid entry, the evicted entry can advance `max_evicted_seq_`; if it overlaps a live snapshot, `CheckAgainstSnapshots()` preserves enough information in `old_commit_map_` so old snapshots still know the evicted prepare was not yet committed. The update uses `ExchangeCommitEntry()` with retry protection.

`AdvanceMaxEvictedSeq()` publishes a future max first, moves prepared entries below the new max into delayed state, fetches live snapshots below max from the DB, updates snapshot caches, initializes old-commit-map buckets for those snapshots, and finally advances `max_evicted_seq_`. `GetSnapshotInternal()` uses `future_max_evicted_seq_` to avoid returning a new snapshot at or below a max whose snapshot list has not yet been captured; in rare cases it calls `AdvanceSeqByOne()` until a larger snapshot is available.

`UpdateSnapshots()`, `CleanupReleasedSnapshots()`, `ReleaseSnapshotInternal()`, `CheckAgainstSnapshots()`, and `MaybeUpdateOldCommitMap()` implement snapshot metadata maintenance. A small atomic `snapshot_cache_` serves lock-free-ish readers; overflow snapshots live in `snapshots_` under `snapshots_mutex_`. Released snapshots trigger old-commit-map cleanup once they are at or below max. Evicted commit entries are retained only for snapshots in the overlap window `prep_seq <= snapshot_seq < commit_seq`.

`SubBatchCounter` counts sub-batches in a write batch by tracking duplicate keys per column family. A duplicate key starts a new sub-batch so each sub-batch has no duplicate user key under its comparator.

## Control flow

Direct write flow begins in `Write()`. If locking is skipped, `WriteInternal()` inserts the batch into DB and creates commit visibility metadata. With two write queues, the first write inserts data and adds prepared state; a second empty WAL-disabled, memtable-disabled write publishes commit metadata from the nonmem queue. With one write queue, one callback can add commit entries because sequence publication is coupled with the write.

Read flow begins by assigning a max sequence and min uncommitted sequence. If a real snapshot exists, its enhanced `min_uncommitted_` and sequence number are used. If no snapshot exists, `SmallestUnCommittedSeq()` supplies the lower bound and DB internals later choose a visible max. `WritePreparedTxnReadCallback::IsVisibleFullCheck()` calls `IsInSnapshot()` for candidate internal sequence numbers. If the callback discovers an unbacked snapshot was effectively released, the read reports `TryAgain`.

Commit-cache eviction flow is the central maintenance loop. `AddCommitted()` may evict an older entry from `commit_cache_`; that entry's commit sequence can become the new `max_evicted_seq_` or contribute to a stepped max advance. Advancing max requires moving old prepares, collecting snapshots, updating snapshot caches, potentially populating `old_commit_map_`, and only then publishing `max_evicted_seq_`.

Snapshot flow is two-sided. Taking a snapshot computes `min_uncommitted_` before getting the DB snapshot and rejects snapshots at or below future max. Releasing a snapshot calls `ReleaseSnapshotInternal()` so old-commit-map rows can be removed when no longer needed.

## State and persistence behavior

Most state is in memory and rebuilt or conservatively reset on recovery. `prepared_txns_` and `delayed_prepared_` represent uncommitted prepared data. `commit_cache_` is an in-memory acceleration structure for recent commits. `max_evicted_seq_` marks the range where cache absence is ambiguous and may require old snapshot metadata. `old_commit_map_` stores only evicted prepare sequences that are not visible to specific old snapshots. `snapshot_cache_`, `snapshots_`, and `snapshots_all_` track live snapshots below max. `future_max_evicted_seq_` prevents new snapshots from escaping the capture window during max advancement.

Persistent behavior comes from WAL and sequence numbers rather than from these in-memory maps. Recovery reads prepared transactions from `DBImpl`, reconstructs prepared state, advances max to the latest sequence, and sets `LastAllocatedSequence`, `LastSequence`, and `LastPublishedSequence` to `last_seq + 1` to create a clean gap after recovery. Commit and rollback markers in WAL determine whether recovered prepares remain uncommitted or become visible.

## Dependencies and integration points

This implementation integrates deeply with `DBImpl`, `versions_`, `WriteImpl`, `NewIteratorImpl`, `SetSnapshotChecker`, `SetRecoverableStatePreReleaseCallback`, `logs_with_prep_tracker`, `ManagedSnapshot`, column family handles and comparators, `PreReleaseCallback`, `ReadCallback`, `TransactionUtil`, and `PessimisticTransactionDB`. It uses `SyncPoint` labels as test hooks and statistics tickers such as `TXN_GET_TRY_AGAIN`, `TXN_DUPLICATE_KEY_OVERHEAD`, `TXN_PREPARE_MUTEX_OVERHEAD`, `TXN_SNAPSHOT_MUTEX_OVERHEAD`, and `TXN_OLD_COMMIT_MAP_MUTEX_OVERHEAD`.

## Risks

The main correctness risk is non-atomic coordination among commit cache, delayed prepared state, snapshot caches, old commit map, and max advancement. The code relies on ordering rules: `future_max_evicted_seq_` is updated before fetching snapshots; prepared entries are copied to delayed state before removal from the heap; commit entries are installed before publishing; prepared entries are removed after publishing. Violating any of these can expose uncommitted values, hide committed values, or allow compaction to drop required versions.

Another risk is cache sizing and entry encoding. `CommitEntry64b` can encode only commit deltas below the format's upper bound; workloads with very large gaps between prepare and commit can hit the runtime guard. Duplicate-key sub-batch accounting must remain consistent with sequence allocation or `RemovePrepared()` and `AddCommitted()` will cover the wrong sequence range. Iterator ownership is also sensitive: without an owned snapshot, a no-snapshot iterator could outlive the commit-map metadata it needs.

## Test signals

`write_prepared_transaction_test.cc` directly covers most paths in this file. High-signal tests include `CommitMap`, `CommitEntry64b.BasicTest`, `OldCommitMapGC`, `CheckAgainstSnapshots`, `SnapshotConcurrentAccess`, `AdvanceMaxEvictedSeqBasic`, `MaxCatchupWithNewSnapshot`, `MaxCatchupWithUnbackedSnapshot`, `CleanupSnapshotEqualToMax`, `SmallestUnCommittedSeq`, `BasicRecovery`, `Rollback`, the non-atomic delayed-prepared/max tests, `AddPreparedBeforeMax`, `CommitOfDelayedPrepared`, iterator tests, and compaction/snapshot-release tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.cc -->
