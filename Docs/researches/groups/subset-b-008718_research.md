# Research: subset-b-008718

Work item `subset-b-008718` covers three RocksDB transaction subsystem files:

- `sources/storage-engines/rocksdb/utilities/transactions/transaction_base.h`
- `sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.cc`
- `sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.h`

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_base.h -->
# sources/storage-engines/rocksdb/utilities/transactions/transaction_base.h

## Purpose

`transaction_base.h` declares `TransactionBaseImpl`, RocksDB's shared internal base class for concrete `Transaction` implementations. It centralizes the public `Transaction` API surface that can be implemented independent of a particular concurrency-control policy: point reads, `GetForUpdate`, multi-get variants, iterators, write operations, savepoints, snapshots, write-batch access, operation counters, lock tracking, and recovery rebuild support. The class remains abstract because subclasses must implement policy-specific locking through `TryLock(...)` and `UnlockGetForUpdate(...)`.

This file is therefore a bridge between the external `rocksdb/utilities/transaction.h` API and the concrete pessimistic/optimistic transaction implementations under `utilities/transactions/`. Its state fields also document the transaction lifecycle: a transaction owns a `WriteBatchWithIndex` for pending writes, optional snapshot state, a `LockTracker`, savepoint metadata, write options, counters, and a commit-time side batch used by two-phase commit modes.

## Important APIs, Types, and Functions

The primary type is `TransactionBaseImpl : public Transaction` declared at line 27. Its constructor accepts a `DB*`, `WriteOptions`, and `LockTrackerFactory`, making both the target database and lock-tracker implementation injectable from the concrete transaction layer. The destructor is virtual via `Transaction`.

The central abstract API is:

- `TryLock(ColumnFamilyHandle*, const Slice&, bool read_only, bool exclusive, bool do_validate, bool assume_tracked)` at lines 39-47. Every tracked write and `GetForUpdate` path is expected to call this before mutating transaction-local state or reading for update.
- `UnlockGetForUpdate(ColumnFamilyHandle*, const Slice&)` at lines 361-363. This is the subclass hook called when `UndoGetForUpdate` determines that a read lock can be released.

Read APIs include `Get`, `GetEntity`, `GetForUpdate`, `GetEntityForUpdate`, `MultiGet`, `MultiGetEntity`, `MultiGetForUpdate`, `GetIterator`, `GetCoalescingIterator`, and `GetAttributeGroupIterator` (lines 55-155). The implementation routes read-your-own-write behavior through `WriteBatchWithIndex` helper methods such as `GetFromBatchAndDB`, `GetEntityFromBatchAndDB`, and multi-get helpers.

