# sources/distributed-fs/ceph-client/net/ipv6/esp6_offload.c

## Purpose
Adds IPv6 ESP GRO/GSO and hardware offload support. It registers ESP as an IPv6 net offload protocol and as an XFRM type offload, enabling receive aggregation, segmentation, hardware transmit marking, and software fallback through the normal `esp6.c` helpers.

## Important APIs, Types, and Functions
Core callbacks are `esp6_gro_receive()`, `esp6_gso_segment()`, `esp6_input_tail()`, `esp6_xmit()`, and `esp6_gso_encap()`. Mode-specific segmentation helpers include `xfrm6_tunnel_gso_segment()`, `xfrm6_transport_gso_segment()`, and `xfrm6_beet_gso_segment()`. Registration is through `struct net_offload esp6_offload` and `struct xfrm_type_offload esp6_type_offload`.

## Control Flow
GRO receive pulls to the ESP offset, parses SPI/sequence, ensures a secpath and XFRM state, records offload metadata, stores next-header offset information, and invokes `xfrm_input()` asynchronously, returning `-EINPROGRESS` to GRO. GSO validates `SKB_GSO_ESP`, strips ESP header/IV for segmentation, adjusts feature masks depending on hardware ESP capabilities, marks `XFRM_GSO_SEGMENT`, and dispatches by outer XFRM mode. Transmit computes ESP trailer sizes, prepares headers for GSO or non-GSO packets, updates offload sequence numbers, fixes IPv6 payload length, either marks the skb for hardware XFRM transmit or falls back to `esp6_output_tail()`.

## State and Persistence
Uses per-packet `struct xfrm_offload`, secpath entries, skb GSO flags, XFRM SA offload device metadata (`x->xso.dev`), and sequence counters in `xo->seq`. No persistent storage exists.

## Dependencies and Integration Points
Depends on `esp6.c` exported output/input helpers, XFRM offload core, IPv6 inet offload tables, GRO/GSO infrastructure, hardware feature bits such as `NETIF_F_HW_ESP`, and mode-specific inner protocol offloads.

## Risks and Test Signals
Risks include wrong next-header offset detection through extension headers, secpath leaks on GRO failure, sequence increments for GSO segment counts, feature-mask mismatch causing bad checksums, BEET IPv4/IPv6 header offset mistakes, and software fallback divergence from normal ESP. Test signals include GRO on ESP and ESP-in-UDP, GSO transport/tunnel/BEET, hardware ESP with and without TX checksum, fallback path, ESN sequencing across GSO, and invalid SPI/state direction rejection.
