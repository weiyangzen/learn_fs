# Research: subset-b-008717 RocksDB Transaction Utilities

This grouped report covers eight RocksDB transaction source files. Each section is source-tree aligned and wrapped for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_test.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_test.cc

## Purpose

This file is a GoogleTest suite for `OptimisticTransactionDB` and the common `Transaction` API when used with optimistic concurrency control. It exercises successful commits, write/read conflicts, snapshots, memtable-history validation, column-family behavior, savepoints, untracked writes, wide-column entity APIs, coalescing/attribute-group iterators, timestamped-snapshot unsupported paths, and parallel OCC validation lock bucket behavior.

The test fixture parameterizes every test over `OccValidationPolicy::kValidateSerial` and `OccValidationPolicy::kValidateParallel`, making the suite a regression net for both serial and bucket-locked parallel conflict validation.

## Important APIs, Types, And Functions

- `OptimisticTransactionTest` owns a temporary DB path, `Options`, `OptimisticTransactionDBOptions`, and `std::unique_ptr<OptimisticTransactionDB>`. Its `OpenImpl()` opens a default-column-family OCC DB and deletes the returned handle after the DB owns the default CF reference.
- `FlushTest2PopulateTxn()` is a helper that reads `foo` through a transaction snapshot, stages an update, and confirms read-your-own-write behavior before validation against flushed memtables.
- `OptimisticTransactionStressTestInserter()` drives `RandomTransactionInserter::OptimisticTransactionDBInsert()` from multiple threads and then relies on `RandomTransactionInserter::Verify()`.
- Test cases use the public transaction API heavily: `BeginTransaction()`, `GetForUpdate()`, `Put()`, `PutEntity()`, `Merge()`, `Delete()`, `SingleDelete`-adjacent delete paths, `PutUntracked()`, `MergeUntracked()`, `DeleteUntracked()`, `PutEntityUntracked()`, `Commit()`, `Rollback()`, `SetSnapshot()`, `SetSavePoint()`, `RollbackToSavePoint()`, `UndoGetForUpdate()`, `MultiGetForUpdate()`, `GetEntity()`, `GetEntityForUpdate()`, `MultiGetEntity()`, `GetIterator()`, `GetCoalescingIterator()`, and `GetAttributeGroupIterator()`.
- The suite also touches lower-level integration points such as `DBImpl::DeleteRange()`, `DBImpl::TEST_SwitchMemtable()`, `SyncPoint`, `PerfContext`, `MakeSharedOccLockBuckets()`, and `CacheAlignedWrapper<port::Mutex>`.

## Control Flow And Behavior

The early conflict tests establish the optimistic transaction contract: keys are tracked during transactional reads/writes and validated only at commit. External writes to tracked keys after a transaction snapshot produce `Status::Busy()` and leave DB state unchanged by the failed transaction. Without a snapshot, `NoSnapshotTest` shows that a transaction may observe the latest value after transaction start and then commit because the tracked sequence boundary is taken at the lock/validation point rather than at begin time.

Snapshot tests exercise multiple snapshot boundaries in one transaction. `MultipleSnapshotTest` stages writes to `AAA`, `BBB`, and `CCC` after different snapshot moments, then validates that each key's conflict boundary follows the snapshot active when it was tracked. It also shows an older snapshot in another transaction conflicting with a later committed write.

Flush and memtable-history tests cover `TransactionUtil::CheckKey` behavior. `FlushTest` confirms validation can still succeed when the relevant memtable has flushed but remains in history. `FlushTest2` forces enough flushes to purge history, expects `Status::TryAgain()`, then demonstrates rollback and replay as a recovery path. `CheckKeySkipOldMemtable` checks both history and immutable memtable paths, uses perf counters to assert the number of memtables examined, and verifies old memtables can be skipped safely without missing conflicts.

Column-family coverage confirms key identity includes CF identity. Writes to identical user keys in different CFs do not conflict, while writes in the same CF do. It also validates `SliceParts` keys/values, multi-CF `MultiGetForUpdate()`, dropped CF failure behavior, and, under parallel validation, that shared OCC lock buckets share pointer space across DB/CF combinations while distinct buckets do not.

Iterator tests validate that transaction-local `WriteBatchWithIndex` overlays DB iterators correctly. `IteratorTest` checks regular iterator ordering, seek behavior, deleted keys, and subsequent conflict detection on a key changed after the snapshot. The coalescing and attribute-group iterator tests validate multi-CF merge views and lazy value preparation when `ReadOptions::allow_unprepared_value` is true. Their sanity tests reject empty CF sets, mismatched comparators, and invalid `io_activity`.

Wide-column tests cover entity reads/writes through transaction overlays. They verify successful `PutEntity`, conflicts against outside direct `PutEntity`, conflicts against another transaction's `PutEntity`, read conflicts via `GetEntityForUpdate`, and invalid-argument handling for null CFs/results and inappropriate `ReadOptions::io_activity`.

## State And Persistence Behavior

The file verifies that failed optimistic commits are atomic: staged tracked and untracked writes do not leak to the DB if conflict validation fails. It explicitly tests rollback of untracked writes and the case where an untracked key is modified externally but should not prevent commit unless a tracked key conflicts.

The sequence-number recovery tests commit transactions, reopen the DB, and commit more transactions to guard against sequence-number regressions after recovery, including a large-value/64-key variant skipped under TSAN due to lock limits.

Timestamped snapshot tests establish that optimistic transactions do not support `CommitAndTryCreateSnapshot()`: missing commit timestamps produce `InvalidArgument`, and an explicit timestamp returns `NotSupported`.

## Dependencies And Integration Points

The tests depend on RocksDB internals and test utilities: `db/db_impl/db_impl.h`, `db/db_test_util.h`, `rocksdb/utilities/optimistic_transaction_db.h`, `rocksdb/utilities/transaction.h`, `test_util/sync_point.h`, `test_util/transaction_test_util.h`, `perf_context`, CRC/hash helpers, and `RandomTransactionInserter`.

