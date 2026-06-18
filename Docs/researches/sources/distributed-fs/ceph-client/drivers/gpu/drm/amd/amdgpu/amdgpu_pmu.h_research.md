
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_pmu.h

## Purpose
Defines the small public interface and event-type encoding for AMDGPU perf PMUs.

## Important APIs, Types, and Functions
`enum amdgpu_pmu_perf_type` distinguishes no PMU, DF-only PMU, and aggregate PMU. `enum amdgpu_pmu_event_config_type` identifies config-encoded event families such as DF and XGMI. `AMDGPU_PMU_EVENT_CONFIG_TYPE_SHIFT` and `AMDGPU_PMU_EVENT_CONFIG_TYPE_MASK` define where the type field lives in `perf_event_attr.config`. Public functions are `amdgpu_pmu_init` and `amdgpu_pmu_fini`.

## Control Flow
PMU implementation code reads these enum values when registering PMUs and when decoding perf event config into `hw_perf_event.config_base`.

## State and Persistence Behavior
No storage is declared here. It defines ABI-like constants used by sysfs event descriptions and perf event parsing.

## Dependencies and Integration Points
Integrated with Linux perf event config encoding, the AMDGPU device lifecycle, and DF/XGMI counter code. Any new event type must be reflected in the enum and the PMU implementation tables.

## Risks and Test Signals
Risks are ABI drift between sysfs event strings and config decoding, especially if the shift/mask changes. Test by reading generated sysfs events and verifying raw perf configs decode to the intended counter family.
