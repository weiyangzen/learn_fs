<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h

## Purpose

`smu_v12_0.h` declares the compact shared SMU12 generation interface. It provides MP aperture constants and prototypes for firmware status, power-gating, GFXOFF/CGPG control, default DPM table setup, mode2 reset, soft frequency range, driver table location, VBIOS boot values, and message-control initialization.

## Important APIs, Types, and Functions

The exported prototypes are `smu_v12_0_check_fw_status`, `powergate_sdma`, `powergate_vcn`, `powergate_jpeg`, `set_gfx_cgpg`, `get_gfxoff_status`, `gfx_off_control`, `fini_smc_tables`, `set_default_dpm_tables`, `mode2_reset`, `set_soft_freq_limited_range`, `set_driver_table_location`, `get_vbios_bootup_values`, and `init_msg_ctl`.

## Control Flow

The header contains no implementation. SMU12 platform code installs a PPT function table and delegates common lifecycle and power-gating actions to the declared helpers. Message-control initialization wires generic messages to the platform's PMFW IDs.

## State and Persistence Behavior

No local state is defined. The functions mutate firmware/device state: media and SDMA power gates, GFXOFF/CGPG state, DPM limits, table addresses, and reset state. Driver-side SMU context stores any resulting cached state.

## Dependencies

It includes `amdgpu_smu.h` and exposes prototypes only for `SWSMU_CODE_LAYER_L2`/`L3` builds. Consumers need common SMU infrastructure and the appropriate SMU12 PMFW/PPSMC headers.

## Integration Points

This is the generation layer between SMU12 platform PPT files and AMDGPU PM core. Common hooks are used by sysfs/hwmon requests, suspend/resume, reset paths, and media power-management code.

## Risks and Edge Cases

The smaller SMU12 API surface means callers should not assume SMU11/13 helpers exist. Power-gating and reset calls must be serialized through PM mutexes where required by the implementation. Soft frequency limits are meaningful only for clock types supported by the platform message map.

## Test Signals

SMU12 platform build, boot firmware-status check, SDMA/VCN/JPEG power-gate toggles, GFXOFF status transitions, mode2 reset, and sysfs frequency-limit tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/smu_v12_0.h -->
