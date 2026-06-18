# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004563`: lines 1-9756, `Docs/researches/chunks/subset-b-004563_research.md`
- `subset-b-004564`: lines 9757-11784, `Docs/researches/chunks/subset-b-004564_research.md`

## Chunk Research

### subset-b-004563: lines 1-9756

# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.c lines 1-9756

Chunk ID: `subset-b-004563`

## Chunk Scope

This chunk covers the first 9,756 lines of Mellanox/NVIDIA Spectrum `mlxsw` router offload logic. It defines the core in-memory model for router interfaces, virtual routers, LPM trees, FIB nodes, neighbors, nexthops, nexthop objects, IP-in-IP and NVE decapsulation, multicast route tables, route-event work items, RIF counters and MAC profiles, and most address-to-RIF orchestration.

The chunk ends at the start of `mlxsw_sp_router_netdevice_interesting()`, after it has identified LAG, bridge, Spectrum port, IPIP overlay, L3 master, and VLAN devices as candidates. The rest of that helper, netdevice notifier handling, concrete RIF operation tables, and router init/fini wiring are in the next chunk.

## Purpose

This code is the router control plane for Spectrum ASIC offload. It listens to Linux routing, nexthop, neighbor, address, multicast route, and netdevice state, mirrors the relevant state in driver-owned data structures, and programs hardware tables through `mlxsw` register payloads.

Within this span, the driver primarily:

- Allocates and manages router interfaces (RIFs) and maps them to Linux netdevices, FIDs, virtual routers, multicast tables, counters, MAC profiles, and hardware RIF indices.
- Maintains virtual routers per Linux FIB table and binds IPv4/IPv6 FIBs to LPM trees whose prefix-bin layout matches currently installed prefixes.
- Converts IPv4 and IPv6 FIB notifications into hardware route entries (`RALUE`) with actions for remote forwarding, local delivery, traps, blackholes, unreachable/prohibit routes, IPIP decap, and NVE decap.
- Converts neighbor and nexthop state into adjacency table entries (`RATR`) and RAUHT neighbor entries, with KVDL-backed ECMP groups and trap fallback when offload is unavailable.
- Handles kernel nexthop objects, including resilient nexthop groups, bucket replacement, bucket activity polling, and nexthop hardware statistics.
- Tracks IP-in-IP overlay devices and promotes/demotes matching local routes into decap routes when tunnel state and local underlay addresses allow offload.
- Bridges L3 address events to the correct RIF type for ports, VLANs, LAGs, bridges, bridge VLAN PVIDs, and macvlan/VRRP MACs.
- Exposes offload statistics through RIF counters, neighbor counters, nexthop counters, devlink DPIPE counters, and `netdev_offload_xstats`.

## Important APIs, Types, and State

Important structures defined or driven in this chunk:

- `struct mlxsw_sp_router`: central router state owned by `struct mlxsw_sp`. Relevant fields used here include `crif_ht`, `rifs_table`, `rifs`, `rif_mac_profiles_idr`, `vrs`, `neigh_ht`, `nexthop_group_ht`, `nexthop_ht`, `nexthop_list`, LPM tree state, delayed neighbor/probe/activity works, `ipip_list`, notifier blocks, RIF/IPIP operation arrays, `nve_decap_config`, `router->lock`, loopback CRIF, adjacency group sizing, resilient nexthop group list, group refcount, and trap adjacency index.
- `struct mlxsw_sp_crif`: a canonical netdevice-to-RIF anchor stored in `crif_ht`. It lets nexthops bind to a device before a RIF exists, and it owns the list of nexthops using that device.
- `struct mlxsw_sp_rif`: common RIF object containing `crif`, tracked netdevice reference, neighbor list, FID, MAC/MTU, hardware RIF index, MAC profile ID, number of occupied RIF entries, VR ID, operation table, `mlxsw_sp` backpointer, and ingress/egress counter state.
- `struct mlxsw_sp_rif_subport` and `struct mlxsw_sp_rif_ipip_lb`: RIF specializations for routed port VLANs and IPIP loopback RIFs.
- `struct mlxsw_sp_rif_ops`: RIF polymorphism hooks for setup, hardware configure/deconfigure, FID acquisition, and FDB deletion. The concrete operation tables are later in the file.
- `struct mlxsw_sp_vr`, `struct mlxsw_sp_fib`, `struct mlxsw_sp_fib_node`, `struct mlxsw_sp_fib_entry`, `struct mlxsw_sp_fib4_entry`, and `struct mlxsw_sp_fib6_entry`: virtual router, per-protocol FIB, prefix node, and IPv4/IPv6 route-entry state.
- `struct mlxsw_sp_lpm_tree` and `struct mlxsw_sp_prefix_usage`: hardware LPM tree layout state, including per-prefix refcounts and shared tree refcounts.
- `struct mlxsw_sp_neigh_entry`: held kernel neighbor reference plus RIF index, cached MAC, connection state, associated nexthops, optional flow counter, and RIF/router list membership.
- `struct mlxsw_sp_nexthop`, `struct mlxsw_sp_nexthop_group_info`, `struct mlxsw_sp_nexthop_group`, `struct mlxsw_sp_nexthop_group_vr_entry`, and `struct mlxsw_sp_nexthop_counter`: driver representation of IPv4/IPv6 route nexthops and kernel nexthop objects, including weights, normalized ECMP distribution, adjacency indices, offload/update flags, per-VR users, resilient buckets, and counters.
- `struct mlxsw_sp_ipip_entry` from the IPIP support layer: referenced here for overlay device tracking, loopback RIF management, decap route linkage, and IPIP nexthop programming.
- `struct mlxsw_sp_fib_event_work` and `struct mlxsw_sp_netevent_work`: heap work items that carry notifier payloads out of atomic/RCU notifier context into mlxsw workqueues where `router->lock` and sometimes RTNL can be taken.

