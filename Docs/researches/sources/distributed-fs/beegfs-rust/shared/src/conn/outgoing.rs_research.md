## sources/distributed-fs/beegfs-rust/shared/src/conn/outgoing.rs

### Purpose
Implements outgoing BeeGFS communication through a reusable connection/buffer pool. It supports request-response TCP messages, fire-and-forget TCP sends, UDP datagram broadcasts, optional stream authentication, address management, and IPv6 filtering.

### Important APIs, Types, and Functions
- `Pool` owns a `Store<Uid>`, UDP socket, optional `AuthSecret`, and `use_ipv6` flag.
- `Pool::new` configures connection limit, auth, and IPv6 usage.
- `request<M, R>` serializes a message, communicates over a stream expecting a response, deserializes the response, and returns `R`.
- `send<M>` serializes and writes a stream message without reading a response.
- `comm_stream` tries reusable streams, then opens a new stream with a permit, then waits up to two seconds for an existing stream.
- `write_and_read_stream` writes the serialized message and optionally reads response header/body.
- `broadcast_datagram` serializes once and sends to all known addresses for each peer.
- `replace_node_addrs` updates the address store for a node UID.

### Control Flow and State
Buffers and streams are pooled in `Store`. New streams are authenticated by sending `AuthenticateChannel` before the real message if `auth_secret` is configured. Failed reused streams are discarded by dropping them. Successful streams are pushed back into the pool.

### Dependencies and Integration Points
Depends on `bee_msg` serialization/deserialization, `conn::store`, `conn::stream`, `AuthSecret`, `Uid`, Tokio UDP, and `timeout`. It is the main client-side transport API for higher-level BeeGFS components.

### Risks and Edge Cases
On early errors in `request`/`send`, buffers may not be returned to the buffer pool because `push_buf` is after fallible awaits. This is not memory unsafe but can reduce pooling efficiency. Header `msg_len` is used to slice into fixed buffers without explicit upper-bound checks, so malformed responses can panic. Authentication writes do not read an auth response, assuming one is unnecessary. If all addresses are IPv6 and `use_ipv6` is false, connection attempts are skipped and the final error still lists all known addresses. UDP broadcast treats send success as socket-level only, not delivery.

### Test Signals
No local tests. Needed coverage includes buffer return on error, connection-limit behavior, authentication prelude, overlarge response headers, IPv6 filtering, and datagram broadcast partial failures.
