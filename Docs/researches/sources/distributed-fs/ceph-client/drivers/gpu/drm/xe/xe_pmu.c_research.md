<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c

## Purpose

`xe_pmu.c` registers a perf PMU for Xe devices and exposes GT residency/frequency plus engine activity counters through sysfs and perf events.

## Important APIs and Functions

The public API is `xe_pmu_register(struct xe_pmu *pmu)`, with cleanup through a devm action. Event config fields encode GT, SR-IOV function, engine class, engine instance, and event ID. Event IDs cover GT C6 residency, engine active ticks, engine total ticks, GT actual frequency, and GT requested frequency. The perf callbacks are `xe_pmu_event_init()`, add/del/start/stop/read helpers, and `xe_pmu_event_destroy()`. Helpers validate params, resolve GTs and hardware engines, acquire/release forcewake where needed, and read GuC PC or GuC engine-activity counters.

## Control Flow and State

Registration skips SR-IOV VFs, creates a PMU name from the DRM device name, installs format/events attribute groups, computes supported event bits, registers with perf, and marks `pmu->registered`. Event init rejects unsupported sampling/modes, invalid CPUs, unknown event IDs, bad GT/engine/function parameters, branch stacks, or unsupported events. Parentless events hold a DRM device reference, a runtime PM reference, and sometimes a forcewake reference stored in `event->pmu_private`. Reads update `hw.prev_count` and `event->count`; frequency events add instantaneous values rather than deltas.

## Dependencies and Integration Points

It integrates Linux perf PMU APIs, sysfs attributes, DRM device lifetime, runtime PM, forcewake, GT idle residency, GuC PC frequency, GuC engine activity, hardware engine lookup, and SR-IOV PF total-VF accounting.

## Risks and Test Signals

Forcewake allocation and release must balance across event lifetime. Frequency events are not monotonic counters and intentionally use different accumulation semantics. Event visibility currently checks support against GT 0, so multi-GT support must stay consistent. Tests should cover sysfs format/event files, invalid config rejection, reserved engine rejection, SR-IOV PF function bounds, VF no-registration path, runtime PM/DRM refs on event init/destroy, forcewake failure cleanup, event stop with update, unregister while events exist, and perf stat readings for all supported counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pmu.c -->
