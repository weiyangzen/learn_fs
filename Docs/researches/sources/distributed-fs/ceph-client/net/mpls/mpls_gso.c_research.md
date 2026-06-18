<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c -->
# sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c

## Purpose
Registers Generic Segmentation Offload support for MPLS unicast and multicast Ethernet protocol types. It temporarily exposes the inner packet to the generic GSO machinery, then restores MPLS headers and skb metadata on each output segment.

## Important APIs, Types, and Functions
`mpls_gso_segment()` is the packet offload callback. `mpls_uc_offload` and `mpls_mc_offload` are `struct packet_offload` registrations for `ETH_P_MPLS_UC` and `ETH_P_MPLS_MC`. `mpls_gso_init()` adds both offloads with `dev_add_offload()`, and `mpls_gso_exit()` removes them.

## Control Flow
The callback requires an inner network header, computes the MPLS header length between current and inner network headers, validates that it is non-zero, pullable, and a multiple of `MPLS_HLEN`, then changes `skb->protocol` to the inner protocol and pulls the MPLS stack. It segments with `skb_mac_gso_segment()` using `skb->dev->mpls_features & features`. On failure it unwinds protocol/header state. On success it iterates each segment, restores MPLS protocol, resets inner/network/mac headers, and pushes back the original MAC plus MPLS header length.

## State and Persistence
The module stores only static offload descriptors. Per-packet state is skb header offsets, protocol, mac length, inner protocol, and segment chain metadata. No durable state or sysctl exists here.

## Dependencies and Integration Points
Depends on the GSO core, packet offload registration, `skbuff` header manipulation, `netdev_features_t`, and MPLS EtherTypes. It complements `af_mpls.c` and `mpls_iptunnel.c`, allowing MPLS-encapsulated packets to be segmented according to inner protocol capabilities advertised in `dev->mpls_features`.

## Risks
Correctness depends on valid inner header metadata being set by the encapsulation path. Header length arithmetic must restore exactly the bytes pulled before segmentation. Bad MPLS header length validation can corrupt skb layout. Device `mpls_features` must be set conservatively; otherwise inner segmentation can produce segments unsupported by the output device.

## Test Signals
Exercise large TCP payloads over MPLS with GSO enabled and disabled, both unicast and multicast MPLS EtherTypes, invalid or missing inner header metadata, multi-label stacks, segmentation failure unwind paths, and packet captures verifying each segment retains the expected MPLS stack and inner protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/mpls_gso.c -->
