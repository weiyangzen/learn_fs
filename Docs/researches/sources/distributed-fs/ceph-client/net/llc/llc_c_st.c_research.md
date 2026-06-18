# Research: sources/distributed-fs/ceph-client/net/llc/llc_c_st.c

## sources/distributed-fs/ceph-client/net/llc/llc_c_st.c

Purpose: Defines the LLC type 2 connection-component state transition table. It is the declarative core consumed by `llc_conn_service()` in `llc_conn.c`: events are matched by `llc_conn_ev_*` predicates, optionally qualified by `llc_conn_ev_qlfy_*` predicates, then action vectors of `llc_conn_ac_*` functions are executed before moving to a next `LLC_CONN_STATE_*`.

Important APIs/types/functions: Exports `struct llc_conn_state llc_conn_state_table[NBR_CONN_STATES]`. The file is composed of `struct llc_conn_state_trans`, `llc_conn_action_t` arrays, and `llc_conn_ev_qfyr_t` arrays. It references the connection states ADM, SETUP, NORMAL, BUSY, REJ, AWAIT, AWAIT_BUSY, AWAIT_REJ, D_CONN, RESET, ERROR, and TEMP. It depends heavily on action helpers from `llc_c_ac.h` and event/qualifier helpers from `llc_c_ev.h`.

Control flow: The table is ordered by event categories used by `llc_build_offset_table()` and `llc_find_offset()`: primitive requests, local busy/simple events, initiate P/F cycle, timers, and received frames. Common transitions cover shared disconnect, reset, SABME, DISC, DM, FRMR, invalid sequence/control cases, and timeout escalation. State-specific blocks encode setup handshakes, normal data transfer, receiver busy/reject handling, await states during poll/final cycles, disconnect confirmation, reset recovery, and FRMR error recovery.

State and persistence behavior: No runtime state is stored in this file; all state lives in `struct llc_sock` fields such as `state`, `vS`, `vR`, `p_flag`, `f_flag`, `s_flag`, `remote_busy_flag`, `cause_flag`, retry counters, and timers. This file determines how those fields are mutated through action callbacks and when upper-layer indications/confirmations are requested.

Dependencies and integration points: Integrated by `llc_conn.c` through `llc_conn_state_table` and the offset table built at init. Its action lists call into PDU builders, timer control, skb queues, and socket notification paths. Correct behavior also depends on `llc_c_ev.c` classifying incoming PDUs and timer events consistently with this table's grouping.

Risks and test signals: Ordering is critical because transitions are scanned linearly from a category offset; inserting a transition in the wrong category can make an event unreachable or misclassified. Many transitions differ only by qualifiers such as retry count, P/F flag, remote busy, expected `N(S)`, or status-setting side effects, so regressions are likely in edge cases: simultaneous SABME/DISC, invalid `N(R)`, timeout at `n2`, local busy entry/exit, and REJ recovery. Useful tests are packetdrill-style LLC2 handshakes, timer-forced retransmission tests, invalid sequence fuzzing, and checking `/proc/net/llc/core` state/timer fields while exercising connect, data, busy, reset, and disconnect paths.
