<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h

## Purpose
Defines SMU v15.0.0 PMFW feature bits, firmware image metadata, and firmware status layout.

## Important APIs, Types, And Constants
Includes `smu15_driver_if_v15_0_0.h` and exports 64 feature bits. Domains include CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN, MPM/MPIO, FCLK/SOC/LCLK/SHUB/DCF/ISP/NPU/GFX/VPE/DACCCLK DPM, deep-sleep clocks, low-power DCN clocks, VRHOT/Z8/PCC/SPM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, CPPC/preferred cores, ATHUB/MMHUB PG, VDDOFF ECO, SC/FP DIDT, CC6, P3T, DS_NPUCLK/DS_VPECLK, and `NUM_FEATURES 64`. `SMU_Firmware_Header`, `SMU_Firmware_Footer`, and `FwStatus_t` define firmware/status metadata.

## Control Flow
Feature bits are consumed by PPSMC feature queries and controls. Firmware image metadata is parsed during PMFW load/validation, and `FwStatus_t` is read as a runtime firmware status table.

## State And Persistence
Feature masks and status fields are volatile firmware state. Firmware header/footer values are persistent image metadata and part of the loader contract.

## Dependencies And Integration
Pairs with `smu15_driver_if_v15_0_0.h` and `smu_v15_0_0_ppsmc.h`. Integrates with NPU/VPE/DACCCLK/ISP/media/display power management, CPPC, low-power states, firmware loading, and SMU status/feature reporting.

## Risks And Test Signals
Risks include feature-bit mismatch with v14/v13, firmware metadata parsing mismatch, and incomplete handling of new NPU/VPE/DACCCLK bits. Test signals include firmware load/header checks, driver-if version, enabled-feature readback, NPU/VPE/VCN/JPEG power transitions, status table sanity, and low-power-state testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h -->
