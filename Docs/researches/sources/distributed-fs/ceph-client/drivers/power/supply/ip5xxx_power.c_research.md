# sources/distributed-fs/ceph-client/drivers/power/supply/ip5xxx_power.c

## Purpose
This I2C driver supports Injoinic IP5xxx power-bank controllers. It registers two supplies from one chip: `ip5xxx-battery` for charger/battery telemetry and writable charge settings, and `ip5xxx-boost` for the USB boost converter output. It also replays an initialization sequence after chip shutdown, because the controller may stop responding on I2C when VIN is absent and boost is off.

## Important APIs, Types, and Functions
`struct ip5xxx` contains the regmap, an `initialized` flag, nested `regmap_field` pointers for charger, boost, battery ADC, button, and WLED controls, plus per-chip scaling constants. `struct ip5xxx_regfield_config` describes field locations and unsupported fields for IP51xx and IP5306 families. `ip5xxx_read()` and `ip5xxx_write()` wrap regmap fields and clear `initialized` on bus errors. `ip5xxx_initialize()` disables light-load shutdown, enables load/VIN wake behavior, enables long-press shutdown, enables NTC when present, and configures button behavior. Battery helpers decode charger status, charge type, health, max voltage, ADC voltage/current/open-circuit voltage, and writable current/voltage/status properties. Boost helpers expose online state and undervoltage limit.

## Control Flow
Probe initializes an 8-bit I2C regmap, selects field config from OF match data or defaults to IP51xx, allocates supported regmap fields, copies scaling constants, then registers the battery and boost power supplies with shared driver data. Every get/set property first calls `ip5xxx_initialize()`, making initialization lazy and repeatable after an I2C error or chip power loss.

## State and Persistence
Driver state is mostly field mappings and cached scaling constants. Hardware state includes charge enable, voltage/current selections, boost enable, undervoltage threshold, NTC/button settings, and auto power behavior. The `initialized` boolean is a software cache of whether the wake/policy sequence has succeeded since the last bus error.

## Dependencies and Integration Points
It depends on I2C regmap, regmap-field allocation, OF compatibles for `injoinic,ip5108`, `ip5109`, `ip5207`, `ip5209`, and `ip5306`, and the power-supply core. Unsupported fields are represented by invalid reg ranges and become `NULL`, with accessors returning `-EOPNOTSUPP`.

## Risks
The write paths compute register values with limited range checking, so out-of-range user values can wrap or program unintended bit patterns if the power-supply core does not constrain them. `ip5xxx_setup_reg()` ignores individual field allocation failures, which turns later property access into unsupported-field errors rather than probe failure. ADC conversions are fixed formulas and must match chip variant. Mutable `psy_desc.type` is not used here, but shared state still means battery and boost operations can interleave without a mutex.

## Test Signals
Test both IP51xx and IP5306 field maps, lazy initialization after simulated I2C failures, battery status fallback through `chg_end`, unsupported-property behavior on IP5306 ADC-less fields, writable charge current/voltage/status, boost online and undervoltage writes, and ADC conversion sanity for positive and negative signed raw values.
