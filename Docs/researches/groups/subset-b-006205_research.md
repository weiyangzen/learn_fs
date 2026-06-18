# Research: subset-b-006205

This grouped report covers Linux TCP congestion-control, diagnostics, BPF socket redirection, DCTCP, and TCP Fast Open sources under `sources/distributed-fs/ceph-client/net/ipv4/`. Each file section is bounded by reconciliation markers and preserves the source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bic.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_bic.c

## Purpose
`tcp_bic.c` implements the legacy BIC TCP congestion-control module named `bic`. It behaves like Reno for small congestion windows and switches to Binary Increase behavior for larger windows, using the last observed maximum cwnd as the search target after congestion.

## Important APIs, Types, And Functions
The file registers a `struct tcp_congestion_ops bictcp` with `.init`, `.ssthresh`, `.cong_avoid`, `.set_state`, `.undo_cwnd`, and `.pkts_acked`. Private per-socket state lives in `struct bictcp`, stored in `inet_csk_ca(sk)`, and includes the growth counter `cnt`, `last_max_cwnd`, cached `last_cwnd` and `last_time`, `epoch_start`, and a delayed-ACK estimator. Module parameters tune behavior: `fast_convergence`, `max_increment`, `low_window`, `beta`, `initial_ssthresh`, and `smooth_part`. `bictcp_register()` enforces the `ICSK_CA_PRIV_SIZE` limit and calls `tcp_register_congestion_control()`.

## Control Flow
`bictcp_init()` resets per-flow state and optionally overrides `snd_ssthresh`. On every ACK, `bictcp_cong_avoid()` first checks `tcp_is_cwnd_limited()`, performs normal `tcp_slow_start()` if applicable, then calls `bictcp_update()` to compute `ca->cnt` and delegates additive increase to `tcp_cong_avoid_ai()`. `bictcp_update()` throttles recalculation to avoid repeated work inside a short jiffy interval, then selects either Reno-like, binary-search, smooth-start, or linear growth depending on `cwnd` relative to `low_window` and `last_max_cwnd`. On congestion, `bictcp_recalc_ssthresh()` closes the epoch, applies fast convergence to `last_max_cwnd`, and returns a beta-scaled or Reno-half threshold. Entering `TCP_CA_Loss` resets the algorithm.

## State, Persistence, Dependencies, And Integration
All flow state is per-socket and transient. Persistent system-level tuning is exposed through module parameters. The module depends on core TCP helpers from `<net/tcp.h>`, jiffies timing, Reno undo, and the congestion-control registry in `tcp_cong.c`. It integrates with TCP through `tcp_congestion_ops`, so selection happens through sysctl or socket-level congestion-control APIs.

## Risks And Test Signals
Risk is concentrated in fixed-point arithmetic, delayed-ACK compensation, and module parameters that can make `cnt` too small or too aggressive. Test signals include successful module registration, selecting `bic` via `TCP_CONGESTION`, cwnd growth below and above `low_window`, loss-induced `ssthresh` and `last_max_cwnd` updates, delayed ACK samples changing growth, and loss-state reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bpf.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_bpf.c

## Purpose
`tcp_bpf.c` wires TCP sockets into sockmap/sk_msg BPF infrastructure. It replaces selected protocol operations for sockets with BPF programs attached, supports redirecting sendmsg data to another TCP socket or back into ingress queues, supports parser/verdict receive paths, and restores original protocol callbacks when BPF state is removed.

## Important APIs, Types, And Functions
Public functions include `tcp_eat_skb()`, `tcp_bpf_sendmsg_redir()`, `tcp_bpf_strp_read_sock()`, `tcp_bpf_update_proto()`, and `tcp_bpf_clone()`. Core private paths are `bpf_tcp_ingress()`, `tcp_bpf_push()`, `tcp_bpf_recvmsg_parser()`, `tcp_bpf_recvmsg()`, `tcp_bpf_send_verdict()`, and `tcp_bpf_sendmsg()`. It maintains `tcp_bpf_prots[TCP_BPF_NUM_PROTS][TCP_BPF_NUM_CFGS]`, covering IPv4/IPv6 and base, TX, RX, and TXRX configurations. The code is conditional on `CONFIG_BPF_SYSCALL`, with stream parser support additionally guarded by `CONFIG_BPF_STREAM_PARSER`.

