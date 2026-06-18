# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rc.h

## Purpose
`trace_rc.h` declares Reliable Connection trace events for timeout-driven RC restart debugging.

## Important APIs, types, and functions
The `rvt_rc_template` event class records device name, QPN, send flags, a supplied PSN, send PSN trackers (`s_psn`, `s_next_psn`, `s_sending_psn`, `s_sending_hpsn`), and receive PSN. The concrete event is `rvt_rc_timeout`.

## Control flow
The tracepoint is emitted by the RC retry timer path in `qp.c` when a response is missing and provider restart scheduling is requested.

## State and persistence
Only trace records persist in the tracing subsystem. The fields are a snapshot of QP transport sequence state at timeout time.

## Dependencies and integration points
It depends on Linux tracepoint infrastructure and `rdmavt_qp.h`. It is useful with provider send/retry traces to explain retransmission windows and PSN divergence.

## Risks
If QP PSN fields are renamed or semantics shift, this trace schema must be updated together with timeout logic. The event is timeout-specific, so it does not cover all RC retry reasons.

## Test signals
Force RC packet loss or delayed ACKs, enable `rvt_rc_timeout`, and verify PSN fields identify the restart point used by provider `notify_restart_rc()` and send scheduling.
