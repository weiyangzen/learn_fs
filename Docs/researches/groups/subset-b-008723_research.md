# subset-b-008723 research

Work item: `subset-b-008723`

This grouped report covers the RocksDB write-prepared/write-unprepared transaction files and the trie-index bitvector implementation listed in the worker prompt. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.h -->
# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.h

## Purpose

`write_prepared_txn_db.h` declares and partially defines `WritePreparedTxnDB`, the pessimistic transaction DB variant that writes prepared transaction data into the DB before commit and uses commit metadata to decide whether sequence numbers are visible to a snapshot. It is the base visibility and recovery substrate used by write-prepared transactions and by write-unprepared transactions. The file also defines callbacks used by `DBImpl::WriteImpl` to add prepared sequence numbers, add commit entries, publish sequences in two-write-queue mode, and count duplicate-key sub-batches.

## Important APIs, types, and functions

The main type is `WritePreparedTxnDB : public PessimisticTransactionDB`. Public integration points override transaction DB methods: `Initialize`, `BeginTransaction`, `Write`, `Get`, `MultiGet`, `NewIterator`, `NewIterators`, and unsupported coalescing/attribute-group iterator methods. The key public visibility API is `IsInSnapshot(prep_seq, snapshot_seq, min_uncommitted, snap_released)`, which determines whether a value written at a prepare sequence is committed at a snapshot.

`SnapshotBackup` distinguishes real RocksDB snapshots from unbacked sequence-number snapshots. `CommitEntry` stores `<prep_seq, commit_seq>`. `CommitEntry64bFormat` and `CommitEntry64b` compact commit-cache entries into 64 bits by storing the high prepare bits plus commit delta. `PreparedHeap` tracks the smallest outstanding prepared sequence with amortized O(1) erase through a secondary erased heap. `WritePreparedTxnReadCallback` adapts DB reads so `DBIter` can skip uncommitted prepared values. `AddPreparedCallback`, `WritePreparedCommitEntryPreReleaseCallback`, and `WritePreparedRollbackPreReleaseCallback` are `PreReleaseCallback` implementations used during write publication. `SubBatchCounter` splits write batches containing duplicate keys into multiple sub-batches for sequence/visibility accounting.

## Control flow and state behavior

The core read path enters `AssignMinMaxSeqs` to compute `min_uncommitted` and `max` from either a real `SnapshotImpl` or current DB state. A read callback then calls `IsInSnapshot` for candidate sequence numbers. `IsInSnapshot` first handles fast cases: sequence 0 is always visible, sequences greater than the snapshot are not, and sequences below `min_uncommitted` are visible. Otherwise it probes the commit cache, handles races with `max_evicted_seq_`, checks `delayed_prepared_` for long-running prepared transactions, then consults `old_commit_map_` for evicted commit-cache entries that overlap old snapshots. If a snapshot is no longer backed and the metadata needed to distinguish visibility has been dropped, the method returns true but flags `snap_released`.

Prepared writes are added through `AddPrepared`, normally from `AddPreparedCallback` before write sequence numbers are fully visible. Commits call `AddCommitted`, which inserts into the fixed-size commit cache and may advance `max_evicted_seq_`. Advancing the max evicted sequence triggers maintenance over live snapshots, old commit maps, and delayed prepared sets so old reads still know which evicted prepared sequence numbers were committed after their snapshot. `SmallestUnCommittedSeq` reads `prepared_txns_`, `delayed_prepared_`, and `DBImpl::GetLatestSequenceNumber` in a deliberately ordered way to avoid missing in-flight prepared data without taking every lock atomically.

State is mostly in-memory metadata rebuilt or advanced during DB initialization: `snapshot_cache_`, `snapshots_`, `snapshots_all_`, `commit_cache_`, `old_commit_map_`, `delayed_prepared_`, `delayed_prepared_commits_`, and `prepared_txns_`. The durable transaction markers and WAL records live in the underlying DB/WAL; this header defines how in-memory visibility state interprets them after recovery.

## Dependencies and integration points

This file depends deeply on RocksDB internals: `DBImpl`, `DBIter`, `SnapshotImpl`, `PreReleaseCallback`, `ReadCallback`, `SnapshotChecker`, `WriteBatch`, `TransactionDBOptions`, `PessimisticTransactionDB`, and `WritePreparedTxn`. It reaches into `DBImpl` publication behavior, statistics tickers, write queues, WAL prep-section tracking, column-family comparator maps, and `SnapshotImpl::min_uncommitted_`. Write-unprepared code is a friend and reuses protected/private machinery such as `AssignMinMaxSeqs`, `ValidateSnapshot`, `AddPrepared`, `RemovePrepared`, `AddCommitted`, and `ShouldRollbackWithSingleDelete`.

