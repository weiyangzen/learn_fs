<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls.h -->
# sources/distributed-fs/ceph-client/include/net/mpls.h

## Purpose
`mpls.h` provides minimal MPLS shim-header helpers for Ethernet protocol classification, skb network-header access, and label-stack-entry construction.

## Important APIs, types, and functions
It defines `MPLS_HLEN`, `struct mpls_shim_hdr`, `eth_p_mpls`, `mpls_hdr`, and `mpls_entry_encode`.

## Control flow
Callers identify MPLS unicast/multicast ethertypes, cast skb network header to an MPLS shim header, and encode label/traffic-class/bottom-of-stack/TTL into a big-endian 32-bit label stack entry.

## State and persistence
No state is stored. The only state is packet header data in skbs.

## Dependencies and integration points
It depends on Ethernet protocol constants, netdevice/skb declarations, and UAPI MPLS bit shifts. It integrates MPLS forwarding, tunnels, and protocol parsing.

## Risks and test signals
Risks include caller failure to ensure the skb has at least four bytes, label/TTL/TC range overflow before shifting, and BOS mistakes for stacked labels. Tests should cover ethertype matching, encode/decode vectors, boundary labels, TTL zero, and skb length validation in callers.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mpls.h` completely for this pass (45 lines, 943 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mpls.h -->
