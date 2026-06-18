<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c

## Purpose
`radeon_sa.c` wraps the DRM suballocator for Radeon small, temporary GPU-visible allocations. These allocations back transient structures such as semaphores and other ring scratch buffers without creating a full BO for every small object.

## Important APIs, types, and functions
The file operates on `struct radeon_sa_manager` and `struct drm_suballoc`. Manager lifecycle is split into `radeon_sa_bo_manager_init`, `radeon_sa_bo_manager_start`, `radeon_sa_bo_manager_suspend`, and `radeon_sa_bo_manager_fini`. Individual allocations use `radeon_sa_bo_new` and `radeon_sa_bo_free`. Debug builds expose `radeon_sa_bo_dump_debug_info`.

## Control flow
Initialization creates one Radeon BO of the requested size and initializes `drm_suballoc_manager` with the requested alignment. Start reserves, pins, and maps the manager BO in the requested domain, publishing GPU and CPU addresses. Suspend reverses the map/pin while keeping the BO allocated for resume. New allocations call `drm_suballoc_new` with nonblocking behavior disabled; frees optionally attach a DMA fence so the suballocation can be reused only after GPU use completes.

## State, dependencies, and integration points
State is held by the manager BO, `domain`, `gpu_addr`, `cpu_ptr`, and the embedded DRM suballocator. The file depends on Radeon BO reservation/pin/kmap helpers and DRM suballocation. `radeon_semaphore.c` uses the device `ring_tmp_bo` manager to allocate 8-byte semaphore slots that are visible to GPU engines.

## Risks and test signals
The main risks are freeing a suballocation before its fence completes, failing to pin/map the manager BO during resume, and exhausting the fixed pool under heavy synchronization pressure. Test signals include semaphore creation/free stress, ring synchronization tests, suspend/resume of the temporary pool, and debugfs suballocator dumps showing sane live/free ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_sa.c -->
