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
