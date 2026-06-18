# sources/distributed-fs/ceph-client/net/rds/cong.c

## Purpose
`cong.c` implements RDS receive-side congestion tracking. It maintains per-local-address bitmaps of congested ports, associates connections with congestion maps, propagates bitmap updates, and supports socket-level congestion monitoring.

## Important APIs, Types, And Functions
Important functions are `rds_cong_get_maps()`, `rds_cong_add_conn()`, `rds_cong_remove_conn()`, `rds_cong_queue_updates()`, `rds_cong_map_updated()`, `rds_cong_updated_since()`, `rds_cong_set_bit()`, `rds_cong_clear_bit()`, `rds_cong_add_socket()`, `rds_cong_remove_socket()`, `rds_cong_wait()`, `rds_cong_update_alloc()`, and `rds_cong_exit()`. State centers on `struct rds_cong_map`, `rds_cong_tree`, `rds_cong_lock`, and `rds_cong_monitor`.

## Control Flow
Connections call `rds_cong_get_maps()` to allocate or find local and foreign congestion maps. Maps are unique per address and own bitmap pages for all ports. When a local port becomes congested/uncongested, bit operations update the bitmap and `rds_cong_queue_updates()` queues send work on all connections tied to the local map. Incoming congestion bitmap updates call `rds_cong_map_updated()`, increment a global generation, wake map waiters and poll waiters, and notify sockets that registered congestion monitors for affected ports.

Senders call `rds_cong_wait()` before sending to a destination port. Nonblocking sends return `-ENOBUFS` if still congested and optionally record a monitor mask. Blocking sends sleep on the map waitqueue until the bit clears. Closing a monitored socket removes it from the monitor list and clears its own bound-port congestion bit if needed.

## State And Persistence
Global state includes an rb-tree of maps, a global generation counter, and a monitored-socket list. Each map owns pages containing little-endian port bits and a list of associated connections. Maps are freed only during module exit after connections are gone.

## Dependencies And Integration Points
This file integrates with RDS send workers, receive-buffer accounting, poll behavior in `af_rds.c`, connection setup in `connection.c`, and message allocation for congestion bitmap sends.

## Risks
The global congestion lock is used in paths that may run with interrupts masked, so queued work is required instead of inline transmit. Bitmap pages are long-lived and freed at exit, making connection lifetime assumptions important. Nonblocking congestion monitor uses a 64-bit mask subset and may lose detail beyond its representable ports. Incorrect update queuing can leave peers with stale congestion state and cause send stalls or ENOBUFS storms.

## Test Signals
Coverage should include map uniqueness, allocation failure, set/clear/test bit for boundary ports, blocking wait wakeup, nonblocking monitor mask behavior, update generation observed by poll, queueing send work for all map connections, close clearing congestion, and module exit freeing all map pages.
