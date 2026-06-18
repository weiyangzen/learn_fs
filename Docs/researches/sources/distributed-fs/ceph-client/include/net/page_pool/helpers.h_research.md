# sources/distributed-fs/ceph-client/include/net/page_pool/helpers.h

Purpose: provides driver-facing inline helpers for page_pool allocation, fragment allocation, netmem allocation, refcounting, recycling, DMA address access, DMA sync, and stats access.

Important APIs and types: wrappers include `page_pool_dev_alloc_pages()`, `page_pool_dev_alloc_frag()`, `page_pool_alloc_netmem()`, `page_pool_dev_alloc_netmem*()`, `page_pool_alloc_va()`, `page_pool_put_page()`, `page_pool_put_full_page()`, `page_pool_recycle_direct()`, `page_pool_free_va()`, `page_pool_get_dma_addr*()`, `page_pool_dma_sync_for_cpu()`, `page_pool_dma_sync_netmem_for_cpu()`, `page_pool_get()/put()`, `page_pool_nid_changed()`, and `page_pool_is_unreadable()`. Fragment helpers manipulate `pp_ref_count` over page/netmem references.

Control flow: RX drivers allocate from the pool on the NAPI hot path, optionally split pages into fragments, attach buffers to skbs/XDP, and return them through put/recycle helpers. Last-reference detection determines whether the pool recycles directly, enqueues to ring, or releases mappings.

State and persistence: updates in-flight fragment refs, pool user refcount, allocation cache, fragment offset, DMA metadata, and optional stats. No durable state.

Dependencies and integration points: depends on `page_pool/types.h`, DMA mapping, netmem, skb recycling, XDP memory, NAPI safe context, and optional page pool stats.

Risks and test signals: risks include wrong `dma_sync_size`, using direct recycling outside safe context, unreadable netmem VA access, negative fragment refs, DMA address packing on 32-bit, and missing last-fragment sync. Test RX recycling, split pages, XDP_DROP direct recycle, DMA sync paths, highmem VA allocation, unreadable memory providers, and CONFIG_PAGE_POOL off builds.
