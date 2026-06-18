# Research: sources/distributed-fs/ceph-client/include/net/llc_c_ev.h

Purpose: `llc_c_ev.h` defines LLC connection-component event IDs, event qualifier IDs, event metadata stored in `skb->cb`, event detector function types, qualifier function types, and helper logic for connection receive-buffer space.

Important APIs/types/functions: event type constants distinguish simple, condition, primitive, PDU, ack timer, P timer, reject timer, busy timer, report-status, and send-ack timer events. Event IDs cover upper-layer primitives (`CONN_REQ`, `DATA_REQ`, `DISC_REQ`, `RESET_REQ`), local busy changes, bad PDUs, received DISC/DM/FRMR/I/REJ/RNR/RR/SABME/UA variants with P/F and validity qualifiers, timer expirations, and transmit-buffer-full. `struct llc_conn_state_ev` stores primitive, type, reason, status, indication, and confirmation fields in `skb->cb`. `llc_conn_ev()` casts skb control storage. The file declares event recognizers, qualifier functions, and `llc_conn_space()`.

Control flow: incoming PDUs or generated primitives are annotated in `skb->cb`, then the state engine probes event functions from transition tables. Qualifier callbacks refine a recognized event using connection state such as data flag, P flag, remote busy flag, retry count, S flag, cause flag, and status-setting side effects. Timer callbacks generate timer-specific event types that re-enter the same transition path.

State and persistence behavior: event metadata is transient per skb and lives in the packet control buffer. Qualifiers read and sometimes write LLC socket state, especially status fields used for upper-layer confirmations. `llc_conn_space()` samples socket receive memory accounting against `sk_rcvbuf`.

Dependencies and integration points: it depends on `net/sock.h`, skb control-buffer layout, LLC connection socket state, PDU parsing, timer callbacks, and connection state tables. It is tightly coupled to `llc_c_st.h` and action functions from `llc_c_ac.h`.

Risks: `skb->cb` sharing is fragile; overlapping users must not clobber `struct llc_conn_state_ev`. Event and qualifier numeric constants are table indexes/contracts. Misclassifying P/F bit, invalid Ns/Nr, or command/response state can drive wrong state transitions. `llc_conn_space()` uses receive memory accounting and must stay consistent with socket queueing behavior.

Test signals: packet-level tests should cover each supervisory/unnumbered/I-frame event family, invalid Ns/Nr handling, P/F bit variants, primitive request/confirm generation, timer-expiration transitions, receive-buffer-full paths, and control-buffer integrity under skb clone/queue operations.
