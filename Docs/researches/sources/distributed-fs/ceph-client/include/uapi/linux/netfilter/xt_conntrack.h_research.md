# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_conntrack.h

## Purpose

`xt_conntrack.h` defines the x_tables match or target option structure for `xt_conntrack`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 79 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`, `linux/netfilter/nf_conntrack_tuple_common.h`. Exported structures include `xt_conntrack_mtinfo1`, `xt_conntrack_mtinfo2`, `xt_conntrack_mtinfo3`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_CONNTRACK_STATE`, `XT_CONNTRACK_PROTO`, `XT_CONNTRACK_ORIGSRC`, `XT_CONNTRACK_ORIGDST`, `XT_CONNTRACK_REPLSRC`, `XT_CONNTRACK_REPLDST`, `XT_CONNTRACK_STATUS`, `XT_CONNTRACK_EXPIRES`, `XT_CONNTRACK_ORIGSRC_PORT`, `XT_CONNTRACK_ORIGDST_PORT`, `XT_CONNTRACK_REPLSRC_PORT`, `XT_CONNTRACK_REPLDST_PORT`, `XT_CONNTRACK_DIRECTION`, `XT_CONNTRACK_STATE_ALIAS`. Macros expose `_XT_CONNTRACK_H`, `XT_CONNTRACK_STATE_BIT`, `XT_CONNTRACK_STATE_INVALID`, `XT_CONNTRACK_STATE_SNAT`, `XT_CONNTRACK_STATE_DNAT`, `XT_CONNTRACK_STATE_UNTRACKED`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`, `linux/netfilter/nf_conntrack_tuple_common.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for kernel module to match connection tracking information.; GPL (C) 2001  Marc Boucher (marc@mbsi.ca).; flags, invflags:.
