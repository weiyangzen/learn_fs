# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_gem.c

Purpose: implements AMD XDNA GEM buffer objects, including shmem BOs, command/share BOs, device heap/device BOs, imported dma-bufs, user-buffer imports, mmap/HMM notification, explicit cache sync, IOMMU mapping hooks, and BO usage accounting.

Important APIs/functions: `amdxdna_drm_create_bo_ioctl()` dispatches BO creation by type. Share/command BOs use DRM shmem or imported user buffers; device heap BOs create a per-client DRM-MM allocator over device memory; device BOs allocate from that heap. `amdxdna_gem_prime_import()` attaches and maps external dma-bufs. `amdxdna_gem_vmap()`, `amdxdna_gem_uva()`, and `amdxdna_gem_dev_addr()` expose CPU/user/device addresses. mmap paths register HMM interval notifiers and insert pages or delegate imported dma-buf mmap. `amdxdna_drm_sync_bo_ioctl()` flushes CPU caches and optionally syncs debug BOs from device. `amdxdna_drm_get_bo_usage()` aggregates per-client memory accounting.

Control flow: open/close GEM funcs attach BOs to clients and maintain usage; free funcs unregister HMM, unmap IOMMU, unpin, vunmap, and free/import-release storage. Command submission pins argument BOs through this API.

State and persistence: BO state includes type, pinned flag, client, mem addresses, mmap notifier list, DRM-MM nodes, dma-buf attachment, assigned context, and accounting counters. It is all kernel runtime state.

Dependencies: DRM shmem/GEM/dma-buf helpers, HMM/mmu interval notifier, IOMMU helpers, user-buffer helper, cache flush helpers, and AMD XDNA UAPI.

Risks: HMM invalidation and unregister workqueue ordering are subtle; stale user virtual addresses can affect PASID mode. Imported BO mmap drops a GEM reference acquired by DRM mmap. Explicit cache sync bounds are not deeply validated against object size in this file. Device heap lifetime is tied to the client and must outlive device BOs.

Test signals: BO create/get-info/mmap/sync for every type, imported dma-buf paths, PASID vs IOVA addressing, HMM invalidation/unmap, close with live heaps/device BOs, memory accounting queries, and cache-sync offset/size edge cases.
