<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h

## Purpose

`smu_v11_0.h` declares the common SMU11 support layer used by SMU11 platform PPT files. It provides MP aperture/register constants, thermal defaults, DPM/power context structures, and prototypes for the shared SMU11 lifecycle, table, power, clock, fan, BACO, reset, and interrupt helpers.

## Important APIs, Types, and Functions

Important constants include MP0/MP1 aperture bases, `smnMP1_FIRMWARE_FLAGS`, `smnMP0_FW_INTF`, `smnMP1_PUB_CTRL`, `TEMP_RANGE_*`, `SMU11_TOOL_SIZE`, PCIe link limits, CTF offsets, and the `link_width` decode table. Types include `smu_11_0_max_sustainable_clocks`, `smu_11_0_dpm_tables`, `smu_11_0_dpm_context`, `smu_11_0_power_state`, `smu_11_0_power_context`, and `smu_11_5_power_context`. Prototypes cover microcode load/fini, SMC table init/fini, power init/fini, firmware status, PPT setup, boot values, table address notification, feature control, DPM table queries, power limits, thermal alerts, fan control, XGMI, GFXOFF, BACO, mode1 reset, soft/hard frequency ranges, PCIe queries, deep sleep, passthrough SBR, user OD restore, and message-control initialization.

## Control Flow

There is no implementation in the header. Platform files install `pptable_funcs` and delegate common steps to these functions: initialize microcode, allocate/init SMU tables, parse VBIOS powerplay data, program table locations, enable features, service sysfs/hwmon requests, send SMC messages, and handle interrupts/reset/suspend paths.

## State and Persistence Behavior

The structures define persistent driver-side state stored under `smu_context`: cached DPM tables, workload policy mask, deep-sleep DCEF clock, power source, power state, boost mode, and fast PPT limits for SMU11.5. Firmware/device state is changed by the declared functions but not stored in this header.

## Dependencies

It includes `amdgpu_smu.h` and is gated by `SWSMU_CODE_LAYER_L2`/`L3` for function prototypes. Consumers depend on SMU11 PMFW headers, PPTable layouts, SOC15 register helpers, and common SMU message/table infrastructure.

## Integration Points

`smu11/arcturus_ppt.c`, `navi10_ppt.c`, `sienna_cichlid_ppt.c`, `vangogh_ppt.c`, `cyan_skillfish_ppt.c`, and `smu_v11_0.c` use this header as the shared generation layer. It is the bridge between AMDGPU PM core and ASIC-specific platform code.

## Risks and Edge Cases

The header declares broad behavior across several ASICs, but not every helper is valid for every platform. Platform `pptable_funcs` must set unsupported hooks to `NULL` or provide guards. DPM table and PCIe bounds must match firmware table sizes. Thermal constants are defaults and must be overwritten from PPTable limits where available.

## Test Signals

SMU11 platform build coverage, boot probe on each SMU11 ASIC, sysfs clock/fan/power tests, BACO/reset/suspend-resume tests, and firmware-version compatibility checks validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v11_0.h -->
