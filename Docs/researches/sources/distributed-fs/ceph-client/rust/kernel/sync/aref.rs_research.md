## sources/distributed-fs/ceph-client/rust/kernel/sync/aref.rs

Purpose: provides `ARef<T>`, an owned Rust pointer for C-style objects that already contain their own reference count, avoiding a second Rust `Arc` allocation.

Important APIs/types/functions: unsafe trait `AlwaysRefCounted` defines `inc_ref` and unsafe `dec_ref`. `ARef<T>` stores `NonNull<T>` and owns one reference count increment. APIs include unsafe `from_raw`, `into_raw`, `Clone`, `Deref`, `From<&T>`, `Drop`, `Unpin`, and equality impls.

Control flow: `From<&T>` and `Clone` increment the object's internal refcount before constructing an owned `ARef`. `Drop` calls `T::dec_ref` for the owned increment. `into_raw` suppresses drop with `ManuallyDrop` and transfers refcount responsibility to the caller.

State/persistence: the state lives in the referenced object, not in `ARef`. `ARef` persists only a non-null pointer and ownership of one reference.

Dependencies/integration: integrates with wrappers around kernel C structs that implement get/put patterns. It uses `NonNull`, `ManuallyDrop`, and Rust trait bounds for thread-safety forwarding.

Risks: `AlwaysRefCounted` is unsafe because implementers must guarantee every instance is refcounted and increments keep memory alive. `from_raw` requires the caller to relinquish an existing increment. After `dec_ref`, the object may be freed and must not be used unless another increment is held.

Test signals: examples demonstrate a minimal implementation and raw round trip. Real tests should use concrete refcounted kernel wrappers to verify get/put balance and clone/drop behavior.
