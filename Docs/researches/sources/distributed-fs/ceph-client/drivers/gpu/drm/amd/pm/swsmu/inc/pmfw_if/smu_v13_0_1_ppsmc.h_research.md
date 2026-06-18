<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h

## Purpose
Defines SMU v13.0.1 PPSMC command IDs for a compact PMFW command ABI.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands cover PMFW and driver-if version reads, VCN power, GFX soft min, unload preparation, table transfer, mode2 reset, enabled-feature query, FCLK/VCN/SOC clock bounds, GFX IMU, GFXOFF allow/disallow, JPEG power, zstates, SmartShift status, and related media controls. `PPSMC_Message_Count` is `0x29`. `Mode_Reset_e` defines the reset argument for `PPSMC_MSG_GfxDeviceDriverReset`.

## Control Flow
The host submits a mailbox ID and optional argument; table transfer uses PMFW-managed table address conventions for this generation. Mode reset commands use the enum argument to select reset type.

## State And Persistence
Runtime state includes media power-gate state, clock min/max requests, GFXOFF permission, zstate permission, SmartShift status query, and table transfer state. It resets with PMFW/device reset.

## Dependencies And Integration
Pairs with `smu_v13_0_1_pmfw.h`, media power management, GFX reset/TDR handling, SmartShift, and clock limit paths.

## Risks And Test Signals
Risks include treating this compact command set like the larger dGPU v13 maps and sending absent feature/table-address commands. Test signals include version reads, VCN/JPEG power tests, mode2 reset, enabled feature query, GFXOFF allow/disallow, and zstate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h -->
