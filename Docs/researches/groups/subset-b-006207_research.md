# Research: subset-b-006207

Grouped research for IPv4 TCP implementation files under `sources/distributed-fs/ceph-client/net/ipv4/`. Each section is delimited for reconciliation into the matching source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_ipv4.c

## Purpose

`tcp_ipv4.c` is the IPv4-specific TCP protocol binding. It connects the address-family-neutral TCP core to IPv4 routing, ICMP, hash tables, request sockets, TIME-WAIT sockets, reset/ACK generation, procfs/BPF iteration, and per-network-namespace TCP defaults. It exports the `tcp_prot` protocol object used by AF_INET stream sockets and supplies `ipv4_specific` callbacks used by `inet_connection_sock`.

The file is not specific to Ceph protocol semantics; within this source tree it is the kernel TCP transport substrate that any Ceph client TCP connection relies on.

## Important APIs, Types, and Functions

Key global state includes `struct inet_hashinfo tcp_hashinfo`, per-CPU IPv4 TCP control sockets in `ipv4_tcp_sk`, and `tcp_exit_batch_mutex` for serialized namespace teardown. `tcp_prot` is the central `struct proto` with socket operations such as `connect`, `recvmsg`, `sendmsg`, `backlog_rcv`, `hash`, and memory accounting hooks. `ipv4_specific` is the `inet_connection_sock_af_ops` table for IPv4 transmit, request creation, child socket creation, PMTU handling, and socket option handling.

Connection setup runs through `tcp_v4_pre_connect()` for cgroup/BPF connect checks and `tcp_v4_connect()` for AF_INET validation, source-route handling, route lookup, local address binding, SYN-SENT hashing, route rebinding after port selection, ISN/timestamp offset generation, Fast Open deferral, and final `tcp_connect()`.

Receive-side entry is `tcp_v4_rcv()`, which validates packet host type, TCP header length, checksum setup, socket lookup, request-socket migration, XFRM policy, TCP-AO/MD5/inbound hash checks, BPF/socket filters, TIME-WAIT handling, and dispatch to `tcp_v4_do_rcv()`. `tcp_v4_do_rcv()` is the socket-locked state dispatcher, using the established fast path, LISTEN cookie/request handling, `tcp_rcv_established()`, and `tcp_rcv_state_process()`.

Reset and ACK generation is handled by `tcp_v4_send_reset()`, `tcp_v4_send_ack()`, `tcp_v4_timewait_ack()`, and `tcp_v4_reqsk_send_ack()`. SYN-ACK output is `tcp_v4_send_synack()`. ICMP/error handling is centered on `tcp_v4_err()`, `tcp_v4_mtu_reduced()`, `tcp_req_err()`, and `tcp_ld_RTO_revert()`.

MD5 support under `CONFIG_TCP_MD5SIG` adds key lookup/add/delete/copy helpers, option parsing through `tcp_v4_parse_md5_keys()`, and hash construction through `tcp_v4_md5_hash_hdr()` and `tcp_v4_md5_hash_skb()`. TCP-AO hooks are integrated beside MD5 for reset and request ACK signing.

Observability APIs include procfs iterators for `/proc/net/tcp`, `tcp_seq_start()`, `tcp_seq_next()`, `tcp_seq_stop()`, and `tcp4_seq_show()`, plus BPF iterator support that batches sockets safely across listening and established hash buckets.

## Control Flow

Outgoing connect starts by checking address length and family, resolving source route options, performing `ip_route_connect()`, rejecting multicast/broadcast routes, updating the bind hash source address if necessary, clearing stale timestamp state if the destination changed, and moving the socket to `TCP_SYN_SENT`. The socket is then inserted through `inet_hash_connect()`, route ports are updated after ephemeral port selection, capabilities are installed from the route, sequence/timestamp offsets are seeded unless TCP repair owns them, and Fast Open or normal `tcp_connect()` sends the SYN. Failures unwind by returning to `TCP_CLOSE`, resetting bind source address, dropping the route, clearing route capabilities, and clearing `inet_dport`.

