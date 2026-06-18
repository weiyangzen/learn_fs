# sources/distributed-fs/ceph-client/net/ipv6/rpl_iptunnel.c

## Purpose

`rpl_iptunnel.c` registers the RPL lightweight tunnel encapsulation type and implements packet input/output handling that inserts an RPL Source Routing Header inline into IPv6 packets. It lets routes carry an RPL SRH through `LWTUNNEL_ENCAP_RPL`.

## Important APIs, Types, And Functions

The private tunnel state is `struct rpl_lwt`, containing a `dst_cache` and flexible `struct rpl_iptunnel_encap` SRH storage. Accessors `rpl_lwt_lwtunnel()` and `rpl_encap_lwtunnel()` decode `lwtunnel_state->data`.

Netlink/lwtunnel operations are implemented by `rpl_build_state()`, `rpl_destroy_state()`, `rpl_output()`, `rpl_input()`, `rpl_fill_encap_info()`, `rpl_encap_nlsize()`, and `rpl_encap_cmp()`, collected in `rpl_ops`. Module-level registration is through `rpl_init()` and `rpl_exit()`. Packet rewriting is centered on `rpl_do_srh_inline()` and `rpl_do_srh()`.

## Control Flow

`rpl_build_state()` accepts only AF_INET6 routes, parses nested `RPL_IPTUNNEL_SRH`, validates the SRH, allocates lwtunnel state, initializes a dst cache, copies the SRH, and marks the state for input and output redirects. Validation requires the byte length to match `hdrlen`, at least one segment, `segments_left * sizeof(in6_addr)` to match the segment payload length, no pre-existing RPL compression, no loop per `ipv6_chk_rpl_srh_loop()`, and a non-multicast final segment.

On output, `rpl_output()` gets a cached dst, calls `rpl_do_srh()`, and if no cached dst exists performs a fresh `ip6_route_output()` for the rewritten destination. It avoids caching if the new dst has the same lwtstate, preventing reference loops. It then swaps the skb dst and calls `dst_output()`. Input is similar but calls `ip6_route_input()`, forces a dst reference from the no-ref route, caches when safe, and hands the packet to `dst_input()`.

`rpl_do_srh_inline()` copies the old IPv6 header, builds an intermediate uncompressed RPL segment list by shifting configured segments and appending the original destination, compresses it relative to the first configured segment, grows headroom, rewrites the IPv6 header and routing header, sets `hdr->daddr` to the first segment, updates `payload_len`, transport header, and checksum state, and frees the temporary buffer.

## State And Persistence Behavior

Each lwtunnel state persists a validated SRH and one `dst_cache`. State is attached to routes and destroyed with `dst_cache_destroy()`. Cached routes are soft state and are deliberately not installed if they would form an lwtstate loop. The file does not own global state beyond registering/unregistering the encapsulation ops.

## Dependencies And Integration Points

It integrates with netlink attributes from `linux/rpl_iptunnel.h`, IPv6 route lookup/output/input, `dst_cache`, the lwtunnel core, and the RPL compression helpers in `rpl.c`. It is selected by route nexthop lightweight tunnel attributes and runs in both forwarding/input and local output paths depending on route use.

## Risks And Edge Cases

The main packet risks are malformed SRH lengths, insufficient headroom, checksum adjustment mistakes, and dst reference loops. Validation rejects compressed user-provided headers because this code expects to control compression during packet rewrite. The temporary buffer allocation size depends on `segments_left`; validation must ensure segment length and `segments_left` remain consistent. Input routing must force a reference after `ip6_route_input()` because that route path installs a no-ref dst.

## Test Signals

Tests should add IPv6 routes with `encap rpl` SRHs, verify invalid SRHs are rejected, send packets through input and output lwt paths, inspect resulting routing headers and destination rewrite, and confirm repeated traffic uses cache without dst loops. Fault-injection or KASAN tests around headroom growth and allocation failure would exercise the drop paths.
