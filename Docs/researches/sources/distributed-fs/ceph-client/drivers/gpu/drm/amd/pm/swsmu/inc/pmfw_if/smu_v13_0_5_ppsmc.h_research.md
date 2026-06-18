<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h

## Purpose
Defines the compact SMU v13.0.5 PPSMC command map.

## Important APIs, Types, And Constants
Commands cover SMU/PMFW versioning, driver-if version, table transfer, GFX reset, enabled-feature query, soft min/max GFX/FCLK/SOC/VCN clocks, GFX IMU, GFXOFF allow/disallow, VCN/JPEG power, SmartShift status, and VPE/UMSCH-related control. `PPSMC_Message_Count` is decimal `27`, and `Mode_Reset_e` supplies the reset argument.

## Control Flow
Each entry is a mailbox command. Reset commands require an enum argument; query commands return the mailbox response value; media power commands toggle firmware-managed gates.

## State And Persistence
Runtime state includes table contents, clock bounds, GFXOFF permission, media power gates, SmartShift query state, and reset requests. It is volatile firmware state.

## Dependencies And Integration
Pairs with `smu_v13_0_5_pmfw.h`, media power, GFX reset/TDR, SmartShift, and clock policy code.

## Risks And Test Signals
Risks include the decimal message count, compact command coverage compared with other v13 files, and missing table-address setup assumptions. Test signals include version checks, table transfer, GFX reset, enabled features, VCN/JPEG power, and clock min/max readback through behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h -->
