# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_LOG.h

## Purpose

`ip6t_LOG.h` defines the IPv6 ip6tables extension ABI for `ip6t_LOG`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 20 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ip6t_log_info`. Macros expose `_IP6T_LOG_H`, `IP6T_LOG_TCPSEQ`, `IP6T_LOG_TCPOPT`, `IP6T_LOG_IPOPT`, `IP6T_LOG_UID`, `IP6T_LOG_NFLOG`, `IP6T_LOG_MACDECODE`, `IP6T_LOG_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: make sure not to change this without changing netfilter.h:NF_LOG_* (!).
