# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gem.h

`panthor_gem.h` defines Panthor GEM extensions, kernel BO wrappers, debugfs flags, BO label limits, inline vmap helpers, and the GEM/kernel-BO API.

Important types are `struct panthor_gem_debugfs`, `struct panthor_gem_object`, and `struct panthor_kernel_bo`. The header defines `PANTHOR_BO_LABEL_MAXLEN`, imported/exported and kernel/FW-mapped debugfs flags, `to_panthor_bo()`, kernel BO GPU VA/size helpers, `panthor_kernel_bo_vmap()`, `panthor_kernel_bo_vunmap()`, and prototypes for GEM init, object creation, handle creation, labels, sync, PRIME import, kernel BO create/destroy, and debugfs printing.

Control flow is limited to inline vmap/vunmap: map only if `kmap` is absent, store `map.vaddr`, and unmap using an `IOSYS_MAP_INIT_VADDR` wrapper when present. All substantive allocation and sync flow is implemented in `panthor_gem.c`.

State described here persists per BO: shmem object, exclusive VM root GEM, uAPI flags, label pointer under mutex, optional debugfs creator/usage, kernel BO VM, VA node, and CPU mapping. Dependencies are DRM shmem, DRM MM, iosys maps, and Panthor VM declarations. Risks center on exclusive VM ownership, correct vmap lifetime, and mixed const/allocated labels. Tests should build all users, validate firmware/heap kernel BO usage, and inspect debugfs state.
