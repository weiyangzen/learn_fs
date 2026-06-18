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
