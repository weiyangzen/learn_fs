# sources/distributed-fs/ceph-client/net/ipv4/tcp_timer.c

## Purpose

`tcp_timer.c` implements TCP transmit-side timers: delayed ACK, retransmission/RTO, RACK reordering timeout dispatch, Tail Loss Probe dispatch, zero-window probe timeout, Fast Open SYNACK retransmission, keepalive, compressed ACK hrtimer, and timer initialization. It enforces retry limits, TCP_USER_TIMEOUT, orphan-resource policy, PMTU black-hole response, and timer deferral when sockets are owned by users.

## Important APIs, Types, and Functions

Public functions include `tcp_clamp_probe0_to_user_timeout()`, `tcp_delack_timer_handler()`, `tcp_retransmit_timer()`, `tcp_write_timer_handler()`, `tcp_syn_ack_timeout()`, `tcp_reset_keepalive_timer()`, `tcp_set_keepalive()`, and `tcp_init_xmit_timers()`. Internal helpers include `tcp_clamp_rto_to_user_timeout()`, `tcp_write_err()`, `tcp_out_of_resources()`, `tcp_orphan_retries()`, `tcp_mtu_probing()`, `tcp_model_timeout()`, `retransmits_timed_out()`, `tcp_write_timeout()`, `tcp_probe_timer()`, `tcp_update_rto_stats()`, `tcp_fastopen_synack_timer()`, `tcp_rtx_probe0_timed_out()`, `tcp_write_timer()`, `tcp_keepalive_timer()`, and `tcp_compressed_ack_kick()`.

## Control Flow

Delayed ACK timer flow starts in `tcp_delack_timer()`. It avoids locking if no ACK/compressed ACK is pending, otherwise locks the socket. If user-owned, work is deferred via `TCP_DELACK_TIMER_DEFERRED`; otherwise `tcp_delack_timer_handler()` checks compressed ACKs, pending state, reschedules if early, adjusts ATO on missed delayed ACKs, sends ACKs, and updates delayed ACK MIBs.

Write timer flow starts in `tcp_write_timer()`, which checks `icsk_pending`, locks the socket, and either dispatches `tcp_write_timer_handler()` or sets `TCP_WRITE_TIMER_DEFERRED`. The handler refreshes timestamps and switches on `ICSK_TIME_REO_TIMEOUT`, `ICSK_TIME_LOSS_PROBE`, `ICSK_TIME_RETRANS`, and `ICSK_TIME_PROBE0`, invoking RACK reordering timeout, TLP send, RTO retransmission, or zero-window probe logic.

RTO logic in `tcp_retransmit_timer()` handles passive Fast Open child SYNACK retransmission first. For established data, it validates `packets_out` and the retransmit queue head. If the peer has a zero window, it treats retransmits as probes and avoids normal timeout unless orphan/user-timeout policy expires. Otherwise it increments timeout MIBs, calls `tcp_write_timeout()` to handle retry exhaustion, black-hole MTU probing, BPF RTO callbacks, Fast Open/MPTCP black-hole detection, and txhash rethink. It then enters loss, updates RTO stats, retransmits the head skb, and applies linear or exponential backoff before arming the next retransmit timer.

Probe and keepalive flows enforce user-visible timeout semantics. `tcp_probe_timer()` sends zero-window probes while respecting `TCP_USER_TIMEOUT`, orphan retry policy, and resource pressure. `tcp_keepalive_timer()` handles FIN_WAIT2 orphan expiry, keepalive enablement, outstanding data suppression, probe counts, user-timeout override, active reset on timeout, and rescheduling.

## State and Persistence Behavior

Timer state is stored in `inet_connection_sock`: `icsk_pending`, `icsk_rto`, `icsk_backoff`, `icsk_retransmits`, delayed ACK state, probe counters/timestamps, user timeout, and timer objects. `tcp_sock` contributes `retrans_stamp`, `rto_stamp`, `total_rto`, `total_rto_recoveries`, `packets_out`, `snd_wnd`, `rcv_tstamp`, Fast Open request state, and compressed ACK counters. Timers hold socket references until callbacks complete or deferred release callbacks run.

## Dependencies and Integration Points

This file integrates with transmit routines in `tcp_output.c` (`tcp_retransmit_skb()`, `tcp_send_probe0()`, `tcp_write_wakeup()`, `tcp_send_ack()`, `tcp_rtx_synack()`), RACK in `tcp_recovery.c`, congestion state transitions, Fast Open, MPTCP, ECN, BPF sockops RTO callbacks, net namespace sysctls, orphan resource checks, dst negative advice/reset, socket locking, hrtimers, and MIB accounting.

## Risks and Edge Cases

Timer code is race-sensitive. It must not run protocol work while a user owns the socket unless it defers and holds a reference. Retry calculations combine jiffies, millisecond user timeouts, and optional microsecond TCP timestamps. Zero-window probes must avoid incorrectly timing out live peers that continue ACKing. Orphan cleanup intentionally violates ideal TCP persistence to protect the host, so resource-pressure thresholds are operationally important. Fast Open SYNACK retransmission differs from normal listener SYNACK retransmission and can affect accepted child sockets.

## Test Signals

Validation should cover delayed ACK scheduling/deferral, compressed ACK hrtimer, RTO backoff, thin-stream linear timeout, TCP_USER_TIMEOUT for retransmits and zero-window probes, orphan timeout/resource aborts, PMTU black-hole probing, RACK/TLP timer dispatch, Fast Open SYNACK retries, keepalive timeout/reset, FIN_WAIT2 orphan behavior, and socket-owned timer deferral through `tcp_release_cb()`. Signals include `LINUX_MIB_TCPTIMEOUTS`, recovery-failure MIBs, abort MIBs, delayed ACK MIBs, retransmission tracepoints, timer pending state, and packet-level retransmit/probe timing.
