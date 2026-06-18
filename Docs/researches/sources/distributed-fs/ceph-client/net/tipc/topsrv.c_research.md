# sources/distributed-fs/ceph-client/net/tipc/topsrv.c

## Purpose
Implements the TIPC topology server. It creates a kernel listening socket on `TIPC_TOP_SRV`, accepts userspace subscriber connections, receives subscription requests, queues topology events back to subscribers, supports in-kernel subscriptions, and manages per-network-namespace server lifetime.

## Important APIs, Types, And Functions
`struct tipc_topsrv` owns the connection idr, namespace pointer, ordered receive/send workqueues, accept work, listener socket, and server name. `struct tipc_conn` owns a topology connection, socket, flags, subscription list, outqueue, work items, and kref. Public functions are `tipc_topsrv_queue_evt`, `tipc_topsrv_kern_subscr`, `tipc_topsrv_kern_unsubscr`, `tipc_topsrv_init_net`, and `tipc_topsrv_exit_net`. Key internal functions handle connection allocation/lookup/close, subscription deletion, socket send/receive work, accept callbacks, listener creation, and namespace start/stop.

## Control Flow And State
Namespace init allocates the server, initializes idr and subscription count, creates ordered workqueues, then creates a critical-importance AF_TIPC SEQPACKET listener bound to the topology service. Listener data-ready queues accept work; accepted sockets get data-ready and write-space callbacks that schedule receive/send work. Receive work reads fixed-size `tipc_subscr` records, creates or cancels subscriptions, and closes malformed connections. Events are copied into `outqueue_entry` objects, sent nonblocking through `kernel_sendmsg`, and retried via write-space callbacks. Timeout events mark entries inactive and trigger subscription deletion after delivery. Shutdown clears callbacks, closes all connections, restores module references for the listener socket, destroys workqueues, idr, and server memory.

## Dependencies And Integration Points
Integrates with `subscr.c`, TIPC sockets (`tipc_sk_bind`, `tsk_set_importance`, `tipc_sk_rcv`), name-table subscriptions, core namespace `tipc_net`, Linux idr, workqueues, kernel sockets, module reference counts, and loopback delivery for kernel subscribers.

## Risks And Test Signals
Risk lies in async lifetime: idr lookup vs close, work items intentionally not flushed per connection, callback locking through `sk_callback_lock`, subscription count balance, and module reference adjustments for internally created sockets. Test signals include multiple concurrent subscribers, malformed short requests, cancel requests, timeout cleanup, send-buffer backpressure, namespace teardown with live connections, kernel subscription loopback delivery, and max-subscription rejection.
