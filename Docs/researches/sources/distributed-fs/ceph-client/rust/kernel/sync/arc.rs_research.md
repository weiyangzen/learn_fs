## sources/distributed-fs/ceph-client/rust/kernel/sync/arc.rs

Purpose: implements kernel-style `Arc`, `ArcBorrow`, and `UniqueArc`, backed by kernel `Refcount`, without weak references, and with implicitly pinned shared data.

Important APIs/types/functions: `Arc<T>` owns a non-null `ArcInner<T>` pointer containing `Refcount` and data. `Arc::new`, `into_raw`, `from_raw`, `as_ptr`, `as_arc_borrow`, `ptr_eq`, and `into_unique_or_drop` are core APIs. `ForeignOwnable` allows C ownership transfer. `ArcBorrow` is a non-owning borrowed refcounted pointer that can be upgraded to `Arc`. `UniqueArc<T>` represents refcount-one ownership, supports mutable access, uninitialized allocation, init/pin-init flows, and conversion to `Arc`.

Control flow: clone increments the saturated refcount; drop decrements and frees the leaked `KBox` when zero. `into_unique_or_drop` manually decrements; if zero, it restores the count to one and returns a pinned `UniqueArc`, otherwise it drops only this reference. Raw conversions reconstruct `ArcInner` from the data pointer via layout offset calculation.

State/persistence: state is heap allocation and refcount. No weak state exists. `UniqueArc` guarantees mutable access only while refcount remains one.

Dependencies/integration: depends on `KBox`, `Refcount`, `ForeignOwnable`, pin-init traits, `Layout`, `NonNull`, and vendored `Any` downcast support.

Risks: raw pointer APIs require exact one-for-one ownership recovery. Saturating refcounts avoid zero overflow but can leak on pathological overflow. Pinned data means no `get_mut` for shared `Arc`; moving out would violate invariants. `ArcBorrow::from_raw` requires the refcount not reach zero and no `UniqueArc` coexist.

Test signals: doctests cover clone/drop, receiver forms, trait-object coercion, uniqueness conversion, uninitialized initialization, pin conversion, borrow traits, and display/debug forwarding. Additional stress should exercise raw/foreign ownership and concurrent clone/drop.
