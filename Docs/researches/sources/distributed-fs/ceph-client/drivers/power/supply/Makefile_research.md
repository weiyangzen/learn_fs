# sources/distributed-fs/ceph-client/drivers/power/supply/Makefile

Purpose: this Kbuild file maps power-supply Kconfig symbols to compiled objects. It builds the core `power_supply.o`, optional helper objects, and one object per battery/charger/fuel-gauge driver, including the subset drivers.

Important APIs, types, and functions: this is declarative Kbuild. `subdir-ccflags-$(CONFIG_POWER_SUPPLY_DEBUG) := -DDEBUG` enables debug messages. `power_supply-y` combines core pieces, conditionally adding sysfs and LED trigger support. Relevant object mappings are `obj-$(CONFIG_BATTERY_88PM860X) += 88pm860x_battery.o`, `obj-$(CONFIG_CHARGER_88PM860X) += 88pm860x_charger.o`, and `obj-$(CONFIG_AB8500_BM) += ab8500_bmdata.o ab8500_charger.o ab8500_fg.o ab8500_btemp.o ab8500_chargalg.o`.

Control flow: Kbuild expands each `obj-$(CONFIG_...)` according to generated config values. Tristate symbols produce built-in or module objects; bool symbols produce only built-in participation. The AB8500 battery-management symbol pulls multiple cooperating compilation units into the same built-in group.

State and persistence: no runtime state exists. Build state appears in generated object files and module artifacts. The Makefile ordering can matter for built-in link ordering and initialization availability.

Dependencies and integration points: the file depends on Kconfig symbols from the sibling Kconfig and on the source files being present with matching names. It integrates with subsystem-wide Kbuild and module installation. `power_supply-y` composition integrates power supply core, sysfs, LEDs, and hwmon support.

Risks: stale object mappings cause selected drivers to silently not build or obsolete files to be referenced. Multi-object groupings like AB8500 can hide intra-group link dependencies and require all companion files to remain buildable together. Debug flags affect every file in the directory, so enabling `POWER_SUPPLY_DEBUG` can alter logging volume broadly.

Test signals: run `make drivers/power/supply/` or targeted object builds for `88pm860x_battery.o`, `88pm860x_charger.o`, and the AB8500 object group under matching configs. Confirm module names and built-in object lists match Kconfig help and that no object is orphaned by `rg '^obj-\\$'` comparisons.
