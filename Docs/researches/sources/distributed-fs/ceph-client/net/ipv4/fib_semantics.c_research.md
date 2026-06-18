# sources/distributed-fs/ceph-client/net/ipv4/fib_semantics.c

## Purpose
`fib_semantics.c` implements shared IPv4 route semantics below tables and rules. It owns `fib_info` allocation, deduplication, refcounting, metrics, nexthop initialization and validation, preferred source validation and caching, route netlink serialization, nexthop/device down-up synchronization, PMTU exception updates, default and multipath path selection, and per-net fib_info hash lifecycle.

## Important APIs, Types, and Functions
The route-type property table is `fib_props[]`, mapping `RTN_*` types to default error and scope. Core lifetime APIs are `fib_create_info()`, `fib_release_info()`, `free_fib_info()`, `fib_nh_common_release()`, and `fib_nh_release()`.

Nexthop creation and validation APIs include `fib_nh_common_init()`, `fib_nh_init()`, `fib_check_nh()`, `fib_check_nh_v4_gw()`, `fib_check_nh_v6_gw()`, `fib_check_nh_nongw()`, `fib_get_nhs()`, `fib_nh_match()`, `fib_metrics_match()`, and `fib_rebalance()`.

Serialization and notification APIs include `fib_nlmsg_size()`, `rtmsg_fib()`, `fib_nexthop_info()`, `fib_add_nexthop()`, and `fib_dump_info()`. Runtime synchronization APIs are `ip_fib_check_default()`, `fib_sync_down_addr()`, `fib_nhc_update_mtu()`, `fib_sync_mtu()`, `fib_sync_down_dev()`, `fib_sync_up()`, `fib_select_path()`, `fib_select_multipath()`, and `fib_result_prefsrc()`.

## Control Flow
Route creation begins in `fib_create_info()`. It validates route type, scope, forbidden flags, nexthop ID existence, multipath array structure, and metrics. It allocates a flexible `fib_info`, initializes metrics, fills direct nexthops or attaches a nexthop object, rejects invalid route-type combinations, validates host-scope restrictions, validates gateways/devices through `fib_check_nh()`, validates preferred source, computes source-address cache, rebalances multipath weights, deduplicates against existing `fib_info`, and finally links the object into hash tables and per-device nexthop lists.

Gateway validation recursively checks reachability. Onlink IPv4 gateways require an output device, up carrier semantics, and a unicast gateway address on that device. Non-onlink IPv4 gateways are looked up in the route table or full rules path with increased scope and must resolve to unicast/local with an egress device. IPv6 gateways delegate to IPv6 nexthop initialization. Nongateway nexthops require a valid up IPv4 device and reject pervasive/onlink flags.

Deletion goes through `fib_release_info()`: when trie references drain, it removes the object from hash tables, preferred-source hash, nexthop object lists or per-device nexthop hashes, marks `fib_dead` with `WRITE_ONCE()`, and releases the final client reference through RCU. `free_fib_info_rcu()` releases nexthop objects or embedded nexthops, route metrics, cached rtable exceptions, per-CPU output routes, lwtunnel state, and netdevice references.

Route dumps compute a conservative netlink size, write `rtmsg`, table, destination, priority, metrics, preferred source, nexthop ID, single or multipath nexthop attributes, lwtunnel encap, class IDs, and offload/trap flags. `rtmsg_fib()` packages trie alias metadata with `fib_dump_info()` and sends notifications to `RTNLGRP_IPV4_ROUTE`.

Device/address synchronization marks route state rather than always deleting objects. `fib_sync_down_addr()` marks routes with a removed preferred source as dead. `fib_sync_down_dev()` marks nexthops and whole `fib_info` objects `LINKDOWN` and/or `DEAD`, calls fib notifiers for nexthop delete events, and rebalances multipath. `fib_sync_up()` clears those flags when devices return and emits nexthop add events. `fib_sync_mtu()` updates PMTU exceptions attached to nexthops.

Path selection uses multipath hashing when multiple paths exist, nexthop objects when attached, neighbor reachability if `fib_multipath_use_neigh` is enabled, source-address affinity scoring, weighted upper bounds, and default-route probing through neighbor state. `fib_select_path()` also fills `flowi4.saddr`, respecting l3mdev source selection.

## State and Persistence Behavior
Per-net state includes `fib_info_hash`, `fib_info_hash_bits`, and `fib_info_cnt`. The hash has two halves: primary `fib_info` deduplication buckets and preferred-source lookup buckets. It grows when the object count reaches the current bucket count.

`fib_info` objects are shared runtime route payloads referenced by trie aliases and lookup results. They hold route metrics, type/scope/protocol/table/priority, preferred source, flags, embedded nexthops or a nexthop object reference, and route cache/exception state. Embedded nexthops are also linked into `dev->fib_nh_head` for device event scans.

Preferred source cache is stored per IPv4 nexthop as `nh_saddr` plus `nh_saddr_genid`, invalidated by `dev_addr_genid`. Multipath upper bounds are atomics updated by `fib_rebalance()`. No durable route state is persisted here.

## Dependencies and Integration Points
The file depends on IPv4 and IPv6 nexthop helpers, ARP/ND neighbor tables, lwtunnel state, rtnetlink metrics, TCP congestion-control metric keys, netdevice refs/trackers, XFRM-independent route cache objects, fib notifiers, DSCP helpers, address selection from `devinet.c`, and trie aliases from `fib_lookup.h`.

It is called by `fib_trie.c` for route insert/delete/dump, by `fib_frontend.c` for address/device lifecycle and route selection, by redirect logic through `ip_fib_check_default()`, and by notifier/offload consumers through route and nexthop event notifications.

## Risks and Edge Cases
Nexthop validation is historically complex. Gateways can be local, directly connected, recursively reachable, forced onlink, IPv6 via IPv4 routes, or hidden behind lwtunnels. Incorrect scope or device validation can accept unreachable routes or reject valid policy/VRF routes.

Lifetime and refcounting are high risk. Lookup readers are RCU-based, while writers remove from hash/list structures under RTNL and defer freeing. The code must avoid freeing alive `fib_info`, leaking netdevice/lwtunnel/metrics references, or leaving embedded nexthops in device hashes.

Multipath behavior depends on weights, linkdown flags, neighbor state, source address affinity, nexthop objects, and sequence wrap. Rebalance errors can skew traffic or select dead nexthops. Device down/up notifier transitions must emit correct add/delete events only when a nexthop becomes externally visible or hidden.

Route serialization must size messages correctly for metrics, nexthop IDs, multipath, IPv6 `RTA_VIA`, lwtunnel encap, offload flags, and nexthop compatibility mode. `-EMSGSIZE` here is treated as a bug in size calculation.

## Test Signals
Creation tests should cover unicast/local/broadcast/throw/unreachable/prohibit route types, invalid scopes, forbidden `DEAD`/`LINKDOWN` flags, preferred source validation, IPv4 and IPv6 gateways, onlink gateways, down devices, missing devices, lwtunnel encap, nexthop IDs, duplicate route deduplication, metrics matching, and multipath attribute validation.

Lifecycle tests should cover route deletion under concurrent lookup, RCU freeing, per-device nexthop hash cleanup, address preferred-source removal, device down/change/unregister/up, PMTU exception update rules, net namespace hash init/exit, and class ID accounting. Path tests should cover weighted ECMP distribution, linkdown ignore, neighbor-aware selection, source-affinity preference, default-route fallback, nexthop objects, and l3mdev source address selection.
