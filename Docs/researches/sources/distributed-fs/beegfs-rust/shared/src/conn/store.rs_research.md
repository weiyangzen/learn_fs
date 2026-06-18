## sources/distributed-fs/beegfs-rust/shared/src/conn/store.rs

### Purpose
Provides in-memory storage for reusable TCP streams, fixed-size message buffers, peer address lists, and per-peer connection permits.

### Important APIs, Types, and Functions
- `Store<T>` holds per-key `(AsyncQueue<StoredStream<T>>, Semaphore)` pairs, a buffer deque, address map, and connection limit.
- `new(connection_limit)` constructs the store.
- `try_pop_stream`, `try_acquire_permit`, `pop_stream`, and `push_stream` implement stream reuse and connection limiting.
- `pop_buf`, `pop_buf_or_create`, and `push_buf` manage reusable `Vec<u8>` buffers sized to `TCP_BUF_LEN`.
- `get_node_addrs` and `replace_node_addrs` manage peer address snapshots.
- `StoredStreamPermit<T>` owns a Tokio semaphore permit for one open stream.
- `StoredStream<T>` wraps `Stream` plus its permit and implements `AsRef` / `AsMut`.

### Control Flow and State
All state is in memory and protected by `Mutex`/`RwLock`. A permit is acquired before opening a new connection and held by the `StoredStream`; dropping the stream releases the permit. Existing streams are queued by peer key. Buffers are pooled globally.

### Dependencies and Integration Points
Uses `AsyncQueue`, `Stream`, Tokio `Semaphore`, and `SocketAddr`. It is used by `conn/outgoing.rs` to implement `Pool`.

### Risks and Edge Cases
`connection_limit == 0` means no new connection permits can be acquired and callers may later wait for a stream that can never exist. Mutex/RwLock poison causes panics through `unwrap`. The buffer pool is unbounded and can retain many 4 MiB buffers after spikes. Address replacement is all-or-nothing; there is no merge or staleness tracking.

### Test Signals
No direct tests. Behavior is partly exercised through `AsyncQueue` tests. Store tests should cover permit release on drop, zero-limit behavior, address replacement, and buffer reuse.
