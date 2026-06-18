# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp.h

## Purpose

`netfilter_arp.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for arp packet processing. The file is 23 lines and is part of the ARP netfilter/arptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`. Macros expose `__LINUX_ARP_NETFILTER_H`, `NF_ARP`, `NF_ARP_IN`, `NF_ARP_OUT`, `NF_ARP_FORWARD`, `NF_ARP_NUMHOOKS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: ARP-specific defines for netfilter.; (C)2002 Rusty Russell IBM -- This code is GPL.; There is no PF_ARP..
