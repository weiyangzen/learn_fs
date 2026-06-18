<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h

## Purpose
Defines SMU v14.0.0 PPSMC command IDs and argument enums for the v14 PMFW mailbox.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands include PMFW/driver-if version, separate VCN0/VCN1 and JPEG0/JPEG1 power, VCN hard/soft clock bounds, GFX/SOC/FCLK min/max, unload preparation, driver DRAM address high/low, table transfers, GFX mode2 reset, enabled-feature query, GFX IMU, GFXOFF allow/disallow, zstate allow, ISP tile power and hard mins, UMSCH power, ISP stutter/MMHUB PG toggles, VPE power/DPM table/clock bounds, LSDMA, and MALL power controller/state. `PPSMC_Message_Count` is `0x3A`; `Mode_Reset_e` and `ZStates_e` define command arguments.

## Control Flow
The driver sends mailbox IDs with optional arguments. VCN/JPEG commands are instance-specific, table transfers require DRAM address setup, and reset/zstate commands require enum arguments.

## State And Persistence
Commands mutate volatile PMFW state: media/ISP/VPE/UMSCH/LSDMA/MALL power, clock bounds, GFXOFF/zstate permissions, table pointers, and reset state.

## Dependencies And Integration
Pairs with `smu_v14_0_0_pmfw.h` and compact v14 driver interface tables. Integrates with display/ISP/VPE/media scheduler power, MALL, GFX reset, firmware feature readback, and table transfer code.

## Risks And Test Signals
Risks include confusing instance-specific VCN/JPEG commands with single-instance generations, wrong tile masks, and stale table-address handling. Test signals include PMFW/driver-if version, table transfer, VCN0/1 and JPEG0/1 power, VPE DPM table, MALL state, LSDMA toggle, GFX reset, and zstate/GFXOFF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h -->