## Risks and edge cases

Correctness depends on memory ordering around `max_evicted_seq_`, `delayed_prepared_empty_`, commit-cache probes, and delayed-prepared cleanup. `IsInSnapshot` contains retry logic and a runtime failure after 100 interrupted max-evicted updates, which signals an unexpected high-contention pattern. The compact `CommitEntry64b` representation assumes commit deltas fit within the configured bit budget; too-large deltas throw. Snapshot release handling is subtle: unbacked snapshots can become invalid once `max_evicted_seq_` passes them. `PreparedHeap` assumes prepare sequence ordering for efficient push/top behavior, and debug assertions guard destructor emptiness except during crash tests. Old snapshots and delayed prepared transactions are expected rare but trigger mutex overhead and logging. Unsupported iterator APIs return `NotSupported`, so callers needing coalescing or attribute-group iterators cannot use this DB mode.

## Test signals

The friend list references extensive write-prepared tests for commit cache, old commit map GC, non-atomic delayed-prepared updates, max-evicted races, snapshot release, recovery, rollback, and smallest-uncommitted behavior. The write-unprepared tests in this work item exercise this header indirectly through read callbacks, recovery, commit/rollback callbacks, WAL prep-section tracking, iterator creation, and snapshot validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_transaction_test.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_transaction_test.cc

## Purpose

`write_unprepared_transaction_test.cc` is the parameterized unit-test suite for RocksDB's `WRITE_UNPREPARED` transaction policy. It validates read-your-own-write semantics after unprepared flushes, snapshot and iterator visibility, crash recovery, commit and rollback behavior, WAL prep-section retention, savepoints, untracked keys, active iterator invalidation, and range-tombstone synthesis safety.

## Important APIs, types, and functions

The test fixture `WriteUnpreparedTransactionTestBase` derives from `TransactionTestBase` and selects ordered writes plus the supplied write policy. `WriteUnpreparedTransactionTest` parameterizes stackable DB usage, two-write-queue mode, write policy, point-lock manager mode, and deadlock timeout. `WriteUnpreparedSnapshotTest` adds `SnapshotAction` (`NO_SNAPSHOT`, `RO_SNAPSHOT`, `REFRESH_SNAPSHOT`) and `VerificationOperation` (`VERIFY_GET`, `VERIFY_NEXT`, `VERIFY_PREV`).

Tests include `ReadYourOwnWrite` in two forms, `RecoveryTest`, `UnpreparedBatch`, `MarkLogWithPrepSection`, `NoSnapshotWrite`, `IterateAndWrite`, `IterateAfterClear`, `SavePoint`, `UntrackedKeys`, and three range-tombstone tests: `RangeTombstoneMultipleBatchesAndCommit`, `RangeTombstoneCalcMaxVisibleSeqExtendedVisibility`, and `RangeTombstoneOwnDeletionsAndRollback`. The helper `VerifyIterator` normalizes forward and reverse iteration into ascending key vectors.

## Control flow and state behavior

The first read-your-own-write test forces unprepared batches into the DB with `FlushWriteBatchToDB(false)` after repeated writes to keys `a` and `b`; it verifies `Get`, `Seek`, `Next`, `SeekToFirst`, `SeekForPrev`, `Prev`, and `SeekToLast` with and without reseek pressure through `max_sequential_skip_in_iterations`. The snapshot test runs 1000 iterations over five keys, uses a counter as a logical sequence, and verifies that values are before or after the chosen snapshot action for `Get`, forward iteration, and reverse iteration.

`RecoveryTest` varies flush threshold, empty/non-empty previous DB state, action (`UNPREPARED`, `ROLLBACK`, `COMMIT`), and number of batches. It writes named transactions, optionally prepares, simulates WAL flush and crash, reopens without delete, obtains prepared transactions, then commits or rolls back and verifies final contents. `UnpreparedBatch` checks that visible DB iterators hide unprepared data before commit and show only committed data after commit. `MarkLogWithPrepSection` switches WAL files between writes and verifies `TEST_FindMinLogContainingOutstandingPrep` tracks the oldest log containing uncommitted prepared/unprepared data until transactions finish.

Iterator-focused tests cover transactions without snapshots, writing while an iterator is active, and invalidating transaction iterators after commit/rollback. Savepoint and untracked-key tests cover rollback of flushed savepoints and manually appended writes in the underlying `WriteBatch`. The range-tombstone tests set `min_tombstones_for_range_conversion`, use statistics and sync points, and verify that synthesized range tombstones are discarded when the iterator's visible sequence is widened to include a transaction's own unprepared writes.

## Dependencies and integration points

