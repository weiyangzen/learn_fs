# Research Report: subset-b-006208

This grouped report covers TCP output, recovery, timer, ULP, signature-pool, congestion-control, PLB, and IPv4 XFRM tunnel sources under `sources/distributed-fs/ceph-client/net/ipv4/`. Each source file section is delimited for reconciliation into source-tree-aligned per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_output.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_output.c

## Purpose

`tcp_output.c` is the Linux TCP transmit-side engine. It turns queued stream data and control events into TCP segments, computes and writes TCP options, manages send and retransmit queues, implements sender-side flow/congestion gating, drives TSO/GSO sizing, pacing, TCP Small Queues, Tail Loss Probe, MTU probing, SYN/SYNACK construction, pure ACK emission, FIN/RST emission, zero-window probes, and active-open setup. It is central to TCP correctness because it owns sequence advancement, `snd_nxt`/`write_seq` transitions, packet accounting, retransmit metadata, and handoff to the IPv4/IPv6 `queue_xmit` path.

## Important APIs, Types, and Functions

The file exports or provides key transmit APIs including `tcp_mstamp_refresh()`, `tcp_rbtree_insert()`, `tcp_select_initial_window()`, `tcp_cwnd_restart()`, `tcp_fragment()`, `tcp_trim_head()`, `tcp_mtu_to_mss()`, `tcp_mss_to_mtu()`, `tcp_mtup_init()`, `tcp_sync_mss()`, `tcp_current_mss()`, `tcp_chrono_stop()`, `tcp_skb_collapse_tstamp()`, `__tcp_retransmit_skb()`, `tcp_retransmit_skb()`, `tcp_xmit_retransmit_queue()`, `tcp_send_fin()`, `tcp_send_active_reset()`, `tcp_send_synack()`, `tcp_make_synack()`, `tcp_connect()`, `tcp_delack_max()`, `tcp_send_delayed_ack()`, `__tcp_send_ack()`, `tcp_send_ack()`, `tcp_send_window_probe()`, `tcp_write_wakeup()`, `tcp_send_probe0()`, and `tcp_rtx_synack()`. Internally, `tcp_write_xmit()` is the main send loop and `__tcp_transmit_skb()` is the packet builder/transmitter.

The main local type is `struct tcp_out_options`, a pre-wire-format option plan containing MSS, SACK block count, BPF option length, window scale, timestamps, Fast Open cookie, MPTCP options, AccECN sizing, and an overloaded `hash_location` used by MD5/AO signing. `struct tsq_work` backs per-CPU TCP Small Queues deferred work. The code relies heavily on `struct tcp_sock`, `struct inet_connection_sock`, `struct sk_buff`, `struct tcp_skb_cb`, retransmit queue RB trees, the write queue list, and the `tsorted_sent_queue`.

## Control Flow

New application data enters the write queue through helpers such as `tcp_queue_skb()` and is pushed by `__tcp_push_pending_frames()` or `tcp_push_one()`. The core `tcp_write_xmit()` loop refreshes the TCP timestamp, optionally attempts MTU probing, checks pacing, computes congestion-window quota, grows/coalesces the head skb when possible, recalculates TSO segmentation, enforces send-window and Nagle/Minshall rules, optionally fragments oversized TSO frames, applies TCP Small Queue throttling, calls `tcp_transmit_skb()`, and then moves the skb from the write queue to the retransmit RB tree via `tcp_event_new_data_sent()`. It updates cwnd validation, PRR accounting, and schedules TLP when data was sent.

`__tcp_transmit_skb()` is the final packet assembly path for original sends and retransmits. It clones or copies the skb when requested, computes TCP options for SYN or established packets, pushes the TCP header, attaches ownership/destructor accounting, fills sequence/ACK/window/control bits, applies urgent pointer and ECN/AccECN state, writes options in strict compatibility order, computes MD5 or TCP-AO MACs when configured, lets cgroup BPF append header options last, computes IPv4/IPv6 checksums, updates ACK/data statistics, GSO metadata, pacing timestamps, and sends through `icsk_af_ops->queue_xmit`.

SYN/SYNACK control flow is split between active and passive open paths. `tcp_connect()` validates MD5/AO configuration, rebuilds route headers, initializes per-connection MSS/window/congestion-control state in `tcp_connect_init()`, allocates and queues the SYN, handles ECN SYN setup, inserts into the retransmit queue, optionally sends Fast Open data with `tcp_send_syn_data()`, updates `snd_nxt`/`pushed_seq`, and arms the retransmit timer. Passive open uses `tcp_make_synack()` to allocate a standalone SYNACK skb, derive request-socket options, include Fast Open/MPTCP/SMC/AccECN/authentication options, and return it to AF-specific send code; `tcp_rtx_synack()` handles retransmission and stats.

Retransmission flow is centered on `__tcp_retransmit_skb()` and `tcp_xmit_retransmit_queue()`. Retransmit trims already-acked bytes, rebuilds route headers, respects a shrunken receive window, fragments to available window and MSS, collapses adjacent retransmit skbs when legal, clears ECN SYN fallback bits after repeated retries, updates retransmission stats and timestamps, and calls `tcp_transmit_skb()`. Queue scanning transmits lost but not already retransmitted packets while respecting cwnd, pacing, TSQ, and PRR.

ACK, FIN, RST, and probe paths allocate minimal control skbs. `__tcp_send_ack()` sends pure ACKs outside the write queue and backs off delayed ACK timer on allocation failure. `tcp_send_fin()` appends FIN to the queued tail or creates a new FIN skb. `tcp_send_active_reset()` emits an untracked RST at an acceptable sequence. `tcp_write_wakeup()` and `tcp_send_probe0()` send partial data or zero-window probes and manage probe backoff.

## State and Persistence Behavior

The file mutates persistent per-socket transport state, not durable storage. Important fields include `snd_nxt`, `write_seq`, `snd_una`, `snd_wnd`, `snd_sml`, `snd_up`, `rcv_wnd`, `rcv_wup`, `window_clamp`, `mss_cache`, `packets_out`, `sacked_out`, `lost_out`, `retrans_out`, `total_retrans`, `bytes_sent`, `bytes_retrans`, pacing timestamps, `tcp_mstamp`, `tcp_wstamp_ns`, `tsorted_sent_queue`, `highest_sack`, `retransmit_skb_hint`, `tlp_high_seq`, `tlp_retrans`, MTU probe state, and ACK compression counters. The write queue and retransmit queue are the main in-memory persistence structures across ACKs, timers, and retransmission events.

