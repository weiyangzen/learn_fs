# sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_backup.c

## Purpose
`wm831x_backup.c` exposes the WM831x backup battery charger as a battery power-supply device. It optionally configures backup charging from platform data and reports status, voltage, and presence.

## Important APIs, Types, And Functions
`struct wm831x_backup` holds the parent PMIC, power-supply handle, descriptor, and generated name. `wm831x_config_backup()` validates and programs backup charger enable, detection, voltage limit, current limit, and constant-voltage mode. `wm831x_backup_read_voltage()` uses AUXADC. `wm831x_backup_get_prop()` reads `WM831X_BACKUP_CHARGER_CONTROL` and serves properties.

## Control Flow
Probe obtains the parent `struct wm831x`, allocates state, calls `wm831x_config_backup()` while tolerating configuration failures, constructs a per-PMIC or default name, fills the descriptor, and registers the supply. Property reads first read the backup charger control register, then report charging status, AUXADC backup voltage, or present based on the charger-status bit.

## State, Persistence, And Dependencies
Driver state is just the descriptor and parent pointer. Hardware state persists in the backup charger control register. Dependencies include WM831x core register locking/unlocking, AUXADC, platform data, and power-supply core.

## Integration Points
The platform driver name is `wm831x-backup`. It is an MFD child of a WM831x PMIC and uses `wm831x_pdata->backup` when available.

## Risks
Configuration failures are intentionally nonfatal, which can leave hardware in bootloader/default state while still registering a readable supply. `PRESENT` is inferred from `WM831X_BKUP_CHG_STS`, which may indicate charger activity rather than physical cell presence. Invalid voltage/current platform values log errors but do not fail probe.

## Test Signals
Validate platform data combinations, invalid `vlim`/`ilim` logging, register unlock failure, AUXADC read failure, status/presence mapping, multiple PMIC naming, and operation when no backup config is provided.
