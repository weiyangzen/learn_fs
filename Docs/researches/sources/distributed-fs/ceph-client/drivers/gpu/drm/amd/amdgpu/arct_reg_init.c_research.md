# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/arct_reg_init.c

## Purpose
This small Arcturus initialization file fills AMDGPU's per-HWIP register-base table from generated Arcturus IP offset data. It makes later `SOC15` register macros resolve the right base arrays for GC, HDP, MMHUB, ATHUB, NBIO, MP0/MP1, UVD, DF, OSSSYS, SDMA0-7, SMUIO, THM, UMC, and RSMU.

## Important APIs, types, and functions
`arct_reg_base_init(struct amdgpu_device *adev)` is the only function. It loops over `MAX_INSTANCE` and assigns `adev->reg_offset[HWIP][i]` pointers to the matching generated `*_BASE.instance[i]` tables from `arct_ip_offset.h`.

## Control flow
The function is linear: for every possible instance index, assign all supported HWIP base pointers, then return zero. There is no validation or conditional behavior.

## State and persistence behavior
It mutates `adev->reg_offset`, which persists for the driver lifetime and is used by subsequent register reads/writes. No hardware registers are accessed directly here.

## Dependencies
It depends on AMDGPU core types, SOC15 common definitions, and generated Arcturus IP offset tables. The correctness of every pointer depends on `arct_ip_offset.h` matching the ASIC.

## Integration points
ASIC bring-up calls this before code uses SOC15 register accessors. ATHUB, SDMA, GC, MMHUB, and other IP blocks rely on these offsets indirectly through `RREG32_SOC15`/`WREG32_SOC15`.

## Risks and edge cases
The function assumes all generated base arrays have `MAX_INSTANCE` entries. A wrong HWIP-to-base mapping causes broad register access corruption. It intentionally initializes only blocks used by the driver; new driver code for another block must add that block here.

## Test signals
Compile-time coverage checks symbol availability. Runtime validation is indirect: IP init succeeds, SOC15 register reads hit expected hardware, and register dumps show sane offsets for every initialized HWIP.
