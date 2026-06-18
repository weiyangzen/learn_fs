# sources/distributed-fs/ceph-client/net/xdp/xsk_buff_pool.c

Purpose: implements AF_XDP buffer pools that bind UMEM, fill/completion rings, netdev queues, DMA mappings, free buffer heads, and driver-facing allocation/free helpers.

Important APIs/functions: `xp_create_and_assign_umem()`, `xp_assign_dev()`, `xp_assign_dev_shared()`, `xp_clear_dev()`, `xp_get_pool()`, `xp_put_pool()`, `xp_dma_map()`, `xp_dma_unmap()`, `xp_alloc()`, `xp_alloc_batch()`, `xp_can_alloc()`, `xp_free()`, `xp_raw_get_data()`, `xp_raw_get_dma()`, and `xp_raw_get_ctx()` are the main surfaces, with several exported for drivers.

Control flow: pool creation allocates buffer heads, TX descriptor cache, geometry, ring pointers, locks, and free lists from a UMEM. Device assignment registers the pool at a queue, sets need-wakeup/copy/zerocopy/SG policy, checks MTU and XDP feature support, calls driver `ndo_bpf(XDP_SETUP_XSK_POOL)`, and falls back to copy unless zero-copy was forced. Allocation consumes valid fill-ring addresses or reused heads, initializes XDP buffer pointers/DMA, and returns buffers to drivers; free returns heads to a pool free list. DMA mapping is shared per UMEM/netdev through `xsk_dma_list` and refcounted maps.

State and persistence: pool state includes UMEM reference, rings, netdev/device pointers, queue id, zero-copy capability, DMA pages, TX descriptors, buffer heads/free lists, frame geometry, need-wakeup cache, xsk TX list, and refcount. Cleanup is deferred through workqueue so RTNL/device teardown happens safely.

Dependencies and integration: used by PF_XDP bind, driver zero-copy paths, DMA APIs, netdevice queue registration, XDP buffer helpers, UMEM lifecycle, and queue descriptor validation.

Risks and test signals: high-risk areas are fallback cleanup after failed zero-copy setup, shared DMA-map refcounts, unaligned address validation across non-contiguous pages, fill-ring invalid descriptor accounting, and deferred pool destruction with device unregister. Tests should cover copy and forced zero-copy, SG MTU limits, TX software checksum incompatibility, shared UMEM across devices/queues, DMA map reuse/unmap, fill-ring exhaustion, invalid aligned/unaligned addresses, and driver unload.
