
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.c

## Purpose
Registers AMDGPU hardware performance-monitoring units with Linux perf for ASIC-specific Data Fabric and XGMI events. It exposes sysfs event/format descriptions under perf event sources and wires perf operations to AMDGPU DF counter callbacks.

## Important APIs, Types, and Functions
`struct amdgpu_pmu_event_attribute` describes one sysfs event/format attribute. `struct amdgpu_pmu_entry` tracks a registered PMU for one device/type. Static config tables define Vega20 and Arcturus events, formats, and event config types. Perf callbacks are `amdgpu_perf_event_init`, `amdgpu_perf_add`, `amdgpu_perf_del`, `amdgpu_perf_start`, `amdgpu_perf_stop`, and `amdgpu_perf_read`. Public lifecycle functions are `amdgpu_pmu_init` and `amdgpu_pmu_fini`.

## Control Flow
Initialization selects configs by ASIC. Vega20 registers both a DF-specific PMU and an aggregate `amdgpu_<minor>` PMU; Arcturus registers the aggregate PMU. Each entry allocates format/event attribute arrays, fills sysfs attribute groups, duplicates the group pointer list, registers with `perf_pmu_register`, and appends to a global list. Perf add decodes the config type, reserves a hardware counter via `df.funcs->pmc_start(..., add counter)`, optionally starts, then read/stop/del interact with `pmc_get_count` and `pmc_stop`.

## State and Persistence Behavior
Registered PMUs persist in the global `amdgpu_pmu_list` until device finalization. Counter index, previous count, current count, and config type live in each perf event's `hw_perf_event`. Attribute storage is dynamically allocated per PMU and freed on `amdgpu_pmu_fini`.

## Dependencies and Integration Points
Depends on Linux perf core, sysfs attribute groups, AMDGPU ASIC IDs, DRM minor index naming, and `adev->df.funcs` for hardware counter operations. User integration is via `perf stat -e` and `/sys/bus/event_source/devices/amdgpu*`.

## Risks and Test Signals
Risks include registering events without DF callbacks, leaking partially allocated attributes, event config type mismatches, counter exhaustion, and incorrect count deltas if hardware counters wrap unexpectedly. Test by inspecting sysfs event sources on Vega20/Arcturus, running perf on each event, forcing init failure paths, unloading the driver, and verifying no stale PMU entries remain.
