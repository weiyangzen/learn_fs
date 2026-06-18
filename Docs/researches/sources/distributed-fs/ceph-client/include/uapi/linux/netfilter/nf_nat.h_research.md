# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_nat.h

## Purpose
Defines netfilter NAT range flags and IPv4/generic NAT range structs used by userspace rule APIs and conntrack/NAT integrations.

## Important APIs, Types, And Functions
Exports `NF_NAT_RANGE_*`, `NF_NAT_RANGE_PROTO_RANDOM_ALL`, `NF_NAT_RANGE_MASK`, `nf_nat_ipv4_range`, `nf_nat_ipv4_multi_range_compat`, `nf_nat_range`, and `nf_nat_range2`.

## Control Flow
Firewall/NAT userspace supplies address and protocol min/max ranges plus flags controlling IP mapping, protocol specificity, randomization, persistence, offsets, and netmap behavior. Kernel NAT code applies these ranges to conntrack tuples.

## State, Persistence, And Dependencies
NAT state persists in rules and conntrack NAT mappings. Depends on `linux/netfilter.h` and `nf_conntrack_tuple_common.h`.

## Integration Points
Used by iptables/nftables NAT expressions, ctnetlink, and NAT helpers.

## Risks
IPv4 compatibility range differs from generic `nf_inet_addr` ranges. `nf_nat_range2` adds `base_proto`; older userspace may only understand earlier structs.

## Test Signals
Validate each flag, IPv4 and IPv6 range rule insertion, random/full-random behavior, persistent mappings, proto offsets, netmap, compatibility multi-range handling, and mask rejection of unknown bits.
