# sources/distributed-fs/ceph-client/drivers/power/supply/chagall-battery.c

Purpose: implements an I2C/regmap fuel-gauge and power LED driver for Pegatron Chagall EC hardware. It exposes a battery power supply backed by EC registers and registers amber/white power LEDs with charging/full default triggers.

Important APIs/types/functions: `struct chagall_battery_data` stores regmap, two `led_classdev`s, power supply, delayed poll work, and last status. `chagall_battery_get_value()` reads two little-endian EC registers for most properties. `chagall_battery_get_property()` converts raw status, temperature, voltage, current, and charge values to power_supply units. `chagall_battery_poll_work()` polls status and emits `power_supply_changed()` when it changes. LED callbacks write brightness to `CHAGALL_REG_LED_AMBER` and `CHAGALL_REG_LED_WHITE`.

Control flow: probe allocates state, initializes an 8-bit regmap, registers the battery supply, registers amber and white LEDs, forces both LEDs off, initializes autocancel delayed work, and starts periodic status polling every five seconds. Property reads directly fetch the corresponding EC register pair and convert units. Suspend cancels poll work; resume schedules it again. The I2C driver binds to `pegatron,chagall-ec`.

State and persistence: `last_state` is the only cached battery state and is used to suppress duplicate change notifications. LED brightness writes affect EC LED registers until firmware/hardware changes them. Battery measurements are read on demand; there is no persistent configuration or writable power-supply property.

Dependencies and integration: depends on I2C, regmap, LED class, devm delayed work helpers, power_supply core, and OF matching. The battery supply uses `external_power_changed = power_supply_changed`, so charger changes can notify the supply without driver-local processing.

Risks and test signals: `regmap_bulk_read()` is asked to read two values into a `u32 *` while the regmap has 8-bit values; reviewers should confirm the intended byte packing across regmap implementations. Status ignores `BATTERY_FULL_DISCHARGED` and treats any non-full/non-discharging state as charging. Polling only detects status changes, not capacity/voltage changes. LED writes ignore regmap errors. Test register endianness, status bit precedence, unit conversions, LED registration and brightness writes, suspend/resume work cancellation, and repeated EC read failures.
