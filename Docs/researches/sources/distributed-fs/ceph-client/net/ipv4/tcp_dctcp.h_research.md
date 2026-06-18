# sources/distributed-fs/ceph-client/net/ipv4/tcp_dctcp.h

## Purpose
`tcp_dctcp.h` provides the minimal inline receive-side CE state machine used by DCTCP to reflect ECN Congestion Experienced state in outgoing ACKs. It is a small integration header, not a standalone module.

## Important APIs, Types, And Functions
`dctcp_ece_ack_cwr()` sets or clears `TCP_ECN_DEMAND_CWR` in `tcp_sk(sk)->ecn_flags` based on the current CE state. `dctcp_ece_ack_update()` accepts a TCP congestion-control event, prior receive-next pointer, and CE-state pointer. It translates `CA_EVENT_ECN_IS_CE` to state 1 and `CA_EVENT_ECN_NO_CE` to state 0.

## Control Flow
When the CE state changes, `dctcp_ece_ack_update()` first checks whether a delayed ACK timer is pending. If so, it temporarily restores the old CE state in the ACK flags and sends an immediate ACK for `prior_rcv_nxt`, preserving the previous feedback boundary. It then marks `ICSK_ACK_NOW` so the new state is acknowledged promptly, updates `prior_rcv_nxt` from `tcp_sk(sk)->rcv_nxt`, stores the new state, and calls `dctcp_ece_ack_cwr()` to update the outgoing ECE/CWR demand flag.

## State, Persistence, Dependencies, And Integration
The header mutates per-socket TCP ECN flags and caller-owned DCTCP state fields. It depends on `struct sock`, `struct tcp_sock`, `inet_csk(sk)->icsk_ack`, `__tcp_send_ack()`, and the `enum tcp_ca_event` values used by TCP ECN receive processing. Its direct integration point in this group is `dctcp_cwnd_event()` in `tcp_dctcp.c`.

## Risks And Test Signals
Risks are ACK ordering bugs at CE transitions, mishandling of delayed ACK state, and incorrect `prior_rcv_nxt` causing ambiguous CE feedback. Tests should feed alternating CE and non-CE receive events, verify immediate ACK generation when a delayed ACK is pending, confirm `TCP_ECN_DEMAND_CWR` state after each transition, and validate that DCTCP alpha accounting sees accurate delivered-CE signals.
