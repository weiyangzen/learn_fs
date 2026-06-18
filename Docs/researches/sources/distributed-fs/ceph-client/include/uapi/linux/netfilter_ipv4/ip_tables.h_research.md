# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ip_tables.h

## Purpose

`ip_tables.h` defines the IPv4 x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 231 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv4.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`. Exported structures include `ipt_ip`, `in_addr`, `ipt_entry`, `xt_counters`, `ipt_icmp`, `ipt_getinfo`, `ipt_replace`, `ipt_get_entries`. Macros expose `_UAPI_IPTABLES_H`, `IPT_FUNCTION_MAXNAMELEN`, `IPT_TABLE_MAXNAMELEN`, `ipt_match`, `ipt_target`, `ipt_table`, `ipt_get_revision`, `ipt_entry_match`, `ipt_entry_target`, `ipt_standard_target`, `ipt_error_target`, `ipt_counters`, `IPT_CONTINUE`, `IPT_RETURN`, `ipt_udp`, `ipt_tcp`, `IPT_TCP_INV_SRCPT`, `IPT_TCP_INV_DSTPT`, and 32 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv4.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: 25-Jul-1998 Major changes to allow for ip chain table; 3-Jan-2000 Named tables to allow packet selection for different uses.; Format of an IP firewall descriptor.
