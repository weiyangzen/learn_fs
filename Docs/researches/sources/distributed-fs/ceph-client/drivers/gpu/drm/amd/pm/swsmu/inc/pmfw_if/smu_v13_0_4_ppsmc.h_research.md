<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h

## Purpose
Defines SMU v13.0.4 PPSMC command IDs for media, clocks, ISP tile power, zstates, VPE/LSDMA, and MALL power control.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands cover PMFW/driver-if version, VCN power, GFX soft min/max/hard min, table address/transfer, mode2 reset, enabled-feature query, SOC/FCLK/VCN bounds, GFX IMU, GFXOFF allow/disallow, JPEG power, zstate allow, ISP tile power and hard-min clocks, UMSCH power, ISP stutter/MMHUB PG toggles, VPE power/DPM table/clock bounds, LSDMA enable/disable, and MALL power controller/state. `PPSMC_Message_Count` is `0x31`; argument enums include `Mode_Reset_e` and `ZStates_e`.

## Control Flow
Mailbox commands mutate PMFW state or return values. ISP tile arguments use tile masks, reset commands use `Mode_Reset_e`, and zstate commands use `ZStates_e`.

## State And Persistence
Runtime state includes VCN/JPEG/ISP/VPE/UMSCH power gates, clock bounds, GFXOFF/zstate permissions, MALL power state, LSDMA enablement, and table contents. State is volatile.

## Dependencies And Integration
Pairs with `smu_v13_0_4_pmfw.h`, ISP/IPU/display code, VPE/LSDMA support, media scheduler power, GFX reset, and MALL power management.

## Risks And Test Signals
Risks include incorrect tile masks, using v14/v15 VCN instance commands on this map, and missing reset/zstate argument validation. Test signals include table transfer, ISP tile power transitions, VPE DPM table reads, LSDMA toggles, MALL state changes, GFX reset, and GFXOFF/zstate smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h -->