Memory accounting is explicit: skb queueing charges `sk_wmem_queued` and socket memory, transmit ownership increments `sk_wmem_alloc`, and `tcp_wfree()` releases TSQ pressure and schedules deferred send work. Authentication and option state are read from per-socket MD5/AO, MPTCP, SMC, Fast Open, ECN, and BPF configuration.

## Dependencies and Integration Points

The file integrates with `net/tcp.h`, `tcp_ecn.h`, MPTCP, SMC, PSP enqueue metadata, cgroup BPF sockops, MD5 and TCP-AO authentication, IPv4/IPv6 AF operations, dst metrics, sysctls under `net->ipv4`, congestion-control callbacks, timers in `tcp_timer.c`, recovery logic in `tcp_recovery.c`, input-side ACK/recovery accounting, tracepoints, SNMP/MIB counters, fq/pacing, and the generic skb/page-frag memory model. It is invoked by sendmsg, connect, close, ACK scheduling, retransmit timers, keepalive/probe timers, and passive-open request-socket code.

## Risks and Edge Cases

The main risks are sequence/accounting corruption when fragmenting, trimming, collapsing, or moving skbs between queues; option-space overflow or wrong option ordering; incorrect MD5/AO hash placement; races between socket ownership, timers, TSQ callbacks, and skb destructors; stale pacing timestamps causing unexpected stalls; wrong window-shrink handling; retransmitting packets still queued in the host stack; and mismatched memory accounting on clone/copy/error paths. Feature interactions are dense: AccECN may alter MSS, MPTCP options take precedence over SACK, SMC/MPTCP/Fast Open compete for SYN option space, BPF writes options last, and TCP-AO/MD5 disable or constrain other options.

Particularly sensitive branches include zero-window probing versus normal RTO handling, Fast Open SYN-data fallback, SYNACK cookie behavior without skb ownership, AO missing-key rejection, MTU probe coalescing from multiple write skbs, and TSQ throttling where TX completion can race the throttled bit.

## Test Signals

Useful signals include TCP selftests for fastopen, md5sig, TCP-AO, mptcp, BPF sockops header options, ECN/AccECN, retransmission and TLP behavior, zero-window probes, keepalive/probe timers, and PMTU/MTU probing. Runtime validation should watch `TCP_MIB_OUTSEGS`, `TCP_MIB_RETRANSSEGS`, `LINUX_MIB_TCPORIGDATASENT`, `LINUX_MIB_TCPLOSSPROBES`, `LINUX_MIB_TCPRETRANSFAIL`, zero-window MIBs, TSQ throttling behavior, tracepoints `trace_tcp_retransmit_skb`, `trace_tcp_send_reset`, and packet captures verifying option order, sequence numbers, ACK numbers, window scaling, GSO segmentation, and authentication MACs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_plb.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_plb.c

## Purpose

`tcp_plb.c` implements TCP Protective Load Balancing state updates. PLB is a host-side datacenter load-balancing optimization that uses persistent transport congestion signals to trigger a transmit hash change, allowing ECMP/WCMP fabrics to place later packets on a different path. The implementation deliberately favors rehashing after idle periods or sustained congestion, and suppresses rehashing for a randomized interval after RTO to avoid returning traffic to a suspected black-holed path.

## Important APIs, Types, and Functions

The exported API is `tcp_plb_update_state()`, `tcp_plb_check_rehash()`, and `tcp_plb_update_state_upon_rto()`. All operate on `struct tcp_plb_state`, whose important fields here are `consec_cong_rounds` and `pause_until`. The functions use per-network-namespace sysctls: `sysctl_tcp_plb_enabled`, `sysctl_tcp_plb_cong_thresh`, `sysctl_tcp_plb_rehash_rounds`, `sysctl_tcp_plb_idle_rehash_rounds`, and `sysctl_tcp_plb_suspend_rto_sec`.

## Control Flow

`tcp_plb_update_state()` is called once per RTT with a congestion ratio. If PLB is disabled it returns. Nonnegative ratios below the threshold clear `consec_cong_rounds`; ratios at or above the threshold increment the counter up to the configured forced-rehash threshold.

`tcp_plb_check_rehash()` evaluates whether the counter reached the forced threshold or the lower idle threshold while `packets_out` is zero. It then validates `pause_until`, clearing stale or wrapped pause windows. If not paused, it calls `sk_rethink_txhash()`, clears the congestion-round counter, increments `tcp_sk(sk)->plb_rehash`, and updates `LINUX_MIB_TCPPLBREHASH`.

`tcp_plb_update_state_upon_rto()` is called on RTO. It chooses a randomized pause between one and two configured suspension intervals, stores `pause_until`, and resets congestion rounds because RTO itself may already have caused a path/hash rethink.

## State and Persistence Behavior

State is per connection in `struct tcp_plb_state` and `tcp_sock::plb_rehash`. It persists for the socket lifetime and is driven by RTT rounds and RTO events. No durable state exists. The jiffies-based `pause_until` explicitly handles wraparound and stale long pauses.

## Dependencies and Integration Points

The module depends on TCP congestion accounting elsewhere to supply `cong_ratio`, on `tcp_jiffies32`, `tcp_sk(sk)->packets_out`, `sk_rethink_txhash()`, per-net IPv4 sysctls, random number generation, and Linux TCP MIB counters. It is intended for TCP flows whose transmit hash affects underlay path choice.

## Risks and Edge Cases

Too aggressive thresholds can cause reordering from path changes, while too conservative thresholds hide persistent imbalance. RTO suspension must be long enough to avoid oscillating back to bad paths. Because this code uses jiffies arithmetic, wrap handling in `tcp_plb_check_rehash()` is important. Rehashing while packets are in flight is allowed for forced rehash but may increase reordering risk.

## Test Signals

Tests should exercise disabled PLB, below-threshold reset, threshold accumulation, forced rehash, idle rehash with no packets out, RTO suspension suppression, pause expiry, and jiffies wrap simulations. Runtime signals include `tcp_sk(sk)->plb_rehash`, `LINUX_MIB_TCPPLBREHASH`, txhash changes, and packet reordering/loss metrics after rehash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_plb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_recovery.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_recovery.c

