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
