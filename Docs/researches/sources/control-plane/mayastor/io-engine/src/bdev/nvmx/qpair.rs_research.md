## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/qpair.rs

### Purpose
`nvmx/qpair.rs` wraps SPDK NVMe I/O qpairs, including allocation, synchronous connection, optional asynchronous connection, state tracking, waiter fan-out, and teardown.

### Important APIs, Types, And Functions
`QPairState` tracks disconnected, optionally connecting, connected, and dropped. `QPair` owns `Rc<RefCell<Inner>>`, with `create()`, `connect()`, `connect_async()`, `as_ptr()`, and `state()`. `Inner` stores raw qpair/controller pointers, controller name, state, and async waiters. With the async feature, `Connection` owns the poller and SPDK async connect context.

### Control Flow
`create()` gets default qpair options from SPDK, raises `io_queue_requests` to at least configured value, forces `create_only` and async mode, allocates a qpair, and starts disconnected. `connect()` is idempotent for already connected qpairs and otherwise calls SPDK sync connect. Drop marks abort-do-not-retry, aborts queued/transport requests, disconnects and frees the qpair, then nulls raw pointers and marks `Dropped`. Async connect coalesces concurrent waiters, polls the SPDK async context, and completes all listeners with the same result.

### State, Persistence, And Dependencies
State is runtime-only and qpair-local. `Rc<RefCell<_>>` indicates intended single-thread/reactor use. Dependencies include SPDK qpair allocation/connect/free APIs, configured NVMe bdev options, futures oneshot, and optional poller/unsafe-ref machinery.

### Integration Points
`channel.rs` creates, connects, drops, and reinitializes qpairs. `handle.rs` optionally awaits async qpair connect before I/O. Poll groups add qpairs by raw pointer.

### Risks
Drop always dereferences `self.as_ptr()` before nulling; double-drop or use after dropped state would be unsafe. Async connection leaks a boxed `Connection` intentionally until callback/poller completion; cancellation paths must free the SPDK probe manually. `Rc<RefCell>` is not thread-safe, so moving qpairs across cores would violate assumptions. The code always sets `async_mode = true` even for sync connect.

### Test Signals
Cover allocation failure, default option merging, sync idempotency, sync failure reverting state, drop abort/disconnect/free ordering, async multiple waiters, async poll errors, qpair dropped during async connect, and feature-disabled behavior.
