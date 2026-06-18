# sources/distributed-fs/ceph-client/drivers/power/supply/test_power.c

## Purpose
`test_power.c` is a synthetic power-supply driver used to exercise power-supply core behavior from module parameters. It registers AC, USB, and battery supplies with adjustable online, status, health, capacity, voltage, current, charge type, charge behavior, and optional extension properties.

## Important APIs, Types, And Functions
Key data is stored in file-scope module parameters such as `ac_online`, `usb_online`, `battery_status`, `battery_capacity`, `battery_charge_behaviour`, and `battery_extension`. `test_power_get_*_property()` callbacks expose AC, USB, and battery properties. `test_power_set_battery_property()` validates bitmasks in `power_supply_desc` before setting charge behavior/type. `test_power_battery_ext*()` implements a `struct power_supply_ext` for manufacture year, max temperature, and `TIME_TO_EMPTY_NOW`. Parameter handlers use `struct kernel_param_ops`, `map_get_value()`, `map_get_key()`, and `power_supply_changed()`.

## Control Flow
Module init registers three supplies from `test_power_desc[]` and `test_power_configs[]`, then registers the battery extension by default. Reads return static or parameter-backed values. Module parameter writes parse string maps or integers, update globals, and notify the corresponding supply after initialization. The battery extension parameter toggles `power_supply_register_extension()` and `power_supply_unregister_extension()`. Module exit forces AC/USB off, sends change events, sleeps 10 seconds to let observers see the event, unregisters supplies, and clears `module_initialized`.

## State, Persistence, And Dependencies
All state is volatile module-global memory. There is no locking around parameter updates or property reads, so it relies on simple integer/bool stores being adequate for a test fixture. It depends on the power-supply core, module parameter infrastructure, generated `UTS_RELEASE`, and extension APIs.

## Integration Points
The AC and USB supplies list `test_battery` as a supplicant. The battery descriptor advertises writable charge behavior and charge type masks and exposes extension-backed properties when enabled. It is not bound to hardware or firmware.

## Risks
Several `param_get_battery_*()` functions use `map_ac_online` instead of their matching maps, so status/health/presence/technology reads can report `unknown` or wrong strings even when writes succeeded. `param_set_battery_present()` notifies `TEST_AC` rather than the battery. `test_power_configure_battery_extension()` sets `battery_extension = enable` even if unregistering an extension that may not be registered or after registration failure paths, so parameter state can diverge from extension state. Lack of locking can expose races during concurrent parameter writes and property reads, acceptable only for testing.

## Test Signals
Load/unload the module and monitor uevents, verify all advertised properties, write valid and invalid charge behavior/type values, toggle `battery_extension`, validate parameter string maps, confirm `power_supply_changed()` fires only after initialization, and specifically test the suspicious getter maps and presence-notification target.
