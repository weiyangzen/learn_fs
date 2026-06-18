# subset-b-005986 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables.h

## Purpose

`nf_tables.h` defines the main nftables userspace ABI: table, chain, rule, set, object, flowtable, expression, verdict, register, and nested netlink attribute identifiers used by `nft` and the kernel nf_tables subsystem. The file is 2022 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Enumerations include `nft_registers`, `nft_verdicts`, `nf_tables_msg_types`, `nft_list_attributes`, `nft_hook_attributes`, `nft_table_flags`, `nft_table_attributes`, `nft_chain_flags`, `nft_chain_attributes`, `nft_rule_attributes`, `nft_rule_compat_flags`, `nft_rule_compat_attributes`, `nft_set_flags`, `nft_set_policies`, `nft_set_desc_attributes`, `nft_set_field_attributes`, `nft_set_attributes`, `nft_set_elem_flags`, and 97 more. Prominent attribute, command, flag, or constant names include `NFT_REG_VERDICT`, `NFT_REG_1`, `NFT_REG_2`, `NFT_REG_3`, `NFT_REG_4`, `NFT_REG32_00`, `NFT_REG32_01`, `NFT_REG32_02`, `NFT_REG32_03`, `NFT_REG32_04`, `NFT_REG32_05`, `NFT_REG32_06`, `NFT_REG32_07`, `NFT_REG32_08`, `NFT_REG32_09`, `NFT_REG32_10`, `NFT_REG32_11`, `NFT_REG32_12`, `NFT_REG32_13`, `NFT_REG32_14`, `NFT_REG32_15`, `NFT_CONTINUE`, and 625 more. Macros expose `_LINUX_NF_TABLES_H`, `NFT_NAME_MAXLEN`, `NFT_TABLE_MAXNAMELEN`, `NFT_CHAIN_MAXNAMELEN`, `NFT_SET_MAXNAMELEN`, `NFT_OBJ_MAXNAMELEN`, `NFT_USERDATA_MAXLEN`, `NFT_OSF_MAXGENRELEN`, `NFT_REG_MAX`, `NFT_REG32_MAX`, `NFT_REG_SIZE`, `NFT_REG32_SIZE`, `NFT_REG32_COUNT`, `NFTA_LIST_MAX`, `NFTA_HOOK_MAX`, `NFT_TABLE_F_MASK`, `NFTA_TABLE_MAX`, `NFT_CHAIN_FLAGS`, and 100 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

User space sends nfnetlink nf_tables commands carrying nested attributes from this header. The kernel validates table/chain/rule/set/object attributes, binds expressions and hooks, then emits notifications using the same command and attribute IDs. Transactions and generation IDs are represented by dedicated message and attribute constants rather than by code in this header.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: enum nft_registers - nf_tables registers; nf_tables used to have five registers: a verdict register and four data; registers of size 16. The data registers have been changed to 16 registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables_compat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables_compat.h

## Purpose

`nf_tables_compat.h` defines nftables compatibility attributes for wrapping legacy x_tables matches and targets inside nftables expressions. The file is 39 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Enumerations include `nft_target_attributes`, `nft_match_attributes`, `anonymous enum`. Prominent attribute, command, flag, or constant names include `NFTA_TARGET_UNSPEC`, `NFTA_TARGET_NAME`, `NFTA_TARGET_REV`, `NFTA_TARGET_INFO`, `NFTA_MATCH_UNSPEC`, `NFTA_MATCH_NAME`, `NFTA_MATCH_REV`, `NFTA_MATCH_INFO`, `NFNL_MSG_COMPAT_GET`, `NFTA_COMPAT_UNSPEC`, `NFTA_COMPAT_NAME`, `NFTA_COMPAT_REV`, `NFTA_COMPAT_TYPE`. Macros expose `_NFT_COMPAT_NFNETLINK_H_`, `NFTA_TARGET_MAX`, `NFTA_MATCH_MAX`, `NFT_COMPAT_NAME_MAX`, `NFTA_COMPAT_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_tables_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_acct.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_acct.h

## Purpose

`nfnetlink_acct.h` defines the nfnetlink ABI for acct, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 46 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Enumerations include `nfnl_acct_msg_types`, `nfnl_acct_flags`, `nfnl_acct_type`, `nfnl_attr_filter_type`. Prominent attribute, command, flag, or constant names include `NFNL_MSG_ACCT_NEW`, `NFNL_MSG_ACCT_GET`, `NFNL_MSG_ACCT_GET_CTRZERO`, `NFNL_MSG_ACCT_DEL`, `NFNL_MSG_ACCT_OVERQUOTA`, `NFACCT_F_QUOTA_PKTS`, `NFACCT_F_QUOTA_BYTES`, `NFACCT_F_OVERQUOTA`, `NFACCT_UNSPEC`, `NFACCT_NAME`, `NFACCT_PKTS`, `NFACCT_BYTES`, `NFACCT_USE`, `NFACCT_FLAGS`, `NFACCT_QUOTA`, `NFACCT_FILTER`, `NFACCT_PAD`, `NFACCT_FILTER_UNSPEC`, `NFACCT_FILTER_MASK`, `NFACCT_FILTER_VALUE`. Macros expose `_UAPI_NFNL_ACCT_H_`, `NFACCT_NAME_MAX`, `NFACCT_MAX`, `NFACCT_FILTER_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_acct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_compat.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_conntrack.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cthelper.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cthelper.h

## Purpose

`nfnetlink_cthelper.h` defines the nfnetlink ABI for cthelper, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 56 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Enumerations include `nfnl_cthelper_msg_types`, `nfnl_cthelper_type`, `nfnl_cthelper_policy_type`, `nfnl_cthelper_pol_type`, `nfnl_cthelper_tuple_type`. Prominent attribute, command, flag, or constant names include `NFNL_MSG_CTHELPER_NEW`, `NFNL_MSG_CTHELPER_GET`, `NFNL_MSG_CTHELPER_DEL`, `NFCTH_UNSPEC`, `NFCTH_NAME`, `NFCTH_TUPLE`, `NFCTH_QUEUE_NUM`, `NFCTH_POLICY`, `NFCTH_PRIV_DATA_LEN`, `NFCTH_STATUS`, `NFCTH_POLICY_SET_UNSPEC`, `NFCTH_POLICY_SET_NUM`, `NFCTH_POLICY_SET`, `NFCTH_POLICY_SET1`, `NFCTH_POLICY_SET2`, `NFCTH_POLICY_SET3`, `NFCTH_POLICY_SET4`, `NFCTH_POLICY_UNSPEC`, `NFCTH_POLICY_NAME`, `NFCTH_POLICY_EXPECT_MAX`, `NFCTH_POLICY_EXPECT_TIMEOUT`, `NFCTH_TUPLE_UNSPEC`, and 2 more. Macros expose `_NFNL_CTHELPER_H_`, `NFCT_HELPER_STATUS_DISABLED`, `NFCT_HELPER_STATUS_ENABLED`, `NFCTH_MAX`, `NFCTH_POLICY_SET_MAX`, `NFCTH_POLICY_MAX`, `NFCTH_TUPLE_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cthelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cttimeout.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_cttimeout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_hook.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_hook.h

## Purpose

`nfnetlink_hook.h` defines the nfnetlink ABI for hook, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 84 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Enumerations include `nfnl_hook_msg_types`, `nfnl_hook_attributes`, `nfnl_hook_chain_info_attributes`, `nfnl_hook_chain_desc_attributes`, `nfnl_hook_chaintype`, `nfnl_hook_bpf_attributes`. Prominent attribute, command, flag, or constant names include `NFNL_MSG_HOOK_GET`, `NFNL_MSG_HOOK_MAX`, `NFNLA_HOOK_UNSPEC`, `NFNLA_HOOK_HOOKNUM`, `NFNLA_HOOK_PRIORITY`, `NFNLA_HOOK_DEV`, `NFNLA_HOOK_FUNCTION_NAME`, `NFNLA_HOOK_MODULE_NAME`, `NFNLA_HOOK_CHAIN_INFO`, `NFNLA_HOOK_INFO_UNSPEC`, `NFNLA_HOOK_INFO_DESC`, `NFNLA_HOOK_INFO_TYPE`, `NFNLA_CHAIN_UNSPEC`, `NFNLA_CHAIN_TABLE`, `NFNLA_CHAIN_FAMILY`, `NFNLA_CHAIN_NAME`, `NFNL_HOOK_TYPE_NFTABLES`, `NFNL_HOOK_TYPE_BPF`, `NFNL_HOOK_TYPE_NFT_FLOWTABLE`, `NFNLA_HOOK_BPF_UNSPEC`, `NFNLA_HOOK_BPF_ID`. Macros expose `_NFNL_HOOK_H_`, `NFNLA_HOOK_MAX`, `NFNLA_HOOK_INFO_MAX`, `NFNLA_CHAIN_MAX`, `NFNLA_HOOK_BPF_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: enum nfnl_hook_attributes - netfilter hook netlink attributes; @NFNLA_HOOK_HOOKNUM: netfilter hook number (NLA_U32); @NFNLA_HOOK_PRIORITY: netfilter hook priority (NLA_U32).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_hook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_log.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_osf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_osf.h

## Purpose

`nfnetlink_osf.h` defines the nfnetlink ABI for osf, including message types and nested attributes used by user space tools to configure or observe that netfilter facility. The file is 120 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/ip.h`, `linux/tcp.h`. Exported structures include `nf_osf_wc`, `nf_osf_opt`, `nf_osf_info`, `nf_osf_user_finger`, `nf_osf_nlmsg`, `iphdr`, `tcphdr`. Enumerations include `iana_options`, `nf_osf_window_size_options`, `nf_osf_attr_type`, `nf_osf_msg_types`. Prominent attribute, command, flag, or constant names include `OSFOPT_EOL`, `OSFOPT_NOP`, `OSFOPT_MSS`, `OSFOPT_WSO`, `OSFOPT_SACKP`, `OSFOPT_SACK`, `OSFOPT_ECHO`, `OSFOPT_ECHOREPLY`, `OSFOPT_TS`, `OSFOPT_POCP`, `OSFOPT_POSP`, `OSFOPT_EMPTY`, `OSF_WSS_PLAIN`, `OSF_WSS_MSS`, `OSF_WSS_MTU`, `OSF_WSS_MODULO`, `OSF_WSS_MAX`, `OSF_ATTR_UNSPEC`, `OSF_ATTR_FINGER`, `OSF_ATTR_MAX`, `OSF_MSG_ADD`, `OSF_MSG_REMOVE`, and 1 more. Macros expose `_NF_OSF_H`, `MAXGENRELEN`, `NF_OSF_GENRE`, `NF_OSF_TTL`, `NF_OSF_LOG`, `NF_OSF_INVERT`, `NF_OSF_LOGLEVEL_ALL`, `NF_OSF_LOGLEVEL_FIRST`, `NF_OSF_LOGLEVEL_ALL_KNOWN`, `NF_OSF_TTL_TRUE`, `NF_OSF_TTL_LESS`, `NF_OSF_TTL_NOCHECK`, `NF_OSF_FLAGMASK`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Control flow is a netlink request/reply or multicast-notification lifecycle: user space sends the message type defined here with nested attributes, kernel netfilter code validates policy and applies the operation, and replies or events reuse the same numeric ABI. This header contributes IDs and layouts, not handlers.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/ip.h`, `linux/tcp.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Check if ip TTL is less than fingerprint one; Do not compare ip and fingerprint TTL at all; Wildcard MSS (kind of)..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_osf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_queue.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nfnetlink_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/x_tables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/x_tables.h

## Purpose

`x_tables.h` defines the common x_tables ABI used by iptables, ip6tables, arptables, and ebtables extensions: match/target containers, counters, alignment, verdict values, and replacement metadata. The file is 188 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/const.h`, `linux/types.h`. Exported structures include `xt_entry_match`, `xt_match`, `xt_entry_target`, `xt_target`, `xt_standard_target`, `xt_error_target`, `xt_get_revision`, `_xt_align`, `xt_counters`, `xt_counters_info`. Macros expose `_UAPI_X_TABLES_H`, `XT_FUNCTION_MAXNAMELEN`, `XT_EXTENSION_MAXNAMELEN`, `XT_TABLE_MAXNAMELEN`, `XT_TARGET_INIT`, `XT_CONTINUE`, `XT_RETURN`, `XT_ALIGN`, `XT_STANDARD_TARGET`, `XT_ERROR_TARGET`, `SET_COUNTER`, `ADD_COUNTER`, `XT_INV_PROTO`, `XT_MATCH_ITERATE`, `XT_ENTRY_ITERATE_CONTINUE`, `XT_ENTRY_ITERATE`, `xt_entry_foreach`, `xt_ematch_foreach`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/const.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used by userspace; Used inside the kernel; Total length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/x_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_AUDIT.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_AUDIT.h

## Purpose