## Control Flow
Transmit redirection enters through `tcp_bpf_sendmsg()` or exported `tcp_bpf_sendmsg_redir()`. User data is copied into `sk_msg`, evaluated by BPF verdict programs, and either pushed with `tcp_bpf_push()`, redirected through `tcp_bpf_sendmsg_redir()`, corked for later evaluation, or dropped with copied-byte adjustment. Receive-side paths use `tcp_bpf_recvmsg()` for queued sk_msg ingress and `tcp_bpf_recvmsg_parser()` for parser-backed streams; both wait on `sk_sleep()` when no data is available and fall back to `tcp_recvmsg()` when no psock or queued TCP data requires normal handling. `tcp_bpf_update_proto()` chooses the correct replacement proto based on installed parser/verdict programs, handles IPv6 proto rebuilds, and restores saved ULP/proto callbacks on teardown.

## State, Persistence, Dependencies, And Integration
Persistent state is socket-local in `struct sk_psock`, saved proto pointers, corked `sk_msg`, apply-bytes accounting, redirect sockets, copied sequence tracking, and ingress queues. Global state is the rebuilt proto table plus a saved IPv6 proto pointer protected by `tcpv6_prot_lock`. The file depends on skmsg, sockmap, stream parser, TLS ULP, TCP send/receive internals, wait queues, socket memory accounting, and proto replacement helpers.

## Risks And Test Signals
Key risks are lock ordering around `lock_sock()`, reference leaks on redirected sockets/pages, incorrect copied byte accounting after BPF cuts or drops, fallback assumptions checked by `tcp_bpf_assert_proto_ops()`, IPv6 proto rebuild races, and interaction with TLS ULP callbacks. Useful tests attach sockmap programs for TX, RX, and TXRX, exercise `SK_PASS`, `SK_DROP`, `SK_REDIRECT`, cork/apply-byte cases, parser FIN handling, `SIOCINQ`, TLS sockets, IPv6 sockets, accept-child cloning, and removal/restore of psock state under active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cdg.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_cdg.c

## Purpose
`tcp_cdg.c` implements CAIA Delay-Gradient TCP congestion control, module name `cdg`. It uses gradients between consecutive RTT windows to infer queue buildup and probabilistically backs off before packet loss, while retaining Reno-style growth and optional coexistence heuristics.

## Important APIs, Types, And Functions
Per-flow state is `struct cdg`, including current and previous RTT min/max, optional gradient ring buffer, summed gradients, delayed-ACK filter state, shadow window, backoff counters, and HyStart tracking. `struct cdg_minmax` stores paired min/max values. `tcp_cdg_cong_avoid()`, `tcp_cdg_acked()`, `tcp_cdg_ssthresh()`, `tcp_cdg_cwnd_event()`, `tcp_cdg_init()`, and `tcp_cdg_release()` populate `struct tcp_congestion_ops tcp_cdg`. Tunables include `window`, `backoff_beta`, `backoff_factor`, `hystart_detect`, `use_ineff`, `use_shadow`, and `use_tolerance`.

## Control Flow
RTT samples arrive through `tcp_cdg_acked()`, which filters delayed ACKs and updates per-round min/max RTT. `tcp_cdg_cong_avoid()` runs HyStart while in slow start, detects round boundaries with `rtt_seq`, computes a delay gradient with `tcp_cdg_grad()`, and if the gradient is positive calls `tcp_cdg_backoff()`. Backoff uses `nexp_u32()` and `get_random_u32()` to turn gradient magnitude into a probability; if triggered it enters CWR with `tcp_enter_cwr()`. If no backoff occurs, Reno congestion avoidance drives cwnd growth, and the shadow window tracks synthetic growth. `tcp_cdg_ssthresh()` chooses beta backoff, no reduction for tolerated non-full state, shadow-window reduction, or Reno half-window depending on CDG state and parameters.

## State, Persistence, Dependencies, And Integration
The gradient buffer is allocated per socket in `tcp_cdg_init()` with `GFP_NOWAIT` and released in `.release`; allocation failure degrades to `window == 1` behavior. All other state is per-socket transient. The module integrates through the congestion-control registry and uses TCP cwnd events for restart and CWR completion. It depends on kernel random numbers, scheduler clock support via TCP timestamps, TCP HyStart stats, and Reno helpers.

