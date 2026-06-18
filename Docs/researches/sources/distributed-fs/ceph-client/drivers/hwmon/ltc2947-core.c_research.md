# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-core.c

Purpose: common hwmon core for the LTC2947 power and energy monitor, shared by the I2C and SPI bus wrappers. It exposes voltage, current, power, temperature, energy, alarms, thresholds, reset-history controls, labels, setup, runtime PM, and OF matching.

Important APIs/types/functions: `struct ltc2947_data` stores the regmap, device, computed energy LSB, and GPIO output mode. `ltc2947_core_probe()` is exported for bus drivers. `ltc2947_val_read()` and `ltc2947_val_write()` switch device pages and perform 16, 24, or 48 bit big-endian transfers with sign extension. The hwmon callbacks are `ltc2947_read()`, `ltc2947_write()`, `ltc2947_is_visible()`, and `ltc2947_read_labels()`, backed by sensor-specific helpers for `in`, `curr`, `power`, `temp`, and `energy64`.

Control flow: probe allocates state, calls `ltc2947_setup()`, then registers `devm_hwmon_device_register_with_info()`. Setup clears status, initializes safe power thresholds, optionally configures an external clock and energy scale, applies firmware properties for accumulator polarity, deadband, and GPIO direction, then enables continuous conversion. Reads and writes dispatch by hwmon sensor type, convert raw register values to standard hwmon units, and use page 0 for live/history registers and page 1 for thresholds.

State and persistence behavior: driver state is devm-managed and nonpersistent, but it programs persistent device registers for thresholds, accumulation policy, GPIO mode, and continuous/shutdown state. Historical min/max reset writes sentinel raw values. Suspend sets the shutdown bit; resume performs a dummy wake read, waits, validates control register state, and re-enables continuous mode.

Dependencies and integration points: depends on regmap supplied by the transport driver, hwmon core, clock framework, firmware property APIs, bitfield helpers, and runtime PM exports. It exports `ltc2947_core_probe`, `ltc2947_pm_ops`, and `ltc2947_of_match` for `ltc2947-i2c.c` and `ltc2947-spi.c`.

Risks: all register accesses rely on global page selection, so interleaved accesses from future code would need serialization. Conversion constants and clamp ranges must match the datasheet to avoid threshold overflow, especially on 32 bit systems. GPIO input and output firmware properties are mutually exclusive. Alarm reading intentionally uses one multi-byte transaction, and changing it can break latch semantics.

Test signals: useful tests are build coverage for I2C and SPI modules, DT/property validation for accumulator and GPIO modes, hwmon sysfs read/write checks for thresholds and reset history, suspend/resume wake tests, external clock boundary tests, and regmap fault injection for page-switch and bulk-transfer failures.
