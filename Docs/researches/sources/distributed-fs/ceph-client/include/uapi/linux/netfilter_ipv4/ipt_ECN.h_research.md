# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ECN.h

## Purpose

`ipt_ECN.h` defines the IPv4 iptables extension ABI for `ipt_ECN`, used to match or target IPv4 packet fields through x_tables. The file is 34 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/xt_DSCP.h`. Exported structures include `ipt_ECN_info`. Macros expose `_IPT_ECN_TARGET_H`, `IPT_ECN_IP_MASK`, `IPT_ECN_OP_SET_IP`, `IPT_ECN_OP_SET_ECE`, `IPT_ECN_OP_SET_CWR`, `IPT_ECN_OP_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/xt_DSCP.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for iptables ipt_ECN target; (C) 2002 by Harald Welte <laforge@gnumonks.org>; This software is distributed under GNU GPL v2, 1991.
