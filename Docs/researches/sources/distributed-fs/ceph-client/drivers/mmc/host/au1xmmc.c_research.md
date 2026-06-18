# sources/distributed-fs/ceph-client/drivers/mmc/host/au1xmmc.c

## Purpose
`au1xmmc.c` is the MMC/SD/SDIO host driver for Alchemy Au1xxx SoCs. It supports platform-data based card power, detect, read-only callbacks, optional DBDMA on supported CPUs, PIO fallback, shared IRQ handling, basic suspend/resume, and optional LED trigger registration.

## Important APIs, Types, and Functions
`struct au1xmmc_host` tracks the `mmc_host`, active request, MMIO base, clock/bus/power state, status enum-like values, DMA and PIO cursors, DBDMA channel IDs, work items, platform data, IRQ, resource, and clock. MMC callbacks are `au1xmmc_request`, `au1xmmc_set_ios`, `au1xmmc_card_readonly`, `au1xmmc_card_inserted`, and `au1xmmc_enable_sdio_irq`. Important helpers include `au1xmmc_send_command`, `au1xmmc_prepare_data`, `au1xmmc_cmd_complete`, `au1xmmc_data_complete`, PIO send/receive helpers, `au1xmmc_irq`, DBDMA init/shutdown/callback, and probe/remove/PM functions.

## Control Flow and State
Probe allocates a devm MMC host but manually requests/remaps MMIO, requests the IRQ, gets/enables the Alchemy peripheral clock, configures caps based on CPU type, sets up card-detect platform hooks, initializes work items, optionally allocates DBDMA channels, resets the controller, and calls `mmc_add_host`. A request starts only from `HOST_S_IDLE`, rejects absent cards, flushes FIFO for data, maps SG data, sets DBDMA descriptors or enables PIO FIFO interrupts, then writes command argument and command bits. The IRQ handles SDIO, timeouts, command complete, PIO FIFO readiness, and schedules bottom-half work for completion.

## State and Persistence Behavior
The host keeps volatile status flags such as `HOST_F_XMIT`, `HOST_F_RECV`, `HOST_F_DMA`, `HOST_F_DBDMA`, `HOST_F_STOP`, and controller states `HOST_S_IDLE/CMD/DATA/STOP`. DMA mappings are released in `au1xmmc_data_complete`; PIO cursors are reset in `au1xmmc_finish_request`. No durable persistence exists. Hardware state is reset by programming enable/status/config/timeout registers and by flushing FIFOs around requests and resume.

## Dependencies and Integration Points
This driver depends on MIPS Alchemy headers, platform data from `au1100_mmc.h`, DBDMA APIs, Linux MMC core, clock APIs, workqueues, IRQs, scatterlist DMA mapping, highmem page mapping for PIO, and optional LED class support. It registers as platform driver `au1xxx-mmc` and uses CPU model detection to set max segment size, f_max, 8-bit support, IRQ sharing, and DBDMA availability.

## Risks and Test Signals
Risks include busy-wait command submission without an explicit timeout, hand-coded DBDMA descriptor setup, platform-data card detect returning `-ENOSYS`, shared IRQ behavior, timeout/error cleanup in PIO with interrupts still enabled, and manual resource cleanup despite partial devm use. Test signals include PIO and DBDMA reads/writes, command response decoding including 136-bit shifts, card absence, SDIO IRQ enable, platform power hooks, Au1100/Au1200/Au1300 CPU capability differences, suspend/resume reset, and probe failure unwind with IRQ/MMIO/clock resources.
