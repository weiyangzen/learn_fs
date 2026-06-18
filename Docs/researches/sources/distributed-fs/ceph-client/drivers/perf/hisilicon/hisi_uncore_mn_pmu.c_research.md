# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_mn_pmu.c

Purpose: Implements the HiSilicon MN uncore PMU for DVM/barrier request and latency events.

Important APIs, types, and functions: `struct hisi_mn_pmu_regs` abstracts register offsets. Device-specific ops implement 48-bit counter access, packed event-type programming, global/per-counter control, interrupt mask/status/clear, and `hisi_mn_pmu_counter_flush()` to drain dynamic requests after stopping counters.

Control flow: ACPI ID `HISI0222` selects v1 metadata. Probe reads SCL and index topology, maps MMIO, initializes IRQ, reads version, names the PMU `hisi_scl%d_mn%d`, adds a dynamic CPU hotplug instance with devm cleanup, initializes common perf callbacks, registers perf, and adds devm unregister cleanup. There is no remove callback; cleanup is devm/platform-driver driven.

State and persistence: Runtime state is common `struct hisi_pmu`. Stop clears perf enable and polls dynamic control until outstanding requests complete or a timeout warns, improving latency counter accuracy.

Dependencies and integration: Uses ACPI/platform resources, property topology, `readl_poll_timeout_atomic`, common HiSilicon uncore helpers, perf, CPU hotplug, IRQ, and devm action cleanup.

Risks and test signals: The driver suppresses bind attributes because unbinding while sampling is unsafe. Flush timeout behavior is a key accuracy and reliability risk. Test event visibility, latency event reads after stop, timeout warning path, CPU hotplug cleanup via devm actions, and platform driver removal.
