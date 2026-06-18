# sources/distributed-fs/ceph-client/net/rxrpc/call_event.c

## Purpose
`call_event.c` is the per-call event engine. It processes queued call packets, call timers, delayed ACKs, pings, keepalives, retransmissions, initial service pings, transmission of fresh data, RACK/TLP timer expiry, and completion-time disconnection/crypto cleanup.

## Important APIs and functions
- `rxrpc_propose_ping()` and `rxrpc_propose_delay_ACK()` schedule future ACK generation.
- `rxrpc_transmit_some_data()` sends fresh DATA if the call state and transmit window allow it.
- `rxrpc_resend_tlp()` retransmits the highest transmitted DATA packet for tail-loss probing.
- `rxrpc_input_call_event()` is the central call-attend handler invoked by the I/O thread.
- Internal helpers handle retransmission of lost txqueue segments, service reply phase start, tx phase closure, and initial parameter pings.

## Control flow
The I/O thread places a call on `local->call_attend_q` through `rxrpc_poke_call()`. `rxrpc_input_call_event()` drains `call->rx_queue`, unshares encrypted DATA skbs if in-place verification may modify them, and passes packets to `rxrpc_input_call_packet()`. It then checks RACK timeout, receive/request/hard lifetime timers, delayed ACK, ping, keepalive, initial-ping event, fresh transmit opportunity, lost-ACK event, lost DATA retransmission, idle ACK requests, and ACK pressure. Finally it restarts the call timer to the earliest pending deadline or completes teardown if the call is complete.

## State and persistence behavior
This file mutates call timer fields (`delay_ack_at`, `ping_at`, `keepalive_at`, `expect_*`, `rack_timo_at`), event bits, tx queue progress, congestion loss counters, and call state. On completion it deletes the timer, disconnects from the connection if still connected, and frees per-call crypto. It intentionally centralizes these changes in the I/O thread path to simplify locking.

## Dependencies and integration points
It depends on `input.c` for packet semantics, `output.c` for ACK/DATA transmission, `input_rack.c` for RACK/TLP, `conn_object.c` for disconnection, `security` hooks for call crypto cleanup, RTT/RTO helpers, tracepoints, and socket notification via call completion.

## Risks
Timer restart logic must include every pending deadline or calls can hang. Retransmission scans must not access freed txqueue entries. Encrypted skb unsharing failures drop packets and rely on retransmission. Completion teardown must not race with call release and refcount ownership.

## Test signals
Use tests or packet traces for delayed ACK expiry, ping keepalive, hard timeout, idle timeout, retransmit on loss, RACK timer expiry, service reply transition, tx underflow, encrypted skb clone handling, and complete-call disconnection.
