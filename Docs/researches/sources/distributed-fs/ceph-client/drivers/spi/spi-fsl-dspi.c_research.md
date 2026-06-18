# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-dspi.c

## Purpose
Implements the Freescale/NXP DSPI controller driver for multiple SoCs, supporting host and target mode, XSPI FIFO command mode, DMA mode, GPIO/native chip selects, per-device timing setup, optional polling, PM suspend/resume, and S32G-specific behavior.

## Important APIs, Types, And Functions
Core state is `struct fsl_dspi`; per-device timing is `struct chip_data`; DMA state is `struct fsl_dspi_dma`; hardware variants are described by `struct fsl_dspi_devtype_data`. Important functions include data conversion helpers, `dspi_setup_accel()`, `dspi_fifo_write()`, `dspi_rxtx()`, `dspi_interrupt()`, `dspi_dma_xfer()`, `dspi_request_dma()`, `dspi_transfer_one_message()`, `dspi_setup()`, `dspi_init()`, `dspi_target_abort()`, `dspi_probe()`, and `dspi_remove()`.

## Control Flow
Probe selects host or target allocation, reads platform data or OF match data, configures endian-specific PUSHR offsets, initializes regmaps, clocks, MCR/RSER state, IRQ or poll mode, optional DMA, speed limits, and registers the controller. Setup computes CTAR timing from clock rate, requested speed, CS setup/hold delays, mode bits, LSB-first, and optional S32G modified transfer format. Message transfer clears FIFOs/status, builds a PUSHR command including PCS/CONT semantics, then runs either DMA chunks or XSPI FIFO writes. IRQ or polling reads previous FIFO data, checks FIFO errors, writes more data, and completes when all words are transferred.

## State And Persistence
Runtime state includes current message/transfer/chip, TX/RX pointers, remaining length, progress, words in flight, command word, MTF flag, completion, DMA buffers, regmaps, and clock. Per-SPI-device `chip_data` caches CTAR value. Hardware is halted after messages unless `cs_change` keeps CS asserted. No persistent storage is used.

## Dependencies And Integration Points
Depends on platform/OF, regmap, DMAengine, clk, pinctrl PM, GPIO descriptors, SPI core, and `linux/spi/spi-fsl-dspi.h` platform data. Compatible data covers VF610, Layerscape families, LX2160A, ColdFire, and S32G.

## Risks
The driver has many variant paths: XSPI vs DMA, host vs target, IRQ vs polling, big vs little endian, and S32G MTF. FIFO error handling protects TX underflow/RX overflow, but command continuation and GPIO CS semantics are subtle. DMA timeouts and target abort must terminate both channels. Speed/timing calculations clamp through table searches and can silently pick maximum prescalers.

## Test Signals
Variant probe matrix, host/target transfers, DMA timeout/abort, XSPI 8-on-16/8-on-32/16-on-32 acceleration, GPIO and native CS with `cs_change`, polling mode, FIFO errors, suspend/resume reinitialization, and S32G >25 MHz MTF are key tests.
