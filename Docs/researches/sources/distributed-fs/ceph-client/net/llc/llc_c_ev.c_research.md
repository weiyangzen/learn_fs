# sources/distributed-fs/ceph-client/net/llc/llc_c_ev.c

## Purpose
`llc_c_ev.c` implements LLC2 connection event matchers and qualifiers used by the connection state machine. Matchers identify primitives, timer events, PDU types, sequence-number conditions, and generic command/response classes; qualifiers check connection flags and set status values.

## Important APIs, Types, and Functions
Primitive matchers include `llc_conn_ev_conn_req()`, `llc_conn_ev_data_req()`, `llc_conn_ev_disc_req()`, and `llc_conn_ev_rst_req()`. PDU matchers cover DISC, DM, FRMR, I command/response variants, REJ/RNR/RR supervisory variants, SABME, UA, generic command/response, and invalid N(R)/N(S) cases. Timer matchers include `llc_conn_ev_p_tmr_exp()`, `llc_conn_ev_ack_tmr_exp()`, `llc_conn_ev_rej_tmr_exp()`, and `llc_conn_ev_busy_tmr_exp()`. Qualifiers check `data_flag`, `p_flag`, `remote_busy_flag`, retry count vs `n2`, `s_flag`, `cause_flag`, transmit-window last-frame conditions, and set status codes.

## Control Flow
The state machine passes an event skb to matcher functions until one returns `0`. PDU matchers inspect LLC headers through `llc_pdu_*` helpers and compare command/response bits, PDU type, poll/final bits, sequence numbers, and receive-space availability. Invalid sequence helpers use circular-window checks to distinguish unexpected-but-in-window from invalid/out-of-window cases. Qualifiers run after a match to enforce flag conditions or annotate the event with a status used by confirmation actions.

## State and Persistence
The file mostly reads state from `struct llc_sock`: `vR`, `vS`, receive window `rw`, transmit window `k`, unacknowledged queue, flags, retry count, and device flags. Qualifier status setters mutate only the transient `llc_conn_state_ev` embedded in the event skb.

## Dependencies and Integration Points
It depends on LLC PDU header accessors, `llc_circular_between()` from the action file, connection-space checks, skbuff queues, and the generated/static LLC connection state tables. Debug prints expose matched invalid sequence cases.

## Risks and Edge Cases
Return convention is inverted from typical predicates: `0` means matched/success and `1` means no match/failure. The receive-window helper also returns negated circular-check results, so maintainers must be careful when changing sequence logic. Loopback skips transmit-window validation in `llc_util_nr_inside_tx_window()`. Matchers assume the skb contains the correct PDU header type for the state-table context.

## Test Signals
Tests should feed crafted LLC PDUs to every matcher, especially boundary sequence numbers around modulo wrap, invalid N(R)/N(S), poll/final bit variants, full receive-space behavior, loopback transmit-window behavior, and all qualifier status-setting functions.
