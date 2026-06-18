<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/output.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/output.c

## Purpose
`output.c` is the AF_RXRPC packet transmission engine. It sends ACKs, PMTU probes, call and connection aborts, DATA and jumbo DATA packets, reject packets, keepalive VERSION packets, and security RESPONSE packets through the local UDP socket.

## Important APIs, Types, And Functions
Important functions include `do_udp_sendmsg()`, `rxrpc_send_ACK()`, `rxrpc_send_probe_for_pmtud()`, `rxrpc_send_abort_packet()`, `rxrpc_send_data_packet()`, `rxrpc_send_conn_abort()`, `rxrpc_reject_packet()`, `rxrpc_send_keepalive()`, and `rxrpc_send_response()`. Internal helpers allocate/fill ACK buffers, start RTT probes, choose REQUEST_ACK reasons, prepare TX queue metadata, and assemble jumbo subpackets.

## Control Flow
ACK transmission allocates page-frag-backed header/SACK/trailer buffers, snapshots receive ACK-window state, fills ACK reason, SACK bytes, advertised receive window and MTU, optionally starts RTT or PMTU probes, and sends through UDP. DATA transmission allocates a wire header, obtains serials for all subpackets, updates TX queue RACK/TLP metadata, secures prebuilt txbufs, sets jumbo headers after the first subpacket, toggles DF according to PMTU/retransmission decisions, advances `tx_transmitted`, handles injected loss, maps send failures to call completion for unrecoverable initial/routing errors, and updates TX backoff. Control packet helpers build ABORT, BUSY, VERSION, and RESPONSE packets and trace outcomes.

## State And Persistence
The file mutates call transmission state: serials, ACK counters, RTT slots, keepalive deadlines, expected-RX timers, RACK/TLP timers, tx counts, `tx_backoff`, `tx_transmitted`, PMTU probe fields, and local page-frag buffers/kvec/bvec scratch arrays. Peer state receives last-transmit marks and PMTU probe flags.

## Dependencies And Integration Points
It depends on `protocol.h`, UDP/UDPv6 send paths, local endpoint DF controls, peer PMTU state, congestion/RACK/TLP helpers, security-prepared txbufs, response SKBs from RxGK/RxKAD, receive ACK state, tracepoints, and rxrpc statistics.

## Risks And Edge Cases
ACK buffer allocation may fail under pressure and drops the ACK. PMTU probes deliberately pad ACKs and must not exceed kvec capacity. Jumbo sequencing and serial assignment must remain consistent across TX queue boundaries. `-EMSGSIZE` is treated specially for PMTU feedback, while some routing errors complete calls. Abort suppression for client calls after all request data is hard-ACKed prevents wasting a reusable channel.

## Test Signals
High-value tests include DATA send/retransmit/jumbo paths, SACK ACK formatting, REQUEST_ACK reason counters, PMTU probe success/failure, IPv6 `do_udp_sendmsg()`, abort/reject packet formatting, connection RESPONSE sends from security modules, injected TX loss, RACK/TLP timer updates, and stats/tracepoint validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/output.c -->
