# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd-idl.h

## Purpose
Defines the on-wire socklnd protocol structures shared by the TCP socket LNet driver and any peer that must parse socklnd handshakes or messages. It is intentionally compact and packed, because the structures are serialized directly across sockets.

## Important APIs, types, and constants
`struct ksock_hello_msg` is the current large-NID hello frame. It carries magic, protocol version, source/destination NIDs and PIDs, incarnation counters, connection type, and deprecated IP-vector fields. `struct ksock_hello_msg_nid4` is the legacy NID4-compatible form used by protocol v2/v3. `struct ksock_msg_hdr` prefixes v2+ data messages with message type, checksum, and two zero-copy cookies. `struct ksock_msg` unions NID4 and NID16 LNet headers after that socklnd header. `KSOCK_MSG_NOOP`, `KSOCK_MSG_LNET`, and `KSOCK_PROTO_V2/V3/V4` define the message and protocol discriminators.

## Control flow and integration
This header has no executable control flow. `socklnd_proto.c` fills and parses these structures in per-version hello, pack, unpack, zero-copy ACK, and matching routines. `socklnd_cb.c` receives `struct ksock_msg_hdr` before deciding whether to consume an LNet header, a NOOP, a zero-copy ACK, or slop bytes. `socklnd.c` uses the hello fields to validate peer identity, connection type, protocol compatibility, and incarnation changes.

## State and persistence
The file defines transient wire state only. The incarnation fields let runtime code distinguish a live peer from a rebooted peer and force protocol renegotiation when necessary. Zero-copy cookies are persisted only in memory by `ksnp_zc_req_list` while a sender waits for a matching ACK.

## Dependencies
Depends on UAPI LNet types and socklnd connection type constants. Packed layout and integer widths are part of the protocol contract.

## Risks and test signals
Risks concentrate in ABI drift: changing field order, packing, widths, or protocol constants breaks interoperability. NID4/NID16 conversion paths should be tested with IPv4, IPv6 or large-NID peers, byte-swapped peers, zero-copy ACK traffic, and mixed protocol-version negotiation.
