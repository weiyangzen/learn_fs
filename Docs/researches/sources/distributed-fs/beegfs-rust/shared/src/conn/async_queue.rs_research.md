## sources/distributed-fs/beegfs-rust/shared/src/conn/async_queue.rs

### Purpose
Provides a small async-safe FIFO queue built from `Mutex<VecDeque<T>>` and `tokio::sync::Notify`, used by the connection store to wait for reusable streams.

### Important APIs, Types, and Functions
- `AsyncQueue<T>` holds `queue: Mutex<VecDeque<T>>` and `notification: Notify`.
- `new()` constructs an empty queue.
- `push(item)` appends to the back and notifies one waiter.
- `try_pop()` pops the front immediately; if more items remain, it notifies one waiter to preserve availability.
- `pop().await` waits for notification and loops until `try_pop()` returns an item.

### Control Flow and State
The queue state is in-memory only. `pop` can awaken spuriously or lose a race to `try_pop`, so it loops. After a successful pop, `try_pop` re-notifies when the queue is still non-empty, avoiding stranded items when multiple waiters exist.

### Dependencies and Integration Points
Uses standard `Mutex` and `VecDeque`, plus Tokio `Notify`. It is used by `conn/store.rs` for per-node stored-stream queues.

### Risks and Edge Cases
`Mutex::lock().unwrap()` panics on poison. Notifications are not tied to exact items, so consumers must tolerate wakeups where another consumer won the item. There is no close/shutdown signal; a `pop` waiter can wait forever if no producer arrives and caller does not wrap it in timeout or select.

### Test Signals
Includes unit tests for `push`/`try_pop`, async `push`/`pop`, and a 16-worker concurrent drain. Tests validate queue ordering and notify behavior under load.
