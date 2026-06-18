# sources/distributed-fs/ceph-client/include/net/inet_ecn.h

Purpose: declares Explicit Congestion Notification helpers for IPv4, IPv6, TCP, tunnels, and skb encapsulation. It centralizes ECN codepoint tests, CE marking, decapsulation rules, and congestion propagation.

Important APIs/functions: helpers classify ECN bits as not-ECT, ECT(0), ECT(1), or CE, test capability, and set CE in IP/IPv6 headers or skbs. Tunnel helpers implement RFC-style ingress/egress ECN handling, including `INET_ECN_encapsulate()`, `INET_ECN_decapsulate()`, and IPv4/IPv6 variants. TCP helpers inspect or clear ECN state in TCP headers. The header also provides skb-level functions to mark CE and update checksums.

Control flow and state: transmit encapsulation combines inner and outer ECN values; receive decapsulation validates combinations and may drop or propagate CE. Persistent state is not stored here, but packet headers and skb metadata are mutated.

Dependencies and integration: integrates with IP, IPv6, TCP, tunnels, GRO/GSO, and fragmentation ECN tables. It is used by tunnel devices and congestion-aware transports.

Risks: incorrect ECN propagation can cause congestion-signal loss or invalid CE combinations. Header checksum updates are required when IPv4 TOS changes. Tests should cover every inner/outer ECN matrix, CE marking checksums, non-ECT tunnel decap behavior, TCP ECN flags, GSO/GRO interactions, and fragmented packet ECN reassembly.