Important exported or cross-module functions in this chunk include:

- RIF/counter helpers: `mlxsw_sp_rif_counter_value_get()`, `mlxsw_sp_rif_counter_alloc()`, `mlxsw_sp_rif_counter_free()`, `mlxsw_sp_rif_by_index()`, `mlxsw_sp_rif_index()`, `mlxsw_sp_rif_dev_ifindex()`, `mlxsw_sp_rif_has_dev()`, `mlxsw_sp_rif_dev_is()`, and `mlxsw_sp_rif_destroy_by_dev()`.
- Neighbor helpers: `mlxsw_sp_rif_neigh_next()`, `mlxsw_sp_neigh_entry_type()`, `mlxsw_sp_neigh_entry_ha()`, `mlxsw_sp_neigh4_entry_dip()`, `mlxsw_sp_neigh6_entry_dip()`, `mlxsw_sp_neigh_counter_get()`, `mlxsw_sp_neigh_entry_counter_update()`, and `mlxsw_sp_neigh_ipv6_ignore()`.
- Nexthop helpers: `mlxsw_sp_nexthop_next()`, `mlxsw_sp_nexthop_is_forward()`, `mlxsw_sp_nexthop_ha()`, `mlxsw_sp_nexthop_indexes()`, `mlxsw_sp_nexthop_rif()`, `mlxsw_sp_nexthop_group_has_ipip()`, `mlxsw_sp_nexthop_counter_get()`, `mlxsw_sp_nexthop_counter_enable()`, `mlxsw_sp_nexthop_counter_disable()`, and `mlxsw_sp_nexthop_eth_update()`.
- IPIP/NVE helpers: `mlxsw_sp_ipip_dev_ul_tb_id()`, `__mlxsw_sp_ipip_entry_update_tunnel()`, `mlxsw_sp_ipip_entry_demote_tunnel()`, `mlxsw_sp_ipip_demote_tunnel_by_saddr()`, `mlxsw_sp_router_nve_promote_decap()`, and `mlxsw_sp_router_nve_demote_decap()`.
- Bridge/VLAN and address event helpers: `mlxsw_sp_router_bridge_vlan_add()`, `mlxsw_sp_port_vlan_router_leave()`, `mlxsw_sp_rif_macvlan_del()`, plus IPv4/IPv6 address notifier callbacks in this chunk.

Key hardware registers touched through payload pack/query/write helpers include `RITR` for RIFs and counters, `RICNT` for RIF counter fetch/clear, `RALTA`/`RALST`/`RALTB` for LPM tree allocation/layout/binding, `RAUHT`/`RAUHTD` for neighbor table update and activity dump, `RATR`/`RATRAD` for adjacency entries and activity, `RALEU` for mass route adjacency update, and `RALUE` for route entries.

## Control Flow

### RIF Counters and RIF Base Model

The file starts by defining CRIFs, common RIFs, RIF parameters, subport RIFs, IPIP loopback RIFs, RIF operations, and MAC profiles. Counter helpers query and edit `RITR`/`RICNT` state, allocate counter IDs from the RIF counter sub-pool, clear stale counter data before enabling, and gate egress DPIPE counters based on devlink DPIPE table settings.

Later RIF creation uses the common model to allocate a VR, allocate one or two contiguous RIF table entries through `gen_pool`, create the correct RIF specialization, hold the netdevice, acquire an FID when the RIF type needs one, configure hardware through `ops->configure()`, add the RIF to multicast routing tables, sync pre-existing neighbors and nexthops, enable stats if requested, and then publish it in `router->rifs`. Destruction reverses this: mark the RIF gone, push pending L3 stats, remove from MR tables, deconfigure hardware, release FID/netdevice/index/VR, and free a destroyable CRIF.

### Virtual Routers and LPM Trees

`mlxsw_sp_vr_get()` maps Linux routing table IDs to Spectrum VRs, squashing local/default/main tables into main for unicast offload. A VR owns IPv4 and IPv6 `struct mlxsw_sp_fib` instances and multicast routing tables. A VR is destroyed only when its RIF count, unicast FIB nodes, and multicast tables are empty.

The LPM tree code tracks which prefix lengths are present in hardware. When a new prefix length appears, `mlxsw_sp_fib_lpm_tree_link()` constructs or reuses an LPM tree with the added prefix bin, then replaces matching VR bindings through `RALTB`. When a prefix length disappears, it attempts the inverse replacement. The replacement is global for all VRs using the protocol's old tree, with rollback on errors.

### IPIP and NVE Decapsulation

