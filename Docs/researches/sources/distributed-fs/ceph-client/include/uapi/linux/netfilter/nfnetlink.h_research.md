# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink.h

## Purpose

`nfnetlink.h` defines the nfnetlink message header, subsystem identifiers, multicast groups, and batch attributes shared by netfilter netlink families. The file is 82 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/nfnetlink_compat.h`. Exported structures include `nfgenmsg`. Enumerations include `nfnetlink_groups`, `nfnl_batch_attributes`. Prominent attribute, command, flag, or constant names include `NFNLGRP_NONE`, `NFNLGRP_CONNTRACK_NEW`, `NFNLGRP_CONNTRACK_UPDATE`, `NFNLGRP_CONNTRACK_DESTROY`, `NFNLGRP_CONNTRACK_EXP_NEW`, `NFNLGRP_CONNTRACK_EXP_UPDATE`, `NFNLGRP_CONNTRACK_EXP_DESTROY`, `NFNLGRP_NFTABLES`, `NFNLGRP_ACCT_QUOTA`, `NFNLGRP_NFTRACE`, `NFNL_BATCH_UNSPEC`, `NFNL_BATCH_GENID`. Macros expose `_UAPI_NFNETLINK_H`, `NFNLGRP_NONE`, `NFNLGRP_CONNTRACK_NEW`, `NFNLGRP_CONNTRACK_UPDATE`, `NFNLGRP_CONNTRACK_DESTROY`, `NFNLGRP_CONNTRACK_EXP_NEW`, `NFNLGRP_CONNTRACK_EXP_UPDATE`, `NFNLGRP_CONNTRACK_EXP_DESTROY`, `NFNLGRP_NFTABLES`, `NFNLGRP_ACCT_QUOTA`, `NFNLGRP_NFTRACE`, `NFNLGRP_MAX`, `NFNETLINK_V0`, `NFNL_SUBSYS_ID`, `NFNL_MSG_TYPE`, `NFNL_SUBSYS_NONE`, `NFNL_SUBSYS_CTNETLINK`, `NFNL_SUBSYS_CTNETLINK_EXP`, and 14 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/nfnetlink_compat.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: General form of address family dependent message.; netfilter netlink message types are split in two pieces:; 8 bit subsystem, 8bit operation..