`xt_AUDIT.h` defines the x_tables match or target option structure for `xt_AUDIT`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 27 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_audit_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_AUDIT_TYPE_ACCEPT`, `XT_AUDIT_TYPE_DROP`, `XT_AUDIT_TYPE_REJECT`. Macros expose `_XT_AUDIT_TARGET_H`, `XT_AUDIT_TYPE_MAX`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for iptables xt_AUDIT target; (C) 2010-2011 Thomas Graf <tgraf@redhat.com>; (C) 2010-2011 Red Hat, Inc..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_AUDIT.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CHECKSUM.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CHECKSUM.h

## Purpose

`xt_CHECKSUM.h` defines the x_tables match or target option structure for `xt_CHECKSUM`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 21 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_CHECKSUM_info`. Macros expose `_XT_CHECKSUM_TARGET_H`, `XT_CHECKSUM_OP_FILL`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for iptables ipt_CHECKSUM target; (C) 2002 by Harald Welte <laforge@gnumonks.org>; (C) 2010 Red Hat Inc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CHECKSUM.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CLASSIFY.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CLASSIFY.h

## Purpose

`xt_CLASSIFY.h` defines the x_tables match or target option structure for `xt_CLASSIFY`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 11 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_classify_target_info`. Macros expose `_XT_CLASSIFY_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CLASSIFY.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNMARK.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNMARK.h

## Purpose

`xt_CONNMARK.h` defines the x_tables match or target option structure for `xt_CONNMARK`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 7 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/xt_connmark.h`. Macros expose `_XT_CONNMARK_H_target`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/xt_connmark.h`.

## Risks and Edge Cases

Key risks are malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNMARK.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNSECMARK.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNSECMARK.h

## Purpose

`xt_CONNSECMARK.h` defines the x_tables match or target option structure for `xt_CONNSECMARK`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 16 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_connsecmark_target_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `CONNSECMARK_SAVE`, `CONNSECMARK_RESTORE`. Macros expose `_XT_CONNSECMARK_H_target`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CONNSECMARK.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CT.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CT.h

## Purpose

`xt_CT.h` defines the x_tables match or target option structure for `xt_CT`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 42 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_ct_target_info`, `nf_conn`, `xt_ct_target_info_v1`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_CT_NOTRACK`, `XT_CT_NOTRACK_ALIAS`, `XT_CT_ZONE_DIR_ORIG`, `XT_CT_ZONE_DIR_REPL`, `XT_CT_ZONE_MARK`, `XT_CT_MASK`. Macros expose `_XT_CT_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel; Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_CT.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_DSCP.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_DSCP.h

## Purpose

`xt_DSCP.h` defines the x_tables match or target option structure for `xt_DSCP`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 27 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/xt_dscp.h`, `linux/types.h`. Exported structures include `xt_DSCP_info`, `xt_tos_target_info`. Macros expose `_XT_DSCP_TARGET_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/xt_dscp.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: x_tables module for setting the IPv4/IPv6 DSCP field; (C) 2002 Harald Welte <laforge@gnumonks.org>; based on ipt_FTOS.c (C) 2000 by Matthew G. Marsh <mgm@paktronix.com>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_DSCP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_HMARK.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_HMARK.h

## Purpose

`xt_HMARK.h` defines the x_tables match or target option structure for `xt_HMARK`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 52 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_hmark_info`. Exported unions include `hmark_ports`, `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_HMARK_SADDR_MASK`, `XT_HMARK_DADDR_MASK`, `XT_HMARK_SPI`, `XT_HMARK_SPI_MASK`, `XT_HMARK_SPORT`, `XT_HMARK_DPORT`, `XT_HMARK_SPORT_MASK`, `XT_HMARK_DPORT_MASK`, `XT_HMARK_PROTO_MASK`, `XT_HMARK_RND`, `XT_HMARK_MODULUS`, `XT_HMARK_OFFSET`, `XT_HMARK_CT`, `XT_HMARK_METHOD_L3`, `XT_HMARK_METHOD_L3_4`. Macros expose `XT_HMARK_H_`, `XT_HMARK_FLAG`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_HMARK.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_IDLETIMER.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_IDLETIMER.h

## Purpose

`xt_IDLETIMER.h` defines the x_tables match or target option structure for `xt_IDLETIMER`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 42 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `idletimer_tg_info`, `idletimer_tg`, `idletimer_tg_info_v1`. Macros expose `_XT_IDLETIMER_H`, `MAX_IDLETIMER_LABEL_SIZE`, `XT_IDLETIMER_ALARM`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for Xtables timer target module.; Copyright (C) 2004, 2010 Nokia Corporation; Written by Timo Teras <ext-timo.teras@nokia.com>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_IDLETIMER.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LED.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LED.h

## Purpose

`xt_LED.h` defines the x_tables match or target option structure for `xt_LED`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 16 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_led_info`. Macros expose `_XT_LED_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Kernel data used in the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LED.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LOG.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LOG.h

## Purpose

`xt_LOG.h` defines the x_tables match or target option structure for `xt_LOG`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 20 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `xt_log_info`. Macros expose `_XT_LOG_H`, `XT_LOG_TCPSEQ`, `XT_LOG_TCPOPT`, `XT_LOG_IPOPT`, `XT_LOG_UID`, `XT_LOG_NFLOG`, `XT_LOG_MACDECODE`, `XT_LOG_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: make sure not to change this without changing nf_log.h:NF_LOG_* (!).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_LOG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_MARK.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_MARK.h

## Purpose

`xt_MARK.h` defines the x_tables match or target option structure for `xt_MARK`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 7 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/xt_mark.h`. Macros expose `_XT_MARK_H_target`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/xt_mark.h`.

## Risks and Edge Cases

Key risks are malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_MARK.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFLOG.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFLOG.h

## Purpose

`xt_NFLOG.h` defines the x_tables match or target option structure for `xt_NFLOG`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 25 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_nflog_info`. Macros expose `_XT_NFLOG_TARGET`, `XT_NFLOG_DEFAULT_GROUP`, `XT_NFLOG_DEFAULT_THRESHOLD`, `XT_NFLOG_MASK`, `XT_NFLOG_F_COPY_LEN`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: This flag indicates that 'len' field in xt_nflog_info is set; 'len' will be used iff you set XT_NFLOG_F_COPY_LEN in flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFLOG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFQUEUE.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFQUEUE.h

## Purpose

`xt_NFQUEUE.h` defines the x_tables match or target option structure for `xt_NFQUEUE`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 39 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_NFQ_info`, `xt_NFQ_info_v1`, `xt_NFQ_info_v2`, `xt_NFQ_info_v3`. Macros expose `_XT_NFQ_TARGET_H`, `NFQ_FLAG_BYPASS`, `NFQ_FLAG_CPU_FANOUT`, `NFQ_FLAG_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: iptables module for using NFQUEUE mechanism; (C) 2005 Harald Welte <laforge@netfilter.org>; This software is distributed under GNU GPL v2, 1991.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_NFQUEUE.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_RATEEST.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_RATEEST.h

## Purpose

`xt_RATEEST.h` defines the x_tables match or target option structure for `xt_RATEEST`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 17 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if.h`. Exported structures include `xt_rateest_target_info`, `xt_rateest`. Macros expose `_XT_RATEEST_TARGET_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_RATEEST.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SECMARK.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SECMARK.h

## Purpose

`xt_SECMARK.h` defines the x_tables match or target option structure for `xt_SECMARK`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 29 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_secmark_target_info`, `xt_secmark_target_info_v1`. Macros expose `_XT_SECMARK_H_target`, `SECMARK_MODE_SEL`, `SECMARK_SECCTX_MAX`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: This is intended for use by various security subsystems (but not; at the same time).; 'mode' refers to the specific security subsystem which the.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SECMARK.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SYNPROXY.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SYNPROXY.h

## Purpose

`xt_SYNPROXY.h` defines the x_tables match or target option structure for `xt_SYNPROXY`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 15 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/nf_synproxy.h`. Macros expose `_XT_SYNPROXY_H`, `XT_SYNPROXY_OPT_MSS`, `XT_SYNPROXY_OPT_WSCALE`, `XT_SYNPROXY_OPT_SACK_PERM`, `XT_SYNPROXY_OPT_TIMESTAMP`, `XT_SYNPROXY_OPT_ECN`, `xt_synproxy_info`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/nf_synproxy.h`.

## Risks and Edge Cases

Key risks are malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_SYNPROXY.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPMSS.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPMSS.h

## Purpose

`xt_TCPMSS.h` defines the x_tables match or target option structure for `xt_TCPMSS`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 13 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_tcpmss_info`. Macros expose `_XT_TCPMSS_H`, `XT_TCPMSS_CLAMP_PMTU`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPMSS.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPOPTSTRIP.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPOPTSTRIP.h

## Purpose

`xt_TCPOPTSTRIP.h` defines the x_tables match or target option structure for `xt_TCPOPTSTRIP`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 16 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_tcpoptstrip_target_info`. Macros expose `_XT_TCPOPTSTRIP_H`, `tcpoptstrip_set_bit`, `tcpoptstrip_test_bit`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TCPOPTSTRIP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TEE.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TEE.h

## Purpose

`xt_TEE.h` defines the x_tables match or target option structure for `xt_TEE`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 15 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`. Exported structures include `xt_tee_tginfo`, `xt_tee_priv`. Exported unions include `nf_inet_addr`. Macros expose `_XT_TEE_TARGET_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TEE.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TPROXY.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TPROXY.h

## Purpose

`xt_TPROXY.h` defines the x_tables match or target option structure for `xt_TPROXY`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 25 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_tproxy_target_info`, `xt_tproxy_target_info_v1`. Exported unions include `nf_inet_addr`. Macros expose `_XT_TPROXY_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: TPROXY target is capable of marking the packet to perform; redirection. We can get rid of that whenever we get support for; mutliple targets in the same rule..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_TPROXY.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_addrtype.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_addrtype.h

## Purpose

`xt_addrtype.h` defines the x_tables match or target option structure for `xt_addrtype`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 45 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_addrtype_info_v1`, `xt_addrtype_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_ADDRTYPE_INVERT_SOURCE`, `XT_ADDRTYPE_INVERT_DEST`, `XT_ADDRTYPE_LIMIT_IFACE_IN`, `XT_ADDRTYPE_LIMIT_IFACE_OUT`, `XT_ADDRTYPE_UNSPEC`, `XT_ADDRTYPE_UNICAST`, `XT_ADDRTYPE_LOCAL`, `XT_ADDRTYPE_BROADCAST`, `XT_ADDRTYPE_ANYCAST`, `XT_ADDRTYPE_MULTICAST`, `XT_ADDRTYPE_BLACKHOLE`, `XT_ADDRTYPE_UNREACHABLE`, `XT_ADDRTYPE_PROHIBIT`, `XT_ADDRTYPE_THROW`, `XT_ADDRTYPE_NAT`, `XT_ADDRTYPE_XRESOLVE`. Macros expose `_XT_ADDRTYPE_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: rtn_type enum values from rtnetlink.h, but shifted; revision 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_addrtype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_bpf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_bpf.h

## Purpose

`xt_bpf.h` defines the x_tables match or target option structure for `xt_bpf`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 42 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/filter.h`, `linux/limits.h`, `linux/types.h`. Exported structures include `bpf_prog`, `xt_bpf_info`, `sock_filter`, `xt_bpf_info_v1`. Enumerations include `xt_bpf_modes`. Prominent attribute, command, flag, or constant names include `XT_BPF_MODE_BYTECODE`, `XT_BPF_MODE_FD_PINNED`, `XT_BPF_MODE_FD_ELF`. Macros expose `_XT_BPF_H`, `XT_BPF_MAX_NUM_INSTR`, `XT_BPF_PATH_MAX`, `XT_BPF_MODE_PATH_PINNED`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/filter.h`, `linux/limits.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: only used in the kernel; only used in the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cgroup.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cgroup.h

## Purpose

`xt_cgroup.h` defines the x_tables match or target option structure for `xt_cgroup`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 41 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/limits.h`. Exported structures include `xt_cgroup_info_v0`, `xt_cgroup_info_v1`, `xt_cgroup_info_v2`. Macros expose `_UAPI_XT_CGROUP_H`, `XT_CGROUP_PATH_MAX`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/limits.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: kernel internal data; kernel internal data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cluster.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cluster.h

## Purpose

`xt_cluster.h` defines the x_tables match or target option structure for `xt_cluster`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 20 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_cluster_match_info`. Enumerations include `xt_cluster_flags`. Prominent attribute, command, flag, or constant names include `XT_CLUSTER_F_INV`. Macros expose `_XT_CLUSTER_MATCH_H`, `XT_CLUSTER_NODES_MAX`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cluster.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_comment.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_comment.h

## Purpose

`xt_comment.h` defines the x_tables match or target option structure for `xt_comment`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 11 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `xt_comment_info`. Macros expose `_XT_COMMENT_H`, `XT_MAX_COMMENT_LEN`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_comment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connbytes.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connbytes.h

## Purpose

`xt_connbytes.h` defines the x_tables match or target option structure for `xt_connbytes`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 27 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_connbytes_info`. Enumerations include `xt_connbytes_what`, `xt_connbytes_direction`. Prominent attribute, command, flag, or constant names include `XT_CONNBYTES_PKTS`, `XT_CONNBYTES_BYTES`, `XT_CONNBYTES_AVGPKT`, `XT_CONNBYTES_DIR_ORIGINAL`, `XT_CONNBYTES_DIR_REPLY`, `XT_CONNBYTES_DIR_BOTH`. Macros expose `_XT_CONNBYTES_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connbytes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlabel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlabel.h