The IPIP section tracks offloadable overlay netdevices in `router->ipip_list`. Registration can create an IPIP entry with a loopback RIF, remote address programming through IPIP ops, and local source-address conflict handling. If another tunnel already uses the same local underlay source address in the same underlay table, the existing tunnel is demoted because the hardware conflict mode is not implemented.

An IPIP entry can be promoted into a decap route when a matching local underlay address route exists and the overlay is up. Promotion allocates a KVDL tunnel adjacency entry, possibly increases parsing depth, links the route to the IPIP entry, changes the FIB entry type to `MLXSW_SP_FIB_ENTRY_TYPE_IPIP_DECAP`, and rewrites the route. Demotion reverses the tunnel linkage and changes the route back to a trap.

Loopback RIF updates are disruptive because RIFs cannot be edited. `__mlxsw_sp_ipip_entry_update_tunnel()` demotes decap first so `RALUE` does not reference a destroyed RIF, recreates the loopback RIF when necessary, updates nexthops if requested, and re-promotes decap if the overlay is up. NVE decap is similar at the route-entry level but uses one `router->nve_decap_config` and an externally supplied tunnel index instead of IPIP entry ownership.

### Neighbor State

Neighbor entries are keyed by kernel `struct neighbour *` in `neigh_ht`, hold a neighbor reference, and are linked to their RIF and the nexthops using them. Neighbor events are scheduled from `NETEVENT_NEIGH_UPDATE` into workqueue context. The work item snapshots MAC, NUD state, and dead state under the neighbor lock, then under `router->lock` creates or updates the driver neighbor entry, writes or deletes the `RAUHT` hardware neighbor, toggles `NTF_OFFLOADED`, updates dependent nexthops, and destroys disconnected unused entries.

Two delayed works keep neighbor state fresh. `neighs_update.dw` periodically dumps ASIC neighbor activity through `RAUHTD` and sends kernel neighbor events for active entries. It also refreshes nexthop neighbors so the kernel treats them as active while traffic is forwarded in hardware. `nexthop_probe_dw` periodically sends probes for unresolved nexthop neighbors to break the case where hardware traffic prevents normal kernel resolution.

IPv6 link-local neighbors are intentionally ignored because packets with link-local destination addresses are trapped after LPM lookup and do not need neighbor-table hardware programming.

### Nexthop Groups and Adjacencies

Nexthops can be Ethernet or IPIP. A nexthop binds to a CRIF, optional RIF, neighbor or IPIP entry, weight, action (`FORWARD`, `DISCARD`, `TRAP`), hardware counter, and update/offload flags. Nexthop groups represent IPv4 `fib_info`, IPv6 route sibling sets, or kernel nexthop objects. Groups track all FIB entries using them and all VR/protocol bindings so adjacency-index changes can be propagated with `RALEU`.

`mlxsw_sp_nexthop_group_refresh()` is the central reconciliation path. It detects offloadability changes, allocates or reallocates KVDL adjacency space, normalizes weights by GCD, rounds group sizes to hardware-supported allocation sizes, assigns `num_adj_entries`, writes `RATR` entries, refreshes route hardware flags, and either updates all FIB users from trap to adjacency or mass-updates existing route entries to a new adjacency range. On allocation or programming failure it clears adjacency validity, marks nexthops not offloaded, updates FIB entries to trap, and frees old KVDL space when applicable.

For normal groups, disconnected nexthops are omitted. For resilient nexthop groups, disconnected buckets remain programmed as traps so bucket identity is preserved. Periodic `RATRAD` activity polling reports resilient bucket activity to the nexthop core, and bucket replacement can be forced or attempted as an inactive-only replacement with a post-write query/compare check.

Kernel nexthop object handling validates unsupported FDB/encap combinations, rejects group entries without a gateway unless they are IPIP-device nexthops or reject nexthops, creates single/group/resilient group info, replaces existing groups by swapping `nhgi` pointers, and defers object destruction while routes still reference the object. Shared counters are stored in an xarray keyed by nexthop object ID.

### FIB Entries and Route Programming

FIB nodes are stored in per-VR/per-protocol rhashtables and lists. Each node has at most one active `fib_entry`, representing the currently selected kernel route for that prefix. Node creation links the prefix length into the LPM tree; node removal unlinks it and may shrink the LPM tree layout.

Route operations use `RALUE`. Remote routes use the nexthop group's adjacency index when available, a preallocated trap adjacency when there is a RIF but no valid adjacency, or ingress trap action otherwise. Local routes point to the RIF from the nexthop group. Trap, blackhole, unreachable/prohibit, IPIP decap, and NVE decap each pack distinct `RALUE` actions. Successful writes update kernel hardware flags: IPv4 through `fib_alias_hw_flags_set()`, IPv6 through `fib6_info_hw_flags_set()`, and nexthop objects through nexthop flag helpers.

IPv4 replace creates a FIB node, builds a `mlxsw_sp_fib4_entry`, gets or creates the nexthop group, links the group to the route's VR/protocol, determines the route type from `fen_info->type`, then links the entry to hardware. Main-table routes are not allowed to replace local-table routes for the same prefix. IPv4 delete looks up an exact entry by table, DSCP, route type, and `fib_info`.

