<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h

## Purpose
Defines SMU v11.5 PPSMC command IDs for APU-oriented power, media, telemetry, and clock control.

## Important APIs, Types, And Constants
The command set includes GFXOFF enable/disable/allow/disallow, ISP tile power, VCN/JPEG/CVIP power, RLC notifications, clock soft/hard min/max for GFX/SOC/FCLK/VCN/ISP/CCLK, table address/transfer, mode2 reset, enabled feature query, post code, frequency queries, PPT/thermal/power/current/voltage/activity metrics, time constants, mitigation hysteresis, DRAM logging, DF pstate control, active WGP request/query, fast/slow PPT limits, and GFXOFF residency/status counters. `PPSMC_Message_Count` is `0x53`.

## Control Flow
The driver sends one mailbox command at a time; table transfers require address setup first, and logging requires address/buffer-size setup plus start/stop messages. Frequency and metrics getters read the response register.

## State And Persistence
Commands modify firmware runtime state such as media power gates, clock bounds, CCLK policy, DF pstate, PPT limits, logging configuration, active WGP request, and GFXOFF residency logging. Persistent state is limited to firmware-side policy until reset.

## Dependencies And Integration
Pairs with `smu_v11_5_pmfw.h`, display/media code, reset/TDR handling, PM metrics, CCLK/DF pstate management, and GFXOFF residency diagnostics.

## Risks And Test Signals
Risks include sending unsupported media-tile commands on the wrong ASIC, failing to retry busy results, and misinterpreting units for frequency and PPT percentages. Test signals include version checks, table transfer, media power up/down, mode2 reset, GFXOFF counters, DRAM logging, and fast/slow PPT limit readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h -->
