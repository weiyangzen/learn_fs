# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.c

Purpose: Implements OMAP DMM/TILER support: TILER block reservation, page pin/unpin programming through PAT refill engines, rotated/tiled address calculation, DMM probe/remove/resume, DRA7 register-access workaround, and debugfs map rendering.

Important APIs/functions: Public APIs include `tiler_reserve_2d()`, `tiler_reserve_1d()`, `tiler_release()`, `tiler_pin()`, `tiler_unpin()`, `tiler_ssptr()`, `tiler_tsptr()`, `tiler_stride()`, `tiler_size()`, `tiler_vsize()`, `tiler_align()`, `tiler_get_cpu_cache_flags()`, `dmm_is_available()`, and `tiler_map_show()`. Internal transaction functions allocate 16-byte-aligned descriptors, append PAT areas with page or dummy-page entries, commit through PAT_DESCR, and wait for IRQ completion/status.

Control flow: Probe maps DMM, optionally enables the DRA7 i878 DMA workaround, reads PAT geometry, allocates dummy/refill memory and engines, creates SITA TCM containers, maps formats to containers, requests IRQ, enables PAT interrupts, and fills all LUTs with dummy pages. Reserving a TILER block allocates TCM space and tracks it globally. Pinning builds PAT descriptors for each TCM slice, programming page physical addresses with optional roll; unpin fills with dummy pages. IRQ ack completes engines and releases async ones, though current fill forces synchronous operation.

State and persistence: Global `omap_dmm` owns hardware state, containers, engine pool, allocation list, dummy/refill DMA memory, and platform data. TILER blocks persist until release. Hardware LUTs are reinitialized on resume and probe; no disk persistence exists.

Dependencies/integration: Depends on TCM/SITA allocator, DMA mapping/engine, IRQ/completion APIs, OMAP GEM for tiled scanout and fbdev ywrap, DRM debugfs, OF match data, and DRA7 machine compatibility.

Risks and test signals: Asynchronous fill is force-disabled because error paths can leak engines. Physical addresses are stored in 32-bit PAT data, so 32-bit DMA constraints matter. Error handling in probe funnels through remove. Test DMM availability, 1D/2D allocations, tiled rotation scanout, fbdev ywrap roll, resume LUT refill, DRA7 i878 fallback, IRQ timeout/error paths, and debugfs map output.
