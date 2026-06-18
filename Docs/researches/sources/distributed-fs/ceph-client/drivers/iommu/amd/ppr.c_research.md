# sources/distributed-fs/ceph-client/drivers/iommu/amd/ppr.c

Purpose: handles AMD Page Request (PPR) logs and generic I/O page fault integration. It allocates/enables the PPR ring, polls entries from interrupts, converts valid hardware page requests into `iopf_fault` events, and sends page responses back as COMPLETE_PPR commands.

Important APIs, types, and functions: `amd_iommu_alloc_ppr_log()`, `amd_iommu_enable_ppr_log()`, `amd_iommu_restart_ppr_log()`, `amd_iommu_poll_ppr_log()`, `amd_iommu_iopf_init()`, `amd_iommu_iopf_uninit()`, `amd_iommu_iopf_add_device()`, `amd_iommu_iopf_remove_device()`, and `amd_iommu_page_response()`. Helpers include `ppr_flag_to_fault_perm()`, `ppr_is_valid()`, and `iommu_call_iopf_notifier()`.

Control flow: init allocates the ring and queue; enable writes the physical ring base/length and turns on PPR interrupts/logging. The interrupt thread in `iommu.c` calls `amd_iommu_poll_ppr_log()`, which waits for entry materialization, optionally clears erratum-sensitive entries, advances the head pointer, validates request type/flags/PASID, reports device faults to generic IOMMU, or immediately completes failed requests. Page responses call back into `amd_iommu_complete_ppr()`.

State and persistence: per-IOMMU state includes `ppr_log`, MMIO head/tail, `iopf_queue`, and a queue name. Per-device `dev_data->ppr` records whether the device was added to the IOPF queue. PPR log memory is hardware-owned while enabled.

Dependencies and integration points: integrates with AMD command completion in `iommu.c`, PCI device lookup, generic `iommu_report_device_fault()`, IOPF queues, PRI enablement in attach, SNP erratum behavior, and hardware PPR field macros.

Risks: invalid or malicious PPR entries must be failed to prevent hanging devices. PASID bounds are checked against `dev_data->max_pasids`. Ring overflow restart is separate from normal polling. If PRI is enabled but IOPF queue add fails, attach disables PRI to avoid unhandled page requests.

Test signals: page request fault injection, invalid PASID/format/GN-bit cases, IOPF queue add/remove around attach/detach, response status propagation, PPR overflow restart, and SNP versus non-SNP entry clearing behavior.
