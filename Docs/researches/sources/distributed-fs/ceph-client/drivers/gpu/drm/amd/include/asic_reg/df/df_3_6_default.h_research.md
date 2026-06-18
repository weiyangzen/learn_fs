# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_default.h

## Purpose
`df_3_6_default.h` provides the default value for an AMD Data Fabric 3.6 access-control register. In this subset, that value is used to restore `mmFabricConfigAccessControl` after broadcast-mode access.

## Important APIs, Types, And Functions
The only exported macro is `mmFabricConfigAccessControl_DEFAULT`, with value `0x00000000`. The header contains no functions, types, variables, or inline logic.

## Control Flow
The header has no direct control flow. `df_v3_6_enable_broadcast_mode()` uses the macro in its disable path, writing the default back to `mmFabricConfigAccessControl` after the enable path has cleared `CfgRegInstAccEn`.

## State, Persistence, And Dependencies
Software state is not stored here. The defined value becomes persistent hardware state when written to the DF register. It is coupled with `df_3_6_offset.h` for the register address and `df_3_6_sh_mask.h` for the field layout.

## Integration Points
The direct consumer is `drivers/gpu/drm/amd/amdgpu/df_v3_6.c`, where broadcast-mode behavior is part of the `amdgpu_df_funcs` table. That same DF implementation also handles perfmon setup, hash querying, clock gating, channel discovery, and RAS poison-mode queries, so restoring fabric access control is part of broader DF lifecycle management.

## Risks
If the reset/default value differs on a specific DF 3.6 ASIC variant, the driver may restore the wrong fabric access mode. The macro name matches the v1.7 default name, so using multiple generation headers in one translation unit would be unsafe.

## Test Signals
Signals include build coverage for `df_v3_6.c`, register traces confirming `mmFabricConfigAccessControl` returns to zero after broadcast-mode exit, and stress tests around DF clock-gating and perfmon operations that require reliable direct DF register access after broadcast writes.
