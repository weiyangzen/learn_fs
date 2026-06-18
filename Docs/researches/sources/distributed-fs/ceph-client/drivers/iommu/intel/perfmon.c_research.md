<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c

Purpose: Intel IOMMU hardware performance-monitoring PMU driver. It discovers VT-d PMU capabilities, exposes perf events and filters via sysfs, assigns events to IOMMU counters, handles freeze/unfreeze and counter overflow interrupts, and registers/unregisters a system-wide perf PMU per IOMMU.

Important APIs/types/functions: public entry points are `alloc_iommu_pmu()`, `free_iommu_pmu()`, `iommu_pmu_register()`, and `iommu_pmu_unregister()`. Internal perf callbacks include `iommu_pmu_event_init()`, `iommu_pmu_add()`, `iommu_pmu_del()`, `iommu_pmu_start()`, `iommu_pmu_stop()`, `iommu_pmu_event_update()`, `iommu_pmu_enable()`, and `iommu_pmu_disable()`.

Control flow: allocation checks ECAP PMS, ECMD support, `DMAR_PERFCAP`, counter/event-group counts, overflow interrupt support, and essential ECMD capability. It reads event-group capabilities, builds per-counter capability matrices, maps config/counter/overflow MMIO windows from offset registers, and stores `iommu->pmu`. Registration fills `struct pmu`, calls `perf_pmu_register()`, then allocates/request a DMAR perf IRQ. Event add selects a compatible free counter, writes event config, programs supported filters from `config1/config2`, and starts if requested. Overflow IRQ reads status, updates assigned events, clears overflow bits, and clears DMAR perf interrupt status.

State and persistence: state lives in `struct iommu_pmu`: capability arrays, used counter bitmap, event pointers, MMIO register bases, IRQ name, and backpointer to `intel_iommu`. Active events persist in hardware counters until stopped/deleted.

Dependencies and integration: depends on Intel VT-d PMU capability macros, enhanced command submission, perf core PMU callbacks, DMAR hardware IRQ allocation, and sysfs PMU attribute machinery.

Risks: capability parsing is hardware-specific; inconsistent per-counter capabilities reduce usable counter count. Filter bit encodings must match the PMU sysfs format. Runtime ECMD errors are intentionally ignored in start/stop, so users may see stale/no counts. `free_iommu_pmu()` assumes `cntr_evcap` is present when `evcap` is present.

Test signals: perf list/sysfs event visibility, perf stat with each event group, filter programming for requester/domain/PASID/ATS/page-table, grouped event scheduling beyond counter count, overflow IRQ delivery, register/unregister on probe/remove, and hardware without PMS/ECMD/PERFCAP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perfmon.c -->
