# sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc lines 1-8839

Chunk: `subset-b-008719`
Source: `sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc`
Lines covered: 1-8839 of 10360

## Purpose

This chunk contains the first and largest part of RocksDB's transaction test suite for `TransactionDB`, especially the pessimistic transaction implementation. It is not production code; it is a dense regression harness that exercises transaction semantics across write policies (`WRITE_COMMITTED`, `WRITE_PREPARED`, `WRITE_UNPREPARED`), ordered vs. unordered write paths, stackable vs. base DB wrapping, optional two-write-queue behavior, and newer wide-column/secondary-index integrations.

The tests validate that transactions preserve read-your-own-writes behavior, key locking, snapshot validation, two-phase commit lifecycle, WAL recovery, prepared transaction log retention, iterator behavior over DB plus transaction-local deltas, savepoints, lock timeout/deadlock detection, duplicate key handling, commit-time batches, entity/wide-column APIs, coalescing/attribute-group iteration, WAL stall APIs, timestamp comparator restrictions, and secondary-index maintenance. Many cases use crash/reopen cycles and internal `DBImpl` test hooks, making this file a contract for storage-layer state transitions as much as a public API test.

The chunk begins with parameter instantiation and ends in the middle of `SecondaryIndexOnKey`; lines 8840-10360 are owned by `subset-b-008720`.

## Test Fixture And Parameterization

The file includes `transaction_test.h`, DB internals, public RocksDB APIs, secondary-index APIs, sync-point test hooks, transaction utility helpers, merge operators, and the pessimistic transaction DB implementation. The namespace is `ROCKSDB_NAMESPACE`.

Parameterized test suites are instantiated near the top:

- `TransactionTest` runs under `DBAsBaseDB` for non-stackable DB opens with combinations of two write queues, write policies, and write ordering.
- `TransactionStressTest` gets the same broad DB/write-policy coverage for heavier concurrent or long-running cases.
- `StackableDBAsBaseDB` runs a narrower set with the transaction DB stacked over a base DB.
- `MySQLStyleTransactionTest` is enabled outside normal valgrind runs, with an extra boolean parameter for slow-thread variants.

The parameter arrays are wrapped by `WRAP_PARAM_WITH_PER_KEY_POINT_LOCK_MANAGER_PARAMS`, so the same tests also exercise point-lock-manager variations. Several individual tests bypass unsupported combinations at runtime, especially write-unprepared iterator restrictions, write-committed-only wide-column/secondary-index features, blob direct-write path limitations, and two-write-queue-specific stalls.

## Important APIs, Types, And Test Helpers

Core public APIs exercised:

- `TransactionDB::Open`, `BeginTransaction`, `GetTransactionByName`, `GetAllPreparedTransactions`, `GetLockStatusData`, `GetDeadlockInfoBuffer`, `SetDeadlockInfoBufferSize`, `LockWAL`, `UnlockWAL`, `Write` with `TransactionDBWriteOptimizations`.
- `Transaction` methods: `Put`, `PutEntity`, `PutUntracked`, `Merge`, `MergeUntracked`, `Delete`, `DeleteUntracked`, `SingleDelete`, `Get`, `GetEntity`, `MultiGet`, `MultiGetEntity`, `GetForUpdate`, `GetEntityForUpdate`, `MultiGetForUpdate`, `GetIterator`, `GetCoalescingIterator`, `GetAttributeGroupIterator`, `SetSnapshot`, `SetSnapshotOnNextOperation`, `ClearSnapshot`, `SetSavePoint`, `RollbackToSavePoint`, `PopSavePoint`, `UndoGetForUpdate`, `Prepare`, `Commit`, `Rollback`, `SetName`, `GetCommitTimeWriteBatch`, `DisableIndexing`, `EnableIndexing`.
- DB-level operations used as implicit transactions or conflicting actors: `Put`, `PutEntity`, `Delete`, `SingleDelete`, `Merge`, `Write`, `Flush`, `FlushWAL`, `CompactRange`, `CreateColumnFamily`, `CreateColumnFamilyWithImport`, `DropColumnFamily`, `CreateColumnFamilies`, `DropColumnFamilies`, `WaitForCompact`.
- Iterator families: normal `Iterator`, `SecondaryIndexIterator`, `AttributeGroupIterator`, and entity/wide-column accessors such as `PinnableWideColumns` and `WideColumns`.

