# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_set.h

## Purpose

`xt_set.h` defines the x_tables match or target option structure for `xt_set`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 94 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/ipset/ip_set.h`. Exported structures include `xt_set_info_v0`, `xt_set_info_match_v0`, `xt_set_info_target_v0`, `xt_set_info`, `xt_set_info_match_v1`, `xt_set_info_target_v1`, `xt_set_info_target_v2`, `xt_set_info_match_v3`, `ip_set_counter_match0`, `xt_set_info_target_v3`, `xt_set_info_match_v4`, `ip_set_counter_match`. Macros expose `_XT_SET_H`, `IPSET_SRC`, `IPSET_DST`, `IPSET_MATCH_INV`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/ipset/ip_set.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Revision 0 interface: backward compatible with netfilter/iptables; Option flags for kernel operations (xt_set_info_v0); match and target infos.
