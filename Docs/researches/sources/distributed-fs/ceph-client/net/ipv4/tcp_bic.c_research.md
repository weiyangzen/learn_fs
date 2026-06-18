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
