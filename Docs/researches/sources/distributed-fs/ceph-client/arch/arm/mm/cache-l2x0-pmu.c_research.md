# sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0-pmu.c

Purpose: exposes L220/PL310 L2 cache controller performance counters as a Linux perf PMU using polling because the counters saturate rather than wrap.

Important APIs/types/functions: key state includes `l2x0_base`, `l2x0_pmu`, `pmu_cpu`, `l2x0_name`, `l2x0_pmu_poll_period`, `l2x0_pmu_hrtimer`, and `events[2]`. Important functions include counter MMIO helpers, `l2x0_pmu_event_read`, `l2x0_pmu_event_configure`, `l2x0_pmu_poll`, event start/stop/add/del/init callbacks, group validation, sysfs event attribute handling, `l2x0_pmu_reset`, CPU hotplug migration, `l2x0_pmu_suspend`, `l2x0_pmu_resume`, `l2x0_pmu_register`, and `l2x0_pmu_init`.

Control flow: `l2x0_pmu_register` is called by L2x0 cache initialization to stash MMIO base and choose PMU name from cache part. Later `device_initcall` allocates/registers a `struct pmu`, resets counters, starts CPU hotplug tracking, and registers with perf. Event add allocates one of two counters and starts the hrtimer if it is the first active event. The timer disables counters, reads and resets active events, re-enables counting, and forwards itself.

State and persistence: active perf events are stored in `events`; counter previous values are in each event's `hw.prev_count`; `pmu_cpu` tracks the CPU owning the pinned timer/context. PMU registration and sysfs attributes persist while the kernel runs.

Dependencies and integration points: depends on `CONFIG_PERF_EVENTS`, L2X0 MMIO register definitions, perf core, hrtimer, CPU hotplug, and `cache-l2x0.c` calling `l2x0_pmu_register`.

Risks: counters saturate at `0xffffffff`, so long poll periods lose event counts; the driver warns but cannot recover lost deltas. Only two counters are available, so event groups must be constrained. CPU hotplug migration must keep the pinned hrtimer and perf context on an online CPU. Sampling and task-attached events are rejected because this is a shared uncore-style PMU.

Test signals: perf list should show `l2c_220` or `l2c_310` events, PL310-only events should be hidden on L220, two-counter group constraints should be enforced, CPU hotplug should migrate `cpumask`, suspend/resume should stop and reload events, and stress tests should check saturation warnings.