The suite includes `transaction_test.h`, `write_unprepared_txn.h`, and `write_unprepared_txn_db.h`. It relies on RocksDB test helpers such as `ReOpen`, `ReOpenNoDelete`, `TEST_Crash`, `TEST_SwitchWAL`, `FlushWAL`, `GetAllPreparedTransactions`, statistics tickers, `SyncPoint`, and transaction internals exposed through friend declarations. It explicitly casts to `WriteUnpreparedTxn` and `WriteUnpreparedTxnDB` to inspect unprepared sequence maps and DB internals.

## Risks and edge cases

The tests target subtle regressions: reseek loops when write-unprepared iterators need to skip invisible versions, snapshot validation gaps for reverse iteration, crashes between unprepared flush and prepare/commit, WAL deletion while uncommitted data still needs recovery, writes during iteration leaving stale `WriteBatchWithIndex` delta iterators, use-after-clear on transaction iterators, rollback of untracked keys, and range tombstone insertion at widened visible sequence numbers. Parameter combinations cover two-write-queue and lock-manager modes, but they still rely on deterministic single-process test orchestration rather than heavy concurrency.

## Test signals

This file is itself the test signal for the write-unprepared implementation. The strongest behavioral signals are that unprepared data is hidden from normal DB iterators, visible to the owning transaction, durable enough for prepared recovery, rolled back on unprepared recovery, and not allowed to seed unsafe range tombstone optimizations. The tests also assert no range tombstones are inserted when own unprepared deletes participate in the visible deletion run, and they check discarded ticker counts where expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_transaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.cc

## Purpose

`write_unprepared_txn.cc` implements `WriteUnpreparedTxn`, the transaction object for RocksDB's write-unprepared policy. Unlike standard write-prepared transactions, it may flush a transaction's data to the DB before prepare, keeps a map of its own unprepared sequence ranges, lets the transaction read those ranges, and repairs state through commit, rollback, savepoint, and recovery paths.

## Important APIs, types, and functions

`WriteUnpreparedTxnReadCallback::IsVisibleFullCheck` treats any sequence in the transaction's `unprep_seqs_` ranges as visible to itself, otherwise delegates to `WritePreparedTxnDB::IsInSnapshot`. The constructor and `Initialize` configure `write_batch_flush_threshold_`, clear `unprep_seqs_`, savepoint state, active iterators, recovery flags, and untracked keys.

Write operation overrides (`Put`, `Merge`, `Delete`, `SingleDelete`) route through `HandleWrite`, which may call `MaybeFlushWriteBatchToDB` before appending and updates `largest_validated_seq_` after successful writes. `RebuildFromWriteBatch` reconstructs tracked keys during recovery without reacquiring locks. `FlushWriteBatchToDB`, `FlushWriteBatchToDBInternal`, and `FlushWriteBatchWithSavePointToDB` turn in-memory write batches into unprepared or prepared DB writes and populate `unprep_seqs_`. `PrepareInternal`, `CommitWithoutPrepareInternal`, `CommitInternal`, `RollbackInternal`, savepoint methods, `Get`, `MultiGet`, `GetIterator`, and `ValidateSnapshot` implement the external transaction behavior.

## Control flow and state behavior

Before each write, `HandleWrite` flushes the existing batch if the flush threshold is exceeded and there are no active transaction iterators. Active iterators deliberately suppress flushing because `WriteBatchWithIndex` delta iterators could point into invalid memory after a flush. `FlushWriteBatchToDBInternal` requires a transaction name, records untracked keys from the current batch, appends an end-prepare marker that can mark the batch as unprepared, counts sub-batches, and calls `DBImpl::WriteImpl` with an `AddPreparedCallback`. On success it sets the transaction ID from the first prepare sequence if needed and records `unprep_seqs_[prepare_seq] = prepare_batch_cnt_`. Unprepared flushes clear the working batch; prepared flushes retain prepare state.

Savepoint-aware flushing splits the existing write batch at recorded byte boundaries. For each segment it rebuilds a new `WriteBatchWithIndex`, flushes it as unprepared, and records a `SavePoint` containing the then-current `unprep_seqs_` plus a managed DB snapshot. Rolling back to a flushed savepoint reads the keys modified since that savepoint at the saved snapshot, builds restorative writes via `WriteRollbackKeys`, flushes them as unprepared, and then reconciles the base transaction savepoint stack with a fake in-memory savepoint.

`CommitInternal` appends a commit marker to the commit-time batch. Empty commit-time batches can update commit metadata in one disabled-memtable write. Non-empty commit-time batches are only accepted for recovery-state optimization unless the code path is changed; if data is included, duplicate-key sub-batches are counted. Two-write-queue mode may require a first write that adds prepared entries for commit-batch data followed by an empty disabled-memtable write that updates the commit map and publishes the sequence. Successful commits remove all prepared ranges from `WritePreparedTxnDB` and clear `unprep_seqs_` and savepoints.

