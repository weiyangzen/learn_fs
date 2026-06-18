# sources/distributed-fs/ceph-client/net/rds/recv.c

## Purpose
`recv.c` implements generic RDS incoming-message handling and socket `recvmsg()`. It initializes/refcounts incoming messages, enforces receive sequence behavior, processes handshake and RDMA extension headers, queues messages on bound sockets, maintains receive-buffer congestion state, returns payload and control messages to user space, drains notification queues, and formats incoming-message info snapshots.

## Important APIs, Types, and Functions
Public functions include `rds_inc_init()`, `rds_inc_path_init()`, `rds_inc_put()`, `rds_recv_incoming()`, `rds_recvmsg()`, `rds_clear_recv_queue()`, `rds_notify_queue_get()`, `rds_inc_info_copy()`, and `rds6_inc_info_copy()`. Important helpers include `rds_recv_rcvbuf_delta()`, `rds_conn_peer_gen_update()`, `rds_recv_incoming_exthdrs()`, `rds_recv_hs_exthdrs()`, `rds_start_mprds()`, `rds_next_incoming()`, `rds_still_queued()`, `rds_notify_cong()`, `rds_cmsg_recv()`, and `rds_recvmsg_zcookie()`.

## Control Flow
Transports call `rds_recv_incoming()` with a completed `rds_incoming`. The function selects the path, drops old retransmitted sequence numbers, advances `cp_next_rx_seq`, handles ping/probe handshake messages, processes multipath and generation-number extension headers, finds the bound destination socket, processes RDMA extension headers, and queues the incoming on `rs_recv_queue` under `rs_recv_lock` if the socket is alive. Queueing updates receive-buffer byte accounting, congestion bits, optional receive timestamp, latency trace, and wakes socket sleepers.

`rds_recvmsg()` first drains RDMA/status notifications or congestion notifications as control messages. If no data is available it either returns `-EAGAIN` in nonblocking mode, optionally after reaping zero-copy completion cookies, or waits on the socket sleep queue. For data, it copies through the transport `inc_copy_to_user` callback, verifies the incoming is still queued, optionally drops it unless `MSG_PEEK` is set, marks `MSG_TRUNC` when user buffer is too small, emits RDMA destination/timestamp/latency control messages, emits zero-copy completion cookies, fills IPv4 or IPv6 source address output, and releases the incoming reference.

Notification handling moves queued `rds_notifier` objects to a temporary list to avoid sleeping while holding `rs_lock`, copies as many as fit in the control buffer, and requeues unconsumed notifications on error. `rds_clear_recv_queue()` is used during socket teardown after unbinding and drops queued incoming objects while reversing receive-buffer accounting.

## State and Persistence
Incoming objects are refcounted and live in transport-private storage or embedded messages. Socket state includes `rs_recv_queue`, `rs_rcv_bytes`, `rs_congested`, `rs_notify_queue`, congestion notification bits, and zero-copy cookie queue. Connection paths persist `cp_next_rx_seq` and handshake/multipath state. All state is volatile kernel memory.

## Dependencies and Integration Points
The file depends on transport callbacks for incoming copy/free, bind lookup via `rds_find_bound()`, send-side ping/pong and retransmit drop helpers, congestion map APIs, RDMA MR unuse from `rdma.c`, message extension parsing from `message.c`, and socket timestamp/errqueue behavior from the networking core.

## Risks
Sequence handling assumes fragments of a message are complete before transport delivery; old retransmitted messages are dropped, but missing middle fragments are hard to detect at this layer. Queue races with another reader are handled by `rds_still_queued()` and iterator revert, but copy-before-drop means careful MSG_PEEK behavior is required. Congestion state hysteresis must match socket byte accounting or peers can be over-throttled. Handshake extension parsing mutates multipath state and can start new connection paths synchronously. Control-message copy failures can leave notifications queued for retry.

## Test Signals
Test receive delivery, no-socket/dead-socket drops, old retransmit sequence drops, MSG_PEEK, MSG_TRUNC, blocking/nonblocking timeout behavior, RDMA destination cmsg, timestamp cmsg, latency trace cmsg, zero-copy completion cmsg, congestion notifications, notification queue truncation, socket teardown queue clearing, ping/pong handshake, and multipath fan-out. Key counters include `s_recv_queued`, `s_recv_delivered`, `s_recv_drop_*`, `s_recv_ack_required`, `s_recv_bytes_added_to_socket`, and `s_recv_bytes_removed_from_socket`.
