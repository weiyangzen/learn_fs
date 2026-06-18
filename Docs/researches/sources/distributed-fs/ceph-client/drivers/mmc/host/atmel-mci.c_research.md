# sources/distributed-fs/ceph-client/drivers/mmc/host/atmel-mci.c

## Purpose
`atmel-mci.c` implements the Atmel/AT91 Multimedia Card Interface and High-Speed MCI host driver. It supports up to two logical MMC slots sharing one controller, multiple hardware generations, PIO/PDC/DMA transfer engines, GPIO card-detect/write-protect, SDIO IRQs, debugfs inspection, and runtime power management.

## Important APIs, Types, and Functions
Important state types are `struct atmel_mci` for controller-wide state, `struct atmel_mci_slot` for per-slot MMC state, `struct atmel_mci_caps` for version-derived quirks, `struct atmel_mci_dma` for DMAengine state, and `enum atmel_mci_state` for the bottom-half state machine. Public MMC callbacks are `atmci_request`, `atmci_set_ios`, `atmci_get_ro`, `atmci_get_cd`, and `atmci_enable_sdio_irq` via `atmci_ops`.

Core functions include `atmci_of_init`, `atmci_get_cap`, `atmci_prepare_command`, `atmci_start_request`, `atmci_work_func`, `atmci_interrupt`, `atmci_read_data_pio`, `atmci_write_data_pio`, `atmci_prepare_data`, `atmci_prepare_data_pdc`, `atmci_prepare_data_dma`, `atmci_dma_complete`, `atmci_pdc_complete`, `atmci_request_end`, `atmci_detect_change`, `atmci_init_slot`, `atmci_configure_dma`, `atmci_probe`, and runtime PM callbacks.

## Control Flow and State
Device tree child nodes describe slots. Probe maps registers, enables `mci_clk`, resets the controller, requests the main IRQ, detects controller capabilities from `ATMCI_VERSION`, selects DMA/PDC/PIO function pointers, initializes runtime PM, and creates slot MMC hosts. Each request is queued per slot under `host->lock`; if idle, `atmci_start_request` selects the slot, optionally resets the controller, applies slot bus selection, programs timeouts/block registers, prepares data, sends the command, starts the transfer engine, and enables interrupts.

Interrupts do minimal status capture and event setting. The state machine in `atmci_work_func` consumes `EVENT_CMD_RDY`, `EVENT_XFER_COMPLETE`, `EVENT_NOTBUSY`, and `EVENT_DATA_ERROR` while moving through `STATE_SENDING_CMD`, `STATE_DATA_XFER`, `STATE_WAITING_NOTBUSY`, `STATE_SENDING_STOP`, and `STATE_END_REQUEST`. It performs response decoding, data completion, stop-command sequencing, and queue advancement. PDC mode double-buffers through PDC registers; DMA mode uses a `rxtx` DMAengine channel and waits for NOTBUSY after completion; PIO mode drains/fills RDR/TDR on RXRDY/TXRDY.

## State and Persistence Behavior
Persistent state is in-memory and hardware-register only: queued slots, active request pointers, pending/completed event bitmaps, cached mode/config registers, slot clocks, card-present flags, runtime PM clock state, debugfs views, and an optional coherent bounce buffer for old controllers without read/write proof. No filesystem or durable media state is written. Card-detect timers debounce GPIO IRQs and cancel/complete active or queued requests with `-ENOMEDIUM` when cards disappear.

## Dependencies and Integration Points
The driver integrates with MMC core, OF child slot bindings, GPIO descriptor APIs, regulators, debugfs, DMAengine, Atmel PDC definitions, pinctrl PM states, timers/workqueues, and platform-driver PM. Version capability gates determine high-speed support, odd clock divider support, config/CSTOR registers, PDC availability, DMA handshaking, read/write proof, data-ordering workarounds, reset-after-transfer quirks, and block-size constraints.

## Risks and Test Signals
Risks include races between IRQ status capture and workqueue state transitions, shared-controller multi-slot clock changes, older hardware data ordering and non-word-size errata, DMA/PDC cleanup on timeout/removal, GPIO detect polarity, and runtime PM while debugfs snapshots registers. Test signals should cover probe with one and two slots, PIO/PDC/DMA fallback, small and non-word-aligned transfers, multiblock stop handling, SDIO IRQ routing, card removal during queued and active requests, runtime suspend/resume, debugfs `regs`/`req`, and DMA channel defer/failure paths.
