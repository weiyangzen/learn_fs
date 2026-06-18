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
