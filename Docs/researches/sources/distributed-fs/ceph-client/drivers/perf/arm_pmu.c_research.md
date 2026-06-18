# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu.c

## Purpose
Common ARM CPU PMU perf core. It provides the `struct pmu` callbacks shared by ARMv5/v6/v7/v8 CPU PMU implementations, including event initialization, counter allocation validation, start/stop/read/add/delete handling, counter period accounting, IRQ/NMI request/free, CPU hotplug reset, and CPU power-management save/restore.

## Important APIs, Types, And Functions
- `armpmu_alloc()`, `armpmu_free()`, and `armpmu_register()` allocate `struct arm_pmu`, per-CPU `struct pmu_hw_events`, install common PMU callbacks, register CPU hotplug and CPU PM notifiers, then call `perf_pmu_register()`.
- `armpmu_map_event()` maps perf hardware, cache, raw, and PMU-specific event encodings through architecture-specific maps.
- `armpmu_event_set_period()` and `armpmu_event_update()` are the central counter accounting helpers used by all CPU PMU IRQ handlers.
- `armpmu_add()`, `armpmu_del()`, `armpmu_start()`, `armpmu_stop()`, and `armpmu_read()` implement the perf event lifecycle.
- `armpmu_request_irq()` and `armpmu_free_irq()` select normal IRQ, NMI, percpu IRQ, or percpu NMI operations through `struct pmu_irq_ops`.
- `arm_perf_starting_cpu()` and `arm_perf_teardown_cpu()` are CPUHP callbacks; `cpu_pm_pmu_notify()` handles CPU low-power entry and exit.

## Control Flow
Architecture drivers call `armpmu_alloc()`, fill hardware callbacks and supported CPU/counter masks, request IRQs, then call `armpmu_register()`. Perf opens call `armpmu_event_init()`, which rejects unsupported CPUs and branch-stack requests without BRBE, maps the event, installs filters, and validates groups against a fake PMU allocation. Scheduling calls `armpmu_add()`, which allocates an index with the hardware-specific `get_event_idx()` and optionally starts the event. IRQ delivery enters `armpmu_dispatch_irq()`, dereferences the per-CPU `arm_pmu *`, invokes the hardware handler, and reports handler latency to perf.

## State And Persistence
Runtime state is per CPU in `pmu->hw_events`: active events, used counter bitmap, IRQ number, branch-stack users, and per-CPU back-pointers. Global static state tracks requested IRQs (`cpu_irq`, `cpu_irq_ops`) and whether any PMU uses NMIs (`has_nmi`). No durable storage exists; all state is reconstructed on probe and hotplug. Counter values persist only in perf event atomics and hardware registers.

## Dependencies And Integration Points
This file depends on Linux perf core, CPU hotplug, CPU PM, IRQ/NMI APIs, KVM PMU host hooks, cpumask/topology helpers, and architecture-specific callbacks installed by files such as `arm_pmuv3.c`, `arm_v7_pmu.c`, `arm_v6_pmu.c`, and `arm_xscale_pmu.c`. The sysfs `cpus` attribute exposes supported CPUs for heterogeneous systems.

## Risks
IRQ handling is delicate: shared PPIs must only be freed when the last CPU user is gone, and NMI fallback must match the free/disable operation. Period programming intentionally caps periods to half counter width to reduce missed wraps, but extreme IRQ latency can still affect counts. CPU PM and hotplug reset paths must run on supported CPUs or stale PMU registers may corrupt subsequent samples. Group validation uses a fake bitmap and depends on architecture-specific `get_event_idx()` behavior being side-effect-free except for the passed bitmap.

## Test Signals
Useful signals include boot logs showing `enabled with ... PMU driver`, `/sys/bus/event_source/devices/<pmu>/cpus`, perf stat/counting on each supported CPU, sampling overflow delivery, CPU hotplug cycles, suspend/resume or CPU idle transitions with active events, heterogeneous CPU rejection tests, and IRQ/NMI registration failures.
