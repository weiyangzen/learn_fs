# sources/distributed-fs/ceph-client/net/ipv4/tcp_recovery.c

## Purpose

`tcp_recovery.c` implements transmit-side loss marking for RACK and NewReno. RACK, defined by RFC 8985, marks losses by elapsed send time relative to the most recently delivered later packet. NewReno support covers non-SACK recovery by marking the next unacked packet lost when duplicate ACK or partial-ACK conditions prove loss.

## Important APIs, Types, and Functions

Key functions are `tcp_rack_skb_timeout()`, `tcp_rack_mark_lost()`, `tcp_rack_reo_timeout()`, and `tcp_newreno_mark_lost()`. Internal helpers include `tcp_rack_reo_wnd()` and `tcp_rack_detect_loss()`. The file uses `tcp_sock::rack` fields, `reord_seen`, `sacked_out`, `reordering`, `srtt_us`, `tsorted_sent_queue`, retransmit queue skbs, and congestion states such as `TCP_CA_Recovery`.

## Control Flow

`tcp_rack_reo_wnd()` computes the reordering window. It returns zero when reordering has not been seen and the connection is already in recovery or has reached duplicate-ACK threshold, unless `TCP_RACK_NO_DUPTHRESH` disables that behavior. Otherwise it uses min RTT divided by four and linearly increases with DSACK-driven `reo_wnd_steps`, capped by smoothed RTT.

`tcp_rack_detect_loss()` scans `tsorted_sent_queue` in send-time order. It skips packets already marked lost but not retransmitted, stops once packets are not older than the current RACK reference, and computes remaining time with `tcp_rack_skb_timeout()`. Expired packets are marked lost and removed from the time-sorted list; nonexpired packets contribute to the maximum reordering timeout.

`tcp_rack_mark_lost()` runs the scan only when `tp->rack.advanced` says newly delivered information advanced RACK. If remaining timeout exists, it arms `ICSK_TIME_REO_TIMEOUT`. `tcp_rack_reo_timeout()` performs the delayed scan, enters recovery if newly marked losses reduced inflight and the socket was not already in recovery, optionally applies cwnd reduction, retransmits lost packets, and rearms RTO unless the retransmit timer is already pending.

`tcp_newreno_mark_lost()` handles non-SACK recovery. Before recovery it marks loss once duplicate ACK count reaches reordering threshold; during recovery it marks the head skb lost on ACK advancement. It fragments a multi-packet head skb down to one MSS before loss marking.

## State and Persistence Behavior

State lives in the socket: RACK timestamps and end sequence, `rack.advanced`, reordering-window steps, loss counters, skb `sacked` flags, and the `tsorted_sent_queue`. Timers persist pending reordering decisions through `ICSK_TIME_REO_TIMEOUT`. There is no durable state.

## Dependencies and Integration Points

This file depends on `tcp_output.c` for retransmission (`tcp_xmit_retransmit_queue()` and `tcp_fragment()`), on input-side ACK processing to update RACK references and DSACK/reordering state, on timer dispatch in `tcp_timer.c`, and on congestion-control recovery helpers such as `tcp_enter_recovery()` and `tcp_cwnd_reduction()`.

## Risks and Edge Cases

Loss marking too early harms reordered paths; too late delays recovery. The zero reordering window during dupthresh/recovery is intentionally aggressive but sensitive to `reord_seen` accuracy. The time-sorted queue must remain consistent when skbs are retransmitted, collapsed, or acknowledged. NewReno assumes a valid retransmit-queue head and must fragment GSO safely before marking one segment lost.

## Test Signals

Useful tests include packet reordering with and without DSACK, tail loss, RACK reordering timeout arming, RTO interaction, SACK versus non-SACK recovery, NewReno partial ACKs, GSO head fragmentation, and sysctl `tcp_recovery` variations. Observe `ICSK_TIME_REO_TIMEOUT`, `lost_out`, retransmission tracepoints, recovery state transitions, and recovery latency.
