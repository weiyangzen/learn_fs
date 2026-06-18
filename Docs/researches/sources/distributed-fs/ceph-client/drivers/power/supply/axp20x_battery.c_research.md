<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c

## Purpose

`axp20x_battery.c` implements the battery power-supply driver for AXP209, AXP221, AXP717, and AXP813 PMIC battery/charger blocks. It reports battery presence, charge status, health, voltage/current, capacity, charge current limits, charge voltage limits, and minimum voltage cutoff, with variant-specific register encodings and IIO channel requirements.

## Important APIs, Types, And Functions

`struct axp20x_batt_ps` stores regmap, device, registered battery supply, IIO channels, maximum constant charge current, variant callbacks, and AXP717 thermistor-disable state. `struct axp_data` describes constant-charge-current scaling, register/mask selection, fuel-gauge validity behavior, power-supply descriptor, max-voltage callbacks, IIO setup, and battery-info programming.

Classic AXP20x/22x/813 paths use `axp20x_battery_get_prop()` and `axp20x_battery_set_prop()`. AXP717 uses `axp717_battery_get_prop()` and `axp717_battery_set_prop()` because status, presence, faults, CV voltage, current limit, and poweroff voltage live in different registers. Voltage-limit helpers decode/encode safe CV values; the setters intentionally reject high lithium-unsafe values such as AXP20x 4.36 V, AXP717 4.35/4.4/5.0 V, and AXP22x 4.22/4.24 V. `axp209_set_battery_info()` and `axp717_set_battery_info()` apply firmware battery information after registration.

## Control Flow

Probe rejects disabled OF nodes, allocates state, gets the parent regmap, selects variant data from OF, configures required IIO channels, registers the battery power supply, reads optional `power_supply_battery_info`, applies design voltage/current values, then initializes `max_ccc` from the current hardware setting. There are no local IRQ handlers; state changes are surfaced by polling properties or external power-supply notifications from other drivers.

## State And Persistence

The driver keeps `max_ccc` as policy state used to bound later current writes. Register writes change PMIC charger configuration: charge enable, CV voltage, constant charge current, poweroff/min voltage, and on AXP717 TS-pin disable. AXP717 `HEALTH` reads clear fault bits by writing them back, so health queries have side effects intended to allow recurring faults to reappear.

## Dependencies And Integration Points

The file integrates with the AXP20x MFD regmap, OF match table, IIO channels (`batt_v`, `batt_chrg_i`, and for classic variants `batt_dischrg_i`), and generic power-supply battery-info parsing. AXP717 also reads the firmware property `x-powers,no-thermistor` and expects monitored battery data before disabling the TS pin.

## Risks And Edge Cases

`axp20x_power_probe()` unconditionally refreshes `max_ccc` from the register after applying battery info, which can override the intended firmware-derived software maximum. AXP717 `CONSTANT_CHARGE_CURRENT_MAX` returns the current programmed charge current but also uses that property as the writable current limit, unlike classic variants where current and max-current are distinct. AXP717 current reporting carries a documented unknown offset and is left raw. Missing or invalid fuel-gauge-valid bits can make capacity return `-EINVAL` on AXP22x/813.

## Test Signals

Build coverage should include all compatibles. Runtime tests should verify IIO scaling, capacity-valid behavior, no-battery capacity behavior on classic variants, AXP717 fault-to-health mapping and fault clearing, safe voltage rejection, charge enable/disable through `STATUS`, DT battery-info application, and `x-powers,no-thermistor` behavior on boards without a battery thermistor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_battery.c -->
