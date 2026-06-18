# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_input.c

## Purpose
Implements IPv6-specific XFRM inbound glue for IPsec and related transforms. It marks IPv6 SPI lookup metadata, handles transport-mode finish and netfilter reinjection, decapsulates ESP-in-UDP for IPv6 including GRO support, receives tunnel packets, and exposes an address-based state lookup path.

## Important APIs, types, and functions
Exports `xfrm6_rcv_spi`, `xfrm6_rcv_tnl`, `xfrm6_rcv`, and `xfrm6_input_addr`. UDP encapsulation entry points are `xfrm6_udp_encap_rcv` and `xfrm6_gro_udp_encap_rcv`. Transport completion is split across `xfrm6_transport_finish` and `xfrm6_transport_finish2`.

## Control flow
`xfrm6_rcv_spi` records tunnel and IPv6 destination-offset metadata in skb control blocks, then calls generic `xfrm_input`. `xfrm6_transport_finish` restores the next-header byte from XFRM mode state, pushes network header bytes back, updates payload length and receive checksum, and either returns to GRO/L2 reinjection or runs the IPv6 pre-routing netfilter hook before `ip6_rcv_finish`.

`__xfrm6_udp_encap_rcv` inspects a UDP-encapsulated payload, eats NAT keepalives, lets IKE packets continue through UDP, identifies ESP packets, unclones the skb, reduces IPv6 payload length, and either pulls UDP/non-ESP-marker bytes or advances the transport header. `xfrm6_udp_encap_rcv` then calls `xfrm6_rcv_encap` for ESP. GRO handling finds ESP offload callbacks, rejects keepalive/IKE-looking payloads, marks UDP as the outer protocol, and calls ESP GRO receive.

`xfrm6_input_addr` allocates or extends the skb security path, tries exact, wildcard-source, then wildcard-address state lookup, rejects wrong-direction SAs, checks validity/expiry under state lock, invokes transform input, records the accepted state in `sec_path`, and updates lifetime byte/packet counters.

## State and persistence behavior
State changes live in skb control blocks, secpath vectors, XFRM state refcounts, state lifetime counters, and IPv6 header fields after UDP decapsulation. No disk persistence exists. A successful `xfrm6_input_addr` holds a state reference by storing it in `sp->xvec`.

## Dependencies and integration points
Depends on generic XFRM input, XFRM state DB, secpath management, netfilter IPv6 pre-routing, ESP offload registration in `inet6_offloads`, UDP encapsulation sockets from UDPv6, IPv4 fallback for IPv4 packets on dual-stack sockets, GRO infrastructure, and IP6 tunnel metadata.

## Risks and test signals
Risks include mishandling keepalive/IKE vs ESP detection, incorrect payload-length adjustment, unclone failure, secpath depth overflow, accepting wrong-direction SAs, and GRO packets losing L2 header context. Test ESP-in-UDP receive, NAT keepalives, IKE pass-through, transport-mode netfilter policy, tunnel receive, wildcard XFRM state lookup, invalid/expired SA rejection, GRO ESP-in-UDP, and XFRM MIB/audit counters on state misses.