## Risks And Test Signals
Risks include invalid module parameter combinations, gradient-buffer allocation failure, probabilistic backoff variance, non-congestion-loss tolerance misclassification, delayed-ACK filtering errors, and shadow-window over- or under-reduction. Tests should validate parameter rejection for non-power-of-two or out-of-range windows, operation with allocation failure, HyStart exits, CWR transitions on rising delay, no leak in `.release`, and fallback behavior with `use_shadow`, `use_ineff`, and `use_tolerance` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cdg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cong.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_cong.c

## Purpose
`tcp_cong.c` is the core pluggable TCP congestion-control registry and the built-in Reno implementation. It manages registration, lookup, default and allowed algorithms, socket assignment and reinitialization, ECN negotiation for algorithms that need it, and shared cwnd growth helpers used by many modules and BPF struct_ops.

## Important APIs, Types, And Functions
The global registry is `tcp_cong_list`, protected for writes by `tcp_cong_list_lock` and read under RCU. Exported APIs include `tcp_register_congestion_control()`, `tcp_unregister_congestion_control()`, `tcp_update_congestion_control()`, `tcp_ca_get_key_by_name()`, `tcp_ca_get_name_by_key()`, `tcp_assign_congestion_control()`, `tcp_init_congestion_control()`, `tcp_cleanup_congestion_control()`, `tcp_set_default_congestion_control()`, `tcp_set_allowed_congestion_control()`, and `tcp_set_congestion_control()`. The shared kfunc/helpers are `tcp_slow_start()`, `tcp_cong_avoid_ai()`, `tcp_reno_cong_avoid()`, `tcp_reno_ssthresh()`, and `tcp_reno_undo_cwnd()`. `tcp_reno` is always non-restricted.

## Control Flow
Algorithms register by validating required callbacks, deriving a jhash key from the name, checking uniqueness, and appending to the RCU list. Socket creation uses `tcp_assign_congestion_control()` to take the netns default with module/BPF refcounting and zero private state. `tcp_init_congestion_control()` calls algorithm `.init` and sets ECN transmit mode. Switching a socket with `tcp_set_congestion_control()` checks destination lock, permissions, non-restricted flags, optional autoload, and module refs, then calls `tcp_reinit_congestion_control()`. Sysctl default changes use `xchg()` on `net->ipv4.tcp_congestion_control`; allowed-list changes parse and mark `TCP_CONG_NON_RESTRICTED`.

## State, Persistence, Dependencies, And Integration
Registry state is global RCU list membership and per-net default pointers. Per-socket state includes selected ops, private `icsk_ca_priv`, initialized flag, and user-set marker. The file depends on module loading, jhash, RCU, BPF module helpers, ECN helpers, tracepoints, and net namespace TCP settings. It is the integration point for all congestion-control modules in this group.

## Risks And Test Signals
Risks include duplicate key/name handling, module refcount lifetime, switching algorithms while initialized, restricted algorithm exposure outside `init_net`, RCU update ordering, and ECN state mismatches. Tests should register/unregister modules, autoload by name, set default and allowed algorithms, switch live sockets, verify cleanup `.release`, validate Reno cwnd behavior, verify kfunc availability for struct_ops, and ensure `TCP_CONG_NEEDS_ECN` triggers ECT negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cubic.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_cubic.c

## Purpose
`tcp_cubic.c` implements the default high-speed CUBIC congestion-control algorithm named `cubic`, including HyStart slow-start exit logic and BTF kfunc exposure for BPF struct_ops.

## Important APIs, Types, And Functions
Per-flow `struct bictcp` tracks CUBIC epoch state, last maximum cwnd, origin point, K, delay minimum, ACK counts, TCP-friendly shadow cwnd, and HyStart sampling. Important functions are `cubictcp_init()`, `cubictcp_cong_avoid()`, `cubictcp_recalc_ssthresh()`, `cubictcp_state()`, `cubictcp_cwnd_event_tx_start()`, `cubictcp_acked()`, `bictcp_update()`, `hystart_update()`, and `cubic_root()`. Tunables include `fast_convergence`, `beta`, `initial_ssthresh`, read-only `bic_scale`, `tcp_friendliness`, `hystart`, `hystart_detect`, `hystart_low_window`, and `hystart_ack_delta_us`. Registration precomputes `beta_scale`, `cube_rtt_scale`, and `cube_factor`.

