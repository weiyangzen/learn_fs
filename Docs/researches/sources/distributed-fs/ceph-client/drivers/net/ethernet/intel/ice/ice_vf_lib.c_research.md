# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib.c

## Purpose
Implements the main SR-IOV VF lifecycle library for the Intel `ice` driver. It owns VF lookup/reference handling, reset orchestration, host-side VF configuration rebuild, VF VSI/control-VSI management, promiscuous mode handling, spoof-check configuration, mailbox counter reset, LLDP bookkeeping, and utility helpers shared by virtchnl handlers.

## Important APIs and Functions
- `ice_get_vf_by_id()` and `ice_put_vf()` provide RCU-safe VF table lookup with `kref` lifetime protection. `ice_release_vf()` drops the PCI VF device reference and calls the hardware-specific `vf_ops->free()`.
- `ice_has_vfs()`, `ice_get_num_vfs()`, and `ice_get_vf_vsi()` expose VF inventory and LAN VSI lookup.
- `ice_check_vf_ready_for_cfg()` waits for reset initialization, rejects disabled VFs, and calls `ice_check_vf_init()`.
- `ice_reset_all_vfs()` resets every allocated VF during PF-level reset flows while holding `pf->vfs.table_lock`.
- `ice_reset_vf()` resets a single VF, optionally notifying it, optionally taking `vf->cfg_lock`, coordinating with LAG, stopping queues, rebuilding the VSI, clearing VF-owned state, and reapplying host-owned configuration.
- `ice_vf_init_host_cfg()` applies initial host defaults: VLAN 0, Rx VLAN filtering, broadcast MAC filter, and spoof checking.
- `ice_vf_set_vsi_promisc()` and `ice_vf_clear_vsi_promisc()` select VLAN-aware or non-VLAN promiscuous filter programming.
- Private virtualization helpers include `ice_initialize_vf_entry()`, `ice_deinitialize_vf_entry()`, `ice_dis_vf_qs()`, `ice_err_to_virt_err()`, `ice_vsi_apply_spoofchk()`, control-VSI helpers, and VF VSI release/invalidation helpers.

## Control Flow
VF reset has a layered flow. `ice_trigger_vf_reset()` clears ACTIVE/INIT, clears mailbox registers outside PF reset, and hits the VF reset register. Reset-all first resets mailbox counters, gates all VF access with `ICE_VF_DIS`, triggers all VF resets, polls reset status, then rebuilds each VF under its `cfg_lock`. Single reset uses `ICE_VF_STATE_DIS`, disables VF queues, issues the required Tx queue AQ disable, polls completion, clears driver caps and allowlist, disables promisc modes, resets FDIR/control VSI, rebuilds/reconfigures the LAN VSI, updates switchdev representation, and resets mailbox abuse counters.

Host-owned state is rebuilt after VSI reconfiguration in `ice_vf_rebuild_host_cfg()`: trust capability, default/broadcast MAC filters, VLAN or port-VLAN config, Tx rate limits, spoof checking, and scheduler aggregator assignment. Driver-owned VF state such as negotiated caps, FDIR rules, queue enable bitmaps, VF VLAN v2 caps, and control VSI is cleared across resets.

## State and Persistence
Persistent host-admin state lives in `struct ice_vf`: `trusted`, `spoofchk`, `port_vlan_info`, `min_tx_rate`, `max_tx_rate`, `hw_lan_addr`, aggregator linkage through VSI, and LLDP counters. VF runtime state is in `vf_states`, `txq_ena`, `rxq_ena`, counters, `driver_caps`, allowlist bits, and FDIR/control-VSI members. The code intentionally preserves host settings across reset while invalidating VF-negotiated state.

## Dependencies and Integration Points
Depends on `ice_vf_lib_private.h`, `ice.h`, `ice_lib.h`, `ice_fltr.h`, `virt/allowlist.h`, VLAN ops, mailbox helpers, FDIR helpers, LAG, eswitch, switchdev representation, AQ VSI update routines, and hardware-specific `ice_vf_ops`. External callers include SR-IOV setup/teardown, virtchnl opcode handlers, devlink/NDO VF controls, reset service tasks, and FDIR control VSI paths.

## Risks
- VF reference users must pair `ice_get_vf_by_id()` with `ice_put_vf()` or leak VF entries.
- Reset sequencing is concurrency-sensitive: `cfg_lock`, PF VF table lock, RCU, PF state bits, and LAG mutex all protect different surfaces.
- Rebuild failures can leave a VF disabled or partially restored; host config rebuild logs errors but continues through later operations.
- Promiscuous mode handling differs for true-promisc, default VSI, port VLAN, and non-zero VLAN cases.
- `ice_vf_update_mac_lldp_num()` decrements an unsigned counter and assumes callers are balanced.

## Test Signals
Exercise PF reset with active VFs, VFLR, VF-requested reset, queue-enable and queue-disable transitions, host-config persistence across reset, port VLAN rebuild, spoofchk toggles, Tx rate limiting restore, switchdev/eswitch VF attach/detach, default VSI promisc handling, and mailbox malicious counter reset on both E830 and non-E830 paths.
