# sources/distributed-fs/ceph-client/drivers/iio/adc/88pm886-gpadc.c

Purpose: IIO GPADC driver for the Marvell 88PM886 PMIC. It exposes internal voltages, external GPADC resistance channels, ground/mic detection voltages, and internal temperature.

Important APIs/types/functions: `struct pm886_gpadc` stores the GPADC regmap. `pm886_gpadc_channels[]` defines voltage, resistance, and temperature IIO channels with per-channel LSB scaling in `address`. `gpadc_get_raw()` bulk-reads a big-endian 12-bit ADC value. `gpadc_set_bias()`, `gpadc_find_bias_current()`, and `gpadc_get_resistance_ohm()` enable bias currents and calculate resistance. `pm886_gpadc_read_raw()`, runtime PM callbacks, and `pm886_gpadc_probe()` complete the driver.

Control flow: probe obtains the parent PMIC and I2C client, creates a dummy I2C device for the GPADC page, initializes an 8-bit regmap, configures the IIO device, ties its fwnode to the parent, enables runtime PM with autosuspend, and registers the IIO device. Each read resumes the device, dispatches raw/scale/offset/processed handling, and autosuspends. Runtime resume enables the ADC block and all channels; runtime suspend disables the block.

State and persistence behavior: driver state is only the regmap pointer. Hardware state is runtime-managed: enabling the ADC and channels on resume, disabling the ADC block on suspend, and briefly enabling per-GPADC bias for resistance reads.

Dependencies and integration points: depends on the 88PM886 MFD core, I2C dummy page addressing, regmap, runtime PM, IIO direct mode, and PMIC register definitions in `linux/mfd/88pm886.h`.

Risks: resistance reads dynamically choose bias levels and reject voltages outside hard-coded empirical bounds; board differences can affect measurability. `gpadc_get_resistance_ohm()` tries to turn bias off even after failures but ignores that cleanup error. Temperature scale/offset reporting relies on IIO fractional semantics with absolute-zero offset. Runtime PM must be active for all register reads.

Test signals: probe with valid and failing dummy-page/regmap creation, raw voltage reads, processed resistance reads across bias levels, temperature raw/scale/offset reads, runtime suspend/resume register writes, autosuspend behavior, and regmap failure injection for bulk reads and bias programming.
