# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw_fsm.c

## Purpose
`mlxfw_fsm.c` drives firmware flashing through a device-provided FSM callback interface and devlink status notifications. It validates MFA2 firmware, locks the device FSM, optionally reactivates prior firmware state, downloads each matching component in aligned blocks, verifies components, activates the image, and releases the FSM.

## Important APIs, Types, and Functions
The exported API is `mlxfw_firmware_flash()`. Core helpers are `mlxfw_fsm_state_err()`, `mlxfw_fsm_state_wait()`, `mlxfw_fsm_reactivate_err()`, `mlxfw_fsm_reactivate()`, `mlxfw_status_notify()`, `mlxfw_flash_component()`, and `mlxfw_flash_components()`. It maps FSM error codes to Linux errnos and extack messages.

## Control Flow and State
`mlxfw_firmware_flash()` checks the MFA2 fingerprint, initializes the MFA2 parser, locks the firmware FSM, waits for `LOCKED`, runs optional reactivation, waits again, flashes all components matching the device PSID, activates the image, waits for `LOCKED`, releases the handle, reports completion, and frees parser state. Component flashing queries max size/alignment/write size, starts component update, waits for `DOWNLOAD`, sends aligned chunks through `fsm_block_download()`, verifies the component, and waits back to `LOCKED`. On component download/verify errors it cancels the FSM; top-level errors release the handle.

State is primarily device firmware FSM state addressed by `fwhandle`. Software state includes current component, chunk offset, reactivation support flag, extack messages, and devlink progress notifications. No firmware data is persisted by this file directly; persistence happens inside device callbacks.

## Dependencies and Integration Points
The file depends on mlxfw device callbacks, MFA2 parser APIs, devlink flash status notification, netlink extack, kernel sleep, modules, and XZ-backed component extraction in `mlxfw_mfa2.c`.

## Risks and Test Signals
Risks include timeout waiting for FSM state, bad alignment causing invalid download chunks, incorrect errno/extack mapping, failing to cancel after partial component update, device reset requirements after reactivation, and component count/PSID mismatches. Test signals are devlink flash of valid and invalid MFA2 files, PSID-not-found failure, callback fault injection at every FSM step, timeout tests, chunk alignment boundary tests, reactivation supported/unsupported/status-error cases, and devlink progress notifications.