## Purpose

`tcp_recovery.c` implements transmit-side loss marking for RACK and NewReno. RACK, defined by RFC 8985, marks losses by elapsed send time relative to the most recently delivered later packet. NewReno support covers non-SACK recovery by marking the next unacked packet lost when duplicate ACK or partial-ACK conditions prove loss.

## Important APIs, Types, and Functions

Key functions are `tcp_rack_skb_timeout()`, `tcp_rack_mark_lost()`, `tcp_rack_reo_timeout()`, and `tcp_newreno_mark_lost()`. Internal helpers include `tcp_rack_reo_wnd()` and `tcp_rack_detect_loss()`. The file uses `tcp_sock::rack` fields, `reord_seen`, `sacked_out`, `reordering`, `srtt_us`, `tsorted_sent_queue`, retransmit queue skbs, and congestion states such as `TCP_CA_Recovery`.

## Control Flow

`tcp_rack_reo_wnd()` computes the reordering window. It returns zero when reordering has not been seen and the connection is already in recovery or has reached duplicate-ACK threshold, unless `TCP_RACK_NO_DUPTHRESH` disables that behavior. Otherwise it uses min RTT divided by four and linearly increases with DSACK-driven `reo_wnd_steps`, capped by smoothed RTT.

`tcp_rack_detect_loss()` scans `tsorted_sent_queue` in send-time order. It skips packets already marked lost but not retransmitted, stops once packets are not older than the current RACK reference, and computes remaining time with `tcp_rack_skb_timeout()`. Expired packets are marked lost and removed from the time-sorted list; nonexpired packets contribute to the maximum reordering timeout.

`tcp_rack_mark_lost()` runs the scan only when `tp->rack.advanced` says newly delivered information advanced RACK. If remaining timeout exists, it arms `ICSK_TIME_REO_TIMEOUT`. `tcp_rack_reo_timeout()` performs the delayed scan, enters recovery if newly marked losses reduced inflight and the socket was not already in recovery, optionally applies cwnd reduction, retransmits lost packets, and rearms RTO unless the retransmit timer is already pending.

`tcp_newreno_mark_lost()` handles non-SACK recovery. Before recovery it marks loss once duplicate ACK count reaches reordering threshold; during recovery it marks the head skb lost on ACK advancement. It fragments a multi-packet head skb down to one MSS before loss marking.

## State and Persistence Behavior

State lives in the socket: RACK timestamps and end sequence, `rack.advanced`, reordering-window steps, loss counters, skb `sacked` flags, and the `tsorted_sent_queue`. Timers persist pending reordering decisions through `ICSK_TIME_REO_TIMEOUT`. There is no durable state.

## Dependencies and Integration Points

This file depends on `tcp_output.c` for retransmission (`tcp_xmit_retransmit_queue()` and `tcp_fragment()`), on input-side ACK processing to update RACK references and DSACK/reordering state, on timer dispatch in `tcp_timer.c`, and on congestion-control recovery helpers such as `tcp_enter_recovery()` and `tcp_cwnd_reduction()`.

## Risks and Edge Cases

Loss marking too early harms reordered paths; too late delays recovery. The zero reordering window during dupthresh/recovery is intentionally aggressive but sensitive to `reord_seen` accuracy. The time-sorted queue must remain consistent when skbs are retransmitted, collapsed, or acknowledged. NewReno assumes a valid retransmit-queue head and must fragment GSO safely before marking one segment lost.

## Test Signals

Useful tests include packet reordering with and without DSACK, tail loss, RACK reordering timeout arming, RTO interaction, SACK versus non-SACK recovery, NewReno partial ACKs, GSO head fragmentation, and sysctl `tcp_recovery` variations. Observe `ICSK_TIME_REO_TIMEOUT`, `lost_out`, retransmission tracepoints, recovery state transitions, and recovery latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_scalable.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_scalable.c

## Purpose

`tcp_scalable.c` registers the Scalable TCP congestion-control algorithm. It is a compact module that increases cwnd by roughly 1 percent per RTT in congestion avoidance and reduces cwnd by one eighth on loss, targeting high-bandwidth long-delay links where Reno growth is too slow.

## Important APIs, Types, and Functions

The main callbacks are `tcp_scalable_cong_avoid()` and `tcp_scalable_ssthresh()`, installed in `struct tcp_congestion_ops tcp_scalable` with `.name = "scalable"`, `.undo_cwnd = tcp_reno_undo_cwnd`, and module init/exit registration through `tcp_register_congestion_control()` and `tcp_unregister_congestion_control()`.

## Control Flow

On ACKs, `tcp_scalable_cong_avoid()` first checks `tcp_is_cwnd_limited()`. In slow start it delegates to `tcp_slow_start()` and stops if all acked packets were consumed there. In congestion avoidance it calls `tcp_cong_avoid_ai()` with an additive-increase denominator of `min(cwnd, 100)`, producing faster growth for large windows than Reno. On loss, `tcp_scalable_ssthresh()` returns `cwnd - cwnd/8`, clamped to at least 2.

## State and Persistence Behavior

The module does not define private per-socket CA state. It mutates standard `tcp_sock` cwnd and ssthresh through core helpers. Registration persists while the module is loaded.

## Dependencies and Integration Points

It depends on the Linux TCP congestion-control framework, standard Reno undo, slow-start, and additive-increase helpers. Users select it by congestion-control name through normal TCP sysctl or socket configuration paths.

## Risks and Edge Cases

The algorithm can be aggressive relative to Reno and may be unfair or lossy on shared bottlenecks. Because it has no private state, behavior is simple but cannot distinguish random loss, queuing, or path changes. Correct cwnd-limited detection is important to avoid growing cwnd when the sender is application limited.

## Test Signals

Tests should verify registration, selection by name, cwnd growth only when cwnd-limited, slow-start handoff, ssthresh reduction by one eighth, undo behavior, and clamp to minimum cwnd 2. Network tests should compare throughput, loss, fairness, and RTT against Reno/CUBIC on long-fat paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_scalable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_sigpool.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_sigpool.c

## Purpose

