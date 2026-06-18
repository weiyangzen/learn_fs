<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h

## Purpose
`pdata.h` defines board-supplied platform data for WM831x devices. It lets non-DT board files describe charger policy, backup battery charging, regulator init data, LEDs, touchscreen IRQs, watchdog action, GPIO defaults, and probe-time hooks.

## Important APIs, types, and functions
Key structs include `wm831x_backlight_pdata`, `wm831x_backup_pdata`, `wm831x_battery_pdata`, `wm831x_buckv_pdata`, `wm831x_status_pdata`, `wm831x_touch_pdata`, `wm831x_watchdog_pdata`, and the aggregate `wm831x_pdata`. Enums define status LED source selection and watchdog actions. Array sizing macros include `WM831X_MAX_STATUS`, `WM831X_MAX_DCDC`, `WM831X_MAX_EPE`, `WM831X_MAX_LDO`, `WM831X_MAX_ISINK`, and `WM831X_GPIO_NUM`.

## Control flow
The MFD core receives `wm831x_pdata`, optionally calls `pre_init`, configures IRQ/GPIO base behavior, creates child devices, supplies per-regulator `regulator_init_data`, and then calls `post_init`. Child drivers consume their sub-structs during probe.

## State and persistence behavior
Platform data is static board configuration. It is not persisted by the driver, but values can program persistent hardware state until reset, suspend, or power loss depending on the target register.

## Dependencies and integration points
The header references `struct wm831x`, `struct regulator_init_data`, Linux `bool`, regulator framework data, LED triggers, IRQ flags, GPIO numbering, charger and watchdog child drivers, and board setup code.

## Risks and test signals
Risks include invalid regulator array indexing, units confusion between mA/uA/mV/minutes, stale GPIO defaults, missing IRQ flags for touch events, and unsafe watchdog reset policy. Test signals include board probe with full/partial pdata, regulator constraint validation, charger limit programming, watchdog action tests, and suspend/shutdown behavior when `soft_shutdown` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pdata.h -->