## Control Flow
`cubictcp_init()` resets state and starts HyStart tracking. ACK processing in `cubictcp_cong_avoid()` performs slow start first, then computes a target cwnd from the cubic function in `bictcp_update()` and applies `tcp_cong_avoid_ai()`. The cubic update starts a new epoch after reductions, computes K using `cubic_root()`, evaluates distance from the origin, and bounds growth with TCP-friendliness and a maximum rate of one packet per two ACKed packets. RTT samples in `cubictcp_acked()` update `delay_min` and invoke HyStart while slow-starting. Loss ends the epoch in `cubictcp_recalc_ssthresh()` and updates `last_max_cwnd`; `TCP_CA_Loss` resets both CUBIC and HyStart state.

## State, Persistence, Dependencies, And Integration
Flow state is transient in `icsk_ca_priv`; module parameters and precomputed scale globals persist for the module lifetime. CUBIC integrates with TCP through `tcp_congestion_ops` and with BPF through `register_btf_kfunc_id_set(BPF_PROG_TYPE_STRUCT_OPS, ...)`. It depends on math64 division, BTF ids, pacing rate for HyStart ACK-delay cushion, TCP MIB HyStart counters, and Reno helpers.

## Risks And Test Signals
Risks include overflow or precision errors in fixed-point cubic math, invalid assumptions around cwnd and RTT ranges, HyStart false positives with pacing/GRO/TSO, stale epochs after application-limited idle periods, and kfunc registration failure preventing module registration. Tests should cover cubic root accuracy, scale-factor setup, cwnd growth after loss and idle restart, HyStart ACK-train and delay exits, `TCP_CA_Loss` reset, module parameter changes, and BPF struct_ops kfunc discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_cubic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.c

## Purpose
`tcp_dctcp.c` implements DataCenter TCP, module name `dctcp`, which uses ECN Congestion Experienced markings to estimate the fraction of marked packets per RTT and reduce cwnd proportionally. It falls back to a Reno-compatible internal ops table when ECN is unavailable on an established socket.

## Important APIs, Types, And Functions
`struct dctcp` stores delivered and delivered-CE snapshots, receive CE state, alpha, next sequence boundary, remembered loss cwnd, and PLB state. Main callbacks are `dctcp_init()`, `dctcp_update_alpha()`, `dctcp_cwnd_event()`, `dctcp_cwnd_event_tx_start()`, `dctcp_ssthresh()`, `dctcp_state()`, `dctcp_cwnd_undo()`, and `dctcp_get_info()`. `dctcp_shift_g` controls EWMA gain and is range-limited to 0..10; `dctcp_alpha_on_init` sets initial alpha. The file registers BTF kfunc ids for BPF struct_ops.

## Control Flow
Initialization permits DCTCP if ECN was negotiated or the socket is listen/close state; otherwise it switches `icsk_ca_ops` to `dctcp_reno` and clears ECT transmission. `dctcp_update_alpha()` runs on ACK events, detects an RTT boundary using `snd_una` and `next_seq`, computes delivered and CE-delivered deltas, updates PLB with instantaneous CE ratio, applies the DCTCP EWMA formula to `dctcp_alpha`, and resets delivered snapshots. `dctcp_ssthresh()` reduces cwnd by `alpha / 2`. Loss paths store `loss_cwnd`, set a Reno-half threshold, and allow `dctcp_cwnd_undo()` to restore at least the pre-loss cwnd. ECN receive events delegate CE ACK state transitions to `tcp_dctcp.h`.

## State, Persistence, Dependencies, And Integration
State is per-socket in `icsk_ca_priv`, with module parameters affecting all flows. The algorithm requires ECN and sets `TCP_CONG_NEEDS_ECN`, integrates with PLB helpers, inet_diag DCTCP info, BTF kfunc registration, and Reno growth. It includes `tcp_dctcp.h` for CE ACK logic.