## Purpose

`xt_connlabel.h` defines the x_tables match or target option structure for `xt_connlabel`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 19 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_connlabel_mtinfo`. Enumerations include `xt_connlabel_mtopts`. Prominent attribute, command, flag, or constant names include `XT_CONNLABEL_OP_INVERT`, `XT_CONNLABEL_OP_SET`. Macros expose `_UAPI_XT_CONNLABEL_H`, `XT_CONNLABEL_MAXBIT`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlabel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlimit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlimit.h

## Purpose

`xt_connlimit.h` defines the x_tables match or target option structure for `xt_connlimit`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 33 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_connlimit_data`, `xt_connlimit_info`, `nf_conncount_data`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_CONNLIMIT_INVERT`, `XT_CONNLIMIT_DADDR`. Macros expose `_XT_CONNLIMIT_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: revision 1; Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connlimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connmark.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connmark.h

## Purpose

`xt_connmark.h` defines the x_tables match or target option structure for `xt_connmark`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 37 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_connmark_tginfo1`, `xt_connmark_tginfo2`, `xt_connmark_mtinfo1`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_CONNMARK_SET`, `XT_CONNMARK_SAVE`, `D_SHIFT_LEFT`, `D_SHIFT_RIGHT`. Macros expose `_XT_CONNMARK_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Copyright (C) 2002,2004 MARA Systems AB <https://www.marasystems.com>; by Henrik Nordstrom <hno@marasystems.com>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_connmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_conntrack.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_conntrack.h

## Purpose

`xt_conntrack.h` defines the x_tables match or target option structure for `xt_conntrack`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 79 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`, `linux/netfilter/nf_conntrack_tuple_common.h`. Exported structures include `xt_conntrack_mtinfo1`, `xt_conntrack_mtinfo2`, `xt_conntrack_mtinfo3`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_CONNTRACK_STATE`, `XT_CONNTRACK_PROTO`, `XT_CONNTRACK_ORIGSRC`, `XT_CONNTRACK_ORIGDST`, `XT_CONNTRACK_REPLSRC`, `XT_CONNTRACK_REPLDST`, `XT_CONNTRACK_STATUS`, `XT_CONNTRACK_EXPIRES`, `XT_CONNTRACK_ORIGSRC_PORT`, `XT_CONNTRACK_ORIGDST_PORT`, `XT_CONNTRACK_REPLSRC_PORT`, `XT_CONNTRACK_REPLDST_PORT`, `XT_CONNTRACK_DIRECTION`, `XT_CONNTRACK_STATE_ALIAS`. Macros expose `_XT_CONNTRACK_H`, `XT_CONNTRACK_STATE_BIT`, `XT_CONNTRACK_STATE_INVALID`, `XT_CONNTRACK_STATE_SNAT`, `XT_CONNTRACK_STATE_DNAT`, `XT_CONNTRACK_STATE_UNTRACKED`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`, `linux/netfilter/nf_conntrack_tuple_common.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for kernel module to match connection tracking information.; GPL (C) 2001  Marc Boucher (marc@mbsi.ca).; flags, invflags:.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cpu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cpu.h

## Purpose

`xt_cpu.h` defines the x_tables match or target option structure for `xt_cpu`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 12 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_cpu_info`. Macros expose `_XT_CPU_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dccp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dccp.h

## Purpose

`xt_dccp.h` defines the x_tables match or target option structure for `xt_dccp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 26 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_dccp_info`. Macros expose `_XT_DCCP_H_`, `XT_DCCP_SRC_PORTS`, `XT_DCCP_DEST_PORTS`, `XT_DCCP_TYPE`, `XT_DCCP_OPTION`, `XT_DCCP_VALID_FLAGS`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dccp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_devgroup.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_devgroup.h

## Purpose

`xt_devgroup.h` defines the x_tables match or target option structure for `xt_devgroup`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 22 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_devgroup_info`. Enumerations include `xt_devgroup_flags`. Prominent attribute, command, flag, or constant names include `XT_DEVGROUP_MATCH_SRC`, `XT_DEVGROUP_INVERT_SRC`, `XT_DEVGROUP_MATCH_DST`, `XT_DEVGROUP_INVERT_DST`. Macros expose `_XT_DEVGROUP_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_devgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dscp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dscp.h

## Purpose

`xt_dscp.h` defines the x_tables match or target option structure for `xt_dscp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 32 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_dscp_info`, `xt_tos_match_info`. Macros expose `_XT_DSCP_H`, `XT_DSCP_MASK`, `XT_DSCP_SHIFT`, `XT_DSCP_MAX`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: x_tables module for matching the IPv4/IPv6 DSCP field; (C) 2002 Harald Welte <laforge@gnumonks.org>; This software is distributed under GNU GPL v2, 1991.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_dscp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ecn.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ecn.h

## Purpose

`xt_ecn.h` defines the x_tables match or target option structure for `xt_ecn`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 36 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/xt_dscp.h`. Exported structures include `xt_ecn_info`. Macros expose `_XT_ECN_H`, `XT_ECN_IP_MASK`, `XT_ECN_OP_MATCH_IP`, `XT_ECN_OP_MATCH_ECE`, `XT_ECN_OP_MATCH_CWR`, `XT_ECN_OP_MATCH_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/xt_dscp.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: iptables module for matching the ECN header in IPv4 and TCP header; (C) 2002 Harald Welte <laforge@gnumonks.org>; This software is distributed under GNU GPL v2, 1991.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ecn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_esp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_esp.h

## Purpose

`xt_esp.h` defines the x_tables match or target option structure for `xt_esp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 16 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_esp`. Macros expose `_XT_ESP_H`, `XT_ESP_INV_SPI`, `XT_ESP_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct xt_esp..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_esp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_hashlimit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_hashlimit.h

## Purpose

`xt_hashlimit.h` defines the x_tables match or target option structure for `xt_hashlimit`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 123 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/limits.h`, `linux/if.h`. Exported structures include `xt_hashlimit_htable`, `hashlimit_cfg`, `xt_hashlimit_info`, `hashlimit_cfg1`, `hashlimit_cfg2`, `hashlimit_cfg3`, `xt_hashlimit_mtinfo1`, `xt_hashlimit_mtinfo2`, `xt_hashlimit_mtinfo3`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_HASHLIMIT_HASH_DIP`, `XT_HASHLIMIT_HASH_DPT`, `XT_HASHLIMIT_HASH_SIP`, `XT_HASHLIMIT_HASH_SPT`, `XT_HASHLIMIT_INVERT`, `XT_HASHLIMIT_BYTES`, `XT_HASHLIMIT_RATE_MATCH`. Macros expose `_UAPI_XT_HASHLIMIT_H`, `XT_HASHLIMIT_SCALE`, `XT_HASHLIMIT_SCALE_v2`, `XT_HASHLIMIT_BYTE_SHIFT`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/limits.h`, `linux/if.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: timings are in milliseconds.; 1/10,000 sec period => max of 10,000/sec.  Min rate is then 429490; seconds, or one packet every 59 hours..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_hashlimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_helper.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_helper.h

## Purpose

`xt_helper.h` defines the x_tables match or target option structure for `xt_helper`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 9 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `xt_helper_info`. Macros expose `_XT_HELPER_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipcomp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipcomp.h

## Purpose

`xt_ipcomp.h` defines the x_tables match or target option structure for `xt_ipcomp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 17 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_ipcomp`. Macros expose `_XT_IPCOMP_H`, `XT_IPCOMP_INV_SPI`, `XT_IPCOMP_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct xt_ipcomp..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipcomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_iprange.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_iprange.h

## Purpose

`xt_iprange.h` defines the x_tables match or target option structure for `xt_iprange`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 21 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_iprange_mtinfo`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IPRANGE_SRC`, `IPRANGE_DST`, `IPRANGE_SRC_INV`, `IPRANGE_DST_INV`. Macros expose `_LINUX_NETFILTER_XT_IPRANGE_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_iprange.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipvs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipvs.h

## Purpose

`xt_ipvs.h` defines the x_tables match or target option structure for `xt_ipvs`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 31 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_ipvs_mtinfo`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_IPVS_IPVS_PROPERTY`, `XT_IPVS_PROTO`, `XT_IPVS_VADDR`, `XT_IPVS_VPORT`, `XT_IPVS_DIR`, `XT_IPVS_METHOD`, `XT_IPVS_VPORTCTL`, `XT_IPVS_MASK`, `XT_IPVS_ONCE_MASK`. Macros expose `_XT_IPVS_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_ipvs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_l2tp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_l2tp.h

## Purpose

`xt_l2tp.h` defines the x_tables match or target option structure for `xt_l2tp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 28 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_l2tp_info`. Enumerations include `xt_l2tp_type`, `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_L2TP_TYPE_CONTROL`, `XT_L2TP_TYPE_DATA`, `XT_L2TP_TID`, `XT_L2TP_SID`, `XT_L2TP_VERSION`, `XT_L2TP_TYPE`. Macros expose `_LINUX_NETFILTER_XT_L2TP_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: L2TP matching stuff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_l2tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_length.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_length.h

## Purpose

`xt_length.h` defines the x_tables match or target option structure for `xt_length`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 12 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_length_info`. Macros expose `_XT_LENGTH_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_length.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_limit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_limit.h

## Purpose

`xt_limit.h` defines the x_tables match or target option structure for `xt_limit`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 25 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_limit_priv`, `xt_rateinfo`. Macros expose `_XT_RATE_H`, `XT_LIMIT_SCALE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: timings are in milliseconds.; 1/10,000 sec period => max of 10,000/sec.  Min rate is then 429490; Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_limit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mac.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mac.h

## Purpose

`xt_mac.h` defines the x_tables match or target option structure for `xt_mac`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 11 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/if_ether.h`. Exported structures include `xt_mac_info`. Macros expose `_XT_MAC_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mark.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mark.h

## Purpose

`xt_mark.h` defines the x_tables match or target option structure for `xt_mark`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 16 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_mark_tginfo2`, `xt_mark_mtinfo1`. Macros expose `_XT_MARK_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_mark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_multiport.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_multiport.h

## Purpose

`xt_multiport.h` defines the x_tables match or target option structure for `xt_multiport`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 30 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_multiport`, `xt_multiport_v1`. Enumerations include `xt_multiport_flags`. Prominent attribute, command, flag, or constant names include `XT_MULTIPORT_SOURCE`, `XT_MULTIPORT_DESTINATION`. Macros expose `_XT_MULTIPORT_H`, `XT_MULTI_PORTS`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Must fit inside union xt_matchinfo: 16 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_multiport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_nfacct.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_nfacct.h

## Purpose

`xt_nfacct.h` defines the x_tables match or target option structure for `xt_nfacct`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 19 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/nfnetlink_acct.h`. Exported structures include `nf_acct`, `xt_nfacct_match_info`, `xt_nfacct_match_info_v1`. Macros expose `_XT_NFACCT_MATCH_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/nfnetlink_acct.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_nfacct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_osf.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_osf.h

## Purpose

`xt_osf.h` defines the x_tables match or target option structure for `xt_osf`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 37 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/nfnetlink_osf.h`. Macros expose `_XT_OSF_H`, `XT_OSF_GENRE`, `XT_OSF_INVERT`, `XT_OSF_TTL`, `XT_OSF_LOG`, `XT_OSF_LOGLEVEL_ALL`, `XT_OSF_LOGLEVEL_FIRST`, `XT_OSF_LOGLEVEL_ALL_KNOWN`, `XT_OSF_TTL_TRUE`, `XT_OSF_TTL_NOCHECK`, `XT_OSF_TTL_LESS`, `xt_osf_wc`, `xt_osf_opt`, `xt_osf_info`, `xt_osf_user_finger`, `xt_osf_finger`, `xt_osf_nlmsg`, `xt_osf_window_size_options`, and 2 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/nfnetlink_osf.h`.

## Risks and Edge Cases

Key risks are malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Copyright (c) 2003+ Evgeniy Polyakov <johnpol@2ka.mxt.ru>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_osf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_owner.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_owner.h

## Purpose

`xt_owner.h` defines the x_tables match or target option structure for `xt_owner`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 25 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_owner_match_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_OWNER_UID`, `XT_OWNER_GID`, `XT_OWNER_SOCKET`, `XT_OWNER_SUPPL_GROUPS`. Macros expose `_XT_OWNER_MATCH_H`, `XT_OWNER_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_owner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_physdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_physdev.h

## Purpose

`xt_physdev.h` defines the x_tables match or target option structure for `xt_physdev`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 24 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if.h`. Exported structures include `xt_physdev_info`. Macros expose `_UAPI_XT_PHYSDEV_H`, `XT_PHYSDEV_OP_IN`, `XT_PHYSDEV_OP_OUT`, `XT_PHYSDEV_OP_BRIDGED`, `XT_PHYSDEV_OP_ISIN`, `XT_PHYSDEV_OP_ISOUT`, `XT_PHYSDEV_OP_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_physdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_pkttype.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_pkttype.h

## Purpose