IPv6 replace ignores multicast and cloned routes, rejects source-specific routes, builds `mlxsw_sp_rt6` references for all siblings, creates or reuses an IPv6 nexthop group, determines local/trap/blackhole/unreachable/remote/IPIP/NVE type, and links the entry. Append/delete paths update a multipath IPv6 entry by adding or removing route siblings and rebuilding the group.

Multicast FIB notifications use the per-VR MR tables from `spectrum_mr`: route add/delete and VIF add/delete acquire the VR, choose IPv4 or IPv6 MR table by family, and delegate to `mlxsw_sp_mr_*` helpers.

### Notifier and Workqueue Flow

FIB notifiers run under RCU and allocate `mlxsw_sp_fib_event_work` with `GFP_ATOMIC`. IPv4 work holds `fib_info`; IPv6 work builds a held array of route siblings; multicast work holds `mfc` or netdevice references. Workqueue callbacks take `router->lock` and, for multicast work, RTNL as well, then perform route changes and release held references.

FIB rule notifications are validated synchronously. Non-default, non-l3mdev rules are rejected for IPv4, IPv6, IPMR, and IP6MR unless they only affect locally generated loopback traffic. IPv4 route adds with IPv6 gateways are rejected.

Netevent work handles neighbor updates, ECMP hash seed changes, and IPv4 forwarding priority updates. Hash and priority updates trigger router reinitialization paths declared in this chunk but completed later.

### Address Events and RIF Selection

RIF creation/destruction is driven by IPv4/IPv6 address events and by bridge VLAN PVID updates. `mlxsw_sp_rif_should_config()` creates a RIF on `NETDEV_UP` when none exists, and removes one on `NETDEV_DOWN` when the device's IPv4/IPv6 address lists are empty. Macvlans do not own RIFs; they piggyback on the lower device's RIF and only program FDB/VRRP MAC state.

`__mlxsw_sp_inetaddr_event()` dispatches by device class:

- Spectrum port devices create routed port VLAN/subport RIFs unless enslaved to bridge/LAG unless the caller requests nomaster handling.
- LAG masters replay the event to lower Spectrum ports.
- Bridge masters create bridge/FID or VLAN RIFs, with 802.1ad bridge IP addresses rejected.
- VLAN devices create port VLAN, LAG VLAN, or bridge VLAN RIFs depending on their real device.
- Macvlan devices add or remove their MAC in the lower RIF's FDB and program VRRP IDs for VRRP MAC ranges.

IPv4 valid-address events can return extack errors synchronously. IPv6 non-UP address events are punted to workqueue context so RTNL and `router->lock` can be taken outside RCU notifier context.

Port MAC/MTU changes are handled by removing the old RIF FDB entry, replacing or editing the MAC profile, rewriting `RITR`, adding the new FDB entry, updating multicast RIF MTU state, and then updating the cached RIF MAC/MTU. The pre-change-address notifier prevents a change that would exceed the hardware MAC profile limit when the current profile is shared.

## State and Persistence Behavior

All persistence is in kernel memory and hardware tables, not on disk. The driver keeps software mirrors so it can reconcile asynchronous kernel events with hardware state:

- `router->rifs` mirrors allocated hardware RIF indices. `rifs_count` and `rif_mac_profiles_count` back occupancy reporting and extack capacity checks.
- `router->vrs` persists VRs while any RIF, unicast route, or multicast route exists for a table. VR teardown is reference-like but based on emptiness checks.
- `router->lpm.proto_trees`, per-tree `prefix_ref_count`, and per-tree refcounts persist prefix layout decisions and are replayed into VR bindings as prefix lengths appear/disappear.
- FIB nodes and entries mirror selected IPv4/IPv6 routes. FIB entries hold references to `fib_info` or `fib6_info` as needed to survive queued work and route replacement.
- Nexthop groups persist separately from routes so several FIB entries can share adjacency programming. Object nexthop groups can persist after deletion until all route users are gone.
- KVDL allocations persist hardware adjacency ranges and tunnel indices; they are freed during group refresh fallback, group destroy, decap demotion, or FIB deletion.
- Neighbor entries hold kernel neighbor references and cached MAC/offload state while connected or while any nexthop depends on them.
- IPIP entries persist while an overlay device remains registered and offloadable, unless demoted by local-address conflicts, overlay changes, or underlay constraints.
- RIF and nexthop counters persist only while enabled by DPIPE, HW stats, or netdev offload xstats. RIF stats are fetched with clear-on-read behavior and pushed before RIF destruction when netdev L3 xstats are enabled.

`router->lock` is the dominant serialization point for shared router data. RCU is used for netdevice and neighbor lookups from notifier or address-list context. Workqueue deferral is used whenever notifier context cannot sleep, cannot take RTNL, or needs object references held beyond the callback. Netdevice references use `netdev_hold()`/`netdev_put()` with trackers; neighbors use `neigh_hold()`/`neigh_release()` or `neigh_clone()`; route objects use `fib_info_hold()` and `fib6_info_hold()`.

## Dependencies and Integration Points

Kernel subsystems integrated in this chunk include:

