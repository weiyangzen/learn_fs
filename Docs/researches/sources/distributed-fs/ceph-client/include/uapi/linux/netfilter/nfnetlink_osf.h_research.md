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
