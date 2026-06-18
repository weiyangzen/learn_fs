# sources/distributed-fs/ceph-client/rust/pin-init/src/alloc.rs

## Purpose
`alloc.rs` adds allocation-backed in-place initialization support for `Box` and `Arc` when `std` or `alloc` is available. It lets users allocate uninitialized storage and initialize it with `Init` or `PinInit` without intermediate moves.

## Important APIs, Types, And Functions
`InPlaceInit<T>` provides `try_pin_init`, `pin_init`, `try_init`, and `init`. Implementations cover `Box<T>` and `Arc<T>`. `InPlaceWrite<T>` is implemented for `Box<MaybeUninit<T>>`. The file also marks `Box<T>` as `ZeroableOption`.

## Control Flow
`Box` initialization allocates `Box::try_new_uninit()` or `Box::new_uninit()` depending on features and delegates to `write_init` or `write_pin_init`. `Arc` initialization allocates an uninitialized `Arc`, gets the unique mutable slot with `Arc::get_mut`, runs the initializer, and then assumes initialization, pinning for the pinned path. Convenience methods convert infallible initializer errors into allocation-error results.

## State And Persistence
State is the allocated uninitialized storage and, after success, an initialized `Box<T>`, `Pin<Box<T>>`, `Arc<T>`, or `Pin<Arc<T>>`. On initializer error, allocation is deallocated without dropping uninitialized `T`.

## Dependencies And Integration Points
It depends on `alloc` or `std`, `AllocError`, `MaybeUninit`, `Pin`, `Init`, `PinInit`, `InPlaceWrite`, and initializer closure constructors. The public crate re-exports `InPlaceInit` for examples and users.

## Risks And Edge Cases
`Arc::get_mut` should always succeed immediately after allocation; the code treats failure as unreachable. Safety depends on not dropping uninitialized memory on failure and not moving a pinned allocation after initialization. Feature combinations change allocation APIs and error types.

## Test Signals
Tests should cover Box and Arc init/pin-init success, allocation failure conversion, initializer failure cleanup, `Box<MaybeUninit<T>>::write_*`, feature combinations with `std` and `alloc`, and `!Unpin` values remaining pinned.