## Risks And Test Signals
Risks include divide-by-zero or overflow around delivered counters, incorrect ECN fallback, stale alpha visible to diagnostics, PLB rehash behavior under CE bursts, and only-once-per-RTT loss handling. Tests should check ECN and non-ECN handshakes, alpha updates for zero, partial, and full CE marking, `dctcp_shift_g` parameter validation, DCTCP inet_diag output, RTO and recovery loss response, PLB state updates, and BPF kfunc registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.h -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.h

## Purpose
`tcp_dctcp.h` provides the minimal inline receive-side CE state machine used by DCTCP to reflect ECN Congestion Experienced state in outgoing ACKs. It is a small integration header, not a standalone module.

## Important APIs, Types, And Functions
`dctcp_ece_ack_cwr()` sets or clears `TCP_ECN_DEMAND_CWR` in `tcp_sk(sk)->ecn_flags` based on the current CE state. `dctcp_ece_ack_update()` accepts a TCP congestion-control event, prior receive-next pointer, and CE-state pointer. It translates `CA_EVENT_ECN_IS_CE` to state 1 and `CA_EVENT_ECN_NO_CE` to state 0.

## Control Flow
When the CE state changes, `dctcp_ece_ack_update()` first checks whether a delayed ACK timer is pending. If so, it temporarily restores the old CE state in the ACK flags and sends an immediate ACK for `prior_rcv_nxt`, preserving the previous feedback boundary. It then marks `ICSK_ACK_NOW` so the new state is acknowledged promptly, updates `prior_rcv_nxt` from `tcp_sk(sk)->rcv_nxt`, stores the new state, and calls `dctcp_ece_ack_cwr()` to update the outgoing ECE/CWR demand flag.

## State, Persistence, Dependencies, And Integration
The header mutates per-socket TCP ECN flags and caller-owned DCTCP state fields. It depends on `struct sock`, `struct tcp_sock`, `inet_csk(sk)->icsk_ack`, `__tcp_send_ack()`, and the `enum tcp_ca_event` values used by TCP ECN receive processing. Its direct integration point in this group is `dctcp_cwnd_event()` in `tcp_dctcp.c`.

## Risks And Test Signals
Risks are ACK ordering bugs at CE transitions, mishandling of delayed ACK state, and incorrect `prior_rcv_nxt` causing ambiguous CE feedback. Tests should feed alternating CE and non-CE receive events, verify immediate ACK generation when a delayed ACK is pending, confirm `TCP_ECN_DEMAND_CWR` state after each transition, and validate that DCTCP alpha accounting sees accurate delivered-CE signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_diag.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_diag.c

## Purpose
`tcp_diag.c` registers the TCP handler for SOCK_DIAG/INET_DIAG netlink monitoring. It dumps TCP socket state, one-socket lookups, optional destruction requests, TCP info, memory and queue data, MD5 signature metadata for privileged callers, and ULP-specific diagnostic data.

## Important APIs, Types, And Functions
The central registration object is `static const struct inet_diag_handler tcp_diag_handler`. Important functions are `tcp_diag_get_info()`, `tcp_diag_get_aux()`, `tcp_diag_get_aux_size()`, `tcp_twsk_diag_fill()`, `tcp_req_diag_fill()`, `sk_diag_fill()`, `tcp_diag_dump()`, `tcp_diag_find_one_icsk()`, `tcp_diag_dump_one()`, and optional `tcp_diag_destroy()`. MD5 helpers are conditional on `CONFIG_TCP_MD5SIG`; destroy support is conditional on `CONFIG_INET_DIAG_DESTROY`.

## Control Flow
Netlink dump requests enter `tcp_diag_dump()`. It walks listen hash buckets, bound-inactive sockets, and established hash buckets according to requested state masks and family/port/bytecode filters. To avoid holding bucket locks while filling skb messages, established and bound walks batch up to `SKARR_SZ` sockets with references, release locks, then call `inet_sk_diag_fill()` or `sk_diag_fill()`. Time-wait and request sockets have specialized fill functions because their layouts differ from full sockets. Single-socket requests use `tcp_diag_find_one_icsk()` to look up IPv4, IPv6, or v4-mapped flows, check cookies, allocate a reply skb sized by `tcp_diag_get_aux_size()`, and unicast the result.