`RollbackInternal` builds a rollback batch by reading the previous visible version of every tracked and untracked key. It writes a rollback marker, writes the restorative batch, and uses `WriteUnpreparedCommitEntryPreReleaseCallback` so the original unprepared ranges are considered committed to the rollback sequence. This lets existing commit-cache machinery make older snapshots skip canceled unprepared values. Two-write-queue rollback mirrors commit by using a second empty write to publish commit metadata. `Clear` unlocks locks unless the transaction was recovered, invalidates active iterators, clears unprepared state, and then clears base state.

Reads (`GetImpl`, `MultiGet`) call `AssignMinMaxSeqs`, use `WriteUnpreparedTxnReadCallback` with the current `unprep_seqs_`, and return `TryAgain` if an unbacked snapshot became invalid. `GetIterator` asks `WriteUnpreparedTxnDB::NewIterator` for a DB iterator widened to the transaction's max visible sequence, wraps it with `WriteBatchWithIndex`, stores it in `active_iterators_`, and registers cleanup. `ValidateSnapshot` checks conflicts with a callback that treats own unprepared ranges as visible.

## Dependencies and integration points

This implementation depends on `DBImpl::WriteImpl`, `WriteBatchInternal` markers (`MarkEndPrepare`, `MarkCommit`, `MarkRollback`, `InsertNoop`), `WriteBatchWithIndex`, `LockTracker`, `TransactionUtil::CheckKeyForConflicts`, write-prepared callbacks and commit-cache APIs, `ManagedSnapshot`, and transaction DB options such as `rollback_merge_operands`, `default_write_batch_flush_threshold`, and two-write-queue configuration. It is tightly coupled to `WriteUnpreparedTxnDB` for iterator creation, snapshot assignment, column-family handle maps, and rollback deletion policy.

## Risks and edge cases

The implementation is sequence-number sensitive. Missing a range in `unprep_seqs_`, removing prepared state before sequence publication, or using an invalid unbacked snapshot can expose uncommitted data or hide committed data. Active iterator suppression of flushing protects memory safety but can increase memory retained in the current write batch. Untracked writes are supported by scanning batches and storing keys, but the header notes they complicate snapshot validation and savepoint rollback is currently less efficient because untracked keys are not recorded per savepoint. Rollback writes all restorative keys in one batch and has TODOs for subdivision and IO priority plumbing. Recovery transactions do not hold locks and rely on `recovered_txn_` cleanup behavior.

## Test signals

`write_unprepared_transaction_test.cc` directly exercises most paths: threshold flushing, read-your-own-write, recovery reconstruction and rollback, commit/rollback after prepare, savepoint flush/rollback, untracked-key rollback, iterator invalidation, writing while iterating, and range-tombstone discard behavior under widened visible sequence numbers. Assertions on `GetUnpreparedSequenceNumbers()` check when flushes populate `unprep_seqs_`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.h -->
# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.h

## Purpose

`write_unprepared_txn.h` declares the write-unprepared transaction class and its read callback. It explains the design problem: a transaction's uncommitted writes may already be in the DB, so reading its own writes cannot rely only on the in-memory `WriteBatchWithIndex`. The transaction must widen reads to the maximum of the snapshot sequence and its own unprepared sequence range, then use a custom callback to distinguish own writes, other unprepared writes, committed post-snapshot writes, and committed snapshot-visible writes.

## Important APIs, types, and functions

`WriteUnpreparedTxnReadCallback : public ReadCallback` accepts a `WritePreparedTxnDB`, snapshot sequence, `min_uncommitted`, a reference to `unprep_seqs`, and snapshot-backing mode. It overrides `IsVisibleFullCheck`, `Refresh`, and exposes `valid()`. `CalcMaxVisibleSeq` computes the read ceiling from the last unprepared range and snapshot sequence.

`WriteUnpreparedTxn : public WritePreparedTxn` overrides write APIs (`Put`, `Merge`, `Delete`, `SingleDelete`), lifecycle APIs (`PrepareInternal`, `CommitWithoutPrepareInternal`, `CommitInternal`, `RollbackInternal`, `Clear`), savepoint APIs (`SetSavePoint`, `RollbackToSavePoint`, `PopSavePoint`), read APIs (`Get`, `MultiGet`, `GetIterator`), recovery (`RebuildFromWriteBatch`), and conflict validation (`ValidateSnapshot`). Private helpers include `WriteRollbackKeys`, flush helpers, savepoint rollback, and `HandleWrite`.

## Control flow and state behavior

