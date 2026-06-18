# sources/distributed-fs/ceph-client/drivers/watchdog/cros_ec_wdt.c

## Purpose
This driver exposes the ChromeOS Embedded Controller hang-detect watchdog as a Linux watchdog. All hardware control is done by EC host commands rather than local registers.

## Important APIs, types, and functions
`union cros_ec_wdt_data` overlays EC request and response payloads. `cros_ec_wdt_send_cmd` builds `EC_CMD_HANG_DETECT` messages and calls `cros_ec_cmd_xfer_status`. Watchdog ops are `cros_ec_wdt_ping`, `cros_ec_wdt_start`, `cros_ec_wdt_stop`, and `cros_ec_wdt_set_timeout`. Probe uses parent `cros_ec_dev` data and EC status commands.

## Control Flow
Probe sends `GET_STATUS`, maps EC watchdog reset status to `WDIOF_CARDRESET`, clears EC status, initializes min/max from EC constants, and registers the watchdog. Start sends `SET_TIMEOUT` with the current reboot timeout, ping sends `RELOAD`, stop sends `CANCEL`, and set-timeout rolls back the cached timeout if the EC command fails. Suspend stops an active watchdog and resume starts it again.

## State and Persistence
The Linux side stores only the watchdog core object and parent EC pointer. The EC owns actual watchdog timing and reset status, which can persist across AP resets until explicitly cleared during probe.

## Dependencies and Integration Points
The driver depends on the cros_ec platform data/protocol headers, platform device binding name `cros-ec-wdt`, EC command transport, PM callbacks, and watchdog core.

## Risks and Test Signals
Risks include EC command version/payload mismatch, bootstatus clear failure, suspend/resume leaving EC watchdog canceled, and timeout rollback correctness. Tests should cover successful and failing EC commands, AP boot caused by EC watchdog, min/max timeout validation through watchdog core, active suspend/resume, and unregister/reboot stop semantics.
