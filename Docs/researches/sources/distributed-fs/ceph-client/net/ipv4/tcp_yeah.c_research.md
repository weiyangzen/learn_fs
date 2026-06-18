# sources/distributed-fs/ceph-client/net/ipv4/tcp_yeah.c

## Purpose

`tcp_yeah.c` implements YeAH TCP, a hybrid congestion-control algorithm that combines Scalable TCP-style fast growth with Vegas-style queue estimation and Reno-friendly fallback. It aims to use high-speed growth when queues are small and become more conservative when persistent queueing or competition is detected.

## Important APIs, Types, and Functions

The private `struct yeah` embeds `struct vegas` as its first field and adds `lastQ`, `doing_reno_now`, `reno_count`, and `fast_count`. Main callbacks are `tcp_yeah_init()`, `tcp_yeah_cong_avoid()`, and `tcp_yeah_ssthresh()`. The congestion ops reuse `tcp_vegas_state()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, `tcp_vegas_get_info()`, and `tcp_vegas_pkts_acked()`.

## Control Flow

Initialization calls `tcp_vegas_init()`, clears YeAH mode counters, sets `reno_count` to 2, and clamps maximum cwnd so multiplicative-decrease arithmetic cannot overflow. On ACKs, `tcp_yeah_cong_avoid()` requires cwnd-limited sending, applies slow start first, then uses Scalable additive increase when not in Reno mode or Reno additive increase when `doing_reno_now` is set.

At the end of each RTT, detected via the embedded Vegas `beg_snd_nxt`, YeAH uses Vegas RTT samples if there are more than two. It estimates queue size as `cwnd * (rtt - baseRTT) / rtt`. If queue exceeds `TCP_YEAH_ALPHA` or RTT inflation exceeds `baseRTT / TCP_YEAH_PHY`, it may reduce cwnd by the smaller of queue-based reduction and `cwnd >> TCP_YEAH_EPSILON`, bounded by `reno_count`, updates ssthresh, increments or seeds `reno_count`, and increases `doing_reno_now`. If queueing is low, it increments `fast_count`, resets `reno_count` after sustained fast operation, and leaves Reno mode. It then advances Vegas RTT boundaries and clears per-RTT samples.

On loss, `tcp_yeah_ssthresh()` uses `lastQ` to reduce less than Reno when the flow has not spent enough consecutive RTTs in Reno mode; otherwise it halves cwnd. It resets `fast_count`, halves `reno_count`, and returns cwnd minus the computed reduction clamped to at least 2.

## State and Persistence Behavior

State is per socket in CA private storage. Embedded Vegas fields track RTT sampling and boundaries. YeAH fields persist queue estimate, Reno-mode duration, fast-mode count, and Reno-count floor across RTTs and loss events. No durable state exists.

## Dependencies and Integration Points

YeAH depends on `tcp_vegas.h` and exported Vegas callbacks, TCP congestion-control registration, slow-start/additive-increase helpers, cwnd clamp, and inet_diag Vegas-compatible reporting. The `struct vegas` prefix layout is an important integration contract.

## Risks and Edge Cases

The hybrid behavior is sensitive to RTT minima and delayed ACK sampling. If base RTT is stale or queue estimates are noisy, YeAH can switch modes or reduce cwnd incorrectly. The embedded-struct layout must remain compatible with Vegas callbacks. Competition detection through `doing_reno_now` and `reno_count` is heuristic and may not be fair against modern controllers.

## Test Signals

Tests should verify module registration, `ICSK_CA_PRIV_SIZE` build check, Vegas sampling reuse, Scalable versus Reno growth modes, queue-triggered cwnd reduction, `fast_count` reset of `reno_count`, loss ssthresh behavior before and after `TCP_YEAH_RHO`, and inet_diag info. Network tests should observe mode switching under induced queueing and fairness against Reno/CUBIC.
