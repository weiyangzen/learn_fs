<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h

## Purpose
`nf_conntrack_tuple.h` defines the canonical conntrack tuple and tuple hash structures used to identify flows and expectations.

## Important APIs, types, and functions
It defines `NF_CT_TUPLE_L3SIZE`, `struct nf_conntrack_man`, `struct nf_conntrack_tuple`, `struct nf_conntrack_tuple_mask`, `struct nf_conntrack_tuple_hash`, tuple debug dump helpers, `NF_CT_DIRECTION`, and tuple equality/mask comparison helpers.

## Control flow
Tuple extraction fills manipulable source fields and fixed destination/protocol/direction fields. Conntracks store original and reply tuple hashes. NAT can manipulate source-side fields while fixed destination fields identify the reverse mapping. Expectations use masks for wildcard matching.

## State and persistence
No independent state is stored; tuples are embedded in conntracks, expectations, hashes, and stack lookup keys.

## Dependencies and integration points
It depends on netfilter address/protocol tuple UAPI, list nulls hash nodes, and inet address comparison helpers. It integrates conntrack hash lookup, NAT, ctnetlink, and expectations.

## Risks and test signals
Risks include direction included/excluded incorrectly for hashing, mask comparison gaps, IPv4/IPv6 address array length assumptions, endian mistakes in ports/keys, and debug-only dumps hiding issues. Tests should cover tuple equality/mask matching for IPv4/IPv6/TCP/UDP/ICMP/GRE/SCTP and original/reply directions.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h` completely for this pass (190 lines, 4705 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_tuple.h -->
