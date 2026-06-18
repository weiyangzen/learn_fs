# sources/distributed-fs/ceph-client/rust/pin-init/examples/pthread_mutex.rs

## Purpose
This example wraps a `libc::pthread_mutex_t` in a pinned Rust type initialized in place. It demonstrates fallible FFI initialization, pinned destruction, and shared ownership through `Arc::try_pin_init`.

## Important APIs, Types, And Functions
Inside `pthread_mtx`, `PThreadMutex<T>` is `#[pin_data(PinnedDrop)]` with pinned raw mutex storage, data, and `PhantomPinned`. `PThreadMutex::new(data)` returns `impl PinInit<Self, Error>`. `lock()` returns `PThreadMutexGuard<'_, T>`, which unlocks on drop and dereferences to `T`. The local `Error` enum represents OS and allocation failures.

## Control Flow
`new()` builds an initializer that initializes pthread attributes, sets the mutex type to `PTHREAD_MUTEX_NORMAL`, writes `PTHREAD_MUTEX_INITIALIZER`, calls `pthread_mutex_init`, destroys attributes, and returns an error on any failed libc call. Pinned drop calls `pthread_mutex_destroy`. The example `main()` creates a pinned `Arc`, spawns worker threads, increments the protected counter, joins all workers, and asserts the final value.

## State And Persistence
State is per `PThreadMutex`: raw pthread mutex bytes and `UnsafeCell<T>`. The mutex persists while the pinned owner exists and is destroyed in `PinnedDrop`. Thread-local work state is temporary.

## Dependencies And Integration Points
It depends on `libc`, `pin_init`, `std::thread`, `Arc`, and `core::pin::Pin`. It is disabled on Windows and ignored under Miri for the heavy pthread workload.

## Risks And Edge Cases
FFI safety depends on correct raw pointer casts through `UnsafeCell` and always destroying initialized pthread attributes. Return codes from `pthread_mutex_lock` and unlock are ignored. Destroying a locked pthread mutex would be erroneous, so users must not drop while guards exist. The large workload may be expensive in CI.

## Test Signals
Signals include successful concurrent counter increments, failure injection for pthread attribute and init calls, correct drop/destroy behavior, Windows cfg exclusion, Miri ignore behavior, and checking no raw mutex is moved after pinning.
