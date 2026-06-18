# sources/distributed-fs/ceph-client/drivers/spi/spi-s3c64xx.c

## Purpose

`spi-s3c64xx.c` is the Samsung S3C64xx/Exynos/FSD/GS101 SPI controller driver. It supports many SoC variants through port-configuration tables, native or automatic chip select, GPIO descriptors, PIO, IRQ-assisted PIO, DMA, runtime PM, clock/prescaler programming, loopback on capable variants, and per-target feedback delay.

## Important APIs, Types, and Functions

`struct s3c64xx_spi_port_config` describes FIFO masks/depth, TX-done bit, clock divider, quirks, high-speed mode, CMU clocking, optional IO clock, loopback, and 32-bit-only MMIO. `struct s3c64xx_spi_driver_data` stores MMIO/clocks/platform/controller pointers, platform info, spinlock, register bus address, completion, state flags, current mode/bits/speed, DMA channel descriptors, port config, port id, FIFO depth, and FIFO masks.

Core functions include `s3c64xx_flush_fifo()`, DMA callback/preparation, `s3c64xx_spi_set_cs()`, transfer-hardware prepare/unprepare, `s3c64xx_spi_can_dma()`, width-specific FIFO I/O helpers, `s3c64xx_enable_datapath()`, DMA and PIO wait functions, `s3c64xx_spi_config()`, `s3c64xx_spi_prepare_message()`, `s3c64xx_spi_transfer_one()`, target controller-data parsing, setup/cleanup, IRQ handling, hardware init, DT parsing, probe/remove, and PM hooks.

## Control Flow

Probe obtains platform/DT controller info, IRQ, host allocation, SoC port config, port id, FIFO depth/masks, DMA directions, SPI hooks/capabilities, MMIO resource, optional GPIO config, clocks, runtime PM, initial hardware state, spinlock/completion, IRQ, error interrupts, then registers the controller. DMA channels are requested during `prepare_transfer_hardware()` unless the DT lacks `dmas`, in which case polling is used.

Setup parses optional per-target `controller-data` and feedback delay, clamps the requested max speed to what the clock/prescaler can provide, stores controller data, and leaves CS inactive. `transfer_one()` reconfigures hardware if speed or bits-per-word changed, chooses DMA for transfers at least FIFO-sized when channels exist, otherwise slices large polling transfers into `fifo_len - 1` pieces, optionally enables RX FIFO-ready IRQ for larger PIO transfers, asserts CS, enables TX/RX datapaths and DMA or writes FIFO data, waits for DMA completion or PIO FIFO fill, handles errors and DMA termination, flushes FIFO, advances sliced buffers, restores original transfer fields, and returns status.

## State and Persistence Behavior

State is volatile: current speed/mode/bpw cache, busy flags, completions, DMA channels/cookies, feedback-delay controller data, FIFO masks/depth, and clock runtime state. Persistent effects are only on attached SPI devices. Runtime resume reinitializes hardware and re-enables error interrupts.

## Dependencies and Integration Points

The driver integrates with Samsung platform data and OF compatibles, clock framework, runtime PM, DMAengine, interrupts, SPI core, GPIO descriptors, and optional SoC-specific GPIO setup callbacks. The variant table maps many compatibles including S3C6410, S5PV210, Exynos generations, Tesla FSD, and Google GS101.

## Risks and Edge Cases

Transfer slicing mutates `xfer->tx_buf`, `rx_buf`, and `len` and restores them at the end; early returns must preserve restoration. DMA TX completion only means FIFO fill, so TX-only DMA requires an extra TX-done poll. PIO receive loops depend on FIFO-level masks and can misbehave if DT FIFO depth or deprecated masks are wrong. Controller-data is allocated in setup for DT devices and freed in cleanup; repeated setup paths must avoid leaks. Polling mode is selected by absence of `dmas`, so malformed DT can silently change behavior. SoCs with 32-bit-only MMIO need the custom 8/16-bit write helpers.

## Test Signals

Test every major port config, FIFO depths 64/128/256, polling/IRQ-assisted PIO/DMA, TX-only/RX-only/full-duplex, 8/16/32-bit words, loopback-capable variants, auto-CS and manual-CS quirks, feedback delay parsing, DMA timeout and residue logging, speed clamping with CMU and prescaler paths, runtime suspend/resume, and DT without `dmas`.
