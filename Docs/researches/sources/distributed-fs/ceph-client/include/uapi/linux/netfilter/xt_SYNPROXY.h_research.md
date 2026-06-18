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
