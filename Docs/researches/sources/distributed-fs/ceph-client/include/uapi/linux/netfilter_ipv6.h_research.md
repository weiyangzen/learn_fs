# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6.h

## Purpose

`netfilter_ipv6.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for ipv6 packet processing. The file is 51 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`, `linux/typelimits.h`. Enumerations include `nf_ip6_hook_priorities`. Prominent attribute, command, flag, or constant names include `NF_IP6_PRI_FIRST`, `NF_IP6_PRI_RAW_BEFORE_DEFRAG`, `NF_IP6_PRI_CONNTRACK_DEFRAG`, `NF_IP6_PRI_RAW`, `NF_IP6_PRI_SELINUX_FIRST`, `NF_IP6_PRI_CONNTRACK`, `NF_IP6_PRI_MANGLE`, `NF_IP6_PRI_NAT_DST`, `NF_IP6_PRI_FILTER`, `NF_IP6_PRI_SECURITY`, `NF_IP6_PRI_NAT_SRC`, `NF_IP6_PRI_SELINUX_LAST`, `NF_IP6_PRI_CONNTRACK_HELPER`, `NF_IP6_PRI_LAST`. Macros expose `_UAPI__LINUX_IP6_NETFILTER_H`, `NF_IP6_PRE_ROUTING`, `NF_IP6_LOCAL_IN`, `NF_IP6_FORWARD`, `NF_IP6_LOCAL_OUT`, `NF_IP6_POST_ROUTING`, `NF_IP6_NUMHOOKS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`, `linux/typelimits.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: IPv6-specific defines for netfilter.; (C)1998 Rusty Russell -- This code is GPL.; (C)1999 David Jeffery.
