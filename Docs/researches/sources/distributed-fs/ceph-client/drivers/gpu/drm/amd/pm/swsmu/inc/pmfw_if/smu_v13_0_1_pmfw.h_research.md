<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h

## Purpose
Defines SMU v13.0.1 PMFW feature bits and `FwStatus_t` for feature control and status reporting.

## Important APIs, Types, And Constants
Exports 61 feature bit positions covering CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, PLL/ULV/VDDOFF, VCN/FCLK/SOC/MP0/LCLK/SHUB/DCF/GFX DPM, deep sleep, GFX temp VMIN, zstates/whisper, low-power blocks, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, CPPC preferred cores, SmartShift, voltage monitor, ATHUB PG, VDDOFF/Zstates ECO, CC6, and UMCCLK/HSPCLK deep sleep. `FwStatus_t` carries enabled features and live firmware status.

## Control Flow
Feature bit positions are consumed by PPSMC feature-mask messages; status is read through firmware table transfer or status queries. There are no functions.

## State And Persistence
Feature masks are runtime PMFW state. `FwStatus_t` is a volatile status snapshot that reflects enabled features and current PM telemetry/control state.

## Dependencies And Integration
Used by SMU v13.0.1 ASIC support and paired with its PPSMC message map. It integrates with APU low-power states, CPPC/SmartShift, media power management, GFX/SOC clock management, and thermal/power status consumers.

## Risks And Test Signals
Risks are feature-bit reorder, stale `NUM_FEATURES`, and incorrect assumptions across v13 variants. Test signals include enabled-feature readback, zstate/S0i3 behavior, SmartShift reporting, VCN/GFX DPM operation, and status table sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h -->