`xt_pkttype.h` defines the x_tables match or target option structure for `xt_pkttype`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 9 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `xt_pkttype_info`. Macros expose `_XT_PKTTYPE_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_pkttype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_policy.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_policy.h

## Purpose

`xt_policy.h` defines the x_tables match or target option structure for `xt_policy`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 73 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`, `linux/types.h`, `linux/in.h`, `linux/in6.h`. Exported structures include `xt_policy_spec`, `in_addr`, `in6_addr`, `xt_policy_elem`, `xt_policy_info`. Exported unions include `xt_policy_addr`, `nf_inet_addr`. Enumerations include `xt_policy_flags`, `xt_policy_modes`. Prominent attribute, command, flag, or constant names include `XT_POLICY_MATCH_IN`, `XT_POLICY_MATCH_OUT`, `XT_POLICY_MATCH_NONE`, `XT_POLICY_MATCH_STRICT`, `XT_POLICY_MODE_TRANSPORT`. Macros expose `_XT_POLICY_H`, `XT_POLICY_MAX_ELEM`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`, `linux/types.h`, `linux/in.h`, `linux/in6.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_quota.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_quota.h

## Purpose

`xt_quota.h` defines the x_tables match or target option structure for `xt_quota`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 23 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_quota_priv`, `xt_quota_info`. Enumerations include `xt_quota_flags`. Prominent attribute, command, flag, or constant names include `XT_QUOTA_INVERT`. Macros expose `_XT_QUOTA_H`, `XT_QUOTA_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rateest.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rateest.h

## Purpose

`xt_rateest.h` defines the x_tables match or target option structure for `xt_rateest`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 39 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if.h`. Exported structures include `xt_rateest_match_info`, `xt_rateest`. Enumerations include `xt_rateest_match_flags`, `xt_rateest_match_mode`. Prominent attribute, command, flag, or constant names include `XT_RATEEST_MATCH_INVERT`, `XT_RATEEST_MATCH_ABS`, `XT_RATEEST_MATCH_REL`, `XT_RATEEST_MATCH_DELTA`, `XT_RATEEST_MATCH_BPS`, `XT_RATEEST_MATCH_PPS`, `XT_RATEEST_MATCH_NONE`, `XT_RATEEST_MATCH_EQ`, `XT_RATEEST_MATCH_LT`, `XT_RATEEST_MATCH_GT`. Macros expose `_XT_RATEEST_MATCH_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rateest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_realm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_realm.h

## Purpose

`xt_realm.h` defines the x_tables match or target option structure for `xt_realm`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 13 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_realm_info`. Macros expose `_XT_REALM_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_realm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_recent.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_recent.h

## Purpose

`xt_recent.h` defines the x_tables match or target option structure for `xt_recent`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 47 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `xt_recent_mtinfo`, `xt_recent_mtinfo_v1`. Exported unions include `nf_inet_addr`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_RECENT_CHECK`, `XT_RECENT_SET`, `XT_RECENT_UPDATE`, `XT_RECENT_REMOVE`, `XT_RECENT_TTL`, `XT_RECENT_REAP`, `XT_RECENT_SOURCE`, `XT_RECENT_DEST`, `XT_RECENT_NAME_LEN`. Macros expose `_LINUX_NETFILTER_XT_RECENT_H`, `XT_RECENT_MODIFIERS`, `XT_RECENT_VALID_FLAGS`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Only allowed with --rcheck and --update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_recent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rpfilter.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rpfilter.h

## Purpose

`xt_rpfilter.h` defines the x_tables match or target option structure for `xt_rpfilter`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 24 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_rpfilter_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_RPFILTER_LOOSE`, `XT_RPFILTER_VALID_MARK`, `XT_RPFILTER_ACCEPT_LOCAL`, `XT_RPFILTER_INVERT`, `XT_RPFILTER_OPTION_MASK`. Macros expose `_XT_RPATH_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_rpfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_sctp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_sctp.h

## Purpose

`xt_sctp.h` defines the x_tables match or target option structure for `xt_sctp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 93 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_sctp_flag_info`, `xt_sctp_info`. Macros expose `_XT_SCTP_H_`, `XT_SCTP_SRC_PORTS`, `XT_SCTP_DEST_PORTS`, `XT_SCTP_CHUNK_TYPES`, `XT_SCTP_VALID_FLAGS`, `XT_NUM_SCTP_FLAGS`, `SCTP_CHUNK_MATCH_ANY`, `SCTP_CHUNK_MATCH_ALL`, `SCTP_CHUNK_MATCH_ONLY`, `bytes`, `SCTP_CHUNKMAP_SET`, `SCTP_CHUNKMAP_CLEAR`, `SCTP_CHUNKMAP_IS_SET`, `SCTP_CHUNKMAP_RESET`, `SCTP_CHUNKMAP_SET_ALL`, `SCTP_CHUNKMAP_COPY`, `SCTP_CHUNKMAP_IS_CLEAR`, `SCTP_CHUNKMAP_IS_ALL_SET`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_set.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_set.h

## Purpose

`xt_set.h` defines the x_tables match or target option structure for `xt_set`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 94 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/ipset/ip_set.h`. Exported structures include `xt_set_info_v0`, `xt_set_info_match_v0`, `xt_set_info_target_v0`, `xt_set_info`, `xt_set_info_match_v1`, `xt_set_info_target_v1`, `xt_set_info_target_v2`, `xt_set_info_match_v3`, `ip_set_counter_match0`, `xt_set_info_target_v3`, `xt_set_info_match_v4`, `ip_set_counter_match`. Macros expose `_XT_SET_H`, `IPSET_SRC`, `IPSET_DST`, `IPSET_MATCH_INV`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/ipset/ip_set.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Revision 0 interface: backward compatible with netfilter/iptables; Option flags for kernel operations (xt_set_info_v0); match and target infos.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_socket.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_socket.h

## Purpose

`xt_socket.h` defines the x_tables match or target option structure for `xt_socket`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 30 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_socket_mtinfo1`, `xt_socket_mtinfo2`, `xt_socket_mtinfo3`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_SOCKET_TRANSPARENT`, `XT_SOCKET_NOWILDCARD`, `XT_SOCKET_RESTORESKMARK`. Macros expose `_XT_SOCKET_H`, `XT_SOCKET_FLAGS_V1`, `XT_SOCKET_FLAGS_V2`, `XT_SOCKET_FLAGS_V3`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_state.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_state.h

## Purpose

`xt_state.h` defines the x_tables match or target option structure for `xt_state`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 13 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `xt_state_info`. Macros expose `_XT_STATE_H`, `XT_STATE_BIT`, `XT_STATE_INVALID`, `XT_STATE_UNTRACKED`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_statistic.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_statistic.h

## Purpose

`xt_statistic.h` defines the x_tables match or target option structure for `xt_statistic`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 37 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_statistic_priv`, `xt_statistic_info`. Enumerations include `xt_statistic_mode`, `xt_statistic_flags`. Prominent attribute, command, flag, or constant names include `XT_STATISTIC_MODE_RANDOM`, `XT_STATISTIC_MODE_NTH`, `XT_STATISTIC_INVERT`. Macros expose `_XT_STATISTIC_H`, `XT_STATISTIC_MODE_MAX`, `XT_STATISTIC_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_statistic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_string.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_string.h

## Purpose

`xt_string.h` defines the x_tables match or target option structure for `xt_string`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 35 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_string_info`, `ts_config`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_STRING_FLAG_INVERT`, `XT_STRING_FLAG_IGNORECASE`. Macros expose `_XT_STRING_H`, `XT_STRING_MAX_PATTERN_SIZE`, `XT_STRING_MAX_ALGO_NAME_SIZE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpmss.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpmss.h

## Purpose

`xt_tcpmss.h` defines the x_tables match or target option structure for `xt_tcpmss`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 12 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_tcpmss_match_info`. Macros expose `_XT_TCPMSS_MATCH_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpmss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpudp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpudp.h

## Purpose

`xt_tcpudp.h` defines the x_tables match or target option structure for `xt_tcpudp`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 37 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_tcp`, `xt_udp`. Macros expose `_XT_TCPUDP_H`, `XT_TCP_INV_SRCPT`, `XT_TCP_INV_DSTPT`, `XT_TCP_INV_FLAGS`, `XT_TCP_INV_OPTION`, `XT_TCP_INV_MASK`, `XT_UDP_INV_SRCPT`, `XT_UDP_INV_DSTPT`, `XT_UDP_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: TCP matching stuff; Values for "inv" field in struct ipt_tcp.; UDP matching stuff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_tcpudp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_time.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_time.h

## Purpose

`xt_time.h` defines the x_tables match or target option structure for `xt_time`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 33 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_time_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `XT_TIME_LOCAL_TZ`, `XT_TIME_CONTIGUOUS`, `XT_TIME_ALL_MONTHDAYS`, `XT_TIME_ALL_WEEKDAYS`, `XT_TIME_MIN_DAYTIME`, `XT_TIME_MAX_DAYTIME`. Macros expose `_XT_TIME_H`, `XT_TIME_ALL_FLAGS`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Match against local time (instead of UTC); treat timestart > timestop (e.g. 23:00-01:00) as single period; Shortcuts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_u32.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_u32.h

## Purpose

`xt_u32.h` defines the x_tables match or target option structure for `xt_u32`, giving user space and kernel extensions a stable binary layout for rule parameters. The file is 43 lines and is part of the generic netfilter UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `xt_u32_location_element`, `xt_u32_value_element`, `xt_u32_test`, `xt_u32`. Enumerations include `xt_u32_ops`. Prominent attribute, command, flag, or constant names include `XT_U32_AND`, `XT_U32_LEFTSH`, `XT_U32_RIGHTSH`, `XT_U32_AT`. Macros expose `_XT_U32_H`, `XT_U32_MAXSIZE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

At runtime an xtables-compatible tool copies one of these option structures into a rule blob. The kernel extension interprets the blob when the rule is installed and again when packets traverse the relevant hook. This header does not implement matching or target actions; it defines the data that drives those modules.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Any way to allow for an arbitrary number of elements?; For now, I settle with a limit of 10 each..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/xt_u32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arp_tables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arp_tables.h

## Purpose

`arp_tables.h` defines the ARP x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 208 lines and is part of the ARP netfilter/arptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_arp.h`, `linux/netfilter/x_tables.h`. Exported structures include `arpt_devaddr_info`, `arpt_arp`, `in_addr`, `arpt_entry`, `xt_counters`, `arpt_getinfo`, `arpt_replace`, `arpt_get_entries`. Macros expose `_UAPI_ARPTABLES_H`, `ARPT_FUNCTION_MAXNAMELEN`, `ARPT_TABLE_MAXNAMELEN`, `arpt_entry_target`, `arpt_standard_target`, `arpt_error_target`, `ARPT_CONTINUE`, `ARPT_RETURN`, `arpt_counters_info`, `arpt_counters`, `ARPT_STANDARD_TARGET`, `ARPT_ERROR_TARGET`, `ARPT_ENTRY_ITERATE`, `ARPT_DEV_ADDR_LEN_MAX`, `ARPT_F_MASK`, `ARPT_INV_VIA_IN`, `ARPT_INV_VIA_OUT`, `ARPT_INV_SRCIP`, and 16 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_arp.h`, `linux/netfilter/x_tables.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Format of an ARP firewall descriptor; src, tgt, src_mask, tgt_mask, arpop, arpop_mask are always stored in; network byte order..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arp_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arpt_mangle.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_arp/arpt_mangle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge.h

## Purpose

`netfilter_bridge.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for bridge packet processing. The file is 45 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `netinet/if_ether.h`, `linux/in.h`, `linux/netfilter.h`, `linux/if_ether.h`, `linux/if_vlan.h`, `linux/if_pppox.h`, `linux/typelimits.h`. Enumerations include `nf_br_hook_priorities`. Prominent attribute, command, flag, or constant names include `NF_BR_PRI_FIRST`, `NF_BR_PRI_NAT_DST_BRIDGED`, `NF_BR_PRI_FILTER_BRIDGED`, `NF_BR_PRI_BRNF`, `NF_BR_PRI_NAT_DST_OTHER`, `NF_BR_PRI_FILTER_OTHER`, `NF_BR_PRI_NAT_SRC`, `NF_BR_PRI_LAST`. Macros expose `_UAPI__LINUX_BRIDGE_NETFILTER_H`, `NF_BR_PRE_ROUTING`, `NF_BR_LOCAL_IN`, `NF_BR_FORWARD`, `NF_BR_LOCAL_OUT`, `NF_BR_POST_ROUTING`, `NF_BR_BROUTING`, `NF_BR_NUMHOOKS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `netinet/if_ether.h`, `linux/in.h`, `linux/netfilter.h`, `linux/if_ether.h`, `linux/if_vlan.h`, `linux/if_pppox.h`, `linux/typelimits.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: bridge-specific defines for netfilter.; Bridge Hooks; After promisc drops, checksum checks..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_802_3.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_802_3.h

## Purpose

`ebt_802_3.h` defines the ebtables bridge match or target parameter ABI for `ebt_802_3`, used by bridge netfilter rules operating on Ethernet frames. The file is 64 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if_ether.h`. Exported structures include `hdr_ui`, `hdr_ni`, `ebt_802_3_hdr`, `ebt_802_3_info`. Macros expose `_UAPI__LINUX_BRIDGE_EBT_802_3_H`, `EBT_802_3_SAP`, `EBT_802_3_TYPE`, `EBT_802_3_MATCH`, `CHECK_TYPE`, `IS_UI`, `EBT_802_3_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: If frame has DSAP/SSAP value 0xaa you must check the SNAP type; to discover what kind of packet we're carrying.; Control field may be one or two bytes.  If the first byte has.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_802_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_among.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_among.h

