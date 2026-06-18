# sources/distributed-fs/ceph-client/include/net/sctp/constants.h

## Purpose
This header centralizes SCTP internal constants, state/event enumerations, default timers, retransmission parameters, path MTU probing limits, address scope policy, xmit results, and AUTH constants.

## Important APIs, Types, And Functions
It defines stream defaults, chunk-type counts, event families (`sctp_event_type`, timeouts, primitives, other events), `union sctp_subtype` constructors, internal errors, association states, socket-state mappings, PLPMTUD states, TSN map sizes, duplicate/gap limits, default heartbeat/SACK/RTO/cookie/rwnd/MTU values, UDP encapsulation port, PF exposure modes, transmit outcomes, transport commands, retransmit/lower-cwnd reasons, address scopes, bind-copy flags, and HMAC identifiers. Name helpers `sctp_cname()`, `sctp_oname()`, `sctp_tname()`, and `sctp_pname()` support diagnostics.

## Control Flow
The state machine indexes by state, event type, and subtype values declared here. Timers and retransmission code use the timeout enumerations and defaults. Transport and congestion-control code use the xmit/retransmit/cwnd enums.

## State And Persistence
The file itself has no mutable state. Its values shape persistent association, transport, and socket configuration initialized elsewhere.

## Dependencies And Integration Points
It depends on SCTP UAPI, IPv6 headers, and TCP socket states. It feeds almost every SCTP header in this set, especially `command.h`, `sm.h`, `sctp.h`, `structs.h`, and `tsnmap.h`.

## Risks And Test Signals
Risks include ABI-visible state mismatches, default timer regressions, TSN gap overflow, incorrect AUTH chunk counts, and PLPMTUD boundary errors. Test signals are state-table coverage, sysctl/default propagation tests, PLPMTUD probing, SACK gap/dup generation, AUTH negotiation, and address scope filtering.
