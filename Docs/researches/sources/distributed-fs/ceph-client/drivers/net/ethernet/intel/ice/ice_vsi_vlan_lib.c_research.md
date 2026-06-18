# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vsi_vlan_lib.c

## Purpose
Implements low-level VLAN operations for VSIs: adding/removing VLAN filters, configuring inner and outer stripping/insertion, setting and clearing inner/outer port VLANs, enabling/disabling Rx VLAN pruning, enabling/disabling Tx VLAN antispoof filtering, and clearing all port VLAN state.

## Important APIs and Functions
- `ice_vsi_add_vlan()` and `ice_vsi_del_vlan()` validate TPID/VID and update `vsi->num_vlan` around filter add/remove.
- Inner operations: `ice_vsi_ena_inner_stripping()`, `ice_vsi_dis_inner_stripping()`, `ice_vsi_ena_inner_insertion()`, `ice_vsi_dis_inner_insertion()`, `ice_vsi_set_inner_port_vlan()`, and `ice_vsi_clear_inner_port_vlan()`.
- Filtering: `ice_vsi_ena_rx_vlan_filtering()`, `ice_vsi_dis_rx_vlan_filtering()`, `ice_vsi_ena_tx_vlan_filtering()`, and `ice_vsi_dis_tx_vlan_filtering()`.
- Outer DVM operations: `ice_vsi_ena_outer_stripping()`, `ice_vsi_dis_outer_stripping()`, `ice_vsi_ena_outer_insertion()`, `ice_vsi_dis_outer_insertion()`, `ice_vsi_set_outer_port_vlan()`, and `ice_vsi_clear_outer_port_vlan()`.
- `ice_vsi_clear_port_vlan()` resets both inner and outer port VLAN context and restores default VLAN flags.

## Control Flow
Filter operations validate TPID and normalize duplicate/missing filter errors (`-EEXIST`, `-ENOENT`, `-EBUSY`) to success where appropriate. Stripping/insertion operations allocate a temporary VSI context, set valid sections, preserve unrelated fields, call `ice_update_vsi()`, and copy updated flags back into `vsi->info` only on success. Port VLAN setters save existing VLAN info into `vsi->vlan_info`, program port-based VLAN fields and pruning, and clearers restore saved VLAN info.

## State and Persistence
Persistent per-VSI VLAN hardware state lives in `vsi->info` fields: `inner_vlan_flags`, `outer_vlan_flags`, `sw_flags2`, `port_based_inner_vlan`, and `port_based_outer_vlan`. `vsi->vlan_info` snapshots previous flags for port VLAN restoration. `vsi->num_vlan` tracks programmed VLAN filter count.

## Dependencies and Integration Points
Depends on `ice_vsi_vlan_lib.h`, `ice_lib.h`, `ice_fltr.h`, `ice.h`, `ice_vlan_mode.h`, AQ `ice_update_vsi()`, filter programming, netdev flags, and hardware VLAN constants. Called through `struct ice_vsi_vlan_ops` by PF, VF, and SF VSI code.

## Risks
- Port VLAN state prevents modifying stripping/insertion and returns success, so callers must account for no-op behavior.
- `ice_cfg_vlan_pruning()` skips enabling pruning while netdev is promiscuous; filtering state may be deferred.
- Only specific TPIDs are valid; wrong TPID produces `-EINVAL`.
- Context update failure leaves cached `vsi->info` unchanged, but partially programmed hardware failure modes depend on AQ behavior.
- `vsi->num_vlan` can become inaccurate if filter programming paths outside this API modify VLAN filters.

## Test Signals
Test valid and invalid TPIDs, duplicate add/delete missing VLAN filters, SVM inner operations, DVM outer operations for 0x8100/0x88a8/0x9100 TPIDs, port VLAN set/clear with priority limits, promisc pruning deferral, Tx VLAN antispoof toggles, `ice_vsi_clear_port_vlan()` in SVM and DVM, and AQ error handling.
