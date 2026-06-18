# Research: sources/distributed-fs/ceph-client/drivers/usb/core/buffer.c

Purpose: provides DMA-coherent buffer allocation helpers for host controller drivers and usbfs mmap. It creates small DMA pools per HCD and routes allocations through local memory pools, DMA pools, coherent DMA allocation, or ordinary pages/kmalloc for PIO-only controllers.

Important APIs: `usb_init_pool_max` adjusts pool sizes for `ARCH_DMA_MINALIGN`. `hcd_buffer_create` and `hcd_buffer_destroy` manage per-HCD DMA pools. `hcd_buffer_alloc`/`hcd_buffer_free` allocate/free arbitrary transfer buffers. `hcd_buffer_alloc_pages`/`hcd_buffer_free_pages` allocate page-sized coherent regions for mmap-capable usbfs buffers.

Control flow: pool creation skips if local memory pool exists or HCD does not use DMA. Allocation first handles zero size, then local memory pool, then PIO-only fallback, then the smallest configured DMA pool that can hold the size, and finally `dma_alloc_coherent`. Free mirrors the same decision tree based on HCD state and size.

State and persistence: per-HCD DMA pools live in `hcd->pool[]`; optional local memory pool is external in `hcd->localmem_pool`. No persistent state. `pool_max[]` is initialized at boot and adjusted for architecture alignment.

Dependencies and integration points: depends on DMA mapping, DMA pools, genalloc local memory pools, HCD helpers, USB bus/HCD conversion, and memory allocation APIs. Used by HCD core and by `devio.c` for mmap'd usbfs transfer buffers.

Risks: size passed to free must match the allocation path; otherwise the wrong pool may be used. Alignment must satisfy architecture DMA requirements. Localmem allocations require correct DMA address handling. PIO fallback uses sentinel DMA values, which callers must treat appropriately.

Test signals: HCD init/destroy with DMA and PIO controllers, allocations at 0, pool thresholds, above-pool sizes, page allocations, localmem pool path, allocation failure unwind, and DMA debug checks.
