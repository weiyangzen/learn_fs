# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_pp_interface.h

## Purpose
Defines the AMDGPU power-management and SMU interface contract. It exposes SMU IP block declarations, power/clock/fan/sensor enums, `amd_pm_funcs`, and versioned telemetry layouts used by hwmon, sysfs/debugfs, display core, XGMI/partition code, and user-visible GPU metrics paths.

## Important APIs, Types, and Functions
Extern IP blocks include `pp_smu_ip_block` and SMU v11 through v15 IP blocks. Policy enums cover forced DPM levels, PM states, VCE levels, fan modes, clock domains, PP sensors, PP tasks, SMC power profiles, overdrive commands, MP1 state, data-fabric C-state, power limit levels/types, XGMI PLPD, and PM policies. `struct amd_pm_funcs` is the central callback table for power transitions, fan PWM/RPM, clock forcing/printing, sensor reads, power limits, power profiles, overdrive, MP1 state, SMU I2C, display clock/voltage requests, watermarks, BACO, PP feature masks, XGMI pstate, GPU/temp/XCP/PM metrics, DPM tables, and RLC notification. Telemetry types include `metrics_table_header`, many `gpu_metrics_v1_*`, `gpu_metrics_v2_*`, `gpu_metrics_v3_0`, flexible attribute layouts, board/baseboard/partition metrics, and attribute encoding macros.

## Control Flow
The header has no implementations. Control flow is callback-driven: the active SMU/DPM backend installs `amd_pm_funcs`, and sysfs, hwmon, display, reset, and metrics code call through it. Metrics consumers inspect `common_header.structure_size`, `format_revision`, and `content_revision` before decoding revision-specific fields.

## State and Persistence
No global state is allocated here. The structs describe PM state stored elsewhere: fan mode, DPM/OD tables, power profiles, clock limits, SMU metrics buffers, XCP partition counters, energy accumulators, and board temperature sensors. Metrics snapshots include accumulated counters and firmware timestamps, so consumers must account for wrap and unit differences.

## Dependencies and Integration Points
The header forward-declares display and clock types and depends on AMDGPU core definitions supplied by includers. Integration points include SMU backend files, `amdgpu_pm.c`, hwmon/sysfs/debugfs, DC display clock negotiation, BACO/reset handling, XGMI controls, partition/XCP telemetry, and firmware metrics returned by SMU.

## Risks and Test Signals
High risks are metrics ABI/layout mistakes, unit mismatches across revisions, unchecked optional callbacks, and applying unsupported power/clock operations. Flexible-array metric formats require bounds checks. Test signals include build coverage across SMU generations, sysfs power profile/OD/fan operations, hwmon reads, display mode changes, GPU metrics decode by version, XGMI/partition metrics on multi-die parts, and reset/BACO flows.
