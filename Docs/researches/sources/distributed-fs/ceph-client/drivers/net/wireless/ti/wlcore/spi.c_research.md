# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/spi.c

## Purpose
`spi.c` is the SPI/WSPI bus glue for wlcore devices. It implements raw command/data transfers, WSPI reset/init sequencing, regulator-based power control, OF family selection, and child platform-device creation for the common wlcore driver.

## Important APIs, Types, and Functions
`struct wl12xx_spi_glue` stores the SPI device, child platform device, and `vwlan` regulator. `spi_ops` provides `read`, `write`, `reset`, `init`, `power`, and a no-op `set_block_size`. `wl12xx_spi_reset()` clocks an all-ones reset sequence. `wl12xx_spi_init()` sends the WSPI init command with CRC7 and extra inverted-chip-select clocks. `wl12xx_spi_raw_read()` and `__wl12xx_spi_raw_write()` build WSPI command words and split transfers into chunks of at most 4092 bytes. `wl12xx_spi_read_busy()` polls busy words until data is ready. `wl12xx_spi_set_power()` toggles the `vwlan` regulator. `wlcore_probe_of()` reads compatible family and clock properties.

## Control Flow
Probe allocates platform data and glue, sets `bits_per_word = 32`, acquires the regulator, parses OF metadata, calls `spi_setup()`, allocates a child platform device named for the family, attaches the SPI IRQ as an IRQ resource, copies platform data, and registers the child. The common wlcore platform probe then uses `spi_ops` for device access. Remove unregisters the child.

## State and Persistence Behavior
The SPI glue keeps only devm-managed pointers and regulator state. Transfer scratch buffers are mostly in `struct wl1271` (`buffer_cmd`, `buffer_busyword`) except dynamically allocated write transfer arrays. No persistent on-disk state exists.

## Dependencies and Integration Points
Dependencies include Linux SPI, regulator, OF matching, platform devices, CRC7, byte swapping, IRQ trigger helpers, and wlcore headers. It integrates with main wlcore via `struct wl1271_if_operations` and with device tree compatibles for wl127x/wl128x/wl18xx.

## Risks and Test Signals
Risks include WSPI command bitfield/endianness errors, busy-word timeout handling, chunking over `SPI_AGGR_BUFFER_SIZE`, ignoring `spi_sync()` return codes in several paths, regulator failures, and ELP wakeup write latency requiring a duplicate write. Test signals include WSPI init/reset success, large read/write chunking, busy timeout behavior, regulator enable/disable, firmware boot over SPI, IRQ delivery, and OF compatible/clock parsing.
