<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/mpmc.rs -->
## sources/cloud-native/nydus/utils/src/mpmc.rs

### Purpose
This module implements a lightweight asynchronous multi-producer multi-consumer queue for Nydus internal request flows. It combines a `Mutex<VecDeque<T>>` with `tokio::sync::Notify` instead of using a full channel type.

### APIs, Types, and Control Flow
`Channel<T>` exposes `new()`, `close()`, `send()`, `try_recv()`, async `recv()`, `flush_pending_prefetch_requests()`, `lock_channel()`, and `notify_waiters()`. `send()` rejects messages after close and returns the message to the caller for lifecycle recovery; otherwise it pushes to the queue and notifies one waiter. `recv()` creates a reusable notification future, enables it before checking the queue, returns `BrokenPipe` on close, awaits notification, and resets the future if another consumer won the race.

### State, Dependencies, and Integration
The persistent state is `closed: AtomicBool`, a `Notify`, and the pending `VecDeque`. The queue is in-memory only and has no durability. The flush method is tailored to prefetch cancellation: the predicate removes queued entries that should no longer run. `lock_channel()` exposes the raw mutex guard for callers that need to inspect or mutate the queue atomically with external state.

### Risks and Test Signals
`send()` checks `closed` before locking but does not recheck under the queue lock, so a close racing with send can leave messages queued after close. This may be acceptable if close means "wake and drain or fail eventually", but callers should know the semantics. Tests cover FIFO behavior, close rejection, flush retention/removal, explicit notify and locking access, async receive across a thread, and closed-channel `BrokenPipe` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/mpmc.rs -->
