# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.c

## Purpose
`vmci_transport.c` implements the VMware VMCI transport for AF_VSOCK. It supports VMCI datagrams and stream sockets, performs stream connection negotiation over VMCI datagram control packets, establishes VMCI queue pairs for data transfer, handles peer detach/resume events, enforces VMCI privilege restrictions, and registers VMCI as dgram plus host-to-guest or guest-to-host transport depending on platform callbacks.

## Important APIs, Types, And Functions
Important internal flows are `vmci_transport_recv_stream_cb()`, `vmci_transport_recv_pkt_work()`, `vmci_transport_recv_listen()`, `vmci_transport_recv_connecting_server()`, `vmci_transport_recv_connecting_client()`, `vmci_transport_recv_connecting_client_negotiate()`, and `vmci_transport_recv_connected()`. Data operations include `vmci_transport_dgram_bind()`, `vmci_transport_dgram_enqueue()`, `vmci_transport_dgram_dequeue()`, `vmci_transport_stream_enqueue()`, `vmci_transport_stream_dequeue()`, `vmci_transport_stream_has_data()`, and `vmci_transport_stream_has_space()`.

## Control Flow
Init creates a VMCI datagram handle for stream control packets, subscribes to queue-pair resumed events, registers the dgram transport feature, and registers a VMCI callback that later adds H2G or G2H features. Stream connect sends a `REQUEST2` with supported notify protocols or an old `REQUEST` under module override. A listener receiving a request creates a pending child, negotiates queue-pair size and notification protocol, sends `NEGOTIATE` or `NEGOTIATE2`, adds the child to the pending list, and schedules pending cleanup. The client receives negotiation, subscribes to detach events, allocates a queue pair, sends an `OFFER`, then waits for `ATTACH`. The server attaches to the offered queue pair, inserts the child in the connected table, sends `ATTACH`, and moves the child to the accept queue.

## State And Persistence
Per-socket VMCI state is `struct vmci_transport`: datagram handle, queue-pair handle and pointer, produce/consume sizes, detach subscription id, notification state, cleanup list node, socket pointer, and lock. Global state includes the stream control handle, queue-pair resumed subscription id, protocol override parameter, cleanup work/list, and the singleton `vmci_transport` callback table.

## Dependencies And Integration Points
The file depends on VMCI datagram, queue-pair, event, context, and privilege APIs; AF_VSOCK core lookup and queue helpers; and `vmci_transport_notify` implementations selected during protocol negotiation. It integrates with restricted VM privilege checks via socket owner credentials and with the AF_VSOCK core as dgram, H2G, or G2H transport.

## Risks And Edge Cases
The handshake is stateful and multi-packet, so failures must send RST and unwind pending refs, queue-pair handles, and detach subscriptions. Bottom-half VMCI callbacks fast-path notifications but defer most processing to workqueues; socket references and locks must be balanced across that boundary. Peer detach may arrive in different contexts and must avoid use-after-free with `trans->lock` and `trans->sk = NULL`. Old/new protocol fallback and the `PROTOCOL_OVERRIDE` module parameter can hide incompatibilities.

## Test Signals
Test VMCI stream connect/listen/accept, datagram bind/send/recv, old and new notification protocol negotiation, invalid packet type and size handling, restricted-context permission checks, queue-pair detach and resume events, pending connection cleanup, RST during connect, host and guest transport registration, module unload after sockets close, and lockdep/KASAN around detach callbacks.