## Purpose

`ebt_among.h` defines the ebtables bridge match or target parameter ABI for `ebt_among`, used by bridge netfilter rules operating on Ethernet frames. The file is 65 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_mac_wormhash_tuple`, `ebt_mac_wormhash`, `ebt_among_info`. Macros expose `__LINUX_BRIDGE_EBT_AMONG_H`, `EBT_AMONG_DST`, `EBT_AMONG_SRC`, `ebt_mac_wormhash_size`, `EBT_AMONG_DST_NEG`, `EBT_AMONG_SRC_NEG`, `ebt_among_wh_dst`, `ebt_among_wh_src`, `EBT_AMONG_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Grzegorz Borowiak <grzes@gnu.univ.gda.pl> 2003; Write-once-read-many hash table, used for checking if a given; MAC address belongs to a set or not and possibly for checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_among.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arp.h

## Purpose

`ebt_arp.h` defines the ebtables bridge match or target parameter ABI for `ebt_arp`, used by bridge netfilter rules operating on Ethernet frames. The file is 38 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if_ether.h`. Exported structures include `ebt_arp_info`. Macros expose `__LINUX_BRIDGE_EBT_ARP_H`, `EBT_ARP_OPCODE`, `EBT_ARP_HTYPE`, `EBT_ARP_PTYPE`, `EBT_ARP_SRC_IP`, `EBT_ARP_DST_IP`, `EBT_ARP_SRC_MAC`, `EBT_ARP_DST_MAC`, `EBT_ARP_GRAT`, `EBT_ARP_MASK`, `EBT_ARP_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arpreply.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arpreply.h

## Purpose

`ebt_arpreply.h` defines the ebtables bridge match or target parameter ABI for `ebt_arpreply`, used by bridge netfilter rules operating on Ethernet frames. The file is 13 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/if_ether.h`. Exported structures include `ebt_arpreply_info`. Macros expose `__LINUX_BRIDGE_EBT_ARPREPLY_H`, `EBT_ARPREPLY_TARGET`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_arpreply.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip.h

## Purpose

`ebt_ip.h` defines the ebtables bridge match or target parameter ABI for `ebt_ip`, used by bridge netfilter rules operating on Ethernet frames. The file is 54 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_ip_info`. Macros expose `__LINUX_BRIDGE_EBT_IP_H`, `EBT_IP_SOURCE`, `EBT_IP_DEST`, `EBT_IP_TOS`, `EBT_IP_PROTO`, `EBT_IP_SPORT`, `EBT_IP_DPORT`, `EBT_IP_ICMP`, `EBT_IP_IGMP`, `EBT_IP_MASK`, `EBT_IP_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Bart De Schuymer <bart.de.schuymer@pandora.be>; April, 2002; added ip-sport and ip-dport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip6.h

## Purpose

`ebt_ip6.h` defines the ebtables bridge match or target parameter ABI for `ebt_ip6`, used by bridge netfilter rules operating on Ethernet frames. The file is 52 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/in6.h`. Exported structures include `ebt_ip6_info`, `in6_addr`. Macros expose `__LINUX_BRIDGE_EBT_IP6_H`, `EBT_IP6_SOURCE`, `EBT_IP6_DEST`, `EBT_IP6_TCLASS`, `EBT_IP6_PROTO`, `EBT_IP6_SPORT`, `EBT_IP6_DPORT`, `EBT_IP6_ICMP6`, `EBT_IP6_MASK`, `EBT_IP6_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/in6.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Kuo-Lang Tseng <kuo-lang.tseng@intel.com>; Manohar Castelino <manohar.r.castelino@intel.com>; Jan 11, 2008.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_ip6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_limit.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_limit.h

## Purpose

`ebt_limit.h` defines the ebtables bridge match or target parameter ABI for `ebt_limit`, used by bridge netfilter rules operating on Ethernet frames. The file is 25 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_limit_info`. Macros expose `__LINUX_BRIDGE_EBT_LIMIT_H`, `EBT_LIMIT_MATCH`, `EBT_LIMIT_SCALE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: timings are in milliseconds.; 1/10,000 sec period => max of 10,000/sec.  Min rate is then 429490; Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_limit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_log.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_log.h

## Purpose

`ebt_log.h` defines the ebtables bridge match or target parameter ABI for `ebt_log`, used by bridge netfilter rules operating on Ethernet frames. The file is 21 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_log_info`. Macros expose `__LINUX_BRIDGE_EBT_LOG_H`, `EBT_LOG_IP`, `EBT_LOG_ARP`, `EBT_LOG_NFLOG`, `EBT_LOG_IP6`, `EBT_LOG_MASK`, `EBT_LOG_PREFIX_SIZE`, `EBT_LOG_WATCHER`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_m.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_m.h

## Purpose

`ebt_mark_m.h` defines the ebtables bridge match or target parameter ABI for `ebt_mark_m`, used by bridge netfilter rules operating on Ethernet frames. The file is 17 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_mark_m_info`. Macros expose `__LINUX_BRIDGE_EBT_MARK_M_H`, `EBT_MARK_AND`, `EBT_MARK_OR`, `EBT_MARK_MASK`, `EBT_MARK_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_t.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_mark_t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nat.h

## Purpose

`ebt_nat.h` defines the ebtables bridge match or target parameter ABI for `ebt_nat`, used by bridge netfilter rules operating on Ethernet frames. The file is 16 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/if_ether.h`. Exported structures include `ebt_nat_info`. Macros expose `__LINUX_BRIDGE_EBT_NAT_H`, `NAT_ARP_BIT`, `EBT_SNAT_TARGET`, `EBT_DNAT_TARGET`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: EBT_ACCEPT, EBT_DROP, EBT_CONTINUE or EBT_RETURN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nflog.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nflog.h

## Purpose

`ebt_nflog.h` defines the ebtables bridge match or target parameter ABI for `ebt_nflog`, used by bridge netfilter rules operating on Ethernet frames. The file is 24 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_nflog_info`. Macros expose `__LINUX_BRIDGE_EBT_NFLOG_H`, `EBT_NFLOG_MASK`, `EBT_NFLOG_PREFIX_SIZE`, `EBT_NFLOG_WATCHER`, `EBT_NFLOG_DEFAULT_GROUP`, `EBT_NFLOG_DEFAULT_THRESHOLD`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_nflog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_pkttype.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_pkttype.h

## Purpose

`ebt_pkttype.h` defines the ebtables bridge match or target parameter ABI for `ebt_pkttype`, used by bridge netfilter rules operating on Ethernet frames. The file is 13 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_pkttype_info`. Macros expose `__LINUX_BRIDGE_EBT_PKTTYPE_H`, `EBT_PKTTYPE_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_pkttype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_redirect.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_redirect.h

## Purpose

`ebt_redirect.h` defines the ebtables bridge match or target parameter ABI for `ebt_redirect`, used by bridge netfilter rules operating on Ethernet frames. The file is 11 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ebt_redirect_info`. Macros expose `__LINUX_BRIDGE_EBT_REDIRECT_H`, `EBT_REDIRECT_TARGET`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

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

Source comments call out: EBT_ACCEPT, EBT_DROP, EBT_CONTINUE or EBT_RETURN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_redirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_stp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_stp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_vlan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_vlan.h

## Purpose

`ebt_vlan.h` defines the ebtables bridge match or target parameter ABI for `ebt_vlan`, used by bridge netfilter rules operating on Ethernet frames. The file is 23 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ebt_vlan_info`. Macros expose `__LINUX_BRIDGE_EBT_VLAN_H`, `EBT_VLAN_ID`, `EBT_VLAN_PRIO`, `EBT_VLAN_ENCAP`, `EBT_VLAN_MASK`, `EBT_VLAN_MATCH`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebt_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebtables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebtables.h

## Purpose

`ebtables.h` defines the Ethernet bridge x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 287 lines and is part of the bridge netfilter/ebtables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if.h`, `linux/netfilter_bridge.h`. Exported structures include `xt_match`, `xt_target`, `ebt_counter`, `ebt_replace`, `ebt_entries`, `ebt_replace_kernel`, `ebt_entry_match`, `ebt_entry_watcher`, `ebt_entry_target`, `ebt_standard_target`, `ebt_entry`. Macros expose `_UAPI__LINUX_BRIDGE_EFF_H`, `EBT_TABLE_MAXNAMELEN`, `EBT_CHAIN_MAXNAMELEN`, `EBT_FUNCTION_MAXNAMELEN`, `EBT_EXTENSION_MAXNAMELEN`, `EBT_ACCEPT`, `EBT_DROP`, `EBT_CONTINUE`, `EBT_RETURN`, `NUM_STANDARD_TARGETS`, `EBT_VERDICT_BITS`, `EBT_ENTRY_OR_ENTRIES`, `EBT_NOPROTO`, `EBT_802_3`, `EBT_SOURCEMAC`, `EBT_DESTMAC`, `EBT_F_MASK`, `EBT_IPROTO`, and 20 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if.h`, `linux/netfilter_bridge.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Bart De Schuymer		<bdschuym@pandora.be>; ebtables.c,v 2.0, April, 2002; This code is strongly inspired by the iptables code which is.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_bridge/ebtables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4.h

## Purpose

`netfilter_ipv4.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for ipv4 packet processing. The file is 54 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`, `linux/typelimits.h`. Enumerations include `nf_ip_hook_priorities`. Prominent attribute, command, flag, or constant names include `NF_IP_PRI_FIRST`, `NF_IP_PRI_RAW_BEFORE_DEFRAG`, `NF_IP_PRI_CONNTRACK_DEFRAG`, `NF_IP_PRI_RAW`, `NF_IP_PRI_SELINUX_FIRST`, `NF_IP_PRI_CONNTRACK`, `NF_IP_PRI_MANGLE`, `NF_IP_PRI_NAT_DST`, `NF_IP_PRI_FILTER`, `NF_IP_PRI_SECURITY`, `NF_IP_PRI_NAT_SRC`, `NF_IP_PRI_SELINUX_LAST`, `NF_IP_PRI_CONNTRACK_HELPER`, `NF_IP_PRI_CONNTRACK_CONFIRM`, `NF_IP_PRI_LAST`. Macros expose `_UAPI__LINUX_IP_NETFILTER_H`, `NF_IP_PRE_ROUTING`, `NF_IP_LOCAL_IN`, `NF_IP_FORWARD`, `NF_IP_LOCAL_OUT`, `NF_IP_POST_ROUTING`, `NF_IP_NUMHOOKS`, `SO_ORIGINAL_DST`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`, `linux/typelimits.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: IPv4-specific defines for netfilter.; (C)1998 Rusty Russell -- This code is GPL.; only for userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ip_tables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ip_tables.h

## Purpose

`ip_tables.h` defines the IPv4 x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 231 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv4.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`. Exported structures include `ipt_ip`, `in_addr`, `ipt_entry`, `xt_counters`, `ipt_icmp`, `ipt_getinfo`, `ipt_replace`, `ipt_get_entries`. Macros expose `_UAPI_IPTABLES_H`, `IPT_FUNCTION_MAXNAMELEN`, `IPT_TABLE_MAXNAMELEN`, `ipt_match`, `ipt_target`, `ipt_table`, `ipt_get_revision`, `ipt_entry_match`, `ipt_entry_target`, `ipt_standard_target`, `ipt_error_target`, `ipt_counters`, `IPT_CONTINUE`, `IPT_RETURN`, `ipt_udp`, `ipt_tcp`, `IPT_TCP_INV_SRCPT`, `IPT_TCP_INV_DSTPT`, and 32 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv4.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: 25-Jul-1998 Major changes to allow for ip chain table; 3-Jan-2000 Named tables to allow packet selection for different uses.; Format of an IP firewall descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ip_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_CLUSTERIP.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_CLUSTERIP.h

## Purpose