Incoming packets enter `tcp_v4_rcv()`. The function performs cheap validation first, then looks up established, listening, request, or TIME-WAIT sockets. `TCP_NEW_SYN_RECV` requests are protected by the listener, can migrate via reuseport, and then are completed via `tcp_check_req()`. Normal sockets pass minimum TTL, XFRM, TCP-AO/MD5 hash, filter, and callback-fill checks before either entering `tcp_v4_do_rcv()` immediately or being coalesced/queued by `tcp_add_backlog()` if owned by userspace. No-socket packets get RSTs when policy and checksum allow. TIME-WAIT packets call `tcp_timewait_state_process()` and may ACK, reset, accept a valid reopening SYN through a listener, or drop.

`tcp_add_backlog()` is an important congestion/memory side path: it validates checksum, tries to coalesce adjacent compatible backlog SKBs, updates sequence/ACK/timestamp metadata, and enforces a backlog memory limit derived from receive and send buffer sizes plus headroom.

## State and Persistence

Persistent runtime state is held in sockets, request sockets, TIME-WAIT sockets, route/dst cache references, and network namespace `ipv4` fields. `tcp_sk_init()` seeds per-net sysctls including ECN, MSS probing, keepalive, retries, TIME-WAIT reuse, SACK, timestamps, RACK, Fast Open, pacing, PLB, and RTO bounds. `tcp_set_hashinfo()` either assigns global `tcp_hashinfo` or allocates per-net hashinfo according to `sysctl_tcp_child_ehash_entries`.

Per-CPU control sockets are created in `tcp_v4_init()` and used for RST/ACK output outside normal socket context. These sockets temporarily inherit net namespace, mark, priority, XFRM policy, and transmit timing from the target socket. Namespace exit uses `tcp_sk_exit_batch()` to purge TIME-WAIT sockets, free per-net hashinfo, decrement death-row references, and destroy Fast Open context under `tcp_exit_batch_mutex`.

MD5/AO key material is socket-attached and RCU-managed. TIME-WAIT and request paths copy or derive enough authentication state to sign challenge ACKs, resets, and SYN-ACK/ACK responses after the full socket is unavailable.

## Dependencies and Integration Points

The file depends on IPv4 routing (`ip_route_connect`, `ip_queue_xmit`, `ip_send_unicast_reply`), inet hash tables, request sockets, TCP core input/output/timer APIs, XFRM policy, netfilter connection tracking reset, cgroup/BPF connect hooks, BPF socket filters and iterators, MPTCP reset options, PSP policy checks, TCP-AO, TCP-MD5, syncookies, Fast Open, procfs, and per-net namespace registration.

Important cross-file integrations in this subset include `tcp_timewait_state_process()` and `tcp_child_process()` from `tcp_minisocks.c`, cached route/metrics consumed by `tcp_metrics.c`, congestion-control setup for passive opens via `tcp_ca_openreq_child()`, and offload registration in `tcp_offload.c` feeding SKBs that eventually reach this receive path.

## Risks

Risk centers on concurrency and protocol edge cases. Socket lookup and request migration rely on correct reference handling across RCU, listener locks, bottom-half locks, and reuseport migration. TIME-WAIT reopening, syncookies, TCP Fast Open, TCP-AO, and MD5 all add special cases where missing a refcount, option validation, or key lookup can cause incorrect drops or unauthenticated responses. Reset/ACK output runs from per-CPU control sockets and must restore namespace/policy state accurately.

Path MTU and ICMP handling are sensitive to spoofing and sequence validation. `tcp_v4_err()` mitigates with established lookup, sequence-window checks, TCP-AO ICMP filtering, minimum TTL checks, and soft-vs-hard error rules. Backlog coalescing is performance-critical but must preserve flags, options, ECN/AccECN bits, timestamps, PSP metadata, and accounting.

## Test Signals

Useful signals include IPv4 connect success/failure paths, PMTU blackhole and ICMP FRAG_NEEDED behavior, ICMP unreachable handling in SYN-SENT and established states, TIME-WAIT reuse and reopening, syncookie accept, TCP Fast Open accept, MD5 and AO signed reset/ACK/SYN-ACK interoperability, `/proc/net/tcp` output under listening/established/TIME-WAIT/request sockets, BPF iterator traversal across hash buckets, namespace teardown with active TIME-WAIT sockets, packet drop reason counters, checksum error counters, backlog coalescing counters, and KASAN/KCSAN/lockdep coverage under concurrent accept/close/receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ipv4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_lp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_lp.c

## Purpose

