<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c

Purpose: implements a per-device memory shrinker that frees purgeable/shrinkable Xe BO backing under kernel memory pressure while respecting reclaim, runtime PM, and TTM constraints.

Important APIs and control flow: `xe_shrinker_create()` allocates/registers a shrinker and stores it in `xe->mem.shrinker`; `xe_shrinker_mod_pages()` updates shrinkable/purgeable accounting under rwlock. `xe_shrinker_count()` reports purgeable pages plus shrinkable pages limited by backup capacity and `__GFP_FS`. `xe_shrinker_scan()` first tries purgeable objects, then backup/writeback paths if allowed, using `xe_shrinker_walk()` to prefer idle/no-writeback shrinking before potentially waiting on GPU or writing back.

State and dependencies: `struct xe_shrinker` stores device pointer, rwlock counters, kernel shrinker pointer, and PM wake worker. Depends on TTM LRU walking, `ttm_backup_bytes_avail()`, `xe_bo_shrink()`, runtime PM helpers, and a workqueue to wake the device outside reclaim when necessary.

Risks and test signals: reclaim context must not deadlock on runtime PM or fs reclaim; tests should cover `__GFP_FS`/`__GFP_IO` combinations, `ttm_bo_shrink_avoid_wait()`, flat-CCS runtime PM wakeups, purge-only behavior, accounting reaching zero before fini, and worker flush on cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.c -->
