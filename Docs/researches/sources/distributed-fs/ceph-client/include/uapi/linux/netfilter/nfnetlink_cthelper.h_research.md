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
