# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/devlink.c

## Purpose
This file provides the ZL3073x devlink integration: device info reporting, driver reinit reload, firmware flash update, allocation of `struct zl3073x_dev` inside a devlink instance, and registration of the `clock_id` driverinit parameter.

## Important APIs and functions
External APIs are `zl3073x_devm_alloc()`, `zl3073x_devlink_register()`, and `zl3073x_devlink_flash_notify()`. Devlink ops are `info_get`, `reload_down`, `reload_up`, and `flash_update`. Static helpers prepare and finish flash mode around `zl3073x_fw_flash()`.

## Control flow
Info reads chip ID, revision, firmware version, and custom config version from registers and publishes fixed/running versions. Reload down supports only `DEVLINK_RELOAD_ACTION_DRIVER_REINIT` and stops normal DPLL operation. Reload up reads the driverinit `clock_id`, applies it if changed, and restarts normal operation without full invariant refetch. Flash update parses the provided firmware, stops normal operation, enters flash mode using the utility component, flashes all present components, leaves flash mode, restarts normal operation, frees firmware memory, and sends final status.

## State and persistence
Devlink owns the allocation container for `struct zl3073x_dev`. `clock_id` is driverinit state that persists across DPLL registration after reload but is not stored in device flash by this code. Firmware flashing modifies device flash through `flash.c`.

## Dependencies and integration points
It depends on `core.c` register/start/stop helpers, `fw.c` parsing/flashing orchestration, `flash.c` flash-mode entry/exit, and devlink APIs. Normal DPLL operation is deliberately stopped before flash mode because normal firmware APIs are unavailable there.

## Risks and tests
If flash prepare fails, the code tries to resume normal operation. `zl3073x_flash_mode_leave()` return is ignored in finish prepare paths, so restart errors are the main visible signal. Tests should cover devlink info, invalid zero clock ID, reload with changed clock ID, malformed firmware, missing utility component, interrupted flashing, and restart after flash failure.