`tcp_sigpool.c` provides a small shared pool of asynchronous hash transforms and per-CPU scratch buffers for TCP signing users such as TCP authentication mechanisms. It avoids each user permanently owning a full set of crypto resources while still allowing atomic/BH-safe hash request setup around packet processing.

## Important APIs, Types, and Functions

Exported APIs are `tcp_sigpool_alloc_ahash()`, `tcp_sigpool_release()`, `tcp_sigpool_get()`, `tcp_sigpool_start()`, `tcp_sigpool_end()`, `tcp_sigpool_algo()`, and `tcp_sigpool_hash_skb_data()`. `struct sigpool_entry` stores a base `crypto_ahash`, algorithm name, `kref`, and flags. `struct sigpool_scratch` is per-CPU and contains a `local_lock_t` plus an RCU-protected scratch pointer. `struct scratches_to_free` batches old scratch buffers for deferred RCU freeing.

## Control Flow

`tcp_sigpool_alloc_ahash()` is the slow path. Under `cpool_mutex`, it reserves per-CPU scratch space at least as large as requested, searches for an existing matching algorithm and increments or reinitializes its kref, or allocates a new pool slot. Allocation duplicates the algorithm string, creates a base ahash with `crypto_alloc_ahash()`, records whether a key is needed, and verifies the transform can be cloned.

Scratch growth in `sigpool_reserve_scratch()` allocates a new buffer per possible CPU, RCU-swaps it into the per-CPU pointer, frees offline/no-old buffers immediately, and defers online old buffers through `call_rcu()`. Cleanup is asynchronous: `tcp_sigpool_release()` drops a kref and schedules work when it reaches zero; `cpool_cleanup_work_cb()` frees zero-ref entries and releases scratch buffers if no entries remain active.

`tcp_sigpool_start()` enters `rcu_read_lock_bh()`, validates the pool id, clones the base ahash, allocates an atomic ahash request, locks the current CPU scratch with `local_lock_nested_bh()`, and returns the request and scratch in `struct tcp_sigpool`. `tcp_sigpool_end()` unlocks scratch, exits RCU BH, frees the request, and frees the cloned hash. `tcp_sigpool_hash_skb_data()` hashes TCP payload bytes after the header, page frags, and nested skb frags recursively using one-entry scatterlists and `crypto_ahash_update()`.

## State and Persistence Behavior

Pool state is process-global within the module: `cpool[]`, `cpool_populated`, `__scratch_size`, per-CPU scratch pointers, and the cleanup work item. References persist across TCP users until released. Scratch buffers persist while at least one pool entry is active and can grow but not shrink until all entries are unused.

## Dependencies and Integration Points

The module depends on the kernel crypto ahash API, RCU, CPU hotplug read locking, per-CPU local locks, workqueues, krefs, skbuff fragment traversal, and TCP header helpers. Signing code integrates by allocating a pool id, starting a per-packet hash context, hashing skb data, then ending and releasing references.

## Risks and Edge Cases

The most sensitive areas are refcount lifetime, RCU scratch replacement, and BH/local lock pairing. A caller must always pair successful `tcp_sigpool_start()` with `tcp_sigpool_end()`. Pool ids become invalid after release and cleanup, so users need their own lifetime discipline. Scratch reallocation can partially fail; the code updates `__scratch_size` only on success but still schedules old scratch freeing. Hashing recursive skb frags must avoid missing payload or hashing header bytes twice.

## Test Signals

Tests should cover duplicate algorithm allocation, reference get/release, cleanup after last release, scratch growth, allocation failure paths, invalid id warnings, start/end lock pairing under BH, algorithms that require keys, hash equivalence for linear skb data, paged frags, and nested frag lists. KASAN/KCSAN/lockdep and crypto selftests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_sigpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_timer.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_timer.c

## Purpose

`tcp_timer.c` implements TCP transmit-side timers: delayed ACK, retransmission/RTO, RACK reordering timeout dispatch, Tail Loss Probe dispatch, zero-window probe timeout, Fast Open SYNACK retransmission, keepalive, compressed ACK hrtimer, and timer initialization. It enforces retry limits, TCP_USER_TIMEOUT, orphan-resource policy, PMTU black-hole response, and timer deferral when sockets are owned by users.

## Important APIs, Types, and Functions

Public functions include `tcp_clamp_probe0_to_user_timeout()`, `tcp_delack_timer_handler()`, `tcp_retransmit_timer()`, `tcp_write_timer_handler()`, `tcp_syn_ack_timeout()`, `tcp_reset_keepalive_timer()`, `tcp_set_keepalive()`, and `tcp_init_xmit_timers()`. Internal helpers include `tcp_clamp_rto_to_user_timeout()`, `tcp_write_err()`, `tcp_out_of_resources()`, `tcp_orphan_retries()`, `tcp_mtu_probing()`, `tcp_model_timeout()`, `retransmits_timed_out()`, `tcp_write_timeout()`, `tcp_probe_timer()`, `tcp_update_rto_stats()`, `tcp_fastopen_synack_timer()`, `tcp_rtx_probe0_timed_out()`, `tcp_write_timer()`, `tcp_keepalive_timer()`, and `tcp_compressed_ack_kick()`.

## Control Flow

Delayed ACK timer flow starts in `tcp_delack_timer()`. It avoids locking if no ACK/compressed ACK is pending, otherwise locks the socket. If user-owned, work is deferred via `TCP_DELACK_TIMER_DEFERRED`; otherwise `tcp_delack_timer_handler()` checks compressed ACKs, pending state, reschedules if early, adjusts ATO on missed delayed ACKs, sends ACKs, and updates delayed ACK MIBs.

Write timer flow starts in `tcp_write_timer()`, which checks `icsk_pending`, locks the socket, and either dispatches `tcp_write_timer_handler()` or sets `TCP_WRITE_TIMER_DEFERRED`. The handler refreshes timestamps and switches on `ICSK_TIME_REO_TIMEOUT`, `ICSK_TIME_LOSS_PROBE`, `ICSK_TIME_RETRANS`, and `ICSK_TIME_PROBE0`, invoking RACK reordering timeout, TLP send, RTO retransmission, or zero-window probe logic.

