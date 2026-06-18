# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.c

## Purpose

`ice_sriov.c` implements SR-IOV support for the ice PF driver. It enables and disables VFs, allocates per-VF queue/MSI-X resources, creates VF VSI resources, maps interrupts and queues into VF PCI-visible registers, handles VF resets and VFLR events, exposes netdev VF administration operations, supports per-VF MSI-X resizing, processes VF LAN overflow/MDD events, and restores VF MSI state after PF FLR.

## Important APIs, Types, And Functions

- VF lifecycle helpers include `ice_create_vf_entries()`, `ice_free_vf_entries()`, `ice_init_vf_vsi_res()`, `ice_start_vfs()`, `ice_free_vf_res()`, and `ice_free_vfs()`.
- SR-IOV enable/configuration entry points include `ice_sriov_configure()`, `ice_pci_sriov_ena()`, `ice_ena_vfs()`, `ice_check_sriov_allowed()`, and `ice_sriov_get_vf_total_msix()`.
- Mapping helpers include `ice_ena_vf_msix_mappings()`, `ice_ena_vf_q_mappings()`, `ice_ena_vf_mappings()`, `ice_dis_vf_mappings()`, and `ice_calc_vf_reg_idx()`.
- VF reset operations are collected in `ice_sriov_vf_ops`: clear reset state, clear mailbox registers, trigger reset, poll reset status, clear reset trigger, free, and post-VSI-rebuild.
- Event paths include `ice_process_vflr_event()`, `ice_vf_lan_overflow_event()`, `ice_print_vf_rx_mdd_event()`, `ice_print_vf_tx_mdd_event()`, and `ice_print_vfs_mdd_events()`.
- VF admin netdev hooks include `ice_set_vf_spoofchk()`, `ice_get_vf_cfg()`, `__ice_set_vf_mac()`, `ice_set_vf_mac()`, `ice_set_vf_trust()`, `ice_set_vf_link_state()`, `ice_set_vf_bw()`, `ice_get_vf_stats()`, and `ice_set_vf_port_vlan()`.
- Dynamic VF resource sizing is handled by `ice_sriov_set_msix_vec_count()` and `ice_sriov_remap_vectors()`.

## Control Flow

The sysfs SR-IOV path enters `ice_sriov_configure()`, which validates PF capability, safe-mode state, and nominal PF readiness. A request for zero VFs frees resources unless VFs are assigned to VMs. A positive request enters `ice_pci_sriov_ena()` and `ice_ena_vfs()`: OICR interrupt handling is temporarily disabled, PCI SR-IOV is enabled, the VF table lock is taken, per-VF vectors and queues are computed from available common MSI-X and queue resources, VF entries are allocated into the RCU hash table, and each VF is started by clearing reset triggers, allocating IRQs, creating a VF VSI, initializing host config, attaching to eswitch, enabling mappings, and setting `VFGEN_RSTAT` active.

Teardown uses `ice_free_vfs()`. It serializes with `ICE_VF_DIS`, disables PCI SR-IOV when VFs are not assigned, walks the VF table under lock, detaches each VF from eswitch, disables queues, frees virtual IRQs, disables mappings, releases control/LAN VSI resources, clears MDD/promisc state, optionally clears VFLR status bits, removes all VF hash entries, and clears PF SR-IOV flags.

VF reset handling is split between generic VF library orchestration and SR-IOV register operations provided through `ice_sriov_vf_ops`. Software resets write `VPGEN_VFRTRIG`; VFLR cleanup clears `GLGEN_VFLRSTAT`, polls PCI transaction pending status, clears mailbox registers, polls `VPGEN_VFRSTAT`, and re-enables mappings after VSI rebuild.

Netdev VF admin calls acquire a VF reference by ID, validate readiness, often take `vf->cfg_lock`, update stored VF state, and either apply immediately to the VSI or reset/notify the VF so virtchnl resource discovery picks up the change. Bandwidth configuration rejects min-rate with DCB enabled, prevents aggregate min-rate oversubscription against current link speed, and delegates scheduler programming to VSI min/max bandwidth helpers. Port VLAN configuration validates VLAN ID/QoS/protocol and resets the VF after updating `vf->port_vlan_info`.

## State And Persistence

VF state is runtime driver and hardware state. `pf->vfs.table` stores `struct ice_vf` objects protected by `pf->vfs.table_lock` with RCU lookup and kref lifetime. `pf->vfs.num_qps_per` and `pf->vfs.num_msix_per` store default allocation. Per-VF fields track VF ID, PCI VF device, VSI indexes, vector range, queue count, MAC state, spoof check, trust, link override, bandwidth, port VLAN, MDD counters, and state bits such as initialized, disabled, active, and promiscuous. Hardware persistence is through PCI SR-IOV capability, queue mapping registers, interrupt mapping registers, mailbox/reset registers, and VF reset status registers. No on-disk persistence is used.

## Dependencies And Integration Points

The file depends on core ice PF/VSI libraries, VF library private helpers, interrupt tracker helpers, eswitch attach/detach, virtchnl state/notification, flow director VF support, VLAN mode and VF VLAN ops, DCB link-speed helpers, firmware AQ event structures, PCI SR-IOV APIs, RCU/kref locking, and netdev VF rtnl operations. It is integrated with PF probe/remove, sysfs `sriov_numvfs`, VF mailbox/reset handling, netdev `.ndo_set_vf_*` hooks, MDD handling, and PF FLR recovery.

## Risks

- Enable and teardown paths are highly order-dependent: PCI SR-IOV, VF hash entries, VSI resources, eswitch attachment, interrupts, queue mappings, and reset status must unwind in the exact reverse order on failure.
- Several operations assume contiguous Tx/Rx queue mapping; scattered VF queue mapping logs errors and is not implemented.
- VF lifetime uses RCU plus krefs; missing `ice_put_vf()` or using a VF after dropping locks can lead to leaks or use-after-free.
- `ice_sriov_set_msix_vec_count()` remaps idle VFs to compact IRQ usage and rebuilds the target VSI; partial failure has a fallback path but still depends on IRQ availability for the old vector count.
- Bandwidth min-rate validation uses current link speed and current VF accounting; link changes after configuration can make prior allocations oversubscribed.
- Trust is rejected in switchdev mode, while other VF settings still operate; behavior must stay aligned with eswitch security expectations.
- VF reset and VFLR paths write hardware registers directly and rely on short polling loops; slow or wedged hardware can leave VF state inconsistent despite logs.

## Test Signals

Useful tests include SR-IOV enable/disable with varied VF counts and resource scarcity, failure injection for VF entry allocation/VSI setup/eswitch attach/IRQ allocation, assigned-VF teardown rejection, VFLR event handling, VF MSI-X resize success and rollback, spoof check/MAC/trust/link/VLAN/bandwidth netdev operation tests, min-rate oversubscription tests, DCB-enabled min-rate rejection, LAN overflow event mapping to VF reset, MDD log rate-limiting checks, and PF FLR MSI-state restore tests.
