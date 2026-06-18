# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.h

## Purpose
This header defines the VMCI vsock notification abstraction used by the stream send, receive, poll, and control-packet paths. It lets the transport plug in either packet-based waiting notifications or queue-state notifications without changing the higher-level socket code.

## Important APIs, types, and functions
`VSOCK_OPTIMIZATION_WAITING_NOTIFY` enables explicit waiting notification packets, and `VSOCK_OPTIMIZATION_FLOW_CONTROL` enables adaptive read-notification windowing. `VMCI_TRANSPORT_MAX_DGRAM_RESENDS` caps notify datagram retries at 10.

`struct vmci_transport_recv_notify_data` stores per-receive temporary state: `consume_head`, `produce_tail`, and `notify_on_block`. `struct vmci_transport_send_notify_data` stores per-send queue-index snapshots. `struct vmci_transport_notify_ops` is the central callback contract, covering socket init/destruct, poll readiness, notify-packet handling, receive/send lifecycle hooks, and connection request/negotiate handling. The header declares `vmci_transport_notify_pkt_ops` and `vmci_transport_notify_pkt_q_state_ops`.

## Control flow
The VMCI transport allocates per-call notify data, invokes the selected ops around blocking and queue operations, and lets the strategy emit or consume control packets. The callback shape enforces a stable sequence: initialize call data, optionally notify before blocking, snapshot before enqueue/dequeue, update state and notify after data movement, then process any incoming notify packets through the strategy.

## State and persistence
The header itself owns no storage. It defines transient per-call structures and the function-pointer contract used to reach per-socket state in `vmci_transport` private data. There is no persistent state beyond the in-memory socket transport object.

## Dependencies and integration points
It includes VMCI definitions and `vmci_transport.h`, so it is specific to the VMware VMCI vsock transport. Its ops are used by both `vmci_transport_notify.c` and `vmci_transport_notify_qstate.c` and by surrounding VMCI stream send/receive code.

## Risks
Any callback signature change must be propagated through every implementation and caller. Compile-time optimization macros can change struct field usage expectations, so layout and initialization paths need to stay synchronized with the private notify structs in `vmci_transport.h`.

## Test signals
Build tests should cover both notify implementations. Runtime tests should verify that each callback is called in the intended order around poll, blocking reads, blocking writes, socket teardown, and negotiation.
