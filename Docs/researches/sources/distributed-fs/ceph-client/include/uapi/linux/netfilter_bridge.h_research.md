# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge.h

## Purpose

`netfilter_bridge.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for bridge packet processing. The file is 45 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `netinet/if_ether.h`, `linux/in.h`, `linux/netfilter.h`, `linux/if_ether.h`, `linux/if_vlan.h`, `linux/if_pppox.h`, `linux/typelimits.h`. Enumerations include `nf_br_hook_priorities`. Prominent attribute, command, flag, or constant names include `NF_BR_PRI_FIRST`, `NF_BR_PRI_NAT_DST_BRIDGED`, `NF_BR_PRI_FILTER_BRIDGED`, `NF_BR_PRI_BRNF`, `NF_BR_PRI_NAT_DST_OTHER`, `NF_BR_PRI_FILTER_OTHER`, `NF_BR_PRI_NAT_SRC`, `NF_BR_PRI_LAST`. Macros expose `_UAPI__LINUX_BRIDGE_NETFILTER_H`, `NF_BR_PRE_ROUTING`, `NF_BR_LOCAL_IN`, `NF_BR_FORWARD`, `NF_BR_LOCAL_OUT`, `NF_BR_POST_ROUTING`, `NF_BR_BROUTING`, `NF_BR_NUMHOOKS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `netinet/if_ether.h`, `linux/in.h`, `linux/netfilter.h`, `linux/if_ether.h`, `linux/if_vlan.h`, `linux/if_pppox.h`, `linux/typelimits.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: bridge-specific defines for netfilter.; Bridge Hooks; After promisc drops, checksum checks..
