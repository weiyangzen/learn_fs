# sources/distributed-fs/ceph-client/net/ipv6/tcp_ao.c

## Purpose
`tcp_ao.c` provides IPv6-specific support for TCP Authentication Option (TCP-AO, RFC 5925). It derives IPv6 traffic keys, looks up matching master keys for sockets and requests, hashes IPv6 pseudoheaders and skbs, parses IPv6 AO socket options, and signs SYN-ACKs.

## Important APIs, types, and functions
`tcp_v6_ao_calc_key()` builds the AO KDF input block containing label `"TCP-AO"`, IPv6 source and destination addresses, ports, send/receive ISNs, and output length, then calls common `tcp_ao_calc_traffic_key()`. Wrappers adapt it to different contexts: `tcp_v6_ao_calc_key_skb()`, `tcp_v6_ao_calc_key_sk()`, and `tcp_v6_ao_calc_key_rsk()`.

Lookup helpers `tcp_v6_ao_lookup()` and `tcp_v6_ao_lookup_rsk()` choose the L3 master index and IPv6 peer address before calling common `tcp_ao_do_lookup()`. Hash helpers are `tcp_v6_ao_hash_pseudoheader()`, `tcp_v6_ao_hash_skb()`, and `tcp_v6_ao_synack_hash()`. `tcp_v6_parse_ao()` delegates socket option parsing to the common TCP-AO parser with `AF_INET6`.

## Control flow
Key derivation starts a TCP signature pool, writes a packed KDF input into the pool scratch buffer, asks common AO code to calculate the traffic key, and ends the pool. The socket wrapper swaps address/port and ISN order for receive direction. The request wrapper derives from `inet_request_sock` IPv6 local/remote addresses and TCP request ISNs.

For packet authentication, pseudoheader hashing writes IPv6 source, destination, TCP length, and protocol into the scratch buffer and updates the async hash request. Full skb hashing delegates to common AO skb hashing with `AF_INET6`. SYN-ACK hashing allocates a temporary traffic-key buffer, derives the request key, hashes the SYN-ACK skb, and frees the buffer.

## State and persistence
This file does not own long-lived AO key state. Keys live in common TCP-AO structures attached to sockets or time-wait/request state. Local state is temporary stack data, signature-pool scratch memory, and a temporary SYN-ACK hash buffer.

## Dependencies and integration points
It integrates with the common TCP-AO implementation, TCP signature pool, crypto ahash API, IPv6 socket/request structures, L3 master device lookup, and the TCPv6 ops tables in `tcp_ipv6.c`. The functions are selected through `tcp_sock_af_ops` and `tcp_request_sock_ops` when `CONFIG_TCP_AO` is enabled.

## Risks and edge cases
Send and receive key derivation must use the correct address/port/ISN orientation or peers will compute different traffic keys. L3 master index selection affects key matching for VRF-bound sockets. SYN-ACK hashing uses `GFP_ATOMIC`; allocation failure must cleanly abort authentication. The packed KDF input layout must remain consistent with RFC 5925 and common AO code. Temporary traffic keys must be freed on every exit path.

## Test signals
Tests should configure TCP-AO on IPv6 sockets, verify successful connection establishment, failed authentication with wrong keys or key IDs, VRF/l3mdev-specific key lookup, send and receive key directionality, SYN-ACK signing under request sockets, option parsing errors, and allocation-failure/error injection around signature pool and SYN-ACK key allocation.
