<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c

## Purpose
`gpio-max7300.c` is the I2C bus wrapper for the shared MAX7300/MAX7301 GPIO expander core in `gpio-max730x.c`.

## Important APIs, types, and functions
It defines I2C `read` and `write` callbacks using SMBus byte-data operations, `max7300_probe()`, `max7300_remove()`, and a `max7300` I2C driver registered at subsys init.

## Control flow
Probe verifies `I2C_FUNC_SMBUS_BYTE_DATA`, allocates `struct max7301`, fills bus callbacks and device pointer, and delegates to `__max730x_probe()`. Remove delegates to `__max730x_remove()`.

## State and persistence behavior
All GPIO state lives in the shared core's `struct max7301` and device registers. This wrapper only provides bus access and driver lifetime.

## Dependencies and integration points
It depends on I2C SMBus byte-data support and the exported MAX730x core helpers from `linux/spi/max7301.h`/`gpio-max730x.c`.

## Risks and edge cases
Adapters without SMBus byte-data support fail probe. Register semantics are inherited from the core; wrapper bugs would manifest as wrong byte register accesses.

## Test signals
Test adapter functionality rejection, probe delegation, read/write SMBus transactions, remove power-down delegation, and early subsys registration for GPIO consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7300.c -->