`ipt_CLUSTERIP.h` defines the IPv4 iptables extension ABI for `ipt_CLUSTERIP`, used to match or target IPv4 packet fields through x_tables. The file is 38 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/if_ether.h`. Exported structures include `clusterip_config`, `ipt_clusterip_tgt_info`. Enumerations include `clusterip_hashmode`. Prominent attribute, command, flag, or constant names include `CLUSTERIP_HASHMODE_SIP`, `CLUSTERIP_HASHMODE_SIP_SPT`, `CLUSTERIP_HASHMODE_SIP_SPT_DPT`. Macros expose `_IPT_CLUSTERIP_H_target`, `CLUSTERIP_HASHMODE_MAX`, `CLUSTERIP_MAX_NODES`, `CLUSTERIP_FLAG_NEW`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/if_ether.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: only relevant for new ones; Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_CLUSTERIP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ECN.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ECN.h

## Purpose

`ipt_ECN.h` defines the IPv4 iptables extension ABI for `ipt_ECN`, used to match or target IPv4 packet fields through x_tables. The file is 34 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter/xt_DSCP.h`. Exported structures include `ipt_ECN_info`. Macros expose `_IPT_ECN_TARGET_H`, `IPT_ECN_IP_MASK`, `IPT_ECN_OP_SET_IP`, `IPT_ECN_OP_SET_ECE`, `IPT_ECN_OP_SET_CWR`, `IPT_ECN_OP_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter/xt_DSCP.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Header file for iptables ipt_ECN target; (C) 2002 by Harald Welte <laforge@gnumonks.org>; This software is distributed under GNU GPL v2, 1991.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ECN.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_LOG.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_LOG.h

## Purpose

`ipt_LOG.h` defines the IPv4 iptables extension ABI for `ipt_LOG`, used to match or target IPv4 packet fields through x_tables. The file is 20 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ipt_log_info`. Macros expose `_IPT_LOG_H`, `IPT_LOG_TCPSEQ`, `IPT_LOG_TCPOPT`, `IPT_LOG_IPOPT`, `IPT_LOG_UID`, `IPT_LOG_NFLOG`, `IPT_LOG_MACDECODE`, `IPT_LOG_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

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

Source comments call out: make sure not to change this without changing netfilter.h:NF_LOG_* (!).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_LOG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_REJECT.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_REJECT.h

## Purpose

`ipt_REJECT.h` defines the IPv4 iptables extension ABI for `ipt_REJECT`, used to match or target IPv4 packet fields through x_tables. The file is 21 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ipt_reject_info`. Enumerations include `ipt_reject_with`. Prominent attribute, command, flag, or constant names include `IPT_ICMP_NET_UNREACHABLE`, `IPT_ICMP_HOST_UNREACHABLE`, `IPT_ICMP_PROT_UNREACHABLE`, `IPT_ICMP_PORT_UNREACHABLE`, `IPT_ICMP_ECHOREPLY`, `IPT_ICMP_NET_PROHIBITED`, `IPT_ICMP_HOST_PROHIBITED`, `IPT_TCP_RESET`. Macros expose `_IPT_REJECT_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_REJECT.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_TTL.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_TTL.h

## Purpose

`ipt_TTL.h` defines the IPv4 iptables extension ABI for `ipt_TTL`, used to match or target IPv4 packet fields through x_tables. The file is 24 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ipt_TTL_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IPT_TTL_SET`, `IPT_TTL_INC`. Macros expose `_IPT_TTL_H`, `IPT_TTL_MAXMODE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: TTL modification module for IP tables; (C) 2000 by Harald Welte <laforge@netfilter.org>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_TTL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ah.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ah.h

## Purpose

`ipt_ah.h` defines the IPv4 iptables extension ABI for `ipt_ah`, used to match or target IPv4 packet fields through x_tables. The file is 18 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ipt_ah`. Macros expose `_IPT_AH_H`, `IPT_AH_INV_SPI`, `IPT_AH_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct ipt_ah..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ecn.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ecn.h

## Purpose

`ipt_ecn.h` defines the IPv4 iptables extension ABI for `ipt_ecn`, used to match or target IPv4 packet fields through x_tables. The file is 16 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter/xt_ecn.h`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IPT_ECN_IP_MASK`, `IPT_ECN_OP_MATCH_IP`, `IPT_ECN_OP_MATCH_ECE`, `IPT_ECN_OP_MATCH_CWR`, `IPT_ECN_OP_MATCH_MASK`. Macros expose `_IPT_ECN_H`, `ipt_ecn_info`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter/xt_ecn.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ecn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ttl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ttl.h

## Purpose

`ipt_ttl.h` defines the IPv4 iptables extension ABI for `ipt_ttl`, used to match or target IPv4 packet fields through x_tables. The file is 24 lines and is part of the IPv4 netfilter/iptables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ipt_ttl_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IPT_TTL_EQ`, `IPT_TTL_NE`, `IPT_TTL_LT`, `IPT_TTL_GT`. Macros expose `_IPT_TTL_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: IP tables module for matching the value of the TTL; (C) 2000 by Harald Welte <laforge@gnumonks.org>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv4/ipt_ttl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6.h

## Purpose

`netfilter_ipv6.h` defines family-specific netfilter hook numbers, priorities, and verdict-related constants for ipv6 packet processing. The file is 51 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/netfilter.h`, `linux/typelimits.h`. Enumerations include `nf_ip6_hook_priorities`. Prominent attribute, command, flag, or constant names include `NF_IP6_PRI_FIRST`, `NF_IP6_PRI_RAW_BEFORE_DEFRAG`, `NF_IP6_PRI_CONNTRACK_DEFRAG`, `NF_IP6_PRI_RAW`, `NF_IP6_PRI_SELINUX_FIRST`, `NF_IP6_PRI_CONNTRACK`, `NF_IP6_PRI_MANGLE`, `NF_IP6_PRI_NAT_DST`, `NF_IP6_PRI_FILTER`, `NF_IP6_PRI_SECURITY`, `NF_IP6_PRI_NAT_SRC`, `NF_IP6_PRI_SELINUX_LAST`, `NF_IP6_PRI_CONNTRACK_HELPER`, `NF_IP6_PRI_LAST`. Macros expose `_UAPI__LINUX_IP6_NETFILTER_H`, `NF_IP6_PRE_ROUTING`, `NF_IP6_LOCAL_IN`, `NF_IP6_FORWARD`, `NF_IP6_LOCAL_OUT`, `NF_IP6_POST_ROUTING`, `NF_IP6_NUMHOOKS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

Packet control flow enters family-specific netfilter hooks in the numeric order defined here. Hook priority constants determine relative ordering of defragmentation, raw, conntrack, mangle, NAT, filter, security, and helper stages in kernel implementation files.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/netfilter.h`, `linux/typelimits.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: IPv6-specific defines for netfilter.; (C)1998 Rusty Russell -- This code is GPL.; (C)1999 David Jeffery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6_tables.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6_tables.h

## Purpose

`ip6_tables.h` defines the IPv6 x_tables table-entry ABI, including rule entry layouts, match/target traversal offsets, counters, table replacement structures, and ioctl/netlink compatibility constants. The file is 272 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv6.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`. Exported structures include `ip6t_ip6`, `in6_addr`, `ip6t_entry`, `xt_counters`, `ip6t_standard`, `xt_standard_target`, `ip6t_error`, `xt_error_target`, `ip6t_icmp`, `ip6t_getinfo`, `ip6t_replace`, `ip6t_get_entries`. Macros expose `_UAPI_IP6_TABLES_H`, `IP6T_FUNCTION_MAXNAMELEN`, `IP6T_TABLE_MAXNAMELEN`, `ip6t_match`, `ip6t_target`, `ip6t_table`, `ip6t_get_revision`, `ip6t_entry_match`, `ip6t_entry_target`, `ip6t_standard_target`, `ip6t_error_target`, `ip6t_counters`, `IP6T_CONTINUE`, `IP6T_RETURN`, `ip6t_tcp`, `ip6t_udp`, `IP6T_TCP_INV_SRCPT`, `IP6T_TCP_INV_DSTPT`, and 37 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

Rule traversal is represented by offsets and sizes: user space builds replacement tables containing entries, matches, targets, counters, and underflow/hook offsets; the kernel validates alignment and offsets, installs the table, and later walks entries in hook order during packet processing. This header defines those ABI layouts rather than the traversal code.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/compiler.h`, `linux/if.h`, `linux/netfilter_ipv6.h`, `linux/netfilter/x_tables.h`, `linux/netfilter/xt_tcpudp.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: 25-Jul-1998 Major changes to allow for ip chain table; 3-Jan-2000 Named tables to allow packet selection for different uses.; Format of an IP6 firewall descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_HL.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_HL.h

## Purpose

`ip6t_HL.h` defines the IPv6 ip6tables extension ABI for `ip6t_HL`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 25 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_HL_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IP6T_HL_SET`, `IP6T_HL_INC`. Macros expose `_IP6T_HL_H`, `IP6T_HL_MAXMODE`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Hop Limit modification module for ip6tables; Maciej Soltysiak <solt@dns.toxicfilms.tv>; Based on HW's TTL module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_HL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_LOG.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_LOG.h

## Purpose

`ip6t_LOG.h` defines the IPv6 ip6tables extension ABI for `ip6t_LOG`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 20 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `ip6t_log_info`. Macros expose `_IP6T_LOG_H`, `IP6T_LOG_TCPSEQ`, `IP6T_LOG_TCPOPT`, `IP6T_LOG_IPOPT`, `IP6T_LOG_UID`, `IP6T_LOG_NFLOG`, `IP6T_LOG_MACDECODE`, `IP6T_LOG_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

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

Source comments call out: make sure not to change this without changing netfilter.h:NF_LOG_* (!).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_LOG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_NPT.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_NPT.h

## Purpose

`ip6t_NPT.h` defines the IPv6 ip6tables extension ABI for `ip6t_NPT`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 17 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `ip6t_npt_tginfo`. Exported unions include `nf_inet_addr`. Macros expose `__NETFILTER_IP6T_NPT`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Used internally by the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_NPT.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_REJECT.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_REJECT.h

## Purpose

`ip6t_REJECT.h` defines the IPv6 ip6tables extension ABI for `ip6t_REJECT`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 23 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_reject_info`. Enumerations include `ip6t_reject_with`. Prominent attribute, command, flag, or constant names include `IP6T_ICMP6_NO_ROUTE`, `IP6T_ICMP6_ADM_PROHIBITED`, `IP6T_ICMP6_NOT_NEIGHBOUR`, `IP6T_ICMP6_ADDR_UNREACH`, `IP6T_ICMP6_PORT_UNREACH`, `IP6T_ICMP6_ECHOREPLY`, `IP6T_TCP_RESET`, `IP6T_ICMP6_POLICY_FAIL`. Macros expose `_IP6T_REJECT_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_REJECT.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ah.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ah.h

## Purpose

`ip6t_ah.h` defines the IPv6 ip6tables extension ABI for `ip6t_ah`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 23 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_ah`. Macros expose `_IP6T_AH_H`, `IP6T_AH_SPI`, `IP6T_AH_LEN`, `IP6T_AH_RES`, `IP6T_AH_INV_SPI`, `IP6T_AH_INV_LEN`, `IP6T_AH_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct ip6t_ah..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_frag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_frag.h

## Purpose

`ip6t_frag.h` defines the IPv6 ip6tables extension ABI for `ip6t_frag`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 26 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_frag`. Macros expose `_IP6T_FRAG_H`, `IP6T_FRAG_IDS`, `IP6T_FRAG_LEN`, `IP6T_FRAG_RES`, `IP6T_FRAG_FST`, `IP6T_FRAG_MF`, `IP6T_FRAG_NMF`, `IP6T_FRAG_INV_IDS`, `IP6T_FRAG_INV_LEN`, `IP6T_FRAG_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct ip6t_frag..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_frag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_hl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_hl.h

## Purpose

`ip6t_hl.h` defines the IPv6 ip6tables extension ABI for `ip6t_hl`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 25 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_hl_info`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `IP6T_HL_EQ`, `IP6T_HL_NE`, `IP6T_HL_LT`, `IP6T_HL_GT`. Macros expose `_IP6T_HL_H`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: ip6tables module for matching the Hop Limit value; Maciej Soltysiak <solt@dns.toxicfilms.tv>; Based on HW's ttl module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_hl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ipv6header.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ipv6header.h

## Purpose

`ip6t_ipv6header.h` defines the IPv6 ip6tables extension ABI for `ip6t_ipv6header`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 29 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_ipv6header_info`. Macros expose `__IPV6HEADER_H`, `MASK_HOPOPTS`, `MASK_DSTOPTS`, `MASK_ROUTING`, `MASK_FRAGMENT`, `MASK_AH`, `MASK_ESP`, `MASK_NONE`, `MASK_PROTO`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: ipv6header match - matches IPv6 packets based; Original idea: Brad Chapman; Rewritten by: Andras Kis-Szabo <kisza@sch.bme.hu>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_ipv6header.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_mh.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_mh.h

## Purpose

`ip6t_mh.h` defines the IPv6 ip6tables extension ABI for `ip6t_mh`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 17 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_mh`. Macros expose `_IP6T_MH_H`, `IP6T_MH_INV_TYPE`, `IP6T_MH_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: MH matching stuff; Values for "invflags" field in struct ip6t_mh..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_mh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_opts.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_opts.h

## Purpose

`ip6t_opts.h` defines the IPv6 ip6tables extension ABI for `ip6t_opts`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 25 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `ip6t_opts`. Macros expose `_IP6T_OPTS_H`, `IP6T_OPTS_OPTSNR`, `IP6T_OPTS_LEN`, `IP6T_OPTS_OPTS`, `IP6T_OPTS_NSTRICT`, `IP6T_OPTS_INV_LEN`, `IP6T_OPTS_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct ip6t_rt..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_opts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_rt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_rt.h

## Purpose

`ip6t_rt.h` defines the IPv6 ip6tables extension ABI for `ip6t_rt`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 34 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/in6.h`. Exported structures include `ip6t_rt`, `in6_addr`. Macros expose `_IP6T_RT_H`, `IP6T_RT_HOPS`, `IP6T_RT_TYP`, `IP6T_RT_SGS`, `IP6T_RT_LEN`, `IP6T_RT_RES`, `IP6T_RT_FST_MASK`, `IP6T_RT_FST`, `IP6T_RT_FST_NSTRICT`, `IP6T_RT_INV_TYP`, `IP6T_RT_INV_SGS`, `IP6T_RT_INV_LEN`, `IP6T_RT_INV_MASK`. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/in6.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "invflags" field in struct ip6t_rt..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_srh.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_srh.h

