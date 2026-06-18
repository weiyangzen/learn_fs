# sources/distributed-fs/ceph-client/rust/kernel/xarray.rs

## Purpose
`xarray.rs` provides a Rust ownership wrapper around Linux's C `struct xarray`. It stores sparse integer-indexed entries whose ownership is represented by `ForeignOwnable`, exposes lock-guarded lookup/mutation/removal/store operations, and destroys all live entries when the array is dropped.

## Important APIs, Types, And Functions
The main public type is `XArray<T: ForeignOwnable>`, initialized through `XArray::new(AllocKind) -> impl PinInit<Self>`. `AllocKind::{Alloc, Alloc1}` selects `XA_FLAGS_ALLOC` or `XA_FLAGS_ALLOC1`. Access is mediated by `Guard<'_, T>`, returned from `try_lock()` or `lock()`, with `get()`, `get_mut()`, `remove()`, and `store()`. `StoreError<T>` carries both the kernel `Error` and the value that could not be inserted.

## Control Flow
Creation uses `pin_init!` and `Opaque::ffi_init` to call `xa_init_flags`. Destruction iterates over all present entries using `xa_find` followed by `xa_find_after`, converts each foreign pointer back into an owned `T`, drops it, then calls `xa_destroy`. Runtime access first takes the xarray spinlock through `xa_lock` or `xa_trylock`; `Guard::drop` releases it with `xa_unlock`. `store()` converts a value with `T::into_foreign`, calls `__xa_store`, checks `xa_err`, returns the old value on success, and reconstructs the new value on failure.

## State And Persistence
State is entirely in the embedded C `xarray` plus type-level ownership invariants. Entries are either `XA_ZERO_ENTRY` or pointers returned by `T::into_foreign`; normal xarray APIs make zero entries appear as null on retrieval. There is no persistence beyond the lifetime of the `XArray`; dropping the wrapper reclaims all stored foreign-owned objects.

## Dependencies And Integration Points
The file depends on kernel bindings for `xa_*`, the kernel allocator flags wrapper, `ForeignOwnable` conversion traits, `Opaque`, `NotThreadSafe`, `build_assert!`, and `pin-init` macros. It is a kernel-safe collection primitive for Rust code that needs Linux xarray behavior while preserving Rust ownership and pin initialization conventions.

## Risks And Edge Cases
The correctness boundary is pointer ownership: any pointer inserted must have come from `T::into_foreign`, and every removed or overwritten pointer must be converted exactly once. `store()` requires `T::FOREIGN_ALIGN >= 4` because xarray uses low pointer bits internally. The guard is explicitly not thread-safe/sendable, and methods assume the xarray lock is held. Dropping while external references exist would violate invariants, so users must respect normal Rust ownership of the wrapper.

## Test Signals
Useful signals include the doctest-style insert/get/get_mut/overwrite/remove flow, allocation-failure injection for `__xa_store`, lock contention behavior for `try_lock`, drop leak checks for multiple stored values, and KASAN/Miri-style checks that overwrite and remove paths do not double-free or lose ownership.
