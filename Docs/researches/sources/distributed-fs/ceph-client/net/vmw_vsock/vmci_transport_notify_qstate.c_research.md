# sources/distributed-fs/ceph-client/net/vmw_vsock/vmci_transport_notify_qstate.c

## Purpose
This file implements the queue-state VMCI vsock notification strategy exported as `vmci_transport_notify_pkt_q_state_ops`. Unlike the explicit waiting-notify strategy, it infers whether notifications are needed from queue transitions such as full-to-not-full and empty-to-not-empty, while still using `READ` and `WROTE` notify packets for wakeups.

## Important APIs, types, and functions
`PKT_FIELD(vsk, name)` maps into `vmci_trans(vsk)->notify.pkt_q_state`. `vmci_transport_notify_waiting_write()` applies adaptive flow-control window logic and checks consume queue free space. `vsock_block_update_write_window()` grows the write notification window when a local receive path blocks. `vmci_transport_send_read_notification()` retries `READ` notifications and clears `peer_waiting_write` on success. Send/receive hooks mirror the generic ops contract but many waiting-packet hooks are NOPs because qstate does not send `WAITING_READ` or `WAITING_WRITE`.

## Control flow
Initialization sets `write_notify_window`, `write_notify_min_window`, and peer-waiting state. Poll-in reports readiness if enough stream data exists; otherwise it grows the write window for established sockets. Poll-out reports available space but does not send a waiting write packet.

On receive, `recv_init()` raises the minimum write notify window to `target + 1` and records `notify_on_block` when the current window must be reevaluated. `recv_pre_block()` grows the window and optionally sends a read notification. `recv_post_dequeue()` uses `smp_mb()` before reading qpair free space; if `free_space == copied`, the queue was full before the read, so it marks `peer_waiting_write` and sends `READ`. It also calls `vsock_data_ready()` as a local wakeup compensation noted by the in-code comment.

On send, `send_post_enqueue()` uses `smp_mb()` and checks whether the produce buffer ready count equals bytes written, meaning the queue was empty before this enqueue. If so, it retries `WROTE` notifications. Incoming notify packet dispatch only consumes `WROTE` and `READ`.

## State and persistence
State is per socket and in memory: write windows, `peer_waiting_write`, and `peer_waiting_write_detected`. There are no explicit waiting-info offsets or generation counters in this strategy. Memory barriers protect qpair state observations around enqueue/dequeue effects.

## Dependencies and integration points
The implementation depends on VMCI qpair counters, VMCI notify send helpers, Linux socket wakeup callbacks, and the common notify ops contract. It integrates as an alternate notification mode for VMCI stream sockets.

## Risks
The transition inference is sensitive to stale qpair counters and memory ordering. If `was_full` or `was_empty` is misdetected, peers can miss wakeups or receive redundant notifications. The adaptive window has the same throughput versus wakeup-frequency tradeoff as the packet strategy.

## Test signals
Exercise full queue reads, empty queue writes, concurrent poll/read/write paths, teardown while notifications are pending, and failure injection for `vmci_transport_send_read()` and `vmci_transport_send_wrote()`. Lockdep/KCSAN-style checks are useful because correctness depends on socket locking and barriers.
