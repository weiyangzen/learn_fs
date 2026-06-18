# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.c

## Purpose
This file handles ATL2 firmware selection and A2 firmware reboot/soft-reset sequencing. It chooses the A2 firmware ops table, records the firmware version, marks chip features, and performs low-level MCP boot restart polling.

## Important APIs, types, and functions
The exported functions are `hw_atl2_utils_initfw` and `hw_atl2_utils_soft_reset`. Internal helper `hw_atl2_mcp_boot_complete` checks the MCP boot register and host request interrupt. Boot state bits include `AQ_A2_BOOT_STARTED`, `AQ_A2_CRASH_INIT`, `AQ_A2_BOOT_CODE_FAILED`, `AQ_A2_FW_INIT_FAILED`, and `AQ_A2_FW_INIT_COMP_SUCCESS`; request bits include reboot, host boot, MAC fast boot, and PHY fast boot.

## Control flow
`hw_atl2_utils_initfw` reads the firmware version through the shared-buffer firmware ops, accepts version 1.x as expected, logs but continues for other versions, assigns `aq_a2_fw_ops`, calls firmware init, and sets `ATL_HW_CHIP_ANTIGUA`. `hw_atl2_utils_soft_reset` clears host request interrupt, writes a reboot request to the MCP boot register, polls for boot start, polls for boot complete or host-boot request, checks failure bits, rejects dynamic firmware load requests, and reinitializes firmware ops if available.

## State and persistence
The code updates `self->fw_ver_actual`, `self->aq_fw_ops`, and `self->chip_features`. It also writes MCP boot and interrupt-clear registers. No filesystem persistence exists.

## Dependencies and integration points
It depends on `hw_atl2_llh` boot/interrupt helpers, `hw_atl2_utils_fw.c` for `aq_a2_fw_ops` and version reading, Linux `iopoll`, and common Atlantic utility logging/version matching. `hw_atl2.c` calls this through `hw_prepare` and reset paths.

## Risks
Unsupported firmware versions are logged but still use `aq_a2_fw_ops`; this favors compatibility but can hide ABI drift. Dynamic host firmware load is explicitly not implemented and returns `-EIO`. Poll timeouts are long enough for boot but can delay probe/reset failure paths. `AQ_CFG_FAST_START` changes reboot request behavior at compile time.

## Test signals
Probe/reset logs should show detected firmware, boot start, boot complete, and no failure bits. Fault injection or hardware logs can validate timeout and failed boot paths. Builds with and without `AQ_CFG_FAST_START` should be checked if that option is used.
