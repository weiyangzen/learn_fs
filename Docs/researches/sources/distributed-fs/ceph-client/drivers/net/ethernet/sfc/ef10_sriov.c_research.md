# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef10_sriov.c

Purpose: Implements EF10 PF/VF SR-IOV support, firmware vSwitch/vPort/vAdaptor management, VF MAC/VLAN/spoof-check/link-state configuration, VF config reporting, and restore/remove paths across resets and unload.

Important APIs and functions: Public entry points include `efx_ef10_sriov_configure()`, `efx_ef10_sriov_init()`, `efx_ef10_sriov_fini()`, VF setters/getters, `efx_ef10_vswitching_probe_*()`, `efx_ef10_vswitching_restore_*()`, and `efx_ef10_vswitching_remove_*()`. Static helpers allocate/free VSWITCHes, VPORTs, VADAPTORs, assign EVB ports, assign VF vports, and manipulate privilege masks through MCDI.

Control flow: PF probe creates a VEB vswitch and PF vport when VFs exist, attaches the PF MAC, then allocates a vAdaptor and records fixed VLAN-filter capabilities. SR-IOV enable allocates per-VF `ef10_vf` state, generates random MACs, creates vports, adds MAC filters, assigns EVB ports, and finally enables PCI SR-IOV. Disable refuses assigned VFs unless forced, disables PCI SR-IOV when possible, frees vport/vswitching state, and clears `vf_count`. MAC/VLAN changes detach active VF netdevs, remove filters and vAdaptors, unassign EVB ports, mutate vport resources, then restore in reverse order or schedule a VF reset on restoration failure.

State and persistence: Maintains `nic_data->vf` array, each VF's `efx`, `pci_dev`, `vport_id`, `vport_assigned`, `mac`, and `vlan`; PF `efx->vf_count`, `efx->vport_id`, `nic_data->vport_mac`, `fixed_features`, and `must_probe_vswitching`. Firmware vSwitch/vPort/vAdaptor state persists in NIC firmware until explicitly freed or reset.

Dependencies and integration points: Uses MCDI commands for EVB, VSWITCH, VPORT, VADAPTOR, privilege mask, and link state; PCI SR-IOV core; generic `efx_net_open/stop`, reset scheduling, filters, and device attach/detach helpers; and netlink VF config structs. It is called from NIC type callbacks and netdev SR-IOV ndo handlers via the generic SR-IOV wrapper.

Risks: Error unwinds must avoid leaking firmware resources or leaving VF drivers attached to invalid vports. Assigned VFs limit cleanup and can leave orphaned VFs until a later unload. VLAN changes have multi-stage restore logic with `rc` and `rc2` interactions. The code assumes QoS 0 only. Spoof-check depends on firmware capability. `efx_ef10_vswitching_remove_pf()` sets `efx->vport_id` to assigned before freeing the vswitch, so correctness relies on firmware semantics and assigned-VF checks.

Test signals: Enable/disable SR-IOV with no assigned VFs, assigned VFs, and forced unload; set VF MAC, VLAN, spoof-check, and link state; query VF config; inject MCDI failures at each vport/vadaptor step; reset PF and verify restore; bind a VF driver while changing VF state; verify fixed VLAN filter features after vAdaptor query.