## State, Persistence, Dependencies, And Integration
The file does not own persistent TCP state; it snapshots socket and request state under appropriate locks and references. It depends on inet hash tables, inet_diag common fill helpers, netlink capability checks, ULP callbacks, MD5 key storage, timewait layout compatibility, and per-net `diag_nlsk`. It integrates with user tools such as `ss` through NETLINK_SOCK_DIAG.

## Risks And Test Signals
Risks include bucket-walk cursor bugs, reference leaks, netns filtering mistakes, message-size underestimation causing `-EMSGSIZE`, leaking MD5 data without `CAP_NET_ADMIN`, and structure-layout assumptions for timewait/request sockets. Tests should dump listeners, established, timewait, SYN_RECV, and bound-inactive sockets; exercise IPv4, IPv6, and v4-mapped lookup; request ULP and MD5 attributes with and without privilege; validate continuation cursors under small receive buffers; and test optional destroy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_fastopen.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_fastopen.c

## Purpose
`tcp_fastopen.c` implements TCP Fast Open server and client support: cookie key management, cookie generation and validation, child socket creation from SYN data, SYN payload queuing, listener fastopen queue accounting, active-side deferred connect, and global blackhole detection/backoff for broken middleboxes.

## Important APIs, Types, And Functions
Public functions include `reqsk_fastopen_remove()`, `tcp_fastopen_init_key_once()`, `tcp_fastopen_destroy_cipher()`, `tcp_fastopen_ctx_destroy()`, `tcp_fastopen_reset_cipher()`, `tcp_fastopen_get_cipher()`, `tcp_fastopen_add_skb()`, `tcp_try_fastopen()`, `tcp_fastopen_cookie_check()`, `tcp_fastopen_defer_connect()`, `tcp_fastopen_active_disable()`, `tcp_fastopen_active_should_disable()`, `tcp_fastopen_active_disable_ofo_check()`, and `tcp_fastopen_active_detect_blackhole()`. Internal helpers cover RCU context freeing, SipHash cookie generation, cookie match checks against primary/backup keys, child creation, queue overflow checks, and no-cookie policy.

## Control Flow
Server-side SYN handling calls `tcp_try_fastopen()`. It checks sysctl enablement, SYN data or cookie request presence, and listener queue capacity. If no-cookie policy permits, or a presented cookie validates against primary/backup keys, `tcp_fastopen_create_child()` builds a full child socket before the handshake completes, links the request via `fastopen_rsk`, starts SYNACK retransmission, initializes TCP transfer state, and queues SYN payload with `tcp_fastopen_add_skb()`. Cookie requests or failed validation return a generated cookie without creating a child. Client-side connect calls `tcp_fastopen_cookie_check()` and `tcp_fastopen_defer_connect()` to decide whether SYN should wait for first write. Blackhole functions disable active TFO for exponential timeout periods when FIN/RST/ofo or timeout patterns indicate middlebox failure.

## State, Persistence, Dependencies, And Integration
TFO key contexts are RCU-published globally per netns or per listener queue and freed with `kfree_sensitive()`. Listener fastopen queues track `qlen`, maximum queue length, reset request list, and per-listener context under `fastopenq->lock`. Child sockets track `fastopen_rsk`, `syn_fastopen_child`, receive sequence adjustments, and SYN data flags. Active blackhole state persists in per-net IPv4 fields `tfo_active_disable_stamp` and `tfo_active_disable_times`. The file depends on request sockets, accept queues, RCU, SipHash, TCP metrics/cache helpers, route metrics, NAPI marking, and MIB counters.

## Risks And Test Signals
Risks include request-socket lifetime races between listener and child, queue accounting errors around reset-defense entries, RCU key replacement races, accepting invalid cookies, SYN payload sequence mistakes, backup-key rotation bugs, and overbroad active TFO disablement. Tests should cover cookie request, valid primary and backup cookies, invalid cookie fallback, no-cookie sysctl and route-metric paths, SYN data and SYN FIN queuing, accept and listener-close lifetime cases, max queue overflow and reset timeout recycling, key reset/get/destroy, deferred connect, and blackhole timeout escalation/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_fastopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_highspeed.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_highspeed.c

## Purpose
`tcp_highspeed.c` implements Sally Floyd's HighSpeed TCP congestion-control module named `highspeed`, based on RFC 3649. It uses a cwnd-indexed AIMD table to increase more aggressively and decrease less sharply at large windows.

