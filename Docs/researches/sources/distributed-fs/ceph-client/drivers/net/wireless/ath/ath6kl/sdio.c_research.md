<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c

## Purpose
`sdio.c` is the SDIO HIF backend for ath6kl. It registers the SDIO driver, creates the core object, implements synchronous and asynchronous mailbox I/O, BMI transport, diagnostic window access, interrupt handling, scatter-gather support, power management, and SDIO-specific probe/remove.

## Important APIs, Types, And Functions
`struct ath6kl_sdio` holds the SDIO function, core pointer, request pools, bounce DMA buffer, scatter pool, IRQ state, async write work, and queue locks. The HIF implementation is `ath6kl_sdio_ops`.

Data movement is handled by `ath6kl_sdio_io()`, `ath6kl_sdio_read_write_sync()`, `ath6kl_sdio_write_async()`, and `ath6kl_sdio_write_async_work()`. Scatter support is handled by `ath6kl_sdio_scat_rw()`, `ath6kl_sdio_alloc_prep_scat_req()`, `ath6kl_sdio_enable_scatter()`, `ath6kl_sdio_async_rw_scatter()`, and cleanup/get/add helpers. BMI and diagnostic entry points are `ath6kl_sdio_bmi_read()`, `ath6kl_sdio_bmi_write()`, `ath6kl_sdio_diag_read32()`, and `ath6kl_sdio_diag_write32()`.

Probe/remove and PM entry points are `ath6kl_sdio_probe()`, `ath6kl_sdio_remove()`, `ath6kl_sdio_suspend()`, `ath6kl_sdio_resume()`, and empty MMC PM hooks.

## Control Flow
Probe allocates `ath6kl_sdio`, DMA buffer, request pools, work item, waitqueue, core object, HIF ops, BMI max size, and mailbox info, then configures SDIO and calls `ath6kl_core_init()` with mailbox HTC. SDIO config enables async 4-bit IRQ mode for newer devices and sets mailbox block size. Power-on enables the function, delays for hardware init, and reconfigures SDIO. Power-off disables the function.

Synchronous I/O rounds block transfers to mailbox block size, bounces unaligned or non-DMA-able buffers through `dma_buffer`, claims the SDIO host, performs fixed or incremental CMD53 access, logs/traces, and releases the host. Async writes allocate a bus request and queue work. IRQ handling releases the host before calling the HIF bottom-half handler, then reclaims it and wakes waiters.

BMI write waits for command credits then writes to mailbox. BMI read waits for RX lookahead before reading. Diagnostic access sets window address registers bytewise and then reads/writes `WINDOW_DATA_ADDRESS`.

## State And Persistence
State is volatile: SDIO enable/disable state, free request lists, async queue, scatter pool, IRQ handling flag, DMA bounce buffer, and core attachment. Firmware/module declarations are build metadata only. No disk state is written.

## Dependencies And Integration Points
The file depends on Linux MMC/SDIO APIs, ath6kl HIF/HTC/BMI/core interfaces, target register definitions, cfg80211 suspend/resume, and tracepoints. `init.c` consumes HIF power/BMI/diag/scatter ops through the generic ops table. `htc_mbox.c` uses mailbox addresses and scatter capabilities populated here.

## Risks
Async stop has comments noting work may be requeued and asserts a hard-coded scatter queue depth. Scatter virtual-buffer cleanup frees `virt_dma_buf`, which is the aligned pointer rather than necessarily the original allocation base, a pattern worth auditing. Bounce buffering serializes through one mutex-protected buffer, so long synchronous transfers can block. BMI read timeout behavior is intentionally conservative and may still be fragile on unusual controllers. Suspend fallback changes host PM flags and must preserve wake/cut-power semantics.

## Test Signals
Test signals include SDIO probe/config logs, CMD52 async IRQ enable failures, block-size setup failures, trace_ath6kl_sdio and trace_ath6kl_sdio_scat events, BMI credit/read timeouts, interrupt bottom-half status, scatter setup fallback to virtual scatter, suspend mode selection, and clean remove after active async I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c -->
