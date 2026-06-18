# sources/distributed-fs/ceph-client/include/net/pfcp.h

Purpose: defines PFCP-over-UDP header layouts, metadata, headroom constants, and helpers for PFCP virtual netdevices.

Important APIs and types: `struct pfcphdr` contains flags, message type, and length. `struct pfcphdr_node` and `struct pfcphdr_session` model node and session message suffixes, including SEID, sequence number, and message priority. `struct pfcp_metadata` carries tunnel metadata type and SEID. Constants define port 8805, flags, version mask, header sizes, IPv4/IPv6 headroom, and node/session metadata types. Inline helpers locate PFCP headers after `udp_hdr()` and test `netif_is_pfcp()`.

Control flow: UDP tunnel/device code parses the base header, branches on SEID/session flag, accesses node/session suffix, and uses metadata for encapsulation/decapsulation.

State and persistence: no state is stored here; PFCP netdevices and tunnel metadata hold runtime state elsewhere.

Dependencies and integration points: depends on UDP/IP/IPv6/ethernet UAPI headers, dst metadata, netdevice rtnl link ops, and skbuff UDP header positioning.

Risks and test signals: risks include insufficient skb length checks before inline casts, endian/bitfield priority mismatch, wrong headroom for encapsulation, and device-kind string drift. Test node/session packet parsing, IPv4/IPv6 encapsulation headroom, malformed short packets, SEID metadata propagation, and PFCP link creation.