## Important APIs, Types, And Functions
The fixed table `hstcp_aimd_vals[]` maps cwnd thresholds to multiplicative-decrease factors scaled by 256; the index is stored per socket in `struct hstcp { u32 ai; }`. The registered callbacks are `hstcp_init()`, `hstcp_cong_avoid()`, `hstcp_ssthresh()`, Reno undo, and the module register/unregister functions.

## Control Flow
`hstcp_init()` resets the table index and clamps `snd_cwnd_clamp` so multiplicative-decrease arithmetic cannot overflow. `hstcp_cong_avoid()` exits unless cwnd-limited. Slow start delegates to `tcp_slow_start()`. In congestion avoidance it adjusts `ca->ai` until the current cwnd lies within the table interval, then accumulates `ca->ai + 1` credits into `snd_cwnd_cnt`; when credits reach cwnd, it increases cwnd by one. On congestion, `hstcp_ssthresh()` subtracts `(cwnd * md) >> 8` using the table value for the current index and floors the threshold at two packets.

## State, Persistence, Dependencies, And Integration
State is per-socket and minimal: only the table index. The AIMD table is static read-only module data. The module depends on core TCP congestion helpers and registers with the common congestion-control list.

## Risks And Test Signals
Risks include off-by-one table index movement at thresholds, overflow despite clamp changes, incorrect slow-start leftover ACK handling, and poor behavior if `ai` is stale after cwnd drops. Tests should select `highspeed`, sweep cwnd across table thresholds in both directions, confirm additive increase scales with `ai`, validate ssthresh values for representative table rows, and exercise module registration and fallback to Reno undo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_highspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_htcp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_htcp.c

## Purpose
`tcp_htcp.c` implements H-TCP, a high-speed, long-distance congestion-control module named `htcp`. It adapts additive increase over time since last congestion and adapts multiplicative decrease using RTT and optional bandwidth-switch heuristics.

## Important APIs, Types, And Functions
`struct htcp` stores fixed-point `alpha` and `beta`, mode-switch state, acknowledged packet count, RTT min/max, last congestion timestamps, undo snapshots, and bandwidth-estimation fields. Core functions are `measure_achieved_throughput()`, `measure_rtt()`, `htcp_beta_update()`, `htcp_alpha_update()`, `htcp_param_update()`, `htcp_recalc_ssthresh()`, `htcp_cong_avoid()`, `htcp_state()`, and `htcp_cwnd_undo()`. Module parameters `use_rtt_scaling` and `use_bandwidth_switch` control adaptive components.

## Control Flow
ACK samples update RTT and achieved-throughput estimates. On loss/recovery state transitions, `htcp_state()` snapshots undo values and records the new congestion time. `htcp_recalc_ssthresh()` calls `htcp_param_update()`, which updates beta using bandwidth and RTT relationships, updates alpha based on time since congestion and optional RTT scaling, fades max RTT, and returns a beta-scaled threshold. During congestion avoidance, H-TCP increments `snd_cwnd_cnt` by recently acknowledged packets and grows cwnd when fixed-point alpha credits exceed cwnd, then recomputes alpha.

## State, Persistence, Dependencies, And Integration
All algorithm measurements are per-socket; module parameters are global. The algorithm integrates through `tcp_congestion_ops` and uses Reno undo as the final undo baseline after restoring H-TCP snapshots. It depends on jiffies, RTT conversion helpers, TCP ACK sampling, and module registration.

## Risks And Test Signals
Risks include jiffies wrap assumptions, RTT unit mistakes, beta clamping, bandwidth switch instability after route changes, undo state restoring stale max RTT or bandwidth, and `pkts_acked` handling when ACK samples are sparse. Tests should cover ACK sampling, congestion events, undo after spurious recovery, parameter toggles, RTT scaling with very low/high RTT, bandwidth switch changes around the 4/5 to 6/5 window, and module registration size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_htcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_hybla.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_hybla.c

## Purpose
`tcp_hybla.c` implements TCP Hybla, module name `hybla`, which compensates high-RTT paths by scaling slow-start and congestion-avoidance growth using a rho factor derived from measured RTT relative to a configurable reference RTT.

