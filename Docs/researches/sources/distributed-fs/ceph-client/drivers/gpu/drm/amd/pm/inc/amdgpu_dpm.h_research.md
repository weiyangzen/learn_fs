# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm.h

### Purpose
`amdgpu_dpm.h` is the central AMDGPU dynamic power-management interface header. It defines shared PM/DPM state structures and declares the public DPM wrapper functions used by sysfs, hwmon, display, reset, media, RAS, virtualization, and ASIC power-management code. It is the contract between common AMDGPU code and the underlying PowerPlay/SMU implementations.

### Important APIs, Types, And Functions
The header defines PM mode and capability enums such as `enum gfx_change_state`, `enum amdgpu_int_thermal_type`, `enum amdgpu_runpm_mode`, `enum ip_power_state`, and BACO/MACO support bits. Core data types include `struct amdgpu_ps`, `struct amdgpu_dpm_thermal`, clock/voltage dependency tables, leakage and phase-shedding tables, UVD/VCE dependency tables, `struct amdgpu_ppm_table`, `struct amdgpu_cac_tdp_table`, `struct amdgpu_dpm_dynamic_state`, `struct amdgpu_dpm_fan`, `struct amdgpu_dpm`, `struct amdgpu_smu_i2c_bus`, `struct config_table_setting`, and `struct amdgpu_pm`.

The function declarations cover sensor reads, APU thermal caps, SMU power/clock gating, SCLK/MCLK queries, XGMI and power profiles, BACO/mode/link resets, MP1 state changes, DF C-state, multi-GPU fan boost, SMU I2C access, ACPI PM events, media and JPEG/VPE enablement, SMU firmware loading, passthrough SBR, HBM bad page/channel reporting, RMA reason reporting, frequency ranges, watermarks, SMU events, GFXOFF residency and status, thermal throttling counters, ECC info, current and forced power states, PowerPlay table get/set, overdrive editing, clock-level printing/emission, PP feature masks, fan controls, power limits, metrics, display configuration, display clocks, UCLK DPM states, PM policies, SDMA/VCN reset support, temperature metrics support, and RAS SMU driver lookup.

### Control Flow
This header does not implement control flow, but it shapes common call flow. Higher layers keep state in `adev->pm`, call these `amdgpu_dpm_*()` functions with an `amdgpu_device`, and the implementation dispatches to the active PM backend. Typical flows include sysfs/hwmon reading sensors through `amdgpu_dpm_read_sensor()`, display code updating clocks and watermarks through display-configuration functions, reset paths checking and invoking BACO or mode/link resets, and overdrive paths printing clock levels, editing DPM tables, then dispatching a readjust task.

### State, Persistence, And Dependencies
`struct amdgpu_pm` is persistent per-device state. It contains mutexes, current/default clocks, I2C and EEPROM adapters, hwmon device pointer, fan metadata, DPM enablement and firmware data, display configuration, SMU private buffer, power-feature masks, per-IP power states, debug masks, stable pstate context, runtime PM mode, OD kobject list, and OD feature mask. `struct amdgpu_dpm` persists legacy PowerPlay power states, requested/current/boot/video states, platform capabilities, dynamic dependency tables, fan and thermal state, power-control limits, activity flags, and forced-level state. The many dependency table pointers require backend allocation/free discipline outside this header.

Dependencies include AMDGPU device/core types, DRM display PM types, I2C adapters, firmware and buffer objects, RAS SMU types, SMU event and temperature metric enums, PowerPlay clock/profile/sensor enums, VCE state types, and kernel synchronization primitives.

### Integration Points
The declarations are consumed by `amdgpu_pm.c`, display/DC integration, reset and runtime power management, media IP block power control, RAS/error-reporting paths, virtualization support, and ASIC-specific SMU managers. The `struct amdgpu_pm` layout is embedded in `struct amdgpu_device`, so changes affect broad driver initialization, suspend/resume, and teardown paths.

### Risks
Because this is a broad cross-module contract, layout or semantic changes can break multiple ASIC backends. Pointer-owning tables in `struct amdgpu_dpm_dynamic_state` and firmware/private-buffer fields require clear ownership outside the type definition. Many functions return `-EOPNOTSUPP` as feature probes; callers rely on consistent behavior to expose or hide user interfaces. `struct amdgpu_pm` mixes locks, kobjects, I2C buses, runtime mode, and firmware state, so initialization and teardown order matters. Adding new OD feature bits requires matching visibility and handler logic in `amdgpu_pm.c`.

### Test Signals
Compile coverage across enabled/disabled ASIC families is the first signal because this header fans out widely. Runtime signals include sysfs/hwmon capability probing, suspend/resume and runtime-PM transitions, BACO/mode reset paths, display clock changes, fan and power-limit controls, metrics retrieval, SMU I2C bus arbitration, RAS/ECC paths, and virtualization mode behavior. Static analysis should watch for uninitialized fields in `struct amdgpu_pm` and stale backend implementations after prototype changes.
