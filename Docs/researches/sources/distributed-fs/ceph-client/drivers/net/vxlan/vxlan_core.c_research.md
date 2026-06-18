<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_core.c

## Purpose
`vxlan_core.c` is the main Linux VXLAN tunnel driver implementation. It registers the `vxlan` rtnetlink link kind, owns netdevice setup/lifecycle, UDP tunnel socket sharing, packet receive/decapsulation, transmit/encapsulation, forwarding database (FDB) learning and management, multicast and VNI-filter hooks, MDB forwarding hooks, switchdev/nexthop integration, and per-net namespace cleanup.

## Important APIs, Types, and Functions
- Module parameters: `udp_port` defaults to Linux legacy VXLAN port 8472; `log_ecn_error` controls rate-limited ECN decapsulation diagnostics.
- Global/private state: `vxlan_net_id`, `all_zeros_mac`, `vxlan_link_ops`, `vxlan_fdb_rht_params`, per-device `vxlan->fdb_hash_tbl`, `vxlan->fdb_list`, `vxlan->hash_lock`, `vxlan->age_timer`, `vxlan->vn4_sock`, `vxlan->vn6_sock`, and `vxlan->default_dst`.
- Socket lookup and VNI dispatch: `vxlan_find_sock()`, `vxlan_vs_find_vni()`, `vxlan_find_vni()`, `vxlan_socket_create()`, `__vxlan_sock_add()`, `vxlan_sock_add()`, and `vxlan_sock_release()`.
- FDB management: `vxlan_fdb_info()`, `vxlan_fdb_notify()`, `vxlan_fdb_create()`, `vxlan_fdb_update()`, `__vxlan_fdb_delete()`, `vxlan_fdb_dump()`, `vxlan_fdb_get()`, `vxlan_fdb_delete_bulk()`, `vxlan_flush()`, and timer callback `vxlan_cleanup()`.
- Switchdev/nexthop exported APIs: `vxlan_fdb_find_uc()`, `vxlan_fdb_replay()`, `vxlan_fdb_clear_offload()`, plus switchdev notifier handling for offload state and externally learned FDB entries.
- Receive path: `vxlan_rcv()` validates VXLAN/VXLAN-GPE headers, maps VNI to device, pulls tunnel headers, applies remote checksum offload, builds collect-metadata tunnel info, parses GBP, learns source MACs, checks ECN, updates stats, and queues to GRO cells.
- Transmit path: `vxlan_xmit()`, `vxlan_xmit_one()`, `vxlan_build_skb()`, `vxlan_xmit_nh()`, and `vxlan_xmit_nhid()` select FDB/default/MDB/nexthop destinations, perform ARP/ND proxy reduction, route-short-circuit handling, PMTU handling, UDP source-port hashing, and IPv4/IPv6 tunnel output.
- Netdevice/rtnl entry points: `vxlan_init()`, `vxlan_uninit()`, `vxlan_open()`, `vxlan_stop()`, `vxlan_setup()`, `vxlan_ether_setup()`, `vxlan_raw_setup()`, `vxlan_validate()`, `vxlan_newlink()`, `vxlan_changelink()`, `vxlan_dellink()`, `vxlan_fill_info()`, and `vxlan_dev_create()`.
- Module lifecycle: `vxlan_init_module()` registers pernet ops, netdevice notifier, switchdev notifier, rtnl link ops, and VNI-filter rtnl handlers; `vxlan_cleanup_module()` unregisters them in reverse.

## Control Flow
Creation starts through rtnetlink `newlink` or `vxlan_dev_create()`: `vxlan_nl2conf()` parses attributes, `vxlan_config_validate()` enforces legal mode combinations and address family rules, `vxlan_config_apply()` programs netdevice parameters and headroom, and `__vxlan_dev_create()` registers the netdevice, links an optional lower device, creates a default all-zero FDB destination, and adds the device to the per-net VXLAN list. Opening a device creates or shares UDP tunnel sockets, registers the device/VNI on the socket hash, joins multicast groups, and starts FDB ageing.

The receive path enters from the UDP tunnel socket callback. `vxlan_rcv()` requires a valid VNI bit, maps the socket plus VNI to a `vxlan_dev`, rejects configured reserved VXLAN header bits, optionally handles GPE, removes the outer VXLAN header, processes remote checksum offload and metadata, then either translates an Ethernet inner packet with `vxlan_set_mac()` or handles raw GPE payload. It validates the inner network header, applies ECN decapsulation, updates device and per-VNI stats, and passes the skb to `gro_cells_receive()`. Drop paths use explicit `skb_drop_reason` values and increment error/drop counters on the relevant checks.