`tcp_lp.c` implements the TCP Low Priority congestion-control module named `lp`. TCP-LP attempts to use excess bandwidth without competing aggressively with normal TCP flows. It detects early congestion from one-way delay inferred from TCP timestamps, then suppresses Reno growth or reduces `snd_cwnd`.

## Important APIs, Types, and Functions

The private congestion-control state is `struct lp`, stored in `inet_csk_ca(sk)`. It tracks flags, smoothed one-way delay (`sowd` shifted by three), minimum/maximum OWD, a reserved max, remote timestamp clock estimate, remote/local reference timestamps, last drop time, and the current inference interval. `enum tcp_lp_state` defines validity and inference flags.

`tcp_lp_init()` initializes per-socket state. `tcp_lp_cong_avoid()` delegates to `tcp_reno_cong_avoid()` only when the algorithm is outside an inference interval. `tcp_lp_remote_hz_estimator()` estimates the peer timestamp frequency from changes in received timestamp value and echoed timestamp. `tcp_lp_owd_calculator()` converts remote and local timestamp domains into a relative OWD estimate. `tcp_lp_rtt_sample()` updates min/max and smoothed OWD. `tcp_lp_pkts_acked()` is the main decision hook called from ACK processing. `tcp_lp_register()` and `tcp_lp_unregister()` register the `tcp_congestion_ops`.

## Control Flow

On ACK samples, `tcp_lp_pkts_acked()` optionally feeds RTT into `tcp_lp_rtt_sample()`, computes the inference interval as three times the positive difference between local TCP timestamp and echoed timestamp, and sets `LP_WITHIN_INF` if the last drop is still within that interval. It then compares smoothed OWD against `owd_min + 15% * (owd_max - owd_min)`. If below threshold, the connection is considered non-congested and returns.

When the smoothed OWD exceeds the threshold, min/max delay windows are reset around current smoothed OWD. If still within inference, TCP-LP forces congestion window to one packet. Otherwise it halves `snd_cwnd`, bounded at one. The drop time is recorded so later ACKs suppress Reno growth during the inference interval.

Remote HZ estimation is continually updated using a 63/64 old plus 1/64 new filter. OWD is valid only after both remote HZ and timestamp-derived delay are positive.

## State and Persistence

State is per TCP socket and lives only for the socket lifetime in the congestion-control private area. The module has no global mutable policy knobs beyond registration. It depends on peer timestamp availability; without valid remote HZ/OWD, ACK samples do not affect congestion state.

## Dependencies and Integration Points

The module integrates through Linux pluggable congestion control via `struct tcp_congestion_ops`. It uses TCP core helpers including `tcp_sk()`, `tcp_time_stamp_ts()`, `tcp_snd_cwnd()`, `tcp_snd_cwnd_set()`, `tcp_reno_cong_avoid()`, `tcp_reno_ssthresh()`, and `tcp_reno_undo_cwnd()`. It depends on TCP timestamp negotiation and `tp->rx_opt.rcv_tsval/rcv_tsecr`.

## Risks

The algorithm is sensitive to timestamp quality, clock scaling, delayed ACK behavior, and asymmetric paths. Integer division in OWD calculation uses `LP_RESOL / remote_hz`, so unusual remote timestamp frequencies can reduce precision. If OWD min/max become stale, the code comments note that threshold behavior can become unsuitable. Aggressive cwnd reduction to one packet during inference can sharply reduce throughput.

## Test Signals

Test with `lp` selected as congestion control and timestamps enabled. Useful signals include cwnd evolution under increasing queue delay, behavior when timestamps are absent or constant, module registration/unregistration, `pr_debug` traces, fairness against Reno/CUBIC flows, recovery after delay decreases, and ensuring `BUILD_BUG_ON(sizeof(struct lp) > ICSK_CA_PRIV_SIZE)` remains satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_metrics.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_minisocks.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_minisocks.c

## Purpose

`tcp_minisocks.c` implements TCP mini-socket behavior: TIME-WAIT sockets, request sockets in SYN-RECV, and creation/processing of full child sockets from completed passive opens. It contains protocol edge handling shared by IPv4 and IPv6 paths, including PAWS, ECN/AccECN inheritance, TCP-MD5/AO TIME-WAIT support, request validation, deferred accept, and child socket dispatch.

## Important APIs, Types, and Functions

