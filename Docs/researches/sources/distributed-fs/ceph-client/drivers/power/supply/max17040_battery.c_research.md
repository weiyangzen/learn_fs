# sources/distributed-fs/ceph-client/drivers/power/supply/max17040_battery.c

## Purpose
This I2C/regmap fuel-gauge driver supports MAX17040, MAX17041, MAX17043, MAX17044, MAX17048, MAX17049, MAX17058, MAX17059, and the MAX77836 battery alias. It reports voltage, capacity, alert threshold, status from suppliers, and optional temperature, with either low-SOC/SOC interrupts or periodic polling.

## Important APIs, Types, and Functions
`struct chip_data` captures chip-specific reset command, VCELL conversion factors, alert support, RCOMP width, and SOC alert capability. `struct max17040_chip` stores client, regmap, work, battery supply, chip data, optional temp IIO channel, cached SOC, alert threshold, double-SOC quirk, and RCOMP value. Helpers reset the chip, program low-SOC and SOC alerts, program RCOMP, convert raw VCELL to microvolts, read SOC/version, parse OF data, and handle SOC-change versus low-SOC alerts. `max17040_get_property()` exposes online/present, voltage, capacity, capacity-alert-min, supplier status, and IIO temperature.

## Control Flow
Probe checks SMBus byte support, initializes a big-endian 16-bit regmap with stride 2, chooses chip ID from I2C or OF data, parses optional `maxim,double-soc`, `maxim,alert-low-soc-level`, and `maxim,rcomp`, gets optional `temp` IIO channel, registers the battery, reads version, resets older MAX17040/41 chips, writes RCOMP, configures low-SOC and SOC alerts if IRQ/capability allow, otherwise starts deferrable polling work. Suspend disables SOC alert or cancels polling and enables IRQ wake if allowed; resume reverses that.

## State and Persistence
The driver caches last SOC to suppress unchanged uevents, low-SOC threshold, quirk state, and RCOMP. Hardware alert thresholds, SOC alert enable, RCOMP, and reset state persist in gauge registers. Polling uses `system_power_efficient_wq`.

## Dependencies and Integration Points
It depends on I2C regmap, OF match data/properties, optional IIO temp channel, power-supply supplier lookup for status, optional IRQ wakeup, PM sleep hooks, and Maxim gauge register semantics.

## Risks
`max17040_get_vcell()`, `max17040_get_soc()`, and alert handling ignore regmap read errors and may report derived values from uninitialized locals. `max17040_set_property()` updates `low_soc_alert` even if the hardware write fails. Older chips are reset during probe, which can disturb accumulated model state. The optional temp channel uses `devm_iio_channel_get()` and treats only `-ENODEV` as absent.

## Test Signals
Test all chip-data conversions, double-SOC threshold bounds, RCOMP length parsing, low-SOC and SOC interrupt handling, fallback polling and uevent suppression, supplier status forwarding, optional temp conversion, suspend/resume wake behavior, MAX17040/41 reset path, and regmap error propagation in property reads.
