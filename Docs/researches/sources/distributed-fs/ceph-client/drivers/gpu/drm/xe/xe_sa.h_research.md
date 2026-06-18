<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h

Purpose: declares SA BO manager APIs and inline address/access helpers.

Important APIs: manager creation via `__xe_sa_bo_manager_init()` and inline `xe_sa_bo_manager_init()` with a 4 KiB guard; allocation/init/free helpers; flush/sync helpers; shadow swap/sync; `to_xe_sa_manager()`, `xe_sa_manager_gpu_addr()`, `xe_sa_bo_gpu_addr()`, `xe_sa_bo_cpu_addr()`, and `xe_sa_bo_swap_guard()`.

Risks and test signals: callers must use the correct CPU flush/sync helpers when `is_iomem` is true and hold the swap guard for shadow operations. Address helpers should be tested against suballocation offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa.h -->
