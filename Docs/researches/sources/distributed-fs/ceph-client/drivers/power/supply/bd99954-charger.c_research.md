<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c

## Purpose

`bd99954-charger.c` is the I2C power-supply driver for the ROHM BD99954 charger. It programs a complete charging profile from firmware and generic battery information, exposes charger and battery-adjacent telemetry through one USB power supply, and handles the BD99954 interrupt hierarchy by acknowledging all active unmasked subinterrupts and refreshing cached charger state.

## Important APIs, Types, And Functions

`struct bd9995x_device` stores the I2C client, regmap, allocated `regmap_field` array from the header, chip ID/revision, parsed initialization data, cached `struct bd9995x_state`, and a mutex. `struct bd9995x_init_data` holds register-selector values for VSYS regulation, input-current limits, trickle/pre/fast charge currents, charge voltages, recharge voltage, overvoltage limit, and termination current.

`bd9995x_power_supply_get_property()` maps cached charge state and live regmap fields to power-supply properties. `bd9995x_get_chip_state()` reads charge-state and input-status fields and derives `online` from VCC or VBUS detection. `bd9995x_fw_probe()` reads `power_supply_battery_info` and ROHM DT properties, converts microvolt/microamp values to register selectors using `linear_range_get_selector_low_array()`, and stores the selectors. `bd9995x_hw_init()` resets the chip, writes a known charging configuration, unmasks interrupt groups, and caches initial state.

## Control Flow

Probe allocates state, initializes a paged 16-bit little-endian regmap with range-window mapping through `MAP_SET`, allocates every regmap field, verifies `BD99954_ID`, reads revision, registers the power supply early so battery-info parsing can use it, parses firmware values, resets and initializes hardware, registers a reset action for cleanup, and requests the active-low threaded IRQ.

The IRQ thread reads `INT0_STATUS` and `F_INT0_SET`, masks `INT0`, acknowledges active unmasked top-level bits, walks active substatus groups `INT1_STATUS` through `INT7_STATUS`, acknowledges active unmasked subbits, restores the top-level mask, refreshes chip state, and calls `power_supply_changed()`.

## State And Persistence

The cached state contains online, charger state, VBAT/VSYS status, and VBUS/VCC status. Hardware is reset at probe and again by devm cleanup, so the driver intentionally overwrites bootloader configuration. Programmed values persist in charger registers while the device remains powered. There are no writable power-supply properties in this driver.

## Dependencies And Integration Points

The C file depends heavily on `bd99954-charger.h` for register addresses, field IDs, field definitions, charge-state constants, interrupt masks, status bits, and manufacturer/IRQ names. Runtime dependencies include I2C, regmap field APIs, linear range helpers, firmware properties, generic power-supply battery info, and OF compatible `rohm,bd99954`.

## Risks And Edge Cases

The driver only supports chip ID `BD99954_ID` although the header defines BD99955/BD99956 IDs. It resets hardware at probe, which can surprise systems expecting firmware-preserved charger state. Missing required ROHM DT properties abort probe. Unsupported battery-info values are rounded down with a warning when possible, which may undercharge or lower current versus the requested profile. `bd9995x_get_prop_batt_current()` reports only positive `IBATP_VAL`, so discharge sign is not represented. IRQ recovery can permanently disable useful notifications if top-level unmask restore fails.

## Test Signals

Tests should verify regmap paging/endian behavior, chip-ID rejection, firmware value-to-selector conversion and rounding, hardware reset completion timeout, initialization field writes, power-supply property units, VCC/VBUS online derivation, battery temperature-to-health mapping, interrupt masking/ack/unmask sequencing, and cleanup reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.c -->