- FIB notifier core for IPv4, IPv6, multicast route, VIF, nexthop, and FIB rule events.
- Nexthop object notifier APIs, including multipath groups, resilient groups, bucket replacement, activity reporting, and hardware stats reporting.
- Neighbor core (`arp_tbl`, `nd_tbl`, `neigh_lookup()`, `neigh_create()`, `neigh_event_send()`, NUD state, `NTF_OFFLOADED`).
- Netdevice, inetaddr, inet6addr, bridge, VLAN, LAG, macvlan, VRF/l3mdev, and RTNL APIs.
- Devlink DPIPE counter enablement and netdev offload xstats reporting.
- `rhashtable`, `idr`, `xarray`, `gen_pool`, `refcount_t`, atomics, delayed work, workqueues, RCU, and netdevice trackers.
- Internal mlxsw hardware and resource APIs: register pack/write/query helpers, KVDL allocation, flow/RIF counters, parsing depth, Spectrum port/VLAN/FID helpers, multicast routing helpers, span respin, and IPIP operation tables.

Major integration points with later or sibling code are the concrete RIF operation tables, router init/fini and notifier registration, Spectrum port bridge/LAG replay helpers, IPIP operation implementations in `spectrum_ipip`, multicast code in `spectrum_mr`, FID/bridge code in Spectrum switching modules, and DPIPE/stat readers that walk RIF, neighbor, and nexthop objects through the exported iteration helpers.

## Risks and Edge Cases

- The chunk is heavily asynchronous. Notifier payloads must hold every referenced object until workqueue execution; missing holds on `fib_info`, `fib6_info`, `mfc`, `net_device`, or `neighbour` would create use-after-free bugs.
- `router->lock` ordering with RTNL is sensitive. Some paths explicitly defer notifications to avoid taking `router->lock` recursively through xstats callbacks, while multicast and IPv6 address work take RTNL before the router lock.
- LPM tree replacement touches all VRs using the protocol default tree. Rollback must restore old bindings on partial failure or routes can point at an LPM layout that does not contain their prefix bins.
- Nexthop group refresh can reallocate adjacency ranges, write new entries, mass-update route users, and free old KVDL ranges. Errors must consistently fall back to traps and avoid leaking old or new KVDL allocations.
- `mlxsw_sp_nexthop_group_refresh()` uses trap fallback for allocation/programming failures. This preserves forwarding correctness through the kernel but can silently reduce hardware offload until warning logs or route flags are inspected.
- Resilient nexthop bucket replacement is race-sensitive. Non-forced replacement depends on activity query/compare semantics and the polling interval; too-small idle timers are forced to avoid reporting false inactive replacement.
- IPIP loopback RIF recreation creates a temporary invalid-reference risk for routes and adjacency entries. The code demotes decap before RIF destruction and migrates nexthops through a mock CRIF; regressions here can leave `RALUE`/`RATR` pointing at freed RIF indices.
- Only one NVE decap configuration is tracked. Attempting multiple simultaneous decap configs would trip warning paths or overwrite assumptions.
- RIF destroy marks `crif->rif = NULL` before nexthop/neighbor teardown. Any code assuming a non-NULL RIF while walking CRIF nexthops can fault or incorrectly program adjacency entries.
- IPv6 link-local neighbors are intentionally not programmed; changes to trap behavior for link-local traffic would need matching neighbor-table changes.
- IPv4 DSCP-specific routes are mirrored but not offloaded (`mlxsw_sp_fib4_entry_should_offload()` rejects nonzero DSCP). Route flags should show trap rather than offload.
- Local table routes are protected from replacement by main-table routes. Changes to kernel route priority semantics could expose stale local/trap behavior.
- Bridge VLAN PVID RIF migration must destroy conflicting VLAN-upper RIFs and migrate nexthops without unoffloading them unnecessarily. PVID churn with active routes is high-risk.
- MAC profile sharing and masked MAC matching mean address changes can fail when profile capacity is exhausted. The pre-change check must match the later replacement behavior.
- Counter fetches clear hardware counters. Calling RIF stat fetch in the wrong path can consume deltas before xstats reporting.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with IPv6, multicast routing, nexthop objects, resilient nexthop groups, bridge VLAN filtering, VRF/l3mdev, macvlan, and IPIP tunnel support enabled and disabled where configurable.
- IPv4 route tests for unicast, local, broadcast, blackhole, unreachable/prohibit, DSCP-specific routes, route replace/delete, local-vs-main priority, IPv6 gateway rejection on IPv4 routes, and offload/trap/offload_failed flag reporting.
- IPv6 route tests for normal routes, multipath sibling append/delete, local routes, anycast, blackhole, reject, multicast/cloned route ignore, source-specific route rejection, and route flag updates across replacement.
- Nexthop object tests for single, group, reject, device-only, IPIP-device, resilient group creation, group replacement, deletion while routes still reference the object, bucket replacement with and without force, bucket activity reporting, and HW stats deltas.
- Neighbor tests for ARP/ND resolution, MAC change, stale/dead neighbor replacement, unresolved nexthop probing, RAUHTD activity refresh, IPv6 link-local ignore behavior, and `NTF_OFFLOADED` toggling.
- ECMP resource tests that exhaust or fragment KVDL adjacency space, verify trap fallback, then verify recovery when resources become available.
- RIF lifecycle tests for routed ports, port VLANs, LAGs, bridge masters, VLAN uppers, bridge VLAN PVID changes, IP address add/remove, netdevice down with remaining addresses, and VRF table assignment.
- IPIP/NVE tests for overlay register/unregister, overlay up/down, MTU changes, underlay VRF moves, duplicate tunnel source addresses, local address route promotion/demotion, parsing-depth refcounts, and decap route flags.
- Macvlan/VRRP tests for macvlan add/remove on a lower RIF, VRRP IPv4/IPv6 MAC programming, and FDB cleanup during RIF deletion.
- Statistics tests for devlink DPIPE RIF/host/adj counters, netdev L3 offload xstats enable/disable, RIF destroy stat push, nexthop object HW stats, and clear-on-read delta handling.
- Concurrency/fault-injection tests for workqueue flushing during router teardown, notifier allocation failures, register write/query failures, RIF index exhaustion, MAC profile exhaustion, LPM tree exhaustion, KVDL allocation failures, and extack messages for unsupported configurations.

