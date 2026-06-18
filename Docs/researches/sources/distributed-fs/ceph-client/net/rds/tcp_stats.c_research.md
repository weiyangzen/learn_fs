# sources/distributed-fs/ceph-client/net/rds/tcp_stats.c

## Purpose
Provides per-CPU RDS TCP transport counters and the transport stats export callback used by the generic RDS counter interface.

## Important APIs, Types, and Functions
Defines per-CPU `struct rds_tcp_statistics rds_tcp_stats` and `rds_tcp_stats_info_copy()`. The exported counter names are `tcp_data_ready_calls`, `tcp_write_space_calls`, `tcp_sndbuf_full`, `tcp_connect_raced`, and `tcp_listen_closed_stale`.

## Control Flow
`rds_tcp_stats_info_copy()` checks available entry capacity, sums all online CPU counter slots into a local aggregate, and formats the results through `rds_stats_info_copy()`. It always returns the number of TCP stats entries so the caller can report total required length.

## State and Persistence
State is per-CPU runtime counter memory, reset on module unload or boot.

## Dependencies and Integration
Depends on `tcp.h` for the statistics structure and on the generic RDS stats formatter from `stats.c`. Registered indirectly through `rds_tcp_transport.stats_info_copy`.

## Risks and Test Signals
Risks mirror global stats: structure/name ordering must remain aligned and snapshots are approximate under concurrent updates. Test signals include counter increments from data-ready/write-space callbacks and visibility through `RDS_INFO_COUNTERS` after TCP transport registration.
