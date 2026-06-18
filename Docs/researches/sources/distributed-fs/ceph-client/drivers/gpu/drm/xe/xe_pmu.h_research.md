<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h

## Purpose

`xe_pmu.h` declares the Xe perf PMU registration interface.

## Important APIs

When `CONFIG_PERF_EVENTS` is enabled, `xe_pmu_register(struct xe_pmu *pmu)` registers the device PMU. Otherwise an inline stub returns 0, allowing the rest of the driver to compile without perf support.

## Control Flow and State

The header has no runtime state. The implementation fills `struct xe_pmu` and registers/unregisters with perf core.

## Dependencies and Integration Points

It includes `xe_pmu_types.h` and is consumed by device initialization.

## Risks and Test Signals

The stub means feature code must not assume PMU sysfs exists when perf is disabled. Build tests should cover both perf-enabled and perf-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.h -->
