<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h

## Purpose

`smu_v14_0.h` declares the shared SMU14 generation interface. It mirrors the SMU13/15 common lifecycle contract with SMU14 register constants, DPM and power contexts, PCIe decode helpers, and function prototypes for microcode, SMC tables, power, PPTable, DPM, BACO, media, thermal, and OD behavior.

## Important APIs, Types, and Functions

Important constants include `FEATURE_MASK`, MP aperture bases, SMU14 firmware flag registers, `MAX_PCIE_CONF`, `SMU14_TOOL_SIZE`, CTF offsets, `DECODE_GEN_SPEED`, `DECODE_LANE_WIDTH`, and `SMU_V14_SOFT_FREQ_ROUND`. Types include `smu_14_0_max_sustainable_clocks`, `smu_14_0_dpm_tables`, `smu_14_0_dpm_context`, `smu_14_0_power_state`, and `smu_14_0_power_context`. Prototypes cover init/load/fini microcode, SMC tables, power, firmware status, PPTable setup/retrieval, boot values, table locations, feature control, display notification, power limits, GFXOFF, IRQ, BACO, DPM frequency limits, performance level, power source, media enablement, BTC, GPO/deep sleep, IMU power-up, default DPM tables, OD editing, and thermal alerts.

## Control Flow

The header contains declarations only. SMU14 platform implementations install hooks in `pptable_funcs` and delegate common operations to these functions through AMDGPU PM core calls.

## State and Persistence Behavior

DPM context persists clock tables, workload policy mask, and deep-sleep DCEF clock. Power context persists power source, boost mode, and power state. Firmware/device state changes occur in the implementation files, not in the header.

## Dependencies

It includes `amdgpu_smu.h`, depends on external decode arrays `decoded_link_speed`/`decoded_link_width`, and is gated by `SWSMU_CODE_LAYER_L2`/`L3` for prototypes.

## Integration Points

SMU14 platform files, especially `smu14/smu_v14_0_2_ppt.c` and common `smu_v14_0.c`, use this header to connect PMFW, PPTable, sysfs, hwmon, reset, and display/media power-management paths.

## Risks and Edge Cases

`FEATURE_MASK` is also defined in nearby generation headers; include order should avoid macro redefinition surprises. Decode macros assume valid indexes. Unsupported hooks must be omitted or guarded for specific SMU14 ASICs.

## Test Signals

Build SMU14 PM, probe firmware, parse/retrieve PPTable, exercise DPM sysfs, power-limit and OD paths, media power toggles, BACO/reset, and thermal alert enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v14_0.h -->
