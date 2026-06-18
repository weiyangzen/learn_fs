# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebtables.h

## Purpose

`ebtables.h` defines the Ethernet bridge x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 287 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if.h`, `linux/netfilter_bridge.h`. Exported structures include `xt_match`, `xt_target`, `ebt_counter`, `ebt_replace`, `ebt_entries`, `ebt_replace_kernel`, `ebt_entry_match`, `ebt_entry_watcher`, `ebt_entry_target`, `ebt_standard_target`, `ebt_entry`. Macros expose `_UAPI__LINUX_BRIDGE_EFF_H`, `EBT_TABLE_MAXNAMELEN`, `EBT_CHAIN_MAXNAMELEN`, `EBT_FUNCTION_MAXNAMELEN`, `EBT_EXTENSION_MAXNAMELEN`, `EBT_ACCEPT`, `EBT_DROP`, `EBT_CONTINUE`, `EBT_RETURN`, `NUM_STANDARD_TARGETS`, `EBT_VERDICT_BITS`, `EBT_ENTRY_OR_ENTRIES`, `EBT_NOPROTO`, `EBT_802_3`, `EBT_SOURCEMAC`, `EBT_DESTMAC`, `EBT_F_MASK`, `EBT_IPROTO`, and 20 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if.h`, `linux/netfilter_bridge.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Bart De Schuymer		<bdschuym@pandora.be>; ebtables.c,v 2.0, April, 2002; This code is strongly inspired by the iptables code which is.
