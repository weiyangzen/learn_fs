# sources/distributed-fs/ceph-client/net/ipv6/ioam6_iptunnel.c

Purpose: implements the IOAM6 lightweight tunnel encapsulation type. It builds lwtunnel state from netlink route attributes, inserts IOAM Hop-by-Hop options either inline or by IPv6-in-IPv6 encapsulation, fills trace data, caches routes, and serializes state back to netlink.

Important APIs, types, and functions: `struct ioam6_lwt`, `struct ioam6_lwt_encap`, `ioam6_build_state()`, `ioam6_output()`, `ioam6_destroy_state()`, `ioam6_fill_encap_info()`, `ioam6_encap_cmp()`, `ioam6_iptunnel_init()`, and `ioam6_iptunnel_exit()`.

Control flow: build-state parses frequency `k/n`, mode, optional source, required destination for non-inline modes, and a trace header. It validates trace type/remlen, allocates lwtunnel state with aligned trace storage, initializes a dst cache and a fake `null_dst`, and constructs the Hop-by-Hop IOAM option blob. Output applies frequency sampling, retrieves or resolves a cached route, performs inline insertion if no Hop-by-Hop header already exists or encap insertion for tunnel/auto modes, fills IOAM data through `ioam6_do_fill()`, then either redirects to the new dst output or calls the original output to avoid lwtunnel reentry.

State and persistence: route-attached lwtunnel state persists with the route. It contains frequency counters, route cache, mode, tunnel endpoints, and immutable tunnel option template. `pkt_cnt` is atomic and per-state. The fake `null_dst` marks the case where transformed packets still use the original route.

Dependencies and integration points: integrates with lwtunnel encap ops, IPv6 route output, dst_cache, skb headroom/csum helpers, IOAM namespace lookup and trace fill, route netlink attribute validation, and IPv6 source address selection.

Risks: inline insertion refuses packets that already have Hop-by-Hop headers, so policy must expect skipped insertion. The fake dst-cache sentinel relies on careful refcount balancing and must not escape into normal routing. Frequency `pkt_cnt % n` behavior depends on validation preventing zero. Trace validation rejects undefined bits but future IOAM bits require updates.

Test signals: route add/dump/delete with IOAM lwt attributes, inline/encap/auto mode output, k-over-n sampling, route-cache invalidation, same-dst sentinel behavior, source selection with and without explicit source, insufficient headroom failure paths, and trace overflow cases.