RTO logic in `tcp_retransmit_timer()` handles passive Fast Open child SYNACK retransmission first. For established data, it validates `packets_out` and the retransmit queue head. If the peer has a zero window, it treats retransmits as probes and avoids normal timeout unless orphan/user-timeout policy expires. Otherwise it increments timeout MIBs, calls `tcp_write_timeout()` to handle retry exhaustion, black-hole MTU probing, BPF RTO callbacks, Fast Open/MPTCP black-hole detection, and txhash rethink. It then enters loss, updates RTO stats, retransmits the head skb, and applies linear or exponential backoff before arming the next retransmit timer.

Probe and keepalive flows enforce user-visible timeout semantics. `tcp_probe_timer()` sends zero-window probes while respecting `TCP_USER_TIMEOUT`, orphan retry policy, and resource pressure. `tcp_keepalive_timer()` handles FIN_WAIT2 orphan expiry, keepalive enablement, outstanding data suppression, probe counts, user-timeout override, active reset on timeout, and rescheduling.

## State and Persistence Behavior

Timer state is stored in `inet_connection_sock`: `icsk_pending`, `icsk_rto`, `icsk_backoff`, `icsk_retransmits`, delayed ACK state, probe counters/timestamps, user timeout, and timer objects. `tcp_sock` contributes `retrans_stamp`, `rto_stamp`, `total_rto`, `total_rto_recoveries`, `packets_out`, `snd_wnd`, `rcv_tstamp`, Fast Open request state, and compressed ACK counters. Timers hold socket references until callbacks complete or deferred release callbacks run.

## Dependencies and Integration Points

This file integrates with transmit routines in `tcp_output.c` (`tcp_retransmit_skb()`, `tcp_send_probe0()`, `tcp_write_wakeup()`, `tcp_send_ack()`, `tcp_rtx_synack()`), RACK in `tcp_recovery.c`, congestion state transitions, Fast Open, MPTCP, ECN, BPF sockops RTO callbacks, net namespace sysctls, orphan resource checks, dst negative advice/reset, socket locking, hrtimers, and MIB accounting.

## Risks and Edge Cases

Timer code is race-sensitive. It must not run protocol work while a user owns the socket unless it defers and holds a reference. Retry calculations combine jiffies, millisecond user timeouts, and optional microsecond TCP timestamps. Zero-window probes must avoid incorrectly timing out live peers that continue ACKing. Orphan cleanup intentionally violates ideal TCP persistence to protect the host, so resource-pressure thresholds are operationally important. Fast Open SYNACK retransmission differs from normal listener SYNACK retransmission and can affect accepted child sockets.

## Test Signals

Validation should cover delayed ACK scheduling/deferral, compressed ACK hrtimer, RTO backoff, thin-stream linear timeout, TCP_USER_TIMEOUT for retransmits and zero-window probes, orphan timeout/resource aborts, PMTU black-hole probing, RACK/TLP timer dispatch, Fast Open SYNACK retries, keepalive timeout/reset, FIN_WAIT2 orphan behavior, and socket-owned timer deferral through `tcp_release_cb()`. Signals include `LINUX_MIB_TCPTIMEOUTS`, recovery-failure MIBs, abort MIBs, delayed ACK MIBs, retransmission tracepoints, timer pending state, and packet-level retransmit/probe timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ulp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_ulp.c

## Purpose

`tcp_ulp.c` implements registration, lookup, attachment, update, listing, and cleanup for pluggable TCP upper-layer protocols such as TLS or other TCP ULP modules. It provides the mechanism behind selecting an ULP by name and binding ULP callbacks to a TCP socket.

## Important APIs, Types, and Functions

Exported functions are `tcp_register_ulp()`, `tcp_unregister_ulp()`, `tcp_get_available_ulp()`, `tcp_update_ulp()`, `tcp_cleanup_ulp()`, and `tcp_set_ulp()`. Internal helpers are `tcp_ulp_find()`, `__tcp_ulp_find_autoload()`, and `__tcp_set_ulp()`. The key type is `struct tcp_ulp_ops`, containing `name`, `owner`, `init`, optional `release`, optional `update`, optional `clone`, and list linkage.

## Control Flow

Registration takes `tcp_ulp_list_lock`, rejects duplicate names, and appends the ops to an RCU-protected global list. Unregistration deletes from the list and waits for `synchronize_rcu()`. Lookup is a linear RCU traversal. `__tcp_ulp_find_autoload()` first searches the list, optionally requests module `tcp-ulp-$name` for capable admins, searches again, and pins the module with `try_module_get()`.

`tcp_set_ulp()` requires the caller to own the socket, resolves the ops, and delegates to `__tcp_set_ulp()`. Attachment rejects sockets that already have a ULP, clears zero-copy support on the socket, rejects LISTEN sockets for ULPs without clone support, calls the ULP `init()` callback, stores `icsk_ulp_ops`, or releases the module reference on failure. Cleanup calls the ULP release callback if present, drops the module reference, and clears the pointer.

## State and Persistence Behavior

The global ULP registry persists while modules are registered. Per-socket ULP state is represented by `inet_connection_sock::icsk_ulp_ops` plus private state created by the ULP `init()` callback. Module references persist for attached sockets until `tcp_cleanup_ulp()`.

## Dependencies and Integration Points

The file depends on Linux lists, spinlocks, RCU, module autoloading, capability checks, socket ownership conventions, and the TCP connection socket. ULP modules call the register API at module init. Socket options or protocol setup call `tcp_set_ulp()` to attach by name. Clone/update hooks integrate with accept, proto replacement, and write-space changes.

## Risks and Edge Cases

Name lookup is linear but expected to be small. Module autoload is gated by `CAP_NET_ADMIN`. Failure to pair attachment cleanup would leak module references. Clearing `SOCK_SUPPORT_ZC` changes socket capabilities when a ULP is installed. LISTEN sockets require clone support because accepted children may need ULP state inheritance. `tcp_cleanup_ulp()` intentionally skips ownership assertions because destruction occurs after normal socket use.

## Test Signals

Tests should verify duplicate registration, unregister synchronization, available-name formatting and truncation warning, autoload success/failure, attach to established sockets, attach rejection for duplicate ULPs and unsupported LISTEN sockets, init failure cleanup, update callback dispatch, release callback dispatch, and module refcount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.c

## Purpose

