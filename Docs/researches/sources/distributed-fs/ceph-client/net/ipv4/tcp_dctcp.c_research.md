# sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.c

## Purpose
`tcp_dctcp.c` implements DataCenter TCP, module name `dctcp`, which uses ECN Congestion Experienced markings to estimate the fraction of marked packets per RTT and reduce cwnd proportionally. It falls back to a Reno-compatible internal ops table when ECN is unavailable on an established socket.

## Important APIs, Types, And Functions
`struct dctcp` stores delivered and delivered-CE snapshots, receive CE state, alpha, next sequence boundary, remembered loss cwnd, and PLB state. Main callbacks are `dctcp_init()`, `dctcp_update_alpha()`, `dctcp_cwnd_event()`, `dctcp_cwnd_event_tx_start()`, `dctcp_ssthresh()`, `dctcp_state()`, `dctcp_cwnd_undo()`, and `dctcp_get_info()`. `dctcp_shift_g` controls EWMA gain and is range-limited to 0..10; `dctcp_alpha_on_init` sets initial alpha. The file registers BTF kfunc ids for BPF struct_ops.

## Control Flow
Initialization permits DCTCP if ECN was negotiated or the socket is listen/close state; otherwise it switches `icsk_ca_ops` to `dctcp_reno` and clears ECT transmission. `dctcp_update_alpha()` runs on ACK events, detects an RTT boundary using `snd_una` and `next_seq`, computes delivered and CE-delivered deltas, updates PLB with instantaneous CE ratio, applies the DCTCP EWMA formula to `dctcp_alpha`, and resets delivered snapshots. `dctcp_ssthresh()` reduces cwnd by `alpha / 2`. Loss paths store `loss_cwnd`, set a Reno-half threshold, and allow `dctcp_cwnd_undo()` to restore at least the pre-loss cwnd. ECN receive events delegate CE ACK state transitions to `tcp_dctcp.h`.

## State, Persistence, Dependencies, And Integration
State is per-socket in `icsk_ca_priv`, with module parameters affecting all flows. The algorithm requires ECN and sets `TCP_CONG_NEEDS_ECN`, integrates with PLB helpers, inet_diag DCTCP info, BTF kfunc registration, and Reno growth. It includes `tcp_dctcp.h` for CE ACK logic.

## Risks And Test Signals
Risks include divide-by-zero or overflow around delivered counters, incorrect ECN fallback, stale alpha visible to diagnostics, PLB rehash behavior under CE bursts, and only-once-per-RTT loss handling. Tests should check ECN and non-ECN handshakes, alpha updates for zero, partial, and full CE marking, `dctcp_shift_g` parameter validation, DCTCP inet_diag output, RTO and recovery loss response, PLB state updates, and BPF kfunc registration.
