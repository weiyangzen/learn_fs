# sources/distributed-fs/ceph-client/rust/pin-init/examples/mutex.rs

## Purpose
`mutex.rs` is a user-space-style example of a pinned mutex built from a spinlock, an intrusive wait list, and `UnsafeCell` data. It demonstrates initializing pinned subfields and using pinned stack wait entries.

## Important APIs, Types, And Functions
`SpinLock` wraps `AtomicBool` and returns `SpinLockGuard`. `CMutex<T>` is `#[pin_data]` with pinned `wait_list` and `data`. `CMutex::new(val: impl PinInit<T>)` returns `impl PinInit<Self>`, `lock()` returns `Pin<CMutexGuard<'_, T>>`, and `get_data_mut()` gives mutable access from `Pin<&mut Self>`. `CMutexGuard` implements `Drop`, `Deref`, and `DerefMut`. `WaitEntry` stores a pinned list node and, under `std`, the parked thread.

## Control Flow
Lock acquisition takes the spinlock. If already locked, it stack-pin-initializes a `WaitEntry` into the wait list, drops the spinlock while waiting, parks the thread under `std`, and retries until the mutex is available. Once acquired it sets `locked = true` and returns a pinned guard. Guard drop takes the spinlock, clears `locked`, unparks the first waiter if any, and releases the spinlock.

## State And Persistence
Persistent state per mutex includes the wait list, spinlock, `Cell<bool>` lock flag, and `UnsafeCell<T>` data. Wait entries are stack-local and unlink through `ListHead` drop. Thread parking state exists only under the `std` feature.

## Dependencies And Integration Points
It depends on `linked_list.rs`, `pin_init` macros, atomics, `UnsafeCell`, `Cell`, and optional `std::thread` primitives. The example is reused by other examples such as `static_init.rs`.

## Risks And Edge Cases
This is demonstrative code, not a production mutex. The spinlock busy-waits, `Cell<bool>` is protected only by the spinlock discipline, and wait-list manipulation relies on correct pinning and drop order. Without `std`, waiting does not actually block. Waking only one waiter and scheduling races around park/unpark are simplified.

## Test Signals
The included `main` under `std` spawns 20 workers and checks a final counter value. Additional signals include contention with many waiters, Miri with reduced workload, drop of waiting entries, `get_data_mut()` exclusive access, and sanitizer checks for intrusive-list pointer safety.
