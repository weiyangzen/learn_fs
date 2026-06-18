# sources/distributed-fs/ceph-client/drivers/perf/alibaba_uncore_drw_pmu.c

Purpose: Implements the Alibaba T-Head Yitian 710 DDR Sub-System Driveway uncore PMU. It exposes DDR subsystem events through perf, handles shared overflow IRQs, migrates PMU contexts on CPU hotplug, and binds ACPI IDs `BABA5000` and historical `ARMHD700`.

Important APIs and functions: `struct ali_drw_pmu` stores MMIO base, PMU, CPU affinity, event/counter arrays, used counter bitmap, and associated shared IRQ. `struct ali_drw_pmu_irq` tracks an IRQ shared by one or more PMU instances with refcount, CPU affinity, and RCU PMU list. Perf callbacks include `ali_drw_pmu_event_init()`, `add`, `del`, `start`, `stop`, and `read`. `ali_drw_pmu_isr()` handles common counter overflow status. Sysfs exposes event aliases, `format/event`, `cpumask`, and identifier.

Control flow: Probe maps MMIO, names the PMU from resource address, resets counters, enables common-counter overflow interrupts, clears status, initializes or reuses a shared IRQ object, then registers the PMU. Event init rejects sampling, task events, CPU-less events, and groups with more than one hardware event. Add allocates one of 16 common counters for non-cycle events; cycle events use a special 64-bit counter path. Start programs preload, event select, counter enable, and global start. IRQ handling disables active counters, reads overflow status, updates/reloads overflowed events, clears status, and re-enables non-stopped counters.

State and persistence: Hardware registers hold counter control, event select, preload, common counters, cycle counters, and overflow interrupt state. Software tracks used counters and event IDs per PMU. Shared IRQ objects persist while any PMU references them. CPU affinity is stored per IRQ and PMU and changes during hotplug migration.

Dependencies and integration points: Depends on ACPI platform probing, perf uncore PMU APIs, cpuhotplug multi-state, IRQ affinity hints, RCU lists, refcounts, and MMIO accessors. Integrates with `drivers/perf/Kconfig` and `Makefile` through `CONFIG_ALIBABA_UNCORE_DRW_PMU`.

Risks: The driver intentionally uses `IRQF_SHARED` due to an MPAM interrupt overlap, but notes that the PMU interrupt should not be shared. Cycle event handling uses `hw.idx = -1`, so code paths must avoid common-counter indexing for cycle events. Event init resets all PMU counters, which can disturb concurrent sessions if perf allowed them, hence the single-hardware-event group restriction is important. IRQ cleanup must respect RCU grace periods; list removal is RCU-style but object free relies on no concurrent handler after IRQ teardown/refcounting.

Test signals: ACPI probe for both IDs, event alias visibility, single event counting, cycle event counting, overflow interrupt updates, shared IRQ with multiple PMU instances, hotplug migration and affinity hint changes, rejection of sampling/task/grouped events, and remove disabling interrupts before unregister.
