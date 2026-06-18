# sources/distributed-fs/ceph-client/drivers/iio/adc/axp288_adc.c

## Purpose
This is the X-Powers AXP288 PMIC ADC driver used on Intel-era tablet platforms. It exposes six direct-mode IIO channels: TS pin temperature, PMIC temperature, GPADC/system temperature, battery charge current, battery discharge current, and battery voltage. It also registers IIO maps for AXP288 battery, charger, PMIC, and GPADC consumer drivers.

## Important APIs, Types, And Functions
`struct axp288_adc_info` stores the parent regmap, IRQ number, a mutex for serialized device access, and whether the TS pin is enabled. `axp288_adc_read_channel()` bulk-reads two PMIC bytes and assembles a 12-bit value. `axp288_adc_set_ts()` temporarily changes the TS current-source mode when reading the GPADC. `axp288_adc_initialize()` applies DMI quirks, detects TS enable state, sets TS current-source mode, and enables all non-TS ADC channels. `axp288_adc_read_raw()` is the IIO callback.

## Control Flow
Probe allocates an IIO device, gets the platform IRQ, obtains the parent AXP20x regmap, initializes ADC hardware, binds channels and IIO info, registers consumer maps, initializes the mutex, and registers the device with devm cleanup. Raw reads lock the mutex, switch TS current source to on-demand for GPADC reads when the TS pin is enabled, read the selected register pair, then restore the current source to always-on for TS before unlocking.

## State And Persistence
The driver intentionally leaves ADCs enabled across system suspend because disabling them can affect internal fuel-gauge behavior. State is limited to `ts_enabled` and the mutex. Firmware/DMI state matters: DMI overrides may modify TS bias current on known machines with broken firmware. The driver does not implement remove-time ADC disable because devm registration and the platform PMIC behavior assume always-on ADC support while bound.

## Dependencies And Integration Points
It depends on the AXP20x MFD regmap/register definitions, DMI matching, IIO core, IIO machine maps, and platform IDs. Consumer maps target `axp288-batt`, `axp288-pmic`, `axp288-gpadc`, and `axp288-chrg`.

## Risks And Test Signals
Risks include upsetting charger/fuel-gauge behavior by mishandling the TS current source, incomplete DMI quirk coverage, ignoring errors when restoring TS current-source mode after reads, and lack of scale/offset conversions. Test signals include successful DMI bias override on listed systems, GPADC nonzero readings when TS is enabled, TS current-source restore after failed and successful reads, all consumer maps present, and raw channel values assembled from the high nibble layout.
