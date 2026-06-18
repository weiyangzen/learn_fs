# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/x_tables.h

## Purpose

`x_tables.h` defines the common x_tables ABI used by iptables, ip6tables, arptables, and ebtables extensions: match/target containers, counters, alignment, verdict values, and replacement metadata. The file is 188 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/const.h`, `linux/types.h`. Exported structures include `xt_entry_match`, `xt_match`, `xt_entry_target`, `xt_target`, `xt_standard_target`, `xt_error_target`, `xt_get_revision`, `_xt_align`, `xt_counters`, `xt_counters_info`. Macros expose `_UAPI_X_TABLES_H`, `XT_FUNCTION_MAXNAMELEN`, `XT_EXTENSION_MAXNAMELEN`, `XT_TABLE_MAXNAMELEN`, `XT_TARGET_INIT`, `XT_CONTINUE`, `XT_RETURN`, `XT_ALIGN`, `XT_STANDARD_TARGET`, `XT_ERROR_TARGET`, `SET_COUNTER`, `ADD_COUNTER`, `XT_INV_PROTO`, `XT_MATCH_ITERATE`, `XT_ENTRY_ITERATE_CONTINUE`, `XT_ENTRY_ITERATE`, `xt_entry_foreach`, `xt_ematch_foreach`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/const.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used by userspace; Used inside the kernel; Total length.
