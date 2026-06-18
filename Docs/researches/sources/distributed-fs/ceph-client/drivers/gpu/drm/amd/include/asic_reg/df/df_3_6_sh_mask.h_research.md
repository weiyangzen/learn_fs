# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_sh_mask.h

## Purpose
`df_3_6_sh_mask.h` defines shifts and masks for AMD Data Fabric 3.6 registers used by AMDGPU. It describes access-control fields, DF clock-gating mode, global hash-interleave controls, DRAM base/limit fields, and low/high hardware assert mask bits used for RAS poison-mode detection.

## Important APIs, Types, And Functions
Important macro groups cover `FabricConfigAccessControl`, `DF_PIE_AON0_DfGlobalClkGater`, `DF_CS_UMC_AON0_DfGlobalCtrl`, `DF_CS_UMC_AON0_DramBaseAddress0`, `DF_CS_UMC_AON0_DramLimitAddress0`, `DF_CS_UMC_AON0_HardwareAssertMaskLow`, and `DF_NCS_PG0_HardwareAssertMaskHigh`. The file includes one ASIC-specific variant, `ALDEBARAN_DF_CS_UMC_AON0_DramBaseAddress0__IntLvNumChan_MASK`, for wider channel-interleave encoding.

## Control Flow
There is no executable flow in the header. In `df_v3_6.c`, these macros shape branch outcomes and register writes: broadcast mode clears `CfgRegInstAccEn`, hash-query logic interprets `GlbHashIntlvCtl64K`, `GlbHashIntlvCtl2M`, and `GlbHashIntlvCtl1G`, channel discovery masks `IntLvNumChan`, DRAM range logic can decode base/limit fields, and RAS poison mode checks `HWAssertMsk0`, `HWAssertMsk1`, `HWAssertMsk28`, and `HWAssertMsk31` for consistency.

## State, Persistence, And Dependencies
The macros are stateless descriptions of persistent hardware fields. They depend on AMD register helper conventions where field names are concatenated into macro names by `REG_GET_FIELD` and field-write helpers. The hardware state they describe affects memory interleaving, fabric hashing, clock gating, and RAS behavior.

## Integration Points
`drivers/gpu/drm/amd/amdgpu/df_v3_6.c` is the main integration point. The masks feed `amdgpu_df_funcs` implementations for initialization, clock-gating, channel reporting, perfmon operation, and `query_ras_poison_mode`. The offset header also reaches `amdgpu_xgmi.c`, so matching field definitions may be relevant to multi-GPU fabric configuration.

## Risks
Incorrect bit definitions can cause subtle platform behavior changes: hash status may be reported incorrectly, channel counts may be wrong, DF clock-gating could be misprogrammed, and poison-mode detection could issue false positives or miss inconsistent hardware assert settings. The 32 single-bit assert-mask definitions are repetitive, so generated off-by-one errors are plausible.

## Test Signals
Useful tests include field extraction against known register snapshots, RAS poison-mode tests for all-on, all-off, and inconsistent bit combinations, ASIC-specific channel-count validation for Aldebaran, clock-gating state checks, and static comparison of generated masks against the DF 3.6 register specification.
