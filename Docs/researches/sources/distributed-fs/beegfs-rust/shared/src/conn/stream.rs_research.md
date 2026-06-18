## sources/distributed-fs/beegfs-rust/shared/src/conn/stream.rs

### Purpose
Wraps Tokio TCP streams behind a BeeGFS-oriented `Stream` type with authentication state, peer address access, readability waits, and timeout-bound reads/writes.

### Important APIs, Types, and Functions
- `TIMEOUT` is two seconds for connect/read/write operations.
- `Stream` stores `InnerStream` and public `authenticated` flag.
- `InnerStream` currently supports only `Tcp(TcpStream)`.
- `From<TcpStream>` creates an unauthenticated `Stream`.
- `connect_tcp(addr)` connects with timeout.
- `readable()` waits until the socket is readable and uses a zero-length `try_read` probe to handle readiness races.
- `read_exact` and `write_all` wrap Tokio I/O in two-second timeouts and warn they are not cancel-safe.
- `addr()` returns the peer address.

### Control Flow and State
The wrapper is a thin stateful transport object. Authentication is an external flag set by request handling. Read/write operations time out but may leave stream contents partially consumed or written, so callers should discard streams after such errors.

### Dependencies and Integration Points
Uses Tokio `TcpStream`, `AsyncReadExt`, `AsyncWriteExt`, and `timeout`; integrated with incoming TCP, outgoing connection pooling, and dispatcher request wrappers.

### Risks and Edge Cases
`addr()` unwraps `peer_addr` and can panic if the OS call fails. `read_exact`/`write_all` are explicitly not cancel-safe. The two-second timeout is fixed and may be too aggressive for slow networks or large 4 MiB messages. The zero-byte readability probe depends on Tokio/socket behavior and may not detect all closure cases uniformly.

### Test Signals
No direct tests. Socket integration tests should cover timeouts, closed-peer detection, address retrieval, and non-reuse after partial I/O errors.