The header documents the iterator/read flow in detail. The read callback passes `CalcMaxVisibleSeq(unprep_seqs, snapshot)` to the parent `ReadCallback` so DB iteration does not filter out the transaction's own unprepared writes too early. `IsVisibleFullCheck` then provides exact visibility. The header also notes an important iterator caveat: max visible sequence is computed when the iterator is created, so later unprepared writes in the same transaction may not appear in that iterator.

Persistent and in-memory transaction state is represented by `unprep_seqs_`, mapping each unprepared or prepared DB write's first sequence to its sub-batch count. `last_log_number_` tracks the last WAL used, while inherited `log_number_` tracks the oldest WAL with uncommitted data. `recovered_txn_` marks transactions rebuilt from recovery shells, for which locks are tracked for rollback but not actually held. `largest_validated_seq_` records how far snapshot validation has proven there are no conflicting committed keys, which is required for safe reverse iteration when own unprepared writes widen visibility.

Savepoint state is split across base `save_points_`, `flushed_save_points_`, and `unflushed_save_points_`. A `SavePoint` stores the `unprep_seqs_` visible at the savepoint and a managed snapshot used to restore old values if rolling back after flushing. Active transaction iterators are stored in `active_iterators_` so they can be invalidated and so flushes can be suppressed while they exist. `untracked_keys_` records keys appended to the underlying batch without normal lock tracking so rollback can still repair them.

## Dependencies and integration points

The header includes `write_prepared_txn.h` and `write_unprepared_txn_db.h`, so the transaction class is intentionally coupled to both write-prepared base behavior and DB-specific iterator/snapshot helpers. It uses `LockTracker`, `WriteBatchWithIndex`, `ManagedSnapshot`, `BaseDeltaIterator`, column-family IDs, RocksDB transaction options, and DB write/read callbacks.

## Risks and edge cases

The header calls out several known risks. Untracked writes can break snapshot validation because checking only the largest sequence for a key can hide smaller committed versions; a TODO proposes either deeper validation or returning `NotSupported`. Savepoint state is redundant and must maintain invariants between flushed and unflushed stacks. Untracked keys are not recorded per savepoint, making rollback less efficient. Active iterators make flushing unsafe because their delta iterator may point into write-batch memory. Reverse iteration is safe only if snapshot validation has excluded committed values between the transaction snapshot and own unprepared sequence numbers.

## Test signals

Friend declarations expose internals to read-your-own-write, recovery, and unprepared-batch tests. The companion test file verifies the documented iterator, savepoint, untracked-key, recovery, and range-tombstone edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.cc

## Purpose

`write_unprepared_txn_db.cc` implements the DB wrapper for the write-unprepared policy. It extends write-prepared DB initialization, converts recovered prepared records into live `WriteUnpreparedTxn` objects, rolls back recovered unprepared records directly, and creates DB iterators that can expose the owning transaction's unprepared writes while preserving write-prepared visibility checks.

## Important APIs, types, and functions

`RollbackRecoveredTransaction` restores DB state for transactions that crashed while still unprepared. `Initialize` sets snapshot/recoverable-state callbacks, registers column families, verifies options, rebuilds prepared recovered transactions, populates prepared sequence metadata, advances max-evicted state, rolls back unprepared recovered transactions, deletes recovery shells, and re-enables compaction. `BeginTransaction` creates or reinitializes `WriteUnpreparedTxn`. `IteratorState` owns a `WriteUnpreparedTxnReadCallback` and optional managed snapshot for DB iterator cleanup. `NewIterator(ReadOptions, ColumnFamilyHandle*, WriteUnpreparedTxn*)` constructs the DB-side iterator used by transaction iterators.

## Control flow and state behavior

During direct rollback of recovered unprepared transactions, batches are processed in reverse sequence order. For each recovered batch, `RollbackWriteBatchBuilder` deduplicates keys per column family using the appropriate comparator, reads the value visible immediately before that batch (`last_visible_txn = batch_seq - 1`), and writes either the old value or a delete into a rollback batch. Merge operands are rolled back only if `rollback_merge_operands` is enabled. A rollback marker is appended and written to DB. In two-write-queue mode the last published sequence is updated manually.

Initialization first installs a `WritePreparedSnapshotChecker` and a recoverable-state pre-release callback that marks recovered-state sub-batches as committed. It then performs the base transaction DB setup: add column families, verify options, remember which column families need compaction re-enabled. For recovered prepared transactions, it creates a real write-unprepared transaction, marks it as recovered, sets log number, ID, name, prepare batch count, records every recovered batch in `unprep_seqs_`, rebuilds tracked keys from each batch, clears the working batch, and marks it `PREPARED`. It separately gathers all recovered prepare sequence ranges in ordered form and calls `AddPrepared` in sequence order.

