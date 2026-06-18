<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/local_event.c

## Purpose
`local_event.c` handles small local-endpoint events that are not part of normal call data delivery, currently the AF_RXRPC VERSION packet response path. It builds the Linux version identity string and replies to remote VERSION requests using the local UDP transport socket.

## Important APIs, Types, And Functions
The file exposes `rxrpc_gen_version_string()` and `rxrpc_send_version_request()`. It uses `rxrpc_version_string`, `struct rxrpc_wire_header`, `struct rxrpc_host_header`, `struct rxrpc_skb_priv`, `struct sockaddr_rxrpc`, `rxrpc_extract_addr_from_skb()`, `kernel_sendmsg()`, and TX tracepoints.

## Control Flow
Module setup calls `rxrpc_gen_version_string()` to fill a bounded `"linux-<UTS_RELEASE> AF_RXRPC"` string. On a VERSION request, `rxrpc_send_version_request()` extracts the source transport address from the received SKB, mirrors the received epoch, cid, call number, service ID, and opposite client/server direction bit into a VERSION reply header, appends the version string, and sends both buffers through `local->socket`.

## State And Persistence
The only persistent state is the static 65-byte version string. Per-packet state is stack-local and derived from the incoming SKB. No endpoint refcount or queue state is mutated; the function assumes the caller owns a live `rxrpc_local`.

## Dependencies And Integration Points
This file integrates with the UDP socket established by `local_object.c`, packet layout from `protocol.h`, address extraction helpers, kernel release metadata, and rxrpc tracing. It is part of the non-call packet handling path used by local endpoint receive dispatch.

## Risks And Edge Cases
If source address extraction fails, the request is silently ignored. The version string is fixed-size and deliberately truncates long `UTS_RELEASE` values. The response uses `kernel_sendmsg()` directly rather than the `do_udp_sendmsg()` helper, so IPv6 behavior depends on the bound socket context already being correct.

## Test Signals
Useful checks include VERSION request/reply interoperability, IPv4 and IPv6 source address extraction, tracepoint emission for send failures and successes, long release-string truncation, and endpoint teardown races where a request arrives while the local socket is shutting down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_event.c -->
