<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ctxld.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ctxld.c

Purpose: Implements the DCSS context loader, a DMA-backed double-buffered mechanism for batching register writes into display hardware.

Important APIs/types/functions: Public APIs include `dcss_ctxld_init()`, `dcss_ctxld_exit()`, `dcss_ctxld_enable()`, `dcss_ctxld_kick()`, `dcss_ctxld_write()`, `dcss_ctxld_write_irqsafe()`, `dcss_ctxld_is_flushed()`, `dcss_ctxld_resume()`, `dcss_ctxld_suspend()`, and `dcss_ctxld_assert_locked()`. Important internal types are `struct dcss_ctxld_item` and `struct dcss_ctxld`.

Control flow: Init allocates two DB buffers and two SB buffers, maps registers, requests the CTXLD IRQ, and enables completion/error interrupts. Writes append `{value, offset}` entries to the current context under spinlock. `dcss_ctxld_enable()` arms the loader; `dcss_ctxld_kick()` starts it when armed and not busy, first asking DPR and scaler to write deferred system-control entries, programming DMA base/count registers, enabling CTXLD, marking in-use, toggling buffers, and clearing sizes for the next context. IRQ completion clears in-use and may run the DCSS disable callback.

State and persistence behavior: Maintains coherent DMA buffers for DB, high-priority SB, and low-priority SB contexts, double-buffer index, per-context counts, `in_use`, `armed`, IRQ state, and spinlock. Hardware persists queued writes until CTXLD consumes them.

Dependencies: DMA coherent allocation, interrupt handling, spinlocks, jiffies/msleep for suspend wait, DCSS DPR/scaler hooks, and low-level MMIO helpers.

Integration points: DPR, scaler, DTG, SS, and CRTC paths queue register writes through CTXLD. CRTC enable/flush/disable arms the loader, while vblank/DTG kick IRQs trigger flush progress.

Risks: Context buffer overflow is guarded only by `WARN_ON` and drops writes. Lock ordering is critical because `dcss_dpr_write_sysctrl()` is called from the locked kick path and asserts the lock. Suspend timeout can leave hardware mid-update.

Test signals: Context write/kick/IRQ completion, buffer toggle behavior, overflow warning tests, suspend with pending context, display disable callback completion, and CTXLD error interrupt logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ctxld.c -->
