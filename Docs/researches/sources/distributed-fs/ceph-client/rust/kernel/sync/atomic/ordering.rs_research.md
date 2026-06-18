## sources/distributed-fs/ceph-client/rust/kernel/sync/atomic/ordering.rs

Purpose: defines marker types and sealed traits for LKMM memory-order annotations used by the Rust atomic wrapper.

Important APIs/types/functions: marker structs are `Relaxed`, `Acquire`, `Release`, and `Full`. `OrderingType` is the internal enum used by dispatch code. Sealed trait `Ordering` exposes `TYPE`; `AcquireOrRelaxed` and `ReleaseOrRelaxed` restrict operation-specific valid orderings.

Control flow: methods in `atomic.rs` accept marker values as zero-sized type arguments and dispatch on `Ordering::TYPE`. Invalid combinations are excluded by trait bounds or produce compile-time `build_error!` in unreachable match arms.

State/persistence: no runtime state.

Dependencies/integration: integrated directly by `Atomic<T>` method signatures and maps to LKMM documentation semantics.

Risks: names resemble Rust standard atomics but semantics are LKMM-specific; developers must not assume C++/Rust memory-model details. `Full` represents fully ordered operations with full-barrier strength, not just acquire+release.

Test signals: compile-time trait bounds are the main signal. Public atomic KUnit tests exercise ordering-specific API paths for load/store/xchg/cmpxchg/arithmetic.
