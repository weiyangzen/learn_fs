# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tuple_common.h

## Purpose
Defines common conntrack tuple direction enum, manipulable protocol-port/key union, and ctinfo-to-direction helper macro.

## Important APIs, Types, And Functions
Exports `ip_conntrack_dir`, `nf_conntrack_man_proto`, and `CTINFO2DIR(ctinfo)`. The union includes generic `all`, TCP/UDP/DCCP/SCTP ports, ICMP id, and GRE key fields in network byte order.

## Control Flow
Conntrack/NAT code maps ctinfo values to original or reply direction and manipulates protocol-specific tuple fields when applying NAT or matching flows.

## State, Persistence, And Dependencies
Tuple state persists in conntrack entries and NAT ranges. Depends on `linux/types.h`, `linux/netfilter.h` for userspace, and `nf_conntrack_common.h`.

## Integration Points
Used by NAT UAPI, ctnetlink, protocol helpers, and nftables/iptables tuple-related code.

## Risks
All fields are network order. GRE key is represented as 16 bits for PPTP compatibility though GRE keys can be 32-bit.

## Test Signals
Validate direction macro around `IP_CT_IS_REPLY`, NAT port/key manipulation, network-order encoding, and compatibility with `nf_nat.h` range structs.
