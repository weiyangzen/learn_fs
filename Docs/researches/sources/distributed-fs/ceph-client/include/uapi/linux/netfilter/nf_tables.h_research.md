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
