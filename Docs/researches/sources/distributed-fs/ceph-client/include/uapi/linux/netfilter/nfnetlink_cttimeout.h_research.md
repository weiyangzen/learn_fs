# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cttimeout.h

## Purpose

`nfnetlink_cttimeout.h` defines the nfnetlink ABI for cttimeout, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 119 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/nfnetlink.h`. Enumerations include `ctnl_timeout_msg_types`, `ctattr_timeout`, `ctattr_timeout_generic`, `ctattr_timeout_tcp`, `ctattr_timeout_udp`, `ctattr_timeout_udplite`, `ctattr_timeout_icmp`, `ctattr_timeout_dccp`, `ctattr_timeout_sctp`, `ctattr_timeout_icmpv6`, `ctattr_timeout_gre`. Prominent attribute, command, flag, or constant names include `IPCTNL_MSG_TIMEOUT_NEW`, `IPCTNL_MSG_TIMEOUT_GET`, `IPCTNL_MSG_TIMEOUT_DELETE`, `IPCTNL_MSG_TIMEOUT_DEFAULT_SET`, `IPCTNL_MSG_TIMEOUT_DEFAULT_GET`, `CTA_TIMEOUT_UNSPEC`, `CTA_TIMEOUT_NAME`, `CTA_TIMEOUT_L3PROTO`, `CTA_TIMEOUT_L4PROTO`, `CTA_TIMEOUT_DATA`, `CTA_TIMEOUT_USE`, `CTA_TIMEOUT_GENERIC_UNSPEC`, `CTA_TIMEOUT_GENERIC_TIMEOUT`, `CTA_TIMEOUT_TCP_UNSPEC`, `CTA_TIMEOUT_TCP_SYN_SENT`, `CTA_TIMEOUT_TCP_SYN_RECV`, `CTA_TIMEOUT_TCP_ESTABLISHED`, `CTA_TIMEOUT_TCP_FIN_WAIT`, `CTA_TIMEOUT_TCP_CLOSE_WAIT`, `CTA_TIMEOUT_TCP_LAST_ACK`, `CTA_TIMEOUT_TCP_TIME_WAIT`, `CTA_TIMEOUT_TCP_CLOSE`, and 34 more. Macros expose `_CTTIMEOUT_NETLINK_H`, `CTA_TIMEOUT_MAX`, `CTA_TIMEOUT_GENERIC_MAX`, `CTA_TIMEOUT_TCP_MAX`, `CTA_TIMEOUT_UDP_MAX`, `CTA_TIMEOUT_UDPLITE_MAX`, `CTA_TIMEOUT_ICMP_MAX`, `CTA_TIMEOUT_DCCP_MAX`, `CTA_TIMEOUT_SCTP_MAX`, `CTA_TIMEOUT_ICMPV6_MAX`, `CTA_TIMEOUT_GRE_MAX`, `CTNL_TIMEOUT_NAME_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/nfnetlink.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.