## Purpose

`ip6t_srh.h` defines the IPv6 ip6tables extension ABI for `ip6t_srh`, used to match or target IPv6 headers, extension headers, or IPv6-specific actions through x_tables. The file is 96 lines and is part of the IPv6 netfilter/ip6tables UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/netfilter.h`. Exported structures include `ip6t_srh`, `ip6t_srh1`, `in6_addr`. Macros expose `_IP6T_SRH_H`, `IP6T_SRH_NEXTHDR`, `IP6T_SRH_LEN_EQ`, `IP6T_SRH_LEN_GT`, `IP6T_SRH_LEN_LT`, `IP6T_SRH_SEGS_EQ`, `IP6T_SRH_SEGS_GT`, `IP6T_SRH_SEGS_LT`, `IP6T_SRH_LAST_EQ`, `IP6T_SRH_LAST_GT`, `IP6T_SRH_LAST_LT`, `IP6T_SRH_TAG`, `IP6T_SRH_PSID`, `IP6T_SRH_NSID`, `IP6T_SRH_LSID`, `IP6T_SRH_MASK`, `IP6T_SRH_INV_NEXTHDR`, `IP6T_SRH_INV_LEN_EQ`, and 13 more. There are no callable functions here; the exported API is the packed rule parameter layout consumed by xtables-compatible user space and kernel modules.

## Control Flow

This UAPI header has no internal execution path. It participates in user/kernel control flow when another subsystem copies, serializes, or validates the constants and structures declared here.

## State and Persistence Behavior

The header stores no state. Its structures may be persisted indirectly in installed rules, nftables objects, conntrack tables, netlink subscribers, or userspace save/restore files. Numeric constants, structure layout, alignment, and maximum lengths are persistent ABI for existing firewall tooling.

## Dependencies and Integration Points

It integrates with netfilter core, nfnetlink/nftables or x_tables, iptables/nftables/ebtables/arptables user-space tools, and kernel match/target/helper modules. It directly includes `linux/types.h`, `linux/netfilter.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; malformed rule blobs can stress offset, size, inversion-flag, mask, and revision validation. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; iptables/nftables/ebtables rule encode-decode round trips; kernel netfilter selftests or packet-path tests for boundary masks, flags, counters, and revision-specific structure sizes; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Values for "mt_flags" field in struct ip6t_srh; Values for "mt_invflags" field in struct ip6t_srh; struct ip6t_srh - SRH match options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netfilter_ipv6/ip6t_srh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netlink.h

## Purpose

`netlink.h` defines the core AF_NETLINK userspace ABI: socket address layout, message headers, flags, attributes, multicast controls, mmap rings, capability flags, and helper macros. The file is 383 lines and is part of the netlink core/diagnostic ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/const.h`, `linux/socket.h`, `linux/types.h`. Exported structures include `sockaddr_nl`, `nlmsghdr`, `nlmsgerr`, `nl_pktinfo`, `nl_mmap_req`, `nl_mmap_hdr`, `nlattr`, `nla_bitfield32`. Enumerations include `nlmsgerr_attrs`, `nl_mmap_status`, `anonymous enum`, `netlink_attribute_type`, `netlink_policy_type_attr`. Prominent attribute, command, flag, or constant names include `NLMSGERR_ATTR_UNUSED`, `NLMSGERR_ATTR_MSG`, `NLMSGERR_ATTR_OFFS`, `NLMSGERR_ATTR_COOKIE`, `NLMSGERR_ATTR_POLICY`, `NLMSGERR_ATTR_MISS_TYPE`, `NLMSGERR_ATTR_MISS_NEST`, `NLMSGERR_ATTR_MAX`, `NL_MMAP_STATUS_UNUSED`, `NL_MMAP_STATUS_RESERVED`, `NL_MMAP_STATUS_VALID`, `NL_MMAP_STATUS_COPY`, `NL_MMAP_STATUS_SKIP`, `NETLINK_UNCONNECTED`, `NETLINK_CONNECTED`, `NL_ATTR_TYPE_INVALID`, `NL_ATTR_TYPE_FLAG`, `NL_ATTR_TYPE_U8`, `NL_ATTR_TYPE_U16`, `NL_ATTR_TYPE_U32`, `NL_ATTR_TYPE_U64`, `NL_ATTR_TYPE_S8`, and 25 more. Macros expose `_UAPI__LINUX_NETLINK_H`, `NETLINK_ROUTE`, `NETLINK_UNUSED`, `NETLINK_USERSOCK`, `NETLINK_FIREWALL`, `NETLINK_SOCK_DIAG`, `NETLINK_NFLOG`, `NETLINK_XFRM`, `NETLINK_SELINUX`, `NETLINK_ISCSI`, `NETLINK_AUDIT`, `NETLINK_FIB_LOOKUP`, `NETLINK_CONNECTOR`, `NETLINK_NETFILTER`, `NETLINK_IP6_FW`, `NETLINK_DNRTMSG`, `NETLINK_KOBJECT_UEVENT`, `NETLINK_GENERIC`, and 61 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

AF_NETLINK control flow is message based: user space writes `nlmsghdr` records with flags and optional attributes, kernel families parse and respond, and multipart or acknowledgement behavior is controlled by message flags. Mmap ring structures define an alternate packetized producer/consumer flow for sockets that use netlink mmap.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with AF_NETLINK sockets, generic netlink, rtnetlink, sock_diag, libmnl/libnl-style parsers, and kernel netlink family implementations. It directly includes `linux/const.h`, `linux/socket.h`, `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: leave room for NETLINK_DM (DM Events); struct nlmsghdr - fixed format metadata header of Netlink messages; @nlmsg_len:   Length of message including header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netlink_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/netlink_diag.h

## Purpose

`netlink_diag.h` defines the netlink socket diagnostic ABI used by sock_diag to request and report AF_NETLINK socket state. The file is 67 lines and is part of the netlink core/diagnostic ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `netlink_diag_req`, `netlink_diag_msg`, `netlink_diag_ring`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `NETLINK_DIAG_MEMINFO`, `NETLINK_DIAG_GROUPS`, `NETLINK_DIAG_RX_RING`, `NETLINK_DIAG_TX_RING`, `NETLINK_DIAG_FLAGS`. Macros expose `_UAPI__NETLINK_DIAG_H__`, `NETLINK_DIAG_MAX`, `NDIAG_PROTO_ALL`, `NDIAG_SHOW_MEMINFO`, `NDIAG_SHOW_GROUPS`, `NDIAG_SHOW_RING_CFG`, `NDIAG_SHOW_FLAGS`, `NDIAG_FLAG_CB_RUNNING`, `NDIAG_FLAG_PKTINFO`, `NDIAG_FLAG_BROADCAST_ERROR`, `NDIAG_FLAG_NO_ENOBUFS`, `NDIAG_FLAG_LISTEN_ALL_NSID`, `NDIAG_FLAG_CAP_ACK`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

sock_diag clients send `netlink_diag_req` filters and receive `netlink_diag_msg` records plus optional memory, group, ring, and flag attributes. The header defines request/report shape only; collection occurs in the netlink diagnostic subsystem.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with AF_NETLINK sockets, generic netlink, rtnetlink, sock_diag, libmnl/libnl-style parsers, and kernel netlink family implementations. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NETLINK_DIAG_NONE, standard nl API requires this attribute!; deprecated since 4.6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/netlink_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nexthop.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nexthop.h

## Purpose

`nexthop.h` defines rtnetlink nexthop object attributes, group flags, resilient group controls, and notifier event constants for shared routing nexthop management. The file is 157 lines and is part of the routing nexthop netlink ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `nhmsg`, `nexthop_grp`. Enumerations include `anonymous enum`. Prominent attribute, command, flag, or constant names include `NEXTHOP_GRP_TYPE_MPATH`, `NEXTHOP_GRP_TYPE_RES`, `NHA_UNSPEC`, `NHA_ID`, `NHA_GROUP`, `NHA_GROUP_TYPE`, `NHA_BLACKHOLE`, `NHA_OIF`, `NHA_GATEWAY`, `NHA_ENCAP_TYPE`, `NHA_ENCAP`, `NHA_GROUPS`, `NHA_MASTER`, `NHA_FDB`, `NHA_RES_GROUP`, `NHA_RES_BUCKET`, `NHA_OP_FLAGS`, `NHA_GROUP_STATS`, `NHA_HW_STATS_ENABLE`, `NHA_HW_STATS_USED`, `NHA_RES_GROUP_UNSPEC`, `NHA_RES_GROUP_PAD`, and 15 more. Macros expose `_UAPI_LINUX_NEXTHOP_H`, `NEXTHOP_GRP_TYPE_MAX`, `NHA_OP_FLAG_DUMP_STATS`, `NHA_OP_FLAG_DUMP_HW_STATS`, `NHA_OP_FLAG_RESP_GRP_RESVD_0`, `NHA_MAX`, `NHA_RES_GROUP_MAX`, `NHA_RES_BUCKET_MAX`, `NHA_GROUP_STATS_MAX`, `NHA_GROUP_STATS_ENTRY_MAX`. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

Routing daemons create, replace, delete, and dump nexthop objects over rtnetlink using the attributes defined here. Group and resilient-group attributes describe selection buckets and idle/unbalanced timers, while notifier types report replace and delete events.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with rtnetlink route management, fib nexthop objects, resilient hashing, routing daemons, and netlink parsers in iproute2-style tooling. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: entry in a nexthop group; default type if not specified; Response OP_FLAGS..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nexthop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfc.h

## Purpose

`nfc.h` defines the NFC generic netlink ABI, including device discovery, target management, LLCP, secure element, firmware, and vendor command attributes. The file is 320 lines and is part of the NFC generic netlink ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`, `linux/socket.h`. Exported structures include `sockaddr_nfc`, `sockaddr_nfc_llcp`. Enumerations include `nfc_commands`, `nfc_attrs`, `nfc_sdp_attr`. Prominent attribute, command, flag, or constant names include `NFC_CMD_UNSPEC`, `NFC_CMD_GET_DEVICE`, `NFC_CMD_DEV_UP`, `NFC_CMD_DEV_DOWN`, `NFC_CMD_DEP_LINK_UP`, `NFC_CMD_DEP_LINK_DOWN`, `NFC_CMD_START_POLL`, `NFC_CMD_STOP_POLL`, `NFC_CMD_GET_TARGET`, `NFC_EVENT_TARGETS_FOUND`, `NFC_EVENT_DEVICE_ADDED`, `NFC_EVENT_DEVICE_REMOVED`, `NFC_EVENT_TARGET_LOST`, `NFC_EVENT_TM_ACTIVATED`, `NFC_EVENT_TM_DEACTIVATED`, `NFC_CMD_LLC_GET_PARAMS`, `NFC_CMD_LLC_SET_PARAMS`, `NFC_CMD_ENABLE_SE`, `NFC_CMD_DISABLE_SE`, `NFC_CMD_LLC_SDREQ`, `NFC_EVENT_LLC_SDRES`, `NFC_CMD_FW_DOWNLOAD`, and 45 more. Macros expose `__LINUX_NFC_H`, `NFC_GENL_NAME`, `NFC_GENL_VERSION`, `NFC_GENL_MCAST_EVENT_NAME`, `NFC_CMD_MAX`, `NFC_ATTR_MAX`, `NFC_SDP_ATTR_MAX`, `NFC_DEVICE_NAME_MAXSIZE`, `NFC_NFCID1_MAXSIZE`, `NFC_NFCID2_MAXSIZE`, `NFC_NFCID3_MAXSIZE`, `NFC_SENSB_RES_MAXSIZE`, `NFC_SENSF_RES_MAXSIZE`, `NFC_ATR_REQ_MAXSIZE`, `NFC_ATR_RES_MAXSIZE`, `NFC_ATR_REQ_GB_MAXSIZE`, `NFC_ATR_RES_GB_MAXSIZE`, `NFC_GB_MAXSIZE`, and 45 more. There are no executable functions; the API surface is message families, commands, attribute IDs, flags, and fixed structures for netlink serialization.

## Control Flow

NFC management flows through generic netlink commands: enumerate devices, start/stop polling, activate/deactivate targets, configure LLCP sockets and secure elements, and exchange vendor or firmware operations. Nested attributes carry device IDs, protocols, target metadata, and payloads.

## State and Persistence Behavior

The header has no storage of its own. State lives in netlink sockets, routing nexthop objects, NFC devices, or diagnostic snapshots maintained by kernel subsystems and userspace daemons. The declared numeric values and structure layouts are persistent UAPI contracts.

## Dependencies and Integration Points

It integrates with the NFC generic netlink family, NFC controller drivers, LLCP, secure element handling, and userspace NFC management daemons. It directly includes `linux/types.h`, `linux/socket.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; nested netlink attribute policies must reject missing, duplicate, overlong, or wrong-endian attributes. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; netlink policy tests covering every command, mandatory attribute, nested attribute, and malformed-length rejection; dump/notification compatibility tests with old and new userspace tools; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Copyright (C) 2011 Instituto Nokia de Tecnologia; Lauro Ramos Venancio <lauro.venancio@openbossa.org>; Aloisio Almeida Jr <aloisio.almeida@openbossa.org>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs.h

