<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c

Purpose: registers a simple counting PMU named `vpa_pmu` for PowerVM L1 VPA-based virtualization counters: L1-to-L2 context-switch latency, L2-to-L1 latency, and aggregate L2 runtime.

Important APIs/types/functions: `vpa_pmu_events_sysfs_show()` formats sysfs `event=0x..`; `VPA_PMU_EVENT_ATTR()` creates named events; `vpa_pmu_event_init()` validates event type and rejects sampling/branch stacks; `get_counter_data()` chooses per-task/vCPU or global KVM HV counter accessors; `vpa_pmu_add()`, `vpa_pmu_read()`, and `vpa_pmu_del()` implement counting; `pseries_vpa_pmu_init()` and cleanup register/unregister the PMU module.

Control flow: module init only succeeds on PowerVM LPAR L1, not KVM guests. Event add enables L2 counter accumulation for the current CPU and stores a baseline. Reads subtract the previous baseline from the current counter and add the delta to `event->count`. Delete performs a final read and disables accumulation for the CPU.

State and persistence: persistent state is the registered `struct pmu`; per-event state uses `event->hw.prev_count`; hypervisor/KVM HV state is toggled via `kvmhv_set_l2_counters_status()`. There is no local allocation.

Dependencies and integration: depends on KVM Book3S HV counter helpers, firmware feature checks, perf PMU registration, sysfs event macros, and module lifecycle. It uses `perf_sw_context` and declares no interrupts/exclude support.

Risks and test signals: `vpa_pmu_read()` does not update `prev_count`, so repeated reads add deltas from the original baseline; per-task versus CPU attachment changes accessor choice; enabling/disabling by `smp_processor_id()` assumes event CPU affinity semantics. Test counting with repeated `perf stat` reads, task-attached and CPU-wide events, concurrent events on the same CPU, LPAR/KVM/bare-metal load gating, and module unload while counters are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c -->
