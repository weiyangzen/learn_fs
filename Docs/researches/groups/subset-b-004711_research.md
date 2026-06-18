# Research Report: subset-b-004711

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c

## Purpose
`vxlan_mdb.c` implements VXLAN multicast database support. It lets user space program bridge-style MDB entries that map multicast IP groups, optional sources, and source VNIs to one or more VXLAN remote tunnel destinations. The datapath uses these entries to replicate eligible multicast traffic to selected remotes instead of using the generic all-zero/default FDB flooding path.

## Important APIs, Types, and Functions
- Core data types: `struct vxlan_mdb_entry_key` (`src`, `dst`, `vni`), `struct vxlan_mdb_entry` (rhashtable/list node plus remotes list), `struct vxlan_mdb_remote` (RCU `vxlan_rdst`, flags, filter mode, route protocol, source list), `struct vxlan_mdb_src_entry`, `struct vxlan_mdb_config`, and `struct vxlan_mdb_flush_desc`.
- Rhashtable configuration: `vxlan_mdb_rht_params` indexes entries by `(source address, group address, source VNI)`.
- Netlink dump/fill: `vxlan_mdb_dump()`, `vxlan_mdb_fill()`, `vxlan_mdb_entry_fill()`, `vxlan_mdb_entry_info_fill()`, and source-list helpers format RTM_NEWMDB bridge MDB payloads.
- Config parsing/validation: `vxlan_mdb_config_init()`, `vxlan_mdb_config_attrs_init()`, `vxlan_mdb_group_set()`, `vxlan_mdb_is_valid_source()`, `vxlan_mdb_config_src_list_init()`, and policy tables for set/delete/get attributes.
- Mutators: public `vxlan_mdb_add()`, `vxlan_mdb_del()`, `vxlan_mdb_del_bulk()` call internal `__vxlan_mdb_add()`, `__vxlan_mdb_del()`, `vxlan_mdb_remote_add()`, `vxlan_mdb_remote_replace()`, `vxlan_mdb_remote_del()`, and `vxlan_mdb_flush()`.
- Datapath APIs: `vxlan_mdb_entry_skb_get()` selects an MDB entry for an outgoing skb; `vxlan_mdb_xmit()` clones and sends to eligible remote destinations via `vxlan_xmit_one()`.
- Lifecycle: `vxlan_mdb_init()` initializes per-device table/list; `vxlan_mdb_fini()` flushes entries and destroys the table.

## Control Flow
MDB add/delete requests arrive through `ndo_mdb_add`/`ndo_mdb_del` registered in `vxlan_core.c`. `vxlan_mdb_config_init()` validates that the bridge MDB port is the VXLAN netdevice, entries are permanent for create/replace, VID is absent, the group is IPv4 or IPv6, and required entry attributes exist. Attribute parsing requires a remote destination IP and validates optional source, filter mode, source list, route protocol, remote port/VNI/ifindex, and source VNI.

`__vxlan_mdb_add()` gets or creates the group entry in the rhashtable/list, then adds or replaces a remote. Replacing swaps in a fresh `vxlan_rdst`, updates source filtering state, notifies RTNLGRP_MDB, then RCU-frees the old destination. For `(*,G)` entries with source lists, source forwarding entries are represented by corresponding `(S,G)` entries; INCLUDE/EXCLUDE controls whether generated source entries are blocked or active. Delete removes a remote, recursively deletes associated source-forwarding entries, sends delete notification, and drops the parent entry when no remotes remain.

Transmit lookup in `vxlan_mdb_entry_skb_get()` only considers multicast, non-broadcast Ethernet frames carrying IPv4 or IPv6. It builds an `(S,G,VNI)` key from inner IP source/destination, tries exact `(S,G)`, then `(*,G)`, then an all-zero group fallback for non-link-local multicast. `vxlan_mdb_xmit()` iterates remotes under RCU, skips blocked remotes and `(*,G)` INCLUDE remotes, clones the skb for all but one remote, and calls `vxlan_xmit_one()` with the MDB entry source VNI.

