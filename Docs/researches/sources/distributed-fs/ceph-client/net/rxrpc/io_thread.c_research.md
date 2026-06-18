# sources/distributed-fs/ceph-client/net/rxrpc/io_thread.c

## Purpose
`io_thread.c` is the top-level receive and event dispatch loop for a local RxRPC UDP endpoint. It accepts packets from the UDP encap hook, parses and routes packets to calls or connections, handles local socket error reports, rejects invalid packets, and runs the per-local I/O kthread loop.

## Important APIs and functions
- `rxrpc_encap_rcv()` receives UDP-encapsulated packets and queues them to the local I/O thread.
- `rxrpc_error_report()` transfers UDP error-queue skbs into the local rx queue.
- `rxrpc_direct_abort()` and `rxrpc_direct_conn_abort()` mark skbs for reject responses.
- `rxrpc_input_packet()` validates packet headers and routes to client or service connection lookup.
- `rxrpc_input_packet_on_conn()` routes connection-level packets, call packets, duplicate terminal packets, implicit service call ends, and new service calls.
- `rxrpc_io_thread()` drains packet queues, connection attend queue, call attend queue, client connection reaping, and new client calls.

## Control flow
The UDP encap hook queues marked skbs to `local->rx_queue` and wakes the I/O kthread. The thread splices rx packets into a private queue, extracts headers, validates packet type/service/call/seq fields, builds peer addresses, resolves client connections by IDR or service connections by peer tree, and then routes to connection or call handlers. Invalid packets are marked for BUSY/ABORT/CONN_ABORT rejection and sent by `rxrpc_reject_packet()`.

## State and persistence behavior
The local I/O thread serializes many call/connection state changes. It owns delayed rx injection movement, drains `conn_attend_q` and `call_attend_q`, processes client reap timer flags, assigns new client calls, and destroys the local endpoint when the kthread stops. Skb `mark` and `priority` carry dispatch and rejection metadata.

## Dependencies and integration points
It integrates with UDP socket `sk_user_data`, local endpoint lifecycle, peer lookup, service accept, client/service connection lookup, call packet queuing, connection event handling, peer error handling, output reject/version handling, PMTU probe ACK handling, and test-only rx delay/loss injection.

## Risks
The encap callback can run without the UDP socket lock while `sk_user_data` changes, so RCU handling and local/io_thread checks are critical. Header validation must reject malformed packets before state lookup. Duplicate terminal packet logic depends on cached channel state. Service packets can create calls, so backlog exhaustion and unsupported services must map to correct rejects/discards.

## Test signals
Test malformed headers, zero call/seq/service IDs, unsupported packet types, VERSION handling, client vs service routing, missing client connection abort, new service call creation, duplicate terminal retransmission, implicit service call end, UDP error queue handling, rx delay/loss injection, and I/O thread shutdown.
