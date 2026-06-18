# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-q.c

## Purpose
Core EHCI queue-head and queue-element-transfer-descriptor engine for control, bulk, and interrupt transfers. It builds qTD chains from URBs, appends them to endpoint QHs using the EHCI dummy-qTD pattern, links/unlinks QHs on async or periodic schedules, processes completions, handles errors and TT buffer cleanup, and works around several controller unlink/writeback quirks.

## Important APIs, types, and functions
Important helpers include `qtd_fill()`, `qh_update()`, `qh_refresh()`, `qtd_copy_status()`, `qh_completions()`, `qh_urb_transaction()`, `qh_make()`, `qh_append_tds()`, `submit_async()`, `intr_submit()` through the scheduler side, `qh_link_async()`, `start_unlink_async()`, `start_iaa_cycle()`, `end_iaa_cycle()`, `end_unlink_async()`, `unlink_empty_async()`, and `scan_async()`. `ehci_clear_tt_buffer_complete()` is exported through `hc_driver`.

## Control flow
URB submission first converts a control/bulk/interrupt URB into one or more qTDs, including setup/status stages, scatterlist fragments, zero-packet termination, data toggles, IOC, and short-read alternate-next behavior. The QH is created per endpoint if needed, initialized for high/full/low speed and TT metadata, and appended by swapping the first new qTD into the previous dummy qTD so hardware never sees a half-built queue. Async QHs are linked after the async head and schedule activation is requested. Completion scanning walks qTDs up to active hardware state, translates tokens into URB status and actual lengths, gives back completed URBs, clears TT buffers for non-stall split errors, and requests QH unlinking when halted, short-read, empty, or dummy-overlay recovery is needed. Async unlinking removes QHs from the hardware list, requests IAA, runs a watchdog for lost IAA, often waits through two cycles, and relinks queued QHs if more work arrived.

## State and persistence behavior
Persistent runtime state includes endpoint `hcpriv` QHs, qTD lists, QH state (`LINKED`, `UNLINK`, `IDLE`, etc.), unlink lists, async activity counts, data toggles in usbcore, TT clearing state, retry counters, and DMA descriptors in EHCI pools. Hardware state is the async schedule and QH overlays modified by the controller.

## Dependencies and integration points
Depends on EHCI descriptor definitions in `ehci.h`, USB core URB/endpoint APIs, DMA pools, TT clear-buffer requests, hrtimer events from `ehci-timer.c`, interrupt scheduling hooks from `ehci-sched.c`, and root-hub state from the common EHCI core.

## Risks and edge cases
The dummy-qTD swap and memory barriers are critical for avoiding hardware races. Short reads, halted QHs, active unlinks, and controller writeback after IAA are all subtle. Full/low-speed TT buffer cleanup intentionally skips STALLs because some hubs misbehave. Async unlink logic contains controller-specific two-cycle and active-stability delays; simplifying it can corrupt memory on affected hardware.

## Test signals
Control transfers with setup/data/status, bulk scatter-gather, `URB_ZERO_PACKET`, short reads with and without `URB_SHORT_NOT_OK`, stalls, babble, DBE, MMF, XactErr retries, unlink/dequeue during giveback, TT clear-buffer completion, lost IAA watchdog, dummy-QH quirk devices, and high concurrency on async queues are key tests.
