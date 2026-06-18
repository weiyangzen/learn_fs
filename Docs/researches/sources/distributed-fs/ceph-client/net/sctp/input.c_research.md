# sources/distributed-fs/ceph-client/net/sctp/input.c

## Purpose
`input.c` is the SCTP ingress and lookup core. It is the handoff from IPv4/IPv6 protocol receive callbacks into SCTP association state, and it also owns endpoint hashing, transport rhashtable lookup, out-of-the-blue packet filtering, backlog requeueing, and common ICMP/ICMPv6 error validation. The code turns an `sk_buff` into an `sctp_chunk`, finds the right `struct sctp_association` or listening/control `struct sctp_endpoint`, and queues work into the receiver inqueue under the socket lock.

## Important APIs, Types, And Functions
Main entry points are `sctp_rcv()`, `sctp_backlog_rcv()`, `sctp_err_lookup()`, `sctp_err_finish()`, `sctp_v4_err()`, `sctp_udp_v4_err()`, `sctp_hash_endpoint()`, `sctp_unhash_endpoint()`, `sctp_transport_hashtable_init()`, `sctp_hash_transport()`, `sctp_unhash_transport()`, `sctp_addrs_lookup_transport()`, `sctp_epaddr_lookup_transport()`, and `sctp_has_association()`. Internal lookup helpers include `__sctp_rcv_lookup_endpoint()`, `__sctp_lookup_association()`, `__sctp_rcv_init_lookup()`, `__sctp_rcv_asconf_lookup()`, `__sctp_rcv_walk_lookup()`, and `__sctp_rcv_lookup_harder()`.

Key state lives in `sctp_ep_hashtable`, `sctp_transport_hashtable`, per-endpoint bind lists, per-transport rhashtable nodes, and skb control blocks (`SCTP_INPUT_CB`). The file relies on AF-specific operations supplied by `protocol.c` and `ipv6.c` for address extraction, validation, interface indexes, and address-parameter conversion.

## Control Flow
`sctp_rcv()` rejects non-host packets, undersized packets, bad CRCs, non-unicast addresses, policy failures, socket-filtered packets, and chunks that cannot be allocated. It linearizes when checksum work needs contiguous bytes, pulls the SCTP common header, selects the AF table from the IP version, constructs source/destination `union sctp_addr` values, and looks up an association by local address, peer address, port, net namespace, and device binding. If no association is found, it falls back to endpoint lookup; if only the control endpoint is found, `sctp_rcv_ootb()` scans all chunks and silently discards OOTB ABORT, SHUTDOWN COMPLETE, malformed chunks, or bundled non-leading INIT.

When a chunk is accepted, `sctp_rcv()` locks the target socket, handles races where an association migrated to a new socket, then either queues the skb to the socket backlog or calls `sctp_inq_push()` immediately. `sctp_backlog_rcv()` later revalidates receiver liveness and may move a backlogged skb to a new socket if peeloff/accept migration changed `rcvr->sk`.

Association lookup is two-stage. The fast path uses the transport rhashtable keyed by net namespace, local port, and peer address, then validates bound device and local bind address. The harder path inspects INIT/INIT-ACK address parameters and AUTH/ASCONF chunk sequences so multihomed associations and ADD-IP traffic can be matched even when the packet source address is not yet a known transport.

## State And Persistence
There is no disk persistence. Runtime persistence is entirely in hash table membership, transport/endpoint reference counts, socket backlog holds, and association timers/statistics. Backlog insertion takes a transport or endpoint hold so state cannot disappear while the skb waits. Transport rhashtable entries are skipped for temporary associations and removed when transports are torn down.

## Dependencies And Integration Points
This file sits between `net_protocol`/`inet6_protocol` handlers and SCTP state-machine processing. It integrates with XFRM policy, socket filters, reuseport selection, L3 master device matching, rhashtable, SCTP AF operations, ICMP modules, UDP tunneling error callbacks, and SCTP MIB counters. It calls out to `sctp_inq_push()` for state-machine delivery and `sctp_retransmit()` for PMTU-driven retransmission.

## Risks
The major risks are reference-count and lock ordering mistakes across softirq receive, socket backlog processing, and socket migration. Lookup hardening must not walk beyond skb bounds while inspecting INIT/ASCONF parameters. OOTB filtering must preserve RFC behavior: dropping dangerous packets without suppressing packets that need state-machine responses. Error handling must validate verification tags before acting on ICMP, or spoofed ICMP could corrupt PMTU, abort associations, or report false socket errors.

## Test Signals
Useful signals include SCTP over IPv4 and UDP encapsulation receive, checksum failures incrementing `SCTP_MIB_CHECKSUMERRORS`, OOTB ABORT/SHUTDOWN COMPLETE discard, INIT/INIT-ACK lookup by embedded address parameters, AUTH plus ASCONF lookup, reuseport endpoint selection, bound-device/L3 master filtering, socket-owned backlog paths, peeloff migration while packets are queued, ICMP frag-needed PMTU updates, ICMP protocol-unreachable abort events, and rhashtable duplicate transport rejection.