Internal and test-only integration points:

- `DBImpl` hooks such as `TEST_FlushMemTable`, `TEST_SwitchMemtable`, `TEST_SwitchWAL`, `TEST_FindMinLogContainingOutstandingPrep`, `TEST_FindMinPrepLogReferencedByMemTable`, `TEST_PreparedSectionCompletedSize`, `TEST_LogsWithPrepSize`, `TEST_GetLastVisibleSequence`, `TEST_GetCurrentLogNumber`, `TEST_IsLogGettingFlushed`, `TEST_UnableToReleaseOldestLog`, `PauseBackgroundWork`, `ContinueBackgroundWork`, mutex and write-controller test hooks.
- `PessimisticTransactionDB::TEST_Crash` to simulate process death while retaining files for recovery.
- `SyncPoint` dependencies/callbacks to force interleavings in lock waiting, flush, WAL stall, and write-thread code.
- `RandomTransactionInserter` from the test utilities for MySQL-style invariants.
- `Checkpoint::ExportColumnFamily` and `CreateColumnFamilyWithImport` for imported-column-family transaction writes.

Local helper type:

- `ThreeBytewiseComparator` compares only the first three bytes. It is used to verify duplicate-key detection respects non-default comparators rather than bytewise string identity.

Local nested secondary-index classes:

- `FooSecondaryIndex` in `SecondaryIndexPutEntity` indexes the `foo` wide column, mutates some primary values, emits errors for specific values, derives secondary key prefixes from the last byte, finalizes prefixes, and stores reversed previous-column values as secondary values.
- `KeySecondaryIndex` begins in `SecondaryIndexOnKey` and derives the secondary key prefix from the primary key by removing a three-byte prefix. The test continues in the next chunk.

## Control Flow And Behavioral Areas

### Basic Transaction API And Read-Your-Own-Writes

The early tests confirm the simplest transaction contracts:

- `SuccessTest` and `SuccessTestPinnable` verify `GetForUpdate`, local `Put`, `GetNumPuts`, `GetID`, commit visibility, and both string and `PinnableSlice` read APIs.
- `TxnOnlyTest` verifies transactions work in an otherwise empty DB.
- `DoubleEmptyWrite`, `TwoPhaseEmptyWriteTest`, and `EmptyTest` cover empty `WriteBatch` writes, empty 2PC transactions, empty commits/rollbacks, and read-only transactional commits.
- `WriteOptionsTest` confirms transaction write options are mutable via `SetWriteOptions` and returned by `GetWriteOptions`.
- `CommitWithoutPrepare` distinguishes `skip_prepare=false` returning `IsTxnNotPrepared` from `skip_prepare=true` allowing a direct commit.

### Iterator And Bounds Semantics

Several tests validate `WriteBatchWithIndex`/delta iterator behavior when transaction-local writes are merged with base DB state:

- `TestUpperBoundUponDeletion` and `TestTxnRespectBoundsInReadOption` ensure transaction iterators respect `iterate_lower_bound` and `iterate_upper_bound`, including deletion markers and forward/backward seeks.
- `IteratorTest` checks ordered traversal over committed data plus uncommitted puts/deletes, reverse navigation, seeks around deleted keys, and `GetForUpdate` validation when a key was modified after the transaction snapshot.
- `DisableIndexingTest` shows `DisableIndexing` hides subsequent local writes from transaction reads/iterators until indexing is re-enabled, while earlier indexed writes remain visible.
- `ReseekOptimization` creates many uncommitted entries before a snapshot to verify iterator reseek optimization does not loop indefinitely while skipping hidden prepared/unprepared versions.
- `CoalescingIterator` and `AttributeGroupIterator` cover newer multi-column-family merged iteration. They create two CFs with overlapping and disjoint keys, flush base DB values, add transaction-local values, and verify merged order and per-CF value selection. With `allow_unprepared_value=true`, they require `PrepareValue()` before values/attribute groups are materialized.
- `CoalescingIteratorSanityChecks` and `AttributeGroupIteratorSanityChecks` verify empty CF lists, mismatched comparators, invalid `io_activity`, and unsupported write policies surface `InvalidArgument` or `NotSupported` as appropriate.

