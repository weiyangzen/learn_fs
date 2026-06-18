# sources/distributed-fs/ceph-client/net/ipv4/route.c

## Purpose

This file is the IPv4 route resolution and route-dst implementation for the kernel networking stack. It builds and validates `struct rtable` destinations for input, output, multicast, broadcast, local, unreachable, blackhole, redirect, PMTU, and netlink `RTM_GETROUTE` paths. It also owns IPv4 route-related dst operations, route cache statistics proc files, per-next-hop exception state for redirects/PMTU, IP ID generation, multipath hash selection, per-net route sysctls, route generation IDs, and inet peer allocation.

## Important APIs, Types, and Functions

- `ipv4_dst_ops` and `ipv4_dst_blackhole_ops`: `struct dst_ops` instances for normal IPv4 dst entries and blackhole dst entries. They provide check, MTU, MSS, PMTU update, redirect, neighbour lookup, and destroy hooks.
- `ip_tos2prio`: exported DS/TOS-to-traffic-priority table.
- `rt_cache_stat`: per-CPU route statistics exposed through proc when `CONFIG_PROC_FS` is enabled.
- `__ip_select_ident()`: exported IP identification generator using per-net siphash keys and global randomized id buckets.
- `struct fib_nh_exception` helpers: `update_or_create_fnhe()`, `find_exception()`, `rt_bind_exception()`, `ip_del_fnhe()`, and `fnhe_flush_routes()` maintain per-nexthop exceptions for redirect gateway and path MTU.
- Redirect and PMTU APIs: `ip_rt_send_redirect()`, `ipv4_redirect()`, `ipv4_sk_redirect()`, `ipv4_update_pmtu()`, `ipv4_sk_update_pmtu()`, and internal `__ip_do_redirect()` / `__ip_rt_update_pmtu()`.
- Route lookup APIs: `ip_route_input_noref()`, `ip_route_use_hint()`, `ip_route_output_key_hash()`, `ip_route_output_key_hash_rcu()`, `ip_route_output_flow()`, `rt_dst_alloc()`, `rt_dst_clone()`, and `ipv4_blackhole_route()`.
- Multipath support under `CONFIG_IP_ROUTE_MULTIPATH`: `fib_multipath_hash()` and helpers for L3, L4, inner, outer, and custom hash field policies.
- Netlink route query support: `inet_rtm_valid_getroute_req()`, `inet_rtm_getroute_build_skb()`, `inet_rtm_getroute()`, `rt_fill_info()`, and `fib_dump_info_fnhe()`.
- Sysctl and init hooks: `sysctl_route_net_init()`, `netns_ip_rt_init()`, `rt_genid_init()`, `ipv4_inetpeer_init()`, `ip_rt_init()`, and `ip_static_sysctl_init()`.

## Control Flow

Input routing enters through `ip_route_input_noref()`, takes RCU, and calls `ip_route_input_rcu()`. Multicast destinations are handled first through `ip_route_input_mc()` after IGMP membership / multicast-forwarding checks. Other packets go to `ip_route_input_slow()`, which rejects martian source/destination cases, builds a `flowi4`, optionally does early flow dissection, performs `fib_lookup()`, handles broadcast/local/unreachable cases, and creates or reuses an input `rtable`. Forwarded unicast traffic is routed by `ip_mkroute_input()` and `__mkroute_input()`, which validate source addresses, determine redirect eligibility, bind any nexthop exception, cache the route if safe, and attach the dst to the skb.

Output routing enters through `ip_route_output_key_hash()` or the RCU variant. The function normalizes source, destination, output interface, loopback, multicast, broadcast, and local-route cases before doing `fib_lookup()` and `fib_select_path()`. `__mkroute_output()` then validates the egress device, handles route-localnet restrictions, recognizes broadcast/multicast/local special cases, checks per-nexthop or per-CPU cached routes, allocates an `rtable`, sets output/input functions, binds lwtunnel state, and caches or marks the route uncached.

Redirect handling starts with dst callback `ip_do_redirect()` or exported wrappers `ipv4_redirect()` and `ipv4_sk_redirect()`. They build a `flowi4`, validate the ICMP redirect code, old gateway, device policy, secure redirects, on-link constraints, and neighbour state. Valid redirects update per-nexthop exception gateway state and can kill the current dst. `ip_rt_send_redirect()` sends outbound ICMP redirects with inet-peer rate/backoff state.

