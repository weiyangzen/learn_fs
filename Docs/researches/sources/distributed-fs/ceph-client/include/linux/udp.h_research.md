# sources/distributed-fs/ceph-client/include/linux/udp.h

## Purpose
Defines in-kernel UDP socket state, hashing helpers, socket flags, encapsulation/GRO hooks, and convenience accessors for UDP networking.

## Important APIs, Types, And Functions
Key exports include `udp_hdr()`, UDP hash-table size constants, `udp_hashfn()`, UDP flag bits, `struct udp_prod_queue`, `struct udp_sock`, flag macros (`udp_test_bit`, `udp_set_bit`, etc.), `UDP_MAX_SEGMENTS`, `udp_sk()`, `udp_set_peek_off()`, no-check6 accessors, `udp_cmsg_recv()`, static keys `udp_encap_needed_key` and `udpv6_encap_needed_key`, `udp_encap_needed()`, `udp_unexpected_gso()`, `udp_allow_gso()`, hash iteration macros, and `udp_tunnel_sk()`.

## Control Flow
UDP paths derive headers from skb transport offsets, hash ports with per-netns mix, set socket flags atomically, and handle GRO/GSO acceptance. `udp_cmsg_recv()` reports UDP GRO segment size via control message when the skb is UDP L4 GSO. `udp_unexpected_gso()` rejects GSO packets not accepted by the socket or suspicious for tunnel encapsulation when encapsulation static keys and callbacks are active.

## State, Persistence, And Dependencies
`struct udp_sock` extends `inet_sock` and stores hash nodes, flags, corking length/GSO size, encapsulation callbacks, GRO callbacks, producer queue, reader queue, forward accounting, peek offset cache, tunnel list, and NUMA drop counters. Dependencies include inet sockets, skbuff, netns hashing, UAPI UDP, static keys, and optional IPv6/UDP tunnel configs.

## Integration Points
Used by IPv4/IPv6 UDP receive/transmit, UDP tunnels, GRO/GSO offload, socket control messages, per-net namespace hash tables, and encapsulation protocols.

## Risks And Test Signals
Risks include accepting unexpected GSO into tunnels, stale `peeking_with_offset`, incorrect per-net hash masks, callback lifetime races, zero-checksum policy mistakes, and cacheline-sensitive field churn. Test signals include UDP GRO/GSO tests, tunnel receive with malformed GSO types, IPv6 zero-checksum options, hash distribution tests, peek-offset recvmsg behavior, and encapsulation static-key enable/disable coverage.
