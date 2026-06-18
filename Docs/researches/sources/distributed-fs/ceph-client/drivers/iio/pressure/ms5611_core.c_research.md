<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c

## Purpose
`ms5611_core.c` is the shared IIO core for Measurement Specialties MS5611 and MS5607 pressure/temperature sensors. It reads and CRC-validates PROM calibration, applies chip-specific second-order compensation, supports separate pressure and temperature oversampling ratios, and exposes direct and triggered-buffer IIO reads.

## Important APIs, types, and functions
`ms5611_prom_is_valid()` implements the PROM CRC4 check. `ms5611_read_prom()` fills the coefficient array. `ms5611_temp_and_pressure_compensate()` and `ms5607_temp_and_pressure_compensate()` apply each chip's datasheet formula. `ms5611_read_raw()` returns processed pressure/temp, scale, and oversampling ratio. `ms5611_write_raw()` validates and changes OSR under direct-mode claim. `ms5611_trigger_handler()` pushes pressure, temperature, and timestamp. `ms5611_probe()` selects compensation, initializes OSR defaults, reads PROM, installs a triggered buffer, and registers IIO.

## Control flow
The bus wrapper allocates state and callbacks, then calls `ms5611_probe()`. Probe enables optional `vdd`, resets the chip, reads and validates PROM, sets up channels and buffer support, and registers. Runtime read paths lock the state mutex, use the bus callback to perform temperature and pressure ADC conversions at the selected OSRs, compensate, and format values. Buffered reads use the same measurement path from the trigger handler.

## State and persistence behavior
Persistent driver state includes PROM coefficients and current pressure/temp OSR pointers. OSR changes affect later conversions and are blocked while buffers are active by `iio_device_claim_direct()`. The hardware itself is reset during probe but not otherwise configured persistently by the core.

## Dependencies and integration points
The core exports `ms5611_probe()` in namespace `IIO_MS5611` and depends on regulators, IIO sysfs, triggered buffers, bus callbacks, and unaligned/endianness handling in wrappers.

## Risks
PROM CRC validation mutates `prom[7]` by masking the CRC nibble during the check; this mirrors common algorithm usage but is worth preserving intentionally. Compensation uses 64-bit arithmetic and second-order low-temperature corrections; incorrect sign/shift changes produce plausible but wrong data. OSR write path must remain direct-mode protected to avoid changing conversion timing during buffered acquisition.

## Test signals
Use datasheet coefficient/raw vectors for MS5611 and MS5607, corrupt PROM CRC tests, OSR read/write validation for all 256-4096 ratios, buffer scan tests, regulator failure injection, and I2C/SPI parity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c -->
