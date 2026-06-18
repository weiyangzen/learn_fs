# sources/distributed-fs/ceph-client/drivers/mmc/host/mxcmmc.c

## Purpose
`mxcmmc.c` is the platform driver for the Freescale i.MX21/i.MX31 and MPC512x SDHC/MMCI block. It registers the `mxc-mmc` MMC host, maps controller registers, handles card detect and SDIO IRQs, and runs either DMA or PIO data transfers for MMC core requests.

## Important APIs, Types, And Functions
The main state carrier is `struct mxcmci_host`, which binds the `mmc_host`, MMIO base, clocks, DMA channel/descriptor, current `mmc_request`/`mmc_command`/`mmc_data`, interrupt mask, watchdog timer, and SoC type. `mxcmci_probe()` allocates and initializes the host, parses DT/platform data, enables clocks, validates the hardware revision, requests DMA and IRQ resources, and calls `mmc_add_host()`. The MMC ops are `mxcmci_request()`, `mxcmci_set_ios()`, `mxcmci_get_ro()`, `mxcmci_enable_sdio_irq()`, and `mxcmci_init_card()`. Transfer helpers include `mxcmci_setup_data()`, `mxcmci_start_cmd()`, `mxcmci_cmd_done()`, `mxcmci_data_done()`, `mxcmci_transfer_data()`, and `mxcmci_watchdog()`.

## Control Flow
Requests enter at `mxcmci_request()`, set `host->req`, optionally prepare data, then write command argument/opcode/control fields. Command completion is reported by `mxcmci_irq()` on `STATUS_END_CMD_RESP`, which reads the response and either finishes command-only requests or schedules PIO data work. DMA reads finish through `mxcmci_dma_callback()`, DMA writes through `STATUS_WRITE_OP_DONE`, and PIO transfers run in `mxcmci_datawork()` outside interrupt context. Data completion may start a stop command or call `mmc_request_done()`.

## State And Persistence
Runtime state is volatile kernel driver state: clocks, `cmdat`, `power_mode`, SDIO enable, DMA fallback state, active request pointers, and a watchdog timer. No durable persistence exists. MPC512x endianness is handled by custom register accessors and buffer swapping.

## Dependencies And Integration Points
The driver integrates with the MMC core, platform driver core, device tree compatibles, legacy `imxmmc_platform_data`, regulators, GPIO slot helpers, DMAengine/imx-dma, clocks, IRQ handling, and PM sleep callbacks.

## Risks And Test Signals
Risk concentrates in mixed DMA/PIO fallback, timeout cleanup, DMA unmap ordering, MPC512x byte swapping, and the i.MX31 SDIO four-bit quirk. Useful signals include boot probe logs, `mmc_add_host()` success, card insertion/removal interrupts, read/write CRC and timeout paths, SDIO IRQ delivery, DMA unavailable fallback, suspend/resume clock restoration, and multi-block SDIO testing on i.MX31.