The test suite is both API-level and implementation-sensitive. It checks public API status codes and values, but also asserts memtable count behavior, lock bucket pointer reuse, cache-aligned bucket memory usage, and flush scheduling through sync points.

## Risks And Edge Cases

- Memtable history retention is a correctness boundary. If history is purged, commit returns `TryAgain`; callers must retry transaction logic rather than blindly retry commit.
- Parallel validation relies on deterministic lock bucket hashing and shared bucket lifetimes. Pointer-space assertions can expose accidental bucket reallocation or loss of sharing.
- Column family drops between transaction tracking and commit must fail safely, without dereferencing invalid handles.
- Untracked operations still write atomically with the transaction batch but intentionally skip conflict tracking; misuse can allow application-level lost updates.
- Entity and multi-CF iterator APIs have stricter argument/CF/comparator requirements than simple key-value paths.

## Test Signals

This file is itself the test signal. It spans unit, integration, concurrency, recovery, and stress coverage for optimistic transactions. Its instantiation over serial and parallel validation makes regressions in either validation lane visible. The stress test uses four threads with 10,000 transactions per thread over a constrained key space, then verifies aggregate consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.cc

## Purpose

This file implements the core pessimistic transaction state machine and the `WriteCommittedTxn` concrete transaction policy. It handles transaction ID generation, lock acquisition and release, snapshot validation, timestamp validation, prepare/commit/rollback transitions, lock stealing for expired transactions, commit-time timestamp application, and write-batch persistence through `DBImpl::WriteImpl()`.

## Important APIs, Types, And Functions

- `PessimisticTransaction::GenTxnID()` returns an atomic increasing transaction ID unless the range-lock manager uses the transaction object's address as ID.
- `PessimisticTransaction::Initialize()` maps `TransactionOptions` into runtime state: lock timeouts, deadlock detection, expiration, snapshots, write-batch byte limits, skip-concurrency-control, skip-prepare, and commit-bypass-memtable thresholds.
- `PessimisticTransaction::{Prepare,Commit,CommitBatch,Rollback,RollbackToSavePoint,SetName}` implement state transitions around `STARTED`, `AWAITING_PREPARE`, `PREPARED`, `AWAITING_COMMIT`, `COMMITTED`, `AWAITING_ROLLBACK`, `ROLLEDBACK`, and `LOCKS_STOLEN`.
- `PessimisticTransaction::TryLock()` is the central point-lock path. It handles already-tracked keys, lock upgrades, snapshot validation, timestamp-aware validation, and lock tracking.
- `PessimisticTransaction::ValidateSnapshot()` delegates conflict detection to `TransactionUtil::CheckKeyForConflicts()`.
- `PessimisticTransaction::LockBatch()` extracts keys from a raw `WriteBatch`, sorts by CF and key, locks them in deterministic order, and returns a lock tracker for cleanup.
- `WriteCommittedTxn::GetForUpdateImpl()` and `GetEntityForUpdate()` add user-timestamp validation on top of base transactional reads.
- `WriteCommittedTxn::Operate()` is the shared write wrapper for put/entity/delete/single-delete/merge and their untracked variants.
- `WriteCommittedTxn::{PrepareInternal,CommitWithoutPrepareInternal,CommitBatchInternal,CommitInternal,RollbackInternal}` provide write-committed persistence details.

## Control Flow And State Transitions

Construction initializes the `TransactionBaseImpl` base with the root DB and the DB's lock tracker factory, then sets `txn_db_impl_` and `db_impl_`. `Initialize()` assigns the transaction ID, sets state to `STARTED`, configures timeout/deadlock/snapshot/write-batch options, inserts expirable transactions into the DB map, and resets read/commit timestamps to `kMaxTxnTimestamp`.

Destruction always unlocks tracked locks, removes expirable transactions, and unregisters named transactions that have not committed. `Clear()` similarly unlocks and then clears base transaction state. Reinitialization unregisters any old named in-flight transaction, reinitializes the base, and re-runs option setup for transaction reuse.

`Prepare()` requires a name, rejects expired transactions, atomically moves expirable transactions from `STARTED` to `AWAITING_PREPARE`, disables future expiration by clearing `expiration_time_`, calls `PrepareInternal()`, and stores `PREPARED` on success. Write-committed prepare appends an end-prepare marker, writes WAL only with memtable disabled, and marks the WAL log as containing a prepare section through a pre-release callback.

`Commit()` has two major paths. A transaction in `STARTED` may commit without prepare only when expirable compare/exchange succeeds or `skip_prepare_` is true; otherwise it returns `TxnNotPrepared`. A `PREPARED` transaction commits through `CommitInternal()`. Successful commits unregister the transaction name, clear locks and batches, mark prepare logs flushed when applicable, and set `COMMITTED`. If commit marker writing fails for a prepared transaction, the state is restored to `PREPARED` so rollback or retry remains possible.

`CommitBatch()` is used for direct `TransactionDB::Write()` wrapping. It rejects batches that already contain user timestamps, locks all keys in sorted order, validates expiration/state, calls `CommitBatchInternal()`, marks `COMMITTED` on success, and unlocks temporary batch locks.

`Rollback()` writes a rollback marker only for prepared or write-unprepared-started transactions with a log number. It clears started transactions directly, preserves `PREPARED` if rollback marker writing fails, and rejects committed transactions.

## Timestamp And Snapshot Behavior

`WriteCommittedTxn` supports user timestamp validation only when `TransactionDBOptions::enable_udt_validation` is enabled. `SanityCheckReadTimestamp()` rejects inconsistent combinations such as validation disabled with a read timestamp, `do_validate=false` with a read timestamp, or validation requested without a read timestamp.

