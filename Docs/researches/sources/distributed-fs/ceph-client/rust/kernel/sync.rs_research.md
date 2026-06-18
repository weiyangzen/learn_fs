## sources/distributed-fs/ceph-client/rust/kernel/sync.rs

Purpose: is the top-level Rust synchronization module, re-exporting synchronization primitives and defining lockdep class-key utilities for locks.

Important APIs/types/functions: it declares submodules for `arc`, `aref`, `atomic`, `barrier`, `completion`, `condvar`, `lock`, `poll`, `rcu`, `refcount`, and `set_once`. Re-exports include `Arc`, `UniqueArc`, `ARef` indirectly through submodule, `Completion`, mutex/spinlock APIs, global locks, `LockedBy`, `Refcount`, and `SetOnce`. `LockClassKey` wraps `struct lock_class_key`; `static_lock_class!` creates static keys; `optional_name!` supplies explicit or file-line lock names.

Control flow: dynamic lock class keys register through `lockdep_register_key` during pin initialization and unregister in pinned drop. Static keys are initialized in static storage and returned as pinned static references.

State/persistence: lock class keys are kernel lockdep state. Static keys persist for the module/kernel lifetime; dynamic keys persist until dropped.

Dependencies/integration: depends on `Opaque`, pin-init, lockdep C bindings, and all synchronization submodules. Lock constructors consume these keys to participate in lockdep checking.

Risks: dynamic keys must remain pinned while registered. Static keys must never run destructors. Misusing foreign-owned dynamic keys in examples can unregister while a lock still references the key.

Test signals: doctests show dynamic and static key usage with `SpinLock`. Broader validation comes from lockdep runtime checks and compilation of re-exported primitives.
