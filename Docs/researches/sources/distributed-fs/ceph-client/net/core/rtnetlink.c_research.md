# sources/distributed-fs/ceph-client/net/core/rtnetlink.c

## Purpose

`rtnetlink.c` is the protocol-independent core of the Linux `NETLINK_ROUTE` / rtnetlink interface. It owns the global RTNL lock, per-network-namespace rtnetlink sockets, message handler registration, dispatch, and a large set of default handlers for network link, bridge, FDB, MDB, and link statistics operations. User space tools such as `ip`, `bridge`, and ethtool-facing code reach this file through rtnetlink messages like `RTM_NEWLINK`, `RTM_GETLINK`, `RTM_SETLINK`, `RTM_NEWNEIGH`, `RTM_GETSTATS`, and bridge-family MDB/FDB operations.

The file is central infrastructure rather than a device driver. It converts netlink payloads into calls on `struct net_device`, `struct net_device_ops`, `struct rtnl_link_ops`, and `struct rtnl_af_ops`, then serializes kernel network-device state back into netlink attributes.

## Important APIs, Types, And Functions

The RTNL locking API is exported through `rtnl_lock()`, `rtnl_lock_interruptible()`, `rtnl_lock_killable()`, `rtnl_trylock()`, `rtnl_unlock()`, `__rtnl_unlock()`, `rtnl_is_locked()`, `lockdep_rtnl_is_held()`, and `refcount_dec_and_rtnl_lock()`. With `CONFIG_DEBUG_NET_SMALL_RTNL`, per-net namespace locks are layered under the global RTNL lock through `rtnl_net_lock()`, `rtnl_net_unlock()`, `rtnl_net_trylock()`, `rtnl_net_lock_killable()`, and lockdep comparison helpers.

`struct rtnl_link` is the registered handler entry for a protocol/message pair. It holds `doit`, `dumpit`, `owner`, `flags`, and an RCU head. `rtnl_msg_handlers` is a two-level RCU table indexed by protocol family and rtnetlink message index. `__rtnl_register_many()`, `__rtnl_unregister_many()`, `rtnl_unregister_all()`, and the internal `rtnl_register_internal()` manage this table.

`struct rtnl_link_ops` registration is handled by `rtnl_link_register()` and `rtnl_link_unregister()`. Link ops provide kind-specific virtual-device creation, validation, serialization, deletion, stats, and slave-link behavior. `struct rtnl_af_ops` registration is handled by `rtnl_af_register()` and `rtnl_af_unregister()` and gives address families a way to add link attributes, validate AF-specific changes, and fill stats.

Message emission helpers include `rtnetlink_send()`, `rtnl_unicast()`, `rtnl_notify()`, `rtnl_set_sk_err()`, `rtmsg_ifinfo_build_skb()`, `rtmsg_ifinfo_send()`, `rtmsg_ifinfo()`, and `rtmsg_ifinfo_newnet()`. Routing helper serializers include `rtnetlink_put_metrics()` and `rtnl_put_cacheinfo()`.

The link-reporting core is `if_nlmsg_size()` plus `rtnl_fill_ifinfo()`. It fills `RTM_NEWLINK` messages with names, indexes, flags, MTU, queue sizes, carrier counters, address data, qdisc, stats, XDP attachment state, VF/SR-IOV information, link kind data, slave info, alternate names, namespace IDs, devlink port handles, DPLL pin handles, parent device data, and AF-specific nests.

The major link mutation handlers are `rtnl_setlink()`, `do_setlink()`, `rtnl_newlink()`, `__rtnl_newlink()`, `rtnl_newlink_create()`, `rtnl_changelink()`, `rtnl_dellink()`, `rtnl_delete_link()`, and `rtnl_configure_link()`. They parse `IFLA_*` attributes, resolve target namespaces, validate policy, and call network core helpers or driver callbacks.