For timestamped column families, `GetForUpdateImpl()` injects the transaction read timestamp into `ReadOptions` when the caller did not provide one, or verifies the caller's timestamp matches `read_timestamp_`. Write operations with timestamp-aware CFs call `TryLock()` before appending to the batch; if indexing is disabled, the CF ID is recorded so commit can later determine timestamp size.

`SetReadTimestampForValidation()` prevents decreasing the read timestamp. `SetCommitTimestamp()` rejects commit timestamps less than or equal to the read timestamp when UDT validation is enabled. `CommitWithoutPrepareInternal()` and `CommitInternal()` require a commit timestamp if the write batch has timestamped keys, update all batch timestamps, and can create a timestamped snapshot through `SnapshotCreationCallback` when `CommitAndTryCreateSnapshot()` requested one.

Snapshot validation happens after lock acquisition. If a key was already validated/locked at a sequence not newer than the active snapshot, validation is skipped; otherwise `TransactionUtil::CheckKeyForConflicts()` checks DB/memtable history with optional timestamp data.

## Persistence Behavior

Write-committed transactions persist prepared state by writing prepare markers to WAL with memtable disabled. Committed prepared transactions write a commit-time batch containing a commit marker and, unless bypass optimization is selected, append the prepared data batch so memtables contain committed data in normal mode.

Large prepared commits can bypass normal memtable insertion when operation count or byte thresholds are met, the `WriteBatchWithIndex` operation count matches the raw batch count, timestamps are not needed, and blob direct-write CFs are absent. The bypass path passes the `WriteBatchWithIndex` into `DBImpl::WriteImpl()` for ingestion and resets `write_batch_` afterward for cleanup/reuse safety.

`CommitWithoutPrepareInternal()` writes the transaction's batch directly through `DBImpl::WriteImpl()` and sets the transaction ID to the used sequence number. `RollbackInternal()` writes a rollback marker batch.

## Dependencies And Integration Points

This file depends on `DBImpl`, column-family/comparator APIs, WAL log prepare tracking, `WriteBatchInternal`, `WriteBatchWithIndexInternal`, `TransactionUtil`, `PessimisticTransactionDB`, `SnapshotCreationCallback`, `SyncPoint`, and RocksDB logging/stats. It is tightly integrated with lock-manager abstractions through `PessimisticTransactionDB::{TryLock,TryRangeLock,UnLock}` and with transaction recovery through prepare/commit/rollback markers.

## Risks And Edge Cases

- State transitions for expirable transactions use atomics because locks may be stolen concurrently after expiration.
- Lock upgrades must downgrade or unlock correctly if snapshot validation fails.
- `assume_tracked` is only valid when the lock tracker already has an equivalent lock; debug assertions enforce this.
- Timestamped commits require accurate timestamp-size discovery even when writes bypass `WriteBatchWithIndex` indexing.
- Commit-bypass optimization must avoid timestamped writes, mismatched WBWI/raw counts, and blob direct writes.
- Failed commit marker writes for prepared transactions are intentionally recoverable; changing that behavior can strand transactions.

## Test Signals

The nearby optimistic and timestamped snapshot tests indirectly cover shared base APIs, commit snapshot behavior, and timestamp rejection/acceptance. Broader transaction tests outside this item are expected to cover pessimistic locking, prepare/commit/rollback, expiration, deadlock, and recovery behavior. This implementation includes `TEST_SYNC_POINT` hooks for expirable commit races and bypass-memtable commit testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.h -->
# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.h

## Purpose

This header declares the pessimistic transaction implementation classes used by `TransactionDB`: abstract `PessimisticTransaction` and concrete `WriteCommittedTxn`. It defines the transaction-facing locking, state, timeout, naming, timestamp, and persistence interfaces implemented in `pessimistic_transaction.cc`.

## Important APIs, Types, And Members

`PessimisticTransaction` derives from `TransactionBaseImpl` and exposes:

- Lifecycle and reuse: constructor, destructor, `Reinitialize()`, `Clear()`.
- Transaction operations: `Prepare()`, `Commit()`, `CommitBatch()`, `Rollback()`, `RollbackToSavePoint()`, `SetName()`.
- Lock/deadlock observability: `GetID()`, `GetWaitingTxns()`, `SetWaitingTxn()`, `ClearWaitingTxn()`, `GetLockTimeout()`, `SetLockTimeout()`, `GetDeadlockTimeout()`, `SetDeadlockTimeout()`, `IsDeadlockDetect()`, `GetDeadlockDetectDepth()`.
- Expiration behavior: `GetExpirationTime()`, `IsExpired()`, `TryStealingLocks()`.
- Range/key helpers: `GetRangeLock()` and `CollapseKey()`.
- Protected abstract persistence hooks: `PrepareInternal()`, `CommitWithoutPrepareInternal()`, `CommitBatchInternal()`, `CommitInternal()`, `RollbackInternal()`.
- Protected lock helpers: `LockBatch()`, `TryLock()`, `ValidateSnapshot()`, and `UnlockGetForUpdate()`.

Key state members include `txn_db_impl_`, `db_impl_`, `expiration_time_`, `read_timestamp_`, `commit_timestamp_`, commit-bypass thresholds, `txn_id_`, waiting transaction metadata, lock/deadlock timeouts, `deadlock_detect_`, `deadlock_detect_depth_`, and `skip_concurrency_control_`.

`WriteCommittedTxn` derives from `PessimisticTransaction` and overrides:

- `GetForUpdate()` overloads for strings and pinnable values.
- `GetEntityForUpdate()`.
- `Put()`, `PutUntracked()`, `PutEntity()`, `PutEntityUntracked()`, `Delete()`, `DeleteUntracked()`, `SingleDelete()`, `SingleDeleteUntracked()`, and `Merge()`.
- Timestamp APIs `SetReadTimestampForValidation()`, `SetCommitTimestamp()`, and `GetCommitTimestamp()`.
- The protected persistence hooks for write-committed prepare/commit/rollback.

