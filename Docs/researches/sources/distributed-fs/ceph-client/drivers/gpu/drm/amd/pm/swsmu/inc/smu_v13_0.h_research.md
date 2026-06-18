<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h

## Purpose

`smu_v13_0.h` declares the shared SMU13 generation interface. It extends the SMU11-style contract with SMU13 firmware flag addresses, Q10 conversion helpers, PCIe decode arrays, DPM/power contexts with capability and board-voltage fields, and prototypes for common lifecycle, table, power, fan, media, BACO, reset, WBRF, UCLK shadow, and interrupt work.

## Important APIs, Types, and Functions

Important constants include MP aperture bases, firmware flag registers, `SMU13_TOOL_SIZE`, `MAX_PCIE_CONF`, CTF offsets, `SMU_13_VCLK_SHIFT`, `SMUQ10_*` helpers, and `SMU_V13_SOFT_FREQ_ROUND`. Types include `smu_13_0_max_sustainable_clocks`, `smu_13_0_dpm_tables`, `smu_13_0_dpm_context`, `smu_13_0_power_state`, and `smu_13_0_power_context` with `atomic_t throttle_status`. Prototypes cover microcode, SMC tables, power, PPTable setup, boot values, table locations, feature control, power limits, thermal alerts, VDD/fan control, XGMI, GFXOFF, BACO, DPM queries, VCN/JPEG, BTC, GPO, deep sleep, IMU power-up, OD editing, mode1 reset, firmware PPTable retrieval, PCIe parameter update, PMFW-state disable, UCLK shadow, WBRF exclusion ranges, boot frequency queries, interrupt work, and custom level reset.

## Control Flow

The header defines no code flow. Platform files in `smu13/` install their function tables and delegate common operations to these helpers. A typical probe path initializes microcode, SMC tables, power contexts, parses or retrieves PPTable data, sets table addresses, enables features, populates DPM tables, and exposes sysfs/hwmon operations.

## State and Persistence Behavior

SMU13 DPM context persists DPM tables, workload policy, deep-sleep DCEF clock, capability bits, and board voltage. Power context persists power source, boost mode, power state, and atomic throttle state. Firmware state is changed through the declared helpers and reflected in metrics or cached tables.

## Dependencies

It includes `amdgpu_smu.h` and depends on common SMU mapping/message infrastructure plus platform-specific PMFW/PPSMC/PPTable headers. Decode macros rely on external arrays `pmfw_decoded_link_speed` and `pmfw_decoded_link_width`.

## Integration Points

`smu13/aldebaran_ppt.c`, `smu_v13_0_0_ppt.c`, `smu_v13_0_7_ppt.c`, and common `smu_v13_0.c` use this header. It integrates with sysfs clocks, fan/hwmon, BACO, reset, WBRF radio-frequency exclusion, display/media power, and GPU metrics.

## Risks and Edge Cases

Array-indexed link decode must validate firmware indexes. Q10 conversions can lose precision if callers mix fixed-point and integer units. The API spans dGPU and APU variants; unsupported hooks must be guarded. Atomic throttle state requires consistent update/read semantics across interrupt and sysfs contexts.

## Test Signals

SMU13 platform builds, probe and firmware-version checks, PPTable parsing/retrieval, DPM sysfs, media power toggles, mode1 reset, UCLK shadow, WBRF exclusion, thermal alert, and GPU metrics validation provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v13_0.h -->
