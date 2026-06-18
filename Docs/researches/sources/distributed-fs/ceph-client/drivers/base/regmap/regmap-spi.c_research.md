<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c

Purpose: Provides the standard SPI regmap transport, including synchronous write/read, gather writes, async writes, and transfer-size limits.

Important APIs/types/functions: `struct regmap_async_spi` embeds regmap async state, `spi_message`, and two transfers. `regmap_spi_write()`, `regmap_spi_gather_write()`, `regmap_spi_async_write()`, `regmap_spi_async_alloc()`, and `regmap_spi_read()` implement callbacks. `regmap_get_spi_bus()` may clone the bus to set max raw sizes. Exported wrappers are `__regmap_init_spi()` and `__devm_regmap_init_spi()`.

Control flow: Simple writes call `spi_write()`. Gather writes build a two-transfer message for register and value buffers and call `spi_sync()`. Async writes populate the preallocated async object, add the register transfer and optional value transfer, set a completion callback that reports `async->m.status`, and call `spi_async()`. Reads use `spi_write_then_read()`. Bus selection clones the static bus when `spi_max_transfer_size()` is finite, adjusts max raw read/write against `spi_max_message_size()` and register reserve size, and marks it `free_on_exit`.

State and persistence behavior: Normal operations are stateless. Async write state persists in per-operation `struct regmap_async_spi` allocated by the callback and owned by regmap core. Cloned bus state persists for the regmap lifetime.

Dependencies and integration points: Depends on SPI core, regmap async interfaces, and regmap default big-endian register/value formatting. `read_flag_mask = 0x80` is advertised for devices using the common SPI read-bit convention.

Risks: Max transfer adjustment can underflow if reserve size exceeds limits, so controller quirks deserve scrutiny. Async buffers must remain valid until SPI completion; this relies on regmap async ownership rules. Devices with nonstandard read flags or endian formats must override config appropriately.

Test signals: Validate synchronous gather messages, async completion status propagation, optional value transfer handling, cloned max raw limits, read flag behavior, and managed/unmanaged init cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c -->
