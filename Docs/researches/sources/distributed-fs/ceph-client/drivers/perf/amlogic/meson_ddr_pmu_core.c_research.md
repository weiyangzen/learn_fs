# sources/distributed-fs/ceph-client/drivers/perf/amlogic/meson_ddr_pmu_core.c

Purpose: Provides the generic perf PMU layer for Amlogic DDR bandwidth counters. Hardware-specific callbacks supply enable/disable, IRQ handling, counter reads, AXI filter programming, channel count, capabilities, and format attributes.

Important APIs and functions: `struct ddr_pmu` wraps `struct pmu`, `struct dmc_info`, accumulated counters, CPU hotplug state, and device metadata. Exported-in-object functions are `meson_ddr_pmu_create()` and `meson_ddr_pmu_remove()`. Perf callbacks include `meson_ddr_perf_event_init()`, `add`, `start`, `stop`, `del`, and `update`. `dmc_irq_handler()` accumulates one-shot hardware counter snapshots. Sysfs exposes bandwidth events with `.unit` and `.scale`, format attributes filtered by hardware capability, `cpumask`, and identifier.

Control flow: Platform-specific probe calls `meson_ddr_pmu_create()`, which allocates the PMU, parses DT resources and IRQ, installs hardware format attributes, creates a CPU hotplug state, fills event aliases according to channel count, and registers perf. Event init rejects sampling/task events and requires a CPU. Event add programs AXI filters from `config1` and `config2` bitmaps, with at most four ports per channel event. Start clears accumulated counters and enables hardware. IRQ handler asks hardware to acknowledge/fill counters, adds them to software totals, and re-enables one-shot timer mode if still enabled. Stop optionally updates from current hardware counters and disables hardware.

State and persistence: Software accumulation in `pmu->counters` preserves counts across periodic hardware timer interrupts during a perf session. Hardware filter and timer/counter state is reset by the hardware-specific disable callback. CPU affinity is stored in `pmu->cpu` and migrated on hotplug with IRQ affinity update.

Dependencies and integration points: Depends on perf event core, platform/OF resource parsing, IRQs, cpuhotplug, sysfs, and `soc/amlogic/meson_ddr_pmu.h`. The G12 implementation supplies `struct dmc_hw_info` through OF match data.

Risks: `ddr_perf_events_attrs` and `ddr_perf_format_attr_group.attrs` are file-global, so multiple hardware instances with different capabilities/channel counts could race or overwrite sysfs layout. `meson_ddr_perf_format_attr_visible()` calls a show method into a fixed 20-byte stack buffer, which depends on current format strings remaining short. Filter programming does not clear previous filters on add except via hardware disable paths, so session sequencing matters.

Test signals: OF probe with all required MMIO resources plus PLL resource, IRQ accumulation, total and per-channel events, AXI filter masks across `config1`/`config2`, capability-based format visibility, CPU hotplug migration, and scale/unit correctness for MB conversion.