## State and Persistence Behavior
MDB state is runtime per-VXLAN-device state: `vxlan->mdb_tbl`, `vxlan->mdb_list`, `vxlan->mdb_seq`, and `VXLAN_F_MDB` in `vxlan->cfg.flags`. Entries and remotes are RCU-freed. Remote destinations own `dst_cache` objects and hold remote IP/port/VNI/ifindex. Source lists are normal hlist allocations tied to a remote. The state is not persisted across reloads; user space is expected to reprogram MDB entries.

`VXLAN_F_MDB` is enabled when the first MDB entry is inserted and disabled when the last entry is removed. `mdb_seq` changes on add/delete and is used by dump consistency checks.

## Dependencies and Integration Points
This file uses bridge MDB netlink ABI (`br_mdb_entry`, `MDBA_*`, `MDBE_*`, RTM_NEWMDB/RTM_DELMDB), rtnetlink, rhashtable, RCU lists, VXLAN address helpers from `vxlan_private.h`, and transmit support in `vxlan_core.c`. It integrates into the VXLAN netdevice operations through `ndo_mdb_*` and into the datapath through `vxlan_xmit()` checking `VXLAN_F_MDB`.

## Risks and Edge Cases
- MDB source-filter semantics are nontrivial: `(*,G)` INCLUDE entries are not directly transmitted by `vxlan_mdb_xmit()`; source-list generated `(S,G)` entries carry forwarding state. Changes must preserve this relationship.
- Remote lookup currently keys remotes by remote IP only. Remote port/VNI/ifindex are part of the stored `vxlan_rdst` and notification output, but not the remote lookup discriminator.
- Recursive source-entry add/delete can partially fail; rollback paths must remove generated source entries and not leave blocked/active state inconsistent.
- RCU pointer replacement in `vxlan_mdb_remote_replace()` must not free old destinations before readers finish.
- All-zero fallback intentionally avoids IPv4 local multicast and IPv6 link-local multicast to leave those on the default flooding path.
- Bulk delete filters only a subset of attributes and permanent state; unsupported state/protocol combinations must remain rejected.

