# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.c

Purpose: implements VSP1 display-list allocation, register-write body pools, optional extended commands, list commit, and frame-end lifecycle management. It is the main persistence layer for hardware register programming across both mem-to-mem and DRM pipelines.

Important APIs and functions: body APIs `vsp1_dl_body_pool_create()`, `vsp1_dl_body_get()`, `vsp1_dl_body_put()`, `vsp1_dl_body_write()`; list APIs `vsp1_dl_list_get()`, `vsp1_dl_list_get_body0()`, `vsp1_dl_list_add_body()`, `vsp1_dl_list_add_chain()`, `vsp1_dl_list_commit()`, `vsp1_dl_list_put()`; manager APIs `vsp1_dlm_create()`, `vsp1_dlm_setup()`, `vsp1_dlm_irq_frame_end()`, `vsp1_dlm_reset()`, and `vsp1_dlm_destroy()`.

Control flow: `vsp1_dlm_create()` allocates a manager, DMA body pool, preallocated lists, and extended command pool when supported. Entity configuration writes register entries into list bodies. Commit fills headers for the head and chained lists, then either enqueues directly in single-shot mode or manages queued/pending replacement in continuous mode. The IRQ frame-end handler retires active lists, promotes queued lists, sends pending updates to hardware, and returns completion/writeback/internal flags.

State and persistence: DMA write-combined pools hold display-list bodies and headers. Lists move through free, active, queued, and pending states under `dlm->lock`. Bodies use refcounts because LUT/CLU table bodies can be shared with a list while the caller drops its local reference. Extended pre-command state is pooled and reset on release.

Dependencies and integration: depends on DMA mapping, spinlocks, refcounting, VSP1 register definitions, and bus-master selection from `vsp1_device`. All entity `configure_*` callbacks and pipeline runners rely on this file.

Risks and test signals: risks include header byte-count mistakes, races with hardware `UPDHDR`, pending-list replacement while waiters expect internal completion, body pool exhaustion, and chain release recursion. Test with streaming mem-to-mem, continuous DRM atomic updates, writeback completion, LUT/CLU rapid updates, partitioned pipelines, and lockdep.
