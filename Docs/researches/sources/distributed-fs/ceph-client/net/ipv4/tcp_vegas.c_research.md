# sources/distributed-fs/ceph-client/net/ipv4/tcp_vegas.c

## Purpose

`tcp_vegas.c` implements the TCP Vegas congestion-control module. Vegas estimates queuing by comparing current RTT with the minimum base RTT and adjusts cwnd once per RTT to keep an estimated number of extra packets in the network between configurable `alpha` and `beta` thresholds. This implementation uses Linux loss recovery unchanged and only supplies congestion-control callbacks.

## Important APIs, Types, and Functions

Exports include `tcp_vegas_init()`, `tcp_vegas_pkts_acked()`, `tcp_vegas_state()`, `tcp_vegas_cwnd_event()`, `tcp_vegas_cwnd_event_tx_start()`, and `tcp_vegas_get_info()`, allowing YeAH and other modules to reuse Vegas sampling. Internal helpers are `vegas_enable()`, `vegas_disable()`, `tcp_vegas_ssthresh()`, and `tcp_vegas_cong_avoid()`. Module parameters are `alpha`, `beta`, and `gamma`. Per-socket state is `struct vegas` from `tcp_vegas.h`.

## Control Flow

Initialization sets `baseRTT` to a large sentinel and enables a fresh Vegas round. `tcp_vegas_pkts_acked()` ignores invalid RTT samples, adds one microsecond to avoid zero, min-filters `baseRTT`, min-filters `minRTT` for the current RTT, and increments `cntRTT`. State and cwnd-event callbacks disable sampling outside `TCP_CA_Open` and reset sampling after cwnd restart or idle transmit start.

`tcp_vegas_cong_avoid()` falls back to Reno when Vegas sampling is disabled. At the end of a Vegas RTT, detected when `ack` passes `beg_snd_nxt`, it advances the next RTT boundary. If there are too few RTT samples, it behaves like Reno. Otherwise it computes target cwnd as `cwnd * baseRTT / minRTT` and `diff = cwnd * (rtt - baseRTT) / baseRTT`. In slow start, `diff > gamma` exits to congestion avoidance and sets cwnd near target. In congestion avoidance, `diff > beta` decrements cwnd, `diff < alpha` increments cwnd, and in-range diff leaves cwnd unchanged. It clamps cwnd and resets the per-RTT sample counters.

## State and Persistence Behavior

Vegas stores only per-connection congestion-control private state in `ICSK_CA_PRIV_SIZE`: RTT minima, sample count, current RTT boundary, and enabled flag. Module parameters persist globally while the module is loaded. Diagnostic state is exposed through `INET_DIAG_VEGASINFO`.

## Dependencies and Integration Points

The module depends on Linux TCP congestion-control registration, Reno helpers for fallback/loss undo, ACK RTT sampling, inet_diag extension structures, and `tcp_vegas.h`. YeAH imports the exported Vegas callbacks and requires `struct vegas` to be first in its private state.

## Risks and Edge Cases

Vegas is sensitive to RTT sample quality; delayed ACKs and too few samples force Reno fallback. A stale `baseRTT` can understate congestion after route changes. The algorithm may underutilize paths when competing with more aggressive loss-based algorithms. Integer division and cwnd clamping must avoid zero cwnd; the implementation enforces a minimum of 2.

## Test Signals

Tests should verify module registration, parameter effects, RTT sampling, idle/recovery restart behavior, Reno fallback with insufficient samples, slow-start exit on `gamma`, additive/decrement decisions around `alpha`/`beta`, inet_diag Vegas info, and interoperability with YeAH. Network tests should observe queueing delay, throughput, and fairness against CUBIC/Reno.
