# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_log.h

## Purpose

`nfnetlink_log.h` defines the nfnetlink ABI for log, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 112 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/nfnetlink.h`. Exported structures include `nfulnl_msg_packet_hdr`, `nfulnl_msg_packet_hw`, `nfulnl_msg_packet_timestamp`, `nfulnl_msg_config_cmd`, `nfulnl_msg_config_mode`. Enumerations include `nfulnl_msg_types`, `nfulnl_vlan_attr`, `nfulnl_attr_type`, `nfulnl_msg_config_cmds`, `nfulnl_attr_config`. Prominent attribute, command, flag, or constant names include `NFULNL_MSG_PACKET`, `NFULNL_MSG_CONFIG`, `NFULA_VLAN_UNSPEC`, `NFULA_VLAN_PROTO`, `NFULA_VLAN_TCI`, `NFULA_UNSPEC`, `NFULA_PACKET_HDR`, `NFULA_MARK`, `NFULA_TIMESTAMP`, `NFULA_IFINDEX_INDEV`, `NFULA_IFINDEX_OUTDEV`, `NFULA_IFINDEX_PHYSINDEV`, `NFULA_IFINDEX_PHYSOUTDEV`, `NFULA_HWADDR`, `NFULA_PAYLOAD`, `NFULA_PREFIX`, `NFULA_UID`, `NFULA_SEQ`, `NFULA_SEQ_GLOBAL`, `NFULA_GID`, `NFULA_HWTYPE`, `NFULA_HWHEADER`, and 17 more. Macros expose `_NFNETLINK_LOG_H`, `NFULA_VLAN_MAX`, `NFULA_MAX`, `NFULA_CFG_MAX`, `NFULNL_COPY_NONE`, `NFULNL_COPY_META`, `NFULNL_COPY_PACKET`, `NFULNL_CFG_F_SEQ`, `NFULNL_CFG_F_SEQ_GLOBAL`, `NFULNL_CFG_F_CONNTRACK`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Packets selected for NFLOG are delivered as log messages containing packet headers, prefix, timestamp, UID/GID, interface, VLAN, hardware address, and payload attributes. User space configures copy mode, queue thresholds, timeout, and flags with configuration messages.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/nfnetlink.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: This file describes the netlink messages (i.e. 'protocol packets'),; and not any kind of function definitions.  It is shared between kernel and; userspace.  Don't put kernel specific stuff in here.
