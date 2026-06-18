# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_default.h

## Purpose
`df_1_7_default.h` provides default reset-style values for the AMD Data Fabric 1.7 register block. In this subset it exports the default value for `mmFabricConfigAccessControl`, used by the DF v1.7 driver to leave broadcast/instance access control in its baseline state.

## Important APIs, Types, And Functions
The file defines only preprocessor constants. Its key export is `mmFabricConfigAccessControl_DEFAULT`, set to `0x00000000`. There are no C types, functions, inline helpers, or data structures.

## Control Flow
This header has no runtime control flow. It participates in control flow when `df_v1_7_enable_broadcast_mode()` disables broadcast mode by writing `mmFabricConfigAccessControl_DEFAULT` through `WREG32_SOC15(DF, 0, mmFabricConfigAccessControl, ...)`.

## State, Persistence, And Dependencies
The header stores no software state. The value it defines is written to a persistent hardware register until later driver or firmware writes change it. It depends only on include guards and is meaningful together with `df_1_7_offset.h`, which defines the register address, and `df_1_7_sh_mask.h`, which defines the bit fields used when broadcast mode is enabled.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v1_7.c` includes this header with the matching offset and mask headers. The DF function table exposes the behavior through `amdgpu_df_funcs.enable_broadcast_mode`, so callers that toggle DF broadcast mode rely on this default value to restore direct register access.

## Risks
The main risk is register-generation drift: if the default value stops matching the hardware generation, disabling broadcast mode could leave stale instance-access bits set or clear bits that should be preserved. Because the macro is untyped and globally named, accidental reuse with another DF generation would compile but target the wrong semantics.

## Test Signals
Useful signals include build coverage for `df_v1_7.c`, register traces showing `mmFabricConfigAccessControl` returning to zero after broadcast-mode exit, and suspend/resume or clock-gating tests that repeatedly enter and leave DF broadcast mode without later register access failures.
