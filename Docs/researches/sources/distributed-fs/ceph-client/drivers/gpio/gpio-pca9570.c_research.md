<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c

## Purpose
Simple I2C GPO-only driver for PCA9570, PCA9571, and SLG7XL45106. All lines are fixed outputs, with direct readback and a software latch for read-modify-write updates.

## Important APIs, types, and functions
`struct pca9570_chip_data` stores line count and optional command byte. `struct pca9570` stores chip data, mutex, and cached output byte. `pca9570_read()`/`write()` use SMBus byte or byte-data access. GPIO callbacks are fixed get_direction, get, and set.

## Control flow
Probe fills a sleeping dynamic-base chip from match data, initializes the mutex, reads current output into `out`, and registers. `set()` updates the cached byte under lock, writes it, then commits the cache only on success.

## State and persistence behavior
`out` is the only shadow state. Initial read failure is ignored, leaving zero as the first cache value. No PM hooks exist.

## Dependencies and integration points
Uses I2C/SMBus, OF/I2C match data, gpiolib, and devm-managed locking/registration.

## Risks and edge cases
Initial read failure can make first set overwrite unknown output bits. There is no `direction_output()` callback despite output-only hardware. Only one byte of GPIOs is supported.

## Test signals
Byte versus command-byte access, fixed output direction, single-bit cache preservation, initial read failure behavior, and SMBus error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca9570.c -->
