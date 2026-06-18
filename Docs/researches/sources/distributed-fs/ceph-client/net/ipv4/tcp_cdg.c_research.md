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
