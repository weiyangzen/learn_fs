# sources/distributed-fs/ceph-client/rust/syn/thread.rs

## Purpose
`thread.rs` defines `ThreadBound<T>`, a wrapper that marks values `Sync` and conditionally `Send` while only exposing references on the thread where the wrapper was created.

## Important APIs, types, and functions
The main type is `ThreadBound<T> { value, thread_id }`. APIs are `ThreadBound::new`, `ThreadBound::get`, `Debug`, and `Copy`/`Clone` for `T: Copy`. Unsafe impls provide `Sync` for all `T` and `Send` for `T: Copy`.

## Control flow
`new` records `thread::current().id()`. `get` compares the current thread id to the stored id and returns `Some(&T)` only on the original thread. `Debug` prints the value on the original thread and `"unknown"` elsewhere.

## State and persistence behavior
State is in-memory value plus original `ThreadId`. Nothing persists across process boundaries.

## Dependencies and integration points
It uses standard thread IDs and formatting traits. It is an internal helper for cases where Syn needs to carry non-thread-safe data through APIs requiring thread-safe wrappers.

## Risks
The unsafe impls rely on Rust assumptions: `T: Copy` implies no `Drop`, and all interior mutability goes through non-`Copy` `UnsafeCell`. If those assumptions change, `Send`/`Copy` reasoning must be revisited. Cross-thread `get` silently returns `None`, so callers must handle absence.

## Test signals
Tests should verify same-thread access, cross-thread denial, debug output on both threads, `Copy`/`Clone` behavior for copyable values, and compile-time trait behavior for `Send`/`Sync`.