### Locking, Conflicts, Deadlocks, And Timeouts

The suite heavily exercises the point lock manager and transaction conflict model:

- `WaitingTxn` validates `GetWaitingTxns`, lock-status introspection, per-CF lock records, perf-context lock wait counters, timeout status text, and post-timeout wait metadata.
- `SharedLocks` covers shared `GetForUpdate` locks, exclusive lock acquisition, upgrade/downgrade expectations, `UndoGetForUpdate`, and lock-status exclusivity flags.
- `DeadlockCycleShared`, `DeadlockCycle`, and `DeadlockStress` build explicit wait-for graphs with sync points and threads. They validate deadlock path contents, buffer ordering, depth-limit behavior, shared-vs-exclusive path metadata, buffer resizing, and high-contention randomized shared/exclusive lock acquisition.
- `WriteConflictTest`, `WriteConflictTest2`, `ReadConflictTest`, `FirstWriteTest`, `FirstWriteTest2`, `PredicateManyPreceders`, and `LostUpdate` establish snapshot validation rules for writes after snapshots, uncommitted locks, reads-for-update, first-sequence edge cases, and lost-update prevention.
- `AssumeExclusiveTracked` clarifies `do_validate` and `assume_tracked`: validation can be bypassed for reads, but the lock is still held; later write operations can assume the key is already exclusively tracked.
- `ValidateSnapshotTest` directly dynamic-casts to `PessimisticTransaction` and calls `ValidateSnapshot` after a prepared transaction commits across flush/history conditions.
- `UntrackedWrites` verifies untracked Put/Merge/Delete variants bypass snapshot conflict tracking but rollback correctly and do not permit later tracked writes to ignore conflicts.
- `ExpiredTransaction`, `TwoPhaseExpirationTest`, `ExpiredTransactionDataRace1`, and `TimeoutTest` cover expiration releasing locks, expired commit failures, db writes waiting for expiration, transaction lock timeout override behavior, and a race where expiration occurs after commit begins.
- `LockLimitTest` and `LockLimitWithTimeoutHangTest` enforce `max_num_locks`, same-key relocking, interaction with timeouts, and a regression where lock-limit plus expired timeout could spin forever.
- `Rollback`, `SavepointTest*`, `UndoGetForUpdateTest*`, and `ReinitializeTest` verify lock release and state reset for rollback, savepoints, popped savepoints, repeated transaction reuse via `BeginTransaction(..., old_txn)`, and manual undo of read locks.

### Two-Phase Commit, WAL, Recovery, And Persistence

The chunk is a major 2PC regression surface:

- `SimpleTwoPhaseTransactionTest`, `PersistentTwoPhaseTransactionTest`, `TwoPhaseRollbackTest`, `TwoPhaseNameTest`, `TwoPhaseDoubleRecoveryTest`, and `TwoPhaseSequenceTest` cover transaction naming, duplicate/invalid names, prepare/commit/rollback sequencing, prepared transaction lookup, durable recovery after crash/reopen, and committed value visibility.
- `CommitTimeBatchFailTest` and commit-time portions of `SimpleTwoPhaseTransactionTest`, `TwoPhaseEmptyWriteTest`, and `SwitchMemtableDuringPrepareAndCommit_WC` validate the special commit-time write batch. Non-empty commit-time batches are invalid unless the transaction is prepared with recovery-specific options. When enabled, commit-time writes survive flush and recovery.
- `LogMarkLeakTest`, `TwoPhaseLogRollingTest`, `TwoPhaseLogRollingTest2`, and `TwoPhaseLogMultiMemtableFlush` assert that WAL log numbers containing outstanding prepares are retained and released at the right time. They differentiate write-committed behavior, where memtables may reference prepare sections, from write-prepared/unprepared policies, where those references should be absent.
- `TwoPhaseOutOfOrderDelete` uses WAL-disabled writes between prepared and logged writes to verify recovery sequence-number accounting does not hide the final WAL-protected value.
- `TwoPhaseLongPrepareTest` keeps a prepared transaction open while many writes, crashes, and reopens happen, then commits the old prepared transaction and validates all data.
- `DoubleCrashInRecovery` corrupts a WAL in point-in-time recovery mode, reopens, optionally writes a later log, crashes/reopens again, and verifies the prepared transaction can still be recovered and committed.
- `DirectWriteCommitPath` validates blob direct-write transaction commit with direct I/O enabled, including post-flush reads.
- `LockWal`, `StallTwoWriteQueues`, and `UnlockWALStallCleared` verify the public WAL lock/stall APIs: prepares and commits should fail while WAL is locked, blocked primary/nonmem write queues should unblock after `UnlockWAL`, and `UnlockWAL` should wait for the stall it owns to be cleared while tolerating unrelated external stalls.