PMTU updates use the same per-nexthop exception mechanism. `ip_rt_update_pmtu()` and socket-specific wrappers build a flow key, route if needed, clamp below the namespace minimum PMTU when configured, and update one or all multipath nexthop exceptions. Socket update flow also deals with locked sockets, stale dsts, xfrm dst paths, and replacing `sk_dst_cache` when a new route is needed.

Netlink `RTM_GETROUTE` builds a synthetic IPv4 skb so the normal input or output route lookup engine can be reused. Strict requests are validated by `inet_rtm_valid_getroute_req()`. The response is either cloned route information from `rt_fill_info()` or an exact FIB match through `fib_dump_info()` when `RTM_F_FIB_MATCH` is requested.

Initialization in `ip_rt_init()` allocates IP ID hash storage, initializes uncached route lists, allocates route accounting if configured, creates dst caches, initializes devinet/FIB/XFRM/proc/netlink/sysctl/pernet components, and registers route generation and inet peer per-net operations.

## State and Persistence Behavior

Route state is mostly in memory and scoped by dst entries, FIB nexthops, and network namespaces. Cached input routes live in `nhc_rth_input`; cached output routes live in per-CPU `nhc_pcpu_rth_output`; routes that fail cache insertion or have no FIB info are linked into per-CPU `rt_uncached_list`. `rt_genid` invalidates dsts after route cache flushes, and `fnhe_genid` invalidates nexthop exceptions. Per-nexthop exceptions persist redirect gateway, PMTU, lock state, expiration, and cached input/output dst pointers until timeout, generation change, deletion, or RCU free.

The file also owns global randomized IP ID bucket arrays (`ip_idents`, `ip_tstamps`) and per-net siphash keys used to avoid simple global ID inference. Inet peer bases are allocated per network namespace and store redirect/error rate state. Proc and sysctl state exposes counters and tunables; writes to route flush sysctl bump both route and exception generation IDs.

## Dependencies and Integration Points

This code sits between the IPv4 FIB/rules engine, dst cache, neighbour/ARP, ICMP, XFRM, lwtunnel, multicast routing, procfs, sysctl, netlink/rtnetlink, net namespaces, and device configuration. It relies heavily on `fib_lookup()`, `fib_select_path()`, `fib_validate_source()`, `fib_multipath_hash_from_keys()`, device configuration macros such as `IN_DEV_FORWARD()` and `IN_DEV_ROUTE_LOCALNET()`, neighbour helpers for IPv4/IPv6 nexthops, and dst lifetime primitives. TCP and ICMP depend on its exported PMTU/redirect and route output helpers.

## Risks and Edge Cases

- Concurrency is delicate: exception tables use a single spinlock plus RCU; route caches use lockless `cmpxchg`; uncached lists are per-CPU with bottom-half locks; dst device references must be preserved on cache replacement and flush.
- Redirect and PMTU exception state can stale routes if generation IDs, expiration checks, or `dst.obsolete` transitions are wrong.
- Martian filtering, `route_localnet`, L3 master devices, proxy ARP, broadcast forwarding, and multicast forwarding all have policy-specific branches that can create security regressions if reordered.
- Multipath hash policies affect flow distribution and ICMP error behavior; custom hash fields must handle absent inner headers and `FLOWI_FLAG_ANY_SPORT` randomization.
- Netlink strict validation must keep `RTM_GETROUTE` from accepting unsupported attributes while maintaining legacy non-strict behavior.
- Namespace sysctl registration mutates table data pointers for non-init namespaces; pointer adjustment and cleanup must remain paired.

## Test Signals

Strong signals include IPv4 forwarding/local delivery tests, martian source/destination tests, multicast and broadcast routing tests, PMTU discovery with multipath and locked MTU routes, ICMP redirect accept/reject behavior, route cache flush/sysctl behavior, `ip route get` netlink tests with strict attributes and `RTM_F_FIB_MATCH`, XFRM route output, lwtunnel redirect paths, L3 master/VRF routes, route namespace creation/destruction, and stress tests for concurrent FIB updates, dst invalidation, and device teardown.