TIME-WAIT handling centers on `tcp_timewait_state_process()`, `tcp_time_wait()`, `tcp_time_wait_init()`, `tcp_twsk_destructor()`, and `tcp_twsk_purge()`. Request/child setup uses `tcp_openreq_init_rwin()`, `tcp_ecn_openreq_child()`, `tcp_ca_openreq_child()`, and `tcp_create_openreq_child()`. SYN-RECV packet validation and completion is `tcp_check_req()`. Established child packet handling is `tcp_child_process()`.

Small helpers include `tcp_in_window()` for sequence-window checks, `tcp_timewait_check_oow_rate_limit()` for out-of-window ACK throttling, `twsk_rcv_nxt_update()` for receive-next and AO SNE updates, and `smc_check_reset_syn_req()` for SMC negotiation cleanup.

## Control Flow

`tcp_timewait_state_process()` first parses timestamps when available and performs PAWS checks. FIN-WAIT-2 mini-sockets repeat receive-window checks, ignore duplicate ACKs, reset on new data after half-close, and transition to true TIME-WAIT when the expected FIN arrives. True TIME-WAIT accepts in-window RST/ACK according to RFC1337 policy, updates timestamp state, reschedules timers, and can accept a new SYN if it is not a duplicate and has a safe sequence/timestamp. Out-of-window non-RST packets trigger rate-limited ACKs.

`tcp_time_wait()` allocates an `inet_timewait_sock`, copies mark, priority, window scaling, receive/send sequence, receive window, timestamps, tx delay, queue mappings, IPv6 metadata when applicable, MD5/AO state, and schedules the hashdance. It enforces a timeout at least derived from RTO and uses fixed `TCP_TIMEWAIT_LEN` for true TIME-WAIT. It then updates TCP metrics and closes the original socket.

`tcp_create_openreq_child()` clones the listener, seeds receive/send sequence variables from the request, initializes timers, timestamp options, window scaling, MSS clamp, ECN/AccECN state, Fast Open fields, BPF socket state, user-frag xarray, and passive-open counters.

`tcp_check_req()` validates packets for request sockets. It handles retransmitted SYNs by retransmitting SYN-ACK with rate limiting, rejects invalid ACKs, PAWS failures, TSecr failures, and out-of-window segments, handles RST/SYN errors, tracks AccECN option observations, supports Fast Open short-circuiting, honors `TCP_DEFER_ACCEPT`, creates child sockets, records RTT, and completes the hashdance.

## State and Persistence

Mini-socket state persists only during handshake or TIME-WAIT. TIME-WAIT sockets store enough connection state to validate late packets and generate ACK/RST responses without a full socket. Request sockets store SYN-derived negotiation state until completion or timeout. Child sockets inherit listener configuration plus request-negotiated options.

MD5 keys may be copied into TIME-WAIT and child sockets. AO state is copied or destroyed through TCP-AO helpers. Congestion control for a child can be selected from route metrics or inherited/defaulted by `tcp_ca_openreq_child()`.

## Dependencies and Integration Points

The file integrates tightly with `tcp_ipv4.c` and IPv6 equivalents through request ops and child creation callbacks. It depends on TCP core state processing, inet connection socket cloning, inet timewait hashdance, dst route metrics, ECN/AccECN helpers, XFRM indirectly through callers, PSP policy, busy poll/NAPI marking, SMC, TCP-AO, TCP-MD5, BPF socket clone hooks, and TCP metrics update.

## Risks

Handshake and TIME-WAIT logic is protocol-edge-heavy. Risks include TIME-WAIT assassination policy, accepting reopening SYNs safely, stale timestamp/PAWS decisions, incorrect request ownership during hashdance, listener overflow behavior, Fast Open reset handling, and dropping or accepting bare ACKs under deferred accept. Concurrency is delicate because request sockets can be stolen, migrated, dropped, or completed by another CPU while packets are being processed.

## Test Signals

Exercise passive opens, SYN retransmission, syncookie/TFO paths, deferred accept, accept-queue overflow with and without abort-on-overflow, TIME-WAIT ACK/RST/new-SYN behavior, FIN-WAIT-2 mini-socket transition, PAWS/TSecr rejection counters, AccECN negotiation/failure modes, MD5/AO child and TIME-WAIT signing, route-selected congestion control on passive open, namespace TIME-WAIT purge, and lockdep/refcount coverage during concurrent accept and packet arrival.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_minisocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_nv.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_nv.c

