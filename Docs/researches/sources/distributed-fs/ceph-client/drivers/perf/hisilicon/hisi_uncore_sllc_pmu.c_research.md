# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_sllc_pmu.c

Purpose: This file implements the HiSilicon system-level last-level cache uncore PMU. It exposes SLLC events and optional target/source/trace-tag filters through perf while reusing the common HiSilicon uncore PMU framework for scheduling, overflow, and hotplug.

Important APIs, types, and functions: `struct hisi_sllc_pmu_regs` captures register offsets and bit shifts for SLLC v2 and v3 variants. Filter helpers decode `config1` fields for target ID minimum/maximum, source ID command/mask, and trace tag enable. `hisi_sllc_pmu_write_evtype()`, counter read/write, counter and interrupt enable/disable, global start/stop, status/clear, and filter operations implement `struct hisi_uncore_ops`. `hisi_sllc_pmu_init_data()` reads topology, maps MMIO, and reads the version register. Static match data supplies v2 and v3 register maps.

Control flow: module init creates the SLLC CPU hotplug state and registers the platform driver. Probe allocates a `struct hisi_pmu`, validates `sccl-id` and `idx-id`, selects match data for `HISI0263` or `HISI0264`, maps MMIO, requests IRQ, sets eight 64-bit counters and event limit `0xff`, registers a hotplug instance, initializes the common PMU, and registers a named PMU such as `hisi_sccl%d_sllc%d`. At event start, common code writes the event type, configures optional filters, enables interrupts, enables the counter, and starts global counting.

State and persistence: Device lifetime state is in `struct hisi_pmu`; variant register state is static. Hardware filter registers are shared per PMU and are set/cleared when events start/stop. There is no persistent storage. Counter values and overflow reload state are volatile.

Dependencies and integration points: Requires ACPI device IDs, platform memory and IRQ resources, CPU hotplug `CPUHP_AP_PERF_ARM_HISI_SLLC_ONLINE`, perf PMU registration, and common exported HiSilicon framework functions. Sysfs events include receive/transmit request/data and cycles, with format fields for filter controls.

Risks: Filter enable bits (`SLLC_FILT_EN`, trace tag, target, source) are global to the PMU, so concurrent filtered events can conflict. `tgtid_is_valid()` only accepts `max > 0 && max >= min`; target ID zero ranges cannot be expressed as a valid active filter. SLLC v2 and v3 register layouts differ substantially, so wrong ACPI match data would misprogram MMIO. The code sets `pmu_events.attr_groups` to v2 groups for both variants, so event/filter sysfs is shared even when v3 hardware semantics differ.

Test signals: Verify ACPI enumeration creates `hisi_sccl*_sllc*`, sysfs `identifier`, `format`, and event files. Run `perf stat` for `cycles`, `rx_req`, and `tx_req`; verify counts change. Test `config1` filters individually and in combinations. Exercise CPU hotplug and overflow IRQ handling under high event rates.
