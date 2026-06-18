# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_core.c

Purpose: common IIO core for Freescale MMA7455L/MMA7456 3-axis accelerometers in 10-bit mode. It provides raw acceleration, fixed 10-bit scale, sample frequency selection, and triggered-buffer reads for I2C and SPI transports.

Important APIs/types/functions: `struct mma7455_data` stores regmap and timestamp-aligned scan buffer. `mma7455_core_regmap` defines 8-bit registers through `MMA7455_REG_TW`. `mma7455_core_probe()` validates WHOAMI, enters measurement mode, sets up triggered buffer, and registers IIO. `mma7455_core_remove()` unregisters and returns to standby. `mma7455_drdy()`, `mma7455_read_raw()`, `mma7455_write_raw()`, and `mma7455_trigger_handler()` implement data access.

Control flow: direct raw reads reject access while the buffer is enabled, poll DRDY up to three times with 20 ms sleeps, bulk-read little-endian 16-bit channel data, sign-extend 10 bits, and return an integer. Triggered reads follow the same DRDY gate then bulk-read X/Y/Z into the scan buffer and push a timestamp. Sample frequency is encoded by `CTL1_DFBW`: reported as 125 or 250 Hz.

State and persistence: no software cache for sample frequency or mode is kept; state is held in device registers and the scan buffer. Probe writes measurement mode, remove writes standby.

Dependencies and integration points: IIO direct/buffer APIs, regmap, trigger consumer support, and bus wrappers via namespace exports.

Risks: `regmap_write()` to measurement mode in probe is not checked, which can allow later registration after a failed mode transition. DRDY polling is short and may fail on slow hardware. Unsupported features include 8-bit mode, interrupts, calibration, and events.

Test signals: WHOAMI mismatch path, 125/250 Hz read-write behavior, raw read blocked during buffer mode, triggered buffer samples in X/Y/Z order, standby on remove, and I2C/SPI transport parity.
