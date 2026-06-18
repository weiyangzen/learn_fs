# sources/distributed-fs/ceph-client/drivers/iio/adc/ina2xx-adc.c

## Purpose
`ina2xx-adc.c` is an IIO driver for TI INA219/220/226/230/231/236 current, voltage, and power monitors. It exposes raw and scaled shunt voltage, bus voltage, current, and power channels, configurable integration/averaging/gain where supported, a shunt-resistor sysfs setting, and a kthread-backed software buffer.

## Important APIs, types, and functions
- `struct ina2xx_config` describes chip defaults, register LSBs, calibration value, and chip family.
- `struct ina2xx_chip_info` stores regmap, capture thread, configuration state, shunt resistor, timing, gain/range, async-readout flag, lock, and scan buffer.
- `ina2xx_read_raw()` implements raw, scale, oversampling ratio, integration time, sample frequency, and hardware gain.
- `ina2xx_write_raw()` updates averaging, integration time, and INA219 hardware gain/range while rejecting writes when buffers are active.
- `ina2xx_set_calibration()` and `ina2xx_init()` program configuration and calibration registers.
- `ina2xx_capture_thread()` polls conversion-ready flags unless async readout is allowed, reads active channels, timestamps, and pushes buffers.
- `ina2xx_probe()` sets defaults from chip type and DT `shunt-resistor`, initializes regmap, configures the chip, installs kfifo buffer setup, and registers IIO.

## Control flow
Probe selects the chip from OF or I2C ID, initializes regmap with 16-bit registers, stores the shunt resistor, patches the default config with family-specific timing and gain fields, writes config/calibration, selects channel tables and IIO info, sets up a kfifo buffer, and registers the device. Direct reads read a single register and convert according to the requested mask. Buffered operation starts a kernel thread that synchronizes to conversion-ready flags and pushes scans until stopped.

## State and persistence
The device configuration register, calibration register, and power mode are hardware state. Driver state mirrors averaging, integration times, vbus range, shunt gain, shunt resistor, and async-readout mode. On remove the driver unregisters IIO and clears mode bits to power down the device. User changes are not persisted across reboot.

## Dependencies and integration points
The driver depends on I2C, regmap, IIO kfifo buffers, IIO sysfs attributes, OF `shunt-resistor`, kthreads, and register layouts for INA219-compatible and INA226-compatible families.

## Risks
- Buffered capture is software timed and may drop samples if the thread falls behind.
- `allow_async_readout` trades synchronization for fewer status reads; users can get repeated or skipped samples if enabled.
- Configuration writes are blocked while buffers are enabled, but sysfs attributes like shunt resistor are not tied to buffer state.
- Power-down on remove can fail and only warns.
- Scan channel signedness is mostly unsigned even for signed registers; consumers must account for scale/sign semantics.

## Test signals
Use regmap/I2C emulation for raw register decoding, scale math for each family, shunt resistor parsing, integration/gain bounds, buffer enable/disable thread lifetime, conversion-ready polling, async-readout mode, and remove-time powerdown.
