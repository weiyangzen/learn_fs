# sources/distributed-fs/ceph-client/drivers/spi/spi-mem.c

## Purpose

`spi-mem.c` implements the SPI memory framework used by NOR/NAND/EEPROM-style devices. It validates memory operations, chooses controller-optimized `mem_ops` when available, provides SPI-message fallback execution, direct-map helpers, status polling, operation sizing/frequency helpers, DMA-map helpers, statistics, tracing, and SPI-memory driver registration wrappers.

## Important APIs, Types, And Functions

Exported APIs include `spi_controller_dma_map_mem_op_data()`, `spi_controller_dma_unmap_mem_op_data()`, `spi_mem_default_supports_op()`, `spi_mem_supports_op()`, `spi_mem_exec_op()`, `spi_mem_adjust_op_size()`, `spi_mem_adjust_op_freq()`, `spi_mem_calc_op_duration()`, direct-map create/destroy/read/write devm and non-devm variants, `spi_mem_poll_status()`, and SPI-mem driver register/unregister functions.

Internal validation covers command/address/dummy/data bus widths, DTR constraints, ECC and swap16 capabilities, per-operation frequency support, and stack-buffer rejection for DMA-able data buffers.

## Control Flow, State, And Persistence

`spi_mem_exec_op()` adjusts frequency, validates the op, checks support, and first attempts controller `mem_ops->exec_op()` under queue flush, runtime PM, bus lock, and IO mutex when no GPIO CS blocks optimized access. If unsupported, it allocates a DMA-able command/address/dummy buffer, builds up to four `spi_transfer` entries, runs `spi_sync()`, and verifies actual length.

Direct maps store a `spi_mem_dirmap_desc`; if controller dirmap creation fails but the template op is supported, the descriptor falls back to repeated `spi_mem_exec_op()`. Status polling uses controller `poll_status()` when available, otherwise read-polls an input op. State is allocated descriptor/driver data and per-CPU SPI statistics; no disk persistence exists.

## Dependencies And Integration Points

The file integrates SPI core internals, runtime PM, DMA mapping, tracepoints, `spi_controller_mem_ops`, `spi_mem_driver`, and upper-layer memory drivers. It is central framework code, so many controller drivers in this subset, especially Microchip CoreQSPI, plug into it through `mem_ops`.

## Risks And Test Signals

Risks include accepting unsupported bus-width/DTR combinations, using non-DMA-safe buffers, lock ordering around direct optimized ops, GPIO-CS incompatibility with controller-native mem ops, and fallback message length mistakes. Test with spi-nor/spi-nand operations across single/dual/quad/octal and DTR variants, stack-buffer warnings, direct-map fallback, per-op frequency limits, status polling timeouts, and statistics/tracepoint validation.
