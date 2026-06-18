# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem.c

## Purpose
Implements etnaviv GEM buffer object allocation, page pinning, scatter-gather mapping, mmap/fault handling, CPU synchronization, IOMMU VRAM mapping references, debugfs object reporting, object release, and userptr support.

## Important APIs, Types, and Functions
Key functions include `etnaviv_gem_get_pages`, `etnaviv_gem_mmap_offset`, `etnaviv_gem_mapping_get/unreference`, `etnaviv_gem_vmap`, `etnaviv_gem_cpu_prep/fini`, `etnaviv_gem_wait_bo`, `etnaviv_gem_free_object`, `etnaviv_gem_obj_add`, `etnaviv_gem_new_handle`, `etnaviv_gem_new_private`, and `etnaviv_gem_new_userptr`. Important ops tables are shmem and userptr `etnaviv_gem_ops`, VM ops, and DRM GEM object funcs.

## Control Flow
Shmem objects are allocated, initialized with DRM GEM, assigned cache flags, added to the driver GEM list, and exposed as handles. Pages and sg tables are allocated lazily under object lock; cached buffers use DMA map/sync for CPU/device coherency. mmap either sets PFNMAP protections for WC/uncached or redirects cached mappings to shmem. Faults pin/get pages and insert PFNs. IOMMU mapping lookup reuses active or reaped mappings, maps pages when needed, increments use counts, and takes object refs. CPU prep waits or tests reservation fences, then syncs caches; fini syncs back to device. Free removes GEM list entries, unmaps all VRAM mappings, releases ops-specific resources, and destroys the GEM object.

## State and Persistence
Each object tracks flags, visible GPU size, pages, sg table, vmap address, GPU-active count, VRAM mapping list, last CPU prep op, and optional userptr metadata. The driver private GEM list persists objects for debugfs until object release.

## Dependencies and Integration Points
Depends on DRM GEM/shmem/PRIME helpers, dma-resv fences, DMA mapping APIs, VM fault APIs, etnaviv IOMMU, GPU wait helpers, and UAPI flags. Userptr uses long-term GUP and current mm ownership checks.

## Risks
Coherency is delicate: DMA API warnings note possible corruption with concurrent CPU/device access. Mapping reuse races require object and MMU locks in the documented order. Userptr pins are restricted to the creating mm. `last_cpu_prep_op` misuse warns on fini without prep. Object free requires inactive GPU state.

## Test Signals
GEM create/mmap/fault tests for cached/WC/uncached, CPU prep/fini coherency tests, userptr permission and lifetime tests, IOMMU mapping stress with reuse/reap, PRIME interactions, dma-resv wait timeouts, and debugfs object accounting.
