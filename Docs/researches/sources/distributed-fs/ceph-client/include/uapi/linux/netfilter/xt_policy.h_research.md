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
