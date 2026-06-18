# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip6.h

## Purpose

`ebt_ip6.h` defines the ebtables bridge match or target parameter ABI for `ebt_ip6`, used by bridge netfilter rules operating on Ethernet frames. The file is 52 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/in6.h`. Exported structures include `ebt_ip6_info`, `in6_addr`. Macros expose `__LINUX_BRIDGE_EBT_IP6_H`, `EBT_IP6_SOURCE`, `EBT_IP6_DEST`, `EBT_IP6_TCLASS`, `EBT_IP6_PROTO`, `EBT_IP6_SPORT`, `EBT_IP6_DPORT`, `EBT_IP6_ICMP6`, `EBT_IP6_MASK`, `EBT_IP6_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/in6.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Kuo-Lang Tseng <kuo-lang.tseng@intel.com>; Manohar Castelino <manohar.r.castelino@intel.com>; Jan 11, 2008.
