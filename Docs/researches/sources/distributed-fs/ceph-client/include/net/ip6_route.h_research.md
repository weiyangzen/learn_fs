# sources/distributed-fs/ceph-client/include/net/ip6_route.h

Purpose: Declares IPv6 route lookup, route mutation, PMTU, redirect, default-router, and dst-cache helpers used by IPv6 input/output paths and socket code.

Important APIs/types/functions: `route_info` represents RA route information options. `RT6_LOOKUP_F_*` flags steer strict interface lookup, reachability, source-address preferences, link-state handling, and no-ref dst behavior. APIs include `ip6_route_input`, `ip6_route_input_lookup`, `ip6_route_output_flags`, `ip6_route_lookup`, `ip6_pol_route`, `ip6_route_add`, `ip6_ins_rt`, `ip6_del_rt`, `rt6_lookup`, `rt6_multipath_hash`, default-router helpers, PMTU/redirect handlers, route dump helpers, device sync functions, and `ip6_fragment`.

Control flow: Output callers build a `flowi6`, look up a dst, optionally store it in socket state through `ip6_dst_store`/`ip6_sk_dst_store_flow`, and use route cookies to detect invalidation. Input lookup and policy lookup feed `fib6_result`, then route selection and nexthop selection decide the dst. PMTU and redirect paths update exceptions under route state.

State and persistence: The header manipulates in-memory dst cache, socket cached destination cookies, route exceptions, MTU metrics, default-router entries, and uncached route lists. `ip6_route_get_saddr` may prefer route prefsrc if it belongs to the same L3 master, otherwise it asks address configuration for a source address.

Dependencies/integration: Integrates `ip6_fib.h`, `addrconf`, sockets, lwtunnel headroom, nexthop objects, L3 master devices, netlink dumps, neighbour lookup, and IPv6 fragmentation.

Risks: `RT6_LOOKUP_F_DST_NOREF` must match release behavior in `ip6_rt_put_flags`; PMTU calculations must subtract lwtunnel headroom; source selection can be wrong across VRFs; RA/default-router paths need lifetime and preference coverage. Test signals include route cache invalidation after route updates, socket dst reuse, VRF source selection, IPv6 forwarding MTU, PMTU exceptions, redirects, and IPv6-disabled fallback returning `-EAFNOSUPPORT`.
