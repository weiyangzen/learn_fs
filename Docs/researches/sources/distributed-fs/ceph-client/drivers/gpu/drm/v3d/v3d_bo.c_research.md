<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c

Purpose: Implements V3D GEM buffer-object creation, lifetime, GPU VA allocation, page-table insertion/removal, PRIME import completion, CPU vmap helpers, and BO-related ioctls.

Important APIs/types/functions: `v3d_create_object()` allocates `struct v3d_bo` and installs object funcs. `v3d_bo_create_finish()` pins shmem pages, allocates a GPU VA range in `v3d->mm` with 4K/64K/1M alignment, updates stats, and inserts PTEs. `v3d_free_object()` unmaps vaddr, removes PTEs, drops stats and DRM MM node, marks pages dirty, and frees shmem. Ioctls cover create, mmap offset, GPU offset, and wait.

Control flow: Userspace create aligns size, creates shmem, finishes GPU mapping, returns GPU offset and GEM handle. PRIME import uses the shmem import helper and then performs the same finish path. Wait ioctl converts nanosecond timeout to jiffies, waits on the GEM reservation object, and decrements timeout for restart semantics.

State and persistence: BO state includes shmem pages/sgt, DRM MM node, optional kernel vaddr, stats counters, and GPU page-table entries. No durable persistence.

Dependencies and integration points: Integrates DRM GEM shmem, DRM MM, dma-buf PRIME, V3D MMU, VMA node mmap offsets, and reservation waiting.

Risks and test signals: Risks include GPU VA leaks on finish failure, PTE/DRM MM mismatch, imported buffer assumptions, timeout semantics, and pages dirty tracking. Tests should cover create/free, PRIME import failure, mmap/get-offset ioctls, wait interrupted/timeout cases, and hugepage alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_bo.c -->
