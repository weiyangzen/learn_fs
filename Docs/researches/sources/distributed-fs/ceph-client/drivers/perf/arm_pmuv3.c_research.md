# sources/distributed-fs/ceph-client/drivers/perf/arm_pmuv3.c

## Purpose
ARMv8/ARMv9 PMUv3 hardware driver. It supplies PMUv3 event maps, sysfs event/format/capability attributes, register accessors, overflow handling, event filtering, branch-record support, user-space counter read support, KVM coordination, PMUv3 feature probing, ACPI/DT driver registration, and mmap user page time/counter metadata.

## Important APIs, Types, And Functions
- `armv8_pmu_init()` installs the hardware callbacks into `struct arm_pmu`.
- `armv8pmu_probe_pmu()` and `__armv8pmu_probe_pmu()` read PMU version, PMCR counter count, PMCEID bitmaps, PMMIR, instruction counter support, and BRBE support.
- `armv8pmu_handle_irq()` clears overflow flags, stops the PMU, updates/reloads overflowing events, saves BRBE stacks when requested, and restarts the PMU.
- `armv8pmu_get_event_idx()` chooses the cycle counter, instruction counter, a single programmable counter, or a chained pair.
- `armv8pmu_set_event_filter()` encodes EL filters, guest/host filters, branch-stack validation, and threshold controls.
- `arch_perf_update_userpage()` exports rdpmc and arch timer conversion data to perf mmap pages.

## Control Flow
On DT, `armv8_pmu_driver_init()` registers a platform driver; on ACPI, it calls `arm_pmu_acpi_probe()`. Probe invokes common platform/ACPI code, then PMUv3 init probes hardware on a supported CPU, allocates per-CPU BRBE stacks if available, installs callbacks, and registers sysfs groups. Event init maps common architectural events if PMCEID advertises them, falls back to implementation-specific cache maps, rejects standalone chain events, and handles user-read constraints. Scheduling starts counters by programming event type, IRQ enable, KVM event masks, and counter enable registers.

## State And Persistence
Important runtime state is stored in `struct arm_pmu`: `pmuver`, `cntr_mask`, `pmceid_bitmap`, `pmceid_ext_bitmap`, `reg_pmmir`, BRBE metadata, and callback pointers. Global `sysctl_perf_user_access` controls user-space direct counter access and is exposed under `kernel/perf_user_access`. Hardware registers hold live counter configuration; no durable state exists.

## Dependencies And Integration Points
This file integrates Linux perf, PMUv3 sysregs from `asm/perf_event.h` and `linux/perf/arm_pmuv3.h`, KVM host/guest PMU hooks, BRBE (`arm_brbe.h`), arch timer/sched_clock user-page metadata, CPU feature helpers, ACPI/OF platform probing, lockup detector retry, and common `arm_pmu.c`.

## Risks
Counter selection has many architectural constraints: chained 64-bit counters require adjacent pairs, user-readable events cannot be chained, PMCCNTR is avoided for thresholds, branch stacks, and SMT, and PMICNTR is not exposed to userspace. User access must clear or restrict unused counters to avoid leaking data. Threshold and branch filters depend on feature registers. KVM deferred counters require correct host/guest synchronization. IRQ handling stops and restarts the whole PMU, so bugs can skew event groups.

## Test Signals
Run perf stat and perf record on PMUv3 systems, including raw events, common PMCEID-visible events, implementation cache events, 64-bit `long` events, user `rdpmc`, threshold formats, BRBE branch stacks, KVM guest/host filtered events, CPU hotplug, and heterogeneous PMUs. Inspect sysfs `events`, `format`, `caps`, `cpus`, and `kernel/perf_user_access` behavior.
