# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fw_update.c

## Purpose
Implements devlink firmware flashing for Intel `ice` devices using Linux PLDM firmware parsing and device AdminQ NVM commands. It validates PLDM records against the PCI device, sends package/component metadata to firmware, erases inactive NVM banks, writes component data in AdminQ-sized blocks, activates updated banks, and reports the reset action needed to complete activation.

## Important APIs, types, and functions
- `struct ice_fwu_priv` embeds `struct pldmfw` and carries `ice_pf`, `netlink_ext_ack`, activation flags, required reset level, and EMP reset availability across PLDM callbacks.
- `ice_devlink_flash_update()` is the devlink entry point. It validates overwrite policy, unified-update support, optional single-component `fw.mgmt` mode, cancels prior pending updates, acquires the NVM write lock, and calls `pldmfw_flash_image()`.
- `ice_send_package_data()` forwards matching PLDM record package data via `ice_nvm_set_pkg_data()`.
- `ice_send_component_table()` builds `struct ice_aqc_nvm_comp_tbl`, sends it with `ice_nvm_pass_component_tbl()`, and delegates firmware response interpretation to `ice_check_component_response()`.
- `ice_flash_component()` maps PLDM component IDs to NVM modules and devlink component names: `NVM_COMP_ID_OROM` -> `fw.undi`, `NVM_COMP_ID_NVM` -> `fw.mgmt`, `NVM_COMP_ID_NETLIST` -> `fw.netlist`.
- `ice_erase_nvm_module()` and `ice_write_nvm_module()` perform erase/write sequencing with devlink progress notifications.
- `ice_write_one_nvm_block()` is exported for one-block write plus firmware completion validation.
- `ice_finalize_update()` calls `ice_switch_flash_banks()` and emits the user-facing activation instruction.
- `ice_get_pending_updates()` refreshes device capabilities from firmware and builds a pending-update bitmap.

## Control flow
`ice_devlink_flash_update()` rejects unsupported overwrite masks, rejects devices without unified update outside recovery mode, initializes PLDM ops based on MAC type, cancels any previous pending update, and holds the NVM resource while `pldmfw_flash_image()` invokes the callback sequence. The callback sequence sends package data, sends component tables, erases inactive banks, writes data in `ICE_AQ_MAX_BUF_LEN` chunks, waits for AdminQ completion events, then activates selected banks. Completion paths map firmware and PLDM failures to devlink status and netlink extended ACK messages.

## State and persistence behavior
Persistent state is in device flash banks, not host files. `activate_flags` accumulates selected components and preservation mode until activation. `reset_level` is captured from the final NVM-bank write when firmware supports reset avoidance; otherwise it defaults to full power cycle. `pf->fw_emp_reset_disabled` records whether EMP reset activation is unavailable after bank switching or reset-cancellation uncertainty. Pending-update state is read from fresh firmware capabilities rather than cached `hw->dev_caps`.

## Dependencies and integration points
Depends on `linux/pldmfw.h`, devlink flash-update callbacks, AdminQ NVM helpers (`ice_aq_update_nvm`, `ice_aq_erase_nvm`, `ice_nvm_write_activate`, `ice_acquire_nvm`), PCI IDs, recovery-mode checks, and firmware capability discovery. It integrates with `devlink/devlink.c` through `ice_devlink_flash_update()` and pending-update reporting.

## Risks
The code depends on exact firmware completion events; mismatched module or offset is treated as corruption and fails the update. NVM resource ownership is critical: most helpers assume the caller already acquired the flash lock. Timeout tuning is operationally important because erase can legitimately take minutes and writes can exceed one second. Component response handling must stay aligned with firmware codes or users will get incorrect update rejection reasons.

## Test signals
Useful validation includes devlink flash update success/failure on matching and non-matching PLDM images, overwrite-mask rejection, single `fw.mgmt` component mode, pending-update cancellation, recovery-mode partial-check behavior, AdminQ timeout/error injection, and activation messages for EMP, PCIe reset, and power-cycle paths.
