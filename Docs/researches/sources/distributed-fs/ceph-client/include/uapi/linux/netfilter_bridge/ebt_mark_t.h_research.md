# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_t.h

## Purpose

`ebt_mark_t.h` defines the ebtables bridge match or target parameter ABI for `ebt_mark_t`, used by bridge netfilter rules operating on Ethernet frames. The file is 24 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ebt_mark_t_info`. Macros expose `__LINUX_BRIDGE_EBT_MARK_T_H`, `MARK_SET_VALUE`, `MARK_OR_VALUE`, `MARK_AND_VALUE`, `MARK_XOR_VALUE`, `EBT_MARK_TARGET`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

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

Source comments call out: The target member is reused for adding new actions, the; value of the real target is -1 to -NUM_STANDARD_TARGETS.; For backward compatibility, the 4 lsb (2 would be enough,.