It also owns `cfs_with_ts_tracked_when_indexing_disabled_`, needed to infer timestamp sizes for CFs written while write-batch indexing is disabled.

## Control Flow And Design

The class split makes `PessimisticTransaction` responsible for concurrency-control mechanics and transaction state, while subclasses decide how prepared and committed data are represented in RocksDB. The abstract hooks allow write-committed, write-prepared, and write-unprepared implementations to share locking and API behavior but persist different marker/data layouts.

Waiting-transaction methods are guarded by `wait_mutex_` and intentionally copy IDs/keys for diagnostic APIs such as deadlock reporting. `timed_out_key_` stores a stable key string for post-timeout inspection, while `waiting_key_` may be a borrowed pointer only valid during lock-manager wait.

`TryLock()` and `ValidateSnapshot()` are private/protected because all public operations should go through higher-level read/write methods that can maintain batch counts, lock trackers, and savepoint state.

## State And Persistence Behavior

The header shows which transaction state is in memory only versus persisted through hooks. Transaction IDs, lock timeout/deadlock fields, expiration, waiting metadata, timestamps, and lock trackers are in-memory runtime state. Prepared/commit/rollback durability is delegated through `PrepareInternal()`, `CommitInternal()`, `CommitWithoutPrepareInternal()`, and `RollbackInternal()`, which write markers/batches through `DBImpl`.

`read_timestamp_` and `commit_timestamp_` default to `kMaxTxnTimestamp`, meaning unset. `use_only_the_last_commit_time_batch_for_recovery_`, `skip_prepare_`, and commit-bypass thresholds mirror `TransactionOptions` and shape recovery/commit behavior in the implementation.

## Dependencies And Integration Points

The header depends on RocksDB public transaction APIs (`rocksdb/utilities/transaction.h`, `transaction_db.h`, `write_batch_with_index.h`), DB/write callback types, snapshots, statuses, autovectors, and internal transaction helpers (`transaction_base.h`, `transaction_util.h`). It forward-declares `PessimisticTransactionDB` to avoid a cyclic include while still storing a DB implementation pointer.

The friend test declaration and virtual hooks indicate tight coupling with RocksDB transaction tests and alternative transaction DB subclasses.

## Risks And Edge Cases

- Waiting-key lifetime is subtle: `waiting_key_` is borrowed, while `timed_out_key_` owns a copy.
- Range lock managers may use transaction object addresses as IDs, so code must not assume IDs are always generated by the atomic counter.
- `SetLockTimeout()` and `SetDeadlockTimeout()` convert milliseconds to microseconds; callers must use API units correctly.
- Timestamped CF support is limited to `WriteCommittedTxn` in the surrounding DB code.
- Skipping concurrency control is a powerful option intended for recovery or trusted paths, not general concurrent use.

## Test Signals

The API declared here is exercised by transaction tests across the RocksDB transaction utility suite. In this subset, `optimistic_transaction_test.cc` exercises shared base APIs and timestamped-snapshot unsupported behavior, while `timestamped_snapshot_test.cc` validates commit timestamp snapshot behavior through `Transaction` APIs implemented for pessimistic write-committed transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.cc

## Purpose

This file implements `PessimisticTransactionDB` and `WriteCommittedTxnDB`, the stackable DB layer that wraps `DBImpl` with transaction support. It validates transaction DB options and column-family timestamp support, prepares DB open options for two-phase commit, constructs the right transaction DB subclass for each write policy, coordinates lock-manager column-family state, wraps direct writes in internal transactions, tracks expirable/named/prepared transactions, and exposes timestamped snapshot operations.

## Important APIs And Functions

- Constructors accept either `DB*` or `StackableDB*`, resolve `DBImpl`, store `TransactionDBOptions`, and create a `LockManager`.
- `Initialize()` registers CFs with the lock manager, validates CF options, re-enables compaction, enables published-sequence tracking for write-committed, and rebuilds recovered prepared transactions.
- `VerifyCFOptions()` ensures timestamped comparators use `sizeof(TxnTimestamp)` and are only used with `WRITE_COMMITTED`.
- `TransactionDB::Open()` overloads prepare column-family and DB options, open `DBImpl`, then wrap it through `WrapDB()`.
- `TransactionDB::PrepareWrap()` enables memtable history, temporarily disables auto compaction during open, and sets `allow_2pc`.
- `WrapAnotherDBInternal()` chooses `WriteUnpreparedTxnDB`, `WritePreparedTxnDB`, or `WriteCommittedTxnDB` based on `write_policy`.
- CF lifecycle methods call the underlying DB and mirror add/remove/update into the lock manager and comparator maps.
- Direct write methods `Put`, `PutEntity`, `Delete`, `SingleDelete`, `Merge`, and `Write` wrap writes in internal transactions unless an optimization explicitly skips concurrency control.
- Expirable/named/prepared tracking methods manage maps guarded by mutexes.
- Timestamp snapshot methods delegate to `DBImpl::{CreateTimestampedSnapshot,GetTimestampedSnapshot,ReleaseTimestampedSnapshotsOlderThan,GetTimestampedSnapshots}`.
- `SnapshotCreationCallback::operator()` creates a timestamped snapshot after memtable insertion during commit.

## Control Flow

Open starts by rejecting incompatible write policies and unordered-write combinations. It copies column-family descriptors, calls `PrepareWrap()` to ensure memtable history and two-phase-commit prerequisites, then opens `DBImpl` with policy-specific `seq_per_batch` and `batch_per_txn` flags. On success it logs the write policy and wraps the DB in the selected transaction DB subclass.

Initialization first adds all column families to the lock manager and validates every CF descriptor. It then re-enables compaction for CFs that were originally enabled. Recovered shell transactions from `DBImpl::recovered_transactions()` are converted into real transaction objects with sync writes and `skip_concurrency_control=true`, are assigned log numbers and names, rebuilt from the recovered write batch, and set to `PREPARED`. If rebuilding succeeds, shell transactions are deleted from `DBImpl`.

