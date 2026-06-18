# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arpt_mangle.h

## Purpose

`arpt_mangle.h` defines Linux UAPI declarations for `arpt_mangle` in the ARP netfilter/arptables area. The file is 27 lines and is part of the ARP netfilter/arptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter_arp/arp_tables.h`. Exported structures include `arpt_mangle`, `in_addr`. Macros expose `_ARPT_MANGLE_H`, `ARPT_MANGLE_ADDR_LEN_MAX`, `ARPT_MANGLE_SDEV`, `ARPT_MANGLE_TDEV`, `ARPT_MANGLE_SIP`, `ARPT_MANGLE_TIP`, `ARPT_MANGLE_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter_arp/arp_tables.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
