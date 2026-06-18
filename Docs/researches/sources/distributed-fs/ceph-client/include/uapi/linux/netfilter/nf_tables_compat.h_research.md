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
