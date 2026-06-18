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
