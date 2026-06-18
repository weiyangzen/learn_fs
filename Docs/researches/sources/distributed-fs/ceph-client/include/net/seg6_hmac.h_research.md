# sources/distributed-fs/ceph-client/include/net/seg6_hmac.h

## Purpose
This header defines SRv6 HMAC key storage and validation APIs for authenticated Segment Routing Headers.

## Important APIs, Types, And Functions
`SEG6_HMAC_RING_SIZE` sets a ring size used by implementation internals. `struct seg6_hmac_info` stores rhashtable/RCU nodes, key id, raw secret for userspace reporting, secret length, algorithm id, and prepared SHA1/SHA256 HMAC keys. APIs compute HMACs over SRH/source address, look up/add/delete key info in a net namespace, push HMAC TLVs, validate skb SRH HMAC, and initialize/exit per-net HMAC state.

## Control Flow
Configuration paths add/delete keys in the per-net rhashtable. Packet output can push HMACs using a selected key, while input validation looks up key id and recomputes the HMAC for comparison.

## State And Persistence
HMAC key objects persist per network namespace in SRv6 per-net data and are RCU-freed. Raw secrets are retained specifically for netlink/userspace export.

## Dependencies And Integration Points
It depends on crypto SHA1/SHA256 HMAC key types, SRv6 core state, IPv6/SRH headers, routing, sockets, and rhashtable.

## Risks And Test Signals
Risks include key lifetime races, raw secret exposure, unsupported algorithm handling, incorrect HMAC coverage, and config-disabled stubs. Test signals include SRv6 HMAC netlink configuration, packet validation accept/reject, key deletion under traffic, namespace teardown, and SHA1/SHA256 algorithm cases.
