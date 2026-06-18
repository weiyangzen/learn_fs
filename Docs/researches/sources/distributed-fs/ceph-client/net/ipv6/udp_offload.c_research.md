# sources/distributed-fs/ceph-client/net/ipv6/udp_offload.c

## Purpose
Provides IPv6 UDP offload registration for GSO/UFO and GRO. It bridges generic UDP segmentation/aggregation code with IPv6 pseudo-header checksums, IPv6 fragment-header insertion, UDP tunnel segmentation, and UDP encapsulation socket lookup for GRO.

## Important APIs, types, and functions
The registered callbacks are `udp6_ufo_fragment`, `udp6_gro_receive`, and `udp6_gro_complete`, installed by `udpv6_offload_init` into `net_hotdata.udpv6_offload` and removed by `udpv6_offload_exit`. Helper `udp6_gro_lookup_skb` locates UDP tunnel or normal UDP sockets for encapsulated GRO decisions.

## Control flow
`udp6_ufo_fragment` handles UDP tunnel GSO first, dispatches UDP L4 GSO to `__udp_gso_segment`, or performs software UFO for legacy `SKB_GSO_UDP`: it completes the UDP checksum, ensures headroom, finds the first fragmentable IPv6 option, inserts a fragment header by moving the unfragmentable header region, selects an identification value, then calls `skb_segment`. `udp6_gro_receive` validates or converts UDP checksums unless the packet is already marked for flush, optionally looks up encapsulation sockets when `udpv6_encap_needed_key` is active, and delegates to `udp_gro_receive`. `udp6_gro_complete` finalizes fraglist or normal GRO packets, setting UDP length, GSO metadata, and pseudo-header checksum before calling `udp_gro_complete`.

## State and persistence behavior
No persistent state is owned. The file mutates per-packet skb headers, checksum flags, `skb_shinfo()` GSO metadata, and NAPI GRO control block fields. The only longer-lived state is the global IPv6 offload callback slot registered at init.

## Dependencies and integration points
Depends on `inet6_add_offload`, `inet6_del_offload`, generic UDP GRO/GSO, UDP tunnel GSO, IPv6 checksum helpers, `ip6_find_1stfragopt`, fragment header layout, and socket lookup from `udp.c`. It integrates with ESP-in-UDP indirectly because GRO socket lookup can find tunnel encapsulation sockets.

## Risks and test signals
Important risks are incorrect header movement when adding the fragment header, checksum mistakes around zero or converted checksums, tunnel-vs-plain GSO dispatch errors, and GRO completion metadata that confuses later segmentation. Test with UDPv6 GSO, UDP tunnel GSO, fraglist GRO, checksum-offload and software-checksum devices, packets with extension headers before the fragmentable region, and unregister/re-register paths during IPv6 stack teardown.
