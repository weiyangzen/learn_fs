# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_REJECT.h

## Purpose

`ipt_REJECT.h` defines the IPv4 iptables extension ABI for `ipt_REJECT`, used to match or target IPv4 packet fields through x_tables. The file is 21 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ipt_reject_info`. Enumerations include `ipt_reject_with`. Prominent attribute, command, flag, or constant names include `IPT_ICMP_NET_UNREACHABLE`, `IPT_ICMP_HOST_UNREACHABLE`, `IPT_ICMP_PROT_UNREACHABLE`, `IPT_ICMP_PORT_UNREACHABLE`, `IPT_ICMP_ECHOREPLY`, `IPT_ICMP_NET_PROHIBITED`, `IPT_ICMP_HOST_PROHIBITED`, `IPT_TCP_RESET`. Macros expose `_IPT_REJECT_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
