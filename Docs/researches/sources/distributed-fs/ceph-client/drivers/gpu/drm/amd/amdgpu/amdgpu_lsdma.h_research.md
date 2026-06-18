## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_lsdma.h

Purpose: declares the LSDMA function table and shared wrapper APIs for memory copy/fill and register polling.

Important APIs/types: `struct amdgpu_lsdma_funcs` contains ASIC callbacks for `copy_mem`, `fill_mem`, and `update_memory_power_gating`. `struct amdgpu_lsdma` stores the selected callback table. Exports are `amdgpu_lsdma_copy_mem()`, `amdgpu_lsdma_fill_mem()`, and `amdgpu_lsdma_wait_for()`.

Control flow contract: ASIC-specific code installs callback pointers in `adev->lsdma.funcs`; generic callers use the wrappers so transfer sizes are chunked and polling is standardized.

State and persistence: only a runtime callback pointer is defined here; no durable state.

Dependencies/integration: relies on `struct amdgpu_device` from broader AMDGPU headers. Used by code paths that need lightweight DMA transfers or memory power-gating changes.

Risks: the header does not encode capability checks; callers need to avoid invoking wrappers on devices without LSDMA callbacks.

Test signals: compile coverage for ASIC callback providers and runtime copy/fill tests on LSDMA-capable hardware.
