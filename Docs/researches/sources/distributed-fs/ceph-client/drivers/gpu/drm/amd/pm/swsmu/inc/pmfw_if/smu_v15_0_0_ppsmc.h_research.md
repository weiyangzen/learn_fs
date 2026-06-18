<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h

## Purpose
Defines SMU v15.0.0 PPSMC mailbox command IDs and argument enums for a compact v15 PMFW ABI.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands include PMFW and driver-if version reads, VCN/JPEG/VPE power, GFX soft min/max, FCLK/SOC/VCN/VPE bounds, unload preparation, table transfers, GFX mode2 reset, enabled-feature query, GFX IMU, GFXOFF allow/disallow, zstate allow, SmartShift status, UMSCH power, and LSDMA enable/disable. `PPSMC_Message_Count` is `0x22`; `Mode_Reset_e` and `ZStates_e` define reset/zstate arguments.

## Control Flow
The host sends a mailbox command with optional argument and checks the standard PPSMC result. Table transfer commands move PMFW driver-interface tables, while reset and zstate commands require enum arguments.

## State And Persistence
Commands affect volatile PMFW state: media/VPE/UMSCH/LSDMA power, clock bounds, GFXOFF/zstate permission, SmartShift query state, table contents, and reset state.

## Dependencies And Integration
Pairs with `smu_v15_0_0_pmfw.h` and the compact SMU 15 driver-interface table. Integrates with media/VPE power management, GFX reset/TDR, SmartShift, clock policy, and table-transfer code.

## Risks And Test Signals
Risks include assuming larger dGPU command maps, missing explicit driver-address messages, and not validating reset/zstate arguments. Test signals include PMFW/driver-if version, table transfer, VCN/JPEG/VPE power transitions, UMSCH/LSDMA toggles, GFX reset, enabled-feature query, SmartShift status, and zstate/GFXOFF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h -->
