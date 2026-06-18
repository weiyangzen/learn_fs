# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.c

## Purpose
Implements MSM GEM buffer object lifetime, page backing, CPU mmap/vmap, IOVA/VMA management, LRU and shrinker-facing state, madvise/purge/evict behavior, dumb buffers, imported buffers, kernel BO helpers, and debug descriptions.

## Important APIs, types, and functions
- Object lifecycle: `msm_gem_new()`, `msm_gem_new_handle()`, `msm_gem_import()`, `msm_gem_free_object()`.
- Backing/page APIs: `msm_gem_get_pages_locked()`, `msm_gem_pin_pages_locked()`, `msm_gem_unpin_pages_locked()`, `put_pages()`.
- VM/IOVA APIs: `msm_gem_get_iova()`, `msm_gem_set_iova()`, `msm_gem_get_and_pin_iova*()`, `msm_gem_unpin_iova()`, `msm_gem_pin_vma_locked()`.
- CPU APIs: `msm_gem_get_vaddr*()`, `msm_gem_put_vaddr*()`, `msm_gem_cpu_prep()`, `msm_gem_cpu_fini()`, mmap fault ops.
- Memory pressure/debug APIs: `msm_gem_madvise()`, `msm_gem_purge()`, `msm_gem_evict()`, `msm_gem_vunmap()`, `msm_gem_describe*()`.

## Control flow
Objects start unbacked in the unbacked LRU. Page allocation locks the object, gets shmem pages, updates memory accounting tracepoints, creates an SG table, performs cache sync for WC buffers, and moves the object to an active LRU. IOVA lookup creates or reuses a GPUVA under VM and object locks via `drm_exec`; pinning maps the VMA with IOMMU prot flags and increments pin counts. Unpinning updates LRU state and closes non-KMS VMAs when appropriate. Close paths drop context memory accounting and tear down legacy kernel-managed VM mappings, while VM_BIND contexts defer teardown to VM close.

CPU fault/vmap paths allocate backing pages on demand, reject purged buffers, insert PFNs for mmap, and pin while vmap references exist. Madvise moves objects between WILLNEED/DONTNEED/PURGED states. Purge unmaps IOVAs, vunmaps, unmaps CPU VMAs, drops backing pages, marks purged, frees mmap offset, and truncates shmem. Evict drops mappings/pages without marking purged. Free removes the object from global lists, tears down GPUVA mappings with VM locks, handles imported sg tables differently from owned pages, drops shared-resv references for NO_SHARE, releases GEM core state, metadata, and object memory.

## State and persistence
State is in `struct msm_gem_object`: flags, madv, vmap count, global list node, pages, sg table, vaddr, debug name, metadata, pin count, and VMA refcount. Device-wide state includes total memory accounting, global object list, and LRUs. Per-file memory accounting is updated on open/close.

## Dependencies and integration points
Depends on DRM GEM/shmem/PRIME/GPUVM/drm_exec, dma-resv, dma mapping, vmalloc, DRM format helpers, trace `gpu_mem`, MSM MMU/VMA helpers, shrinker code, KMS VM, and PRIME export/import callbacks.

## Risks
Lock ordering is subtle: object locks, VM reservation objects, LRU lock, obj list lock, and fs reclaim require the documented special cases. Pin counts and VMA references must stay balanced or memory cannot be purged. Imported buffers are permanently treated as pinned/resident. Purge/evict must avoid active or pinned objects. `MSM_BO_NO_SHARE` swaps reservation objects and changes sharing semantics.

## Test signals
Exercise GEM create/open/close/free, mmap faults after madvise/purge, IOVA get/set/pin/unpin, VM_BIND versus legacy VM teardown, shrinker purge/evict, PRIME import/export, NO_SHARE rejection, CPU prep timeout/boost, memory accounting tracepoints, and lockdep under concurrent submit/shrinker/close.