## Purpose

`tcp_nv.c` implements the `nv` TCP congestion-control module. TCP-NV is a Vegas-like congestion-avoidance algorithm aimed primarily at data-center environments where flows can use queue buildup rather than loss as the congestion signal. It estimates current delivery rate and minimum RTT to compute a target congestion window, then adjusts growth and reductions around that target.

## Important APIs, Types, and Functions

Module parameters tune behavior: `nv_pad`, `nv_pad_buffer`, `nv_reset_period`, `nv_min_cwnd`, `nv_cong_dec_mult`, `nv_ssthresh_factor`, `nv_rtt_factor`, `nv_loss_dec_factor`, `nv_cwnd_growth_rate_neg`, `nv_cwnd_growth_rate_pos`, `nv_dec_eval_min_calls`, `nv_inc_eval_min_calls`, `nv_ssthresh_eval_min_calls`, `nv_stop_rtt_cnt`, and `nv_rtt_min_cnt`.

`struct tcpnv` is the per-socket private state. It tracks RTT reset timing, growth factor, growth/catch-up/reset flags, evaluation counters, adaptive minimum cwnd, last/min/new/base/lower-bound RTTs, max rate per RTT, RTT round start sequence, last `snd_una`, and consecutive no-congestion count.

Core functions are `tcpnv_init()`, `tcpnv_reset()`, `nv_get_bounded_rtt()`, `tcpnv_cong_avoid()`, `tcpnv_recalc_ssthresh()`, `tcpnv_state()`, `tcpnv_acked()`, and `tcpnv_get_info()`. Registration is through `tcp_register_congestion_control()`.

## Control Flow

Initialization resets counters, optionally gets a BPF-provided base RTT with `BPF_SOCK_OPS_BASE_RTT`, sets a lower bound at about 80% of base RTT, enables cwnd growth, and initializes min RTT tracking. Congestion avoidance grows only when cwnd-limited and `nv_allow_cwnd_growth` is set. Slow start uses the TCP core slow-start helper, then additive increase uses a count derived from `cwnd_growth_factor`.

ACK processing in `tcpnv_acked()` ignores duplicate/no-timestamp samples and non-open/non-disorder CA states. It computes bytes newly ACKed, averages RTT according to `nv_rtt_factor`, estimates rate from in-flight bytes and RTT, tracks max rate for the current RTT, updates min RTT windows, and periodically resets active min RTT to the newly observed min with randomized timing around `nv_reset_period`.

Once an RTT round completes, it computes `cwnd_by_slope = max_rate * min_rtt / (80000 * mss)` and `max_win = cwnd_by_slope + nv_pad`. If current cwnd is above `max_win`, and enough samples/RTTs have been collected, it disables growth, updates ssthresh, and reduces cwnd proportionally to the excess. If cwnd is below `max_win - nv_pad_buffer`, and enough samples exist, it enables growth and may adjust the growth factor. Otherwise it leaves cwnd unchanged. Loss/CWR/recovery states disable growth and mark reset; loss can reduce growth rate.

## State and Persistence

All algorithm state is per socket in `ICSK_CA_PRIV_SIZE`. Module parameters are global and mutable through module parameter sysfs permissions where exposed. Diagnostic state is available through `tcpnv_get_info()` using the Vegas info netlink attribute, reporting enabled state, RTT count, last RTT, and min RTT.

## Dependencies and Integration Points

The module depends on TCP core congestion-control callbacks, ACK samples, `tcp_call_bpf()` for optional base RTT, `tcp_slow_start()`, `tcp_cong_avoid_ai()`, `tcp_is_cwnd_limited()`, inet diag Vegas info compatibility, random bytes for min-RTT reset jitter, and module registration.

## Risks

TCP-NV is explicitly tuned for environments where competing flows also use NV or similar avoidance; it can be unfair against loss-based congestion controls. RTT noise from interrupt moderation, LRO/TSO, ACK aggregation, or reverse-path congestion can produce wrong queue estimates. The adaptive minimum cwnd and sample-count gates mitigate sparse ACK samples but add complexity. Integer fixed-point parameters require careful bounds to avoid overly aggressive growth or reduction.

## Test Signals

