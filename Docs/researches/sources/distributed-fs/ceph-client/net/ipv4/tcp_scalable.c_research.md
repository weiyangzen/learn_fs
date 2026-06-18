# sources/distributed-fs/ceph-client/net/ipv4/tcp_scalable.c

## Purpose

`tcp_scalable.c` registers the Scalable TCP congestion-control algorithm. It is a compact module that increases cwnd by roughly 1 percent per RTT in congestion avoidance and reduces cwnd by one eighth on loss, targeting high-bandwidth long-delay links where Reno growth is too slow.

## Important APIs, Types, and Functions

The main callbacks are `tcp_scalable_cong_avoid()` and `tcp_scalable_ssthresh()`, installed in `struct tcp_congestion_ops tcp_scalable` with `.name = "scalable"`, `.undo_cwnd = tcp_reno_undo_cwnd`, and module init/exit registration through `tcp_register_congestion_control()` and `tcp_unregister_congestion_control()`.

## Control Flow

On ACKs, `tcp_scalable_cong_avoid()` first checks `tcp_is_cwnd_limited()`. In slow start it delegates to `tcp_slow_start()` and stops if all acked packets were consumed there. In congestion avoidance it calls `tcp_cong_avoid_ai()` with an additive-increase denominator of `min(cwnd, 100)`, producing faster growth for large windows than Reno. On loss, `tcp_scalable_ssthresh()` returns `cwnd - cwnd/8`, clamped to at least 2.

## State and Persistence Behavior

The module does not define private per-socket CA state. It mutates standard `tcp_sock` cwnd and ssthresh through core helpers. Registration persists while the module is loaded.

## Dependencies and Integration Points

It depends on the Linux TCP congestion-control framework, standard Reno undo, slow-start, and additive-increase helpers. Users select it by congestion-control name through normal TCP sysctl or socket configuration paths.

## Risks and Edge Cases

The algorithm can be aggressive relative to Reno and may be unfair or lossy on shared bottlenecks. Because it has no private state, behavior is simple but cannot distinguish random loss, queuing, or path changes. Correct cwnd-limited detection is important to avoid growing cwnd when the sender is application limited.

## Test Signals

Tests should verify registration, selection by name, cwnd growth only when cwnd-limited, slow-start handoff, ssthresh reduction by one eighth, undo behavior, and clamp to minimum cwnd 2. Network tests should compare throughput, loss, fairness, and RTT against Reno/CUBIC on long-fat paths.
