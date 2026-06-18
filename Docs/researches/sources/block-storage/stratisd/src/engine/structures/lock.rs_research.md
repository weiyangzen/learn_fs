# File Research: sources/block-storage/stratisd/src/engine/structures/lock.rs

## Purpose

This file implements two locking abstractions used by the Stratis engine:

- `Lockable<Arc<RwLock<T>>>`: a small wrapper around Tokio owned read/write locks with tracing and blocking helpers.
- `AllOrSomeLock<U, T>`: a custom asynchronous lock over a `Table<U, T>` that supports locking either individual entries or all entries, with read/write modes and nonblocking “available subset” acquisition.

The file also defines guard types for shared/exclusive access and for all/some read/write access.

## Simple Lockable Wrapper

`SharedGuard<G>` and `ExclusiveGuard<G>` wrap lock guards, implement `Deref` and, for exclusive guards, `DerefMut`, and trace on drop.

`Lockable<Arc<RwLock<T>>>` provides:

- `new_shared(t)`
- async `read()` and `write()` returning owned Tokio guards wrapped as `SharedGuard`/`ExclusiveGuard`
- blocking versions using `futures::executor::block_on`

`Lockable<Arc<T>>` is cloneable by cloning the inner `Arc`.

## AllOrSomeLock Model

`AllOrSomeLock<U, T>` stores:

- `lock_record: Arc<Mutex<LockRecord<U>>>`
- `inner: Arc<Mutex<UnsafeCell<Table<U, T>>>>`

`U` must implement `AsUuid`, giving copyable UUID-like keys used by `Table`.

The lock supports:

- `read(key)` for one entry
- `write(key)` for one entry
- `read_all()` for all entries
- `write_all()` for all entries
- `read_all_available()` for currently readable non-conflicting entries
- `write_all_available()` for currently writable non-conflicting entries
- `modify_all()` for exclusive mutation of the whole `Table`
- `upgrade(read_guard)` from single read guard to single write guard
- `Default` via an empty table

## Lock State

`LockRecord<U>` tracks:

- `all_read_locked: u64`
- `all_write_locked: bool`
- `read_locked: HashMap<U, u64>`
- `write_locked: HashSet<U>`
- `waiting: VecDeque<Waiter<U>>`
- `woken: HashMap<u64, WaitType<U>>`
- `next_idx: u64`

`WaitType<U>` encodes `Upgrade(U)`, `SomeRead(U)`, `SomeWrite(U)`, `AllRead`, and `AllWrite`.

`Waiter<U>` stores a wait type, `Waker`, and unique future index.

## Conflict Rules

The lock allows concurrent reads when they do not conflict with writes or all-write. Key rules:

- `SomeRead(uuid)` conflicts with write on the same uuid and all-write.
- `SomeWrite(uuid)` conflicts with read/write on the same uuid, all-read, and all-write.
- `Upgrade(uuid)` waits until no other read exists for that uuid and no global conflicting locks exist.
- `AllRead` conflicts with any write or all-write.
- `AllWrite` conflicts with everything.
- Already-woken waiters are considered during conflict checks so newly arriving requests do not bypass compatible wake batches.

`wake()` drains the waiting queue and wakes every waiter that does not conflict with existing acquisitions or already-woken tasks.

`cancel(idx)` removes a future from both waiting and woken state when a future is dropped before completion.

## Futures And Guards

Each async acquisition is represented by a custom `Future`:

- `SomeRead`
- `SomeWrite`
- `AllRead`
- `AllWrite`
- `AllReadAvailable`
- `AllWriteAvailable`
- `AllModify`
- `Upgrade`

The futures lock both the record and inner table mutex, resolve key names/UUIDs, decide whether to wait, install waiters, and return guard objects containing raw pointers into the table.

Single-entry guards:

- `SomeLockReadGuard<U, T>`
- `SomeLockWriteGuard<U, T>`

All-entry guards:

- `AllLockReadGuard<U, T>`
- `AllLockReadAvailableGuard<U, T>`
- `AllLockWriteGuard<U, T>`
- `AllLockWriteAvailableGuard<U, T>`
- `AllLockModifyGuard<U, T>`

The read/write guards provide lookup and iteration helpers. Write guards expose mutable lookups/iteration. All guards release their recorded acquisitions on drop and call `wake()`.

Several guards support `into_dyn()` when `T: Pool`, converting typed pool guards into `dyn Pool` guards while suppressing duplicate drop accounting in the original guard.

`SomeLockWriteGuard::downgrade()` converts a single write guard into a read guard by moving the lock record from write-held to read-held for that UUID.

`Into<Vec<SomeLockReadGuard<...>>>` and `Into<Vec<SomeLockWriteGuard<...>>>` are implemented for all/all-available guards to split aggregate guards into per-entry guards while updating lock-record accounting.

## Unsafe Interior Mutability Contract

The file uses `UnsafeCell<Table<U, T>>` and raw pointers so guards can outlive the short mutex critical section. Safety relies on `LockRecord` enforcing aliasing rules:

- read guards may coexist only with compatible readers
- mutable guards are issued only when no conflicting readers/writers exist
- all-write/modify prevents all other access
- available-subset guards record locks only for the subset they expose
- drop paths release lock-record state and wake compatible waiters

The custom `Send` and `Sync` impls require corresponding bounds on `U` and `T`, but the core aliasing guarantee is manual and tied to correct lock-record bookkeeping.

## Integration Points

- Uses `Table<U, T>` for name/UUID storage.
- Uses `PoolIdentifier<U>` to resolve acquisition requests by name or UUID.
- Uses the engine `Pool` trait for dynamic pool guard conversion.
- Uses Tokio `RwLock` only for the simpler `Lockable`; `AllOrSomeLock` is fully custom.

## Test Coverage

The local unit test `test_cancelled_future()` constructs an empty `AllOrSomeLock`, holds `write_all()`, polls two pending `read_all()` futures, and verifies canceled futures do not leave stale waiters. This targets the cancellation cleanup path in `Drop` for acquisition futures.

## Correctness Notes

- The lock uses a wrapping `u64` index; comments state it supports up to `u64::MAX` futures before index reuse.
- `add_waiter()` guards against spurious wakeups and prioritizes futures that have already waited by pushing them to the front on repeated waits.
- `woken_or_new()` both validates and consumes a woken record for the acquiring future.
- `modify_all()` grants mutable access to the whole `Table`, not merely all current entries, so it is used when the container itself must change.
- The design is powerful but fragile: bugs in drop flags, `into_dyn()`, aggregate splitting, or available-subset accounting could produce stale locks or aliasing violations.
