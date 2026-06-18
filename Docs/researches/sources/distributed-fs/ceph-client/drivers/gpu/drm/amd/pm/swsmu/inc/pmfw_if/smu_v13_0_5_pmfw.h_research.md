<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h

## Purpose
Defines SMU v13.0.5 PMFW feature bits and `FwStatus_t` for another v13 APU/server variant with a distinct feature ordering.

## Important APIs, Types, And Constants
Exports 50 feature bits covering data/PPT/TDC/thermal/FIT/EDC, C-state boost, PROCHOT, CCLK/FCLK/LCLK/GFX/SOC/SHUB/MP0/DCF/VCN DPM, PSI7/DLDO, deep sleep, DVO, CC6/PC6/per-CCX PC6, DF cstates/light cstate, clock gating, fan controller, CPPC/preferred cores, GMI/XGMI controls, PCIe speed controller, PCC, S0i3, VDDOFF, ATHUB PG, and GFXOFF. `FwStatus_t` reports enabled features and live status.

## Control Flow
Feature masks are programmed or queried by PPSMC commands; status is read from firmware. There are no functions.

## State And Persistence
Feature bitmasks and status fields are volatile PMFW state. The enum order and `NUM_FEATURES 50` are persistent ABI definitions shared by driver and firmware.

## Dependencies And Integration
Pairs with `smu_v13_0_5_ppsmc.h` and integrates with CCLK/FCLK/LCLK/GFX/SOC clock control, PCIe speed control, CPPC, fan/thermal, and GFXOFF policy.

## Risks And Test Signals
Risks are variant confusion with other v13 feature maps and assumptions that low-numbered bits match older APUs. Test signals include enabled-feature readback, CCLK/FCLK/GFX DPM behavior, PCIe speed control, GFXOFF state, fan/thermal readings, and CPPC operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h -->
