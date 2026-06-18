<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c

## Purpose
`xt_nat.c` implements legacy x_tables `SNAT` and `DNAT` targets backed by nf_nat. It translates userspace NAT range structures into `nf_nat_range2` and invokes core NAT setup.

## Important APIs, Types, and Functions
`xt_nat_checkentry_v0()` and `xt_nat_checkentry()` acquire NAT hook support. `xt_nat_destroy()` releases it. `xt_nat_convert_range()` converts `struct nf_nat_ipv4_range` to `struct nf_nat_range2`. Target functions include IPv4 and IPv6 SNAT/DNAT variants for revision 0 and current revision, all registered in `xt_nat_target_reg[]`.

## Control Flow, State, and Persistence
Rule insertion enables NAT for the family and hook. On the first packet of a conntrack flow, target functions pass the configured range and manipulation direction to `nf_nat_setup_info()`. NAT state then persists in conntrack for subsequent packets; this file does not maintain separate tables.

## Dependencies and Integration Points
The module integrates with nf_nat, conntrack, x_tables targets, IPv4 and IPv6 NAT range UAPIs, and hook restrictions for source versus destination NAT. It is compatibility glue for iptables NAT semantics.

## Risks and Test Signals
Risks include hook misuse, revision 0 range conversion, IPv4/IPv6 range differences, missing conntrack/NAT support, and applying NAT after connection state is already committed. Tests should cover SNAT and DNAT in valid hooks, invalid hooks rejected, IPv4 revision 0 conversion, IPv6 ranges, persistent translation across flow packets, namespace cleanup, and failure paths in NAT support acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nat.c -->
