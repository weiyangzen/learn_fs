<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h

## Purpose

`smu_v15_0.h` declares the shared SMU15 generation interface. It defines SMU15 driver-interface version constants, MP aperture/register constants, DPM/power contexts including GL2 clock support, and prototypes for common SMU15 microcode, SMC table, PPTable, DPM, power, BACO, media, OD, and thermal operations.

## Important APIs, Types, and Functions

Key constants include `SMU15_DRIVER_IF_VERSION_INV`, `SMU15_DRIVER_IF_VERSION_SMU_V15_0`, `SMU15_DRIVER_IF_VERSION_SMU_V15_0_8`, `FEATURE_MASK`, MP aperture bases, `smnMP1_FIRMWARE_FLAGS`, `smnMP1_PUB_CTRL`, `MAX_PCIE_CONF`, `SMU15_TOOL_SIZE`, CTF offsets, and decode macros. Types include `smu_15_0_max_sustainable_clocks`, `smu_15_0_dpm_tables` with `gl2_table`, `smu_15_0_dpm_context` with `caps` and `board_volt`, `smu_15_0_power_state`, and `smu_15_0_power_context` with atomic throttle status. Prototypes mirror SMU14 plus SMU15-specific PPTable retrieval and OD editing.

## Control Flow

No implementation lives here. SMU15 platform code installs `pptable_funcs`, initializes message maps, loads firmware, creates SMC/driver tables, sets DRAM table locations, exchanges PMFW tables, enables features, and services user-facing PM operations through these declared helpers.

## State and Persistence Behavior

The DPM context persists per-clock tables, workload mask, deep-sleep DCEF clock, caps, and board voltage. Power context persists power source, boost mode, power state, and throttle status. Firmware state is modified by implementations through SMC messages and table transfers.

## Dependencies

It includes `amdgpu_smu.h`, relies on common SMU infrastructure, and pairs with SMU15 PMFW/PPSMC headers such as `smu_v15_0_8_pmfw.h` and `smu_v15_0_8_ppsmc.h`. The duplicate `FEATURE_MASK` definition is harmless only if identical.

## Integration Points

`smu15/smu_v15_0.c` and `smu15/smu_v15_0_8_ppt.c` use this header to connect PMFW protocol, GPU metrics, clock/thermal/power sysfs, reset, media, and table-management paths.

## Risks and Edge Cases

Driver-interface versions must match PMFW expectations. `enum smu_15_0_power_state` uses lowercase enum constants unlike earlier headers, so copy/paste assumptions can break builds. GL2 clock handling requires callers to include the new table and map entries. As with other generations, unsupported hooks need platform guards.

## Test Signals

Build SMU15 code, probe SMU15.0.8 firmware, verify driver-interface version checks, table address setup, metrics/static/system table transfers, DPM/sysfs behavior including GL2, power-limit changes, reset/BACO, and thermal alerts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v15_0.h -->
