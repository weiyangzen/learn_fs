# sources/distributed-fs/ceph-client/arch/sh/kernel/perf_event.c

Purpose: adapts SH hardware performance counters to Linux perf PMU operations.

Important APIs and control flow: per-CPU `cpu_hw_events` tracks assigned events and used/active masks. `__hw_perf_event_init()` reserves PMU hardware for the first event, maps raw/cache/generic hardware events through `sh_pmu`, sets `event->destroy`, and stores hardware config. `sh_perf_event_update()` reads a raw counter, atomically swaps `prev_count`, computes delta, and adds to perf count. PMU ops add/delete/start/stop/read events, manipulating per-CPU slots and `sh_pmu` enable/disable callbacks. `register_sh_pmu()` installs a platform PMU, marks no-interrupt capability, registers `"cpu"` PMU, and sets a CPU hotplug prepare state.

State, dependencies, and risks: state includes global `sh_pmu`, `num_events`, reservation mutex, and per-CPU masks/events. Dependencies include platform `struct sh_pmu` callbacks/event maps, perf core, CPU hotplug, and hardware counters without overflow interrupts. Risks include sampling limitations, counter wrap width assumptions (`shift` remains zero), event slot conflicts, and incomplete reserve/release stubs. Test signals are `perf stat` raw/hardware/cache events, CPU hotplug reset, concurrent events up to `MAX_HWEVENTS`, and no sampling expectation.
