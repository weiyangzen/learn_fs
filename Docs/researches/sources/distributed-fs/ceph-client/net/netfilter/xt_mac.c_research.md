<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c

## Purpose
`xt_mac.c` implements source MAC address matching for Ethernet-like packets.

## Important APIs, Types, and Functions
`mac_mt()` compares the skb's Ethernet source address with `struct xt_mac_info.srcaddr`. `mac_mt_reg[]` registers `mac` for IPv4 and IPv6 families.

## Control Flow, State, and Persistence
The matcher requires the packet to have a link-layer header and an Ethernet header. It compares `eth_hdr(skb)->h_source` to the configured address and applies inversion. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, skb MAC header validity, and Ethernet header layout. It is meaningful primarily in ingress hooks where the original L2 source is present.

## Risks and Test Signals
Risks include using the match in hooks where MAC headers are absent or rewritten, non-Ethernet devices, and bridged/tunneled traffic expectations. Tests should cover matching and inverted MACs, no MAC header, short headers, IPv4/IPv6 aliases, and ingress versus local-output behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mac.c -->
