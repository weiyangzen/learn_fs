## sources/distributed-fs/beegfs-rust/shared/src/conn/incoming.rs

### Purpose
Implements incoming BeeGFS TCP listener and UDP receiver loops. It reads message headers/bodies into fixed buffers and forwards requests to a generic dispatcher.

### Important APIs, Types, and Functions
- `listen_tcp(listen_addr, dispatch, stream_authentication_required, run_state)` binds a `TcpListener`, spawns an accept loop, and spawns `stream_loop` per accepted connection.
- `stream_loop` owns a `Stream`, allocates one TCP buffer, waits for readability or shutdown, and calls `read_stream`.
- `read_stream` reads a BeeGFS header, validates authentication state if required, reads the body, and dispatches a `StreamRequest`.
- `recv_udp(sock, dispatch, run_state)` spawns a datagram receive loop.
- `recv_datagram` allocates a UDP buffer, receives a packet, and spawns per-datagram dispatch through `SocketRequest`.

### Control Flow and State
TCP handling is one task per connection, with request-response semantics on a single stream. UDP handling allocates a new buffer per received datagram and handles dispatch in a separate task so the receive loop can continue. Shutdown is coordinated through `RunStateHandle`. Authentication state is stored on the `Stream`.

### Dependencies and Integration Points
Depends on `conn::stream::Stream`, `conn::msg_dispatch`, `bee_msg::{Header, deserialize_header}`, `AuthenticateChannel`, Tokio networking, and `run_state`. The dispatcher owns message deserialization, handler selection, and response writing.

### Risks and Edge Cases
After `deserialize_header`, `read_stream` indexes `buf[Header::LEN..header.msg_len()]` without checking `header.msg_len() <= TCP_BUF_LEN`; a malformed header can panic before `read_exact` returns an error. Similarly, UDP dispatch deserializes only the header and passes the full 64 KiB buffer to the dispatcher, so body length validation relies on later deserialization. Incoming TCP has no connection limit. Per-datagram allocation can be costly under high UDP load.

### Test Signals
No local tests. Important integration tests should cover invalid headers, overlarge `msg_len`, authentication-required behavior, graceful shutdown, and UDP datagram parsing with short packets.
