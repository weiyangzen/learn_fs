## sources/distributed-fs/beegfs-rust/shared/src/run_state.rs

### Purpose
Implements shared application run-state signaling for graceful asynchronous shutdown and pre-shutdown notification.

### Important APIs, Types, and Functions
- Internal `RunState` enum has `Running`, `PreShutdown`, and `Shutdown`.
- `WeakRunStateHandle` can observe state without blocking shutdown completion.
- `RunStateHandle` observes state and holds a count receiver that keeps shutdown waiting until strong handles are dropped.
- `RunStateControl` sends state changes and waits for strong handles to close.
- `new()` creates a connected `RunStateHandle` and `RunStateControl`.
- `wait_for_shutdown` completes only on `Shutdown`.
- `wait_for_pre_shutdown` completes on `PreShutdown` or `Shutdown`.
- `pre_shutdown()` reports whether pre-shutdown has begun.
- `RunStateHandle::clone_weak()` creates a non-blocking observer.
- `RunStateControl::pre_shutdown()` sends the preparatory state; `shutdown(self)` sends final shutdown and awaits handle drop.

### Control Flow and State
State is broadcast through Tokio watch channels. Tasks select on wait futures and exit when signaled. Strong run-state handles keep `count_tx.closed().await` pending until dropped, while weak handles do not.

### Dependencies and Integration Points
Used by `conn/incoming.rs` listener/receiver loops and likely other async components. Depends on Tokio `watch` and standard `Deref`/`DerefMut` forwarding.

### Risks and Edge Cases
If a task keeps a `RunStateHandle` after receiving shutdown, `RunStateControl::shutdown` waits forever. `pre_shutdown` is one-way and cannot return to running. Watch receiver closure breaks wait loops, effectively treating sender drop as shutdown.

### Test Signals
Includes a Tokio test verifying pre-shutdown state, weak handle behavior, and shutdown completion after dropping the strong handle.
