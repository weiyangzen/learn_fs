# sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_power.c

## Purpose
`wm831x_power.c` is the main WM831x PMIC power-supply driver. It registers wall, USB, and optionally battery supplies; configures the battery charger from platform data; reports source/voltage/health/charge state; handles PMIC IRQs; and optionally tracks USB PHY current-limit notifications.

## Important APIs, Types, And Functions
`struct wm831x_power` stores parent PMIC, supply handles/descriptors/names, battery-present flag, USB PHY, and notifier. Wall/USB helpers use `wm831x_power_check_online()` and `wm831x_power_read_voltage()`. Battery configuration is built from `struct chg_map` tables and `wm831x_battery_apply_config()` inside `wm831x_config_battery()`. Runtime status helpers are `wm831x_bat_check_status()`, `wm831x_bat_check_type()`, and `wm831x_bat_check_health()`. IRQ handlers include `wm831x_bat_irq()`, `wm831x_syslo_irq()`, and `wm831x_pwr_src_irq()`.

## Control Flow
Probe allocates state, builds names, configures the charger if platform data is present, registers wall and USB supplies, checks `CHARGER_CONTROL_1` to decide whether to register the battery, requests SYSLO, power-source, and eight battery IRQs, and optionally registers a USB PHY notifier from the `phys` phandle. Power-source IRQs notify wall/USB/battery; battery IRQs notify battery if present; USB limit notifications choose the highest supported current limit no greater than the requested limit and update `WM831X_POWER_STATE`.

## State, Persistence, And Dependencies
Runtime state includes descriptors, `have_battery`, IRQ registrations, and optional USB notifier. Hardware persistence is in charger control, power state, system status, and charger status registers. Dependencies are WM831x MFD core/AUXADC/PMU headers, platform data, IRQ names from the MFD cell, USB PHY notifier, and power-supply core.

## Integration Points
The platform driver is `wm831x-power`. It registers names like `wm831x-wall`, `wm831x-usb`, and `wm831x-battery` with numeric suffixes when platform data provides a PMIC number. Battery is marked `use_for_apm`.

## Risks
Error unwind uses raw `platform_get_irq_byname()` in the battery IRQ loop while registration used `wm831x_irq()`, so failed-probe cleanup may free the wrong Linux IRQ for battery events. The name setup uses `sizeof(power->wall_name)` for battery and USB buffers, currently same size but fragile. Configuration failures are logged but nonfatal. Battery registration is skipped if charger enable is not set after configuration, which can hide a physically present battery when policy disables charging.

## Test Signals
Test charger configuration maps, no-platform-data probe, wall/USB/battery property reads, optional battery registration, all IRQ request/unwind paths, USB PHY notifier current-limit mapping, remove freeing all IRQs, and source-change notifications.
