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