### subset-b-004564: lines 9757-11784

# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.c lines 9757-11784

## Scope and Purpose

This chunk covers the lower half of Spectrum router orchestration: CRIF registration for interesting netdevices, router-related netdevice notifier dispatch, LAG/VRF/address replay helpers, concrete RIF operation tables for subport, FID, VLAN, and IP-in-IP loopback router interfaces, underlay loopback RIF sharing, RIF table/resource initialization, IP-in-IP and multipath-hash global setup, DSCP-priority programming, and the top-level `mlxsw_sp_router_init()` / `mlxsw_sp_router_fini()` lifecycle.

The code is the integration layer between Linux netdevice/notifier state and Mellanox Spectrum hardware router resources. It translates netdevice topology changes, L3 interface creation, tunnel loopback needs, and routing hash policy into hardware register writes and driver-owned state (`router->crif_ht`, `router->rifs`, VR references, FID bindings, resource counters, notifier blocks).

## Important APIs, Types, and Functions

- `struct mlxsw_sp_crif` is the "candidate RIF" record keyed by `struct net_device *` in `router->crif_ht`. This chunk registers/unregisters CRIFs for devices that may later host a RIF and uses `crif->can_destroy` to defer freeing when netdevice unregister races with an existing RIF.
- `mlxsw_sp_crif_register()` / `mlxsw_sp_crif_unregister()` allocate, insert, remove, and eventually free CRIFs. Unregistration also walks `crif->nexthop_list` and calls `mlxsw_sp_nexthop_type_fini()` so nexthops stop referencing the disappearing device.
- `mlxsw_sp_router_netdevice_event()` is the central netdevice notifier callback. Under `router->lock`, it handles `NETDEV_REGISTER` / `NETDEV_UNREGISTER`, offload xstats commands, IP-in-IP overlay/underlay events, router port address/MTU events, and VRF upper-device changes.
- `mlxsw_sp_router_port_offload_xstats_cmd()` and `mlxsw_sp_netdevice_offload_xstats_cmd()` implement L3 offload xstats enable, disable, used-report, and delta-report notifier commands for devices that already have a RIF.
- `mlxsw_sp_netdevice_router_port_event()` handles `NETDEV_CHANGEMTU`, `NETDEV_CHANGEADDR`, and `NETDEV_PRE_CHANGEADDR` by finding the lower `mlxsw_sp`, resolving the RIF, and delegating to router-port change validators / appliers.
- `mlxsw_sp_port_vrf_join()` / `mlxsw_sp_port_vrf_leave()` rebuild a RIF when a lower L3 device joins or leaves an L3 master, because the associated virtual router can change.
- `mlxsw_sp_netdevice_enslavement_replay()` and `mlxsw_sp_netdevice_deslavement_replay()` replay `NETDEV_UP` address events over an upper-device tree so existing addresses create RIFs when topology changes; rollback uses `mlxsw_sp_router_unreplay_inetaddr_up()`.
- `mlxsw_sp_router_port_join_lag()` / `mlxsw_sp_router_port_leave_lag()` program router membership for the default VID and all VLAN uppers when a Spectrum port joins or leaves a LAG.
- `struct mlxsw_sp_rif_ops` implementations in this chunk define hardware behavior for:
  - `mlxsw_sp_rif_subport_ops`: subport RIFs on a port/LAG plus VLAN.
  - `mlxsw_sp_rif_fid_ops`: bridge/FID RIFs.
  - `mlxsw_sp1_rif_vlan_ops` and `mlxsw_sp2_rif_vlan_ops`: VLAN RIFs, differing by eFID programming.
  - `mlxsw_sp1_rif_ipip_lb_ops` and `mlxsw_sp2_rif_ipip_lb_ops`: IP-in-IP loopback RIFs, differing by Spectrum generation underlay model.
- `mlxsw_sp_ul_rif_get()` / `mlxsw_sp_ul_rif_put()` create and reference-count generic underlay loopback RIFs per VR. Exported wrappers `mlxsw_sp_router_ul_rif_get()` and `mlxsw_sp_router_ul_rif_put()` expose this to other driver code under `router->lock`.
- `mlxsw_sp_rifs_init()` / `mlxsw_sp_rifs_fini()` allocate the RIF pointer table, create the `gen_pool` allocator, initialize MAC-profile IDR/counters, and register devlink occupancy callbacks.
- `mlxsw_sp_mp_hash_init()` builds and writes RECR2 multipath hash configuration from IPv4/IPv6 sysctls when `CONFIG_IP_ROUTE_MULTIPATH` is enabled.
- `mlxsw_sp_router_init()` constructs the router subsystem, initializes all subcomponents, registers kernel notifiers, and includes a complete reverse-order error unwind path. `mlxsw_sp_router_fini()` unregisters notifiers, flushes ordered work, and tears everything down.

