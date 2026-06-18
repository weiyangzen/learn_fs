# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_queue.h

## Purpose

`nfnetlink_queue.h` defines the nfnetlink ABI for queue, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 130 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/nfnetlink.h`. Exported structures include `nfqnl_msg_packet_hdr`, `nfqnl_msg_packet_hw`, `nfqnl_msg_packet_timestamp`, `nfqnl_msg_verdict_hdr`, `nfqnl_msg_config_cmd`, `nfqnl_msg_config_params`. Enumerations include `nfqnl_msg_types`, `nfqnl_vlan_attr`, `nfqnl_attr_type`, `nfqnl_msg_config_cmds`, `nfqnl_config_mode`, `nfqnl_attr_config`. Prominent attribute, command, flag, or constant names include `NFQNL_MSG_PACKET`, `NFQNL_MSG_VERDICT`, `NFQNL_MSG_CONFIG`, `NFQNL_MSG_VERDICT_BATCH`, `NFQA_VLAN_UNSPEC`, `NFQA_VLAN_PROTO`, `NFQA_VLAN_TCI`, `NFQA_UNSPEC`, `NFQA_PACKET_HDR`, `NFQA_VERDICT_HDR`, `NFQA_MARK`, `NFQA_TIMESTAMP`, `NFQA_IFINDEX_INDEV`, `NFQA_IFINDEX_OUTDEV`, `NFQA_IFINDEX_PHYSINDEV`, `NFQA_IFINDEX_PHYSOUTDEV`, `NFQA_HWADDR`, `NFQA_PAYLOAD`, `NFQA_CT`, `NFQA_CT_INFO`, `NFQA_CAP_LEN`, `NFQA_SKB_INFO`, and 22 more. Macros expose `_NFNETLINK_QUEUE_H`, `NFQA_VLAN_MAX`, `NFQA_MAX`, `NFQA_CFG_MAX`, `NFQA_CFG_F_FAIL_OPEN`, `NFQA_CFG_F_CONNTRACK`, `NFQA_CFG_F_GSO`, `NFQA_CFG_F_UID_GID`, `NFQA_CFG_F_SECCTX`, `NFQA_CFG_F_MAX`, `NFQA_SKB_CSUMNOTREADY`, `NFQA_SKB_GSO`, `NFQA_SKB_CSUM_NOTVERIFIED`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Packets selected by NFQUEUE are serialized into `NFQNL_MSG_PACKET` messages with packet metadata attributes; user space returns `NFQNL_MSG_VERDICT` messages that carry verdict IDs, marks, queue-bypass decisions, and optional packet modifications. Queue configuration flows through config command and mode attributes.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/nfnetlink.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Flags for NFQA_CFG_FLAGS; flags for NFQA_SKB_INFO; packet appears to have wrong checksums, but they are ok.
