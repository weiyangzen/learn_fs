# sources/distributed-fs/ceph-client/net/sctp/transport.c

## Purpose
Defines lifecycle, routing, timers, PMTU/PLPMTUD, RTO estimation, congestion-window control, and reference management for an SCTP transport representing one remote peer address.

## Important APIs, Types, And Functions
Exports constructors/destructors and state updates including `sctp_transport_new`, `sctp_transport_free`, `sctp_transport_set_owner`, timer reset helpers, `sctp_transport_pmtu`, `sctp_transport_pl_send`, `sctp_transport_pl_recv`, `sctp_transport_update_pmtu`, `sctp_transport_route`, `sctp_transport_hold`, `sctp_transport_put`, `sctp_transport_update_rto`, `sctp_transport_raise_cwnd`, `sctp_transport_lower_cwnd`, `sctp_transport_burst_limited`, `sctp_transport_reset`, `sctp_transport_immediate_rtx`, and dst helpers.

## Control Flow
Initialization copies the peer address, sets defaults from netns SCTP sysctls, initializes timers/lists, nonce, and refcount. Free marks the transport dead, deletes active timers while dropping their held references, and releases the final reference; destruction frees packets, association refs, dst, and memory through RCU. Routing refreshes dst/source address and PMTU. PLPMTUD tracks BASE, ERROR, SEARCH, and COMPLETE states on probe send/receive and packet-too-big signals. RTO updates follow SCTP smoothing rules with sysctl alpha/beta divisors and min/max clamps. Congestion control raises cwnd in slow start or avoidance, lowers it on T3, fast retransmit, ECNE, or inactivity, and enforces max-burst temporarily.

## State And Persistence
Transport state is entirely in-memory: timers, refcount, dst, source/peer addresses, RTO/RTT variables, cwnd/ssthresh/flight size, path error counters, heartbeat/reconf/probe state, and PLPMTUD search fields.

## Dependencies And Integration Points
Integrates with association lifecycle, SCTP timers/state machine event generators, routing address-family hooks, dst cache, SCTP outqueue retransmit, netns sysctls, and congestion/PMTU sync back to the association.

## Risks
High-risk areas are timer reference leaks, freeing while RCU readers hold transport pointers, incorrect PLPMTUD state transitions after black-hole detection, cwnd math under fast recovery, stale dst usage, and RTO changes when `rto_pending` is not set.

## Test Signals
Test timer start/delete/free races, route refresh after obsolete dst, PMTU too-low and PLPMTUD packet-too-big paths, RTO first and subsequent RTT samples, cwnd transitions for each lower reason, burst limiting/reset, and immediate retransmit timer behavior.
