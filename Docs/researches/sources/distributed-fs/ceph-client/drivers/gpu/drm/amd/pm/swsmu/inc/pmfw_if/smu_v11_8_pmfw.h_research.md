<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h

## Purpose
Defines SMU v11.8 PMFW feature bits, generated feature masks, and firmware status layout for a CPU/GFX-focused SMU generation.

## Important APIs, Types, And Constants
Exports 64 feature bits covering CCLK controller, GFX effective frequency, data calculation, thermal, PLL power down, FCLK/GFX/SOC DPM, deep-sleep clocks, core C-states, G6 SSC, STAPM, PROCHOT/CPUOFF, GFX CKS, UMC/DF throttling, SOC DPM, and related low-power controls. It also defines `FEATURE_*_MASK` helpers and `FwStatus_t`.

## Control Flow
The header is declarative. SMU message handlers use the bit positions to enable/query features, while the driver reads `FwStatus_t` to observe current firmware state.

## State And Persistence
Feature masks are runtime PMFW state. `FwStatus_t` contains firmware telemetry and control state such as enabled features, clock/frequency values, power/thermal information, and status counters. The state resets with firmware/device reset.

## Dependencies And Integration
Used by SMU v11.8 support and paired with `smu_v11_8_ppsmc.h`. Integrates with core pstate, GFXCLK, telemetry reporting, WGP control, CAC weight handling, GFX frequency/VID forcing, and feature readback paths.

## Risks And Test Signals
Risks are feature-bit ABI mismatch and mask width mistakes across 64 bits. Test signals include enabled-feature masks, telemetry reporting start/stop, pstate query/request results, GFX frequency/VID force/unforce, and thermal/prochot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h -->