`tcp_vegas.c` implements the TCP Vegas congestion-control module. Vegas estimates queuing by comparing current RTT with the minimum base RTT and adjusts cwnd once per RTT to keep an estimated number of extra packets in the network between configurable `alpha` and `beta` thresholds. This implementation uses Linux loss recovery unchanged and only supplies congestion-control callbacks.

## Important APIs, Types, and Functions

Exports include `tcp_vegas_init()`, `tcp_vegas_pkts_acked()`, `tcp_vegas_state()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, and `tcp_vegas_get_info()`, allowing YeAH and other modules to reuse Vegas sampling. Internal helpers are `vegas_enable()`, `vegas_disable()`, `tcp_vegas_ssthresh()`, and `tcp_vegas_cong_avoid()`. Module parameters are `alpha`, `beta`, and `gamma`. Per-socket state is `struct vegas` from `tcp_vegas.h`.

## Control Flow

Initialization sets `baseRTT` to a large sentinel and enables a fresh Vegas round. `tcp_vegas_pkts_acked()` ignores invalid RTT samples, adds one microsecond to avoid zero, min-filters `baseRTT`, min-filters `minRTT` for the current RTT, and increments `cntRTT`. State and cwnd-event callbacks disable sampling outside `TCP_CA_Open` and reset sampling after cwnd restart or idle transmit start.

`tcp_vegas_cong_avoid()` falls back to Reno when Vegas sampling is disabled. At the end of a Vegas RTT, detected when `ack` passes `beg_snd_nxt`, it advances the next RTT boundary. If there are too few RTT samples, it behaves like Reno. Otherwise it computes target cwnd as `cwnd * baseRTT / minRTT` and `diff = cwnd * (rtt - baseRTT) / baseRTT`. In slow start, `diff > gamma` exits to congestion avoidance and sets cwnd near target. In congestion avoidance, `diff > beta` decrements cwnd, `diff < alpha` increments cwnd, and in-range diff leaves cwnd unchanged. It clamps cwnd and resets the per-RTT sample counters.

## State and Persistence Behavior

Vegas stores only per-connection congestion-control private state in `ICSK_CA_PRIV_SIZE`: RTT minima, sample count, current RTT boundary, and enabled flag. Module parameters persist globally while the module is loaded. Diagnostic state is exposed through `INET_DIAG_VEGASINFO`.

## Dependencies and Integration Points

The module depends on Linux TCP congestion-control registration, Reno helpers for fallback/loss undo, ACK RTT sampling, inet_diag extension structures, and `tcp_vegas.h`. YeAH imports the exported Vegas callbacks and requires `struct vegas` to be first in its private state.

## Risks and Edge Cases

Vegas is sensitive to RTT sample quality; delayed ACKs and too few samples force Reno fallback. A stale `baseRTT` can understate congestion after route changes. The algorithm may underutilize paths when competing with more aggressive loss-based algorithms. Integer division and cwnd clamping must avoid zero cwnd; the implementation enforces a minimum of 2.

## Test Signals

Tests should verify module registration, parameter effects, RTT sampling, idle/recovery restart behavior, Reno fallback with insufficient samples, slow-start exit on `gamma`, additive/decrement decisions around `alpha`/`beta`, inet_diag Vegas info, and interoperability with YeAH. Network tests should observe queueing delay, throughput, and fairness against CUBIC/Reno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.h -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.h

## Purpose

`tcp_vegas.h` is the shared private-state and callback interface for Vegas-style congestion-control modules. It defines the `struct vegas` layout used by `tcp_vegas.c` and embedded as the first field of `struct yeah` in `tcp_yeah.c`, then declares reusable Vegas functions.

## Important APIs, Types, and Functions

The central type is `struct vegas`, containing `beg_snd_nxt`, `beg_snd_una`, `beg_snd_cwnd`, `doing_vegas_now`, `cntRTT`, `minRTT`, and `baseRTT`. Declared functions are `tcp_vegas_init()`, `tcp_vegas_state()`, `tcp_vegas_pkts_acked()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, and `tcp_vegas_get_info()`.

## Control Flow

The header has no executable control flow. It establishes the ABI between congestion modules and the Vegas implementation: modules install declared callbacks in `struct tcp_congestion_ops` or call them from their own wrappers.

## State and Persistence Behavior

The struct fields persist per socket inside congestion-control private storage. `beg_*` fields delimit an RTT-sized measurement window, `doing_vegas_now` controls active sampling, `cntRTT` and `minRTT` are reset each RTT, and `baseRTT` persists as the long-term propagation-delay estimate.

## Dependencies and Integration Points

It assumes inclusion in TCP congestion-control modules with access to `struct sock`, `struct ack_sample`, `enum tcp_ca_event`, and `union tcp_cc_info` definitions through surrounding TCP headers. The layout is important for YeAH because `struct yeah` embeds `struct vegas` first and reuses exported Vegas callbacks.

## Risks and Edge Cases

Changing `struct vegas` size or order can break modules that embed it or rely on `ICSK_CA_PRIV_SIZE` constraints. Declared functions are GPL-exported by `tcp_vegas.c`, so build configuration and module dependencies must ensure symbols are available.

## Test Signals

Build tests should cover Vegas and YeAH modules together, including `BUILD_BUG_ON(sizeof(... ) > ICSK_CA_PRIV_SIZE)` checks. Runtime tests should verify YeAH callbacks operate on the embedded Vegas prefix correctly and inet_diag reporting remains consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_veno.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_veno.c

## Purpose

`tcp_veno.c` implements TCP Veno, a Vegas-inspired congestion-control algorithm intended to improve behavior over wireless access networks. It estimates whether loss is likely due to congestion by comparing current RTT with base RTT, then uses different cwnd increase and multiplicative decrease behavior for congestive versus non-congestive states.

## Important APIs, Types, and Functions

The file defines private `struct veno` with `doing_veno_now`, RTT counters/minima, `inc`, and `diff`. Callbacks include `tcp_veno_init()`, `tcp_veno_pkts_acked()`, `tcp_veno_state()`, `tcp_veno_cwnd_event()`, `tcp_veno_cwnd_event_tx_start()`, `tcp_veno_cong_avoid()`, and `tcp_veno_ssthresh()`. These are registered in `struct tcp_congestion_ops tcp_veno` under `.name = "veno"`.

