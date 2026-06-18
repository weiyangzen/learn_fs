# sources/distributed-fs/ceph-client/net/ipv6/exthdrs.c

## Purpose
Implements IPv6 extension-header receive handlers and outbound option construction. It parses hop-by-hop and destination TLVs, handles router alert, IOAM, jumbogram, CALIPSO, Mobile IPv6 HAO, routing headers including SRv6 and RPL source routing, registers inbound protocol handlers, and provides exported helpers for building and renewing transmit options.

## Important APIs, Types, and Functions
Receive-side functions include `ip6_parse_tlv()`, `ipv6_parse_hopopts()`, `ipv6_destopt_rcv()`, `ipv6_rthdr_rcv()`, `ipv6_srh_rcv()`, `ipv6_rpl_srh_rcv()`, `ipv6_hop_ra()`, `ipv6_hop_ioam()`, `ipv6_hop_jumbo()`, and `ipv6_hop_calipso()`. Registration uses `ipv6_exthdrs_init()`/`ipv6_exthdrs_exit()`. Outbound helpers include `ipv6_push_nfrag_opts()`, `ipv6_push_frag_opts()`, `ipv6_dup_options()`, `ipv6_renew_options()`, `__ipv6_fixup_options()`, and `__fl6_update_dst()`.

## Control Flow
Hop/destination parsing pulls enough header bytes, enforces sysctl length/count limits, validates padding, and dispatches known TLVs while applying unknown-option action bits. Routing-header processing validates destination and source-route policy, handles SRH/RPL segment advancement with route relookup and loopback recursion, decapsulates inner IPv4/IPv6 when segments are exhausted, and records offsets in `IP6CB`. Outbound helpers push headers in reverse order for TCP-style output, copy or replace socket options into a new `ipv6_txoptions`, and adjust flow destination when source-routing is configured.

## State and Persistence
Packet state is recorded in `struct inet6_skb_parm` (`IP6CB`) flags and offsets. Socket transmit options are refcounted `struct ipv6_txoptions` allocated from socket memory. Runtime behavior depends on per-net/per-device sysctls for option limits and SRv6/RPL/IOAM enablement.

## Dependencies and Integration Points
Depends on IPv6 protocol registration, addrconf, routing, ICMPv6 parameter problems, CALIPSO validation, IOAM namespaces/events, SRv6 HMAC, RPL compression helpers, XFRM Mobile IPv6 checks, and skb checksum adjustment. Datagram and routing code consume the exported option helpers.

## Risks and Test Signals
Risks include malformed TLV length/padding handling, option-count DoS limits, cloned skb mutation, checksum updates for SRH, RPL compression arithmetic, route-loop recursion, and source-routing policy bypass. Test signals include hop/destination fuzzing, sysctl max option limits, unknown TLV action bits, jumbogram validation, CALIPSO/IOAM/SRv6/RPL packets, MIPv6 HAO, outbound option replacement, and cmsg visibility of parsed offsets.
