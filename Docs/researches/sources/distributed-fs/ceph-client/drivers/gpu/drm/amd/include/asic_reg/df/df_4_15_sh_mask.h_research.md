# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_15_sh_mask.h

## Purpose
`df_4_15_sh_mask.h` defines the shift and mask for the DF 4.15 `NCSConfigurationRegister1` field that disables local processing of internal atomics. It is the field-layout companion to `df_4_15_offset.h`.

## Important APIs, Types, And Functions
The exported macros are `NCSConfigurationRegister1__DisIntAtomicsLclProcessing__SHIFT`, set to `0x3`, and `NCSConfigurationRegister1__DisIntAtomicsLclProcessing_MASK`, set to `0x0003FFF8L`. There are no runtime APIs.

## Control Flow
The header has no flow. `df_v4_15_hw_init()` builds `dis_lcl_proc` from bits 1, 2, and 13, shifts it by `DisIntAtomicsLclProcessing__SHIFT`, ORs it into `regNCSConfigurationRegister1`, and writes the result when `adev->have_atomics_support` is enabled.

## State, Persistence, And Dependencies
The macros do not store state. They define how software writes persistent hardware state controlling NCS internal atomic local-processing behavior. The consumer currently uses the shift macro directly and does not mask before ORing, so correctness of both the chosen bit set and the field layout is important.

## Integration Points
The direct integration is `drivers/gpu/drm/amd/amdgpu/df_v4_15.c` through the `hw_init` hook in `amdgpu_df_funcs`. The field affects devices with atomic support and therefore ties into GPU initialization rather than an optional debug path.

## Risks
The defined mask covers bits 3 through 17, but the current consumer only shifts and ORs selected bits. If the input bit set grows beyond the mask or the shift changes, the code could set unintended register bits. A missing clear step means firmware-provided values are preserved, which may be intended but makes validation dependent on reset state.

## Test Signals
Useful checks include static validation that `(dis_lcl_proc << SHIFT)` stays inside `MASK`, register readback after `df_v4_15_hw_init()`, boot tests with `have_atomics_support` both true and false, and workload tests that exercise internal atomics after initialization.
