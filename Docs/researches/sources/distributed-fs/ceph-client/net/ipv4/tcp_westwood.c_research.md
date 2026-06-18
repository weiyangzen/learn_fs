# sources/distributed-fs/ceph-client/net/ipv4/tcp_westwood.c

## Purpose

`tcp_westwood.c` implements TCP Westwood+, a congestion-control module that estimates end-to-end bandwidth from returning ACKs and uses bandwidth-delay product estimates to set cwnd/ssthresh after congestion events. Its probing phase remains Reno-like, while loss response uses measured bandwidth and minimum RTT.

## Important APIs, Types, and Functions

Private `struct westwood` stores bandwidth estimates, RTT window start, bytes acknowledged in the current estimation bucket, sequence tracking, delayed/duplicate ACK accounting, current/min RTT, and flags. Important callbacks are `tcp_westwood_init()`, `tcp_westwood_pkts_acked()`, `tcp_westwood_ack()`, `tcp_westwood_event()`, and `tcp_westwood_info()`, registered in `tcp_westwood` with Reno `ssthresh`, `cong_avoid`, and `undo_cwnd`.

## Control Flow

Initialization clears bandwidth accounting, sets RTT/min RTT to a conservative initial value, records current `snd_una`, and marks the first ACK. `tcp_westwood_pkts_acked()` records the latest RTT sample in jiffies. `westwood_update_window()` checks whether at least max(current RTT, 50 ms) elapsed since the current bandwidth window; when elapsed, it filters `bk / delta` into `bw_ns_est` and then `bw_est`, clears `bk`, and starts a new window.

ACK processing is split into fast and slow paths. Fast path calls `westwood_fast_bw()`, updates the bandwidth window, adds newly acknowledged bytes from `snd_una` movement, updates `snd_una`, and min-filters RTT. Slow path accounts for duplicate ACKs and delayed/partial ACKs through `westwood_acked_count()` so `bk` reflects likely acknowledged bytes even when `snd_una` does not advance normally.

On `CA_EVENT_COMPLETE_CWR`, Westwood sets ssthresh and cwnd to `bw_est * rtt_min / mss_cache`, clamped to at least 2. On `CA_EVENT_LOSS`, it sets ssthresh to the same estimate and resets RTT-min tracking for the next ACK. Diagnostic output reuses the Vegas inet_diag info attribute to report current and minimum RTT.

## State and Persistence Behavior

All algorithm state is per socket in CA private storage. Bandwidth estimates persist across RTT windows and loss events. `reset_rtt_min` causes the next ACK to seed a fresh min-RTT interval after loss. Module registration persists while loaded.

## Dependencies and Integration Points

Westwood integrates with TCP congestion-control callbacks, ACK-event flags (`CA_ACK_SLOWPATH`), Reno congestion avoidance, inet_diag Vegas-compatible info, jiffies timing, and standard TCP sequence/cwnd helpers. It depends on accurate ACK processing and RTT samples from the core TCP input path.

## Risks and Edge Cases

Bandwidth estimation can be skewed by ACK compression, delayed ACKs, duplicate ACK accounting, very small RTT windows, or application-limited sending. `mss_cache` must be nonzero for BDP conversion. Reusing Vegas diagnostic attributes may surprise tooling expecting actual Vegas semantics. The initial RTT is intentionally conservative and can affect early loss response.

## Test Signals

Tests should cover registration, initial state, fast/slow ACK accounting, duplicate and delayed ACK behavior, bandwidth filtering, RTT-min reset after loss, cwnd/ssthresh update on CWR/loss, inet_diag info, and throughput behavior on lossy wireless-like links and ACK-compressed paths.
