# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/Makefile

## Purpose
Defines how the Aquantia PHY driver is linked from its submodules.

## Important APIs, Types, and Functions
`aquantia-objs` always includes `aquantia_main.o`, `aquantia_firmware.o`, and `aquantia_leds.o`. When `CONFIG_HWMON` is set, it also includes `aquantia_hwmon.o`. `obj-$(CONFIG_AQUANTIA_PHY)` emits the final `aquantia.o` object.

## Control Flow and State
Build-time composition is conditional on HWMON. Runtime behavior in `aquantia.h` stubs out `aqr_hwmon_probe` when HWMON is not reachable, while this Makefile ensures the implementation is linked only when needed.

## Dependencies and Integration Points
Depends on the parent `CONFIG_AQUANTIA_PHY` symbol and optional `CONFIG_HWMON`. Integrates the firmware, LED, HWMON, and main driver modules into one PHY driver.

## Risks and Test Signals
Risks include mismatched stubs and object composition, unresolved HWMON symbols, or missing LED/firmware objects from the aggregate. Test signals are Aquantia builds with HWMON enabled and disabled, plus module symbol checks for `aqr_firmware_load`, LED callbacks, and `aqr_hwmon_probe`.