Direct non-transactional writes are intercepted so they still participate in locking. Single-key operations create an internal transaction, disable indexing, call the corresponding untracked operation, commit, and delete the transaction. `Write()` uses `WriteWithConcurrencyControl()`, which updates protection info if needed, disables indexing, locks all batch keys through `CommitBatch()`, and relies on sorted lock ordering to avoid deadlocks among direct `Write()` calls.

`WriteCommittedTxnDB::Write()` rejects timestamped batches because user timestamps must go through the transaction API, then either writes directly when DB/options allow `skip_concurrency_control` or delegates to the locking wrapper.

## State And Persistence Behavior

`PessimisticTransactionDB` owns in-memory state around durable transaction data: `lock_manager_`, `column_family_mutex_`, `expirable_transactions_map_`, `transactions_`, and DB option/logger references. Prepared transaction durability lives in WAL/recovery records owned by `DBImpl`; this wrapper reconstructs live transaction objects from those records on open.

The destructor deletes entries from `transactions_`, which represent named in-flight or prepared transactions. A TODO notes this approach is unsafe/unclear because deletion is expected to remove entries as a side effect.

Timestamped snapshots are managed as shared snapshots inside `DBImpl`. `CreateTimestampedSnapshot()` rejects `kMaxTxnTimestamp`, and commit-time snapshot creation happens via `SnapshotCreationCallback` so the snapshot sequence matches the commit sequence used by `WriteImpl()`.

## Dependencies And Integration Points

This file depends on `DBImpl`, `TransactionDBMutexFactory`, lock managers, write-prepared/write-unprepared transaction DBs, `SecondaryIndexMixin`, `WriteBatchInternal`, logging, mutex utilities, and test sync points. It is the bridge between public `TransactionDB` APIs and lower-level DB, WAL, memtable, column-family, and snapshot machinery.

It also updates comparator maps through virtual hooks so write-prepared/write-unprepared subclasses can maintain timestamp/comparator metadata without imposing base-class fast-path overhead.

## Risks And Edge Cases

- Open-time option changes are correctness requirements: no memtable history means conflict validation can fail with `TryAgain`, and no `allow_2pc` means marker recovery cannot work.
- Timestamped CFs are only supported for write-committed transactions; direct DB writes to timestamped CFs are rejected.
- `skip_concurrency_control` bypasses all transaction locking and must be used only when external serialization is guaranteed.
- Recovered transactions skip concurrency control to avoid deadlocks with WAL-originated keys and rely on application recovery discipline.
- Dropping/creating CFs requires `column_family_mutex_` to keep lock-manager maps in sync with DB state.
- The destructor's transaction-map deletion TODO is a real ownership-risk signal.

## Test Signals

`timestamped_snapshot_test.cc` exercises commit-time and explicit timestamped snapshot APIs implemented here. The optimistic test's column-family and iterator cases exercise analogous transaction DB wrapper expectations. Broader RocksDB transaction tests cover open/recovery, prepared transactions, direct-write locking, CF lifecycle, and lock-manager behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.h -->
# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.h

## Purpose

This header declares the pessimistic transaction DB wrapper classes and the commit-time snapshot callback. It defines the interface between public `TransactionDB` operations, lock-manager coordination, transaction object creation/reuse, column-family lifecycle, recovery tracking, and timestamped snapshot management.

## Important APIs, Types, And Members

`PessimisticTransactionDB` derives from `TransactionDB` and declares:

- Opening/initialization support: constructors, destructor, `Initialize()`, `ValidateTxnDBOptions()`, `VerifyCFOptions()`, and protected `ReinitializeTransaction()`.
- Transaction creation: pure virtual `BeginTransaction()` and private `BeginInternalTransaction()`.
- Direct write overrides: `Put()`, `PutEntity()`, `Delete()`, `SingleDelete()`, `Merge()`, `Write()`, and inline `WriteWithConcurrencyControl()`.
- Column-family lifecycle: `CreateColumnFamily`, `CreateColumnFamilies`, `CreateColumnFamilyWithImport`, `DropColumnFamily`, `DropColumnFamilies`, and `AddColumnFamily()`.
- Lock-manager facade: `TryLock()`, `TryRangeLock()`, `UnLock()` overloads, `GetLockStatusData()`, `GetDeadlockInfoBuffer()`, `SetDeadlockInfoBufferSize()`, and `GetLockTrackerFactory()`.
- Transaction maps: `InsertExpirableTransaction()`, `RemoveExpirableTransaction()`, `TryStealingExpiredTransactionLocks()`, `GetTransactionByName()`, `RegisterTransaction()`, `UnregisterTransaction()`, and `GetAllPreparedTransactions()`.
- Timestamped snapshots: `CreateTimestampedSnapshot()`, `GetTimestampedSnapshot()`, `ReleaseTimestampedSnapshotsOlderThan()`, and `GetTimestampedSnapshots()`.
- Timestamp rejection helpers: `FailIfBatchHasTs()` and `FailIfCfEnablesTs()`.

State members include `DBImpl* db_impl_`, `info_log_`, immutable `txn_db_options_`, `lock_manager_`, `column_family_mutex_`, `map_mutex_`/`expirable_transactions_map_`, and `name_map_mutex_`/`transactions_`.

`WriteCommittedTxnDB` overrides `BeginTransaction()` and `Write()` methods for write-committed policy, including the optimization-aware `Write()` overload.

`SnapshotCreationCallback` derives from `PostMemTableCallback` and carries `DBImpl`, commit timestamp, optional notifier, and output snapshot reference.

## Control Flow And Design

The header sets `PessimisticTransactionDB` as the common base for all pessimistic write policies. It owns concurrency-control infrastructure and delegates policy-specific transaction objects to subclasses. `WriteCommittedTxnDB` creates either a plain `WriteCommittedTxn` or a `SecondaryIndexMixin<WriteCommittedTxn>` depending on configured secondary indices.

