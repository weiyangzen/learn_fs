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