Write APIs include `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, plus untracked versions of the same operation families (lines 157-245). The tracked APIs default `do_validate` to `!assume_tracked`, while untracked APIs pass `do_validate=false` and still go through `TryLock` so subclasses can decide how to record or bypass validation.

Snapshot APIs are `GetSnapshot`, `GetTimestampedSnapshot`, `SetSnapshot`, `SetSnapshotOnNextOperation`, and `ClearSnapshot` (lines 255-272). Deferred snapshot creation is represented by `snapshot_needed_` and optional `snapshot_notifier_`.

Savepoint APIs are `SetSavePoint`, `RollbackToSavePoint`, and `PopSavePoint` (lines 49-53). The nested `SavePoint` struct at lines 402-430 captures snapshot state, deferred snapshot state, operation counters, and a `LockTracker` containing locks acquired since that savepoint.

State inspection and support APIs include `GetWriteBatch`, `GetCommitTimeWriteBatch`, `GetTrackedLocks`, `GetNumPuts`, `GetNumPutEntities`, `GetNumDeletes`, `GetNumMerges`, `GetNumKeys`, `GetElapsedTime`, `GetWriteOptions`, `SetWriteOptions`, and `RebuildFromWriteBatch` (lines 247-313).

## Control Flow

For normal tracked writes, callers enter one of the public mutation methods (`Put`, `PutEntity`, `Merge`, `Delete`, or `SingleDelete`). The implementation flow is: call the subclass-defined `TryLock` with `read_only=false` and `exclusive=true`; if it succeeds, append the operation to the write batch returned by `GetBatchForWrite`; then increment the relevant counter. `PutEntity` delegates to `PutEntityImpl`, which follows the same lock-then-batch pattern for wide-column writes.

For untracked writes, the flow is intentionally similar, but validation is disabled. The names do not mean "do not call the lock hook"; they mean the subclass receives `do_validate=false`, which is important for callers that already performed conflict checks or intentionally skip validation.

For `GetForUpdate`, the method first validates option combinations, then calls `TryLock` with `read_only=true` and the requested exclusivity. Only after the key is tracked or locked does it read through `GetImpl`. `MultiGetForUpdate` locks all requested keys first and fails the whole operation if any lock fails, then performs per-key reads. This preserves a simple all-keys-tracked contract for later conflict checking and unlock behavior.

Plain `Get` and `MultiGet` do not acquire update locks. They normalize `ReadOptions::io_activity` where applicable and read through `WriteBatchWithIndex`, ensuring pending transaction-local writes shadow DB state.

Savepoint control flow mirrors two stacks: `write_batch_` owns its own write-batch savepoints, while `TransactionBaseImpl::save_points_` owns transaction metadata. `SetSavePoint` pushes metadata and calls `write_batch_.SetSavePoint()`. `RollbackToSavePoint` restores snapshot/deferred-snapshot state and counters, rolls back the write batch, subtracts locks acquired since the savepoint from the global lock tracker, and pops the metadata savepoint. `PopSavePoint` discards the top savepoint, but when nested savepoints exist it merges the top savepoint's new lock tracker into the next one down so a later rollback still knows which locks were acquired after that older savepoint.

Deferred snapshot control flow is driven by `SetSnapshotOnNextOperation`: it marks `snapshot_needed_` and stores an optional notifier. `SetSnapshotIfNeeded` checks that flag, creates a write-conflict-boundary snapshot through `SetSnapshot`, and notifies the caller after creation. This supports APIs like commit-and-create-snapshot flows without forcing immediate snapshot acquisition.

## State and Persistence Behavior

`TransactionBaseImpl` keeps pending transaction changes in `write_batch_`, a `WriteBatchWithIndex` declared at lines 432-433. This is not durable by itself; it is the in-memory transaction write set that later commit paths consume. When indexing is disabled via `DisableIndexing`, `GetBatchForWrite` returns the underlying `WriteBatch` instead of the indexed wrapper, so future writes are appended but not available through the index for read-your-own-write lookup. That switch is performance-sensitive and changes read visibility of subsequent pending writes.

For two-phase commit configurations, `InitWriteBatch` inserts a noop into the write batch when the batch is empty (lines 368-376). The supporting `.cc` implementation calls it during construction and `Clear` when `DBImpl::allow_2pc()` is true. This ensures prepared transaction batches have the required internal structure even before user writes are appended.

`commit_time_batch_` at lines 451-453 stores extra data to persist with the commit when prepare is not skipped. It is separate from the normal write set so commit-time markers or metadata can be handled by write-committed/write-prepared friends without polluting normal operation counts.

Snapshots are held in `std::shared_ptr<const Snapshot>` with a custom release path declared through `ReleaseSnapshot`. The supporting implementation wraps raw snapshots returned by `DBImpl` so they are released via `DB::ReleaseSnapshot` rather than deleted. `ClearSnapshot` resets the shared pointer and clears deferred snapshot flags.

Lock state lives in `tracked_locks_`, with savepoint-relative lock deltas in `SavePoint::new_locks_`. For pessimistic transactions, tracked locks represent actually acquired locks. For optimistic transactions, the comments clarify they are requested locks used for commit-time conflict checking. The base class deliberately avoids encoding which semantics apply.

`RebuildFromWriteBatch` is a recovery integration hook. The implementation iterates a source `WriteBatch`, strips timestamps from keys when the column family comparator has timestamp size, and replays supported operations through the transaction API. Prepare/commit/rollback markers are rejected for this rebuild path.

## Dependencies and Integration Points

Key dependencies include:

- `rocksdb/utilities/transaction.h` and `transaction_db.h` for the public API contract and transaction DB options.
- `WriteBatchWithIndex` and `WriteBatchInternal` for pending write storage, read-your-own-write lookup, savepoint behavior, 2PC noop insertion, timestamp-size metadata, and protection info.
- `LockTracker` and `LockTrackerFactory` for point-lock tracking, savepoint deltas, and optimistic conflict-check bookkeeping.
- `DB`, `DBImpl`, `ColumnFamilyHandle`, `Snapshot`, `Comparator`, `Iterator`, `PinnableSlice`, and wide-column types for the database-facing API.
- `CoalescingIterator` and `AttributeGroupIteratorImpl` in the implementation for multi-column-family iterator composition.

The class declares `WriteCommittedTxn` and `WritePreparedTxn` as friends, showing that concrete 2PC-capable transaction variants need direct access to private commit-time state. Pessimistic and optimistic transaction classes integrate by deriving from this base and implementing locking/unlocking policy. The point/range lock managers consume the tracked lock requests indirectly through those subclasses.

## Risks and Edge Cases

The highest-risk behavior is the split between validation, tracking, and actual locking. A subclass `TryLock` implementation must interpret `read_only`, `exclusive`, `do_validate`, and `assume_tracked` consistently with the base write/read flows. A mismatch can produce missed conflict detection, leaked locks, or duplicate lock accounting.

Savepoints are another sensitive area. Rollback subtracts locks recorded since the savepoint from the global tracker, while `PopSavePoint` merges nested lock deltas downward. Bugs here can either unlock too much or keep locks longer than intended. Any change to `TrackKey`, `UndoGetForUpdate`, or savepoint merging must be tested with nested savepoints and repeated operations on the same key.

`DisableIndexing` creates a behavioral trap: future writes go directly to the underlying `WriteBatch`, so code expecting reads through `WriteBatchWithIndex` to see all pending writes can be surprised. This should remain a specialized performance option with clear call-site expectations.

Snapshot lifetime is safe only if snapshots always come from the associated `DB` and are released through the custom deleter. Reinitialization changes `db_` and write options, so code paths must avoid carrying old snapshot state across reuse; the implementation calls `ClearSnapshot` during `Reinitialize`.

`MultiGetForUpdate` locks keys sequentially and returns a vector filled with the first lock error if any key fails. Callers should understand partial lock acquisition may have happened before failure and rely on transaction cleanup/rollback for release.

## Test Signals

Relevant tests should cover transaction read-your-own-write semantics, savepoints, rollback/pop with nested savepoints, `UndoGetForUpdate`, untracked operations, optimistic conflict checking, pessimistic lock release, snapshots, 2PC prepared transaction recovery, timestamped keys, wide-column entity operations, and `DisableIndexing`. Good regression signals include transaction DB tests that assert operation counters, `GetNumKeys`, pending batch contents, lock conflict outcomes, and snapshot sequence behavior before and after savepoint rollback.

Integration test names are not declared in this header, but adjacent transaction test suites under RocksDB's `utilities/transactions` area are the right place to look. Changes to this class should also run tests exercising both `WriteCommittedTxn` and `WritePreparedTxn`, since those friend classes rely on private commit-time and write-batch state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.cc

## Purpose

`transaction_db_mutex_impl.cc` provides RocksDB's default implementation of the `TransactionDBMutexFactory` abstraction. It adapts standard-library `std::mutex` and `std::condition_variable` to the `TransactionDBMutex` and `TransactionDBCondVar` interfaces used by transaction lock managers. The concrete mutex and condition-variable classes are intentionally private to this translation unit; the public header exposes only the factory.

This file supports transaction key-lock waiting in both point-lock and range-lock paths. When a user does not configure `TransactionDBOptions.custom_mutex_factory`, lock managers allocate these default primitives through `TransactionDBMutexFactoryImpl`.

## Important APIs, Types, and Functions

The internal `TransactionDBMutexImpl` class derives from `TransactionDBMutex` and wraps one `std::mutex` (lines 18-33). It implements:

- `Lock()`, which blocks on `mutex_.lock()` and returns `Status::OK()`.
- `TryLockFor(int64_t timeout_time)`, which performs a non-blocking `try_lock` only when `timeout_time == 0`; otherwise it blocks with `mutex_.lock()` and intentionally ignores the timeout for mutex acquisition.
- `UnLock()`, an inline wrapper around `mutex_.unlock()`.

The internal `TransactionDBCondVarImpl` class derives from `TransactionDBCondVar` and wraps one `std::condition_variable` (lines 35-51). It implements:

- `Wait(shared_ptr<TransactionDBMutex>)`, which waits indefinitely.
- `WaitFor(shared_ptr<TransactionDBMutex>, int64_t timeout_time)`, which waits indefinitely for negative timeouts and uses `std::condition_variable::wait_for` for non-negative microsecond timeouts.
- `Notify()` and `NotifyAll()`, mapped to `notify_one` and `notify_all`.

The exported factory methods are `TransactionDBMutexFactoryImpl::AllocateMutex()` and `AllocateCondVar()` (lines 53-60). They allocate the hidden concrete classes and return them as shared pointers to the public interfaces.

## Control Flow

Lock-manager code receives a factory, asks it for a mutex or condition variable, and then calls only the public virtual methods. With the default factory, `AllocateMutex` constructs `TransactionDBMutexImpl`; `AllocateCondVar` constructs `TransactionDBCondVarImpl`.

For mutex acquisition, `Lock()` always blocks until the `std::mutex` is acquired. `TryLockFor(0)` attempts a non-blocking acquisition and returns `Status::TimedOut(Status::SubCode::kMutexTimeout)` when `try_lock` fails. `TryLockFor(timeout != 0)` blocks until the mutex is acquired and returns OK. The comment explains this is deliberate: older GCC versions had known `std::timed_mutex` bugs, and RocksDB expects these mutexes to be held briefly with at most one mutex held at a time. Timeouts are instead enforced on condition-variable waits.

For condition-variable waits, callers pass a `TransactionDBMutex` that is already locked. The implementation downcasts it to `TransactionDBMutexImpl`, constructs a `std::unique_lock<std::mutex>` with `std::adopt_lock`, and calls `wait` or `wait_for`. After the wait returns, it calls `release()` on the `unique_lock` so the lock remains owned by the caller and the destructor does not unlock it. This preserves the interface contract that `Wait` is called with the mutex locked and returns with the mutex still locked.

`WaitFor` treats `timeout_time < 0` as infinite wait. For non-negative values it converts the timeout from microseconds to `std::chrono::microseconds`, uses `wait_for`, and returns `Status::TimedOut(kMutexTimeout)` only when the condition-variable wait reports timeout. Spurious wakeups return OK, matching the public interface.

## State and Persistence Behavior

The file manages only transient synchronization state. No RocksDB data, transaction metadata, or lock table contents are persisted here. The lifetime of each primitive is controlled by `std::shared_ptr` returned from the factory; lock-manager data structures hold those shared pointers.

`TransactionDBMutexImpl` stores one `std::mutex`, and `TransactionDBCondVarImpl` stores one `std::condition_variable`. The condition variable does not own the mutex; it relies on callers passing a compatible default mutex implementation. The downcast makes that compatibility assumption explicit.

Timeout state is not persisted. The only status-bearing behavior is returning `TimedOut(kMutexTimeout)` from non-blocking mutex acquisition failure or condition-variable timeout.

## Dependencies and Integration Points

This file depends on:

- `utilities/transactions/transaction_db_mutex_impl.h` for the factory declaration.
- `rocksdb/utilities/transaction_db_mutex.h` for the abstract mutex, condition variable, and factory interfaces.
- Standard `<mutex>`, `<condition_variable>`, and `<chrono>` for implementation.
- RocksDB `Status` and `Status::SubCode::kMutexTimeout` through the public mutex header.

Integration points include point lock manager stripes, range tree lock manager portability wrappers, and any transaction DB code that uses `TransactionDBOptions.custom_mutex_factory`. Adjacent references show point lock manager code defaults to `std::make_shared<TransactionDBMutexFactoryImpl>()` when no custom factory is configured, and range lock code also instantiates this implementation for default behavior.

## Risks and Edge Cases

The main risk is the `static_cast<TransactionDBMutexImpl*>` in condition-variable waits. It is correct only when the mutex was allocated by this same default factory. If a custom factory mixes a custom mutex with this condition variable, behavior is undefined. The intended contract is that a factory produces compatible mutex and condition-variable implementations as a pair.

Timeout semantics are deliberately uneven. `TryLockFor(timeout > 0)` can block longer than the requested timeout because it ignores the timeout while acquiring the mutex. Lock acquisition timeout is only honored for `timeout == 0`; positive timeouts are effectively deferred to `WaitFor`. This is documented in-code, but it is a behavioral detail that tests and custom implementations should not accidentally assume away.

The use of `std::adopt_lock` requires the passed mutex to already be locked by the current thread. Passing an unlocked mutex or a mutex locked by another thread violates the standard-library precondition and can lead to undefined behavior. That is why this implementation must remain tightly coupled to the lock-manager calling convention.

Condition variables can wake spuriously, and the implementation returns OK in that case. Callers must always re-check their lock-table predicates after waiting.

The file includes `<sstream>` and `<thread>` even though this implementation does not use them; this is harmless but may be leftover include noise.

## Test Signals

Useful tests should exercise successful lock/unlock, non-blocking `TryLockFor(0)` timeout behavior, `WaitFor` timeout behavior in microseconds, negative-timeout infinite waits, `Notify` waking one waiter, `NotifyAll` waking all waiters, and spurious-wakeup-safe lock-manager loops. Integration tests in point and range transaction locking are more valuable than unit tests against these wrappers alone because the correctness depends on caller-side predicate checks and lock ownership conventions.

Concurrency tests should also verify that lock-manager operations do not rely on positive `TryLockFor` enforcing a strict mutex acquisition deadline. The deadline that matters for real contention is the condition-variable wait path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.h -->
# sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.h

## Purpose

`transaction_db_mutex_impl.h` declares RocksDB's default `TransactionDBMutexFactoryImpl`. The factory is the public construction hook for default transaction DB synchronization primitives, while the concrete mutex and condition-variable implementations remain hidden in `transaction_db_mutex_impl.cc`.

This separation lets transaction lock managers depend on a stable factory type without exposing implementation details such as `std::mutex` or `std::condition_variable`. It also preserves the customization point documented by `TransactionDBOptions.custom_mutex_factory`: applications can replace the entire factory when they need custom synchronization primitives.

## Important APIs, Types, and Functions

The file includes only `rocksdb/utilities/transaction_db_mutex.h`, which defines `TransactionDBMutex`, `TransactionDBCondVar`, and `TransactionDBMutexFactory`.

It forward-declares `TransactionDBMutex` and `TransactionDBCondVar` inside `ROCKSDB_NAMESPACE` (lines 12-13), then declares:

- `class TransactionDBMutexFactoryImpl : public TransactionDBMutexFactory` (line 17).
- `std::shared_ptr<TransactionDBMutex> AllocateMutex() override` (line 19).
- `std::shared_ptr<TransactionDBCondVar> AllocateCondVar() override` (line 20).

No constructor, destructor, fields, or additional policy methods are declared. The default constructor and destructor are sufficient because the factory is stateless.

## Control Flow

The header itself has no executable control flow. Its role is to let lock-manager code instantiate or store the default factory. At runtime, call sites create `TransactionDBMutexFactoryImpl` when transaction DB options do not provide a custom mutex factory. They then call `AllocateMutex` and `AllocateCondVar`, whose definitions in the `.cc` file return hidden default implementations.

Because the concrete classes are not declared in the header, users cannot directly construct a default mutex or condition variable. They must go through the factory interface. That keeps the mutex/condition-variable pairing consistent and leaves room to change implementation details without changing external transaction lock-manager code.

## State and Persistence Behavior

`TransactionDBMutexFactoryImpl` is stateless. It does not store configuration, own live mutexes, or persist any state. Each allocation call returns a new shared pointer to a synchronization object owned by the caller's lock-manager structures.

There is no on-disk state and no database metadata touched by this header. All behavior is transient process synchronization delegated to the `.cc` implementation.

## Dependencies and Integration Points

The main dependency is the public transaction mutex abstraction in `rocksdb/utilities/transaction_db_mutex.h`. That public header defines the contract that `AllocateMutex` and `AllocateCondVar` must satisfy: mutexes support blocking lock, timed try-lock, and unlock; condition variables support wait, timed wait, notify one, and notify all.

Integration points include:

- `TransactionDBOptions.custom_mutex_factory`, which can override this default factory.
- Point lock manager setup, where default transaction DB locking creates a `TransactionDBMutexFactoryImpl` if options do not supply one.
- Range tree lock manager setup and portability wrappers that use the same factory abstraction for lock and condition-variable allocation.
- Tests that instantiate `TransactionDBMutexFactoryImpl` directly to exercise default transaction locking.

## Risks and Edge Cases

The header's main design constraint is that `AllocateMutex` and `AllocateCondVar` must return compatible implementations. The `.cc` condition variable downcasts the mutex passed to `Wait`/`WaitFor` to the hidden default mutex type, so mixing a condition variable from this factory with a mutex from a different factory is unsafe. Keeping both allocation methods on one factory helps prevent that misuse.

Because this header exposes only a stateless concrete factory, any future default synchronization behavior that needs configuration would require an API extension or a different factory type. That is acceptable for the current implementation but should be considered before adding knobs to default transaction locking.

Another minor risk is dependency surface: including the public mutex abstraction here is necessary, but this file intentionally avoids including standard synchronization headers. Adding concrete implementation details to this header would increase rebuild cost and expose implementation choices that are currently private.

## Test Signals

Header-level coverage is indirect. Build tests should catch signature drift against `TransactionDBMutexFactory`. Runtime tests should instantiate `TransactionDBMutexFactoryImpl`, allocate a mutex and condition variable, and verify they satisfy the public interface contract through transaction lock-manager tests. Custom factory tests should also ensure RocksDB consistently uses a single factory's mutex and condition-variable pair rather than mixing default and custom primitives.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.h -->