The inline `WriteWithConcurrencyControl()` shows direct-write wrapping: update protection bytes, begin an internal transaction, disable indexing, call `CommitBatch()` so keys are locked in sorted order, then delete the temporary transaction. This keeps direct DB writes from racing with explicit transactions.

The timestamp helper methods document a policy boundary: timestamped writes cannot bypass transaction APIs. Direct batches containing timestamped keys and direct operations against timestamp-enabled CFs return `NotSupported`.

## State And Persistence Behavior

Most members are in-memory coordination structures around persistent RocksDB state. The lock manager tracks held locks; transaction maps track expirable and named/prepared transactions; `DBImpl` owns WAL/memtable/snapshot persistence. `GetAllPreparedTransactions()` is marked not thread-safe and intended for recovery when a single thread is active.

`SnapshotCreationCallback` persists no data by itself; it runs after memtable work and asks `DBImpl` to create a timestamped snapshot associated with the commit sequence and timestamp.

## Dependencies And Integration Points

The header integrates public `rocksdb/db.h`, `rocksdb/options.h`, `rocksdb/utilities/transaction_db.h` with internal `db_iter`, `read_callback`, `snapshot_checker`, point/range lock managers, `pessimistic_transaction.h`, and write-prepared transaction types. It also exposes virtual comparator-map update hooks used by subclasses that need CF comparator metadata.

Friend declarations show integration with write-prepared/write-unprepared internals and many recovery/crash tests.

## Risks And Edge Cases

- The direct write wrapper creates temporary transactions; correctness depends on `CommitBatch()` locking every relevant key and unlocking on all paths.
- The inline timestamp rejection helpers must stay consistent with timestamp support in `WriteCommittedTxn`.
- `GetAllPreparedTransactions()` is explicitly not thread-safe.
- `TEST_Crash()` is a virtual hook to relax assertions in crash tests; misuse outside tests could hide invariants.
- Lock-manager state must be updated for every CF add/drop/import path to avoid stale lock maps.

## Test Signals

Timestamp snapshot tests use the APIs declared here. Transaction DB tests elsewhere exercise the policy-specific open path, recovery, direct write wrapping, lock-status/deadlock APIs, timestamp rejection helpers, and CF lifecycle. The header's extensive friend test list indicates known coverage for recovery and crash scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/snapshot_checker.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/snapshot_checker.cc

## Purpose

This small implementation file provides snapshot-membership helpers used by RocksDB's transaction-aware snapshot and garbage-collection logic. It implements the write-prepared snapshot checker adapter, a singleton checker that disables GC, and fast predicates for determining whether a sequence number is definitely in or definitely not in a snapshot.

## Important APIs And Functions

- `WritePreparedSnapshotChecker::WritePreparedSnapshotChecker(WritePreparedTxnDB*)` stores the transaction DB pointer used for membership checks.
- `WritePreparedSnapshotChecker::CheckInSnapshot(sequence, snapshot_sequence)` calls `WritePreparedTxnDB::IsInSnapshot()` with `kMinUnCommittedSeq`, reports `kSnapshotReleased` if the snapshot was released, and otherwise returns `kInSnapshot` or `kNotInSnapshot`.
- `DisableGCSnapshotChecker::Instance()` returns a static singleton using `STATIC_AVOID_DESTRUCTION`.
- `DataIsDefinitelyInSnapshot(seqno, snapshot, snapshot_checker)` returns true when `seqno <= snapshot` and either no checker is needed or the checker confirms membership.
- `DataIsDefinitelyNotInSnapshot(seqno, snapshot, snapshot_checker)` returns true when `seqno > snapshot` or an available checker explicitly says the data is not in the snapshot.

## Control Flow And Behavior

The write-prepared checker is an adapter around `WritePreparedTxnDB::IsInSnapshot()`. It accounts for write-prepared transactions where sequence-number order alone is insufficient because prepared-but-uncommitted or delayed-commit records can appear around a snapshot boundary.

The two free predicates provide fast-path sequence comparisons with optional checker refinement. `LIKELY` and `UNLIKELY` annotations bias the branch predictor toward ordinary inclusion and away from explicit not-in-snapshot checker results.

## State And Persistence Behavior

The file has no durable state. `WritePreparedSnapshotChecker` holds a raw pointer to its owning/associated transaction DB. `DisableGCSnapshotChecker::Instance()` owns a process-lifetime singleton. Membership decisions reflect transaction state maintained elsewhere by `WritePreparedTxnDB`.

## Dependencies And Integration Points

It depends on `db/snapshot_checker.h`, branch prediction/static lifetime helpers from `port/lang.h`, and `utilities/transactions/write_prepared_txn_db.h`. The functions are used by DB iterators, compaction, flush, and transaction conflict paths that need to decide snapshot visibility under transaction-aware write policies.

## Risks And Edge Cases

- The TODO around `min_uncommitted` means the checker currently passes `kMinUnCommittedSeq`; changes to write-prepared visibility rules may need a more precise minimum uncommitted sequence.
- A released snapshot is distinct from simply not-in-snapshot and is propagated as `kSnapshotReleased`.
- Raw `txn_db_` lifetime must exceed checker use.
- The free predicates only return "definitely" answers; callers must handle inconclusive cases outside these helpers.

## Test Signals

Coverage is likely indirect through write-prepared transaction visibility, compaction, recovery, and snapshot tests. This subset's timestamped snapshot tests exercise related snapshot APIs, but write-prepared-specific membership behavior is covered by other transaction suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/snapshot_checker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/timestamped_snapshot_test.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/timestamped_snapshot_test.cc

## Purpose

This file tests timestamped snapshot creation and lookup for transaction DBs, primarily the write-committed policy. It validates `Transaction::CommitAndTryCreateSnapshot()`, explicit `TransactionDB::CreateTimestampedSnapshot()`, ordering constraints between snapshot sequence numbers and timestamps, snapshot retrieval/range APIs, release behavior, notifier ordering, transaction reuse, and DB close behavior with outstanding snapshots.

