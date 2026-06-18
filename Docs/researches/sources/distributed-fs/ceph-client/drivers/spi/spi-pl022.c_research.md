# sources/distributed-fs/ceph-client/drivers/spi/spi-pl022.c

## Purpose
`spi-pl022.c` is the AMBA/PrimeCell SPI controller driver for ARM PL022 SSP and related vendor variants. It exposes the PL022 block as a Linux `spi_controller`, supports interrupt, polling, and optional DMA-engine transfers, and adapts register programming for ARM, ST, ST PL023, and LSI variants with different FIFO depths, control register layouts, loopback support, and internal chip-select handling.

## Important APIs, Types, And Functions
- `struct vendor_data` captures per-IP differences: FIFO depth, max bits-per-word, ST extended control registers, PL023 restrictions, loopback, and internal CS control.
- `struct pl022` is controller runtime state: AMBA device, mapped registers, clock, SPI controller, platform data, current transfer/chip, TX/RX cursors, FIFO accounting, DMA channels/tables, dummy DMA page, and current chip select.
- `struct chip_data` is per-SPI-device state stored with `spi_set_ctldata()`: CR0/CR1/DMACR/CPSR register images, bytes-per-word, read/write access width, DMA enablement, and transfer type.
- `pl022_probe()` allocates/registers the SPI controller, maps AMBA resources, enables the clock, initializes hardware defaults, requests IRQ, probes DMA, and enables runtime PM.
- `pl022_setup()` validates per-device controller data or DT properties, computes clock divisors, derives word-size read/write modes, and precomputes register images for later transfer use.
- `pl022_transfer_one()` restores chip state, flushes the FIFO, and dispatches to polling or interrupt/DMA paths.
- `readwriter()` is the core PIO pump, draining RX FIFO and filling TX FIFO while maintaining `exp_fifo_level` to avoid RX FIFO overrun.
- DMA support is built around `pl022_dma_autoprobe()`, `pl022_dma_probe()`, `configure_dma()`, `dma_callback()`, `terminate_dma()`, and `pl022_dma_remove()`.
- PM hooks are `pl022_suspend()`, `pl022_resume()`, `pl022_runtime_suspend()`, and `pl022_runtime_resume()`.

## Control Flow
Probe begins from the AMBA match table, selects a `vendor_data` entry, derives platform data from board data or DT, allocates `spi_controller`, maps registers, gets the SSP clock, writes default register values, installs `pl022_interrupt_handler()`, optionally discovers DMA channels, then registers the controller. Device setup runs lazily per SPI device; it builds a `chip_data` register image based on SPI mode, bits-per-word, max speed, PL022-specific controller data, and vendor layout.

Transfers start in `pl022_transfer_one()`. The driver restores the per-device register image, flushes stale FIFO data, and sets transfer cursors. Polling mode enables SSP and repeatedly calls `readwriter()` until TX/RX are complete or a 1000 ms timeout fires. Interrupt mode enables TX and error interrupts; the IRQ handler handles overrun as fatal, otherwise pumps FIFO via `readwriter()`, disables TX interrupt after TX completion, and finalizes when RX reaches `rx_end`. DMA mode configures RX/TX DMA channels and scatterlists, enables the hardware DMA bits already present in the chip register image, suppresses PL022 data interrupts, and finalizes from the RX DMA callback.

## State And Persistence Behavior
The driver keeps no persistent storage outside kernel runtime state. Hardware configuration is represented as cached register images in `chip_data` and reloaded on every transfer, which limits cross-device register leakage. Transfer state is transient in `struct pl022`: buffer cursors, current chip, FIFO expected level, and DMA mapping state. Runtime PM disables/enables the SSP clock and selects pinctrl idle/default states; system suspend delegates to SPI core suspend and forced runtime PM. DMA scatterlists and the dummy page are allocated at transfer or probe time and freed on completion, error, remove, or DMA termination.

## Dependencies And Integration Points
This driver integrates with AMBA device matching, the SPI core, DT/board `struct pl022_ssp_controller` data, optional DMA engine slave channels named `rx` and `tx`, the common clock framework, runtime/system PM, pinctrl, and GPIO-descriptor chip selects through `host->use_gpio_descriptors`. It imports PL022-specific public definitions from `<linux/amba/pl022.h>`. It registers early via `subsys_initcall()` so SPI devices needed early in boot can bind.

## Risks
- DMA mapping assumes both RX and TX channels are available; partial DMA availability falls back to PIO/interrupt only at setup/probe boundaries.
- `BUG_ON()` is used in DMA helper paths for unexpected scatterlist and bus-width conditions, so invalid internal state can become a kernel panic.
- Polling transfers have a fixed timeout and only diagnose by dumping selected registers.
- Odd transfer lengths with 16/32-bit word widths are rejected, but surplus RX bytes can still be observed and warned about if hardware delivers more than expected.
- The DT controller-data path accepts many PL022-specific properties; invalid combinations are caught by `verify_controller_parameters()`, but board descriptions remain a major compatibility surface.
- Runtime PM relies on balanced probe/remove behavior around `pm_runtime_put()` and `pm_runtime_get_noresume()`.

## Test Signals
- Probe success/failure with each AMBA ID variant and DT/platform-data path.
- SPI loopback and mode 0-3 transfers across 4-16 bit ARM variant and 4-32 bit ST variants.
- DMA and non-DMA transfers, including missing DMA channel fallback and RX overrun handling.
- Polling timeout behavior under stalled hardware.
- Runtime suspend/resume and system suspend/resume with active SPI clients.
- Internal CS register operation on the LSI variant and GPIO descriptor CS operation on other variants.