## Control Flow

Router initialization is staged in dependency order. `mlxsw_sp_router_init()` allocates `struct mlxsw_sp_router`, binds it to `mlxsw_sp`, selects generation-specific operations through `router_ops->init()`, initializes list/work structures, enables global routing hardware via `__mlxsw_sp_router_init()` / RGCR, initializes IP-in-IP state, CRIF hash table, RIF resources, nexthop tables, LPM, multicast router support, VRs, a fallback loopback RIF, neighbor handling, multipath hashing, DSCP mapping, and finally registers address, validator, netevent, netdevice, nexthop, and FIB notifiers. Every later step has a matching `goto` unwind that reverses only already-completed work.

Netdevice events enter `mlxsw_sp_router_netdevice_event()`. The handler first creates a CRIF on `NETDEV_REGISTER` for devices considered router-interesting, then dispatches to the most specific event family: offload xstats, IP-in-IP overlay, IP-in-IP underlay, regular router port events, or VRF change-upper events. On `NETDEV_UNREGISTER`, it removes the CRIF after event-specific cleanup. The whole path runs under `router->lock`, synchronizing with RIF creation/destruction and nexthop references.

RIF configuration is polymorphic through `router->rif_ops_arr`. Subport, FID, and VLAN configure paths all acquire a RIF MAC profile, write a RITR hardware entry, replay macvlan FDB entries, install the RIF device MAC into the FDB, and bind the FID to the RIF. FID/VLAN paths additionally add the router port to broadcast and multicast flood lists. Their error paths unwind in reverse order, which is critical because partial hardware state can forward packets incorrectly.

IP-in-IP loopback RIF control diverges by hardware generation. Spectrum-1 (`mlxsw_sp1_rif_ipip_lb_configure()`) gets the underlay VR directly and programs the loopback RIF with `ul_vr->id` and underlay RIF ID 0. Spectrum-2+ (`mlxsw_sp2_rif_ipip_lb_configure()`) creates or references a separate generic underlay RIF and programs the overlay loopback with that RIF index. Deconfigure paths undo the loopback RITR operation and put the VR or underlay RIF reference.

Multipath hash initialization collects policy from network namespace sysctls, builds header/field bitmaps for outer and optionally inner IPv4/IPv6/L4 fields, adjusts parser depth if inner headers must be parsed, and writes RECR2. If the register write fails after parser-depth adjustment, it restores the old parser-depth state.

Router finalization reverses initialization: unregister notifiers, flush ordered work (`mlxsw_core_flush_owq()`), stop multipath parser-depth usage, finish neighbor/fallback-RIF/VR/multicast/LPM/nexthop/RIF/CRIF/IP-in-IP/global-router state, cancel delayed nexthop activity work, destroy the mutex, and free the router object.

## State and Persistence Behavior

All state is in-memory driver state mirrored into hardware registers and resource tables. There is no disk persistence in this chunk. Durable behavior across device lifetime comes from kernel notifiers replaying existing netdevice, address, FIB, nexthop, VRF, and tunnel state into the driver after initialization.

Important state holders include:

- `router->crif_ht`, keyed by `net_device *`, tracks devices that can own RIFs or be referenced by nexthops.
- `router->rifs` stores RIF pointers by hardware RIF index. `router->rifs_count` and `router->rif_mac_profiles_count` back devlink resource occupancy.
- `router->rifs_table` is a `gen_pool` allocating hardware RIF indices from `MLXSW_SP_ROUTER_GENALLOC_OFFSET` through the device-reported `MAX_RIFS` range.
- `struct mlxsw_sp_vr` reference counts and `rif_count` track virtual-router ownership. Underlay loopback RIFs use `vr->ul_rif_refcnt` and `vr->ul_rif`.
- RIF hardware state is programmed with RITR writes, RGCR controls global router enablement, TIGCR controls tunnel ingress configuration, RECR2 controls ECMP hash selection, and RDPM maps DSCP to switch priority.
- `router->inc_parsing_depth` remembers whether multipath hashing currently requires increased parsing depth, so later reinitialization/finalization can adjust it safely.
- `router->lb_crif` is a synthetic CRIF with no netdevice used to back the generic loopback RIF for blackhole nexthops, because nexthop code expects a non-NULL CRIF.

## Dependencies and Integration Points

This chunk integrates with the Linux networking core through netdevice, inetaddr, inet6addr, validator, netevent, nexthop, and FIB notifier APIs. It uses `netdev_walk_all_upper_dev_rcu()` / `netdev_for_each_upper_dev_rcu()` for upper-device traversal, VLAN helpers (`is_vlan_dev()`, `vlan_dev_vlan_id()`, `vlan_dev_real_dev()`), bridge FDB lookup/notifiers (`br_fdb_find_port()`, `call_switchdev_notifiers()`), L3 master helpers (`netif_is_l3_master()`, `l3mdev_fib_table()`), macvlan helpers, and multipath sysctl accessors.