## Purpose

`nfs.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 133 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Enumerations include `nfs_stat`, `nfs_ftype`. Prominent attribute, command, flag, or constant names include `NFS_OK`, `NFSERR_PERM`, `NFSERR_NOENT`, `NFSERR_IO`, `NFSERR_NXIO`, `NFSERR_ACCES`, `NFSERR_EXIST`, `NFSERR_XDEV`, `NFSERR_NODEV`, `NFSERR_NOTDIR`, `NFSERR_ISDIR`, `NFSERR_INVAL`, `NFSERR_FBIG`, `NFSERR_NOSPC`, `NFSERR_ROFS`, `NFSERR_MLINK`, `NFSERR_NAMETOOLONG`, `NFSERR_NOTEMPTY`, `NFSERR_DQUOT`, `NFSERR_STALE`, `NFSERR_REMOTE`, `NFSERR_WFLUSH`, and 57 more. Macros expose `_UAPI_LINUX_NFS_H`, `NFS_PROGRAM`, `NFS_PORT`, `NFS_RDMA_PORT`, `NFS_MAXDATA`, `NFS_MAXPATHLEN`, `NFS_MAXNAMLEN`, `NFS_MAXGROUPS`, `NFS_FHSIZE`, `NFS_COOKIESIZE`, `NFS_FIFO_DEV`, `NFSMODE_FMT`, `NFSMODE_DIR`, `NFSMODE_CHR`, `NFSMODE_BLK`, `NFSMODE_REG`, `NFSMODE_LNK`, `NFSMODE_SOCK`, and 5 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NFS protocol definitions; This file contains constants mostly for Version 2 of the protocol,; but also has a couple of NFSv3 bits in (notably the error codes)..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs2.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs2.h

## Purpose

`nfs2.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs2`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 68 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs2_fh`. Enumerations include `nfs2_ftype`. Prominent attribute, command, flag, or constant names include `NF2NON`, `NF2REG`, `NF2DIR`, `NF2BLK`, `NF2CHR`, `NF2LNK`, `NF2SOCK`, `NF2BAD`, `NF2FIFO`. Macros expose `_LINUX_NFS2_H`, `NFS2_PORT`, `NFS2_MAXDATA`, `NFS2_MAXPATHLEN`, `NFS2_MAXNAMLEN`, `NFS2_MAXGROUPS`, `NFS2_FHSIZE`, `NFS2_COOKIESIZE`, `NFS2_FIFO_DEV`, `NFS2MODE_FMT`, `NFS2MODE_DIR`, `NFS2MODE_CHR`, `NFS2MODE_BLK`, `NFS2MODE_REG`, `NFS2MODE_LNK`, `NFS2MODE_SOCK`, `NFS2MODE_FIFO`, `NFS2_VERSION`, and 18 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NFS protocol definitions; This file contains constants for Version 2 of the protocol.; NFSv2 file types - beware, these are not the same in NFSv3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs3.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs3.h

## Purpose

`nfs3.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs3`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 104 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs3_fh`. Enumerations include `nfs3_createmode`, `nfs3_ftype`, `nfs3_time_how`. Prominent attribute, command, flag, or constant names include `NFS3_CREATE_UNCHECKED`, `NFS3_CREATE_GUARDED`, `NFS3_CREATE_EXCLUSIVE`, `NF3NON`, `NF3REG`, `NF3DIR`, `NF3BLK`, `NF3CHR`, `NF3LNK`, `NF3SOCK`, `NF3FIFO`, `NF3BAD`, `DONT_CHANGE`, `SET_TO_SERVER_TIME`, `SET_TO_CLIENT_TIME`. Macros expose `_UAPI_LINUX_NFS3_H`, `NFS3_PORT`, `NFS3_MAXDATA`, `NFS3_MAXPATHLEN`, `NFS3_MAXNAMLEN`, `NFS3_MAXGROUPS`, `NFS3_FHSIZE`, `NFS3_COOKIESIZE`, `NFS3_CREATEVERFSIZE`, `NFS3_COOKIEVERFSIZE`, `NFS3_WRITEVERFSIZE`, `NFS3_FIFO_DEV`, `NFS3MODE_FMT`, `NFS3MODE_DIR`, `NFS3MODE_CHR`, `NFS3MODE_BLK`, `NFS3MODE_REG`, `NFS3MODE_LNK`, and 40 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NFSv3 protocol definitions; Flags for access() call; Flags for create mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs4.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs4.h

## Purpose

`nfs4.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs4`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 188 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Macros expose `_UAPI_LINUX_NFS4_H`, `NFS4_BITMAP_SIZE`, `NFS4_VERIFIER_SIZE`, `NFS4_STATEID_SEQID_SIZE`, `NFS4_STATEID_OTHER_SIZE`, `NFS4_STATEID_SIZE`, `NFS4_FHSIZE`, `NFS4_MAXPATHLEN`, `NFS4_MAXNAMLEN`, `NFS4_OPAQUE_LIMIT`, `NFS4_MAX_SESSIONID_LEN`, `NFS4_ACCESS_READ`, `NFS4_ACCESS_LOOKUP`, `NFS4_ACCESS_MODIFY`, `NFS4_ACCESS_EXTEND`, `NFS4_ACCESS_DELETE`, `NFS4_ACCESS_EXECUTE`, `NFS4_ACCESS_XAREAD`, and 114 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: include/linux/nfs4.h; NFSv4 protocol definitions.; Copyright (c) 2002 The Regents of the University of Michigan..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs4_mount.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs4_mount.h

## Purpose

`nfs4_mount.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs4_mount`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 72 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs_string`, `nfs4_mount_data`, `sockaddr`. Macros expose `_LINUX_NFS4_MOUNT_H`, `NFS4_MOUNT_VERSION`, `NFS4_MOUNT_SOFT`, `NFS4_MOUNT_INTR`, `NFS4_MOUNT_NOCTO`, `NFS4_MOUNT_NOAC`, `NFS4_MOUNT_STRICTLOCK`, `NFS4_MOUNT_UNSHARED`, `NFS4_MOUNT_FLAGMASK`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs4_mount.h; Copyright (C) 2002  Trond Myklebust; structure passed from user-space to kernel-space during an nfsv4 mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs4_mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_fs.h

## Purpose

`nfs_fs.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_fs`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 63 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/magic.h`. Macros expose `_UAPI_LINUX_NFS_FS_H`, `NFS_DEF_UDP_TIMEO`, `NFS_DEF_UDP_RETRANS`, `NFS_DEF_TCP_TIMEO`, `NFS_DEF_TCP_RETRANS`, `NFS_MAX_UDP_TIMEOUT`, `NFS_MAX_TCP_TIMEOUT`, `NFS_DEF_ACREGMIN`, `NFS_DEF_ACREGMAX`, `NFS_DEF_ACDIRMIN`, `NFS_DEF_ACDIRMAX`, `FLUSH_SYNC`, `FLUSH_STABLE`, `FLUSH_LOWPRI`, `FLUSH_HIGHPRI`, `FLUSH_COND_STABLE`, `NFSDBG_VFS`, `NFSDBG_DIRCACHE`, and 15 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/magic.h`.

## Risks and Edge Cases

Key risks are maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs_fs.h; Copyright (C) 1992  Rick Sladkey; OS-specific nfs filesystem definitions and declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_idmap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_idmap.h

## Purpose

`nfs_idmap.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_idmap`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 65 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `idmap_msg`. Macros expose `_UAPINFS_IDMAP_H`, `IDMAP_NAMESZ`, `IDMAP_TYPE_USER`, `IDMAP_TYPE_GROUP`, `IDMAP_CONV_IDTONAME`, `IDMAP_CONV_NAMETOID`, `IDMAP_STATUS_INVALIDMSG`, `IDMAP_STATUS_AGAIN`, `IDMAP_STATUS_LOOKUPFAIL`, `IDMAP_STATUS_SUCCESS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: include/uapi/linux/nfs_idmap.h; UID and GID to name mapping for clients.; Copyright (c) 2002 The Regents of the University of Michigan..
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_mount.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_mount.h

## Purpose

`nfs_mount.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_mount`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 69 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/in.h`, `linux/nfs.h`, `linux/nfs2.h`, `linux/nfs3.h`. Exported structures include `nfs_mount_data`, `nfs2_fh`, `sockaddr_in`, `nfs3_fh`. Macros expose `_LINUX_NFS_MOUNT_H`, `NFS_MOUNT_VERSION`, `NFS_MAX_CONTEXT_LEN`, `NFS_MOUNT_SOFT`, `NFS_MOUNT_INTR`, `NFS_MOUNT_SECURE`, `NFS_MOUNT_POSIX`, `NFS_MOUNT_NOCTO`, `NFS_MOUNT_NOAC`, `NFS_MOUNT_TCP`, `NFS_MOUNT_VER3`, `NFS_MOUNT_KERBEROS`, `NFS_MOUNT_NONLM`, `NFS_MOUNT_BROKEN_SUID`, `NFS_MOUNT_NOACL`, `NFS_MOUNT_STRICTLOCK`, `NFS_MOUNT_SECFLAVOUR`, `NFS_MOUNT_NORDIRPLUS`, and 2 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/in.h`, `linux/nfs.h`, `linux/nfs2.h`, `linux/nfs3.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs_mount.h; Copyright (C) 1992  Rick Sladkey; structure passed from user-space to kernel-space during an nfs mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfs_mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsacl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfsacl.h

## Purpose

`nfsacl.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfsacl`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 33 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Macros expose `_UAPI__LINUX_NFSACL_H`, `NFS_ACL_PROGRAM`, `ACLPROC2_NULL`, `ACLPROC2_GETACL`, `ACLPROC2_SETACL`, `ACLPROC2_GETATTR`, `ACLPROC2_ACCESS`, `ACLPROC3_NULL`, `ACLPROC3_GETACL`, `ACLPROC3_SETACL`, `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`, `NFS_ACL_MASK`, `NFS_ACL_DEFAULT`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: File: linux/nfsacl.h; (C) 2003 Andreas Gruenbacher <agruen@suse.de>; Flags for the getacl/setacl mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/cld.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/cld.h

## Purpose

`cld.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 97 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `cld_name`, `cld_princhash`, `cld_clntinfo`, `cld_msg`, `cld_msg_v2`, `cld_msg_hdr`. Enumerations include `cld_command`. Macros expose `_NFSD_CLD_H`, `CLD_UPCALL_VERSION`, `NFS4_OPAQUE_LIMIT`, `SHA256_DIGEST_SIZE`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Upcall description for nfsdcld communication; Copyright (c) 2012 Red Hat, Inc.; Author(s): Jeff Layton <jlayton@redhat.com>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/cld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/debug.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/debug.h

## Purpose

`debug.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 34 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/sunrpc/debug.h`. Macros expose `_UAPILINUX_NFSD_DEBUG_H`, `NFSDDBG_SOCK`, `NFSDDBG_FH`, `NFSDDBG_EXPORT`, `NFSDDBG_SVC`, `NFSDDBG_PROC`, `NFSDDBG_FILEOP`, `NFSDDBG_AUTH`, `NFSDDBG_REPCACHE`, `NFSDDBG_XDR`, `NFSDDBG_LOCKD`, `NFSDDBG_PNFS`, `NFSDDBG_ALL`, `NFSDDBG_NOCHANGE`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/sunrpc/debug.h`.

## Risks and Edge Cases

Key risks are wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfsd/debug.h; Debugging-related stuff for nfsd; Copyright (C) 1995 Olaf Kirch <okir@monad.swb.de>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/export.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/export.h

## Purpose

`export.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 79 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Macros expose `_UAPINFSD_EXPORT_H`, `NFSCLNT_IDMAX`, `NFSCLNT_ADDRMAX`, `NFSCLNT_KEYMAX`, `NFSEXP_READONLY`, `NFSEXP_INSECURE_PORT`, `NFSEXP_ROOTSQUASH`, `NFSEXP_ALLSQUASH`, `NFSEXP_ASYNC`, `NFSEXP_GATHERED_WRITES`, `NFSEXP_NOREADDIRPLUS`, `NFSEXP_SECURITY_LABEL`, `NFSEXP_SIGN_FH`, `NFSEXP_NOHIDE`, `NFSEXP_NOSUBTREECHECK`, `NFSEXP_NOAUTHNLM`, `NFSEXP_MSNFS`, `NFSEXP_FSID`, and 11 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: include/linux/nfsd/export.h; Public declarations for NFS exports. The definitions for the; syscall interface are in nfsctl.h.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/stats.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/stats.h

## Purpose

`stats.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 18 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/nfs4.h`. Macros expose `_UAPILINUX_NFSD_STATS_H`, `NFSD_USAGE_WRAP`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/nfs4.h`.

## Risks and Edge Cases

Key risks are wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfsd/stats.h; Statistics for NFS server.; Copyright (C) 1995, 1996 Olaf Kirch <okir@monad.swb.de>.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/stats.h -->
