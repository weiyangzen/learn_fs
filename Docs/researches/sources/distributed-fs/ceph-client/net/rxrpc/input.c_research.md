# sources/distributed-fs/ceph-client/net/rxrpc/input.c

## Purpose
`input.c` implements per-call packet semantics. It processes DATA, ACK, ACKALL, and ABORT packets; maintains receive and transmit windows; queues data to recvmsg; handles jumbo packet splitting; derives RTT samples; drives congestion control; and feeds RACK/TLP loss detection.

## Important APIs and functions
- `rxrpc_input_call_packet()` dispatches packet types for an active call.
- `rxrpc_input_data()` and `rxrpc_input_data_one()` validate DATA, maintain receive SACK state, queue in-order/out-of-order packets, and choose ACK reasons.
- `rxrpc_input_ack()` validates ACKs, rotates the transmit window, parses soft ACKs and trailers, updates RTT/congestion/RACK/TLP, and responds to pings.
- `rxrpc_congestion_degrade()` reduces cwnd after idle transmission.
- `rxrpc_implicit_end_call()` handles a new service call implicitly ending the previous call on a channel.

## Control flow
Call packets are queued by `io_thread.c` and drained by `call_event.c`, which invokes `rxrpc_input_call_packet()`. DATA may transition a client into reply receive phase, reset server request idle timers, split jumbo subpackets, queue data to `recvmsg_queue`, and propose or send ACKs. ACKs validate monotonicity, hard-ACK packets by freeing txbufs, process soft ACK/NAK bitmaps per txqueue segment, update trailer-advertised receive window/MTU, advance phase state, drive congestion control, arm RACK loss timers, and send ping responses when required.

## State and persistence behavior
Receive state includes `ackr_window`, `ackr_wtop`, `ackr_sack_base`, `ackr_sack_table`, `rx_highest_seq`, `RXRPC_CALL_RX_LAST`, and queues for in-order and out-of-order skbs. Transmit state includes `tx_bottom`, `tx_top`, `tx_queue`, ACK counters, lost/retransmitted bits, `RXRPC_CALL_TX_LAST`, and `RXRPC_CALL_TX_ALL_ACKED`. Congestion state follows slow start, congestion avoidance, packet loss, and fast retransmit modes.

## Dependencies and integration points
It integrates with output ACK sending, txbuf release, recvmsg notification, call state completion, RTT helpers, RACK/TLP implementation, PMTU peer state, and connection terminal packet caching through later disconnection.

## Risks
ACK validation and txqueue rotation are correctness-critical and must reject window regression/overflow. Jumbo splitting clones skbs and mutates private header state. Receive SACK table indexing must stay aligned as the window advances. NAT/address-change heuristics convert certain ACKs into remote aborts. Congestion and RACK interact through shared ACK summary fields.

## Test signals
Test in-order, duplicate, out-of-order, beyond-window, after-last, and jumbo DATA; ACK hard/soft window advancement; ACK regression rejection; ACK trailer MTU/rwind updates; ACKALL; remote ABORT; implicit service call termination; congestion transitions; RACK/TLP hooks; and ping/ping-response RTT samples.
