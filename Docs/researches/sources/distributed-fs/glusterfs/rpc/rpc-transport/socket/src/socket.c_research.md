# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.c` implements GlusterFS's socket-backed `rpc_transport_ops`. It owns TCP/UNIX socket listen/connect/accept, nonblocking event handling, outbound RPC record framing, inbound RPC record parsing, SSL/TLS setup and handshake, keepalive/nodelay/window options, disconnect cleanup, throttling, and the volume options exported by the socket transport. The source was read as a complete 4642-line file for this report.

## Important APIs, Types, and Functions

The public transport surface is the `tops` table, wiring `.listen`, `.connect`, `.disconnect`, `.submit_request`, `.submit_reply`, peer/local address getters, and `.throttle` to this implementation. Module lifecycle entry points are `init`, `reconfigure`, and `fini`, with `options[]` describing tunables such as `transport.socket.ssl-enabled`, certificate/key paths, `transport.listen-backlog`, `tcp-window-size`, `transport.tcp-user-timeout`, keepalive settings, `transport.socket.nodelay`, and `non-blocking-io`.

Core connection functions include `socket_init`, `socket_listen`, `socket_connect`, `socket_connect_finish`, `socket_disconnect`, `socket_server_event_handler`, `socket_event_handler`, and helpers for bind/nonblock/nodelay/keepalive/connect-finish. Outbound I/O is staged through `__socket_ioq_new`, `__socket_ioq_churn_entry`, `__socket_ioq_churn`, `socket_submit_outgoing_msg`, and `__socket_rwv`/`__socket_writev`. Inbound parsing is handled by `socket_proto_state_machine`, `__socket_read_frag`, `__socket_read_request`, `__socket_read_reply`, `__socket_read_vectored_request`, `__socket_read_vectored_reply`, `__socket_read_accepted_reply`, `__socket_read_accepted_successful_reply_v2`, and `__socket_read_simple_msg`.

SSL/TLS is concentrated in `init_openssl_mt`, `ssl_setup_connection_params`, `ssl_setup_connection_prefix`, `ssl_complete_connection`, `ssl_setup_connection_postfix`, `ssl_teardown_connection`, `ssl_do`, `ssl_handle_server_connection_attempt`, and `ssl_handle_client_connection_attempt`.

## Control Flow

Client connect resolves the remote address, creates a socket, applies socket options, optionally binds a local address, makes the fd nonblocking, starts `connect`, registers the fd with Gluster's event pool, and lets `socket_event_handler` finish the connection with `getsockopt(SO_ERROR)`. Server listen resolves the local address, creates and configures a socket, binds/listens, and registers a listener event handler. Accepted sockets are wrapped in new `rpc_transport_t` objects, initialized with inherited options, notified to RPC service through `RPC_TRANSPORT_ACCEPT`, then registered for normal socket events.

Event flow is nonblocking and stateful. `socket_event_handler` first completes plain or SSL handshakes if the fd is not logically connected. It then drains pending writes on `POLLOUT`, parses inbound RPC records on `POLLIN`, and treats negative return or poll errors as disconnects. Received messages are packaged as `rpc_transport_pollin_t`, then delivered asynchronously through `socket_event_poll_in_async` so the event loop can resume while upper layers process the message.

The inbound parser reads an ONC/RPC fragment header, allocates or extends an `iobuf`, reads the RPC message type, then dispatches to request or reply state machines. Request parsing can use an RPC service vector sizer to split program headers and payload into separate iovecs. Reply parsing maps XID to request metadata before deciding whether a Gluster read reply can use a vectored payload path. Multi-fragment records loop until the last-fragment bit is seen, then the final iovec set is handed to the transport layer.

## State and Persistence Behavior

All runtime state lives in `socket_private_t` attached to `rpc_transport_t`. It includes fd/index/generation, connection flags, SSL context/session state, outgoing queue, keepalive/window options, read-ahead cache state, inbound parser state, and an async notification counter/condition variable. The implementation has no file-backed persistence. It persists kernel sockets, OpenSSL objects, `iobuf`/`iobref` references, and queued outbound RPC messages only for the lifetime of the transport. Disconnect and `fini` release queued `ioq` entries, unregister/close event fds, free SSL contexts/cert path copies, and unref inbound buffers.

## Dependencies and Integration Points

This file integrates with Gluster's RPC transport framework (`rpc-transport.h`), event pool (`gf_event_register`, `gf_event_select_on`, `gf_event_handled`, `gf_event_unregister_close`), RPC service/client notification path (`rpc_transport_notify` events such as CONNECT, DISCONNECT, ACCEPT, MSG_RECEIVED, MAP_XID_REQUEST), `iobuf`/`iobref` memory management, Gluster dict/options parsing, address helpers from the socket transport support code, generated XDR headers, and OpenSSL. OS dependencies include sockets, `fcntl`, `shutdown`, `setsockopt`, TCP keepalive/TCP_USER_TIMEOUT, `accept`, `connect`, `listen`, `bind`, UNIX socket path cleanup, and IPv4/IPv6 address handling.

## Risks and Edge Cases

The highest-risk areas are partial-read state transitions, vectored read/write pointer mutation, and disconnect races between event threads and async notifications. SSL handshake is split across epoll events and must rearm read/write interest correctly for `SSL_ERROR_WANT_READ` and `SSL_ERROR_WANT_WRITE`. Fragment sizes are checked against a 1 GiB aggregate read guard and `RPC_MAX_FRAGMENT_SIZE` on write, but malformed peer inputs still stress allocation and state reset paths. The read-ahead cache borrows the active inbound iobuf memory, so pointer lifetime and state reset order are important. Accepted transport setup has multiple early-failure paths that must balance refs, event registration, socket close, and RPC service notification. Certificate option changes can break TLS setup, and the code deliberately ignores certificate purpose restrictions with `X509_PURPOSE_ANY` for shared client/server settings.

## Test Signals

Useful signals include RPC transport unit/integration tests for TCP and UNIX sockets, SSL and non-SSL connection setup, reconnect/disconnect races, keepalive/nodelay/window option coverage, malformed fragment/message type tests, large and multi-fragment record tests, Gluster FOP read reply vectored payload tests, NFS/GNFS read/write payload tests, event-thread-death notification tests, and leak/refcount checks around failed accept/connect/register paths. Build coverage should include OpenSSL 1.0.x and 1.1+ conditionals, Linux TCP_USER_TIMEOUT, IPv6, and `BUILD_GNFS`.
