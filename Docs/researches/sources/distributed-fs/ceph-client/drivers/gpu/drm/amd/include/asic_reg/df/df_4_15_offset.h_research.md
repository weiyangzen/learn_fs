# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_offset.h

## Purpose
`df_4_15_offset.h` provides the Data Fabric 4.15 register offset needed by the AMDGPU DF v4.15 implementation. In this subset it exposes `NCSConfigurationRegister1`, used to control local processing of internal atomics.

## Important APIs, Types, And Functions
The file exports `regNCSConfigurationRegister1` with offset `0x0901` and `regNCSConfigurationRegister1_BASE_IDX` with base index `4`. It contains no C functions or types.

## Control Flow
The header is declarative. `df_v4_15_hw_init()` reads `regNCSConfigurationRegister1` when `adev->have_atomics_support` is true, ORs in a shifted bit set, and writes the register back through `WREG32_SOC15`.

## State, Persistence, And Dependencies
No software state is stored. The addressed hardware register persists the selected NCS atomic-processing policy until reset or another writer updates it. The offset depends on SOC15 register access and must be paired with `df_4_15_sh_mask.h` for the `DisIntAtomicsLclProcessing` field location.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v4_15.c` includes this header and exposes the programming through `amdgpu_df_funcs.hw_init`. The behavior is tied to the device capability flag `have_atomics_support`, so it integrates with broader ASIC discovery and initialization.

## Risks
A wrong offset or base index could modify an unrelated DF register during hardware initialization. Since the consumer ORs bits into the register, stale or mis-shifted values may accumulate unless the target mask is correct. The `reg*` naming also differs from older `mm*` headers, so helper compatibility matters.

## Test Signals
Signals include successful build of `df_v4_15.c`, hardware-init traces showing a read and write to base index 4 offset `0x0901` only when atomics support is present, and atomics-capability tests that confirm local internal atomic processing is disabled for the intended lanes/bits.
