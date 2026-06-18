## sources/distributed-fs/beegfs-rust/shared/src/conn/msg_dispatch.rs

### Purpose
Defines transport-agnostic request dispatch traits and concrete request wrappers for TCP streams and UDP sockets.

### Important APIs, Types, and Functions
- `DispatchRequest` is implemented by dispatchers that can handle any `Request` asynchronously.
- `Request` abstracts response writing, connection authentication, peer address access, header access, and body deserialization.
- `StreamRequest<'a>` wraps a mutable `Stream`, shared buffer, and header reference.
- `SocketRequest<'a>` wraps an `Arc<UdpSocket>`, peer address, buffer, and header reference.
- `Request::respond` serializes a response into the same buffer and writes it to the stream or UDP peer.
- `deserialize_msg<M>` calls `bee_msg::deserialize_body`.
- `test::TestRequest` is a lightweight request double.

### Control Flow and State
Dispatchers receive a request wrapper and decide how to deserialize and handle it. `StreamRequest::authenticate_connection` mutates the underlying stream's `authenticated` flag. UDP authentication is a no-op.

### Dependencies and Integration Points
Depends on `bee_msg::{serialize, deserialize_body, Header, Msg}`, `bee_serde`, `conn::stream::Stream`, Tokio `UdpSocket`, and `SocketAddr`. Used by both incoming TCP and UDP paths.

### Risks and Edge Cases
Responses reuse the request buffer; large responses can fail serialization if they exceed buffer size. UDP responses may exceed practical MTU even if under `UDP_BUF_LEN`. Generic associated async functions are convenient but can make trait-object use difficult. Authentication is transport-specific and silently ignored for UDP.

### Test Signals
Contains a test helper but no direct assertions. Dispatcher-level tests can use `TestRequest` to verify authentication and handler selection without sockets.