### Column Families, Imported CFs, Timestamp Comparators, And DB Options

Column-family interactions appear throughout:

- `ColumnFamiliesTest` and `ColumnFamiliesTest2` validate transactional writes, deletes, `SliceParts`, MultiGetForUpdate, dropped CF handling, and isolation of same key bytes across CFs.
- `WriteImportedColumnFamilyTest` exports a CF through checkpoint metadata, imports it into a new CF, and verifies transactional writes work against the imported CF.
- `ToggleAutoCompactionTest` opens multiple CFs with different `disable_auto_compactions` settings and confirms mutable CF options preserve the configured values under `TransactionDB::Open`.
- `OpenAndEnableU64Timestamp` allows timestamp-aware comparators only for write-committed transaction DBs; write-prepared/unprepared reject opening/creating such CFs through the transaction layer, even if the underlying `DBImpl` can create one.
- `OpenAndEnableU32Timestamp` rejects non-64-bit timestamp comparator use through transaction DB create/open paths.
- `WriteWithBulkCreatedColumnFamilies` verifies bulk CF creation and drop operations allow transactional DB writes to created handles.

### MultiGet, Merge, Duplicate Keys, And Write Optimizations

The chunk covers batched read/write details:

- `MultiGetBatchedTest`, `MultiGetLargeBatchedTest`, and `MultiGetSnapshot` validate transaction-local batch overlays for deletes, puts, and merges, including >`MultiGetContext::MAX_BATCH_SIZE` paths that force vector-backed autovectors and merge-context allocation. `MultiGetSnapshot` ensures prepared but uncommitted data is hidden from a snapshot taken between prepare and commit.
- `SingleDeleteTest` and `MergeTest` verify transaction read-your-own-writes for single-delete and merge operations and that locks prevent conflicting concurrent merges.
- `MergeOperandFilteringRespectsPublishedBoundary` checks compaction-filter merge operand filtering does not drop operands at/below the published boundary for WC/WP/WU snapshot contexts.
- `DeleteRangeSupportTest` documents that `DeleteRange()` is directly banned, while range deletions via `Write()` are only allowed with the correct `TransactionDBWriteOptimizations` promises. Write-committed needs skipped concurrency control; write-prepared/unprepared also need skipped duplicate-key checking.
- `Optimizations` iterates combinations of `skip_concurrency_control` and `skip_duplicate_key_check` to ensure basic writes remain correct.
- `DuplicateKeys` is a broad duplicate-key contract test. It covers duplicate keys in plain write batches, non-bytewise comparator equivalence, duplicate handling under prepare/rollback/commit-time batches, merge/delete/single-delete combinations, max-successive-merge interaction, savepoint rollback, and crash recovery of prepared duplicate-heavy transactions across default and non-default CFs.
- `MemoryLimitTest` sets a tiny `max_write_batch_size` with no flush threshold and expects the third put to fail with `IsMemoryLimit` without changing the tracked put count.
- `SeqAdvanceTest` uses helper methods from the fixture (`TestTxn0`...`TestTxn4` and `exp_seq`) to assert expected visible sequence-number advancement across transaction patterns, optional flushes, optional WAL flush/reopen branches, and repeated reopen cycles.

### Snapshot Lifecycle

