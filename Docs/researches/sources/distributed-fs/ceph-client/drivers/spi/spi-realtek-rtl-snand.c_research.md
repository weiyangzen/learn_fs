# sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl-snand.c

## Purpose
`spi-realtek-rtl-snand.c` is a SPI memory controller driver for Realtek RTL930x SPI-NAND controllers. It implements `spi_mem` operations using command/address/dummy/data phases, supports dual/quad bus widths, switches between small PIO-style register transfers and DMA for larger data phases, and uses IRQ completion for DMA.

## Important APIs, Types, And Functions
- `struct rtl_snand` stores device, regmap, and DMA completion.
- `rtl_snand_supports_op()` accepts default-supported `spi_mem` ops with one-byte single-lane commands.
- `rtl_snand_xfer_head()` asserts CS and emits command, address, and dummy phases with appropriate bus-width register fields.
- `rtl_snand_xfer()` handles small data phases in up-to-4-byte chunks through read/write command/data registers.
- `rtl_snand_dma_xfer()` maps the data buffer, enables DMA IRQ, chunks DMA lengths, starts DMA direction triggers, waits for completion, and unmaps.
- `rtl_snand_irq()` acknowledges DMA interrupt and completes the wait unless status indicates controller/data read/write busy bits.
- `rtl_snand_exec_op()` chooses DMA for data phases larger than 32 bytes.
- `rtl_snand_probe()` maps registers through regmap, sets 32-bit DMA mask, requests IRQ, configures SPI memory capabilities, and registers the controller.

## Control Flow
Probe allocates a SPI host, initializes MMIO regmap, completion, IRQ, and DMA mask, then registers a two-chip-select controller with `spi_mem` ops and dual/quad mode bits. Execution starts in `rtl_snand_exec_op()`, logs the operation, chooses PIO or DMA, and wraps all operations with explicit CS assert/deassert. The head function sends command/address/dummy phases and waits for controller idle between each. PIO loops over data chunks; DMA maps the full buffer, then runs one or more controller DMA chunks with max read length 2080 bytes and max write length 520 bytes.

## State And Persistence Behavior
Runtime state is limited to regmap and the DMA completion. No per-device state is stored. DMA transfers use a transient DMA mapping and temporarily enable `SNAFCFR_DMA_IE`; it is disabled on exit. CS state is written directly through `SNAFCCR`.

## Dependencies And Integration Points
The driver integrates platform/OF matching for RTL9301/RTL9302/RTL9303 SNAND compatibles, SPI memory, regmap MMIO, DMA mapping, IRQ completions, and the SPI core. It is specialized for SPI-NAND-style memory operations rather than full-duplex SPI messages.

## Risks
- `rtl_snand_irq()` returns `IRQ_NONE` when busy/status bits are set; incorrect status interpretation could lead to DMA timeouts.
- DMA maps `op->data.buf.in` even for output direction through the union field; this works only if the union pointer layout is valid and should be tested carefully.
- DMA chunk sizes are hard-coded and asymmetric for reads/writes.
- PIO copies raw register-endian `u32` values into buffers for partial chunks, so endianness must match hardware expectations.
- DMA timeout is fixed at 20 ms per chunk.

## Test Signals
- PIO operations for command-only, address, dummy, small read, and small write phases.
- DMA reads over 2080 bytes and writes over 520 bytes to exercise chunking.
- Dual/quad address/data bus-width operations.
- IRQ completion, timeout path, and DMA interrupt disable/unmap cleanup.
- Probe on each RTL930x compatible with 32-bit DMA mask.
