# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_conntrack.h

## Purpose

`nfnetlink_conntrack.h` defines the nfnetlink ABI for conntrack, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 292 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/nfnetlink.h`. Enumerations include `cntl_msg_types`, `ctnl_exp_msg_types`, `ctattr_type`, `ctattr_tuple`, `ctattr_ip`, `ctattr_l4proto`, `ctattr_protoinfo`, `ctattr_protoinfo_tcp`, `ctattr_protoinfo_dccp`, `ctattr_protoinfo_sctp`, `ctattr_counters`, `ctattr_tstamp`, `ctattr_nat`, `ctattr_protonat`, `ctattr_seqadj`, `ctattr_natseq`, `ctattr_synproxy`, `ctattr_expect`, and 7 more. Prominent attribute, command, flag, or constant names include `IPCTNL_MSG_CT_NEW`, `IPCTNL_MSG_CT_GET`, `IPCTNL_MSG_CT_DELETE`, `IPCTNL_MSG_CT_GET_CTRZERO`, `IPCTNL_MSG_CT_GET_STATS_CPU`, `IPCTNL_MSG_CT_GET_STATS`, `IPCTNL_MSG_CT_GET_DYING`, `IPCTNL_MSG_CT_GET_UNCONFIRMED`, `IPCTNL_MSG_EXP_NEW`, `IPCTNL_MSG_EXP_GET`, `IPCTNL_MSG_EXP_DELETE`, `IPCTNL_MSG_EXP_GET_STATS_CPU`, `CTA_UNSPEC`, `CTA_TUPLE_ORIG`, `CTA_TUPLE_REPLY`, `CTA_STATUS`, `CTA_PROTOINFO`, `CTA_HELP`, `CTA_NAT_SRC`, `CTA_TIMEOUT`, `CTA_MARK`, `CTA_COUNTERS_ORIG`, and 135 more. Macros expose `_IPCONNTRACK_NETLINK_H`, `CTA_NAT`, `CTA_MAX`, `CTA_TUPLE_MAX`, `CTA_IP_MAX`, `CTA_PROTO_MAX`, `CTA_PROTOINFO_MAX`, `CTA_PROTOINFO_TCP_MAX`, `CTA_PROTOINFO_DCCP_MAX`, `CTA_PROTOINFO_SCTP_MAX`, `CTA_COUNTERS_MAX`, `CTA_TIMESTAMP_MAX`, `CTA_NAT_MINIP`, `CTA_NAT_MAXIP`, `CTA_NAT_MAX`, `CTA_PROTONAT_MAX`, `CTA_SEQADJ_MAX`, `CTA_NAT_SEQ_MAX`, and 9 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Conntrack tooling sends get/new/delete operations and receives create/update/destroy/expectation events. Tuple, protocol, NAT, counter, mark, label, helper, timeout, and timestamp attributes are nested to describe each tracked flow or expectation.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/nfnetlink.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.
