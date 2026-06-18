## `sources/distributed-fs/ceph-client/arch/x86/events/rapl.c`

Purpose: implements the Intel/AMD RAPL perf PMUs for read-only energy counters. It exposes package/die scoped `power` events and, on AMD/Hygon, per-core `power_core` energy events.

Important APIs, types, and functions: `struct rapl_pmu` tracks one topology-scoped PMU instance, active events, and overflow-prevention hrtimer. `struct rapl_pmus` owns the perf `pmu`, counter mask, and indexed PMU instances. `struct rapl_model` maps CPU models to MSR tables and energy domains. Core operations are `rapl_pmu_event_init()`, `add()`, `start()`, `stop()`, `read()`, `rapl_event_update()`, `rapl_check_hw_unit()`, `init_rapl_pmus()`, and module init/exit.

Control flow: module init matches CPU model/feature, reads the energy unit MSR, computes a conservative timer interval, allocates per-package/die/core PMU objects, probes domain MSRs with `perf_msr_probe()`, registers PMUs, and advertises units. Event init validates type, system-wide CPU binding, no sampling, config bits, supported domain bit, topology index, and assigns `pmu_private`. Active events are list-managed under a raw spinlock. The hrtimer periodically updates software counts so 32-bit hardware counters do not wrap unnoticed.

State and persistence: energy MSRs are free-running hardware counters shared with other tools. Software state includes global model pointer, hardware unit arrays, `rapl_pmus_pkg/core`, per-PMU active lists, and event `prev_count`/`count`. No persistent storage beyond kernel lifetime.

Dependencies and integration points: Linux perf core, hrtimers, topology package/die/core IDs, x86 CPU model matching, MSR reads, `probe.c`, and sysfs event/format groups. Event counts are fixed-point 32.32 Joules and userspace scales using the exposed `.scale` files.

Risks: unit quirks are model-specific; wrong unit means wrong energy reporting. Topology index failures disable events on unusual CPU maps. The core-scope branch validates against the package-domain maximum, which warrants regression attention. Hrtimer/list locking must prevent update-vs-stop races.

Test signals: `perf list | grep power`, sysfs `events/*.{unit,scale}`, `perf stat -a -e power/energy-pkg/ sleep 1`, wrap behavior under long runs, model-specific domain visibility, and module unload cleanup.