Snapshot-related tests establish precise timing:

- `NoSnapshotTest` permits transactions without a snapshot to read the latest committed value and commit after a later transaction-local write.
- `MultipleSnapshotTest` repeatedly calls `SetSnapshot`, writes at different snapshots, reads through both transaction and DB views, and verifies a later transaction with an older snapshot sees a conflict.
- `DeferSnapshotTest`, `DeferSnapshotTest2`, `DeferSnapshotSavePointTest`, and `SetSnapshotOnNextOperationWithNotification` validate deferred snapshot creation. A plain `Get` does not necessarily instantiate the deferred snapshot, mutating or update-locking operations do, notifiers receive the created snapshot, and savepoint rollback restores deferred/real snapshot state.
- `ClearSnapshotTest` confirms clearing a snapshot returns reads to latest committed state.

### Wide Columns, Entities, Coalesced Attribute Groups

Wide-column/entity APIs are tested under write-committed only:

- `PutEntitySuccess` verifies `PutEntity`, `GetEntity`, `GetEntityForUpdate`, `GetNumPutEntities`, and commit visibility for `WideColumns`.
- `PutEntityWriteConflict` shows transaction-local entity writes are visible to transaction `GetEntity` and `MultiGetEntity`, block conflicting DB-level `PutEntity`, and become visible after commit.
- `PutEntityReadConflict` shows an entity read-for-update at a snapshot locks the key and blocks conflicting DB-level entity writes.
- `EntityReadSanityChecks` verifies invalid arguments for null CF handles, null result buffers, invalid `io_activity`, bad multiget arrays, and `GetEntityForUpdate` with `do_validate=false`.
- `PutEntityRecovery` prepares a transaction with a wide-column entity, reopens, fetches by name, commits, and verifies wide-column persistence.
- `CoalescingIterator` and `AttributeGroupIterator` then exercise entity/value materialization in merged multi-CF iteration, including lazy preparation under `allow_unprepared_value`.

### Secondary Indexes

Secondary-index tests appear at the end of this chunk and continue into the next chunk:

- `SecondaryIndexPutDelete` registers a `SimpleSecondaryIndex` on the default wide column, binds CF1 as primary and CF2 as secondary, writes default-CF and primary-CF records, verifies only eligible primary-CF records produce raw secondary entries, queries through `SecondaryIndexIterator`, updates values through implicit transactions, verifies stale secondary entries are removed/replaced, and finally deletes/single-deletes keys through explicit and implicit transactions to ensure both primary and secondary CFs are empty.
- `SecondaryIndexPutEntity` defines `FooSecondaryIndex` and tests the custom secondary-index callback contract. It verifies errors from `UpdatePrimaryColumnValue`, `GetSecondaryKeyPrefix`, `FinalizeSecondaryKeyPrefix`, and `GetSecondaryValue`; primary-value mutation from `"baz"` to `"quux"`; secondary key/value generation; forward/backward `SecondaryIndexIterator` navigation; and replacement/removal of index entries after DB-level `PutEntity` updates.
- `SecondaryIndexOnKey` starts at line 8772. In this chunk, it defines `KeySecondaryIndex`, which indexes the primary key after stripping a three-byte prefix and rejects too-short keys. The rest of the test's setup/assertions are outside this chunk.

## State And Persistence Behavior

The central persisted state under test is RocksDB key/value data, wide-column entities, WAL contents, prepared transaction metadata, commit-time write batches, and secondary-index entries. Tests deliberately vary when data is in active memtables, immutable memtables, flushed SSTs, WAL-only state, imported CF files, or recovered prepared transaction objects.

Important persistence contracts captured here:

- Prepared transactions are addressable by name after crash/reopen until commit or rollback unregisters them.
- WAL files containing outstanding prepares cannot be released; after commit they may still be retained by memtables in write-committed mode until relevant memtables flush.
- Write-prepared and write-unprepared policies use different visibility/recovery machinery and should not report memtable prepare-log references in places write-committed does.
- Commit-time write batches are only durable/replayable in the supported prepared-transaction mode and may differ across write policies.
- Crash recovery must preserve prepared transactions, duplicate-key semantics, wide-column `PutEntity` data, and valid logs after a point-in-time-corrupted WAL.
- Snapshot and last-visible-sequence behavior must remain stable across flushes, compactions, WAL flushes, and reopen cycles.
- Secondary-index maintenance is transactional: index CF entries are written, updated, and deleted atomically with primary CF changes.

