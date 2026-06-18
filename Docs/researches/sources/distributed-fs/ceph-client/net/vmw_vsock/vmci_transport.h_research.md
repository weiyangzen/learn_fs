# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport.h

## Purpose
`vmci_transport.h` defines the VMCI transport private protocol contract shared by `vmci_transport.c` and VMCI notification implementations. It describes control packet types, packet layouts, notification state structures, per-socket VMCI transport state, and exported notification-send helpers.

## Important APIs, Types, And Functions
Important definitions include `VMCI_TRANSPORT_PACKET_VERSION`, control resource IDs, notification protocol bits `VSOCK_PROTO_PKT_ON_NOTIFY` and `VSOCK_PROTO_ALL_SUPPORTED`, `enum vmci_transport_packet_type`, `struct vmci_transport_packet`, `struct vmci_transport_notify_pkt`, `struct vmci_transport_notify_pkt_q_state`, `union vmci_transport_notify`, and `struct vmci_transport`. Exported helpers include `vmci_transport_send_wrote_bh()`, `vmci_transport_send_read_bh()`, `vmci_transport_send_wrote()`, `vmci_transport_send_read()`, `vmci_transport_send_waiting_write()`, and `vmci_transport_send_waiting_read()`.

## Control Flow
The header itself has no executable control flow, but it defines the stream control vocabulary: request/negotiate/offer/attach establish queue pairs; wrote/read and waiting-read/waiting-write drive notification protocols; reset and shutdown tear connections down; request2/negotiate2 carry protocol bitmasks for newer notify schemes.

## State And Persistence
`struct vmci_transport` persists per socket in `vsk->trans`. It stores datagram and queue-pair handles, queue sizes, detach subscription id, negotiated notification state, selected notify ops, cleanup list linkage, a guarded socket pointer for asynchronous VMCI events, and a spinlock protecting that pointer.

## Dependencies And Integration Points
The header depends on VMCI definitions/API headers, `vsock_addr.h`, and `af_vsock.h`. Notification source files consume the packet and notify state layouts, while `vmci_transport.c` owns allocation, handshake, and data movement.

## Risks And Edge Cases
The packet layout is wire-visible within VMCI control datagrams, so version and field changes must preserve compatibility. The `vmci_trans()` macro assumes `vsk->trans` is a valid VMCI allocation; callers must only use it after successful transport assignment. Notification structures encode subtle waiting/read/write state that must stay consistent with the negotiated notify ops.

## Test Signals
Useful signals include build coverage for all VMCI transport sources, protocol negotiation between old and new packet types, layout/endian checks for `struct vmci_transport_packet`, notification wait/read/write behavior, and event-detach tests validating `struct vmci_transport` lifetime.
