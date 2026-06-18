# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/devlink/devlink.c

## Purpose
`devlink.c` adds devlink integration for ixgbe physical functions. It exposes device identity and firmware versions, supports E610 flash update and firmware activation reload through EMP reset, allocates the adapter through `devlink_alloc()`, and registers a physical devlink port with a PCI DSN based switch ID.

## Important APIs, Types, and Functions
`struct ixgbe_info_ctx` stores formatted version strings and pending E610 inactive bank metadata. Version helpers format DSN, OROM, ETRACK, firmware API/build/security revision, NVM, and netlist versions. `ixgbe_devlink_info_get()` is the devlink info callback. E610-specific callbacks are `ixgbe_devlink_info_get_e610()` and `ixgbe_devlink_pending_info_get_e610()`. Reload operations are `ixgbe_devlink_reload_empr_start()` and `ixgbe_devlink_reload_empr_finish()`. Public lifecycle functions are `ixgbe_allocate_devlink()` and `ixgbe_devlink_register_port()`.

## Control Flow
Info retrieval allocates a context, refreshes E610 firmware version if needed, publishes serial number and board ID, publishes running OROM and bundle ID, then for E610 discovers device capabilities, reads inactive bank versions for pending updates, and publishes running and stored firmware component versions. Firmware activation reload is E610-only: reload down checks pending updates and EMP reset availability, triggers `ixgbe_aci_nvm_update_empr()`, and reload up polls `FWSM` until firmware valid, records the performed action, clears mismatch/rollback flags, and refreshes firmware version.

## State and Persistence Behavior
The file creates runtime devlink objects (`adapter->devlink`, `adapter->devlink_port`) and reads firmware/NVM state from hardware. Flash update and EMP reload alter persistent device firmware banks through helpers in the firmware update code, while this file mainly exposes metadata and triggers activation. Adapter flags for API mismatch and rollback are cleared after successful reload.

## Dependencies and Integration Points
It integrates with Linux devlink info, flash update, reload, and port APIs; PCI DSN; ixgbe EEPROM/NVM helpers; E610 Admin Command Interface helpers; PLDM image flashing; and adapter allocation used by probe. It depends on `devlink.h` declarations and `ixgbe_fw_update.h`.

## Risks and Edge Cases
Most extended version reporting is E610-specific and must not run on older MACs. Pending inactive bank reads are best effort and clear the pending flag on read failure, which can hide stored version details. EMP reset is rejected if no pending update exists or if firmware disables EMP reset. Reload finish uses fixed 500 ms polling up to 10 seconds and returns `-ETIME` if firmware valid never appears.

## Test Signals
Use `devlink info` on legacy ixgbe and E610 devices, flash image update with pending versions, `devlink reload action fw_activate`, no-pending reload rejection, EMP-disabled rejection, firmware-valid timeout injection, and devlink port registration failure injection.