## Important APIs, Types, And Functions

- The `TimestampedSnapshotWithTsSanityCheck` instantiation covers unsupported write-prepared/write-unprepared combinations where timestamped commit snapshot creation should be rejected.
- The `TransactionTest` instantiation covers write-committed DBs across stackable DB, two-write-queue, per-key lock manager, and deadlock-timeout parameter combinations.
- `TsCheckingTxnNotifier` implements `TransactionNotifier::SnapshotCreated()` and asserts nondecreasing snapshot sequence and timestamp order.
- Tests use `CommitAndTryCreateSnapshot()`, `SetCommitTimestamp()` indirectly through commit helper, `Prepare()`, `Rollback()`, `BeginTransaction(..., old_txn)`, `CreateTimestampedSnapshot()`, `GetLatestTimestampedSnapshot()`, `GetTimestampedSnapshot()`, `GetAllTimestampedSnapshots()`, `GetTimestampedSnapshots(lb, ub)`, `ReleaseTimestampedSnapshotsOlderThan()`, `Close()`, and snapshot reads via `ReadOptions::snapshot`.

## Control Flow And Behavior

The sanity-check fixture confirms unsupported policies. Without a commit timestamp, `CommitAndTryCreateSnapshot()` returns `InvalidArgument`. With an explicit timestamp under unsupported policies, it returns `NotSupported`. The write-committed fixture repeats the missing timestamp case and expects `InvalidArgument`.

`ReuseExistingTxn` verifies that an existing transaction object can be reused after a commit that created a timestamped snapshot. It commits `v1` at timestamp 100, reuses the same object via `BeginTransaction(..., old_txn)`, commits `v2` at timestamp 110, and verifies old snapshots still read their respective historical values.

`CreateSnapshotWhenCommit` validates commit-time snapshot creation after a prepared transaction. It records the pre-transaction sequence, updates ten keys, prepares, commits with timestamp 1 and notifier, then checks that the created snapshot has the expected timestamp and sequence, is attached to the transaction, and is visible through latest/exact/all snapshot lookup APIs.

`CreateSnapshot` tests explicit DB snapshot creation. It rejects `kMaxTxnTimestamp`, creates timestamp 100, deletes all keys afterward, and verifies reads through the timestamped snapshot still see pre-delete values. It also validates latest/exact/all lookup.

`SequenceAndTsOrder` enforces ordering: a new snapshot cannot use a smaller timestamp than the latest timestamped snapshot; exact same timestamp and same sequence reuses the existing snapshot; larger timestamp with same sequence creates a new object; same or smaller timestamp at a higher sequence fails or returns no snapshot from `CommitAndTryCreateSnapshot()` while the commit itself remains OK.

`MultipleTimestampedSnapshots` creates 100 committed transactions at increasing timestamps, validates exact lookup, invalid range arguments, half-open range results, all/latest retrieval, release by lower bound, and that application-held `shared_ptr` snapshots remain valid after DB releases them. It then clears the shared pointers and closes/deletes the DB.

## State And Persistence Behavior

Timestamped snapshots are shared snapshot objects with both sequence number and transaction timestamp. They preserve historical reads while held. Release removes them from DB lookup structures but does not invalidate application-held `shared_ptr`s. Close fails with `Aborted` when DB-owned timestamped snapshots are still outstanding, as tested by `CloseDbWithSnapshots`.

Commit-time creation integrates with transaction persistence: snapshots are created at the commit sequence after successful write path and can be returned from the transaction's `GetTimestampedSnapshot()`.

## Dependencies And Integration Points

The tests include `utilities/transactions/transaction_test.h`, which supplies parameterized transaction DB setup across write policies. They depend on transaction APIs, timestamped snapshot APIs, `TransactionNotifier`, `DBImpl::seq_per_batch()` checks, and `ManagedSnapshot` for coexistence with non-timestamped snapshots.

## Risks And Edge Cases

- Timestamped snapshot creation requires a real commit timestamp; `kMaxTxnTimestamp` is an invalid sentinel.
- Snapshot timestamp order must be monotonic with sequence publication; equal timestamps are only reusable when sequence number is unchanged.
- Write-prepared/write-unprepared currently do not support timestamped snapshots in the tested configurations.
- Outstanding timestamped snapshots can block clean DB close.
- Snapshot notifier callbacks are not thread-safe in this helper; external synchronization would be required in concurrent use.

## Test Signals

This file is the direct regression suite for timestamped snapshot APIs. It covers positive, negative, reuse, range, release, and close-lifetime behavior under write-committed configurations plus unsupported-policy sanity checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/timestamped_snapshot_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_base.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/transaction_base.cc

## Purpose

This file implements `TransactionBaseImpl`, the shared base for RocksDB transaction implementations, plus the public `Transaction::CommitAndTryCreateSnapshot()` helper. It provides common write-batch management, snapshot lifecycle, savepoints, read-your-own-write reads, transactional iterators, multi-get/entity APIs, lock tracking, untracked writes, operation counters, recovery rebuild from write batches, and commit-time snapshot request state.

## Important APIs And Functions

