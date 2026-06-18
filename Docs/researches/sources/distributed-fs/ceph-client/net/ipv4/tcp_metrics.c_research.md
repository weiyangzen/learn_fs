# sources/distributed-fs/ceph-client/net/ipv4/tcp_metrics.c

## Purpose

`tcp_metrics.c` implements the TCP metrics cache: a global RCU hash table keyed by source address, destination address, address family, and network namespace. It remembers path-derived RTT, RTT variance, slow-start threshold, congestion window, reordering, and TCP Fast Open metrics so later connections to the same peer can start with better defaults. It also exposes the cache through generic netlink.

## Important APIs, Types, and Functions

`struct tcp_metrics_block` is the main cache node. It stores next pointer, namespace, source/destination `inetpeer_addr`, stamp, lock bitmask, metric array, Fast Open metrics, and RCU head. `struct tcp_fastopen_metrics` stores cached MSS, SYN loss count, experimental-cookie attempt state, last SYN loss time, and cookie.

Lookup helpers include `tcp_get_metrics()`, `__tcp_get_metrics()`, `__tcp_get_metrics_req()`, `tcpm_new()`, and `tcpm_check_stamp()`. Metric access is wrapped by `tcp_metric_get()`, `tcp_metric_set()`, and `tcp_metric_locked()` with `READ_ONCE`/`WRITE_ONCE` pairing. `tcpm_suck_dst()` initializes or refreshes metrics from route metrics and optionally clears Fast Open state.

Public TCP hooks are `tcp_update_metrics()` on successful connection close, `tcp_init_metrics()` when initializing a socket from cached values, `tcp_peer_is_proven()` for request-socket peer validation, and Fast Open cache accessors `tcp_fastopen_cache_get()` and `tcp_fastopen_cache_set()`.

Generic netlink support is provided by `tcp_metrics_fill_info()`, `tcp_metrics_nl_dump()`, `tcp_metrics_nl_cmd_get()`, `tcp_metrics_nl_cmd_del()`, and the `tcp_metrics_nl_family` definition.

## Control Flow

On connection completion/close, `tcp_update_metrics()` confirms the dst, skips when `tcp_nometrics_save` is set, and either clears cached RTT if the session backed off or lacked RTT, or creates/updates a metrics block. RTT is updated conservatively: larger newly observed RTT replaces the cached value, while lower values decay via EWMA to avoid underestimation. RTT variance uses deviation and `mdev_us`. Slow-start threshold, cwnd, and reordering are saved depending on whether the flow remained in initial slow start, reached congestion avoidance, or had less reliable state.

On new connection setup, `tcp_init_metrics()` resets `snd_ssthresh`, looks up metrics, applies locked cwnd clamps, cached ssthresh, and reordering, then seeds the first RTO from cached RTT only if it is larger than the current SYN-derived RTT. If neither SYN nor cache produced RTT, it restores the conservative fallback timeout.

Cache creation hashes the peer address mixed with net namespace. If a bucket chain depth exceeds `TCP_METRICS_RECLAIM_DEPTH`, lookup encodes a reclaim request and `tcpm_new()` reuses the oldest entry in that bucket instead of allocating. Stale entries older than one hour are refreshed from route metrics.

Generic netlink GET parses destination and optional source address, returns matching metrics, and DUMP walks all buckets with RCU. DEL either flushes all metrics for the net namespace when no destination is supplied or removes matching entries under `tcp_metrics_lock`.

## State and Persistence

The cache is in-memory only and allocated at boot by `tcp_metrics_hash_alloc()`. It persists across sockets but not reboot. It is global but stores a `struct net *` per entry and filters by namespace. Per-entry lifetime is RCU-managed; updates occur under `tcp_metrics_lock` for chain mutations and seqlock protection for Fast Open fields. `tcp_net_metrics_exit_batch()` flushes entries for dead namespaces.

Boot parameter `tcpmhash_entries=` controls hash size. Default size is 16K slots on larger systems and 8K on smaller systems.

## Dependencies and Integration Points

Dependencies include inetpeer address helpers, dst metrics (`RTAX_RTT`, `RTAX_RTTVAR`, `RTAX_SSTHRESH`, `RTAX_CWND`, `RTAX_REORDERING`), TCP socket state, Fast Open cookie structures, generic netlink, RCU, spinlocks, seqlocks, and net namespace lifecycle hooks. IPv6 and IPv4-mapped IPv6 peers are supported when IPv6 is enabled.

## Risks

Metrics can bias new connections incorrectly if stale or learned during atypical congestion, so the code intentionally avoids underestimating RTT and has sysctls to disable saving ssthresh or all metrics. Hash bucket reclaim by oldest stamp bounds depth but can evict active-use peer history. Concurrency risks include reading partially updated metrics, mitigated by `READ_ONCE`/`WRITE_ONCE`, RCU, and seqlock for Fast Open. Netlink deletion must safely unlink while dumps may be reading.

## Test Signals

Check cached RTT/RTO seeding across repeated connections, behavior with `tcp_nometrics_save` and `tcp_no_ssthresh_metrics_save`, Fast Open cookie/MSS/SYN-loss persistence, `ip tcp_metrics show/delete` or equivalent generic netlink flows, namespace teardown cleanup, IPv4/IPv6/v4-mapped keying, boot hash-size parameter behavior, and RCU/lockdep validation during concurrent dump/delete/update.
