# sources/distributed-fs/ceph-client/drivers/nvdimm/nd_perf.c

Purpose: Implements the generic libnvdimm performance monitoring unit registration helper used by architecture or platform NVDIMM PMU providers. It exposes a fixed set of NVDIMM event encodings, PMU format metadata, and a hotplug-aware `cpumask` sysfs attribute.

Important APIs and flow: `register_nvdimm_pmu()` validates provider-supplied PMU callbacks (`event_init`, `add`, `del`, `read`, and `name`), allocates PMU attribute-group storage, installs `format`, `events`, and dynamic `cpumask` groups, initializes CPU hotplug state, and calls `perf_pmu_register()`. `unregister_nvdimm_pmu()` unregisters perf state, removes hotplug state, frees PMU attribute groups, and frees the provider object. `nvdimm_events_sysfs_show()` prints `event=0xNN`; `nvdimm_pmu_cpumask_show()` reports the current designated CPU.

State and persistence behavior: Runtime state lives in `struct nvdimm_pmu`: `dev`, `pmu.attr_groups`, `arch_cpumask`, `cpu`, `cpuhp_state`, and hotplug `node`. No persistent media state is modified. CPU offline handling removes the CPU from `arch_cpumask`, chooses another allowed CPU or NUMA-local CPU, and migrates perf context with `perf_pmu_migrate_context()`.

Dependencies and integration points: Depends on `linux/nd.h` PMU macros, perf PMU registration, CPU hotplug multi-state APIs, cpumask helpers, and platform devices. Providers supply the actual counter access callbacks.

Risks and test signals: Hotplug teardown must match registration even after partial failures. The dynamic cpumask group frees only the attrs array and group, while the `perf_pmu_events_attr` allocation is not separately retained in this file. Tests should cover invalid provider callbacks, PMU register failure cleanup, CPU online/offline migration, empty `arch_cpumask`, and NUMA node without online CPUs.
