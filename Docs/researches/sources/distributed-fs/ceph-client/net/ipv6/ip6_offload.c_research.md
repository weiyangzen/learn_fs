# sources/distributed-fs/ceph-client/net/ipv6/ip6_offload.c

Purpose: registers and implements IPv6 GSO/GRO packet offload handling, including extension-header parsing and offload support for IPv6-in-IPv4/SIT, IPv6-in-IPv6, and IPv4-in-IPv6 tunnels.

Important APIs, types, and functions: `ipv6_gso_segment()`, `ipv6_gro_receive()`, `ipv6_gro_complete()`, `ipv6_offload_init()`, and tunnel callbacks `sit_*`, `ip4ip6_*`, and `ip6ip6_*`. It includes `tcpv6_offload.c` and initializes TCP and extension-header offloads.

Control flow: GSO resets headers, pulls the IPv6 header and registered extension headers marked `INET6_PROTO_GSO_EXTHDR`, delegates segmentation to the next protocol offload, then fixes payload lengths and fragment headers for UDP fragmentation. GRO reads the IPv6 header from the GRO cursor, compares flow keys across the GRO list ignoring length and traffic class, pulls extension headers, sets transport offsets, and delegates to TCP, UDP, or generic protocol offload. GRO complete updates payload length, skips extension headers, and completes the inner protocol, marking encapsulation for tunnel callbacks.

State and persistence: initialization stores an IPv6 `packet_offload` in `net_hotdata.ipv6_packet_offload`, adds it to device offload lists, and registers inet/inet6 tunnel offloads. Runtime state is skb/GRO/GSO metadata only.

Dependencies and integration points: depends on global `inet6_offloads`, `net_hotdata` TCP/UDP offload structs, device offload registration, GRO/GSO helpers, TCPv6 and UDPv6 offload code, and extension-header offload init.

Risks: extension-header parsing assumes registered offload flags accurately identify headers safe to skip. Fragment offset fixups for UDP GSO are sensitive to payload length calculations. The file directly includes `tcpv6_offload.c`, so build ordering and symbol visibility differ from normal separate compilation. Encapsulation feature masking must respect hardware offload capabilities.

Test signals: TCPv6/UDPv6 GRO and GSO, packets with Hop-by-Hop/Destination/Routing extension headers, UDP fragmentation GSO, nested IPv6 tunnels, SIT/ip4ip6/ip6ip6 GRO complete, hardware feature masking for encapsulation, and failure paths for missing protocol offloads.
