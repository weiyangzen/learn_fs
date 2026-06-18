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
