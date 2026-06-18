# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.h

## Purpose
This header declares the GC 12.1 GMC helper entry points consumed by the v12.0 IP block implementation.

## Important APIs, Types, and Functions
It declares `gmc_v12_1_set_gmc_funcs(struct amdgpu_device *adev)`, `gmc_v12_1_set_irq_funcs(struct amdgpu_device *adev)`, and `gmc_v12_1_init_vram_info(struct amdgpu_device *adev)`. These install v12.1-specific GMC and IRQ callback tables and seed default VRAM type/width.

## Control Flow and State
The header has no runtime flow. The implementation writes function pointers into `adev->gmc`, configures IRQ source function pointers, and initializes `adev->gmc.vram_type`/`vram_width`.

## Dependencies and Integration Points
It depends on `struct amdgpu_device` being visible in including files. `gmc_v12_0.c` includes it and calls the helpers when GC IP version is 12.1.0.

## Risks and Test Signals
The risk is mismatched helper signatures or failure to call them during v12.1 early init. Test signals include GC 12.1 boot selecting v12.1 callbacks, HBM4 metadata appearing in GMC state, retry-fault processing, and PASID TLB invalidation.
