# sources/distributed-fs/ceph-client/net/rds/tcp_recv.c

## Purpose
Adapts TCP byte streams into complete RDS incoming messages, including partial header/data reassembly, congestion bitmap updates, skb-backed payload retention, copy-to-user support, and receive callback scheduling.

## Important APIs, Types, and Functions
Exports `rds_tcp_inc_free()`, `rds_tcp_inc_copy_to_user()`, `rds_tcp_recv_path()`, `rds_tcp_data_ready()`, `rds_tcp_recv_init()`, and `rds_tcp_recv_exit()`. Internal helpers include `rds_tcp_inc_purge()`, `rds_tcp_cong_recv()`, `rds_tcp_data_recv()`, and `rds_tcp_read_sock()`.

## Control Flow
`rds_tcp_data_ready()` runs under the TCP callback lock, reads available data with `GFP_ATOMIC`, and queues receive work if allocation fails. The worker path locks the socket and retries with `GFP_KERNEL`. `rds_tcp_data_recv()` is the `tcp_read_sock()` descriptor callback: it allocates a `struct rds_tcp_incoming` when needed, copies header bytes until complete, records payload length, clones payload ranges into an skb list, and when header and data are complete either applies a congestion bitmap or passes the incoming message to `rds_recv_incoming()`. Complete messages reset header/data counters and drop the incoming reference.

## State and Persistence
Receive state is `t_tinc`, `t_tinc_hdr_rem`, `t_tinc_data_rem`, and each incoming object's `ti_skb_list`. The remote congestion map pages are mutated when receiving `RDS_FLAG_CONG_BITMAP`. State is volatile and cleared on path shutdown or incoming free.

## Dependencies and Integration
Depends on TCP `tcp_read_sock()`, skb copy/extract helpers, RDS incoming lifetime helpers, congestion map updates, socket callback locking, and the TCP incoming kmem cache. It integrates with RDS receive delivery and userspace copyout through the transport `inc_copy_to_user` callback.

## Risks and Test Signals
Risks include partial-read state corruption, allocation failure in callback context, malformed congestion-map sizes, skb clone lifetime, and shutdown races with the receive queue. Test signals are fragmented headers, fragmented payloads across many skbs, zero-length messages, congestion bitmap exact-size updates, allocation-failure fallback to worker, copy-to-user over multi-skb payloads, and receive-drain wakeups during shutdown.
