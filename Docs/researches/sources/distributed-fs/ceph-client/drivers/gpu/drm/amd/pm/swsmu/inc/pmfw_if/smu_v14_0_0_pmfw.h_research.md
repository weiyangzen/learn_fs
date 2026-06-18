<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h

## Purpose
Defines SMU v14.0.0 PMFW feature bits, firmware image header/footer types, and firmware status layouts for v14.0.0 and v14.0.1.

## Important APIs, Types, And Constants
Exports 63 feature bits covering CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN0/1, MPM/MPIO, FCLK/SOC/LCLK/SHUB/DCF/ISP/IPU/GFX/VPE DPM, low-power DCN clocks, zstates/IOMMUL2 PG, deep-sleep clocks, whisper/SMU low power, GFX DEM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, DVO, CPPC/preferred cores, CLDO, ATHUB PG, VDDOFF/Zstates ECO, CC6, DS_UMCCLK/ISPCLK/HSPCLK/IPU/VPE, Smart L3, and PCC. `SMU_Firmware_Header`, `SMU14_Firmware_Footer`, `FwStatus_t`, and `FwStatus_t_v14_0_1` define packed firmware/status metadata.

## Control Flow
The feature bits drive PPSMC feature queries and controls. Firmware header/footer structs are parsed when validating or loading PMFW images, while status structs are read back from PMFW shared state.

## State And Persistence
Feature masks and status fields are runtime state. Firmware header/footer fields are persistent image metadata. Distinct status variants preserve ABI compatibility across v14.0.0 and v14.0.1.

## Dependencies And Integration
Includes `smu14_driver_if_v14_0_0.h` and pairs with v14 PPSMC headers. Integrates with firmware loading/validation, feature enablement, status reporting, media/display/IPU/VPE power, CPPC, and low-power state handling.

## Risks And Test Signals
Risks include using the wrong status struct for v14.0.1, feature bit comments that differ by subgeneration, and firmware image metadata mismatch. Test signals include firmware header parsing, enabled-feature readback, status table sanity, VCN/IPU/VPE power tests, CPPC/zstate/S0i3 behavior, and driver-if version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h -->
