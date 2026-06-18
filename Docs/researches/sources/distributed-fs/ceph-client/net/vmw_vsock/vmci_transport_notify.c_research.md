# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify.c

## Purpose
This file implements the packet-based VMCI vsock stream notification strategy exported as `vmci_transport_notify_pkt_ops`. It coordinates wakeups between peers by sending and consuming VMCI transport control packets such as `READ`, `WROTE`, `WAITING_READ`, and `WAITING_WRITE`. The code optimizes stream blocking behavior with optional waiting notifications and flow control, using queue-pair occupancy to avoid excessive wakeups while still notifying a peer when reads free space or writes make data available.

## Important APIs, types, and functions
The file is driven through `struct vmci_transport_notify_ops` from `vmci_transport_notify.h`. Its callback table includes socket lifecycle hooks, poll hooks, receive/send pre/post hooks, packet dispatch, and negotiation hooks. `PKT_FIELD(vsk, name)` maps notification state into `vmci_trans(vsk)->notify.pkt`.

Important helpers include `vmci_transport_notify_waiting_write()`, which decides whether a blocked peer writer should be notified based on `peer_waiting_write`, consume queue free space, and the adaptive `write_notify_window`; `vmci_transport_notify_waiting_read()`, which checks whether the peer is waiting to read and whether the produce queue has data; `send_waiting_read()` and `send_waiting_write()`, which build `struct vmci_transport_waiting_info` from qpair indexes and generation counters; and `vmci_transport_send_read_notification()`, which retries `vmci_transport_send_read()` up to `VMCI_TRANSPORT_MAX_DGRAM_RESENDS`.

Packet handlers `vmci_transport_handle_wrote()`, `vmci_transport_handle_read()`, `vmci_transport_handle_waiting_read()`, and `vmci_transport_handle_waiting_write()` update waiting flags and call socket wakeups such as `vsock_data_ready()` or `sk->sk_write_space()`.

## Control flow
Socket initialization resets all notification fields, waiting flags, queue generations, and waiting-info snapshots. Poll-in first checks `vsock_stream_has_data(vsk) >= target`; if not ready on an established socket, it sends `WAITING_READ`. Poll-out checks `vsock_stream_has_space(vsk)`; if full, it sends `WAITING_WRITE`.

On receive, `recv_init()` may grow `write_notify_min_window` to fit the caller target and request a notification if the new minimum exposes sender throttling. `recv_pre_block()` sends `WAITING_READ` and may emit a read notification before sleeping. `recv_pre_dequeue()` snapshots consume indexes; `recv_post_dequeue()` detects consume queue generation wrap and sends `READ` if bytes were consumed. On send, `send_pre_enqueue()` snapshots produce indexes and `send_post_enqueue()` updates produce generation, then sends `WROTE` if the peer is waiting to read.

Incoming notify packets are dispatched by `vmci_transport_notify_pkt_handle_pkt()`. `WROTE` clears `sent_waiting_read` and wakes readers. `READ` clears `sent_waiting_write` and wakes writers. `WAITING_*` records peer wait state and may immediately reply with `WROTE` or `READ` if qpair state already satisfies the wait.

## State and persistence
All state is per socket and in memory under `vmci_trans(vsk)->notify.pkt`: waiting flags, sent-waiting suppression flags, adaptive windows, queue generation counters, and peer waiting information. There is no durable persistence. Correctness depends on socket locking across qpair index snapshots and enqueue/dequeue operations.

## Dependencies and integration points
The file depends on VMCI qpair primitives, VMCI transport send helpers, `struct vsock_sock`, Linux socket callbacks, and packet definitions from `vmci_transport.h`. It is selected by the VMCI transport negotiation path as one possible notify implementation. `process_request()` and `process_negotiate()` initialize window values to the negotiated consume size.

## Risks
Generation and offset math must remain paired with qpair wrap behavior, otherwise waiting notifications can target the wrong queue generation. Retry failure currently logs an error but does not schedule durable resend work. The adaptive window decreases when a peer blocks and increases on local blocking, so regressions can cause either high wakeup traffic or throughput loss. Build-time macros hide alternate behavior, so both optimized and fallback configurations need coverage.

## Test signals
Useful tests include stream send/recv blocking tests across full and empty queue transitions, poll readiness tests, wrap-around queue tests, mixed endpoint compatibility tests, retry-failure injection, and throughput/latency checks with `VSOCK_OPTIMIZATION_FLOW_CONTROL` enabled.