## Control Flow

Initialization sets `basertt` to a large sentinel, initializes `inc`, and enables sampling. ACK sampling tracks the minimum base RTT and per-round minimum RTT with zero protection. State callbacks enable sampling only in open congestion state and reset after cwnd restart or idle transmit start.

`tcp_veno_cong_avoid()` falls back to Reno if sampling is disabled and returns when not cwnd-limited. With two or fewer RTT samples, it uses Reno. Otherwise it computes `target_cwnd = cwnd * basertt / minrtt` in fixed-point form and sets `diff` to the estimated excess. Slow start uses standard TCP slow start first. In congestion avoidance, if `diff < beta`, Veno increases every RTT using `tcp_cong_avoid_ai(tp, cwnd, acked)`; otherwise it increases only every other RTT using the `inc` toggle and `snd_cwnd_cnt`. `tcp_veno_ssthresh()` cuts cwnd by one fifth when `diff < beta`, otherwise by half.

## State and Persistence Behavior

Veno state is per socket in congestion-control private storage. `basertt` persists as the propagation estimate, while `minrtt` is reset after each congestion-avoidance pass. `cntrtt` is incremented by ACK sampling and notably is not reset in the active code, matching the file's commented-out reset line.

## Dependencies and Integration Points

The module depends on TCP congestion-control registration, Reno fallback/undo helpers, ACK RTT samples, `tcp_is_cwnd_limited()`, and standard cwnd/ssthresh helpers. It is selectable by congestion-control name while the module is loaded.

## Risks and Edge Cases

Wireless-loss classification depends on `diff` accuracy and RTT sampling; stale or noisy base RTT can misclassify congestion. The retained `cntrtt` behavior means once enough samples have been collected, Reno fallback for insufficient samples will rarely recur until reinit. Integer fixed-point arithmetic must stay within cwnd clamp. The algorithm can be unfair when competing with more aggressive controllers.

## Test Signals

Tests should verify registration, initialization, RTT sampling, state toggles, cwnd-limited gating, Reno fallback before enough samples, non-congestive versus congestive increase paths, the every-other-RTT toggle, ssthresh one-fifth versus half reductions, and behavior after idle restart/RTO recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_veno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_westwood.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_westwood.c

## Purpose

`tcp_westwood.c` implements TCP Westwood+, a congestion-control module that estimates end-to-end bandwidth from returning ACKs and uses bandwidth-delay product estimates to set cwnd/ssthresh after congestion events. Its probing phase remains Reno-like, while loss response uses measured bandwidth and minimum RTT.

## Important APIs, Types, and Functions

Private `struct westwood` stores bandwidth estimates, RTT window start, bytes acknowledged in the current estimation bucket, sequence tracking, delayed/duplicate ACK accounting, current/min RTT, and flags. Important callbacks are `tcp_westwood_init()`, `tcp_westwood_pkts_acked()`, `tcp_westwood_ack()`, `tcp_westwood_event()`, and `tcp_westwood_info()`, registered in `tcp_westwood` with Reno `ssthresh`, `cong_avoid`, and `undo_cwnd`.

## Control Flow

Initialization clears bandwidth accounting, sets RTT/min RTT to a conservative initial value, records current `snd_una`, and marks the first ACK. `tcp_westwood_pkts_acked()` records the latest RTT sample in jiffies. `westwood_update_window()` checks whether at least max(current RTT, 50 ms) elapsed since the current bandwidth window; when elapsed, it filters `bk / delta` into `bw_ns_est` and then `bw_est`, clears `bk`, and starts a new window.

ACK processing is split into fast and slow paths. Fast path calls `westwood_fast_bw()`, updates the bandwidth window, adds newly acknowledged bytes from `snd_una` movement, updates `snd_una`, and min-filters RTT. Slow path accounts for duplicate ACKs and delayed/partial ACKs through `westwood_acked_count()` so `bk` reflects likely acknowledged bytes even when `snd_una` does not advance normally.

On `CA_EVENT_COMPLETE_CWR`, Westwood sets ssthresh and cwnd to `bw_est * rtt_min / mss_cache`, clamped to at least 2. On `CA_EVENT_LOSS`, it sets ssthresh to the same estimate and resets RTT-min tracking for the next ACK. Diagnostic output reuses the Vegas inet_diag info attribute to report current and minimum RTT.

## State and Persistence Behavior

All algorithm state is per socket in CA private storage. Bandwidth estimates persist across RTT windows and loss events. `reset_rtt_min` causes the next ACK to seed a fresh min-RTT interval after loss. Module registration persists while loaded.

## Dependencies and Integration Points

Westwood integrates with TCP congestion-control callbacks, ACK-event flags (`CA_ACK_SLOWPATH`), Reno congestion avoidance, inet_diag Vegas-compatible info, jiffies timing, and standard TCP sequence/cwnd helpers. It depends on accurate ACK processing and RTT samples from the core TCP input path.

## Risks and Edge Cases

Bandwidth estimation can be skewed by ACK compression, delayed ACKs, duplicate ACK accounting, very small RTT windows, or application-limited sending. `mss_cache` must be nonzero for BDP conversion. Reusing Vegas diagnostic attributes may surprise tooling expecting actual Vegas semantics. The initial RTT is intentionally conservative and can affect early loss response.

## Test Signals

Tests should cover registration, initial state, fast/slow ACK accounting, duplicate and delayed ACK behavior, bandwidth filtering, RTT-min reset after loss, cwnd/ssthresh update on CWR/loss, inet_diag info, and throughput behavior on lossy wireless-like links and ACK-compressed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_westwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_yeah.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_yeah.c

## Purpose

`tcp_yeah.c` implements YeAH TCP, a hybrid congestion-control algorithm that combines Scalable TCP-style fast growth with Vegas-style queue estimation and Reno-friendly fallback. It aims to use high-speed growth when queues are small and become more conservative when persistent queueing or competition is detected.

## Important APIs, Types, and Functions

