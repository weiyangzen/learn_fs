# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7924.c

Purpose: I2C regmap IIO direct-mode driver for the TI ADS7924 12-bit four-channel ADC, with firmware channel validation, optional reset GPIO, vref regulator support, and continuous auto-scan operation.

Important APIs/types/functions: `struct ads7924_data` keeps device, regmap, vref regulator, reset GPIO, mutex, and `conv_invalid` stale-sample flag. `ads7924_get_adc_result()` reads two auto-incremented result bytes and handles first-conversion delay. `ads7924_read_raw()` exposes raw and scale. `ads7924_set_conv_mode()`, `ads7924_reset()`, and `ads7924_probe()` perform device setup.

Control flow: probe validates child-node `reg` properties, initializes I2C regmap with writeable-register filtering, enables `vref`, resets by GPIO or reset register, switches through AWAKE into AUTO_SCAN, registers a devm cleanup to return to IDLE, programs minimum acquisition time and zero power-up time, marks the first conversion invalid, and registers IIO. A raw read locks the device, optionally waits one conversion window to avoid stale data, reads the channel result pair, right-shifts the 12-bit sample, and returns it.

State and persistence: configuration is held in mode, acquisition, power, and reset registers; `conv_invalid` is an in-memory guard after mode changes; no persistent storage. Regulator and idle-mode cleanup are device-managed.

Dependencies and integration: I2C regmap, optional reset GPIO, vref regulator, firmware child nodes, and IIO direct mode. Matches `ti,ads7924`.

Risks: the channel validation only checks that at least one valid child node exists while the IIO device still exposes all four static channels; mode transitions require an AWAKE intermediate state; first raw read after auto-scan start deliberately sleeps. Test signals include invalid child-node rejection, reset path coverage, stale-conversion delay, scale from regulator voltage, and regmap access errors.
