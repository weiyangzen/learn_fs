# sources/distributed-fs/ceph-client/net/rxrpc/input_rack.c

## Purpose
`input_rack.c` implements RACK-TLP loss detection for RxRPC DATA transmission. It tracks delivered transmit timestamps, detects reordering, marks lost packets, calculates and handles RACK reorder timers, sends tail loss probes, and processes ACKs of TLP probes.

## Important APIs and functions
- `rxrpc_input_rack_one()` and `rxrpc_input_rack()` update RACK state when packets are newly ACKed.
- `rxrpc_rack_detect_loss_and_arm_timer()` scans NACKed/unacked packets and arms reorder timers.
- `rxrpc_tlp_calc_pto()` computes probe timeout bounded by RTO.
- `rxrpc_tlp_send_probe()` sends new data or retransmits the highest transmitted DATA as a loss probe.
- `rxrpc_tlp_process_ack()` interprets ACKs for active TLP probes.
- `rxrpc_rack_timer_expired()` handles RACK reorder, TLP PTO, and RTO modes.

## Control flow
ACK processing in `input.c` calls RACK update helpers for hard and soft ACKs. RACK records the newest delivered transmit timestamp/sequence and tracks forward ACK progress. Loss detection computes a reordering window, scans txqueue NACK bits, and marks entries lost once their transmit time is old enough relative to the latest delivered packet. Timer expiry either rescans loss, sends a TLP probe, or marks losses on RTO.

## State and persistence behavior
State is stored in `struct rxrpc_call`: `rack_xmit_ts`, `rack_rtt`, `rack_rtt_ts`, `rack_reo_wnd`, multiplier/persistence fields, `rack_fack`, `rack_end_seq`, DSACK/reordering markers, `rack_timer_mode`, `rack_timo_at`, `tlp_serial`, `tlp_seq`, `tlp_is_retrans`, and `tlp_rtt_taken`. Packet loss is represented by per-txqueue `segment_lost` and `segment_retransmitted` bits plus call counters.

## Dependencies and integration points
This file depends on txqueue metadata populated by output, ACK summaries from `input.c`, RTO/RTT helpers, call transmit helpers in `call_event.c`, and timer scheduling in `call_event.c`.

## Risks
RACK decisions depend on correct transmit timestamps; lost packets are assigned `UINT_MAX` timestamps to avoid reuse. Reordering-window adaptation is approximate because RxRPC only has ACK duplicate reasons rather than TCP DSACK. TLP handling must avoid concurrent probes and clear probe state on sufficient ACK progress.

## Test signals
Use deterministic ACK/NAK traces for in-order delivery, reordering, duplicate ACKs, RTO recovery, TLP new-data probe, TLP retransmit probe, single-loss repair, and timer mode transitions. Tracepoints should show loss scans, lost marks, probe sends, and ACK interpretation.