## Test Signals
- Add, replace, get, dump, delete, and bulk-delete MDB entries for IPv4 and IPv6 groups, with and without source VNI, remote VNI, remote port, ifindex, and route protocol.
- Validate rejection of non-permanent creates, VID, non-multicast group addresses, multicast source addresses, source on all-zero group, source lists without filter mode, and empty `(*,G)` INCLUDE lists.
- Send multicast traffic through exact `(S,G)`, `(*,G)`, all-zero fallback, link-local multicast, blocked remote, INCLUDE, and EXCLUDE configurations; verify replication count and remote selection.
- Exercise replace while traffic is active to catch RCU destination lifetime issues.
- Confirm `ip mdb show`/netlink dumps remain consistent across partial dumps using `mdb_seq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c

## Purpose
`vxlan_multicast.c` manages underlay multicast group membership for VXLAN sockets. It joins and leaves IPv4 IGMP or IPv6 multicast groups for the device default remote group and, when VNI filtering is enabled, for per-VNI remote groups.

## Important APIs, Types, and Functions
- `vxlan_igmp_join()` and `vxlan_igmp_leave()` perform the family-specific socket multicast join/leave operations using the VXLAN UDP socket and target interface index.
- `vxlan_group_used()` determines whether another running VXLAN device sharing the same socket still needs a multicast group, avoiding premature leave.
- `vxlan_group_used_by_vnifilter()` checks default and per-VNI remote groups for VNI-filter devices.
- `vxlan_multicast_join()` joins the default group and then per-VNI groups when `VXLAN_F_VNIFILTER` is set.
- `vxlan_multicast_leave()` leaves the default group only when it is no longer used, then leaves eligible per-VNI groups.

## Control Flow
On device open, `vxlan_core.c` calls `vxlan_multicast_join()`. If the default remote address is multicast, it calls `vxlan_igmp_join()` using `default_dst.remote_ifindex`, treating `-EADDRINUSE` as success. For VNI-filter devices it then scans the VNI group list and joins multicast per-VNI remote groups that differ from the default group. If any per-VNI join fails, the function rolls back previous joins in the group list.

On device stop or group change, `vxlan_multicast_leave()` checks whether the default multicast group is still used by another running VXLAN device sharing the relevant socket and interface. If not, it leaves the group. VNI-filter leave then scans per-VNI nodes and leaves each multicast group that is no longer used by another device or VNI.

## State and Persistence Behavior
The file does not allocate persistent driver state. It mutates multicast membership state held by the kernel socket/network stack. Decisions are based on live `vxlan_net` device lists, socket refcounts, running state, default destination, and VNI-filter lists. State disappears when sockets/devices are released.

## Dependencies and Integration Points
The code depends on `ip_mc_join_group()`, `ip_mc_leave_group()`, `ipv6_sock_mc_join()`, `ipv6_sock_mc_drop()`, socket locking, rtnl dereference rules, and VXLAN private helpers. It is called from device open/stop, VNI-filter group update/delete paths, and changelink default group updates.

## Risks and Edge Cases
- Shared sockets mean group membership must not be dropped while any other VXLAN device or VNI on the socket still uses the group.
- The family is derived from the device default remote address; mixed or incorrectly initialized address families could make the wrong socket path run.
- VNI-filter scans use `list_for_each_entry_safe()` under RTNL assumptions; callers must hold appropriate serialization.
- Rollback in `vxlan_multicast_join_vnigrp()` leaves all earlier matching groups up to the last successful node; changes to iteration order could alter rollback coverage.
- IPv6 paths are compile-time gated by `CONFIG_IPV6`.

## Test Signals
- Bring up/down VXLAN devices with IPv4 and IPv6 multicast remotes and confirm IGMP/MLD membership changes.
- Open multiple VXLAN devices sharing a socket/group and verify stopping one device does not drop membership needed by the other.
- Add/delete per-VNI multicast groups on a VNI-filter device while up and verify joins/leaves and rollback on injected errors.
- Change default multicast remote/interface through rtnetlink and check leave/join ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_multicast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h

## Purpose
`vxlan_private.h` is the internal header shared by the VXLAN implementation files. It defines the private per-net and FDB data structures, hash helpers, address helpers, VNI-filter lookup helper, and cross-file function prototypes for core, VNI-filter, multicast, and MDB modules.

## Important APIs, Types, and Functions
- `struct vxlan_net` stores per-network-namespace VXLAN state: device list, UDP socket hash buckets, and nexthop notifier.
- `struct vxlan_fdb_key` and `struct vxlan_fdb` define the forwarding database key and entry, including rhashtable node, RCU head, timestamps, remotes list, state/flags, nexthop linkage, and owning VXLAN device pointer.
- `NTF_VXLAN_ADDED_BY_USER` marks user-added FDB entries beyond standard neighbor flags.
- Hash helpers `vni_head()` and `vs_head()` select VNI and socket hash buckets.
- Remote helpers `first_remote_rcu()` and `first_remote_rtnl()` return the first non-nexthop remote destination under the relevant locking context.
- Address helpers `vxlan_addr_equal()`, `vxlan_nla_get_addr()`, `vxlan_nla_put_addr()`, `vxlan_addr_is_multicast()`, and `vxlan_addr_size()` abstract IPv4/IPv6 support, with IPv6-disabled fallbacks.
- `vxlan_vnifilter_lookup()` retrieves a per-VNI node from a device VNI group using `vxlan_vni_rht_params`.
- Prototypes expose FDB update/delete/create, transmit, VNI-in-use validation, VNI-filter init/update/stats, multicast join/leave/group-used, and MDB netdevice/datapath APIs.

## Control Flow
This header does not implement high-level control flow, but it is on the hot path for both RX and TX. `vxlan_core.c` uses the hash helpers for socket/VNI lookup, FDB operations, and remote selection. `vxlan_vnifilter.c` uses the exported rhashtable params and lookup contract to maintain per-VNI state. `vxlan_multicast.c` uses address helpers and VNI group access. `vxlan_mdb.c` uses address helpers and `vxlan_xmit_one()` for multicast replication.

## State and Persistence Behavior
The structures declared here describe in-memory runtime state only. `struct vxlan_net` is allocated per net namespace by pernet operations; `struct vxlan_fdb` instances are allocated, inserted, aged, notified, and RCU-freed by `vxlan_core.c`. Address helper behavior changes with `CONFIG_IPV6`: without IPv6, IPv6 netlink addresses are rejected with `-EAFNOSUPPORT`.

## Dependencies and Integration Points
The header includes `linux/rhashtable.h` and relies on VXLAN public structures from `<net/vxlan.h>` included by users. It forms the internal ABI among `vxlan_core.c`, `vxlan_vnifilter.c`, `vxlan_multicast.c`, and `vxlan_mdb.c`. Its prototypes also reflect the public integration of VXLAN internals with netdevice operations and bridge/MDB rtnetlink.

## Risks and Edge Cases
- Inline helpers encode locking expectations: `first_remote_rcu()` is for RCU readers and `first_remote_rtnl()` for RTNL contexts. Using the wrong helper can produce lifetime or lockdep bugs.
- `first_remote_*()` returns `NULL` for nexthop-backed FDB entries; callers must handle nexthop state separately.
- IPv6-disabled helper variants reject IPv6 netlink input and only compare IPv4 addresses; new code must not assume IPv6 fields are valid without compile-time guards.
- `vxlan_vnifilter_lookup()` uses `rcu_dereference_rtnl()` and assumes callers are in an RTNL-compatible context or otherwise follow established lookup rules.

## Test Signals
- Build-test VXLAN with and without `CONFIG_IPV6`.
- Exercise FDB entries with normal remotes and nexthop-backed remotes to verify `first_remote_*()` caller behavior.
- Add/delete VNI-filter entries and ensure `vxlan_vnifilter_lookup()` correctly gates RX dispatch and stats.
- Netlink-test IPv4 and IPv6 address parsing/serialization paths, including short/invalid attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_vnifilter.c -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_vnifilter.c

## Purpose
`vxlan_vnifilter.c` implements VNI filtering for VXLAN collect-metadata mode. It lets a single VXLAN netdevice accept and track an explicit set or range of VNIs, optionally with per-VNI remote multicast/group destinations, per-VNI default FDB entries, socket VNI-hash registration, multicast membership management, statistics, netlink notifications, and RTM_GET/NEW/DELTUNNEL control.

## Important APIs, Types, and Functions
- `vxlan_vni_rht_params` defines the rhashtable used by `struct vxlan_vni_group`.
- Socket/VNI registration: `vxlan_vs_add_vnigrp()`, `vxlan_vs_del_vnigrp()`, and internal `vxlan_vs_add_del_vninode()` add/remove VNI nodes from the shared VXLAN socket VNI hash.
- Stats: `vxlan_vnifilter_count()`, `vxlan_vnifilter_stats_add()`, `vxlan_vnifilter_stats_get()`, and netlink stat fill helpers maintain per-VNI per-cpu counters.
- Netlink dump/notify: `vxlan_vnifilter_notify()`, `vxlan_vnifilter_dump_dev()`, and `vxlan_vnifilter_dump()` format RTM_NEWTUNNEL/DELTUNNEL/GETTUNNEL messages, coalescing contiguous ranges when stats are not requested.
- Group/default FDB management: `vxlan_update_default_fdb_entry()`, `vxlan_vni_update_group()`, `vxlan_vnilist_update_group()`, and `vxlan_vni_delete_group()` create/delete all-zero FDB entries and join/leave multicast groups for per-VNI remotes.
- VNI mutation: `vxlan_vni_add()`, `vxlan_vni_del()`, `vxlan_vni_update()`, `vxlan_vni_add_del()`, and `vxlan_process_vni_filter()` implement range add/delete/update from netlink attributes.
- Lifecycle and rtnl registration: `vxlan_vnigroup_init()`, `vxlan_vnigroup_uninit()`, `vxlan_vnifilter_init()`, and `vxlan_vnifilter_uninit()`.

## Control Flow
When a VXLAN device is configured with `VXLAN_F_VNIFILTER`, `vxlan_core.c` calls `vxlan_vnigroup_init()` during device init. User space then sends `RTM_NEWTUNNEL` or `RTM_DELTUNNEL` messages with `VXLAN_VNIFILTER_ENTRY` attributes. `vxlan_vnifilter_process()` verifies the target device is VXLAN and VNI filtering is enabled, parses each entry, validates VNI range and optional group address, then calls `vxlan_vni_add_del()`.

Adding a VNI first updates an existing node if present. New VNIs are rejected if `vxlan_vni_in_use()` finds a conflicting VXLAN device. The code allocates a node with per-cpu stats, inserts it into the VNI rhashtable, adds it to a sorted list, registers it on open sockets if the device is up, updates the default FDB entry for either the per-VNI group or device default remote, joins multicast if needed, and emits an RTM_NEWTUNNEL notification.

Deleting a VNI removes any per-VNI default FDB entry, leaves multicast membership if no other device/VNI uses it, removes the node from the rhashtable and sorted list, notifies RTM_DELTUNNEL, removes socket hash entries when up, and RCU-frees the node. Device uninit walks all VNIs and performs the same cleanup before destroying the VNI rhashtable.

Dumping walks either a selected VXLAN device or all VXLAN devices in the namespace. Without stats, adjacent VNIs with the same remote group are coalesced into ranges; with stats, entries are emitted individually because each VNI has separate counters.

## State and Persistence Behavior
State is per VXLAN device in `vxlan->vnigrp`, which contains a rhashtable and sorted list of `struct vxlan_vni_node` objects. Each node has per-cpu stats, VNI, remote IP, socket hash nodes for IPv4/IPv6, and RCU lifetime. The module also registers rtnetlink tunnel message handlers at VXLAN module init. No state persists to disk; user space must reapply VNI filters after reboot/recreate.

## Dependencies and Integration Points
The file depends on rtnetlink tunnel message ABI (`RTM_GETTUNNEL`, `RTM_NEWTUNNEL`, `RTM_DELTUNNEL`, `tunnel_msg`, `VXLAN_VNIFILTER_*` attrs), rhashtable, RCU lists, per-cpu u64 stats, VXLAN FDB helpers from `vxlan_core.c`, multicast helpers from `vxlan_multicast.c`, and device/socket state from `<net/vxlan.h>`. It integrates with receive dispatch in `vxlan_vs_find_vni()`, transmit/receive stat accounting in `vxlan_core.c`, multicast membership on add/delete/group update, and default FDB creation for per-VNI remote groups.

## Risks and Edge Cases
- Range operations are not transactionally rolled back: an error midway through `vxlan_vni_add_del()` can leave earlier VNIs changed.
- `vxlan_vni_add()` inserts the VNI into the hash/list before `vxlan_vni_update_group()`; if group/FDB update fails, the node may remain unless higher layers repair it.
- Multicast group changes interact with shared socket membership; `vxlan_group_used()` must be correct to avoid dropping groups still in use.
- Sorted-list/range coalescing assumes list order remains ascending by VNI. Changes to insertion order would break dump compression and cursor behavior.
- Stats use per-cpu u64 sync; readers must keep the fetch-retry pattern to avoid torn counters on 32-bit systems.
- `vxlan_process_vni_filter()` increments `vnis` even if an entry fails, but returns the error; callers must handle partial application.

## Test Signals
- Add/delete single VNIs and ranges through RTM_NEWTUNNEL/DELTUNNEL, including duplicate adds, missing entries, invalid ranges, and VNI conflict with another VXLAN device.
- Configure per-VNI IPv4/IPv6 multicast groups and verify default FDB entries, socket VNI hash dispatch, IGMP/MLD joins/leaves, and notifications.
- Dump VNI filters with and without stats and confirm range coalescing only happens without stats.
- Send traffic across multiple VNIs in collect-metadata mode and verify per-VNI RX/TX/drop/error counters.
- Inject failures in FDB update or multicast join paths to check partial-add cleanup expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_vnifilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig

## Purpose
`drivers/net/wan/Kconfig` defines the kernel configuration menu for WAN interface support and the protocol/card drivers in this directory. It gates the generic HDLC layer, HDLC protocol personalities, WAN card drivers, firmware build options, and related X.25/LAPB pseudo devices.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. Important symbols include:
- `WAN`: top-level boolean menu controlling WAN interface support.
- `HDLC`: generic HDLC layer, tristate, required by most synchronous WAN card drivers.
- `HDLC_RAW`, `HDLC_RAW_ETH`, `HDLC_CISCO`, `HDLC_FR`, `HDLC_PPP`, `HDLC_X25`: protocol modes layered on generic HDLC.
- `PCI200SYN`, `WANXL`, `PC300TOO`, `N2`, `C101`, `FARSYNC`, `FSL_QMC_HDLC`, `FSL_UCC_HDLC`, `SLIC_DS26522`, `IXP4XX_HSS`, `LAPBETHER`: device/driver feature symbols.
- `WANXL_BUILD_FIRMWARE`: optional firmware rebuild path for the wanXL driver.
- It also sources `drivers/net/wan/framer/Kconfig`.

## Control Flow
Kconfig is evaluated by the kernel configuration system. Enabling `WAN` reveals subordinate WAN options. Enabling `HDLC` makes the protocol-specific HDLC modules selectable. Individual card symbols declare dependencies such as `HDLC && ISA`, `HDLC && PCI`, `HAS_IOPORT`, platform controller symbols, or protocol dependencies. The selected symbols drive compilation through the directory `Makefile`.

## State and Persistence Behavior
Selected values persist in the kernel build `.config`. At runtime this file has no behavior. Tristate symbols determine whether drivers are built in, built as modules, or omitted.

## Dependencies and Integration Points
The file integrates with the kernel Kconfig system and `drivers/net/wan/Makefile`. `CONFIG_C101` specifically controls compilation of `c101.o` and depends on `HDLC && ISA`. `HDLC_X25` depends on compatible LAPB/HDLC tristate combinations. `SLIC_DS26522` selects `BITREVERSE` and is constrained to specific SoCs or `COMPILE_TEST`.

## Risks and Edge Cases
- Dependency expressions must keep module/built-in combinations valid; `HDLC_X25` has a more complex LAPB expression to avoid unusable link combinations.
- Legacy ISA drivers such as `C101` are only visible with ISA and HDLC enabled, which affects test coverage on modern configs.
- `WANXL_BUILD_FIRMWARE` invokes toolchain requirements and should stay optional and disabled by default for normal builds.
- Moving or renaming symbols requires matching `Makefile`, module alias, and user documentation updates.

## Test Signals
- Run `olddefconfig`/`menuconfig` combinations for `WAN`, `HDLC`, and each driver symbol.
- Build-test `CONFIG_C101=m`, `CONFIG_HDLC=m`, and representative PCI/platform WAN drivers.
- Check that invalid LAPB/HDLC tristate combinations hide or disable `HDLC_X25`.
- Verify `WANXL_BUILD_FIRMWARE=y` only builds when firmware build prevention is disabled and the expected tools are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wan/Makefile

## Purpose
`drivers/net/wan/Makefile` maps WAN Kconfig symbols to object files and defines the optional wanXL firmware build pipeline. It is the build-system counterpart to `drivers/net/wan/Kconfig`.

## Important APIs, Types, and Functions
- Object mappings: `obj-$(CONFIG_HDLC) += hdlc.o`, protocol modules (`hdlc_raw.o`, `hdlc_cisco.o`, etc.), card drivers (`c101.o`, `n2.o`, `farsync.o`, `wanxl.o`, `pci200syn.o`, `pc300too.o`, `ixp4xx_hss.o`, `fsl_qmc_hdlc.o`, `fsl_ucc_hdlc.o`, `slic_ds26522.o`), and `obj-y += framer/`.
- Firmware artifacts: `clean-files := wanxlfw.inc`, `targets += wanxlfw.inc wanxlfw.bin wanxlfw.o`.
- `CROSS_COMPILE_M68K` and conditional `M68KCC`/`M68KLD` selection support building wanXL QUICC firmware on non-m68k hosts.
- Custom commands: `build_wanxlfw`, `m68kld_bin_o`, and `m68kas_o_S` transform `wanxlfw.S` to object, binary, then C include data when `CONFIG_WANXL_BUILD_FIRMWARE=y`.

## Control Flow
During kbuild, selected `CONFIG_*` values append object files to the directory build. The `framer/` subdirectory is always descended through `obj-y`. When `WANXL_BUILD_FIRMWARE` is enabled, kbuild compiles `wanxlfw.S` with an m68k assembler/compiler, links a raw binary at text address `0x1000`, converts it to a C byte array include using `hexdump` and `sed`, and makes `wanxl.o` depend on that generated include.

## State and Persistence Behavior
The file creates build artifacts only in the object tree. Generated `wanxlfw.inc`, `.bin`, and `.o` are declared as targets/clean files so kbuild can track and remove them. There is no runtime state.

## Dependencies and Integration Points
This Makefile depends on Kconfig symbols from the same directory, kbuild `if_changed`/`if_changed_dep` infrastructure, the m68k toolchain for firmware rebuilding, and source files such as `c101.c`, `hdlc*.c`, `wanxl.c`, and `wanxlfw.S`. `CONFIG_C101` directly builds the C101 driver researched in this work item.

## Risks and Edge Cases
- Firmware rebuild depends on external m68k tools unless building on m68k; missing tools will fail builds only when `WANXL_BUILD_FIRMWARE=y`.
- Generated firmware include content is produced by shell text processing; changes to formatting commands can affect C syntax consumed by `wanxl.o`.
- `obj-y += framer/` means the subdirectory is visited regardless of top-level `WAN` object choices; its own Kconfig/Makefile must gate actual objects correctly.
- Object names must stay synchronized with Kconfig symbols and source filenames.

## Test Signals
- Build representative configs with `CONFIG_C101=m`, `CONFIG_HDLC=m`, and no WAN drivers to confirm object selection.
- Run `make clean` or inspect clean targets to verify generated wanXL firmware artifacts are removed.
- Test `CONFIG_WANXL_BUILD_FIRMWARE=y` on m68k and non-m68k toolchain environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/c101.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/c101.c

## Purpose
`c101.c` is a Linux network driver for the Moxa C101 SuperSync ISA synchronous serial WAN card. It exposes the card as a generic HDLC network device, configures the Hitachi HD64570 SCA controller through a memory-mapped ISA window, handles carrier/clock settings, and delegates most HDLC ring and transmit/receive mechanics to the shared `hd64570.c` implementation.

## Important APIs, Types, and Functions
- Module parameter: `hw` is a string of card descriptors in `irq,ram:irq,ram...` format.
- Hardware constants: `C101_PAGE`, `C101_DTR`, `C101_SCA`, `C101_WINDOW_SIZE`, `C101_MAPPED_RAM_SIZE`, `RAM_SIZE`, `TX_RING_BUFFERS`, `RX_RING_BUFFERS`, and `CLOCK_BASE`.
- Main state type: `card_t` stores the netdevice, TX lock, mapped memory base, physical window, sync serial settings, ring state, SCA register shadow values, IRQ, current page, and global linked-list pointer. `typedef card_t port_t` adapts the single-port card to shared SCA helper expectations.
- I/O helpers/macros: `sca_in`, `sca_out`, `sca_inw`, `sca_outw`, `openwin()`, `sca_get_page()`, and shared adapter macros such as `port_to_card()`, `winbase()`, and `get_port()`.
- Interrupt/control: `sca_msci_intr()` handles SCA modem/status events; `set_carrier()` maps DCD status from MSCI1 to netdev carrier state; `c101_set_iface()` programs clock source selection.
- Netdevice operations: `c101_open()`, `c101_close()`, `c101_ioctl()`, `c101_siocdevprivate()`, with `ndo_start_xmit = hdlc_start_xmit`.
- Probe/lifecycle: `c101_run()` validates parameters, allocates `alloc_hdlcdev()`, requests IRQ and memory window, maps hardware, initializes SCA/rings, registers the HDLC device, and links it into `first_card`; `c101_init()` parses the `hw` module parameter; `c101_cleanup()` unregisters and destroys all cards.

## Control Flow
Module initialization requires the `hw` parameter. `c101_init()` prints the driver version and parses one or more `irq,ram` pairs separated by `:`. Each pair calls `c101_run()`, which rejects invalid IRQs and memory windows, allocates card/netdevice state, requests the IRQ using shared `sca_intr`, claims and maps the ISA memory window, resets/initializes the card window and DTR, calls shared `sca_init()`, configures netdevice and HDLC callbacks, registers the HDLC device, initializes SCA port memory, sets initial carrier, and appends the card to the global list.

Opening the interface calls `hdlc_open()`, asserts DTR, enables RTS through the SCA channel used by this board, calls `sca_open()`, configures interrupt enables for TX and carrier-detect status, updates carrier, enables SCA interrupt routing, and applies clock/interface settings with `c101_set_iface()`. Closing reverses the active hardware state by calling `sca_close()`, dropping DTR/RTS, and closing the HDLC layer.

`c101_ioctl()` handles `IF_GET_IFACE` by returning `sync_serial_settings`, handles `IF_IFACE_SYNC_SERIAL` for privileged updates to clock type and loopback, and delegates other settings to `hdlc_ioctl()`. `c101_set_iface()` translates `CLOCK_EXT`, `CLOCK_TXFROMRX`, `CLOCK_INT`, and `CLOCK_TXINT` into SCA RX/TX clock register bits and calls `sca_set_port()`.

## State and Persistence Behavior
State is runtime-only. A linked list rooted at `first_card` tracks initialized cards for cleanup. Each card stores SCA ring indices, mapped window address, IRQ, current page, line settings, and carrier-related shadows. The driver does not persist settings; module reload requires the `hw` parameter again and resets default clock type to `CLOCK_EXT`.

Hardware memory and IRQ resources are explicitly acquired in `c101_run()` and released in `c101_destroy_card()`. Netdevice registration persists only while the module/card instance is loaded.

## Dependencies and Integration Points
The driver depends on the generic HDLC core (`alloc_hdlcdev()`, `register_hdlc_device()`, `hdlc_open()`, `hdlc_close()`, `hdlc_ioctl()`, `hdlc_start_xmit()`), Linux ISA memory/IRQ APIs, user capability checks, and the shared HD64570 SCA support included directly via `#include "hd64570.c"`. Kconfig exposes it as `CONFIG_C101`, and the WAN Makefile builds it as `c101.o`.

