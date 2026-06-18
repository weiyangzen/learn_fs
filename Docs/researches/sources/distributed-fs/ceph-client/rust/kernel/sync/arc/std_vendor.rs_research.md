## sources/distributed-fs/ceph-client/rust/kernel/sync/arc/std_vendor.rs

Purpose: vendors the standard-library-style `Arc<dyn Any + Send + Sync>::downcast` operation for this kernel `Arc` implementation.

Important APIs/types/functions: `downcast<T>` checks `Any::is::<T>()` on the trait object and, on success, casts the internal `ArcInner<dyn Any + Send + Sync>` pointer to `ArcInner<T>`, forgets the original `Arc`, and returns `Arc<T>`. On mismatch it returns the original trait-object `Arc` in `Err`.

Control flow: type check first, pointer cast second. The refcount ownership is preserved by forgetting `self` before constructing the new typed `Arc` from the same inner pointer.

State/persistence: no new state; it retypes an existing refcounted allocation.

Dependencies/integration: depends on private `ArcInner`, public `Arc`, and `core::any::Any`. Integrates with trait-object storage using the kernel Arc.

Risks: soundness depends on `Any::is::<T>()` matching the actual data allocation and on `ArcInner<T>` having compatible metadata handling after downcast. Forgetting `self` is required to avoid decrementing the refcount during successful conversion.

Test signals: no local tests. Standard downcast success/failure cases should be compiled for sized concrete types and should verify pointer identity/refcount preservation.