## Important APIs, Types, And Functions
`struct hybla` stores enable state, fractional cwnd credits, integer and fixed-point rho/rho-squared values, and minimum observed RTT. The key functions are `hybla_recalc_param()`, `hybla_init()`, `hybla_state()`, `hybla_fraction()`, and `hybla_cong_avoid()`. The module parameter `rtt0` is the reference RTT in milliseconds.

## Control Flow
Initialization sets cwnd/clamp, calculates rho from initial srtt, records minimum RTT, and sets cwnd to rho. On each congestion-avoidance call, the algorithm recalculates rho if a new minimum RTT appears. If the flow is not cwnd-limited, it returns. If Hybla is disabled because the CA state is not open, it delegates to Reno. In slow start it computes an exponential increment based on rho integer/fractional parts; outside slow start it computes `rho^2 / cwnd` in fixed-point units. Fractional increments are accumulated in `snd_cwnd_cents`, converted to packets when they reach 128, then cwnd is clamped to ssthresh and `snd_cwnd_clamp`.

## State, Persistence, Dependencies, And Integration
All growth state is per-socket; `rtt0` persists as a module parameter. The module integrates through TCP congestion ops and delegates ssthresh/undo to Reno. It depends on TCP srtt, cwnd helpers, and fixed-point tables for fractional powers.

## Risks And Test Signals
Risks include division by an invalid `rtt0`, excessive growth for high rho, fixed-point overflow in `1 << min(rho, 16)`, stale minimum RTT, and reduced behavior outside `TCP_CA_Open`. Tests should validate module parameter behavior, initialization with different RTTs, slow-start increments, congestion-avoidance fractional accumulation, state transitions to Reno fallback, cwnd clamp enforcement, and min-RTT recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_hybla.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_illinois.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_illinois.c

## Purpose
`tcp_illinois.c` implements TCP Illinois, a hybrid loss and delay based congestion-control module named `illinois`. It adapts additive increase alpha and multiplicative decrease beta from measured queueing delay, aiming for fast growth when delay is low and conservative behavior as delay rises.

## Important APIs, Types, And Functions
`struct illinois` tracks RTT sum/count, base and max RTT, round end sequence, alpha, beta, ACKed packet count, and hysteresis state for low-delay detection. Core functions are `tcp_illinois_init()`, `tcp_illinois_acked()`, `alpha()`, `beta()`, `update_params()`, `tcp_illinois_state()`, `tcp_illinois_cong_avoid()`, `tcp_illinois_ssthresh()`, and `tcp_illinois_info()`. Module parameters `win_thresh` and `theta` control when adaptive sizing starts and how many low-delay RTTs are required before returning to max alpha.

## Control Flow
ACK samples update base RTT, max RTT, sum, count, and latest ACKed packet count. `tcp_illinois_cong_avoid()` updates alpha and beta when ACK advances beyond `end_seq`, then applies slow start or fixed-point additive increase using current alpha. `update_params()` uses Reno-like alpha/beta below `win_thresh`; otherwise it computes average and maximum queueing delay, updates alpha through a convex function and beta through a delay-based linear function, and resets per-round RTT sampling. On loss, state resets alpha, beta, and hysteresis to baseline. `tcp_illinois_ssthresh()` reduces cwnd by the beta-scaled decrement. `tcp_illinois_info()` exposes Vegas-style diagnostic data through inet_diag.

## State, Persistence, Dependencies, And Integration
Flow state is per-socket and reset at initialization, round boundaries, and loss. Module parameters are global read-mostly values. The algorithm integrates through `tcp_congestion_ops`, uses Reno undo, uses inet_diag `INET_DIAG_VEGASINFO`, and depends on `do_div()` for RTT averages.

## Risks And Test Signals
Risks include RTT sample overflow, invalid average when `cnt_rtt` is zero, hysteresis delaying alpha recovery too long, beta becoming too aggressive under noisy max RTT, and diagnostic consumers interpreting Illinois data as Vegas-style fields. Tests should cover low/high delay alpha and beta regions, `win_thresh` Reno behavior, loss reset, round-boundary parameter updates, diagnostic info output, duplicate ACK samples without RTT, RTT clamp to `RTT_MAX`, and cwnd clamp enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_illinois.c -->
