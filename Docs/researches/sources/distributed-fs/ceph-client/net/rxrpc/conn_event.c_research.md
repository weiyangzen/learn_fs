# sources/distributed-fs/ceph-client/net/rxrpc/conn_event.c

## Purpose
`conn_event.c` processes connection-level events and packets: aborts, challenges, responses, delayed final ACK retransmission, service security transitions, and queued RESPONSE transmission.

## Important APIs and functions
- `rxrpc_abort_conn()` marks a connection locally aborted and pokes it.
- `rxrpc_input_conn_packet()` handles BUSY, ABORT, CHALLENGE, and RESPONSE packets targeted at call number zero.
- `rxrpc_input_conn_event()` runs in the I/O thread for connection-attend events, abort propagation, response sending, service-secured notification, and final ACK timers.
- `rxrpc_process_connection()` is the workqueue processor for queued connection-level skbs and challenge issuance.
- `rxrpc_conn_retransmit_call()` retransmits cached terminal ACK or ABORT for a previous call.
- `rxrpc_post_response()` stores the newest challenge response for I/O-thread transmission.

## Control flow
Input routes callNumber-zero packets to `rxrpc_input_conn_packet()`. CHALLENGE packets are either posted to a call/socket for userspace-managed response or queued directly to the connection work processor. RESPONSE packets are verified by the security module, then the service connection transitions from challenging to service and a special skb mark is queued to the local I/O thread so all challenged calls can be notified. ABORTs mark the connection aborted and propagate completion to active channel calls.

## State and persistence behavior
Connection abort fields are stored before `RXRPC_CONN_ABORTED` with release semantics. Connection event bits track challenge and abort-call work. Channels cache terminal ACK/ABORT information after calls disconnect; delayed final ACK bits in `conn->flags` drive later retransmission. `tx_response` is protected by `local->lock` and retains the newest response by challenge serial.

## Dependencies and integration points
The file depends on security module hooks, output helpers for ACK/ABORT/RESPONSE, connection workqueue scheduling, call completion and socket notification, I/O-thread queues, and peer MTU/window data for ACK trailers.

## Risks
Security handshakes require careful skb unsharing for in-place decryption. Userspace-managed challenge delivery can fail if no call/socket can receive it. Final ACK retransmission must ignore stale call IDs. Connection abort propagation must handle all active channels without racing teardown.

## Test signals
Exercise rxkad/rxgk challenge-response flows, invalid challenge/response aborts, connection abort propagation, delayed final ACK retransmission, userspace-managed RESPONSE replacement, service-secured notification, and cloned skb verification paths.
