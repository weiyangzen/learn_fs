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
