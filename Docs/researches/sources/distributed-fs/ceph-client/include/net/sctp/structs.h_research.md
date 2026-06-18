# sources/distributed-fs/ceph-client/include/net/sctp/structs.h

## Purpose
This is the main SCTP data-model header. It defines address abstractions, global hash state, per-socket options, cookies, parameters, address-family operations, messages/chunks/packets, transports, in/out queues, bind addresses, endpoints, streams, associations, cmsg parsing, and debug counters.

## Important APIs, Types, And Functions
Important structures include `union sctp_addr`, `struct sctp_globals`, `struct sctp_sock`, `struct sctp_cookie`, `struct sctp_signed_cookie`, `union sctp_params`, `struct sctp_af`, `struct sctp_pf`, `struct sctp_datamsg`, `struct sctp_chunk`, `struct sctp_packet`, `struct sctp_transport`, `struct sctp_inq`, `struct sctp_outq`, `struct sctp_bind_addr`, `struct sctp_ep_common`, `struct sctp_endpoint`, stream structs, `struct sctp_priv_assoc_stats`, and `struct sctp_association`. APIs cover stream init/free/update, AF/PF registration, datamsg/chunk lifecycle, packet assembly/transmit, transport routing/timers/congestion/PMTU, in/out queue management, bind address operations, endpoint lookup/refcounting, INIT verification/processing, association lifecycle/update/peer management, ASCONF ACK cache, and address comparison.

## Control Flow
Sockets own `sctp_sock` and an endpoint. Associations inherit endpoint binding, negotiate cookie/peer capabilities, create transports, receive chunks through `sctp_inq`, reorder/deliver data through `sctp_ulpq`, and transmit via `sctp_outq`, stream scheduler, packet bundling, and transport xmit callbacks. Handshake state stores peer INIT/cookie data; established paths update TSN maps, rwnd, congestion, timers, AUTH, ASCONF, and stream-reset state.

## State And Persistence
This file defines nearly all persistent SCTP kernel state: global endpoint/port/transport hashes, socket defaults, endpoint shared keys and feature flags, association TCB fields, peer transport lists, timers, queues, buffer accounting, stream sequence numbers, retransmission lists, ASCONF queues, AUTH keys, security IDs, and RCU/refcount lifetime.

## Dependencies And Integration Points
It depends on crypto SHA keys, radix trees, rhashtable, sockets, IPv4/IPv6 headers, sk_buffs, workqueues, SCTP UAPI structs, SCTP auth, TSN maps, ULP events/queues, and stream interleaving. It is the shared contract for SCTP protocol, input, output, state-machine, socket, proc, and stream files.

## Risks And Test Signals
Risk is broad: refcount/RCU lifetime, timer cancellation, transport hash consistency, chunk ownership, skb control block reuse, PMTU/congestion accounting, authentication key lifetime, stream interleaving sequence state, ASCONF serialization, rwnd/sndbuf accounting, and security label propagation. Test signals include full SCTP connect/send/shutdown, multihoming failover, retransmission, SACK gaps, PR-SCTP abandon/FWD-TSN, AUTH, ADDIP/ASCONF, stream reset/add, PLPMTUD, peeloff, IPv6, UDP encapsulation, and memory-leak/object-counter tests.
