# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_compat.h

## Purpose

`nfnetlink_compat.h` defines the nfnetlink ABI for compat, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 64 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `nfattr`. Macros expose `_NFNETLINK_COMPAT_H`, `NF_NETLINK_CONNTRACK_NEW`, `NF_NETLINK_CONNTRACK_UPDATE`, `NF_NETLINK_CONNTRACK_DESTROY`, `NF_NETLINK_CONNTRACK_EXP_NEW`, `NF_NETLINK_CONNTRACK_EXP_UPDATE`, `NF_NETLINK_CONNTRACK_EXP_DESTROY`, `NFNL_NFA_NEST`, `NFA_TYPE`, `NFA_ALIGNTO`, `NFA_ALIGN`, `NFA_OK`, `NFA_NEXT`, `NFA_LENGTH`, `NFA_SPACE`, `NFA_DATA`, `NFA_PAYLOAD`, `NFA_NEST`, and 4 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Old nfnetlink macros for userspace; nfnetlink groups: Up to 32 maximum; Generic structure for encapsulation optional netfilter information..
