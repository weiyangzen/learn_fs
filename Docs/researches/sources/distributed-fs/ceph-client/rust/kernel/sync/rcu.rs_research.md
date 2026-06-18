# Research: sources/distributed-fs/ceph-client/rust/kernel/sync/rcu.rs

## sources/distributed-fs/ceph-client/rust/kernel/sync/rcu.rs

Purpose: provides RAII evidence for holding the RCU read-side lock. Important APIs are `Guard::new`, `Guard::unlock`, `Default`, `Drop`, and free function `read_lock`.

Control flow: creating a `Guard` calls `rcu_read_lock`; dropping it calls `rcu_read_unlock`. `unlock(self)` consumes the guard and relies on normal drop at the end of the method call. State is not stored beyond `NotThreadSafe`; the real state is per-thread/per-CPU kernel RCU state. Dependencies are `bindings` and `NotThreadSafe`. Integration points include accessors that require proof of RCU read-side protection and code borrowing RCU-protected kernel objects. Risks include assuming the guard is `Send` or can cross task contexts, because it intentionally is not thread-safe; nesting is delegated to kernel RCU semantics. Test signals are compile-time non-`Send` behavior, balanced lock/unlock in simple paths, and use with APIs that assert RCU protection.
