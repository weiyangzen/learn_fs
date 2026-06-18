# Research: sources/distributed-fs/ceph-client/include/net/llc_c_ac.h

Purpose: `llc_c_ac.h` declares LLC Type 2 connection-component state-transition actions. These are the action functions referenced by the connection state table to send PDUs, notify upper layers, update sequence variables, start/stop timers, and modify connection flags.

Important APIs/types/functions: the file assigns numeric action IDs such as `LLC_CONN_AC_CONN_IND`, `SEND_DISC_CMD_Pb_SET_X`, `SEND_I_CMD_Pb_SET_1`, `SEND_REJ_RSP_Fb_SET_1`, `START_ACK_TMR`, `UPDATE_Nr_RECEIVED`, `Vr_INC_BY_1`, and `START_SENDACK_TMR_IF_NOT_RUNNING`. `llc_conn_action_t` is the action function signature over `struct sock *` and `struct sk_buff *`. Declarations cover indication/confirm actions, PDU send/resend actions, timer control callbacks, flag setters, retry and sequence updates, disconnect/reset helpers, transmit-window adjustment, and `llc_circular_between()`.

Control flow: the LLC connection state engine evaluates an event, checks qualifiers, then runs a NULL-terminated action list made of functions declared here. Actions may enqueue indications to the socket receive queue, construct outbound LLC PDUs, change `llc_sock` state variables, schedule timers, remove acknowledged PDUs, or retransmit queued I PDUs. Timer callbacks re-enter the same state machinery by producing timer-expiration events.

State and persistence behavior: actions mutate in-memory `struct llc_sock` fields such as P/F/S/data/remote-busy/cause flags, retry count, `vS`, `vR`, unacknowledged PDU queues, timers, and connection state. State persists for the socket lifetime and across timer callbacks but has no durable storage.

Dependencies and integration points: this header depends on `struct sock`, `sk_buff`, and timer infrastructure. Implementations integrate with `llc_conn.h` socket state, `llc_pdu.h` PDU construction, state tables in `llc_c_st.h`, event definitions in `llc_c_ev.h`, and upper-layer AF_LLC primitives.

Risks: the action numbers are table contracts; renumbering or missing entries can make state transitions execute the wrong behavior. Sequence-number arithmetic is modulo 128 and easy to get wrong. Timer start/stop order can cause duplicate expirations or missed retransmits. Multi-action transitions must keep skb ownership clear because some actions consume, clone, or requeue frames.

Test signals: exercise connection setup/disconnect/reset, I-frame send and ACK removal, retransmission on ack/P/rej/busy timer expiry, remote/local busy transitions, rejected/FRMR frames, circular sequence comparisons around wrap, and skb ownership under failure injection.
