# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_irq.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_irq.c

### Purpose
`sdio_irq.c` implements SDIO interrupt registration, dispatch, polling/threaded IRQ handling, workqueue signaling, and host IRQ enable/disable integration for SDIO function drivers.

### Important APIs, Types, And Functions
Exports are `sdio_signal_irq()`, `sdio_claim_irq()`, and `sdio_release_irq()`. Internal functions include `sdio_get_pending_irqs()`, `process_sdio_pending_irqs()`, `sdio_run_irqs()`, `sdio_irq_work()`, `sdio_irq_thread()`, `sdio_card_irq_get()`, `sdio_card_irq_put()`, and `sdio_single_irq_set()`.

### Control Flow
Claiming an IRQ reads `IENx`, enables the function bit plus master enable, records the handler, starts a kthread or enables host IRQs depending on host capabilities, and updates the single-IRQ fast path. The IRQ thread claims the host, processes pending interrupts, releases the host, backs off on errors, adapts polling frequency for non-SDIO-IRQ hosts, and enables host SDIO IRQs while sleeping. Workqueue mode handles `MMC_CAP2_SDIO_IRQ_NOTHREAD` by scheduling `sdio_irq_work()`. Dispatch skips suspended cards, optionally calls a single registered handler directly when an IRQ was signaled, otherwise reads `INTx` and invokes handlers for pending function bits. Release clears the handler, decrements host IRQ use, disables function/master bits when appropriate, and stops thread/host IRQs on the last user.

### State, Persistence, And Dependencies
State is in `host->sdio_irqs`, `host->sdio_irq_thread`, `host->sdio_irq_pending`, `host->sdio_irq_thread_abort`, `card->sdio_single_irq`, and each `func->irq_handler`. Hardware-visible state is in CCCR `IENx` and `INTx`, plus host controller SDIO IRQ enable/ack callbacks. Dependencies include kthreads, wait/scheduler APIs, CMD52 helpers, host/card quirks, and MMC host claim/release.

### Integration Points
Function drivers call this API while the host is claimed. `sdio_bus_remove()` warns and releases leaked handlers. `sdio.c` restarts IRQ processing after resume. Host drivers can either provide native SDIO IRQ signaling or rely on polling.

### Risks
Handlers run with the host already claimed and must not call `sdio_claim_host()` recursively. Single-IRQ fast path assumes a signaled IRQ maps to the only registered handler without reading `INTx`. Polling broken cards may need dummy reads to avoid fake interrupts. Suspend blocks processing and cancels work, but race windows around resume and pending flags must be tested. Last-user release must stop the kthread and disable host IRQs without leaving master enable set.

### Test Signals
Test native SDIO IRQ, no-native polling, NOTHREAD workqueue mode, one-function fast path, multiple function handlers, pending bit with missing handler/function, claim busy, release last handler, card suspend/resume with pending IRQs, and driver removal with leaked IRQ handler.
