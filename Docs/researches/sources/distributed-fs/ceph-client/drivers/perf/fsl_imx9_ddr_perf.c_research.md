# sources/distributed-fs/ceph-client/drivers/perf/fsl_imx9_ddr_perf.c

Purpose: Implements the NXP i.MX9 DDRC PerfMon PMU for i.MX91/93/94/95. It exposes reference and counter-specific DDR controller events, supports AXI ID/mask filters with v1/v2 layouts, and manages a 64-bit cycle counter plus ten normal counters.

Important APIs, types, and functions: `struct ddr_pmu` tracks `struct pmu`, MMIO base, active CPU, IRQ, IDA ID, event array, active count, and `imx_ddr_devtype_data`. Event descriptors use `struct imx9_pmu_events_attr` with optional device-type visibility. Key helpers include `ddr_perf_counter_global_config()`, `ddr_perf_counter_local_config()`, `imx93_ddr_perf_monitor_config()`, `imx95_ddr_perf_monitor_config()`, `ddr_perf_alloc_counter()`, `ddr_perf_event_add()`, and `ddr_perf_irq_handler()`.

Control flow: Probe maps MMIO, initializes PMU callbacks, reads match data, allocates an ID/name, installs CPU-hotplug callbacks, requests and pins IRQ, and registers perf. PMU enable globally freezes/resets then enables interrupts and freeze-on-condition. Event add decodes event ID and requested counter from `config`, allocates the dedicated cycle counter, a requested counter-specific slot, or any free normal counter, programs AXI filter registers for v1/v2 devices, and starts if requested. Interrupt updates all active counters, clears counters, and re-enables global monitoring.

State and persistence: State is volatile. `events[11]` owns counters and `active_events` counts scheduled events. Hardware counters are cleared after reads; global control register freezes all counters on disable/overflow. Filter state is in PMCFG registers and depends on SoC generation.

Dependencies and integration: Uses OF platform matching, perf PMU sysfs groups, MMIO, IRQ affinity, CPU hotplug migration, and IDA naming. It does not enable clocks itself, unlike the i.MX8 driver.

Risks and test signals: Counter encoding is easy to misuse because `event` spans both event ID and counter-specific bits. V1/v2 filter programming has distinct register layouts and visibility rules. Probe error handling should be checked for `ida_alloc()` failures and IRQ affinity failures. Test signals are event visibility by compatible string, dedicated counter allocation rejection, overflow IRQ updates, AXI filter counts, and CPU offline migration.
