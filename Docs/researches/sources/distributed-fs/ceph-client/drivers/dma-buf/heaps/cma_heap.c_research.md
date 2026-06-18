# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/cma_heap.c

Purpose: implements a dma-buf heap exporter backed by CMA contiguous memory regions, exposing one heap for the default CMA region and one per named CMA area.

Important APIs/types/functions: defines `struct cma_heap`, `struct cma_heap_buffer`, attachment state, `cma_heap_buf_ops`, and heap op `cma_heap_allocate()`. Init path `add_cma_heaps()` calls `__add_cma_heap()` for default and enumerated CMA regions.

Control flow: allocation page-aligns length, allocates buffer state, chooses CMA alignment up to `CONFIG_CMA_ALIGNMENT`, allocates contiguous pages through `cma_alloc()`, zeroes them, builds a page pointer array, fills dma-buf export info, and calls `dma_buf_export()`. Attach builds an sg table from the page array and stores per-device attachment state. Map/unmap uses `dma_map_sgtable()` and `dma_unmap_sgtable()`. CPU begin/end invalidates/flushes vmap ranges and syncs mapped attachment sg tables. mmap installs PFN fault operations; faults insert PFNs from the page array. vmap/vunmap reference-count a `vmap()` of all pages. Release warns on leaked kernel mappings, frees the page array, releases CMA pages, and frees buffer state.

State and persistence behavior: each buffer owns contiguous CMA pages, page array, attachment list, mutex, vmap address/count, and length until dma-buf release. Each attachment owns a separate sg table and mapped flag. Registered heaps persist after module init.

Dependencies and integration points: depends on CMA APIs, dma-buf/dma-heap framework, DMA mapping APIs, VM fault/mmap APIs, scatterlist helpers, and optional device CMA areas discovered by CMA enumeration.

Risks and test signals: allocation can be expensive and may fail under fragmentation or fatal signals during highmem zeroing. mmap uses PFN insertion with IO/PFNMAP flags, so page fault behavior differs from normal page-backed mmap. `map_dma_buf()` maps the attachment's table in place and tracks a single mapped flag. Test signals include allocation from default/named CMA heaps, zero-filled buffers, DMA map/unmap, mmap page faults over full length with SIGBUS past end, CPU sync over mapped attachments, vmap refcounting, and release returning pages to CMA.