After recovered prepared metadata is registered, `Initialize` advances `max_evicted_seq_` to the DB latest sequence and creates a sequence gap after recovery by setting last allocated, last sequence, and last published sequence to `last_seq + 1` when nonzero. Only then does it roll back recovered unprepared transactions. Compaction is re-enabled after prepared/unprepared recovery is resolved because compaction needs correct snapshot and prepare metadata to avoid preserving or dropping the wrong versions.

`NewIterator` ensures `ReadOptions::io_activity` is compatible, obtains or creates a snapshot, and rejects iterator creation if the transaction has unprepared writes and `largest_validated_seq_` is newer than the chosen snapshot. That guard protects `Prev()` semantics: reverse iteration can otherwise stop too early when committed values exist between snapshot sequence and own unprepared sequence. The DB iterator is created with `MaxVisibleSeq()` from the callback, making own unprepared writes reachable, and cleanup deletes `IteratorState`.

## Dependencies and integration points

The implementation uses `DBImpl::recovered_transactions`, `DBImpl::WriteImpl`, `logs_with_prep_tracker`, `VersionSet` sequence setters, column-family handles and comparators, `ArenaWrappedDBIter`, `ColumnFamilyHandleImpl`, `SuperVersion`, `ManagedSnapshot`, and the write-prepared snapshot checker. It relies on `WriteUnpreparedTxn` internals through friendship and on write-prepared metadata functions such as `AddPrepared`, `AdvanceMaxEvictedSeq`, and `GetCFHandleMap`.

## Risks and edge cases

Recovery ordering is critical. `AddPrepared` must happen before advancing max-evicted sequence, and unprepared rollback must happen only after max-evicted state can preserve snapshot decisions. The direct rollback path intentionally writes rollback records to WAL even during recovery because application XIDs might not be unique across restarts; disabling WAL could let later recovered transactions with the same name resurrect rolled-back data. Iterator creation can return `nullptr` for unvalidated writes, so callers must handle that failure. Rollback builder depends on comparator-aware deduplication and currently has TODOs for IO priority plumbing.

## Test signals

`RecoveryTest` verifies prepared recovered transactions are exposed by `GetAllPreparedTransactions` and can later commit or roll back, while unprepared recovered transactions are not exposed and are rolled back. Iterator behavior is exercised by read-your-own-write, no-snapshot, reverse iteration, and range-tombstone tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.h -->
# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.h

## Purpose

`write_unprepared_txn_db.h` declares the write-unprepared transaction DB wrapper and the commit pre-release callback specialized for a transaction that may have many unprepared sequence ranges. It is the public class boundary between transaction objects and the write-prepared visibility engine.

## Important APIs, types, and functions

`WriteUnpreparedTxnDB : public WritePreparedTxnDB` inherits constructors and overrides `Initialize` and `BeginTransaction`. It declares `NewIterator(ReadOptions, ColumnFamilyHandle*, WriteUnpreparedTxn*)`, a transaction-aware iterator factory distinct from normal DB iterator creation. It also declares private `RollbackRecoveredTransaction` for direct recovery cleanup.

`WriteUnpreparedCommitEntryPreReleaseCallback : public PreReleaseCallback` accepts a `WritePreparedTxnDB`, `DBImpl`, reference to `unprep_seqs`, optional commit data batch count, and `publish_seq` flag. Its `Callback` computes the last commit sequence, calls `AddCommitted` for every sequence covered by every unprepared range, optionally adds commit metadata for data written with the commit/rollback batch, and publishes the sequence in two-write-queue mode when configured.

## Control flow and state behavior

The DB class itself stores no new data members in the header; it reuses write-prepared state and implements write-unprepared behavior in the `.cc` file. The callback is stateful and must outlive the corresponding `WriteImpl` callback execution. Its `unprep_seqs_` reference points to transaction-owned sequence metadata, so callers must not clear or mutate that map until `WriteImpl` has finished invoking the callback. For each `(prepare_seq, batch_cnt)` pair, the callback commits every sequence from `prepare_seq` through `prepare_seq + batch_cnt - 1` to the same `last_commit_seq`.

If `data_batch_cnt_ > 0`, commit-time or rollback data written in the same write is also committed to the same last commit sequence. In two-write-queue mode, `SetLastPublishedSequence(last_commit_seq)` is called only when `publish_seq_` is true; some two-phase flows use a first callback to add prepared entries without publishing and a second disabled-memtable write to publish commit metadata.

## Dependencies and integration points

