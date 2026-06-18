# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/socket.h` is the private state and protocol-state header for the GlusterFS socket RPC transport. It defines socket defaults, RPC fragment limits, inbound parser state enums, outbound queue entries, and the `socket_private_t` structure consumed by `socket.c`. The source was read as a complete 264-line file for this report.

## Important APIs, Types, and Functions

Important constants include `GF_DEFAULT_SOCKET_LISTEN_PORT`, `RPC_MAX_FRAGMENT_SIZE`, socket window bounds, keepalive defaults, and `GF_SOCKET_RA_MAX`. Parser enums define the record, fragment, simple-message, request-header, vectored-request, and vectored-reply states used by the nonblocking reader. `struct ioq` stores one outbound framed RPC message as an iovec list plus pending write cursor and optional `iobref`.

`struct gf_sock_incoming_frag` tracks the current fragment cursor, bytes read, pending vector, and request/reply parser substate. `struct gf_sock_incoming` tracks whole-record buffers, payload vectors, request metadata, read-ahead cache fields, fragment header, message type, and record state. `socket_private_t` is the owning transport-private state: outbound queue/lock, socket options, fd/event ids, SSL objects and paths, connection booleans, server/client role flags, and async notification synchronization.

## Control Flow

The header has no executable control flow, but its enums encode the control flow in `socket.c`: records progress from no state to fragment header to fragment body to complete; fragments progress from message type to request/reply body; request and reply bodies may pause at each read boundary and resume after another epoll event.

## State and Persistence Behavior

The structures define in-memory state only. `socket_private_t` persists for the lifetime of a transport, while `gf_sock_incoming` and `ioq` entries are repeatedly reset/freed as messages are received or sent. SSL certificate/key/CA path strings are dynamically copied in the implementation and freed during reset/fini.

## Dependencies and Integration Points

The header depends on OpenSSL headers, `rpc-transport.h`, Gluster list/iovec/iobuf types through included transport headers, and protocol types such as `rpc_request_info_t`, `msg_type_t`, and `mgmt_ssl_t`. It is tightly coupled to `socket.c` and intentionally not a public protocol API.

## Risks and Edge Cases

State enum changes must match switch statements in `socket.c`; missing reset transitions can leave stale parser state across records. `struct ioq` uses a union of `list_head` and explicit next/prev fields, so list layout assumptions must stay aligned. Padding fields suggest layout/alignment sensitivity. Changing `MAX_IOVEC` assumptions or parser substructure sizes affects outbound framing and inbound memory behavior.

## Test Signals

Compile coverage of socket transport is the primary signal. Runtime tests should exercise partial reads/writes across every parser enum state, queue churn with multiple pending messages, SSL and non-SSL connection lifecycles, and teardown while async notifications are in progress.
