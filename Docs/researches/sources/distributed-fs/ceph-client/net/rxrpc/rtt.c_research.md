<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rtt.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rtt.c

## Purpose
`rtt.c` calculates smoothed RTT, RTT variance, RTO, RACK minimum RTT, and retransmission backoff for AF_RXRPC calls, adapting TCP-style RFC6298/Jacobson logic.

## Important APIs, Types, And Functions
Externally used functions are `rxrpc_call_add_rtt()`, `rxrpc_get_rto_backoff()`, and `rxrpc_call_init_rtt()`. Internal helpers include `rxrpc_rto_min_us()`, `__rxrpc_set_rto()`, `rxrpc_bound_rto()`, `rxrpc_rtt_estimator()`, `rxrpc_set_rto()`, `rxrpc_update_rtt_min()`, and `rxrpc_ack_update_rtt()`.

## Control Flow
Call initialization sets initial RTO and deviation. When an ACK response matches an RTT probe, `rxrpc_call_add_rtt()` computes elapsed microseconds, ignores negative samples, updates the RACK min RTT, feeds the sample to the estimator, recalculates bounded RTO, resets backoff, increments sample counters, publishes recent peer SRTT/RTO, and traces the sample. Timeout selection reads current RTO, shifts by backoff, optionally increments backoff for retransmissions, clamps to at least 1 microsecond, and returns a ktime.

## State And Persistence
Per-call persistent fields include `srtt_us` scaled by 8, `mdev_us`, `mdev_max_us`, `rttvar_us`, `rto_us`, `backoff`, `rtt_count`, `rtt_taken`, and `min_rtt`. Peer fields `recent_srtt_us` and `recent_rto_us` cache current diagnostics.

## Dependencies And Integration Points
The file is used by ACK/RTT probe handling in `output.c` and ACK receive paths, RACK/TLP timeout logic, peer proc diagnostics, and tracepoints. It depends on kernel minmax helpers, jiffies/ktime conversion, and rxrpc call/peer structures.

## Risks And Edge Cases
The current minimum RTO helper returns 200 microseconds but `rxrpc_bound_rto()` clamps with a hardcoded 200000 microsecond lower term plus 100000 slack, so changes must be made carefully. Negative time samples are ignored. Backoff uses left shifts and caps increment only when doubling stays under the max.

## Test Signals
Unit-style tests should feed first and subsequent RTT samples, decreasing RTT variance, negative samples, retransmission backoff growth, max RTO clamp, peer diagnostic updates, and RACK min RTT window behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rtt.c -->
