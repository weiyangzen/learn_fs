# Research: sources/distributed-fs/ceph-client/rust/kernel/sync/set_once.rs

## sources/distributed-fs/ceph-client/rust/kernel/sync/set_once.rs

Purpose: implements a thread-safe container that can be populated once and then read for the lifetime of the container. Important APIs are `SetOnce::new`, `Default`, `as_ref`, `populate`, `copy`, `Drop`, and `Send`/`Sync` impls.

Control flow: `init` is an atomic state machine: `0` uninitialized, `1` one writer owns initialization, `2` initialized for shared reads. `populate` does `cmpxchg(0, 1, Relaxed)`, writes `T`, then publishes with `Release` store to `2`. `as_ref` uses `Acquire` load and returns a reference only for state `2`. Drop destroys the value only if initialized. State persists in `MaybeUninit<T>` and the monotonic atomic flag. Dependencies are kernel atomic ordering wrappers, `UnsafeCell`, and `MaybeUninit`. Integration points are one-time global or per-object initialization without full `Once` blocking semantics. Risks include failed populators dropping their input immediately, readers seeing `None` while another thread is in state `1`, no retry/blocking primitive, and requiring `T: Send + Sync` for shared use because drop may happen on any thread. Test signals include racing `populate` calls, acquire/release visibility, drop of initialized vs empty containers, and `copy` for `Copy` values.
