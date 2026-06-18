<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h

## Purpose
Defines the generic ARM PMU driver interface used by ARM and arm64 PMU implementations to integrate hardware counters with the Linux perf core.

## Important APIs, Types, And Functions
- `ARMPMU_MAX_HWEVENTS` is 32 on 32-bit ARM and 33 on arm64 to account for newer PMUv3 counters.
- ARM PMU event flags include `ARMPMU_EVT_64BIT`, `ARMPMU_EVT_47BIT`, and `ARMPMU_EVT_63BIT`, asserted to fit within `PERF_EVENT_FLAG_ARCH`.
- Mapping helpers include unsupported sentinel constants and `PERF_MAP_ALL_UNSUPPORTED`/`PERF_CACHE_MAP_ALL_UNSUPPORTED`.
- `struct pmu_hw_events` tracks active events, used counter bitmap, per-CPU PMU device ID, IRQ, branch stack, and branch-user count.
- `struct arm_pmu` embeds `struct pmu` and supplies callbacks for IRQ handling, enable/disable, event index allocation, filters, counter read/write, start/stop/reset, event mapping, PMUv3 mapping, plus CPU masks, platform device, per-CPU event state, CPU PM notifier, sysfs attr groups, PMUv3 metadata, and ACPI CPU ID.
- Public helpers include `armpmu_event_update()`, `armpmu_event_set_period()`, `armpmu_map_event()`, `arm_pmu_device_probe()`, `arm_pmu_acpi_probe()`, `kvm_host_pmu_init()`, `arm_pmu_irq_is_nmi()`, `armpmu_alloc()`, `armpmu_free()`, `armpmu_register()`, `armpmu_request_irq()`, and `armpmu_free_irq()`.
- PMU format macros generate sysfs format attributes and extract config fields.

## Control Flow
Platform or ACPI probe matches CPU/PMU information through `pmu_probe_info`, allocates `struct arm_pmu`, initializes callbacks and event maps, requests interrupts, and registers the PMU with perf. Perf core calls PMU callbacks to map events, allocate counters, program periods, start/stop counters, handle overflow IRQ/NMI, and update counts. Branch sampling and KVM host PMU setup attach through optional fields/callbacks.

## State And Persistence
State is split between the PMU object, supported CPU mask, per-CPU `pmu_hw_events`, active-event arrays, used counter bitmaps, PMUv3 capability bitmaps, IRQ assignments, and sysfs attribute groups. Counter values themselves live in hardware and are synchronized into perf event state.

## Dependencies And Integration Points
Depends on interrupts, perf core, platform devices, sysfs, CPU type detection, ACPI, KVM, and architecture PMU register implementations. It integrates with `/sys/devices/*/events` and `format` attributes, perf event scheduling, CPU PM notifications, and virtualization support.

## Risks And Edge Cases
Risks include wrong event mapping tables, counter width flag mismatch, unsupported cache events being exposed, counter index allocation races, per-CPU IRQ lifetime errors, heterogeneous CPU filtering mistakes, NMI versus IRQ handler assumptions, and PMUv3 common-event bitmap drift.

## Test Signals
Probe PMU via DT and ACPI, run `perf stat` hardware/cache events, sample overflow interrupts, validate sysfs events/format/caps, CPU hotplug and suspend/resume, branch-stack sampling, KVM host PMU initialization, heterogeneous CPU event filtering, and counter-width rollover tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmu.h -->
