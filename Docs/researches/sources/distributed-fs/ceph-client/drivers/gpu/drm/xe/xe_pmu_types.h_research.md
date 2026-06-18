<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h

## Purpose

`xe_pmu_types.h` defines the per-device state used by Xe's perf PMU integration.

## Important APIs and Types

`XE_PMU_MAX_GT` is fixed at 2 and checked against `XE_MAX_GT_PER_TILE` in the implementation. `struct xe_pmu` embeds `struct pmu base`, a `registered` flag, registered PMU `name`, and a `supported_events` bitmap indexed by event ID.

## Control Flow and State

The structure is stored in `struct xe_device`. `registered` gates event init/read behavior and avoids double unregister. `supported_events` controls sysfs visibility and event validation.

## Dependencies and Integration Points

It includes Linux perf and spinlock type headers. It is used by `xe_pmu.c` and device lifetime code.

## Risks and Test Signals

The GT maximum must match driver topology assumptions. Tests should verify event bit population on devices with and without GuC PC or engine activity support and confirm unregister clears `registered` before perf teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu_types.h -->