This header includes `write_prepared_txn_db.h` and `write_unprepared_txn.h`, and it integrates with `DBImpl`, `PreReleaseCallback`, `SequenceNumber`, and transaction internals. `WriteUnpreparedTxn` uses this callback in commit and rollback paths to update write-prepared commit-cache metadata for all unprepared batches as a unit.

## Risks and edge cases

The callback assumes `unprep_seqs` is non-empty and asserts that in the constructor. It relies on correct sub-batch counts; undercounting leaves unprepared sequence numbers uncommitted, while overcounting can incorrectly mark unrelated sequences committed. The reference member is efficient but lifetime-sensitive. Publishing in two-write-queue mode is explicitly optional, so callers must choose the flag correctly or readers may see inconsistent publication order.

## Test signals

The callback is exercised indirectly by commit and rollback tests for unprepared batches, recovery tests, and WAL prep-section tests. Two-write-queue parameterization in the test suite is important because it validates the publication branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/bitvector.cc -->
# sources/storage-engines/rocksdb/utilities/trie_index/bitvector.cc

## Purpose

`bitvector.cc` implements the serialized immutable bitvector and Elias-Fano compressed monotone sequence declared in `bitvector.h`. These data structures support the experimental trie index, especially LOUDS-style rank/select navigation and compressed offset storage.

## Important APIs, types, and functions

For `Bitvector`, the implementation provides `SerializedSize`, `EncodeTo`, `InitFromData`, `BuildFrom`, `BuildRankLUT`, `BuildSelectHints`, `FindNthZeroBit`, and `DistanceToNextSetBit`. `FindNthOneBit`, `Rank1`, `NextSetBit`, and `PrevSetBit` are inline in the header for hot paths. For `EliasFano`, it implements `BuildFrom`, `SerializedSize`, `EncodeTo`, and `InitFromData`.

## Control flow and state behavior

`Bitvector::SerializedSize` computes the exact binary footprint: two fixed 64-bit header fields, raw 64-bit words, a uint32 rank LUT padded to 8 bytes, and select1/select0 hint arrays padded to 8 bytes. `EncodeTo` appends that layout with `memcpy` and zero padding for alignment. `InitFromData` parses the same layout from external memory, validates header fields (`num_ones <= num_bits`, `num_bits <= UINT32_MAX`), derives all array counts, verifies sufficient size and pointer alignment, assigns raw pointers into the caller-owned buffer, and validates select hint bounds against the rank LUT size.

`BuildFrom` creates an owned serialized-like memory block from a `BitvectorBuilder`. It first allocates words plus rank LUT, copies builder words, builds the rank LUT to discover `num_ones_`, then resizes storage to include select hints, recomputes all internal pointers, and builds hint arrays. `BuildRankLUT` writes cumulative popcounts at every 256-bit sample boundary and sets `num_ones_`. `BuildSelectHints` records the rank sample that contains every 256th one or zero. `FindNthZeroBit` uses select0 hints, scans rank samples, masks padding bits in the last word, and calls `FindNthSetBitInWord` on the inverted word. `DistanceToNextSetBit` asserts the starting position is set and returns the distance to the next set bit or the sentinel distance to `num_bits_`.

`EliasFano::BuildFrom` handles empty input by building an empty high bitvector so serialization remains consistent. For non-empty sorted values, it computes `low_bits = floor(log2(universe / count))` when useful, builds unary-coded high bits by appending gaps and one bits, and packs low bits into an owned uint64 word array. `EncodeTo` writes `count`, `universe`, `low_bits`, the high bitvector, and low words. `InitFromData` validates header fields, limits `count_` to a reasonable maximum to avoid overflow, parses the high bitvector, derives low-word size, checks size/alignment, and points `low_words_` into external memory.

## Dependencies and integration points

The file depends on `util/coding.h` for fixed-width integer encoding in Elias-Fano, `util/math.h` via the header for popcount/log operations, `port/lang.h`, `rocksdb::Status`, and raw `Slice`-compatible byte storage. It is intended for trie index metadata blocks, where serialized data may be block-cache memory and must outlive objects initialized with `InitFromData`.

## Risks and edge cases

The deserialization path is intentionally defensive but still depends on alignment guarantees from serialized buffers or block cache allocations. `Bitvector` pointers into external data become invalid if the backing slice is freed. `BuildRankLUT` asserts `num_bits_ <= UINT32_MAX`; release builds rely on earlier construction constraints or deserialization checks. Select hint correctness is critical because hints index into the rank LUT. `FindNthZeroBit` must mask padding bits in the last word so implicit zeros beyond `num_bits_` are not selectable. Elias-Fano assumes monotone input and uses assertions rather than runtime corruption errors in `BuildFrom`, so builder callers must validate ordering if data is untrusted.

## Test signals

