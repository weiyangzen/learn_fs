# sources/distributed-fs/ceph-client/net/sctp/output.c

## Purpose
`output.c` implements packet-level SCTP output assembly. It owns `struct sctp_packet` initialization, chunk bundling decisions, DATA accounting when chunks are appended, AUTH/SACK/PAD opportunistic bundling, GSO packet packing, checksum setup, and final transmission through AF-specific `sctp_xmit` callbacks.

## Important APIs, Types, And Functions
External APIs include `sctp_packet_init()`, `sctp_packet_config()`, `sctp_packet_free()`, `sctp_packet_append_chunk()`, `sctp_packet_transmit_chunk()`, and `sctp_packet_transmit()`. Core helpers are `sctp_packet_reset()`, `sctp_packet_bundle_auth()`, `sctp_packet_bundle_sack()`, `sctp_packet_bundle_pad()`, `__sctp_packet_append_chunk()`, `sctp_packet_can_append_data()`, `sctp_packet_append_data()`, `sctp_packet_will_fit()`, `sctp_packet_pack()`, and `sctp_packet_gso_append()`.

## Control Flow
`sctp_packet_config()` prepares a transport packet for a flush cycle: it sets the verification tag, path MTU, header overhead, route cache, PMTU synchronization, optional prepended ECNE chunk, socket dst caps, and GSO max size. `sctp_packet_append_chunk()` first applies DATA-specific congestion/window/Nagle checks, then may prepend AUTH and pending SACK chunks before appending the requested chunk. `__sctp_packet_append_chunk()` updates packet flags and, for DATA/I-DATA, assigns TSN and stream sequence numbers, marks RTT measurement candidates, and accounts flight size, outstanding bytes, and peer rwnd.

`sctp_packet_transmit_chunk()` flushes a packet when appending hits PMTU/GSO limits, unless a COOKIE-ECHO packet must remain constrained. `sctp_packet_transmit()` allocates the outgoing head skb, writes the SCTP common header, verifies a dst exists, packs chunks into one skb or a GSO frag list, starts autoclose if DATA was sent, applies ECN capability, updates association packet stats, and calls the transport AF `sctp_xmit()` function. Cleanup frees unsent non-DATA control chunks and resets the packet object.

## State And Persistence
State is in-memory and per packet/transport/association. DATA append mutates transport `flight_size`, association `outstanding_bytes`, peer rwnd, TSN counters, stream sched numbering, chunk `sent_at`, `sent_count`, and RTT flags. Packet flags such as `has_data`, `has_sack`, `has_auth`, `has_cookie_echo`, and `ipfragok` live only for a flush cycle.

## Dependencies And Integration Points
This file depends on chunk constructors from the state machine, SCTP auth, SACK generation, stream scheduler callbacks, PMTU/path state in transports, skbuff allocation/accounting, AF-specific xmit from `protocol.c`/`ipv6.c`, device GSO capabilities, xfrm dst checks, and SCTP MIB/stat counters.

## Risks
The major risks are accounting chunks as in flight before final xmit, mismatched AUTH key bundling, bad PMTU/GSO split decisions, incorrect CRC offload selection, freeing control chunks while preserving DATA chunks for retransmission, and Nagle/rwnd/cwnd checks that can stall or overrun transmission. GSO packing must preserve AUTH HMAC placement and recalculate HMAC after chunks are copied.

## Test Signals
Exercise DATA sends under rwnd full, cwnd full, Nagle delay, no-delay, PMTU-full, GSO-enabled, GSO-disabled, AUTH-required, pending SACK bundling, COOKIE-ECHO bundling, heartbeat PLPMTUD PAD chunks, UDP encapsulation, xfrm routes, missing dst, autoclose timer start, and checksum paths with and without SCTP CRC offload.