- `Transaction::CommitAndTryCreateSnapshot()` sets or validates the commit timestamp, marks that a snapshot should be created during commit, calls virtual `Commit()`, and returns the transaction's created timestamped snapshot.
- Constructor/destructor initialize DB pointers, comparator, `WriteBatchWithIndex`, lock tracker, commit-time batch, start time, and two-phase write-batch markers; destructor releases any held snapshot.
- `Clear()` and `Reinitialize()` reset write batches, savepoints, counters, locks, snapshots, ID, name, log number, write options, protection bytes, and comparator state.
- Snapshot methods: `SetSnapshot()`, `SetSnapshotInternal()`, `SetSnapshotOnNextOperation()`, and `SetSnapshotIfNeeded()`.
- Savepoint methods: `SetSavePoint()`, `RollbackToSavePoint()`, and `PopSavePoint()`.
- Read APIs: `Get()`, `GetImpl()`, `GetEntity()`, `GetForUpdate()` overloads, `GetEntityForUpdate()`, `MultiGet()`, `MultiGetEntity()`, and `MultiGetForUpdate()`.
- Iterator APIs: `GetIterator()`, `GetCoalescingIterator()`, `GetAttributeGroupIterator()`, and templated `NewMultiCfIterator()`.
- Write APIs: `PutEntityImpl()`, `Put()`, `Merge()`, `Delete()`, `SingleDelete()`, and untracked variants.
- Utility/state APIs: `PutLogData()`, `GetWriteBatch()`, `GetElapsedTime()`, operation counters, `GetNumKeys()`, `TrackKey()`, `GetBatchForWrite()`, `UndoGetForUpdate()`, `RebuildFromWriteBatch()`, and `GetCommitTimeWriteBatch()`.

## Control Flow

Construction prepares a transaction-local `WriteBatchWithIndex` and lock tracker. If the DB allows two-phase commit, `InitWriteBatch()` sets up the batch for prepare/commit markers. `Clear()` resets transient state while preserving object allocation for reuse.

`CommitAndTryCreateSnapshot()` first resets the caller-provided output pointer, checks whether a commit timestamp is already set, optionally sets it from the argument, rejects mismatched timestamps, and calls `SetSnapshotOnNextOperation()`. It then invokes virtual `Commit()` implemented by the concrete transaction type. After commit succeeds, it returns `GetTimestampedSnapshot()` if one was created.

Reads go through `WriteBatchWithIndex` overlay helpers so transaction-local writes shadow DB state. `Get()` and `MultiGet()` normalize `ReadOptions::io_activity` to `kGet` or `kMultiGet` and reject inappropriate values. `GetForUpdate()` locks/tracks the key before reading and rejects `do_validate=false` with an explicit snapshot because that combination would make conflict semantics undefined.

Writes first call virtual `TryLock()` with `read_only=false`, `exclusive=true`, and validation controlled by tracked/untracked mode. On success they append the operation to either the `WriteBatchWithIndex` or raw base `WriteBatch`, then increment counters.

Savepoints snapshot the current snapshot pointer, pending snapshot creation state, operation counters, and a new lock tracker for locks acquired after the savepoint. Rollback restores those fields, rolls back the write batch, subtracts new locks from the global tracker, and pops the savepoint. Pop merges newer savepoint locks into the next savepoint down so later rollback can still unlock correctly.

`NewMultiCfIterator()` validates non-empty CF lists and comparator compatibility, obtains child DB iterators, wraps each through the transaction write-batch overlay, and constructs either a `CoalescingIterator` or `AttributeGroupIteratorImpl`.

`RebuildFromWriteBatch()` iterates a persisted write batch during recovery, strips timestamps from keys according to CF comparator timestamp size, deserializes wide-column entities, and rebuilds the transaction by calling public transactional write APIs. It rejects prepare/commit/rollback markers because recovered data batches should not contain metadata markers at this stage.

## State And Persistence Behavior

`TransactionBaseImpl` owns in-memory transaction state: DB pointer, write options, comparator, start time, transaction-local write batch, commit-time batch, savepoint stack, operation counters, tracked locks, snapshot/shared snapshot state, snapshot notifier, transaction ID/name/log number, and indexing mode.

It does not itself persist commits; concrete subclasses provide `Commit()`/`Prepare()`/`Rollback()` behavior. It does, however, shape persistent data through write batches and recovery rebuild. `GetBatchForWrite()` switches between indexed and raw writes when `DisableIndexing()` is used, affecting read-your-own-write visibility and timestamp-size metadata availability.

Snapshot ownership is managed with a custom `shared_ptr` deleter that calls `DB::ReleaseSnapshot()`. `SetSnapshotInternal(nullptr)` releases any previously held snapshot.

## Dependencies And Integration Points

The implementation depends on DB internals (`DBImpl`, column families, comparators), iterator implementations (`CoalescingIterator`, `AttributeGroupIteratorImpl`), `WriteBatchWithIndex`, `LockTracker`, wide-column serialization, logging, string utilities, and virtual lock/unlock hooks implemented by optimistic/pessimistic transaction subclasses.

It is the shared implementation behind both optimistic and pessimistic transaction APIs. Tests in `optimistic_transaction_test.cc` directly exercise many of its paths: savepoints, untracked writes, entity APIs, iterators, `UndoGetForUpdate()`, and operation counters.

## Risks And Edge Cases

- Snapshot lifecycle is subtle because snapshots are stored in `shared_ptr` with a DB-release deleter, not deleted directly.
- `SetSnapshotIfNeeded()` invokes notifier immediately for ordinary snapshots; commit-time timestamped snapshots use subclass callbacks instead.
- `UndoGetForUpdate()` must respect savepoint lock scopes; unlocking too much can miss conflicts, while unlocking too little can cause false conflicts or held locks.
- `DisableIndexing()` improves batch-write paths but removes transaction-local index visibility for subsequent reads and complicates timestamp-size lookup in subclasses.
- `MultiGetForUpdate()` locks keys one by one and fails the entire operation on the first lock failure; already acquired locks remain tracked for transaction cleanup.
- Recovery rebuild strips timestamps from persisted keys; timestamp-size metadata must match the current CF comparator.

## Test Signals

`optimistic_transaction_test.cc` provides direct signals for success/conflict behavior, savepoints, untracked writes, `UndoGetForUpdate`, entity reads/writes, multi-get entity sanity checks, coalescing iterators, and attribute-group iterators. `timestamped_snapshot_test.cc` validates `CommitAndTryCreateSnapshot()` behavior through concrete write-committed transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_base.cc -->
