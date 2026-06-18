# sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c

## Purpose
`omap.c` is the legacy OMAP MMC host driver for OMAP1/OMAP2-era controllers. It supports multiple logical slots on one controller, slot power and cover switches, PIO or DMA transfers, command abort timers, and platform-data-based board integration.

## Important APIs, Types, And Functions
`struct mmc_omap_host` owns controller state: current request/command/data, clocks, DMA channels, IRQ, MMIO base, slot arbitration, workqueue, timers, and feature flags. `struct mmc_omap_slot` represents each MMC slot and stores its `mmc_host`, power GPIOs, cover GPIO, saved CON register, and queued request. Main functions are `mmc_omap_probe()`, `mmc_omap_new_slot()`, `mmc_omap_request()`, `mmc_omap_set_ios()`, `mmc_omap_prepare_data()`, `mmc_omap_start_command()`, `mmc_omap_irq()`, `mmc_omap_cmd_done()`, `mmc_omap_xfer_done()`, and cover-event helpers including exported `omap_mmc_notify_cover_event()`.

## Control Flow
Requests are serialized by `slot_lock`. If another slot owns the controller, the request is queued on that slot; otherwise `mmc_omap_select_slot()` switches hardware state and starts it. Data setup chooses DMA when all SG lengths are block-aligned and channels/configuration are available; otherwise it initializes an atomic SG iterator for IRQ-driven PIO. IRQ processing drains FIFO signals, handles command/data CRC and timeout errors, detects end-of-command and end-of-data, then coordinates DMA completion (`brs_received` and `dma_done`) before finishing, sending stop, or aborting.

## State And Persistence
State is in memory only. Slot register settings, power mode, selected slot, queued requests, DMA progress flags, cover polling timers, and delayed clock-off state are retained while the driver is bound. There is no persistent state.

## Dependencies And Integration Points
The driver depends on `omap_mmc_platform_data`, board callbacks, GPIO descriptors, clocks, DMAengine, MMC core, workqueues, timers, sysfs attributes, and platform IRQ/resource management.

## Risks And Test Signals
Risks include multi-slot arbitration, request queuing under locks, DMA/PIO race handling, abort work disabling/enabling IRQs, cover polling behavior, and hardware-specific register shift differences. Test signals include one-slot and multi-slot enumeration, PIO fallback, DMA completion ordering, command timeout aborts, cover switch sysfs updates, stop command paths, card removal during transfer, and cleanup of timers/workqueue on remove.
