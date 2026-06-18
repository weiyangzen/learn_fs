# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_bo.h

Purpose: defines the core TTM buffer object API for GEM-backed graphics memory objects, placement validation, reservation, eviction/shrinking, CPU mappings, VM faults, moves, pinning, and LRU walks.

Important APIs/types/functions: `enum ttm_bo_type`, `struct ttm_buffer_object`, `ttm_bo_kmap_obj`, `ttm_operation_ctx`, LRU walk structures, shrink flags, reserve/unreserve helpers, validation/init/fini, kmap/vmap/mmap/fault/access APIs, memory-space allocation, move helpers, populate/setup export, pin/unpin, eviction/swapout, and guarded LRU cursor iteration.

Control flow: callers initialize a BO with placement and optional SG/reservation, reserve it via dma-resv/ww mutexes, validate or move it to a compatible `ttm_resource`, attach fences on submission, unreserve to return it to LRU, and later fault/map/access/pin/evict/shrink/swap as needed. Inline reserve paths convert interrupted waits to `-ERESTARTSYS` and no-wait reservation to `-EBUSY`.

State and persistence: BO state includes GEM base, bdev, type, resource, TT backing, deletion flag, bulk move, priority, pin count, delayed delete work, and external SG table. Most mutable members require reservation lock; LRU operations require device LRU lock.

Dependencies and integration: depends on DRM GEM, dma-resv/fence, VM, TTM device/resource/placement/TT, kmap iterators, workqueues, and scatter-gather. It is central to TTM-using DRM drivers.

Risks and test signals: locking order, deadlock handling, delayed deletion, fence synchronization, resource transitions, CPU mapping cache policy, and VM fault behavior are high risk. Test multi-BO reservation with deadlock backoff, eviction under pressure, pin/unpin, mmap faults, panic kmap, shrink/backup, SG BOs, and suspend/hibernation swapout.