The private `struct yeah` embeds `struct vegas` as its first field and adds `lastQ`, `doing_reno_now`, `reno_count`, and `fast_count`. Main callbacks are `tcp_yeah_init()`, `tcp_yeah_cong_avoid()`, and `tcp_yeah_ssthresh()`. The congestion ops reuse `tcp_vegas_state()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, `tcp_vegas_get_info()`, and `tcp_vegas_pkts_acked()`.

## Control Flow

Initialization calls `tcp_vegas_init()`, clears YeAH mode counters, sets `reno_count` to 2, and clamps maximum cwnd so multiplicative-decrease arithmetic cannot overflow. On ACKs, `tcp_yeah_cong_avoid()` requires cwnd-limited sending, applies slow start first, then uses Scalable additive increase when not in Reno mode or Reno additive increase when `doing_reno_now` is set.

At the end of each RTT, detected via the embedded Vegas `beg_snd_nxt`, YeAH uses Vegas RTT samples if there are more than two. It estimates queue size as `cwnd * (rtt - baseRTT) / rtt`. If queue exceeds `TCP_YEAH_ALPHA` or RTT inflation exceeds `baseRTT / TCP_YEAH_PHY`, it may reduce cwnd by the smaller of queue-based reduction and `cwnd >> TCP_YEAH_EPSILON`, bounded by `reno_count`, updates ssthresh, increments or seeds `reno_count`, and increases `doing_reno_now`. If queueing is low, it increments `fast_count`, resets `reno_count` after sustained fast operation, and leaves Reno mode. It then advances Vegas RTT boundaries and clears per-RTT samples.

On loss, `tcp_yeah_ssthresh()` uses `lastQ` to reduce less than Reno when the flow has not spent enough consecutive RTTs in Reno mode; otherwise it halves cwnd. It resets `fast_count`, halves `reno_count`, and returns cwnd minus the computed reduction clamped to at least 2.

## State and Persistence Behavior

State is per socket in CA private storage. Embedded Vegas fields track RTT sampling and boundaries. YeAH fields persist queue estimate, Reno-mode duration, fast-mode count, and Reno-count floor across RTTs and loss events. No durable state exists.

## Dependencies and Integration Points

YeAH depends on `tcp_vegas.h` and exported Vegas callbacks, TCP congestion-control registration, slow-start/additive-increase helpers, cwnd clamp, and inet_diag Vegas-compatible reporting. The `struct vegas` prefix layout is an important integration contract.

## Risks and Edge Cases

The hybrid behavior is sensitive to RTT minima and delayed ACK sampling. If base RTT is stale or queue estimates are noisy, YeAH can switch modes or reduce cwnd incorrectly. The embedded-struct layout must remain compatible with Vegas callbacks. Competition detection through `doing_reno_now` and `reno_count` is heuristic and may not be fair against modern controllers.

## Test Signals

Tests should verify module registration, `ICSK_CA_PRIV_SIZE` build check, Vegas sampling reuse, Scalable versus Reno growth modes, queue-triggered cwnd reduction, `fast_count` reset of `reno_count`, loss ssthresh behavior before and after `TCP_YEAH_RHO`, and inet_diag info. Network tests should observe mode switching under induced queueing and fairness against Reno/CUBIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_yeah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tunnel4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tunnel4.c

## Purpose

`tunnel4.c` is the generic IPv4 XFRM tunnel dispatcher for IP-in-IP, IPv6-in-IPv4, and MPLS-in-IPv4 protocols. It lets tunnel implementations register prioritized `struct xfrm_tunnel` handlers and wires those handlers into the IPv4 protocol receive and ICMP error paths.

## Important APIs, Types, and Functions

Exported APIs are `xfrm4_tunnel_register()` and `xfrm4_tunnel_deregister()`. Internal state consists of three RCU handler lists: `tunnel4_handlers`, `tunnel64_handlers`, and `tunnelmpls4_handlers`, protected for updates by `tunnel4_mutex`. Helpers and callbacks include `fam_handlers()`, `tunnel4_rcv()`, optional `tunnel4_rcv_cb()`, `tunnel64_rcv()`, `tunnelmpls4_rcv()`, `tunnel4_err()`, `tunnel64_err()`, `tunnelmpls4_err()`, protocol descriptors, and module init/exit.

## Control Flow

Registration selects a handler list by family, locks the mutex, walks the RCU list in priority order, rejects duplicate priority, and inserts the handler before the first lower-priority entry. Deregistration removes the matching handler from the selected list, unlocks, and waits for `synchronize_net()` before returning.

Receive handlers first ensure enough header bytes are present with `pskb_may_pull()`. They iterate the relevant handler list under RCU and call each handler's `handler(skb)`. A return value of zero means the handler consumed the skb and receive processing succeeds. If no handler accepts the packet, the code sends ICMP destination/port unreachable and frees the skb. Error handlers similarly iterate and stop when a handler's `err_handler()` returns zero, otherwise returning `-ENOENT`.

Module init registers `net_protocol` handlers for `IPPROTO_IPIP`, optionally `IPPROTO_IPV6` and `IPPROTO_MPLS`, and optionally registers XFRM input AF info for tunnel callbacks. Failures unwind previously registered protocols. Module exit unregisters in reverse order and logs failures.

## State and Persistence Behavior

Handler lists are global module state and persist until handlers deregister or the module exits. RCU protects readers while mutex-protected updates mutate list links. No per-namespace or durable state is stored in this file.

## Dependencies and Integration Points

The file integrates with the IPv4 protocol table via `inet_add_protocol()`/`inet_del_protocol()`, XFRM tunnel handlers, optional IPv6/MPLS builds, optional `xfrm_input_afinfo`, ICMP error generation, skbuff header pulling/freeing, and RCU network synchronization. Registered tunnel modules supply the actual encapsulation-specific receive and error behavior.

## Risks and Edge Cases

Duplicate priorities are rejected, so independent tunnel modules must coordinate priority values. A handler that returns zero owns the skb; later handlers will not run. If no handler accepts traffic, ICMP unreachable is emitted, which can affect diagnostics and peer behavior. Optional build combinations require correct init unwind. Deregistration must wait for readers to avoid use-after-free.

## Test Signals

Tests should verify priority-ordered insertion, duplicate priority rejection, deregistration and `-ENOENT`, receive dispatch for IPIP/IPv6/MPLS, fallback ICMP unreachable and skb free, error dispatch, optional XFRM callback behavior, module init failure unwind, and RCU safety under concurrent receive and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tunnel4.c -->