FDB support is implemented by `rtnl_fdb_add()`, `rtnl_fdb_del()`, `rtnl_fdb_get()`, `rtnl_fdb_dump()`, default exported operations `ndo_dflt_fdb_add()`, `ndo_dflt_fdb_del()`, `ndo_dflt_fdb_dump()`, and notification helpers. Bridge link support is implemented by `ndo_dflt_bridge_getlink()`, `rtnl_bridge_getlink()`, `rtnl_bridge_setlink()`, `rtnl_bridge_dellink()`, and `rtnl_bridge_notify()`.

Statistics support is implemented by `rtnl_stats_get()`, `rtnl_stats_dump()`, `rtnl_stats_set()`, `rtnl_fill_statsinfo()`, `if_nlmsg_stats_size()`, and offload-xstats helpers such as `rtnl_offload_xstats_fill()` and `rtnl_offload_xstats_notify()`. MDB support is implemented by `rtnl_mdb_dump()`, `rtnl_mdb_get()`, `rtnl_mdb_add()`, and `rtnl_mdb_del()`.

Initialization is performed by `rtnetlink_init()`, which registers pernet operations, installs a netdevice notifier, and registers the built-in rtnetlink handlers declared in `rtnetlink_rtnl_msg_handlers[]`.

## Control Flow

For each network namespace, `rtnetlink_net_init()` creates a `NETLINK_ROUTE` socket using `netlink_kernel_create()` with `rtnetlink_rcv()` as input and `rtnetlink_bind()` as the group bind gate. Received skbs are passed through `netlink_rcv_skb()` to `rtnetlink_rcv_msg()`.

`rtnetlink_rcv_msg()` validates the message type, minimal payload length, and operation kind. Non-GET operations require `CAP_NET_ADMIN`. Dump GET operations lookup a `dumpit` handler by family and message type, take a module reference, optionally compute a minimum allocation for `RTM_GETLINK`, and start a netlink dump through `rtnetlink_dump_start()`. Non-dump operations lookup a `doit` handler, enforce bulk-delete support, and either call it unlocked when flagged or call it under RTNL.

`RTM_GETLINK` dump requests flow through `rtnl_dump_ifinfo()`: parse request attributes, optionally resolve a target namespace, apply master/kind filters, iterate devices with dump cursor state, and call `rtnl_fill_ifinfo()` for each device. Single getlink requests flow through `rtnl_getlink()`, which resolves one device, synchronizes linkwatch carrier state, fills one skb, and unicasts it back.

`RTM_SETLINK` and change parts of `RTM_NEWLINK` flow into `do_setlink()`. It validates address lengths and size limits, optionally moves a device to another netns, locks device ops, then applies attributes in sequence: hardware map, MAC address, MTU, group, name, alias, broadcast address, flags, master linkage, carrier, queue length, GSO/GRO limits, operstate, link mode, VF data, VF port data, AF-specific data, protodown, and XDP FD replacement. Several changes can be committed before a later attribute fails.

`RTM_NEWLINK` parses base and nested link-info attributes, resolves the link kind via `rtnl_link_ops_get()` and optional module autoload, validates kind-specific data, resolves target/link/peer namespaces, locks the ordered namespace set with `rtnl_nets_lock()`, then either changes an existing device or creates a new one. Creation uses `rtnl_create_link()` and either `ops->newlink()` or `register_netdevice()`, followed by flag/master configuration.

FDB and MDB handlers follow a similar pattern: parse and validate strict or legacy netlink payloads, resolve the device, decide whether the operation applies to bridge master behavior or self behavior, call the appropriate `net_device_ops` callback, and emit notifications when a default operation succeeds without driver notification.

## State And Persistence Behavior

The global `rtnl_mutex` serializes most link and device topology changes. `defer_kfree_skb_list` temporarily stores skbs to free after RTNL unlock. `rtnl_msg_handlers` persists registered rtnetlink operations in RCU-protected tables. `link_ops` and `rtnl_af_ops` persist registered link-kind and address-family extension providers, guarded by mutex/RTNL plus RCU/SRCU grace periods.

Per-network-namespace persistent state is `net->rtnl`, the netlink socket created during namespace init and released during namespace exit. Link operations mutate persistent `struct net_device` fields such as name, MTU, group, flags, link mode, carrier, queue limits, GSO/GRO limits, protodown state, alternate names, XDP attachment, master/slave relationships, namespace placement, and offload stats enablement. FDB/MDB state is delegated to bridge/device callbacks or default unicast/multicast address list operations.