Driver-internal dependencies include CRIF and RIF allocation helpers, virtual-router management, FID allocation/binding/flood programming, nexthop cleanup, IP-in-IP overlay/underlay event handling, multicast-router table integration, LPM setup, neighbor handling, RIF counter/offload xstats handling, parser-depth accounting, devlink resource accounting, and Spectrum generation-specific router ops.

Hardware integration is through Mellanox register pack/write helpers:

- RITR for RIF, subport, FID, VLAN, generic loopback, and IP-in-IP loopback entries.
- RGCR for global router enablement and maximum RIF count.
- TIGCR for IP-in-IP tunnel ingress configuration.
- RECR2 for ECMP/multipath hash seed and field selection.
- RDPM for DSCP-to-priority mapping.

## Risks and Edge Cases

- Netdevice unregister can be delivered more than once through `netdev_run_todo()`. The unregister handler explicitly checks `NETREG_UNREGISTERED` and warns only if the CRIF unexpectedly remains.
- CRIF lifetime is split from RIF lifetime. If a netdevice unregisters while `crif->rif` still exists, the code marks `can_destroy` and defers freeing until `mlxsw_sp_rif_destroy()`; misuse could lead to dangling nexthop or RIF references.
- Error unwinds must stay exactly reverse-ordered. Subport/FID/VLAN configure paths program multiple hardware and software objects; missing one cleanup step can leave FID floods, FDB entries, MAC profiles, or RITR entries leaked.
- `mlxsw_sp_router_replay_inetaddr_up()` calls `mlxsw_sp_rif_should_config(crif->rif, dev, NETDEV_UP)` even when `crif->rif` is NULL due to the preceding `if (!crif || crif->rif) return 0;`. This is likely safe only if that helper tolerates a NULL old/current RIF; otherwise it is a fragile call contract.
- Upper-device traversal uses RCU-style helpers while the router mutex is held. Callers must already be in a context where these helpers are valid, and future changes need to preserve locking assumptions.
- Spectrum-1 and Spectrum-2+ IP-in-IP loopback programming differ materially. Accidentally using the wrong `rif_ops_arr` would program underlay VR/RIF identifiers incorrectly and break tunnel decapsulation/encapsulation.
- Underlay loopback RIF reference counting uses `refcount_inc_not_zero()` and shared `vr->ul_rif`; failure paths must put the VR only when creation fails, while normal put only destroys on the last reference.
- Multipath hash policy reads sysctls with `READ_ONCE()` and mirrors them into hardware. Runtime sysctl changes need a caller outside this chunk to rerun hash initialization; otherwise hardware and kernel policy can diverge.
- Parser-depth increments are global resource-sensitive state. RECR2 write failure is handled, but any later path that changes `router->inc_parsing_depth` must remain balanced with finalization.
- `mlxsw_sp_rifs_fini()` relies on WARN checks for leaked RIFs and MAC profiles. A warning here indicates earlier lifetime bugs, not recoverable cleanup.

## Test and Validation Signals

- Router probe/remove tests should verify `mlxsw_sp_router_init()` succeeds and `mlxsw_sp_router_fini()` leaves zero RIF count, empty RIF table entries, empty MAC-profile IDR, empty IP-in-IP list, and no live notifier side effects.
- Fault-injection around each initialization stage should confirm the matching unwind label unregisters/destroys only initialized components and leaves no devlink resource occupancy leaks.
- Netdevice lifecycle tests should cover register/unregister of plain ports, VLANs, bridges, LAGs, VRF enslave/deslave, and duplicate unregister rebroadcasts.
- RIF configuration tests should validate subport, FID, and VLAN RIF creation/destruction with macvlan uppers, FDB insertion/removal, FID flood enable/disable, MAC profile refcounting, and expected RITR register payloads.
- LAG router join tests should include a LAG with multiple VLAN upper devices and inject failure after some VLAN joins to verify rollback of already-joined VIDs and default VID.
- IP-in-IP tests should separately cover Spectrum-1 and Spectrum-2+ behavior, checking underlay VR refcounts, underlay RIF sharing, `ul_vr_id` / `ul_rif_id` storage, and loopback RITR programming.
- Offload xstats tests should enable/disable L3 stats, request used/delta reports, and destroy RIFs while stats are enabled to verify final stat push and notification scheduling.
- Multipath hash tests should exercise IPv4/IPv6 policies 0-3, custom field masks, inner-field masks, nonzero and zero hash seeds, parser-depth increment/decrement, and RECR2 write failure rollback.
- DSCP initialization can be validated by confirming RDPM entries match `rt_tos2priority(i << 2)` for all hardware DSCP slots.

## Cross-Chunk Notes

This chunk depends on earlier definitions for `mlxsw_sp_rif_create()`, `mlxsw_sp_rif_destroy()`, `mlxsw_sp_rif_ipip_lb_op()`, virtual-router/FID/nexthop helpers, and IP-in-IP event handling. Later or merged research should connect these RIF operation tables to the earlier RIF selection logic (`mlxsw_sp_dev_rif_type()`), inet address events that call RIF creation/destruction, and FIB/nexthop code that consumes the fallback loopback RIF and underlay RIF wrappers.
