# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.c

## Purpose
`ice_eswitch_br.c` implements switchdev bridge offload support for ice e-switch mode. It tracks one offloaded bridge per e-switch, links PF uplink and port representor netdevs as bridge ports, offloads FDB entries into hardware advanced switch rules, handles bridge VLAN objects and attributes, ages dynamic FDB entries, and coordinates switchdev/netdev notifier lifetimes.

## Important APIs, Types, and Functions
- `ice_eswitch_br_offloads_init()` allocates bridge offload state, creates an ordered workqueue, registers switchdev and netdev notifiers, and starts delayed FDB ageing work.
- `ice_eswitch_br_offloads_deinit()` cancels delayed work, unregisters notifiers, destroys the workqueue, and deallocates bridge state under RTNL.
- `ice_eswitch_br_is_dev_valid()` accepts only ice PF netdevs, representors, and LAG masters.
- `ice_eswitch_br_netdev_to_port()` maps representor/PF/LAG netdevs to `struct ice_esw_br_port`.
- `ice_eswitch_br_port_link()` / `ice_eswitch_br_port_unlink()` handle bridge membership changes from `NETDEV_CHANGEUPPER`.
- `ice_eswitch_br_init()`, `ice_eswitch_br_get()`, `ice_eswitch_br_deinit()`, and `ice_eswitch_br_verify_deinit()` manage the single bridge object.
- `ice_eswitch_br_fdb_entry_create()`, `ice_eswitch_br_fdb_entry_find_and_delete()`, `ice_eswitch_br_fdb_flush()`, and cleanup helpers maintain FDB state.
- `ice_eswitch_br_flow_create()` creates a paired forward rule and guard rule for each FDB entry; `ice_eswitch_br_flow_delete()` removes both.
- `ice_eswitch_br_fwd_rule_create()` and `ice_eswitch_br_guard_rule_create()` build hardware advanced-rule lookup/action data for MAC and optional VLAN.
- `ice_eswitch_br_switchdev_event()` handles async FDB add/delete events by queueing `ice_eswitch_br_fdb_event_work()`.
- `ice_eswitch_br_event_blocking()` handles switchdev blocking object/attribute operations for VLAN add/delete, VLAN filtering, and ageing time.
- VLAN helpers include `ice_eswitch_br_vlan_filtering_set()`, `ice_eswitch_br_port_vlan_add()`, `ice_eswitch_br_port_vlan_del()`, `ice_eswitch_br_vlan_create()`, `ice_eswitch_br_set_pvid()`, and cleanup/flush helpers.
- `ice_eswitch_br_update_work()` runs periodic ageing of non-user FDB entries.

## Control Flow
Bridge offloads are initialized when switchdev mode is enabled by the e-switch core. Init allocates `pf->eswitch.br_offloads`, registers three notifier paths, and schedules periodic update work. Netdev upper-change notifications link or unlink valid devices to a Linux bridge. Link either creates the single bridge object for the bridge ifindex or reuses it, then creates an uplink bridge port for PF/LAG devices or a VF representor bridge port for representors. Unlink verifies the device belongs to the bridge, deinitializes the port, and destroys the bridge if it has no ports.

Switchdev FDB notifications are filtered for bridge upper devices and valid ice devices. FDB add/delete work is copied into an allocated work item because the notifier path may be atomic; the ordered workqueue later takes RTNL, maps the netdev to a bridge port, and creates or deletes the FDB entry. FDB creation optionally validates VLAN metadata, replaces existing entries, allocates an entry, creates hardware forward and guard rules, inserts the entry into the rhashtable and list, and sends switchdev offload notifications.

Blocking switchdev handlers process VLAN add/delete and bridge attributes synchronously. VLAN filtering changes flush the FDB before toggling the bridge flag. VLAN add supports trunk VLANs or a port VLAN/PVID mode with simultaneous PVID and untagged flags; port VLAN on the uplink is rejected. Periodic delayed work takes RTNL, removes non-user FDB entries whose `last_use + ageing_time` has expired, and reschedules itself every second.

## State and Persistence Behavior
All state is runtime-only. `pf->eswitch.br_offloads` points to the offload container. `br_offloads->bridge` tracks the single bridge, including `ifindex`, flags, ageing time, `ports` xarray, `fdb_ht` rhashtable, and `fdb_list`. Each bridge port records VSI pointer/index, type, representor id, PVID, and VLAN xarray. Each FDB entry stores MAC/VID key data, owning netdev, bridge port, hardware rule pair, user-added flag, and `last_use`. Hardware advanced rules persist in device state while entries exist and are explicitly deleted during cleanup.

## Dependencies and Integration Points
This file depends on Linux switchdev notifiers, blocking switchdev handlers, netdevice upper/lower APIs, bridge/VLAN object definitions, LAG master detection, RTNL locking, workqueues, xarrays, rhashtable, jiffies ageing helpers, and switchdev FDB notifications. It integrates with ice representors, PF uplink netdevs, ice switch advanced rules, VLAN operations, VF port VLAN helpers, and tracepoints.

## Risks and Edge Cases
- Only one bridge is supported per e-switch; attempts to link ports to a different bridge return `-EOPNOTSUPP`.
- LAG support picks the first lower ice device; absence of an ice lower device returns no port or no-op link behavior.
- Dynamic FDB ageing uses `last_use` set at creation and is not refreshed in this file, so offloaded dynamic entries age based on driver-observed creation time unless another path updates it.
- VLAN filtering flushes the entire FDB, which is correct for lookup semantics but disruptive.
- Untagged filtering without VLAN filtering is not supported; FDB entries with VID are ignored in that mode.
- PVID/untagged VLAN push/pop is only supported together and not on uplink ports; partial flag combinations return `-EOPNOTSUPP`.
- FDB creation replaces existing entries before allocating and installing the new one; if new hardware rule creation fails, the old entry is already gone.
- Workqueue/notifier teardown relies on unregistering notifiers, destroying the queue, and taking RTNL to wait for in-progress events; ordering is critical to avoid use-after-free.

## Test Signals
- Switchdev bridge tests should link/unlink PF uplink, representors, and LAG masters; verify one-bridge-only enforcement and bridge destruction when last port leaves.
- FDB tests should add/delete user and dynamic entries with and without VLAN filtering, validate hardware forward/guard rule creation and deletion, and verify switchdev offload notifications.
- VLAN tests should cover trunk VLAN add/delete, duplicate VLAN updates, PVID+untagged success on representor ports, PVID-only or untagged-only rejection, uplink PVID rejection, and FDB flush on VLAN filtering toggles.
- Ageing tests should set bridge ageing time and verify non-user entries are removed while user-added entries are retained.
- Failure injection should cover allocation failures, rhashtable insertion failure, advanced rule add/delete failures, notifier registration failure labels, and workqueue allocation failure.
- Concurrency tests should stress FDB events during bridge unlink and offload deinit under RTNL.
