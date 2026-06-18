# sources/distributed-fs/ceph-client/drivers/spi/spi-imx.c

## Purpose

`spi-imx.c` is the Freescale/NXP i.MX SPI controller driver covering multiple CSPI and ECSPI generations from i.MX1 through i.MX6UL-era variants. It supports host and, where hardware allows, target mode; PIO, polling, interrupt-driven, and SDMA-backed transfers; dynamic burst programming; word delays; GPIO and native chip selects; runtime PM; and SoC-specific register layouts through callback tables.

## Important APIs, Types, and Functions

`struct spi_imx_devtype_data` abstracts SoC generation differences with callbacks for interrupt control, message/transfer preparation, trigger, RX availability, reset, DMA watermark setup, disable, and capability flags. `struct spi_imx_data` stores controller/device resources, clocks, active transfer buffers/counters, target state, DMA completions/package data, FIFO watermarks, and selected devtype data.

The driver contains register programming families for MX51/ECSPI (`mx51_ecspi_*`), MX31/MX35, MX21/MX27, and MX1. Transfer setup is handled by `spi_imx_setupxfer()`, transfer execution by `spi_imx_transfer_one()`, `spi_imx_pio_transfer()`, `spi_imx_poll_transfer()`, `spi_imx_pio_transfer_target()`, and `spi_imx_dma_transfer()`. DMA packaging uses `struct dma_data_package` plus helpers for bounce buffers, endian/order adjustment, burst splitting, DMA mapping, watermark calculation, DMA submission, and RX copyback.

## Control Flow

Probe matches the OF compatible to a devtype table, selects host or target allocation based on `spi-slave`, reads optional SPI-ready control and `num-cs`, sets controller mode bits according to hardware generation, maps MMIO, requests IRQ, obtains and enables clocks, initializes runtime PM, optionally requests SDMA channels, resets the controller, disables interrupts, registers the SPI controller, and autosuspends.

Before each message, runtime PM resumes the device and the devtype `prepare_message()` programs mode, CS selection, loopback, SPI_READY, CPOL/CPHA, CS polarity, and for ECSPI waits for configuration propagation at low SCLK rates. `spi_imx_setupxfer()` resolves speed, bits-per-word, buffer accessors, dynamic burst eligibility, DMA eligibility, RX-only CPHA flip state, and target burst size, then calls the devtype transfer-preparation callback.

Transfer execution flushes RX FIFO, then chooses target PIO, DMA, short-transfer polling, or interrupt PIO. PIO fills TX FIFO, triggers hardware, drains RX in ISR or polling loop, and completes when FIFO counters reach zero. DMA builds one or two packages when ECSPI burst length constraints require splitting, prepares aligned bounce buffers, configures DMA widths/watermarks, submits RX before TX, triggers hardware, waits for completions or target abort, copies valid RX bytes back, and falls back to PIO only when failure happened before start.

## State and Persistence Behavior

Driver state persists for the controller lifetime: devtype callbacks, clocks, mapped registers, DMA channel ownership, runtime PM configuration, default bus clock, and target-mode flags. Per-transfer state includes buffer pointers, counters, dynamic burst state, `usedma`, completions, bounce buffers, and target abort flag. Hardware state is reprogrammed per message and per transfer; runtime suspend disables clocks, while prepare/unprepare message brackets runtime PM usage.

## Dependencies and Integration Points

The driver depends on OF matching, platform MMIO/IRQ, Linux clock and pinctrl APIs, runtime PM, DMAengine and i.MX SDMA bindings, SPI core host/target APIs, GPIO descriptor CS support, and module parameters `use_dma` and `polling_limit_us`. It integrates with many `fsl,*-cspi` and `fsl,*-ecspi` compatibles.

## Risks and Edge Cases

This file carries high complexity around DMA byte ordering, unaligned lengths, dynamic burst, and word delay. DMA bounce-buffer allocation is per transfer and can fall back only before start. `spi_imx_dma_map()` checks `dma_mapping_error()` with `ret < 0`, but that API returns nonzero error status; this deserves static-analysis attention. Target mode has hardware errata requiring maximum 512-byte transfers and disabling ECSPI after completion. Runtime PM must be balanced if devtype preparation fails. Polling mode can fall back to interrupt mode after a timeout threshold.

## Test Signals

Test every supported compatible/devtype, host and target mode, native and GPIO CS, SPI_READY, loopback, CPOL/CPHA/CS-high/CS-word/RX_CPHA_FLIP/MOSI idle, 1 to 32 bits-per-word, dynamic burst aligned and unaligned lengths, word delay, PIO/polling/IRQ/DMA paths, DMA split at 512-byte burst boundaries, DMA map/allocation failure fallback, target abort, runtime PM, suspend/resume pinctrl states, and module parameter combinations.
