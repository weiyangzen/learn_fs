# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_shrinker.c

## Purpose
Implements memory-pressure reclaim for MSM DRM GEM buffers. It registers a Linux shrinker for GEM object pages and a vmap purge notifier for kernel virtual mappings, using the driver's GEM LRU buckets to reclaim buffers in increasing order of cost and disruption.

## Important APIs, Types, and Functions
- `msm_gem_shrinker_init()` allocates/registers `priv->shrinker` and registers `priv->vmap_notifier`.
- `msm_gem_shrinker_cleanup()` unregisters the vmap notifier and frees the shrinker.
- `msm_gem_shrinker_count()` reports reclaimable objects from `priv->lru.dontneed` and, when swap is available and eviction enabled, `priv->lru.willneed`.
- `msm_gem_shrinker_scan()` runs four reclaim stages: purge idle dontneed, evict idle willneed, wait/purge active dontneed when blocking is allowed, and wait/evict active willneed when swap and blocking are allowed.
- `with_vm_locks()` locks all GPUVM reservation objects associated with a GEM object before calling `msm_gem_purge()` or `msm_gem_evict()`.
- `msm_gem_shrinker_vmap()` responds to global vmap pressure by unmapping up to `vmap_shrink_limit` mappings across dontneed, willneed, and pinned LRUs.

## Control Flow
The count path is cheap and only reads LRU counts. The scan path builds a local reclaim-stage array, then calls `drm_gem_lru_scan()` for each enabled stage while decrementing `nr_to_scan`. Each object candidate is filtered for purgeability/evictability and current GPU activity. Active stages call `dma_resv_wait_timeout()` briefly before retrying purge/evict. Successful reclaim emits `trace_msm_gem_shrink()`. Vmap purge follows a separate notifier path and scans LRUs for `is_vunmapable()` objects, then calls `msm_gem_vunmap()`.

## State and Persistence
Persistent state lives in `msm_drm_private`: GEM LRU lists, shrinker pointer, and vmap notifier. The module parameter `enable_eviction` gates swappable buffer eviction. No on-disk state exists. The shrinker mutates GEM residency state by purging pages or evicting to swap, and the vmap notifier mutates CPU virtual mapping state.

## Dependencies and Integration Points
Depends on DRM GEM LRU helpers, dma-resv/ww locking, MSM GEM object helpers, Linux shrinker infrastructure, vmap purge notifier infrastructure, and tracepoints from `msm_gpu_trace.h`. It interacts with VM_BIND mappings by locking all GPUVM reservation objects associated with an object before page-table-affecting purge/evict work.

## Risks
Reclaim runs under memory pressure, so deadlock avoidance is central. The code avoids holding `priv->lru.lock` across page acquisition paths, does not do slow ww backoff inside `with_vm_locks()`, and skips candidates it cannot lock. Risks include incomplete reclaim under contention, excessive waiting in blocking reclaim, and correctness bugs if GEM/GPUVM reservation relationships change. Eviction depends on swap availability and `enable_eviction`.

## Test Signals
Useful signals include shrinker invocation under memory pressure, `trace_msm_gem_shrink`, `trace_msm_gem_purge_vmaps`, debugfs `msm_gem_shrinker_shrink()` under `CONFIG_DEBUG_FS`, no lockdep warnings during reclaim, and successful GPU operation after reclaiming idle and active buffers.
