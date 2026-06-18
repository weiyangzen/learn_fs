## sources/distributed-fs/ceph-client/rust/kernel/sync/completion.rs

Purpose: wraps Linux completions as a Rust synchronization primitive for one task or work item to signal that work has completed.

Important APIs/types/functions: `Completion` contains pinned `Opaque<bindings::completion>`. `Completion::new` initializes with `init_completion`. `complete_all` wakes all current and future waiters, and `wait_for_completion` blocks uninterruptibly until completion.

Control flow: initialization occurs through `Opaque::ffi_init`. Waiters call `wait_for_completion` on the raw pointer. Producers call `complete_all`, permanently setting the completion done state.

State/persistence: state is the underlying C `struct completion`, including wait queues and done count. It is in-memory and usually embedded in a pinned owner.

Dependencies/integration: depends on pin-init, `Opaque`, and C completion bindings. Commonly integrates with workqueues and `Arc`-owned task objects.

Risks: `wait_for_completion` is uninterruptible and has no timeout, so misuse can deadlock. `complete_all` is permanent for the current completion state; this wrapper does not expose reinitialization. Object lifetime must outlive waiters and signalers.

Test signals: doctest shows a workqueue task completing and a waiter blocking until `complete_all`. Runtime tests should cover multiple waiters, already-completed waits, and teardown ordering.
