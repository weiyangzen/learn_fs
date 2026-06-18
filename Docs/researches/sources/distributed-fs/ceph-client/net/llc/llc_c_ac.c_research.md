# sources/distributed-fs/ceph-client/net/llc/llc_c_ac.c

## Purpose
`llc_c_ac.c` implements LLC2 connection-component actions executed by the connection state table. Each action takes a socket and event skb, mutates connection state, emits PDUs, starts/stops timers, or reports primitives back to upper layers.

## Important APIs, Types, and Functions
The file exports many `llc_conn_ac_*` action functions plus timer callbacks `llc_conn_pf_cycle_tmr_cb()`, `llc_conn_busy_tmr_cb()`, `llc_conn_ack_tmr_cb()`, and `llc_conn_rej_tmr_cb()`. Important categories include primitive indication/confirmation (`conn`, `data`, `disc`, `rst`), PDU send helpers for DISC/DM/FRMR/I/REJ/RNR/RR/SABME/UA, busy and poll flag manipulation, ack aggregation (`ack_must_be_send`, `ack_pf`, `npta`), transmit window adjustments, sequence updates (`vS`, `vR`, `last_nr`, `X`), and timer control.

## Control Flow
State-table matches call these actions in configured order. PDU actions allocate frames with `llc_alloc_frame()`, initialize LLC headers and PDU-specific fields, build MAC headers, then send through `llc_conn_send_pdu()`. Data I-frame sends increment `vS` and hold an skb reference for transmit/accounting. Ack-update paths remove acknowledged PDUs, restart or stop ack timers, and emit data confirmations when a previously failed data request becomes sendable. Timer callbacks allocate zero-length event skbs, set the event type, and either process the event immediately or queue it to socket backlog if userspace owns the socket lock.

## State and Persistence
All state is in `struct llc_sock`: sequence numbers, retry count, busy flag, poll flag, send-state flags, cause/data flags, transmit window `k`, receive window `rw`, unacknowledged queue, timers, stored rejected header, and socket wakeups. No persistent storage is used.

## Dependencies and Integration Points
The action layer depends on `llc_conn_state_process()`, LLC PDU helpers, SAP state, socket wakeups, skbuff queues, timers, and netdevice MAC header creation. It is tightly coupled to `llc_c_st.c` state tables and `llc_c_ev.c` event predicates.

## Risks and Edge Cases
Many functions allocate skb frames in atomic contexts and must free on MAC-header failure. Timer event processing must not run state transitions while userspace owns the socket, hence backlog queuing. Sequence/window math is modulo `LLC_2_SEQ_NBR_MODULO`. Some functions return `0` despite internal send failures or contain legacy comments, so callers rely on state-table semantics rather than strict errno propagation.

## Test Signals
State-machine tests should cover every PDU action, timer callback, retry-count boundary, p/f flag clearing and socket wakeup, remote-busy handling, ack aggregation thresholds, transmit window increase/decrease, FRMR resend, loopback behavior, and allocation-failure paths.
