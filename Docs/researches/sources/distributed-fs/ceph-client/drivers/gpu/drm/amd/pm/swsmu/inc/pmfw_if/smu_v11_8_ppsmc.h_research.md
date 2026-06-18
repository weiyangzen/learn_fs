<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h

## Purpose
Defines SMU v11.8 PPSMC mailbox commands for core pstate, GFXCLK, telemetry, WGP, CAC weights, soft CCLK bounds, and GFX frequency/VID control.

## Important APIs, Types, And Constants
Standard result constants are present. Command IDs include driver table address high/low, table transfers, core pstate request/query, GFXCLK request/query, VDDCR_SOC clock query, DF pstate query, S3 power-off register configuration, active WGP request/query, telemetry reporting start/stop/clear max, core enable mask, GC RSMU soft reset, GFX/L3 CAC weight operations, driver table VMID, CCLK soft min/max, GFX frequency and VID get/force/unforce, and enabled feature query. `PPSMC_Message_Count` is `0x3E`.

## Control Flow
Commands are mailbox operations. Table and S3 register commands require address high/low ordering; telemetry commands toggle ongoing firmware reporting; force/unforce commands alter GFX frequency/VID state until released.

## State And Persistence
Runtime state includes driver table pointer/VMID, requested pstates, telemetry reporting state, active WGP/core masks, CAC weights, CCLK bounds, and forced GFX frequency/VID. State is firmware-resident and volatile.

## Dependencies And Integration
Pairs with `smu_v11_8_pmfw.h` and integrates with CPU core pstate control, graphics frequency management, telemetry consumers, soft reset paths, and CAC/power tuning code.

## Risks And Test Signals
Risks include leaving forced GFX frequency/VID active, wrong VMID/table address programming, and command ID gaps marked reserved. Test signals include version checks, table transfer, telemetry report lifecycle, pstate query, active WGP query, force/unforce round trips, and soft reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h -->
