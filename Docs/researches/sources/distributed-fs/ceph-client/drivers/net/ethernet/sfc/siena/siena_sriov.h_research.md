<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h

## Purpose
Declares Siena-specific SR-IOV constants and the PF-side SR-IOV API used by the Siena NIC type and event/flush paths.

## Important APIs, Types, And Functions
- Resource constants: `EFX_VI_SCALE_MAX`, `EFX_VI_BASE`, `EFX_VF_COUNT_MAX`, `EFX_MAX_VF_EVQ_SIZE`, and `EFX_VF_BUFTBL_PER_VI`.
- Lifecycle/configuration declarations: `efx_siena_sriov_probe()`, `efx_siena_sriov_configure()`, `efx_siena_sriov_init()`, `efx_siena_sriov_fini()`, `efx_siena_sriov_wanted()`, `efx_siena_sriov_reset()`, `efx_siena_sriov_flr()`.
- VF netlink operations: `efx_siena_sriov_set_vf_mac()`, `efx_siena_sriov_set_vf_vlan()`, `efx_siena_sriov_set_vf_spoofchk()`, `efx_siena_sriov_get_vf_config()`.
- Event helpers: `efx_siena_sriov_event()`, TX/RX flush completion handlers, and descriptor-fetch error handling.

## Control Flow
The header lets `siena.c` wire SR-IOV callbacks into `siena_a0_nic_type`, while farch event code can report VF user events, queue flush completions, FLR, and descriptor-fetch errors back to the SR-IOV backend. `efx_siena_sriov_enabled()` compiles to a real `vf_init_count` check under `CONFIG_SFC_SIENA_SRIOV` and to `false` otherwise.

## State And Persistence Behavior
This file defines hardware resource layout constraints rather than owning state. The constants determine how VIs and buffer table entries are partitioned between PF and VF BAR/register access.

## Dependencies And Integration Points
Includes `net_driver.h` and relies on `struct efx_nic`, `struct efx_channel`, `efx_qword_t`, and Linux `ifla_vf_info`. Its declarations are consumed by Siena probe/init/remove, event handling, netdev VF ops, and module-level SR-IOV workqueue setup.

## Risks And Test Signals
Incorrect VI scale/base/count constants would corrupt PF/VF register ownership. Build coverage should include both `CONFIG_SFC_SIENA_SRIOV=y` and disabled cases. Runtime signals are correct VF count/resource sizing and no SR-IOV callbacks used when the feature is compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/siena_sriov.h -->
