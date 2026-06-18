# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c

## Purpose

`ixgbe_fw_update.c` implements devlink firmware flashing for E610 ixgbe devices using PLDM firmware packages. It parses a PLDM image through the kernel `pldmfw` helper, passes package metadata and component tables to device firmware, erases inactive NVM banks, writes new component payloads, and requests bank activation. It also exposes a pending-update query used by devlink reload/status code.

## Important APIs, Types, and Functions

The central private state is `struct ixgbe_fwu_priv`, which embeds `struct pldmfw`, carries the `ixgbe_adapter`, netlink `extack`, component activation flags, and whether EMP reset activation is available. Public exports are `ixgbe_flash_pldm_image()` and `ixgbe_get_pending_updates()`.

The PLDM callback table `ixgbe_fwu_ops_e610` wires `pldmfw_op_pci_match_record`, `ixgbe_send_package_data()`, `ixgbe_send_component_table()`, `ixgbe_flash_component()`, and `ixgbe_finalize_update()`. `ixgbe_send_package_data()` copies PLDM package data and sends it with `ixgbe_nvm_set_pkg_data()`. `ixgbe_send_component_table()` accepts only OROM, NVM, and NETLIST component IDs, builds an `ixgbe_aci_cmd_nvm_comp_tbl`, sends it via `ixgbe_nvm_pass_component_tbl()`, and uses `ixgbe_check_component_response()` to translate firmware accept/reject codes into `extack` messages. `ixgbe_write_nvm_module()` writes component bytes in `IXGBE_ACI_MAX_BUFFER_SIZE` blocks using `ixgbe_aci_update_nvm()` and sends devlink progress notifications. `ixgbe_erase_nvm_module()` wraps `ixgbe_aci_erase_nvm()` with a 300-second devlink timeout notice. `ixgbe_switch_flash_banks()` calls `ixgbe_nvm_write_activate()` and decodes EMP reset availability. `ixgbe_cancel_pending_update()` discovers and reverts existing pending inactive-bank updates before a new flash.

## Control Flow

`ixgbe_flash_pldm_image()` starts by rejecting non-E610 hardware. It maps devlink overwrite flags to NVM preservation policy: preserve all, preserve selected settings/identifiers, or preserve nothing. It rejects unsupported overwrite masks and devices without unified-update support unless firmware recovery mode prevents capability discovery. It initializes `ixgbe_fwu_priv`, notifies devlink that flashing is preparing, cancels any pending previous update, acquires the NVM write resource, and calls `pldmfw_flash_image()`. The PLDM helper then calls back into this file for package data, component tables, per-component flash, and finalization. The NVM lock is released after the PLDM helper returns.

For each component, `ixgbe_flash_component()` maps PLDM identifiers to inactive-bank module pointers and devlink component names: OROM to `fw.undi`, NVM to `fw.mgmt`, and NETLIST to `fw.netlist`. It ORs the matching activation flag into `priv->activate_flags`, erases the module, then writes the payload. Finalization activates all selected components in one bank-switch command and updates `adapter->fw_emp_reset_disabled` according to firmware capability.

## State and Persistence Behavior

The file writes persistent device flash on inactive banks and requests a persistent bank activation. `activate_flags` accumulate across components in a single flash session and start with the requested preservation policy. Existing pending updates are persistent device state; this driver can revert them by issuing `IXGBE_ACI_NVM_REVERT_LAST_ACTIV`. `ixgbe_get_pending_updates()` reads device capabilities and returns a volatile bitmap reflecting persistent pending NVM/OROM/NETLIST activation. Runtime state includes devlink progress, `extack` diagnostics, and `adapter->fw_emp_reset_disabled`, which guides later devlink reload behavior but is not itself flash state.

## Dependencies and Integration Points

The implementation depends on Linux `pldmfw`, devlink flash update APIs, netlink extended ACK, E610 Admin Command Interface wrappers (`ixgbe_nvm_set_pkg_data`, `ixgbe_nvm_pass_component_tbl`, `ixgbe_aci_update_nvm`, `ixgbe_aci_erase_nvm`, `ixgbe_nvm_write_activate`), NVM resource locking, and hardware capability discovery. `devlink/devlink.c` registers `ixgbe_flash_pldm_image()` as `.flash_update` and calls `ixgbe_get_pending_updates()` for reload/update status.

## Risks and Test Signals

Firmware update is high risk because failures can leave pending inactive-bank data, require power cycle, or reject later updates. Important risk points are exact component ID filtering, block write offsets and `last_cmd`, NVM lock coverage, preservation flag mapping, canceling pending updates without erasing desired state, and recovery-mode behavior. `ixgbe_send_package_data()` duplicates PLDM bytes because the AdminQ call may mutate or require a writable buffer; allocation failure must abort cleanly. Test signals include devlink flash of matching and non-matching PLDM images, unsupported overwrite masks, downgrade/reject component responses, forced `ixgbe_acquire_nvm()` failure, erase/write failures mid-component, previous pending update cancellation for all and individual components, recovery mode flashing, pending bitmap reporting, and reload guidance when EMP reset is unavailable.
