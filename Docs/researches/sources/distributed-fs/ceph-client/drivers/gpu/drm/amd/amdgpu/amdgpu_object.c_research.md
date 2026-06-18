
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.c

## Purpose
Implements AMDGPU buffer-object lifecycle and placement policy on top of DRM GEM and TTM. It creates user, VM, kernel, ISP-imported, and fixed-offset VRAM BOs; maps and unmaps them for the CPU; pins, unpins, fences, syncs, wipes, and reports them; and initializes/finalizes the driver memory manager.

## Important APIs, Types, and Functions
Key exported entry points are `amdgpu_bo_create`, `amdgpu_bo_create_user`, `amdgpu_bo_create_vm`, `amdgpu_bo_create_reserved`, `amdgpu_bo_create_kernel`, `amdgpu_bo_create_kernel_at`, `amdgpu_bo_create_isp_user`, `amdgpu_bo_free_kernel`, `amdgpu_bo_free_isp_user`, `amdgpu_bo_kmap`, `amdgpu_bo_pin`, `amdgpu_bo_unpin`, `amdgpu_bo_fault_reserve_notify`, `amdgpu_bo_release_notify`, `amdgpu_bo_sync_wait_resv`, and GPU-address helpers. `amdgpu_bo_placement_from_domain` translates AMDGPU GEM domains into TTM placements including VRAM, GTT, CPU, GDS/GWS/OA, doorbell, and preemptible memory. `amdgpu_bo_set_metadata`, `amdgpu_bo_get_metadata`, and tiling helpers handle user BO side metadata.

## Control Flow
Creation validates domain capacity, normalizes alignment, initializes a GEM private object, derives placement, calls `ttm_bo_init_reserved`, optionally clears VRAM with a kernel fence, and unreserves unless the caller supplied a reservation object. Kernel helpers then reserve, pin, optionally bind GART, and map. Pinning rejects userptrs, narrows imported BOs to GTT, selects preferred VRAM/GTT policy, validates placement through TTM, increments pin counters, and updates VRAM/GART pin accounting. Move and release callbacks update VM state, invalidate exported dma-buf mappings, unmap CPU kmap state, and wipe flagged VRAM before release.

## State and Persistence Behavior
Persistent runtime state lives in `struct amdgpu_bo` and TTM resources: preferred/allowed domains, placement array, flags, kmap, VM base, parent BO, KFD association, and XCP partition ID. User BO metadata and tiling flags are heap-owned by `struct amdgpu_bo_user`. Device accounting is held in atomics such as `vram_pin_size`, `visible_pin_size`, `gart_pin_size`, and `num_vram_cpu_page_faults`. No on-disk persistence is performed, but release wiping protects prior VRAM contents from later users.

## Dependencies and Integration Points
Depends heavily on DRM GEM, dma-buf, dma-resv, TTM, AMDGPU VM, VRAM/GTT managers, KFD eviction fences, GMC address translation, and tracepoints. It is called by GEM ioctls, GPU VM code, display scanout paths, firmware/kernel allocations, ISP/V4L2 integration, debugfs BO reporting, and page fault handling.

## Risks and Test Signals
Risks include incorrect domain fallback, leaked reservations on error paths, stale CPU mappings across moves, imported dma-buf pin imbalance, visible-VRAM migration failure on CPU faults, and release-wipe failures during suspend/unplug. Test by exercising GEM BO creation flags, VRAM-only and VRAM/GTT fallback, CPU faults on invisible VRAM, exported/imported dma-bufs, KFD eviction release, suspend teardown, debugfs BO output, and pin accounting under repeated pin/unpin cycles.
