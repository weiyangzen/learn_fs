# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_eswitch_br.h

## Purpose
`ice_eswitch_br.h` declares the private data structures and entry points for ice switchdev bridge offloads. It models FDB keys, hardware rule pairs, FDB entries, bridge ports, the bridge object, bridge offload notifier container, queued FDB work, and VLAN metadata.

## Important APIs, Types, and Functions
- `struct ice_esw_br_fdb_data` is the rhashtable key: destination MAC address and VLAN ID.
- `struct ice_esw_br_flow` stores the two hardware rule handles associated with an FDB entry: forwarding rule and guard rule.
- `ICE_ESWITCH_BR_FDB_ADDED_BY_USER` distinguishes static/user FDB entries from dynamic entries for notification and ageing behavior.
- `struct ice_esw_br_fdb_entry` stores hash/list linkage, flags, owning netdev, bridge port, hardware flow, and last-use timestamp.
- `enum ice_esw_br_port_type` distinguishes uplink ports from VF representor ports.
- `struct ice_esw_br_port` stores bridge back pointer, VSI pointer/index, port type, PVID, representor id, and per-port VLAN xarray.
- `ICE_ESWITCH_BR_VLAN_FILTERING` is the bridge flag toggled by switchdev VLAN filtering attributes.
- `struct ice_esw_br` stores the single bridge state: offload container, port xarray, FDB rhashtable/list, Linux bridge ifindex, flags, and ageing time.
- `struct ice_esw_br_offloads` stores PF pointer, bridge pointer, netdev/switchdev notifier blocks, ordered workqueue, and delayed ageing work.
- `struct ice_esw_br_fdb_work` packages switchdev FDB notifications for deferred workqueue handling.
- `struct ice_esw_br_vlan` stores VID and bridge VLAN flags.
- Container macros convert notifier/work pointers back to bridge offload and FDB work structures.
- `ice_eswitch_br_is_vid_valid()` treats VID 0 and VID 1 as special untagged/PVID cases that should not add VLAN lookup fields.
- Exported functions are `ice_eswitch_br_offloads_init()`, `ice_eswitch_br_offloads_deinit()`, and `ice_eswitch_br_fdb_flush()`.

## Control Flow
The header has no standalone runtime flow. It defines the structures walked by `ice_eswitch_br.c`: notifier callbacks enter through `ice_esw_br_offloads`, bridge ports are looked up in `ice_esw_br.ports`, FDB entries are looked up by `ice_esw_br_fdb_data`, and delayed work uses the container macros to regain the parent offload object.

## State and Persistence Behavior
The declared structures are in-memory bridge offload state. They mirror Linux bridge configuration and ice hardware rules while switchdev offloads are active. No state is persisted across driver unload or switchdev teardown. FDB hardware rules are represented by pointers that must be explicitly deleted before freeing entries.

## Dependencies and Integration Points
The header depends on kernel rhashtable, workqueue, notifier, netdevice, switchdev, xarray, list, and Ethernet/VLAN types via included and surrounding driver headers. It is included by `ice_eswitch.c` for offload init/deinit and by `ice_eswitch_br.c` for implementation. It also embeds pointers to ice PF/VSI and representor-facing bridge port state.

## Risks and Edge Cases
- `ice_eswitch_br_is_vid_valid()` intentionally excludes VID 1 as well as VID 0; code adding VLAN lookups must preserve the bridge convention described in the comment.
- The FDB entry owns hardware rule pointers; freeing an entry without deleting both rules leaks hardware state.
- `struct ice_esw_br_port.vlans` needs xarray initialization and flush/destroy discipline in every port lifecycle path.
- The header models only VF representor bridge ports, even though current implementation also treats SF/representor netdevs through generic representor helpers; future type distinctions may need extension.

## Test Signals
- Compile coverage should ensure all container macros match the exact struct member names used by notifier and delayed-work registration.
- Static analysis should verify rhashtable key fields match `ice_fdb_ht_params` in the implementation.
- Runtime bridge tests should validate VID 0/1 handling, FDB rule cleanup, VLAN xarray cleanup, and ageing work container conversion.
