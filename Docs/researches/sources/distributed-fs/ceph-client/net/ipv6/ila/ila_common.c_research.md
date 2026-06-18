# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_common.c

## Purpose
Provides common ILA locator update and checksum-adjustment logic shared by lwtunnel and xlat paths. It changes the destination locator portion of an IPv6 address while preserving or updating transport checksums according to the configured ILA checksum mode.

## Important APIs, Types, and Functions
Exports `ila_init_saved_csum()` and `ila_update_ipv6_locator()`. Internal helpers include `get_csum_diff_iaddr()`, `get_csum_diff()`, `ila_csum_do_neutral_fmt()`, `ila_csum_do_neutral_nofmt()`, and `ila_csum_adjust_transport()`.

## Control Flow
`ila_init_saved_csum()` precomputes a checksum delta when a fixed `locator_match` is known. `ila_update_ipv6_locator()` inspects `p->csum_mode`: it can update TCP/UDP/ICMPv6 checksums incrementally, apply formatted checksum-neutral mapping while toggling the C-bit, apply unformatted neutral mapping, or do nothing. After checksum handling, it writes the new locator into the IPv6 destination address.

## State and Persistence
State is carried in `struct ila_params`, especially precomputed `csum_diff`, locator values, and checksum mode. Packet mutation is in-place on the skb IPv6 destination and optional transport checksum field. No persistent storage exists.

## Dependencies and Integration Points
Depends on skb pull checks, TCP/UDP/ICMPv6 header definitions, incremental checksum helpers, and UAPI checksum mode constants. Called by `ila_lwt.c` and the xlat implementation.

## Risks and Test Signals
Risks include failing to parse extension headers before transport checksums, UDP zero checksum handling, checksum-neutral bit misuse, locator-match vs dynamic diff mistakes, and partial checksum state interactions. Test signals include TCP/UDP/ICMPv6 translations in each checksum mode, CHECKSUM_PARTIAL UDP packets, SIR-to-ILA and ILA-to-SIR neutral-map directions, malformed short transport headers, and checksum verification after locator replacement.
