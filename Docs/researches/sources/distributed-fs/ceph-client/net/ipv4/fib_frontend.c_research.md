# sources/distributed-fs/ceph-client/net/ipv4/fib_frontend.c

## Purpose
`fib_frontend.c` is the IPv4 FIB frontend. It owns per-namespace FIB table setup, route rtnetlink and legacy route ioctl parsing, address-type queries, source validation/reverse-path filtering, automatic route creation and deletion from interface addresses, route dumps, netdevice/address event handling, and IPv4 FIB pernet initialization.

## Important APIs, Types, and Functions
Table management APIs are `fib_new_table()`, `fib_get_table()`, `fib_replace_table()`, `fib_unmerge()`, and `fib_flush()`. Address type APIs are `inet_addr_type_table()`, `inet_addr_type()`, `inet_dev_addr_type()`, and `inet_addr_type_dev_table()`.

Source validation is implemented by `fib_validate_source()` and `__fib_validate_source()`. Route user interfaces are `ip_rt_ioctl()`, `rtentry_to_fib_config()`, `rtm_to_fib_config()`, `inet_rtm_newroute()`, `inet_rtm_delroute()`, `ip_valid_fib_dump_req()`, and `inet_dump_fib()`.

Address-derived route manipulation is handled by `fib_magic()`, `fib_add_ifaddr()`, `fib_modify_prefix_metric()`, and `fib_del_ifaddr()`. Lifecycle hooks are `fib_inetaddr_event()`, `fib_netdev_event()`, `fib_disable_ip()`, `ip_fib_net_init()`, `ip_fib_net_exit()`, `fib_net_init()`, `fib_net_exit()`, `fib_net_exit_batch()`, and `ip_fib_init()`.

## Control Flow
Per-net initialization registers fib notifiers, allocates the FIB table hash, creates default tables/rules, initializes `fib_semantics` hashes, creates a `NETLINK_FIB_LOOKUP` socket, and initializes proc entries. In non-multiple-table builds the local and main trie tables are created directly. In multiple-table builds `fib_new_table()` lazily allocates trie tables, records main/default RCU shortcuts, and aliases local to main until custom rules force `fib_unmerge()`.

Route add/delete through rtnetlink parses `struct rtmsg` and attributes into `struct fib_config`, validates DSCP/TOS, prefix length and host bits, gateway versus via exclusivity, nexthop-id exclusivity, lwtunnel encap types, table selection, and route type. Add creates the target table and calls `fib_table_insert()`; delete verifies nexthop ID existence and calls `fib_table_delete()`.

Legacy `SIOCADDRT` and `SIOCDELRT` ioctls translate `struct rtentry` into the same `fib_config` model. The conversion preserves historical quirks such as metric minus one, classful mask defaults from userspace, alias labels choosing preferred source, gateway scope inference, and metrics mapping to `RTAX_ADVMSS`, `RTAX_WINDOW`, and `RTAX_RTT`.

Source validation builds a reverse lookup flow from packet source/destination, l3mdev, optional mark, DSCP, ports from early flow dissection when required by rules, and RPF settings. It fast-paths common cases without custom local routes/rules, treats IPsec-secpath packets as exempt from rp_filter, rejects invalid local/broadcast sources, and returns drop reasons such as `SKB_DROP_REASON_IP_RPFILTER`.

Interface address events call `fib_add_ifaddr()` and `fib_del_ifaddr()` to create or delete local, prefix, and broadcast routes. Device events synchronize nexthop state, flush route cache, update MTU exceptions, and disable IP on unregister or last-address removal. Route dumps iterate the FIB table hash with resumable callback args and strict dump filters for table and output device.

## State and Persistence Behavior
State is runtime and per-net. `net->ipv4.fib_table_hash` contains `struct fib_table` objects; optional RCU shortcuts point at main/default tables. Flags such as `fib_has_custom_local_routes` and `fib_has_custom_rules` influence source validation. `dev_addr_genid` changes when addresses affect routes.

Address-derived route state is stored in normal FIB tables, not separately. Route cache and nexthop state are flushed or marked dead/linkdown on address and device changes. The `NETLINK_FIB_LOOKUP` socket exists per namespace and is released during net exit.

## Dependencies and Integration Points
The file depends on trie table operations from `fib_trie.c`, shared fib_info semantics from `fib_semantics.c`, policy rules from `fib_rules.c`, notifier setup from `fib_notifier.c`, rtnetlink, lwtunnel, nexthop objects, l3mdev/VRF, XFRM/IPsec, ARP, IPv4 route cache, flow dissector data, procfs, and netdevice/inetaddr notifier chains.

It integrates with `devinet.c` through address notifiers and direct calls from address insertion/deletion paths. It integrates with `route.c` through lookup, source validation, and path selection. Userspace integration is through `RTM_NEWROUTE`, `RTM_DELROUTE`, `RTM_GETROUTE`, route ioctls, and the legacy FIB lookup netlink family.

## Risks and Edge Cases
Rules and table aliasing are subtle. `fib_unmerge()` must split local and main tables before custom rules can expose different semantics. Failure can leak local routes into the wrong table or break local route dumps.

Route parser risks include invalid DSCP with ECN bits, nonzero host bits for prefixes, mutually exclusive gateway/via/nexthop specifications, IPv6 gateway via `RTA_VIA`, lwtunnel validation, and preserving compatibility for old ioctls.

Source validation is security-sensitive because it implements martian-source and reverse-path filtering decisions. Custom rules, VRF/l3mdev, IPsec exemptions, local addresses in containers, marks, and flow-dissected port selectors all affect whether packets are dropped.

Device/address synchronization must avoid deleting shared broadcast/local routes still used by other addresses and must flush routes when preferred source addresses disappear. Net exit destroys tables in reverse order because the local table can reference main-table data.

## Test Signals
Test route netlink add/delete/dump with main, local, default, custom tables, nexthop IDs, multipath, `RTA_VIA`, lwtunnel encap, invalid prefixes, invalid DSCP, and strict dump filters. Test route ioctl add/delete for gateway, reject, device alias, and metrics.

Lifecycle tests should cover address add/delete generating local/prefix/broadcast routes, secondary address promotion, metric replacement through address replace, device up/down/change/unregister, MTU change exception updates, VRF upper changes, and namespace teardown ordering. Source-validation tests should cover rp_filter modes, IPsec secpath exemption, custom local routes/rules, accept_local, src_valid_mark, l3mdev, and port-matching rules.
