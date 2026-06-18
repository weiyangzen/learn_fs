# sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_getport.h

## Purpose
This header declares helpers for extracting L4 ports from IPv4/IPv6 packets for ipset match dimensions and defines which protocols carry ports.

## Important APIs, Types, and Functions
It declares `ip_set_get_ip4_port()` and, when IPv6 iptables is enabled, `ip_set_get_ip6_port()`. The fallback IPv6 inline returns `false` when IPv6 support is not built. `ip_set_proto_with_ports()` returns true for TCP, SCTP, UDP, and UDPLITE.

## Control Flow
Callers parse skb protocol state, ask the appropriate helper to extract source or destination port and protocol, and gate port-dependent matching with `ip_set_proto_with_ports()`. IPv6 builds without `CONFIG_IP6_NF_IPTABLES` short-circuit unsupported extraction.

## State and Persistence
No persistent state is declared. Results are derived from packet headers.

## Dependencies and Integration Points
The header depends on `sk_buff`, kernel types, and uapi IP protocol constants. It integrates with ipset hash/list types that include port dimensions and with IPv4/IPv6 netfilter packet parsing.

## Risks
Fragmented, malformed, or non-initial L4 headers can make extraction fail. Build-time IPv6 support changes behavior. Protocols without ports must not be treated as matchable port keys.

## Test Signals
Packet tests for TCP/UDP/SCTP/UDPLITE source and destination ports, fragmented packets, non-port protocols, IPv6-enabled and IPv6-disabled builds, and short skb/header-boundary cases.
