# sources/distributed-fs/ceph-client/drivers/mmc/host/via-sdmmc.c

## Purpose
This file implements the `via_sdmmc` PCI MMC host driver for VIA SD/MMC card reader hardware, currently matched by `PCI_VENDOR_ID_VIA` and device id `0x9530`. It exposes the controller through the Linux MMC core with command, data, card-detect, write-protect, power, clock, interrupt, and suspend/resume handling.

## Important APIs, types, and functions
- `struct via_crdr_mmc_host` is the private host state. It stores the active `mmc_request`, command, data phase, MMIO bases for SDC/DDMA/PCI-control register windows, saved PM register images, card-detect and completion work, timeout timer, spinlock, power state, reject flag, and quirks.
- Register mirror structs `struct sdhcreg` and `struct pcictrlreg` support suspend/resume and reset restore.
- `via_sdc_ops` registers `.request`, `.set_ios`, and `.get_ro` with the MMC core.
- `via_sd_probe()` enables the PCI device, requests BAR regions, maps BAR0, derives controller sub-bases, resets/powers the controller, initializes the MMC host, requests the shared IRQ, enables controller interrupts, applies the Lenovo 300 ms power-delay quirk, and calls `mmc_add_host()`.
- `via_sd_remove()` rejects new requests, disables interrupts, aborts active DMA/request state, removes the MMC host, frees IRQ/timer/work, powers off pads, unmaps MMIO, and releases PCI resources.
- `via_sd_suspend()`/`via_sd_resume()` save and restore PCI-control and SDC register state around power/reset sequencing.

## Control flow
MMC requests enter `via_sdc_request()` under `host->lock`. The driver enables the SDC DMA clock, clears pending write-one-to-clear SDC status, stores `host->mrq`, rejects requests if no card or removal is in progress, and otherwise calls `via_sdc_send_command()`. Command setup selects controller response encoding from `mmc_resp_type()`, programs argument/control registers, arms a timeout timer, and calls `via_sdc_preparedata()` when the command has data. Data setup requires a single DMA segment (`mmc->max_segs = 1` and `BUG_ON(count != 1)`), configures DDMA, and writes block length/count and interrupt enable bits.

The IRQ path `via_sdc_isr()` first validates the PCI interrupt-status bit, filters SDC status, handles card-detect interrupts by scheduling `carddet_work`, then dispatches command-status bits to `via_sdc_cmd_isr()` and data-status bits to `via_sdc_data_isr()`. Successful command completion reads response registers in `via_sdc_get_response()`. Successful or failed data completion unmaps DMA, sets `bytes_xfered`, and either sends a stop command or queues `finish_bh_work`. `via_sdc_finish_bh_work()` deletes the timer, clears active pointers, drops the spinlock, and calls `mmc_request_done()`.

## State and persistence
Runtime state is entirely in kernel memory and hardware registers. There is no on-disk persistence. The saved PM register images preserve controller state across suspend/resume. `host->power` tracks selected voltage for reset and resume. `host->reject` prevents new commands during remove. The timer is a per-request watchdog and the work items defer card detection and request completion out of IRQ context.

## Dependencies and integration points
The driver depends on PCI, MMIO accessors, DMA mapping, Linux MMC host APIs, workqueues, timers, IRQs, and PM helpers. Hardware integration is via PCI BAR0 with fixed register-window offsets. MMC integration is through `devm_mmc_alloc_host()`, `mmc_add_host()`, `mmc_detect_change()`, and `mmc_request_done()`.

## Risks and edge cases
- Data DMA only supports one scatter-gather entry; callers rely on `mmc->max_segs = 1`, but unexpected mapping results trigger `BUG_ON()`.
- DMA at 375 kHz is known broken; `via_set_ddma()` silently forces the controller to 8 MHz, which can surprise low-speed initialization paths.
- Timeout, removal, and IRQ completion share `host->cmd`/`host->data`/`host->mrq`; correctness depends on the spinlock and deferred completion ordering.
- `via_reset_pcictrl()` manipulates power/reset outside the lock after saving state, so races are mitigated by caller context but remain sensitive during card removal.
- Response packing is hardware-specific and should be regression-tested for R2 and short responses.

## Test signals
Useful validation signals include PCI probe/remove on matching hardware, card insertion/removal during idle and transfer, single- and multi-block read/write, timeout injection, write-protect reporting, suspend/resume with a card inserted, and DMA mapping behavior when requests exceed one segment. Kernel logs for "forcing card speed to 8MHz", timeout messages, and unexpected interrupts are important diagnostics.
