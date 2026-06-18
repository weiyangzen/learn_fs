<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c

## Purpose
`amdgpu_ttm.c` is the AMDGPU implementation of the DRM TTM memory-management backend. It wires TTM buffer-object operations to AMD GPU memory domains, GART binding, VRAM/GTT/on-chip range managers, DMA-accelerated moves/fills, userptr/HMM page handling, debug memory access, and initialization/teardown of memory-manager state. In this tree it also owns a newer `AMDGPU_PL_MMIO_REMAP` placement used for a fixed MMIO remap page and dma-buf export support.

## Important APIs, Types, And Functions
The file registers `amdgpu_bo_driver`, a `struct ttm_device_funcs`, with callbacks for `ttm_tt_create`, populate/unpopulate/destroy, eviction decisions, move handling, I/O reservation/PFN translation, debug memory access, and delete/release notifications. `struct amdgpu_ttm_tt` extends `struct ttm_tt` with the backing GEM object, GART offset, userptr metadata, a `bound` flag, and optional partition pool ID.

Core exported entry points include `amdgpu_ttm_init`, `amdgpu_ttm_fini`, `amdgpu_ttm_set_buffer_funcs_status`, `amdgpu_copy_buffer`, `amdgpu_ttm_clear_buffer`, `amdgpu_fill_buffer`, `amdgpu_ttm_alloc_gart`, `amdgpu_ttm_recover_gart`, `amdgpu_ttm_domain_start`, userptr helpers, PTE/PDE flag helpers, `amdgpu_ttm_evict_resources`, debugfs init, and `amdgpu_ttm_mmio_remap_alloc_sgt/free_sgt`. Local helpers cover eviction placement, GPU copy-window mapping, blit moves, TTM backend binding/unbinding, VRAM reservation, memory-training reservation, per-partition TTM pools, MMIO remap BO allocation, and SDMA/MMIO debug reads.

## Control Flow
Initialization starts with `ttm_device_init`, optional per-memory-partition TTM pools, VRAM manager setup for discrete GPUs, BAR ioremap of visible VRAM, reservation of firmware/VGA/memory-training regions, GTT manager setup, doorbell and MMIO-remap range managers, the singleton MMIO-remap BO, preempt manager, GDS/GWS/OA managers, and a small SDMA debug-access BO. Teardown reverses those allocations, frees reserved VRAM regions, unmaps the aperture, tears down range managers, and finalizes TTM.

Buffer movement flows through `amdgpu_bo_move`. Simple SYSTEM/GTT transitions use null moves with backend bind/unbind. VRAM-to-SYSTEM and SYSTEM-to-VRAM moves may request a TT hop. Other movable domains prefer accelerated blits through `amdgpu_move_blit`, which delegates to `amdgpu_ttm_copy_mem_to_mem`. That function walks source and destination resources with `amdgpu_res_cursor`, maps inaccessible ranges through temporary GART windows, emits copy packets with TMZ/DCC flags when needed, limits each job to 256 MiB, and returns the last fence. If acceleration is unavailable and both resources are CPU visible/copyable, the fallback is `ttm_bo_move_memcpy`.

GART binding is split between populate/bind/unbind. Userptr BOs allocate an sg table shell during populate, later pin pages with `sg_alloc_table_from_pages` and `dma_map_sgtable`; imported DMA-bufs map attachments on bind; internal TT objects come from TTM pools. Bind computes AMDGPU PTE flags, assigns a GART offset only for TT resources with GART address space, and binds pages into the GART. Reset recovery recomputes PTE flags and rebinds.

## State And Persistence
Long-lived state is in `adev->mman`: the TTM device, VRAM/GTT/preempt managers, optional partition pools, buffer-function scheduler entities and GART windows, reserved VRAM BOs, aperture mapping, and the SDMA debug BO. `struct amdgpu_ttm_tt` persists per-BO userptr/import/binding state. Reserved regions are materialized as kernel BOs so TTM cannot allocate over firmware, VGA, driver usage, or memory-training data. Userptr state persists task and flags until TT destruction; HMM ranges are populated by callers during validation.

## Dependencies And Integration Points
This file is tightly coupled to DRM TTM, DRM scheduler, dma-resv/fence, DMA-buf, Linux DMA mapping, HMM, debugfs, AMDGPU BO/VM/GART/VRAM/GTT managers, SDMA buffer functions, RAS and PSP memory-training state, Atom firmware reserved memory queries, doorbell management, and XGMI/APU partition data. The MMIO-remap path integrates with dma-buf import/export policy by synthesizing `sg_table` entries with `dma_map_resource`, because the remap page has no `struct page` backing.

## Risks
Memory-domain correctness is high risk: wrong PTE flags, GART offsets, TMZ flags, or DCC copy flags can corrupt GPU-visible memory. Error paths in `amdgpu_ttm_set_buffer_funcs_status` and the MMIO-remap singleton need leak and double-free coverage because they allocate scheduler entities, drm_mm nodes, pinned BOs, and range managers in sequence. `amdgpu_ttm_mmio_remap_alloc_sgt` assumes a small contiguous MMIO resource and depends on callers to validate placement and peer-DMA policy. Userptr pin/unpin depends on exactly paired HMM tracking and SG cleanup. Debugfs VRAM/IOMEM access is privileged but still sensitive to IOMMU translation, page mapping checks, and device removal.

## Test Signals
Useful signals include TTM move tests across SYSTEM/GTT/VRAM including multi-hop moves, suspend/resume toggling buffer funcs, GPU reset GART recovery, userptr eviction/revalidation, imported dma-buf bind/unbind, SR-IOV and XGMI firmware-buffer allocation paths, reserved VRAM range accounting, debugfs VRAM/IOMEM read/write smoke tests, and explicit MMIO-remap BO export/import tests checking sg allocation/free, DMA unmap, and teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c -->
