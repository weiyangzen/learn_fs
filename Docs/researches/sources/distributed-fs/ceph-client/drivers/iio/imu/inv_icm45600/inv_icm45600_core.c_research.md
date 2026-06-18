# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_core.c

Purpose: shared core for ICM45600 devices. It wraps physical 8-bit regmaps with a 16-bit virtual register regmap, validates and resets chips, manages regulators/runtime PM/system sleep, owns common configuration, IRQ handling, temperature ABI, chip-info exports, and creation of accel/gyro child IIO devices.

Important APIs and functions: indirect-register helpers `inv_icm45600_ireg_read/write()` implement banked access with required delays. `inv_icm45600_set_accel_conf()` and `set_gyro_conf()` sanitize keep-values, force power mode based on ODR, write config/filter registers, and update `PWR_MGMT0`. `inv_icm45600_core_probe()` allocates state, enables regulators, reads mount matrix, creates custom regmap, sets up chip/FIFO/children/IRQ/runtime PM, and exports the probe entry. `inv_icm45600_temp_read_raw()` provides shared temp channel behavior.

Control flow: probe requires named `int1`, optional reset, WHOAMI check, default config, timestamp enable, FIFO init, child init, threaded IRQ, then autosuspend setup. IRQ top half timestamps both IIO devices; thread reads INT status, reads/parses FIFO on threshold/full, and warns on full. Suspend disables streaming and stores sensor modes; resume restores modes/FIFO stream; runtime suspend powers all sensors off and disables VDDIO.

State and persistence: `st->conf`, `st->suspended`, `st->timestamp`, `st->fifo`, regulators, and chip info are persistent driver state. Hardware config persists in PWR, config, filter, FIFO, interrupt, and offset registers.

Risks and tests: indirect register access uses shared buffer and precise delays; custom regmap must not recurse incorrectly. Reset differs by I3C path. FIFO stream restoration order matters. Test signals include I2C/SPI/I3C probe, WHOAMI mismatch handling, runtime PM cycles, system suspend with active buffers, temp reads with all sensors off, IRQ FIFO parsing, and debugfs register access.
