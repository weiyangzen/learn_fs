# sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c

## Purpose
`pxamci.c` is the PXA2xx/PXA3xx Multimedia Card Interface driver. It handles a quirky controller that requires clock stopping before register access, uses DMA with a single SG segment, supports platform and DT setup, and exposes SDIO IRQ and GPIO/platform read-only/card-detect behavior.

## Important APIs, Types, And Functions
`struct pxamci_host` holds the MMC host, locks, MMIO resource, clock divisor state, command attributes, interrupt mask, power controls, active request pointers, and RX/TX DMA channels. `pxamci_probe()` initializes limits, parses OF/platform data, configures OCR and caps, maps registers, requests IRQ/DMA channels, configures GPIO/platform callbacks, and calls `mmc_add_host()`. Main ops are `pxamci_request()`, `pxamci_set_ios()`, `pxamci_get_ro()`, `pxamci_enable_sdio_irq()`, and `mmc_gpio_get_cd()`. Core helpers include `pxamci_setup_data()`, `pxamci_start_cmd()`, `pxamci_cmd_done()`, `pxamci_data_done()`, `pxamci_irq()`, and `pxamci_dma_irq()`.

## Control Flow
`pxamci_request()` stops the clock, prepares DMA for data, builds `CMDAT`, and starts the command. The IRQ handler masks `MMC_I_REG` against `MMC_I_MASK`, then handles command response and data-transfer completion. `pxamci_cmd_done()` reads the unusual response FIFO layout, maps timeout/CRC errors, enables data completion IRQ, and starts write DMA late on PXA27x erratum #91. `pxamci_data_done()` unmaps DMA, sets transferred bytes or error, then sends stop or completes the request.

## State And Persistence
Runtime state includes `clkrt`, `cmdat`, IRQ mask, power mode, detect delay, active request/data, DMA cookie and length. There is no durable storage; platform callbacks may manipulate external power or GPIO state.

## Dependencies And Integration Points
The driver uses the MMC core, DMAengine, PXA CPU detection helpers, regulator and GPIO frameworks, platform data, OF parsing, clocks, IRQs, and the register constants from `pxamci.h`.

## Risks And Test Signals
Risks include known hardware errata, single-SG DMA limitation, response parsing, clock-stop requirements, DMA error callback reentry, and mixed GPIO/platform power and write-protect definitions. Test signals include PXA25x versus PXA27x/PXA3xx caps, 26 MHz high-speed operation, SDIO IRQ, DMA read/write including write-late erratum path, stop command handling, GPIO CD/WP, and remove-time DMA termination.