Test selecting `nv` as congestion control, module parameter changes, cwnd and ssthresh evolution under controlled queue buildup, loss recovery and return to open state, BPF base RTT injection, inet diag Vegas info output, min RTT reset timing, behavior with high NIC coalescing, fairness among NV flows and against CUBIC/Reno, and `BUILD_BUG_ON(sizeof(struct tcpnv) > ICSK_CA_PRIV_SIZE)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_nv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_offload.c

## Purpose

`tcp_offload.c` provides IPv4 TCP segmentation and receive offload glue. It registers TCPv4 GSO/GRO callbacks with the IPv4 protocol offload table and implements common TCP GSO/GRO helpers that split large TCP SKBs on transmit and aggregate compatible TCP packets on receive.

## Important APIs, Types, and Functions

Transmit segmentation paths include `tcp4_gso_segment()`, `tcp_gso_segment()`, `__tcp4_gso_segment_list()`, `__tcpv4_gso_segment_list_csum()`, `__tcpv4_gso_segment_csum()`, and `tcp_gso_tstamp()`. Receive aggregation paths include `tcp_gro_lookup()`, `tcp_gro_receive()`, `tcp_gro_complete()`, `tcp4_check_fraglist_gro()`, `tcp4_gro_receive()`, and `tcp4_gro_complete()`. `tcpv4_offload_init()` installs these callbacks into `net_hotdata.tcpv4_offload` and calls `inet_add_offload()`.

## Control Flow

`tcp4_gso_segment()` first verifies the SKB is TCPv4 GSO and has a pullable TCP header. For fraglist GSO, it can segment via list processing if the frame is already a valid single-MSS fraglist and not dodgy; otherwise it forces checksum recomputation. If checksum state is not partial, it builds the TCPv4 pseudo-header checksum before delegating to `tcp_gso_segment()`.

`tcp_gso_segment()` validates header length and checksum start, pulls the TCP header, checks MSS, and either lets hardware handle robust GSO or software-segments with `skb_segment()`. It updates sequence numbers, FIN/PSH/CWR flags, checksums, transmit timestamp ownership, `ooo_okay`, and TCP Small Queue destructor/accounting so completion accounting follows the final segment.

`tcp_gro_receive()` searches for an existing same-flow packet by TCP ports, compares flags, ACK sequence, options, network flush criteria, MSS, sequence continuity, and decrypted state, then aggregates through SKB GRO helpers when safe. It forces flush on small final segments and on urgent, push, reset, SYN, or FIN flags. `tcp_gro_complete()` marks the aggregate as checksum-partial GSO and carries AccECN CWR state in the GSO type.

`tcp4_check_fraglist_gro()` enables fraglist GRO only when the device supports it and no established socket is found for the flow. `tcp4_gro_complete()` finalizes either fraglist GSO metadata or normal TCPv4 pseudo-header checksum and fixed-IP-ID flags.

## State and Persistence

The file has no long-lived per-flow state. It mutates SKB metadata, shared-info GSO/GRO fields, checksums, destructor/sk ownership, timestamp flags, and NAPI GRO control blocks. Registration state persists in the IPv4 offload table after `tcpv4_offload_init()`.

## Dependencies and Integration Points

Dependencies include SKB segmentation/GRO core, checksum helpers, NAPI GRO metadata, IPv4 pseudo-header checksum, protocol offload registration, established socket lookup for fraglist GRO, netdevice feature flags, TCP Small Queues destructor `tcp_wfree`, and GSO type flags including TCPv4, fraglist, fixed IP ID, and AccECN.

## Risks

Offload code is high-risk for checksum, sequence, and accounting bugs. Incorrect segmentation can corrupt TCP streams, misplace FIN/PSH/CWR flags, lose transmit timestamps, or break TCP Small Queue memory accounting. GRO aggregation must reject flows with differing options, ACKs, flags, encryption state, MSS, or sequence continuity. Fraglist GRO depends on socket lookup and device support; wrong selection can hand unsupported packet shapes to the stack or hardware.

## Test Signals

Validate software GSO and hardware GSO fallback, fraglist GSO checksum rewriting after address/port changes, GRO aggregation and forced flush cases, AccECN CWR propagation, transmit timestamp selection across segments, TSQ destructor/accounting under large writes, checksum correctness with CHECKSUM_PARTIAL and CHECKSUM_NONE inputs, GRO fraglist behavior with and without established sockets, and packetdrill or selftests for segmented FIN/PSH/SYN/RST boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_offload.c -->
