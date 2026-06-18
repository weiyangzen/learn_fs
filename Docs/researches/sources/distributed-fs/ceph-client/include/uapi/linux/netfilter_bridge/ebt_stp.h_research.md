# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_stp.h

## Purpose

`ebt_stp.h` defines the ebtables bridge match or target parameter ABI for `ebt_stp`, used by bridge netfilter rules operating on Ethernet frames. The file is 47 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_stp_config_info`, `ebt_stp_info`. Macros expose `__LINUX_BRIDGE_EBT_STP_H`, `EBT_STP_TYPE`, `EBT_STP_FLAGS`, `EBT_STP_ROOTPRIO`, `EBT_STP_ROOTADDR`, `EBT_STP_ROOTCOST`, `EBT_STP_SENDERPRIO`, `EBT_STP_SENDERADDR`, `EBT_STP_PORT`, `EBT_STP_MSGAGE`, `EBT_STP_MAXAGE`, `EBT_STP_HELLOTIME`, `EBT_STP_FWDD`, `EBT_STP_MASK`, `EBT_STP_CONFIG_MASK`, `EBT_STP_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
