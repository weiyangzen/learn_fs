<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h

## Purpose
Defines SMU v11.5 PMFW feature bit positions and the firmware status layout used by driver feature control and telemetry paths.

## Important APIs, Types, And Constants
Exports 60 `FEATURE_*_BIT` positions covering CCLK/FCLK/SOC/GFX/DCEFCLK/VCN/ISP/A55/CVIP DPM, fan/PPT/TDC/thermal/FIT/EDC, PLL power down, ULV/VDDOFF, C-state/CC6, deep sleep clocks, GFX temperature VMIN, S0i2/S0i3, low-power blocks, PSI/PROCHOT/STAPM, CPPC, OS C-states, ATHUB power gating, ECO deep C-state, and GFX EDC. `FwStatus_t` reports enabled features and key clock/voltage/power/temperature/activity fields.

## Control Flow
This header does not execute code. SMU messages enable features by bit position, and firmware updates `FwStatus_t` for driver reads.

## State And Persistence
Feature masks represent firmware runtime policy. `FwStatus_t` is runtime telemetry/state exported from PMFW, including clock frequencies, power/thermal values, activity, and status flags. No disk persistence is involved.

## Dependencies And Integration
Included by SMU v11.5 ASIC support and paired with `smu_v11_5_ppsmc.h` messages. Integrates with CPU/APU power management, graphics/media power gating, CPPC, fan/thermal control, and metrics readers.

## Risks And Test Signals
Feature-bit order must match firmware exactly. Adding or removing bits without updating `NUM_FEATURES` and feature masks can toggle the wrong feature. Test signals include enabled-feature readback, GFX/VCN/ISP/CVIP power transitions, CPPC and C-state behavior, thermal/fan telemetry, and SMU status table sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h -->