## Risks and Edge Cases
- The driver is legacy ISA hardware code with direct memory-mapped I/O and an included C implementation. Build and runtime coverage are likely sparse on modern systems.
- `hw` parsing accepts partial success: invalid trailing parameters can still return success if at least one card initialized.
- `request_irq()` is called before memory window mapping; `c101_destroy_card()` must tolerate partially initialized fields, which it does through `irq`/`win0base` checks.
- IRQ validation excludes IRQ 6 with a FIXME, but hardware/platform conflicts are otherwise user-provided.
- Carrier detect is wired through MSCI1 while traffic uses MSCI0, leading to non-obvious interrupt and register handling.
- `c101_set_iface()` is callable from ioctl while the device may be running; hardware register updates rely on existing serialization assumptions from the HDLC/WAN stack.

## Test Signals
- Build-test `CONFIG_C101=m` with `CONFIG_HDLC=m` and `CONFIG_ISA=y`.
- Load without `hw` and verify initialization fails cleanly; load with invalid IRQ/RAM values and confirm errors with no resource leaks.
- On hardware or emulation, open/close the interface, verify DTR/RTS transitions, carrier changes from DCD, and HDLC transmit/receive.
- Exercise `SIOCWANDEV` get/set for all supported clock types and invalid loopback/clock values, including capability enforcement.
- Unload after partial and successful initialization to verify IRQ, memory region, ioremap, netdevice, and card allocations are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/c101.c -->
