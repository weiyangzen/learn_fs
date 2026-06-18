# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32.c

## Purpose

`spi-stm32.c` is the main STM32 SPI controller driver covering STM32F4, STM32F7, STM32H7, and STM32MP25 variants. It supports host mode and, for H7/MP25-style compatibles, target mode; PIO, interrupt, polling, DMA, and optional RX DMA/MDMA chaining through SRAM; runtime PM; GPIO chip selects; and variant-specific register layouts.

## Important APIs, Types, and Functions

`struct stm32_spi_regspec` describes variant register offsets and bit masks. `struct stm32_spi_cfg` binds variant operations for FIFO sizing, BPW masks, disable/config, BPW/mode/data-idleness/TSIZE setup, FIFO access, DMA start/callbacks, IRQ handlers, divisors, feature flags, and DMA-burst policy. `struct stm32_spi` holds controller state, MMIO/clock/IRQ, FIFO size, feature set, current transfer parameters, DMA channels, optional SRAM pool and MDMA channel.

Core SPI hooks are `stm32_spi_prepare_msg()`, `stm32_spi_transfer_one()`, `stm32_spi_unprepare_msg()`, and `stm32_spi_optimize_message()`. Variant data paths include F4/F7 data-register access, H7 FIFO access, FX and H7 IRQ handlers, H7 polling, and DMA setup/start/callback helpers. Probe selects config from OF match data, allocates host or target controller, maps resources, requests threaded IRQ, enables clock/reset, detects FIFO and feature set, configures the controller, requests DMA channels, optional SRAM/MDMA resources, enables runtime PM, and registers.

## Control Flow

Preparation programs CPOL/CPHA/LSB-first/CS-high/RDY bits and optional inter-data idleness. Each transfer records TX/RX buffers, determines DMA eligibility, sets BPW, baud divisor, communication type, mode registers, optional data idleness, and H7/MP25 TSIZE. Transfer then chooses DMA, short-transfer polling, or IRQ. DMA prepares RX before TX, optionally chains RX DMA into SRAM with MDMA to final memory, enables DMA request bits, starts channels, enables SPI, and completes through DMA callbacks or SPI EOT IRQ depending on mode. IRQ paths service TX/RX FIFO/data-register events, handle overrun/mode fault/suspend, disable hardware, and finalize transfers.

## State and Persistence Behavior

All state is volatile. The driver maintains current transfer state under a spinlock and caches variant/feature information. Runtime suspend disables the clock and selects sleep pinctrl; resume restores default pinctrl and clock. Remove unregisters, disables hardware, disables PM, releases DMA/MDMA channels, frees SRAM buffer, and selects sleep pins.

## Dependencies and Integration Points

The driver integrates deeply with the Linux SPI core, DMAengine, genalloc SRAM pools, pinctrl, reset controls, runtime PM, threaded IRQs, and device tree properties including `spi-slave`, `st,spi-midi-ns`, and `sram`. It exposes standard SPI devices in host mode and target-mode handlers in device mode.

## Risks and Edge Cases

Several callbacks finalize transfers from IRQ, DMA callback, or polling paths, so double-finalization and disable ordering are key risks. DMA fallback from descriptor preparation clears RX DMA request but may leave TX request state dependent on which failure label is taken. `stm32_spi_prepare_rx_dma_mdma_chaining()` uses `GFP_ATOMIC` and temporary SG tables while under spinlock, increasing allocation-failure sensitivity. In probe error cleanup, `gen_pool_free()` is called when `spi->sram_pool` exists, even if allocation failed and `sram_rx_buf` is NULL. The MP25 config omits `.write_tx` and `.read_rx`, yet inherits H7 IRQ/poll transfer functions that call those hooks when PIO is used, which is a strong null-callback risk unless MP25 always uses DMA or the missing assignments are intentional elsewhere.

## Test Signals

Build and boot-test all compatibles. Exercise host and target mode, 4- through 32-bit BPW where supported, CPOL/CPHA/LSB/CS-high/RDY, 3-wire TX/RX, simplex/full-duplex, short polling, IRQ PIO, DMA TX/RX/full-duplex, DMA fallback, MDMA chaining with SRAM, transfer splitting at TSIZE limits, overrun/mode-fault/suspend IRQs, runtime/system PM, probe deferral and partial resource cleanup, and MP25 limited/full feature detection.
