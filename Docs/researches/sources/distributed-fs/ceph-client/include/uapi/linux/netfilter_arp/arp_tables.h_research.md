# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arp_tables.h

## Purpose

`arp_tables.h` defines the ARP x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 208 lines and is part of the ARP netfilter/arptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_arp.h`, `linux/netfilter/x_tables.h`. Exported structures include `arpt_devaddr_info`, `arpt_arp`, `in_addr`, `arpt_entry`, `xt_counters`, `arpt_getinfo`, `arpt_replace`, `arpt_get_entries`. Macros expose `_UAPI_ARPTABLES_H`, `ARPT_FUNCTION_MAXNAMELEN`, `ARPT_TABLE_MAXNAMELEN`, `arpt_entry_target`, `arpt_standard_target`, `arpt_error_target`, `ARPT_CONTINUE`, `ARPT_RETURN`, `arpt_counters_info`, `arpt_counters`, `ARPT_STANDARD_TARGET`, `ARPT_ERROR_TARGET`, `ARPT_ENTRY_ITERATE`, `ARPT_DEV_ADDR_LEN_MAX`, `ARPT_F_MASK`, `ARPT_INV_VIA_IN`, `ARPT_INV_VIA_OUT`, `ARPT_INV_SRCIP`, and 16 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_arp.h`, `linux/netfilter/x_tables.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Format of an ARP firewall descriptor; src, tgt, src_mask, tgt_mask, arpop, arpop_mask are always stored in; network byte order..
