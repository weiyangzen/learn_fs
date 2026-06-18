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
