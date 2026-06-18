## sources/distributed-fs/ceph-client/rust/kernel/revocable.rs

Purpose: implements `Revocable<T>`, a pinned wrapper whose contents can be made inaccessible and dropped at runtime after RCU readers finish. It lets Rust objects model kernel resources that disappear while references may briefly be in flight.

Important APIs/types/functions: `Revocable::new` pin-initializes an `AtomicBool` availability flag and `Opaque<T>` data. `try_access` takes an RCU read lock and returns `RevocableGuard`; `try_access_with_guard` reuses an existing RCU guard and returns `&T`; `try_access_with` runs a closure under the short-lived guard. Unsafe `access` bypasses revocation checks. `revoke`, unsafe `revoke_nosync`, and `revoke_internal<SYNC>` revoke and drop contents. `RevocableGuard` dereferences to `T` while holding `rcu::Guard`.

Control flow: readers acquire RCU, check `is_available` with relaxed ordering, then dereference data. Revocation atomically swaps availability from true to false, optionally calls `synchronize_rcu`, then drops the object in place. Pinned drop only drops data if it has not already been revoked.

State/persistence: state is in-memory: availability flag plus pinned opaque data. Once revoked, data is dropped exactly once and never reinitialized.

Dependencies/integration: depends on Rust RCU wrappers, kernel `synchronize_rcu`, `Opaque`, pin-init, `PinnedDrop`, and `AtomicBool`. Integrates with subsystems that need revocable, RCU-protected shared objects.

Risks: readers must not sleep while holding `RevocableGuard`, because revocation may wait for RCU grace periods. Relaxed atomics rely on RCU for lifetime, not ordering of data initialization. Unsafe `revoke_nosync` and `access` require external proof that no concurrent users or revocation exist. Double-drop prevention hinges on only one successful `swap(true -> false)` path.

Test signals: doctests cover access before and after `revoke` and explicit RCU-guard access. Additional tests should exercise concurrent readers, repeated revocation returning false, and drop without prior revoke.
