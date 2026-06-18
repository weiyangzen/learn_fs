# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_offset.h

## Purpose
`df_4_3_offset.h` provides Data Fabric 4.3 register offsets for RAS poison-mode discovery. It maps the low and high hardware assert mask registers used by the DF v4.3 driver.

## Important APIs, Types, And Functions
The file exports `regDF_CS_UMC_AON0_HardwareAssertMaskLow` at `0x0e3e`, `regDF_NCS_PG0_HardwareAssertMaskHigh` at `0x0e3f`, and matching `_BASE_IDX` macros set to `4`. It contains no executable code.

## Control Flow
The header is used by `df_v4_3_query_ras_poison_mode()`, which reads both registers with `RREG32_SOC15`, extracts four assert-mask bits using the companion shift/mask header, and returns true, false, or warns on inconsistent mixed settings.

## State, Persistence, And Dependencies
No software state is stored. The addressed registers are persistent DF hardware state that reflects RAS poison handling configuration. The offsets depend on SOC15 access with base index 4 and on `df_4_3_sh_mask.h` for bit definitions.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v4_3.c` includes this header and exposes poison-mode reporting through `amdgpu_df_funcs.query_ras_poison_mode`. The result can inform higher-level AMDGPU RAS handling and diagnostics.

## Risks
Wrong offsets or base indices would make poison-mode detection read unrelated registers, potentially causing false diagnostics or hiding inconsistent RAS settings. Because the logic treats mixed bit states as a warning and false result, any address error could downgrade valid poison mode.

## Test Signals
Signals include register readback tests for base index 4 offsets `0x0e3e` and `0x0e3f`, simulated or captured register values for all-on/all-off/mixed assert bits, and RAS diagnostic logs confirming the warning path only appears for genuinely inconsistent hardware state.
