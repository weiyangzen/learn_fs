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