No tests are in this file, but strong expected signals include round-trip encode/decode for empty and non-empty bitvectors, rank/select over boundary positions, zero selection in partial final words, move construction/assignment of owned data, Elias-Fano access across word-boundary low-bit packing, malformed input rejection, and alignment failure handling. Trie index seek and iteration tests should also exercise the hot rank/select paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/bitvector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/bitvector.h -->
# sources/storage-engines/rocksdb/utilities/trie_index/bitvector.h

## Purpose

`bitvector.h` declares the experimental trie-index succinct bitvector and Elias-Fano structures. `Bitvector` stores immutable bits with O(1) rank/select, next/previous set-bit search, and serialization support. `BitvectorBuilder` incrementally builds the bit stream. `EliasFano` compresses monotonically non-decreasing uint64 sequences while supporting O(1) random access.

## Important APIs, types, and functions

Constants `kBitsPerRankSample = 256`, `kWordsPerRankSample = 4`, and `kOnesPerSelectHint = 256` define lookup-table granularity. Utility functions include `Popcount`, `Ctz`, `CtzNonZero`, and `FindNthSetBitInWord`, with a BMI2/PDEP fast path on x86_64 when available and a portable popcount binary search fallback.

`BitvectorBuilder` exposes `Append`, `AppendWord`, `AppendMultiple`, `Reserve`, `GetBit`, `NumBits`, and `Words`. `Bitvector` deletes copy, implements move with pointer reseating, and exposes `InitFromData`, `EncodeTo`, `BuildFrom`, `GetBit`, `Rank1`, `Rank0`, `FindNthOneBit`, `FindNthZeroBit`, `NextSetBit`, `PrevSetBit`, `DistanceToNextSetBit`, `NumBits`, `NumOnes`, `NumZeros`, and `SerializedSize`. Private helpers build rank/select metadata and recompute internal pointers after moves.

`EliasFano` deletes copy, implements move with low-word pointer reseating, and exposes `BuildFrom`, `InitFromData`, `EncodeTo`, `Access`, `Count`, `Universe`, and `SerializedSize`.

## Control flow and state behavior

`BitvectorBuilder` appends bits LSB-first into uint64 words. `AppendMultiple` optimizes runs by filling a partial trailing word, appending full words, then appending a final partial word. `AppendWord` is for word-aligned bulk append, especially 256-bit dense-node label maps.

`Bitvector` has two ownership modes. `BuildFrom` allocates `owned_data_` and points `words_`, `rank_lut_`, and select hints into it. `InitFromData` points those raw pointers into external serialized memory, and the caller must keep that memory alive. Copying is deleted because raw pointers could dangle; moving is supported and reseats pointers into `owned_data_` when owned storage is non-empty. Rank uses a uint32 cumulative LUT at 256-bit boundaries plus unrolled popcount over up to three whole words and one partial word. Select uses hints to narrow to a small rank-sample range and scans words with popcount. Next/previous set-bit functions use trailing-zero and floor-log operations with sentinel `num_bits_` for not found.

`EliasFano` stores high bits as a `Bitvector` with one bits at `high[i] + i`, and low bits packed into uint64 words. `Access(i)` selects the i-th high one, subtracts `i` to recover the high part, extracts `low_bits_` bits from `low_words_`, handles cross-word extraction, and combines high and low. Like `Bitvector`, initialized-from-data instances point into external memory, while built instances own low-bit storage.

## Dependencies and integration points

The header depends on RocksDB portability/math helpers (`BitsSetToOne`, `CountTrailingZeroBits`, `FloorLog2`), `rocksdb::Slice`, `rocksdb::Status`, and standard vector/string storage. It is a foundational component for trie-index metadata, likely used by dense/sparse LOUDS trie structures for label bitmaps, child navigation, and compressed offsets.

## Risks and edge cases

Most API contracts are enforced with assertions, so callers must respect preconditions in release builds: positions must be in bounds, `AppendWord` must be word-aligned, Elias-Fano input must be monotone, and `Access` requires `i < count_`. External-memory initialization is lifetime-sensitive. `Rank1(pos)` permits `pos == num_bits_`, but relies on a sentinel rank sample and valid word access only when a partial word is present. `Access` includes an explicit guard against shifting by 64 when low bits start on a word boundary. The uint32 rank LUT limits bitvectors to `UINT32_MAX` bits, which the comments argue is far above realistic trie-index sizes.

## Test signals

Expected tests should cover builder append variants, rank and select at sample boundaries, all-ones/all-zeros vectors, partial final words, next/previous set-bit sentinel behavior, serialization round trips, move construction/assignment with small and large owned strings, external-buffer lifetime usage, and Elias-Fano empty, dense, sparse, duplicate, and word-crossing cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/bitvector.h -->