## Dependencies And Integration Points

This file integrates with many subsystems:

- Transaction engine: pessimistic transactions, point locks, deadlock detector, lock manager, transaction name registry, savepoints, tracked/untracked keys, commit-time batches.
- DB core: write queues, write controller stalls, WAL lock/unlock, memtable switching/flushing, compaction, flush scheduling, WAL recovery modes, sequence-number visibility, column-family metadata.
- Storage formats: WriteBatch/WriteBatchWithIndex, merge operators, single-delete semantics, wide columns/entities, blob files/direct write, secondary index encoding.
- Test infrastructure: GoogleTest parameterization, `ROCKSDB_GTEST_BYPASS/SKIP`, `SyncPoint`, fault filesystem, random transaction inserter, mock/plain table factories, checkpoint export/import.
- Performance/context instrumentation: `get_perf_context()` lock wait counters and timing.

## Risks And Maintenance Notes

- Many assertions depend on internal implementation details (`TEST_*` hooks, log-number retention, write-policy-specific memtable references). Correct production changes can require updating these tests rather than preserving exact internals.
- Several tests are intentionally skipped for write-unprepared or non-write-committed policies. Adding support for iterators, entities, coalescing iterators, attribute-group iterators, or secondary indexes in those policies should revisit the bypasses.
- Long-running and threaded tests are gated from regular valgrind because they are expensive and timing-sensitive.
- Sync-point tests can become flaky if internal sync-point names or queue sequencing change without updating dependencies.
- `DuplicateKeys` encodes subtle comparator and duplicate-sub-batch assumptions; changes to WriteBatch duplicate detection, commit-time batch conflict semantics, or recovery replay order can break it.
- WAL and recovery tests mutate real test files and inject corruption; they depend on the fault filesystem and `ReOpenNoDelete` preserving files as expected.
- `SingleDelete` expectations mention undefined DB API behavior after overwrites; these tests document current behavior but are not general semantic guarantees.
- The chunk boundary splits `SecondaryIndexOnKey`, so whole-test conclusions for that case require `subset-b-008720`.

## Test Signals

High-value signals in this chunk:

- Status classes: `OK`, `InvalidArgument`, `NotFound`, `Busy`, `TimedOut`, `Deadlock`, `Expired`, `LockLimit`, `MemoryLimit`, `TxnNotPrepared`, `Incomplete`, `NotSupported`, `Corruption`, `Aborted`.
- Data assertions after commit/recovery verify exact values for regular keys, merged operands, wide-column sets, secondary-index keys/values, and absence after delete/single-delete.
- Lock assertions verify other transactions time out while keys are locked and later succeed after rollback/commit/undo/savepoint rollback.
- Deadlock assertions verify wait-for path shape, exclusivity, CF id, waiting key, timestamps, buffer capacity, and depth-limit metadata.
- WAL/log assertions verify min-log-to-keep, prepared-section heaps, memtable references, unable-to-release-oldest-log flags, and log flush requests.
- Iterator assertions verify seek/next/prev validity, bounded iteration, lazy value preparation, attribute groups, and secondary-index logical keys over raw encoded entries.
- Recovery assertions validate `GetTransactionByName`, `GetAllPreparedTransactions`, commit after crash, and stable data after reopen.

## Cross-Chunk References

This report covers lines 1-8839 only. The following work is visibly incomplete at the boundary and must be reconciled with `subset-b-008720`:

- `SecondaryIndexOnKey` begins at line 8772 and the `KeySecondaryIndex::GetSecondaryValue` method signature is cut off at line 8839. Its full setup, operations, and assertions are in the next chunk.
- The remaining tests listed by the source outline after line 8839 include transaction DB collapse-key behavior, WAL sync with pending prepare, and commit-bypass-memtable tests. They are intentionally not analyzed here except as file-level context for the later merge lane.
