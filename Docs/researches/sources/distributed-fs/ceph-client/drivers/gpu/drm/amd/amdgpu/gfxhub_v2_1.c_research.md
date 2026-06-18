# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c

## Purpose
This file implements the GFXHUB 2.1 backend for later GC 10.3 devices. It is close to v2.0 but adds SR-IOV handling, UTCL2 harvest programming, mode2 register save/restore, and a halt path for quiescing EA activity.

## Important APIs, Types, and Functions
`gfxhub_v2_1_funcs` exports the standard GFXHUB callbacks plus `utcl2_harvest`, `mode2_save_regs`, `mode2_restore_regs`, and `halt`. Private functions mirror v2.0 for invalidate request generation, fault-status printing, GART enable/disable, fault default policy, and VM hub initialization.

## Control Flow and State
GART enable optionally programs VF FB location copy registers, then initializes VMID0 page tables, apertures, TLB/cache controls, context0, disabled identity aperture, user contexts, and invalidation ranges. SR-IOV VFs skip many L2 and system-aperture register writes that the PF owns. `utcl2_harvest()` computes disabled shader-array bits from eFuse and VBIOS fields for selected GC 10.3 IPs and writes the harvest bypass register. `save_regs()` snapshots many GCVM context, L2, dummy fault, and protection registers into `adev->gmc`; `restore_regs()` replays them and restores FB location and L1 TLB control. `halt()` disables default fault handling, invalidates user page-table ranges, and polls `GRBM_STATUS2` for EA/link idle.

## Dependencies and Integration Points
It depends on GC 10.3 register headers and is selected by `gmc_v10_0.c` for GC 10.3.x IP versions. Mode2 save/restore integrates with lower-power reset paths. UTCL2 harvest is invoked before GFX block register setup in GMC v10 hardware init.

## Risks and Test Signals
Key risks are SR-IOV PF/VF register ownership, saved-register stride correctness, harvested-SA bit translation, and `halt()` timeouts. Test signals include GC 10.3 boot and reset, VF assignment, S0ix/mode2 cycles, harvested SKU boot, fault logging, and GPUVM invalidation after GFXOFF.
