# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_spi.c

## Purpose
`bme680_spi.c` is the SPI transport driver for BME680, adapting the chip's paged 7-bit SPI register address space to regmap and delegating sensor logic to the BME680 core.

## Important APIs, Types, And Functions
`struct bme680_spi_bus_context` stores the SPI device and current memory page. `bme680_regmap_spi_select_page()` changes the page bit in the status register with read-modify-write. `bme680_regmap_spi_write()` and `bme680_regmap_spi_read()` implement regmap bus operations, masking or setting bit 7 for write/read. `bme680_spi_probe()` allocates context, initializes regmap, and calls `bme680_core_probe()`.

## Control Flow
Probe sets `current_page` unknown, builds a custom regmap bus, and enters the shared core. Each regmap transfer selects the correct page for the target register before issuing SPI IO.

## State And Persistence
The only transport state is the cached current page. It is volatile and initialized to invalid on probe to force the first page write.

## Dependencies And Integration Points
It uses SPI, custom regmap bus callbacks, shared BME680 core definitions, runtime PM ops, OF/SPI ID matching, and the `IIO_BME680` namespace.

## Risks
Every page switch requires a status register read-modify-write; failures block subsequent register access. Cached page state can become stale if another agent changes the page bit outside this regmap. The write helper copies exactly two bytes, matching 8-bit register/value regmap assumptions.

## Test Signals
Test register accesses on both page ranges, warm-boot first access, page switch error propagation, SPI ID/OF matching, and regmap multi-byte reads used by the core.
