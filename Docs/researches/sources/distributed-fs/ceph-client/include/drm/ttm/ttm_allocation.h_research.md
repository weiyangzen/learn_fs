# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_allocation.h

Purpose: defines allocation policy flags shared by TTM page pools and devices.

Important APIs/types/functions: `TTM_ALLOCATION_POOL_BENEFICIAL_ORDER(n)` stores the maximum high-order allocation useful to the caller in low 8 bits. `TTM_ALLOCATION_POOL_USE_DMA_ALLOC` requests coherent DMA allocations. `TTM_ALLOCATION_POOL_USE_DMA32` requests DMA32-capable pages. `TTM_ALLOCATION_PROPAGATE_ENOSPC` preserves resource-manager `-ENOSPC` instead of converting it to `-ENOMEM`.

Control flow: no functions. TTM pool/device initialization and allocation paths consume these bits to select allocation backend, DMA zone, and error propagation.

State and persistence: flags become persistent policy in `ttm_device` or `ttm_pool` instances for their lifetime.

Dependencies and integration: relies on `BIT()` being available from includers. Used by `ttm_device.h`, `ttm_pool.h`, and BO allocation paths.

Risks and test signals: overlapping low-order values with policy bits or losing `ENOSPC` semantics can change eviction behavior. Test DMA32 allocations, coherent DMA pool use, high-order fallback, and expected errno from exhausted resource managers.
