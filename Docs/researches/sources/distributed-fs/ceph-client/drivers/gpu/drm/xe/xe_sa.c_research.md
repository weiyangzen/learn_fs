<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c

Purpose: implements suballocated BO managers used for small GPU-visible allocations, with optional shadow BO support and CPU staging for iomem-backed VRAM.

Important APIs and control flow: `__xe_sa_bo_manager_init()` creates a managed pinned GGTT BO, optionally allocates CPU staging memory when the BO mapping is iomem, optionally creates a shadow BO and swap mutex, initializes the DRM suballocator excluding a guard region, and registers managed cleanup. `__xe_sa_bo_new()`, `xe_sa_bo_alloc()`, `xe_sa_bo_init()`, and `xe_sa_bo_free()` wrap DRM suballocation flows. `xe_sa_bo_flush_write()` and `xe_sa_bo_sync_read()` copy between CPU staging and GPU BO for iomem mappings; `xe_sa_bo_swap_shadow()` and `xe_sa_bo_sync_shadow()` manage shadow BO contents.

State and dependencies: `struct xe_sa_manager` stores DRM suballocator base, primary/shadow BOs, swap guard, CPU pointer, and iomem flag. Depends on managed BO creation, GGTT pinning, DRM managed cleanup, `xe_map_memcpy_*`, and DRM suballoc.

Risks and test signals: failures after creating BOs rely on DRM managed cleanup, and iomem staging must be flushed/synced explicitly. Tests should cover oversize allocation returning `-ENOBUFS`, guard-size exclusion, shadow swap under lockdep, iomem versus non-iomem CPU pointers, and fence-delayed free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.c -->
