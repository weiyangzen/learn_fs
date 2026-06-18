<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h

## Purpose
This header defines the Arcturus SMU11 driver interface tables and constants shared between the Linux driver and PMFW. It specifies PPTable layout, feature bits, clock level counts, I2C command/request structures, power/thermal/voltage/DPM enums, metrics/config/debug/activity tables, table IDs used for SMU table transfer messages, and related ABI constants.

## Important APIs, Types, and Functions
- Version and sizing: `PPTABLE_ARCTURUS_SMU_VERSION`, `NUM_*_DPM_LEVELS`, max level macros, `NUM_FEATURES`, and XGMI level counts.
- Feature and throttler ABI: `FEATURE_*_BIT` and `FEATURE_*_MASK` for DPM, deep sleep, ULV, VCN, thermal, fan, OOB, Vmin; `THROTTLER_*` bits; workload bits; XGMI state values.
- I2C ABI: `I2cControllerConfig_t`, `SwI2cCmd_t`, `SwI2cRequest_t`, controller/port/name/throttler/protocol/speed/command enums.
- Main firmware tables: packed `PPTable_t`, `DriverSmuConfig_t`, `SmuMetrics_t`, `AvfsDebugTable_t`, `AvfsFuseOverride_t`, and `DpmActivityMonitorCoeffInt_t`.
- Table transfer IDs: `TABLE_PPTABLE`, `TABLE_AVFS`, `TABLE_PMSTATUSLOG`, `TABLE_SMU_METRICS`, `TABLE_DRIVER_SMU_CONFIG`, `TABLE_OVERDRIVE`, `TABLE_WAFL_XGMI_TOPOLOGY`, `TABLE_I2C_COMMANDS`, and `TABLE_ACTIVITY_MONITOR_COEFF`.

## Control Flow
The file is data layout rather than executable logic. The Arcturus SMU backend fills or reads these packed structures, stages them in driver BOs, and transfers them with PMFW table-transfer messages. During SMU setup, the PPTable provides feature enablement, infrastructure limits, DPM frequency tables, fan settings, AVFS curves, XGMI training data, board telemetry, spread spectrum, I2C controllers, memory channel masks, and MMHUB padding. Runtime metrics reads copy `SmuMetrics_t` from PMFW, and configuration/activity/I2C tables are transferred when backend operations request them.

## State and Persistence Behavior
The tables represent persistent firmware-visible state for the running device. `PPTable_t` is consumed by PMFW as board and policy configuration. `DriverSmuConfig_t` stores averaging time constants. `SmuMetrics_t` is a snapshot of current telemetry. I2C request structures carry bounded command batches. The file uses packed layout around the main PPTable so alignment and padding are part of the ABI. Many fields include units such as MHz, mV Q2, Celsius, Amps, Q16, and IEEE float stored in integer words.

## Dependencies and Integration Points
- Used by `arcturus_ppt` code and common SMU table transfer helpers.
- Integrates with `amdgpu_smu.h` table IDs, feature maps, workload maps, metrics conversion, power limit/fan/thermal/sysfs paths, I2C support, XGMI policy, and RAS bad page flows.
- The PMFW binary must use exactly the same structure sizes, field order, and table IDs.

## Risks
- Any structural edit requires interface-version coordination; changing field order, packing, padding, or array counts breaks PMFW table parsing.
- Several comments mark FIXME/pending spec areas; those fields should be treated as firmware ABI even if documentation is incomplete.
- Units are mixed and sometimes fixed point. Misinterpreting Q formats or MHz/kHz/Celsius units can create unsafe voltage, thermal, or fan behavior.
- Table IDs must match the message-layer `TransferTable*` command arguments; cross-ASIC reuse can upload the wrong table type.
- Feature bit positions differ from Navi10, so common feature maps must be ASIC-specific.

## Test Signals
- Compile Arcturus backend and verify expected `sizeof(PPTable_t)`, `sizeof(SmuMetrics_t)`, and table IDs against firmware headers.
- Run SMU initialization to confirm PPTable transfer, enabled feature mask retrieval, DPM table population, thermal/fan limits, XGMI policy, and metrics reads.
- Exercise I2C command table transfers and confirm command count bounds at `MAX_SW_I2C_COMMANDS`.
- Validate metrics conversion for clocks, fan, socket power, HBM temperature, throttler status, and energy accumulator.
- Negative ABI tests should detect changed packing, missing MMHUB padding, or feature bit renumbering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu11_driver_if_arcturus.h -->
