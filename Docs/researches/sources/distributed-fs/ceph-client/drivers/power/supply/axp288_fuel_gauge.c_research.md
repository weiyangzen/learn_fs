<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c

## Purpose

`axp288_fuel_gauge.c` is the native AXP288 battery fuel-gauge driver for Intel tablet-class systems. It reports battery status, presence, health, voltage, OCV, capacity, low-capacity alert threshold, technology, and, unless disabled by module parameter, charge/current values derived from coulomb-counter and IIO channels.

## Important APIs, Types, And Functions

`struct axp288_fg_info` stores regmap, six IRQs, three IIO channels, registered battery supply, mutex, static initial state, and cached measurement registers. `fuel_gauge_update_registers()` is the main refresh path: it blocks P-unit I2C access, reads input status and capacity, reads battery voltage IIO, reads OCV, optionally reads charge/discharge current and 15-bit coulomb-counter/design-capacity words, then caches results for 60 seconds.

`fuel_gauge_get_status()` derives charging, discharging, and full states from VBUS validity, fuel-gauge valid/capacity bits, charge direction, discharge current, and the `no_current_sense_res` mode. `fuel_gauge_get_property()` maps cached values to power-supply units. `fuel_gauge_set_property()` writes the low-capacity alert threshold. `axp288_fuel_gauge_read_initial_regs()` validates fuel-gauge enable/configuration, determines max design voltage, reads initial battery presence, and reads low-capacity threshold.

## Control Flow

Probe requires the native-driver ACPI quirk, applies DMI no-battery exclusions for mini PCs and HDMI sticks, allocates state, maps platform IRQs to virtual regmap IRQs, obtains global IIO channels by name because x86 lacks normal device/channel maps, validates initial PMIC state with IOSF P-unit access blocked, optionally removes current-related properties when `no_current_sense_res` is set, registers the battery supply, and requests threaded IRQs.

## State And Persistence

Measurements are cached for 60 seconds and invalidated on fuel-gauge IRQs or `external_power_changed()`. The only normal writable user state is `CAPACITY_ALERT_MIN`, persisted in `AXP288_FG_LOW_CAP_REG`. The module parameter `no_current_sense_res` changes the property surface and capacity source for the lifetime of the module.

## Dependencies And Integration Points

Dependencies include AXP20x MFD regmap/IRQ, Intel IOSF MBI, ACPI quirk helpers, DMI quirk matching, IIO channels named `axp288-chrg-curr`, `axp288-chrg-d-curr`, and `axp288-batt-volt`, and power-supply external-power notifications from the charger.

## Risks And Edge Cases

No-battery DMI matching is essential because some headless systems falsely report a battery. `fuel_gauge_desc.num_properties` is mutated globally when `no_current_sense_res` is set; this is acceptable for a single driver instance but risky for hypothetical mixed instances. Capacity-invalid bits only log an error and still return masked capacity. Missing platform IRQs are skipped during mapping, but the request loop later requests all six `info->irq[]` entries, so zero/uninitialized IRQ values are a risk if firmware omits entries. Current sign depends on charge-direction state and separate charge/discharge IIO channels.

## Test Signals

Tests should cover DMI no-battery exclusions, probe deferral for missing IIO channels, `no_current_sense_res` property count and capacity source, 15-bit valid-bit failures, low-capacity threshold writes, full-status heuristics near 90-100 percent, external-power invalidation, all six fuel-gauge IRQs, and IOSF unblock behavior after read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp288_fuel_gauge.c -->
