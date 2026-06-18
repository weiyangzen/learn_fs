# sources/distributed-fs/ceph-client/net/ipv6/seg6_iptunnel.c

## Purpose

`seg6_iptunnel.c` implements SRv6 lightweight tunnel encapsulation for route nexthops. It inserts SRHs inline or encapsulates IPv4, IPv6, or Ethernet payloads inside an outer IPv6/SRH header, supports reduced encapsulation modes, optional per-route tunnel source addresses, HMAC population, dst caching, and netfilter hooks around lwtunnel processing.

## Important APIs, Types, And Functions

The private lwtunnel state is `struct seg6_lwt`, containing input/output `dst_cache` objects, a per-route `tunsrc`, and flexible `struct seg6_iptunnel_encap` data. The route-facing ops are `seg6_build_state()`, `seg6_destroy_state()`, `seg6_input()`, `seg6_output()`, `seg6_fill_encap_info()`, `seg6_encap_nlsize()`, and `seg6_encap_cmp()`, collected in `seg6_iptun_ops`. Registration is via `seg6_iptunnel_init()` and `seg6_iptunnel_exit()`.

Packet rewrite helpers are `__seg6_do_srh_encap()`, `seg6_do_srh_encap()`, `seg6_do_srh_encap_red()`, `__seg6_do_srh_inline()`, exported `seg6_do_srh_inline()`, and dispatcher `seg6_do_srh()`. Source and flow metadata helpers include `seg6_lwt_headroom()`, `set_tun_src()`, and `seg6_make_flowlabel()`.

## Control Flow

`seg6_build_state()` parses nested `SEG6_IPTUNNEL_SRH` and optional `SEG6_IPTUNNEL_SRC`, accepts AF_INET/AF_INET6 depending on mode, validates mode constraints, validates the SRH with `seg6_validate_srh(..., reduced=false)`, allocates state, initializes two dst caches, copies tunnel info, validates per-route source address, sets lwtunnel type/redirect flags/headroom, and returns the state.

`seg6_do_srh()` dispatches by mode. Inline mode requires an IPv6 skb and inserts the SRH after the existing IPv6 header. ENCAP/ENCAP_RED handles offloads, accepts IPv4 or IPv6 payloads, chooses `IPPROTO_IPV6` or `IPPROTO_IPIP`, pushes an outer IPv6 header and SRH, and changes skb protocol to IPv6. L2ENCAP modes require a valid MAC header, copy L2 bytes into the inner payload, and use `IPPROTO_ETHERNET`.

Full encapsulation pushes an outer IPv6 header plus SRH, inherits traffic class/hop-limit from IPv6 inner packets or initializes IPv6 control block for non-IPv6 payloads, sets the outer destination to the first segment, selects source by per-route source, per-net source, or dynamic address selection, optionally computes HMAC, fixes payload length and checksum. Reduced encapsulation omits the first SID from the SRH, and for one-SID/no-HMAC cases can skip the SRH entirely and put the SID directly in the outer destination.

Input and output paths both use separate dst caches. If a cache miss occurs, output builds a `flowi6` and calls `ip6_route_output()`, while input calls `ip6_route_input()` and forces a dst reference from the no-ref result. Both avoid caching when the resulting dst uses the same lwtstate, grow link-layer headroom as needed, install the new dst, and call `dst_input()` or `dst_output()`. When lwtunnel netfilter hooks are enabled, pre/post routing and local-out hooks wrap processing.

## State And Persistence Behavior

Route-attached lwtunnel state persists the SRH, mode, optional tunnel source, and caches until route teardown. Two caches are maintained so input and output route resolutions do not alias. Per-route source overrides per-net SRv6 `tun_src`, and dynamic source selection is fallback only. HMAC bytes are generated per packet and not stored in state. The module registers one lwtunnel encap type and owns no additional global mutable state.

## Dependencies And Integration Points

The file integrates with lwtunnel route attributes from `linux/seg6_iptunnel.h`, SRH validation and per-net data from `seg6.c`, optional HMAC from `seg6_hmac.c`, IPv6 route lookup, dst cache, offload helpers, netfilter lwtunnel static key, address selection, and lightweight tunnel headroom accounting used by IPv6 route MTU calculations.

## Risks And Edge Cases

High-risk areas are skb headroom manipulation, reduced SRH length calculations, HMAC recomputation after reduced-header edits, dst cache reference loops, offload handling, and protocol transitions for IPv4/L2 payloads. Inline mode is IPv6-only and rejects other protocols. Per-route tunnel source rejects any, multicast, and loopback addresses, but dynamic/per-net source still depends on address-selection success. Reduced mode can skip the SRH only in the one-SID/no-HMAC case; future TLVs or flags would need to revisit that assumption, as noted by the source comment.

## Test Signals

Tests should cover all five modes, IPv4 and IPv6 encap, L2 encap with and without MAC headers, reduced one-SID skip behavior, reduced multi-SID TLV copying, HMAC TLV population, per-route versus per-net tunnel source selection, invalid SRH/mode/source rejection, dst cache hit/miss and loop avoidance, netfilter hook enabled paths, GSO/offload handling, and packet capture validation of outer header, next-header, destination SID, payload length, and checksum state.
