## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic.rs

Purpose: exposes Linux Kernel Memory Model-compatible atomics to Rust, intentionally mapping to kernel C atomic/READ_ONCE/WRITE_ONCE semantics rather than Rust's standard atomic memory model.

Important APIs/types/functions: `Atomic<T>` is transparent over `AtomicRepr<T::Repr>`. Unsafe `AtomicType` defines representation compatibility; unsafe `AtomicAdd` defines valid wrapping arithmetic. Methods include `new`, unsafe `from_ptr`, `as_ptr`, `get_mut`, `load`, `store`, `xchg`, `cmpxchg`, `fetch_add`, `fetch_sub`, and `add`. `AtomicFlag` wraps an architecture-appropriate `Flag` for efficient boolean RMW. Raw helpers `atomic_load`, `atomic_store`, `xchg`, and `cmpxchg` work directly on C-side fields.

Control flow: values transmute to representation with `into_repr`, call selected C primitive based on ordering marker type, then transmute back. Load accepts acquire/relaxed; store accepts release/relaxed; exchange and cmpxchg accept all four marker orderings; arithmetic is available for representation types that implement arithmetic ops.

State/persistence: atomic memory is the wrapped value or a borrowed C field. No persistence beyond memory.

Dependencies/integration: depends on `internal` generated atomic traits, `ordering` marker types, predefined implementations, `build_error!`, C bindings, and LKMM.

Risks: `AtomicType` safety is subtle: same size/alignment and round-trip transmutability are required, padding-containing types are excluded, and pointer transfer safety is justified only because dereference remains unsafe. `from_ptr` requires LKMM-race-free concurrent access. Mixed C/Rust atomic use must match ordering expectations.

Test signals: KUnit tests in `predefine.rs` cover loads/stores, acquire-release, xchg, cmpxchg, arithmetic, bool, pointers, and `AtomicFlag`.
