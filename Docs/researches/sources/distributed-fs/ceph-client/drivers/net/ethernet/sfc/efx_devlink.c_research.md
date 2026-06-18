# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_devlink.c

Purpose: Implements devlink registration, info reporting, flash update dispatch, and EF100 MAE devlink port registration/MAC operations for PF and VF representor ports.

Important APIs and functions: Public lifecycle functions are `efx_probe_devlink_and_lock()`, `efx_probe_devlink_unlock()`, `efx_fini_devlink_lock()`, and `efx_fini_devlink_and_unlock()`. EF100 SR-IOV helpers include PF/representor set/unset devlink port functions. Devlink ops include `.info_get` and `.flash_update`. Static info helpers report stored NVRAM versions and running MC/FPGA/datapath/SoC/board versions across GET_VERSION output revisions.

Control flow: Probe skips VFs, allocates devlink private storage, locks and registers devlink, and stores `efx`. Info requests query board config, NVRAM partition metadata, and running versions, reporting errors via extack while returning devlink info fields. Flash update passes firmware to `efx_reflash_flash_firmware()`. Under SR-IOV, mport descriptors are converted to devlink PCI PF/VF port attrs; VF port MAC get/set looks up firmware client IDs and uses MCDI MAC commands.

State and persistence: Maintains `efx->devlink`, devlink private `efx`, `efx->dl_port`, and `efx_rep->dl_port`. Firmware/NVRAM versions and MACs are persistent device state queried or modified through MCDI.

Dependencies and integration points: Uses Linux devlink APIs, MCDI version/NVRAM/board/MAC commands, EF100 MAE mport lookup, EF100 representor structs, and reflash code. Called from PCI probe/remove and representor lifecycle.

Risks: Devlink lock/unlock ordering spans netdev registration; failures after devlink registration need balanced cleanup. Info reporting ORs errors and emits a generic extack while individual helpers log details. MAC set is restricted to VF mports. Port registration silently ignores alias/undefined mports. Version parsing depends on output length and flags matching firmware command versions.

Test signals: PF devlink registration/unregistration, VF probe skipping devlink, `devlink info` on firmware with V1 through V5 GET_VERSION layouts, missing NVRAM partitions, flash update dispatch, MAE PF/VF devlink ports, VF MAC get/set success/failure, and cleanup on representor removal.
