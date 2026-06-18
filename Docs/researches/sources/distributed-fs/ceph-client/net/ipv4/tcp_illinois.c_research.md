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
