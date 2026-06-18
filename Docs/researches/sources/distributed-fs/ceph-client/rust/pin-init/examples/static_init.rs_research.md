# sources/distributed-fs/ceph-client/rust/pin-init/examples/static_init.rs

## Purpose
`static_init.rs` demonstrates lazy one-time initialization of a static pinned value using `UnsafeCell<MaybeUninit<T>>`, a stored initializer, a spinlock, and a present flag.

## Important APIs, Types, And Functions
`StaticInit<T, I>` stores the cell, optional initializer, `SpinLock`, and `present` flag. `StaticInit::new(init)` is const. Its `Deref` implementation performs lazy initialization. `CountInit` implements `PinInit<CMutex<usize>>` and initializes a mutex after a delay. `COUNT` is a static `StaticInit<CMutex<usize>, CountInit>`.

## Control Flow
Dereferencing first checks `present`. If false, it takes the spinlock, rechecks `present`, takes the initializer out of the `Cell<Option<I>>`, calls `__pinned_init` on the static memory slot, marks `present = true`, and returns a shared reference. The example main concurrently updates both `COUNT` and a separate `Arc<CMutex<_>>`.

## State And Persistence
The static cell persists for the program lifetime. Once initialized, the value is never dropped. The initializer is consumed exactly once and `present` guards subsequent dereferences.

## Dependencies And Integration Points
It depends on the example mutex, `pin_init`, `UnsafeCell`, `MaybeUninit`, and optional `std` threading. It models how pinned static initialization might work in systems code.

## Risks And Edge Cases
The implementation is demonstrative and uses `Cell` in a static type with unsafe `Sync`; correctness depends on the spinlock protecting all mutation. It uses sleeps for demonstration, unwraps an infallible initializer, and calls `unreachable_unchecked` if the initializer is missing while `present` is false. The static value is leaked by design.

## Test Signals
Signals include multi-threaded first access racing through the spinlock, exactly-once initialization, final counter checks, no double initialization, and sanitizer/Miri review of unsafe `Sync` and `UnsafeCell` access.
