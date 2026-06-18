# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spisg.c

## Purpose

`spi-amlogic-spisg.c` is a generic SPI controller driver for the Amlogic A4 SPI scatter-gather communication controller. Unlike the SPIFC drivers, it implements normal SPI message transfer using DMA descriptors and supports host or target allocation depending on the `spi-slave` device-tree property.

## Important APIs, types, and functions

- `struct spisg_device` stores controller/device pointers, regmap, clocks, completion, status, cached speed, and cached config register values.
- `struct spisg_descriptor` is the hardware descriptor with start/bus config and TX/RX physical addresses.
- `struct spisg_descriptor_extra` tracks allocated TX/RX scatter-gather link tables for cleanup.
- `aml_spisg_clk_init()` creates a divider clock backed by the controller `CFG_CLK_DIV` field.
- `aml_spisg_setup_transfer()` translates a `spi_transfer` into a descriptor, maps linear or SG buffers, sets lane, op mode, data mode, block size/count, and speed.
- `aml_spisg_transfer_one_message()` allocates descriptor arrays, adds optional CS hold delay descriptor, maps descriptors, starts hardware, waits for IRQ completion, cleans DMA mappings, finalizes the SPI message, and releases the hardware semaphore.
- `aml_spisg_prepare_message()` derives CPOL/CPHA/LSB/3-wire/chipselect settings from the SPI device.
- `aml_spisg_irq()` handles descriptor error and chain-done interrupts.
- Runtime PM callbacks switch clocks and pinctrl state.

## Control flow

Probe chooses host or target controller allocation, maps registers, creates regmap, resets the device, initializes clocks and default config, enables runtime PM, fills SPI controller callbacks and limits, requests the IRQ, registers the controller, and releases the initial runtime PM reference.

Transfer flow starts by acquiring the controller semaphore register. It counts transfers, allocates descriptors plus extra tracking records, configures each transfer, calculates timeout from transfer length and effective speed, optionally appends a null descriptor for CS hold, marks the final descriptor EOC, maps the descriptor list, writes descriptor-list registers, waits for completion, unmaps all resources, updates `actual_length` on success, finalizes the message, and releases the semaphore.

## State and persistence behavior

Cached config state (`cfg_spi`, `cfg_start`, `cfg_bus`) is reused across descriptors and updated per message/transfer. Hardware semaphore state is stored in `SPISG_REG_CFG_READY`. Runtime PM turns `sclk` and `core` clocks on/off and selects pinctrl default/sleep states. DMA descriptor and SG-link allocations are per-message and freed after completion.

## Dependencies and integration points

The driver depends on OF (`amlogic,a4-spisg`), regmap-mmio, reset control, clocks (`core`, `pclk`, generated divider `sclk`), DMA mapping, IRQs, pinctrl PM states, runtime PM, and the SPI core. It advertises quad TX/RX, 3-wire, CPOL/CPHA, LSB-first, DMA capability, and target abort.

## Risks and edge cases

- The source contains duplicated `if (!paddr) {` and `if (ret) {` lines in `aml_spisg_setup_transfer()`/`clk_init()` as read here; this must be resolved in compile-tested code.
- `can_dma()` unconditionally returns true, so DMA mapping paths must handle all transfer buffers correctly.
- `nbits_to_lane[xfer->tx_nbits]` and RX equivalent assume valid nbits indexes within 0..4.
- Descriptor allocation packs `struct spisg_descriptor` and `struct spisg_descriptor_extra` in one allocation with manual pointer arithmetic; size/count changes need care.
- Error paths after partial descriptor setup must clean only mappings that were established; descriptor fields are zeroed to help.
- Timeout is estimated from data length and speed with tolerance, but target mode can wait indefinitely.
- Remove disables `core` and `pclk`, while runtime suspend disables `sclk` and `core`; clock-state symmetry should be tested.

## Test signals

Build with `CONFIG_SPI_AMLOGIC_SPISG`. Runtime tests should cover PIO-sized and large DMA messages, TX-only/RX-only/full-duplex-looking half-duplex transfers, SG and linear buffers, quad lane transfers, CS setup/hold delays, target mode and target abort, runtime suspend/resume, IRQ error bits, descriptor-chain completion, and semaphore-busy handling.
