# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_srh.h

## Purpose

`ip6t_srh.h` defines the IPv6 ip6tables extension ABI for `ip6t_srh`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 96 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `ip6t_srh`, `ip6t_srh1`, `in6_addr`. Macros expose `_IP6T_SRH_H`, `IP6T_SRH_NEXTHDR`, `IP6T_SRH_LEN_EQ`, `IP6T_SRH_LEN_GT`, `IP6T_SRH_LEN_LT`, `IP6T_SRH_SEGS_EQ`, `IP6T_SRH_SEGS_GT`, `IP6T_SRH_SEGS_LT`, `IP6T_SRH_LAST_EQ`, `IP6T_SRH_LAST_GT`, `IP6T_SRH_LAST_LT`, `IP6T_SRH_TAG`, `IP6T_SRH_PSID`, `IP6T_SRH_NSID`, `IP6T_SRH_LSID`, `IP6T_SRH_MASK`, `IP6T_SRH_INV_NEXTHDR`, `IP6T_SRH_INV_LEN_EQ`, and 13 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "mt_flags" field in struct ip6t_srh; Values for "mt_invflags" field in struct ip6t_srh; struct ip6t_srh - SRH match options.
