# sources/distributed-fs/ceph-client/drivers/perf/thunderx2_pmu.c

Purpose: Cavium/Marvell ThunderX2 ACPI uncore PMU driver for socket-local L3C, DMC, and CCPI2 units. It exposes each discovered uncore block as a perf PMU with event aliases and cpumask pinning.

Important APIs, types, and functions: `struct tx2_uncore_pmu` holds PMU identity, node/CPU, MMIO base, active counter bitmap, event slots, hrtimer, attribute groups, and type-specific callbacks for counter base initialization, start, and stop. Discovery uses `get_tx2_pmu_type`, `tx2_uncore_pmu_init_dev`, and `tx2_uncore_pmu_add`. Perf callbacks are `tx2_uncore_event_init`, `add`, `del`, `start`, `stop`, `read`; periodic 32-bit maintenance is `tx2_hrtimer_callback`.

Control flow: module init registers a multi-instance CPU hotplug state and platform driver. Probe requires ACPI, sets NUMA node, and walks child ACPI devices one level below `CAV901C`, accepting `CAV901D` L3C, `CAV901F` DMC, and `CAV901E` CCPI2. Each PMU maps its `_CRS` MMIO resource, sets type-specific limits and sysfs groups, selects an online CPU from the same node, registers perf, adds hotplug instance, and joins a global list. Event init rejects sampling, task attach, CPU-less events, invalid event IDs, and overlarge groups. Add allocates counters and computes register bases; start programs event controls and starts an hrtimer for 32-bit L3C/DMC only.

State and persistence: runtime state is in `tx2_pmus`, per-PMU active counter bitmaps, event arrays, hrtimer state, selected CPU, and MMIO counters. L3C/DMC are 32-bit and use a 2-second hrtimer to sample before overflow; CCPI2 uses 64-bit reads without hrtimer. Counts are prorated for L3 tiles or DMC channels.

Dependencies and integration: depends on ACPI namespace/resources, perf, hrtimer, cpuhotplug, MMIO, and NUMA CPU masks.

Risks: no hardware overflow IRQ for L3C/DMC means high-rate events can still wrap between 2-second ticks. DMC data-transfer events are divided by four to convert 16-byte granularity to 64-byte units, so event semantics must match documentation. Hotplug can leave `cpu >= nr_cpu_ids` if no local CPU remains. Test signals include ACPI child discovery, sysfs PMUs `uncore_l3c_N`, `uncore_dmc_N`, `uncore_ccpi2_N`, group sizing, hrtimer count monotonicity, and node-local CPU migration.
