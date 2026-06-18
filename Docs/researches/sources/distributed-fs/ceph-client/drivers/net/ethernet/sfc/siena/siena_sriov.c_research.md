<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c

## Purpose
Implements Siena PF-side SR-IOV support, including firmware SR-IOV enablement, VF resource reservation, VFDI mailbox protocol handling, VF queue/filter/status management, VF reset notification, peer address publication, and netlink VF configuration callbacks.

## Important APIs, Types, And Functions
- Core VF state: `struct siena_vf`, `struct efx_memcpy_req`, `struct efx_local_addr`, and `struct efx_endpoint_page`.
- SR-IOV lifecycle: `efx_siena_sriov_probe()`, `efx_siena_sriov_init()`, `efx_siena_sriov_fini()`, `efx_siena_sriov_reset()`, `efx_siena_sriov_flr()`, `efx_init_sriov()`, `efx_fini_sriov()`.
- VFDI handling: `efx_siena_sriov_event()`, `efx_siena_sriov_vfdi()`, `efx_vfdi_init_evq()`, `efx_vfdi_init_rxq()`, `efx_vfdi_init_txq()`, `efx_vfdi_fini_all_queues()`, filter and status-page handlers.
- VF configuration: `efx_siena_sriov_set_vf_mac()`, `efx_siena_sriov_set_vf_vlan()`, `efx_siena_sriov_set_vf_spoofchk()`, `efx_siena_sriov_get_vf_config()`, `efx_siena_sriov_wanted()`.

## Control Flow
Probe asks firmware how many VFs and VIs are available, bounds by `max_vfs`, and reserves an extra MSI-X channel for VFDI events. Init enables firmware SR-IOV, allocates a DMA `vfdi_status` page, allocates per-VF state and request buffers, discovers PCI VF requester IDs, publishes PF/VF counts, enables user events, then calls `pci_enable_sriov()`. VF user events are assembled as four ordered VFDI address words; a complete request queues work, DMAs the request page from the VF, dispatches by `op`, then writes response `rc` and `op` back to guest memory.

## State And Persistence Behavior
All state is runtime PF memory and firmware configuration. Per VF, the driver tracks requester ID, VFDI sequence/address state, request buffer, buffer-table base, RX/TX filter IDs, MAC/VLAN endpoint, status-page DMA address, peer pages, EVQ0 backing pages, queue bitmasks/counts, retry masks, waitqueues, and reset work. Firmware SR-IOV enablement and PCI VF enablement are undone during fini.

## Dependencies And Integration Points
Depends on PCI SR-IOV capability registers, Siena MCDI `MC_CMD_SRIOV` and `MC_CMD_MEMCPY`, farch registers and buffer table writes, filters, queue/event register tables, netdev RTNL locking, workqueues, `vfdi.h` ABI definitions, and `siena.c` NIC type hooks. Netlink VF operations reach this file through generic SR-IOV wrappers and the NIC type table.

## Risks And Test Signals
The VFDI sequence state machine rejects malformed or overlapping requests; bugs can hang guest VF initialization. Queue count tracking is tied to flush completion events and retry masks. Status updates use generation fields and DMA ordering barriers; broken ordering can expose torn data to guests. Test signals include VF creation/removal, guest VFDI queue init/fini/filter/status operations, spoof-check changes only while TX queues are stopped, FLR/reset notification events, flush timeout/retry logs, and peer list updates after VF/PF MAC changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.c -->
