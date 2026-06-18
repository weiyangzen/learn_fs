<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c

## Purpose
`gpio-max7301.c` is the SPI bus wrapper for the shared MAX7300/MAX7301 GPIO expander core.

## Important APIs, types, and functions
It defines `max7301_spi_write()` and `max7301_spi_read()` for 16-bit command words, `max7301_probe()`, `max7301_remove()`, and a SPI driver registered at subsys init.

## Control flow
Probe forces `bits_per_word = 16`, calls `spi_setup()`, allocates `struct max7301`, fills read/write callbacks and device pointer, then delegates to `__max730x_probe()`. Reads use a write/read command cycle; writes send one 16-bit word.

## State and persistence behavior
The wrapper stores no GPIO state. Shared core fields and device registers hold pin config, output levels, and power state.

## Dependencies and integration points
It depends on SPI devices named `max7301`, the shared MAX730x core, and early subsys registration after SPI postcore init so GPIO consumers can probe early.

## Risks and edge cases
Changing `bits_per_word` can fail on controllers that do not support 16-bit transfers. Endianness of the 16-bit command word must match SPI controller expectations and chip protocol.

## Test signals
Test SPI setup failure, 16-bit read/write transactions, delegation to shared core, remove power-down, and early availability to dependent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7301.c -->
