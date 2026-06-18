# sources/distributed-fs/ceph-client/net/ipv6/tcpv6_offload.c

## Purpose
`tcpv6_offload.c` registers TCPv6 GRO and GSO callbacks. It lets the IPv6 stack coalesce inbound TCPv6 packets and segment outbound TCPv6 skbs, including fraglist GRO/GSO cases and checksum repair when segmented packets carry differing headers.

## Important APIs, types, and functions
`tcp6_gro_receive()` validates the TCPv6 GRO checksum, pulls the TCP header, optionally detects fraglist GRO eligibility with `tcp6_check_fraglist_gro()`, and delegates to common `tcp_gro_receive()`. `tcp6_gro_complete()` finalizes a GRO skb, marks `SKB_GSO_TCPV6`, computes the pseudoheader checksum, or marks fraglist GSO. `tcp6_gso_segment()` validates TCPv6 GSO, handles fraglist segmentation, fixes partial checksum state, and delegates to `tcp_gso_segment()`.

Fraglist-specific helpers are `tcp6_check_fraglist_gro()`, `__tcpv6_gso_segment_csum()`, `__tcpv6_gso_segment_list_csum()`, and `__tcp6_gso_segment_list()`. `tcpv6_offload_init()` installs the callbacks in `net_hotdata.tcpv6_offload` and registers them with `inet6_add_offload()`.

## Control flow
On GRO receive, the code avoids checksum work when a flush is already required. Otherwise it validates with `ip6_gro_compute_pseudo`, pulls the TCP header, checks whether a matching established socket exists for fraglist GRO, records `NAPI_GRO_CB(skb)->is_flist`, and passes the packet to generic TCP GRO.

On GRO completion, fraglist packets set `SKB_GSO_FRAGLIST | SKB_GSO_TCPV6`, copy the segment count, and mark checksum unnecessary. Non-fraglist packets write an inverted TCPv6 pseudoheader checksum, set TCPv6 GSO type, and run common TCP GRO completion.

On GSO, non-TCPv6 skbs and too-short headers fail. Fraglist GSO uses `skb_segment_list()` only when the skb layout matches the expected gso size and is not dodgy; otherwise checksum is forced back to software. If checksum state is not partial, the code builds the pseudoheader checksum before calling common TCP GSO. Segment-list checksum repair normalizes source/destination IPv6 addresses and TCP ports across later segments when they differ from the first segment.

## State and persistence
The file owns no persistent per-flow state. It initializes a global hotdata offload callback structure at boot/module init. Runtime state is in skb shared info, NAPI GRO control block fields, checksums, and temporary socket lookup references.

## Dependencies and integration points
It depends on generic GRO/TCP offload code, IPv6 pseudoheader checksum helpers, inet6 established socket lookup, NAPI GRO metadata, skb fraglist segmentation, `ip6_offload.h`, and the IPv6 offload registry. It is reached by device receive/transmit offload paths, not normal TCP socket code directly.

## Risks and edge cases
Fraglist GRO must not merge packets for an established socket that expects normal stream processing. Socket lookup references must be released. Checksum repair for segment lists must update IPv6 addresses and TCP ports exactly once per changed segment. The GSO path must reject malformed or non-TCPv6 skbs and avoid trusting dodgy fraglist layouts. Incorrect `gso_type` flags would hand incompatible skbs to drivers.

## Test signals
Tests should exercise TCPv6 GRO aggregation, GRO checksum failure flushing, fraglist GRO with and without established socket lookup, TCPv6 GSO with `CHECKSUM_PARTIAL`, GSO from software checksum state, fraglist GSO valid and dodgy layouts, NAT-like segment-list checksum repair for changed addresses/ports, and registration through `inet6_add_offload()`.
