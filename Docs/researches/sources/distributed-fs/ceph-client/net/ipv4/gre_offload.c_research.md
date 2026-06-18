# sources/distributed-fs/ceph-client/net/ipv4/gre_offload.c

## Purpose
`gre_offload.c` provides GRE GSO and GRO support for IPv4 and, when enabled, IPv6 offload tables. It lets encapsulated GRE traffic be segmented and coalesced while preserving GRE checksum, key, and inner protocol semantics.

## Important APIs, Types, And Functions
The main callbacks are `gre_gso_segment`, `gre_gro_receive`, and `gre_gro_complete`, grouped in `gre_offload`. `gre_offload_init` registers the callbacks with `inet_add_offload(IPPROTO_GRE)` and optionally `inet6_add_offload`.

## Control Flow
GSO validates that the skb is encapsulated and has at least a GRE header, pulls outer tunnel headers, converts skb context to the inner packet, filters hardware features, segments the inner packet with `skb_mac_gso_segment`, then pushes outer headers back onto each segment. If GRE checksum is required it computes or sets up hardware checksum offload, including special adjustment for GSO partial.

GRO rejects already marked encapsulation, reads the GRE header from GRO offsets, supports only version 0 with key and checksum flags, rejects GRE checksum under FOU/GUE because the GRE header location is not trackable there, finds the inner protocol GRO handler, validates header length, optionally validates checksum, compares flags/protocol/key against existing packets in the GRO list, pulls GRE bytes, updates checksum state, and delegates to the inner GRO callback.

GRO completion marks encapsulation, sets `SKB_GSO_GRE`, derives GRE header length from key/checksum flags, delegates completion to the inner protocol, and sets the inner MAC header.

## State And Persistence
No per-flow state is owned by this file. Persistent state is the registered `net_offload` callback table. Per-packet state is carried in skb headers, `skb_shinfo`, and `NAPI_GRO_CB`.

## Dependencies And Integration Points
It depends on skb GSO/GRO helpers, GRE header definitions, inet/inet6 offload registration, device hardware feature flags, IPsec dst state, FOU/GUE GRO markers, and inner protocol offload callbacks found by ethertype.

## Risks
Risks include corrupting skb header offsets during GSO unwind, incorrect GRE checksum handling with partial GSO, over-aggregation packets with different GRE keys or flags, and unsupported sequence/routing flags. FOU/GUE interaction is intentionally conservative for GRE checksum.

## Test Signals
Test GRE GSO with and without GRE checksum, hardware checksum offload, GSO partial, IPsec destinations, GRO aggregation with matching and mismatching keys, unsupported sequence flag rejection, FOU/GUE-encapsulated GRE checksum rejection, IPv6 registration failure unwind, and packet header offsets after segmentation.
