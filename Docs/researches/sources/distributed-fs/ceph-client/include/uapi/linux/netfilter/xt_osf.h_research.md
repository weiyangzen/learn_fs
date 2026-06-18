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
