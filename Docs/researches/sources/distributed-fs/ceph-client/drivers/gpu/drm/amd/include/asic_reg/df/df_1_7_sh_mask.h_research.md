# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_1_7_sh_mask.h

## Purpose
`df_1_7_sh_mask.h` defines bit shifts and masks for selected AMD Data Fabric 1.7 registers. It lets register-helper macros extract or update fields without hard-coded bit arithmetic in the DF v1.7 implementation.

## Important APIs, Types, And Functions
The file exports field macros for `FabricConfigAccessControl`, `DF_PIE_AON0_DfGlobalClkGater`, `DF_CS_AON0_DramBaseAddress0`, and `DF_CS_AON0_CoherentSlaveModeCtrlA0`. Important fields include `CfgRegInstAccEn`, `CfgRegInstAccRegLock`, `CfgRegInstID`, `MGCGMode`, `AddrRngVal`, `LgcyMmioHoleEn`, `IntLvNumChan`, `IntLvAddrSel`, `DramBaseAddr`, and `ForceParWrRMW`.

## Control Flow
There is no executable flow in the header. Consumers use the masks inside read/modify/write flows: `df_v1_7_enable_broadcast_mode()` clears `CfgRegInstAccEn`, `df_v1_7_get_fb_channel_number()` masks and shifts `IntLvNumChan`, `df_v1_7_update_medium_grain_clock_gating()` replaces `MGCGMode`, and `df_v1_7_enable_ecc_force_par_wr_rmw()` updates `ForceParWrRMW` through `WREG32_FIELD15`.

## State, Persistence, And Dependencies
The macros do not store state. They describe persistent hardware fields in DF configuration registers. They depend on AMD's register-helper naming convention where `REG_GET_FIELD` and `WREG32_FIELD15` construct macro names from register and field identifiers.

## Integration Points
The direct integration is `drivers/gpu/drm/amd/amdgpu/df_v1_7.c`. Higher-level integration is through `amdgpu_df_funcs`, especially clock-gating, channel-number, broadcast-mode, and ECC setup hooks.

## Risks
Bitfield mistakes can silently produce wrong register programming. A bad `IntLvNumChan` mask changes memory-channel reporting; a bad `MGCGMode` mask can break clock-gating policy; a bad `CfgRegInstAccEn` mask can leave the fabric in broadcast mode or prevent broadcast writes. The `L` suffix also relies on callers treating masks as 32-bit register values.

## Test Signals
Useful checks include static comparison against hardware register specifications, unit-style tests of `REG_GET_FIELD` expansions for representative values, runtime register traces for clock-gating toggles, HBM channel-count validation on supported ASICs, and ECC RMW enablement checks.
