<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h

## Purpose
`amdgpu_ttm.h` is the public AMDGPU TTM memory-management contract. It defines private TTM placement IDs, memory-manager state containers, buffer copy/fill flags, VRAM reservation metadata, and exported helpers used across AMDGPU memory, VM, DMA-buf, userptr, and debug paths.

## Important APIs, Types, And Functions
Private placements are `AMDGPU_PL_GDS`, `AMDGPU_PL_GWS`, `AMDGPU_PL_OA`, `AMDGPU_PL_PREEMPT`, `AMDGPU_PL_DOORBELL`, and `AMDGPU_PL_MMIO_REMAP`; `__AMDGPU_PL_NUM` must track the last private placement. `struct amdgpu_gtt_mgr` wraps a TTM resource manager and `drm_mm`. `struct amdgpu_ttm_buffer_entity` combines a DRM scheduler entity, a mutex, a GART node, and up to two GART window offsets used by blit/fill jobs.

`struct amdgpu_mman` is the central device memory-manager state: TTM device, optional partition pools, aperture mapping, buffer-function ring/entities, VRAM/GTT/preempt managers, reserved regions, and SDMA debug-access BO. `struct amdgpu_copy_mem` describes BO/resource/offset tuples for copy paths. Copy flags encode TMZ, read decompression, write compression, and GFX12 DCC metadata.

The header declares manager lifecycle, GART allocation/recovery, VRAM sg-table export, reservation helpers, accelerated copy/fill helpers, userptr helpers, PTE/PDE flag helpers, debugfs setup, and MMIO-remap sg-table allocation/free. Inline helpers compute an entity GART address and convert a `drm_mm_node` start page to a byte offset.

## Control Flow
Other AMDGPU modules include this header to create and move BOs, bind pages into GART, expose VRAM/GTT manager state, validate userptr pages, and access accelerated copy/fill operations. The placement constants drive switch statements in move, eviction, I/O mapping, and manager initialization paths. The function pointer-free data structures here are initialized by `amdgpu_ttm.c` and later consumed by VM, GEM, DMA-buf, KFD, debugfs, and IP-block code.

## State And Persistence
`struct amdgpu_mman` is persistent for the lifetime of `adev->mman.initialized`. Its reserved-region array tracks BOs and optional CPU mappings for stolen, firmware, driver, and memory-training VRAM spans. Buffer entities persist while accelerated buffer functions are enabled. The header also exposes fields that encode queue-like round-robin state for move/clear entities and per-device debug-access memory.

## Dependencies And Integration Points
The header depends on Linux DMA direction, DRM GPU scheduler, DRM TTM placement, and AMDGPU VRAM/HMM/GMC headers. It forms the compile-time interface between TTM implementation, GTT/VRAM managers, VM/userptr handling, dma-buf export/import, doorbell and MMIO-remap resource managers, and copy emitters.

## Risks
Changing placement IDs is ABI-like inside the driver because TTM manager indices, switch statements, and resource-manager initialization must remain synchronized. `AMDGPU_COPY_FLAGS_SET/GET` must match packet emitter expectations. `struct amdgpu_mman` lifetime and initialization order are delicate because many modules assume subfields exist only after `amdgpu_ttm_init` and buffer funcs exist only after explicit enablement. The declared `amdgpu_ttm_tt_has_userptr` and `amdgpu_ttm_tt_userptr_invalidated` are not implemented in the paired `.c` file, so build coverage across configurations is important.

## Test Signals
Build all relevant AMDGPU configs, especially userptr on/off, debugfs on/off, and MMIO-remap users. Runtime signals include manager debugfs presence for each private placement, successful GART/VRAM allocation, correct copy flag behavior on GFX12 DCC buffers, and source-tree users compiling against the added `AMDGPU_PL_MMIO_REMAP` placement and sg-table API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h -->