The transmit path starts at `ndo_start_xmit`. In collect-metadata bridge mode, tunnel info supplies VNI/NHID; in direct metadata mode, `vxlan_xmit_one()` is called with skb tunnel info. Proxy mode can consume ARP or IPv6 ND requests locally via `arp_reduce()` or `neigh_reduce()`. MDB lookup is attempted before normal FDB multicast flooding when `VXLAN_F_MDB` is set. Normal forwarding looks up the destination MAC in the FDB, falls back to the all-zero default entry, emits L2 miss notifications where configured, then encapsulates one or more remote destinations or selects a nexthop group path. `vxlan_xmit_one()` resolves IPv4/IPv6 routes, honors local-bypass and PMTU behavior, builds the VXLAN header including GBP/GPE/remote checksum bits, and calls UDP tunnel output helpers.

FDB mutations are serialized by `vxlan->hash_lock` and published with RCU/list/rhashtable operations. Netlink FDB add/delete/dump/get map through netdevice operations. Learned entries are created by `vxlan_snoop()` on receive when learning is enabled. Ageing runs in `vxlan_cleanup()` and removes non-permanent, non-NOARP, non-externally-learned entries whose `updated` timestamp exceeds `cfg.age_interval`.

## State and Persistence Behavior
All driver state is in-kernel runtime state. Per-net namespace state (`struct vxlan_net`) tracks devices, UDP socket hashes, and a nexthop notifier. Per-device state tracks VXLAN config, default destination, FDB hash/list, MDB table, VNI filter group, GRO cells, sockets, and ageing timer. FDB and destination entries are RCU-freed; remote destinations keep `dst_cache` objects; nexthop-backed FDB entries hold nexthop references and membership on `nh->fdb_list`.

There is no disk persistence. User-visible persistent configuration is represented through rtnetlink attributes and netlink notifications. FDB/MDB/VNI-filter state is rebuilt by user space after reboot or module reload. Dynamic FDB entries age out, static/permanent entries remain until device teardown or explicit deletion.

## Dependencies and Integration Points
This file depends heavily on kernel networking infrastructure: rtnetlink, netdevice ops, UDP tunnel sockets, GRO, IP/IPv6 tunnel helpers, ARP/ND neighbor tables, rhashtable, RCU, switchdev, nexthop objects, net namespaces, ethtool, and VXLAN definitions from `<net/vxlan.h>`. It delegates per-VNI filtering to `vxlan_vnifilter.c`, multicast group membership to `vxlan_multicast.c`, and MDB multicast forwarding to `vxlan_mdb.c` through prototypes in `vxlan_private.h`.

Externally, it integrates with bridge/FDB netlink operations, switchdev hardware offload notifiers, lower netdevice unregister and UDP tunnel port push/drop notifications, nexthop deletion events, iproute2 VXLAN attributes, and metadata tunnel users such as TC/openvswitch-like paths.

## Risks and Edge Cases
- Locking is subtle: FDB lookup and traversal mix RCU, RTNL, and `hash_lock`; changes must preserve lock ordering and RCU lifetime rules.
- Socket sharing depends on matching receive flags, address family, port, and l3mdev binding. Incorrect flag matching can misdeliver VNIs or break collect-metadata devices.
- Header reserved-bit validation intentionally diverges from RFC ignoring behavior; adding VXLAN extensions must update `used_bits` and config validation coherently.
- Error handling in FDB update must roll back remote/nexthop changes after switchdev notification failures; partial rollback bugs would leak stale offload or destination state.
- Local-bypass and PMTU logic can reinject locally or drop with tunnel errors. Tests should cover route-local, multicast/broadcast, metadata and non-metadata combinations.
- IPv6 behavior is conditional on `CONFIG_IPV6` and runtime `ipv6_mod_enabled()`. Link-local IPv6 additionally depends on `remote_ifindex`.
- `vxlan_changelink()` only allows a restricted subset of fields to change. New mutable attributes need multicast leave/join, FDB default update, and adjacency handling.
- FDB age timer skips permanent/NOARP/ext-learned entries; changes to flags or state handling may alter learning/offload semantics.

## Test Signals
- Create/delete VXLAN links with IPv4, IPv6, multicast, unicast, GPE, GBP, collect-metadata, and VNI-filter attributes; verify `ip -d link show` reflects `vxlan_fill_info()`.
- Exercise FDB add/replace/append/delete/bulk-delete/get/dump including nexthop-backed FDBs, default all-zero entries, source VNI, remote port/VNI/ifindex, and switchdev notification error paths.
- Transmit/receive traffic across learned and static FDB entries, unknown unicast, broadcast, multicast, metadata mode, MDB mode, and nexthop groups; validate counters and drop reasons.
- Verify ARP/ND proxy reduction, L2/L3 miss notifications, route short circuit, local bypass, ECN handling, PMTU behavior, and remote checksum offload.
- Unregister lower devices, delete nexthops, close/open devices repeatedly, and remove net namespaces to catch RCU/list/socket lifetime regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_core.c -->
