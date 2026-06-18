<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h

## Purpose
`nf_conntrack_l4proto.h` defines the L4 protocol plugin ABI for conntrack and declares built-in TCP/UDP/ICMP/SCTP/GRE packet handlers, tuple conversion helpers, timeout netlink conversion, and per-net protocol state accessors.

## Important APIs, types, and functions
It defines `struct nf_conntrack_l4proto` with packet/drop, netlink tuple/protoinfo, timeout object, and procfs callbacks. It declares tuple extraction/inversion for ICMP/ICMPv6, error handlers, per-protocol packet handlers, per-net init functions, generic protocol object, `nf_ct_l4proto_find`, port tuple netlink helpers, invalid logging helpers, pernet accessors, TCP liberal/established helpers, and optional SCTP/GRE accessors.

## Control flow
Conntrack core finds an L4 proto by IP protocol, parses tuples, handles protocol-specific packet state, serializes/deserializes netlink attributes, and uses timeout object callbacks. Error packets are matched to inner tuples. TCP helpers can set liberal mode or check established/assured state.

## State and persistence
State lives in per-net protocol structs under `net->ct.nf_ct_proto`, per-conntrack protocol-private union, and protocol object callback tables. The header stores no globals beyond extern declarations.

## Dependencies and integration points
It depends on netlink/nla policy, conntrack, netns generic state, sysctl optional invalid logging, and protocol-specific UAPI state. It integrates L4 protocols with conntrack core and ctnetlink.

## Risks and test signals
Risks include tuple parsing at wrong data offsets, ICMP error inversion, netlink policy/size mismatch, timeout object conversion bugs, optional protocol CONFIGs, and callers using TCP helpers on non-TCP conntracks. Tests should cover TCP/UDP/ICMP/ICMPv6/SCTP/GRE flows, error packets, ctnetlink dump/restore, invalid logging, and timeout policies.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h` completely for this pass (227 lines, 7071 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_l4proto.h -->
