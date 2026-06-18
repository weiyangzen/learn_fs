# sources/distributed-fs/ceph-client/net/ipv6/route.c

## Purpose

`route.c` is the IPv6 FIB front-end and dst-cache implementation. It turns route configuration, fib6 trie lookups, policy rules, nexthops, device state, PMTU updates, ICMP redirects, and rtnetlink/ioctl requests into usable `struct rt6_info` destination entries. It owns the AF_INET6 `dst_ops`, special unreachable/prohibit/blackhole route entries, per-net route sysctls/proc output, route netlink handlers, and lifecycle registration for IPv6 route support.

## Important APIs, Types, And Functions

The core externally visible APIs are `ip6_route_lookup()`, `rt6_lookup()`, `ip6_pol_route()`, `ip6_route_input_lookup()`, `ip6_route_input()`, `ip6_route_output_flags()`, `ip6_blackhole_route()`, `ip6_update_pmtu()`, `ip6_sk_update_pmtu()`, `ip6_redirect()`, `ip6_sk_redirect()`, `ip6_route_add()`, `ip6_del_rt()`, `ipv6_route_ioctl()`, `addrconf_f6i_alloc()`, `rt6_add_dflt_router()`, `rt6_get_dflt_router()`, `rt6_purge_dflt_routers()`, `rt6_sync_up()`, `rt6_sync_down_dev()`, `rt6_disable_ip()`, `rt6_mtu_change()`, `inet6_rt_notify()`, `fib6_rt_update()`, `fib6_info_hw_flags_set()`, `ip6_route_init()`, and `ip6_route_cleanup()`.

Key internal state is stored in `struct fib6_info`, `struct fib6_nh`, `struct fib6_result`, `struct rt6_info`, `struct rt6_exception`, and per-net `net->ipv6` fields. The file defines per-CPU `rt6_uncached_list` lists for uncached dsts, `rt6_exception_lock` for nexthop exception buckets, `ip6_dst_ops_template`, `ip6_dst_blackhole_ops`, and templates for null/prohibit/blackhole entries.

Lookup helpers include `fib6_table_lookup()`, `rt6_select()`, `fib6_select_path()`, `rt6_multipath_hash()`, `rt6_find_cached_rt()`, `ip6_create_rt_rcu()`, `ip6_rt_cache_alloc()`, and per-CPU cache helpers `rt6_get_pcpu_route()` / `rt6_make_pcpu_route()`. Mutation helpers include `fib6_nh_init()`, `ip6_route_info_create()`, `ip6_route_info_create_nh()`, `__ip6_ins_rt()`, `ip6_route_del()`, `ip6_route_multipath_add()`, and `ip6_route_multipath_del()`.

## Control Flow

Input lookup starts in `ip6_route_input()`, builds `flowi6` from the packet, performs early flow dissection for multipath hashing, and installs a no-ref dst from `ip6_route_input_lookup()`. That calls fib rules with `ip6_pol_route_input()`, which delegates to `ip6_pol_route()`. Output lookup follows `ip6_route_output_flags()`, which wraps `ip6_route_output_flags_noref()` under RCU and safely takes a dst ref unless the returned dst is already on the uncached list.

`ip6_pol_route()` performs policy-table lookup, then `fib6_table_lookup()`, then `fib6_select_path()` for ECMP/nexthop-object selection. It checks per-nexthop exception buckets first. If no exception is found, it either creates a special uncached clone for `FLOWI_FLAG_KNOWN_NH` or creates/uses a per-CPU route copy. `ip6_pol_route_lookup()` is a similar rule callback that returns a referenced `rt6_info` and creates a fresh dst when needed.

Route addition flows from rtnetlink `inet6_rtm_newroute()` or ioctl through `rtm_to_fib6_config()` / `rtmsg_to_fib6_config()`, `fib6_config_validate()`, `ip6_route_info_create()`, nexthop initialization, and `fib6_add()` under the table lock. Multipath add parses each `rtnexthop`, creates one `fib6_info` per nexthop, inserts them as siblings, then emits consolidated notifications and rolls back partial insertion on failure. Deletion locates matching fib6 nodes, optionally removes cached exceptions, and deletes one route or all siblings depending on gateway/multipath flags.

PMTU and redirect events create or update exception routes. `__ip6_rt_update_pmtu()` lowers metrics in place where safe, or allocates a route-cache clone and inserts it into a nexthop exception bucket. `rt6_do_redirect()` validates ICMPv6 Redirect constraints, updates neighbor state, creates a dynamic gateway/on-link cache exception, and notifies `NETEVENT_REDIRECT`.

## State And Persistence Behavior

Persistent route state lives in fib6 tables within each network namespace. Per-net special routes and sysctls are initialized by `ip6_route_net_init()`; late proc entries are created by `ip6_route_net_init_late()`. Per-CPU dst cache entries hang off nexthops and are invalidated by route generation IDs. Exception routes are per-nexthop hash buckets protected by `rt6_exception_lock` and RCU-freed, with randomized depth pruning to limit side-channel exposure. Uncached dsts are tracked per CPU so device teardown can replace references with `blackhole_netdev`.

Expiration is split across fib routes and dst clones: `RTF_EXPIRES` routes use `dst.expires` or `fib6_info->expires`; GC scans exception buckets and fib GC lists. PMTU exceptions set `RTF_MODIFIED` and expire after `ip6_rt_mtu_expires`. RA route information and default routers are added with finite or infinite lifetimes and are purged when RA policy no longer accepts them.

## Dependencies And Integration Points

This file integrates with `net/ipv6` FIB internals (`ip6_fib`, fib6 rules, nexthop objects), dst and xfrm, neighbor discovery, addrconf, l3mdev/VRF routing, rtnetlink, netdevice notifiers, lightweight tunnels, netevent notifiers, SNMP stats, procfs, sysctl, BPF iterators, and optional IPv6 subtrees, router preferences, multicast routing, multiple tables, and proc/BPF support. It also cooperates directly with lwtunnel encapsulations such as SRv6/RPL through `fib_nh_common_init()`, `lwtunnel_set_redirect()`, and `lwtunnel_headroom()`.

## Risks And Edge Cases

The main risks are lifetime and concurrency bugs: dst references are mixed with no-ref lookup paths, RCU-held `fib6_info` references, per-CPU route caches, and exception bucket mutation. Device unregister/down paths must reliably replace or release dst device references, especially for uncached routes. PMTU and redirect exceptions are security-sensitive because untrusted network events can create cached route state; the code validates redirect source/gateway, multicast targets, neighbor options, and PMTU bounds. Multipath route add/delete has partial failure rollback and notification ordering risks. Netlink parsing must reject unsupported IPv6 attributes, invalid gateway/local addresses, internal flags such as `RTF_CACHE`/`RTF_PCPU`, and inconsistent nexthop-object combinations.

## Test Signals

Useful signals are IPv6 route selftests via `ip -6 route add/del/get`, multipath and nexthop-object tests, PMTU tests that verify exception creation/expiration, ICMPv6 redirect tests, VRF/l3mdev link-scope tests, route dump filtering and cloned exception dumps, device down/unregister tests, RA default-router lifetime tests, and lockdep/KASAN/RCU validation under route churn. Runtime observability includes rtnetlink notifications, `/proc/net/ipv6_route`, `/proc/net/rt6_stats`, route sysctls, fib6 tracepoints, and BPF iterator output when enabled.
