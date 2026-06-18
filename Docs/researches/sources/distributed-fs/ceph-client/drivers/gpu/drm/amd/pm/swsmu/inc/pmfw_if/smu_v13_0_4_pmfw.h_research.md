<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h

## Purpose
Defines SMU v13.0.4 PMFW feature bits and `FwStatus_t`, adding ISP/IPU-related DPM and v13.0.4-specific low-power controls.

## Important APIs, Types, And Constants
Exports 59 feature bits for fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN/FCLK/SOC/MP0/LCLK/SHUB/DCF/ISP/IPU/GFX DPM, deep-sleep clocks, zstates/whisper, SMU/fuse/GFX DEM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, DVO, CPPC, FASTBYPASS CLDO, ATHUB PG, VDDOFF/Zstates ECO, CC6, UMCCLK/ISPCLK/HSPCLK/IPUCLK deep sleep, and MPCCX whisper mode.

## Control Flow
The file supplies bit positions for feature-mask commands and a firmware status structure for reads. It has no functions.

## State And Persistence
Feature masks control volatile firmware policy. `FwStatus_t` is live PMFW state and telemetry. The bit order is a persistent ABI contract for this ASIC generation.

## Dependencies And Integration
Used by SMU v13.0.4 support and paired with its PPSMC commands. It integrates with ISP/IPU power/clock management, DVO, CPPC, GFX/media power, and low-power state handling.

## Risks And Test Signals
Risks include cross-using v13.0.1/v13.0.5 feature maps, especially where bit 44 semantics differ, and stale `NUM_FEATURES`. Test signals include feature-mask readback, ISP/IPU DPM behavior, VCN/GFX DPM, DVO/CPPC paths, zstate/S0i3, and status telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h -->