The file itself does not persist state across reboot or outside kernel memory. Its persistence is runtime kernel state plus registered callbacks.

## Dependencies And Integration Points

This code depends heavily on netlink attribute parsing (`nlmsg_parse*`, `nla_parse*`, `nla_put*`), network namespace APIs, netdevice core helpers, device notifier chains, RCU/SRCU, module references, devlink, DPLL, BPF/XDP, bridge data types, VLAN validation, and address-family extension hooks. IPv6-specific MDB validation is compiled conditionally.

Driver integration is through `struct net_device_ops`: VF setters/getters, FDB/MDB operations, bridge set/get/delete operations, offload stats hooks, XDP changes through `dev_change_xdp_fd()`, and device configuration callbacks. Virtual link-kind integration is through `struct rtnl_link_ops`: validation, allocation, setup, `newlink`, `changelink`, `dellink`, link-info serializers, slave serializers, peer netns handling, and xstats. Address-family integration is through `struct rtnl_af_ops` for per-AF link and stats data.

User-space ABI integration is strict: this file contains compatibility handling for old `RTM_GETLINK` and FDB dump request shapes, strict-check paths for newer requests, and careful netlink extack messages for invalid input.

## Risks And Edge Cases

`do_setlink()` intentionally has partial-commit behavior. If an early attribute is applied and a later driver callback or validation fails, the file logs a rate-limited warning that the interface may be left with an inconsistent configuration. Callers and tests must not assume all-or-nothing semantics.

Locking is high risk. The file mixes global RTNL, optional per-net RTNL mutexes, netdev instance locks, `dev_addr_sem`, RCU, SRCU, module references, pernet setup/cleanup exclusion, and callback paths into drivers. The ordered `rtnl_nets` helper and `rtnl_lock_unregistering_all()` exist specifically to avoid deadlocks around multi-netns link creation and link-op unregistration.

Netlink ABI validation is broad and security-sensitive. Non-GET operations require `CAP_NET_ADMIN`, target namespace operations check capabilities in the target user namespace, and multicast route groups have bind restrictions. Attribute policies reject or constrain many fields, but driver callbacks still receive parsed nested data and must maintain their own invariants.

Buffer sizing is another recurring risk. `if_nlmsg_size()` and `if_nlmsg_stats_size()` must match their fill functions; `-EMSGSIZE` in many single-message paths is treated as a kernel bug warning. Kind-specific and AF-specific callbacks can also create sizing mismatches.

RCU/SRCU lifetime rules matter for registered `rtnl_link_ops`, `rtnl_af_ops`, and handler tables. Incorrect module owner handling or missing grace periods could expose use-after-free. The code uses `try_module_get()`, `module_put()`, `kfree_rcu()`, `synchronize_net()`, `synchronize_srcu()`, and RCU list traversal to manage this.

Compatibility paths preserve older user-space behavior and therefore constrain cleanup. Changes to legacy request parsing, `RTNL_FLAG_DUMP_SPLIT_NLM_DONE`, FDB dump request handling, or default handler behavior could regress existing tools.

## Test Signals

Useful tests include rtnetlink selftests or integration tests that exercise `ip link add/set/del/show`, namespace moves, target netns IDs, XDP FD replacement, alternate interface names, protodown reasons, VF configuration failures, and group operations. Bridge/FDB/MDB coverage should include strict and legacy dump requests, `NTF_SELF` versus `NTF_MASTER`, bulk delete support flags, VLAN validation, and notification delivery.

Kernel debug signals include lockdep for RTNL/per-net lock ordering, KASAN/KCSAN for RCU and callback lifetime issues, extack strings for invalid netlink requests, `WARN_ON(err == -EMSGSIZE)` in sizing-sensitive paths, and the rate-limited partial-change warning from `do_setlink()`. User-space ABI tests should check both strict netlink validation and legacy request compatibility.
