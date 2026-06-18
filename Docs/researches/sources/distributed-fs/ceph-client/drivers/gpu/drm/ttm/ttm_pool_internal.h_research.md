# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool_internal.h

Purpose: internal inline helpers for interpreting `struct ttm_pool` allocation flags.

Important APIs: `ttm_pool_uses_dma_alloc()` checks `TTM_ALLOCATION_POOL_USE_DMA_ALLOC`, `ttm_pool_uses_dma32()` checks `TTM_ALLOCATION_POOL_USE_DMA32`, and `ttm_pool_beneficial_order()` returns the low byte of `alloc_flags` as the largest order that is considered beneficial for direct reclaim.

Control flow and state: the helpers are pure flag readers. They are used by pool allocation, freeing, initialization, tests, and device pool assertions to select DMA versus global pools, set `GFP_DMA32`, decide when to suppress direct reclaim for high-order allocations, and expose expected pool behavior to KUnit.

Dependencies and integration: includes TTM allocation and pool public headers. It is intentionally private to TTM implementation and tests, avoiding exposure of allocation flag interpretation as public ABI.

Risks and test signals: any change in flag layout, especially the low-byte beneficial-order encoding, must be coordinated with callers in `ttm_pool.c` and tests in `ttm_pool_test.c`/`ttm_device_test.c`. Because the helpers are simple, build and KUnit assertion failures are the primary signals.
