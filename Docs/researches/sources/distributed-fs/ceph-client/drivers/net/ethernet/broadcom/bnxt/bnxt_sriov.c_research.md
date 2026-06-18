# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.c

## Purpose
Implements SR-IOV control for the bnxt Ethernet driver. On PFs it validates netdev VF operations, allocates VF bookkeeping and firmware mailbox buffers, reserves firmware resources for enabled VFs, creates VF representors in switchdev mode, disables and frees VFs, and mediates forwarded VF HWRM requests. On VFs it tracks PF-assigned MAC policy and asks the PF to approve local MAC changes.

## Important APIs, Types, And Functions
The externally visible netdev/PCI entry points are `bnxt_sriov_configure()`, `bnxt_cfg_hw_sriov()`, `__bnxt_sriov_disable()`, `bnxt_get_vf_config()`, `bnxt_set_vf_mac()`, `bnxt_set_vf_vlan()`, `bnxt_set_vf_bw()`, `bnxt_set_vf_link_state()`, `bnxt_set_vf_spoofchk()`, `bnxt_set_vf_trust()`, `bnxt_hwrm_exec_fwd_req()`, `bnxt_update_vf_mac()`, and `bnxt_approve_mac()`. The core state carrier is `bp->pf.vf[]`, an array of `struct bnxt_vf_info` entries containing firmware FIDs, PF-assigned MACs, VF-reported MACs, VLAN/BW/link/trust/spoof flags, and per-VF DMA HWRM request buffers.

Firmware command helpers include `bnxt_hwrm_func_vf_resc_cfg()` for new resource-manager VF reservation, `bnxt_hwrm_func_cfg()` for older fixed allocation, `bnxt_hwrm_func_buf_rgtr()` for registering VF request buffer pages, `bnxt_hwrm_func_vf_resource_free()` for teardown, `bnxt_hwrm_roce_sriov_cfg()` for RoCE VF limits, and forwarded-response helpers `bnxt_hwrm_fwd_resp()`, `bnxt_hwrm_fwd_err_resp()`, and `bnxt_hwrm_exec_fwd_resp()`.

## Control Flow
PF SR-IOV enable starts at `bnxt_sriov_configure()`. It rejects requests while the netdev is down, firmware reset is active, or VFs are assigned, then disables existing VFs before enabling a new count. `bnxt_sriov_enable()` calculates the largest feasible VF count from RX/TX/CP/stat/RSS/VNIC resources, allocates `bp->pf.vf`, DMA request pages, and the VF event bitmap, configures firmware resources, calls `pci_enable_sriov()`, and creates VF representors if `bp->eswitch_mode` is switchdev.

Disable flows through `bnxt_sriov_disable()` or `__bnxt_sriov_disable()`. Representors are destroyed first under `devl_lock()`. If VFs are assigned, the PF cannot call `pci_disable_sriov()` and instead forwards a PF driver unload async event to all VFs; otherwise it disables PCI SR-IOV and frees VF firmware resources. The wrapper then restores PF firmware resources under RTNL and netdev instance locks.

Forwarded VF requests are processed by `bnxt_hwrm_exec_fwd_req()`, which scans `bp->pf.vf_event_bmap`, clears pending bits, decodes the encapsulated HWRM request in the VF DMA buffer, and either executes it, rejects it, or synthesizes a PF-controlled response. MAC-related requests are constrained by PF-assigned MAC and trusted-VF state. Link query responses can be rewritten when the PF forced VF link up/down.

## State And Persistence Behavior
All state is in driver memory and firmware configuration, not on disk. The PF mirrors admin configuration in `bp->pf.vf[]` so it can report VF settings and replay selected parameters during reset (`__bnxt_set_vf_params()`). Hardware resource accounting mutates `bp->hw_resc` after VF reservation, and teardown re-queries/restores capabilities. VF request buffers are coherent DMA pages registered with firmware; `vf_event_bmap` is a bitmap of pending forwarded requests. VF-side `bp->vf.mac_addr` records the PF-assigned administrative MAC and is used to decide whether local MAC changes require PF approval.

## Dependencies And Integration Points
The file depends heavily on bnxt HWRM request infrastructure (`hwrm_req_init()`, `hwrm_req_send()`, held responses, and short `FUNC_CFG` requests), PCI SR-IOV APIs, rtnl/netdev locking, firmware capability flags, ethtool speed conversion, RoCE/ULP capability macros, and VF representor helpers from `bnxt_vfr.c`. It integrates with ndo VF callbacks, PCI `.sriov_configure`, firmware async events, firmware reset/resource restore paths, and switchdev representor creation.

## Risks
Resource calculations are sensitive to firmware generation, aggregation rings, NQ/MSI-X accounting, pre-reserved VNICs, and reservation strategy. Partial enable failures require ordered unwinding of PCI SR-IOV, firmware resources, and local memory. Forwarded request validation is security-sensitive because untrusted VFs can attempt MAC or link-related operations. The PF mirrors admin state before/after firmware operations in a few places, so failed HWRM commands or reset replay bugs can desynchronize Linux-visible state from firmware.

## Test Signals
Useful signals include enabling and disabling varying VF counts, reducing requested VF count when resources are constrained, changing VF MAC/VLAN/rate/link/spoof/trust through iproute2, observing VF MAC approval from an untrusted and trusted VF, hot reset with SR-IOV enabled, assigned-VF disable behavior, switchdev enable with representor creation, RoCE SR-IOV resource provisioning, and firmware error-injection around each HWRM allocation/free path.
